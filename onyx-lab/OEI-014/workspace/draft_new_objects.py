#!/usr/bin/env python3
"""OEI-014 步骤 2 — 新增 20 条对象的内容草稿（唯一来源）。

本刀的目标（TASK §3.1）：10 个具体行业各 **≥4** 条（现在各 2 条）、每个行业
**≥1 条 `industry_note`**（`insurance` / `public_sector` / `technology` 现在是 0）、
`deliverable_template` **≥6**（现在 4）、总数 **65–70**。

铺开方式：**每个具体行业 +2 条，共 20 条**，每条**恰好携带 1 个具体行业**，
分配为 3 条 `industry_note`（补三个洞）+ 3 条 `deliverable_template`（4 → 7）
+ 7 条 `case` + 3 条 `risk_check` + 2 条 `methodology` + 2 条 `proposal_play`。

内容纪律（§3.2.1，`test_consulting_seed_discipline.py` 机检）：
  - title / summary 以中文为主（CJK 占比 ≥0.2）；
  - 客户名一律"某 + 行业 + 规模"（"某中型保险公司"），或"机构名脱敏"；
  - **无竞品名**、**无精确数字**（不出现"节省 30%"这类形态）、**无 ACME / X 客户 占位**；
  - 合成内容一律 `source_origin="synthetic_variant"` + `confidence="synthetic"`。

锚点纪律（§3.3）：每条都要有一个**具体**行业词落在自己的 `title` 或 `summary` 里，
且该词不能是 `ai` / `public` / `tech` / `制造(业)` / `供应链` 这类弱词。
下面的 `anchor_note` 只是给人看的备注；**机器判据由 `anchor_scan.py` 独立给出**
（`03-anchor-basis.json`），不采信这段注释。

用法：python draft_new_objects.py     → 写出 workspace/draft-new-objects.json
"""
from __future__ import annotations

import json
from pathlib import Path

WS = Path(__file__).resolve().parent

# 便捷构造：所有新增对象共用后 3 个字段（合成内容的诚实标注）
def _o(**kw) -> dict:
    kw.setdefault("source_origin", "synthetic_variant")
    kw.setdefault("confidence", "synthetic")
    kw.setdefault("review_state", "approved")
    return {
        "id": kw["id"], "type": kw["type"], "title": kw["title"], "summary": kw["summary"],
        "practice": kw["practice"], "engagement_phase": kw["engagement_phase"],
        "client_industry": kw["client_industry"], "problem_types": kw["problem_types"],
        "methods": kw["methods"], "deliverables": kw["deliverables"],
        "outcomes": kw["outcomes"], "source_origin": kw["source_origin"],
        "confidence": kw["confidence"], "review_state": kw["review_state"],
    }


