# KERNEL_BOUNDARY.md — Kernel 能力边界矩阵

> Version: 1.1（v1.0 = 2026-09-20 初版；v1.1 = 同日收口一致性修复）
> Date: 2026-09-20
> Status: **Active — 已收口，矩阵与 `V3_CLOSEOUT.md` §1 一致**
>
> ⚠️ **V3 收口修订（2026-09-20，v1.1）**：矩阵本体已按 `V3_CLOSEOUT.md` §1 逐行修正 ——
>
> | 行 | 修正 |
> |---|---|
> | 1 Permission Enforcement | 收窄为「仅**强制点** + scope 契约」；policy 来源可外包 |
> | 5 Knowledge / Retrieval | **拆分**：仅 Knowledge 留 Kernel；Retrieval 机制移出 → Provider |
> | 9 Domain Workflow Specification | 硬收窄为「仅业务判据 + 责任人 + 审批要求」；含执行顺序即移出 |
> | 10 Agent Selection / Action Planning | **降级为接口声明**（不再是 Kernel PRIMARY） |
> | 20 Tool Layer | 收窄为「仅 Tool **准入** / 权限收口」；选择与执行移出 |
> | 25 Private Deployment | **转约束行**（非能力，不计入所有权） |
>
> 另修正 §3.1 的权限判据（区分强制点与 policy 来源）与 §3.2 的 Workflow 示例（由执行顺序改为业务判据）。
> 逐项裁决依据见 **`V3_CLOSEOUT.md` §1**。**未新增任何能力、未重新设计 Kernel。**
> 关联: `docs/v3/PRD_V3.md` · `docs/v3/RUNTIME_COMPARISON.md` · `docs/v3/KERNEL_ARCHITECTURE_V3.md` · `docs/adr/ADR-011.md`
> 证据: `docs/v3/EVIDENCE_V3_ADDENDUM.md`（C43–C48）+ `docs/research_v2/evidence-matrix-v2.md`（C01–C42）

---

## 0. 本文件回答什么

一句话：

> **在一个企业业务闭环里，哪一层由 Kernel 拥有、哪一层由执行/上下文能力提供、哪一层属于企业系统本身。**

本文件是**裁决表**，不是描述表。每一格给出的是**所有权归属**，并且必须能回答"如果这一层消失，谁负责"。

---

## 1. 六个参与方（先定义清楚，否则矩阵无意义）

| 参与方 | 是什么 | 不是什么 |
|---|---|---|
| **Kernel**（Domain Intelligence Kernel） | 业务智能层：Context（含 Entity / Relation / Temporal / Permission scope）/ Domain Ontology / Deterministic Business Rules / Decision / Evidence。【**V3 收口**：Retrieval 机制、Tool 选择与执行、Agent·Runtime 动态选择、执行编排**均不属于 Kernel**；Agent/Runtime Selection 仅保留**接口声明**】 | 不是执行引擎，不是 Agent Harness，不是搜索引擎，不是连接器平台，不是编排器 |
| **Trigger.dev** | Durable Workflow / Execution Runtime：Tasks / Runs / Queues / Retry / Wait / Concurrency / Scheduling / Durable Execution / Observability [C43] | 不懂业务语义，不做业务决策 |
| **DSH**（DeepSeek Harness） | 插件化 Agent Runtime / Agent Harness：Agent Loop / Tools / Skills / Session / Sandbox / Subagents / Storage / Trajectory [C44] | 不提供企业上下文，不提供领域本体，不做跨 Agent 的业务语义共享 |
| **PentAGI** | 领域 Agent 应用（自主渗透测试）：多 Agent 监督 + 沙箱执行 + 模型无关 [C45] | 不是通用 Kernel；是被 Kernel 调用的一类 capability，也是"领域 Agent 应用"的参照物 |
| **Glean** | Provider：企业搜索 / 连接器 / 权限继承 / Enterprise Graph / Agent 能力 [C01–C42] | **不是** Kernel 的底座；是可插拔的一项 Provider |
| **Enterprise System** | 事实来源：ERP / OA / HRIS / 工单 / 文档库 / 合同库 / 数据仓库 | 不是 AI 系统；一切企业事实的最终权威 |

