#!/usr/bin/env python3
"""OEI-011 — machine reproduction of a TASK-vs-reality conflict.

Finding: TASK §6 A4 mandates a bounded increment (total ≥ 44, industry_note ≥ 6,
risk_check ≥ 6). `tests/unit/test_consulting_seed_count.py:34-50` asserts the
type distribution with `==` (EXACT: case 10 / methodology 10 / proposal_play 6 /
deliverable_template 4 / risk_check 4 / industry_note 2). TASK §3.4 and §8 do NOT
authorize changing that file, and §6 A9 says "其余断言零改动".

That is arithmetically impossible to satisfy: sum(expected) == 36 == current
total, so every added object makes at least one `actual[t] == n` false.

This script proves it WITHOUT touching the repository:
  - it reads the real seed,
  - builds the increment in memory,
  - then calls the ACTUAL test functions, imported from the real test file,
    against a catalog built from the incremented seed.

Output is pure JSON on stdout (verdict inside the JSON); the human line goes to
stderr. Nothing is written outside OEI-011's own directory tree.

Usage:  uv run python blocked_repro.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"
TEST_FILE = ECE / "tests" / "unit" / "test_consulting_seed_count.py"

sys.path.insert(0, str(ECE / "src"))

from ece.consulting.service import ConsultingCatalog  # noqa: E402


def _load_test_module():
    spec = importlib.util.spec_from_file_location("kc001_seed_count", TEST_FILE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _catalog_from(raw_objects: list[dict]) -> ConsultingCatalog:
    """Build a catalog the same way the production loader does.

    `from_seed_path` reads a file; we need the same construction from in-memory
    objects so no file is written.
    """
    from ece.consulting.models import KnowledgeObject

    return ConsultingCatalog([KnowledgeObject(**o) for o in raw_objects])


def _try(test_fn, catalog) -> dict:
    try:
        test_fn(catalog=catalog)
        return {"outcome": "pass", "assertion_error": None}
    except AssertionError as exc:
        return {"outcome": "fail", "assertion_error": str(exc)}


# The minimal object that A4 forces: one more `industry_note` (A4 needs ≥6, there
# are 2). Content is irrelevant to this finding — only the `type` matters.
ONE_MORE_INDUSTRY_NOTE = {
    "id": "industry-note-oei011-probe-999",
    "type": "industry_note",
    "title": "探针行业观察",
    "summary": "仅用于证明数量断言冲突的探针对象，不会被写入仓库。",
    "practice": ["strategy"],
    "engagement_phase": ["proposal"],
    "client_industry": ["retail"],
    "problem_types": ["industry_context"],
    "methods": ["public_observation"],
    "deliverables": ["industry_brief"],
    "outcomes": ["industry_context_visible"],
    "source_origin": "synthetic_variant",
    "confidence": "synthetic",
    "review_state": "approved",
}


def main() -> int:
    raw = json.loads(SEED.read_text(encoding="utf-8"))
    mod = _load_test_module()

    base_counts = Counter(o["type"] for o in raw)
    expected = {
        "case": 10,
        "methodology": 10,
        "proposal_play": 6,
        "deliverable_template": 4,
        "risk_check": 4,
        "industry_note": 2,
    }

    # --- scenario 1: today's seed (control) -------------------------------
    base_catalog = _catalog_from(raw)

    # --- scenario 2: +1 industry_note (the smallest change A4 forces) ------
    plus_one_catalog = _catalog_from([*raw, ONE_MORE_INDUSTRY_NOTE])

    # --- scenario 3: a full A4-satisfying plan (9 new objects) ------------
    # 7 concrete industries currently hold 1 object each and A4 wants ≥2;
    # industry_note needs +4 (2→6); risk_check needs +2 (4→6). Four of the
    # industry_note additions double as the second object for 4 thin industries;
    # the remaining 3 thin industries get a `case`. Total 36+9 = 45 ≥ 44.
    plan = [
        # industry_note ×4 — one per thin industry (each exactly 1 concrete industry)
        ("industry-note-cn-manufacturing-2026-003", "industry_note", "manufacturing"),
        ("industry-note-cn-logistics-2026-004", "industry_note", "logistics"),
        ("industry-note-cn-healthcare-2026-005", "industry_note", "healthcare"),
        ("industry-note-cn-energy-2026-006", "industry_note", "energy"),
        # case ×3 — the remaining thin industries (cases must be concrete, never cross_industry)
        ("case-technology-data-platform-011", "case", "technology"),
        ("case-public-sector-service-window-012", "case", "public_sector"),
        ("case-insurance-underwriting-013", "case", "insurance"),
        # risk_check ×2 — genuinely generic (cross_industry)
        ("risk-check-timeline-slippage-005", "risk_check", "cross_industry"),
        ("risk-check-benefit-realization-006", "risk_check", "cross_industry"),
    ]
    plan_objects = [
        {
            "id": oid,
            "type": t,
            "title": "占位",
            "summary": "占位",
            "practice": ["strategy"],
            "engagement_phase": ["diagnosis"],
            "client_industry": [ind],
            "problem_types": ["industry_context"],
            "methods": ["public_observation"],
            "deliverables": ["industry_brief"],
            "outcomes": ["industry_context_visible"],
            "source_origin": "synthetic_variant",
            "confidence": "synthetic",
            "review_state": "approved",
        }
        for oid, t, ind in plan
    ]
    plan_catalog = _catalog_from([*raw, *plan_objects])
    plan_counts = Counter(o["type"] for o in plan_objects)
    final_counts = base_counts + plan_counts
    final_industry = Counter(
        ind for o in [*raw, *plan_objects] for ind in o["client_industry"]
    )

    scenarios = {
        "control_today_seed": {
            "objects": len(raw),
            "type_counts": dict(sorted(base_counts.items())),
            "test_total_object_count_meets_minimum": _try(
                mod.test_total_object_count_meets_minimum, base_catalog
            ),
            "test_type_distribution_matches_documented_targets": _try(
                mod.test_type_distribution_matches_documented_targets, base_catalog
            ),
        },
        "plus_one_industry_note": {
            "objects": len(raw) + 1,
            "type_counts": dict(sorted((base_counts + Counter(["industry_note"])).items())),
            "test_total_object_count_meets_minimum": _try(
                mod.test_total_object_count_meets_minimum, plus_one_catalog
            ),
            "test_type_distribution_matches_documented_targets": _try(
                mod.test_type_distribution_matches_documented_targets, plus_one_catalog
            ),
        },
        "a4_satisfying_plan": {
            "objects": len(raw) + len(plan_objects),
            "type_counts": dict(sorted(final_counts.items())),
            "industry_match_counts": dict(sorted(final_industry.items())),
            "test_total_object_count_meets_minimum": _try(
                mod.test_total_object_count_meets_minimum, plan_catalog
            ),
            "test_type_distribution_matches_documented_targets": _try(
                mod.test_type_distribution_matches_documented_targets, plan_catalog
            ),
        },
    }

    contradiction = {
        "frozen_assertion": "tests/unit/test_consulting_seed_count.py:34-50",
        "frozen_assertion_is_cast_as": "==",
        "expected_sum_equals_current_total": sum(expected.values()) == len(raw),
        "expected_sum": sum(expected.values()),
        "current_total": len(raw),
        "why_impossible": (
            "sum(expected) == current total (36). Every added object increments some "
            "actual[t], and the test requires actual[t] == expected[t] for all six "
            "types. Therefore ANY increment — even one object — makes the assertion "
            "false. A4 mandates total >= 44 and industry_note >= 6 and risk_check >= 6."
        ),
        "authorized_test_edits_per_task_s3_4_and_s8": [
            "tests/unit/test_consulting_documents.py:263",
            "tests/unit/test_consulting_documents.py:315",
            "tests/unit/test_consulting_engine_merge.py:339",
            "tests/integration/test_s32_assembly.py:92 (step 0.1)",
            "+ new files",
        ],
        "this_file_is_not_authorized": True,
    }

    out = {
        "task": "OEI-011",
        "what_this_is": "reproduction of a TASK-vs-reality conflict (no repo writes)",
        "seed_path": str(SEED),
        "test_file": str(TEST_FILE),
        "assertion_inventory_complete": {
            "sites_coupling_to_catalog_size_or_distribution": [
                {"site": "tests/unit/test_consulting_documents.py:263",
                 "assertion": "static_catalog_size == 36",
                 "authorized_by_task": True, "breaks_on_increment": True},
                {"site": "tests/unit/test_consulting_documents.py:315",
                 "assertion": "static_catalog_size == 36",
                 "authorized_by_task": True, "breaks_on_increment": True},
                {"site": "tests/unit/test_consulting_engine_merge.py:339",
                 "assertion": "total == 36",
                 "authorized_by_task": True, "breaks_on_increment": True},
                {"site": "tests/unit/test_consulting_seed_count.py:29",
                 "assertion": "len(catalog.objects) >= 36",
                 "authorized_by_task": False, "breaks_on_increment": False},
                {"site": "tests/integration/test_consulting_api_contract.py:55",
                 "assertion": "total >= 36",
                 "authorized_by_task": False, "breaks_on_increment": False},
                {"site": "tests/unit/test_consulting_seed_count.py:34-50",
                 "assertion": "actual[type] == expected[type] for all six types (EXACT)",
                 "authorized_by_task": False,
                 "breaks_on_increment": True,
                 "listed_in_task_s1_5": False,
                 "note": "TASK §1.5 calls its table an exhaustive inventory "
                         "(我逐个核过) and names only five sites; this sixth site is "
                         "the strictest one and is absent from that table."},
            ]
        },
        "scenarios": scenarios,
        "contradiction": contradiction,
        "verdict": "BLOCKED",
        "verdict_reason": (
            "A4 (total>=44, industry_note>=6, risk_check>=6) is unsatisfiable while "
            "test_consulting_seed_count.py:34-50 keeps its `==` distribution assertion, "
            "and TASK §3.4/§8/A9 forbid editing that file. Reproduction: the real test "
            "function, run against the incremented catalog, raises AssertionError in "
            "both the minimal (+1) and the full (+9) scenario."
        ),
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    print(
        "BLOCKED — TASK A4 vs frozen exact-distribution assertion; "
        "see stdout JSON for the reproduction",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
