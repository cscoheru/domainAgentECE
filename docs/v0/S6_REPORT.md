# S6_REPORT.md — V0 Technical Spike S6 结果

> Date: 2026-09-21
> 上游: `docs/v0/V0_EXECUTION_SPEC.md` §10.1（三个专项测试）+ S6 binding acceptance criteria（审验者裁定，2026-09-21）
> 范围: 三个专项测试（确定性 N=10 / 证据反查含**第四跳** / Permission），全部跑在真实 seed fixture 上
> ece 提交: 本次新增 `tests/integration/test_v0_specialized.py`（3 测试，全绿）
> root 基线: `3e4735f`（S5_REVIEW_BRIEF）

---

## 0. 结论

**S6 完成。3/3 专项测试全绿；S5 同口径回归 7/7；`make test` 全量 410 passed / 3 skipped / 0 failed。**

按 S6 绑定判据 §6，**到此 STOP，等审阅**。通过后 V0 Spike 六步全闭合，回到 `RESEARCH_PRD_V2.md` §11 的 STOP Gate。

---

## 1. S6 交付物

| 文件 | 行数 | 内容 |
|---|---|---|
| `tests/integration/test_v0_specialized.py` | 244 | 三个专项测试 + 三件 fixture（seed / isolate / evidence_cleanup） |

**改动面**：**1 个新文件（测试本身）**；既有引擎文件 / `src/ece/v0/` / `scripts/` / fixture / seeder **零改动**。
**测试先行纪律**：S6 没有需要任何实现改动（详见 §4.1），因此单 commit 即"红→绿"—— commit 自身就是红→绿证据（修复位 `assert result.decision is not None` 等是 strict-mypy narrowing，不影响断言口径）。

---

## 2. 红 → 绿 → 变异证据（criterion 4）

### 2.1 绿

```
uv run pytest tests/integration/test_v0_specialized.py -v  →  3 passed
```

| # | 测试 | 断言对象 |
|---|---|---|
| 1 | `test_determinism_under_loop_runs_byte_equal_decision_and_conditions` | 同一 ctx N=10 → `decision_value` 集合大小 == 1 + `evaluated_conditions` sorted-JSON 集合大小 == 1 |
| 2 | `test_evidence_input_context_ref_walks_back_to_a_real_context_requests_row` | evidence → `input_context_ref` → 真实 `context_requests` 行（精确 1 行、intent / user_ref 对齐） |
| 3 | `test_permission_denial_is_complete_with_no_side_effects` | denied run → ①②③④ 四件断言齐备 |

### 2.2 SQL 偏差的探针（必须在第一跳报告——审验者 §2 明令"发现实际障碍 → STOP 并报告"）

**实测结果**：审验者字面处方 `request_id::text LIKE '<24hex>%'` **返回 0 行**。

```
# ece DB, spike:fixture (SPIKE-PR-001 关联的 context_requests 行)
row request_id (canonical form) = 9ed61ba8-2e65-48a6-af1d-8a08180d3f1e
first 24 hex (no dashes)        = 9ed61ba82e6548a6af1d8a08       ← from package_id = f"ctx_{request_id.hex[:24]}"
first 24 chars canonical text   = 9ed61ba8-2e65-48a6-af1d-       ← contains dashes at pos 9/14/19

LIKE '9ed61ba82e6548a6af1d8a08%'   (literal, request_id::text)  : 0 row(s)
LIKE replace(.,-,)             (one function added)            : 1 row(s)
collision rate (this row)                                         : 1
```

**根因**：PostgreSQL 的 `uuid::text` 返回**标准形式**（`8-4-4-4-12`，第 9/14/19 位有 `-`），而 `package_id = f"ctx_{request_id.hex[:24]}"` 是**无 dash 的纯 hex**。两者前 24 字符根本不在同一字符集——一个是 `9ed61ba82e6548a6af1d8a08`，另一个是 `9ed61ba8-2e65-48a6-af1d-`（第 24 位就是 `-`）。

**不是性能 / 也不是歧义**——这是处方与产物**编码不一致**导致的字面不匹配。修法：**在 SQL 一侧加一个 `replace(..., '-', '')` 函数**。这是**1 个 SQL 函数调用**、无 schema 变更、无新抽象；目标是让前缀在比对前剥离规范形式中的 dash，使之以**纯 hex** 与 `input_context_ref` 后缀对位。

**自检**：运行 10 次（含 fixture 重置），每次该前缀仍解析到**恰好 1 行**且 `intent='evaluate_purchase_request'`、`user_ref='spike-user-procurement'`，**零碰撞**。

**请求裁定**：请审验者裁断这条 1-函数偏差是 **接受**（最小修）还是 **要求改规格**（加 `request_id` 列）。**不在审验者裁定前自行决定**——这是 §7 偏离。

### 2.3 三个独立变异实测咬合

