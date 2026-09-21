# Foundation Reuse Study — 最小裁定版（仅在整包超限时使用）

> ⚠️ **这是删节版，不是全文合并。** 只含裁定所需的最小集合：结论、A–F 终判、报告状态、主矩阵。
> 删节方式是**整节丢弃，绝不改写任何一节**。被删部分见合并包 1–3 与三份源文件。
> **仅在整包超出 Codex 输入上限时使用这一份。**
>
> 仓库 `domainAgentECE` ｜ 目录 `docs/research/` ｜ 生成 2026-09-21

==============================================================================
==============================================================================
# 来源文件：`FOUNDATION_REUSE_STUDY.md`
> §1 Executive Summary · §11 最终判断（指令 §20 的 A–F）· §12 报告状态
==============================================================================

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
九个候选全部完成源码级考察（3 个 `CLOSE`、5 个 `REFERENCE ONLY`、1 个可"取零件"）。
**没有任何一个候补能覆盖 Kernel 的六项核心能力。**

> ⚠️ **考察范围的一处限定**（Codex 裁定 §一 要求修正；原文曾简写为"九个候选全部源码级考察完毕"）：
>
> **六个候选（A–F）的仓库坐标由指令明确给出**（`ZJU-REAL/HugAgentOS`、`semantica-agi/semantica`、
> `trustgraph-ai/trustgraph`、`turtacn/OpenEAAP`、`GramosoftAI/GSearchAI`、`qiantongtech/qKnow`）；
> **三个候选（G/H/I）指令未给仓库坐标**，其中 `mcp-agent-framework` 在 GitHub 上**不存在同名仓库** ——
> 本研究**采用了替代坐标（最接近者）进行调查**。
>
> 因此准确表述是：**六个明确坐标候选 + 三个采用替代坐标调查的候选**，
> **后三者的结论以坐标推断为前提，需确认**。
> 不应被读成"九个都经过了同等确定性的 repo identity verification"。
>
> （Codex 裁定原文此处写作"八个明确坐标候选"；经复核指令原文，
> **明确给出路径的是六个（A–F）**，此处按实际数量更正。）

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

------------------------------------------------------------------------------

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

------------------------------------------------------------------------------

## 12. 报告状态

### **PASS WITH CONDITIONS → 研究任务已关闭**

> **Codex 裁定（2026‑09‑21）**：*"这份 Foundation Reuse Study 的核心结论基本成立，
> 而且与我们前面的 V3 架构判断是相容的"* —— 不建议回头改 V3，也不因此做 V4。
> **Foundation Reuse Study 可以正式关闭。** 详见 §13。

研究任务本身完成：九个候选完成源码级考察（其中三个采用替代坐标，见 §1.2 限定），
指令 §16 要求的十节齐备，指令 §17 的证据纪律
（Claim / Source / Evidence / Confidence / Last Verified）在
`FOUNDATION_REUSE_CODE_NOTES.md` 中逐条落实。

三个条件（**都不阻塞 V0**）：

| # | 条件 | 处置 |
|---|---|---|
| 1 | **Candidate G/H/I 的仓库坐标** | ⚠️ **仍需确认**。表述已按 Codex §一 修正（§1.2 限定）；若 Codex 所指另有其库，这三节结论需重做。**不阻塞 V0** |
| 2 | TrustGraph 的 **CLA 正文在仓外**（*Fiduciary* CLA），未读到原文 | ✅ **按 Codex §二 降级**：现在不必解决。仅当**真的要 fork / vendor / 修改 / 分发其代码**时才进入法务确认；若只是"参考其 PROV-O 命名图设计"则无碍 |
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

---

------------------------------------------------------------------------------

==============================================================================
# 来源文件：`FOUNDATION_REUSE_MATRIX.md`
> §3 主矩阵（Capability × Candidate × Reuse Level）
==============================================================================

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

------------------------------------------------------------------------------
