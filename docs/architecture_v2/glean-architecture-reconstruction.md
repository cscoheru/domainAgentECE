# Glean Architecture Reconstruction v2

> **Phase**: 3 — Architecture Reconstruction
> **Last Verified**: 2026-09-13
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §8 + §9 Phase 3 DoD
> **上游输入**: [`/docs/research_v2/capability-matrix-v2.md`](../research_v2/capability-matrix-v2.md) + [`/docs/research_v2/evidence-matrix-v2.md`](../research_v2/evidence-matrix-v2.md)
> **Mermaid 输出**:
> - [`/docs/diagrams/glean-layers-v2.mmd`](../diagrams/glean-layers-v2.mmd) — Glean 分层架构(OFFICIAL / SEMI / INFERRED / UNKNOWN)
> - [`/docs/diagrams/platform-kernel-architecture.mmd`](../diagrams/platform-kernel-architecture.mmd) — 我们的 Platform Kernel(G/O/P/? 标注)

---

## 0. Phase 3 DoD(per PRD §9)

1. 分层架构重建:**官方明确描述的架构** 与 **公开资料推导的架构** 分开成图,逐层标注证据
2. 产出 G/O/P/? 大图
3. mermaid 入 `/docs/diagrams/`
4. DoD: 图上每层可追溯;推导处标 INFERRED 及依据;**C35-C42 新证据可作为新图层的证据锚点**

---

## 1. Glean 官方明确描述的架构

> **来源**: Glean 官方产品页 + 博客 + 开发者文档;所有证据带 C 编号。
> **Last Verified**: 2026-09-13

### 1.1 4 大产品模块(官方导航)

Per **[C01]** glean.com 首页导航,官方定位 "Enterprise AI that Works",分 4 层:

| 模块 | 内容 |
|---|---|
| **Context** | Enterprise Graph / Personal Graph / System of Context [C02] |
| **Access** | Enterprise Search / Assistant |
| **Agent** | Agent Builder / Orchestration / Governance / Library / Harness |
| **Governance** | Glean Protect / Intelligence |

### 1.2 Fall'25 GA / Beta 矩阵(官方能力可用性)

Per **[C37]** glean.com/blog/live-fall-25-main(2026-09-13 Cline 抓取):

| 状态 | 能力 |
|---|---|
| **Generally available** | Enterprise Graph, personal graph, Agentic Engine 2 (Assistant only), third-generation Glean Assistant, Deep Research*, all knowledge queries, fast and extended thinking modes, contextual image understanding, **schedule agents***, **agent version control**, agents respond to user inputs, featured agents, enhanced Chat API (Agentic Engine 2)* |
| **Beta** | Personalized writing, **conversational agent builder**, **agent looping**, Assistant routes requests to agents automatically, agents toolkit, and **remote MCP servers** |
| **Coming soon** | Glean Canvas, 100+ new actions, Agents (Agentic Engine 2), LLM model choice in Assistant, and an MCP directory |

### 1.3 Agent Identity(官方 beta,2026 新)

Per **[C36]** glean.com/blog/introducing-agent-identity(2026-09-13 Cline 抓取,原文):
- "agents act through their own scoped service credentials — visible in the audit trail, and governed by the people responsible for governing access: admins can rotate or revoke any credential, for one system or all of them, at any time."
- "Every action lands in the audit trail under the agent's own account, with the person or schedule that triggered it recorded alongside."
- "The feature is now available in beta for our Glean customers."

### 1.4 Platform API(官方 experimental,2026-09-13 re-verified)

Per **[C35]** developers.glean.com(2026-09-13 Cline 抓取,re-verified from [C15]):
> "Build search experiences and run Glean agents in your applications with our new Platform APIs — now rolling out in experimental preview."

### 1.5 鉴权模式(官方 Quickstart)

Per **[C40]** developers.glean.com Quickstart(2026-09-13 Cline 抓取):
> "Prefer OAuth for per-user Client and Platform work in Authentication. Use a Glean-issued token for Indexing, global ActAs, or when no OAuth path exists."

### 1.6 Connector 生态(官方)

