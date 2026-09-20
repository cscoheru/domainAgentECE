# PRD_V3.md — Domain Intelligence Kernel

> Version: 3.0
> Date: 2026-09-20
> Status: **Active — 已收口**
>
> ⚠️ **V3 收口修订（2026-09-20）**：Codex 独立审查判定「Kernel 职责有向 Agent Platform 膨胀的风险；V0 与 2–4 周不匹配」。
> **§17（Agent Selection）、§32（V0 Scope）、§16.2（Workflow 步骤序列示例）已被 `V3_CLOSEOUT.md` 取代**；
> §22/§23/§24（Adapter 设计）推迟。**其余章节不变。**
> **V3 = Architecture Hypothesis，不是 Product-Market Validation。**
> 取代关系：本文件**不废除** `RESEARCH_PRD_V2.md`（降级为 V2 阶段交付物，保留不删，作为证据链与决策史）
> 上游输入：`RESEARCH_PRD_V2.md`（V2 Master PRD）· `RED_TEAM_REVIEW.md`（v3 战略约束）· `docs/research/`（v1）· `docs/research_v2/`（v2，C01–C42）· `docs/architecture_v2/`（K1–K8 定义）· `docs/product_v2/reference-applications.md` · `docs/v3/EVIDENCE_V3_ADDENDUM.md`（C43–C48）· 用户指令文件（2026-09-20）
> 治理文件：根 `CLAUDE.md`（商业战略）· `ece/CLAUDE.md`（工程铁律）

---

## 1. Executive Summary

**Kernel 是业务智能层，不是基础执行层。**

本项目要构建的是一个 **Domain Intelligence Kernel**：它把企业业务 Context、领域语义、知识、证据、推理、决策与业务工作流**组织起来**，并据此**选择**合适的 Agent / Runtime / Model / 企业系统去完成业务闭环。

核心定位声明（V3 的宪法条文）：

> **Kernel 不是 Trigger.dev，不是 DeepSeek Harness，不是 PentAGI，也不是它们的竞争品；Kernel 位于这些执行能力之上，负责企业业务 Context、Domain Semantics、Reasoning、Decision 和 Agent/Workflow Selection。**

V3 相对 V2 的三处实质推进：

1. **对照系扩展**。V2 只把 Kernel 与 Glean 对照；V3 把对照系扩展到**执行运行时（Trigger.dev）**与 **Agent Harness（DSH / PentAGI）**，并明确 Kernel 位于二者之上。
2. **两个新的一级对象**：**Evidence**（业务证据）与 **Domain Workflow Specification**（业务工作流语义，区别于执行工作流）。
3. **Glean 降到 Provider**。从 v0.1 的"底座"、V2 的"可选 Adapter"，降为 V3 的"**可插拔 Provider 之一**"，与本地知识库 / 企业 API / MCP / 开源栈并列。

**本阶段不写生产代码。** 交付物为 6 份文档 + 1 个 ADR，完成后 STOP，等人工审阅 `PRD_V3 + KERNEL_BOUNDARY + RUNTIME_COMPARISON` 三份文件。

---

## 2. Problem Definition

### 2.1 真正的问题

企业 AI 的失败，绝大多数不是"模型不够强"，而是**Agent 在错误的业务上下文中工作**：

| 失败形态 | 表现 | 根因 |
|---|---|---|
| **越权** | Agent 看到了不该看的数据 | 权限没在数据访问层强制 |
| **无依据** | 结论说得通，但没人知道依据是什么 | 缺少业务证据对象 |
| **错在语义** | 结论格式正确但业务上错误 | 没有领域本体与确定性规则 |
| **断在时间** | 用的是过期政策/失效合同 | 没有时态上下文 |
| **不可交付** | 企业不敢让它真正执行 | 不可授权、不可审计、不可追溯 |
| **不可复用** | 换个 Agent 就得重来 | Context 不是共享语义层，而是巨大 prompt |

### 2.2 问题不在检索层

RAG 解决的是"找得到"；企业的痛点早已越过这一层。红队 v3 的判定是：**必须先"持续维护企业自己的上下文"，才谈得上连接各信息孤岛**，并且 AI-native 不等于"上下文以后再说"——第一个工作流就必须带着窄切片上下文运行，否则退化为纯 RAG 问答，跌入红海。

### 2.3 问题也不在编排层

Trigger.dev 类运行时解决"任务可靠跑完"；DSH 类 harness 解决"Agent 持续工作"。两者都在**执行**维度上成熟，且都在快速商品化。真正的空白在**判断**维度：做什么、为什么做、基于什么做、谁授权、如何追溯。

---

## 3. Strategic Context

### 3.1 可达市场约束（红队 v3 主路径 D）

| 项 | 内容 | 证据 |
|---|---|---|
| 可达市场 | **中国大陆** | U-G1 由 UNKNOWN 翻为 CONFIRMED（无 Glean 客户） |
| 信任货币 | **数据主权**（私有化部署 + 国产开源模型 + 数据不出域） | 红队 v3 §0.6 |
| 部署形态 | 私有化优先，SaaS 不是唯一模式 | 红队 v3 §0.8 |
| 不可做 | 横向平台（连接一切 + 通用搜索 + 通用 Agent 平台） | 红队 v3 §0.7.2「横向 = 死亡陷阱」 |
| 正确姿势 | **Workflow-first, Context-accretes** | 红队 v3 §0.7.2 |

### 3.2 Glean 的新定位

**Glean Partner = Optional；Kernel = Main Track。** Partner 路径已取消（用户决定，`research_v2/README.md:21`）；若 Glean 重新联系，可作为 Provider 或 Partner 通道探索，但**PRD V3 不依赖 Glean Partner approval**。

### 3.3 为什么 P0 问题变了

V2 的核心问题是"我们自己做哪 20%、借 Glean 哪 50%、OSS 哪 30%"。
V3 的核心问题是"**在执行能力已经商品化的世界里，什么是不随执行能力变更而失效的产品价值？**"

答案：

> **企业业务 Context + 领域语义 + 推理 + 决策 + 业务工作流 + 证据 + Agent/Runtime 选择。**

这七项合起来就是 Kernel。它们不依赖 Glean，不依赖 Trigger.dev，不依赖 DSH，不依赖任何具体 LLM。

---

## 4. Lessons From V2 Research

### 4.1 做对了什么

| 项 | 结论 |
|---|---|
| 证据纪律 | Claim / Source / Evidence / Confidence / Last Verified 五要素；UNKNOWN 不得作为设计前提 |
| 分层重建 | Glean 四模块 + 九层堆叠（官方 / 半官方 / 推断 / 未知四分） |
| 能力矩阵 | 16 能力 × 8 列，每格挂 C 编号或标 `?` |
| Kernel 最小集 | K1–K8 + D1，并给出"缺失即不成立"的准入判据 |
| Reference Application 语义 | 明确"**Reference Application ≠ 产品定义**"，三个样本仅作 Kernel 验证 |
| 反锁定 | `portability.md` + `platform-kernel-definition.md:174`：Kernel 自建不可替代，集成是可选项 |

### 4.2 做错了什么（V3 必须修正）

| 缺陷 | 事实 | V3 修正 |
|---|---|---|
| **C22/C23 无来源 URL** | "Domain 层是 Glean 空白"整条论题建立在无 URL 的推断上；仅被"收紧"从未被确认 | 强制使用反证式措辞；且把自建理由**重心从"Glean 没有"移到"私有化 + 领域纵深"**（见 §7.3） |
| **对照系只有 Glean** | V2 的 Kernel 定义是"相对 Glean 的最小不可替代集"，一旦 Glean 补齐领域能力，Kernel 的存在理由被削弱 | V3 把对照系扩展为"Provider + Runtime"，Kernel 边界改为**类别级** |
| **未定义执行维度** | V2 未讨论 Kernel 与执行运行时/Agent Harness 的关系 | V3 §18/§19 + ADR-011 |
| **无 Evidence 一级对象** | EvidenceIQ 里有"证据"，但架构层未把 Evidence 建模为一等公民 | V3 §14 Evidence Model |
| **无 Workflow 语义分层** | 业务工作流与执行工作流混为一谈 | V3 §16 Domain Workflow Specification |
| **v2 文档残留缺陷** | `research_v2/README.md` 陈旧重复行、缺口计数错误（写 4 个实际 5 个）、`capability-matrix-v2.md:20` 与新证据矛盾、`04-permission-security.md:36-37` 重复行 | V3 **不修改** v2 文档（保留证据链），但**不复用**这些结论的数字 |
| **客户验证为零** | 无 `docs/customer/notes/`，无一场访谈 | V3 §30 把验证作为**GO 的硬前置**，而非可选项 |

