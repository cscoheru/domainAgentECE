# FOUNDATION_REUSE_STUDY.md

> **开源底座 / Framework / Infrastructure Reuse Assessment**
> 一次**代码级技术尽调**，不是 V4 Architecture Rewrite。
>
> **本阶段纪律（指令 §19）**：NO PRODUCTION CODE CHANGE / NO ARCHITECTURE CHANGE /
> NO DEPENDENCY INSTALL / NO OSS VENDOR-IN / NO FORK / NO MIGRATION / NO DATABASE CHANGE /
> NO V0 CHANGE / NO PRD CHANGE。
> 只做 **READ → INSPECT → COMPARE → DOCUMENT**。
>
> 配套文件：`FOUNDATION_REUSE_MATRIX.md`（能力 × 候选 × 复用等级）、
> `FOUNDATION_REUSE_CODE_NOTES.md`（逐仓库代码级证据与出处）。
> Last Verified: 2026-09-20

---

## 1. Executive Summary

> 考察于 2026‑09‑20；报告成稿 2026‑09‑21。逐仓库证据见 `FOUNDATION_REUSE_CODE_NOTES.md`。

### 1.1 为什么研究

V3 Architecture Freeze 已成立（`V3_CLOSEOUT.md:158`）。产品方向不是"中国版 Glean"，
也不是通用 Agent 平台，而是 **Domain Intelligence Kernel**。
Kernel 应该拥有的是**业务语义与业务智能边界**，而不是所有底层技术基础设施。

于是出现一个对工程量影响很大的问题：

> **能不能把"自己要写的 Kernel"压缩到只剩业务语义层，
> 而 Context / Ontology / Evidence / Provenance 等底层能力尽可能借力成熟 OSS？**

这个问题的答案是"很可能是可以"还是"其实没有"，**不能凭 README 判断**。
本研究做的就是这件事：**代码级技术尽调**，而不是 README Research。

### 1.2 发现了什么（五条结论）

**结论一：不存在可以作为"完整 Kernel foundation"的开源项目。**
九个候选全部源码级考察完毕（3 个 `CLOSE`、5 个 `REFERENCE ONLY`、1 个可"取零件"）。
**没有任何一个候补能覆盖 Kernel 的六项核心能力。**

**结论二（最重要）：全部九个候选里，没有一个把 Business Evidence 建成为可用的一等对象。**
唯一真正把它建成一等对象的 `DataLogicEngine`（`TraceEvidence` 带 content hash、locator、
authority、`provenance_completeness` 评分；独立的 `TraceClaim`；一等的
`ClaimEvidenceLink`；甚至建模了 `EvidenceConflict`）——
**许可证是 PolyForm Noncommercial，禁止商业复用**（已独立核验 LICENSE 正文）。
> 对照 `KERNEL_BOUNDARY.md:195` 那句预判："DSH 的 Trajectory 回答不了这个问题，
> Trigger.dev 的 tracing 也回答不了。" —— **实测：开源的 tracing / trajectory / lineage 也都回答不了。**

**结论三：唯一"许可干净 + 形状像内核"的候选是 Semantica，但它只覆盖六项里的三项。**
`semantica-agi/semantica`（13,310★，**纯 MIT**，基础安装**零必需基础设施**）
在 **Provenance / Context Update / Context Model** 三项上达到 **Level 3（Foundation reuse）**，
且 `provenance/`、`context/context_graph.py`、`change_management/` 对
`server`/`worker`/`explorer` 都是 import 干净的。
**但它的 Evidence = Level 0（`class Evidence` 根本不存在）、
Business Rules = Level 1（引擎确实确定性，但规则语言只是 `min_/max_/required_` 元数据谓词桩）、
Domain Ontology = Level 1（演示级模板注册表）、Permission = Level 1（只有 REST 认证）。**

**结论四：V0 阶段任何 OSS 底座都没有"接入位"。**
V0 的冻结形态是"单进程 + 单 PostgreSQL 库 + 不建抽象层 + 1 个 Local Provider + 1 个 InProcessExecutor"
（`V3_CLOSEOUT.md:65-85, :106`）。因此本研究能影响的是 **V1+ 的选型**，
以及在 V0 阶段**零架构代价**的取舍（数据模型形状、术语与标准对齐）。

**结论五：许可证是本次筛选中最主要的过滤器 —— 九个候选里只有四个干净。**

| 许可证状况 | 候选 |
|---|---|
| ✅ 干净可商用 | **Semantica**（纯 MIT）、TrustGraph（Apache-2.0）、knowledgeops-agent（MIT）、mcp-agent（Apache-2.0）、OpenEAAP（Apache-2.0） |
| ⚠️ 带附加条款（需业务决策） | **HugAgentOS**（Apache-2.0 **+ 附加条款**：多租户 SaaS 受限；**白标需商业许可**；单组织内部私有化明文允许）、**qKnow**（Apache-2.0 + 条件：必须保留品牌；**条款可被对方单方面变更**） |
| ❌ 法律不可用 | **GSearchAI**（**根本没有 LICENSE 文件**，README 自称 MIT 无效）、**DataLogicEngine**（PolyForm Noncommercial，商业使用需另签） |
| ⚠️ 待核 | TrustGraph 的 CLA 正文在仓外（*Fiduciary* CLA），**未读到原文** |

### 1.3 必须同时上报的两条"指令前提修正"

本研究在源码层面发现**候选清单本身需要修正**，其中两条影响结论的成立：

1. **坐标问题**：`OpenEAAP` 与 `GSearchAI` 在 zread 上返回 `repo not found` ——
   那是**索引缺失，不是仓库不存在**（经 GitHub API 核实二者均真实存在）。
   而 **Candidate G/H/I 三个指令未给仓库路径**，其中 **`mcp-agent-framework` 在 GitHub 上不存在同名仓库**。
   我用最接近者代替，**这三节的结论以我的坐标推断为前提，需 Codex 确认**。
2. **"表面很像"在源码层不成立**：指令 §三 说 HugAgentOS "概念与我们当前 Kernel 非常接近，
   包括 … **Invariants** … **Action Contracts** …"。逐条核验后：
   **`Invariants` 与 `Action Contracts` 在代码里不存在**（后者全库 0 命中，仅出现在 README 与架构 SVG 中）；
   Roles/Permissions 只是 prompt 里的 reviewer 人设；
   Concepts/Relations/Workflows 真实但**只是 JSONB 里的 Pydantic 结构，没有自己的表**。
   > **这是"README Research 会得出错误结论"的一个直接实例，也是本研究价值的直接证明。**

### 1.4 哪些能力明显可以复用

| 能力 | 最佳可得 | 层级 | 何时可用 |
|---|---|---|---|
| **Provenance**（溯源机制） | **Semantica** `provenance/`（W3C PROV-O `ProvenanceEntry`、**哈希链 `verify_chain()`**、ABC 存储、`export_prov()`） | **3** | V1+ |
| **Context Update**（时态撤回） | **Semantica** `retract_node/retract_edge` + `_closing_valid_until` + `state_at()` + 快照恢复 | **3** | V1+ |
| **Context**（结构化 + 双时态部分） | **Semantica** `ContextGraph` + `ContextNode/Edge` + `BiTemporalFact(valid_from, valid_until, recorded_at, superseded_at)` | **3**（**Permission scope 须自建**） | V1+ |
| **推理后端**（非规则语言） | **Semantica** `DatalogReasoner` / `ReteEngine` / `SPARQLReasoner` —— **已核实零 LLM 介入** | **2** | V1+ |
| **事实血缘设计**（非业务证据） | **TrustGraph** 命名图 PROV-O（`urn:graph:source`） | **2** | 参考 |
| **RDF/quad 表示** | **TrustGraph** `Term` / `Triple(s,p,o,g)` + RDF-star | **2** | 参考 |
| **MCP 消费 / 模型网关** | **mcp-agent**（Apache-2.0，**但已休眠 8 个月**） | **2** | 参考 |
| **标准对齐**（非项目） | **W3C PROV-O**（溯源）+ **OMG DMN**（决策/规则表达） | **1** | **V0 即可，零成本** |
| Knowledge Retrieval / Vector Search / Graph Storage | 多候选 Level 2，但**均带自己的基础设施要求** | 2 | V1+（与 V0 单库纪律冲突，见 §9） |

