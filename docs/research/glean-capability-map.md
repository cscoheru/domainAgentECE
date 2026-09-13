# Glean Capability Map

> Phase: Gate 1 — Glean Capability Research
> Last Verified: 2026-09-03
> Sources: 官方产品页 / 开发者文档（见文末来源列表）
> 证据等级: CONFIRMED（官方原文）/ STRONGLY INFERRED（官方多页交叉）/ INFERRED（合理推断）/ UNKNOWN（无法确认）

---

## 1. Glean 到底是什么

Glean 官方定位：**"Enterprise AI that Works"** —— 一站式企业 AI 平台（Work AI Platform），不是单一搜索工具。

四层结构（CONFIRMED，glean.com 首页产品导航，2026-09-03）：

```text
┌─────────────────────────────────────────────┐
│ 4. Governance: Glean Protect / Intelligence │
│    （安全、模型路由、AI 网关、用量控制）      │
├─────────────────────────────────────────────┤
│ 3. Agent: Agent Builder / Orchestration /   │
│    Governance / Library / Harness           │
├─────────────────────────────────────────────┤
│ 2. Access: Enterprise Search / Assistant    │
│    （权限感知、个性化、引用接地）             │
├─────────────────────────────────────────────┤
│ 1. Context: Enterprise Graph / Personal     │
│    Graph / System of Context                │
│    底层: 275+ Connectors + 实时权限同步      │
└─────────────────────────────────────────────┘
```

## 2. 模块能力清单

| 模块 | 解决什么问题 | 使用方式 | 置信度 |
|---|---|---|---|
| Enterprise Context | 把分散数据变成 AI 可用上下文 | 平台内置，配置为主 | CONFIRMED（结构细节 UNKNOWN） |
| Enterprise Search | 跨 100+ 源的权限感知检索 | Client API + Platform API | CONFIRMED |
| Connectors & Actions | 275+ 数据源接入 + 自然语言触发跨系统操作 | 配置 + Indexing SDK + OpenAPI 自定义 Action + MCP | CONFIRMED |
| Glean Assistant | 企业知识问答、主动提醒、内容创作、工作执行 | 平台内置 | CONFIRMED |
| Agent Builder | 无代码构建 reasoning-based agents + complex workflows | Builder UI（配置） | CONFIRMED（营销级声明） |
| Agent Orchestration | 事件触发、Agent 间任务路由、外部系统连接 | 配置 + Platform API (Triggers) | CONFIRMED |
| Agent Governance | rollout / share / certify / 权限控制 | 平台内置 | CONFIRMED |
| Agent Observability | adoption、error rate、up/down votes、ROI | 平台内置 | CONFIRMED |
| Glean Intelligence | 模型自动路由、Model Hub、用量控制、AI Gateway | 平台内置 | CONFIRMED |
| Glean Protect | 安全合规、AI 安全扩展 | 平台内置 | CONFIRMED（细节未验证） |
| Developer Platform | Platform API / Client API / Indexing API / Web SDK / Agent Toolkit / Remote MCP Server | API/SDK（Python/TS/Java/Go） | CONFIRMED |

## 3. 逐项详解

### 3.1 Enterprise Context（企业上下文）

- 官方概念：**Enterprise Graph**、**Personal Graph**、**System of Context**（产品导航原文："Ground AI in company context"）。
- 开发者文档声明：Agent "reason over the knowledge graph, not just a prompt window"（在知识图谱上推理，而非仅提示词窗口）。
- **UNKNOWN**：图谱的实体类型、关系 schema、是否可自定义本体、是否可通过 API 读写图谱结构 —— 公开资料未披露。这是对我们的 Domain Ontology 决策最关键的未知项。

**对我们的意义**：Glean 提供"数据接地"，但不提供"业务语义"。控制项-证据类型这类领域本体必须我们自建。

### 3.2 Enterprise Search

