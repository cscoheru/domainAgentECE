# RESEARCH_PRD_V2.md — Glean Architecture Reverse Engineering & Enterprise AI Platform Kernel

> Version: 2.0
> Status: **Active** —— 本文件取代 `RESEARCH_PRD.md`（v0.2 降级为历史输入，保留不删）
> 日期：2026-09-13
> 触发事件：Glean 已主动联系，**下周沟通 Partner 事项**（联系人 Robin）→ 研究线升版，并与 ECE 开发线并行
> 上游输入：`docs/research/Glean Architecture Research v2.md`（研究问题重定义）、`docs/research/*`（v1 研究产出）、`docs/research/evidence-matrix.md`（C01–C25 证据基线）、`RED_TEAM_REVIEW.md`（v3 战略约束）、根目录 `CLAUDE.md`（治理框架继续有效）

---

# 1. 研究目标变更

旧目标（v1，已废弃）：

> Glean → Domain Product（为 EvidenceIQ / 采购 Agent 寻找立足点）

新目标（v2）：

> **Glean → Reverse Engineering → Enterprise AI Platform Kernel → 再决定哪些自己做、哪些借助 Glean**

最终产出不是"一份漂亮的 Glean 分析报告"，而是：

> **找到 Enterprise AI Platform Kernel 的最小不可替代集合。**

执行主线：

```text
Glean Research
      ↓
Capability Map
      ↓
Architecture Reconstruction
      ↓
Build / Buy / Integrate / Partner Matrix
      ↓
Platform Kernel
      ↓
Reference Applications
      ↓
Demo / Customer Validation
```

---

# 2. 五个核心研究问题

全部研究必须围绕以下五问组织，任何模块文档的结论都要能挂到其中一问：

### Q1. Glean 到底是什么？
不是产品功能列表，而是：**Glean 的 Enterprise AI Platform 是由哪些能力层组成的？**

### Q2. 这些能力之间是什么关系？
画出层间依赖链（Connectors → Index/Knowledge → Enterprise Graph → Search/Retrieval → Context → Assistant/Agent → Tools/Actions），并逐层回答：**这是官方明确描述的架构，还是我们根据公开资料推导的架构？**（这个区别必须显式标注）

### Q3. Glean 的真正技术壁垒在哪里？
不是"Glean 有什么功能"，而是：**如果我今天重新做 Glean，最难复制的是什么？**
候选清单（逐项评估技术含量）：Connector ecosystem / Permission synchronization / Entity resolution / Enterprise Graph / Search ranking / Context assembly / Agent runtime / Governance / Evaluation / Agent identity / Memory。

### Q4. 哪些是 Glean 的规模优势，而不是 MVP 必需品？
对每项能力归入六类：`必须有 / 核心壁垒 / 规模优势 / 成熟度优势 / 商业生态优势 / 暂时没必要`。
（例：Glean 有 275+ connectors，但我们第一版绝不复制。）

### Q5. 如果不用 Glean，我们自己最应该做哪一层？
最终问题：**"如果明天 Glean 不允许我们使用，我们仍然可以独立构建 Enterprise AI Platform 的哪些核心部分？"**
（Partner 会谈反而使此问更关键：谈判筹码 = 我们不可替代的部分。）

---

# 3. 双轨并行（不可互相阻塞）

| 轨道 | 内容 | 治理文件 | 节奏 |
|---|---|---|---|
| **Track A：Glean Architecture Research v2** | 本 PRD。为下周 Partner 会谈与 Build/Buy/Integrate 决策服务 | 根目录 `CLAUDE.md` + 本文件 | Phase 0 在 Partner 会谈前完成（**硬截止**） |
| **Track B：ECE v0 开发** | `ece/` 仓库，Procurement 领域包验证引擎架构 | `ece/CLAUDE.md`、`ece/TASKS.md` | 按 Sprint 0–6 独立推进 |

两轨关系：

1. ECE 是 Platform Kernel 假设的**参考实现**——研究结论未推翻 ECE 已定架构前，Track B 照常推进。
2. Track A 产出 Build/Buy/Integrate/Partner 结论后，以 **ADR 形式回写** Track B（例如：某层改走 Glean Adapter、砍掉某自建模块、或确认全部自建）。
3. ADR 回写之前，任何一轨不得以"等待研究结论"为由阻塞另一轨。

