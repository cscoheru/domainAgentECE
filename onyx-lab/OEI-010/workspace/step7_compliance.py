"""OEI-010 step 7 (A8/A9) — the compliance surface: list, delete, trace.

A8 asks two things that pull in opposite directions, which is the point of the
cut: an injected memory must be **traceable** (`context_items` +
`GET /api/v1/audit/context/{request_id}`) while the user-facing surfaces must
stay **silent** (`ece/demos/spa/**` untouched, no "which memories were used"
display anywhere).

A9 is deletion: soft, permission-scoped, and non-destructive to the audit trail.
The interesting assertions are the negatives — a caller deleting someone else's
memory, or bulk-deleting an org's memories without org write permission — and the
one that makes deletion safe for compliance: after the memory is gone, the
historical record that it WAS injected must survive.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step7_compliance.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _client import (  # noqa: E402
    assemble_context,
    create_memory,
    delete_memory,
    delete_memory_bulk,
    dump,
    fresh_app,
    hdr,
    list_memory,
    sql_exec,
    sql_rows,
    sql_scalar,
)

FIN = "demo-user-finance"        # org:consulting-a
PROC = "demo-user-procurement"   # org:consulting-a
ENG = "demo-user-engineering"    # org:consulting-b
ADMIN = "demo-user-admin"        # org:consulting-a + org_admin
ORGA = "org:consulting-a"

TAG = "oei010 step7 probe"
S_FIN = f"{TAG} finance listable memory"
S_FIN_BULK = f"{TAG} finance bulk-delete candidate"
S_FIN_TRACE = f"{TAG} finance traceable memory"
S_PROC = f"{TAG} procurement memory (other user's)"
S_ORGA = f"{TAG} org-a memory (bulk-delete target)"


def main() -> int:
    client, engine = fresh_app()
    out: dict = {"setup": {}, "list": {}, "delete": {}, "bulk": {}, "trace": {}}

    sql_exec(engine, "DELETE FROM acl_entries WHERE object_ref IN "
                     "(SELECT 'memory:' || id FROM memories WHERE statement LIKE :p)",
             p=f"{TAG}%")
    sql_exec(engine, "DELETE FROM memories WHERE statement LIKE :p", p=f"{TAG}%")

    # ── setup ─────────────────────────────────────────────────────────────
    fin = create_memory(client, FIN, scope="user", owner_ref=FIN, statement=S_FIN)
    bulk = create_memory(client, FIN, scope="user", owner_ref=FIN, statement=S_FIN_BULK)
    trace = create_memory(client, FIN, scope="user", owner_ref=FIN, statement=S_FIN_TRACE)
    proc = create_memory(client, PROC, scope="user", owner_ref=PROC, statement=S_PROC)
    org = create_memory(client, ADMIN, scope="org", owner_ref=ORGA, statement=S_ORGA)
    out["setup"] = {
        "fin_user_memory": fin, "fin_bulk_candidate": bulk,
        "fin_traceable_memory": trace, "proc_user_memory": proc,
        "org_memory": org,
    }
    for key, res in out["setup"].items():
        if res["status"] != 200:
            print(f"SETUP FAILED: {key} -> {res}", file=sys.stderr)
            return 1
    fin_id = fin["body"]["memory"]["id"]
    trace_id = trace["body"]["memory"]["id"]
    proc_id = proc["body"]["memory"]["id"]
    org_id = org["body"]["memory"]["id"]

    def list_summary(user_ref: str, *, include_inactive: bool = False) -> dict:
        res = list_memory(client, user_ref, include_inactive=include_inactive)
        body = res["body"]
        # NB: the LIST endpoint returns `memories` (plural); the context package
        # uses `memory` (singular). Reading the wrong one yields a silent zero.
        rows = body.get("memories", []) if res["status"] == 200 else []
        return {
            "status": res["status"],
            "count": len(rows),
            "our_statements": sorted(
                r["statement"] for r in rows if r["statement"] in
                (S_FIN, S_FIN_BULK, S_FIN_TRACE, S_PROC, S_ORGA)
            ),
            "raw": res,
        }

    # ── A9.1: GET /memory is caller-visible only ──────────────────────────
    out["list"]["finance_default"] = list_summary(FIN)
    out["list"]["engineering_default"] = list_summary(ENG)
    out["list"]["procurement_default"] = list_summary(PROC)

    # ── A9.2: soft delete by id, and who is allowed to ────────────────────
    #    someone else's memory -> 403, and the row must be untouched
    out["delete"]["other_users_memory_DENY"] = delete_memory(client, FIN, proc_id)
    out["delete"]["proc_row_after_denied_delete"] = {
        "deleted_at": sql_scalar(
            engine, "SELECT deleted_at FROM memories WHERE id = :i", i=proc_id
        ),
    }
    #    the owner's own memory -> 200, soft
    out["delete"]["own_memory_ALLOW"] = delete_memory(client, FIN, fin_id)
    out["delete"]["own_row_after_delete"] = {
        "row_still_exists": sql_scalar(
            engine, "SELECT count(*) FROM memories WHERE id = :i", i=fin_id
        ),
        "deleted_at": str(sql_scalar(
            engine, "SELECT deleted_at FROM memories WHERE id = :i", i=fin_id
        )),
    }
    #    idempotent: deleting again is not an error
    out["delete"]["own_memory_again"] = delete_memory(client, FIN, fin_id)
    #    a nonexistent id -> 404 (not 403: the caller cannot be told whether a
    #    foreign memory exists, and a missing id is indistinguishable from one)
    out["delete"]["nonexistent_id"] = delete_memory(client, FIN, 999_999_999)

    # ── A9.3: bulk delete, with the permission negative ───────────────────
    #    org scope without org write permission -> 403
    out["bulk"]["org_by_plain_user_DENY"] = delete_memory_bulk(client, FIN, "org")
    out["bulk"]["org_rows_after_denied_bulk"] = {
        "live_org_a_memories": sql_scalar(
            engine, "SELECT count(*) FROM memories WHERE owner_ref = :o "
                    "AND scope = 'org' AND deleted_at IS NULL",
            o=ORGA,
        ),
    }
    #    user scope -> deletes only the CALLER's own user memories
    out["bulk"]["user_by_owner_ALLOW"] = delete_memory_bulk(client, FIN, "user")
    out["bulk"]["after_user_bulk"] = {
        "fin_live_user_memories": sql_scalar(
            engine, "SELECT count(*) FROM memories WHERE owner_ref = :o "
                    "AND scope = 'user' AND deleted_at IS NULL", o=FIN,
        ),
        "proc_live_user_memories": sql_scalar(
            engine, "SELECT count(*) FROM memories WHERE owner_ref = :o "
                    "AND scope = 'user' AND deleted_at IS NULL", o=PROC,
        ),
    }
    #    org scope WITH org write permission -> allowed
    out["bulk"]["org_by_admin_ALLOW"] = delete_memory_bulk(client, ADMIN, "org")

    # ── A9.1b: include_inactive widens only the activity guard ────────────
    out["list"]["finance_include_inactive"] = list_summary(FIN, include_inactive=True)
    out["list"]["engineering_include_inactive"] = list_summary(ENG, include_inactive=True)

    # ── A8: traceability ─────────────────────────────────────────────────
    # A fresh memory so it is definitely live at injection time, then one
    # context call, then read back its own trace as its owner.
    trace2 = create_memory(client, FIN, scope="user", owner_ref=FIN,
                           statement=f"{TAG} audit-trail memory")
    trace2_id = trace2["body"]["memory"]["id"]
    ctx = assemble_context(client, FIN)
    out["trace"]["context_call"] = {
        "status": ctx["status"],
        "request_id": ctx["body"].get("request_id"),
        "injected_memory_refs": [m["ref"] for m in ctx["body"].get("memory", [])],
        "our_statements_injected": sorted(
            m["statement"] for m in ctx["body"].get("memory", [])
            if m["statement"] in (S_PROC, S_ORGA, f"{TAG} audit-trail memory")
        ),
        "metadata": ctx["body"].get("metadata", {}),
    }
    request_id = ctx["body"].get("request_id")

    audit = client.get(f"/api/v1/audit/context/{request_id}",
                       headers=hdr(FIN))
    out["trace"]["audit_as_owner"] = {
        "status": audit.status_code,
        "request_id": audit.json().get("request_id") if audit.status_code == 200 else None,
        "memory_items": [
            i for i in (audit.json().get("items", []) if audit.status_code == 200 else [])
            if i.get("item_kind") == "memory"
        ],
    }
    # the trace belongs to its owner: someone else gets 403
    other = client.get(f"/api/v1/audit/context/{request_id}", headers=hdr(ENG))
    out["trace"]["audit_as_other_user"] = {"status": other.status_code}

    # context_items rows, read straight from the audit table
    out["trace"]["context_items_for_request"] = [
        {"seq": r[0], "item_kind": r[1], "ref": r[2], "decision": r[3], "reason": r[4]}
        for r in sql_rows(
            engine,
            "SELECT seq, item_kind, ref, decision, reason FROM context_items "
            "WHERE request_id = :r AND item_kind = 'memory' ORDER BY seq",
            r=str(request_id),
        )
    ]

    # ── A9.4: deletion does NOT erase the audit trail ─────────────────────
    delete_memory(client, FIN, trace2_id)
    out["trace"]["after_delete_row"] = {
        "deleted_at": str(sql_scalar(
            engine, "SELECT deleted_at FROM memories WHERE id = :i", i=trace2_id
        )),
    }
    audit_after = client.get(f"/api/v1/audit/context/{request_id}", headers=hdr(FIN))
    out["trace"]["audit_after_delete"] = {
        "status": audit_after.status_code,
        "memory_items": [
            i for i in (audit_after.json().get("items", [])
                        if audit_after.status_code == 200 else [])
            if i.get("item_kind") == "memory"
        ],
    }
    out["trace"]["context_items_after_delete"] = sql_scalar(
        engine,
        "SELECT count(*) FROM context_items WHERE request_id = :r AND item_kind = 'memory'",
        r=str(request_id),
    )
    # and the deleted memory is gone from injection, but the trace above is not
    after = assemble_context(client, FIN)
    out["trace"]["not_reinjected_after_delete"] = {
        "our_statements_injected": sorted(
            m["statement"] for m in after["body"].get("memory", [])
            if m["statement"] in (f"{TAG} audit-trail memory",)
        ),
    }

    # ── A8: the SPA must be silent ───────────────────────────────────────
    # Recorded here as data; the git-level proof is in step 7's shell companion.
    out["trace"]["spa_check"] = {
        "method": "see evidence/07-audit-provenance.txt (git diff + grep)",
        "expectation": "zero changes under ece/demos/spa/**",
    }

    # ── assertions ────────────────────────────────────────────────────────
    fails: list[str] = []
    L, D, B, T = out["list"], out["delete"], out["bulk"], out["trace"]

    # list: caller-visible only
    if S_PROC in L["finance_default"]["our_statements"]:
        fails.append("A9.1: finance can list procurement's user memory")
    if S_ORGA not in L["finance_default"]["our_statements"]:
        fails.append("A9.1: finance cannot list its own org's memory")
    if S_ORGA in L["engineering_default"]["our_statements"]:
        fails.append("A9.1: engineering (org B) can list org A's memory")
    if S_FIN in L["engineering_default"]["our_statements"]:
        fails.append("A9.1: engineering can list finance's user memory")
    if S_PROC not in L["procurement_default"]["our_statements"]:
        fails.append("A9.1: procurement cannot list its own memory")

    # delete: permission + soft
    if D["other_users_memory_DENY"]["status"] != 403:
        fails.append(f"A9.2: deleting another user's memory returned "
                     f"{D['other_users_memory_DENY']['status']}, expected 403")
    if D["proc_row_after_denied_delete"]["deleted_at"] is not None:
        fails.append("A9.2: a DENIED delete still soft-deleted the row")
    if D["own_memory_ALLOW"]["status"] != 200:
        fails.append("A9.2: the owner could not delete its own memory")
    if D["own_row_after_delete"]["row_still_exists"] != 1:
        fails.append("A9.2: delete removed the row instead of setting deleted_at")
    if D["own_row_after_delete"]["deleted_at"] in ("None", ""):
        fails.append("A9.2: deleted_at was not written")
    if D["own_memory_again"]["status"] != 200:
        fails.append("A9.2: re-deleting an already-deleted memory is not idempotent")
    if D["own_memory_again"]["body"].get("already_deleted") is not True:
        fails.append("A9.2: re-delete did not report already_deleted=true")
    if D["nonexistent_id"]["status"] != 404:
        fails.append(f"A9.2: deleting a nonexistent id returned "
                     f"{D['nonexistent_id']['status']}, expected 404")

    # bulk: the permission negative is the point
    if B["org_by_plain_user_DENY"]["status"] != 403:
        fails.append(f"A9.3: bulk org delete by a plain user returned "
                     f"{B['org_by_plain_user_DENY']['status']}, expected 403")
    if B["org_rows_after_denied_bulk"]["live_org_a_memories"] < 1:
        fails.append("A9.3: the denied bulk delete still deleted org memories")
    if B["after_user_bulk"]["fin_live_user_memories"] != 0:
        fails.append("A9.3: bulk user delete left the caller's own memories live")
    if B["after_user_bulk"]["proc_live_user_memories"] < 1:
        fails.append("A9.3: bulk user delete reached ANOTHER user's memories")
    if B["org_by_admin_ALLOW"]["status"] != 200:
        fails.append(f"A9.3: bulk org delete by an org_admin returned "
                     f"{B['org_by_admin_ALLOW']['status']}")

    # include_inactive: widens only the caller's OWN inactive rows
    if S_FIN not in L["finance_include_inactive"]["our_statements"]:
        fails.append("A9.1b: include_inactive did not return finance's own deleted memory")
    if S_FIN in L["engineering_include_inactive"]["our_statements"]:
        fails.append("A9.1b: include_inactive leaked finance's memory to engineering")

    # traceability
    if ctx["status"] != 200:
        fails.append("A8: the audited /context call failed")
    if f"{TAG} audit-trail memory" not in T["context_call"]["our_statements_injected"]:
        fails.append("A8: the memory under audit was not injected")
    if T["audit_as_owner"]["status"] != 200:
        fails.append(f"A8: owner could not read its own trace "
                     f"({T['audit_as_owner']['status']})")
    if not T["context_items_for_request"]:
        fails.append("A8: no item_kind='memory' rows in context_items")
    for item in T["context_items_for_request"]:
        if item["decision"] != "allowed":
            fails.append(f"A8: memory audit row has decision={item['decision']}")
        if item["reason"] == "":
            fails.append("A8: memory audit row has an empty reason")
    if T["audit_as_other_user"]["status"] != 403:
        fails.append(f"A8: another user read someone else's trace "
                     f"({T['audit_as_other_user']['status']})")

    # audit survives deletion
    if T["context_items_after_delete"] != len(T["context_items_for_request"]):
        fails.append("A9.4: deleting the memory removed its audit history")
    if not T["audit_after_delete"]["memory_items"]:
        fails.append("A9.4: the trace no longer shows the memory after deletion")
    if T["not_reinjected_after_delete"]["our_statements_injected"]:
        fails.append("A9.4: a deleted memory was injected again")

    # the statement is never the thing being audited — the REF is
    for item in T["context_items_for_request"]:
        if item["ref"] != f"memory:{trace2_id}":
            fails.append(f"A8: memory audit ref is {item['ref']!r}, expected memory:{trace2_id}")
        if "audit-trail memory" in item["reason"]:
            fails.append("A8: the audit reason contains the memory STATEMENT")

    out["assertions_checked"] = [
        "GET /memory returns only the caller's user memory + its own org memory",
        "another user's memory is not listable",
        "deleting another user's memory is 403 and leaves the row untouched",
        "the owner's delete is a soft delete (row kept, deleted_at set)",
        "re-deleting is idempotent",
        "bulk org delete without org write permission is 403 and deletes nothing",
        "bulk user delete removes only the caller's own user memories",
        "bulk org delete by an org_admin succeeds",
        "include_inactive returns the caller's own inactive memories only",
        "an injected memory appears in context_items with item_kind='memory'",
        "the owner can read its own /audit/context/{request_id} trace; others get 403",
        "the audit ref is the memory ref, never the statement text",
        "soft-deleting the memory does NOT remove its audit history",
        "a deleted memory is not injected again",
    ]
    out["failures"] = fails
    out["verdict"] = "FAIL" if fails else "PASS"

    # A8 (provenance/no-UI) and A9 (compliance deletion) are separate acceptance
    # items, so they get separate evidence files. Both come out of this one run
    # — they share the setup (the audited request must exist before it can be
    # deleted), and re-deriving one of them in a second script would mean two
    # slightly different fixture states in the same evidence set.
    a8_fails = [f for f in fails if f.startswith("A8")]
    a9_fails = [f for f in fails if f.startswith("A9")]
    provenance = {
        "what_this_proves": (
            "A8: an injected persistent memory is traceable — it appears in "
            "context_items (item_kind='memory') and in "
            "GET /api/v1/audit/context/{request_id} for the request's owner — "
            "while remaining absent from every user-facing surface."
        ),
        "trace": out["trace"],
        "assertions_checked": [a for a in out["assertions_checked"] if "audit" in a
                               or "injected memory appears" in a],
        "failures": a8_fails,
        "verdict": "FAIL" if a8_fails else "PASS",
    }
    out["a8_provenance_evidence_file"] = "evidence/07-audit-provenance.json"
    out["a9_failures"] = a9_fails

    (Path(__file__).resolve().parent.parent / "evidence" /
     "07-audit-provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

    for f in fails:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        "PASS — Step 7 (A8/A9): listing is caller-scoped; deletes are soft and "
        "permission-checked (with 403 negatives that delete nothing); an "
        "injected memory is traceable via context_items and the audit endpoint "
        "even after deletion."
        if not fails else f"FAIL — Step 7 (A8/A9): {len(fails)} assertion(s) failed",
        file=sys.stderr,
    )

    dump(out)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
