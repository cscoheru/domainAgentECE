# ARCHITECTURE_DECISION_V3.md — 架构决策记录

> Version: 1.0
> Date: 2026-09-20
> Status: **Active**
> 关联: `docs/v3/PRD_V3.md` · `docs/v3/KERNEL_ARCHITECTURE_V3.md` · `docs/v3/KERNEL_BOUNDARY.md` · `docs/adr/ADR-011.md`
> 上游: `RESEARCH_PRD_V2.md`（V2 架构决策）· `docs/architecture_v2/build-buy-integrate-partner-matrix.md` · `docs/adr/ADR-001` … `ADR-010`

---

## 0. 本文件的性质

这是一份**决策记录**，不是描述文档。它回答：

1. V3 相对 V2 做了哪些**架构性决策**？
2. 每条决策的**依据**与**被否决的备选**是什么？
3. 哪些 V2 决策被**继承**、哪些被**扩展**、哪些被**推翻**？

---

## 1. 决策总览

| # | 决策 | 类型 | 状态 |
|---|---|---|---|
| AD-V3-1 | Kernel 定位于执行运行时与 Agent Harness **之上** | 边界 | **新增** |
| AD-V3-2 | Kernel 边界对照系从「Glean 单一」扩展为「Provider + Runtime 类别」 | 边界 | **新增** |
| AD-V3-3 | **Evidence** 提升为一级业务对象 | 数据模型 | **新增** |
| AD-V3-4 | **Domain Workflow Specification** 与 **Execution Workflow** 分层 | 语义 | **新增** |
| AD-V3-5 | Adapter 从单一 ContextAdapter 推广为三类接口 | 抽象 | **扩展 ADR-001**〔V0 义务 SUPERSEDED → V1+〕 |
| AD-V3-6 | Kernel 自建理由重心从「Glean 空白」移到「私有化 + 领域纵深 + 业务正确性」 | 战略 | **修正** |
| AD-V3-7 | 私有化部署升为一级设计目标 | 部署 | **升格** |
| AD-V3-8 | 不预设最终 vertical；Reference Application ≠ 产品定义 | 产品 | **继承并强化** |
| AD-V3-9 | V0 运行时必须是最朴素的进程内实现 | 运行时 | **新增** |
| AD-V3-10 | 引入执行/Agent 运行时依赖须写 ADR | 治理 | **新增**（→ ADR-011） |

**被推翻的 V2 决策**：**无**。V3 全部为新增或扩展，V2 的 K1–K8 + D1 与 ADR-001…010 全部**保持有效**。

**被推翻的 v0.1 决策**（作废文件）：**1 条** —— "Glean 拥有 Context/Search/Permissions/Connectors" 的边界划分（见 §3.1）。

---

## 2. 核心决策详述

### AD-V3-1 — Kernel 位于执行运行时与 Agent Harness 之上

**决策**：Kernel 的定位是**业务智能层**。它不实现任何执行能力（队列/重试/调度/持久化执行/worker）或 harness 能力（agent loop/session/sandbox/subagent）。

**依据**：

1. 这两类能力已被成熟实现覆盖（Trigger.dev [C43] / DSH [C44] / PentAGI [C45]），且在快速商品化。
2. ECE 铁律 3「垂直纪律」明令禁止自研消息队列 / 自研 Runtime / 微服务。
3. 红队 v3 §0.7.2：横向平台 = 死亡陷阱。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| Kernel 内置薄执行引擎并长期演进 | 会腐蚀定位（团队精力从"业务推理质量"转向"执行稳定性"）；违背铁律 3 |
| Kernel 完全不做执行语义，直接调用函数 | 无法表达"业务上应该怎么做"与"该交给哪个运行时"——失去编排语义层 |
| 把 Kernel 定位成"更强的 DSH" | 与 §9 Non-Goals 直接冲突；DSH 的赛道已被充分竞争 |

**验证方式**：`KERNEL_BOUNDARY.md` §9 的"拿掉测试"——拿掉 Trigger.dev / DSH / PentAGI，Kernel 架构仍成立。

---

### AD-V3-2 — 边界对照系扩展为类别级

**决策**：Kernel 的边界不再相对"某个具体系统"定义，而相对**三类别**定义：

```
执行运行时（Execution Runtime）  — 可靠执行
Agent Harness（Agent Runtime）   — Agent 如何工作
Provider                          — 原料来源
```

