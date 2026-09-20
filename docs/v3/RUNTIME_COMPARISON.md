# RUNTIME_COMPARISON.md — Kernel 与执行/上下文系统的对照

> Version: 1.0
> Date: 2026-09-20
> Status: **Active**
> 关联: `docs/v3/KERNEL_BOUNDARY.md` · `docs/v3/PRD_V3.md` · `docs/adr/ADR-011.md`
> 证据: C43（Trigger.dev）· C44（DSH）· C45（PentAGI）· C01–C42（Glean）

---

## 0. 一句话结论

> **Kernel 不应该被实现成 Trigger.dev / DSH / PentaGI / Glean 的复制品，因为它回答的不是"怎么可靠地跑"、也不是"Agent 怎么工作"、也不是"数据在哪"，而是"这家企业在这个业务情境下，应该做什么决定、依据是什么、谁有权这么做、以及这个结论如何被追溯"。**

前四者都是**能力**（capability），Kernel 是**判断**（judgment）。能力可以购买、集成、替换；判断必须自己拥有，否则产品没有存在理由。

---

## 1. 一张图定位所有参与者

```
                        USER / BUSINESS GOAL
                                │
                                ▼
                 ┌──────────────────────────┐
                 │      DOMAIN KERNEL       │   ← 本项目的产品
                 │  Context / Ontology      │
                 │  Permission / Evidence   │
                 │  Reasoning / Decision    │
                 │  Domain Workflow Spec    │
                 │  Agent & Runtime Select  │
                 └────────────┬─────────────┘
                              │  Execution Intent
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
       Agent Runtime    Workflow Runtime    Providers
              │               │                │
         DSH [C44]      Trigger.dev [C43]    Glean [C01–C42]
         PentAGI [C45]   (或自建薄执行器)      本地知识 / 企业 API / MCP
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                     ENTERPRISE SYSTEMS
                              │
                              ▼
                     RESULT / STATE CHANGE
                              │
                              ▼
                     BUSINESS EVIDENCE  ← 再次进入 Kernel
                              │
                              ▼
                       CONTEXT UPDATE
                              │
                              └──────→ next action
```

**读法**：这张图的关键不是层数，而是 **Kernel 在图上只有一个相邻层**——它的上方是业务目标，下方是执行意图。Kernel **不直接调用企业系统**，也**不直接运行任务**。它把"该做什么"翻译成执行意图，再交给相应的运行时。

---

## 2. Kernel vs Trigger.dev

| 维度 | Kernel | Trigger.dev [C43] |
|---|---|---|
| **解决的问题** | 企业应该做什么，为什么，依据是什么 | 这些工作如何被**可靠地跑完** |
| **核心对象** | Context / Evidence / Decision / Workflow Spec | Task / Run / Queue / Attempt / Span |
| **关心的失败** | 结论错了、依据不足、越权访问 | 任务超时、进程崩溃、重试、并发过载 |
| **"正确"的定义** | 业务正确性（这个判断对不对） | 执行正确性（这个任务跑完了没有） |
| **时间尺度** | 业务周期（审计期、合同有效期） | 执行周期（秒/分/小时，最长可跨部署） |
| **对 LLM 的态度** | 规则优先，LLM 仅做理解与叙述 | 无关；LLM 调用只是任务体里的一段代码 |
| **持久化的是什么** | 业务上下文与证据 | 执行状态与 tracing |
| **典型问题** | "供应商年度准入该不该通过？" | "这 200 个准入检查任务有没有全部跑完、失败的有没有重试？" |

### 2.1 为什么 Kernel 不实现 Queue / Retry / Scheduler

不是因为"做不出来"，而是因为：

1. **它们与业务语义正交**。重试策略、并发上限、调度窗口是工程参数，不随领域变化。
2. **成熟实现已经存在且更可靠**。自研意味着要自己解决恰好一次语义、崩溃恢复、水平扩展、可观测性——这些是 Trigger.dev 的整个产品。
3. **铁律 3 明令禁止**。ECE `CLAUDE.md` 铁律 3「垂直纪律」把"消息队列 / 自研 Runtime / 微服务"列入禁止自研清单，除非 ADR 明确推翻。
4. **它会腐蚀 Kernel 的定位**。一旦 Kernel 有了执行引擎，团队精力会不可避免地从"业务推理质量"转向"执行稳定性"——这正是红队警告的"横向 = 死亡陷阱"。

### 2.2 但也正因如此，集成 Trigger.dev 需要 ADR

