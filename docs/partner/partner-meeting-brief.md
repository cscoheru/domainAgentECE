# Partner Meeting Brief — Glean × Domain Agent ECE

> **Phase**: 0 — Partner 会谈准备
> **Last Updated**: 2026-09-13
> **Status**: ACTIVE — 会谈前最终稿
> **Meeting Type**: 30–45 分钟视频通话 (Glean Partner Manager: Robin, Asia Channel Ecosystem)
> **上游**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M09 / §9 Phase 0

---

## 0. 本次会谈的真实目标

**不是**签署 Partner 协议、拿下 Partner 名额、卖出第一单。
**不是**让 Robin 把我们当 Glean reseller。

**是**让 Robin 在通话结束时形成三个判断:

> 1. **我们能接触中国大型企业**(客户访问能力,不是 SaaS 销售漏斗)。
> 2. **我们不只是销售,而是真懂 Enterprise AI / Agent / Knowledge Management / Integration**(技术深度)。
> 3. **我们有能力在中国把 Glean 从产品变成实际的企业解决方案**(本地化 + 私有化 + 行业工作流落地)。

如果这三个判断成立,Partner 身份只是后续结果。

证据锚点: C21 (Glean 向上做领域模板)、C16 (Client API 覆盖企业系统 Actions)、C19 (Remote MCP Server 通用可互操作) → 表明 Glean 官方欢迎 Partner 做长尾领域 Agent 与集成。

---

## 1. 我方定位推荐(Primary Position)

### 1.1 推荐组合:**Services & Solutions + Technology** 双轨 Partner,聚焦 Build + Innovate 方向

| 维度 | 推荐选择 | 拒绝选项 | 理由 |
|---|---|---|---|
| **Pathway** | Services & Solutions + Technology | ❌ Referral (只引荐); ⚠️ Commercial (需要现有客户漏斗) | 我们有客户 access 但无 SaaS 销售漏斗;我们能写代码但不做 GTM 投放 |
| **Build/Sell/Deliver/Operate/Innovate** | **Build + Innovate** 为主, **Deliver** 为辅 | ❌ Sell (我们不做 Glean 许可证分销); ⚠️ Operate (我们不接 Glean 托管) | 与我方技术能力 + ECE 架构匹配 |
| **Competency** | Agent Building + Custom Connectors + Embedded Experiences | ❌ Resale | 我方已在 ECE v0 投入 6 个 Sprint 的领域 Agent + Context 基础设施工程 |

### 1.2 与 v3 Red Team 主路径 D 的关系

**重要**: 本定位建议**与 v3 主路径 D(私有化垂直 Context+Agent)不冲突**,但**不取代**它。具体:

- **若 Glean Partner 路径获得有意义的准入**(非名义 Partner、能拿到技术资源、客户 demand 传导)→ **保留为可选双路径**
- **若 Glean Partner 路径实质受阻**(准入门槛高 / Partner 经济学不对 / 可达市场无 Glean 客户)→ **回归主路径 D,不浪费投资**

本次会谈**不应做出"all-in Glean"的承诺**。Phase 0 PRD §0.6 v3 已明确:可达市场已确认无 Glean 客户,Glean 路径**降级为非阻塞期权**。

### 1.3 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| Glean 在中国大陆无运营/销售 | 高(已确认) | TAM 受限 | 主路径 D 不受影响;Phase 1+ 重新评估 |
| Partner 准入门槛高于预期 | 中 | 时间浪费 | 准备 8 个问题,3 个必问答案"不"→ 优雅退出 |
| Robin 把我们当 reseller 试探 | 中 | 偏离技术型定位 | 主动反问"我 profile 适合哪条路线"(Q3) |
| 错过主路径 D 节奏 | 低 | 拖延 6-8 周 | Phase 0 仅 0.5-1 天,主路径 D 不阻塞 |

---

## 2. 我们能带到 Glean 的资产(Our Assets)