### 1.5 哪些不能复用（必须自己拥有）

| 能力 | 判定 | 依据 |
|---|---|---|
| **Evidence** | ✅ **必须完全自建** | 全部九个候选无一把 Business Evidence 建成可用的一等对象；唯一建成的许可阻断 |
| **Deterministic Business Rules** | ✅ **必须自建** | 最好的是 Semantica，但决策路径上的规则语言是 `min_/max_/required_` 元数据谓词桩；引擎可借 |
| **Domain Ontology** | ✅ **基本自建** | 现有三者分别是：演示模板（Semantica 硬编码 2 个域）、LLM 抽取词表（TrustGraph）、基础设施自描述（TrustGraph `schema.ttl`） |
| **Permission scope**（访问裁决） | ✅ **必须自建** | 铁律 1 + `KERNEL_BOUNDARY.md:117-136`；TrustGraph 的 IAM 自述"信任总线"、Semantica 只有 REST auth —— **两者都与"在数据访问层强制"相反** |
| **Decision 语义** | ⚠️ **形状可借，语义自建** | Semantica 的 `Decision` + `DecisionRecorder` 形状接近，但语义是我们的 |
| **Context Update 的决策/证据部分** | ⚠️ **设计可借，语义自建** | Semantica 的时态撤回是通用的；**决策变更与证据累积的 API 不存在** |
| **Domain Evaluation** | ✅ **本来就是我们最强的资产** | `data/eval/e1..e6.json`；Semantica 的 `evals/` 深度为 **UNKNOWN** |

### 1.6 对当前架构是否有影响

**没有影响（No Impact）。**

- 没有任何候选迫使修改 V3 边界、Kernel 核心、数据模型阶段归属或 V0 范围。
- 没有任何候选构成"架构冲突"。
- 唯一一条"实施精化"级建议是：**Evidence 的溯源子模型对齐 W3C PROV-O**
  （§11.1 的横切发现：PROV-O 覆盖溯源一半但**既无 `Claim` 也无 `Decision` 概念**）——
  这属于**字段命名与关系形状的选择，不涉及架构改动**，也不需要引入任何依赖。
- **本研究不改变 V0。V0 的六步闭环照原计划执行。**

### 1.7 一句话总结

> **开源能替我们做"上下文与溯源"，做不了"证据与规则"；
> 而 Evidence 与确定性业务规则恰好是 Kernel 的核心资产
> —— 开源最好的那部分，正好不是我们的差异化所在。**
>
> 所以本研究的结论不是"找到了底座"，也不是"白研究了"，
> 而是：**把自建量压缩到"一个很薄的 Kernel 语义层"这件事，证据支持它是必需的，
> 而不是因为我们没找到。**

---

## 2. Current V3 Boundary

> 本节**只引用**现有文档，**不重新定义架构**（指令 §16.2）。
> 引用的每一处都给出 `文件:行号`。

### 2.1 六个参与方

`docs/v3/KERNEL_BOUNDARY.md:35-44` 定义六个参与方，并附「不是什么」一列：

| 参与方 | 是什么 | 不是什么 |
|---|---|---|
| **Kernel**（Domain Intelligence Kernel） | 业务智能层：Context / Domain Ontology / Deterministic Business Rules / Decision / Evidence | 不是执行引擎、不是 Agent Harness、不是搜索引擎、不是连接器平台、不是编排器 |
| **Trigger.dev** | Durable Workflow / Execution Runtime（Tasks / Runs / Queues / Retry / Wait / Concurrency / Scheduling / Durable Execution / Observability） | 不懂业务语义，不做业务决策 |
| **DSH**（DeepSeek Harness） | 插件化 Agent Runtime / Harness（Agent Loop / Tools / Skills / Session / Sandbox / Subagents / Storage / Trajectory） | 不提供企业上下文，不提供领域本体，不做跨 Agent 的业务语义共享 |
| **PentAGI** | 领域 Agent 应用（自主渗透测试） | 不是通用 Kernel；是被 Kernel 调用的一类 capability |
| **Glean** | Provider：企业搜索 / 连接器 / 权限继承 / Enterprise Graph / Agent 能力 | **不是** Kernel 的底座；是可插拔的一项 Provider |
| **Enterprise System** | 事实来源：ERP / OA / HRIS / 工单 / 文档库 / 合同库 / 数据仓库 | 不是 AI 系统；一切企业事实的最终权威 |

术语纪律（`KERNEL_BOUNDARY.md:46`）：**"Provider" ≠ "Kernel"。Provider 提供原料，Kernel 生产业务结论。**

### 2.2 Kernel 核心（去掉任一项即不成立）

`docs/v3/V3_CLOSEOUT.md:27-35`：

```
Context（含 Entity / Relation / Temporal / Permission scope）
Domain Ontology
Deterministic Business Rules
Decision
Evidence
```

链尾是 `Context Update`，`V3_CLOSEOUT.md:101-102` 明确：
**判定一个 Kernel 不是"规则引擎 + RAG"的关键不是那 5 项核心对象本身，而是链尾的 Context Update。**

### 2.3 明确移出 Kernel

`docs/v3/V3_CLOSEOUT.md:37-44`：

```
Retrieval 机制（召回 / 融合 / 排序）   → Provider
Tool 选择与工具执行                   → Runtime / Harness
Agent / Runtime 动态选择              → V1（V0 仅固定，不选择）
执行编排（顺序 / 分支 / 重试 / 并发）   → Runtime
```

### 2.4 Kernel MUST NOT（结构性禁止清单）

`docs/v3/KERNEL_BOUNDARY.md:212-235`——**每一项都有成熟实现，Kernel 重建即违规**：

```
❌ Queue / Retry Engine / Scheduler / Concurrency Engine / Worker Runtime
❌ Durable Execution / Checkpointing Engine
❌ Agent Loop / Session Runtime / Sandbox / Subagent Runtime
❌ 横向企业搜索引擎（100+ 源、排名算法）
❌ Connector 平台（275+ 连接器、连接器市场）
❌ Agent Builder UI / Prompt 市场 / Skill 市场 / 通用多 Agent 编排平台
❌ 通用 RAG pipeline / "上传文档→问答" 产品
❌ 向量数据库平台 / 通用 Graph 数据库平台
❌ 多租户 SaaS 计费 / 企业级 Admin Console / K8s / 微服务 / 消息队列
❌ 模仿 Glean 同款的 execution-path 评估
```

**判定测试（四问，缺一即不自建）**（`KERNEL_BOUNDARY.md:237-242`）：
① 这是业务语义层还是执行/基础设施层？② Glean / 开源 / 运行时是否已提供且成熟？
③ 是否是 V0（2–4 周）闭环的必需项？④ 是否产生领域 IP（换公司仍可复用）？

> **本研究的方法论正是把第 ② 问从"凭感觉"变成"读过源码"**——这是本文件存在的理由。

### 2.5 适配器边界与硬规则

`docs/v3/KERNEL_ARCHITECTURE_V3.md:169-192` 定义三类接口：
`ProviderInterface`（原料）/ `AgentRuntimeInterface`（执行者）/ `ExecutionRuntimeInterface`（可靠执行）。

硬规则（`:194-216`）中最重要两条：