**依据**：

1. V2 的 Kernel 定义是"相对 Glean 的最小不可替代集"。这个定义有一个结构性弱点：**一旦 Glean 补齐领域能力，Kernel 的存在理由被削弱**。
2. 类别级定义下，具体系统可替换、可消失、可新增，Kernel 边界不变。
3. 这也是"集成而非重建"原则（Principle 9）的架构前提——只有类别级接口才谈得上"可替换"。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| 沿袭 V2，只与 Glean 对照 | 单点依赖；Glean 策略变化即动摇 Kernel 论证 |
| 为每个已知系统单独定义边界 | 组合爆炸；新增系统须重写边界文档 |
| 不定义边界，靠"不做平台"的自我约束 | 不可检验，不可审计 |

---

### AD-V3-3 — Evidence 提升为一级业务对象

**决策**：`Evidence` 成为 Kernel 的一等对象，与 Context / Entity / Decision 同级；拥有独立 schema、独立生命周期、独立持久化。

**依据**：

1. 企业场景真正被追问的是"**这个业务结论是怎么产生的**"（V3 指令 §32）。
2. 红队 v3 的核心批评之一是"V2 的护城河假设薄弱"——**可追溯性是可以被客户直接感知并验证的价值**，比"更聪明的 Agent"更容易证明。
3. 现有实现（ECE v0）只有工程审计表（`context_requests` / `context_items`），**没有业务证据对象**。这是可识别的缺口。

**关键约束**：Evidence ≠ Execution Reference。前者属 Kernel，后者属运行时。二者关联但不可互相替代（`KERNEL_BOUNDARY.md` §5）。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| 用运行时的 tracing 充当证据 | 业务证据的完整性会绑定在第三方日志保留策略上——企业不可接受 |
| 用 Context 的 `sources[]` 充当证据 | 只记录了"从哪取的"，缺少"支持什么主张、谁批准、关联哪个决策" |
| 用 LLM 生成的自然语言说明充当证据 | 不可复现、不可审计 |

---

### AD-V3-4 — Domain Workflow Specification ≠ Execution Workflow

**决策**：业务工作流语义与执行工作流**分层**。Kernel 只产出前者；后者由 Adapter 依据运行时的能力生成。

**依据**：

1. 两者的读者、变更频率、表达语言完全不同（业务专家 vs 工程师；业务规则变 vs 工程变）。
2. 换运行时不应改变业务语义——如果只有一张图，换运行时必须改业务定义。
3. 审计需要的是"业务上应该怎么做"的记录，不是"这次跑成什么样"的记录。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| 单一工作流图（业务与执行合一） | 换运行时必须重写；业务专家无法参与；审计证据错层 |
| 不做工作流语义，靠 Agent 自由发挥 | 失去可复现性与可审计性；红队 §0.5 明确要求窄而深的工作流 |
| 用 BPMN 等业务流程标准 | V0 过重；且标准面向"流程自动化"而非"业务判断" |

---

### AD-V3-5 — Adapter 三类接口（扩展 ADR-001）〔**V0 义务已 SUPERSEDED**〕

> ⚠️ **SUPERSEDED for V0**（`V3_CLOSEOUT.md` §2.2 / §2.4）：**V0 不建三类接口抽象层。**
> 本决策的**决策方向仍然有效**（三类接口是可替换性设计），但**降为 V1+ 方向**。
> V0 只保留三件**具体实现**：Local Provider / InProcessExecutor / 固定 Agent（直接调用）。
> 下文的"V0 实现"读作 **V1+ 目标**。

**决策**：ADR-001 的单一 `ContextAdapter` 推广为三类接口：Provider Interface / Agent Runtime Interface / Execution Runtime Interface。**（V1+）**

**与 ADR-001 的关系**：**扩展，不推翻**。ADR-001 的 11 个方法全部归入 Provider Interface 的 `context.*`。ADR-001 的 Mock-first 策略、CI 门禁、切换验收测试**全部继续有效**，并逐类复制。

**依据**：ADR-001 已经论证了"抽象 + Mock-first + 可替换"的必要性；V3 只是把它从"上下文后端"这一个维度扩展到"上下文 + Agent + 执行"三个维度。理由完全相同——**避免不可逆锁定**。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| 只保留 ContextAdapter，运行时直接调用 | 运行时若被直接调用，Kernel 与具体运行时耦合；换运行时需改 Kernel 代码 |
| 为一类接口造一个插件框架 | V0 过重；铁律 3 禁止平台化 |

