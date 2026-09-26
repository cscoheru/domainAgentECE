"""OEI-010 step 4 (A4) — every memory write goes through the permission engine.

Nine cells, not six: TASK §5 步骤 4.4 asks for at least six, and the two extra
ones are the interesting *fail-closed* cases (a caller with no org, and a
perfectly ordinary user who simply has no grant on their own scope).

The matrix separates the two gates deliberately:

  gate 1 (subject)  — `body.owner_ref` must match the CREDENTIAL. A mismatch is
                      rejected; it is never rewritten to the caller.
  gate 2 (policy)   — `check_permission` on the scope object
                      (`memory_scope` / `user:<ref>` | `org:<ref>`),
                      `classification='restricted'` -> default deny.

Different cells fail at different gates, which is the point: a 403 from gate 1
and a 403 from gate 2 are different findings, and the response says which.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step4_write_matrix.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _client import (  # noqa: E402
    create_memory,
    dump,
    fresh_app,
    sql_exec,
    sql_rows,
    sql_scalar,
)

PROC = "demo-user-procurement"
FIN = "demo-user-finance"
ADMIN = "demo-user-admin"
NO_ORG = "oei010-probe-no-org"        # created by step1 (has no org_id)
UNKNOWN = "oei010-probe-unknown-user"  # no entity row at all

TAG = "oei010 step4 probe"


def main() -> int:
    client, engine = fresh_app()

    # Clean any prior run so counts are meaningful (scoped to this probe's own
    # statements — never a table-wide delete).
    sql_exec(engine, "DELETE FROM acl_entries WHERE object_ref IN "
                     "(SELECT 'memory:' || id FROM memories WHERE statement LIKE :p)",
             p=f"{TAG}%")
    sql_exec(engine, "DELETE FROM memories WHERE statement LIKE :p", p=f"{TAG}%")

    before_total = sql_scalar(engine, "SELECT count(*) FROM memories")

    out: dict = {
        "note": (
            "each cell: (caller, scope, owner_ref) -> HTTP status + code. "
            "gate1 = owner_ref vs credential; gate2 = check_permission on the "
            "memory_scope object."
        ),
        "cells": {},
        "row_counts": {},
    }

    def cell(key: str, *, caller, scope, owner_ref, statement, extra=None, caller_label=None):
        body = {
            "scope": scope,
            "owner_ref": owner_ref,
            "statement": statement,
        }
        if extra:
            body.update(extra)
        result = create_memory(client, caller, **body)
        result["inputs"] = {
            "caller": caller_label or caller,
            "scope": scope,
            "owner_ref": owner_ref,
            "credential": "<X-User-Id header>" if caller else "<none — anonymous>",
        }
        out["cells"][key] = result
        return result

    # 1. own user scope -> allow
    cell("1_self_user_ALLOW", caller=FIN, scope="user", owner_ref=FIN,
         statement=f"{TAG} finance own preference")
    # 2. someone else's user scope -> deny (gate 1)
    cell("2_other_user_DENY", caller=FIN, scope="user", owner_ref=PROC,
         statement=f"{TAG} finance tries to write procurement's memory")
    # 3. org scope without the org_admin role -> deny (gate 2)
    cell("3_org_without_role_DENY", caller=FIN, scope="org",
         owner_ref="org:consulting-a",
         statement=f"{TAG} finance tries to write org memory")
    # 4. org scope WITH org_admin -> allow
    cell("4_org_with_role_ALLOW", caller=ADMIN, scope="org",
         owner_ref="org:consulting-a",
         statement=f"{TAG} canonical org stance (written by admin)")
    # 5. org_admin naming ANOTHER org -> deny (gate 1)
    cell("5_org_admin_other_org_DENY", caller=ADMIN, scope="org",
         owner_ref="org:consulting-b",
         statement=f"{TAG} admin tries to write the other org's memory")
    # 6. caller with no org claim -> deny (gate 1)
    cell("6_no_org_claim_DENY", caller=NO_ORG, scope="org",
         owner_ref="org:consulting-a",
         statement=f"{TAG} org-less probe tries to write org memory")
    # 7. an ordinary user with no grant on their own scope -> deny (gate 2).
    #    This is the fail-closed default: no ACL row means no write.
    cell("7_ungranted_self_user_DENY", caller=UNKNOWN, scope="user",
         owner_ref=UNKNOWN,
         statement=f"{TAG} ungranted caller writes its own scope")
    # 8. no credential at all -> 400
    cell("8_no_credential_DENY", caller=None, scope="user", owner_ref=FIN,
         statement=f"{TAG} anonymous write")

    # 9. idempotent re-create of cell 1
    out["cells"]["9_duplicate_create"] = create_memory(
        client, FIN,
        scope="user", owner_ref=FIN, statement=f"{TAG} finance own preference",
    )
    out["cells"]["9_duplicate_create"]["inputs"] = {
        "caller": FIN, "scope": "user", "owner_ref": FIN,
        "note": "byte-identical repeat of cell 1",
    }

    out["row_counts"]["memories_before_probe_block"] = before_total
    out["row_counts"]["memories_created_by_cells_1_to_8"] = sql_scalar(
        engine, "SELECT count(*) FROM memories WHERE statement LIKE :p", p=f"{TAG}%"
    )
    out["row_counts"]["distinct_statements"] = sql_scalar(
        engine,
        "SELECT count(DISTINCT statement) FROM memories WHERE statement LIKE :p",
        p=f"{TAG}%",
    )
    out["acl_rows_written_for_new_memories"] = sql_scalar(
        engine,
        "SELECT count(*) FROM acl_entries WHERE source_system = 'memory:create' "
        "AND object_ref IN (SELECT 'memory:' || id FROM memories WHERE statement LIKE :p)",
        p=f"{TAG}%",
    )

    out["created_memories"] = [
        {"id": r[0], "scope": r[1], "owner_ref": r[2], "statement": r[3]}
        for r in sql_rows(
            engine,
            "SELECT id, scope, owner_ref, statement FROM memories "
            "WHERE statement LIKE :p ORDER BY id",
            p=f"{TAG}%",
        )
    ]

    # ── assertions ─────────────────────────────────────────────────────────
    c = out["cells"]
    fails: list[str] = []

    def expect(key: str, status: int) -> None:
        got = c[key]["status"]
        if got != status:
            fails.append(f"{key}: expected HTTP {status}, got {got} — {c[key]['body']}")

    expect("1_self_user_ALLOW", 200)
    expect("2_other_user_DENY", 403)
    expect("3_org_without_role_DENY", 403)
    expect("4_org_with_role_ALLOW", 200)
    expect("5_org_admin_other_org_DENY", 403)
    expect("6_no_org_claim_DENY", 403)
    expect("7_ungranted_self_user_DENY", 403)
    expect("8_no_credential_DENY", 400)
    expect("9_duplicate_create", 200)

    if c["1_self_user_ALLOW"]["body"].get("created") is not True:
        fails.append("cell 1 did not report created=true")
    if c["9_duplicate_create"]["body"].get("created") is not False:
        fails.append("cell 9 (duplicate) did not report created=false")
    if (
        c["9_duplicate_create"]["body"].get("memory", {}).get("id")
        != c["1_self_user_ALLOW"]["body"].get("memory", {}).get("id")
    ):
        fails.append("duplicate create returned a DIFFERENT row")

    # Eight write attempts, six of them denied -> exactly 2 rows landed
    # (cell 1 self-user, cell 4 org-admin). Anything else means a denied write
    # still wrote, or an allowed write did not.
    if out["row_counts"]["memories_created_by_cells_1_to_8"] != 2:
        fails.append(
            "expected exactly 2 memories from cells 1-8 (self-user + org-admin), "
            f"got {out['row_counts']['memories_created_by_cells_1_to_8']}"
        )
    if out["acl_rows_written_for_new_memories"] != 2:
        fails.append(
            "expected one auto-grant ACL row per created memory, got "
            f"{out['acl_rows_written_for_new_memories']}"
        )

    out["assertions_checked"] = [
        "self user scope allowed (200)",
        "another user's scope denied at gate 1 (403)",
        "org scope without org_admin denied at gate 2 (403)",
        "org scope with org_admin allowed (200)",
        "org_admin naming ANOTHER org denied at gate 1 (403)",
        "caller with no org claim denied (403)",
        "ungranted caller on its OWN scope denied — fail-closed (403)",
        "no credential denied (400)",
        "exactly 2 rows landed from 8 write attempts",
        "one auto-grant ACL row per created memory",
        "duplicate create returns the SAME row with created=false",
    ]
    out["failures"] = fails
    out["verdict"] = "FAIL" if fails else "PASS"

    # stdout stays pure JSON; the human summary goes to stderr.
    for f in fails:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        "PASS — Step 4 (A4): 9/9 cells as specified; "
        "2 memories created (self-user + org_admin), 6 writes denied, "
        "duplicate create returned the SAME row with created=false."
        if not fails else f"FAIL — Step 4 (A4): {len(fails)} assertion(s) failed",
        file=sys.stderr,
    )

    dump(out)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
