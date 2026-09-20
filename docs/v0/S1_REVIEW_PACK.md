# S1 Review Pack

> 用途: 供**外部独立审查** S1 是否满足进入 S2 的条件。
> 本文件是**证据包**,不是总结。凡无法证明者标 `UNKNOWN` / `NOT CHECKED`。
> 生成者 = S1 实施者本人,不是独立第三方。

---

## 1. Execution Status

| 项 | 值 |
|---|---|
| **S1 状态** | **PASS WITH CONDITIONS**（条件见 §12） |
| **是否启动过 S2** | **NO**（未创建任何 S2 文件，未修改 S2 相关代码） |
| **S1 开始时间** | 2026-09-20，`docs/v0/V0_EXECUTION_SPEC.md` 获批之后。**精确墙钟 `UNKNOWN`** —— 仓库中无该事件的提交记录；可证明的最早锚点是 root commit `4f189e7`（`2026-09-20T18:59:44+08:00`，spec 交付） |
| **S1 结束时间** | 本文件生成的时刻。最近一次 ece 提交 `8cb6824` |
| **当前 git commit（ece）** | `8cb6824`（其上 `a7ccb97` = A+B 修复，`8dbdd6c` = S1 seeder） |
| **当前 git commit（root）** | `6b55861`（S1 报告）；本文件尚未提交 |
| **当前工作树是否 clean** | **YES**（`git status --short` 为空，已验证于本文件生成前） |

> ⚠️ **本文件本身尚未提交**。若审查者拉取本文件时 `git status` 非空，那正是本文件。

---

## 2. V0 Execution Spec Compliance

对照 `docs/v0/V0_EXECUTION_SPEC.md` §1（S1 相关条款）：

| Requirement | Status | Evidence |
|---|---|---|
| §1 fixture 用 `source_id` 寻址 | MET | `scripts/seed_v0_spike_fixture.py` 全文无 `PR\d{3}` 字面量；`_display_id_for()` 运行时解析 |
| §1 不硬编码 display_id | MET | `grep -nE "PR4[0-9]{2}\|SUP4[0-9]{2}"` → 无命中；**且现在 fixture 用显式 `SPIKE-*` id** |
| §1 `source_system` 唯一 | MET | `spike:v0-technical-fixture`，全库唯一（§9 已验证） |
| §1 幂等 | MET | 连跑两次：第二次 `removed={'relationships':1,'entities':7,'acl_entries':1}` 后重建（§7 原始输出） |
| §1 DELETE-then-INSERT 仅作用自身 source_system | MET | `_delete_own_rows()` 四处删除均 `WHERE source_system = :s`；无 `LIKE` |
| §1 3 供应商只建 1 条 SELECTS | MET | §5 计数 + §7 self-check |
| §1 PR 初始 `review_status = pending` | MET | §5 DB 查询；self-check 断言 |
| §1 seed 后 self-check | MET | `self_check()` 失败即 `return 1`；§7 原始输出 |
| §1 标注 `TECHNICAL SPIKE FIXTURE / NOT CUSTOMER-VALIDATED / NOT PRODUCT REFERENCE WORKFLOW` | MET | 模块 docstring + 运行时打印 + **写入 PR `attributes.fixture_notice`** |
| §12 范围锁（1 pack / 1 WorkflowSpec / 1 Agent / 1 Local Provider / 1 InProcessExecutor / 最小 Permission / 最小 Evidence） | MET | S1 只新增 1 个 seeder；未新增 pack / WorkflowSpec / Adapter / Interface / Kernel object |
| §1「fixture 必须明确标记」的**可机检形式** | **PARTIAL** | 标记是**文本**（docstring + attribute），**没有** CI 断言禁止误用。记为风险 R4 |
| §1 fixture 是否有 cleanup/reset 机制 | **PARTIAL** | 有 canonical re-seed（DELETE 自身 + 重建）；**无 teardown**（fixture 预期长期存在）。见 §9 |

**未对照项**：§3–§10 属 S3–S6，S1 不涉及。

---

## 3. Actual Files Changed

### 3.1 `git status --short`（本文件生成前）

```
（空）
```

### 3.2 `git diff --name-status 8dbdd6c a7ccb97`

```
M	data/eval/e1_resolution.json
M	data/eval/e2_permission.json
M	data/eval/e3_context.json
M	data/eval/e4_relationships.json
M	data/eval/e5_temporal.json
M	data/eval/e6_agent.json
M	scripts/gen_eval_datasets.py
M	scripts/run_p1_single_variable_experiment.sh
M	scripts/seed_relationships.py
M	scripts/seed_v0_spike_fixture.py
M	src/ece/entities/pipeline.py
M	src/ece/seed.py
M	tests/integration/test_eval_asset_integrity.py
M	tests/integration/test_s12_entity_pipeline.py
M	tests/integration/test_s24_e2_security.py
M	tests/integration/test_s4_5_temporal.py
M	tests/integration/test_s5_mcp.py
```