### 4.3 从 V2 继承的不变式（不可降级）

```
Permission Before Intelligence   —— 权限在数据访问层强制，不靠 prompt
间接泄露防护                      —— post-filter 会通过排序/计数侧信道泄露
业务正确性评估                    —— 独立于检索质量评估
领域包隔离                        —— 引擎核心零领域 import
LLM 不可知                        —— 仅 OpenAI 兼容端点，无厂商 SDK
垂直纪律                          —— 不自建队列/微服务/K8s/自研 Runtime
```

---

## 5. Red Team Corrections

来源：`RED_TEAM_REVIEW.md`（v3，2026-09-03；根目录与 `docs/product/` 两份字节相同）。红队总判定为 **"C. 暂缓——先验证 Y"**，是**对过早承诺的否决**，不是对方向的背书。V3 必须以此语气呈现。

### 5.1 五条载重级修正

| # | 修正 | 对 V3 的约束 |
|---|---|---|
| R1 | **信任阶梯不可复制**。"Glean 的真正护城河不是基础设施清单，而是用七年爬完'信任阶梯'所积累的企业理解与信任"；"复制技术栈容易，复制七年的信任位置不可能" | 不得把"技术架构更优"当成 GTM 理由 |
| R2 | **不能以独立 Agent 产品直达企业**。"跨 Silo 的 Agent 必须寄生在已获信任的上下文平台上"；企业只会把"执行"交给已获信任的一方 | V3 必须以**与客户共建**（私有化部署进客户环境）为路径，而非独立 SaaS |
| R3 | **中国信任货币 = 数据主权**。"部署形态一次性消解信任问题"——把"你敢不敢把数据给我"换成"我根本不拿你的数据" | 私有化部署升为**一级设计目标**（§26） |
| R4 | **横向 = 死亡陷阱**。与 Dify/FastGPT/MaxKB/RAGFlow 及大厂方案正面竞争 = 重资金、重工程、长周期 | §33 Explicit Non-Goals 的立法依据 |
| R5 | **Workflow-first, Context-accretes**。卖的不是上下文平台，是"**一个领域工作流**——价值在第一次运行即产生"；窄切片（3–6 个系统、只读+导入）；由软件+AI 持续维护 → 平时是"持续合规上下文"，用时"一键成包" | §16 / §28 / §31 的立法依据 |

### 5.2 必须携带的三项诚实限定

| 项 | 事实 |
|---|---|
| **客户验证为零** | 全部评分、假设、阈值都是**计划**，不是实测结果。V3 不得引用任何阈值作为已验证结论 |
| **护城河假设未验证** | 红队 §三判定"当前 MVP 范围内，护城河假设不成立"；"v0.1 的 A ≈ 4 条规则 + 4 个金标准案例，宣称的三层可防御资产是超前兑付" |
| **杀器级 UNKNOWN** | U-G1（Glean 可得性）虽已解决为"无 Glean"；但 G2（框架-地域匹配）仍开放——原 MVP scope 明确排除 ISO27001，而等保/内控/个保审计才是中国可达市场的主流框架 |

### 5.3 V3 相对红队的立场

红队要求"在 Y 完成前不写一行 MVP 代码"。V3 **部分接受**：

- ✅ 接受：不进入大规模 Coding；V0 范围压到 2–4 周；客户验证作为 GO 硬前置。
- ⚠️ 调整：红队写于 2026-09-03，其"Y 验证"针对的是**当时的 C1 审计证据产品方向**。V3 已把产品定义从"某个领域 Agent"上移为"Kernel"，红队的多数具体质疑（如"这是 GRC 平台的 feature"）**不再直接命中**——但**结构性质疑仍然有效**（护城河薄、客户验证缺、地域框架错配）。V3 §37 Validation Gates 把这些质疑转成可执行闸门。
- ❌ 不接受的推论：红队"暂缓"不等于"停止"；V3 允许在**零客户数据、纯内部**的前提下做 Kernel V0 technical spike（不面向客户交付）。

---

## 6. Product Thesis

> **企业的 AI 能力正在被两层商品化：执行层（怎么可靠跑）与 harness 层（Agent 怎么工作）。当这两层都变成可插拔商品时，唯一不可商品化的是"这家企业在这个业务情境下应该做什么"——而它由业务 Context、领域语义、证据、推理与决策构成。**

因此：

- **产品 = Kernel**（业务判断层），**Reference Application = 证明 Kernel 价值的载体**。
- Kernel 的价值不由"支持多少 Agent / 多少模型 / 多少连接器"衡量，而由**业务结论的正确性与可追溯性**衡量。
- Kernel 的护城河假设是：**领域本体 + 业务规则 + 评估语料 + 客户环境内随使用沉淀的上下文**（红队 §0.7.2 认定的"IP 太薄"的正面解药）。
- **该假设尚未验证**（§5.2），V3 不把它当作既成事实。

---

## 7. Kernel Definition

### 7.1 定义

> **Kernel = 企业业务判断的最小不可省略层。任意一层缺失，Kernel 不再成立。**

### 7.2 准入判据（三层测试，任一层通过即可入选）

1. **业务语义层**？——执行/基础设施层一律排除。
2. **不可外购**？——私有化部署约束、领域纵深、业务正确性评估需求使外包不成立。
3. **V0 闭环必需**？——否则缓建。

### 7.3 自建理由的重心转移（V3 关键修正）

V2 的自建理由是"Glean 未覆盖纵深（C22/C23）"。**该理由是推断且无 URL**。V3 把重心移到三条**与 Glean 无关**的理由：

| 理由 | 是否依赖 Glean 状态 |
|---|---|
| **私有化部署约束**：可达市场要求数据不出域，SaaS Provider 形态不成立 | ❌ 不依赖 |
| **领域纵深**：审计/采购的业务规则与评估语料是领域资产，任何通用平台都不会替客户沉淀 | ❌ 不依赖 |
| **业务正确性评估**：结论对不对，必须由领域评估体系回答 | ❌ 不依赖 |
| （旧理由）Glean 不覆盖 | ⚠️ 依赖，且为推断 |

**效果**：即使 Glean 明天补齐领域能力，Kernel 边界依然成立。这是 V3 相对 V2 最实质的稳健性提升。

---

## 8. What Kernel Is

Kernel 拥有并负责：

| # | 职责 | 一句话 |
|---|---|---|
| 1 | **Context 构造与生命周期** | 把"当前业务情境"变成结构化状态，而非一段 prompt |
| 2 | **Entity / Relationship 归一** | 同一供应商在四个系统里是同一个供应商 |
| 3 | **Domain Ontology** | 这个领域的业务语义（控制项↔证据、评标标准…） |
| 4 | **Knowledge 组织** | 哪些知识对这个业务判断相关 |
| 5 | **Evidence 生产与管理** | 业务结论的依据对象，可追溯 |
| 6 | **Reasoning** | 规则优先的确定性推理 + LLM 轻量理解与叙述 |
| 7 | **Decision** | 产出业务裁决（或"证据不足"） |
| 8 | **Domain Workflow Specification** | 业务上应该怎么完成这件事 |
| 9 | **Agent / Tool / Runtime Selection** | 决定用谁做、用什么工具、跑在哪个运行时 |
| 10 | **Policy** | 业务规则与合规策略 |
| 11 | **Permission Enforcement** | 权限在数据访问层强制 |
| 12 | **Domain Evaluation** | 业务正确性评估 |

**Kernel 的一句话自我描述**：

> **让 Agent 在正确的业务上下文中工作，并让它的每个结论都可授权、有依据、可追溯。**

---

## 9. What Kernel Is Not

