# S5_REPORT.md — V0 Technical Spike S5 结果

> Date: 2026-09-21
> 上游: `docs/v0/V0_EXECUTION_SPEC.md` §9（六步调用关系）· §10（逐步验证）· §11（端到端输出形状）
> 审验者（Gemini）给出的 S5 binding acceptance criteria（8 条，本报告逐条对账）
> 范围: `run_v0_loop` —— 六步编排 + 逐步断言 + §11 输出
> ece 提交: `7581eb1`（红，4 测试）→ `67ad0e6`（红，7 测试最终形态）→ `a78e91a`（实现，转绿）
> root 基线: `745e1ce`

---

## 0. 结论

**S5 完成。8 条 binding acceptance criteria 全部实测通过。**

按"每完成一个 S 就回来验一次"的节奏，**到此 STOP，等审阅**。通过后进 S6（三个专项测试）。

---

## 1. S5 交付物

| 文件 | 行数 | 内容 |
|---|---|---|
| `src/ece/v0/loop.py` | 276 | `V0LoopResult` + `run_v0_loop`（六步编排 + 闭环判据） |
| `src/ece/v0/__init__.py` | 11 | 公共 API 再导出 |
| `scripts/run_v0_loop.py` | 226 | §11 输出 + §10 逐步断言（CLI 入口） |
| `tests/integration/test_v0_loop.py` | 313 | 7 个测试（红 commit `7581eb1` + 3 个补充） |

**改动面**：2 个新路径（`src/ece/v0/`、`scripts/run_v0_loop.py`）+ 1 个测试文件（其本身是 S5 新增，`7581eb1` 引入）。
**既有引擎文件零改动** —— `git diff --name-only HEAD` 对 `.` 过滤后无输出。

---

## 2. 红 → 绿 → 变异证据（criterion 6）

### 2.1 红（实测复现，不是自述）

提交顺序是 **测试先、实现后**：`7581eb1`（4 测试）→ `67ad0e6`（7 测试，最终形态）→ `a78e91a`（实现）。
**两处红都实测复现**（把实现目录移开、checkout 该 commit 的文件）：

```console
$ git checkout 7581eb1 -- tests/integration/test_v0_loop.py
$ mv src/ece/v0 /tmp/ece_v0_aside
$ uv run pytest tests/integration/test_v0_loop.py -q ; echo $?
E   ModuleNotFoundError: No module named 'ece.v0'
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!
2
```

最终形态的 7 个测试同样复现（`67ad0e6` 之后、`a78e91a` 之前）：

```console
$ mv src/ece/v0 /tmp/ece_v0_aside2
$ uv run pytest tests/integration/test_v0_loop.py -q ; echo $?
E   ModuleNotFoundError: No module named 'ece.v0'
2
```

### 2.2 绿

```
uv run pytest tests/integration/test_v0_loop.py -q  →  7 passed
```

### 2.3 过程偏差自陈（criterion 6 的诚实边界）

红 commit 的测试文件是 **4 个测试**；最终文件是 **7 个**（`git diff 7581eb1` = +129/−17）。差异两部分：

1. **4 个原测试的 fixture 加固**（+17/−17 量级）：`isolate_pr_attrs` autouse fixture —— 不加的话 `happy_path` 写回的 `review_status='review_required'` 会泄漏到 `denied` 测试，使其"DB 未被修改"的断言假失败。
2. **3 个新测试**（+129 行）：见 §2.4 清单 —— 它们针对**已存在**的实现行为，因此**不是测试先行**。

**处置**：不声称这 3 个测试符合 criterion 6 的"测试先行"字面要求；它们的有效性由 §2.5 的变异证明，而不是由"我先写了测试"证明。这一点请审验者按其独立变异复核（裁定 §4 已明确"每轮审验继续做独立变异而非采信自报"）。

### 2.4 测试清单（7 个）