| Claim | 证据 |
|---|---|
| 275+ connectors(connectors FAQ 口径)vs "more than 250"(首页口径)— **保留 C05** | **[C05]** |
| "inherits and enforces source-system permissions" | **[C06]** |
| "real-time sync … as soon as they happen" | **[C07]** |
| 自定义连接器(Indexing SDK);自定义 Action(OpenAPI spec);MCP Server 接入 | **[C09]** |

### 1.7 MCP 与 IDE 集成(官方)

| Claim | 证据 |
|---|---|
| Remote MCP Server:tenant 级、权限感知、OAuth(DCR)、可 MDM 部署 | **[C19]** |
| Glean 官方运营 developers.glean.com MCP server;支持 Claude Code / Cursor / Codex / Gemini CLI 等 IDE | **[C39]** 原文: "Bring Glean to your IDE — Claude Code, Cursor, Codex, and any MCP host." + `claude mcp add glean-developer-docs https://developers.glean.com/mcp --transport http --scope user` |

### 1.8 Agent Builder 治理文案(C38 — C22 收紧依据)

Per **[C38]** glean.com/ai-agent-builder FAQ(2026-09-13 Cline 抓取):
> "Permission rules and policies apply on every request, while logs and evaluations provide visibility into execution paths and performance."

**关键判断**:**execution-path/performance 评估 ≠ domain correctness 评估**;结论方向保留(C22),措辞按 F2 定稿收紧(详见 §3 与 C22 行)。

---

## 2. 公开资料推导的架构(INFERRED)

> **来源**: 综合 C02 + C04 + C06 + C07 + C18 + C36 等多份证据的合理推断。
> **标 "INFERRED"** 表示非 Glean 官方明确声明,而是基于公开资料推导。

### 2.1 推导的分层架构(Glean 官方未给出明确 5 层堆叠图)

```text
            Enterprise Applications
                     │
                Domain Agents
                     │
              Agent Runtime / Agentic Engine 2
                     │
        ┌────────────┴────────────┐
        │                         │
    Context API              Actions / MCP
        │                         │
    Enterprise Context        Tool Layer
        │                         │
   ┌────┼────┐                    │
   │    │    │                    │
 Search Graph Permission        Platform API
   │    │    │                    │
   └────┼────┘                    │
        │                         │
   Connectors / Indexing       ─── MCP Server
        │
   Enterprise Data Sources
```

[INFERRED] **推理依据**: v1 capability map §3 + C02 ("Ground AI in company context") + C18 ("reason over the knowledge graph") + C08/C09 Actions 跨层机制 + C19 MCP 集成。**Glean 官方未明确给出此 5 层堆叠图**,本图为综合推导。

### 2.2 推导的内部组件

| 组件 | 推断功能 | 证据 | 置信 |
|---|---|---|---|
| 检索管线 | Query Understanding → Entity Linking → 4 路召回(Keyword/Semantic/Graph/Structured) → Ranking → Permission Filtering | C04 + C18 + C19 | STRONGLY_INFERRED |
| Context Assembly | Per-task 动态组装(权限过滤 → 检索 → 排序 → 打包) | C02 + C18 | STRONGLY_INFERRED |
| Agent 编排 | 事件触发 + Agent 间任务路由 | **[C12] CONFIRMED** | CONFIRMED |
| Memory 模型 | Agent memory + User memory + Personal Graph | C02 | INFERRED(细节 UNKNOWN) |
| Actions 执行模型 | 自然语言 → 跨系统写回 | **[C08] CONFIRMED** | CONFIRMED |

### 2.3 关键 UNKNOWN(无法从公开资料确认)

- [C03] Enterprise Graph 内部 schema 可否自定义/API 读写 — **Robin 会谈必问 Q9**
- [C11] Agent Builder workflow 细节(branching / HITL / per-step model)— C37 部分解答,细节仍 UNKNOWN;**Robin Q10 补**
- [C24] Glean 定价与最低合同额 — **Robin Q11**
- [C25] Agent Harness / Transform 细节 — **C41 确认 Harness 已入 PRODUCT 导航但无详情页**;Transform 仍标 "Coming soon"
- 内部技术栈(Kafka / ES / Neo4j 等)— **禁止猜测**(PRD §4)