> **术语纪律**：本文件中 "Provider" ≠ "Kernel"。Provider 提供**原料**，Kernel 生产**业务结论**。

---

## 2. 主边界矩阵

**标注约定**：

- `PRIMARY` — 该层的主要所有者；这一层缺失等于该系统不成立
- `Adapter` — Kernel 通过接口调用它，Kernel 自己**不实现**
- `Tool` — 在该系统中作为可被调用的工具存在
- `Provider` — 可作为 Kernel 的一项数据/能力来源接入（可替换）
- `Source` — 事实来源
- `UNKNOWN` — 证据不足，不得作为设计前提（per `RESEARCH_PRD_V2.md` §4.5）
- `约束` — **非功能约束**，不属于任何一方「拥有」的能力，**不计入所有权**（见行 25）
- `—` — 不属于该系统的职责

| # | Capability | Kernel | Trigger.dev | DSH | PentAGI | Glean | Enterprise System | 证据 / 备注 |
|---|---|---|---|---|---|---|---|---|
| 1 | **Permission Enforcement**（访问裁决） | **PRIMARY**（仅**强制点** + scope 契约） | — | — | — | Provider（**policy 来源**：源系统 ACL 继承） | Source（ACL 事实） | ADR-003；ECE P2 铁律；C06/C07。**Kernel 在数据访问层强制，不靠 prompt**；**V3 收口**：policy **来源**可外包给 Provider，**强制点**不可（`V3_CLOSEOUT.md` §1.1） |
| 2 | **Business Context**（业务情境结构化状态） | **PRIMARY** | — | — | — | Provider（企业实体/关系原料） | Source | C02/C18；C47 |
| 3 | **Enterprise Entity / Relationship**（企业实体与关系） | **PRIMARY**（归一后） | — | — | — | Provider | Source | C18/C23；跨系统归一 = Kernel 自建（ADR-007） |
| 4 | **Domain Ontology**（领域本体：控制项↔证据、评标标准…） | **PRIMARY** | — | — | 领域内自带（安全测试本体） | UNKNOWN（schema 可定制性 = C03 永久 UNKNOWN） | — | ADR-009；**不得**把 Glean 的企业图谱等同于领域本体（见 §4） |
| 5 | **Knowledge / Retrieval** | **PRIMARY**（**仅 Knowledge 作为 Context 要素**） | — | Tool | Tool | Provider（**Retrieval 机制**：召回 / 融合 / 排序 + 横向搜索） | Source | ADR-006/K8；**V3 收口**：Retrieval 机制已**移出 Kernel** → Provider（`V3_CLOSEOUT.md` §1.1/§1.3）；**不重建横向搜索引擎** |
| 6 | **Evidence**（业务证据对象） | **PRIMARY** | Execution Reference（run/trace，**非业务证据**） | Agent Output | Agent Output | Provider（可作证据来源） | Source | 见 §5 Evidence 模型；**这是 V3 新增的一级对象** |
| 7 | **Reasoning**（业务推理） | **PRIMARY**（规则优先 + LLM 轻量） | — | Agent-level（模型推理） | Agent-level | Agent-level | — | ADR-010；C22/C23 仅反证式表述 |
| 8 | **Business Decision**（业务裁决） | **PRIMARY** | — | Agent 产出建议 | Agent 产出建议 | Agent 产出建议 | 人类最终负责 | 采购场景 v0 定位"建议生成"非自动决策 |
| 9 | **Domain Workflow Specification**（业务上应怎么做） | **PRIMARY**（**仅业务判据 + 责任人 + 审批要求**） | — | — | — | — | — | **V3 新概念**；**V3 收口**：硬收窄 —— **一旦含执行顺序 / 分支 / 重试 / 并发，即移出 Kernel**（`V3_CLOSEOUT.md` §1.1）；见 §3.2 |
| 10 | **Agent Selection / Action Planning** | **V0: 固定 Agent**（**无 Selection 概念**） | — | — | — | — | — | **V3 收口**：去掉后 Kernel 仍能产出 Decision，故不作核心能力。**Codex 第二轮判词 §3 修正**：V0 只有一个固定 Agent，因此 **V0 根本不存在 Selection** —— 工程上必须理解成「V0: Fixed Agent」，**不是**「Agent Selection Interface」，否则极易被实现成一个多余的 selector。动态选择推迟到 V1，且届时须另写 ADR |
| 11 | **Policy**（业务规则/合规策略） | **PRIMARY** | — | — | 领域内自带 | Provider（Glean Protect = 平台安全策略） | Source | 注意区分：Kernel Policy = **业务规则**；Glean Protect = **平台安全** |
| 12 | **Domain Evaluation**（业务正确性） | **PRIMARY** | — | — | 领域内自带 | **反证式空白**（C22 收紧后措辞，见 §6） | — | ADR-008；最高 IP 声明必须带限定语 |
| 13 | **Platform Observability**（采纳率/错误率/ROI） | 简化版 | PRIMARY（run tracing） | Trajectory | Langfuse 集成 | PRIMARY（完整版） | — | C14；Row 13 裁决 = Build 简化 + Integrate 完整 |
| 14 | **Workflow Execution**（可靠执行） | **Adapter** | **PRIMARY** | — | — | — | — | C43；Kernel **不实现** queue/retry/scheduler |
| 15 | **Agent Runtime / Harness** | **Adapter** | — | **PRIMARY** | **PRIMARY**（领域特化） | Provider | — | C44/C45 |
| 16 | **Agent Loop** | — | — | **PRIMARY** | **PRIMARY** | Provider | — | Kernel **不实现** agent loop |
| 17 | **Queue / Retry / Scheduler** | — | **PRIMARY** | Runtime dependent | Runtime dependent | Provider | — | 铁律 3 禁止自研 |
| 18 | **Durable Execution / Checkpointing** | — | **PRIMARY** | Runtime dependent | Runtime dependent | — | — | C43 |
| 19 | **Sandbox / 隔离执行环境** | — | — | **PRIMARY** | **PRIMARY** | — | — | C44/C45 |
| 20 | **Tool Layer / Tool Contract** | **PRIMARY**（**仅 Tool 准入 / 权限收口**） | Tool execution | Tool | Tool | Provider（Remote MCP Server） | — | ADR-004；C19；工具**准入**归 Kernel；**V3 收口**：工具**选择与执行移出 Kernel** → Runtime/Harness（`V3_CLOSEOUT.md` §1.1/§1.3） |
| 21 | **Enterprise API Access** | **Adapter** | Tool execution | Tool | Tool | Connector | **PRIMARY** | — |
| 22 | **Enterprise Search** | Provider | — | Tool | Tool | **PRIMARY / Provider** | Source | 明确**不自建**横向搜索（capability-matrix-v2 Row 2） |
| 23 | **Connector Ecosystem** | 自建框架 + 3 个 mock | — | — | — | Provider（275+） | Source | C05/C09；**绝不自建 275+** |
| 24 | **Temporal Context**（as_of / 有效期） | **PRIMARY** | — | — | — | UNKNOWN | Source | ECE 已有 `relationships.valid_from/valid_to` |
| 25 | **Private Deployment**〔**约束行**〕 | **约束**（非能力） | 可自托管（Apache 2.0）[C43] | 本地可运行 [C44] | 可自托管 [C45] | SaaS 为主（约束下不适用） | 约束来源 | **V3 收口行**：**非功能约束，不属于任何参与方「拥有」的能力，不计入所有权**（`V3_CLOSEOUT.md` §1.4）。红队 v3 主路径 D：数据主权 = 中国市场的信任货币 |
| 26 | **Model Independence** | **PRIMARY**（OpenAI 兼容端点） | — | **PRIMARY**（无强制供应商）[C44] | **PRIMARY**（多供应商）[C45] | Provider | — | ECE 铁律 5：LLM 不可知 |

