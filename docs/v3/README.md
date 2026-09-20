# docs/v3 — Domain Intelligence Kernel (PRD V3)

> Version: 1.1
> Date: 2026-09-20
> Status: **CLOSED OUT — V3 收口完成，STOP**
> ⚠️ **先读 `V3_CLOSEOUT.md`** —— 它是 V3 的收口裁定，取代下列文件中被点名的部分。
> **V3 = Architecture Hypothesis，不是 Product-Market Validation。**
> 本目录为 V3 阶段交付物。**不修改** v1（`docs/research/` `docs/architecture/` `docs/product/` `docs/cases/` `docs/customer/`）与 v2（`docs/research_v2/` `docs/architecture_v2/` `docs/product_v2/`）的任何文件。

---

## 1. 交付物清单

| 文件 | 内容 | 审阅优先级 |
|---|---|---|
| **`V3_CLOSEOUT.md`** | **收口裁定**：Kernel 边界终裁 / V0 最小闭环 / 删除推迟清单 / 下一步三动作 | ⭐⭐⭐ **先读** |
| **`PRD_V3.md`** | 主 PRD，40 章 + 3 附录（§17/§32/§16.2 已被收口取代） | ⭐⭐⭐ |
| **`KERNEL_BOUNDARY.md`** | 26 行能力边界矩阵 + 边界自检 + MUST NOT 清单 | ⭐⭐⭐ |
| **`RUNTIME_COMPARISON.md`** | Kernel vs Trigger.dev / DSH / PentaGI / Glean / Generic Agent Platform / RAG Platform | ⭐⭐⭐ |
| `KERNEL_ARCHITECTURE_V3.md` | 五层架构 + 三类接口 + 数据模型 + 8 条架构不变式 | ⭐⭐ |
| `ARCHITECTURE_DECISION_V3.md` | 10 条 V3 架构决策 + 与 v0.1/V2/ECE 铁律的关系 + BBIP 矩阵 | ⭐⭐ |
| `MVP_SCOPE_V3.md` | V0 最小范围（2–4 周）+ 规模红线 + 验收 DoD | ⭐⭐ |
| `EVIDENCE_V3_ADDENDUM.md` | 新增证据 C43–C48（证据纪律要求） | ⭐ |
| `SELF_REVIEW_V3.md` | **红队自检**：5 项架构测试 + 8 条对抗性自审（含 3 条未缓解风险） | ⭐⭐⭐ |
| `CODEX_REVIEW_BRIEF.md` | **送 Codex 的独立审查任务书**：两轮次 + 必答问题 + 反馈 schema + 取证命令 | ⭐⭐⭐ |
| `CODEX_FINAL_CLOSEOUT.md` | **最终收口刀报告**（两处剩余问题处置 + R40R2.7 runner 修复 + 真实失败记录 + Remaining Issues） | ⭐⭐⭐ **先读** |
| `CODEX_ROUND3_CLOSEOUT_REPORT.md` | **大刀收口最终报告**（判词 §七 格式：判定 / 七项状态 / P1 证据 / 已知问题 / commit / ready for audit） | ⭐⭐⭐ **先读** |
| `CODEX_ROUND3_FINDINGS.md` | **第三轮判词落实记录**（CONDITIONAL PASS → P1' 补齐 DB 指纹 + 执行关系修正）| ⭐⭐⭐ |
| `CODEX_ROUND2_FINDINGS.md` | **第二轮判词落实记录** + 第三轮送审范围（P1/P2/P3 + 三处修正 + 冻结声明） | ⭐⭐⭐ |
| `A_CUSTOMER_VALIDATION.md` | **A 执行件**：48h Customer Access Test + 中国三问 + 访谈纪律 + 记录模板 + 判定门。**照着做即可** | ⭐⭐⭐ |
| `../adr/ADR-011.md` | Kernel ↔ Runtime 边界决策 | ⭐⭐⭐ |
| `../diagrams/kernel-architecture-v3.mmd` | V3 架构 mermaid 图 | ⭐ |

