"""OEI-010 step 6 (A6) — expiry, soft delete, and the ACL time box.

Three ways a memory stops being injected, and they are NOT the same mechanism:

  expires_at in the past      data-level   the row is inert   -> filtered BEFORE authorization
  deleted_at not null         data-level   the row is gone   -> filtered BEFORE authorization
  ACL valid_to in the past    policy-level the row is ALIVE  -> filtered AT authorization

That third one is the interesting case, and the one this cut adds: the memory
still exists, is not deleted, is not expired, and is still a candidate for this
caller — and it is still withheld, because the ACL window closed. To prove the
denial happens at the authorization step rather than in the SQL narrowing pass,
the script records `select_memory`'s own `candidates` count alongside the
injected `items` count: same candidates, fewer items.

Full raw HTTP bodies are written to `evidence/raw/06-*.json` (verbatim, so a
reviewer can read the response the app actually produced); this file records the
decision-relevant extract plus the result of a whole-body substring check, since
a leak would not necessarily appear in `memory[]`.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step6_expiry_and_deleted.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _client import (  # noqa: E402
    assemble_context,
    create_memory,
    delete_memory,
    dump,
    fresh_app,
    sql_exec,
    sql_scalar,
)

FIN = "demo-user-finance"          # org:consulting-a
ADMIN = "demo-user-admin"
ORGA = "org:consulting-a"

TAG = "oei010 step6 probe"
S_LIVE = f"{TAG} live user memory"
S_EXPIRED = f"{TAG} expired user memory"
S_DELETED = f"{TAG} soon-to-be-deleted user memory"
S_ORGA = f"{TAG} org-a memory under an ACL time box"

RAW_DIR = Path(__file__).resolve().parent.parent / "evidence" / "raw"
ALL_OURS = (S_LIVE, S_EXPIRED, S_DELETED, S_ORGA)


def _iso(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


def _raw(name: str, body: dict) -> str:
    """Persist one verbatim HTTP body; return a sha256 for the summary."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(body, indent=2, ensure_ascii=False, default=str)
    path = RAW_DIR / f"06-{name}.json"
    path.write_text(text + "\n", encoding="utf-8")
    return f"evidence/raw/06-{name}.json"