**行数**：26（指令草表 15 行；补充 11 行，其中 `Permission Enforcement` / `Domain Evaluation` / `Temporal Context` / `Policy` 为关键补漏）。
**其中行 25 为约束行**（非能力，不计入所有权）—— 即 **25 行能力 + 1 行约束 = 26 行**。

**V3 收口后 Kernel 仍为 `PRIMARY` 的行**（6 行收口改动后逐行核验所得）：

```
行 1  Permission Enforcement      仅强制点 + scope 契约
行 2  Business Context
行 3  Enterprise Entity / Relationship
行 4  Domain Ontology
行 6  Evidence
行 7  Reasoning                   规则优先
行 8  Business Decision
行 9  Domain Workflow Specification  仅业务判据 + 责任人 + 审批要求
行 11 Policy
行 12 Domain Evaluation
行 24 Temporal Context
```

**已不再是 Kernel `PRIMARY` 的行**：行 5（仅 Knowledge 保留）、行 10（**V0: 固定 Agent，无 Selection**）、行 20（仅 Tool 准入）、行 25（转约束行）。

---

## 3. 本矩阵最重要的三行

### 3.1 行 1 — Permission Enforcement（**概念上应读作 Enforcement Boundary**）

**这是 Kernel 之所以是 Kernel 的第一理由。**

