"""OEI-010 — reproduction of a latent fragility this cut REPORTS but may not fix.

`tests/integration/test_s32_assembly.py:92` asserts a CLOSED item_kind set:

    assert r[0] in ("entity", "relationship")

OEI-010 adds `item_kind='memory'` rows to the same `context_items` table for the
same request. So once the assembled user has an eligible memory, that assertion
fails — on correct behaviour.

An earlier revision of this cut widened the literal to include "memory". That was
REVERTED: TASK §8 permits changes to existing test files only in their
fixture / stub / dependency-injection / import parts, and says plainly that
assertions must not be changed. When a constraint is explicit and the benefit is
a one-token edit, the constraint wins.

So this script exists to *prove* the fragility rather than describe it, and the
finding is handed to the next cut as a transfer-out item. It reproduces the two
halves:

  PART 1  with the PRE-CUT assertion  -> FAILS once an eligible memory exists
  PART 2  with the same data present  -> the full suite still passes 847/0,
          because the live memories belong to a DIFFERENT user than the one this
          test assembles for (`demo-user-procurement`), which is why the suite is
          green today and why the fragility is latent rather than active.

stdout is text (`evidence/12c-s32-item-kind-fragility.txt`).

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step12c_s32_fragility.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _client import create_memory, fresh_app  # noqa: E402

ECE_DIR = Path(__file__).resolve().parents[3] / "ece"
TARGET = "tests/integration/test_s32_assembly.py"
TEST = f"{TARGET}::test_assemble_writes_context_items_with_valid_decisions"
OWNER = "demo-user-procurement"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=ECE_DIR, capture_output=True, text=True)


def main() -> int:
    client, engine = fresh_app()

    print("== OEI-010 — latent fragility in test_s32_assembly.py:92 (TRANSFER-OUT) ==")
    print()
    print("Assertion under discussion:")
    print(f'  {TARGET}:92')
    print('      assert r[0] in ("entity", "relationship")')
    print()

    # A live memory OWNED BY the user that test assembles for.
    res = create_memory(
        client, OWNER, scope="user", owner_ref=OWNER,
        statement="oei010 s32-fragility probe memory",
    )
    mem_id = res["body"]["memory"]["id"]
    print(f"fixture: created a live user-scope memory for {OWNER} (id={mem_id}, "
          f"HTTP {res['status']})")

    # run the test as committed (assertions pre-cut)
    proc = _run(["uv", "run", "pytest", TEST, "-q"])
    print()
    print("--- PART 1: run with the PRE-CUT assertion (== what is committed) ---")
    print(proc.stdout.strip()[-1200:] or proc.stderr.strip()[-1200:])
    print(f"exit status: {proc.returncode}")
    verdict_p1 = "FAILS (as predicted)" if proc.returncode != 0 else "PASSED"
    print(f"=> {verdict_p1}")

    if proc.returncode == 0:
        print()
        print("The fragility did NOT reproduce. Investigate before trusting the"
              " transfer-out note: either the memory was not injected, or the"
              " assertion no longer sees the row.")

    # clean up the fixture
    from sqlalchemy import text  # noqa: PLC0415

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM acl_entries WHERE object_ref = :o"),
            {"o": f"memory:{mem_id}"},
        )
        conn.execute(text("DELETE FROM memories WHERE id = :i"), {"i": mem_id})
    print()
    print("fixture removed (memory + its ACL row)")

    print()
    print("--- PART 2: why the committed suite is nonetheless green ---")
    print("The full suite was run twice on this commit (see 12b-test-suite-raw.txt):")
    print("  847 passed, 0 failed  — with memories present (owned by demo-user-finance)")
    print("  847 passed, 0 failed  — with an empty memories table")
    print("The test assembles for 'demo-user-procurement'. Memories owned by")
    print("'demo-user-finance' are neither user-scope visible to procurement nor")
    print("in procurement's org scope, so no memory row appears in ITS request and the")
    print("closed-set assertion never sees kind='memory'.")
    print()
    print("=> The suite passes today by fixture luck, not because the assertion is")
    print("   still correct. Any future cut that gives demo-user-procurement (or its")
    print("   org) a memory will turn it red with no code defect behind it.")

    print()
    print("--- recommendation for the next cut ---")
    print(f"  widen {TARGET}:92 to a set that includes \"memory\", or assert the")
    print("  invariant it is actually about (every audit row has a decision in")
    print("  {allowed, denied} and a non-empty reason) without enumerating kinds.")
    print("  This cut did NOT do so: TASK §8 forbids changing assertions.")
    print()
    print("--- verdict ---")
    print("REPORTED as a transfer-out item; NOT patched by OEI-010.")
    return 0 if proc.returncode != 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