引入 Trigger.dev 是**引入一项新的横向基础设施依赖**。按 ECE `CLAUDE.md` §3.3，这必须"停下写 ADR"。这正是 `docs/adr/ADR-011.md` 存在的理由。

`★` 关键限定：**ADR-011 决策的不是"用不用 Trigger.dev"，而是"Kernel 与执行运行时的接口长什么样"。** 具体实现可以在 V0 用最朴素的进程内执行器，在 V1 换成 Trigger.dev——接口不变。

---

## 3. Kernel vs DeepSeek Harness (DSH)

| 维度 | Kernel | DSH [C44] |
|---|---|---|
| **解决的问题** | 企业业务语义、授权与可追溯 | 如何让一个 Agent 在真实环境里**持续工作** |
| **核心对象** | Context / Ontology / Evidence / Decision | Agent / Session / Tool / Sandbox / Trajectory |
| **插件化对象** | 领域包（ontology / 规则 / spec） | model / tool / sandbox / loop / storage / UI |
| **上下文边界** | 企业级、跨 Agent、受权限约束 | 会话级（session），跨 Agent 时靠 harness 状态传递 |
| **权限** | 数据访问层强制 | 不负责（沙箱 ≠ 授权） |
| **产出** | 业务证据与决策 | Agent 输出与轨迹 |
| **可替换性** | 换领域包换行业 | 换 harness 换执行底座 |

### 3.1 三个必须说清的差别

**差别一：Session Context ≠ Business Context。**
DSH 的 session 承载的是"这个 Agent 这一轮看到了什么"；Kernel 的 Context 承载的是"这家企业在这个业务情境下的结构化状态"。前者是执行态的，后者是业务态的。把前者当后者用，结果是：换一个 Agent、换一次会话，业务上下文就断了。

**差别二：Subagent ≠ 跨 Agent 业务语义共享。**
DSH 支持 subagent 作为子运行时，但子 Agent 之间传递的是 harness 状态。Kernel 要求的是：

```
Agent A → Evidence / State Change → Context → Agent B
```

而不是：

```
Agent A → 巨大 Prompt → Agent B
```

后者不可审计：B 的结论依赖一段无法复现的自然语言。前者可审计：B 的结论可以回溯到 A 产生的**具名证据对象**。

**差别三：Trajectory ≠ Evidence。**
DSH 的 Trajectory 是"DevTools for agents"——它回答"模型看到了什么、做了什么"。企业要问的是"这个业务结论的依据是什么、谁批准的"。前者是工程记录，后者是业务证据。两者需要关联，但不能互相替代。

### 3.2 为什么这是互补而不是竞争

DSH 越成熟，Kernel 越有价值——因为 Agent 能做的事情越多，"做什么才是对的"这个问题就越关键。反过来，Kernel 越成熟，DSH 也越好用——因为 Agent 拿到的业务上下文质量更高。

**这是分工，不是竞争。** 判据很简单：**DSH 的 roadmap 上不会出现"企业领域本体"或"审计证据充分性判断"**；Kernel 的 roadmap 上不会出现"sandbox 隔离"或"agent loop 调度"。

---

## 4. Kernel vs PentAGI

| 维度 | Kernel | PentAGI [C45] |
|---|---|---|
| **是什么** | 领域无关的 Kernel（V0 以采购/审计领域包验证） | **领域特化的 Agent 应用**（自主渗透测试） |
| **领域** | 可换领域包 | 固定：安全测试 |
| **多 Agent** | 不做 Agent 编排（交运行时） | 自带多 Agent 监督（researcher/developer/executor） |
| **沙箱** | 不做 | 核心能力（Docker 隔离执行） |
| **与 Kernel 的关系** | — | **Kernel 可以调用的 Agent Runtime 之一** |

**关键判断**：PentAGI 不是 Kernel 的竞争品，而是 **Kernel 之上"领域 Agent 应用"的一个真实样本**。它证明了：

1. 领域 Agent 应用可以做到很深（渗透测试领域）；
2. 一个可用的 Agent 应用需要多 Agent 监督 + 沙箱 + 工具链——**这些正是 Kernel 要外包给运行时的东西**；
3. 如果一个团队要自己造 PentAGI 这一层，成本极高；Kernel 的价值主张因此更清晰：**让领域 Agent 应用不必重复解决 Context / 权限 / 证据 / 评估**。

