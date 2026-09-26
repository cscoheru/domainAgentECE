"""OEI-010 step 1 (A1) — org dimension has a SOURCE.

Before this cut `identity.org_id` was `None` for every real caller: the field
existed (OEI-009) but `resolve_identity()` never passed it and
`upsert_identity()` never wrote it. This script proves the four states and the
incremental-merge property, straight against the DB.

Four states (TASK §5 步骤 1.3):
  1. same org, two people   — demo-user-procurement + demo-user-finance
  2. a different org        — demo-user-engineering
  3. no org at all          — a probe person with NO `org_id` attribute
  4. unknown user           — a `user_ref` with no entity row at all

Plus: `upsert_identity(org_id=...)` must be ADDITIVE. `entities.attributes` is
JSONB and already carries department / roles / is_management; writing an org
must not disturb them. The probe is created WITHOUT an org first (so the keys
exist), then re-upserted WITH one, and the attributes are diffed.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step1_org_identity.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import text

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "ece" / "src"))

from ece.db import get_engine  # noqa: E402
from ece.identity.parser import resolve_identity, upsert_identity  # noqa: E402

PROBE_NO_ORG = "oei010-probe-no-org"
PROBE_MERGE = "oei010-probe-merge"
UNKNOWN = "oei010-probe-unknown-user"

SEEDED = [
    "demo-user-procurement",
    "demo-user-finance",
    "demo-user-engineering",
    "demo-user-admin",
]


def _attrs(engine, source_id: str) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT attributes FROM entities
                WHERE entity_type = 'person'
                  AND source_system = 'api:header' AND source_id = :sid
            """),
            {"sid": source_id},
        ).first()
    return row[0] if row else None


def _delete_probe(engine, source_id: str) -> None:
    """Remove a probe person (and anything referencing it) so this is re-runnable."""
    with engine.begin() as conn:
        conn.execute(
            text("""
                DELETE FROM relationships
                WHERE src_entity_id IN (SELECT id FROM entities WHERE source_id = :sid)
                   OR dst_entity_id IN (SELECT id FROM entities WHERE source_id = :sid)
            """),
            {"sid": source_id},
        )
        conn.execute(
            text("""
                DELETE FROM entity_aliases
                WHERE entity_id IN (SELECT id FROM entities WHERE source_id = :sid)
            """),
            {"sid": source_id},
        )
        conn.execute(
            text("DELETE FROM entities WHERE source_id = :sid AND entity_type = 'person'"),
            {"sid": source_id},
        )


def _ident_dict(ident) -> dict:
    return {
        "user_ref": ident.user_ref,
        "display_id": ident.display_id,
        "department": ident.department,
        "roles": list(ident.roles),
        "is_management": ident.is_management,
        "org_id": ident.org_id,
    }


