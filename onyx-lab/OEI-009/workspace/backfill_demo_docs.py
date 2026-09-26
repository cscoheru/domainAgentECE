"""OEI-009 step 1.4 — backfill the 3 historical demo docs into engine_documents.

Why a separate script:
- TASK v1.3 §4 step 1.4 says: "回填现有 3 份演示文档（不改名、不重传）"
- The 3 docs already exist in Onyx project id=1 with their *historical* titles
  (`case-management-consulting.md`, `methodology-framework.md`,
  `play-sales-delivery.md`). The registry rows for them MUST use these
  exact titles — that's what /api/search returns when the engine recalls them.
- Classification defaults to `public` per TASK (preserves "anonymous can see
  them" surface, A3 / "演示行为不退化").
- Idempotent: rerunning produces zero new rows.

Inputs:
- DATABASE_URL  (env var)  → temp PG (this is the worker's PG, NOT the demo
  project's Onyx; we read the file list from Onyx via /api/user/projects/files/1,
  then write into our local PG).
- ONYX_COOKIE   → /home/fisher/.onyx-lab/.secrets/admin-cookies.txt

Usage:
    cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/workspace
    DATABASE_URL=postgresql+psycopg://ece:ece@127.0.0.1:55432/ece \
      uv run python backfill_demo_docs.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Repo layout: this script lives under workspace/, the package under ../ece/.
_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "ece" / "src"))

from ece.consulting.registry import backfill_demo_files  # noqa: E402
from ece.db import get_engine  # noqa: E402


ONYX_BASE = os.environ.get("ECE_ONYX_BASE", "http://127.0.0.1:8080")
COOKIE_FILE = os.environ.get(
    "ECE_ONYX_COOKIE_FILE", "/home/fisher/.onyx-lab/.secrets/admin-cookies.txt"
)
PROJECT_ID = 1
CLASSIFICATION = "public"
UPLOADED_BY = "system:backfill-oei009"

# Rework fix (VERDICT #2 follow-up): register ONLY the 3 historical demo docs.
# v1 iterated every file in the project — when a stray `ece-*` comparison doc
# was present, it got backfilled as `public`, defeating the restricted-demo
# setup. The whitelist is the contract: exactly these three, nothing else.
DEMO_TITLES = (
    "case-management-consulting.md",
    "methodology-framework.md",
    "play-sales-delivery.md",
)


def _fetch_demo_files(project_id: int) -> list[dict]:
    """GET /api/user/projects/files/{project_id} → list of file rows."""
    import httpx  # local import — this script isn't on the production path

    jar = httpx.Cookies()
    text = Path(COOKIE_FILE).read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or (line.startswith("#") and not line.startswith("#HttpOnly_")):
            continue
        sep = "\t" if "\t" in line else None
        parts = line.split(sep) if sep else line.split()
        if len(parts) < 7:
            continue
        domain, _flag, path_, _secure, _expires, name = parts[:6]
        value = "\t".join(parts[6:]) if sep == "\t" else " ".join(parts[6:])
        jar.set(name, value, domain=domain.lstrip("#HttpOnly_"), path=path_ or "/")
    with httpx.Client(base_url=ONYX_BASE, cookies=jar, timeout=30.0) as cli:
        resp = cli.get(f"/api/user/projects/files/{project_id}")
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise SystemExit(f"unexpected response shape: {type(data).__name__}")
    return data


def main() -> int:
    print(f"== OEI-009 step 1.4 — backfill demo project id={PROJECT_ID}")
    print(f"   onyx base  : {ONYX_BASE}")
    print(f"   cookie file: {COOKIE_FILE}")
    print(f"   sql engine : {os.environ.get('DATABASE_URL')}")

    files = _fetch_demo_files(PROJECT_ID)
    print(f"   onyx reports {len(files)} files in project id={PROJECT_ID}")

    # Normalize: only the 3 whitelisted demo titles; skip everything else
    # (stray ece-* comparison docs, probes) and incomplete rows.
    rows: list[dict] = []
    skipped: list[str] = []
    for f in files:
        if not isinstance(f, dict):
            continue
        fname = f.get("name") or ""
        fid = f.get("id") or ""
        if not fname or not fid:
            continue
        if fname not in DEMO_TITLES:
            skipped.append(fname)
            continue
        rows.append(
            {
                "engine_filename": fname,            # verbatim historical title
                "original_filename": fname,          # same — no rename, no re-upload
                "engine_document_id": str(fid),
                "title": fname,
            }
        )

    print(f"   will register {len(rows)} rows (classification={CLASSIFICATION})")
    if skipped:
        print(f"   skipped (not in DEMO_TITLES whitelist): {sorted(skipped)}")

    sql_engine = get_engine()
    n_after = backfill_demo_files(
        sql_engine,
        demo_files=rows,
        engine_name="onyx",
        engine_project_id=PROJECT_ID,
        classification=CLASSIFICATION,
        uploaded_by=UPLOADED_BY,
    )
    print(f"   engine_documents now has {n_after} rows")

    # Print the registered rows for the evidence file.
    from sqlalchemy import text as _sql_text

    with sql_engine.connect() as conn:
        reg_rows = conn.execute(
            _sql_text(
                """
                SELECT id, engine_filename, engine_document_id, classification, uploaded_by
                FROM engine_documents
                WHERE engine_name = 'onyx' AND engine_project_id = :pid
                ORDER BY id
                """
            ),
            {"pid": PROJECT_ID},
        ).fetchall()

    evidence = []
    for r in reg_rows:
        evidence.append(
            {
                "id": int(r[0]),
                "engine_filename": r[1],
                "engine_document_id": r[2],
                "classification": r[3],
                "uploaded_by": r[4],
            }
        )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))

    # Re-run for idempotency check (Step 1.4 acceptance A3).
    n_after_2 = backfill_demo_files(
        sql_engine,
        demo_files=rows,
        engine_name="onyx",
        engine_project_id=PROJECT_ID,
        classification=CLASSIFICATION,
        uploaded_by=UPLOADED_BY,
    )
    print(f"\n   second run: engine_documents still {n_after_2} rows (idempotent: {n_after == n_after_2})")
    if n_after != n_after_2:
        print("   FAIL — backfill is NOT idempotent")
        return 1

    print("\n   PASS — backfill idempotent, rows printed above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())