| # | 测试 | 断言对象 |
|---|---|---|
| 1 | `test_happy_path_runs_all_six_steps_and_re_read_matches_decision` | 六步串联 + §8 不变量 + `review_evidence_id` 是排序第一条 |
| 2 | `test_denied_branch_returns_no_permitted_context_and_does_not_modify_db` | denied → `decision=None`、reason、DB 逐字节未变 |
| 3 | `test_auto_approved_path_also_propagates_decision_value_through` | decision_value 透传（S4 条件 F 的循环层回归） |
| 4 | `test_loop_module_does_not_route_decision_through_an_llm` | 源文禁词 |
| 5 | **`test_re_read_asks_the_assembly_path_again`** | 重读是**第二次 `assemble_context`**（计数 2 次且参数相同） |
| 6 | **`test_loop_result_carries_every_step_product`** | `V0LoopResult` 六步产物齐备（§10 闭环行） |
| 7 | **`test_runner_script_imports_the_loop_rather_than_reimplementing_it`** | runner 是 thin wrapper（R2 教训的结构性守卫） |

### 2.5 5 个变异实测咬合

变异由一次性 harness 执行（改源码 → 跑 `pytest tests/integration/test_v0_loop.py -q` →
记录 `FAILED` 行 → 还原；harness 是临时文件、不入库）。**每条的精确改动如下，可手工复现**
（锚点在 `src/ece/v0/loop.py` 中各出现恰好一次）：

| 变异 | `old` → `new` | 必须咬 | 实测红集 |
|---|---|---|---|
| **M-α** | `…dec, evidence_ids[0])` → `…dec, evidence_ids[-1])` | happy_path | `{happy_path}` ✅ |
| **M-β** | `…pr["attrs"]["amount"], len(quotes))` → `…, len(quotes) + 3)` | happy_path | `{happy_path, auto_approved, carries_every_step, re_read_asks}` ✅ |
| **M-γ** | `    if ctx.denied and pr is None:` → `    if False:` | denied | `{denied}` ✅ |
| **M-δ** | `    re_read_attrs = _re_read_through_assembly(engine, user_ref, display_id)` → `    re_read_attrs = dict(pr_attrs_before)` | re_read_asks | `{happy_path, auto_approved, carries_every_step, re_read_asks}` ✅ |
| **M-ε** | `    if re_read_attrs.get(DECISION_KEY) != dec["decision_value"]:` → `… != "review_required":` | auto_approved | `{auto_approved}` ✅ |

**5/5 咬合。**

> **M-δ 是关键变异**：它模拟的正是"我写了，然后我读我自己写的快照"——一个从不回到 Context 的假闭环。它被 4 个测试同时咬住，其中 `re_read_asks` 是**专门为它写的**：它数 `assemble_context` 的调用次数，所以哪怕返回值"碰巧对"也会红。
> **M-ε 是 S4 条件 F 的同型复发检查**：把判据换成字面量后，只有 `auto_approved` 测试咬 —— 证明"用 `decision_value` 而非硬编码"这件事仍然只由一个测试守着，这正是它的职责。

---

## 3. 8 条 binding acceptance criteria 逐条对账

| # | 判据 | 自测方式 | 状态 |
|---|---|---|---|
| **1** | 六步串联 + denied 不进 [3] | `loop.py:107-156`；测试 #1/#2；M-γ 证明 denied 分支承重 | ✅ |
| **2** | 重读闭环走 `assemble_context`；`V0LoopResult` 全字段齐备 | `_re_read_through_assembly`（第二次真 `assemble_context`）+ 测试 #5 计数；`_assert_loop_closed` 断言 §8 不变量；测试 #6 逐字段对 §10 | ✅ |
| **3** | §11 输出形状六段 | §4 逐项对账（含 3 处**已裁定过的**文案/取值差异） | ✅ |
| **4** | 寻址纪律：`source_id` 寻址、`display_id` 运行时解析、禁硬编码 `PR4xx` | `_resolve_display_id`；源文无 `PR4` 字面量；测试 #7 禁 runner 直接摸引擎层 | ✅ |
| **5** | 先决条件：M-F 补测作为独立 commit 先行闭合 | `7df2245`（S4 闭合，先于 `7581eb1`） | ✅ |
| **6** | 测试先行 + ≥3 变异 | 见 §2 —— commit 顺序是测试(`67ad0e6`)先于实现(`a78e91a`)，两处红均实测复现；**3 个补充测试是在实现已存在的工作区里写的，非先行，已自陈**；5 个变异全咬 | ✅（含偏差自陈） |
| **7** | 纯边界：无 LLM / 无新 abstraction / 规则仍纯 / 既有文件零改动 | 测试 #4；`run_v0_loop` 仅 import 六步函数；既有引擎文件 `git diff` 为空 | ✅ |
| **8** | 完成定义 | §5（ruff/mypy/lint-imports）+ §6（`make test`）+ STOP | ✅ |