---

# 4. 证据纪律（铁律，违反 = 返工）

1. 每条结论五要素齐全：**Claim / Source / Evidence / Confidence / Last Verified**。
2. 置信度四级（沿用 v1 定义）：`CONFIRMED`（官方原文）/ `STRONGLY_INFERRED`（官方多页交叉印证）/ `INFERRED`（合理推断）/ `UNKNOWN`（无法确认）。
3. **禁止猜测 Glean 内部技术实现**（如 Kafka / Elasticsearch / Neo4j）——除非有公开证据，否则一律标 UNKNOWN。
4. 架构描述必须区分并标注两类：**官方明确描述的架构** vs **由公开资料推导的架构**。
5. **UNKNOWN 不得作为设计前提**；设计若依赖某 UNKNOWN，必须写 ADR 记录假设与验证方式。
6. 证据编号承接 `docs/research/evidence-matrix.md` 的 **C01–C25**，新增从 **C26** 起；所有 v2 文档引用 Glean 能力必须标 C 编号。
7. 引用官方原文时保留 URL 与关键引文，注明抓取日期（本次基线 2026-09-13）。
8. 营销级声明（如产品页 slogan）标注"营销级"，不与工程事实混用。

---

# 5. 资料源优先级与种子清单

优先级（高→低）：

1. 官方产品页 / 官方博客（glean.com）
2. 官方开发者文档（developers.glean.com：Client API / Platform API / Indexing / MCP 指南）
3. 官方 API Reference（schema 即事实）
4. 可靠第三方报道 / 分析 —— 只作旁证
5. 社区 / 论坛 —— 只作线索，不作结论

种子 URL（Phase 1 首批抓取，v2 研究文档已识别的 2025–2026 关键更新）：

```text
https://www.glean.com                                  # 产品导航全量
https://www.glean.com/connectors                       # 连接器/权限/Actions
https://www.glean.com/ai-agent-builder                 # Agent Builder
https://www.glean.com/blog/live-fall-25-main           # Enterprise Graph / 三代 Assistant / Agent 能力
https://www.glean.com/blog/introducing-independent-agents  # 独立 Agent（AI coworkers）
https://www.glean.com/blog/introducing-agent-identity  # Agent Identity（scoped credentials）
https://www.glean.com/blog/glean-partner-network       # Partner Network（Build/Sell/Deliver/Operate/Innovate）
https://developers.glean.com                           # Client API / Platform API / Agent Toolkit / SDK
https://developers.glean.com/guides/mcp                # Remote MCP Server
```

同时：**复核 C01–C25 的原始来源是否仍成立**（v1 抓取于 2026-09-03，距今 10 天，重点核对 experimental preview 状态与产品线变化）。

---

# 6. 九个研究模块

每个模块产出一份文档（路径见 §10），统一结构：研究问题 → 证据表（C 编号）→ 能力判断表（Confirmed/Inferred/Unknown）→ 对 Platform Kernel 的含义（挂到 Q1–Q5）。

## M01 Data / Connector Layer

研究管线：

```text
Enterprise Sources → Connector → Ingestion → Normalization → Index → Permission
```

重点不是统计"有多少 connector"，而是搞清楚 **Connector 到底负责什么**，逐项判断（官方确认 / 推断 / 未知）：

- authentication / crawling / incremental sync / metadata
- document extraction / ACL / user-group mapping
- deletion / freshness / structured data

## M02 Enterprise Context Layer —— 整个研究的中心

Glean 正在把自己明确定义为 **Context Layer**（Enterprise Graph 是 Search、Assistant、Agents 的共同 context foundation）。拆开研究：

- Entity（Person / Organization / Team / Document / Customer / Supplier / Project / Ticket / Product …）
- Relationship（Person→belongs_to→Team；Person→works_on→Project；Project→has_document→Document；Customer→has_activity→Opportunity …）
- Semantic understanding / Enterprise Graph / Personal Graph
- Context assembly / Temporal context / Permissions

**本模块终极问题**：

