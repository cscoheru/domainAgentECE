# R2_SEED_FIX_SPEC.md — canonical seed 无法恢复 relationships 的最小修复方案

> Date: 2026-09-20
> Status: **DRAFT — 待审。本文件不含任何代码修改；未创建任何实现文件。**
> 上游: Codex S1 Gate 裁定（`NO-GO / HOLD pending R2`）· 问题 A–J
> 依据: 对 ece 工作树的直接阅读 + **对活库的只读查询**（ece `8cb6824`，工作树 clean）

---

## 0. 一句话

R2 的根因不是「忘了在 Makefile 里多写一行」，而是：

> **「canonical seed」在仓库里有三份互相不一致的定义，且没有一份是完整的。**

因此最小修复的目标是**让唯一的程序入口完整**，而不是在调用链末端补一行命令。
本次修复**不新增 Kernel object、不改 V0 Execution Spec、不改业务规则、不改 evaluation 标准、不开始 S2**。

---

## 1. 证据基线（先说清楚哪些是实测、哪些是读码推断）

| # | 结论 | 方法 | 证据 |
|---|---|---|---|
| E1 | `make seed` = `uv run python -m ece.seed` → `run_seed()`，只做 3 件事：demo 实体 / 测试用户 / 3 条 ACL | 读 `Makefile:76` + `src/ece/seed.py:363-382` | 全文无 relationship 写入 |
| E2 | `run_seed()` **没有任何外部调用者**（无测试、无脚本 import） | `grep -rn "run_seed\|seed_from_demo_json" src/ tests/ scripts/` | 仅 `seed.py` 自身 `__main__`；测试只 import `seed_from_demo_json` |
| E3 | CI 的 seed 链条里**没有** relationship 步骤 | 读 `.github/workflows/ci.yml:47-73` | `gen-dataset → md5 → migrate → downgrade/upgrade → make seed → gen-eval-datasets → ingest_demo_docs` |
| E4 | 关系数据当前由 **3 个测试文件**靠 `subprocess` 现场补 | `grep -rn "seed_relationships" tests/` | `test_s14_seed_idempotent.py:62`、`test_cut040r2_state_integrity.py:116`、`test_s4_5_temporal.py:47` |
| E5 | 事故 `1204 → 4` 的 4 条残留 = **3 条 HAS_ROLE + 1 条 spike SELECTS** | 活库查询 + 读 wipe 谓词 | 见 §B.3，与 S1_REVIEW_PACK §5.3 记录吻合 |
| E6 | **E5 评测集 30 条用例全部是 `SELECTS`，零条 `HAS_ROLE`** | `python3` 解析 `data/eval/e5_temporal.json` | `{'SELECTS': 30}`，每条 `expected_count: 6`，`as_of` 只用于证明非时序关系恒可见 |
| E7 | `scripts/seed_temporal_roles.py` 是**孤儿脚本**，无任何调用者 | `grep -rn "seed_temporal_roles"` | 唯一命中是 `test_s4_5_temporal.py` 里**同名 source_system**（in-process 自播种），不是调用该脚本 |
| E8 | 活库当前计数 | `SELECT count(*)` | entities **444** / relationships **1204** / acl_entries **4** |

> ⚠️ **E6 是本 spec 最重要的发现**：它把 R2 的严格最小范围钉死在 relationships 上 —— 时序角色既不被 E5 需要，也不被 canonical seed 需要。详见 §E。

---

## A. 当前 canonical seed / `make seed` 的实际调用链是什么？

**`make seed` 本身的链条**（`Makefile:76` → `src/ece/seed.py`）：

```
make seed
└─ uv run python -m ece.seed
   └─ run_seed()                                    src/ece/seed.py:363
      ├─ [1] seed_from_demo_json(engine, data/dataset/demo.json)   :162
      │      ├─ 5 类实体 upsert（supplier/product/purchase_request/contract/policy）
      │      │    └─ display_id 由 _deterministic_display_id() 显式给定（PR001..PR200 等）
      │      └─ _seed_entity_departments(engine)     :319   ← jsonb 合并 attributes.department
      ├─ [2] seed_test_users(engine)                 :139   ← 4 个 demo 用户（upsert_identity）
      └─ [3] seed_acl_entries(engine)                :218   ← 3 条 ACL（tag demo:cut-040-test-acl）
```