---

### AD-V3-6 — 自建理由重心转移

**决策**：Kernel 各层自建的理由**不再依赖**"Glean 未覆盖"。重心移到三条与 Glean 状态无关的理由：私有化部署约束、领域纵深、业务正确性评估。

**依据**：

1. **C22/C23 是 `STRONGLY_INFERRED` 且无来源 URL**（`EVIDENCE_V3_ADDENDUM.md` §3）。整个"Glean 空白 = 最高 IP"的论题建立在一个没有 URL 的推断上。把它当作自建的主要理由，等于把架构押在一条可能被证伪的论断上。
2. 三条新理由**在 Glean 补齐领域能力的情况下仍然成立**。
3. 这同时缓解了 `platform-kernel-definition.md:146` 自己承认的保守假设（"若 Glean 真做了则我方 IP 价值减损"）。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| 沿用 V2，以"Glean 空白"为主要理由 | 证据薄弱；且是单点论证 |
| 放弃自建，直接买 Glean | 可达市场无 Glean 客户（U-G1 CONFIRMED）；私有化约束下 SaaS 形态不成立 |

**表述纪律（强制）**：任何文档不得写"Glean 没有领域本体/推理/评估能力"，只能引用 `research_v2/07-governance-evaluation.md:57` 的反证式措辞。

---

### AD-V3-7 — 私有化部署升为一级设计目标

**决策**：私有化不是"部署选项之一"，而是**架构前提**。任一 Kernel 必需层若只能跑在 SaaS 上，则产品在可达市场不成立。

**依据**：红队 v3 §0.6/§0.7.3——中国市场的信任货币是**数据主权**；"部署形态一次性消解信任问题"。

**验收项**（V0）：完全离线可运行 / 单容器或内网部署 / 数据不外传 / 模型可替换。

**现状**：ECE v0 的 compose 形态满足前两项；后两项**尚无验收测试**（列为待补）。

---

### AD-V3-8 — 不预设最终 vertical

**决策**：V3 **不宣布**最终 vertical。审计证据 / 采购评估 / KM / HR Q&A / TPRM 全部保留为候选。Reference Application = 证明 Kernel 价值的载体，**不是产品定义**。

**依据**：红队核心结论——"不应在没有客户验证之前把其中一个宣布为最终产品"。

**与 V2 的关系**：V2 已确立"Reference Application ≠ 产品"的语义（三样本仅作 Kernel 验证）；V3 继承并强化为"连 vertical 都不预设"。

**风险**：抽象层级升高 → 定位漂移风险（`PRD_V3.md` §36 P8）。缓解：§33 立法清单 + GO 条件要求"已选定一个 Reference Workflow"。

---

### AD-V3-9 — V0 运行时必须是最朴素的进程内实现

**决策**：V0 的**执行与 Agent 能力**必须是最朴素的**进程内具体实现**（无队列、无重试、无 sandbox、无 agent loop）。
〔V3_CLOSEOUT §2.2 收口：**不抽象为 interface** —— V0 直接使用 Local Provider / InProcessExecutor / 固定 Agent。〕

**依据**：

1. 若 V0 就引入 Trigger.dev / DSH，会**在验证 Kernel 之前先验证集成**——两个变量同时变，无法归因。
2. 进程内实现足以跑通 6 步闭环；V0 要验证的是**闭环成立**，不是接口形状。（接口形状是 V1 的事。）
3. 符合 V0 "2–4 周"的规模约束（Codex：可比 2–4 周更小）。

**被否决的备选**：

| 备选 | 否决理由 |
|---|---|
| V0 直接集成 Trigger.dev 以"更真实" | 变量混淆；且在私有化约束未验证前引入外部依赖 |
| V0 不做执行抽象，直接函数调用 | 之后抽取接口的成本远高于现在定义 |

---

### AD-V3-10 — 引入运行时依赖须写 ADR

**决策**：引入任何执行运行时或 Agent Harness 依赖（Trigger.dev / DSH / PentAGI / 其他）属于**新的横向基础设施依赖**，必须先写 ADR。

**依据**：`ece/CLAUDE.md` §3.3 "是否引入了新的横向依赖？若是，停下写 ADR。" 这是既有治理规则，V3 将其明确适用于运行时类别。