OBJECTS: list[dict] = [
    # ================= banking (2 → 4) =================
    _o(
        id="case-banking-credit-approval-014", type="case",
        title="某城商行小微信贷审批时效评估",
        summary="为某中型城商行梳理小微信贷审批的等待环节与贷后检查负担, 给出分级授权与集中作业建议. 客户名脱敏, 数据为示意.",
        practice=["operations", "risk_management"],
        engagement_phase=["diagnosis", "implementation"],
        client_industry=["banking"],
        problem_types=["approval_breakdown", "turnaround_time", "decision_latency"],
        methods=["process_mapping", "queue_analysis", "risk_scoring"],
        deliverables=["diagnostic_report", "sop"],
        outcomes=["approval_layers_clarified", "bottleneck_identified"],
    ),
    _o(
        id="risk-check-banking-branch-007", type="risk_check",
        title="银行网点转型的落地风险清单",
        summary="城商行网点转型常见风险: 柜面人员安置 / 自助设备替代节奏 / 客户迁移意愿三类检查项, 用于实施阶段前置识别.",
        practice=["organization_design", "change_management"],
        engagement_phase=["implementation"],
        client_industry=["banking"],
        problem_types=["role_clarity", "customer_experience", "organization_alignment"],
        methods=["risk_register", "risk_scoring", "stakeholder_interview"],
        deliverables=["risk_register"],
        outcomes=["risks_documented"],
    ),
    # ================= consumer_goods (2 → 4) =================
    _o(
        id="case-consumer-goods-distributor-015", type="case",
        title="某快消品牌经销商库存与铺货诊断",
        summary="为某中型快消品牌评估经销商库存结构与铺货节奏, 识别动销差异与补货规则缺口, 给出渠道分层与观察口径建议. 客户名脱敏, 数据为示意.",
        practice=["operations", "sales", "supply_chain"],
        engagement_phase=["diagnosis"],
        client_industry=["consumer_goods"],
        problem_types=["inventory_imbalance", "channel_efficiency"],
        methods=["channel_tiering", "inventory_analysis", "cohort_analysis"],
        deliverables=["diagnostic_report", "replenishment_rules"],
        outcomes=["channel_hand_off_visible", "replenishment_rules_drafted"],
    ),
    _o(
        id="proposal-play-consumer-goods-listing-007", type="proposal_play",
        title="快消新品铺货提案打法",
        summary="面向快消品牌的新品铺货提案组织方式: 先对齐经销商分层与货架资源, 再给铺货节奏与动销观察口径, 避免只谈铺货率.",
        practice=["sales", "growth"],
        engagement_phase=["proposal"],
        client_industry=["consumer_goods"],
        problem_types=["proposal_setup", "channel_efficiency"],
        methods=["proposal_outline", "narrative_design", "channel_tiering"],
        deliverables=["proposal_outline", "expansion_priorities"],
        outcomes=["proposal_structure_ready"],
    ),
    # ================= energy (2 → 4) =================
    _o(
        id="case-energy-grid-load-016", type="case",
        title="某电网企业负荷预测协同评估",
        summary="为某省级电网企业评估负荷预测与检修计划的协同方式, 识别跨部门口径差异与滚动更新频率缺口, 给出预测节拍建议. 客户名脱敏, 数据为示意.",
        practice=["operations", "governance"],
        engagement_phase=["diagnosis", "implementation"],
        client_industry=["energy"],
        problem_types=["capacity_planning", "data_availability", "process_breakdown"],
        methods=["process_mapping", "scenario_planning", "stakeholder_interview"],
        deliverables=["diagnostic_report", "roadmap"],
        outcomes=["process_breakdowns_identified", "data_risks_visible"],
    ),
    _o(
        id="risk-check-energy-maintenance-008", type="risk_check",
        title="电力检修窗口期的执行风险清单",
        summary="电力企业检修窗口期常见风险: 停机窗口压缩 / 备件到位时序 / 跨专业协同三类检查项, 用于实施阶段风险前置.",
        practice=["operations", "risk_management"],
        engagement_phase=["implementation"],
        client_industry=["energy"],
        problem_types=["capacity_planning", "role_clarity", "supply_resilience"],
        methods=["risk_register", "risk_scoring"],
        deliverables=["risk_register"],
        outcomes=["risks_documented"],
    ),
    # ================= healthcare (2 → 4) =================
    _o(
        id="case-healthcare-outpatient-017", type="case",
        title="某三甲医院门诊流程等待评估",
        summary="为某三甲医院评估门诊挂号到就诊的等待环节与检查预约衔接, 给出分时段号源与导诊动线建议. 机构名脱敏, 数据为示意.",
        practice=["operations", "service_design"],
        engagement_phase=["diagnosis"],
        client_industry=["healthcare"],
        problem_types=["patient_journey", "turnaround_time", "service_consistency"],
        methods=["process_mapping", "queue_analysis", "journey_map"],
        deliverables=["diagnostic_report", "service_blueprint"],
        outcomes=["touchpoints_visible", "bottleneck_identified"],
    ),
    _o(
        id="deliverable-template-healthcare-005", type="deliverable_template",
        title="医院门诊服务蓝图模板",
        summary="面向医院门诊场景的服务蓝图骨架: 患者旅程阶段 / 前台可见动作 / 后台支撑 / 等待触点与信息断点.",
        practice=["service_design", "consulting_delivery"],
        engagement_phase=["diagnosis"],
        client_industry=["healthcare"],
        problem_types=["deliverable_structure", "patient_journey"],
        methods=["service_blueprint", "journey_map"],
        deliverables=["service_blueprint", "journey_map"],
        outcomes=["touchpoints_visible", "service_stages_clarified"],
    ),
    # ================= insurance (2 → 4, 且补 industry_note) =================
    _o(
        id="industry-note-cn-insurance-2026-007", type="industry_note",
        title="中国保险业 2026 业务关注点",
        summary="公开行业观察整理: 寿险与财险在核保、理赔时效与服务一致性上的关注点, 不涉及具体公司数据, 仅作行业语境.",
        practice=["strategy", "industry_analysis"],
        engagement_phase=["qualification", "proposal"],
        client_industry=["insurance"],
        problem_types=["industry_context"],
        methods=["public_observation"],
        deliverables=["industry_brief"],
        outcomes=["industry_context_visible"],
    ),
    _o(
        id="risk-check-insurance-underwriting-009", type="risk_check",
        title="保险核保数字化的落地风险清单",
        summary="保险核保环节数字化常见风险: 规则与人工复核的边界 / 影像件质量 / 告知一致性三类检查项, 用于实施阶段前置识别.",
        practice=["risk_management", "governance"],
        engagement_phase=["implementation"],
        client_industry=["insurance"],
        problem_types=["risk_disclosure", "compliance_gap", "process_breakdown"],
        methods=["risk_register", "policy_review"],
        deliverables=["risk_register", "compliance_review"],
        outcomes=["risks_documented"],
    ),
    # ================= logistics (2 → 4) =================
    _o(
        id="case-logistics-warehouse-018", type="case",
        title="某物流企业仓储拣选效率评估",
        summary="为某中型物流企业评估仓储拣选路径与波次安排, 识别高峰期运力与仓配衔接缺口, 给出排班与库位调整建议. 客户名脱敏, 数据为示意.",
        practice=["operations", "supply_chain"],
        engagement_phase=["diagnosis", "implementation"],
        client_industry=["logistics"],
        problem_types=["network_efficiency", "capacity_planning", "process_breakdown"],
        methods=["process_mapping", "network_modeling", "staffing_plan"],
        deliverables=["diagnostic_report", "staffing_plan"],
        outcomes=["process_breakdowns_identified", "bottleneck_identified"],
    ),
    _o(
        id="proposal-play-logistics-network-008", type="proposal_play",
        title="物流网络优化的提案打法",
        summary="物流网络优化提案的组织方式: 先给网络现状与运力口径, 再给干线-仓配的分层改进选项与推进节奏, 避免只给单一方案.",
        practice=["strategy", "supply_chain"],
        engagement_phase=["proposal"],
        client_industry=["logistics"],
        problem_types=["proposal_setup", "network_efficiency"],
        methods=["proposal_outline", "network_modeling", "scenario_planning"],
        deliverables=["proposal_outline", "network_assessment"],
        outcomes=["proposal_structure_ready"],
    ),
    # ================= manufacturing (2 → 4) =================
    _o(
        id="deliverable-template-manufacturing-006", type="deliverable_template",
        title="工厂现场诊断报告模板",
        summary="面向工厂现场的诊断报告骨架: 产线概况 / 工单与在制品 / 良率与停机 / 改进机会与优先级.",
        practice=["operations", "process_redesign"],
        engagement_phase=["diagnosis"],
        client_industry=["manufacturing"],
        problem_types=["deliverable_structure", "performance_gap"],
        methods=["report_skeleton", "gemba_walk"],
        deliverables=["diagnostic_report"],
        outcomes=["report_structure_ready"],
    ),
    _o(
        id="methodology-manufacturing-oee-011", type="methodology",
        title="设备综合效率拆解方法",
        summary="面向工厂产线的设备综合效率拆解: 可用率 / 性能率 / 良率三段分解与工时损失归类口径, 用于定位损失集中环节.",
        practice=["operations", "performance_management"],
        engagement_phase=["diagnosis", "implementation"],
        client_industry=["manufacturing"],
        problem_types=["performance_gap", "waste_identification", "capacity_planning"],
        methods=["process_mapping", "kpi_tree", "data_sampling"],
        deliverables=["kpi_tree", "waste_register"],
        outcomes=["performance_gap_visible", "waste_categories_visible"],
    ),
    # ================= public_sector (2 → 4, 且补 industry_note) =================
    _o(
        id="industry-note-cn-public-sector-2026-008", type="industry_note",
        title="中国公共部门 2026 服务关注点",
        summary="公开行业观察整理: 政务大厅与一网通办在服务标准化、窗口协同与材料精简上的关注点, 不涉及具体单位数据, 仅作行业语境.",
        practice=["strategy", "industry_analysis"],
        engagement_phase=["qualification", "proposal"],
        client_industry=["public_sector"],
        problem_types=["industry_context"],
        methods=["public_observation", "policy_review"],
        deliverables=["industry_brief"],
        outcomes=["industry_context_visible"],
    ),
    _o(
        id="case-public-sector-permit-cycle-019", type="case",
        title="某市政务大厅审批事项周期评估",
        summary="为某市政务大厅评估高频审批事项的流转周期与材料补正次数, 给出并联办理与一次性告知改进建议. 单位名脱敏, 数据为示意.",
        practice=["operations", "governance"],
        engagement_phase=["diagnosis", "implementation"],
        client_industry=["public_sector"],
        problem_types=["turnaround_time", "process_breakdown", "decision_latency"],
        methods=["process_mapping", "public_observation", "policy_review"],
        deliverables=["diagnostic_report", "remediation_plan"],
        outcomes=["process_breakdowns_identified", "decision_rights_clarified"],
    ),
    # ================= retail (2 → 4) =================
    _o(
        id="deliverable-template-retail-007", type="deliverable_template",
        title="零售门店巡检报告模板",
        summary="面向连锁零售门店的巡检报告骨架: 门店动线与陈列 / 库存与缺货 / 导购执行 / 整改事项与优先级.",
        practice=["operations", "sales_effectiveness"],
        engagement_phase=["diagnosis", "delivery"],
        client_industry=["retail"],
        problem_types=["deliverable_structure", "service_consistency"],
        methods=["report_skeleton", "process_mapping"],
        deliverables=["diagnostic_report", "remediation_plan"],
        outcomes=["report_structure_ready", "service_stages_clarified"],
    ),
    _o(
        id="methodology-retail-shelf-012", type="methodology",
        title="门店坪效与货架贡献分析方法",
        summary="零售门店的坪效与货架贡献分析: 按品类与货架段拆解贡献度, 识别低效陈列与缺货损失口径, 用于调整陈列优先级.",
        practice=["strategy", "operations"],
        engagement_phase=["diagnosis"],
        client_industry=["retail"],
        problem_types=["channel_efficiency", "performance_gap", "inventory_imbalance"],
        methods=["cohort_analysis", "benchmarking", "inventory_analysis"],
        deliverables=["benchmark_table", "improvement_opportunities"],
        outcomes=["performance_gap_visible"],
    ),
    # ================= technology (2 → 4, 且补 industry_note) =================
    _o(
        id="industry-note-cn-technology-2026-009", type="industry_note",
        title="中国科技企业 2026 经营关注点",
        summary="公开行业观察整理: 软件与互联网企业在研发投入节奏、续费结构与交付毛利上的关注点, 不涉及具体公司数据, 仅作行业语境.",
        practice=["strategy", "industry_analysis"],
        engagement_phase=["qualification", "proposal"],
        client_industry=["technology"],
        problem_types=["industry_context"],
        methods=["public_observation"],
        deliverables=["industry_brief"],
        outcomes=["industry_context_visible"],
    ),
    _o(
        id="case-technology-rd-delivery-020", type="case",
        title="某软件企业研发交付节奏评估",
        summary="为某中型软件企业评估需求排期到上线的交付节奏, 识别版本范围蔓延与测试资源缺口, 给出迭代节拍与冻结规则建议. 客户名脱敏, 数据为示意.",
        practice=["operations", "process_redesign"],
        engagement_phase=["diagnosis", "implementation"],
        client_industry=["technology"],
        problem_types=["scope_creep", "capacity_planning", "deliverable_structure"],
        methods=["process_mapping", "change_control", "stakeholder_interview"],
        deliverables=["diagnostic_report", "roadmap"],
        outcomes=["scope_protected", "bottleneck_identified"],
    ),
]