### 3.3 `git diff --stat 8dbdd6c a7ccb97`

```
 data/eval/e1_resolution.json                   | 200 +++++++--------
 data/eval/e2_permission.json                   |  90 +++----
 data/eval/e3_context.json                      | 340 ++++++++++++-------------
 data/eval/e4_relationships.json                |  60 ++---
 data/eval/e5_temporal.json                     |  60 ++---
 data/eval/e6_agent.json                        |  90 +++----
 scripts/gen_eval_datasets.py                   |  14 +-
 scripts/run_p1_single_variable_experiment.sh   |  12 +
 scripts/seed_relationships.py                  |  37 ++-
 scripts/seed_v0_spike_fixture.py               |  33 ++-
 src/ece/entities/pipeline.py                   |  19 +-
 src/ece/seed.py                                |  50 +++-
 tests/integration/test_eval_asset_integrity.py |   1 +
 tests/integration/test_s12_entity_pipeline.py  |  12 +-
 tests/integration/test_s24_e2_security.py      |  15 +-
 tests/integration/test_s4_5_temporal.py        |  20 +-
 tests/integration/test_s5_mcp.py               |  42 ++-
 17 files changed, 640 insertions(+), 455 deletions(-)
```

### 3.4 逐文件说明

| path | 类型 | 修改目的 | 属 S1 scope? |
|---|---|---|---|
| `scripts/seed_v0_spike_fixture.py` | **added**（commit `8dbdd6c`）| S1 交付物：spike fixture seeder | ✅ 是 |
| `scripts/seed_relationships.py` | modified | **A**：`_fetch_display_ids` 改显式 allowlist，不再吞并外来 fixture | ⚠️ 用户批准的 A |
| `src/ece/entities/pipeline.py` | modified | **B**：`upsert_entity` 增可选 `display_id`（纯新增参数） | ⚠️ 用户批准的 B（触及 Kernel 模块） |
| `src/ece/seed.py` | modified | **C'**：demo seed 改确定性 display_id（`_deterministic_display_id`）+ ACL 对象从 DB 派生 | ⚠️ **超出字面 A+B，已标注**（见 §11 R1） |
| `scripts/gen_eval_datasets.py` | modified | C' 连带：4 处实体查询加 `source_system` scope | ⚠️ 同上 |
| `scripts/run_p1_single_variable_experiment.sh` | modified | 过程缺陷修复：加 SAFETY GATE（src/ 脏则 `exit 2`） | ⚠️ 超出，但属缺陷修复（§4 of S1_REPORT） |
| `tests/integration/test_eval_asset_integrity.py` | modified | G2 偏差查询 scope 到 demo PR | ⚠️ 连带 |
| `tests/integration/test_s12_entity_pipeline.py` | modified | r4test supplier 改显式 display_id | ⚠️ 连带 |
| `tests/integration/test_s24_e2_security.py` | modified | r4test person/PR 改显式 display_id | ⚠️ 连带 |
| `tests/integration/test_s4_5_temporal.py` | modified | 去硬编码 `PR201`，改运行时解析 | ⚠️ 连带 |
| `tests/integration/test_s5_mcp.py` | modified | 去硬编码 `PR201` ×2，改运行时解析 | ⚠️ 连带 |
| `data/eval/*.json` ×6 | modified | 数据集重生成（数据为派生 artifact） | ⚠️ 连带 |
| `reports/.../single-variable-v2/*` | modified（commit `8cb6824`）| P1 重跑后的归档刷新 | ⚠️ 连带 |

> **诚实标注**：S1 实际改动**远大于**"新增一个 seeder"。原因见 S1_REPORT §1–§2：S1 暴露了跨 fixture 隔离缺陷，用户批准 A+B 修复，实施中又必须加 C'。
> **真正“S1 产物”只有 1 个新文件**；其余 17 个是修复与连带。

---

## 4. S1 Fixture

