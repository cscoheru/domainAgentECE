# Domain Product Layer — EvidenceIQ（审计证据智能）

> Phase: Gate 2/4
> 本文定义 Domain 层七要素在 MVP 中的具体形态

## 1. Domain Ontology（领域本体）— 核心资产 #1

```text
ComplianceProgram（SOC2 Type II / ISO27001）
 └── ControlDomain（CC1 组织 / CC5 逻辑访问 / CC6 …）
      └── ControlItem（控制项，如 CC6.2 访问评审）
           ├── requires EvidenceType[]（证据类型需求，如：评审记录/工单/导出报告）
           ├── hasOwner: Role（控制责任人角色）
           ├── appliesTo: SystemScope（适用系统范围）
           └── frequency: 审计期间要求（如季度评审×2）

Evidence（证据）
 ├── type: EvidenceType
 ├── source: 系统来源 / url / updatedAt（新鲜度）
 ├── covers: SystemScope（覆盖度）
 └── confidence: 完整性评级

EvidenceGap（缺口）= ControlItem × 缺失证据类型 / 过期 / 覆盖不足
ActionItem（行动）= Gap → owner → task → deadline
AuditPackage（输出物）= ControlItem[] × Evidence[] × Gap[] × ActionItem[]
```

- 版本管理：本体以 JSON/YAML 文件独立于代码（`src/domain/ontology/`），可迁移、可测试、可扩展。
- 初始覆盖：SOC2 CC 域 12 个代表性控制项（MVP 足够），ISO27001 映射留扩展点。

## 2. Domain Knowledge（领域知识）

- 每个控制项的"什么算合格证据"判定标准（如 CC6.2：评审记录须含完整用户清单+审批人+日期，且期间内每个季度至少一次）。
- 证据类型 → 典型来源系统映射（访问评审 → IT 工单系统；培训记录 → HR 系统）。
- 形式：知识文件 + 规则表，Agent prompt 注入 + 确定性规则混合使用。

## 3. Domain Reasoning（领域推理）— 核心资产 #2

四类推理规则（确定性规则优先，LLM 负责解释与边界判断）：

1. **充分性推理**：证据集合是否满足控制项的证据类型需求（类型×数量×期间）。
2. **新鲜度推理**：updatedAt 是否落在审计期间要求内（政策过期 → gap）。
3. **覆盖度推理**：证据 covers 是否 ⊇ appliesTo（访问评审只覆盖 2/3 系统 → partial gap）。
4. **归因与路由推理**：Gap → 责任人角色 → create_task 派工建议（含 deadline 建议）。

每条推理输出必须携带：结论 + 依据（引用的证据/规则编号）+ 置信度。

## 4. Domain Workflow（领域工作流）

```text
[Ingest] 输入审计范围（框架+期间+系统范围）
   ↓
[Map] Control Intake Agent：控制项 → 证据需求清单（本体驱动）
   ↓
[Retrieve] Evidence & Gap Agent：逐类检索（权限感知）→ 候选证据集
   ↓
[Reason] 充分性/新鲜度/覆盖度推理 → Evidence Matrix + Gap List
   ↓
[Act] create_task 派工缺口责任人（写回 Mock/Glean）
   ↓
[Approve] 合规经理人工确认（审批点，MVP 为 UI 确认按钮）
   ↓
[Package] 输出 Audit-Ready Evidence Pack
```

## 5. Domain Agents（1–2 个，窄而深）

按十二要素规范（Role/Goal/Context/Ontology/Knowledge/Tools/Workflow/Reasoning/Guardrails/Evaluation/Output/KPI），详见 `agent-runtime.md` §Agent 规格。

## 6. Domain Evaluation — 核心资产 #3

见 `docs/research/glean-evaluation.md` §MVP 落地：10–20 回归案例，五维评分（业务正确性/推理质量/证据质量/行动正确性/有用性）。

## 7. Business Outcome Model

| 指标 | Before（参考值，访谈校准） | MVP 目标 |
|---|---|---|
| 审计准备周期 | 3–4 周 | ≤3 天（初稿） |
| 证据缺口暴露时点 | 审计现场 | 提前 4–6 周 |
| 单控制项证据归集 | 30–60 分钟人工 | 自动 + 人工确认 |
