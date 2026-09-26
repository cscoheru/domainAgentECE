"""OEI-010 step 5 (A5) — memory READ happens after permission, per row.

One identical `POST /api/v1/context` (same intent, same root entity) is issued
as five different callers. The memory set must differ per caller — and differ in
exactly the ways the scope model says, with no leakage:

  caller                     user scope          org scope
  -------------------------  ------------------  ------------------------
  demo-user-finance (org A)  its own memory      org A memory
  demo-user-engineering (B)  -                   org B memory only
  demo-user-procurement (A)  its own memory      org A memory
  probe with no org          -                   -
  unknown user               -                   -

Leak assertions are substring checks on the WHOLE serialised response, not just
on `memory[]`: a forbidden statement must not appear anywhere — not in
`documents`, not in `sources`, not in an error string. That is what "完全看不到"
has to mean, and checking only the obvious array would not establish it.

Fixture note: org-B's memory is inserted with SQL, not through the API. That is
not a shortcut around the write path — it is a consequence of it. Candidate A
grants `org_admin` write on an org's scope, and gate 1 requires the writer's OWN
`org_id` to equal `owner_ref`, so writing org-B's memory needs an `org_admin`
who BELONGS to org B. The seed has none (only `demo-user-admin`, who is in org
A). Rather than widen the policy for the sake of a test, the read-path fixture is
written directly and the gap is reported.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step5_read_matrix.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _client import (  # noqa: E402
    assemble_context,
    create_memory,
    dump,
    fresh_app,
    sql_exec,
    sql_scalar,
    sql_write_scalar,
)

FIN = "demo-user-finance"           # org:consulting-a
PROC = "demo-user-procurement"      # org:consulting-a
ENG = "demo-user-engineering"       # org:consulting-b
NO_ORG = "oei010-probe-no-org"
UNKNOWN = "oei010-probe-unknown-user"

TAG = "oei010 step5 probe"
S_FIN = f"{TAG} finance-only preference"
S_PROC = f"{TAG} procurement-only preference"
S_ORGA = f"{TAG} org-a canonical terminology"
S_ORGB = f"{TAG} org-b canonical terminology"

ALL_STATEMENTS = (S_FIN, S_PROC, S_ORGA, S_ORGB)


def main() -> int:
    client, engine = fresh_app()

    # Reset only this probe's own rows (precise predicate, never a table sweep).
    sql_exec(engine, "DELETE FROM acl_entries WHERE object_ref IN "
                     "(SELECT 'memory:' || id FROM memories WHERE statement LIKE :p)",
             p=f"{TAG}%")
    sql_exec(engine, "DELETE FROM memories WHERE statement LIKE :p", p=f"{TAG}%")

    out: dict = {"setup": {}, "callers": {}, "probes": {}}

    # ── three memories through the real API ────────────────────────────────
    out["setup"]["fin_user_scope"] = create_memory(
        client, FIN, scope="user", owner_ref=FIN, statement=S_FIN
    )
    out["setup"]["proc_user_scope"] = create_memory(
        client, PROC, scope="user", owner_ref=PROC, statement=S_PROC
    )
    out["setup"]["org_a_scope"] = create_memory(
        client, "demo-user-admin", scope="org", owner_ref="org:consulting-a",
        statement=S_ORGA,
    )

    # ── org-B memory: direct fixture (see module docstring for why) ────────
    org_b_id = sql_write_scalar(
        engine,
        """
        INSERT INTO memories (scope, owner_ref, statement, classification, source, source_ref)
        VALUES ('org', 'org:consulting-b', :s, 'restricted', 'fixture:oei010-read-matrix',
                'read-path fixture — no seeded org_admin exists in org B')
        ON CONFLICT ON CONSTRAINT uq_memories_scope_owner_ref_statement DO NOTHING
        RETURNING id
        """,
        s=S_ORGB,
    )
    if org_b_id is None:
        org_b_id = sql_scalar(
            engine, "SELECT id FROM memories WHERE statement = :s", s=S_ORGB
        )
    sql_exec(
        engine,
        """
        INSERT INTO acl_entries (subject_type, subject_ref, object_type, object_ref,
                                 effect, source_system, note)
        VALUES ('org', 'org:consulting-b', 'memory', :oref, 'allow',
                'fixture:oei010-read-matrix', 'read-path fixture')
        ON CONFLICT DO NOTHING
        """,
        oref=f"memory:{org_b_id}",
    )
    out["setup"]["org_b_scope_fixture"] = {
        "memory_id": org_b_id,
        "acl_object_ref": f"memory:{org_b_id}",
        "via": "SQL fixture (no seeded org_admin belongs to org B)",
    }

    for key in ("fin_user_scope", "proc_user_scope", "org_a_scope"):
        if out["setup"][key]["status"] != 200:
            print(f"SETUP FAILED: {key} -> {out['setup'][key]}")
            return 1

    # ── caller -> org, resolved the same way the app does ─────────────────
    for label, caller in (
        ("finance_org_a", FIN),
        ("engineering_org_b", ENG),
        ("procurement_org_a", PROC),
        ("probe_no_org", NO_ORG),
        ("unknown_user", UNKNOWN),
    ):
        out["callers"][label] = {
            "user_ref": caller,
            "resolved_org_id": sql_scalar(
                engine,
                "SELECT attributes->>'org_id' FROM entities "
                "WHERE entity_type='person' AND source_id = :s",
                s=caller,
            ),
        }

    # ── the five probes ───────────────────────────────────────────────────
    for label in out["callers"]:
        caller = out["callers"][label]["user_ref"]
        resp = assemble_context(client, caller)
        body = resp["body"]
        memories = body.get("memory", []) if resp["status"] == 200 else []
        whole_body = json.dumps(body, ensure_ascii=False)
        seen = {m["statement"] for m in memories}
        out["probes"][label] = {
            "caller": caller,
            "caller_org_id": out["callers"][label]["resolved_org_id"],
            "status": resp["status"],
            "memory_count": len(memories),
            "metadata_memory_count": body.get("metadata", {}).get("memory_count"),
            "metadata_memory_dropped": body.get("metadata", {}).get("memory_dropped"),
            "memory": [
                {"ref": m["ref"], "scope": m["scope"], "statement": m["statement"]}
                for m in memories
            ],
            "memory_sources": [
                s for s in body.get("sources", []) if s.get("system") == "ece:memory"
            ],
            # THE leak check: which forbidden statements appear ANYWHERE in the
            # serialised response (not just in `memory[]`). Must always be [].
            "forbidden_statement_hits_anywhere": [
                s for s in ALL_STATEMENTS if s not in seen and s in whole_body
            ],
            "response_sha256": hashlib.sha256(
                json.dumps(body, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest(),
        }

    # ── assertions ────────────────────────────────────────────────────────
    #
    # Membership, not set equality. The database already holds memories from
    # earlier steps (step 4's own probe rows, legitimately still active), so an
    # exact-set assertion would fail for a reason that has nothing to do with
    # this cut's behaviour. What A5 actually claims is entitlement:
    #
    #   own user scope   -> present
    #   own org scope    -> present
    #   another user's   -> absent
    #   another org's    -> absent
    #
    # and, separately, that a non-entitled statement appears NOWHERE in the
    # response — which is the stronger, non-negotiable half.
    p = out["probes"]
    fails: list[str] = []

    def statements(label: str) -> set[str]:
        return {m["statement"] for m in p[label]["memory"]}

    ENTITLED = {
        "finance_org_a": {S_FIN, S_ORGA},
        "procurement_org_a": {S_PROC, S_ORGA},
        "engineering_org_b": {S_ORGB},
        "probe_no_org": set(),
        "unknown_user": set(),
    }
    FORBIDDEN = {
        "finance_org_a": {S_PROC, S_ORGB},
        "procurement_org_a": {S_FIN, S_ORGB},
        "engineering_org_b": {S_FIN, S_PROC, S_ORGA},
        "probe_no_org": {S_FIN, S_PROC, S_ORGA, S_ORGB},
        "unknown_user": {S_FIN, S_PROC, S_ORGA, S_ORGB},
    }

    for label in p:
        if p[label]["status"] != 200:
            fails.append(f"{label}: /context returned {p[label]['status']}")
            continue

        got = statements(label)
        missing = ENTITLED[label] - got
        if missing:
            fails.append(f"{label}: entitled memory NOT injected: {missing}")

        leaked = FORBIDDEN[label] & got
        if leaked:
            fails.append(f"{label}: NOT entitled but injected anyway: {leaked}")

        # the stronger half: not in `memory[]` AND not anywhere else either
        hits = p[label]["forbidden_statement_hits_anywhere"]
        if hits:
            fails.append(f"{label}: statement text leaked into the response: {hits}")

        # metadata agrees with the array it describes
        if p[label]["metadata_memory_count"] != p[label]["memory_count"]:
            fails.append(
                f"{label}: metadata.memory_count != len(memory) "
                f"({p[label]['metadata_memory_count']} vs {p[label]['memory_count']})"
            )

        # every injected memory carries a provenance source entry (A8 relies on this)
        sourced = {s["record_id"] for s in p[label]["memory_sources"]}
        if sourced != {m["ref"] for m in p[label]["memory"]}:
            fails.append(
                f"{label}: memory[] and sources[] disagree "
                f"({sorted(sourced)} vs {sorted(m['ref'] for m in p[label]['memory'])})"
            )

        # deterministic order: org scope first, then most recent (A7)
        scopes = [m["scope"] for m in p[label]["memory"]]
        if scopes != sorted(scopes, key=lambda s: s != "org"):
            fails.append(f"{label}: org scope did not sort first ({scopes})")

    # the two org-A callers share the org memory but not each other's user memory
    if S_ORGA not in statements("finance_org_a") or S_ORGA not in statements("procurement_org_a"):
        fails.append("org memory is not shared across the two org-A callers")
    if S_FIN in statements("procurement_org_a"):
        fails.append("finance's user memory is visible to procurement (same org)")

    # different orgs -> different memory sets
    if statements("finance_org_a") & statements("engineering_org_b"):
        fails.append("two different orgs share a memory set")

    # the two org-less callers, in different ways, both see nothing
    if statements("probe_no_org") or statements("unknown_user"):
        fails.append("an org-less/unknown caller saw memory")

    out["assertions_checked"] = [
        "entitled memory present for every caller",
        "non-entitled memory absent from memory[] for every caller",
        "non-entitled statement text absent from the ENTIRE response body",
        "metadata.memory_count == len(memory[])",
        "sources[] carries exactly the injected memory refs",
        "org scope sorts before user scope",
        "org memory shared between the two org-A callers",
        "user memory NOT shared between the two org-A callers",
        "different orgs yield disjoint memory sets",
        "org-less and unknown callers see no memory at all",
    ]
    out["failures"] = fails
    out["verdict"] = "FAIL" if fails else "PASS"

    # stdout stays pure JSON (the evidence file must parse); the human summary
    # goes to stderr so `python step5.py > 05.json` yields a loadable document.
    for f in fails:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        "PASS — Step 5 (A5): one query, 5 callers, per-scope memory sets; "
        "org-A memory invisible to org-B / no-org / unknown callers "
        "(substring-checked against the entire response); org scope sorts first."
        if not fails else f"FAIL — Step 5 (A5): {len(fails)} assertion(s) failed",
        file=sys.stderr,
    )

    dump(out)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
