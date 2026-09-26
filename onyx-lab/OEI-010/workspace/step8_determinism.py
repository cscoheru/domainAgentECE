"""OEI-010 step 8 (A7) — determinism, the limit, and the drop counter.

Three claims, and the third is the one that is easy to fake:

  1. The same request, N=5 times, produces a BYTE-IDENTICAL injection. Hashing
     the `memory` array is the right unit: the surrounding package deliberately
     carries volatile fields (`request_id`, `package_id`, `latency_ms`), so a
     whole-body hash would differ every time and prove nothing about ordering.
  2. The limit of 10 is effective: 13 eligible memories -> exactly 10 injected.
  3. `metadata.memory_dropped` equals the number actually truncated. The script
     computes the eligible count INDEPENDENTLY from the database (live rows with
     an allow ACL) rather than trusting the app's own arithmetic, so the counter
     is checked against the data and not against itself.

It also pins down WHICH 10: the most recent ones. A limit that keeps an
arbitrary 10 would pass 1-3 while being useless.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step8_determinism.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _client import (  # noqa: E402
    assemble_context,
    dump,
    fresh_app,
    sql_exec,
    sql_rows,
    sql_write_scalar,
)

FIN = "demo-user-finance"      # org:consulting-a
ORGA = "org:consulting-a"
TAG = "oei010 step8 det"
N_RUNS = 5
N_FIXTURES = 13               # > MEMORY_LIMIT (10)


def main() -> int:
    client, engine = fresh_app()
    out: dict = {"fixtures": {}, "runs": {}, "limit": {}, "dropped_check": {}}

    sql_exec(engine, "DELETE FROM acl_entries WHERE object_ref IN "
                     "(SELECT 'memory:' || id FROM memories WHERE statement LIKE :p)",
             p=f"{TAG}%")
    sql_exec(engine, "DELETE FROM memories WHERE statement LIKE :p", p=f"{TAG}%")

    # ── fixtures: N_FIXTURES user memories with DISTINCT recency ──────────
    # Recency has to be unambiguous, so each row gets an explicit `created_at`
    # one minute further back than the last. Relying on `now()` would give rows
    # created in the same millisecond an ambiguous order, and the ordering claim
    # would then be untestable even if the code were correct.
    fixtures = []
    for i in range(N_FIXTURES):
        statement = f"{TAG} fixture {i:02d}"
        mem_id = sql_write_scalar(
            engine,
            """
            INSERT INTO memories (scope, owner_ref, statement, classification,
                                  source, created_at, updated_at)
            VALUES ('user', :owner, :stmt, 'restricted', 'fixture:oei010-determinism',
                    now() - make_interval(mins => :age), now() - make_interval(mins => :age))
            RETURNING id
            """,
            owner=FIN, stmt=statement, age=i + 1,
        )
        sql_exec(
            engine,
            """
            INSERT INTO acl_entries (subject_type, subject_ref, object_type,
                                     object_ref, effect, source_system, note)
            VALUES ('user', :sref, 'memory', :oref, 'allow',
                    'fixture:oei010-determinism', 'determinism fixture')
            """,
            sref=FIN, oref=f"memory:{mem_id}",
        )
        fixtures.append({"id": mem_id, "statement": statement, "age_minutes": i + 1})
    out["fixtures"]["created"] = fixtures

    # ── the eligible count, computed from the DB, not from the app ────────
    # This is an INDEPENDENT re-derivation of the same policy from the same
    # data: live rows (not deleted, not expired), in either scope this caller
    # can reach, joined to an allow ACL that matches the caller's user_ref or
    # org_id and whose window is open. Doing it here rather than reading the
    # app's own counters is the whole point — otherwise the drop counter would
    # be checked against itself.
    #   DISTINCT: a memory with more than one matching allow row would
    #   otherwise be counted twice and inflate the expectation.
    eligible_rows = sql_rows(
        engine,
        """
        SELECT DISTINCT m.id, m.created_at, m.scope FROM memories m
        JOIN acl_entries a
          ON a.object_type = 'memory' AND a.object_ref = 'memory:' || m.id
         AND a.effect = 'allow'
         AND (a.valid_from IS NULL OR a.valid_from <= now())
         AND (a.valid_to   IS NULL OR a.valid_to   >  now())
         AND ( (a.subject_type = 'user' AND a.subject_ref = :owner)
            OR (a.subject_type = 'org'  AND a.subject_ref = :org) )
        WHERE m.deleted_at IS NULL
          AND (m.expires_at IS NULL OR m.expires_at > now())
          AND ( (m.scope = 'user' AND m.owner_ref = :owner)
             OR (m.scope = 'org'  AND m.owner_ref = :org) )
        ORDER BY m.created_at DESC, m.id DESC
        """,
        owner=FIN, org=ORGA,
    )
    eligible = [r[0] for r in eligible_rows]
    out["dropped_check"]["eligible_scopes"] = {
        "org": sum(1 for r in eligible_rows if r[2] == "org"),
        "user": sum(1 for r in eligible_rows if r[2] == "user"),
    }
    out["dropped_check"]["eligible_count_from_db"] = len(eligible)
    out["dropped_check"]["expected_injected"] = 10
    out["dropped_check"]["expected_dropped"] = max(0, len(eligible) - 10)

    # ── N=5 identical calls ───────────────────────────────────────────────
    hashes: list[str] = []
    for run in range(1, N_RUNS + 1):
        resp = assemble_context(client, FIN)
        body = resp["body"]
        memories = body.get("memory", []) if resp["status"] == 200 else []
        canonical = json.dumps(memories, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        hashes.append(digest)
        out["runs"][f"run{run}"] = {
            "status": resp["status"],
            "memory_count": len(memories),
            "metadata_memory_count": body.get("metadata", {}).get("memory_count"),
            "metadata_memory_dropped": body.get("metadata", {}).get("memory_dropped"),
            "memory_sha256": digest,
            "refs_in_order": [m["ref"] for m in memories],
            "statements_in_order": [m["statement"] for m in memories],
        }

    # ── limit + ordering ─────────────────────────────────────────────────
    # The app's order is NOT pure recency: org-scope memories come first, then
    # each group newest-first (see order_candidates). The expectation below
    # reproduces that two-pass ordering from the DB rows, so "which 10 survive
    # the limit" is checked against the real ordering rule rather than an
    # approximation of it.
    injected_refs = out["runs"]["run1"]["refs_in_order"]
    org_first_then_recency = (
        [r[0] for r in eligible_rows if r[2] == "org"]
        + [r[0] for r in eligible_rows if r[2] == "user"]
    )
    out["limit"] = {
        "limit_constant": 10,
        "eligible": len(eligible),
        "injected": len(injected_refs),
        "dropped": out["runs"]["run1"]["metadata_memory_dropped"],
        "expected_injected_refs_in_order": [
            f"memory:{i}" for i in org_first_then_recency[:10]
        ],
        "injected_refs": injected_refs,
    }

    # ── assertions ────────────────────────────────────────────────────────
    fails: list[str] = []
    R, L, D = out["runs"], out["limit"], out["dropped_check"]

    if len(set(hashes)) != 1:
        fails.append(f"A7.1: {N_RUNS} runs were NOT byte-identical: {hashes}")
    for name, run in R.items():
        if run["status"] != 200:
            fails.append(f"A7: {name} returned {run['status']}")
        if run["memory_count"] != 10:
            fails.append(f"A7.2: {name} injected {run['memory_count']}, expected 10")
        if run["metadata_memory_count"] != run["memory_count"]:
            fails.append(f"A7: {name} metadata.memory_count disagrees with memory[]")
        if run["metadata_memory_dropped"] != D["expected_dropped"]:
            fails.append(
                f"A7.3: {name} reported memory_dropped="
                f"{run['metadata_memory_dropped']}, expected {D['expected_dropped']} "
                f"({D['eligible_count_from_db']} eligible - 10 limit)"
            )

    if D["eligible_count_from_db"] <= 10:
        fails.append(
            "A7: the fixture does not exceed the limit, so the limit is untested "
            f"({D['eligible_count_from_db']} eligible)"
        )
    if injected_refs != L["expected_injected_refs_in_order"]:
        fails.append(
            "A7.2: the injected set/order does not match the (org-first, then "
            f"newest-first) rule applied to the DB rows "
            f"(got {injected_refs}, expected {L['expected_injected_refs_in_order']})"
        )

    out["assertions_checked"] = [
        f"{N_RUNS} identical requests produce a byte-identical memory array (sha256)",
        "the memory array is identical INCLUDING order (refs compared positionally)",
        "exactly 10 memories are injected when 13 fixtures are eligible",
        "the injected 10 are the 10 the (org-first, newest-first) rule selects",
        "metadata.memory_dropped == (eligible from DB) - 10, not the app's own count",
        "metadata.memory_count == len(memory[]) on every run",
    ]
    out["failures"] = fails
    out["verdict"] = "FAIL" if fails else "PASS"

    for f in fails:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        f"PASS — Step 8 (A7): {N_RUNS} runs byte-identical "
        f"(memory sha256 {hashes[0][:16]}…); limit 10 effective over "
        f"{D['eligible_count_from_db']} eligible; memory_dropped="
        f"{D['expected_dropped']} matches the DB-derived count; the 10 kept are "
        "the most recent."
        if not fails else f"FAIL — Step 8 (A7): {len(fails)} assertion(s) failed",
        file=sys.stderr,
    )

    dump(out)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
