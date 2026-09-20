# CODEX_FINAL_CLOSEOUT.md — 最终收口刀报告

> Date: 2026-09-20
> 依据: Codex 第三轮最后审验（`blueprintECE/0920/codex第三轮最后审验.md`）
> 性质: **最终收口刀**（非架构迭代）。V3_CLOSEOUT 保持最终裁定。
> ece commit: `f3a6639` → 本轮追加 · 根仓 commit: 本轮追加

---

## 1. 两处剩余问题 → 处置

| # | 判词要求 | 状态 |
|---|---|---|
| **1** | `MVP_SCOPE_V3.md` 仍含被误读为"当前状态"的旧结论 | ✅ **已修 4 处**（§2） |
| **2** | R40R2.7：E3/E4/E5 runner 仍崩 —— 不能直接盖章"不阻塞" | ✅ **runner 已修；真实失败已记录，未修**（§3） |

---

## 2. MVP_SCOPE_V3 的 4 处修正（判词指定）

| # | 项 | 原（会被读作当前状态） | 现 |
|---|---|---|---|
| 1 | **E2 状态** | `❌ 5 暴露 + 5 失败` | `✅ 61/61，0 暴露 0 失败`；5/5 标注为 *historical*（C47） |
| 2 | **三类 Interface** | `ProviderInterface` / `AgentRuntimeInterface` / `ExecutionRuntimeInterface` 各一 V0 实现 | **V0 不建三类接口抽象层**；V0 只保留三件**具体实现**（Local Provider / InProcessExecutor / 固定 Agent）。三类 interface 标注为 **HISTORICAL / V1+ DIRECTION** |
| 3 | **§6 DoD** | `§2 的 13 步` | `§2 的 6 步`（以 V3_CLOSEOUT §2 为准）；并明确 V0 运行时**不要求** interface 抽象层 |
| 4 | **§7 规模红线** | `Provider 实现 2` / `Runtime 实现 1` / `Agent 1–2` | `Local Provider 1` / `InProcessExecutor 1` / `Agent 1（固定，无 Selection）` / **`接口抽象层 0`** / `外部适配器 0` |

**原则遵守**：未删除任何历史内容；凡保留旧内容之处一律显式标注 `HISTORICAL` / `SUPERSEDED` / `V1+`。
**同一文档不再出现两个"当前状态"。**

### 2.1 全量一致性扫描的额外发现（判词未列举，一并清理）

| 文件 | 旧表述 | 处置 |
|---|---|---|
| `ARCHITECTURE_DECISION_V3.md` AD-V3-5 | "三类接口" 作为 V0 决策 + 验证项 `V0 三个接口各有进程内实现` | 加 **SUPERSEDED for V0** 标记；验证项改为 `V1 验收` |
| `ARCHITECTURE_DECISION_V3.md` AD-V3-9 | "Execution Runtime **Interface** 与 Agent Runtime **Interface** 的默认实现" | 改为"执行与 Agent 能力的**进程内具体实现**"，并注明不抽象为 interface |
| `README.md` §4 | "评测套件未跑通：E3/E4 runner 裸崩" | 改为当前真实状态 + 注明 runner 已修 |
| `PRD_V3.md` §38.1 | E3/E4/E5 "runner 裸崩 ❌ 未跑通" | 改为当前真实数字 + 失败性质 |
| `CODEX_ROUND2_FINDINGS.md` §2 | "证据等级：由『可信』提升为**严格因果证明**"（未标注） | 加 **SUPERSEDED** 标记 + 指向修正口径 |

---

## 3. R40R2.7 — runner 契约修复 + 真实失败记录

### 3.1 修复内容（**只修 runner ↔ runtime contract**）

**实测确认真实契约**（非假设）：

```
assemble_context(engine, user_ref, intent, entities, as_of: date | None = None, pack="procurement")
    -> ContextPackage   # dataclass，11 字段，含 .to_dict()
```

| 文件 | 契约错误 | 修法 |
|---|---|---|
| `run_e3_context.py` | `pkg.get(...)` → `'ContextPackage' object has no attribute 'get'` | `.to_dict()` |
| `run_e4_relationships.py` | 同上 | `.to_dict()` |
| `run_e5_temporal.py` | 同上 **+** `as_of` 传字符串 → `'str' object has no attribute 'isoformat'` | `.to_dict()` **+** `date.fromisoformat()` at boundary |

