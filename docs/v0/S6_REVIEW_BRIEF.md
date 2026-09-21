# S6_REVIEW_BRIEF.md — 审验导航（三个专项测试）

> Date: 2026-09-21
> 审验对象: S6 = spec §10.1 三个专项测试（确定性 N=10 / 证据反查含**第四跳** / Permission）
> 交付报告: `docs/v0/S6_REPORT.md`
> **本文件只做导航：告诉你审什么、怎么复现、哪些断言最值得攻击。判定请你自己下，不要采信报告的自述。**

---

## 1. 仓库与提交

| 仓库 | 路径 | 本次提交（待） |
|---|---|---|
| ECE 代码仓 | `ece/` | 单 commit：`tests/integration/test_v0_specialized.py`（3 测试，全绿） |
| 治理/文档仓 | 根目录 | `S6_REPORT.md` |

**改动面只有 1 个新文件**——既有引擎文件 / `src/ece/v0/` / `scripts/` / fixture / seeder **零改动**（§0 改动面 + §7 实现位置）。

---

## 2. 本次审验的路径地图

```
ece/tests/integration/test_v0_specialized.py    244 行  ← S6 唯一交付物
├── fixtures (3)
│   ├── spike_fixture_seed (module)            ← 与 test_v0_loop.py 字面相同
│   ├── isolate_pr_attrs (autouse)             ← 与 test_v0_loop.py 字面相同
│   └── evidence_cleanup                       ← 与 test_v0_loop.py 字面相同
├── helper (1)
│   └── _read_pr_attrs_direct
└── tests (3)
    ├── test_determinism_under_loop_runs_byte_equal_decision_and_conditions  (T-D)
    ├── test_evidence_input_context_ref_walks_back_to_a_real_context_requests_row  (T-T)
    └── test_permission_denial_is_complete_with_no_side_effects  (T-P)
```

被测对象（**未改**，但测试直接调）：

```
ece/src/ece/v0/loop.py                   ← run_v0_loop（步骤 [1]–[6] 编排 + §8 不变量）
ece/src/ece/domain_packs/procurement/agent/v0_rules.py  ← evaluate_rule_R_SPIKE_REVIEW + build_decision
ece/src/ece/context/assembly.py          ← assemble_context（S1 验过的）
ece/src/ece/context/update.py            ← apply_context_update（S4 验过的）
ece/src/ece/evidence/store.py            ← persist_evidence（S2 验过的）
```

规格（**冻结**，不是本轮审验对象）：

```
docs/v0/V0_EXECUTION_SPEC.md  §10.1 (the three specialized tests)
docs/v0/S5_REPORT.md  §9 (the only cross-boundary known item: evidence_ids[0] tiebreak)
```

---

## 3. 复现命令（请自己跑，不要读报告里的数字）

```bash
cd ece

# 1) 目标测试
uv run pytest tests/integration/test_v0_specialized.py -v

# 2) 第四跳偏差的探针（§4.1 必读——这次有 1-函数 SQL 偏差需要你裁定）
uv run python - <<'PY'
import uuid
from sqlalchemy import text
from ece.db import get_engine
with get_engine().connect() as c:
    rows = c.execute(text(
        "SELECT request_id::text AS r FROM context_requests ORDER BY requested_at DESC LIMIT 1"
    )).all()
rid = rows[0].r
prefix_hex = rid.replace("-", "")[:24]
prefix_canon24 = rid[:24]
print(f"rid             = {rid}")
print(f"first 24 hex    = {prefix_hex}")
print(f"first 24 chars  = {prefix_canon24!r}  (note the dashes)")
hits_literal = c.execute(text(
    "SELECT count(*) FROM context_requests WHERE request_id::text LIKE :p"
), {"p": prefix_hex + "%"}).scalar()
hits_replace = c.execute(text(
    "SELECT count(*) FROM context_requests WHERE replace(request_id::text, '-', '') LIKE :p"
), {"p": prefix_hex + "%"}).scalar()
print(f"LIKE literal    : {hits_literal} row(s)")
print(f"LIKE replace(.) : {hits_replace} row(s)")
PY

# 3) 全量回归
make test

# 4) 静态
uv run ruff check src/ece/v0/ scripts/run_v0_loop.py tests/integration/test_v0_specialized.py
uv run mypy src/ece/v0/ scripts/run_v0_loop.py
uv run lint-imports
```