---

## 4. §11 输出形状对账（criterion 3）

实测输出（`uv run python scripts/run_v0_loop.py`，退出码 0）：

```
INPUT
  user_ref = spike-user-procurement
  root     = SPIKE-PR-001

[1] CONTEXT
  package_id = ctx_442d2912e7f14aabb4fe14a7
  counts     = {entities: 1, relationships: 1}

[2] ENTITY / KNOWLEDGE
  pr.ref          = SPIKE-PR-001   (由 source_id SPIKE-PR-001 运行时解析)
  pr.attrs.amount = 1280000
  quotes          = [SPIKE-SUP-A]    → len = 1
  knowledge       = 1 条 SELECTS 关系 + sources[]

[3] RULE  R-SPIKE-REVIEW
  amount_gte_threshold   : amount >= 1000000  (actual=1280000) → passed=true
  quote_count_lt_required: quote_count < 3  (actual=1) → passed=true

[4] DECISION
  decision_id    = dec_f8da7240-96ef-483a-92e1-e1f9dd96b9a4
  decision_key   = 'review_status'
  decision_value = 'review_required'
  reason         = '金额 1,280,000 ≥ 1,000,000 且仅 1 家报价（需 3 家）→ 需人工复核'

[5] EVIDENCE
  ev_1  claim='报价家数 1 < 3'
        source={spike:v0-technical-fixture, SPIKE-PR-001}  observed=1 threshold=3
        input_context_ref=ctx_442d2912e7f14aabb4fe14a7  ts=2026-09-21 10:26:43.940074+00:00
  ev_2  claim='金额 1,280,000 ≥ 1,000,000'
        source={spike:v0-technical-fixture, SPIKE-PR-001}  observed=1280000 threshold=1000000
        input_context_ref=ctx_442d2912e7f14aabb4fe14a7  ts=2026-09-21 10:26:43.940074+00:00

[6] CONTEXT UPDATE
  SPIKE-PR-001.attrs.review_status : 'pending' → 'review_required'
  + review_decision_id = 'dec_f8da7240-96ef-483a-92e1-e1f9dd96b9a4'
  + review_evidence_id = 'ev_df726a82-2c22-4c2d-869d-15ba00b3336a'
  + review_updated_at = '2026-09-21T10:26:43.947609+00:00'

RE-READ
  assemble_context(...).entities[...].attrs.review_status == 'review_required'   ✅

=== §10 per-step checks ===
  all checks passed

*** PASS: six steps chained, loop closed back onto Context ***
```

### 4.1 与 §11 逐项对应的 3 处差异（都是**已知且已裁定**的，不是本轮新引入）

| # | §11 写 | 实测 | 说明 |
|---|---|---|---|
| **D-1** | `reason = "…（100万阈值）且…"` | `'金额 1,280,000 ≥ 1,000,000 且仅 1 家报价（需 3 家）→ 需人工复核'` | S3 已裁定。§11 的 `reason` 是**示意散文**，契约是"`reason` 是条件的纯函数"（`_build_reason` 三分支、无时间戳/uuid），S3 的确定性测试守住的是后者。S3 审验已 PASS，本轮**不改 S3 实现去迎合 §11 文案**。 |
| **D-2** | `ev_1` = 金额、`ev_2` = 报价家数 | `ev_1` = 报价家数、`ev_2` = 金额 | S2 已裁定。排序契约是 `ORDER BY evidence_timestamp, claim`；两行 `evidence_timestamp` 相同（单次 `persist_evidence` 调用内同一 `datetime.now(UTC)`），故按 `claim` 排序，`报`(U+62A5) < `金`(U+91D1)。§11 的 `ev_1`/`ev_2` 标签是**示意编号**，不是顺序契约。 |
| **D-3** | `pr.ref = PR4xx` | `SPIKE-PR-001` | 既有设计。seeder 给 fixture 实体**显式** `display_id`（= `source_id`），使其永不触碰共享数字命名空间 `PR###`（`seed_v0_spike_fixture.py` 注释 + cut-040R-2 S1 发现）。§11 的 `PR4xx` 是示意。 |