1. **命名用业务语义，禁止出现厂商标识符**（`glean` / `trigger` / `dsh` / `pentagi`），并有 **CI 门禁**：
   ```bash
   ! grep -rEi 'glean|triggerdev|trigger\.dev|deepseek.?harness|dsh|pentagi' src/kernel/ src/domain_packs/
   ```
2. **每个 Kernel 决策都必须有 execution intent 可复现**（`KERNEL_ARCHITECTURE_V3.md:224-252`）：
   > **运行时无权直接写入企业事实。** 一切"业务事实"必须经 Kernel 的 Evidence Layer 转换与记录。

### 2.6 数据模型与持久化

`docs/v3/KERNEL_ARCHITECTURE_V3.md:256-276` 列出 14 个对象及其阶段归属。
V0 阶段对象：Context / Entity / Relation / Ontology / Knowledge / **Evidence** / Reasoning /
**Decision** / WorkflowSpec / Action / AgentRef / Policy。V1 阶段：RuntimeRef / ExecutionRef。

关系图中一条关键约束（`:290`）：
> `Evidence → ExecutionRef` 是 **0:1 且仅引用**。ExecutionRef 消失不影响 Evidence 的完整性与可追溯性。

持久化（`:292-295`）：
> **V0/V1：PostgreSQL（单库承担结构化 + FTS + pgvector + JSONB）**——铁律 3 垂直纪律，
> 不引入 OpenSearch / Redis / Neo4j。**Evidence 必须与 Context 同库**：业务证据的存续不能外包给运行时。

### 2.7 V0 的范围（对本次研究最关键的约束）

`docs/v3/V3_CLOSEOUT.md:65-85`——**V0 只允许**：

```
1 个 Domain Pack          1 个固定 WorkflowSpec     1 个固定 Agent
1 个 InProcessExecutor    1 个 Local Provider       最小 Permission enforcement
最小 Evidence
```

**V0 不实现**：动态 Agent/Runtime Selection、任一 Adapter（Trigger.dev / DSH / Glean）、多 Agent、
通用 Connector、Builder UI、通用 RAG 平台、通用 Workflow Engine、**三类接口抽象层**。

`V3_CLOSEOUT.md:106` 进一步明确：**ADR-011 §3（三类接口）与 §5（V0 各有进程内实现）的 V0 义务被收口取代** ——
V0 只保留**具体实现**（1 个 Local Provider + 1 个 InProcessExecutor，直接调用），**不建抽象层**。
三类接口设计作为 **V1 方向**保留。

`docs/v3/V3_CLOSEOUT.md:89-92` 的 V0 成功判据：
> **证明 Kernel technical loop 成立** —— `Context → Entity/Knowledge → 一个确定性 Business Rule →
> Decision → Evidence → Context Update` 这一条链能在窄切片上端到端跑通，且每步产出可验证。
> **V0 不负责证明 PMF。**

### 2.8 本节对本次研究的约束含义（本研究的推论，非架构改动）

把 §2.7 与本研究的题目放在一起，得到一个**必须一开始就说明的结构性事实**：

> **V0 是"单进程 + 单 PostgreSQL 库 + 无抽象层"的形态。**
> 因此任何 OSS 底座**都不可能在 V0 阶段被接入**——V0 的冻结范围里根本没有"接入一个底座"的位置。
> **本研究能影响的是 V1+ 的技术选型，以及在 V0 阶段"零架构代价"的取舍**（例如数据模型形状、
> 术语对齐、标准对齐）。

这条推论不修改任何架构，但它决定了后面 §7「Recommended Technical Composition」必须分成
**V0 可用 / V1+ 才可用**两栏来写，否则会给出一个当前无法执行的建议。

---

---

## 3. Candidate Projects

九个候选，坐标与许可一览（**含本研究对指令清单的修正**）：

| # | 指令中的名称 | 实际仓库 | 语言 | ★ | 许可 | 裁决 |
|---|---|---|---|---|---|---|
| A | HugAgentOS | `ZJU-REAL/HugAgentOS` | Python | 1,109 | Apache-2.0 **+ 附加条款** | REFERENCE ONLY |
| B | Semantica | `semantica-agi/semantica` | Python | 13,310 | **纯 MIT** | ⭐ **可取零件**（非整体嵌入） |
| C | TrustGraph | `trustgraph-ai/trustgraph` | Python | 2,736 | Apache-2.0（CLA 正文 UNKNOWN） | REFERENCE ONLY |
| D | OpenEAAP | `turtacn/OpenEAAP` | **Go** | **1** | Apache-2.0 | **CLOSE** |
| E | GSearchAI | `GramosoftAI/GSearchAI` | Python 后端 / TS 前端 | 26 | ❌ **无 LICENSE** | **CLOSE** |
| F | qKnow | `qiantongtech/qKnow` | Java | 280 | Apache-2.0 **+ 条件** | **CLOSE** |
| G | "KnowledgeOps Agent" ⚠️坐标推断 | `however-yir/knowledgeops-agent` | Java | 194 | MIT | REFERENCE ONLY |
| H | "mcp-agent-framework" ⚠️坐标推断 | `lastmile-ai/mcp-agent` | Python | 8,549 | Apache-2.0 | REFERENCE ONLY |
| I | "DataLogicEngine" ⚠️坐标推断 | `kherrera6219/DataLogicEngine` | Python | **6** | ❌ **PolyForm Noncommercial** | **CLOSE** |

> ⚠️ **G/H/I 的坐标是我按名称推断的**（指令未给路径，且 `mcp-agent-framework` 无同名仓库）。
> **若 Codex 所指另有其库，这三节需重做。**

---

## 4. Code-Level Findings

> 本节的每一条判断在 `FOUNDATION_REUSE_CODE_NOTES.md` 里都有 `path:line` 与原文片段。
> 本节给结论，那里给出处。

### 4.1 Kernel 六项能力 × 九候选（快查网格）

| 能力 | A HugAgentOS | **B Semantica** | C TrustGraph | D–F | G | H | I |
|---|---|---|---|---|---|---|---|
| Context | 0 | **3**⚠️ | 0 | 0 | 0 | 0 | 0–1 |
| Domain Ontology | **2**⚠️ | 1 | 1 | 1 | 1 | 0 | 0–1 |
| Business Rules | **2**⚠️ | 1 | 0 | 0–1 | 1–2 | 0 | 1 |
| Decision | 1 | **2/3** | 0 | 0–1 | 1–2 | 0 | 1 |
| **Evidence** | 0–1 | **0** | 0 | 0 | 0 | 0 | **1**（许可阻断） |
| Context Update | 0 | **3** | 0 | 0 | 1 | 0 | 0 |

⚠️ = 带重要保留（见下）。D–F = OpenEAAP / GSearchAI / qKnow 合并列（三者均为 CLOSE，无区分必要）。
等级定义见 `FOUNDATION_REUSE_MATRIX.md` §1。

### 4.2 逐候选要点

**A. HugAgentOS**（`ZJU-REAL/HugAgentOS`）
- *License*：Apache-2.0 **+ 四条附加条款且冲突时优先**。**单组织内部私有化部署明文允许**；
  多租户 SaaS（与其托管商业版竞争）与**去标识白标**需另购商业许可。⚠️ `pyproject.toml` 却声明 MIT
  —— **元数据不可信，以 LICENSE 为准**。
- *Activity*：创建仅 2 个月，**2 位真实贡献者**，**后端无 CI**，releases 全是 desktop tag。
- *Architecture*：**没有 `kernel/` 包**；`core/` 是"非 HTTP 且非编排"的剩余集合（LLM 管道、KB/RAG、sandbox、
  channels 与领域本体共用同一 import 根）。
- *Core data model*：89 张表。**Ontology 是真实一等对象**（`ontology_packs` / `_versions` /
  `_enforcement_events` / `_review_runs` / `_drafts`）；但 `Concept`/`Relation`/`Constraint`/`Workflow`
  **只是 JSONB 里的 Pydantic 结构，没有自己的表**。