| 项 | 值 |
|---|---|
| **fixture 文件路径** | `scripts/seed_v0_spike_fixture.py` |
| **source_system** | `spike:v0-technical-fixture` |
| **source_id** | `SPIKE-PR-001` / `SPIKE-SUP-A` / `SPIKE-SUP-B` / `SPIKE-SUP-C` / `SPIKE-POL-001` / `spike-user-procurement` / `spike-user-unrelated` |
| **display_id（本次改为显式）** | `SPIKE-PR-001` / `SPIKE-SUP-A/B/C` / `SPIKE-POL-001` / `SPIKE-U-PROC` / `SPIKE-U-UNREL` |
| **entity_type 分布** | purchase_request ×1 / supplier ×3 / policy ×1 / person ×2 |
| **relationship** | **1 条**：`SPIKE-PR-001 -SELECTS-> SPIKE-SUP-A`（`source_system` 同 fixture） |
| **alias** | **0 条**（seeder 不建 alias） |
| **ACL** | **1 条**：`('user','spike-user-unrelated','entity','SPIKE-PR-001','deny', spike)` |
| **PR 关键属性** | `amount=1280000`；`review_status="pending"`；`fixture_notice="TECHNICAL SPIKE FIXTURE — NOT CUSTOMER-VALIDATED — NOT PRODUCT REFERENCE WORKFLOW"` |
| **是否幂等** | **YES** — 连跑两次结果逐字段相同（§7 原始输出） |
| **可否用 source_system/source_id 精确定位** | **YES** — `SELECT ... WHERE source_system='spike:v0-technical-fixture' AND source_id=:sid` |
| **是否存在 hardcoded display_id** | **NO** — 且现在**显式指定**，见下 |
| **cleanup / reset 机制** | **canonical re-seed**（每次运行先 `DELETE ... WHERE source_system = :s` 再重建）。**无 teardown** |
| **是否可能污染既有数据** | 见 §9。**当前无污染**，但 S1 之前版本**确实污染过**（见 §9.2） |

### 4.1 关于 UUID

| 问题 | 回答 |
|---|---|
| fixture 是否使用 UUID？ | **间接使用**。`entities.id` 是 `gen_random_uuid()` 默认值（DB 侧生成）；**fixture 自身不生成、不引用任何 UUID**。 |
| UUID 如何生成？ | PostgreSQL `gen_random_uuid()`（见 `\d entities`：`id | uuid | not null | gen_random_uuid()`） |
| 如何保证测试可重复？ | **通过不使用 UUID 达成**：fixture 的一切寻址用 `source_id`；关系与 ACL 用 `display_id`。UUID 只在 `DELETE ... WHERE source_system=:s` 的子查询里被间接使用。因此重播产生新 UUID **不影响可重复性**。 |

---

## 5. Database State Before / After

### 5.1 ⚠️ 必须先声明：S1 过程中执行过**全库重置**

解除阻塞（A+B+C'）时执行了 `alembic downgrade base` → `upgrade head`。**这销毁并重建了全部表**。

因此**不存在**一个干净的"S1 前 vs S1 后逐行 diff"。以下只报告**可证明**的事实。

| 项 | 值 |
|---|---|
| S1 执行前 DB 状态 | **UNKNOWN（已销毁）** —— 被 `downgrade base` 覆盖。可查到的唯一痕迹：`ece/reports/eval-archive/2026-09-20-cut040R2/` 中的历史 stdout |
| S1 执行后 DB 状态 | 见 5.2（当前实测） |
| 新增记录数 | 重置后为**全量重建**，"新增"无意义。**fixture 自身新增**：entities +7 / relationships +1 / acl_entries +1 |
| 修改记录数 | **UNKNOWN**（重置前状态已不可比） |
| 删除记录数 | **UNKNOWN**（同上）。重置本身删除全部行 |
| 是否修改既有测试数据 | **YES** —— 见 §3.4 中 5 个 `tests/integration/test_*.py` |
| 是否修改 seed 数据 | **YES** —— `src/ece/seed.py`（确定性 display_id + ACL 派生）、`scripts/seed_relationships.py`（allowlist） |
| 是否修改 ACL / permission 数据 | **YES** —— `seed_acl_entries()` 的 `object_ref` 由硬编码改为派生；ACL 表内容随之变化 |
| 是否修改其他 domain 数据 | **UNKNOWN** —— 无重置前快照可比 |

### 5.2 当前实测计数（本文件生成时）

```
        t         | count
------------------+-------
 entities         |   444
 relationships    |  1204
 acl_entries      |     4
 entity_aliases   |     1
 context_requests |  1180
 context_items    |  4293

fixture 自身:
 entities      | 7
 relationships | 1
 acl_entries   | 1
```

### 5.3 一次**真实发生的** fixture 破坏与恢复（诚实记录）

在执行"确定性验证"时,我做了两次裸 `DELETE demo:demo + seed_from_demo_json`,**未恢复关系**,导致：

```
relationships: 1204 → 4        ← demo 关系 fixture 被毁
```

随后执行 `uv run python scripts/seed_relationships.py` 恢复为 1204，并全量复验通过。

**这是 §11 R2 的来源**（`make seed` 路径不含关系播种）。

---

## 6. Test Execution

