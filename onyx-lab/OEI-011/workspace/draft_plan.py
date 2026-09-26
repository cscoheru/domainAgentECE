#!/usr/bin/env python3
"""OEI-011 — draft of steps 1–4, built and verified ENTIRELY IN MEMORY.

Why this exists: OEI-011 is blocked (`evidence/00-blocked-contract-conflict.json`)
because TASK A4 mandates an increment while `tests/unit/test_consulting_seed_count.py:34-50`
freezes the type distribution with `==` and TASK §3.4/§8/A9 forbid editing that file.

Nothing in the repository is modified. This script:
  1. derives the `client_industry` annotation for the 24 blank objects, with a
     machine-recomputable basis column (§3.1.6 / A3);
  2. defines 9 new objects that satisfy A4's bounded-increment targets (§3.2);
  3. runs the REAL §1.6 gate test functions (schema + discipline), imported from
     the real test files, against the merged catalog — proving A5 is satisfiable;
  4. computes A4's coverage targets and A7/A8's per-industry match counts using
     the same `ConsultingCatalog.search()` the `/library` route calls.

Outputs (all under onyx-lab/OEI-011/workspace/):
  draft-industry-annotations.json, draft-new-objects.json, draft-coverage-targets.json

Usage:  uv run python draft_plan.py
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"
OUT = Path(__file__).resolve().parent

sys.path.insert(0, str(ECE / "src"))

from ece.consulting import metadata as md  # noqa: E402
from ece.consulting.models import KnowledgeObject  # noqa: E402
from ece.consulting.service import ConsultingCatalog  # noqa: E402

CROSS = "cross_industry"
SCANNED_FIELDS = ("title", "summary", "practice", "problem_types", "methods")

# `metadata._INDUSTRY_KEYWORDS` matches with plain substring `in`, which produces
# false positives on English text ("supply_ch*ai*n", "av*ai*lability",
# "public_benchmark"). For a basis column that a reviewer can trust, English
# keywords are matched on token boundaries; CJK keywords stay substring (CJK has
# no word delimiter). The raw-substring result is reported alongside so the
# difference is visible rather than assumed.
_ENGLISH_KW = re.compile(r"^[a-z]+$")


def industry_terms(obj: dict) -> dict:
    blob = " ".join(
        [obj["title"], obj["summary"], " ".join(obj["practice"]),
         " ".join(obj["problem_types"]), " ".join(obj["methods"])]
    ).lower()
    strict, loose = [], []
    for vocab, kws in md._INDUSTRY_KEYWORDS:
        for kw in kws:
            if kw.lower() not in blob:
                continue
            loose.append(f"{vocab}:{kw}")
            if _ENGLISH_KW.match(kw):
                if re.search(rf"\b{re.escape(kw)}\b", blob):
                    strict.append(f"{vocab}:{kw}")
            else:
                strict.append(f"{vocab}:{kw}")
    return {"strict_hits": strict, "loose_substring_hits": loose}


# ---------------------------------------------------------------------------
# Step 1 — annotate the 24 blank objects (§3.1)
# ---------------------------------------------------------------------------
# Rule applied: an object that carries no concrete-industry anchor in its own
# title/summary/practice/problem_types/methods is a generic method / generic
# template / generic risk list → `cross_industry` (§3.1.4/§3.1.5). The one object
# whose own text names an industry (lean-waste-walk, "用于制造业与服务运营场景")
# is still `cross_industry` because it explicitly spans manufacturing AND service
# operations — attaching it to manufacturing would be the "硬贴行业" §3.1.5 bans.
ANNOTATION_NOTES = {
    "methodology-lean-waste-walk-005": (
        "对象自述'用于制造业与服务运营场景'——同时覆盖制造业与服务业，不是行业专属；"
        "按 §3.1.5（判断不了/跨行业 → cross_industry），贴 manufacturing 属于'硬贴行业'。"
    ),
    "methodology-value-chain-003": (
        "loose 扫描命中 technology:'ai'，实为 practice 'supply_chain' 的子串（ch-ai-n）；"
        "按词边界严格扫描为 0 命中。"
    ),
    "methodology-benchmarking-public-010": (
        "loose 扫描命中 public_sector:'public'，实为 methods 'public_benchmark' 的子串；"
        "按词边界严格扫描为 0 命中。"
    ),
    "risk-check-data-availability-001": (
        "loose 扫描命中 technology:'ai'，实为 problem_types 'data_availability' 的子串"
        "（av-ai-lability）；按词边界严格扫描为 0 命中。"
    ),
}
DEFAULT_NOTE = (
    "title / summary / practice / problem_types / methods 五个字段中均无具体行业锚点："
    "该对象是通用方法/模板/风险清单，不针对特定行业（§3.1.4）。"
)


def build_annotations(raw: list[dict]) -> list[dict]:
    rows = []
    for o in raw:
        if o.get("client_industry"):
            continue  # already annotated — §2 forbids narrowing or replacing it
        scan = industry_terms(o)
        rows.append(
            {
                "id": o["id"],
                "type": o["type"],
                "title": o["title"],
                "old_value": [],
                "new_value": [CROSS],
                "basis_field": "summary",
                "basis_quote": o["summary"],
                "basis_scan": scan,
                "basis_note": ANNOTATION_NOTES.get(o["id"], DEFAULT_NOTE),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Step 2 — the 9 new objects (§3.2).  Content rules honoured:
#   - anonymized clients ("某 + 行业 + 规模"), no real company names;
#   - source_origin=synthetic_variant + confidence=synthetic;
#   - no competitor firm tokens; no precision numeric claims;
#   - every field filled from the existing vocabularies.
# ---------------------------------------------------------------------------
NEW_OBJECTS: list[dict] = [
    # --- industry_note ×4: A4 needs >=6 (have 2). Each carries EXACTLY ONE
    #     concrete industry (§3.1.3). These also lift four thin industries to 2.
    {
        "id": "industry-note-cn-manufacturing-2026-003",
        "type": "industry_note",
        "title": "中国制造业 2026 供应链关注点",
        "summary": "公开行业观察整理: 制造企业的产能布局、关键物料替代与供应商集中度三类关注点, 不涉及具体公司数据, 仅作行业语境.",
        "practice": ["strategy", "industry_analysis"],
        "engagement_phase": ["qualification", "proposal"],
        "client_industry": ["manufacturing"],
        "problem_types": ["industry_context", "supply_resilience"],
        "methods": ["public_observation"],
        "deliverables": ["industry_brief"],
        "outcomes": ["industry_context_visible"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    {
        "id": "industry-note-cn-logistics-2026-004",
        "type": "industry_note",
        "title": "中国物流行业 2026 网络布局观察",
        "summary": "公开行业观察整理: 干支线衔接、仓储节点分层与时效承诺口径三类议题, 不涉及具体公司数据, 仅作行业语境.",
        "practice": ["strategy", "industry_analysis"],
        "engagement_phase": ["qualification", "proposal"],
        "client_industry": ["logistics"],
        "problem_types": ["industry_context", "network_efficiency"],
        "methods": ["public_observation"],
        "deliverables": ["industry_brief"],
        "outcomes": ["industry_context_visible"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    {
        "id": "industry-note-cn-healthcare-2026-005",
        "type": "industry_note",
        "title": "中国医疗健康行业 2026 服务运营观察",
        "summary": "公开行业观察整理: 连锁医疗机构的分级衔接、服务一致性与一线人员配置三类议题, 仅作行业语境.",
        "practice": ["strategy", "industry_analysis"],
        "engagement_phase": ["qualification", "proposal"],
        "client_industry": ["healthcare"],
        "problem_types": ["industry_context", "service_consistency"],
        "methods": ["public_observation"],
        "deliverables": ["industry_brief"],
        "outcomes": ["industry_context_visible"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    {
        "id": "industry-note-cn-energy-2026-006",
        "type": "industry_note",
        "title": "中国能源行业 2026 采购与合规观察",
        "summary": "公开行业观察整理: 能源企业的事业部授权层级、采购合规审视与风险分级口径三类议题, 仅作行业语境.",
        "practice": ["strategy", "industry_analysis"],
        "engagement_phase": ["qualification", "proposal"],
        "client_industry": ["energy"],
        "problem_types": ["industry_context", "compliance_gap"],
        "methods": ["public_observation"],
        "deliverables": ["industry_brief"],
        "outcomes": ["industry_context_visible"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    # --- case ×3: A4 needs each concrete industry >=2; these cover the three
    #     thin industries not covered above. A `case` MUST be a concrete
    #     industry, never cross_industry (§3.1.3).
    {
        "id": "case-technology-data-platform-011",
        "type": "case",
        "title": "某科技公司数据平台选型诊断",
        "summary": "为某中型科技公司梳理数据平台现状与工具链重叠情况, 输出选型标准与分阶段落地建议. 客户名脱敏, 数字仅作示意.",
        "practice": ["operations", "consulting_delivery"],
        "engagement_phase": ["diagnosis", "proposal"],
        "client_industry": ["technology"],
        "problem_types": ["data_availability", "decision_latency"],
        "methods": ["stakeholder_interview", "data_sampling"],
        "deliverables": ["diagnostic_report", "roadmap"],
        "outcomes": ["data_risks_visible", "roadmap_communicated"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    {
        "id": "case-public-sector-service-window-012",
        "type": "case",
        "title": "某事业单位窗口服务流程梳理",
        "summary": "协助某事业单位梳理窗口服务流程与前后台衔接, 输出职责矩阵与短期过渡安排. 客户名脱敏, 数字仅作示意.",
        "practice": ["governance", "process_redesign"],
        "engagement_phase": ["diagnosis", "delivery"],
        "client_industry": ["public_sector"],
        "problem_types": ["process_breakdown", "role_clarity"],
        "methods": ["process_mapping", "raci_matrix"],
        "deliverables": ["raci_matrix", "transition_plan"],
        "outcomes": ["decision_rights_clarified", "process_breakdowns_identified"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    {
        "id": "case-insurance-underwriting-013",
        "type": "case",
        "title": "某保险公司核保流程时效评估",
        "summary": "为某中型保险公司评估核保环节的等待时间与复核集中度, 给出分级授权与流程改进建议. 客户名脱敏, 数据为示意.",
        "practice": ["operations", "risk_management"],
        "engagement_phase": ["diagnosis", "implementation"],
        "client_industry": ["insurance"],
        "problem_types": ["turnaround_time", "approval_breakdown"],
        "methods": ["process_mapping", "queue_analysis"],
        "deliverables": ["diagnostic_report", "sop"],
        "outcomes": ["bottleneck_identified", "process_breakdowns_identified"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    # --- risk_check ×2: A4 needs >=6 (have 4). Both are genuinely generic
    #     (no industry anchor) → cross_industry (§3.1.4).
    {
        "id": "risk-check-timeline-slippage-005",
        "type": "risk_check",
        "title": "进度延期风险",
        "summary": "项目排期延期的早期信号与三步应对 (里程碑复核、关键路径识别、客户侧资源确认), 适用于各类咨询项目.",
        "practice": ["consulting_delivery", "change_management"],
        "engagement_phase": ["proposal", "delivery"],
        "client_industry": [CROSS],
        "problem_types": ["capacity_planning", "stakeholder_alignment"],
        "methods": ["risk_register", "change_control"],
        "deliverables": ["risk_register"],
        "outcomes": ["risks_documented"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
    {
        "id": "risk-check-benefit-realization-006",
        "type": "risk_check",
        "title": "收益兑现风险",
        "summary": "项目结项后改进措施未落地的常见成因与三道检查 (责任归属、度量口径、复盘节奏), 适用于各类改进项目.",
        "practice": ["consulting_delivery", "performance_management"],
        "engagement_phase": ["delivery"],
        "client_industry": [CROSS],
        "problem_types": ["kpi_alignment", "organization_alignment"],
        "methods": ["kpi_tree", "risk_register"],
        "deliverables": ["risk_register"],
        "outcomes": ["risks_documented"],
        "source_origin": "synthetic_variant",
        "confidence": "synthetic",
        "review_state": "approved",
    },
]


def _load_test_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _run_gate(fn, catalog) -> dict:
    """Run a real gate test function; return its outcome without raising."""
    try:
        fn(catalog=catalog)
        return {"outcome": "pass", "error": None}
    except AssertionError as exc:
        return {"outcome": "fail", "error": str(exc)}


def main() -> int:
    raw = json.loads(SEED.read_text(encoding="utf-8"))
    annotations = build_annotations(raw)

    # Apply in memory: only `client_industry` changes on the 24.
    by_id = {a["id"]: a for a in annotations}
    merged = []
    for o in raw:
        if o["id"] in by_id:
            o = {**o, "client_industry": by_id[o["id"]]["new_value"]}
        merged.append(o)
    merged_all = [*merged, *NEW_OBJECTS]

    # --- A1 check: only client_industry differs, per object (in-memory proof) ---
    hash_rows = []
    for old, new in zip(raw, merged, strict=True):
        def canon(d: dict, drop: str) -> str:
            return json.dumps(
                {k: v for k, v in sorted(d.items()) if k != drop},
                ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            )
        hash_rows.append(
            {
                "id": old["id"],
                "all_other_fields_identical": canon(old, "client_industry")
                == canon(new, "client_industry"),
                "client_industry_changed": old.get("client_industry")
                != new.get("client_industry"),
            }
        )

    # --- A2 check: values + the case/industry_note ban -----------------------
    allowed = md.ALLOWED_INDUSTRIES | {CROSS}
    violations = []
    for o in merged_all:
        if not o["client_industry"]:
            violations.append({"id": o["id"], "why": "client_industry is empty"})
        for v in o["client_industry"]:
            if v not in allowed:
                violations.append({"id": o["id"], "why": f"value {v!r} outside vocabulary"})
        if o["type"] in ("case", "industry_note") and CROSS in o["client_industry"]:
            violations.append({"id": o["id"], "why": f"{o['type']} carries {CROSS}"})

    # --- A5 proof: run the REAL gate tests against the merged catalog --------
    gates_dir = ECE / "tests" / "unit"
    schema_mod = _load_test_module("kc001_schema", gates_dir / "test_consulting_seed_schema.py")
    disc_mod = _load_test_module("kc001_disc", gates_dir / "test_consulting_seed_discipline.py")

    catalog = ConsultingCatalog([KnowledgeObject(**o) for o in merged_all])
    gate_results = {}
    for mod in (schema_mod, disc_mod):
        for fname in dir(mod):
            if not fname.startswith("test_"):
                continue
            # Module-scoped fixtures are plain functions taking `catalog`/`seed_raw`;
            # drive them from the merged data explicitly.
            fn = getattr(mod, fname)
            varnames = fn.__code__.co_varnames[: fn.__code__.co_argcount]
            kwargs = {}
            if "catalog" in varnames:
                kwargs["catalog"] = catalog
            elif "seed_objects" in varnames:
                kwargs["seed_objects"] = [KnowledgeObject(**o) for o in merged_all]
            elif "seed_raw" in varnames:
                kwargs["seed_raw"] = merged_all
            if varnames:
                gate_results[f"{mod.__name__}::{fname}"] = _try_with(fn, kwargs)
            else:
                # No-arg tests read the real seed file from disk; they cannot be
                # driven from the in-memory increment. Recorded, not silently skipped.
                gate_results[f"{mod.__name__}::{fname}"] = {
                    "outcome": "not_driven_in_memory",
                    "error": "reads the on-disk seed; unaffected by an in-memory plan",
                }

    # --- A4 coverage targets --------------------------------------------------
    type_counts = Counter(o["type"] for o in merged_all)
    industry_counts = Counter(v for o in merged_all for v in o["client_industry"])
    cross_count = industry_counts.get(CROSS, 0)

    # --- A7/A8: per-value match counts through the real search path ----------
    match_counts = {}
    for v in sorted(catalog.facets().facets["client_industries"]):
        match_counts[v] = catalog.search(client_industry=[v], limit=100).total

    targets = {
        "before": {"total": len(raw), "type_counts": dict(sorted(Counter(o["type"] for o in raw).items())),
                   "industry_counts": dict(sorted(Counter(v for o in raw for v in o["client_industry"]).items())),
                   "industries_with_1_object": sorted(
                       i for i, n in Counter(v for o in raw for v in o["client_industry"]).items() if n == 1)},
        "after": {"total": len(merged_all), "type_counts": dict(sorted(type_counts.items())),
                  "industry_counts": dict(sorted(industry_counts.items())),
                  "cross_industry_count": cross_count},
        "a4_thresholds": {
            "total>=44": len(merged_all) >= 44,
            "every_concrete_industry>=2": all(
                n >= 2 for i, n in industry_counts.items() if i != CROSS),
            "industry_note>=6": type_counts["industry_note"] >= 6,
            "risk_check>=6": type_counts["risk_check"] >= 6,
            "cross_industry>=10": cross_count >= 10,
        },
        "a7_facet_has_all_10_concrete_plus_cross": sorted(
            catalog.facets().facets["client_industries"]) == sorted(
            [*md.ALLOWED_INDUSTRIES, CROSS]) or sorted(
            catalog.facets().facets["client_industries"]),
        "a7_a8_match_counts_per_industry_value": match_counts,
        "a7_no_zero_match_value": all(n >= 2 for n in match_counts.values()),
        "new_object_ids_collide_with_existing": sorted(
            {o["id"] for o in NEW_OBJECTS} & {o["id"] for o in raw}),
    }

    (OUT / "draft-industry-annotations.json").write_text(
        json.dumps(annotations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "draft-new-objects.json").write_text(
        json.dumps(NEW_OBJECTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "draft-coverage-targets.json").write_text(
        json.dumps(
            {"a1_only_client_industry_changed": hash_rows,
             "a2_violations": violations,
             "a5_gate_results": gate_results,
             "targets": targets},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"annotations={len(annotations)} new_objects={len(NEW_OBJECTS)} "
          f"total_after={len(merged_all)}", file=sys.stderr)
    print(f"A1 other-fields-identical: {all(r['all_other_fields_identical'] for r in hash_rows)} "
          f"({sum(r['all_other_fields_identical'] for r in hash_rows)}/{len(hash_rows)})", file=sys.stderr)
    print(f"A2 violations: {len(violations)}", file=sys.stderr)
    print(f"A4: {targets['a4_thresholds']}", file=sys.stderr)
    print(f"A7 no zero-match value: {targets['a7_no_zero_match_value']}", file=sys.stderr)
    fails = {k: v for k, v in gate_results.items() if v["outcome"] != "pass"}
    print(f"A5 gate failures: {len(fails)} {list(fails)}", file=sys.stderr)
    return 0


def _try_with(fn, kwargs) -> dict:
    try:
        fn(**kwargs)
        return {"outcome": "pass", "error": None}
    except AssertionError as exc:
        return {"outcome": "fail", "error": str(exc)}


if __name__ == "__main__":
    raise SystemExit(main())