**边界规则**：若某任务需要"在隔离环境中自主执行多步攻击性/探测性操作"，那是 PentAGI 类运行时的职责。Kernel 的职责是：判断**是否应该**执行、**依据什么**执行、**谁授权**、以及**留下什么证据**。

---

## 5. Kernel vs Glean

| 维度 | Kernel | Glean [C01–C42] |
|---|---|---|
| **解决的问题** | 企业业务语义与决策 | 企业信息"找得到、看得对" |
| **定位** | 判断层 | **Provider（可插拔）** |
| **强项** | 领域本体 / 业务推理 / 业务证据 / 权限裁决 | 275+ 连接器 / 横向搜索 / 源系统 ACL 继承 / Enterprise Graph |
| **部署** | 私有化优先（主路径 D） | SaaS 为主 |
| **可达市场** | 中国大陆（私有化 + 国产开源模型） | 中国大陆无客户（红队 v3 U-G1 CONFIRMED） |
| **在 V3 中的角色** | — | 与本地知识 / 企业 API / MCP 并列的**一项 Provider** |

### 5.1 V0.1 → V2 → V3 的三次降级

| 阶段 | Glean 的地位 | 问题 |
|---|---|---|
| **PRD v0.1（作废）** | **底座**（Glean 拥有 Context/Search/Permission/Connectors） | 一旦 Glean 不合作，产品整体不成立 |
| **V2（`platform-kernel-definition.md:174`）** | **可选 Adapter**（"Kernel 自建不可替代，Glean 集成作为可选 Adapter，不替换 Kernel"） | 方向正确，但对照系仍只有 Glean 一个 |
| **V3（本文件）** | **Provider 之一**，与本地知识库 / 企业 API / 开源栈 / MCP 并列 | 对照系扩展为"任意 Provider + 任意 Runtime" |

### 5.2 表述纪律（强制）

C22 / C23 是**无来源 URL 的推断**。因此：

- ❌ 不可写："Glean 没有领域本体/推理/评估能力。"
- ✅ 必须写："**未见 Glean 提供领域正确性/业务推理质量评估的公开证据**（`research_v2/07-governance-evaluation.md:57`）；Glean Enterprise Graph schema 的可定制性 **C03 = UNKNOWN**。"

**更重要的架构性理由**：Kernel 自建这些层**不只因为"Glean 没有"**，更因为：

1. **私有化部署**：Glean 的 SaaS 形态在可达市场不成立；
2. **领域纵深**：审计/采购的业务规则与评估语料，任何通用平台都不会替客户沉淀；
3. **数据主权**：Trust 的货币在中国是"我根本不拿你的数据"（红队 v3 §0.6）。

即使 Glean 明天补齐了领域能力，这三条理由仍然成立。**这是 Kernel 边界比 V2 更稳的原因。**

---

## 6. Kernel vs Generic Agent Platform

| 维度 | Kernel | Generic Agent Platform |
|---|---|---|
| **核心隐喻** | 企业业务情境的结构化状态 | Agent 的构建与编排工具 |
| **用户** | 业务专家 + 领域工程师 | Agent 开发者 |
| **交付物** | 业务结论 + 证据 | Agent 定义 + 运行 |
| **多租户** | 明确不做（V0/V1） | 通常核心卖点 |
| **典型形态** | 无 Builder UI（`glean-x-product.md`：我方资源放 Domain Agent 而非 Builder UI） | 可视化编排 + Prompt/Skill 市场 |
| **护城河假设** | 领域本体 + 评估语料 + 客户环境内沉淀的上下文（随使用复利加深） | 工具链成熟度 + 生态 |

**为什么不做**：

1. **红海**。Agent 平台赛道在中国极度拥挤（Dify / FastGPT / MaxKB / RAGFlow + 大厂方案）。
2. **IP 太薄**。平台能力会被快速商品化；红队明确指出"不要把壁垒定义为 LLM / RAG / Vector DB / Agent Framework"。
3. **与客户价值脱节**。客户买的不是"一个 Agent 平台"，是"一件以前要 2 小时、现在 10 分钟的事"。

**因此**：Kernel 没有 Agent Builder UI，没有 Prompt 市场，没有可视化编排器。Agent 定义必须是**版本化文件（code-first / YAML）**，可进 git，可在 Claude Code / Cursor / VS Code 里编辑（沿用 `research_v2/08-platform-developer.md` 的结论）。

---

## 7. Kernel vs RAG Platform