> Glean 的 Enterprise Graph 到底是不是"Knowledge Graph"？
> 还是 = Knowledge Graph + Search Index + Entity System + Permission + Context Assembly？

如果是后者，我们的 Enterprise Context Engine（ECE）思路就有明确的技术基础与对照系。重点补证据：图谱实体/关系 schema 是否可自定义、可否 API 读写（对应 C03，当前 UNKNOWN，会谈必问）。

## M03 Search / Retrieval Layer

不要停在"支持 keyword + semantic"。要画出管线并逐项标注证据等级：

```text
User Query → Query Understanding → Intent / Entity
    → Candidate Retrieval（Keyword / Semantic / Graph / Structured 四路）
    → Ranking → Permission Filtering → Context Assembly → Answer / Agent
```

判断表（示例格式）：Keyword=Confirmed；Entity-aware=Inferred；Exact ranking algorithm=Unknown。

## M04 Permission / Security Layer

**重要性可能超过 Search**——企业 AI 与普通 RAG 的最大差别之一是"谁可以看到什么"。研究链路：

```text
Identity → User/Group/Role → Source ACL → Document ACL → Entity ACL
    → Search → Context → Agent → Action
```

五个专项：① Search permission ② Agent permission ③ Tool permission ④ Action authorization ⑤ **Agent Identity**（2026 新：Agent 拥有自己的 scoped credentials，而非简单继承运行用户权限）。

同时回答：permission filtering 发生在检索前还是检索后（对应我们 ADR-004 的 Permission Before Intelligence 是否行业共识）。

## M05 Agent Runtime Layer

研究 Agent 的完整生命周期与运行时能力，逐项判断（官方确认 / 推断 / 未知）：

- Planning / Reasoning / Branching / Looping / Tool Calling
- Human Approval（人工审批步骤）/ Model Selection（逐步选模型）
- Workflow 型 vs Reasoning 型 Agent 的官方区分
- Agent-to-Agent（Orchestration / 任务路由）、事件触发、调度
- Memory（Agent memory / User memory / Personal Graph 的关系）
- Verification / Guardrails
- Independent Agents（2026 新：AI coworkers）与 Agent Harness（coming soon，对应 C25）

## M06 Action / Tool Layer

研究工具与动作如何进入 Agent：

- Agent Toolkit（search / employee_search 等内置工具）
- Remote MCP Server（tenant 级、权限感知、OAuth(DCR)、可管控，对应 C19）
- 自定义 Action（OpenAPI spec）
- 写回安全：Actions 权限模型、审批流、审计

**对 Kernel 的含义**：MCP 已成为工具层事实标准 → 我们的 Tool 层应原生 MCP 化（可与 Glean、Claude Code、任何 runtime 互操作）。

## M07 Governance / Evaluation Layer

- Glean Protect（安全合规）与 Intelligence（模型路由 / Model Hub / AI Gateway / 用量控制）的能力边界
- Agent Governance：rollout / share / certify / 权限控制
- Agent Observability 指标：adoption / error rates / votes / ROI（对应 C14）——**重点复核是否仍无业务正确性 / 领域推理质量评估（对应 C22）**

**对 Kernel 的含义**：若 Glean 观测仍停留在平台级指标，则 **Domain Evaluation 是我们最高 IP 价值的空白层**（v1 已判断，v2 需用 2026-09 最新资料复核）。

## M08 Platform / Developer Layer

- Platform API（experimental preview，对应 C15）当前状态：Agents / Chat / Search / Skills / Triggers 覆盖度
- Client API 清单（对应 C16）与官方 SDK（Python/TS/Java/Go，对应 C20）
- **关键新问题**：Agent 定义能否完全在 Builder UI 之外创建/管理（Agent Definition as Code → Runtime API）？
- Web SDK / Agent Toolkit 的 framework-agnostic 程度（对应 C17）

**对 Kernel 的启示**（v2 研究文档明确要求）：Glean 没有把 Agent Builder 限制成封闭低代码平台；我们自己的 Platform Kernel 也**不应设计成"所有东西必须在我们的 UI 里构建"**：

```text
              Agent Developer
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Claude Code   Cursor      Web UI
        │           │           │
        └───────────┼───────────┘
                    ↓
              Agent Definition
                    ↓
                Runtime API
                    ↓
             Enterprise Context
```

