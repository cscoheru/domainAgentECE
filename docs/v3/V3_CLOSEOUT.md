# V3_CLOSEOUT.md — V3 收口裁定

> Date: 2026-09-20
> 收口依据: Codex 独立审查（2026-09-20，`blueprintECE/0920/基于v3的codex反馈.md`）
> 判词要点: 架构自洽但**过完整**；Kernel 职责有向「上层 Agent Platform」膨胀的风险；V0 与 2–4 周目标不匹配；商业价值未验证。
> **本文件是 V3 的收口裁定**，取代 `PRD_V3.md` / `KERNEL_BOUNDARY.md` / `MVP_SCOPE_V3.md` / `ADR-011.md` 中被点名的部分。其余内容不变。
> **V3 = Architecture Hypothesis，不是 Product-Market Validation。**
> 本文件之后 STOP：不写 V4，不扩 PRD，不重新研究 Glean，不开始大规模实现。
> **本文件自身的审验范围**（送审文件清单 / 五个必答问题 / 取证命令）见 `CODEX_REVIEW_BRIEF.md` **§8**。

---

## 1. V3 最终确定的 Kernel 边界

### 1.1 逐项裁决

判据：**如果没有这一项，Kernel 是否仍然成立？**（"成立"含"可交付"——一个无法交付给企业的 Context Kernel 不算成立）

| 项 | 裁决 | 理由 |
|---|---|---|
| **Permission Enforcement** | **保留，收窄** | 去掉则 Kernel 产出未经授权的结论，企业不可交付 → **不成立**。收窄为：Kernel 只拥有 **强制点**（数据访问层）与 **scope 契约**；**policy 来源可以是 Provider** |
| **Knowledge / Retrieval** | **拆分** | Knowledge 作为 Context 要素 → **保留**（去掉则推理无输入）；**Retrieval 机制（4 路召回 / 融合 / 排序）→ 移出**，归 Provider |
| **Agent Selection / Action Planning** | **降级为接口声明** | 去掉后 Kernel 仍能产出 Decision → **仍成立**。故不作核心能力，只保留接口 / 策略声明；**V0 不实现动态选择** |
| **Tool Selection** | **拆分** | **Tool 准入（权限收口）→ 保留**；**工具选择与执行 → 移出**，归 Runtime / Harness |
| **Domain Workflow Specification** | **保留，硬收窄** | 保留，但**只描述「业务判据 + 责任人 + 审批要求」**；一旦包含执行顺序 / 分支 / 重试 / 并发，即成为执行编排器，**立即移出 Kernel** |

### 1.2 收口后的 Kernel 核心（去掉任一项即不成立）

```
Context（含 Entity / Relation / Temporal / Permission scope）
Domain Ontology
Deterministic Business Rules
Decision
Evidence
```

### 1.3 明确移出 Kernel

```
Retrieval 机制（召回 / 融合 / 排序）        → Provider
Tool 选择与工具执行                        → Runtime / Harness
Agent / Runtime 动态选择                   → V1（V0 仅固定，不选择）
执行编排（顺序 / 分支 / 重试 / 并发）        → Runtime
```

### 1.4 一处分类错误修正（作者自查）

`KERNEL_BOUNDARY.md` 行 25 把 **`Private Deployment` 列为能力行**属**范畴错误**——它是**非功能约束**，不是任何参与方"拥有"的能力。该行作废，改记为**约束**。其余 25 行不变。

---

## 2. V0 最小闭环

**V0 不再以「完整 Kernel」为目标。**

```
Context
  → Entity / Knowledge
  → 一个确定性 Business Rule
  → Decision
  → Evidence
  → Context Update
```

### 2.1 V0 只允许

```
1 个 Domain Pack
1 个固定 WorkflowSpec
1 个固定 Agent
1 个 InProcessExecutor
1 个 Local Provider
最小 Permission enforcement
最小 Evidence
```

### 2.2 V0 不实现

```
✗ 动态 Agent Selection          ✗ 动态 Runtime Selection
✗ 任一 Adapter（Trigger.dev / DSH / Glean）
✗ 多 Agent                      ✗ 通用 Connector
✗ Builder UI                    ✗ 通用 RAG 平台
✗ 通用 Workflow Engine          ✗ 三类接口抽象层
```

### 2.3 V0 的成功判据

> **证明 Kernel technical loop 成立** —— 即
> `Context → Entity/Knowledge → 一个确定性 Business Rule → Decision → Evidence → Context Update`
> 这一条链能够在窄切片上端到端跑通,且每步产出可验证。

不是"做出完整 Kernel"。

> ⚠️ **Codex 第二轮判词 §5 修正**：原文写的是「能够形成一个**真实业务价值闭环**」——**这个说法太强**。
> V0 最多证明**技术闭环成立**。
> **真实业务价值必须由 A（Customer Validation）来证明。**
> 因此明确：**V0 不负责证明 PMF（Product-Market Fit）。**
> 这是一条重要边界 —— 越界会把"工程跑通"误当作"市场成立"。
>
> 另外,判定一个 Kernel 不是"规则引擎 + RAG"的关键**不是那 5 项核心对象本身**,
> 而是链尾的 **Context Update**（结论回流改变下一轮的业务状态）。V0 必须真的实现这一步。

