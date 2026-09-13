# Glean × Our Product — Architecture Boundary

> Phase: Gate 2 — Product Boundary Gate
> Last Verified: 2026-09-03
> 证据引用见 docs/research/evidence-matrix.md（C 编号）

## 1. 边界总图

```text
┌────────────────────────────────────────────────────┐
│                DOMAIN PRODUCT（我们）                │
│                                                    │
│  Domain UI（审计工作台：Evidence Pack / Gap List）   │
│  Domain Agents（Control Intake / Evidence & Gap）   │
│  Domain Ontology（控制项-证据类型-责任人映射）        │
│  Domain Reasoning（充分性/覆盖度/新鲜度/抽样推理）    │
│  Domain Workflows（审计准备流程 + 审批点）            │
│  Domain Evaluation（业务正确性回归集）                │
│  Business Outcome Model（审计准备时间/缺口提前期）    │
└──────────────────────┬─────────────────────────────┘
                       │ Context Adapter（唯一边界接口）
┌──────────────────────▼─────────────────────────────┐
│                 GLEAN（基础设施，不自建）             │
│  Enterprise Context（Graph）/ Search / Permissions  │
│  Connectors（275+）/ Actions / Agent Infrastructure │
│  Governance / Observability / Model Routing         │
└──────────────────────┬─────────────────────────────┘
                       │
              Enterprise Systems（客户已有系统）
```

## 2. Capability Matrix（Gate 2 交付）

| Capability | Glean Native | Glean API | Partner Ext. | 我们建？ | IP 潜力 | 证据 |
|---|---|---|---|---|---|---|
| Enterprise Search | ✅ 权限感知/个性化/引用 | ✅ Client+Platform API | — | ❌ 不建 | 低 | C04 |
| Enterprise Context | ✅ Graph 索引 | 部分（Indexing 推送） | — | ❌ 不建（仅推送领域数据源） | 低 | C02/C03 |
| Permissions | ✅ 继承源系统 ACL | ✅ | — | ❌ 不建（仅领域级语义门控） | 低 | C06/C07 |
| Connectors | ✅ 275+ | ✅ Indexing SDK | ✅ | ❌ 不建 | 低 | C05/C09 |
| Actions/写回 | ✅ Actions | ✅ OpenAPI 自定义 | ✅ MCP | ❌ 不建（仅定义领域动作语义） | 低 | C08/C09 |
| Agent Runtime | ✅ Builder/Orchestration | ✅ Toolkit/Platform API | ✅ | ⚠️ MVP 自建薄 runtime（因 C11 UNKNOWN + C15 experimental；POC 再评估迁移） | 低 | C10-C18 |
| Governance | ✅ Protect/certify | ✅ | — | ❌ 不建（仅审批点+领域审计日志） | 低 | C13/C19 |
| Observability | ✅ adoption/error/votes | ✅ | — | ⚠️ 薄层（运行日志） | 低 | C14 |
| Platform Evaluation | — | — | — | ⚠️ 简单统计即可 | 低 | C14/C22 |
| **Domain Ontology** | ❌ | — | — | ✅ **核心资产** | **高** | C03/C23 |
| **Domain Reasoning** | ❌ | — | — | ✅ **核心资产** | **高** | C23 |
| **Domain Workflow** | ❌（模板级，见 C21 风险） | — | — | ✅ **核心资产** | **高** | C12/C21 |
| **Domain Knowledge** | ❌ | — | — | ✅（控制框架知识库） | **高** | — |
| **Domain Evaluation** | ❌ | — | — | ✅ **核心资产（长期 IP）** | **高** | C22/C23 |
| **Domain KPI/Outcome** | ❌ | — | — | ✅（审计准备周期等） | 中-高 | — |

## 3. 边界规则（强制）

1. **Domain 层零 Glean 依赖**：`src/domain/**` 不得 import 任何 Glean SDK / glean 命名空间。
2. 唯一合法通路：`ContextAdapter` 接口（见 context-adapter.md）。
3. Glean 专属概念（datasource、connector）只允许出现在 `src/adapters/glean/**`。
4. 判定一个功能建不建的顺序：Glean 是否已提供 → 合作伙伴生态是否提供 → 是否 MVP 必需 → 是否产生 Domain IP。

## 5. 战略假设验证结论（对照 CLAUDE.md 第 6 节架构假设）

| 原假设 | 验证结果 |
|---|---|
| Glean = Context+Search+Permissions+Connectors+AgentInfra+Governance | ✅ 成立（C01-C19） |
| 我们应聚焦 Domain Intelligence 七层 | ✅ 成立，且 Domain Evaluation 确认为最可防御资产（C22/C23） |
| 修正 1：Glean 正向上移做领域模板（C21）| 薄封装不可持续，必须深推理 |
| 修正 2：Platform API experimental (C15) | Mock-first 是必需（ADR-001） |
| 修正 3：Agent Builder workflow 能力 UNKNOWN (C11) | MVP 自建薄 runtime，不押注 Builder |