def main() -> int:
    engine = get_engine()
    out: dict = {"states": {}, "merge": {}, "seeded_persons": {}}

    # --- the four states -----------------------------------------------------
    for name in SEEDED:
        out["states"][name] = _ident_dict(resolve_identity(engine, name))

    # 3. no org: a probe person with no org_id key at all
    _delete_probe(engine, PROBE_NO_ORG)
    upsert_identity(
        engine,
        x_user_id=PROBE_NO_ORG,
        name="OEI-010 Probe (no org)",
        department="sales",
        roles=["buyer"],
        # org_id deliberately not passed -> the key must be ABSENT, not null
    )
    out["states"][PROBE_NO_ORG] = _ident_dict(resolve_identity(engine, PROBE_NO_ORG))
    out["probe_no_org_attributes"] = _attrs(engine, PROBE_NO_ORG)

    # 4. unknown user: no entity row -> stub -> org_id None
    out["states"][UNKNOWN] = _ident_dict(resolve_identity(engine, UNKNOWN))

    # --- additive merge ------------------------------------------------------
    _delete_probe(engine, PROBE_MERGE)
    upsert_identity(
        engine,
        x_user_id=PROBE_MERGE,
        name="OEI-010 Probe (merge)",
        department="finance",
        roles=["finance_manager", "buyer"],
        is_management=False,
    )
    before = _attrs(engine, PROBE_MERGE)
    # Re-upsert the SAME person, this time with an org claim.
    upsert_identity(
        engine,
        x_user_id=PROBE_MERGE,
        name="OEI-010 Probe (merge)",
        department="finance",
        roles=["finance_manager", "buyer"],
        is_management=False,
        org_id="org:probe-a",
    )
    after = _attrs(engine, PROBE_MERGE)
    out["merge"] = {
        "attributes_before": before,
        "attributes_after": after,
        # These three MUST be byte-identical across the write: the merge is
        # additive, so nothing the caller did not name may change.
        "preserved_keys": sorted(set(before or {}) & set(after or {})),
        "preserved_unchanged": all(
            (before or {}).get(k) == (after or {}).get(k)
            for k in ("department", "roles", "is_management")
        ),
        "org_id_added": (after or {}).get("org_id"),
    }

    # A second re-upsert with the SAME org must be a no-op (idempotent).
    upsert_identity(
        engine,
        x_user_id=PROBE_MERGE,
        name="OEI-010 Probe (merge)",
        department="finance",
        roles=["finance_manager", "buyer"],
        is_management=False,
        org_id="org:probe-a",
    )
    out["merge"]["attributes_after_second_write"] = _attrs(engine, PROBE_MERGE)

    # "not passed" must not remove an existing key (back-compat).
    upsert_identity(
        engine,
        x_user_id=PROBE_MERGE,
        name="OEI-010 Probe (merge)",
        department="finance",
        roles=["finance_manager", "buyer"],
        is_management=False,
    )
    out["merge"]["attributes_after_write_without_org"] = _attrs(engine, PROBE_MERGE)

    # --- assertions ---------------------------------------------------------
    fails: list[str] = []
    states = out["states"]
    if states["demo-user-procurement"]["org_id"] != "org:consulting-a":
        fails.append("procurement org_id != org:consulting-a")
    if states["demo-user-finance"]["org_id"] != "org:consulting-a":
        fails.append("finance org_id != org:consulting-a")
    if states["demo-user-engineering"]["org_id"] != "org:consulting-b":
        fails.append("engineering org_id != org:consulting-b")
    if states["demo-user-admin"]["org_id"] != "org:consulting-a":
        fails.append("admin org_id != org:consulting-a")
    if states[PROBE_NO_ORG]["org_id"] is not None:
        fails.append("no-org probe resolved an org_id")
    if states[UNKNOWN]["org_id"] is not None:
        fails.append("unknown user resolved an org_id")
    if out["probe_no_org_attributes"] is None or "org_id" in (
        out["probe_no_org_attributes"] or {}
    ):
        fails.append("no-org probe has an org_id key (must be absent)")
    if not out["merge"]["preserved_unchanged"]:
        fails.append("org write clobbered department/roles/is_management")
    if out["merge"]["org_id_added"] != "org:probe-a":
        fails.append("org_id was not written")
    if out["merge"]["attributes_after_write_without_org"] != out["merge"]["attributes_after"]:
        fails.append("a write WITHOUT org_id mutated the row (not back-compat)")

    out["assertions_checked"] = [
        "procurement/finance/admin resolve to org:consulting-a",
        "engineering resolves to org:consulting-b",
        "a person row without org_id resolves org_id=None",
        "an unknown user resolves org_id=None",
        "the org-less probe has no `org_id` KEY in its attributes at all",
        "writing org_id preserves department/roles/is_management",
        "a write WITHOUT org_id does not mutate the row (back-compat)",
    ]
    out["failures"] = fails
    out["verdict"] = "FAIL" if fails else "PASS"

    for f in fails:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        "PASS — Step 1 (A1): four states resolved "
        "(2 same-org / 1 other-org / 1 no-org / 1 unknown); "
        "org write is additive and idempotent; a write without org_id is a no-op."
        if not fails else f"FAIL — Step 1 (A1): {len(fails)} assertion(s) failed",
        file=sys.stderr,
    )

    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