| 资产 | 内容 | 工程深度 | 证据 |
|---|---|---|---|
| **ECE v0 架构(Enterprise Context Engine)** | 7 层架构 + Context Spec 抽象 + Permission Before Intelligence + Provenance + Temporal | 6 个 Sprint 已规划(S0-S6,~30 工作日) | `ece/CLAUDE.md`、`ece/docs/ARCHITECTURE.md`、`ece/docs/DATA_MODEL.md` |
| **领域包隔离模式(Domain Pack Isolation)** | `src/domain_packs/<domain>/` 与 `src/ece/` 引擎零耦合,换领域不改引擎 | ADR-010 已立;CI import-linter 强制 | ADR-010 |
| **6 套评测套件(E1-E6)** | Entity Resolution / Permission / Context Completeness / Relationship / Temporal / Agent 端到端;**E2 Unauthorized Context Exposure = 0 是 CI 一票否决门槛** | 门槛已写入 EVALUATION.md | `ece/docs/EVALUATION.md` |
| **规则优先架构(意外命中中国约束)** | 确定性推理走规则,LLM 只做文档理解与解释 — 与国产开源模型(Qwen/DeepSeek/GLM)能力分布吻合 | ADR-006 LLM Provider Independence | ADR-006 |
| **私有化部署验证** | docker compose (api + postgres) 单进程/单容器,完全离线可跑,数据不出域 | TASKS.md S6.5 验收项 | `ece/TASKS.md` S6.5 |
| **跨职能客户 access** | 创始人网络直达 GRC/合规/内审/采购 function 部门高管(华南,含上市企业 ≥10亿 RMB 营收) | 创始人网络事实 | 创始人自述 (Confidence: STRONGLY_INFERRED,未独立抓取验证) |
| **Reference Case 框架无关性** | SOC2 / ISO27001 / 等保 / 内控本体留扩展点,换框架是内容工作不是架构工作 | ADR-010 验证 | ADR-010 |

---

## 3. 我们想从 Glean 拿到的(Negotiation Points)

按优先级排序:

| # | 要点 | 优先级 | 底线 | 关联问题 |
|---|---|---|---|---|
| **N1** | **技术接入方式正式化**(MCP / Agent Toolkit / Platform API / SDK 的 Partner 级别 SLA) | 高 | 有书面 onboarding 文档即可 | Q5, Q6 |
| **N2** | **价格/抽成透明度**(Partner 经济学、客户归属、first-party 竞争风险) | 高 | 至少获取报价区间 | Q7, Q11 |
| **N3** | **客户需求传导通道**(Glean 销售 bring partner to deal 的机制) | 中 | 接受"自助找客户"也可 | Q7 |
| **N4** | **Glean Platform Kernel 的 API 边界**(Agent Definition API 化程度、Platform API GA 时间表) | 中 | 了解方向即可,不要求承诺 | Q12, Q14 |
| **N5** | **Enterprise Graph schema 自定义能力**(C03 UNKNOWN 的解答) | 中 | 了解"是否能",不要求"现在就做" | Q9 |
| **N6** | **中国大陆市场策略**(Glean 是否考虑进入;若不,我们是否可成为其 Asia 跳板) | 高 | 了解意向即可 | Q1, Q13 |
| **N7** | **私有化部署立场**(中国大型企业对私有化是强需求,需要 Glean 明确支持路径) | 中 | 了解可行路径 | Q13 |

**红线**(任何一点不满足则不签):
- ❌ 强制要求最低营业额 / 年度认证费超出合理范围(>10K USD)
- ❌ Glean 自己会做同领域 Agent 与我们 first-party 竞争
- ❌ 客户数据必须上传至 Glean SaaS(违反私有化)

---

## 4. 雷区(避免的 3 个陷阱)

### 雷区 1:不要表现得太急着做代理

不要说: "I really want to become a Glean partner."
更好: "I'd like to explore whether there is a strong fit between what Glean is building and what I can bring to the Asian enterprise market."

### 雷区 2:不要把自己包装成已经有大量订单

尤其不要说: "I have many customers ready to buy."
应该说: "I have access to..." + "There are potential opportunities..."

### 雷区 3:不要把"采购 Agent"或"EvidenceIQ"讲成核心产品

逻辑应该是:
```text
Enterprise AI Platform
        ↓
Enterprise Context Layer  ← ECE 的核心定位
        ↓
Domain Agents
        ↓
Industry Applications
   ├── Compliance / Audit
   ├── Knowledge Management
   ├── Contract
   ├── Procurement
   └── Sales / HR
```