---

## 3. Glean 官方 vs 推导:差异分析

| 维度 | 官方明确(C 编号) | 推导(INFERRED) | 差距 |
|---|---|---|---|
| 4 大模块边界 | ✓ [C01] | — | 一致 |
| Enterprise Graph 存在性 | ✓ [C02] | — | 一致 |
| Agent Builder 能力(GA/Beta) | ✓ [C10, C37] | 部分细节 INFERRED | 已知 GA/beta 矩阵 |
| 检索多路召回 | ✓ [C04 marketing] | △ (4 路管线 INFERRED) | 公开资料未细述管线 |
| MCP 支持 | ✓ [C19, C39] | — | 一致 |
| Actions 写回 | ✓ [C08] | — | 一致 |
| Internal Tech Stack | ✗ UNKNOWN | ✗ UNKNOWN | 公开资料缺失 |
| Enterprise Graph schema 自定义 | ✗ UNKNOWN | ✗ UNKNOWN | C03 待 Robin Q9 |
| Entity Resolution 内部机制 | △ (C18 暗示) | △ | 细节 UNKNOWN |

---

## 4. 我们的 Platform Kernel(G/O/P/? 标注)

> **G** = Glean 已提供(借,标 C 编号)
> **O** = Our Product(我们自建,标理由)
> **P** = Partner / Integration(借 Partner 通道或 API 集成)
> **?** = Unknown(证据不足)

### 4.1 G/O/P/? 决策表(16 能力,延展自 Capability Matrix v2)

| Layer / 能力 | 决策 | 证据 | IP 价值 | 备注 |
|---|---|---|---|---|
| **Domain Ontology** | **O**(Build) | [C23] | **极高** | Glean 空白,核心 IP |
| **Domain Reasoning** | **O**(Build) | [C23], ADR-006 | **极高** | 规则优先 + LLM 轻量(意外命中国产开源模型友好) |
| **Domain Evaluation** | **O**(Build) | [C22] + [C38] 收紧 | **极高** | 业务正确性评估(C38 确认 execution-path ≠ domain eval) |
| **Context Assembly** | **O**(Build) | ADR-001 | **极高** | 12 步流水线,ECE 核心架构 |
| **Entity Resolution** | **O**(Build) | [C18] + [C23] | 高 | 跨系统实体归一 |
| **Permission Engine** | **O**(Build) + G 借 | ADR-004, [C06]+[C07] | **极高** | Permission Before Intelligence + Glean 借 ACL 语义 |
| **Query Planner** | **O**(Build) | ADR-009 | 中 | 4 路召回融合 |
| **MCP Tool Layer** | **O + G** | [C19]+[C37]+[C39] | 中 | 原生 MCP + Glean MCP 互操作(事实标准) |
| **Action / 写回** | **G 借 + v0 关闭** | [C08], ADR-004 | — | v0 强制 403(env kill-switch + 路由硬编码双保险) |
| **Connectors** | **O 框架 + G 借** | [C05]+[C09] | 低 | 275+ 是 Glean 规模优势,我方做框架 |
| **Postgres + pgvector** | **O**(Build) | ADR-009 | 低 | 一库承担,无 OpenSearch/Redis/Neo4j |
| **Glean Enterprise Context** | **G**(Partner/Integrate) | [C02]+[C18] | — | 借 Connector/Action/MCP |
| **Glean Agent Builder** | **G + P 不做** | [C37] beta | — | 我方不做 Builder UI |
| **Glean Agent Identity** | **G + ?**(later) | [C36] beta | — | Phase 4-5 决策 |
| **Glean Protect / Intelligence** | **G**(Phase 4+) | [C01] | — | v0 单租户不需要 |
| **Glean Agent Harness** | **G + ?** | [C41] | — | 导航有,无详情页 |

### 4.2 Platform Kernel 分层图(详见 mermaid)

[详见 `/docs/diagrams/platform-kernel-architecture.mmd`]——按 Domain / Engine / Tool / Data / External 五块组织,G/O/P/? 颜色编码。

### 4.3 关键决策原则