**审阅建议**（用户原话）：先看 `PRD_V3 + KERNEL_BOUNDARY + RUNTIME_COMPARISON` 三份，重点检查**有没有又偷偷把 Kernel 做成"Agent 平台"**。

---

## 2. 一页摘要

**Kernel 是业务智能层，不是基础执行层。**

> Kernel 不是 Trigger.dev，不是 DeepSeek Harness，不是 PentaGI，也不是它们的竞争品；Kernel 位于这些执行能力之上，负责企业业务 Context、Domain Semantics、Reasoning、Decision 和 Agent/Workflow Selection。

```
Business Goal
   ↓
┌──────────────────────────────┐
│      DOMAIN KERNEL           │  ← 产品
│  Context / Ontology /        │
│  Permission / Evidence /     │
│  Reasoning / Decision /      │
│  Workflow Spec / Selection   │
└──────────────┬───────────────┘
               │ Execution Intent
   ┌───────────┼───────────┐
   ▼           ▼           ▼
Agent RT   Workflow RT   Providers
DSH        Trigger.dev   Glean / Local / API / MCP
PentAGI    进程内(V0)
   └───────────┼───────────┘
               ▼
        ENTERPRISE SYSTEMS
               ↓
        Evidence → Context Update → next action
```

---

## 3. V3 相对 V2 的三处实质推进

| # | 推进 | 位置 |
|---|---|---|
| 1 | **对照系扩展**：从"只与 Glean 对照"到"与 Provider + Agent Runtime + Execution Runtime 三类对照" | `KERNEL_BOUNDARY.md` `RUNTIME_COMPARISON.md` |
| 2 | **两个新的一级对象**：`Evidence`（业务证据）与 `Domain Workflow Specification`（业务工作流语义） | `PRD_V3.md` §14/§16 |
| 3 | **Glean 降到 Provider**：底座 → 可选 Adapter → 可插拔 Provider 之一 | `PRD_V3.md` §21 |

**自建理由重心转移**（V3 关键修正）：从"Glean 未覆盖（C22/C23，**无来源 URL 的推断**）"移到"私有化部署约束 + 领域纵深 + 业务正确性评估"——**这三条在 Glean 补齐领域能力时仍然成立**。

---

## 4. 诚实声明（必读）

本目录**不掩盖**以下事实：

| 项 | 事实 |
|---|---|
| **客户验证 = 0** | 无一场访谈、无一份脱敏数据。全部评分与阈值都是**计划** |
| ~~权限硬门未通过~~ **已修复（2026-09-20）** | ECE v0 曾实测 E2 = **5 暴露 + 5 失败**（C47，*historical*）。**现为 61/61（0 暴露 0 失败）** —— ece `037260b` 修复 + `32a0b92` 单变量实验。`Permission Before Intelligence` 现已在实现层达成 |
| **评测套件部分失败** | E3 = 15.0%（数据集过期所致，重生成后 100%）；E5 = 0.0%（含真实问题）；E4 = 100% 但 vacuous。**runner 已不崩**（R40R2.7 已修） |
| **护城河假设未验证** | 红队判定"当前范围内护城河假设不成立" |
| **C22/C23 无来源 URL** | "Glean 不覆盖领域层"是**推断**，V3 全文使用反证式措辞，未写成事实 |
| **C43/C44 抓取受限** | Trigger.dev 原文抓取被工具限制拒绝；DSH 仅二手来源 |
| **框架-地域错配未解决** | 红队 G2：原 MVP scope 排除 ISO27001，而可达市场主流是等保/内控/个保审计 |

---

## 5. 收口后状态（STOP）

Codex 独立审查判词：**架构自洽但过完整；Kernel 职责有向「上层 Agent Platform」膨胀的风险；V0 与 2–4 周不匹配。**

收口结果见 **`V3_CLOSEOUT.md`**。要点：