**首次适用**：`docs/adr/ADR-011.md`（Kernel ↔ Runtime boundary）。

---

## 3. 与既有决策的关系全表

### 3.1 与 v0.1 PRD（作废）的关系

| v0.1 的主张 | V3 处置 |
|---|---|
| Glean 拥有 Enterprise Context / Search / Permissions / Connectors / Agent Infra / Governance / Observability | ❌ **推翻**——Kernel 拥有 Context / Entity / Permission 的**强制权**；Glean 降为 Provider |
| 我们拥有 Domain Ontology / Reasoning / Agents / Workflows / Evaluation / KPI / UX | ✅ 保留并扩展（新增 Evidence / Workflow Spec） |
| "没有 Glean，产品仍应有价值" | ✅ 保留（`PRD_V3.md` 附录 B） |
| Strong/Soft Dependency 划分 | ❌ **推翻**——改为"可选 Provider"，无强依赖项 |
| 禁止清单（不做 Agent 平台 / RAG / Connector 平台 / UI-first） | ✅ 全部保留 |

### 3.2 与 V2 决策的关系

| V2 决策 | V3 处置 |
|---|---|
| K1–K8 + D1（`platform-kernel-definition.md`） | ✅ **全部继承**（`KERNEL_ARCHITECTURE_V3.md` §7） |
| "Kernel 自建不可替代，Glean 集成作为可选 Adapter，不替换 Kernel"（`:174`） | ✅ **继承并泛化**为"任意 Provider / 任意 Runtime" |
| 8 个 Build ADR（ADR-003…010） | ✅ **全部保持有效**，不修改 |
| Build/Buy/Integrate/Partner 四向矩阵 | ✅ 继承，新增 3 项 Integrate（Queue/Retry、Durable Execution、Agent Runtime） |
| 3 个 Reference Application（EvidenceIQ / Procurement / HR Q&A） | ✅ 继承为**候选池**，但不预设最终 vertical |
| STOP Gate 十问 | ✅ 已答（V2）；V3 附录 A 以新框架重答 |
| "不做 Agent Builder UI" | ✅ 继承（ADR 一致） |
| Row 13 Platform Observability = Build 简化 + Integrate 完整 | ✅ 继承 |

### 3.3 与 ECE 铁律的关系

| 铁律 | V3 处置 |
|---|---|
| P1 Context First | ✅ 强化（Context 成为核心对象，新增 Lifecycle） |
| P2 Permission Before Intelligence | ✅ **不动摇**（`KERNEL_BOUNDARY.md` 行 1） |
| P3 Enterprise Context ≠ Vector RAG | ✅ 继承 |
| P4 Domain First | ✅ 继承 |
| P5 Platform Independent | ✅ **强化**（从"不绑 Glean/LLM"扩展到"不绑任何 Runtime"） |
| 铁律 3 垂直纪律 | ✅ 强化（§33 Non-Goals + AD-V3-1） |
| 铁律 4 领域包隔离 | ✅ 强化（CI 门禁扩展到 provider/runtime 厂商标识） |
| 铁律 5 LLM 不可知 | ✅ 继承 |

---

## 4. Build / Buy / Integrate 矩阵（V3 版）

**判定规则**（沿用 V2 并扩展）：

- **Build**：业务语义层 + 不可外购（私有化/领域纵深/正确性评估）+ V0 必需
- **Buy / Use**：有成熟第三方且非核心
- **Integrate**：需要该能力但**不应自建**（横向基础设施 / 执行能力）

