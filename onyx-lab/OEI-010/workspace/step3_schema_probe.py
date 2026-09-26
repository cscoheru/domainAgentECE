"""OEI-010 step 3 (A3) — `memories` schema: live inspection + real violations.

The migration is only half the claim; the other half is that the constraints
actually BITE. So this does not describe them — it triggers them and prints the
database's own error text, including the constraint name.

  * duplicate `(scope, owner_ref, statement)`  -> UniqueViolation
  * `scope = 'team'` (outside the vocabulary)  -> CheckViolation
  * `confidence = 1.50` (outside 0..1)         -> CheckViolation

Every attempt happens inside a transaction that is ROLLED BACK, so the probe is
side-effect free and re-runnable.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step3_schema_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "ece" / "src"))

from ece.db import get_engine  # noqa: E402

TABLE = "memories"


def _constraint_name(exc: IntegrityError) -> str:
    """The constraint the DATABASE named — from the driver's diagnostics, not ours."""
    orig = getattr(exc, "orig", None)
    diag = getattr(orig, "diag", None)
    name = getattr(diag, "constraint_name", None)
    return name or "<driver exposed no constraint_name>"


def main() -> int:
    engine = get_engine()
    fails: list[str] = []

    # ---- live column list ---------------------------------------------------
    with engine.connect() as conn:
        cols = conn.execute(
            text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = :t
                ORDER BY ordinal_position
            """),
            {"t": TABLE},
        ).fetchall()
    print(f"== columns of `{TABLE}` ({len(cols)}) ==")
    for c in cols:
        print(f"  {c[0]:<16} {c[1]:<26} nullable={c[2]:<3} default={c[3]}")

    # ---- constraints --------------------------------------------------------
    with engine.connect() as conn:
        cons = conn.execute(
            text("""
                SELECT c.conname, c.contype, pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_class t ON t.oid = c.conrelid
                WHERE t.relname = :t
                ORDER BY c.conname
            """),
            {"t": TABLE},
        ).fetchall()
    print(f"\n== constraints on `{TABLE}` ({len(cons)}) ==")
    for name, ctype, definition in cons:
        print(f"  {name:<42} type={ctype}  {definition}")

    # ---- indexes ------------------------------------------------------------
    with engine.connect() as conn:
        idx = conn.execute(
            text("""
                SELECT indexname, indexdef FROM pg_indexes
                WHERE tablename = :t ORDER BY indexname
            """),
            {"t": TABLE},
        ).fetchall()
    print(f"\n== indexes on `{TABLE}` ({len(idx)}) ==")
    for name, definition in idx:
        print(f"  {name:<42} {definition}")

    # ---- violation probes ---------------------------------------------------
    print("\n== constraint probes (each rolled back) ==")

    def probe(label: str, sql: str, params: dict, expect: str) -> None:
        try:
            with engine.begin() as conn:
                conn.execute(text(sql), params)
                # Reaching here means the DB accepted it -> the constraint is
                # MISSING. Force a rollback by raising out of the context.
                raise AssertionError(f"{label}: statement was ACCEPTED (no constraint fired)")
        except AssertionError as exc:
            print(f"  [FAIL] {label}: {exc}")
            fails.append(label)
        except IntegrityError as exc:
            name = _constraint_name(exc)
            first_line = str(exc.orig).strip().splitlines()[0]
            print(f"  [ok]   {label}")
            print(f"         expected : {expect}")
            print(f"         db says  : {first_line}")
            print(f"         constraint: {name}")

    base = (
        "INSERT INTO memories (scope, owner_ref, statement, classification, source"
        "{extra_cols}) VALUES (:scope, :owner_ref, :statement, 'restricted', "
        "'probe:oei010'{extra_vals})"
    )

    # Seed one row so the duplicate has something to collide with. Committed,
    # then removed at the end of the probe block.
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO memories (scope, owner_ref, statement, classification, source)
                VALUES ('user', 'oei010-probe-dup', 'probe statement', 'restricted', 'probe:oei010')
                ON CONFLICT ON CONSTRAINT uq_memories_scope_owner_ref_statement
                DO NOTHING
            """)
        )

    probe(
        "duplicate (scope, owner_ref, statement)",
        base.format(extra_cols="", extra_vals=""),
        {"scope": "user", "owner_ref": "oei010-probe-dup", "statement": "probe statement"},
        "UniqueViolation on uq_memories_scope_owner_ref_statement",
    )
    probe(
        "scope outside the vocabulary ('team')",
        base.format(extra_cols="", extra_vals=""),
        {"scope": "team", "owner_ref": "x", "statement": "s"},
        "CheckViolation on ck_memories_scope",
    )
    probe(
        "confidence outside 0..1 (1.50)",
        base.format(extra_cols=", confidence", extra_vals=", :confidence"),
        {"scope": "user", "owner_ref": "x", "statement": "s", "confidence": 1.5},
        "CheckViolation on ck_memories_confidence",
    )

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM memories WHERE source = 'probe:oei010'")
        )

    with engine.connect() as conn:
        left = conn.execute(
            text("SELECT count(*) FROM memories WHERE source = 'probe:oei010'")
        ).scalar_one()
    print(f"\n  probe residue after cleanup: {left} row(s)")

    if fails:
        print(f"\nFAIL — {len(fails)} constraint probe(s) did not fire: {fails}")
        return 1
    print("\nPASS — Step 3 (A3): schema present; all three constraints fire by name.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