**关系、部门实体、角色实体，一个都不在里面。**

**事实上的完整链条**（从 CI + 脚本文档字符串重建）：

```
make gen-dataset                      # data/dataset/demo.json
alembic upgrade head
make seed                             # ← 到这一步，relationships 仍为 0
uv run python scripts/seed_relationships.py      # ← 只存在于「人记得跑」和「测试自己补」
uv run python scripts/seed_temporal_roles.py     # ← 孤儿，见 E7
make gen-eval-datasets                # E1–E6 数据集（依赖 display_id）
uv run python scripts/ingest_demo_docs.py
```

**所以今天仓库里有三份互相不一致的「canonical seed」定义：**

| 定义 | 出处 | 含 relationships？ |
|---|---|---|
| ① `make seed` | `Makefile:76` | ❌ |
| ② CI 链条 | `.github/workflows/ci.yml` | ❌（整条链条都没有） |
| ③ 测试自愈 | 3 个测试文件的 `subprocess.run` | ✅ 但**只在该测试进程内** |

三者没有任何一处被声明为权威。这正是 R2 能长期存活的结构性原因。

---

## B. 为什么 entities 会恢复而 relationships 不恢复？

三个独立原因叠加，缺一不成灾：

### B.1 关系播种不在同一个函数里

`run_seed()` 只调用三个 seeder，关系播种由**独立进程级脚本**承载（`scripts/seed_relationships.py`，不在 `src/` 包内，无 import 路径）。`make seed` 完成后，`relationships` 表 **0 行**。

### B.2 测试重播的粒度是**函数级**，不是入口级

这是**最关键**的一条：

```python
# tests/integration/test_s14_seed_idempotent.py:51-52
r1 = seed_from_demo_json(engine, demo)     # ← 重播的是「函数」
r2 = seed_from_demo_json(engine, demo)
```

测试 wipe 后重播的是 `seed_from_demo_json()`，**不是** `run_seed()`，更不是 `make seed`。

> **推论：即使把关系塞进 `run_seed()`，函数级重播依然不恢复关系。**
> 这与 R40R2.1（RC-6 状态洗库）是同型教训 —— 当时的结论是「修复必须落在**与重播同粒度**的位置」，
> 所以 `_seed_entity_departments()` 被搬进了 `seed_from_demo_json()` 内部。

### B.3 但 4 条残留可以精确解释，证明这不是「随机丢失」

wipe 谓词（`test_s14_seed_idempotent.py:36-44`）只删**触及 `demo:demo` 实体的关系**：

| source_system | 条数 | 两端实体 | 是否被 wipe？ |
|---|---|---|---|
| `demo:seed_relationships` | 1200 | PR/product/supplier/policy（全部 `demo:demo`） | ✅ 全删 |
| `demo:seed_temporal_roles` | 3 | U001–U003（`api:header`）→ role（`demo:seed_temporal_roles`） | ❌ 幸存 |
| `spike:v0-technical-fixture` | 1 | 两端都是 spike | ❌ 幸存 |

**3 + 1 = 4** —— 与 S1_REVIEW_PACK §5.3 记录的 `1204 → 4` 逐字吻合。因果链闭合。

---

## C. 最小修复点在哪里？

### C.0 修复原则

- 修复必须落在**唯一程序入口**（`run_seed()`），而不是 Makefile 末端；
- 修复必须**不引入新抽象**（不建 seeder registry、不改 seed 架构）；
- 修复必须**保持既有 CLI 契约**，使 3 处测试调用**零改动**。

### C.1 核心修复（**必需**）

把 `scripts/seed_relationships.py` 的**逻辑**提炼为 `src/ece/seed.py` 内的可导入函数：

```
src/ece/seed.py
  ├─ seed_demo_relationships(engine) -> dict    # NEW：从脚本原样搬入逻辑
  └─ run_seed()
       ├─ [1] seed_from_demo_json(...)
       ├─ [2] seed_test_users(...)              ← 必须在关系之前（person 依赖）
       ├─ [3] seed_acl_entries(...)
       └─ [4] seed_demo_relationships(engine)   ← NEW
```