```
❌ 不是 China Glean         —— 不做企业搜索平台 / 100+ 连接器 / 通用企业图谱
❌ 不是 Generic RAG        —— 不做"上传文件→问答" / 通用向量库抽象 / 通用 RAG pipeline
❌ 不是 Generic Agent 平台  —— 不做 Agent Builder UI / Prompt 市场 / Skill 市场 / 可视化编排
❌ 不是 Trigger.dev        —— 不做 Queue / Retry / Scheduler / Durable Execution / Worker Runtime
❌ 不是 DSH                —— 不做 Agent Loop / 通用 tool runtime / 通用 session runtime / 通用 sandbox / 通用 subagent runtime
❌ 不是完整 Connector 平台  —— 不做 100+ 企业连接器 / 连接器市场 / 爬取平台
❌ 不是模型层              —— 不训练模型、不绑定厂商、不做模型路由产品
```

**判据**：上述每一项都有成熟实现或在快速商品化。重建 = 铁律 3 违规 + 红队 §0.7.2 死亡陷阱。

---

## 10. Kernel Core Objects

V3 至少定义以下对象。**V0 不要求全部实现**，但必须明确归属阶段。

| 对象 | 说明 | 归属 |
|---|---|---|
| **Context** | 针对当前业务情境的结构化状态与相关信息集合 | **V0** |
| **Entity** | 企业实体（人/组织/供应商/合同/采购申请/项目…） | **V0** |
| **Relation** | 实体间关系（含时态有效性 + provenance + confidence） | **V0** |
| **Ontology** | 领域本体（实体类型、关系类型、业务判据） | **V0** |
| **Knowledge** | 与判断相关的知识片段与来源 | **V0** |
| **Evidence** | 业务证据对象 | **V0** |
| **Reasoning** | 推理过程（规则命中链 + LLM 叙述） | **V0** |
| **Decision** | 业务裁决（含置信度与"证据不足"态） | **V0** |
| **WorkflowSpec** | 业务工作流语义（Domain Workflow Specification） | **V0** |
| **Action** | 建议或执行的业务动作 | **V0**（建议）；执行 V1 |
| **AgentRef** | 被选中的 Agent 及其定义引用（code-first） | **V0** |
| **RuntimeRef** | 被选中的运行时引用 | **V1** |
| **ExecutionRef** | 执行引用（run/trace，指向外部运行时） | **V1** |
| **Policy** | 业务规则与合规策略 | **V0**（最小集） |

**每个对象必须定义**：identifier · lifecycle · relationship · ownership · persistence · version · provenance · permission · auditability。
**V0 只要求其中三项全部齐备**：`identifier` · `provenance` · `permission`。其余按阶段补齐。

---

## 11. Context Model

### 11.1 Context 不是什么

Context ≠ Prompt ≠ Chat history ≠ Vector DB ≠ Memory ≠ RAG result。
**Context 是针对当前 Business Situation 的结构化状态与相关信息集合。**

### 11.2 Context 的构成

```
Context
├── User            谁在问（身份、部门、角色、管理职）
├── Organization    组织与部门树
├── Role            权限角色
├── Task            当前业务任务（intent + spec）
├── Entity          涉及的实体及其归一身份
├── Relationships   实体间关系（含时态）
├── Current State   业务当前状态（合同生效中？政策过期？）
├── Knowledge       相关知识
├── Evidence        已有证据
├── Business Rules  适用规则
├── Workflow State  工作流所处阶段
├── Permissions     可访问边界
├── History         相关历史决策
└── Decision Context 决策情境（谁最终负责）
```

### 11.3 Context Lifecycle

```
Create → Enrich → Reason → Plan → Execute → Observe
   → Generate Evidence → Update → Persist
```

**关键**：Evidence 的生成**反馈回 Context**，形成闭环。这与"一次性检索 → 生成"的 RAG 流程有本质区别。

### 11.4 Context 跨 Agent 传递

原则（V3 硬约束）：

```
✅ Agent A → Evidence / State Change → Context → Agent B
❌ Agent A → 巨大 Prompt → Agent B
```

**理由**：后者不可审计——B 的结论依赖一段无法复现的自然语言。前者可审计——B 的结论可回溯到 A 产生的**具名证据对象**。

**但并非所有 Context 都共享**。共享范围由以下维度共同决定：

`Scope` · `Permission` · `Tenant`（V0 单租户）· `User` · `Task` · `Entity` · `Workflow` · `Agent` · `Sensitive Data`

**V0 规则**：共享以 `Task` 为界；跨 Task 共享必须显式声明；敏感数据默认不共享。

---

## 12. Entity / Ontology Model

### 12.1 三者必须分开

| 层 | 内容 | 可迁移性 |
|---|---|---|
| **Entity Model** | 企业有哪些实体类型、如何识别同一实体 | 跨公司基本一致 |
| **Enterprise Graph**（Glean 提供） | 具体企业的实体实例与关系 | 换公司要重连 |
| **Domain Ontology** | **这个领域的业务语义**：控制项需要哪些证据、证据充分性判据、评标标准 | **跨公司可复用**（同领域） |

**v0.1 的错误**是把"实体/关系/上下文"整体划给 Glean，导致 Kernel 失去企业上下文所有权。**V3 的修正**：Entity Model 与 Domain Ontology 都归 Kernel；Glean 只是**企业实体实例与关系的一个可选来源**。

### 12.2 Entity Resolution（跨系统归一）

渐进流水线（沿用 ADR-007）：`exact(source_id)` → `normalized_name` → `alias table` → `rule`（剥离"有限公司/华南"等） → `embedding`（阈值） → `LLM 辅助`（**仅产生 candidate + confidence**）。

**铁律**：LLM 的猜测不得直接成为企业事实。`method='llm'` 的结果一律 `status='pending'`，需规则或人工通道确认。

**实测基线**：ECE v0 的 E1 实体消歧 **98.5%（64/65，≥95% 达标）**（C47）。

### 12.3 Domain Ontology

YAML Context Specification 形态：

```yaml
spec: <name>
version: <n>
root_entity: <type>
requires:            # 该业务任务需要哪些 Context
  entities: [...]    # 实体类型 + 过滤
  relationships: [...] # 关系类型 + 跳数
  documents: [...]   # 文档类型 + 时间窗
  business_data: [...] # 结构化数据
  temporal: {as_of: ...}
limits: {...}
```

**框架不可知**：SOC2 → ISO27001 → 等保 → 内控 → 个保审计的迁移是**内容工作而非架构工作**（ADR-009）。这也直接回应红队 G2（框架-地域错配）——**换框架不需要改引擎**。

---

## 13. Knowledge Model

Kernel 的知识分成三类，处理方式不同：

| 类型 | 例 | 处理 |
|---|---|---|
| **领域知识**（规则性） | "政策证据必须有生效期与审批人" | 进 Ontology + 规则引擎，**确定性** |
| **企业知识**（事实性） | "NimbusWorks 的休假政策 v3.2 生效于 2026-01-01" | 进 Entity/文档库，带 provenance 与时态 |
| **通用知识**（常识性） | 行业惯例 | LLM 自带，**不写入企业事实** |

**边界**：LLM 的内部知识**永远不构成企业事实**。它只能用于理解与叙述，不能用于裁决。

**检索的地位**：4 路召回（Keyword / Vector / Structured / Relationship）是 Knowledge 的**输入机制之一**，不是 Kernel 的核心。融合后统一收口于 Permission Engine 之后。

---

## 14. Evidence Model

### 14.1 为什么 Evidence 是一级对象

V3 指令 Principle 8：Agent 执行产生的不应该只有 `text`，而应该是 `Evidence / Decision / State Change / Execution Reference`。

企业场景真正被追问的是："**这个业务结论是怎么产生的。**"

### 14.2 Evidence 结构

```
Evidence
├── source            来源（系统 + 记录 ID）
├── claim             该证据支持的主张
├── timestamp         证据自身时间 + 抓取时间
├── actor             行为人（人类）
├── agent             产生该证据的 Agent（可为空）
├── runtime           执行引用（ExecutionRef，指向外部运行时）
├── input_context     所用 Context 的引用（可复现）
├── decision          关联的 Decision
└── execution_reference  执行轨迹引用
```

### 14.3 Evidence ≠ Execution Reference（硬边界）

| | Business Evidence | Execution Reference |
|---|---|---|
| 归属 | **Kernel** | 执行运行时 / Agent Harness |
| 回答 | "这个业务结论的依据是什么" | "这段代码跑得怎么样 / Agent 做了什么" |
| 例 | 来源 + 主张 + 时间 + 审批 | run_id / span / 耗时 / 重试 / tool call |
| 生产者 | Kernel | Trigger.dev / DSH / PentAGI |