- *Ontology*：**业务语义声明 + 通用引擎**。`Constraint` 用 JSON Schema 2020-12 求值、
  **闸门处零 LLM**（真实优点）—— 但 `ConstraintTarget.kind: Literal["tool","tool_parameter","output"]`，
  **规则只能约束工具调用与答案文本，不能约束领域业务对象**。
- *Evidence*：**Runtime Trace + Citation**（截断 trace + citations 交给 LLM reviewer），
  **不是 Business Evidence**。
- *Context Update*：**NOT FOUND**（`ProfileMemory` 会话开始即冻结）。
- *扩展点*：`OntologyPackDocument` / `StorageBackend` ABC / plugin.json / SKILL.md / MCP。
  **但没有 decision evaluator / evidence provider / context updater 的 Protocol 或 ABC。**
- *耦合* ⭐ `ARCHITECTURAL COUPLING RISK`：ontology 闸门是 **AgentScope 中间件**
  （`OntologyGateMiddleware`），硬编码在 3,536 行的 `workflow.py` 里；
  `Constraint` 求值**需要工具注册表**；修复回路走 **SSE 流式层**；演化走演化平面。
  **Domain Pack 无法独立使用。**
- *另一条结构性事实*：**这是只读下游镜像**（`CONTRIBUTING.md:9-13`：`src/**` 由上游自动生成、对外只读、
  PR 不予合并）→ **Level 3（fork）这条路在证据上不成立**。
- *Storage*：必需 PostgreSQL 15 + Redis 7；Milvus/Neo4j 在可选 profile。
  ⭐ **私有化是它的强项**：自带 Tauri 桌面应用与**离线安装路径**，气隙部署是**在维护的一等目标**。
- *Reuse*：Domain Ontology **2**⚠️（受工具调用形状限制）、Business Rules **2**⚠️、Knowledge Retrieval **2**、
  Vector Search **2**、Observability **2**、Domain Evaluation **2**；其余 0–1。

**B. Semantica**（`semantica-agi/semantica`）—— **唯一破例**
- *License*：**纯 MIT**，无 CLA，仓内无双许可；`docs/project-license.md:41-44` 明列
  "free for business use / Modify / Distribute / **Use in proprietary software**"。**最干净的一个。**
- *Activity*：当天仍在提交；13,310★ / 1,500 forks。CI 确实加固（CodeQL、Dependabot、
  hash-pinned requirements、verify-action-pins）。⚠️ 测试**偏模拟**
  （`tests/verify_context_sync.py` 打了 `integration` marker 却自己定义 `MockVectorStore`）。
- *Architecture*：**是产品/平台，不是库** —— 一个 wheel 五个 console script，**Explorer 的 React 产物
  被打进 wheel**（CI 断言）。**但依赖方向正确**：server→core，从不 core→server；
  `context/`/`kg/`/`ontology/`/`reasoning/`/`provenance/` **都不 import** server/explorer/worker。
  ⚠️ **命名陷阱**：`semantica/core/` 是**编排管道**，不是内核；真数据模型在扁平兄弟包里。
- *Core data model*：`ContextGraph` + `ContextNode/Edge`（带 `valid_from/valid_until`）；
  **双时态** `BiTemporalFact(valid_from, valid_until, recorded_at, superseded_at)`；
  `Decision`（`decision_models.py:87`）；`DecisionRecorder`；`Policy` 版本化。
- *Ontology*：**薄** —— `_load_domain_templates()` **硬编码恰好两个域**（healthcare/finance），
  **而 docstring 宣称五个**；类只是 `{"name","comment"}`。周边机器（OWL 生成、SHACL、pyshacl）真实，
  但**没有不变式/约束/公理，也没有业务规则↔本体的绑定**。
- *Rules* ⭐：**引擎是真的确定性** —— 在 `reasoner.py`/`deductive_reasoner.py`/`policy_engine.py`
  grep `LLM|openai|anthropic|provider` **零命中**；Datalog 是 native 半朴素不动点求值、
  保证终止；Rete 有 alpha/beta 节点；SPARQL 有原生路径 + rdflib 回退。
  ⚠️ **但决策路径上的规则语言只是 `min_/max_/required_` 元数据谓词** —— 无表达力、无规则↔本体绑定、
  无逐决策版本化。
- *Evidence* ⭐：**NOT FOUND** —— 全库 `evidence` 有 117 处字符串命中、**类型定义 0 个**。
  最接近的是 `ProvenanceEntry`（血缘）与 `supporting_evidence`（运行时轨迹）。
- *Provenance* ⭐：**本仓对我们最有价值的资产** —— W3C PROV-O `ProvenanceEntry`（20 个字段）、
  `ProvenanceManager`（1,521 行）、**哈希链 `verify_chain()`**、`ProvenanceStorage(ABC)` + SQLite/内存实现、
  `export_prov()` 到 Turtle。
- *Context Update* ⭐：**支持，形态是"时态闭合"** —— `retract_node/retract_edge` 只**关闭有效期窗口**
  （`_closing_valid_until` 只会收窄，不会放宽）并写 `UPDATE_NODE` 审计事件；
  `state_at()` 可重建任意时点状态；`change_management/` 提供快照/比较/恢复。
  ⚠️ **决策变更与证据累积的 API 不存在**；⚠️ `ContextGraph` 是**内存实现**。
- *耦合*：**中等，且弱于其他候选** —— 每一个 runtime 依赖都在 **optional extras** 里，
  基础 `dependencies` 是 22 个纯库包（**无 FastAPI / 无 celery / 无 broker**）；
  重层在 `orchestrator` 里**懒加载且包 try/except**。
  ⚠️ **修正一个假设**：`test_issue_1513_slim_core.py` **不是**"能单独 import core"，
  它断言的是**依赖数量 == 22** —— **"slim core" 是打包保证，不是解耦产物；
  不存在可单独构建的 `semantica-core` 发行包。**
- *扩展点*：唯一的真 ABC 是 `ProvenanceStorage`；`GraphStore`/`VectorStore` 是**具体门面
  （`backend: Any`），无 ABC、无 Protocol** → 插件契约是**约定的鸭子类型**。
  **不存在"自定义领域本体 + 规则集"的一等扩展清单。**
- *Storage* ⭐：**必需后端：无。** 基础安装纯内存 + rdflib/networkx。
  离线路径现实：`llm-ollama` + `embeddings-local` + `nlp-spacy` + `tripletstore-oxigraph`
  + `vectorstore-sqlite`（`infra` extra 的 Kafka/Pulsar/RabbitMQ **可以避开**）。
- *Reuse*：Provenance **3**、Context Update **3**、Context Model **3**⚠️（**Permission scope 须自建**）、
  Decision **2/3**、Entity/Relationship **2**、Graph/Vector Store **2**、Observability **2**；
  **Evidence 0**、Ontology **1**、Business Rules **1**、Permission **1**、Agent Runtime **1**、
  Workflow **1**、Domain Evaluation **1（UNKNOWN）**。

**C. TrustGraph**（`trustgraph-ai/trustgraph`）
- *License*：Apache-2.0 干净；**CLA 是"许可授予"而非版权转让**（项目自述），
  ⚠️ **但 CLA 正文在仓外（*Fiduciary* CLA），未读到原文 → UNKNOWN**。
- *Activity*：活跃（当天有提交）；2,736★；**贡献者极度集中**（`cybermaggedon` 982）→ 实质单厂商。
- *Architecture* ⭐ **决定性事实：不可嵌入。** `pip install trustgraph` 装到的是**客户端**。
  **broker 是强制的**：`pubsub.py:29-38` 默认 `pulsar://pulsar:6650`（或 rabbitmq/kafka），
  **没有进程内总线**；消费模型是 Docker 容器 + `:8888` API gateway。