`scripts/seed_relationships.py` 降级为 **thin wrapper**（保留文件名、CLI、exit code 语义、stdout 关键字）。

**为什么顺序必须是 entities → users → relationships**：
`seed_relationships.py:109` 用 `_fetch_display_ids(engine, "person")` 取 `api:header` 的 person；
而 person 由 `upsert_identity()` 在 `seed_test_users()` 中创建（`seed.py:150`）。
若把关系播种放进 `seed_from_demo_json()`，首次运行时 person 尚不存在 → 关系阶段必然拿不到人。

### C.2 不采用的方案（及理由，供审阅者核验判断）

| 方案 | 不采用的理由 |
|---|---|
| 在 `Makefile` 的 `seed` target 后加第二行命令 | CI 链条仍不完整 —— 任何绕过 Makefile 的 `python -m ece.seed` 路径依旧缺失；且 CI 需要改两处 |
| 把关系播种塞进 `seed_from_demo_json()` | **顺序不成立**（见 C.1）：person 在 `seed_test_users()` 之后才存在。且会改变该函数「只写实体」的既有契约，超出最小修复 |
| 用 `subprocess` 从 `run_seed()` 调脚本 | 引入跨进程事务可见性问题（`test_s4_5_temporal.py:11-19` 已记录过这个坑），且拿不到 engine |

### C.3 建议追加（**可选，请审阅者裁定**）

**环境完整性自检**：让「关系图为空」**响亮失败**，而不是产出 vacuous 结果。

- 位置：`scripts/run_e4_relationships.py` / `run_e5_temporal.py` 入口处加前置断言
  （`SELECT count(*) FROM relationships WHERE source_system='demo:seed_relationships'` > 0，
  否则 `exit 2` + 明确提示）。
- 理由：目前 E4/E5 的前置条件**只写在 docstring 里**（`run_e4_relationships.py:14-17`: *"Note: E4 depends on the relationships table being seeded"*），
  运行时零检查。这正对应裁定书 §3 担心的 *vacuous pass*。
- 这**不改变任何评测语义**（不改数据集、不改阈值、不改断言），只是把已有的隐含前提变成显式失败。

若审阅者认为此项越界，可单独裁掉 —— **C.1 独立成立**。

---

## D. 修复后 canonical seed 的预期状态是什么？

**在空库上执行 `make gen-dataset && make db-upgrade && make seed`，期望：**

| 对象 | 来源 | 期望条数 |
|---|---|---|
| entities — `demo:demo` | `seed_from_demo_json` | **420**（PR 200 + product 100 + supplier 50 + contract 50 + policy 20） |
| entities — `api:header` | `seed_test_users` | **4**（U001–U004） |
| entities — `demo:seed_departments` | `seed_demo_relationships` | **4**（D001–D004） |
| relationships — `demo:seed_relationships` | `seed_demo_relationships` | **1200**（200 PR × 6） |
| acl_entries — `demo:cut-040-test-acl` | `seed_acl_entries` | **3** |
| **合计** | | **entities 428 / relationships 1200 / ACL 3** |

**不变式（可逐条机检）**：

1. 每个 demo PR 恰 **6** 条 `demo:seed_relationships` 关系
   （`BELONGS_TO` / `SUBMITTED_BY` ×2 / `SELECTS` / `CONTAINS` / `SUBJECT_TO` 各 1）
2. `demo:seed_relationships` 的关系**只**触达 `demo:demo` / `demo:seed_departments` / `api:header` 三类实体
   （`_FIXTURE_SOURCE_SYSTEMS` allowlist 保证，S1 已修）
3. demo display_id 号段恒为 `PR001..PR200` / `SUP001..SUP050` / …（`_deterministic_display_id` 保证）

> 注：活库现有 444 entities / 1204 relationships，多出的是 **spike fixture 7 + r4test 3 + r5test 1 + U005(运行时) 1 + admin:api 1 = 13**，
> 以及 spike 的 1 条 SELECTS。这些不属于 canonical seed，也不应被本修复触及。

