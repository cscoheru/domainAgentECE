# CODEX_ROUND3_FINDINGS.md — 第三轮判词落实记录

> Date: 2026-09-20
> 判词原文: `/Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0920/codex第三轮判词.md`
> 判词结论: **CONDITIONAL PASS**
> 性质: 落实记录 + 第四轮送审范围。*不是*架构迭代（`V3_CLOSEOUT.md` §5.1 已冻结架构）。

---

## 1. 判词总表（Codex 原文 → 落实状态）

| 项 | Codex 判定 | 落实 |
|---|---|---|
| V3 收口 | ✅ PASS | — |
| Kernel Boundary | ✅ PASS | — |
| V0 收缩 | ✅ PASS | — |
| **P1 单变量实验** | ⚠️ **MAJOR：DB state 证据尚未闭合** | → **P1' 已补**（§2） |
| P2 E1 hermeticity | ✅ PASS（"可以关闭"） | 不再动 E1 |
| P3 Customer Access | ✅ PASS | — |
| RC-7 / RC-8 / RC-11 | ✅ PASS | — |
| E1 污染归因 | ✅ PASS | — |
| 架构冻结 | ✅ PASS（"V3 可以正式冻结"） | — |
| 整体文档循环 | ✅ 已停止 | — |

**Codex 原话**：「不是因为 Permission 修复有问题。恰恰相反：**Permission 当前 61/61、
0 exposure 的结果，我认为可信。** 需要补的是**实验设计的证据严谨度**，不是重新修 Permission。」

---

## 2. [MAJOR] P1' — 补齐 DB 状态证据（已完成）

### 2.1 Codex 的批评（照抄）

> 「你提供的 P1 证据只证明：两组使用同一个 `e2_permission.json`。
> 它没有充分证明：两组使用完全相同的数据库 state。」
>
> 「尤其作者自己写明：RC-9 是 `seed.py` 的数据/seed 修复，而不是代码修复。
> 这恰恰说明 **seed state 是实验变量之一**。」
>
> 「所以目前最严谨的结论应该是：**E2 fixed code 在当前固定数据库状态 + 固定数据集上
> 由 4/4 → 0/0**。而不是：**037260b 相对于 baseline 的完整代码变化被严格因果证明。**」

### 2.2 作者承认

**这个批评是对的，我原来的声明过强。**

原 P1 只固定了数据集；两臂共用的那个 DB 状态**已经是 `037260b` 的修后 seed 产出的**，
所以 seed/数据层面的修复（RC-6/7/9）在两臂中均已生效 —— 它确实是一个**未受控变量**。
另外原实验两臂运行时环境不同（宿主 uvicorn vs docker）。

→ 原归档中「证据等级：由『可信』提升为**严格因果证明**」一句**已撤回**并就地标注。

### 2.3 P1' 实验设计（`single-variable-v2/`）

补齐两点：

1. **DB 状态指纹** —— `scripts/db_state_fingerprint.sql`，对 E2 依赖的全部状态
   （`entities` 的身份列 + `attributes.department` / `is_management` / `roles`；`acl_entries` 全表）
   做**有序 md5**。在两臂**之前 / 之间 / 之后**各取一次。
2. **两臂同运行时** —— 均跑宿主 uvicorn（同 venv、同 `DATABASE_URL`），
   消除"宿主 vs docker"的环境差异。

### 2.4 结果

| 项 | 值 |
|---|---|
| **F0**（两臂开始前） | `faff49167d6781e6245dcd58ab116c10` |
| **F1**（ARM A 结束后） | `faff49167d6781e6245dcd58ab116c10` |
| **F2**（ARM B 结束后） | `faff49167d6781e6245dcd58ab116c10` |
| baseline commit | `c92316370b87343ba76c5776f9d56eb05e3f7be3` |
| fixed commit | `93ed0e307fd22f9b30b5a16314344c730bd837ff` |
| dataset sha256 | `7f82340adcbca4118aae51ad20090a0c40fd75f8301e1e7cd59c2a9d5ca9670c` |
| ARM A（baseline） | **4 暴露 + 4 失败**，exit 2 |
| ARM B（fixed） | **0 暴露 + 0 失败**，exit 0 |

**F0 == F1 == F2 → DB 状态在两臂之间未被改动，已证明。**

原始 stdout + 完整实验记录：`single-variable-v2/EXPERIMENT_RECORD.txt`、`E2-baseline-code.txt`、`E2-fixed-code.txt`。
复现：`bash scripts/run_p1_single_variable_experiment.sh`。

### 2.5 修正后的结论口径（严格，以此为准）

> 在【固定 DB 状态】+【固定数据集】+【同一运行时】下，
> **permission RUNTIME 代码**由 baseline 改为 fixed，E2 从 4 暴露/4 失败 变为 0/0。

**本实验【不】测量的**：