**二者必须关联，不可互相替代。** Kernel 的 Evidence 带 `execution_reference` 字段指向运行时的轨迹；但运行时的轨迹**不构成**业务证据。

### 14.4 不变式

> **Kernel 产出的每一条业务结论，必须能回答"它是怎么产生的"，且该回答不依赖任何一个特定运行时的存续。**

后半个从句很重要：如果业务证据的完整性依赖 Trigger.dev 的日志保留策略，那它就不是企业证据。

---

## 15. Reasoning / Decision Model

### 15.1 规则优先，LLM 轻量（ADR-010）

```
确定性判断  → 纯代码规则引擎（金额阈值、比价要求、审批链完整性、价格偏离带、证据充分性…）
理解与叙述  → LLM（文档理解、生成解释性文字）
```

**禁止**：让 LLM 做确定性业务裁决。

**理由**（三条同时成立）：

1. **正确性**：审计/采购的合规判断不可依赖"模型感觉"。
2. **可解释**：规则命中链可逐条列出并复核。
3. **中国约束**（红队 §0.8）：规则优先的负载分布**恰好对国产开源模型友好**——不是巧合，应升格为卖点。

### 15.2 Decision 的形态

```
Decision
├── conclusion        业务结论
├── reasoning_summary 推理摘要（引用规则编号）
├── rules_fired       命中的规则清单（可逐条复核）
├── evidence[]        支撑证据
├── risks[]           风险项
├── recommendation    建议动作
├── confidence        置信度
└── status            ok | insufficient_context | need_review
```

**`insufficient_context` 是一等输出**。证据不足时必须明说，**不得猜测**（ECE 评估模型的核心要求）。

### 15.3 人在回路

V0 定位"**建议生成**"而非自动决策（ADR-007 合规红线）。任何写回企业系统的动作（V1+）必须是 `need_review` 态，经人工审批。

---

## 16. Domain Workflow Specification

### 16.1 这是 V3 的新增维度

| | **Domain Workflow Specification** | **Execution Workflow** |
|---|---|---|
| 归属 | **Kernel** | 执行运行时 |
| 表达 | 业务上应该怎么完成这件事 | 计算机实际上怎么执行 |
| 读者 | 业务专家 | 工程师 |
| 变更频率 | 低（业务规则变时） | 高（工程变时） |
| 产物 | 结构化业务步骤 + 判据 + 责任人 | Task 图 + Wait + Retry + Approval 节点 |

### 16.2 示例："审核供应商年度准入"

**Kernel 层（Domain Workflow Specification）**：

```
Supplier
  → 获取供应商历史
  → 检查质量记录
  → 检查合同
  → 检查财务
  → 进行规则判断
  → 生成风险判断
  → 人工确认
  → 更新 Supplier Status
```

**执行层（由 Adapter 映射）**：

```
Task A → Task B → Task C → Wait → Task D → Human Approval → Task E
```

### 16.3 硬约束

> **Kernel 只产出左侧（业务语义）；右侧（执行图）由 Adapter 依据运行时的能力生成。**

**为什么必须分开**：

1. 业务专家看不懂、也不该看懂 task 图；
2. 换运行时不应该改变业务语义；
3. 审计需要的是"业务上应该怎么做"的记录，不是"这次跑成了什么样"的记录。

---

## 17. Agent Selection / Action Planning

Kernel 依据 Context 决定**用谁做**：

| 维度 | 判断依据 |
|---|---|
| **Agent 选择** | 任务类型 + 领域包 + 所需工具 + 该 Agent 的评估记录 |
| **Tool 选择** | 任务需要哪些能力；工具准入由 Kernel 控制（MCP 归一） |
| **Runtime 选择** | 任务特征：需要自主多步探索 → Agent Harness（DSH / PentAGI 类）；需要可靠长跑 → Workflow Runtime（Trigger.dev 类）；两者都不需要 → 进程内薄执行器 |
| **Model 选择** | 任务对确定性的要求；规则优先部分不调模型 |

**Agent 定义必须 code-first**：YAML / 版本化文件，可进 git，可在 Claude Code / Cursor / IDE 中编辑（`research_v2/08-platform-developer.md` 结论：Glean 没把 Agent Builder 限制成封闭低代码平台，我们也不应把所有东西锁在 UI 里）。

**V0 限制**：Runtime 选择表**留空**（V0 只有进程内执行）。Agent 选择只有 1–2 个固定 Agent。**V0 不实现动态选择。**

---

## 18. Execution Runtime Boundary

**参见 `docs/v3/RUNTIME_COMPARISON.md` §2 与 `docs/adr/ADR-011.md`。**

### 18.1 边界

```
Kernel  决定：做什么、为什么做、基于什么 Context 做、应该调用什么能力
Runtime 负责：把这些工作可靠地执行起来
```

### 18.2 Kernel MUST NOT 实现

```
❌ Queue          ❌ Retry Engine      ❌ Scheduler
❌ Durable Execution Engine           ❌ Worker Runtime
❌ Task Execution Engine              ❌ Concurrency Engine
```

### 18.3 接口形态（V3 定，V0 不实现）

Kernel 向执行运行时发出的不是"一个函数调用"，而是**Execution Intent**：

```
ExecutionIntent
├── workflow_spec_ref     Domain Workflow Specification 引用（业务语义）
├── context_ref           本次执行所用的 Context 引用
├── evidence_requirements 期望产出哪些证据
├── permission_scope      执行边界（不可越权）
├── approval_required     是否需要人工审批
└── proposed_steps[]      建议步骤（业务语言，非 task 图）
```

**运行时返回**：`ExecutionResult { status, execution_ref, outputs[], evidence_candidates[] }`

**关键**：`evidence_candidates` 必须回到 Kernel 转为正式 **Evidence**——运行时无权直接写入企业事实。

---

## 19. Agent Runtime Boundary

### 19.1 边界

Agent Runtime / Harness（DSH [C44]、PentAGI [C45]、未来 Glean Harness [C25 UNKNOWN]）负责"**Agent 怎么工作**"：

```
Model / Agent Loop / Tools / Skills / Session / Memory /
Sandbox / MCP / Subagents / Storage / Scheduling / Runtime Environment
```

### 19.2 Kernel MUST NOT 实现

```
❌ Agent Loop              ❌ 通用 tool runtime
❌ 通用 session runtime     ❌ 通用 sandbox
❌ 通用 subagent runtime
```

### 19.3 Kernel 必须提供而 Harness 不提供的

见 `KERNEL_BOUNDARY.md` §8 完整对照表。摘要：

**领域本体 · 企业实体归一 · 数据访问层权限 · 时态上下文 · 业务规则引擎 · 领域评估 · 业务证据 · 业务工作流语义 · 跨 Agent 业务语义共享 · 跨运行时业务连续性**

---

## 20. Provider / Adapter Architecture

### 20.1 三类接口（V3 核心抽象）

```
Kernel
 │
 ├── Provider Interface              （原料：数据与知识）
 │      ├── GleanProvider            [C01–C42]
 │      ├── LocalKnowledgeProvider
 │      ├── EnterpriseDataProvider   （ERP/OA/HRIS 只读）
 │      └── MCPProvider
 │
 ├── Agent Runtime Interface         （执行者：Agent 能力）
 │      ├── DSHAdapter               [C44]
 │      ├── PentAGIAdapter           [C45]
 │      ├── OtherAgentAdapter
 │      └── InProcessAgent（V0 默认）
 │
 └── Execution Runtime Interface     （可靠执行）
        ├── TriggerDevAdapter        [C43]
        ├── InProcessExecutor（V0 默认）
        └── OtherWorkflowRuntimeAdapter
```

### 20.2 硬规则

1. **Kernel 不直接依赖具体 Provider / Runtime**——只依赖接口。
2. **每一类接口在 V0 都必须有一个"最朴素实现"**（本地知识 / 进程内 Agent / 进程内执行器），保证 Kernel 在无任何外部依赖时可独立运行。
3. **接口必须 Provider-neutral**：命名用**业务语义**（`context.search` / `evidence.record` / `workflow.execute`），**禁止**出现 `glean` / `trigger` / `dsh` 等厂商标识。
4. **CI 强制**：领域层与 Kernel 核心的源码中不得出现任何厂商标识符（沿用 `mvp-scope.md` 的 grep 门禁做法，扩展到运行时）。