| 维度 | Kernel | RAG Platform |
|---|---|---|
| **检索的地位** | 众多输入之一（4 路召回中的一路） | 核心机制 |
| **上下文来源** | 实体 + 关系 + 结构化业务数据 + 时态 + 权限 + 文档 | 主要为文档 chunk 向量检索 |
| **权限** | 数据访问层强制（硬门） | 常见为检索后过滤或 prompt 约束 |
| **推理** | 规则引擎（确定性）+ LLM 轻量解释 | 主要是 LLM 生成 |
| **评估** | 业务正确性（结论对不对） | 检索质量（召回/命中） |
| **失败模式** | 结论错误但引用充分（**最危险**） | 检索不到 / 幻觉 |

**最关键的差别**：RAG 的失败是"没找到"，Kernel 必须防的失败是"**找错了还理直气壮**"。

审计/采购场景里，一个引用充分、格式漂亮、但结论错误的输出，比"我不知道"危险得多。这正是为什么 Kernel 要求：

1. **确定性判断走规则不走 LLM**（ADR-010）；
2. **不足时输出 `insufficient_context` 而非猜测**（ECE 评估模型）；
3. **每条结论必须可追溯到具名证据**（Evidence 模型）；
4. **业务正确性评估独立于检索质量评估**（ADR-008）。

---

## 8. 汇总对照表

| | Kernel | Trigger.dev | DSH | PentAGI | Glean | Generic Agent Platform | RAG Platform |
|---|---|---|---|---|---|---|---|
| 业务语义 | **PRIMARY** | — | — | 领域内 | Provider | — | — |
| 领域本体 | **PRIMARY** | — | — | 领域内 | UNKNOWN | — | — |
| 权限裁决 | **PRIMARY** | — | — | — | Provider | — | 常缺 |
| 业务证据 | **PRIMARY** | 执行引用 | Agent 输出 | Agent 输出 | Provider | — | — |
| 业务推理 | **PRIMARY** | — | Agent 级 | Agent 级 | Agent 级 | Agent 级 | LLM 生成 |
| 业务正确性评估 | **PRIMARY** | — | — | 领域内 | 反证式空白 | — | — |
| 业务 Workflow 语义 | **PRIMARY** | — | — | 领域内 | — | — | — |
| 可靠执行 | Adapter | **PRIMARY** | — | — | — | 部分 | — |
| Agent 循环 | — | — | **PRIMARY** | **PRIMARY** | Provider | **PRIMARY** | — |
| 沙箱隔离 | — | — | **PRIMARY** | **PRIMARY** | — | 部分 | — |
| 横向搜索 | Provider | — | Tool | Tool | **PRIMARY** | — | 部分 |
| 连接器生态 | 3 mock | — | — | — | **PRIMARY** | — | — |
| 私有化优先 | **PRIMARY** | 可自托管 | 本地可跑 | 可自托管 | SaaS 为主 | 视实现 | 视实现 |
| 模型无关 | **PRIMARY** | — | **PRIMARY** | **PRIMARY** | Provider | 视实现 | 视实现 |

---

## 9. 最终一句话（V3 指令 §23 要求）

> **因为 Kernel 不是"把任务跑起来"、不是"让 Agent 一直工作"、不是"把数据连起来"、也不是"把文档检索出来"，而是"在企业的权限与业务语义边界内，产出一个有依据、可授权、可追溯的业务判断"——前四者可以买、可以换、可以集成，只有最后一项必须自己拥有，它就是产品本身。**

---

## 10. 本文件的证据局限（诚实声明）

| 局限 | 影响 |
|---|---|
| C43（Trigger.dev）来自检索面摘要，**直接原文抓取被工具限制拒绝** | 具体能力细节（如自托管资源要求）未逐字核验，不得用于容量规划 |
| C44（DSH）仅有二手来源（教程/评测），**未取得原始仓库 README 逐字核验** | DSH 的能力集合可能在版本间变化；V3 只使用其**类别定位**（Agent Harness），不使用其具体实现细节 |
| C45（PentAGI）为本机一手核验，**但其"可被外部编排调用"的 API 表面未验证** | 不得声称 PentAGI 可直接作为 Kernel 的运行时适配器；列为待补证据（`EVIDENCE_V3_ADDENDUM.md` §5） |
| Glean Agent Harness（C25/C41）= **UNKNOWN** | V3 不得假设 Glean 的 Harness 与 DSH 同类或不同类 |

**原则**：以上局限**不影响本文件的边界结论**，因为边界是**类别级**的（执行运行时 / Agent Harness / Provider），而局限都在**实现细节级**。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