> ⚠️ **Codex 第二轮判词 §3 修正**：把这一项理解成 **IAM（身份与访问管理）** 是错的。
> Kernel 拥有的不是"一套账号体系"，而是 **enforcement boundary**：
> **在哪一点上裁决、按什么 scope 裁决**。
> 身份目录、组同步、凭据轮换、策略库都可以来自外部（Provider / 企业 IAM）；
> **Kernel 只负责那个不可外包的裁决点**。
> 这也修正了 `V3_CLOSEOUT.md` §1.1 的一处措辞含混 —— 那里把「企业交付前提」与
> 「Kernel 核心能力」混在一起说；正确的表述是：**Kernel 拥有 enforcement point + scope contract，
> policy source 可以外部提供。**

- 企业的第一道墙不是"数据不够"，而是"谁可以看到什么"（红队 v3 §0.1：企业森严的部门壁垒）。
- 若权限靠 prompt 约束（"请不要回答没有权限的信息"），则整个系统在企业场景**不可交付**——法务/审计不接受。
- 因此 Kernel 必须在**数据访问层**（SQL 子查询）强制，而非检索后过滤（post-filter 会通过排序/计数侧信道泄露）。
- **不与任何 Runtime 共享**：Trigger.dev / DSH / PentAGI 都不做这件事，也不应该做。

> **判据**：任何设计方案若把权限的**强制点**放到 Kernel 之外，直接否决。
> （**V3 收口补充**：policy **来源**可以是 Provider —— 例如 Glean 的源系统 ACL 继承；但**强制点**必须在 Kernel。二者不可混淆。）

### 3.2 行 9 — Domain Workflow Specification

**这是 V3 相对 V2 的新增维度，也是 Kernel 与执行运行时的分水岭。**

| | Domain Workflow Specification | Execution Workflow |
|---|---|---|
| 归属 | **Kernel** | Trigger.dev / 任意执行运行时 |
| 表达 | "业务上应该怎么完成这件事" | "计算机实际上怎么可靠执行这些任务" |
| 示例 | 供应商年度准入：**需核查的判据**（质量记录在覆盖期内无重大不合格 / 合同在有效期内 / 财务无逾期 / 准入标准满足）＋ **责任人**（采购负责人）＋ **审批要求**（超阈值须财务复核） | Task A → Task B → Wait → Task C → Human Approval → Task D |
| 变化频率 | 低（业务规则变化时） | 高（工程/基础设施变化时） |
| 谁看懂 | 业务专家 | 工程师 |

