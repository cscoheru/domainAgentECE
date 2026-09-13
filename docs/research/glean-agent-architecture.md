# Glean Agent Architecture（研究）

> Phase: Gate 1
> Last Verified: 2026-09-03
> 关联证据：C10–C14, C15, C17, C18, C21（见 evidence-matrix.md）

## 1. 官方 Agent 架构图景（公开可确认部分）

```text
User / Event Trigger (Orchestration)
        ↓
Agent（Builder 中定义: instructions + context + tools）
        ↓
Retrieval: Enterprise Search / Knowledge Graph（permission-aware）
        ↓
Tools / Actions: 连接器动作 / 自定义 OpenAPI Action / MCP 工具
        ↓
Answer / Action（带引用）
        ↓
Governance: rollout / share / certify
        ↓
Observability: adoption / errors / votes / ROI
```

## 2. Agent Builder（无代码层）

- **CONFIRMED**：支持构建 "reasoning-based agents and complex workflows powered by enterprise context"；有构建-测试-迭代循环；有 Agent Library（可复用 Agent）；有部署/分享/认证机制。
- **UNKNOWN（C11）**：分支、循环、人工审批步骤、每步模型选择、版本管理、导入导出等工程细节。**在验证 C11 前不得假设 Agent Builder 能承载我们的 Domain Workflow** —— MVP 自建轻量 workflow 执行器（见 agent-runtime.md）。

## 3. Agent Orchestration（编排层）

- **CONFIRMED（C12）**：事件触发、Agent 间任务路由、外部系统连接。
- 对我们的意义：POC 阶段若把我们的 Domain Agent 挂到 Glean，Orchestration 是入口候选（Platform API Triggers）。

## 4. 开发者侧 Agent 能力（代码层）

| 能力 | 说明 | 置信度 |
|---|---|---|
| Platform API Agents | 以 API 创建/运行 Agent（experimental preview） | CONFIRMED (C15) |
| Agent Toolkit | search / employee_search 等工具导出为 LangChain / CrewAI / OpenAI Agents SDK / Google ADK / MCP 工具 | CONFIRMED (C17) |
| Client API Agents | 查询/管理用户可见 Agent | CONFIRMED (C16) |
| 知识图谱推理 | "reason over the knowledge graph, not just a prompt window" | CONFIRMED (C18) |

**关键判断**：Glean 开发者生态是 **"把 Glean 检索/人员能力作为工具提供给任意 Agent 框架"**，而不是"必须在 Glean 里跑 Agent"。这意味着我们的 Domain Agent 完全可以自建 runtime、通过 Context Adapter 调 Glean 检索 —— 与 CLAUDE.md 架构原则一致。

## 5. 战略风险：平台向上侵蚀

- 官方博客已发布销售 Agent 套件（C21）、Agent Library 提供可复用 Agent。
- **含义**：任何"Glean + 一层薄提示词"的产品都会被平台模板吞没。我们的护城河必须落在：
  1. 深层 Domain Ontology（如审计控制-证据映射，Glean 不可能有）
  2. Domain Reasoning（充分性/覆盖度/新鲜度/抽样推理）
  3. Domain Evaluation（业务正确性基准与回归集）
- 这三项共同构成可防御的 Domain Intelligence 资产。

## 6. 对 MVP 的直接影响

1. MVP 不用 Glean Agent Builder 承载 workflow（C11 UNKNOWN → 不作为前提）。
2. MVP 自建窄而深的 Domain Agent（Role/Goal/Context/Ontology/Knowledge/Tools/Workflow/Reasoning/Guardrails/Evaluation/Output/KPI 十二要素齐全）。
3. POC 阶段评估两条集成路径：a) Domain Agent 通过 Glean 检索工具取 context；b) Domain Agent 发布为 Glean 可调用 Agent/MCP 工具。