---

## 4. 审验重点：**4 个最值得攻击的断言**

### R-1 「SQL 1-函数偏差是否是最小修」（**这一轮最重要**，请优先打）

报告 §2.2 / §4.1 已经把这条偏差主动报上来了。**攻击点**：
- 我说"UUID canonical form 第 9/14/19 位有 dash，导致字面前缀匹配返回 0 行"——这是真的吗？第 24 位到底是 hex 还是 dash？前缀长度 24 是否真的覆盖到第一段 dash 后面的内容？
- `replace(..., '-', '')` 这 1 个函数，**有无副作用**？例如：会不会让两条 `request_id` 因去 dash 后碰撞？（实测 10 次重复，零碰撞，但 10 次样本不够 → 你能不能想到一条测试覆盖？）
- 比 1-函数更小的修？比如只把 `replace(request_id::text, '-', '')` 换成 `LEFT(...)` 等等。
- 是否应改成 §7 偏离的"加 `request_id` 列"以避免 LIKE 前缀扫描？

→ 这是本轮**唯一可能"实际有更好的解"**的地方。其余 R-2 / R-3 / R-4 都是结构判断。

### R-2 「T-D 的 byte-equality 是否真的咬得到非纯函数」（避免 §2.4 的失败变异同型）

报告自陈：第一次 `M-T-D-1` 写崩了循环、看起来"咬住了"但其实是 `TypeError`，不是断言失败。第二次换成 `random.randint(0, 9)` 才**真正**咬到断言。
**攻击点**：报告给的 `M-T-D-1` 是否足够刁？比如：
- 在 `evaluate_rule_R_SPIKE_REVIEW` 内部（非 `loop.py`）注入 `datetime.now()` → `reason` 不变（`reason` 是 booleans 的纯函数），但 `evaluated_conditions` 也不变（`actual` 是输入的纯函数）。**这种变异不会被咬**——因为规则本身是纯的。
- 把 `decision_id` 写入 `evaluated_conditions` 数组的某个嵌套字段？这种"半深"变异会不会溜过去？

→ 建议：你**亲自**做一次非纯变异。如果有没咬住的，说明 `evaluated_conditions` 的断言位置不够深。

### R-3 「T-P 的 `entities.attributes` 逐字节未变 + `evidence_records` 表行数未涨」是否够硬

报告 §4.2 提到：S5 的 denied 测试覆盖了"DB 未变"，但**没断言 evidence_records 表行数**（只在 evidence_cleanup 里删自己的）。T-P 显式断言了**全局**行数未变。
**攻击点**：
- 在 `loop.py` 的 `apply_context_update` 调用前**插入一行 evidence 写入**（即使 denied 分支），只让 `entities.attributes` 不变 → `attrs_after == attrs_before` 通过，但 `ev_after > ev_before` 让 T-P 咬。
- 这种"半污染"现实吗？`apply_context_update` 怎么会跑到 evidence？答：现在不会；但**如果未来有人在循环里加一步副作用**，T-P 必须能抓。

→ 跑一次这种变异。如果没咬住，说明我的"全局 evidence 行数"断言位置比"未触到 apply_context_update"还弱。

### R-4 「T-T 的 `intent = 'evaluate_purchase_request'` + `user_ref = 'spike-user-procurement'` 是循环自己写的」**吗？