| Capability | Build | Buy/Use | Integrate | 判据 | 与 V2 的差异 |
|---|---|---|---|---|---|
| Permission Enforcement | ✅ | | | 硬门；不可外购 | 同 |
| Context Model / Assembly | ✅ | | | 核心架构 | 同 |
| Entity Resolution | ✅ | | | 跨系统归一 | 同 |
| Domain Ontology | ✅ | | | 领域资产 | 同 |
| Business Reasoning | ✅ | | | 规则优先 | 同 |
| Domain Evaluation | ✅ | | | 业务正确性 | 同 |
| **Evidence Model** | ✅ | | | 可追溯性 | 🆕 **V3 新增** |
| **Domain Workflow Spec** | ✅ | | | 业务语义层 | 🆕 **V3 新增** |
| Agent Selection | ✅ | | | 判断层 | 🆕 **V3 新增** |
| Query Planner | ✅ | | | 私有化 | 同 |
| MCP Tool Layer | ✅ | | ✅ | 事实标准 | 同 |
| Data Store | ✅ | | | 单库承担 | 同 |
| **Queue / Retry** | | Trigger.dev 类 | ✅ | 厂商无关接口 | 🆕 **V3 新增** |
| **Durable Execution** | | Trigger.dev 类 | ✅ | 同上 | 🆕 **V3 新增** |
| **Agent Runtime / Harness** | | DSH / PentAGI 类 | ✅ | 可替换 | 🆕 **V3 新增** |
| LLM | | 国产开源 / API | ✅ | OpenAI 兼容 | 同 |
| Enterprise Search | | | ✅ 或不接 | 不做横向 | 同 |
| Connector 生态 | 仅框架 + 3 mock | | ✅（Glean） | 不自建 275+ | 同 |
| Enterprise API | | 客户系统 | ✅ | 只读优先 | 同 |
| Enterprise Graph | | | ✅（Glean） | C03 UNKNOWN | 同 |

**分布**：Build **12** · Buy/Use **4** · Integrate **6**。

**V2 → V3 差异**：Build +3（Evidence / Workflow Spec / Agent Selection）；Integrate +3（Queue-Retry / Durable Execution / Agent Runtime）。

---

## 5. 被否决的架构方向（V3 明确不做）

| 方向 | 否决理由 |
|---|---|
| **中国版 Glean** | 横向平台 = 死亡陷阱（红队 §0.7.2）；与 Dify/FastGPT/MaxKB/RAGFlow 正面竞争 |
| **Generic RAG 平台** | 红海；不产生领域 IP |
| **Generic Agent 平台** | 红海；护城河薄；与 §33 冲突 |
| **自研执行引擎** | 铁律 3；且 Trigger.dev 类已成熟 |
| **自研 Agent Harness** | 同上；DSH 类已成熟且插件化 |
| **更聪明的 Agent**（把 Kernel 做成"更大的 Agent"） | 与产品定位冲突；Agent 能力商品化最快 |
| **完整 Connector 平台** | 275+ 连接器的规模优势不可复制，也不需要 |
| **多租户 SaaS** | V0/V1 明确不做；私有化优先 |
| **UI 优先** | 红队：卖工作流，不卖平台；UI 是最低成本项 |

---

## 6. 决策的可检验性

每条决策必须能被检验，否则是空话。

| 决策 | 检验方式 | 检验时机 |
|---|---|---|
| AD-V3-1 Kernel 在执行之上 | `KERNEL_BOUNDARY.md` §9 拿掉测试 | V3 审阅时 |
| AD-V3-2 类别级边界 | 新增任一 Provider/Runtime 不需改边界文档 | 持续 |
| AD-V3-3 Evidence 一级 | V0 存在 `Evidence` 对象且结论可追溯 | V0 验收 |
| AD-V3-4 Workflow 分层 | 存在独立的 Workflow Spec 文件且不含 task 图 | V0 验收 |
| AD-V3-5 三类接口 | ~~V0 三个接口各有进程内实现~~ → **V1+ 方向**（V0 不建抽象层，见 V3_CLOSEOUT §2.2） | V1 验收 |
| AD-V3-6 理由重心 | 文档中无"Glean 没有 X"式断言 | V3 审阅时 |
| AD-V3-7 私有化 | 断网 + 本地模型跑通 | V0 验收（**待补验收项**） |
| AD-V3-8 不预设 vertical | 无任何文档宣布最终 vertical | V3 审阅时 |
| AD-V3-9 V0 进程内 | V0 依赖清单中无外部运行时 | V0 验收 |
| AD-V3-10 运行时须 ADR | `docs/adr/ADR-011.md` 存在 | ✅ 已完成 |

---

## 7. 未决事项

| # | 事项 | 阻塞什么 | 谁决定 |
|---|---|---|---|
| 1 | 第一个 Reference Workflow | GO 条件 | 客户验证 |
| 2 | 是否/何时引入 Trigger.dev | V1 运行时选型 | ADR-011 之后的实测 |
| 3 | Evidence 保留期与合规对齐 | 企业交付 | 客户访谈 |
| 4 | 最终 vertical | 产品方向 | 客户验证 |
| 5 | Kernel 是否需要多租户 | V1+ 架构 | 待定 |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