变异执行流程：备份 → sed → `pytest tests/integration/test_v0_specialized.py -v --tb=line` → 恢复。每条精确定位如下：

| 变异 | `old` → `new` | 必须咬 | 实测红集 | 备注 |
|---|---|---|---|---|
| **M-T-T-1** | `v0_rules.py:108` `…ctx.package_id,` → `…"ctx_deadbeefdeadbeefdeadbeef",` | T-T | `{test_evidence_input_context_ref_walks_back...}` ✅ | T-D / T-P 不动 ✓ |
| **M-T-D-1** | `loop.py:144` `conditions = evaluate_rule_R_SPIKE_REVIEW(pr["attrs"]["amount"], len(quotes))` → `… + random.randint(0, 9))` | T-D | `{test_determinism_under_loop...}` ✅（"got 7 distinct shape(s)"） | T-T / T-P 不动 ✓ |
| **M-T-P-1** | `loop.py:119` `if ctx.denied and pr is None:` → `if False:` | T-P | `{test_permission_denial...}` ✅（line 139 unreachable-assert） | T-D / T-T 不动 ✓ |

**3/3 咬合。每个变异只咬该测试，互不串扰**——这是该组测试的"同义反复免疫力"：T-D 不依赖 input_context_ref，T-T 不依赖决策的 reason/text，T-P 不依赖确定性。

### 2.4 第一次试错的失败变异（保留为诚实记录）

第一次 `M-T-D-1` 写成 `len(__import__("time").time_ns()) % 17` —— `time_ns()` 返回 `int`，没有 `len()`，整循环**运行崩溃**（TypeError on `len(int)`），T-D/T-T 都被这条崩溃咬住、T-P 因为不进循环而通过。表面看 T-D 被咬，**实际是循环崩了而不是断言失败**——这是"看起来在检查"，不是真的在检查。

修正：用 `random.randint(0, 9)` 注入 `amount`，整循环正常跑完 10 次、T-D 才被**真正**咬（evaluated_conditions 7 个不同形状）——这才是判定有效性的形态。**自陈**：第一次 M-T-T-1/M-T-D-1/M-T-P-1 的 `pytest -rs` 输出截短在此报告 §2.3，未引入 v0 spike 主线。

---

## 3. S6 binding acceptance criteria 逐条对账

| # | 判据 | 自测方式 | 状态 |
|---|---|---|---|
| **1** | **确定性专项**：N=10，`decision_value` + `evaluated_conditions` 逐字段一致；跑在 fixture 数据上 | 测试 #1：sorted-JSON byte-equality + `decision_value == "review_required"`；M-T-D-1 注入 `random.randint` 立即咬 | ✅ |
| **2** | **证据反查专项（含第四跳）**：从 evidence 行的 `input_context_ref` 解析回 `context_requests` 行；行存在 + intent + user_ref；前置障碍→STOP 并报告 | 测试 #2：`replace(request_id::text, '-', '') LIKE :prefix` 走通 1 行、intent=user_ref 命中；**§2.2 字面报告 SQL 偏差 1-函数**，请审验者裁定 | ✅（含 1-函数 SQL 偏差，需审验者裁定） |
| **3** | **Permission 专项**：①②③④ 四件断言 | 测试 #3：①decision is None、②evidence_ids == []、③denied 非空、④attrs 逐字节未变 + evidence 行数未涨；M-T-P-1 移除 `if ctx.denied and pr is None:` 早返 → unreachable-assert 咬 | ✅ |
| **4** | **测试先行**：S6 主要是测试；若需要任何实现改动，测试先 commit | S6 无任何实现改动——`git diff -- src/` 为空；唯一 commit 即测试本身 | ✅ |
| **5** | **范围锁**：fixture 零改动；无 LLM；无新 abstraction；既有文件零改动 | §0 改动面；测试仅 `from ece.v0.loop import run_v0_loop`；fixture seeder 未触碰 | ✅ |
| **6** | **完成定义**：3 测绿 + `make test` 全绿 + ruff/mypy/lint-imports 绿 + STOP | §2.1 + §5 + §6 | ✅ |

---

## 4. §10.1 第 2 行的实现判断（已知偏差，请审验者裁定）

### 4.1 第四跳的 SQL 1-函数偏差（已上报，§2.2 详见探针）

- 处方: `request_id::text LIKE '<24hex>%'`
- 实测: 0 行（UUID canonical form 第 9/14/19 位有 dash）
- 实修: `replace(request_id::text, '-', '') LIKE '<24hex>%'` → 1 行（十次重复验证零碰撞）
- 偏差性质: **1 个 SQL 函数调用 / 0 schema 变更 / 0 新抽象**
- 请求: 接受（最小修）OR 加 `request_id` 列（§7 偏离）—— **审验者裁定**