**未修改**：Kernel 架构 / Permission Engine / 测试语义 / 测试预期 / 数据集。
**未做**：改阈值 / 改 expected / 改数据让测试通过。

### 3.2 结果（原始 stdout: `ece/reports/eval-archive/2026-09-20-cut040R2/R40R2.7/`）

| 套件 | exit | 总 case | pass | fail | 性质 |
|---|---|---|---|---|---|
| **E3** | 1 | 100 | 15 | 85 | **数据集过期**（非 Kernel 逻辑失败） |
| **E4** | 0 | 30 | 30 | 0 | **vacuous pass**（非真实通过） |
| **E5** | 1 | 30 | 0 | 30 | **真实失败**（含测试污染） |

**runner 不再因类型/API contract 错误而崩溃 —— 本轮要求已达成。**

### 3.3 三类失败的区分与证据

#### A. E3 —— 数据集过期，**不是**业务逻辑失败

**根因**：`_next_display_id` 按"现有最大数字 +1"分配（`pipeline.py:49`）。`test_s14_seed_idempotent`
的 **DELETE + 重播**会让 `display_id` **整体上移** —— 当前 PR 的 display_id 已是 `PR202–PR401`，
而 **`PR001` 已不存在**。`e3_context.json` 引用的正是 `PR001` 等旧 display_id。

**诊断证据（决定性）**：从当前 DB 重新生成数据集后，**E3 = 100.0% PASS**。
诊断在 `/tmp` 进行，**仓库数据集已还原**（`git checkout -- data/eval/`）—— 未用改数据的方式让测试变绿。

#### B. E4 —— 100% 是 **vacuous**

边界 `[expected_count_min=0, expected_count_max=100]`：对象不存在 → 0 条关系 → 落在区间内 → 判通过。
**E4 的 100% 不构成"关系正确性已验证"的证据。**

#### C. E5 —— 真实失败（两个独立成因）

| 成因 | 证据 |
|---|---|
| **测试污染** | `expected_count = 5`，实测 **6** —— 多出的一条 `SUBMITTED_BY → U007` 来自 `src.system = 'test:seed_relationships_test'`（**测试创建**的关系） |
| **时态过滤语义待明确** | 关系行的 `valid = [None, None]`（无有效期）：`as_of=2024-01-01` 命中 6 条，而 `as_of=2024-12-31` / `2025-06-30` 命中 **0 条** |

**未修 —— 按判词 STOP 交裁定。**

### 3.4 顺带发现（第 5 个同族缺陷）

> **`display_id` 在每次 wipe+重播后整体漂移，且单调增长。**

与 RC-6 / R4 重名 / `seed_departments` 同族：**测试会改变它自己和其他组件依赖的状态**。
影响：任何以 `display_id` 为键的外部资产（评测数据集、文档、演示脚本）都会**静默过期**。
E1/E2 不受影响（E1 按名字解析、E2 只按 `object_ref` 字符串比对 ACL），E3/E5 受影响。

---

## 4. 其余 8 项检查（判词 §"只检查"）

| 检查 | 结果 |
|---|---|
| A ∥ C；B waits for A | ✅ 全仓一致（V3_CLOSEOUT / README / A_CUSTOMER_VALIDATION / findings 记录） |
| V3 = frozen architecture | ✅ 无新增 Kernel 对象 / 无扩大 26 行边界 / 无 V3.x·V4 / 无新 Adapter 抽象 |
| V0 = 6-step technical loop | ✅ MVP_SCOPE_V3 §2/§6.1/§7 已统一为 6 步 |
| Permission = 61/61 | ✅ |
| E1 = 98.5% | ✅ |
| P1 = fixed DB + fixed dataset + same runtime | ✅ F0 == F1 == F2 = `f20d9b8c…\|439\|1\|3` |
| P1 不再使用 "strict causal proof" | ✅ 全部替换为 A/B/C 三分口径；`CODEX_ROUND2_FINDINGS` 的旧表述已标 SUPERSEDED |
| 历史旧数字保留并标 historical/superseded | ✅ 未删除任何历史内容 |

