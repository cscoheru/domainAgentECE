"""OEI-009 step 3.3 — timebox end-to-end (expire / restore).

Takes the ACL row created in step 2.6 (allow alice on engine_document:<id>,
valid_from=today, valid_to=today+ACL_VALID_DAYS) and:

  1. With valid_to=today+N (active) — alice sees 4 docs.
  2. After UPDATE acl_entries SET valid_to=yesterday — alice sees 3 docs.
  3. After UPDATE valid_to=today+N again — alice sees 4 docs (restored).

Saves the three raw library responses plus the ACL state diffs.

Note: this only mutates `valid_to` (which the OEI-009 timebox rules 1–4
in check_permission consult). The other ACL rows (deny / role / dept)
are unaffected.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

import httpx

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "ece" / "src"))

from sqlalchemy import text as _sql_text  # noqa: E402

from ece.db import get_engine  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Same fixed query as step 2.6 — single source of truth, so the timebox e2e
# and the A4 matrix cannot drift apart (v1 hardcoded a different string).
from step26_demo_falsifiable import ACL_VALID_DAYS, DEMO_QUERY as QUERY  # noqa: E402

ONYX_BASE = os.environ.get("ECE_ONYX_BASE", "http://127.0.0.1:8080")
COOKIE_FILE = os.environ.get(
    "ECE_ONYX_COOKIE_FILE", "/home/fisher/.onyx-lab/.secrets/admin-cookies.txt"
)
PROJECT_ID = 1
DEMO_USER = "alice"


def _library_response(client, query: str, headers: dict) -> dict:
    r = client.get(
        "/api/v1/consulting/library",
        params={"q": query},
        headers=headers,
    )
    return {
        "status": r.status_code,
        "engine_status": r.json().get("engine_status"),
        "engine_items_titles": sorted(
            it["title"] for it in r.json().get("engine_items", [])
        ),
    }


def main() -> int:
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    # Restore target = the same window step 2.6 created (see ACL_VALID_DAYS).
    active_until = today + dt.timedelta(days=ACL_VALID_DAYS)

    sql_engine = get_engine()
    # 1. Find the step 2.6 ACL row by subject + source_system.
    with sql_engine.connect() as conn:
        rows = conn.execute(
            _sql_text(
                """
                SELECT id, object_ref, valid_from, valid_to
                FROM acl_entries
                WHERE subject_type='user' AND subject_ref=:sub
                  AND object_type='engine_document' AND effect='allow'
                  AND source_system='system:oei009-step26'
                """
            ),
            {"sub": DEMO_USER},
        ).fetchall()
    if not rows:
        print("ERROR: step 2.6 ACL row not found; run step26_demo_falsifiable.py first")
        return 1
    acl_id = int(rows[0][0])
    object_ref = rows[0][1]

    out: dict = {"acl_id": acl_id, "object_ref": object_ref, "stages": []}

    # Set up TestClient once (env already set by caller).
    os.environ["ECE_CONTENT_ENGINE"] = "onyx"
    for mod in list(sys.modules):
        if mod.startswith("ece."):
            del sys.modules[mod]

    from fastapi.testclient import TestClient  # noqa: PLC0415

    from ece.main import app  # noqa: PLC0415

    client = TestClient(app)

    # Stage A: active window (as set by step 2.6; we re-affirm here).
    with sql_engine.begin() as conn:
        conn.execute(
            _sql_text("UPDATE acl_entries SET valid_to=:vt WHERE id=:id"),
            {"vt": active_until, "id": acl_id},
        )
    with sql_engine.connect() as conn:
        acl_now = conn.execute(
            _sql_text("SELECT valid_from, valid_to FROM acl_entries WHERE id=:id"),
            {"id": acl_id},
        ).first()
    out["stages"].append(
        {
            "label": "A: valid_to=today+%d (active)" % ACL_VALID_DAYS,
            "acl_valid_to": str(acl_now[1]),
            "library_alice": _library_response(client, QUERY, {"X-User-Id": DEMO_USER}),
        }
    )

    # Stage B: valid_to=yesterday (expired → alice should lose access).
    with sql_engine.begin() as conn:
        conn.execute(
            _sql_text("UPDATE acl_entries SET valid_to=:vt WHERE id=:id"),
            {"vt": yesterday, "id": acl_id},
        )
    with sql_engine.connect() as conn:
        acl_now = conn.execute(
            _sql_text("SELECT valid_from, valid_to FROM acl_entries WHERE id=:id"),
            {"id": acl_now[1] if False else acl_id},  # keep id stable
        ).first()
    out["stages"].append(
        {
            "label": "B: valid_to=yesterday (expired)",
            "acl_valid_to": str(acl_now[1]),
            "library_alice": _library_response(client, QUERY, {"X-User-Id": DEMO_USER}),
        }
    )

    # Stage C: restore the active window.
    with sql_engine.begin() as conn:
        conn.execute(
            _sql_text("UPDATE acl_entries SET valid_to=:vt WHERE id=:id"),
            {"vt": active_until, "id": acl_id},
        )
    with sql_engine.connect() as conn:
        acl_now = conn.execute(
            _sql_text("SELECT valid_from, valid_to FROM acl_entries WHERE id=:id"),
            {"id": acl_id},
        ).first()
    out["stages"].append(
        {
            "label": "C: valid_to=today+%d (restored)" % ACL_VALID_DAYS,
            "acl_valid_to": str(acl_now[1]),
            "library_alice": _library_response(client, QUERY, {"X-User-Id": DEMO_USER}),
        }
    )

    print(json.dumps(out, indent=2, default=str))

    # Acceptance: A and C see 4, B sees 3.
    titles_a = out["stages"][0]["library_alice"]["engine_items_titles"]
    titles_b = out["stages"][1]["library_alice"]["engine_items_titles"]
    titles_c = out["stages"][2]["library_alice"]["engine_items_titles"]

    fail = False
    if len(titles_a) != 4:
        print(f"FAIL A: expected 4, got {len(titles_a)}")
        fail = True
    if len(titles_b) != 3:
        print(f"FAIL B: expected 3, got {len(titles_b)}")
        fail = True
    if len(titles_c) != 4:
        print(f"FAIL C: expected 4, got {len(titles_c)}")
        fail = True
    if fail:
        return 1
    print("PASS — Step 3.3 timebox e2e: A=4, B=3 (expired), C=4 (restored).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())