"""OEI-010 step 9 (A10) — the existing `to_dict()` contract must not regress.

A10 asks for a key-by-key comparison, not a "looks fine". So this compares three
independent things and requires all three to agree:

  1. the key list parsed out of the PRE-CUT source  (`git show HEAD:<file>`)
  2. the key list parsed out of the CURRENT source
  3. the key list produced at RUNTIME by `to_dict()`

(3) is what catches a source that looks right but does not match what executes.
The claim is precise: the first 11 keys are unchanged and in the same order, and
exactly one key — `memory` — is appended at the end. Appending matters: a key
inserted in the middle would still "be there" while silently shifting positional
consumers.

The `metadata.counts` sub-dictionary is checked the same way, because it is a
second, nested contract that OEI-009 established.

stdout is plain text (`evidence/10-package-keys-diff.txt`), so the assertions
print as a readable before/after diff rather than as JSON booleans.

Run from the ECE repo root:
    DATABASE_URL=... uv run --project <ece> python step9_package_keys.py
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


REL_PATH = "src/ece/context/assembly.py"
CLASS = "ContextPackage"


def _find_ece_repo() -> Path:
    """Locate the ECE repo by its marker file, not by counting `..` levels.

    Counting parents is fragile — this script lives four levels below the
    project root and the ECE repo is a SIBLING of `onyx-lab/`, so an off-by-one
    silently produces a path that does not exist.
    """
    starts = [Path(__file__).resolve(), Path.cwd().resolve()]
    for start in starts:
        for candidate in [start, *start.parents]:
            if (candidate / "src" / "ece" / "main.py").is_file():
                return candidate
    raise SystemExit(
        "could not locate the ECE repo root (no src/ece/main.py above "
        f"{Path(__file__).resolve()} or {Path.cwd()})"
    )


ECE_DIR = _find_ece_repo()


def _returned_keys(source: str, class_name: str) -> list[str]:
    """Parse the key order out of a class's `to_dict` literal return.

    Uses the AST rather than a regex over text so that a key appearing in a
    comment or a docstring cannot be mistaken for a real one — the whole point
    of this evidence is that it reflects the code, not the prose around it.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "to_dict":
                    for sub in ast.walk(item):
                        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Dict):
                            return [
                                k.value for k in sub.value.keys
                                if isinstance(k, ast.Constant)
                            ]
    raise SystemExit(f"could not find {class_name}.to_dict in the source")


def _counts_keys(source: str) -> list[str]:
    """Parse the `metadata["counts"]` key order out of the source.

    Read from the code, including from the PRE-CUT revision, so the comparison
    is "unchanged from HEAD" rather than "matches a list I typed from memory".
    (Typing it from memory is how this check first failed: the fourth key is
    `rows`, not `business_data`.)
    """
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == "counts"
                    and isinstance(value, ast.Dict)
                ):
                    return [
                        k.value for k in value.keys if isinstance(k, ast.Constant)
                    ]
    raise SystemExit("could not find the metadata['counts'] literal in the source")