| # | command | result | passed | failed | skipped | warnings | time |
|---|---|---|---|---|---|---|---|
| 1 | `uv run pytest -m "not eval and not eval_llm" -q` | **exit 0** | **359** | **0** | **3** | 2 | **UNKNOWN**（未计时；同规模历史约 27–30s，属推测，不引用） |
| 2 | `uv run pytest tests/integration/test_eval_asset_integrity.py -o addopts="" -v` | exit 0 | 6 | 0 | 0 | — | `0.35s`（pytest 自报） |
| 3 | `uv run python scripts/run_e1_resolution.py --data data/eval/e1_resolution.json --base-url http://127.0.0.1:8765` | exit 0 | 64/65 | 1 | 0 | — | UNKNOWN |
| 4 | `uv run python scripts/run_e2_permission.py --data data/eval/e2_permission.json --base-url http://127.0.0.1:8765` | **exit 0** | 61 | 0 | 0 | — | UNKNOWN |
| 5 | `uv run python scripts/run_e3_context.py --data data/eval/e3_context.json` | exit 0 | 100/100 | 0 | 0 | — | UNKNOWN |
| 6 | `uv run python scripts/run_e4_relationships.py --data data/eval/e4_relationships.json` | exit 0 | 30/30 | 0 | 0 | — | UNKNOWN |
| 7 | `uv run python scripts/run_e5_temporal.py --data data/eval/e5_temporal.json` | exit 0 | 30/30 | 0 | 0 | — | UNKNOWN |
| 8 | `uv run python scripts/seed_v0_spike_fixture.py` | **exit 0** | — | — | — | — | UNKNOWN |
| 9 | `uv run ruff check src scripts tests` | exit 0 | — | — | — | — | UNKNOWN |
| 10 | `uv run python scripts/gen_eval_datasets.py` | exit 0 | — | — | — | — | UNKNOWN |

**必要说明**：

- **是否执行完整测试套件**：**YES**（#1 为 `-m "not eval and not eval_llm"`；被 deselect 的 `eval`/`eval_llm` 标记用例**未执行**）
- **是否只执行 targeted tests**：#2–#10 是 targeted；#1 是完整（受 marker 过滤）
- **是否存在 unrelated failures**：**NO**（#1 失败数为 0）
- **是否有测试因环境原因未执行**：**YES**
  - 3 个 `test_s5_5_real_llm` 因 `ECE_LLM_BASE_URL not set` 跳过
  - `eval` / `eval_llm` 标记用例被 `-m` deselect（E6 real-LLM 等）
- **未执行**：`make eval`（需 LLM 端点）；E6；纯 RAG baseline 对照

---

## 7. Test Output / Evidence

### 7.1 完整套件（`uv run pytest -m "not eval and not eval_llm" -q`）

> 项目 `pyproject.toml` 设 `addopts = "-q"`，**不输出汇总行**。计数由进度点统计（脚本见 §13）。

```
........................................................................ [ 20%]
........................................................................ [ 40%]
........................................................................ [ 60%]
..................................................sss................... [ 80%]
....................................................................     [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/starlette/testclient.py:53
  ... DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated ...

tests/integration/test_s13_jwt_auth.py::test_decode_jwt_token_invalid_signature
  ... InsecureKeyLengthWarning: The HMAC key is 12 bytes long ...

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```

**计数**：`总 362 / 通过 359 / 跳过 3 / 失败 0`，**exit 0**。

### 7.2 FER guards（6/6）

```
tests/integration/test_eval_asset_integrity.py::test_g1_e3_dataset_display_ids_all_exist PASSED [ 16%]
tests/integration/test_eval_asset_integrity.py::test_g1_e4_e5_dataset_display_ids_all_exist PASSED [ 33%]
tests/integration/test_eval_asset_integrity.py::test_g2_relationship_fixture_is_canonical PASSED [ 50%]
tests/integration/test_eval_asset_integrity.py::test_g3_null_validity_means_always_valid PASSED [ 66%]
tests/integration/test_eval_asset_integrity.py::test_g4_e5_expected_count_matches_fixture PASSED [ 83%]
tests/integration/test_eval_asset_integrity.py::test_g4_e4_bounds_are_not_vacuous PASSED [100%]
============================== 6 passed in 0.35s ===============================
```

### 7.3 S1 fixture self-check（第二次运行 = 幂等验证）

```
TECHNICAL SPIKE FIXTURE — NOT CUSTOMER-VALIDATED — NOT PRODUCT REFERENCE WORKFLOW
------------------------------------------------------------------------
source_system        : spike:v0-technical-fixture
removed (prior rows) : {'relationships': 1, 'entity_aliases': 0, 'entities': 7, 'acl_entries': 1}
entities created     : 7
relationships created: 1
PR display_id        : SPIKE-PR-001  (resolved at runtime)
------------------------------------------------------------------------
SELF-CHECK PASSED — all 7 fixture entities present, 1 SELECTS relationship,
                     PR review_status='pending', DENY acl on current display_id.
```

### 7.4 E2 权限套件

```
=== E2 Permission Suite Results ===
Total cases:        61
Failures:           0
Exposures:          0
Failure+Exposure %: 0.0%

*** PASS: 0 Unauthorized Exposure, 0 permission failure (cut-006 R2) ***
```

---

## 8. S1 Execution Log

> 只记录实际发生的事。时间戳取自 git commit 时间（`+08:00`）；无提交的步骤标 `UNKNOWN`。