### 2.4 对 ADR-011 的影响

ADR-011 的状态仍为 Accepted，但其 **§3（三类接口）与 §5（V0 必须各有进程内实现）的 V0 义务被本收口取代**：V0 只保留**具体实现**（1 个 Local Provider + 1 个 InProcessExecutor，直接调用），**不建抽象层**。三类接口设计作为 **V1 方向**保留。

---

## 3. 明确删除 / 推迟的 V3 内容

| 内容 | 处置 | 位置 |
|---|---|---|
| Kernel 拥有 Retrieval 机制 | **删除**（移出 Kernel） | `KERNEL_BOUNDARY.md` 行 5 |
| Kernel 拥有 Agent Selection 实现 | **删除**（降为接口声明） | `KERNEL_BOUNDARY.md` 行 10；`PRD_V3.md` §17 |
| Kernel 拥有 Tool Selection | **删除**（只留 Tool 准入） | `KERNEL_BOUNDARY.md` 行 20 |
| WorkflowSpec 含执行顺序 | **删除**（只留判据/责任人/审批） | `PRD_V3.md` §16.2 的步骤序列示例 |
| `Private Deployment` 作为能力行 | **删除**（改记为约束） | `KERNEL_BOUNDARY.md` 行 25 |
| 三类接口抽象层进 V0 | **推迟到 V1** | `ADR-011.md` §3/§5；`KERNEL_ARCHITECTURE_V3.md` §3 |
| Adapter 设计细节（基于 C43/C44） | **推迟**，待运行时选型时再写 ADR | `PRD_V3.md` §22/§23/§24 |
| 13 步 V0 闭环 / 12 个 Build 能力 | **替换**为本文件 §2 的 6 步闭环 | `PRD_V3.md` §32；`MVP_SCOPE_V3.md` §2/§3 |
| 动态 Runtime / Agent 选择 | **推迟到 V1** | `PRD_V3.md` §17 |

**保留不动**：Evidence 一级对象、Domain Workflow Specification 的"业务判据"部分、Kernel 五层架构（作为 V1+ 的架构假设）、C43–C48 证据登记、SELF_REVIEW 的 8 条弱点。

---

## 4. 下一阶段的三个动作

**必须同时进入**（不是串行）：

| # | 动作 | 内容 | 前置 |
|---|---|---|---|
| **A** | **一个真实客户问题验证** | Step 0（48h Customer Access 冒烟，≥10 人外联、≥5 人应约）+ Step 0.6（中国三问：监管真实性 / 模型部署形态 / 私有化决策链） | 无（可立即启动） |
| **B** | **一个最小 Reference Workflow** | 由 A 的结果决定，**不提前拍板**。候选仍为采购 / 知识管理 / 审计 / Video Factory 等 | 依赖 A |
| **C** | **一个可运行的 V0 technical spike** | 本文件 §2 的 6 步闭环 | **建议优先**：先修 Permission 硬门（当前实测 5 暴露 + 5 失败），它是唯一不依赖客户、纯技术、可立即推进的前置 |

**三者关系**：A 决定"验什么"，B 定义"跑什么"，C 证明"跑得通"。任一单独推进都不构成下一阶段。

---

## 5. 状态

```
V3 = Architecture Hypothesis   ✅ 已交付并收口
V3 ≠ Product-Market Validation ❌ 未做，也不由文档解决
```

### 5.1 架构冻结点（Codex 第二轮判词 §1 明令）

> **本文件是架构冻结点。不要再出现 V3.1 / V3.2 / V4 架构迭代。**

Codex 原话：**"但这是最后一次。"**

因此自本文件起：

```
✅ 允许：执行（P1/P2 测试卫生、V0 spike、客户验证）
✅ 允许：对本文件与 V3 文档做 errata 级修正（错别字、措辞、事实更正）
❌ 不允许：新增架构层级、新增核心对象、新增接口族
❌ 不允许：V3.1 / V3.2 / V4 的架构重写
❌ 不允许：再写 PRD
```

若执行过程中发现架构确实有错，**走 ADR（新增一条，不重写既有的），不重写 PRD。**

---

## 6. 后续状态跟踪

| 日期 | 事件 | 位置 |
|---|---|---|
| 2026-09-20 | Codex 第一轮判词 → 本收口 | `blueprintECE/0920/基于v3的codex反馈.md` |
| 2026-09-20 | 矩阵一致性修复（8.B） | `KERNEL_BOUNDARY.md` v1.1 |
| 2026-09-20 | **Codex 第二轮判词：11 PASS / 1 FAIL(E1 hermeticity) / 1 需修正** | `blueprintECE/0920/Codex 第二轮正式判词.md` |
| 2026-09-20 | P1 单变量实验 + P2 E1 hermeticity 已落实 | ece 仓 `93ed0e3` |
| 2026-09-20 | P3 + 三处修正已落实 | `CODEX_ROUND2_FINDINGS.md` |

**第二轮判词结论**：V3 架构 **GO — 可以封版**；V3 PRD **STOP**；Glean Research **STOP**；
Kernel Architecture **FREEZE**；Customer Validation **GO**；V0 **GO — 可以开始 Technical Spike**。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
