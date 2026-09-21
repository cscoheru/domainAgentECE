# FOUNDATION_REUSE_MATRIX.md

> **Foundation Reuse Study 的矩阵产出。**
> 本文件回答的是「**哪一层用什么**」，**不是**「哪个项目最好」。
>
> 指令 §4 明令禁止的输出：Best / Winner / 1st-2nd-3rd / Overall Score /
> 推荐某项目作为唯一底座。**本文件不含这些**，因为候选项目承担的架构层级本就不同，
> 排名会把不同层的东西放在同一把尺子上。
>
> 最终结论见 `FOUNDATION_REUSE_STUDY.md`；代码出处见 `FOUNDATION_REUSE_CODE_NOTES.md`。
> Last Verified: 2026-09-20

---

## 1. 四种「复用」的定义（指令 §6）

判定每个候选对每项能力时，必须区分这四个等级。**"借鉴"与"复用"不可混为一谈。**

| Level | 名称 | 含义 | 允许的动作 | 不允许的动作 |
|---|---|---|---|---|
| **0** | No Reuse | 完全不相关 | — | — |
| **1** | Conceptual Reference | 只能借鉴 | 借鉴 architecture / data model / design pattern / terminology | **不能直接拿代码** |
| **2** | Component Reuse | 可复用独立模块 | 复用 parser / graph abstraction / provenance component / rule engine / storage adapter / ontology parser / evaluator | **不能把整个项目作为 Kernel** |
| **3** | Foundation Reuse | 核心数据模型 / engine 作为我们的底层基础 | fork / wrapper / adapter / extension，**我们的 Kernel 语义层定义在其上** | 不能把它的业务语义当成我们的 |
| **4** | Direct Adoption | 项目本身成为某一层的主要实现 | 直接采用，不重新实现它 | 不能与 Kernel 语义混淆 |

> **Level 3 与 Level 4 的分界**：Level 4 是「这一层就它了」（例：Trigger.dev → Workflow Execution）；
> Level 3 是「它的数据模型/引擎做底，语义由我们定义」。
> **Level 3 对 Kernel 层尤其危险**——因为 Kernel 的语义正是我们唯一不可让渡的资产，
> 所以 `Kernel` 归属的能力拿到 Level 3 时必须逐条论证语义层确实是我们的。

---

## 2. 能力归属（V3 冻结边界，引用原文，不重新定义架构）

来源：`docs/v3/KERNEL_BOUNDARY.md:63-90`（主边界矩阵 26 行）、
`docs/v3/KERNEL_BOUNDARY.md:98-109`（V3 收口后 Kernel 仍为 PRIMARY 的 11 行）、
`docs/v3/V3_CLOSEOUT.md:27-44`（Kernel 核心 + 明确移出 Kernel）。

