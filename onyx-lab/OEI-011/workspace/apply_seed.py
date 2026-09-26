#!/usr/bin/env python3
"""OEI-011 步骤 1+2 — apply the industry annotations and the bounded increment.

Reuses the drafts produced while the cut was blocked (`draft-industry-annotations.json`,
`draft-new-objects.json`) but writes to and re-verifies against the REAL seed file,
as TASK v1.1 requires.

Guarantees:
  - the seed file is written with exactly the serializer the original used
    (`json.dumps(..., ensure_ascii=False, indent=2)`, no trailing newline), verified
    by an exact round-trip of the pristine bytes before any write;
  - every pre-existing object keeps every field byte-identical except
    `client_industry` — proven by a canonical-JSON sha256 against
    `git show a463658:<seed>`;
  - each annotation's basis quote is checked to actually occur in that object's own
    fields (A3: the basis must be locatable in the object itself).

Usage:  uv run python apply_seed.py [--check-only]
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"
BASE_REV = "a463658"  # OEI-010's HEAD; the pre-cut baseline for A1
WS = Path(__file__).resolve().parent

FIELD = "client_industry"


def canonical(obj: dict, drop: str | None = None) -> str:
    return json.dumps(
        {k: v for k, v in sorted(obj.items()) if k != drop},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def baseline_objects() -> list[dict]:
    blob = subprocess.run(
        ["git", "-C", str(ECE), "show", f"{BASE_REV}:src/ece/consulting/seed/consulting_objects.json"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8")
    return json.loads(blob)


def main(argv: list[str]) -> int:
    check_only = "--check-only" in argv
    annotations = json.loads((WS / "draft-industry-annotations.json").read_text(encoding="utf-8"))
    new_objects = json.loads((WS / "draft-new-objects.json").read_text(encoding="utf-8"))
    base = baseline_objects()
    cur_raw = SEED.read_text(encoding="utf-8")
    cur = json.loads(cur_raw)

    if not check_only:
        # Round-trip guard: refuse to rewrite the file unless the pristine bytes
        # are reproduced exactly by the serializer we are about to use.
        assert json.dumps(cur, ensure_ascii=False, indent=2) == cur_raw, (
            "seed file does not round-trip with ensure_ascii=False, indent=2 — "
            "rewriting it would reformat untouched objects"
        )

    # --- step 1: annotate, changing ONLY client_industry -------------------
    frag = {a["id"]: a for a in annotations}
    unknown = set(frag) - {o["id"] for o in cur}
    assert not unknown, f"annotations reference unknown ids: {sorted(unknown)}"
    new_seed = []
    for o in cur:
        a = frag.get(o["id"])
        new_seed.append({**o, FIELD: list(a["new_value"])} if a else o)

    # --- step 2: append the bounded increment -----------------------------
    # Idempotent: a new object whose id is already present is REPLACED in place
    # rather than appended a second time, so re-running this script on an
    # already-applied seed is a no-op instead of a duplication.
    new_ids = {o["id"] for o in new_objects}
    existing_ids = {o["id"] for o in new_seed}
    already = new_ids & existing_ids
    if already:
        print(f"note: {len(already)} new-object ids already present -> replacing in place",
              file=sys.stderr)
        new_seed = [next((n for n in new_objects if n["id"] == o["id"]), o) for o in new_seed]
        to_append = [n for n in new_objects if n["id"] not in existing_ids]
    else:
        to_append = new_objects
    new_seed.extend(to_append)

    if not check_only:
        SEED.write_text(json.dumps(new_seed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {SEED} ({len(new_seed)} objects)", file=sys.stderr)
    else:
        print("--check-only: nothing written", file=sys.stderr)

    # --- A1 evidence: other fields byte-identical to a463658 ---------------
    lines, all_equal = [], True
    for i, (old, new) in enumerate(zip(base, new_seed, strict=False), 1):
        assert old["id"] == new["id"], (old["id"], new["id"])
        h_old, h_new = sha(canonical(old, FIELD)), sha(canonical(new, FIELD))
        ok = h_old == h_new
        all_equal &= ok
        lines.append(
            f"[{i:2d}/{len(base)}] {old['id']}\n"
            f"        baseline({BASE_REV}) other-fields sha256 = {h_old}\n"
            f"        current            other-fields sha256 = {h_new}   "
            f"{'EQUAL' if ok else '*** DIFFERENT ***'}"
        )
    lines.append("")
    lines.append(
        f"RESULT: other fields identical in {len(base)}/{len(base)} objects"
        if all_equal else "RESULT: MISMATCH — see the *** DIFFERENT *** lines above"
    )
    (WS.parent / "evidence" / "02-existing-36-unchanged-hashes.txt").write_text(
        "\n".join(
            [
                "== OEI-011 步骤 1 — '既有 36 个对象只加了 client_industry' 的哈希证明 (A1) ==",
                f"baseline: git show {BASE_REV}:src/ece/consulting/seed/consulting_objects.json",
                "hash: sha256 of the canonical JSON (sorted keys, compact separators) of the",
                "      object with `client_industry` removed — i.e. EVERY OTHER FIELD.",
                "      The seed file's own serializer was verified to round-trip the pristine",
                "      bytes exactly, so 'other fields unchanged' is a statement about content,",
                "      not about formatting.",
                "",
                *lines,
                "",
                "NOTE: A1 requires the pre-existing objects to be unchanged in every field",
                "except client_industry. It does NOT require the file's byte layout to be",
                "unchanged (9 objects were appended, which necessarily shifts the tail).",
                "---- done ----",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # --- A3 evidence: the basis table, with the quote locatability check ---
    scanned = {f: None for f in ("title", "summary", "practice", "problem_types", "methods")}
    out_rows = []
    for a in annotations:
        obj = next((o for o in base if o["id"] == a["id"]), None)
        assert obj is not None, a["id"]
        hay = " ".join(
            [obj["title"], obj["summary"], " ".join(obj["practice"]),
             " ".join(obj["problem_types"]), " ".join(obj["methods"])]
        )
        quote = a["basis_quote"]
        out_rows.append(
            {
                **{k: a[k] for k in ("id", "type", "title", "old_value", "new_value",
                                     "basis_field", "basis_quote", "basis_scan", "basis_note")},
                # A3: the basis must be locatable in the object's OWN fields.
                "basis_quote_is_substring_of_own_fields": quote in hay,
                "scanned_fields": list(scanned),
                "value_after": a["new_value"],
            }
        )
    unlocatable = [r["id"] for r in out_rows if not r["basis_quote_is_substring_of_own_fields"]]
    (WS.parent / "evidence" / "01-industry-annotation-basis.json").write_text(
        json.dumps(
            {
                "step": "OEI-011 step 1",
                "rule": (
                    "An object with no concrete-industry anchor in its own "
                    "title/summary/practice/problem_types/methods is a generic "
                    "method/template/risk list -> cross_industry (TASK 3.1.4/3.1.5). "
                    "Attachment to a specific industry without such an anchor is the "
                    "'硬贴行业' that 3.1.5 forbids."
                ),
                "annotated_count": len(out_rows),
                "unlocatable_basis": unlocatable,
                "all_basis_locatable_in_own_fields": not unlocatable,
                "rows": out_rows,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"A1 other-fields identical: {len(base)}/{len(base)} -> {all_equal}", file=sys.stderr)
    print(f"A3 basis locatable in own fields: {len(out_rows) - len(unlocatable)}/{len(out_rows)}",
          file=sys.stderr)
    return 0 if all_equal and not unlocatable else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