- *Core data model*：`Term` + `Triple(s,p,o,g)`；**`Context` NOT FOUND**（只有 `EntityContext`）；
  Workspace/Collection 是**多租户文档命名空间**，无语义；"Context Core" 是 dump/restore 打包。
- *"Hypergraph"* ⚠️：**不是一等 n 元边类型** —— 是 RDF-star reification（`QuotedTriple`）+
  命名图分组。**得到的是 n 元建模能力，不是可挂规则的 hyperedge 类型。**
- *Ontology*：**两件事不要混** ——（a）`specs/ontology/trustgraph.ttl` 是**项目自己的内部词表**
  （Document/Chunk/Question/Thought/Plan…，基础设施自描述）；（b）**BYOO 真实且声明式**
  （`OntologyProperty(domain, range, cardinality, functional)`，经配置推送加载）。
  ⚠️ **但本体只约束 LLM 抽取，事实是概率性的**；`ontology-prompt.md` 是摄取期提示词；
  **ingest 之后不做任何约束检查 —— 约束是提示词文本。**
- *Evidence* ⭐：**是数据血缘（fact lineage），不是业务证据** —— 三层 provenance（抽取血缘 /
  查询期可解释性 / agent 轨迹）**都没有** decision id、actor、claim、asserted-time、规则引用或 context 快照。
  "哪份文档产出了这条 triple" ≠ "这个决策为什么这样下"。
- *Context Update*：**不支持** —— 一次写摄取 + 只读检索 + 粗粒度管理删除；
  **全库无任何时态谓词**（no `valid_from/valid_to`、无双时态、无实体状态变更、无证据累积）。
- *耦合* ⭐ `ARCHITECTURAL COUPLING RISK` = HIGH：**agent trace 与业务事实写在同一个 triple store**
  （`urn:graph:retrieval`）—— **我们的 Evidence 层会和它们的 agent 轨迹在存储层无法区分**；
  且 IAM 自述 *"trusts the bus … no per-request auth against the caller"*，
  与铁律 1（在数据访问层强制）**正相反**。
- *扩展点*：后端/处理器层干净（broker Protocol、ProcessorSpec、多存储后端、消息翻译器）；
  **但知识对象模型不可扩展** —— 固定 `Triple(s,p,o,g)` + `Term`，
  **没有为 Decision/Rule/Evidence/Context-version 这类新内核对象预留任何接口**。
- *Storage*：**Pulsar + Cassandra + Qdrant + Garage S3** 全为必需，再加 gateway/librarian/config/
  flow/IAM/metering 与每 processor 一进程。文档自承 *"15+ containers"* →
  **这是平台承诺，不是一个依赖。问题不是可行性，是重量。**
- *Reuse*：Entity/Relationship **2**、Provenance **2**（**事实血缘，非业务证据**）、
  Knowledge Retrieval **2**、Graph Storage **2**、Vector Search **2**、Observability **2**；
  Context/Rules/Decision/Evidence/Context Update **全 0**。

**D. OpenEAAP** —— **CLOSE**
- *License*：Apache-2.0 干净（本批唯一无歧义的），**但救不活下面的问题**。
- *Activity*：最后提交 **2026-01-21（约 8 个月）**；**1★**；2 位贡献者（其中一位是 `openhands-agent`）；
  0 releases；**无 CI**；仓库里**提交了未解决的补丁冲突残骸**（`.orig`/`.rej`）与
  `test_output.log`/`SYNTAX_FIXES_SUMMARY.md`/`COMMIT_SUMMARY.md` —— **调试中途被提交**。
- *数据模型*：Context/Ontology/Evidence/Provenance **均无一等对象**；
  `kg_entities`/`kg_relations` **有表但无对应领域实体**；
  `decision_type ('permit','deny','conditional')` 是**授权 PDP**（`PolicyDecisionPoint.Evaluate`），
  **不是业务裁决**；`AccessRequest.Context` 是 `map[string]interface{}` —— **一个 blob**。
- *裁决*：架构上是 Agent Runtime（orchestrator/executor/scheduler/runtime adapters/training/RLHF），
  且是 Go —— 与 Python Kernel 无运行时交集。

**E. GSearchAI** —— **CLOSE**
- *License* ⭐ **硬阻断**：`/license` → **404**；遍历 538 个文件**零个** licen/copying/notice。
  而 `README.md:10` 挂 MIT 徽章、`:286` 写 *"See the `LICENSE` file for details"* —— **该文件不存在**。
  **法律默认：无许可 = 保留所有权利。README 的 MIT 主张没有法律效力。**
- *Activity*：`main` 最后提交 2026-07-04；2 位贡献者；`tests/__init__.py` 只有一行 docstring；
  `.github/workflows/deploy.yml` **不是 CI**，是自托管 runner 上 `git reset --hard origin/backdev`；
  仓库内有 3.7MB `response.md`、`vector.zip`、`scratch.py`、`tester_zone/`。
- *数据模型*：`OntologyRule{source_class, relation, target_class}` **是三元组模式，不是确定性业务规则**；
  `OntologyResolver` 是 **embedding 共指消解**（余弦 > 0.92），**是实体去重，不是本体推理**；
  Context/Decision/Evidence/Provenance **NOT FOUND**。
- *裁决*：横向企业搜索 + RAG 平台 —— **正是铁律 3 判为死亡陷阱的那一类**。

**F. qKnow** —— **CLOSE**
- *License*：**不是 Apache-2.0** —— 是"Apache-2.0 **+ 附加条件**"：商业使用允许但**必须保留 qKnow 品牌**；
  白标/OEM/rebranding 需另购；**附加条款 2a 允许 Producer 单方面收紧或放宽条款**。
  每个源文件头都带该声明。**因 Apache 禁止附加限制，这已不属 OSI 开源。**
- *Activity*：本批最健康（280★，6 贡献者，9 天前提交）—— **但 0 个 GitHub Releases、无 CI**。
- *数据模型*：**Ontology NOT FOUND** —— 有的是**刻意的 schema-free 模型**
  （`DynamicEntity` + `@DynamicLabels` + `@CompositeProperty`）；`ExtSchema` 是**表→图 schema 映射**；
  "领域规则"只以 **Markdown 散文**存在于一个技能包里；Decision/Evidence/Provenance **NOT FOUND**。
- ⚠️ *命名陷阱*：它的 "Context"（`KbRuntime`）是**流程执行的变量表**，**不是企业上下文**。
- *裁决*：Java/Spring，**与 Python Kernel 没有一个类可 import**；
  且许可证要求任何被采纳产物**保留 qKnow 品牌可见**、**对方可单方面改条款**。

**G. KnowledgeOps Agent**（坐标推断）—— REFERENCE ONLY
- *License*：MIT 干净。*Activity*：活跃（13 天前），194★，**4 位贡献者**。
- ⭐ *意外发现*：**CI 是全部九个候选里最像样的** —— JaCoCo **覆盖率门禁**、CycloneDX SBOM，
  以及一个 **evaluator-contract job，断言 citation 命中率 ≥0.70 且幻觉率 ≤0.05**。
  另有 Testcontainers、**租户隔离测试**；CHANGELOG 记录了 MCP 适配器 SSRF 加固与
  跨租户任务劫持修复。**它把评测指标写成了 CI 契约，与 E1–E6 的门禁思路同源。**
- *数据模型*：**规则/策略真实**（`ActionPolicyGuard.evaluate(AgentAction)` 返回**带类型的拒绝原因**）；
  **工作流状态真实**（`WorkflowState.canTransitionTo` 显式转移表）；本体**浅**
  （带 `validFrom/validTo/confidence` 的时态三元组，无类无公理）；
  **Decision NOT FOUND**；Audit 是 **HTTP 访问日志，不是决策溯源**。