| # | command | result | files changed | DB / fixture effect | next action |
|---|---|---|---|---|---|
| 1 | （接 spec 获批）读 `ece/` 现有件：`assemble_context` / `rules.py` / `context_specs` / audit 表 schema | 确认确定性规则**已存在**，V0 只缺 Decision / Evidence / Context Update | 无 | 无 | 设计 fixture |
| 2 | 查 `_load_acl_for` 的 `object_type` | 确认 = `'entity'`，ACL 按 display_id 匹配 | 无 | 无 | 设计权限拦截 |
| 3 | **写** `scripts/seed_v0_spike_fixture.py` | 新增 | +1 文件 | 无 | 运行 |
| 4 | `uv run python scripts/seed_v0_spike_fixture.py` | **exit 0**，self-check PASSED | 无 | +7 entities / +1 rel / +1 acl | 独立复核 |
| 5 | 独立 DB 侧查询（7 实体 / 1 关系 / ACL） | 全部符合 | 无 | 无 | 漂移韧性验证 |
| 6 | wipe 测试 + 查 fixture 存活 | 7/7 存活，ACL 与 display_id 一致 | 无 | wipe 删除并重播 demo:demo | 跑全套 |
| 7 | `uv run pytest -m "not eval and not eval_llm" -q` | **exit 1 —— 356P/3S/3F** | 无 | 无 | **诊断** |
| 8 | 诊断：查 PR 号段 | `demo:demo` 从 PR201..PR400 → **PR403..PR602**；PR402 = spike | 无 | 无 | 定位根因 |
| 9 | 诊断：查 PR402 关系构成 | `demo:seed_relationships` 6 + `spike` 1 = **7** | 无 | 无 | 定位根因 |
| 10 | 查 `_fetch_display_ids` / `_next_display_id` / `upsert_entity` 签名 | 确认两个隔离缺陷 | 无 | 无 | **STOP 报告** |
| 11 | **写** `docs/v0/S1_REPORT.md`；commit ece `8dbdd6c` + root `6b55861` | 已提交 | +1 文件 | 无 | 等裁定 |
| 12 | （用户批 `A + B`）**改** `seed_relationships.py`（allowlist） | 已改 | +37/-… | 无 | 下一项 |
| 13 | **改** `upsert_entity` 增可选 `display_id` | 已改 | +19/-… | 无 | 下一项 |
| 14 | **改** spike seeder：7 实体显式 `SPIKE-*` id | 已改 | +33/-… | 无 | 验证 |
| 15 | `downgrade base` + `upgrade head` | 成功 | 无 | **全库销毁并重建** | 重播 |
| 16 | `python -m ece.seed` / `seed_relationships.py` / `seed_v0_spike_fixture.py` | 420 / 1200 / 7 实体 | 无 | 重建 | 重生成数据集 |
| 17 | `gen_eval_datasets.py` + 跑 pytest | **仍 357P/3S/2F**（G1×2） | data/eval ×6 | 无 | **诊断** |
| 18 | 诊断：查号段 | demo PR = **PR202..PR401** —— 被 `r4test` PR201 抬高 | 无 | 无 | 定位第三个贡献者 |
| 19 | 查测试中 `upsert_entity` 自动 id 的调用点 | `test_s12`（supplier）+ `test_s24`（person, PR） | 无 | 无 | 修复 |
| 20 | **改** `test_s12` / `test_s24` 用显式 id；删除旧 r4test 泄漏实体 | 已改 | +27/-… | −3 entities | 重生成 |
| 21 | **改** `seed.py` 加 `_deterministic_display_id`（**C'**）+ ACL 派生 | 已改 | +50/-… | 无 | 验证确定性 |
| 22 | 连续两次 `DELETE demo:demo + seed` 并查号段 | **两次均 PR001..PR200 / SUP001..SUP050** | 无 | **关系被毁（1204→4）** | 继续验证 |
| 23 | 查其他消费方：`gen_eval_datasets` / `seed.py::_nth` / G2 / `test_s4_5_temporal` / `test_s5_mcp` | 5 处未 scope 或硬编码 | — | — | 统一修 |
| 24 | **改** 5 处（scope / 运行时解析） | 已改 | +90/-… | 无 | 跑全套 |
| 25 | `uv run pytest` | **357P/4S/1F**（`test_s5_mcp` unknown-user） | 无 | 无 | 修最后一处 |
| 26 | **改** `test_s5_mcp` 去硬编码 + `ruff --fix` | 已改 | +42/-… | 无 | 跑全套 |
| 27 | `uv run pytest` | **exit 0 —— 359P/3S/0F** | 无 | 无 | 全量评测 |
| 28 | E1–E5 | 98.5% / 61-61 / 100% / 100% / 100% | 无 | 无 | 提交 |
| 29 | commit ece `a7ccb97`（A+B+C'+连带） | 已提交 | 17 文件 | 无 | 打包 |
| 30 | 生成 `ab-pack.zip` | 完成 | +1 | 无 | 回报 |
| 31 | **（本文件前置）** 发现 `relationships` = **4** —— 步骤 22 的裸 DELETE 毁了 fixture | 已发现 | — | 关系失效 | 恢复 |
| 32 | `seed_relationships.py` + `seed_v0_spike_fixture.py` | 1204 关系恢复 | 无 | 恢复 | 全量复验 |
| 33 | `uv run pytest` + E1–E5 | **359P/3S/0F**；98.5% / 61-61 / 100% / 100% / 100% | 无 | 无 | 提交 reports |
| 34 | commit ece `8cb6824`（reports 刷新） | 已提交 | +2 文件 | 无 | 写本文件 |
| 35 | 生成 `docs/v0/S1_REVIEW_PACK.md`（本文件） | — | +1 文件 | 无 | **STOP** |