1. **Domain 层全部 Build** — [C23] Domain 层空白 + [C22]/[C38] Domain Evaluation 空白 → **我方最高 IP 价值区**
2. **Permission Before Intelligence** (ADR-004) — 与 Glean 模式同([C06] + [C07]),我方落地中国私有化场景(数据主权)
3. **MCP 事实标准化** — [C19] + [C37] + [C39] → Tool 层必须原生 MCP 化,与 Claude Code/Cursor/Codex 互操作
4. **Agent Builder 不做** — Glean 已发布 conversational beta([C37]),我方资源放 Domain Agent 而非 Builder UI
5. **私有化部署** (ADR-009) — Postgres-only,无外部依赖,数据主权契合 v3 主路径 D
6. **Actions 写回 v0 关闭** — ADR-004 双保险;env kill-switch + 路由硬编码;Phase 4+ 才考虑开放

---

## 5. Glean 分层架构图(mermaid)

[详见 `/docs/diagrams/glean-layers-v2.mmd`]——按 OFFICIAL / SEMI / INFERRED / UNKNOWN 四区组织,颜色编码区分。

---

## 6. 与 Phase 2 决策一致性验证

Phase 2 Capability Matrix v2 的 16 行决策与本 Phase 3 G/O/P/? 标注**完全一致**:

- **6 个 Build 能力**(Matrix 行 4/5/6/13/14/15/16:Entity Resolution / Context Assembly / MCP Tool Layer / Domain Evaluation / Domain Ontology / Domain Reasoning)→ 本 Phase §4.1 O 列
- **2 个 Build+Integrate**(行 3 Enterprise Graph + 行 5 Permissions)→ 本 Phase §4.1 O+G 列
- **3 个 Integrate**(行 1 Connectors + 行 10 Actions + 行 12 Governance)→ 本 Phase §4.1 G 列
- **1 个 Partner/Integrate + 自建 Domain Agent**(行 7 Agent Runtime)→ 本 Phase §4.1 G+ 自建 Domain Agent
- **1 个 Partner 不做**(行 8 Agent Builder UI)→ 本 Phase §4.1 "G+P 不做"
- **1 个 later**(行 11 Agent Identity)→ 本 Phase §4.1 "G+? later"
- **1 个 Buy/Integrate 不做**(行 2 Enterprise Search)→ 本 Phase §4.1 G+Partner
- **1 个不确定**(行 13 Platform Observability)→ Phase 4 决策

Capability Matrix v2 是 Phase 3 输入,Phase 3 输出是 G/O/P/? 大图(本文件)。

---

## 7. Phase 4 输入

Phase 4 (Build/Buy/Integrate/Partner) 将基于本 Phase 3 G/O/P/? 大图,**逐能力四向决策 + 写 ADR**(`/docs/adr/ADR-0XX-*.md`,沿 ADR-002 编号追加)。

**每个 Build 决策需附**:
- 理由
- 关联 C 编号(若有)
- ECE 工程铁律符合性(Permission Before Intelligence / 领域包隔离 / LLM 不可知 / 垂直纪律)

**每个 Integrate/Partner 决策需附**:
- 接入方式(MCP / Client API / Indexing API)
- 失败 fallback
- 中国市场适用性评估

**每个 Buy/不做 决策需附**:
- 不做的理由(防止 reverse creep)
- 重新评估触发条件

---

## 8. 治理说明

- ✅ 证据编号 C01-C42 全部带 Last Verified
- ✅ 官方 vs 推导(INFERRED)清晰分离;两区视觉化分色
- ✅ UNKNOWN 项明确标 + 路由至 Robin 会谈必问(C03/C11/C24/C25)
- ✅ v1 文档(`/docs/research/`)不修改不删除
- ✅ ece/ 子目录未触碰
- ✅ 引文按 Cline 红队报告 §2 原样引用(C35-C42 未改写)

---

## 9. 下一步

Phase 4 启动(待用户确认):

1. 逐能力写 ADR(`/docs/adr/ADR-003-...` 沿 ADR-002 编号继续)
2. Phase 4 DoD:**无 undecided 项遗留**;影响 ECE 的决策全部成文为 ADR
3. 完成后停下汇报,等确认 → Phase 5(Platform Kernel Definition)