| Capability | V3 Owner | 原文依据 | Keep Ourselves | 现有实现状况（ECE v0 实况） |
|---|---|---|---|---|
| **Context Model**（含 Entity/Relation/Temporal/Permission scope） | **Kernel** | `V3_CLOSEOUT.md:30` | **YES** | ✅ 已实现：`context_items` / `context_requests` / `entities` / `relationships`（含 `valid_from`/`valid_to`） |
| **Domain Ontology** | **Kernel** | `KERNEL_BOUNDARY.md:68` 行 4；ADR-009 | **YES** | ✅ 已实现：`ece/src/ece/domain_packs/procurement/ontology.py` |
| **Entity / Relationship** | **Kernel**（归一后） | `KERNEL_BOUNDARY.md:67` 行 3 | **YES** | ✅ 已实现：`entities` / `entity_aliases` / `entity_revisions` / `relationships` / `resolution_pending` |
| **Business Rules**（Deterministic） | **Kernel** | `V3_CLOSEOUT.md:32` | **YES** | ✅ 已实现：`domain_packs/procurement/agent/rules.py` |
| **Decision** | **Kernel** | `KERNEL_BOUNDARY.md:72` 行 8；`KERNEL_ARCHITECTURE_V3.md:269` | **YES** | ❌ **尚无对象/表**（Kernel V0 新建） |
| **Evidence**（业务证据） | **Kernel** | `KERNEL_BOUNDARY.md:70` 行 6；`KERNEL_ARCHITECTURE_V3.md:267` | **YES** | ❌ **尚无对象/表**（只有 `ontology_rejections` 与 `context/provenance.py`，二者都不是 Evidence） |
| **Provenance** | **Kernel**（Evidence 的组成部分） | `KERNEL_ARCHITECTURE_V3.md:260-275` 对象表 provenance 列 | **YES** | ⚠️ 部分：`context/provenance.py`（Context 溯源），非业务证据溯源 |
| **Context Update** | **Kernel** | `V3_CLOSEOUT.md:102`（链尾决定"是不是规则引擎+RAG"） | **YES** | ❌ **尚无**（V0 必须真的实现这一步） |
| **Temporal Context** | **Kernel** | `KERNEL_BOUNDARY.md:88` 行 24 | **YES** | ✅ 已实现：`relationships.valid_from/valid_to` |
| **Domain Workflow Specification** | **Kernel**（**仅业务判据 + 责任人 + 审批要求**） | `KERNEL_BOUNDARY.md:73` 行 9；`:152-154` 硬收窄 | **YES** | ⚠️ 部分：`context_specs/evaluate_purchase_request.yaml` |
| **Policy**（业务规则/合规策略） | **Kernel** | `KERNEL_BOUNDARY.md:75` 行 11 | **YES** | ⚠️ 部分 |
| **Permission Enforcement** | **Kernel + Provider** | `KERNEL_BOUNDARY.md:65` 行 1；`:117-136` | **Partial** | ✅ 已实现强制点：`acl_entries` + `permissions/`（数据访问层强制）；policy **来源**可外包 |
| **Domain Evaluation** | **Kernel** | `KERNEL_BOUNDARY.md:76` 行 12 | **YES** | ✅ 已实现：`data/eval/e1..e6.json` + `tests/evaluation/` |
| **Knowledge Retrieval**（召回/融合/排序机制） | **Provider** | `V3_CLOSEOUT.md:22` 拆分；`:40` 移出 | **NO** | — |
| **Enterprise Search** | **Provider** | `KERNEL_BOUNDARY.md:86` 行 22 | **NO** | 明确**不自建**横向搜索 |
| **Graph Storage** | **Infrastructure** | `KERNEL_ARCHITECTURE_V3.md:294` | **NO** | V0/V1 用 PostgreSQL 单库承担 |
| **Vector Search** | **Provider** | `KERNEL_ARCHITECTURE_V3.md:294`（pgvector） | **NO** | — |
| **Agent Runtime / Harness** | **Runtime** | `KERNEL_BOUNDARY.md:79` 行 15 | **NO** | — |
| **Agent Loop** | **Runtime** | `KERNEL_BOUNDARY.md:80` 行 16 | **NO** | Kernel **不实现** |
| **Agent Selection** | V0 **固定 Agent，无 Selection** | `KERNEL_BOUNDARY.md:74` 行 10 | **NO** | ⚠️ 工程上必须理解成「V0: Fixed Agent」 |
| **Workflow Execution** | **Runtime** | `KERNEL_BOUNDARY.md:78` 行 14 | **NO** | — |
| **Queue / Retry / Scheduler** | **Runtime** | `KERNEL_BOUNDARY.md:81` 行 17 | **NO** | 铁律 3 禁止自研 |
| **Durable Execution / Checkpointing** | **Runtime** | `KERNEL_BOUNDARY.md:82` 行 18 | **NO** | — |
| **Sandbox / 隔离执行** | **Runtime** | `KERNEL_BOUNDARY.md:83` 行 19 | **NO** | — |
| **MCP** | **Infrastructure** | 指令 §二；`KERNEL_BOUNDARY.md:84` 行 20（仅 Tool **准入**归 Kernel） | **NO** | — |
| **Model Gateway** | **Infrastructure** | `KERNEL_BOUNDARY.md:90` 行 26（LLM 不可知） | **NO** | 铁律 5 |
| **Observability** | **Runtime**（Kernel 仅简化版） | `KERNEL_BOUNDARY.md:77` 行 13 | **NO** | — |
| **Connector Ecosystem** | **Provider** | `KERNEL_BOUNDARY.md:87` 行 23 | **NO** | 仅自建 ≤3 个 mock 框架，**绝不自建 275+** |

**归一化口径**：上表 26 行对应 `KERNEL_BOUNDARY.md` 的 26 行（25 能力 + 1 约束行）。
本表**不含** `Private Deployment`——按 `V3_CLOSEOUT.md:48` 它是**非功能约束**，不是任何一方拥有的能力。

> ⚠️ **"现有实现状况"一列是本研究新增的**，它把「V3 归属」与「ECE v0 实际写到哪」分开——
> 二者常被混淆。最要紧的一条：**Kernel 的 Evidence / Decision / Context Update 三个对象，
> 仓库里目前一个对象/表都没有**。这不是"要不要换掉现有实现"的问题，
> 而是"这三个是新写的，可不可以借力"的问题——**这正是本次研究真正能省工作量的地方**。