---

## 9. Isolation / Pollution Check

| # | 检查项 | 结果 | 证据 |
|---|---|---|---|
| 1 | S1 fixture 是否使用唯一 source_system | **YES** | `SELECT source_system, count(*) FROM entities GROUP BY 1` → `spike:v0-technical-fixture` 仅此一家 |
| 2 | S1 fixture 是否使用唯一 source_id | **YES** | 7 个 `SPIKE-*` / `spike-user-*`，前缀与现有 fixture 不重叠 |
| 3 | S1 是否修改已有 fixture | **YES** | `data/eval/*.json` ×6（重生成）；`reports/.../single-variable-v2/*`（P1 重跑刷新） |
| 4 | S1 是否修改 `seed.py` | **YES** | 加 `_deterministic_display_id`（C'）+ ACL 对象派生 |
| 5 | S1 是否修改 ACL seed | **YES** | `seed_acl_entries()` 的 `object_ref` 由硬编码改派生；ACL 表内容随之变化 |
| 6 | S1 是否修改 identity seed | **NO** | `_TEST_USERS` 未改；`seed_test_users()` 未改 |
| 7 | S1 是否修改既有 entity attributes | **YES（历史上）** | `test_s24_e2_security` 创建的 `S24 Test PR` 曾以自动 display_id 占用 PR201 —— **已改显式 id**；**当前无遗留** |
| 8 | S1 是否留下临时数据 | **NO（当前）** | 步骤 20 已删除旧 r4test 泄漏实体；`git status` clean；fixture 为**预期长期存在**的数据，非临时 |
| 9 | S1 是否影响 E1/E2/E3/E4/E5 | **YES —— 曾被影响，现已修复** | E1 曾 90.8%（`SPIKE-SUP-A` 劫持槽位）；E2 曾 1 failure（ACL 对象错位）。**现全部 100%/98.5%** |
| 10 | 是否执行 S1 前后对比 | **PARTIAL** | 号段前后对比**有**（`demo:demo` PR001..PR200 恒定，见 §7/§13）；**全库逐行前后对比 UNKNOWN**（§5.1：经历全库重置） |
| 11 | S1 是否有 NOT CHECKED 项 | **YES** | 见下 |

**NOT CHECKED**：

- 全库重置前的精确 DB 快照（未留存）
- `context_requests` / `context_items` 的历史增长来源（本次未审计）
- 多进程 / 并发下 fixture 的隔离性（单进程验证）
- Windows / WSL2 下的行为（本刀范围外，对应原刀 41）

---

## 10. Git Diff Evidence

### 10.1 name-status / stat

见 §3.2 / §3.3（原文粘贴）。

### 10.2 关键修改的 old / new / why

#### (a) `src/ece/entities/pipeline.py` — `upsert_entity`（**安全/数据隔离相关**）

| | |
|---|---|
| **old behavior** | 签名无 `display_id`；恒调用 `_next_display_id(engine, entity_type)` = **该 entity_type 全局 max+1** |
| **new behavior** | 增加**可选** `display_id: str \| None = None`；`resolved_display_id = display_id or _next_display_id(...)`。既有调用（不传该参数）**行为完全不变** |
| **why changed** | 任何外来同类型实体都会抬高全局 max，使 demo 重播分配到新号段 → 冻结的 E3/E4/E5 数据集静默失效（K4） |

#### (b) `src/ece/seed.py` — `_deterministic_display_id`（**数据隔离相关**）

| | |
|---|---|
| **old behavior** | `seed_from_demo_json` 不传 `display_id` → 依赖全局 max+1 → 重播号段随表内其它实体漂移 |
| **new behavior** | 传 `_deterministic_display_id(entity_type, idx)` = `<PREFIX><idx+1:03d>`，由 demo.json 的**有序位置**推导 |
| **why changed** | 使 demo 号段**与表内其它实体无关**，重播恒为 `PR001..PR200` 等；这是 C' |

#### (c) `src/ece/seed.py` — `seed_acl_entries` 的 `object_ref`（**权限相关**）