这与我们以 Claude Code / Cursor 为主的工作方式高度契合——Agent Definition 必须是版本化文件（code-first），不是锁在 UI 里的配置。

## M09 Partner Boundary —— **优先级最高，Partner 会谈前必须完成**

背景：官方已发布 Partner Network，明确五种角色与 Partner competencies：

```text
Build / Sell / Deliver / Operate / Innovate          ← 五种 Partner 角色
Agent Building / Custom Connectors / Embedded Experiences   ← competencies
```

反向研究 Glean 希望 Partner 在哪里创造价值：

```text
                    GLEAN
  ┌────────────────────────────────────┐
  │ Enterprise Context / Search        │
  │ Permissions / Connectors           │
  │ Agent Runtime / Governance         │
  └──────────────────┬─────────────────┘
                     │
               Partner API
                     │
  ┌──────────────────▼─────────────────┐
  │              PARTNER               │
  │ Domain Solution / Custom Agent     │
  │ Custom Connector / Integration     │
  │ Industry Workflow / Deployment     │
  │ Managed Service                    │
  └────────────────────────────────────┘
```


---

# 7. Capability Matrix v2 格式（Phase 2 核心产出）

升级 v1 的矩阵：不再只判 "Glean Native / Configurable / API"，而是直接服务 Build/Buy/Integrate/Partner 决策。下表为 v2 研究文档给出的**初始假设值**，Phase 2 必须逐格以证据重填或校正——填表不是目的，四向决策才是：

| Capability | Glean Native | API/SDK | Partner Extension | 我们需要自建 | IP 价值 | MVP |
|---|---|---|---|---|---|---|
| Connectors | ✓ | ✓ | ✓ | △ | 中 | 3 个 |
| Enterprise Search | ✓ | ✓ | | × | 低 | × |
| Enterprise Graph | ✓ | ✓ | | △ | 高 | ✓ |
| Entity Resolution | ✓/? | ? | ? | ✓ | **高** | ✓ |
| Permissions | ✓ | ✓ | | △ | **极高** | ✓ |
| Context Assembly | ✓/? | ✓/? | | ✓ | **极高** | ✓ |
| Agent Runtime | ✓ | ✓ | ✓ | △ | 高 | ✓ |
| Agent Builder | ✓ | ✓ | ✓ | × | 中 | × |
| MCP | ✓ | ✓ | ✓ | ✓ | 中 | ✓ |
| Actions | ✓ | ✓ | ✓ | ✓ | 高 | ✓ |
| Agent Identity | ✓ | ? | ? | later | 高 | × |
| Governance | ✓ | ✓ | ✓ | △ | 高 | 基础 |
| Evaluation | ✓ | ? | ? | **✓** | **极高** | ✓ |
| Domain Ontology | | | ✓ | **✓** | **极高** | ✓ |
| Domain Reasoning | | | ✓ | **✓** | **极高** | ✓ |

填写规则：每个非空格必须挂 C 编号证据或显式标 `?`；"我们需要自建"列与 IP 价值列联合产生四向决策：

```text
Build（自建）/ Buy（采购）/ Integrate（集成）/ Partner（借 Glean Partner 通道）
```

---

# 8. 最终架构图（G/O/P/? 标注，Phase 3 核心产出）

先做 Kernel 分层图（旧"Glean × Domain Product"图降级后移），再逐层标注所有权：

```text
                Enterprise Applications
                         │
                    Domain Agents
                         │
                  Agent Runtime
                         │
              ┌──────────┴──────────┐
              │                     │
          Context API            Actions
              │                     │
       Enterprise Context      Tool / MCP
              │
     ┌────────┼─────────┐
     │        │         │
   Search   Graph   Permission
     │        │         │
     └────────┼─────────┘
              │
        Enterprise Data
              │
       Connectors / APIs
```

标注规则：每层标 `G / O / P / ?`——

```text
G = Glean 已提供（引用 C 编号）
O = Our Product（我们自建，说明理由与 IP 价值）
P = Partner / Integration（借 Partner 通道或 API 集成）
? = 证据不足，待会谈验证
```

**这张图完成以后，我们才真正知道自己应该做什么。**（同时产出 mermaid 版本入 `/docs/diagrams/`）