def main() -> int:
    fails: list[str] = []

    head_source = subprocess.run(
        ["git", "show", f"HEAD:{REL_PATH}"],
        cwd=ECE_DIR, capture_output=True, text=True, check=True,
    ).stdout
    head_keys = _returned_keys(head_source, CLASS)
    head_counts = _counts_keys(head_source)

    cur_source = (ECE_DIR / REL_PATH).read_text(encoding="utf-8")
    cur_keys = _returned_keys(cur_source, CLASS)

    # A REAL assembled package, not a bare constructor. `metadata.counts` and
    # `metadata.memory_count` are populated by `_finalize`, so a hand-built
    # ContextPackage has an empty metadata and would report "counts keys
    # changed" — a false alarm about the contract this step exists to check.
    sys.path.insert(0, str(ECE_DIR / "src"))
    from ece.context.assembly import assemble_context  # noqa: PLC0415
    from ece.db import get_engine  # noqa: PLC0415

    pkg = assemble_context(
        engine=get_engine(),
        user_ref="demo-user-finance",
        intent="evaluate_purchase_request",
        entities=[{"type": "purchase_request", "id": "PR0001"}],
    )
    runtime = pkg.to_dict()
    runtime_keys = list(runtime.keys())
    print(f"assembled package request_id={pkg.request_id} "
          f"user payload keys={sorted(pkg.user)}")
    print(f"injected memories in this package: {len(runtime['memory'])}")
    print()

    print("== OEI-010 step 9 (A10) — ContextPackage.to_dict() key contract ==")
    print(f"source: {REL_PATH}")
    print(f"pre-cut revision: {subprocess.run(['git','rev-parse','--short','HEAD'], cwd=ECE_DIR, capture_output=True, text=True).stdout.strip()}")
    print()
    print(f"pre-cut keys ({len(head_keys)}):")
    for i, k in enumerate(head_keys, 1):
        print(f"  {i:2d}. {k}")
    print()
    print(f"current keys ({len(cur_keys)}):")
    for i, k in enumerate(cur_keys, 1):
        mark = "  <-- NEW (appended)" if i > len(head_keys) else ""
        print(f"  {i:2d}. {k}{mark}")
    print()
    print(f"runtime keys from to_dict() ({len(runtime_keys)}):")
    for i, k in enumerate(runtime_keys, 1):
        print(f"  {i:2d}. {k}")
    print()

    # ---- assertion 1: runtime == current source --------------------------
    if runtime_keys != cur_keys:
        fails.append(
            f"runtime to_dict() keys != source keys:\n"
            f"    runtime: {runtime_keys}\n    source : {cur_keys}"
        )

    # ---- assertion 2: pre-cut keys are a strict PREFIX, in order ---------
    if len(cur_keys) != len(head_keys) + 1:
        fails.append(
            f"expected exactly one new key ({len(head_keys)} -> {len(head_keys)+1}), "
            f"got {len(head_keys)} -> {len(cur_keys)}"
        )
    if cur_keys[: len(head_keys)] != head_keys:
        fails.append(
            "the pre-cut keys are NOT an unchanged prefix.\n"
            f"    pre-cut: {head_keys}\n    current: {cur_keys[:len(head_keys)]}"
        )
    if cur_keys[len(head_keys):] != ["memory"]:
        fails.append(
            f"the appended key(s) are {cur_keys[len(head_keys):]}, expected ['memory']"
        )

    # ---- assertion 3: the new key actually carries the injected memories --
    if not isinstance(runtime.get("memory"), list):
        fails.append(f"to_dict()['memory'] is {type(runtime.get('memory'))}, expected list")
    if len(runtime["memory"]) != len(pkg.memory):
        fails.append("to_dict()['memory'] disagrees with the package's own memory list")

    # ---- assertion 4: the nested counts contract is untouched ------------
    counts = runtime["metadata"].get("counts", {})
    print(f"metadata.counts keys, pre-cut ({len(head_counts)}): {head_counts}")
    print(f"metadata.counts keys, runtime ({len(counts)}): {list(counts.keys())}")
    print()
    if list(counts.keys()) != head_counts:
        fails.append(
            f"metadata.counts keys changed vs pre-cut: "
            f"{list(counts.keys())} != {head_counts}"
        )
    # memory must NOT be smuggled into counts — it is reported as its own
    # metadata key (memory_count) so that existing counts consumers are safe.
    if "memory" in counts or "memory_count" in counts:
        fails.append("counts gained a memory key; it belongs in metadata, not counts")
    for extra in ("memory_count", "memory_dropped"):
        if extra not in runtime["metadata"]:
            fails.append(f"metadata is missing {extra}")
    print("metadata top-level keys:")
    for i, k in enumerate(runtime["metadata"], 1):
        print(f"  {i:2d}. {k}")
    print()

    print("== diff ==")
    print(f"  pre-cut : {len(head_keys)} keys")
    print(f"  current : {len(cur_keys)} keys")
    print(f"  added   : {[k for k in cur_keys if k not in head_keys]}")
    print(f"  removed : {[k for k in head_keys if k not in cur_keys]}")
    print(f"  reordered: {[k for k in head_keys if k in cur_keys][:len(head_keys)] != head_keys[:len(cur_keys) - 1]}")
    print()

    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("PASS — Step 9 (A10): the existing 11 keys are unchanged and in the same")
    print("order; exactly one key (`memory`) is appended at the end; runtime matches")
    print("the source; metadata.counts keeps its original 5 keys and memory is")
    print("reported as metadata.memory_count / memory_dropped instead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