- *Evidence* ⭐：**不是一等对象** —— `EvidenceItem` 是从 RAG chunk 临时构造的内存 DTO，
  用**硬编码权重**（0.50/0.30/0.20）打分并**截断到 180 字符**；**任何迁移里都没有 `evidence` 表**。
- *Reuse*：Rules/Decision **1–2**、Workflow state **1**、Ontology **1**、Security **1**、**Evidence 0**。
- *对指令 §7 的直接回答*：问"Workflow State / Security / Evidence 是否有可复用实现"——
  **前两个有，Evidence 没有。**

**H. mcp-agent**（坐标推断）—— REFERENCE ONLY
- *License*：Apache-2.0 干净。*Activity* ⚠️：**最后 push 2026-01-25（约 8 个月）**，
  **138 个未关 issue** —— **实质已休眠**。其余指标很好（8,549★、60 贡献者、CI 完备）。
- *是什么*：Agent Runtime + MCP 框架。`executor/temporal/`（durable execution）、
  `workflows/`（orchestrator/router/swarm/parallel/evaluator-optimizer…）、
  `server/app_server.py`（129KB），以及一个**能部署到厂商云**的 CLI。
- *数据模型*：`core/context.py:66 class Context(MCPContext)` 是 **server 注册表 + 配置容器**，
  **不是领域上下文**；Rules/Evidence/Ontology **NOT FOUND**；`PolicyAction` 是 runtime 控制
  （何时重规划/停止），**不产生持久化决策记录**。
- *裁决*：**如指令所预测，它是 Agent Runtime reference 而非 Kernel foundation**；
  占据的正是我们的 RUNTIME 边界。可选借鉴其 MCP 客户端与模型网关（各 Level 2）。

**I. DataLogicEngine**（坐标推断）—— **CLOSE**，但**唯一的 Evidence 正面样本**
- *License* ⭐ **商业硬阻断**（已独立核验）：**PolyForm Noncommercial License 1.0.0**，
  2026-01-15 起从 MIT 改版。LICENSE 正文：*"Commercial use, production deployment in a business
  environment, or integration into a paid product requires a separate commercial license agreement."*
  MIT 的 SDK **不是漏洞**（`sdk/LICENSE_NOTICE.md` 明言由应用许可管辖）。1.4.0 及更早的 MIT **对当前代码无效**。
- *Activity*：6★；3 位贡献者**实际是一个人**外加 `claude`（77 次 AI 辅助提交）；
  **3,074 文件 / 386MB**；**文档体量压倒代码**（`HANDOFF.md` 110KB、`TODO.md` 115KB、
  `PRODUCTION_COMPLETION_PLAN_2026.md` **378KB**）。⚠️ 版本号三处矛盾
  （pyproject 4.4.3 / LICENSE 写 1.5.0+ / 唯一 tag `V1.0.4`）。
- ⭐ *Evidence 是一等对象*（**全部候选里唯一**）：`TraceEvidence` 带 `content_hash`(sha256)、
  **`locator`(page/section/line_range)**、`authority`、**三个时间戳**
  （`captured_at`/`effective_at`/`retrieved_at`）、`transformation_chain`、`permissions`、
  **`provenance_completeness` 评分**、`used_by_claims/personas/stages`；
  独立的 `TraceClaim`（`status = supported|partial|unsupported|contested`）；
  **一等的 `ClaimEvidenceLink` 关系对象**；甚至建模了 **`EvidenceConflict`**；
  `TracePolicyDecision`（`decision = allow|block|flag|redact` + `rationale`）。
  另有 `backend/compliance/evidence.py` **强制执行硬契约**（缺证据即抛 `ComplianceEvidenceError`），
  以及一个**真实的 OPA/Rego 规则闸门**（critical domain 要求 confidence ≥0.995 + 人工复核，
  **带确定性 Python 回退**）。
- *裁决*：**许可禁止任何代码复用** → `CLOSE`；但它的 **数据模型形状值得读（Level 1）**。
- *可抄的一条具体设计*：**Evidence 上的三个时间戳**（见 §11.2）。

---

## 5. Reuse Matrix

完整矩阵（能力 × 候选 × 等级）见 **`FOUNDATION_REUSE_MATRIX.md`**（含 Level 0–4 定义与
能力归属的逐行出处）。此处只给**结论性的最佳可得表**：

| Capability | V3 Owner | 最佳可得 | 等级 | 何时可用 | 保留 / 缺口 |
|---|---|---|---|---|---|
| Context Model | Kernel | Semantica | **3** | V1+ | **Permission scope 须自建**；`ContextGraph` 是内存实现 |
| Domain Ontology | Kernel | HugAgentOS | **2** | 参考 | 受工具调用形状限制；Semantica/TrustGraph 仅 1 |
| Entity / Relationship | Kernel | Semantica / TrustGraph | **2** | V1+ / 参考 | 两者都可用作**表示法**，独立于其运行时 |
| Business Rules | Kernel | HugAgentOS / Semantica | **2 / 1** | 参考 | **规则语言必须自建**；Semantica 的推理引擎可作后端 |
| Decision | Kernel | Semantica | **2/3** | V1+ | **形状可借，语义自建** |
| **Evidence** | Kernel | DataLogicEngine | **1** | **仅概念** | **代码许可阻断 → 必须完全自建** |
| Provenance | Kernel | **Semantica** | **3** | V1+ | 最值得关注的一项 |
| Context Update | Kernel | **Semantica** | **3** | V1+ | 决策变更 / 证据累积 API **不存在** |
| Knowledge Retrieval | Provider | Semantica / mcp-agent | 2 | V1+ | 与 V0 单库纪律冲突（见 §9） |
| Graph Storage | Infrastructure | Semantica（多后端门面） | 2 | V1+ | 鸭子类型，无 ABC；V0 不引入 |
| Vector Search | Provider | Semantica | 2 | V1+ | 同上 |
| Agent Runtime | Runtime | mcp-agent | 1 / **不要** | — | 明确越界 |
| Agent Loop | Runtime | — | 0 | — | 明确越界 |
| Workflow Execution | Runtime | mcp-agent / TrustGraph | 1 / **不要** | — | `RUNTIME_COMPARISON.md` 已覆盖运行时选型 |
| Queue / Retry / Durable | Runtime | Trigger.dev 等 | — | — | **不在本研究范围**（见 `RUNTIME_COMPARISON.md`） |
| MCP | Infrastructure | mcp-agent | **2** | V1+ | Apache-2.0 干净；**但项目已休眠 8 个月** |
| Model Gateway | Infrastructure | mcp-agent / Semantica | 2 | V1+ | ECE 铁律 5 已定 OpenAI 兼容端点 |
| Observability | Runtime | Semantica / HugAgentOS | 2 | V1+ | 标准栈（Prometheus/OTel），非创新 |
| Permission Enforcement | Kernel + Provider | 全部 ≤1 | **1** | — | **强制点必须自建**（铁律 1） |
| Connector | Provider | — | 0 | — | 只自建 ≤3 个 mock |
| Search | Provider | — | 0 | — | 不自建横向搜索 |
| **Domain Evaluation** | Kernel | **我们自己（E1–E6）** | — | **V0 已有** | 开源候选最强者也只有 Level 2，且语义不同（技能晋升 ≠ 领域决策正确性） |

---

## 6. Kernel Boundary Impact

指令 §16.6 要求四选一：

| 选项 | 是否成立 | 说明 |
|---|---|---|
| **No impact** | ✅ **成立** | 没有任何候选迫使修改 V3 边界、Kernel 核心、数据模型阶段归属或 V0 范围 |
| Implementation refinement only | ⚠️ **一处可选** | **Evidence 的溯源子模型对齐 W3C PROV-O**（§11.1）—— 只是字段命名与关系形状，不改架构、不引入依赖 |
| Potential ADR | ⚠️ **一处可选** | 若采纳上条，编号应为 **ADR-012**（当前最新为 ADR-011）。**本研究不代为签发** |
| Architecture conflict | ❌ **不成立** | 无任何候选与 V3 边界冲突 |