---

## 5. 最终验收（判词 §七 的 10 项）

原始 stdout: `ece/reports/eval-archive/2026-09-20-cut040R2/FINAL_ACCEPTANCE/acceptance.txt`

| # | 检查 | 结果 |
|---|---|---|
| 1 | 完整 pytest | **353 passed / 3 skipped / 0 failed**，exit 0 |
| 2 | E1 | **98.5%**（64/65）PASS |
| 3 | E2 | **61/61，0 暴露 0 失败** PASS |
| 4 | E3 | exit 1，15.0%（数据集过期；重生成后 100%） |
| 5 | E4 | exit 0，100%（**vacuous**） |
| 6 | E5 | exit 1，0.0%（**真实失败**，已记录） |
| 7 | P1 experiment | F0 == F1 == F2；ARM A exit 2 / ARM B exit 0 |
| 8 | git diff | 仅 runner 契约 + 脚本 + 文档；**无架构改动** |
| 9 | 工作树污染 | 重名实体 **0**；pytest **幂等**（439→439）；r4-test 残留仅保留一对 |
| 10 | 文档一致性 | §2 清理后无已知冲突 |

> pytest 基线 **353P/3S/0F 未变化** —— 本轮代码改动**只涉及 runner**（未被 pytest 收集），
> 故测试结果无新增/变化。

---

## 6. Remaining Issues

| # | 问题 | 影响 | 处置 |
|---|---|---|---|
| **K1** | `/permissions/check` 的 `req.user_ref` 允许调用者指定授权主体 | Production 阻塞 | 已登记 `TASKS.md` 附录 J / **PG-1**（V0 允许 / Production 禁止） |
| **K2'** | **E3 数据集过期**（display_id 漂移） | E3 当前 15%，非逻辑失败 | **未修** —— 需裁定：重生成数据集？还是让 display_id 稳定？ |
| **K2''** | **E5 真实失败**（测试污染 + 时态过滤语义） | E5 当前 0% | **未修** —— 按判词 STOP 交裁定 |
| **K2'''** | **E4 vacuous pass** | 关系正确性未被真正验证 | 需裁定边界是否应收紧 |
| **K3** | ACL 模型无 `classification` 维度 | 若产品需要则须改模型 | 已在 `engine.py` 标注 |
| **K4** | `display_id` 跨 wipe+重播漂移且单调增长 | 以 display_id 为键的外部资产会静默过期 | **未修** —— 新发现，同族缺陷第 5 例 |

**K2 / K2' / K2'' / K4 均未扩大修复范围** —— 按判词要求记录后 STOP，交最终裁定。

---

## 7. 提交物

| 项 | 位置 |
|---|---|
| 修改后的代码 | `ECE_SOURCE/scripts/run_e{3,4,5}_*.py` |
| 修改后的文档 | `DOCS/`（MVP_SCOPE_V3 / ARCHITECTURE_DECISION_V3 / README / PRD_V3 / CODEX_ROUND2_FINDINGS） |
| git diff / stat | `ECE_DIFF/` |
| E3/E4/E5 原始 stdout | `RAW_STDOUT/R40R2.7/E{3,4,5}.txt` |
| 完整 pytest stdout | `RAW_STDOUT/FINAL_ACCEPTANCE/acceptance.txt` |
| E1 / E2 / P1 结果 | 同上 + `RAW_STDOUT/EXPERIMENT_RECORD.txt` |
| 最终 commit hash | ece `f3a6639` → 本轮追加；根仓 本轮追加 |

---

## 8. 状态

```
V3 架构          FREEZE （无变更）
Glean Research   STOP
Kernel Boundary  PASS
E2 Permission    PASS，可关闭
P1 单变量证据     PASS，可关闭
E1 Hermeticity   PASS，可关闭
Customer A       GO
C Technical Spike GO（工程验证：runner 已修；E3/E5 真实失败待裁定）
V4               禁止启动
```

**STOP** —— 未进入下一轮自主开发。等待最终独立审验（GO / NO-GO）。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