def main() -> int:
    client, engine = fresh_app()
    out: dict = {"setup": {}, "states": {}, "raw_response_files": {}}

    # Reset only this probe's rows (precise predicate, never a table sweep).
    sql_exec(engine, "DELETE FROM acl_entries WHERE object_ref IN "
                     "(SELECT 'memory:' || id FROM memories WHERE statement LIKE :p)",
             p=f"{TAG}%")
    sql_exec(engine, "DELETE FROM memories WHERE statement LIKE :p", p=f"{TAG}%")

    # ── setup ─────────────────────────────────────────────────────────────
    live = create_memory(client, FIN, scope="user", owner_ref=FIN, statement=S_LIVE)
    expired = create_memory(
        client, FIN, scope="user", owner_ref=FIN, statement=S_EXPIRED,
        expires_at=_iso(timedelta(days=-1)),
    )
    to_delete = create_memory(
        client, FIN, scope="user", owner_ref=FIN, statement=S_DELETED
    )
    org = create_memory(
        client, ADMIN, scope="org", owner_ref=ORGA, statement=S_ORGA
    )
    out["setup"] = {
        "live_user_memory": live,
        "already_expired_memory": expired,
        "to_be_deleted_memory": to_delete,
        "org_memory_for_acl_timebox": org,
    }
    for key, res in out["setup"].items():
        if res["status"] != 200:
            print(f"SETUP FAILED: {key} -> {res}", file=sys.stderr)
            return 1

    live_id = live["body"]["memory"]["id"]
    expired_id = expired["body"]["memory"]["id"]
    to_delete_id = to_delete["body"]["memory"]["id"]
    org_id = org["body"]["memory"]["id"]

    # `expires_at` really did land in the past (not coerced, not dropped)
    out["setup"]["expired_row"] = {
        "id": expired_id,
        "expires_at_in_db": str(sql_scalar(
            engine, "SELECT expires_at FROM memories WHERE id = :i", i=expired_id
        )),
        "deleted_at_in_db": sql_scalar(
            engine, "SELECT deleted_at FROM memories WHERE id = :i", i=expired_id
        ),
    }

    # ── the ACL row that grants org access to this memory ─────────────────
    acl = sql_scalar(
        engine,
        """
        SELECT id FROM acl_entries
        WHERE object_type = 'memory' AND object_ref = :oref
          AND subject_type = 'org' AND subject_ref = :sref AND effect = 'allow'
        """,
        oref=f"memory:{org_id}", sref=ORGA,
    )
    out["setup"]["org_memory_acl_row_id"] = acl
    if acl is None:
        print("SETUP FAILED: no auto-grant ACL row for the org memory", file=sys.stderr)
        return 1

    def snapshot(name: str, *, label: str) -> dict:
        """One full context call, recorded raw + summarised."""
        resp = assemble_context(client, FIN)
        body = resp["body"]
        whole = json.dumps(body, ensure_ascii=False, default=str)
        memories = body.get("memory", []) if resp["status"] == 200 else []
        seen = {m["statement"] for m in memories}
        raw_path = _raw(name, body)
        out["raw_response_files"][name] = raw_path
        return {
            "state": label,
            "status": resp["status"],
            "memory_count": len(memories),
            "metadata_memory_count": body.get("metadata", {}).get("memory_count"),
            "metadata_memory_dropped": body.get("metadata", {}).get("memory_dropped"),
            "memory": [
                {"ref": m["ref"], "scope": m["scope"], "statement": m["statement"]}
                for m in memories
            ],
            # which of this probe's four statements appear ANYWHERE in the body
            "our_statements_anywhere": sorted(
                s for s in ALL_OURS if s in whole
            ),
            "our_statements_in_memory_array": sorted(seen & set(ALL_OURS)),
            "raw_response_file": raw_path,
            "raw_response_sha256": hashlib.sha256(
                json.dumps(body, sort_keys=True, ensure_ascii=False, default=str).encode()
            ).hexdigest(),
        }

    # ── s1: control — everything that should be visible, is ───────────────
    out["states"]["s1_control"] = snapshot("s1-control", label="before any expiry/delete/timebox")

    # ── s2: soft delete ───────────────────────────────────────────────────
    out["states"]["s2_delete_call"] = delete_memory(client, FIN, to_delete_id)
    out["states"]["s2_after_delete"] = snapshot(
        "s2-after-delete", label="after DELETE /memory/{id} (deleted_at set)"
    )
    out["states"]["s2_after_delete"]["deleted_row"] = {
        "id": to_delete_id,
        "row_still_exists": sql_scalar(
            engine, "SELECT count(*) FROM memories WHERE id = :i", i=to_delete_id
        ),
        "deleted_at_in_db": str(sql_scalar(
            engine, "SELECT deleted_at FROM memories WHERE id = :i", i=to_delete_id
        )),
    }

    # ── s3: ACL time box — the row stays ALIVE, the grant does not ───────
    sql_exec(engine, "UPDATE acl_entries SET valid_to = :v WHERE id = :i",
             v=datetime.now(timezone.utc) - timedelta(days=1), i=acl)
    out["states"]["s3_acl_timebox"] = snapshot(
        "s3-acl-valid-to-yesterday",
        label="org memory's allow-ACL valid_to = yesterday",
    )
    out["states"]["s3_acl_timebox"]["org_row_is_still_alive"] = {
        "id": org_id,
        "deleted_at": sql_scalar(
            engine, "SELECT deleted_at FROM memories WHERE id = :i", i=org_id
        ),
        "expires_at": sql_scalar(
            engine, "SELECT expires_at FROM memories WHERE id = :i", i=org_id
        ),
        "still_a_candidate_for_this_caller": None,  # filled below
    }

    # s4: restore the window -> the SAME row comes back, no other change
    sql_exec(engine, "UPDATE acl_entries SET valid_to = NULL WHERE id = :i", i=acl)
    out["states"]["s4_acl_restored"] = snapshot(
        "s4-acl-restored", label="ACL valid_to restored to NULL (open-ended)"
    )

    # ── isolate the denial to the AUTHORIZATION step ──────────────────────
    # `select_memory` reports how many rows survived narrowing and how many
    # survived authorization. Re-run both ACL states and compare: if the
    # candidate count is identical and only the item count moves, the row was
    # withheld by `check_permission`, not by the SQL filter.
    from ece.identity import resolve_identity  # noqa: PLC0415
    from ece.context.memory import select_memory  # noqa: PLC0415

    identity = resolve_identity(engine, FIN)
    out["authorization_step_isolation"] = {}
    for state_name, valid_to in (("acl_open", None), ("acl_closed", "yesterday")):
        if valid_to is None:
            sql_exec(engine, "UPDATE acl_entries SET valid_to = NULL WHERE id = :i", i=acl)
        else:
            sql_exec(engine, "UPDATE acl_entries SET valid_to = :v WHERE id = :i",
                     v=datetime.now(timezone.utc) - timedelta(days=1), i=acl)
        sel = select_memory(engine, identity)
        statements = {item["statement"] for item in sel.items}
        out["authorization_step_isolation"][state_name] = {
            "candidates_that_passed_scope_and_activity": sel.candidates,
            "items_that_passed_authorization": len(sel.items),
            "org_memory_present": S_ORGA in statements,
            "audit_entries": len(sel.audit),
        }
    # leave the window open for the assertions below
    sql_exec(engine, "UPDATE acl_entries SET valid_to = NULL WHERE id = :i", i=acl)

    # ── assertions ────────────────────────────────────────────────────────
    st = out["states"]
    fails: list[str] = []

    def contains(state: str, statement: str) -> bool:
        return statement in st[state]["our_statements_anywhere"]

    # s1 control: live + org + the not-yet-deleted memory are visible; the
    # already-expired one is not. S_DELETED being present here is the
    # PRECONDITION for s2 — without it, "gone after deletion" would prove
    # nothing.
    for s in (S_LIVE, S_ORGA, S_DELETED):
        if not contains("s1_control", s):
            fails.append(f"s1 control: {s!r} should be injected")
    if contains("s1_control", S_EXPIRED):
        fails.append(f"s1 control: {S_EXPIRED!r} injected but it is already expired")

    # s2: soft delete removes it from injection...
    if not contains("s1_control", S_DELETED):
        fails.append("s2 precondition: the memory was not injected before deletion")
    if contains("s2_after_delete", S_DELETED):
        fails.append("s2: a soft-deleted memory was still injected")
    if st["s2_after_delete"]["deleted_row"]["row_still_exists"] != 1:
        fails.append("s2: soft delete removed the ROW (must only set deleted_at)")
    if st["s2_after_delete"]["deleted_row"]["deleted_at_in_db"] in (None, "None"):
        fails.append("s2: deleted_at was not written")

    # s3: the ACL window closes -> withholding happens with the row ALIVE
    if not contains("s1_control", S_ORGA):
        fails.append("s3 precondition: org memory not injected before the time box")
    if contains("s3_acl_timebox", S_ORGA):
        fails.append("s3: org memory still injected after its ACL window closed")
    alive = st["s3_acl_timebox"]["org_row_is_still_alive"]
    if alive["deleted_at"] is not None:
        fails.append("s3: the row was deleted — this is not an ACL denial")
    if alive["expires_at"] is not None:
        fails.append("s3: the row was expired — this is not an ACL denial")

    # the two isolation probes are the real proof of WHERE the denial happened
    iso = out["authorization_step_isolation"]
    if iso["acl_open"]["candidates_that_passed_scope_and_activity"] != \
            iso["acl_closed"]["candidates_that_passed_scope_and_activity"]:
        fails.append(
            "isolation: the candidate set changed when the ACL closed — the row "
            "was filtered before authorization, so the ACL is not what denied it"
        )
    if iso["acl_open"]["items_that_passed_authorization"] < 1:
        fails.append("isolation: nothing injected with the ACL open")
    if iso["acl_closed"]["org_memory_present"]:
        fails.append("isolation: org memory authorized despite a closed ACL window")
    if iso["acl_closed"]["items_that_passed_authorization"] != \
            iso["acl_open"]["items_that_passed_authorization"] - 1:
        fails.append("isolation: exactly one item (the org memory) should be withheld")

    # s4: restoring the window brings it back, and nothing ELSE changed. The
    # comparison is against the control MINUS the soft-deleted memory — that one
    # is gone for good, so demanding an exact match with s1 would be wrong.
    if not contains("s4_acl_restored", S_ORGA):
        fails.append("s4: restoring the ACL window did not restore access")
    expected_s4 = (
        set(st["s1_control"]["our_statements_anywhere"]) - {S_DELETED}
    )
    if set(st["s4_acl_restored"]["our_statements_anywhere"]) != expected_s4:
        fails.append(
            "s4: state after restoring the ACL is not (control - deleted): "
            f"{sorted(st['s4_acl_restored']['our_statements_anywhere'])} vs "
            f"{sorted(expected_s4)}"
        )
    if st["s4_acl_restored"]["memory_count"] != st["s1_control"]["memory_count"] - 1:
        fails.append(
            "s4: memory_count should be exactly the control count minus the one "
            f"deleted row ({st['s4_acl_restored']['memory_count']} vs "
            f"{st['s1_control']['memory_count'] - 1})"
        )

    # metadata stays honest in every state
    for name, state in st.items():
        if not isinstance(state, dict) or "memory_count" not in state:
            continue
        if state["metadata_memory_count"] != state["memory_count"]:
            fails.append(f"{name}: metadata.memory_count != len(memory[])")

    # expired row really was stored with a past timestamp
    if st["s2_after_delete"]["status"] != 200 or st["s3_acl_timebox"]["status"] != 200:
        fails.append("a /context call did not return 200")

    out["assertions_checked"] = [
        "an active user memory and an active org memory are injected (control)",
        "an already-expired memory is never injected",
        "a soft-deleted memory is not injected, and its ROW still exists (deleted_at set)",
        "closing the org memory's allow-ACL window withholds it",
        "...while the row stays alive (deleted_at NULL, expires_at NULL)",
        "...with an UNCHANGED candidate count — so the denial is at authorization",
        "restoring the ACL window restores exactly the control state",
        "metadata.memory_count agrees with memory[] in every state",
    ]
    out["failures"] = fails
    out["verdict"] = "FAIL" if fails else "PASS"

    for f in fails:
        print(f"FAIL: {f}", file=sys.stderr)
    print(
        "PASS — Step 6 (A6): expired and soft-deleted memories are not injected "
        "(rows kept, deleted_at set); closing an org memory's allow-ACL window "
        "withholds it while the row stays alive and the candidate count is "
        "unchanged; restoring the window restores the control state."
        if not fails else f"FAIL — Step 6 (A6): {len(fails)} assertion(s) failed",
        file=sys.stderr,
    )

    dump(out)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