# 「为什么是这一条」——§5 步骤 2.3 要求 `02-new-objects-list.json` 带目标理由。
RATIONALE: dict[str, str] = {
    "case-banking-credit-approval-014": "banking 第 3 条：行业深度 2→4，且补一条 case（案例是该行业的演示面）",
    "risk-check-banking-branch-007": "banking 第 4 条：补一条行业相关的风险清单（风险清单最容易被误标为通用，这里明确锚定网点）",
    "case-consumer-goods-distributor-015": "consumer_goods 第 3 条：补 case，锚点落在快消与经销商",
    "proposal-play-consumer-goods-listing-007": "consumer_goods 第 4 条：补 proposal_play（该行业原有 case + note，缺提案类）",
    "case-energy-grid-load-016": "energy 第 3 条：补 case",
    "risk-check-energy-maintenance-008": "energy 第 4 条：补风险清单",
    "case-healthcare-outpatient-017": "healthcare 第 3 条：补 case",
    "deliverable-template-healthcare-005": "healthcare 第 4 条 + deliverable_template 第 5 条（4→≥6 的第 1 条）",
    "industry-note-cn-insurance-2026-007": "insurance 无 industry_note（0→1），这是 §1.2 三个洞之一",
    "risk-check-insurance-underwriting-009": "insurance 第 4 条：补风险清单；锚点用「核保」",
    "case-logistics-warehouse-018": "logistics 第 3 条：补 case",
    "proposal-play-logistics-network-008": "logistics 第 4 条：补 proposal_play",
    "deliverable-template-manufacturing-006": "manufacturing 第 3 条 + deliverable_template 第 2 条",
    "methodology-manufacturing-oee-011": "manufacturing 第 4 条：补 methodology；锚点用「设备综合效率」（不是弱词「制造」）",
    "industry-note-cn-public-sector-2026-008": "public_sector 无 industry_note（0→1），三个洞之二；锚点用「政务大厅」「一网通办」",
    "case-public-sector-permit-cycle-019": "public_sector 第 4 条：补 case；锚点用「政务大厅」",
    "deliverable-template-retail-007": "retail 第 3 条 + deliverable_template 第 3 条",
    "methodology-retail-shelf-012": "retail 第 4 条：补 methodology；锚点用「门店」「坪效」",
    "industry-note-cn-technology-2026-009": "technology 无 industry_note（0→1），三个洞之三；锚点用「科技企业」",
    "case-technology-rd-delivery-020": "technology 第 4 条：补 case；锚点用「软件」",
}