---

## 3. 主矩阵（Capability × Candidate × Reuse Level）

**"Code Reuse" 与 "Architecture Reuse" 是两列，不要合成一列** ——
很多候选**代码拿不了但架构值得借鉴**（例：TrustGraph 的 PROV-O 命名图设计），
反过来也有**代码能拿但架构不该学**的。混在一起会得出错误结论。

| Capability | V3 Owner | Candidate OSS | Code Reuse | Architecture Reuse | Keep Ourselves | Notes |
|---|---|---|---|---|---|---|
| **Context Model** | Kernel | Semantica | **3**（`context/context_graph.py`，import 干净） | **3** | ⚠️ 部分 | ⚠️ **不含 Permission scope**（Semantica 只有 REST auth）；`ContextGraph` 是**内存实现** |
| **Domain Ontology** | Kernel | HugAgentOS / Semantica / TrustGraph | 1–2 | 1–2 | ✅ **是** | 三者分别是：演示模板（Semantica 硬编码 2 域）/ LLM 抽取词表（TrustGraph）/ 基础设施自描述 |
| **Entity / Relationship** | Kernel | Semantica · TrustGraph | **2** | **2** | ⚠️ 表示法可借 | 两者都只提供**表示法**，语义在我们 |
| **Business Rules** | Kernel | HugAgentOS / Semantica | 1–2 | 1–2 | ✅ **是** | HugAgentOS 的 `Constraint` 只能咬**工具参数**；Semantica 的规则语言是 `min_/max_/required_` 桩 |
| **Decision** | Kernel | Semantica | **2/3** | **2/3** | ⚠️ 形状可借 | `Decision` + `DecisionRecorder` + 先例 + 因果链确实建成了 |
| **Evidence** | Kernel | DataLogicEngine（仅概念） | **1**（代码许可阻断） | **1** | ✅ **是** | ⭐ **九个候选无一建成可用的一等对象** |
| **Provenance** | Kernel | **Semantica** | **3** | **3** | ⚠️ 机制可借 | ⭐ 哈希链 `verify_chain()` + PROV-O + ABC 存储 + Turtle 导出。**本研究的最高价值发现** |
| **Context Update** | Kernel | **Semantica** | **3** | **3** | ⚠️ 设计可借 | 时态撤回 + `state_at()` + 快照恢复；**决策变更/证据累积 API 不存在** |
| **Knowledge Retrieval** | Provider | Semantica / mcp-agent | 2 | 1 | **NO** | V0 单库纪律下不可用（须新基础设施） |
| **Graph Storage** | Infrastructure | Semantica（多后端门面） | 2 | 1 | **NO** | 鸭子类型，**无 ABC / 无 Protocol**；V0 不引入 Neo4j |
| **Vector Search** | Provider | Semantica / HugAgentOS | 2 | 1 | **NO** | 同上（Milvus / Qdrant 均超出 V0 单库） |
| **Agent Runtime** | Runtime | mcp-agent | 1 | 1 | **NO** | 明确越界；且 mcp-agent **已休眠 8 个月** |
| **Agent Loop** | Runtime | — | 0 | 0 | **NO** | Kernel 不实现（MUST NOT 清单） |
| **Workflow Execution** | Runtime | TrustGraph / mcp-agent | 1 | 1 | **NO** | `RUNTIME_COMPARISON.md` 已覆盖运行时选型，本研究不重做 |
| **Queue / Retry / Scheduler** | Runtime | — | 0 | 0 | **NO** | 铁律 3 禁止自研 |
| **Durable Execution** | Runtime | mcp-agent（Temporal） | 1 | 1 | **NO** | 同上 |
| **MCP** | Infrastructure | mcp-agent | **2** | 2 | **NO** | Apache-2.0 干净、成熟；**但项目休眠，选它需评估替代** |
| **Model Gateway** | Infrastructure | mcp-agent / Semantica | 2 | 1 | **NO** | 铁律 5 已定 OpenAI 兼容端点，无需引入 |
| **Observability** | Runtime | Semantica / HugAgentOS | 2 | 1 | **NO** | 标准栈（Prometheus / OTel / structlog），非创新 |
| **Permission Enforcement** | Kernel + Provider | 全部 ≤ 1 | **1** | 1 | **Partial → 强制点必须自建** | TrustGraph IAM **信任总线**、Semantica 只有 REST auth —— **两者都与"在数据访问层强制"相反** |
| **Connector** | Provider | — | 0 | 0 | **NO** | 只自建 ≤3 个 mock，绝不自建 275+ |
| **Search** | Provider | — | 0 | 0 | **NO** | 不自建横向搜索 |
| **Domain Evaluation** | Kernel | 我们自己（E1–E6） | — | 1（Semantica `evals/` 深度 UNKNOWN） | ✅ **是** | 开源最强者也只有 Level 2，且语义不同（**技能晋升 ≠ 领域决策正确性**） |