| | |
|---|---|
| **old behavior** | 硬编码 `"SUP052"` / `"PR003"` / `"CON002"` |
| **new behavior** | 从 DB 派生：`_nth(type, n)` 用 `source_system='demo:demo'` + `ORDER BY display_id`，**与 `gen_eval_datasets.py` 同 scope 同排序** |
| **why changed** | 硬编码值会在 display_id 位移后与数据集错位（FER 期确实发生过：提交里是 `PR003`，数据集里是 `PR203`） |

#### (d) `scripts/seed_relationships.py` — `_fetch_display_ids`（**fixture 隔离相关**）

| | |
|---|---|
| **old behavior** | `SELECT display_id FROM entities WHERE entity_type = :t` —— **无 source_system 范围** |
| **new behavior** | 按 `_FIXTURE_SOURCE_SYSTEMS` allowlist 加 `AND source_system = :s`；未映射类型 `raise KeyError` |
| **why changed** | 原实现会**吞并任何同类型外来实体**（曾给 spike PR 加 6 条 demo 关系） |

#### (e) `scripts/run_p1_single_variable_experiment.sh` — SAFETY GATE

| | |
|---|---|
| **old behavior** | 直接 `git checkout <commit> -- src/`，**静默冲掉未提交的 `src/` 改动** |
| **new behavior** | 入口检查 `git status --porcelain -- src/`，非空则打印并 `exit 2` |
| **why changed** | 该脚本已在 FER 期**实际造成数据丢失**：它回滚了未提交的 `seed.py` 修复，导致 `db24826` 的"全绿"与提交内容不一致 |

---

## 11. Risk Register

| # | Risk | Severity | Evidence | Blocks S2? |
|---|---|---|---|---|
| **R1** | **C'（demo 确定性 display_id）超出字面 A+B 授权** | **高** | §3.4 / §10.2(b)；实施者已自行标注 | **不阻塞实现，但阻塞"授权确认"** —— 需审阅者判定 |
| **R2** | **`make seed` 路径不恢复关系 fixture** —— 任何 `wipe + seed` 都留下空关系图 | **高** | §5.3：本人在确定性验证中实际触发（1204→4）；已手工恢复 | **可能阻塞 S2** —— S2 若走"重置→seed"会把 E4/E5 测成 0 |
| **R3** | **原始数据丢失**：全库重置销毁了 S1 前的 DB 状态，无快照 | 中 | §5.1 | 否（但削弱可审计性） |
| **R4** | **fixture 标记是文本，无 CI 断言**禁止把 spike fixture 当产品方向 | 中 | §2 最后两行 | 否 |
| **R5** | **`db24826`（FER）内容与其实测状态不一致** —— 已定位并修根因，但**该历史提交本身未修正** | 中 | §10.2(e) | 否（已加守门，防复发） |
| **R6** | **S1 修改了 5 个既有测试文件** —— 虽为"去硬编码"性质，但属改动既有测试 | 中 | §3.4 | 需审阅者确认可接受 |
| **R7** | `_deterministic_display_id` 依赖 **demo.json 的记录顺序** —— 若 demo.json 重排，号段会变 | 中 | 代码注释已写明机制 | 否（demo.json 由 `make gen-dataset` 生成，顺序稳定；**未加顺序守护**） |
| **R8** | E1 仍为 98.5%（`e1-054` 长期失败），非本刀引入 | 低 | S1_REPORT 已记录 | 否 |
| **R9** | 并发 / 多进程下 fixture 隔离未验证 | 低 | §9 #11 | 否（V0 单进程） |

---

## 12. S1 Gate Recommendation

### GO WITH CONDITIONS

**理由**：S1 的交付物（spike fixture）及其为解除自身阻塞所需的一切修复**均已实施并全量验证通过**
（pytest 359P/3S/0F；E1 98.5%；E2 61/61；E3/E4/E5 100%；6/6 guard PASS；fixture self-check PASS；
demo 号段恒定）。**未发现阻止进入 S2 的技术问题。**

**但**存在以下必须由审阅者确认或后续处理的**非阻塞条件**：

1. **确认 C' 的授权**（R1）—— demo seed 改确定性 display_id 超出字面 A+B。**若不认可，S1 需回退该项并重新设计数据隔离方案。**
2. **确认修改 5 个既有测试可接受**（R6）—— 性质为"去硬编码 display_id"，未改断言语义、未降标准。
3. **S2 开始前必须先解决 R2** —— `make seed` 不恢复关系 fixture；S2 若依赖 E4/E5 会测出假 0。**建议：在 S2 的第一刀里把关系播种并入标准 seed 路径，或给 `run_v0_loop` 前置自检。**
4. **R5 的历史提交 `db24826` 不做修正**（其内容与当时实测不一致），仅靠新增守门防复发。若要求追溯更正，请指出。

---

## 13. Exact Reproduction Commands

> 全部在 `/Users/kjonekong/projects/domainAgentECE/ece` 下执行。**均为实际执行过的命令。** 前置：`docker compose up -d`、`uv run alembic upgrade head`。