循环在 `assemble_context(...)` 时把 `user_ref=user_ref` 和 `intent="evaluate_purchase_request"` 写进去；evidence 写入时再读回来塞进 evidence row。**这等于循环写什么就读什么**——任何 invariant 都不会破。
**攻击点**：
- 改 `assemble_context` 让它写一个错误的 intent（"evaluate_something_else"），循环不会知道 → T-T 仍通过（因为 evidence.input_context_ref 解析回的行确实有错的 intent——但 T-T 断言的是 intent == spec 值，所以 T-T 会爆）。✓
- 改 `persist_evidence` 让它写 `actor_user_ref="spike-user-evil"` 替换原始 user_ref → 循环不会知道 → T-T 仍通过（因为 T-T 查的是 `context_requests.user_ref`、不是 `evidence_records.actor_user_ref`）—— **这种变异不被咬**。

→ 后一种变异没咬住。是不是该把 `actor_user_ref` 也断言上？我没做（**自陈**：把"行存在 + intent + user_ref"作为最小判据已经覆盖了"可查"的本质；actor_user_ref 是 evidence row 的字段，不是 context_requests 的字段，不属于"反查链"的范围）。**这是判定题，不是 bug 题**。

---

## 5. 你可以（也应该）做的独立变异

报告给了 3 个（M-T-T-1 / M-T-D-1 / M-T-P-1，见 S6_REPORT §2.3）。**请不要复用它们**——S5 裁定 §4 已定"每轮审验做独立变异"。

已经被用过、避开的变异方向：
- `input_context_ref` → 常量（T-T 方向）
- `amount` 注入 `random.randint`（T-D 方向）
- denied 分支 `if False:`（T-P 方向）

**建议优先打的**（§4 R-1 ~ R-4）：
- 试一个**比 1-函数更小**的第四跳修法（或比 1-函数更大的、避免 LIKE 扫描的修法）；
- 试一个**非纯变异但不被 T-D 咬**（见 R-2）；
- 试一个"只污染 evidence 不污染 entities"的**半污染**变异（见 R-3）。

---

## 6. 判定要求

请给：

1. **PASS / PASS WITH CONDITIONS / FAIL** 三选一；
2. 你**实际跑过**的命令与真实输出（不要引用报告的数字）；
3. 你的**独立变异**清单 + 每个变异的红/绿实测结果；
4. **§4 R-1 必答**：1-函数偏差是否接受 / 要求加 `request_id` 列 / 其他。
5. 若有 failure：`failure / root cause / affected scope / proposed minimal fix`（四段式）；
6. 是否通过 S6（即：**V0 Spike 六步全闭合**，回 `RESEARCH_PRD_V2.md` §11 STOP Gate 十问）。

**范围锁**（请据此判定越界，不要建议扩张）：
- 不得引入 LLM；
- 不得新增 Kernel object / Adapter / Interface abstraction / Runtime / Queue；
- 不得改 V3 PRD、V0 Execution Spec、Kernel Boundary、`rules.py`、ontology、permission semantics；
- 不得改 E1–E5 数据集或 evaluation threshold；
- 不得通过修改 expected / threshold / fixture 迎合实现；
- 不得扩 schema（除非你裁断 §4 R-1 要"加 `request_id` 列"，那就走 §7 偏离路径）;
- 不得自行进入 spike 外任何工作（即使终验通过，也只回 STOP Gate 十问）。

---

## 7. 已知未闭合项（移交，本轮非缺陷）

1. **§4 R-1 SQL 1-函数偏差** —— 等你裁定。
2. **S5 移交的 `evidence_ids[0]` 中文 tiebreak 脆弱点**（S5_REPORT §9）—— **未触动**，仍在你待裁定清单上。

---

## 8. 我主动自陈的两处偏差

1. **§4 R-1 SQL 1-函数偏差**（= S6_REPORT §2.2）—— 字面报告，请审验。
2. **第一次 M-T-D-1 写崩了循环**（= S6_REPORT §2.4）—— 自陈"看起来咬住"与"真的咬住"的区别，并给出重做。

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