### 20.3 与 ADR-001 的关系

ADR-001 定义了单一的 **ContextAdapter**（Domain 与上下文后端之间）。V3 **推广**为三类接口。ADR-001 **不被推翻**，是其超集。

---

## 21. Glean Integration

| 项 | 内容 |
|---|---|
| **定位** | Provider 之一（企业搜索 / 连接器 / 权限继承 / Enterprise Graph / Agent 能力） |
| **前提** | 客户已有 Glean 且愿意接入 |
| **不依赖** | Kernel 的任一层不因 Glean 缺席而不成立 |
| **证据** | C01–C42；其中 C03（图谱 schema 可定制性）/ C24（定价）/ C25（Harness）= **STILL_UNKNOWN 且原地封闭**（原定会谈已取消） |
| **表述纪律** | 不得声称"Glean 不做领域层"；只能引用反证式措辞（`KERNEL_BOUNDARY.md` §6） |

**接入方式**：`GleanProvider` 实现 Provider Interface；映射关系沿用 `architecture/context-adapter.md` 的 11 方法表（`search` / `get_entity` / `get_person` / `get_organization` / `get_customer` / `get_project` / `get_metric` / `get_record` / `create_task` / `send_message` / `update_record`）。

**Partner 路径**：Optional。若 Glean 重新接触，可探索 Services & Solutions / Technology / Build 方向；**不得让 V3 依赖 Partner approval**。

---

## 22. DSH Integration

| 项 | 内容 |
|---|---|
| **定位** | Agent Runtime Adapter 之一（Agent Harness） |
| **能力** | Agent Loop / Tools / Skills / Session / Sandbox / Subagents / Storage / Trajectory [C44] |
| **证据级别** | `STRONGLY_INFERRED` + `SECONDARY_ONLY`——**未取得原始仓库逐字核验**，不得用于实现细节设计 |
| **V0** | **不实现**。V0 使用进程内薄 Agent |
| **价值** | 它是"Agent 能力商品化"的实证——越成熟，Kernel 的"判断层"价值越突出 |

**适配器形态（V1 设计，非 V0）**：`DSHAdapter` 实现 Agent Runtime Interface——把 Kernel 的 `ExecutionIntent` 翻译成 DSH 的任务描述，把 DSH 的产出翻译回 `evidence_candidates`。

**关键约束**：DSH 的 session 状态**不得**成为业务 Context 的存储介质。业务 Context 必须存在 Kernel 侧，DSH 只是执行者。

---

## 23. Trigger.dev Integration

| 项 | 内容 |
|---|---|
| **定位** | Execution Runtime Adapter 之一 |
| **能力** | Tasks / Runs / Queues / Retry / Waits & Waitpoints / Concurrency / Scheduling / Durable Execution / Tracing [C43] |
| **证据级别** | `CONFIRMED`（多官方面交叉），但 `TOOL_BLOCKED`（原文抓取被工具限制拒绝） |
| **V0** | **不实现**。V0 使用进程内薄执行器 |
| **待验证** | 自托管的资源要求与依赖——**决定"私有化优先"约束下是否可行**（P0 待补证据） |

**为什么这一条需要 ADR**：引入 Trigger.dev 是引入一项**新的横向基础设施依赖**。按 `ece/CLAUDE.md` §3.3，必须停下写 ADR。→ `docs/adr/ADR-011.md`。

**关键**：ADR-011 决策的是**接口**，不是**选型**。V0 用进程内执行器，V1 可换 Trigger.dev，Kernel 语义不变。

---

## 24. PentaGI Integration

| 项 | 内容 |
|---|---|
| **定位** | **领域 Agent 应用**（自主渗透测试），可作为 Kernel 调用的 Agent Runtime 之一 |
| **能力** | 多 Agent 监督 + 沙箱化执行 + 模型供应商无关 + Web UI/API + 可观测集成 [C45] |
| **证据级别** | `CONFIRMED`（本机一手核验） |
| **V0** | **不实现** |
| **待验证** | 其 API 表面是否允许外部编排调用（P1 待补证据） |

**作为参照物的价值**：PentAGI 展示了"一个可用的领域 Agent 应用"需要什么（多 Agent + 沙箱 + 工具链 + 可观测）——**这些正是 Kernel 要外包出去的东西**。它同时证明了领域 Agent 应用可以做到很深，从而反衬出 Kernel 的价值主张：**让领域 Agent 应用不必重复解决 Context / 权限 / 证据 / 评估**。

**边界**：不得声称 PentAGI 已经是 Kernel 的运行时适配器；它目前只是一个**候选**。

---

## 25. MCP / API Integration

| 项 | 内容 |
|---|---|
| **定位** | Tool Layer 的事实标准（ADR-004） |
| **Kernel 侧** | ① 原生 MCP **Server**（暴露 Kernel 能力给任意 MCP 客户端）② MCP **Client**（消费外部工具） |
| **权限收口** | **工具准入由 Kernel 控制**，工具执行由运行时完成 |
| **证据** | C19 / C37 / C39（Glean 官方运行 MCP server，`claude mcp add` 一行接入） |

**V0 工具最小集**：`search` / `get_record` / `create_task` / `send_message`（沿用 ADR-004）。
**写回**：V0 强制关闭（env kill-switch + 路由硬编码双保险）。

---

## 26. Private Deployment

### 26.1 一级设计目标（不是部署选项）

**理由**（红队 v3 §0.6）：中国市场的信任货币是**数据主权**。企业客户的真实障碍不是预算，而是：

`信息壁垒` · `部门孤岛` · `安全` · `数据治理` · `内部上下文` · `权限` · `企业信息边界`

### 26.2 架构要求

```
Customer Environment
        │
        ├── Kernel              （必需，且必须可独立运行）
        ├── Local Knowledge     （必需，V0 用本地 mock/文件）
        ├── Local Model         （必需，V0 用 OpenAI 兼容本地端点）
        ├── Enterprise API      （可选）
        ├── MCP                 （可选）
        └── Optional External Provider （可选：Glean 等）
```

**硬性验收项（V0 必须满足）**：

1. **完全离线可运行**：模型与数据均在企业环境内，无外网依赖。
2. **单容器 / 内网部署**：不依赖任何 SaaS 控制面。
3. **数据不外传**：不采集、不上传；审计日志本地留存。
4. **模型可替换**：通过 OpenAI 兼容端点，可在无任何厂商 SDK 的前提下切换模型。

**现状**：ECE v0 的 `docker-compose.yml` 已满足 (1)(2) 的形态（api + postgres 两容器，本地端口映射）；(3)(4) **尚无验收测试**（红队 §0.8 标注为待补）。

---

## 27. Open-source Model Strategy

| 项 | 内容 |
|---|---|
| **原则** | LLM 不可知（铁律 5）：仅通过 OpenAI 兼容端点，禁止任何厂商 SDK 依赖或模型名硬编码 |
| **目标模型** | DeepSeek / Qwen / GLM 等国产开源模型，经 vLLM 或 Ollama 本地部署 |
| **架构优势** | **规则优先** 的负载分布恰好对国产开源模型友好（红队 §0.8），应升格为卖点 |
| **未完成的验证** | 红队 §0.7 Step 0.7 要求：用国产开源模型在真实任务上实测，与前沿闭源模型对照。**尚未执行** |
| **风险** | 国产模型文档理解/长文本已够用，但复杂推理弱于前沿闭源（红队 §0.9） |

**判定标准**（红队原定）：若开源模型质量显著掉档（错误率翻倍以上）→ 升级为架构风险；否则确认"规则优先 + 开源模型"组合成立。

**V3 立场**：这是**GO 的硬前置之一**（§37），不得推迟到 POC 之后。

---

## 28. Reference Application Strategy

### 28.1 定义

> **Reference Application = 证明 Kernel 价值的业务载体。它不是产品定义，不是产品线，也不是市场裁决。**

V2 已确立此语义（`product_v2/reference-applications.md`：三个样本仅作 Kernel 验证）。V3 继承并强化。

### 28.2 V3 的候选池（不预设最终 vertical）