---

## E. 是否应该把 `seed_relationships.py` 纳入 canonical seed？

### E.1 relationships —— **是，且以「提炼为函数」的方式纳入**

理由：

1. **它是 E4/E5 的硬依赖**，却是 `make seed` 唯一漏掉的大块数据（1200 行 vs 428 行实体）。
2. **把它做成函数而非加一行命令**，才能同时服务三种调用者（`make seed` / 未来的测试 / 任何 programmatic 入口），且获得 engine 与 in-process 事务。
3. **成本极低且零回归风险**：`run_seed()` **没有任何外部调用者**（E2），改动影响面是可证明的。

### E.2 `seed_temporal_roles` —— **不纳入（本轮）**

| 判据 | 结论 |
|---|---|
| E5 评测集需要它吗？ | **不需要**。30 条用例全是 `SELECTS` + `expected_count: 6`（E6） |
| canonical seed 需要它吗？ | **不需要**。它只服务 `test_s4_5_temporal.py`，而该测试**自己 in-process 播种**（`test_s4_5_temporal.py:44-97`） |
| 它有调用者吗？ | **没有**，是孤儿脚本（E7） |

**结论**：把它纳入 canonical seed 属于**超出 R2 范围**的扩张，且没有消费者。
建议记为观察项 `R2-obs-1`（孤儿脚本：删除 / 保留 / 纳入，待后续裁量），**本刀不动**。

> 这样一来，R2 的严格最小范围与裁定书的字面范围**完全一致**：只修 relationships。

---

## F. 修复是否会影响现有 E1–E5 数据集、ACL、identity 或 V0 fixture？

| 对象 | 是否受影响 | 依据 |
|---|---|---|
| **E1 数据集** | ❌ 不影响 | E1 用例引用 `PR###`/`SUP###` display_id；本修复不改实体分配（`_deterministic_display_id` 已固定） |
| **E2 数据集 / ACL** | ❌ 不影响 | `seed_acl_entries` 已改为从 DB 派生 `object_ref`（`seed.py:233-248`），本修复不触碰 |
| **E3 数据集** | ❌ 不影响 | 只读实体/上下文，关系播种是**增量**，不删不改已有行 |
| **E4 数据集** | ✅ **正向修复** | E4 当前依赖关系表非空；修复后不再 vacuous |
| **E5 数据集** | ✅ **正向修复** | 同上；30 条 `expected_count: 6` 在修复后恒可满足 |
| **identity（`seed_test_users`）** | ❌ 不影响 | 未被本修复触碰；且关系阶段**依赖**它先跑（C.1） |
| **V0 spike fixture** | ❌ 不影响 | spike 用显式 `SPIKE-*` display_id，不占 demo 号段；`_FIXTURE_SOURCE_SYSTEMS` allowlist 已把 `spike:*` 排除在关系播种之外（S1 修复 `a7ccb97`） |

**幂等性是唯一需要注意的耦合点**：关系播种现有的 `DELETE FROM relationships WHERE source_system = :s`
（`seed_relationships.py:141-147`）**只删自己的 tag**，因此对其它 fixture（spike / temporal / 未来新增）**无副作用**。此行为必须在提炼为函数时**原样保留**。

### F.1 一处**已确认但本刀不修**的潜在缺陷（观察项）

`_seed_departments`（`seed_relationships.py:79-90`）调用 `upsert_entity` 时**不传 display_id**，
department 的 `D001..D004` 仍是**全局 max+1** 分配 —— 即 K4（display_id 漂移）在 `department` 这一类型上**仍然存在**。
当前无消费者受害（E1–E5 数据集均不引用 `D0xx`，已核验），故**本刀不修**，记为 `R2-obs-2`。

> 按裁定书 §7「刹车」要求，此项**不在本刀实施**，仅登记。

---

## G. 如何验证 reset → canonical seed 后 relationships 完整恢复？