**这三处我刻意不改实现去迎合文档**（Codex 的 S1 裁定明文禁止"修改业务规则/评估标准以适应修复"）。若审验者认为 §11 应升级为字面契约，那是改**规格**的决策，请明示。

### 4.2 关于"六步是否都真的发生"的一个额外守卫

`_assert_loop_closed` 除了断言 §8 的不变量（`re_read.review_status == dec.decision_value`），还**独立读一次原始行**并逐键比对四个 `review_*`：

- 来源 A = 装配路径（调用方会看到的）
- 来源 B = 原始 `SELECT`（表里存的）

两者由不同代码产生，**一致是证据，不一致是 bug** —— 任一情况都不是自证。若未来装配路径引入缓存/归一化把二者拉开，这里会先炸。

---

## 5. 静态检查

| 项 | 结果 |
|---|---|
| **ruff** | `All checks passed!`（1 个自动修：`scripts/run_v0_loop.py` 未用的 `typing.Any`） |
| **mypy** | `Success: no issues found in 3 source files` |
| **lint-imports** | `Contracts: 2 kept, 0 broken`（Domain pack isolation KEPT / Engine core isolation KEPT） |

**注**：`ruff format --check` 在本仓**不是门槛** —— 既有引擎文件（`src/ece/context/`、`src/ece/evidence/`）有 10 个文件也不通过它。故本轮未执行格式化，避免制造大面积无关 diff。

---

## 6. 全量回归（criterion 8）

```
make test  →  407 passed, 3 skipped, 3 deselected, 0 failed  (74.90s)
```

S4 闭合基线 400 passed → S5 新增 7 个测试 = 407。**零失败、零退化。**

---

## 7. 两处需要审验者注意的实现判断

### 7.1 实现放在 `src/ece/v0/loop.py`，`scripts/run_v0_loop.py` 是 CLI

§9 的签名行写的是 `scripts/run_v0_loop.py :: run_v0_loop(...)`。我把实现放进**包内**，脚本 import 它：

- 测试需要 `from ece.v0 import run_v0_loop` —— 脚本不是可导入包；
- R2 的教训是**一份实现**（`seed_relationships.py` 从"三份互相不一致的副本"降级为 thin wrapper）；
- `scripts/` 下既有 runner（`run_e3_context.py` 等）也全部是"薄入口 + 包内实现"。

测试 #7 用静态检查守住这条：runner **只准** import `ece.v0`，不准触碰 `ece.context.assembly` / `ece.evidence` / `ece.domain_packs` —— 否则它就能漂移成第二份实现。**如果审验者认为函数必须字面住在脚本里，请明示**，但那样会丢掉可测性。

### 7.2 `_resolve_source_refs` 是新增的展示层 helper

§11 要求把供应商印成源身份（`SUP-SPIKE-A`），而 Context 的关系形状只带 `display_id`（`assembly.py` 步骤 5）。`_resolve_source_refs` 是 `_resolve_display_id` 的**逆映射**，只为让 §11 可逐项打印。它不是 abstraction、不进 `ece/context/`、不改变任何语义 —— 若审验者认为不必要，可以删（代价是 §11 的 `[2]` 行只能印 display_id）。

---

## 8. 本阶段**未做**的事

- 未跑三个专项测试（S6：确定性 / 证据反查含**第四跳** / Permission）
- 未引入任何 LLM / Adapter / Runtime / 新 Kernel 对象
- 未改动既有引擎文件（`git diff` 为空）
- 未改 S2/S3/S4 的实现或测试
- 未为了迎合 §11 文案而改规则或 Decision 实现

---

## 9. 已知未闭合项（移交 S6，不自行扩张）

- **证据反查第四跳**：`decision → evidence → source → input_context_ref → 原始 Context`。前四跳在 S2 已可查；第四跳（`input_context_ref` → 原始 Context 行）目前只能是**前缀匹配** —— `package_id = f"ctx_{request_id.hex[:24]}"` 派生自 `request_id`，而 `context_requests` 无 `package_id` 列。S5 的脚本与测试只做了**取值往返相等**，未真的查回原 Context。按 S4 裁定，这一跳**留给 S6**。
- 脚本每次运行会**真实写入** evidence 行与 `entities.attributes`（这是循环的本意，非缺陷）；它不做清理。`review_status` 由 seeder 的幂等重播复位。

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
**Status**: S5 完成，等审验。**审验通过前不进入 S6。**