- "Search your entire knowledge graph — 100+ connected sources, ranked, permission-aware, and fast, from one query"（CONFIRMED）。
- Search 同时是 Chat / Assistant / Agents 的检索底座 —— Search 在 Glean Agent 架构中是 **context retrieval service** 角色，不是独立产品。

### 3.3 Connectors & Actions

- **275+** 开箱连接器（connectors 页明确写 "275+ out-of-the-box connectors"；首页写 "more than 250"，取更具体数字）。
- 权限："Glean inherits and enforces source-system permissions, so users only see data they're already allowed to access"（CONFIRMED）。
- 实时同步："updates to data and permissions are reflected as soon as they happen in the source system"（CONFIRMED）。
- **Actions（写回能力）**："users to describe a task in natural language and trigger work across connected systems"（CONFIRMED）。
- 扩展方式四种：标准连接器 / Indexing SDK 自定义连接器 / OpenAPI 自定义 Action / MCP Server 接入外部工具。

### 3.4 Agent 体系

详见 `glean-agent-architecture.md`。要点：

- Agent Builder：无代码构建"reasoning agents + complex workflows powered by enterprise context"（CONFIRMED，营销级）。
- Workflow 内部能力（分支/循环/人工审批/逐步选模型）：**UNKNOWN**（帮助中心未抓取成功）。
- 官方已在向上做**领域模板**（官方博客发布 "8 个销售 Agent 套件"）→ 薄封装产品有被平台吞没风险。

### 3.5 Developer Platform（对我们最重要的接口层）

| API/SDK | 内容 | 状态 |
|---|---|---|
| Platform API | Agents / Chat / Search / Skills / Triggers | **experimental preview**（官方标注） |
| Client API | Search / Chat / Documents / Entities / Tools / Verification / Insights / Governance 等 | GA |
| Indexing API | Datasources / Documents / People / Permissions / Custom Metadata | GA |
| Web SDK | renderSearchBox / renderChat / renderSearchResults 嵌入组件 | GA |
| Agent Toolkit | search / employee_search 等工具，适配 LangChain / CrewAI / OpenAI Agents SDK / Google ADK / MCP | GA |
| Remote MCP Server | tenant 级、OAuth(DCR)、权限感知、可 MDM 部署 | GA（默认对合格租户开启） |

**关键判断**：Platform API 仍处 experimental preview + Glean 本身走企业销售流程 → **MVP 阶段无法依赖真实 Glean 环境，Mock-first 是必需而非权宜**（详见 ADR-001）。

## 4. 结论：哪些直接利用 / 哪些不重建

### 直接利用（POC 阶段接入 Glean 后）

- Search / 检索与引用
- Connectors + 实时权限同步
- Actions 写回（create_task / send_message 类）
- Agent 运行底座（可选：见 ADR-002 讨论）
- 治理、审计、模型路由

### 不重建（禁止投入）

- 自研搜索引擎 / 自研连接器平台 / 自研权限系统 / 自研 Agent 平台 / 自建向量库集群

### 我们必须自建（Glean 不提供）

- Domain Ontology（控制-证据映射等）
- Domain Reasoning（充分性/覆盖度/新鲜度推理）
- Domain Workflow（审计准备流程）
- Domain Evaluation（业务正确性评估——Glean observability 只有平台指标）

## 5. 来源

| # | 来源 | URL | 类型 | 验证日期 |
|---|---|---|---|---|
| 1 | Glean 首页 | https://www.glean.com/ | 官方产品页 | 2026-09-03 |
| 2 | Glean Agents 产品页 | https://www.glean.com/product/agents | 官方产品页 | 2026-09-03 |
| 3 | Glean Connectors 页 | https://www.glean.com/connectors | 官方产品页 | 2026-09-03 |
| 4 | Glean Developer Platform | https://developers.glean.com/ | 官方开发者文档 | 2026-09-03 |
| 5 | Glean MCP 指南 | https://developers.glean.com/guides/mcp | 官方开发者文档 | 2026-09-03 |
| 6 | Glean Blog | https://www.glean.com/blog | 官方博客 | 2026-09-03 |