```bash
# ── 1. 彻底重置 ──────────────────────────────────────────
uv run alembic -c src/ece/migrations/alembic.ini downgrade base
uv run alembic -c src/ece/migrations/alembic.ini upgrade head
make gen-dataset

# ── 2. canonical seed（修复后应为完整入口）───────────────
make seed

# ── 3. 关系完整性断言 ────────────────────────────────────
docker compose exec -T db psql -U ece -d ece -c \
  "SELECT source_system, count(*) FROM relationships GROUP BY 1 ORDER BY 2 DESC;"
# 期望: demo:seed_relationships = 1200        ← 关键断言

docker compose exec -T db psql -U ece -d ece -c \
  "SELECT count(*) FROM (SELECT src_entity_id FROM relationships
     WHERE source_system='demo:seed_relationships'
     GROUP BY src_entity_id HAVING count(*) <> 6) t;"
# 期望: 0      ← 每个 PR 恰 6 条（G2 不变式）

# ── 4. 评测闭环 ──────────────────────────────────────────
make gen-eval-datasets
uv run python scripts/run_e4_relationships.py --data data/eval/e4_relationships.json   # 期望 Accuracy 100.0%
uv run python scripts/run_e5_temporal.py      --data data/eval/e5_temporal.json        # 期望 Accuracy 100.0%
```

**判据**：第 3 步的 `1200` 与 `0` 是**必检项**；若为 0 或 NULL，说明修复未生效 —— 此时 E4/E5 即便报 100% 也属 vacuous。

---

## H. 如何证明重复执行 canonical seed 仍然幂等？

```bash
# 连跑两次完整 canonical seed
make seed
docker compose exec -T db psql -U ece -d ece -c \
  "SELECT source_system, relation, count(*) FROM relationships GROUP BY 1,2 ORDER BY 1,2;" > /tmp/run1.txt

make seed
docker compose exec -T db psql -U ece -d ece -c \
  "SELECT source_system, relation, count(*) FROM relationships GROUP BY 1,2 ORDER BY 1,2;" > /tmp/run2.txt

diff /tmp/run1.txt /tmp/run2.txt && echo "IDEMPOTENT: 关系分布逐字相同"
```

**幂等契约（必须同时成立）**：

| 层 | 判据 |
|---|---|
| 实体 | 第二次 `created_by_type` 全为 0（既有契约，`test_s14` 已守） |
| ACL | `deleted = 3` 后重建 3，净变化 0（`seed.py:298-315` 已有 DELETE-then-INSERT） |
| **关系** | 第二次 `Removed 1200 prior 'demo:seed_relationships' rows` 后重建 1200，**净变化 0** |
| 总数 | 两次运行后 `entities` / `relationships` / `acl_entries` 三表 `count(*)` 完全相同 |

**注意**：关系播种的「canonical reseed」语义（DELETE 自己的 tag → 重建）**不破坏幂等**，
因为删除范围被限定在自身 `source_system`，且 `uq_relationships_triple` 唯一索引兜底。
提炼为函数时**必须保留 DELETE-then-INSERT**，不可退化为纯 `ON CONFLICT DO NOTHING`
（否则其它测试遗留的 7–8 条脏行会静默存活 —— `seed_relationships.py:129-132` 记录过这个历史事故）。

---

## I. 修复范围涉及哪些文件？

| 文件 | 动作 | 说明 |
|---|---|---|
| `src/ece/seed.py` | **EDIT** | 新增 `seed_demo_relationships(engine) -> dict`（自脚本原样搬入 `_FIXTURE_SOURCE_SYSTEMS` / `_fetch_display_ids` / `_seed_departments` / 6 条 rel_specs / DELETE-then-INSERT）；`run_seed()` 在 `seed_test_users()` 之后增加调用；返回摘要新增 `relationships` 字段 |
| `scripts/seed_relationships.py` | **EDIT（降级）** | 保留文件名与 CLI 契约，改为 `from ece.seed import seed_demo_relationships` 的 thin wrapper；`__main__` 保持 **exit 0 / exit 1** 语义与 stdout 关键字 `Total relationships in DB: N` |
| `ece/README.md` | **EDIT** | 写入**唯一权威** canonical 链条（消除 §A 的三份歧义定义） |
| `scripts/run_e4_relationships.py` | **EDIT（仅当采纳 C.3）** | 入口前置断言，不改任何评测语义 |
| `scripts/run_e5_temporal.py` | **EDIT（仅当采纳 C.3）** | 同上 |