> **本研究不修改 V3、不修改 V0、不修改 PRD、不修改 KERNEL_BOUNDARY**（指令 §15 明令）。
> 上面两条"可选"是本研究的**建议**，是否采纳由 Codex / 用户决定。

---

## 7. Recommended Technical Composition

指令 §12 要求回答："如果我们希望最大限度减少自己写代码的数量，同时不破坏 V3 Kernel Boundary，
那么未来技术栈应该如何组合？"

**答案必须分成两栏** —— 因为 §2.7 已证明 V0 的冻结形态里**没有"接入一个底座"的位置**。

### 7.1 V0 可用（2–4 周闭环，**不引入任何 OSS**）

```
Domain Application
        ↓
Our Kernel Semantic Layer          ← 全部自建（六项能力）
        ↓
InProcessExecutor + LocalProvider  ← 直接调用，不建抽象层（V3_CLOSEOUT.md:106）
        ↓
PostgreSQL 单库（结构化 + FTS + pgvector + JSONB）
```

**这一栏里没有任何候选项目。** 这不是保守，是 `V3_CLOSEOUT.md:65-85` 的直接推论。

### 7.2 V1+ 才可用（冻结后的选型，**须先立 ADR**）

```
Domain Application
        ↓
Our Domain Kernel Semantics        ← 不变，仍全部自建
        ↓
OSS 可借的底层能力（Level 2–3）：
   · Semantica provenance/            ← Level 3（哈希链、PROV-O、ABC 存储、Turtle 导出）
   · Semantica context/context_graph  ← Level 3（时态撤回 + state_at + 快照恢复）
   · Semantica reasoning/             ← Level 2（**零 LLM 的推理后端**：Datalog/Rete/SPARQL）
   · TrustGraph 的 PROV-O 命名图设计   ← Level 2（**事实血缘**参考）
        ↓
Runtime（见 RUNTIME_COMPARISON.md，本研究不重做）：
   · Trigger.dev（Durable Execution）  · DSH（Agent Harness）  · PentAGI（领域 Agent 应用）
        ↓
Provider: Glean / GraphRAG / Enterprise APIs       ← 可替换
        ↓
Enterprise Systems
```

**必须自己拥有、不在这张图里外包的部分**：
Evidence（完整语义）· Deterministic Business Rules（规则语言与判据）· Domain Ontology ·
Decision 语义 · Permission enforcement point · Domain Evaluation。

### 7.3 一句判断

> 指令 §12 给了两种可能的形态：一种是把 OSS 插在"我们的 Kernel 语义层"与运行时之间；
> 另一种是"**OSS 目前没有一个合适的 Kernel foundation**，那就自己实现一个很薄的 Kernel 语义层，
> 下面全部复用成熟基础设施"。
>
> **证据支持后者**，但有一个重要修正：**"下面全部复用成熟基础设施"这句在 V0 不成立**
> （V0 用单库、单进程），而在 V1+ 成立 —— 但**能复用的"基础设施"里，没有一项是 Evidence 或规则**。

---

## 8. Build vs Reuse Boundary

指令 §16.8 要求五栏：

### Build ourselves（**必须自己拥有**）
- **Evidence**（完整语义：source / claim / time / actor / triggering agent / context / decision / execution reference）
- **Deterministic Business Rules**（规则语言 + 判据）
- **Domain Ontology**（领域概念 / 关系 / 约束 / 不变式）
- **Decision** 语义与 Decision Record
- **Permission enforcement point** + scope 契约（policy **来源**可外包）
- **Context Update** 的决策与证据语义（时态撤回机制可借）
- **Domain Evaluation**（已有 E1–E6，是本项目最强的资产）
- Context 的 **Permission scope** 维度

### Reuse OSS（**V1+，须先立 ADR**）
- **Provenance 机制**（Semantica `provenance/`，Level 3）—— 本研究的最高价值发现
- **时态撤回 / 时点状态**（Semantica `context_graph.py`，Level 3）
- **推理后端**（Semantica `reasoning/`，Level 2；**注意：引擎确定 ≠ 规则语言够用**）
- **MCP 客户端与模型网关**（mcp-agent，Level 2；**但项目已休眠，需评估替代**）
- **事实血缘设计**（TrustGraph，Level 2，参考）

### Provider
- Knowledge Retrieval（召回/融合/排序）· Enterprise Search · Connector · Glean
- **明确不自建**：横向搜索、275+ 连接器

### Runtime
- Trigger.dev（Durable Workflow / Queue / Retry / Scheduler）
- DSH（Agent Loop / Tools / Sandbox / Subagents）
- PentAGI（领域 Agent 应用）
- **明确不自建**：Agent Loop、Durable Execution Engine、通用工作流引擎

### Adapter
- 三类接口（`ProviderInterface` / `AgentRuntimeInterface` / `ExecutionRuntimeInterface`）
  是 **V1 方向**，**V0 不建抽象层**（`V3_CLOSEOUT.md:106`）
- **硬规则**：Kernel 源码中不得出现厂商标识符（CI 门禁，`KERNEL_ARCHITECTURE_V3.md:208-214`）

> **另有第六栏，本研究建议单列：标准（非项目）**
> - **W3C PROV-O** —— Evidence 溯源子模型的形状依据（Level 1，**零依赖，V0 即可对齐**）
> - **OMG DMN** —— 确定性业务规则/决策表的表达参考（Level 1，可选）

---

## 9. Risks