**两者不可混为一谈**，也不可合并成一张图。Kernel 产出前者，映射到后者由 Adapter 完成。

> ⚠️ **V3 收口（硬收窄）**：Domain Workflow Specification **只描述「业务判据 + 责任人 + 审批要求」**。
> **一旦包含执行顺序、分支、重试、并发，即成为执行编排器，立即移出 Kernel**（`V3_CLOSEOUT.md` §1.1）。
> 上表左列的 Example 已按此重写为**判据形式**，不再使用箭头序列。

### 3.3 行 24（Temporal Context）+ 行 25（Private Deployment，**约束行**）

这两项是**中国市场的入场券**（红队 v3 §0.6/§0.7.3），但**性质不同**：

- **Temporal（行 24，能力）**：审计/合规/采购结论几乎全部是时间相关的（"这条政策在审计期内是否有效"）。没有时态的企业 Context 在审计场景直接失效。→ 归 Kernel（Context 的组成部分）。
- **Private（行 25，约束）**：数据不出域。这不是"部署选项"，是**架构前提**。若 Kernel 的任一必需层只能跑在 SaaS 上，则整个产品在中国可达市场不成立。
  → **它不是一个"能力"，因此没有所有者归属**；它是施加在**所有层**上的约束（见 §2 行 25 的「约束行」标注与 `V3_CLOSEOUT.md` §1.4）。

---

## 4. 一个必须避免的概念混淆：Glean Enterprise Graph ≠ Domain Ontology

行 3 与行 4 必须分开看：

| | Glean Enterprise Graph | Kernel Domain Ontology |
|---|---|---|
| 内容 | 企业里**有哪些**人/团队/文档/项目及其关系 | **这个领域的业务语义**：控制项需要哪些证据、证据充分性判据、评标标准… |
| 回答 | "谁是谁、谁和谁有关" | "这份证据够不够格、这个采购申请合不合理" |
| 来源 | 企业系统连接 + 归一 | 领域专家知识 + 客户在使用中沉淀 |
| 可迁移性 | 换公司要重连 | 换公司**基本可复用**（同一领域） |
| 证据状态 | C02 CONFIRMED（存在）；schema 可定制性 **C03 UNKNOWN** | 我方自建（ADR-009） |

**v0.1 PRD 的错误**：把 Domain Ontology 放在"我们拥有"的同时，把 Context/Search/Permission 划给 Glean，导致 Kernel 失去企业上下文的所有权，退化为"一个领域插件"。**V3 的修正**：Kernel 拥有企业上下文层；Glean 只是这一层的一个**可选原料来源**。

---

## 5. Evidence 模型的边界（V3 新增一级对象）

行 6 是 V3 相对 V2 的第二个新增维度。四种"产出"必须严格区分：

| 产出 | 产生者 | 回答的问题 | 例 |
|---|---|---|---|
| **Execution Reference** | Trigger.dev / Runtime | "这段代码跑了多久、成没成功、重试几次" | run_id, span, 耗时, 状态 |
| **Agent Output** | DSH / PentAGI / 任意 Agent | "Agent 说了什么、调了什么工具" | 消息流, tool call, 轨迹 |
| **Business Evidence** | **Kernel** | "**这个业务结论是怎么产生的**" | 来源 + 主张 + 时间 + 行为人 + 触发 Agent + 所用 Context + 决策 + 执行引用 |
| **State Change** | Enterprise System | "企业事实变了什么" | 供应商状态更新, 任务已派工 |

**Kernel 的 Evidence ≠ Runtime 的 Execution Reference。** 前者是业务可追溯性，后者是工程可观测性。二者需要**关联**（Evidence 里带 execution_reference），但**不可互相替代**。