> seed / 数据层面的修复（RC-6 部门注入位置、RC-7 专属对象、RC-9 ACL 词表）——
> 它们已由修后的 seed 写入 DB，两臂共用同一份，故其贡献在本设计中**恒为 0**。
> 要测量它们需另设一臂：**baseline 代码 + baseline seed 产出的 DB**。

---

## 3. 三个必改项 → 状态

| # | Codex 要求 | 状态 |
|---|---|---|
| **1** | P1 补齐 DB state fingerprint，证明两臂除目标代码变量外完全相同 | ✅ **已补**（§2，F0==F1==F2） |
| **2** | E1 hermeticity 关闭后不再折腾 E1；98.5% 已达当前 acceptance | ✅ **接受，不动**。E1 自此为验收基线，不再迭代 |
| **3** | 停止 V3 架构工作；**A 与 C 并行，B 等 A** | ✅ **已接受**（§4 的两处文档不一致已修正） |

---

## 4. Codex §10 — 执行关系修正（已落实）

Codex 指出 `V3_CLOSEOUT §4`（"必须同时进入"）与 `A_CUSTOMER_VALIDATION`（"B 和 C 都不许拍板"）
**表述不一致**，并给出正确逻辑：

```
A Customer Discovery  →  决定 B 做什么
C Technical Spike     →  独立验证 Kernel 是否跑得通
因此: A 和 C 可以并行; B 等 A。
```

**落实**（两处均为 errata 级修正）：

| 文件 | 原 | 现 |
|---|---|---|
| `V3_CLOSEOUT.md` §4 | "必须同时进入（不是串行）" | **推进关系图**：A ∥ C；B 等 A。并说明原文措辞不准 |
| `A_CUSTOMER_VALIDATION.md` | "后面的 B 和 C 都不许拍板" | **"A 与 C 可以并行；B 等 A 的结果"** |

> Codex 说"不用为了这个再写文档，执行时按这个逻辑理解即可"。
> 作者仍然改了 —— 理由：这是一处**事实性矛盾**（两文档互相打架），
> 属 `V3_CLOSEOUT` §5.1 明确允许的 errata 级修正，不新增任何架构内容。

---

## 5. Codex §9 — `/permissions/check` 升级为生产门槛（已标注）

Codex：「不阻塞 V0。但我会把它列为：**V0 → Production 的必过门槛**。」

→ `ece/src/ece/api/identity.py` 中该行上方的标注已升级，明写
**V0 → Production 必过门槛**：任何真实授权链启用前必须删除 `req.user_ref`，
只从认证凭据解析 principal。

---

## 6. Codex 明确的「V3 不该再做的一件事」

> **不要再增加任何"Kernel 架构证明"。**
> 包括：不再写 V4；不再增加 Kernel 对象；不再扩大 26 行矩阵；
> 不再继续证明"Kernel 与 DSH/Glean/Trigger.dev 的区别"。

**本项目接受此约束，并记为冻结期纪律。** 与 `V3_CLOSEOUT.md` §5.1 的冻结点一致。

Codex 给出下一次真正该产出的东西：

> **一个真实企业问题 + 一份真实数据 + 一个跑通的 V0
> `Context → Decision → Evidence → Context Update`。**

---

## 7. 第四轮送审范围

**必读**

```
docs/v3/CODEX_ROUND3_FINDINGS.md   ← 本文件
docs/v3/V3_CLOSEOUT.md             ← §4 推进关系修正 / §5.1 冻结点
docs/v3/A_CUSTOMER_VALIDATION.md   ← 执行关系修正
codex 第三轮判词原文（仓库外）
```

**ece 仓**

```
ece/ commit（本轮）
ece/scripts/db_state_fingerprint.sql                    ← 指纹定义
ece/scripts/run_p1_single_variable_experiment.sh        ← 可复现实验
ece/reports/eval-archive/2026-09-20-cut040R2/single-variable-v2/EXPERIMENT_RECORD.txt
ece/src/ece/api/identity.py                             ← §9 生产门槛标注
ece/reports/eval-archive/2026-09-20-cut040R2/README.md  ← 原过度声明的撤回标注
```

**建议的核验问题**

1. **P1' 是否真的闭合了 MAJOR？** F0==F1==F2 是否足以证明 DB 恒定？
   指纹的覆盖面（entities 的身份列 + 三个 attribute + acl_entries 全表）
   是否覆盖了 E2 依赖的全部状态？有无遗漏的表/列？
2. **修正后的结论口径是否准确？** "本实验不测量 seed/数据层修复"这一限定是否到位？
   是否还需要补第三臂（baseline 代码 + baseline seed 产出的 DB）？
3. **§4 的两处 errata 是否越界？** Codex 说"不用再写文档"，作者仍然改了 ——
   这是必要的 errata 还是不听指令？
4. **`V0 → Production` 门槛的标注是否足以防止它被遗忘？**
   只在代码注释里够吗，还是应该进 TASKS.md / ADR？

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