| 风险 | 具体 | 严重度 |
|---|---|---|
| **License** ⭐ 最主要 | **GSearchAI 无 LICENSE（法律不可用）**；**DataLogicEngine PolyForm Noncommercial（商业阻断）**；**HugAgentOS 白标/多租户 SaaS 需商业许可**（单组织私有化被明文允许）；**qKnow 必须保留品牌且对方可单方面变更条款**；**TrustGraph 的 CLA 正文在仓外、未读（UNKNOWN）** | **高**（其中两条为硬阻断） |
| **候选坐标不确定** | G/H/I 三个坐标是本研究的推断；`mcp-agent-framework` **不存在同名仓库** | **中**（若不确认，三节结论需重做） |
| **Abandoned project** | mcp-agent **8 个月未更新 + 138 未关 issue（实质休眠）**；OpenEAAP **8 个月 + 1★**；HugAgentOS 创建仅 2 个月、**2 位贡献者、后端无 CI** | **中** |
| **Architecture coupling** | HugAgentOS：ontology 闸门 = AgentScope 中间件，**硬编码在 3,536 行 workflow 内**，规则求值**需要工具注册表** → `ARCHITECTURAL COUPLING RISK` **结构性**；TrustGraph：**agent trace 与业务事实同表** + broker 强制 → **HIGH**；Semantica：**中等**（extras 隔离 + 懒加载，但一个 wheel 五入口） | **高**（A/C）**/** 中（B） |
| **Vendor lock-in** | TrustGraph **贡献者极度集中**（1 人 982 commits）→ 实质单厂商；Semantica 贡献者名单为空区块、少数维护者；HugAgentOS **是只读下游镜像**（fork 即 fork 生成产物） | **中** |
| **Data model incompatibility** | TrustGraph 固定 `Triple(s,p,o,g)`，**没有为新内核对象（Decision/Rule/Evidence）预留任何接口**；Semantica **无 `Evidence` 类型**；HugAgentOS `Constraint` 只能咬工具参数；qKnow 刻意 schema-free | **中** |
| **Security** | GSearchAI 仓库内含 3.7MB `response.md`、`vector.zip`、`scratch.py`、`tester_zone/`；OpenEAAP **提交了未解决的补丁冲突残骸**；HugAgentOS **后端无 CI**（ontology 区域测试仅 3 个文件对 4,761 行 ORM）；TrustGraph IAM **不做逐请求鉴权** | **中**（若采纳才上升为高） |
| **Migration cost** | **V0 为 0**（不引入任何 OSS）；V1+ 引入 Semantica 那部分需评估 wheel 拆分与依赖面 | **低**（当前） |
| **"开源替我们做差异化"的误判风险** | 若有人因为"Semantica 很强"就把它当底座，会**恰好把 Evidence 与 Rules 建在别人的语义上**——而那两项是 Kernel 的核心资产 | **中**（认知风险） |

---

## 10. Next Action

指令 §16.10："只给下一阶段技术验证建议。" 因此本节**不给路线图**，只给验证动作。

1. **不建议为"寻找 Kernel foundation"做技术 Spike。**
   本研究的结论是**没有可整体采用的底座**（§11 A/B）。为一个不存在的东西做 Spike 是浪费。

2. **唯一值得做的最小验证（可选，且建议推迟到 V0 闭环之后）**：
   验证 **Semantica 的 `provenance/` 与 `context/context_graph.py` 能否独立使用**。
   这是唯一 Level 3 候选，且它是**唯一可能改变"Evidence 之外的自建量"的项目**。
   **最小验证边界**（严格限定，不得扩大）：
   - 在**隔离环境**（新 venv，不进项目依赖）安装 Semantica 基础包；
   - **只 import** `semantica.provenance` 与 `semantica.context.context_graph`；
   - 断言四件事：① 不拉入 server/worker/explorer；② PROV-O 导出可用；
     ③ 时态撤回 + `state_at()` 可用；④ 依赖清单与私有化/离线要求相容；
   - **不写进生产代码、不改架构、不 vendor-in。**
   > 若验证失败，结论回到"全部自建"；若通过，也只是"V1+ 多一个可评估的选项"。

3. **V0 该做的事不因本研究改变**：Context Update 与 Evidence 本来就是 V0 必须落地的
   （`V3_CLOSEOUT.md:65-85`），而本研究**恰恰证明了它们没有开源替代品** ——
   这是一条支持"就按原计划做"的证据，而不是一条变更建议。

4. **可选的一条零成本精化**：把 Evidence 的溯源字段按 **W3C PROV-O** 的形状命名
   （`wasDerivedFrom` / `wasAttributedTo` / `used` / `wasGeneratedBy` 的语义，
   不必引入 RDF）。这不需要 ADR 也能做，但若要固化则建议立 **ADR-012**。

---

## 11. 最终判断（指令 §20 要求）

### A. 是否存在可以作为 Kernel Foundation 的 OSS？

**不存在"完整的"。存在"部分的"。**

没有任何候选覆盖 Kernel 的六项核心能力。最好的 **Semantica 覆盖三项**
（Context 结构化与时态部分 / Provenance / Context Update，均 Level 3），
但它的 **Evidence = 0、Business Rules = 1、Domain Ontology = 1、Permission = 1**。

### B. 如果存在，是整个 foundation，还是部分 component？

**部分 component —— 而且是少数几项，且不在最难的位置。**

Semantica 的 `provenance/`、`context/context_graph.py`、`change_management/`
对 `server`/`worker`/`explorer` import 干净，是真实的组件级可复用；
但**它覆盖的正好不是我们的差异化所在**（Evidence 与业务规则）。

⚠️ 一条必须同时说明的**削弱因素**：**不存在可单独构建的 `semantica-core` 发行包**
（那个"slim core"测试断言的是**依赖数量 == 22**，是打包保证，不是解耦产物）。

### C. 哪些部分我们应该直接复用？

按价值排序（**全部在 V1+，且须先立 ADR**）：

1. **Semantica 的 `provenance/`**（Level 3）—— 哈希链、PROV-O、ABC 存储、Turtle 导出
2. **Semantica 的时态撤回 + `state_at()` + 快照恢复**（Level 3）
3. **Semantica 的推理后端**（Level 2）—— **确定性的 Datalog/Rete/SPARQL，零 LLM**
4. **mcp-agent 的 MCP 客户端 / 模型网关**（Level 2）—— 但需评估休眠风险或替代
5. **标准对齐**：W3C PROV-O（**V0 即可，零依赖**）

### D. 哪些部分必须自己拥有？

**六项中的 Evidence 与 Deterministic Business Rules 必须完全自建**
（前者：九个候选无一建成可用的一等对象；后者：最好的也只是元数据谓词桩）。
**Domain Ontology、Permission scope、Decision 语义、Context Update 的决策/证据语义、
Domain Evaluation 也须自建**（可借形状，不可借语义）。

### E. 是否值得为 OSS foundation 做下一轮技术 Spike？

**不值得为"找底座"做 Spike**（没有底座可找）。
**但值得为"Semantica 的 provenance/ 能否独立使用"做一次极小的只读验证**
—— 因为它是唯一的 Level 3 候选，也是唯一可能真正减少自建量的项目。
**建议推迟到 V0 闭环之后**（V0 不需要它，且 V0 的结论不受它影响）。

### F. 如果做 Spike，最小验证应该是什么？

见 §10 第 2 条 —— 四步四断言，严格限定在隔离环境与只读范围，
**不得写进生产代码、不得改架构、不得 vendor-in**。

---

## 12. 报告状态

### **PASS WITH CONDITIONS**

研究任务本身完成：九个候选全部源码级考察，指令 §16 要求的十节齐备，
指令 §17 的证据纪律（Claim / Source / Evidence / Confidence / Last Verified）在
`FOUNDATION_REUSE_CODE_NOTES.md` 中逐条落实。

三个条件（**都不阻塞 V0**）：

| # | 条件 | 影响 |
|---|---|---|
| 1 | **确认 Candidate G/H/I 的仓库坐标** | 若 Codex 所指另有其库，这三节结论需重做 |
| 2 | TrustGraph 的 **CLA 正文在仓外**（*Fiduciary* CLA），未读到原文 | 仅在未来考虑采纳其 provenance 设计时才需要 |
| 3 | Semantica 的 `evals/` 深度为 **UNKNOWN** | 不影响结论（Domain Evaluation 我们本来就自建） |

### 本研究**未做**的事（指令 §15/§19/§21）

- ❌ 未修改 `PRD_V3.md` / `KERNEL_BOUNDARY.md` / `V3_CLOSEOUT.md` / 任何 V0 文档
- ❌ 未进入 V4
- ❌ 未修改任何架构
- ❌ **未把任何 OSS 引入 production code**
- ❌ 未安装依赖、未 fork、未迁移、未改数据库
- ❌ 未排名、未给 Overall Score、未推荐任何项目作为唯一底座

只做了：**READ → INSPECT → COMPARE → DOCUMENT**。

### 必须由你决定的事项

1. **G/H/I 三个候选的坐标**是否就是 Codex 所指（若不是，那三节需重做）。
2. 是否认可本研究的核心结论 —— **"不存在可整体采用的 OSS Kernel foundation；
   Evidence 与 Deterministic Business Rules 必须自建"** —— 这决定 V1+ 的路线。
3. 是否要就 **Evidence 溯源子模型对齐 PROV-O** 立 **ADR-012**（唯一的实施精化建议，不改架构）。
4. 是否要在 V0 闭环**之后**授权一次对 Semantica `provenance/` 的**最小只读验证**（§10 第 2 条）。
5. **HugAgentOS 的许可证条件**（白标 / 多租户 SaaS 需商业许可；单组织私有化明文允许）
   是否要纳入长期法务备案 —— 本研究**不建议采纳它**，故此项仅为备案。
6. 本研究**不改变 V0**。若你认可这一点，V0 按原计划继续。

**STOP。** 等待 Codex 审阅。**不自行进入技术 Spike，不自行签发 ADR，不进入 S2。**