| 候选 | 来源 | Kernel 负载 | 状态 |
|---|---|---|---|
| **审计证据准备**（EvidenceIQ） | v1 C1 / V2 App 1 | K4/K5/K6 核心 | 保留为候选 |
| **采购评估**（Procurement Agent） | ECE v0 领域包 / V2 App 2 | K5 核心 | 保留为候选（**已有可运行实现**） |
| **HR Q&A** | v1 C10 / V2 App 3 | 全轻 | 保留为候选 |
| **知识管理**（泸州老窖连接） | 用户资产 | 待定义 | 保留为候选 |
| **合规问卷 / TPRM** | v1 C9 | 中 | 保留（C1 扩展） |
| **Video Factory** | 用户项目 | 内容生产 | 见 §29（technical spike，非产品） |

**V3 明确不宣布最终 vertical**。红队的关键结论：**不应在没有客户验证之前把其中一个宣布为最终产品**。

### 28.3 选择判据（客户验证前）

一个候选要成为第一参考应用，必须同时满足：

1. Kernel 的 K1（权限）+ K4/K5/K6（领域三件套）在其上**有实质负载**；
2. 创始人人脉**直接可达**（2–4 周内能约到访谈）；
3. 痛点**周期性且刚性**（不是一次性）；
4. 已有**可运行的窄切片**（不要求从零开始）。

按此，**采购评估**目前满足度最高（已有 ECE v0 实现 + 可运行评测套件），**审计证据**在"痛点深度"上最强但需要从零构建。二者都不是最终答案。

---

## 29. Video Factory as Technical Validation

**定位**：**Technical Spike，不是产品**。

用户陈述 [C46]：Video Factory 使用 Trigger.dev 做编排。若成立，它可作为 Kernel 架构的**真实验证场**：

```
User Goal → Brand Context → Product Context → Content Context
  → Audience Context → Creative Reasoning → Production Plan
  → Agent / Model Selection → Trigger.dev
  → LLM / TTS / Image / Video → Quality Evaluation
  → Evidence → Context Update
```

其中：

- **Trigger.dev**：负责可靠执行；
- **Kernel**：负责理解内容生产业务上下文、生成 Production Plan、选择 Agent/Model/Workflow、管理结果产生的业务 Evidence。

**限制**：

1. C46 证据级别为 `USER_STATED`——本机未找到 Video Factory 仓库，**不得当作既成事实**；
2. **不得**因此把 Video Factory 变成 Kernel 的最终产品；
3. 它是 V0 之后的 spike 候选，**不在 V0 范围内**。

---

## 30. Customer Validation Strategy

### 30.1 现状（诚实声明）

**客户验证为零。** 无 `docs/customer/notes/`，无一场访谈，无一份脱敏数据。全部评分、阈值、假设都是**计划**。

### 30.2 验证链条

```
Customer Problem Discovery
   → Candidate Workflow
   → Context Requirements
   → Kernel Fit
   → POC
   → Evidence
   → Vertical Selection
```

### 30.3 必做的三步（沿用红队 v3，但重排顺序）

| 步骤 | 内容 | 门槛 |
|---|---|---|
| **Step 0** | 48 小时 Customer Access 冒烟：列 ≥10 位画像内联系人，发一句话邀请 | ≥5 人应约 → CA 假设存活；**<5 → 触发 Kill Criterion #1** |
| **Step 0.6** | **中国三问**（问所有合规/审计/法务受访者，先问不看 Demo）：① 监管真实性（等保/内控/个保审计是否在做）② 模型部署形态 ③ 私有化决策链 | 验证"私有化 + 开源模型"约束 |
| **Step 0.7** | 国产开源模型技术实测 | 见 §27 |

**访谈纪律**（红队 §0.8/§309）：**前 3–5 场不看 Demo、纯问题访谈**。原 `interview-guide.md` 的"先 Demo 后访谈"顺序会锚定受访者、污染痛点数据，**执行时必须改变顺序**。

### 30.4 度量与门（沿用 `customer/validation-metrics.md`，标注为未验证）

```
Score = 0.3×Severity + 0.2×Pilot意愿 + 0.2×Data可得 + 0.15×Cost + 0.15×Pay信号
≥ 3.5   → POC 推进
2.5–3.5 → 补访谈（累计 ≥8 场）再判
< 2.5   → 回到候选表启动下一个候选
```

**POC 触发（四项全需）**：① ≥2 家确认相同痛点（Severity≥4）② ≥1 家愿提供脱敏真实数据 ③ 客户配 1 技术 + 1 业务对口人 ④ 共同定义成功指标。

**⚠️ 以上全部为计划值，未经任何实测。**

---

## 31. MVP Definition

### 31.1 MVP 的判定

> **能在 10–15 分钟内向潜在客户完整演示的一个真实业务场景，且该场景的结论具备可追溯依据，并能展示"切用户即数据隔离"的权限行为。**

### 31.2 MVP 不是

- 不是"这是我们的 Enterprise AI Platform"的平台演示；
- 不是 Agent 数量 / 模型数量 / 连接器数量的展示；
- 不是 UI 演示。

### 31.3 MVP 必须证明的三件事（沿用 V2 STOP Gate Q10）

1. **Permission Before Intelligence**——切用户重问，数据隔离可见；
2. **Domain Reasoning**——规则优先 vs 纯 LLM 的对照；
3. **Domain Evaluation**——ECE 优于纯 RAG baseline。

**V3 追加第四件**（V3 新增维度）：

4. **Evidence 可追溯**——每条结论可回答"是怎么产生的"，且该回答不依赖任何外部运行时的存续。

### 31.4 MVP 的形态

MVP **不是** Kernel 的完整实现，而是**一条 Kernel 闭环在窄切片上跑通**：

```
User Goal → Create Context → Resolve Entities → Retrieve Knowledge/Evidence
  → Reason → Create Decision → Create Domain Workflow
  → Select Agent/Tool/Runtime → Execute → Collect Result
  → Create Evidence → Update Context → Return Business Outcome
```

---

## 32. V0 Scope

### 32.1 规模约束

> **如果只有 2–4 周工程能力，Kernel 最小可运行版本是什么？**

### 32.2 V0 必须包含

| # | 内容 | 来源 |
|---|---|---|
| 1 | **Context Object**（结构化 + 生命周期） | 已有（ECE `context/`） |
| 2 | **Entity Object**（+ 跨系统归一） | 已有（ECE `entities/`） |
| 3 | **Evidence Object**（新） | **V0 新增** |
| 4 | **Domain Workflow Specification**（新） | **V0 新增**（YAML，最小形态） |
| 5 | **Agent / Tool Selection**（固定 1–2 Agent，无动态选择） | 部分已有 |
| 6 | **Provider Adapter**（最小：本地知识 + 进程内） | 部分已有 |
| 7 | **Execution Adapter**（最朴素：进程内执行器） | **V0 新增**（极薄） |
| 8 | **Context Update**（Evidence 回写 Context 的闭环） | **V0 新增** |
| 9 | **Basic Trace**（本地 `context_requests` + Evidence 链） | 已有 |
| 10 | **Permission Engine**（数据访问层强制，硬门） | 已有，✅ **实测已通过**（E2 61/61，2026-09-20） |

### 32.3 V0 明确不含

```
❌ 100 Connectors      ❌ Agent Builder      ❌ Enterprise Search
❌ Vector DB Platform  ❌ Workflow Designer  ❌ Multi-tenant SaaS
❌ Trigger.dev 集成    ❌ DSH 集成           ❌ PentAGI 集成
❌ 动态 Runtime 选择    ❌ 写回企业系统        ❌ 跨 Agent 运行时协作
❌ UI（除最小演示台）    ❌ 多框架切换          ❌ 计费/Admin Console
```

### 32.4 V0 的验收（GO 条件见 §37）

| 项 | 门槛 |
|---|---|
| Permission | **Unauthorized Exposure = 0**（硬门，一票否决） |
| Entity Resolution | E1 ≥ 95% |
| Context Completeness | E3 ≥ 90% |
| 业务正确性 | E2/E4/E5/E6 达标 + 纯 RAG baseline 对照 |
| Provenance | 100%（每条结论可追溯） |
| 私有化 | 离线 + 本地模型跑通 |
| Provider-neutral | CI 断言领域层零厂商标识 |

---

## 33. Explicit Non-Goals

见 `KERNEL_BOUNDARY.md` §7 完整清单。V3 立法禁止：

```
不是 China Glean / 不是 Generic RAG / 不是 Generic Agent Platform
不是 Trigger.dev / 不是 DSH / 不是完整 Connector Platform / 不是模型层
```