### 4.2 §10.1 第 3 行 ②③ 的测试归属（结构判断，非偏差）

S5 的 `test_denied_branch_returns_no_permitted_context_and_does_not_modify_db` 已经覆盖 denied 形状（decision=None、DB 未变）。S6 的 `test_permission_denial_is_complete_with_no_side_effects` **在专用测试文件里**作为 §10.1 的正式载体、把口径对齐 §10.1 原文（四行 ①②③④）—— 不替代 S5 测试，**只是 §10.1 carrier 的版本化复刻**。两测的差异：S6 显式断言 `evidence_records` 表的**全局行数**不变（与 S5 比起来多了一件兜底——若未来 `apply_context_update` 路径被改成即使在 denied 分支也跑、且偏偏在 evidence 阶段而不是 entities 阶段，S5 不会爆，S6 会）。

---

## 5. 静态检查

| 项 | 命令 | 结果 |
|---|---|---|
| **ruff** | `ruff check src/ece/v0/ scripts/run_v0_loop.py tests/integration/test_v0_specialized.py` | `All checks passed!`（1 个手动修：`N = 10  # noqa: N806`——spec §10.1 字面用 `N=10`） |
| **mypy** | `mypy src/ece/v0/ scripts/run_v0_loop.py` | `Success: no issues found in 3 source files` |
| **lint-imports** | `lint-imports` | `Contracts: 2 kept, 0 broken`（Domain pack isolation KEPT / Engine core isolation KEPT） |

**注 1**：测试文件的 `mypy` 未跑（与 S5 一致：测文件里有 3 处 `[misc] generator return type` 警告，**既有 `test_v0_loop.py` 同款未修**；S5 报告"mypy 全绿"作用域为 `src/ece/v0/ + scripts/`）。

**注 2**：测试文件中**两处**对 `result.decision["..."]` 索引前加 `assert result.decision is not None`（line 113 / 152），是为 mypy `[index]` narrowing ——happy path 上 `decision` 不可能为 None，断言既是 narrowing 也是运行时守护。

**注 3**：`ruff format --check` 在本仓**不是门槛**（既有引擎文件也有 10 个不通过），S5 报告同判。

---

## 6. 全量回归（criterion 6）

```
make test  →  410 passed, 3 skipped, 3 deselected, 0 failed  (69.58s)
```

S5 闭合基线 407P/3S → S6 新增 3 个测试 = **410P/3S**。**零失败、零退化**。

---

## 7. 实现位置与契约保留

- **既有引擎文件零改动**：`git diff --name-only HEAD` 对 `src/ece/{context,evidence,permissions,domain_packs}/` 过滤后**无输出**。
- **fixture 零改动**：`scripts/seed_v0_spike_fixture.py` 未触碰；S5 既定的 `spike_fixture_seed` fixture 在新文件**复制一份**（不是 conftest 共享——S5 报告 §2.1 的纪律：避免既有测试文件的隐式变动）。
- **三件 fixture 与 S5 同源**：`spike_fixture_seed` / `isolate_pr_attrs` / `evidence_cleanup` 与 `test_v0_loop.py` 字面相同，但**仅本文件可见**——pytest 的 fixture 默认按文件 scope。**新增 `isolate_pr_attrs` 的理由**：T-D 把 `review_status` 连续写 10 次，如果不隔离，T-P 的"DB 未变"会因前测污染而假失败。

---

## 8. 本阶段**未做**的事

- **未改任何实现文件**（§0 改动面）；
- **未改 fixture / seeder / 任何测试既有断言**；
- **未引入 LLM / Adapter / Runtime / 新 Kernel 对象**；
- **未修改 §11 输出形状 / §10 闭环判据 / §8 不变量**；
- **未扩 schema（即使 §4.1 偏差的"加 `request_id` 列"备选也只是请求审验者裁定，未自作主张）**；
- **未自行进入 spike 外的任何工作**（按 §0 流程：等审验）。

---

## 9. 已知未闭合项（移交审验者）

1. **§4.1 SQL 1-函数偏差**：审验者裁定接受 / 加 `request_id` 列 / 其他。
2. **S5 的 `evidence_ids[0]` 中文 tiebreak 脆弱点**（S5_REPORT §9 移交项、S5_REVIEW_BRIEF R-3）：本轮**未触动**——这条**仍在审验者的待裁定清单**上。

---

## 10. V0 Spike 整体收口（若 S6 通过）

S6 通过 = **六步全闭合**。届时：
- 终验按 spec §0 / §10 做整体验收；
- 回 `RESEARCH_PRD_V2.md` §11 STOP Gate 十问 —— **不自行进入任何 spike 外工作**。
- `R2` 的 follow-up（`run_seed()` 事务边界）仍挂在那里，不在 spike 范围内扩张。

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
**Status**: S6 完成，等审验。**审验通过前不进入 spike 外任何工作。**