### 13.1 重建 fixture（幂等，可任意次重跑）

```bash
uv run python scripts/seed_v0_spike_fixture.py
# 期望: exit 0 + "SELF-CHECK PASSED — all 7 fixture entities present, 1 SELECTS relationship,"
#       + "PR review_status='pending', DENY acl on current display_id."
```

### 13.2 独立核对 fixture（不依赖 self-check）

```bash
docker compose exec -T db psql -U ece -d ece -c "
SELECT entity_type, source_id, display_id,
       attributes->>'review_status' AS review_status,
       attributes->>'amount' AS amount
FROM entities WHERE source_system='spike:v0-technical-fixture' ORDER BY 1,2;"

docker compose exec -T db psql -U ece -d ece -c "
SELECT r.relation, s.source_id AS src, d.source_id AS dst
FROM relationships r
JOIN entities s ON s.id=r.src_entity_id
LEFT JOIN entities d ON d.id=r.dst_entity_id
WHERE r.source_system='spike:v0-technical-fixture';"
# 期望: 恰好 1 行 SELECTS / SPIKE-PR-001 -> SPIKE-SUP-A

docker compose exec -T db psql -U ece -d ece -c "
SELECT subject_ref, object_type, object_ref, effect
FROM acl_entries WHERE source_system='spike:v0-technical-fixture';"
# 期望: 1 行 deny / spike-user-unrelated / entity / SPIKE-PR-001
```

### 13.3 全套 pytest（计数由进度点统计；项目 `addopts = "-q"` 不输出汇总行）

```bash
uv run pytest -m "not eval and not eval_llm" -q > /tmp/p.txt 2>&1; echo "exit=$?"
python3 - <<'PY'
import re
t = open('/tmp/p.txt').read(); tot=sk=fa=0
for line in t.splitlines():
    m = re.match(r'^([.sF]+)\s+\[\s*\d+%\]', line)
    if m: tot += len(m.group(1)); sk += m.group(1).count('s'); fa += m.group(1).count('F')
print(f'总 {tot} / 通过 {tot-sk-fa} / 跳过 {sk} / 失败 {fa}')
PY
# 期望: exit=0 ; 总 362 / 通过 359 / 跳过 3 / 失败 0
```

### 13.4 FER guards

```bash
uv run pytest tests/integration/test_eval_asset_integrity.py -o addopts="" -v
# 期望: 6 passed
```

### 13.5 E1 / E2

```bash
uv run python scripts/run_e1_resolution.py --data data/eval/e1_resolution.json --base-url http://127.0.0.1:8765
uv run python scripts/run_e2_permission.py --data data/eval/e2_permission.json --base-url http://127.0.0.1:8765
# 期望: E1 Accuracy 98.5% ; E2 Exposures 0 / Failures 0 / exit 0
```

### 13.6 E3 / E4 / E5

```bash
uv run python scripts/run_e3_context.py --data data/eval/e3_context.json
uv run python scripts/run_e4_relationships.py --data data/eval/e4_relationships.json
uv run python scripts/run_e5_temporal.py --data data/eval/e5_temporal.json
# 期望: 三次均 Accuracy 100.0% 且 exit 0
```

### 13.7 确定性验证（demo 号段与表内其它实体无关）

```bash
for i in 1 2; do
  docker compose exec -T db psql -U ece -d ece -c "BEGIN;
    DELETE FROM relationships WHERE src_entity_id IN (SELECT id FROM entities WHERE source_system='demo:demo')
       OR dst_entity_id IN (SELECT id FROM entities WHERE source_system='demo:demo');
    DELETE FROM entities WHERE source_system='demo:demo'; COMMIT;"
  uv run python -m ece.seed > /dev/null 2>&1
  docker compose exec -T db psql -U ece -d ece -t -A -c \
    "SELECT entity_type||' '||min(display_id)||' .. '||max(display_id) FROM entities
     WHERE source_system='demo:demo' GROUP BY entity_type ORDER BY 1;"
done
# 期望: 两次输出逐字相同; purchase_request PR001 .. PR200 ; supplier SUP001 .. SUP050

# ⚠️ 本命令会毁掉关系 fixture，必须恢复：
uv run python scripts/seed_relationships.py
uv run python scripts/seed_v0_spike_fixture.py
```

### 13.8 P1 脚本 SAFETY GATE

```bash
git status --porcelain -- src/    # 若为空则下一步应正常开始
bash scripts/run_p1_single_variable_experiment.sh
# 期望: src/ 干净时正常跑；src/ 脏时应输出
#   "REFUSING TO RUN: src/ has uncommitted changes; ..." 并 exit 2
```

---

**生成者**: Claude（Fable 5.1）· **生成时间**: 2026-09-20
**性质声明**: 本文件由 **S1 实施者本人**生成，**不是独立第三方**。请以对抗性标准审阅。