---

# 9. 执行 Phase 与验收（DoD）

> 时间基准：2026-09-13 启动；Partner 会谈在下周（约 09-14 ~ 09-20 之间），Phase 0 为**硬截止**。
> 每个 Phase 完成后：更新 `research_v2/README.md` 进度表 → 汇报 → 等确认再进入下一 Phase。

## Phase 0 — Partner 会谈准备（硬截止：会谈前；预计 0.5–1 天）

- 完成 M09 全部研究（Partner Network 官方资料为准）。
- 产出 `docs/partner/partner-meeting-brief.md`：我方定位选项（Build/Sell/Deliver/Operate/Innovate 各角色的依赖、风险、与我方资产匹配度）+ 推荐定位 + 我方可以展示的资产（ECE 架构思路、领域包、评估体系）+ 谈判要点。
- 产出 `docs/partner/questions-for-glean.md`：必问清单——至少覆盖 ①图谱 schema 可否自定义/API 读写（C03）②Agent Builder workflow 细节（C11）③定价与 Partner 商务条款（C24）④Agent 定义 API 化程度 ⑤中国区 / 私有化部署立场 ⑥Platform API experimental preview 的 GA 时间表。
- DoD：能在 30 分钟内讲清"我们该成为哪种 Partner + 我们有什么 + 我们要什么 + 我们怕什么"。

## Phase 1 — Evidence Collection（1–2 天）

- 种子 URL 全量抓取（§5 清单）+ 复核 C01–C25。
- 新增证据从 C26 起编号，产出 `docs/research_v2/evidence-matrix-v2.md`（含 C01–C25 复核结论列）。
- DoD：九个模块各有骨架证据；无证据处显式 UNKNOWN；所有 URL 注明抓取日期。

## Phase 2 — Capability Map（1–2 天）

- 产出 M01–M08 模块文档（每篇含：研究问题、证据表、能力判断表、对 Kernel 的含义）。
- Capability Matrix v2（§7 格式）全表重填。
- DoD：矩阵每格挂 C 编号或标 `?`；每模块结论挂到 Q1–Q5。

## Phase 3 — Architecture Reconstruction（1 天）

- 分层架构重建：**官方明确描述的架构** 与 **公开资料推导的架构** 分开成图，逐层标注证据。
- 产出 G/O/P/? 大图（§8）+ mermaid 入 `/docs/diagrams/`。
- DoD：图上每层可追溯；推导处标 INFERRED 及依据。

## Phase 4 — Build / Buy / Integrate / Partner（0.5–1 天）

- 逐能力四向决策 + 理由，产出 `docs/architecture_v2/build-buy-integrate-partner-matrix.md`。
- 每个与我们自建倾向相关的决策写 ADR（`/docs/adr/`，沿现有编号追加，当前最大 ADR-002；**注意与 `ece/docs/adr/` 是两套编号，不要混淆**）。
- DoD：无" undecided "项遗留；影响 Track B 的决策全部成文为 ADR。

## Phase 5 — Platform Kernel Definition（0.5–1 天）

- 定义 **最小不可替代集合**：哪些层必须自建、哪些可被 Glean/Partner 替代、哪些缓建。
- 与 ECE 现有架构（`ece/docs/ARCHITECTURE.md`）做映射：已覆盖 / 缺口 / 冗余。
- DoD：一张 Kernel 清单表 + 与 ece/ 模块的映射表 + 缺口的处置建议（补建/换向/砍掉）。

## Phase 6 — Reference Applications（0.5 天）

- 把 EvidenceIQ（审计证据）、Procurement Agent（采购评估）等历史候选**重述为 Kernel 之上的参考应用**：各自用到 Kernel 哪些层、验证哪个假设。
- DoD：`docs/product_v2/reference-applications.md`，每个候选含 Kernel 依赖图。

---

# 10. 输出文件结构