### 3.1 从矩阵读出的三件事

1. **Level 3 只出现在三个格子**，而且**全在 Semantica 的同一侧**
   （Context / Provenance / Context Update）—— 这三项恰好是"通用上下文基础设施"。
2. **Kernel 六项里，Evidence 与 Business Rules 的最高可得是 Level 1–2，
   且都带"代码不可用"或"语义不适用"的保留** → **必须自建**。
3. **所有 `Keep Ourselves = NO` 的行（Provider / Infrastructure / Runtime）拿到的最高等级是 2**，
   而 2 的意思是"可复用独立组件"—— 但它们**都要求引入 V0 冻结之外的基础设施**
   （Neo4j / Cassandra / Kafka / Milvus / 容器编排），**因此对 V0 全部不可用**（见 §5.2）。

---

## 4. 逐候选 × 逐能力 等级网格

| 能力 | A HugAgentOS | **B Semantica** | C TrustGraph | D OpenEAAP | E GSearchAI | F qKnow | G KnowledgeOps | H mcp-agent | I DataLogicEngine |
|---|---|---|---|---|---|---|---|---|---|
| Context Model | 0 | **3**⚠️ | 0 | 0 | 0 | 0 | 0 | 0 | 0–1 |
| Domain Ontology | **2**⚠️ | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 0–1 |
| Entity / Relationship | 0–1 | **2** | **2** | 0 | 1 | 1 | 1 | 0 | 0–1 |
| Business Rules | **2**⚠️ | 1 | 0 | 1 | 1 | 0 | **1–2** | 0 | 1 |
| Decision | 1 | **2/3** | 0 | 1 | 0 | 0 | **1–2** | 0 | 1 |
| **Evidence** | 0–1 | **0** | 0 | 0 | 0 | 0 | 0 | 0 | **1**🔒 |
| Provenance | 0 | **3** | **2** | 1 | 0 | 0 | 1 | 0 | 1 |
| Context Update | 0 | **3** | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| Knowledge Retrieval | **2** | 2 | 2 | 1 | **2** | 2 | **2** | 1 | 1 |
| Graph Storage | 1 | **2** | **2** | 1 | 1 | 1 | 1 | 0 | 1–2 |
| Vector Search | **2** | **2** | **2** | 1 | **2** | 1 | **2** | 0 | 1 |
| Agent Runtime | 1 | 1 | 0 | **1** | 1 | 0 | 1 | **2** | 0 |
| Agent Loop | 1 | 1 | 0 | 1 | 0 | 0 | 1 | **2** | 0 |
| Workflow Execution | 1 | 1 | 1 | **1** | 0 | **1** | **1–2** | **2** | 0 |
| Queue / Retry | 1 | 1 | 1 | **1** | 1 | 1 | **1–2** | 1 | 0 |
| Durable Execution | 1 | 1 | 1 | 1 | 0 | 0 | 1 | **2** | 0 |
| MCP | 1 | 1 | 1 | 0 | 0 | 1 | 1 | **2** | 0 |
| Model Gateway | 1 | 1 | 1 | 1 | 0 | 1 | 1 | **2** | 0 |
| Observability | **2** | **2** | **2** | 1 | 0 | 1 | 1 | 2 | 1 |
| Permission Enforcement | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| Connector | 0 | 0 | 0 | 0 | **2** | 0 | 0 | 0 | 0 |
| Search | 0 | 0 | 0 | 0 | **2** | 1 | 1 | 0 | 0 |
| Domain Evaluation | **2** | 1❓ | 0 | 0 | 1 | 1 | 1 | 0 | 0 |

🔒 = 许可证阻断代码使用 · ⚠️ = 见 `CODE_NOTES` 的相应保留 · ❓ = UNKNOWN

**读法提醒**：本网格**不是排名**。行内的数字可比（同一能力的四个等级），
**列之间不可比** —— 一个候选在 Agent Runtime 拿 2，另一个在 Evidence 拿 1，
这两个数字比较大小没有意义。

---

## 5. 「Keep Ourselves」的依据

### 5.1 Kernel 六项：为什么 Evidence 与 Rules 必须自建

不是"没有更好的实现"，而是**三条独立的证据同时指向这个结论**：

