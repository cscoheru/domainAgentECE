"""OEI-009 — evidence ↔ REPORT consistency guard (R1 follow-through).

codex VERDICT #2 §4.1 failed the cut because `05-per-result-filter-matrix.json`
disagreed with itself: the JSON data said `demo_user = 5`, the script's own
summary line said 5, the script's PASS sentence said 4, and `REPORT.md` said 4.

The rework fixed the run; this script keeps it fixed. It re-parses the three
engine-facing evidence files and asserts that every number they contain also
appears in `REPORT.md` — so the next person who edits either side gets a
failure instead of a silent contradiction.

Usage:
    uv run --project <ece> python check_evidence_consistency.py
Exit code 0 = consistent; 1 = some claim disagrees (printed).
"""
from __future__ import annotations

import json
import pathlib
import sys

CUT = pathlib.Path(__file__).resolve().parent.parent
E = CUT / "evidence"


def load_first_json(name: str) -> dict:
    """Evidence files may carry prose before/after the JSON payload."""
    lines = (E / name).read_text().splitlines()
    i = next(k for k, line in enumerate(lines) if line.strip().startswith("{"))
    obj, _ = json.JSONDecoder().raw_decode("\n".join(lines[i:]))
    return obj


def main() -> int:
    five = load_first_json("05-per-result-filter-matrix.json")
    seven = load_first_json("07-side-channel.txt")
    eight = load_first_json("08-timebox-acl.json")
    report = (CUT / "REPORT.md").read_text()
    five_raw = (E / "05-per-result-filter-matrix.json").read_text()

    checks: list[tuple[str, bool]] = []

    # --- 05: the A4 matrix -------------------------------------------------
    for identity, expected in (("anonymous", 3), ("demo_user", 4), ("other_user", 3)):
        checks.append((
            f"05 demo/{identity} == {expected}",
            five[f"demo__{identity}"]["engine_items_count"] == expected,
        ))
    for identity, expected in (("anonymous", 0), ("demo_user", 1), ("other_user", 0)):
        checks.append((
            f"05 isolation/{identity} == {expected}",
            five[f"isolation__{identity}"]["engine_items_count"] == expected,
        ))
    checks.append((
        "05 raw demo: count == distinct == 4 (no chunk duplicates)",
        five["raw_recall"]["demo_query"]["count"]
        == five["raw_recall"]["demo_query"]["distinct_count"]
        == 4,
    ))
    checks.append((
        "05 raw isolation: count == distinct == 1",
        five["raw_recall"]["isolation_query"]["count"]
        == five["raw_recall"]["isolation_query"]["distinct_count"]
        == 1,
    ))
    checks.append(("05 cleanup: zero delete failures", five["cleanup"]["delete_failures"] == []))
    checks.append(("05 stale index cleared before probing", five["stale_clear"]["cleared"] is True))
    checks.append((
        "05 no restricted title leaks to anonymous/other_user",
        not any(
            five[f"{q}__{ident}"]["restricted_visible"]
            for q in ("demo", "isolation")
            for ident in ("anonymous", "other_user")
        ),
    ))
    checks.append((
        "05 script's PASS line present and matches the data it printed",
        five_raw.strip().splitlines()[-1].startswith("PASS — Step 2.6 (R1)"),
    ))

    # --- 07: engine_status branches ---------------------------------------
    checks.append((
        "07 no-hit is a REAL zero-result state (0 items, status ok)",
        seven["branch_no_hit"]["engine_items_count"] == 0
        and seven["branch_no_hit"]["engine_status"] == "ok",
    ))
    checks.append((
        "07 unavailable branch reports unavailable",
        seven["branch_unavailable"]["engine_status"] == "unavailable",
    ))
    checks.append((
        "07 static baseline sha still equals the historical (pre-rework) value",
        seven["static_determinism"]["baseline_matches_historical"] is True,
    ))
    checks.append((
        "07 all four branches share one static sha256 (engine-orthogonal)",
        len({
            seven["branch_static_baseline"]["static_sha256"],
            seven["branch_ok"]["static_sha256"],
            seven["branch_unavailable"]["static_sha256"],
            seven["branch_no_hit"]["static_sha256"],
        }) == 1,
    ))

    # --- 08: timebox e2e ---------------------------------------------------
    checks.append((
        "08 stages are A=4 / B=3 (expired) / C=4 (restored)",
        [len(s["library_alice"]["engine_items_titles"]) for s in eight["stages"]] == [4, 3, 4],
    ))

    # --- REPORT.md must quote the same numbers ----------------------------
    checks.append(("REPORT quotes 'alice 4' and 'bob 3'", "alice 4" in report and "bob 3" in report))
    checks.append(("REPORT quotes the no-hit 0-item state", "`branch_no_hit` = 0 条" in report))
    checks.append(("REPORT quotes A=4 / B=3 / C=4", "A=4 / B=3（过期）/ C=4（恢复）" in report))
    checks.append(("REPORT carries the real commit hash", "a884d41" in report))

    failed = 0
    for name, ok in checks:
        print(f"  [{'OK ' if ok else 'FAIL'}] {name}")
        failed += 0 if ok else 1
    print()
    if failed:
        print(f"*** {failed} INCONSISTENCY(IES) — evidence and REPORT disagree ***")
        return 1
    print(f"ALL CONSISTENT ({len(checks)} checks) — evidence, script summaries and REPORT agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