企业场景里真正被追问的是前者："你为什么得出这个结论？依据在哪？谁批准的？"——DSH 的 Trajectory 回答不了这个问题，Trigger.dev 的 tracing 也回答不了。

---

## 6. 关于"Glean 空白"的表述纪律（强制）

C22 / C23 是 `STRONGLY_INFERRED` 且**无来源 URL**（见 `EVIDENCE_V3_ADDENDUM.md` §3）。行 4 / 行 12 引用时**必须**使用 V2 已批准的反证式措辞，不得简写为事实：

> **未见 Glean 提供领域正确性 / 业务推理质量评估的公开证据；官方 Agent 治理文案出现的 "evaluations" 语义指向执行路径与性能（C38），不构成 domain evaluation 的证据。**
> —— `docs/research_v2/07-governance-evaluation.md:57`

同理，"Glean 无领域本体能力"必须写成"**未见公开证据表明 Glean 的 Enterprise Graph schema 支持自定义领域本体（C03 = UNKNOWN）**"，而非"Glean 不能做本体"。

**理由**：一旦这两条推断被证伪，Kernel 的"最高 IP"论题需要重估。把推断写成事实，就是把整个架构押在一条没有 URL 的论断上。V3 的保守假设是：**若 Glean 真做了，则我方该层 IP 价值减损，但 Kernel 边界仍然成立**（因为 Kernel 的自建理由是私有化部署与领域纵深，不只是"Glean 没有"）。

---

## 7. Kernel MUST NOT（结构性禁止清单）

以下每一项都有成熟实现，**Kernel 重建即违规**（铁律 3 + 红队 v3 §0.7.2"横向 = 死亡陷阱"）：

```
❌ Queue / Retry Engine / Scheduler / Concurrency Engine / Worker Runtime
      → 属 Trigger.dev 类执行运行时 [C43]
❌ Durable Execution / Checkpointing Engine
      → 属 Trigger.dev 类执行运行时 [C43]
❌ Agent Loop / Session Runtime / Sandbox / Subagent Runtime
      → 属 DSH / PentAGI 类 Agent Harness [C44][C45]
❌ 横向企业搜索引擎（100+ 源、排名算法）
      → 属 Glean 类 Provider；V2 已裁决"Buy/Integrate，不做横向"
❌ Connector 平台（275+ 连接器、连接器市场）
      → 属 Glean 类 Provider；仅自建 ≤3 个 mock 连接器框架
❌ Agent Builder UI / Prompt 市场 / Skill 市场 / 通用多 Agent 编排平台
      → 通用 Agent 平台 = 红海
❌ 通用 RAG pipeline / "上传文档→问答" 产品
❌ 向量数据库平台 / 通用 Graph 数据库平台
❌ 多租户 SaaS 计费 / 企业级 Admin Console / K8s / 微服务 / 消息队列
      → 除非 ADR 明确推翻（铁律 3）
❌ 模仿 Glean 同款的 execution-path 评估
      → 语义不同，模仿即失去差异化（platform-kernel-definition §6）
```

**判定测试（四问，缺一即不自建）**：

1. 这是业务语义层，还是执行/基础设施层？——执行层 → 不自建
2. Glean / 开源 / 运行时是否已提供且成熟？——是 → 不自建
3. 是否是 V0（2–4 周）闭环的必需项？——否 → 缓建
4. 是否产生领域 IP（换公司仍可复用）？——否 → 不自建

---

## 8. 反向问题："Kernel 到底比 DSH 多了什么？"

这是本文件必须正面回答的核心质疑。**不允许**回答"更多 Memory"或"更多 Knowledge"——那是量变，不是边界。

按业务语义回答（每一行都是 DSH **在架构上不负责**的）：