**追加立法（V3 特有）**：

```
❌ 不把 Kernel 做成"更大的 Agent"
❌ 不把 Kernel 做成"更大的 Trigger.dev"
❌ 不把 Kernel 做成"中国版 Glean"
❌ 不在缺乏客户验证前宣布最终 vertical
❌ 不实现任何执行/基础设施层能力（即使"顺手"）
```

---

## 34. Build / Buy / Integrate

**原则**：不要机械接受下表；按实际架构判断。能力无法确认时标 `UNKNOWN`。

| Capability | Build | Buy / Use | Integrate | 判据 |
|---|---|---|---|---|
| **Permission Enforcement** | ✅ | | | 铁律 P2；不可外购（可达市场无 Glean） |
| **Context Model / Assembly** | ✅ | | | 核心架构；私有化约束 |
| **Entity Resolution** | ✅ | | | 跨系统归一；领域纵深 |
| **Domain Ontology** | ✅ | | | 领域资产；跨公司可复用 |
| **Business Reasoning** | ✅ | | | 规则优先；正确性 |
| **Domain Evaluation** | ✅ | | | 业务正确性；反证式空白 |
| **Evidence Model** | ✅ | | | 企业可追溯性；V3 新增 |
| **Domain Workflow Spec** | ✅ | | | 业务语义层；V3 新增 |
| **Agent Selection** | ✅ | | | 判断层 |
| **Query Planner**（4 路召回） | ✅ | | | 私有化；不借横向搜索 |
| **MCP Tool Layer** | ✅ | | ✅ | 事实标准；双向互操作 |
| **Data Store**（Postgres+pgvector） | ✅ | | | 单库承担，私有化友好 |
| **Queue / Retry** | | Trigger.dev 类 | ✅ | 厂商无关接口；V0 进程内 |
| **Durable Execution** | | Trigger.dev 类 | ✅ | 同上 |
| **Agent Runtime / Harness** | | DSH / PentAGI 类 | ✅ | 可替换；V0 进程内 |
| **LLM** | | 国产开源 / API | ✅ | OpenAI 兼容；不绑厂商 |
| **Enterprise Search** | | | ✅（Glean）或不接 | 明确不做横向 |
| **Connector 生态** | 仅框架 + 3 mock | | ✅（Glean 275+） | 绝不自建 275+ |
| **Enterprise API** | | 客户系统 | ✅ | 只读优先 |
| **Enterprise Graph（实例）** | | | ✅（Glean） | C03 UNKNOWN，不作前提 |

**分布**（V3）：Build **12** · Buy/Use **4** · Integrate **6**。

**与 V2 的差异**：V3 新增 Build 项 `Evidence Model` / `Domain Workflow Spec`；新增 Integrate 项 `Queue/Retry` / `Durable Execution` / `Agent Runtime`（V2 时这些尚未进入对照系）。

---

## 35. Technical Risks

| # | 风险 | 严重度 | 缓解 |
|---|---|---|---|
| T1 | **执行运行时接口设计过早**——过早抽象出一个错误的接口，比不抽象更贵 | 高 | ADR-011 只定**类别级**接口；V0 用进程内实现验证接口形状 |
| T2 | **国产开源模型质量不达标**（复杂推理弱） | 高 | §27 Step 0.7 实测；规则优先降低模型依赖 |
| T3 | **私有化部署约束与外部运行时冲突**——Trigger.dev 自托管可能有资源/依赖门槛 | 中 | P0 待补证据；V0 不依赖它 |
| T4 | ~~**权限硬门未通过**~~ **已解除（2026-09-20）** —— 曾实测 E2 = 5 暴露 + 5 失败（C47，*historical*）；现为 **61/61** | ~~高~~ 已关闭 | 修复见 ece `037260b`（六根因）+ `32a0b92`（单变量实验）。**注**：E3/E4/E5 runner 仍崩（R40R2.7），属 T4 的剩余部分 |
| T5 | **评测状态被自身测试破坏**——seed 注入的属性被 pytest 洗掉（C48） | 中 | 把不变式放入 `seed_from_demo_json` 自愈；状态完整性测试 |
| T6 | **对照系证据薄弱**——C43/C44 抓取受工具限制，C44 仅二手来源 | 中 | 边界为类别级，实现细节待补；不得用于容量规划 |
| T7 | **领域包隔离被侵蚀**——外部运行时/Provider 的厂商标识渗透进 Kernel | 中 | CI grep 门禁（扩展到 runtimes/providers） |
| T8 | **Evidence 依赖外部运行时存续**——业务证据完整性绑定在第三方日志保留策略上 | 中 | Evidence 必须自持；`execution_reference` 仅作引用不作依赖 |

---

## 36. Product Risks

| # | 风险 | 严重度 | 来源 |
|---|---|---|---|
| P1 | **护城河假设未验证**——红队判定"当前范围内护城河假设不成立"，"三层可防御资产是超前兑付" | **高** | 红队 §三 |
| P2 | **零客户验证**——所有假设无一手证据（红队：10 问中 6 问高风险、0 问有一手证据） | **高** | 红队 §一 |
| P3 | **框架-地域错配**（G2 未解决）——可达市场主流是等保/内控/个保审计，而原 MVP scope 明确排除 ISO27001 | **高** | 红队 §六 |
| P4 | **是现有 GRC 平台的一个 feature**——Hyperproof/AuditBoard/Vanta 都在射程内 | 高 | 红队 §八 |
| P5 | **红海侧翼**——企业知识库/RAG 私有化赛道在中国极度拥挤 | 高 | 红队 §0.9 |
| P6 | **solo founder 产能是硬约束** | 中 | 红队 §0.9 |
| P7 | **"持续维护"是留存故事而非首单卖点**——Demo 与首谈中不可本末倒置 | 中 | 红队 §0.9 |
| P8 | **定位漂移**——Kernel 概念太抽象，容易被做成"又一个平台" | 中 | 本文件 §33 |

**P8 的特别说明**：V3 把产品定义为 Kernel，抽象层级比 V2 更高，**定位漂移风险也随之升高**。缓解措施：① §33 立法清单；② §37 GO 条件要求"已选定一个 Reference Workflow"；③ 任何"平台化"倾向必须先在真实客户场景中验证。

---

## 37. Validation Gates

### 37.1 STOP / GO 判据（V3 指令 §39）

**GO（全部满足才进入 Technical Spike）**：

```
☐ Architecture Boundary = Clear        （本 V3 文档集已给出，待人工审阅）
☐ Core Objects = Defined               （§10，V0/V1/Future 已分阶段）
☐ V0 Scope = Small                     （§32，2–4 周）
☐ Runtime Interfaces = Defined          （§20，类别级）
☐ Reference Workflow = Selected         ← ❌ 未完成
☐ Customer Validation Path = Defined    （§30，但未执行）
```

**STOP（任一成立则不进入 Coding）**：

```
✗ Kernel boundary 不清楚
✗ Kernel 与 DSH 重叠
✗ Kernel 与 Trigger.dev 重叠
✗ Kernel 与 Glean 重叠
✗ V0 范围过大
✗ Product thesis 不成立
```

### 37.2 三个硬前置（V3 追加）

| # | 硬前置 | 现状 |
|---|---|---|
| **G-A** | **客户验证至少跑完 Step 0（48h CA 冒烟）+ Step 0.6（中国三问）** | ❌ 未执行 |
| **G-B** | **国产开源模型实测（§27 Step 0.7）** | ❌ 未执行 |
| **G-C** | **Permission 硬门 E2 = 0 暴露** | ✅ **已通过**（61/61，2026-09-20） |

**G-C 的说明**：这是**唯一一个纯技术、可立即推进**的前置（不依赖客户）。已有明确根因清单与修复单。V3 建议优先推进 G-C。

### 37.3 Kill Criteria

沿用红队 §八：48h CA <5 人应约 / ≥3 场证据准备 <1 人周 / ≥3 场已用 GRC 平台且满意 / 0 场愿 POC / 框架-地域错配 / 垂直场景无本土第一推动力 —— **任一触发则重新选题**。

---

## 38. Implementation Boundary

### 38.1 现有实现资产（ECE v0 / Track B）

ECE v0 是 Kernel 的**参考实现**。当前实测状态（全部由 CC 亲跑并归档，raw stdout 见归档目录）：