**明确不修改**：

```
src/ece/entities/pipeline.py          # Kernel 模块，本刀零改动
src/ece/permissions/*                 # 权限语义
scripts/gen_eval_datasets.py          # 评测资产生成
data/eval/*.json                      # 冻结评测数据集
data/dataset/demo.json                # 合成数据
Makefile                              # 走函数路线后无需改（见 C.2）
src/ece/context/*                     # V0 Execution Spec §3/§4 的范围
.github/workflows/ci.yml              # 修复后 CI 自动获得关系（因为走的是 make seed）
```

**改动规模预估**：净新增约 **90–110 行**（大部分是从脚本平移），删除/替换脚本内约 **110 行**。
**不新增任何文件**（除本 spec）。

---

## J. 是否需要修改测试？如果需要，明确哪些 assertion 不变。

### J.1 **不需要修改任何现有测试**

3 处依赖 `scripts/seed_relationships.py` 的测试（E4）**零改动**，前提是 wrapper 保持：

| 契约 | 位置 | 必须保持 |
|---|---|---|
| 命令形式 | `test_s14_seed_idempotent.py:62`、`test_cut040r2_state_integrity.py:116`、`test_s4_5_temporal.py:47` | `["uv","run","python","scripts/seed_relationships.py"]` 可执行 |
| 退出码 | `test_s4_5_temporal.py:54` | `returncode != 0` → skip；**成功必须返回 0** |
| stdout | 人读 + 归档 | `Total relationships in DB: N` 关键字保留（非机器断言，但避免破坏归档可比性） |

### J.2 **所有现有 assertion 不变**（逐条声明）

```
✗ 不修改任何 expected 值
✗ 不修改任何 expected_count（E4/E5 数据集保持冻结）
✗ 不降低任何断言强度
✗ 不删除任何失败用例
✗ 不修改任何业务规则（rules.py / ontology / permissions）
✗ 不修改 test_eval_asset_integrity.py 的 6 个 guard（G1/G2 语义不变）
```

### J.3 **建议新增（1 个防回归 guard，非修改）**

```
tests/integration/test_eval_asset_integrity.py（同族新增一个 test）
  test_canonical_seed_restores_relationships():
      调 run_seed() → 断言 demo:seed_relationships count == 1200
                     且每 PR 恰 6 条
```

理由：R2 之所以能长期存活，正是**没有任何测试在守「canonical seed 的完整性」**。
这个 guard 把 §D 的不变式变成 CI 硬门槛。**它不修改任何既有测试。**

---

## 附 1. 本 spec 不做的事（对照裁定书 §10 特别要求）

```
✗ 未实施任何代码修改          ✗ 未开始 S2
✗ 未扩大 S1 scope             ✗ 未做 architecture refactor
✗ 未新增 Kernel capability    ✗ 未修改 V3 boundary / PRD
✗ 未修改业务规则              ✗ 未修改 evaluation 标准
✗ 未创建 Decision / Evidence / Context Update 实现
```

## 附 2. 需审阅者裁定的 2 个点

1. **C.3 环境完整性自检**是否采纳？（采纳 = E4/E5 在关系缺失时响亮失败；裁掉 = C.1 独立成立）
2. **E.2 孤儿脚本 `seed_temporal_roles.py`** 登记为 `R2-obs-1` 是否正确？（本刀不动，仅登记）

## 附 3. 登记但本刀不修的观察项

| ID | 内容 | 为何不修 |
|---|---|---|
| `R2-obs-1` | `scripts/seed_temporal_roles.py` 无调用者（孤儿）；其数据不被 E5 需要 | 超出 R2 字面范围；无消费者 |
| `R2-obs-2` | `department` 的 `D001..D004` 仍走全局 max+1（K4 在 `department` 类型上仍存在） | 当前无消费者受害（E1–E5 均不引用 `D0xx`）；裁定书 §7 要求刹车 |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: DRAFT — 待 Codex 审阅。**审阅通过前不实施任何代码修改。**