| Kernel 独有 | 为什么 DSH 不负责 | 缺失后果 |
|---|---|---|
| **领域本体** | DSH 的 Ontology 概念不存在；它是 harness，不是 domain model | Agent 无法判断"证据够不够格"，只能生成"看起来合理"的文本 |
| **企业实体归一** | 单 Agent 视角无跨系统归一义务 | 同一供应商在 ERP/OA/合同里三个名字 → 结论遗漏或重复 |
| **权限在数据访问层强制** | DSH 不管企业 ACL；沙箱 ≠ 权限 | 越权数据进入 Agent 上下文 → 企业不可交付 |
| **时态上下文** | Session 生命周期 ≠ 业务有效期 | "政策在审计期内是否有效"无法回答 |
| **业务规则引擎** | LLM 推理 ≠ 确定性业务规则 | 审计/采购的合规判断不可依赖"模型感觉" |
| **领域评估** | Trajectory 评的是过程，不是业务正确性 | 无法回答"这个结论对不对"，只能回答"Agent 做了什么" |
| **Evidence（业务证据对象）** | Session log 是工程记录，不是业务证据 | 企业追问"依据在哪"时无答案 |
| **Domain Workflow Specification** | Harness 表达的是执行，不是业务语义 | 业务专家无法参与定义与审阅流程 |
| **跨 Agent 的业务语义共享** | Subagent 共享的是 harness 状态，不是业务 Context | A 的结论无法作为 B 的业务前提被审计 |
| **跨运行时/跨模型的业务连续性** | 绑定在单一 harness 内 | 换 harness 即丢失业务上下文历史 |

**一句话**：

> **DSH 让 Agent 能干活；Kernel 让 Agent 干对的事、且干得可追溯、可授权、可在企业内交付。**

---

## 9. 边界自检（拿掉测试）

按 V3 指令 §37 的 Architecture Success Test，逐个拿掉外部系统，Kernel 是否仍然成立：

| 拿掉 | Kernel 是否成立 | 依据 |
|---|---|---|
| Trigger.dev | ✅ 成立 | 行 14 = Adapter。换任意执行运行时（含自建薄执行器）不改变 Kernel 语义 |
| DSH | ✅ 成立 | 行 15/16 = Adapter。E1（实体消歧）已证明 Kernel 可在无 Agent Harness 时独立产出结论 |
| PentAGI | ✅ 成立 | 行 15。它只是可被调用的一类 capability |
| Glean | ✅ 成立 | 行 2/3/22/23 皆为 Provider 或"不自建"。ECE v0 已在无 Glean 环境下跑通（C47） |
| 所有具体 LLM | ✅ 架构成立、⚠️ 质量待验 | 铁律 5：OpenAI 兼容端点；红队 §0.7 要求国产开源模型实测（**尚未执行**） |

**结论**：五项测试全部通过。但注意第 5 项的限定语——**架构上成立不等于质量上成立**，国产模型实测是尚未完成的验证项（红队 §0.7 Step 0.7），不得当作已验证。

---

## 10. 与既有 ADR 的一致性

| 既有 ADR | 与本文件关系 |
|---|---|
| ADR-001 Context Adapter 抽象 + Mock-first | 本文件是其**推广**：Adapter 从"上下文后端"扩展为三类接口（Provider / Agent Runtime / Execution Runtime） |
| ADR-003 Permission Engine | 本文件行 1 的原始来源，**不修改** |
| ADR-004 MCP Tool Layer | 本文件行 20 的来源；补充"工具准入归 Kernel、执行归 Runtime" |
| ADR-006 Context Assembly | 行 2/5 的来源，**不修改** |
| ADR-008 Domain Evaluation | 行 12 的来源，**不修改** |
| ADR-009 / 010 Ontology / Reasoning | 行 4 / 行 7 的来源，**不修改** |
| `platform-kernel-definition.md:174` | "Kernel 自建不可替代，Glean 集成作为可选 Adapter，不替换 Kernel" —— 本文件把其中"Glean"泛化为"任意 Provider 与任意 Runtime" |
| **ADR-011（本 V3 新增）** | 把本文件 §7/§8/§9 固化为可执行的运行时边界决策 |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