| 项 | 实测 | 判定 |
|---|---|---|
| 基线测试 | **353 passed / 3 skipped / 0 failed**（本地，live API）<br>*历史*：CI 签名 349P/5S/3D（CI 无 live API，两个 E2 wrapper 会 skip） | ✅ exit 0 |
| **E1 实体消歧** | **98.5%**（64/65） | ✅ 达标（≥95%） |
| **E2 权限套件** | **0 暴露 + 0 失败（61/61）** | ✅ **硬门已通过** |
| **E3 Context 完整性** | **runner 裸崩**（`ContextPackage.get`） | ❌ 未跑通（R40R2.7） |
| **E4 Relationships** | **runner 裸崩**（同上） | ❌ 未跑通（R40R2.7） |
| **E5 Temporal** | **0.0%**（`str.isoformat`） | ❌ 未跑通（R40R2.7） |
| E6 Agent | 未跑（需 LLM） | ⏸ |

> *历史*：E2 曾为 5 暴露 + 5 失败、E1 曾因测试污染降至 95.4% —— 两者均已于 2026-09-20 修复
> （ece `037260b` / `93ed0e3`）。历史原始 stdout 保留于归档的 `baseline-seeded/` 与
> `single-variable-v2/`（后者已 `superseded` 前者）。

**归档**：`ece/reports/eval-archive/2026-09-20-cut040R2/`

### 38.2 诚实结论

> **Kernel 的架构已在 ECE v0 中成型，核心不变式（Permission Before Intelligence）已实测通过（E2 61/61）。
> 但领域评测套件 E3/E4/E5 的 runner 仍然崩，尚未跑通 —— Context 闭环的实测数字目前缺失。**

**因此 V3 不得声称**：

```
❌ "Kernel 已实现"
❌ "领域评估体系已建立"（E3/E4/E5 尚未跑通）
```

**可以声称**：

```
✅ Kernel 的分层与接口已在参考实现中成型
✅ Permission 的强制点在架构上已固化（数据访问层 SQL 子查询），且已实测通过（E2 = 0/0）
✅ Permission Before Intelligence 在实现层已达成（61/61）
✅ 评测套件的框架与数据集已就位（E1–E6）
✅ E1 已达标（98.5%）；E3/E4/E5 待修 runner（R40R2.7）
```

### 38.3 与 Track B 的关系

- Track B（`ece/` 仓）继续独立推进，**不受本 PRD 阻塞**。
- 本 PRD 对 Track B 的**新增要求**：§10 的 `Evidence` / `WorkflowSpec` 两个 V0 新增对象；§20 的三类接口抽象。
- **本阶段不写生产代码**（V3 指令 §19/§40）。上述要求以**任务条目**形式提出，待 V3 审阅通过后由 Track B 承接。

---

## 39. Phase Plan

```
Phase V3-0  本 PRD 交付（当前）
   ↓
Phase V3-1  人工审阅 PRD_V3 + KERNEL_BOUNDARY + RUNTIME_COMPARISON
   ↓        ← STOP 点。审阅不过则回到 V3-0
Phase V3-2  三硬前置（G-A 客户验证 / G-B 国产模型实测 / G-C 权限硬门）
   ↓        ← 可并行；G-C 可立即启动
Phase V3-3  Technical Spike（窄切片闭环，进程内运行时）
   ↓
Phase V3-4  Kernel V0
   ↓
Phase V3-5  Reference Application
   ↓
Phase V3-6  Customer Validation → Vertical Selection
   ↓
Phase V3-7  Runtime Adapter（Trigger.dev / DSH / PentAGI 按需接入）
```

**节奏约束**：

- V3-0 到 V3-1 之间**不写代码**（V3 指令 §40）；
- V3-2 的三项硬前置**可以并行**，但 **G-B 与 G-A 必须有结果**才进 V3-3；
- V3-3 的运行时**必须是最朴素的进程内实现**——不得在 spike 阶段引入 Trigger.dev/DSH（否则会在验证 Kernel 之前先验证集成）。

---

## 40. Open Questions

| # | 问题 | 影响 | 谁能回答 |
|---|---|---|---|
| Q1 | 第一个 Reference Workflow 选哪个？（审计证据 / 采购评估 / 其他） | GO 条件之一 | 客户验证 |
| Q2 | 可达市场的第一推动力是什么？（监管强制 vs 内部频率） | Kill Criterion #6 | 中国三问 |
| Q3 | 国产开源模型在核心任务上是否达标？ | 架构风险 | Step 0.7 实测 |
| Q4 | Trigger.dev 自托管在客户内网是否可行？ | 运行时选型 | 待补证据 P0 |
| Q5 | DSH 是否允许自定义 context provider（Kernel 注入点）？ | 适配器形态 | 待补证据 P1 |
| Q6 | PentAGI 的 API 是否可被外部编排调用？ | 适配器可行性 | 待补证据 P1 |
| Q7 | Evidence 对象的持久化与保留策略如何与客户合规要求对齐？ | 企业交付 | 客户访谈 |
| Q8 | "持续维护上下文" 的商业模式如何定价？ | 商业模型 | 客户访谈 |
| Q9 | Kernel 是否需要多租户（V1 之后）？ | 架构 | 待定（当前明确不做） |
| Q10 | 若 Glean 补齐领域能力，Kernel 边界是否需要调整？ | 战略 | 已缓解（§7.3：自建理由不依赖 Glean 状态） |

---

## 附录 A — V3 必须回答的 10 个问题

| # | 问题 | 答案位置 | 一句话答案 |
|---|---|---|---|
| Q1 | Kernel 到底是什么？ | §7 | 企业业务判断的最小不可省略层 |
| Q2 | Kernel 为什么存在？ | §2 / §6 | 执行与 harness 两层商品化后，唯一不可商品化的是"应该做什么" |
| Q3 | Kernel 与 Glean 的边界？ | §21 / `KERNEL_BOUNDARY.md` | Glean = Provider；Kernel = 判断层 |
| Q4 | Kernel 与 Trigger.dev 的边界？ | §23 | Trigger.dev 执行；Kernel 决定 |
| Q5 | Kernel 与 DSH 的边界？ | §22 | DSH 让 Agent 能干活；Kernel 让 Agent 干对的事 |
| Q6 | Kernel 与 PentAGI 的边界？ | §24 | PentAGI = 领域 Agent 应用；Kernel 是它可调用的判断层 |
| Q7 | Kernel 的核心 IP？ | §6 | 领域本体 + 业务规则 + 评估语料 + 客户环境内沉淀的上下文 |
| Q8 | Kernel V0 最小实现？ | §32 | Context/Entity/Evidence/WorkflowSpec/Provider/Execution Adapter/Context Update/Trace |
| Q9 | 第一批 Reference Application 怎么验证？ | §28 / §30 | 客户验证选 vertical；三硬前置 + POC 四条件 |
| Q10 | **如果没有 Glean，Kernel 是否仍然成立？** | §7.3 | **YES**（自建理由不依赖 Glean 状态） |

---

## 附录 B — 自检：拿掉测试

| 拿掉 | Kernel 是否成立 | 依据 |
|---|---|---|
| Trigger.dev | ✅ | §18 / §20：Adapter 层 |
| DSH | ✅ | §19 / §20：Adapter 层 |
| PentAGI | ✅ | §24：可选 capability |
| Glean | ✅ | §21 + §7.3 |
| 所有具体 LLM | ✅ 架构 / ⚠️ 质量待验 | §27 |

**结论**：五项架构测试全部通过。第 5 项的**质量**部分未经验证，已列为硬前置 G-B。

---

## 附录 C — 最终判断标准

> **我们是否真的找到了一个不依赖某个特定 Agent、Workflow Runtime、LLM、Glean 或 Connector 的核心产品价值？**

**V3 的答案**：

```
Enterprise Business Context
      + Domain Semantics
      + Reasoning
      + Decision
      + Business Workflow
      + Evidence
      + Agent / Runtime Selection
= Domain Intelligence Kernel
```

**但**：这个核心价值的**商业成立性未经任何客户验证**（§30 / §5.2）。架构上自洽 ≠ 商业上成立。V3 交付的是**架构边界**，不是**商业验证**。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active — 待人工审阅
**Review Focus**: PRD_V3 + KERNEL_BOUNDARY + RUNTIME_COMPARISON