```text
/docs
  /research_v2/
    README.md                          # 模块索引与进度看板
    01-data-connector.md
    02-enterprise-context.md
    03-search-retrieval.md
    04-permission-security.md
    05-agent-runtime.md
    06-action-tool.md
    07-governance-evaluation.md
    08-platform-developer.md
    09-partner-boundary.md
    evidence-matrix-v2.md              # 承接 C01–C25，新增 C26+
  /architecture_v2/
    glean-architecture-reconstruction.md
    platform-kernel-definition.md
    build-buy-integrate-partner-matrix.md
  /product_v2/
    reference-applications.md
  /partner/
    partner-meeting-brief.md           # Phase 0 交付（会谈用）
    questions-for-glean.md             # Phase 0 交付（会谈用）
  /adr/
    ADR-0XX-*.md                       # 沿根目录现有编号追加（当前最大 ADR-002）
  /diagrams/
    platform-kernel-architecture.mmd
    glean-layers-v2.mmd
```

规则：旧 `/docs/research/*`、`/docs/architecture/*`、`/docs/product/*` **一律不修改不删除**，作为 v1 基线被 v2 引用；v2 产出全部落在 `_v2` 目录与 `/partner/`。

---

# 11. STOP Gate（回答完即停）

研究不是无限进行。**当且仅当以下 10 问全部有证据支持的答案时 STOP：**

1. Glean 的核心架构是什么？
2. Enterprise Graph 到底承担什么角色？
3. Context 是如何形成的？
4. Permission 在哪里进入整个链路？
5. Agent Runtime 需要哪些基础能力？
6. Action / MCP / Tool 是如何进入 Agent 的？
7. Governance / Evaluation 在哪里？
8. Glean 哪些能力是它真正的壁垒？
9. 我们自己的 Platform Kernel 最少需要什么？
10. 第一版 Demo 应该证明什么？

回答完：

```text
STOP RESEARCH → ARCHITECTURE → BUILD
```

**不要再继续堆研究文档。** 剩余未知项全部转入 `questions-for-glean.md` 由会谈裁决。

---

# 12. 既有资产的降级与保留

| 资产 | 处置 |
|---|---|
| `RESEARCH_PRD.md`（v0.2） | 降级为历史输入，保留不删 |
| `docs/product/recommended-mvp.md`（EvidenceIQ） | **不删除，降级为 Reference Application Candidate**（不再是产品方向） |
| 采购 Agent（ECE v0 领域包） | 同上——作为 Kernel 的参考实现与参考应用候选，Track B 继续开发不受阻 |
| `docs/research/*`（v1 研究产出） | 保留作为证据基线与对照 |
| `RED_TEAM_REVIEW.md` v3 | 战略约束继续有效（中国市场 / 私有化 / 数据主权）；Glean 路径由"非阻塞期权"升回**并行主选项之一**，最终取舍由本次研究与 Partner 会谈共同裁决 |
| 根目录 `CLAUDE.md` | 治理框架有效；§16 执行入口已指向本文件 |

---

# 13. 禁止事项

1. 禁止猜测 Glean 内部技术实现（无证据一律 UNKNOWN）。
2. 禁止把本研究做成 "Glean Clone 可行性报告"——我们不做横向平台。
3. 禁止为研究而研究：STOP Gate 之后再写新研究文档 = 违规。
4. 禁止因研究阻塞 `ece/` 开发（Track B 独立推进）。
5. 禁止在本 PRD 各 Phase 写产品代码（研究线只产出文档 + ADR）。
6. 禁止把营销级声明当作工程事实（须标注"营销级"）。
7. EvidenceIQ / Procurement 不得在本研究结论产出前被拔高回"产品方向"。

---

# 14. 启动指令（Claude Code 从这里开始）

1. 通读本 PRD + `docs/research/evidence-matrix.md` + `docs/research/glean-capability-map.md`（v1 基线）。
2. **先执行 Phase 0**（Partner 会谈硬截止），再按 Phase 1→6 顺序推进。
3. 网页抓取使用 §5 种子清单起步；无法访问的来源显式标 BLOCKED 并在汇报中说明。
4. 每完成一个 Phase：更新 `docs/research_v2/README.md` 进度 → 停下汇报 → 等人工确认。
5. 完成 STOP Gate 十问后：输出总结报告并 **STOP**。


必答：**"我到底应该成为哪一种 Partner？"**——结合我方资产（ECE 引擎、领域包、评估体系、中国市场与私有化能力）给出角色建议 + 依赖与风险。