# Evidence Matrix（证据矩阵）

> 规则：每条重要结论必须可追溯。禁止把推测写成事实。
> 置信度：CONFIRMED（官方原文）/ STRONGLY_INFERRED（官方多页交叉印证）/ INFERRED（合理推断）/ UNKNOWN（无法确认）
> Last Verified: 2026-09-03

| # | Claim | Source | Source Type | Evidence | Confidence | Last Verified |
|---|---|---|---|---|---|---|
| C01 | Glean 定位为企业 AI 平台（非单一搜索），模块含 Context/Search/Assistant/Agents/Protect/Intelligence | glean.com 首页 | 官方产品页 | 产品导航完整列出上述模块 | CONFIRMED | 2026-09-03 |
| C02 | Enterprise Context 由 Enterprise Graph / Personal Graph / System of Context 构成，用于"Ground AI in company context" | glean.com 首页导航 | 官方产品页 | 导航原文 | CONFIRMED | 2026-09-03 |
| C03 | Enterprise Graph 内部 schema（实体/关系类型）可否自定义、可否 API 读写 | — | — | 公开资料未披露 | UNKNOWN | 2026-09-03 |
| C04 | Search 覆盖 100+ 连接源，ranked、permission-aware | developers.glean.com 首页 | 官方开发者文档 | "Search your entire knowledge graph — 100+ connected sources" | CONFIRMED | 2026-09-03 |
| C05 | 开箱连接器数量 275+ | glean.com/connectors FAQ | 官方产品页 | FAQ 原文 "275+ out-of-the-box connectors"；首页写 "more than 250"（取更具体值） | CONFIRMED | 2026-09-03 |
| C06 | 连接器继承并强制源系统权限 | glean.com/connectors FAQ | 官方产品页 | "inherits and enforces source-system permissions" | CONFIRMED | 2026-09-03 |
| C07 | 数据与权限支持实时同步 | glean.com/connectors FAQ | 官方产品页 | "real-time sync … as soon as they happen" | CONFIRMED | 2026-09-03 |
| C08 | Actions：自然语言描述任务并跨连接系统触发操作（写回能力） | glean.com/connectors FAQ | 官方产品页 | "supports actions … trigger work across connected systems" | CONFIRMED | 2026-09-03 |
| C09 | 自定义连接器用 Indexing SDK；自定义 Action 用 OpenAPI spec；可接 MCP Server | glean.com/connectors | 官方产品页 | 原文三段说明 | CONFIRMED | 2026-09-03 |
| C10 | Agent Builder 支持"reasoning-based agents 和复杂 workflow，powered by enterprise context" | glean.com/product/agents | 官方产品页 | "Build, test, and iterate with ease…" | CONFIRMED（营销级） | 2026-09-03 |
| C11 | Agent Builder workflow 细节：分支/循环/人工审批步骤/逐步模型选择 | — | — | 帮助中心页面未抓取成功，公开产品页未展开 | UNKNOWN | 2026-09-03 |
| C12 | Agent Orchestration：事件触发、Agent 间任务路由、连接外部系统 | glean.com/product/agents | 官方产品页 | "Trigger agents from key events, route tasks between agents…" | CONFIRMED | 2026-09-03 |
| C13 | Agent Governance：rollout / share / certify / 规模化控制 | glean.com/product/agents | 官方产品页 | "Roll out, share, and certify agents with the controls needed…" | CONFIRMED | 2026-09-03 |
| C14 | Agent Observability：adoption、error rates、upvotes/downvotes、ROI | glean.com/product/agents | 官方产品页 | "Get deep insights into adoption, error rates…" | CONFIRMED | 2026-09-03 |
| C15 | Platform API（Agents/Chat/Search/Skills/Triggers）处于 experimental preview | developers.glean.com 首页 | 官方开发者文档 | "now rolling out in experimental preview" | CONFIRMED | 2026-09-03 |
| C16 | Client API 覆盖 Search/Chat/Documents/Entities/Tools/Verification/Insights/Governance 等 | developers.glean.com 导航 | 官方开发者文档 | Client API Reference 目录列表 | CONFIRMED | 2026-09-03 |
| C17 | Agent Toolkit 提供 search / employee_search 工具，适配 LangChain/CrewAI/OpenAI Agents SDK/Google ADK/MCP | developers.glean.com 首页 | 官方开发者文档 | 示例代码 + "Framework-agnostic by design" | CONFIRMED | 2026-09-03 |
| C18 | Glean Agents "reason over the knowledge graph, not just a prompt window" | developers.glean.com 首页 | 官方开发者文档 | Agents 卡片原文 | CONFIRMED | 2026-09-03 |
| C19 | Remote MCP Server：tenant 级、权限感知、OAuth(DCR)、可禁用/管控、可 MDM 部署 | developers.glean.com/guides/mcp | 官方开发者文档 | 整页指南 | CONFIRMED | 2026-09-03 |
| C20 | 官方 API 客户端：Python / TypeScript / Java / Go | developers.glean.com 首页 | 官方开发者文档 | 安装命令列表 | CONFIRMED | 2026-09-03 |
| C21 | Glean 官方向上做领域模板（如"8 个销售 Agent 套件"） | glean.com/blog | 官方博客 | "The new playbook for sales productivity starts with agents"（2025-12-11） | CONFIRMED | 2026-09-03 |
| C22 | Glean Agent 观测不含业务正确性/领域推理质量评估 | 推断 | — | C14 列出的指标全部是平台级（adoption/error/votes/ROI），无业务正确性维度 | STRONGLY_INFERRED | 2026-09-03 |
| C23 | Domain 层（领域本体/推理/评估）是 Glean 未覆盖的空白 | 推断 | — | 由 C03 + C22 交叉推断 | STRONGLY_INFERRED | 2026-09-03 |
| C24 | Glean 定价模式与最低合同额 | — | — | 公开资料无定价 | UNKNOWN | 2026-09-03 |
| C25 | Glean Agent Harness（新产品）与 Glean Transform（coming soon）能力细节 | glean.com 首页 | 官方产品页 | 导航标注 "Coming soon"，无详情 | UNKNOWN | 2026-09-03 |

## 使用规则

1. 任何架构/产品文档引用 Glean 能力时，必须标注本文 C 编号。
2. UNKNOWN 项不得作为设计前提；如设计依赖某 UNKNOWN 项，必须在 ADR 中记录假设与验证方式。
3. 下次研究迭代优先补齐：C03（图谱 schema）、C11（Agent Builder workflow 细节）、C24（定价）。