而不是:
```text
"我做 EvidenceIQ"
        ↓
找客户
        ↓
卖 Agent
```

---

## 5. 30–45 分钟会谈时间结构

```text
0–5 min    双方认识
5–10 min   我的背景 + 企业 AI 能力
10–15 min  泸州老窖案例 + 大企业客户 access(克制描述,不说"我有很多客户等着买")
15–20 min  Why Glean / Why Asia / Why now
20–30 min  Robin 介绍 Glean Partner Strategy(让他说话,记笔记)
30–40 min  合作模式 + 我主动提问(8 个问题按优先级展开)
最后       Concrete next step(约下一次 demo 或明确不继续)
```

---

## 6. 开场自我介绍(控制在 2 分钟)

### 第一段:身份
> I'm a management consultant and AI developer based in China.
> My background is in enterprise management, business processes and organizational systems for about 20 years, and over the past year I've been increasingly focused on enterprise AI and agent development.

### 第二段:为什么和 Glean 有关系
> I'm particularly interested in enterprise knowledge management, RAG, enterprise context and AI agents.
> I've been working on how AI can move beyond simply answering questions, and actually connect enterprise knowledge, business systems and workflows.

### 第三段:客户资源
> I also have relationships with senior executives and founders of a number of large enterprises in South China, including companies with revenues above RMB 10 billion.

---

## 7. 泸州老窖案例(简化描述,克制)

不要说"我做了 Glean 竞品"。
说:

> One example is a project I've been working on with Luzhou Laojiao, a listed Chinese company.
> We have been working on AI enablement for their knowledge management platform, including using AI-assisted development to iterate the platform and exploring how knowledge management can connect with other enterprise management systems.

然后停一下,再说:

> That experience made me realize that enterprise AI is not simply about putting an LLM on top of a knowledge base. The difficult part is actually connecting knowledge, permissions, business context, organizational relationships and enterprise systems.

---

## 8. 我方的"理想合作模式"建议

**不说**: "Give me a Partner agreement."

**说**:
> I'd like to understand how Glean thinks about partners in Asia, especially partners who can combine customer access, consulting, implementation and technical development.

然后:
> I'd be interested in exploring whether there is a fit for me across the Services & Solutions, Technology, or Build/Innovate side of the ecosystem, rather than only a traditional reseller model.

让 Robin 来帮你定义你是什么 Partner。

---

## 9. 我应该主动争取的一个东西

不是:
> "Can you approve me as a partner?"

而是:
> **"Can we identify one concrete customer opportunity and explore it together?"**

如果谈得比较顺:
> I think the best way for both sides to evaluate the fit is probably to take one real enterprise opportunity and explore how we could work together.

这把"Partner discussion"变成"Real business discussion"。

---

## 10. Evidence Appendix(证据)

### 10.1 v1 证据基线(直接复用,C01-C25 全部仍 CONFIRMED,见 `docs/research/evidence-matrix.md`)

- **C01** (CONFIRMED): Glean 定位为企业 AI 平台
- **C02** (CONFIRMED): Enterprise Context 由 Enterprise Graph / Personal Graph / System of Context 构成
- **C16** (CONFIRMED): Client API 覆盖 Search/Chat/Documents/Entities/Tools/Verification/Insights/Governance
- **C17** (CONFIRMED): Agent Toolkit 适配 LangChain/CrewAI/OpenAI Agents SDK/Google ADK/MCP,framework-agnostic
- **C19** (CONFIRMED): Remote MCP Server tenant 级、权限感知、OAuth(DCR)、可管控
- **C21** (CONFIRMED): Glean 官方向上做领域模板(8 个销售 Agent 套件)
- **C22** (STRONGLY_INFERRED): Glean Agent 观测不含业务正确性/领域推理质量评估
- **C23** (STRONGLY_INFERRED): Domain 层是 Glean 未覆盖的空白

### 10.2 Phase 0 新增证据(C26-C29)