```
Kernel 核心收窄为 5 项：
  Context · Domain Ontology · Deterministic Business Rules · Decision · Evidence

移出 Kernel：
  Retrieval 机制 / Tool 选择与执行 / Agent·Runtime 动态选择 / 执行编排

V0 收缩为 6 步最小闭环（不再是"完整 Kernel"）：
  Context → Entity/Knowledge → 一个确定性 Business Rule
          → Decision → Evidence → Context Update
```

**下一阶段推进关系**（Codex 第三轮判词 §10 修正 —— 旧表述"必须同时进入"已作废）：

```
A 客户发现  ──┐
              ├─→ B 选 Reference Workflow（等 A）
C V0 Spike  ──┘   （A 与 C 并行，互不阻塞）
```

```
A. 一个真实客户问题验证         ← 可立即启动（Step 0 Customer Access Test + Step 0.6 中国三问）
B. 一个最小 Reference Workflow   ← 由 A 决定，不提前拍板
C. 一个可运行的 V0 technical spike ← 可立即启动（纯技术，不依赖客户）
```

**STOP** —— 不写 V4 / 不扩 PRD / 不重研 Glean / 不开始大规模实现。

### 执行进展（2026-09-20）

| 动作 | 状态 |
|---|---|
| **A** 客户问题验证 | 执行件已交付并**按第二轮判词修正**（`A_CUSTOMER_VALIDATION.md`）；**实际访谈未开始**（需真人） |
| **C** V0 technical spike | **Permission 硬门 5 暴露 + 5 失败 → 61/61 全绿**（ece `037260b`）<br>**+ P1 严格单变量实验**：同一数据集下 baseline 代码 4E/4F vs 修后 0E/0F（ece `93ed0e3`）<br>**+ P2 E1 hermeticity 已修**：全套 pytest 后零重名，E1 回到 98.5%<br>未做：R40R2.7（E3/E4/E5 runner 仍崩） |
| — | A 未跑完前，**不拍板 B**（选 Reference Workflow） |

**Codex 第二轮判词结论**：V3 架构 **GO（可封版）** · Kernel Architecture **FREEZE** ·
Customer Validation **GO** · V0 **GO（可开始 Technical Spike）**。详见 `CODEX_ROUND2_FINDINGS.md`。

---

## 6. 文件位置说明

V3 指令 §20 建议输出到 `docs/` 根（含 `ADR/` 子目录）。实际采用：

- 文档 → **`docs/v3/`**（沿用既有 `research_v2/` `architecture_v2/` `product_v2/` 的版本目录惯例，避免与 v1/v2 文件混放）
- ADR → **`docs/adr/ADR-011.md`**（沿用根 ADR 系列命名 `ADR-NNN.md`）

**与指令的两处偏差（已声明）**：

1. §20 要求 `ADR-003-kernel-runtime-boundary.md`。但 `docs/adr/ADR-003.md` 已存在（Permission Engine，Status: Accepted）。按根 ADR 系列"沿现有编号追加"的规则，新 ADR 编号为 **ADR-011**，文件名为系列惯例的裸编号形式。
2. §20 建议的 `KERNEL_ARCHITECTURE_V3.md` / `ARCHITECTURE_DECISION_V3.md` 等文件名已按要求保留。

**未修改的文件**：v1 / v2 全部目录、根目录全部治理文件（`CLAUDE.md` / `RESEARCH_PRD_V2.md` / `RED_TEAM_REVIEW.md` / `Enterprise Context Engine.md`）。

---

## 7. 编号与约定

| 项 | 值 |
|---|---|
| 证据编号 | 承接 C01–C42，新增 **C43–C48**（下一可用 C49） |
| ADR 编号 | 根系列 ADR-001…010 → 新增 **ADR-011**（与 `ece/docs/adr/` 系列独立编号，互不冲突） |
| 置信度 | `CONFIRMED` / `STRONGLY_INFERRED` / `INFERRED` / `UNKNOWN`（UNKNOWN 不得作为设计前提） |
| 表述纪律 | 不得写"Glean 没有 X"；须用反证式措辞 |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Review Focus**: `PRD_V3` + `KERNEL_BOUNDARY` + `RUNTIME_COMPARISON`