def main() -> int:
    ids = [o["id"] for o in OBJECTS]
    assert len(ids) == len(set(ids)), "duplicate ids in draft"
    assert len(OBJECTS) == 20, f"expected 20, got {len(OBJECTS)}"
    per_ind: dict[str, int] = {}
    per_type: dict[str, int] = {}
    for o in OBJECTS:
        assert len(o["client_industry"]) == 1, (
            f"{o['id']}: 新增对象默认恰好 1 个具体行业（§3.2.4），got {o['client_industry']}")
        per_ind[o["client_industry"][0]] = per_ind.get(o["client_industry"][0], 0) + 1
        per_type[o["type"]] = per_type.get(o["type"], 0) + 1
    assert set(per_ind) == set(ANCHOR_INDUSTRIES), (
        f"每行业都要铺到；缺 {set(ANCHOR_INDUSTRIES) - set(per_ind)}")
    assert all(v == 2 for v in per_ind.values()), per_ind

    out = {
        "step": "OEI-014 step 2 draft",
        "count": len(OBJECTS),
        "per_industry": dict(sorted(per_ind.items())),
        "per_type": dict(sorted(per_type.items())),
        "objects": OBJECTS,
        "rationale": RATIONALE,
    }
    (WS / "draft-new-objects.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {WS / 'draft-new-objects.json'}: {len(OBJECTS)} objects", flush=True)
    print(f"  per_industry: {dict(sorted(per_ind.items()))}", flush=True)
    print(f"  per_type    : {dict(sorted(per_type.items()))}", flush=True)
    return 0


ANCHOR_INDUSTRIES = (
    "banking", "consumer_goods", "energy", "healthcare", "insurance",
    "logistics", "manufacturing", "public_sector", "retail", "technology",
)

if __name__ == "__main__":
    raise SystemExit(main())