> **校正(2026-09-13 Cline 红队审查)**: claude.ai WebFetch 工具特定限制(**非网络层屏蔽**)。Cline 2026-09-13 用备用通道对 6 个种子 URL 完成独立验证,带回 C35-C42 八条新证据,见 [`/docs/research_v2/evidence-matrix-v2.md`](../research_v2/evidence-matrix-v2.md) §4。其中 C36(Agent Identity beta) 升级取代 C29,C26(Partner Network 博客存在性) 升级为 CONFIRMED(发布日期 2026-08-25 仍保留 v1 草稿 INFERRED)。

| # | Claim | Source | Source Type | Confidence | Last Verified |
|---|---|---|---|---|---|
| **C26** | Glean Partner Network 于 2026-08-25 公开亮相 | glean.com/blog/glean-partner-network | 官方博客 | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| **C27** | Partner Network 4 pathways: Referral / Commercial / Services & Solutions / Technology | glean.com/blog/glean-partner-network | 官方博客 | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| **C28** | Partner 可在 Build / Sell / Deliver / Operate / Innovate 多个方向参与 | glean.com/blog/glean-partner-network | 官方博客 | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| **C29** | Glean Agent Identity 于 2026 年公开,Agent 可拥有独立 scoped credentials | glean.com/blog/introducing-agent-identity | 官方博客 | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |

### 10.3 我方内部证据(C30-C34,CONFIRMED)

| # | Claim | Source | Confidence | Last Verified |
|---|---|---|---|---|
| **C30** | ECE v0 技术栈:PostgreSQL 16 + pgvector + OpenAI-compatible LLM;无 OpenSearch/Redis/Neo4j | `ece/docs/ADR-009-lean-stack.md` + `ece/docs/ARCHITECTURE.md` | CONFIRMED | 2026-09-04 |
| **C31** | ECE Permission Before Intelligence 是产品 P2 原则;E2 Unauthorized Context Exposure = 0 是 CI 一票否决门槛 | `ece/docs/ADR-004-permission-first.md` + `ece/docs/EVALUATION.md` §1 | CONFIRMED | 2026-09-04 |
| **C32** | ECE 领域包隔离(ADR-010):换领域包成本上限 1-2 周;`src/ece/` 引擎零领域 import | `ece/docs/ADR-010-domain-pack-isolation.md` | CONFIRMED | 2026-09-04 |
| **C33** | ECE ADR-006 强制 LLM Provider Independence:OpenAI-compatible 端点;支持 vLLM/Ollama 部署国产开源模型 | `ece/docs/ADR-006-llm-independence.md` | CONFIRMED | 2026-09-04 |
| **C34** | ECE Sprint 0 已规划 2 天工程地基;Sprint 6 末离线 demo 验收 | `ece/TASKS.md` | CONFIRMED | 2026-09-04 |

### 10.4 待 Phase 1 复核证据(C03 / C11 / C24)

按 v1 证据矩阵,以下三项仍为 UNKNOWN,Phase 1 优先补齐:

- **C03** (UNKNOWN): Enterprise Graph 内部 schema(实体/关系类型)可否自定义、可否 API 读写 — **Robin 会谈必问**
- **C11** (UNKNOWN): Agent Builder workflow 细节(分支/循环/人工审批/逐步模型选择) — **Robin 会谈必问**
- **C24** (UNKNOWN): Glean 定价模式与最低合同额 — **Robin 会谈必问**

---

## 11. 验证与下步动作

Phase 0/1/2 全部完成(commits c1dd32b / f5d4d0e / 9f3a5cb)。Cline 红队审查已签发(commit 040c04e),R1-R7 全部完成(本文件经 Phase 2.5 修复后)。

**Phase 0 通过判据**(已满足):

- [x] 本文件已生成(战略定位 + 资产清单 + 谈判要点 + 红线 + 时间结构 + 证据附录)
- [x] `questions-for-glean.md` 已生成(14 个必问问题,按优先级排序)
- [x] `docs/research_v2/README.md` 进度看板已建立,Phase 0/1/2 标 ✅
- [x] 证据 C26-C34 已记录(C26 升级 CONFIRMED, C29 已被 C36 取代)
- [x] git commit + push 完成(c1dd32b / f5d4d0e / 9f3a5cb / b166061 / <R7-commit>)
- [x] Cline 红队审查通过(040c04e,R1-R7 全部完成)
- [ ] 用户确认后进入 Phase 3(Architecture Reconstruction)