1. **Evidence 的代码级证据**（`CODE_NOTES` §11）：
   把 V3 要求的 8 个 Evidence 字段逐个比对全部候选的代码 ——
   **没有任何项目 8 个全有**；最高的 DataLogicEngine 约 6/8 而**许可阻断**；
   **`claim` 与 `triggering agent` 两项在所有候选里都未被建模**。
2. **Business Rules 的代码级证据**：最好的是 Semantica，它的**引擎确实确定性**
   （grep `LLM|openai|anthropic|provider` 零命中，native Datalog 半朴素不动点、保证终止），
   但**决策路径上的规则语言只是 `min_/max_/required_` 元数据谓词** ——
   它能表达"金额 ≥ 阈值"，表达不了"供应商资质在覆盖期内无重大不合格"。
3. **标准层面的证据**：**W3C PROV-O 覆盖溯源那一半，但既无 `Claim` 概念也无 `Decision` 概念**；
   OMG DMN 覆盖决策与规则表，但它是**表达标准，不是实现**。
   → 连标准都只覆盖一半，实现自然更不可能完整。

### 5.2 为什么 Provider / Infrastructure 的 Level 2 对 V0 不可用

指令与 V3 的冻结形态（`V3_CLOSEOUT.md:65-85, 106`；`KERNEL_ARCHITECTURE_V3.md:294`）是：

```
1 个 Domain Pack · 1 个固定 WorkflowSpec · 1 个固定 Agent
1 个 InProcessExecutor · 1 个 Local Provider
PostgreSQL 单库（结构化 + FTS + pgvector + JSONB）
不引入 OpenSearch / Redis / Neo4j · 不建三类接口抽象层
```

而所有 Provider / Infrastructure 项的 Level 2 复用都**要求引入该候选自己的基础设施**：

| 候选 | Level 2 组件 | 引入它需要 | 与 V0 冻结的冲突 |
|---|---|---|---|
| HugAgentOS | KB 检索 / Milvus 向量 | **Milvus + Redis（+可选 Neo4j）** | ❌ 违反"PostgreSQL 单库" |
| TrustGraph | 图存储 / 向量 / 检索 | **Pulsar + Cassandra + Qdrant + Garage** | ❌ 严重违反（15+ 容器） |
| Semantica | 图/向量后端 | 基础版可纯内存 ✅，但要**持久化**就需图后端或 `SEMANTICA_KG_PATH` | ⚠️ 内存可用，持久化受限 |
| mcp-agent | MCP 客户端 | 轻量（但占用 RUNTIME 边界） | ⚠️ 边界问题而非基础设施问题 |

> **结论**：`Keep Ourselves = NO` 的那一行行之所以是 NO，是因为**我们打算从 Provider 层消费它们
> （Glean / 企业 API），而不是在 Kernel 里自己实现**；
> 而"从开源拿走 Level 2 组件"这条路在 V0 会**以引入新基础设施为代价**，与冻结形态冲突。
> 这不是"不能复用"，而是"**V0 不是复用的时机**"。

### 5.3 一个反例（必须写明，避免自证）

`Keep Ourselves` 列如果全部是 YES 或 NO，就有"先射箭再画靶"的嫌疑。因此写明反例：

- **Permission Enforcement** 写的是 **Partial 而不是 YES** ——
  因为在 `KERNEL_BOUNDARY.md:117-136` 的 V3 收口里，Kernel 拥有的**只是强制点 + scope 契约**，
  **policy 来源可以是 Provider**（例如 Glean 的源系统 ACL 继承）。这一项**不该全自建**。
- **Context Model** 写的是 **⚠️ 部分**而不是 YES —— 因为 Semantica 在结构与时态部分
  确实达到 Level 3，我们的自建量在这一项上**有可能实质减少**（V1+）。
- **Domain Evaluation** 写 YES 的依据是**我们自己已经有的 E1–E6**，
  而不是"别人做得差"——开源里 HugAgentOS 的 `evals/`（成对统计 + `effect_size` + `p_value`）
  其实做得比多数候选好，只是**语义不同**（技能/Agent 晋升 vs 领域决策正确性）。

---

## 6. 本矩阵的结论（一句话）

> **23 项能力里，Kernel 的 8 项应自建（其中 Evidence 与 Business Rules 是硬性自建），
> 11 项归 Provider / Infrastructure / Runtime 且 V0 一律不引入，
> 4 项（Provenance / Context Update / Context 结构化与时态 / 推理后端）**存在 Level 2–3 的开源可借，
> 但全部落在 V1+，且全部需要先立 ADR**。
>
> **开源能替我们做"上下文与溯源"，做不了"证据与规则"。**
