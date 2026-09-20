# R2_IMPLEMENTATION_REPORT.md — canonical seed 修复实施报告

> Date: 2026-09-20
> Status: **实施完成，待审。未进入 S2。**
> 上游: `docs/v0/R2_SEED_FIX_SPEC.md`（Codex 裁定 **GO WITH MINOR CONDITIONS**）
> ece 基线 commit: `8cb6824` → 本刀实施 commit: **`b5c92e2`**
> 证据归档: `ece/reports/r2-verification/`（11 个原始输出文件 + 全量 diff）

---

## 0. 结论

# **R2 PASS**

批准范围内的 9 条要求**全部实施**，A–H 全部验证项**全部通过**，禁区**零改动**。

**有两项需要你确认的边界判断**（均不影响 R2 正确性，可各自单独裁掉）：

1. `ece/README.md` 我除了新增「Canonical seed」一节，还改了「快速开始」里的一行 —— 原文
   `make setup  # uv 同步依赖 + alembic 迁移 + seed 合成数据` 与 Makefile 实际不符
   （`setup` 只有 `uv sync --all-groups`）。它本身就是「canonical seed 的第三份错误定义」。
2. 新增的 regression guard 里我加了一个**负向对照**（第 6 条要求未列）。
   理由：没有它，precondition 就是一个**未被验证的断言** —— 正是本项目反复出现的模式。

---

## 1. 实际修改文件

| 文件 | 动作 | 行数变化 |
|---|---|---|
| `src/ece/seed.py` | EDIT — 新增 `seed_demo_relationships()` / `demo_relationship_fixture_status()` / `_fetch_display_ids()` / `_seed_fixture_departments()`；`run_seed()` 增加第 4 阶段；`__main__` 增加关系摘要 | +263 −2 |
| `scripts/seed_relationships.py` | EDIT — 降级为 thin wrapper，调用 `ece.seed.seed_demo_relationships()` | +32 −155 |
| `scripts/run_e4_relationships.py` | EDIT — 新增 precondition（缺失/不完整 → `exit 2`） | +23 −2 |
| `scripts/run_e5_temporal.py` | EDIT — 同上 | +19 −0 |
| `ece/README.md` | EDIT — 新增 Canonical seed 唯一权威链条；修正 `make setup` 一行的错误描述 | +35 −2 |
| `tests/integration/test_canonical_seed_completeness.py` | **NEW** — G5/G6 regression guard（含负向对照） | +176（新文件） |
| `reports/r2-verification/` | **NEW** — 原始 stdout 证据归档 | 11 文件 |

```
 README.md                       |  37 +++++-
 scripts/run_e4_relationships.py |  23 +++-
 scripts/run_e5_temporal.py      |  19 +++
 scripts/seed_relationships.py   | 187 +++++-----------------------
 src/ece/seed.py                 | 263 +++++++++++++++++++++++++++++++++++++++-
 5 files changed, 367 insertions(+), 162 deletions(-)
```

**实现方式是「提炼共享逻辑」而非复制**（符合第 9 条）：`scripts/seed_relationships.py` 现在
是 32 行的 wrapper，唯一的 relationship seeding 实现位于 `src/ece/seed.py`。
全仓搜索确认不存在第二份实现。

---

## 2. 实际命令（按执行顺序）

```bash
# ── 静态检查 ────────────────────────────────────────────────
uv run ruff check .                    # All checks passed!
uv run mypy src tests                  # Success: no issues found in 119 source files
uv run lint-imports                    # Contracts: 2 kept, 0 broken

# ── A. 空库 reset → migrate ─────────────────────────────────
docker exec ece-db-1 psql -U ece -d ece -c "SELECT count(*) FROM entities, ..."   # 重置前: 444/1204/4
uv run alembic -c src/ece/migrations/alembic.ini downgrade base   # 0007→…→0001→base
uv run alembic -c src/ece/migrations/alembic.ini upgrade head     # →0007_user_orgs
make gen-dataset                       # md5 = f98a76ca10a025d530e1d018582a13ca（= CI baseline）

# ── B/C/D. 第一次 make seed（空库）──────────────────────────
make seed
uv run python scripts/ingest_demo_docs.py

# ── E/F. 幂等：连跑 + 逐字比对 ──────────────────────────────
make seed                              # 第 2 次
make seed                              # 第 3 次（快照 A→B 比对）

# ── G. E4/E5 precondition 正反两面 ──────────────────────────
uv run python scripts/run_e4_relationships.py --data data/eval/e4_relationships.json
uv run python scripts/run_e5_temporal.py      --data data/eval/e5_temporal.json
docker exec ece-db-1 psql -U ece -d ece -c "DELETE FROM relationships WHERE source_system='demo:seed_relationships';"   # 负向对照
uv run python scripts/run_e4_relationships.py ...   # 期望 exit 2
uv run python scripts/run_e5_temporal.py      ...   # 期望 exit 2
make seed                              # 恢复

# ── H. 全量测试 ─────────────────────────────────────────────
uv run pytest -m "not eval and not eval_llm" -rs
uv run pytest tests/integration/test_canonical_seed_completeness.py -v
uv run pytest tests/integration/test_eval_asset_integrity.py -q

# ── 附加回归确认（S1 基线对照）──────────────────────────────
uv run python scripts/run_e1_resolution.py --data data/eval/e1_resolution.json --base-url http://127.0.0.1:8765
uv run python scripts/run_e2_permission.py --data data/eval/e2_permission.json --base-url http://127.0.0.1:8765
uv run python scripts/run_e3_context.py    --data data/eval/e3_context.json

# ── 恢复被重置清除的 S1 spike fixture ───────────────────────
uv run python scripts/seed_v0_spike_fixture.py
```

---

## 3. reset → seed 结果（A / B / C / D）

### A. 空库确认

```
重置前: entities 444 / relationships 1204 / acl_entries 4
downgrade base: 0007→0006→0005→0004→0003→0002→0001→base 全部执行
upgrade head  : →0001→…→0007_user_orgs 全部执行
重置后: entities 0 / relationships 0 / acl_entries 0
```

### B. `make seed` 输出（空库，第一次）

```
Seed complete: {'supplier': 50, 'product': 100, 'purchase_request': 200, 'contract': 50, 'policy': 20}
Total created: 420
Total skipped: 0
Relationships: {'BELONGS_TO': 200, 'SUBMITTED_BY': 400, 'SELECTS': 200, 'CONTAINS': 200, 'SUBJECT_TO': 200}
              (replaced 0 prior rows, 4 departments)
Total relationships in DB: 1200
```

> **这一行就是 R2 的修复**：修复前同样的 `make seed` 在这里输出 `Total relationships in DB: 0`。

### B′. entities = **428**（逐项核对）

```
 total_entities
----------------
            428
```

| source_system | entity_type | count |
|---|---|---|
| `api:header` | person | 4 |
| `demo:demo` | contract | 50 |
| `demo:demo` | policy | 20 |
| `demo:demo` | product | 100 |
| `demo:demo` | purchase_request | 200 |
| `demo:demo` | supplier | 50 |
| `demo:seed_departments` | department | 4 |
| **合计** | | **428** |

与 spec §D 的预测**逐项相同**。

### C / D. 关系数量与「每 PR 恰 6 条」

```
      source_system      |   relation   | count
-------------------------+--------------+-------
 demo:seed_relationships | BELONGS_TO   |   200
 demo:seed_relationships | CONTAINS     |   200
 demo:seed_relationships | SELECTS      |   200
 demo:seed_relationships | SUBJECT_TO   |   200
 demo:seed_relationships | SUBMITTED_BY |   400
                                              = 1200
```

| 断言 | 结果 |
|---|---|
| `demo:seed_relationships` 总数 == 200 PR × 6 | **1200** ✅ |
| 偏离 6 条的 demo PR | **0 行** ✅ |
| **没有任何关系的** demo PR（`HAVING` 查不到的盲区）| **0** ✅ |
| `acl_entries` | **3** ✅ |

> 第三行是刻意补的：`HAVING count(*) <> 6` 只看得见**有关系行的** PR，一个 0 关系的 PR
> 不会出现在 JOIN 结果里。只查偏离会漏掉最严重的情况（图整个空掉）。

---

## 4. 第二次 seed 结果（E / F，幂等）

```
Seed complete: {'supplier': 0, 'product': 0, 'purchase_request': 0, 'contract': 0, 'policy': 0}
Total created: 0
Relationships: {...200/400/200/200/200...} (replaced 1200 prior rows, 4 departments)
Total relationships in DB: 1200
```

**逐字比对**（非空快照，行数已核）：

| 比对对象 | 行数 | 结果 |
|---|---|---|
| 关系分布（`source_system` × `relation` × `count`） | 5 | ✅ 逐字相同 |
| 每 PR 关系数（200 个 PR） | 200 | ✅ 逐字相同 |
| 三表总数（entities / relationships / acl_entries） | 3 | ✅ 逐字相同 |

三次 `make seed` 的结果完全相同：实体 `created=0`，关系 `replaced 1200 → 1200`，分布零漂移。

---

## 5. E4/E5 precondition 验证（G）

### G1 — 完整 fixture 下（**未手工执行 `seed_relationships.py`**）

```
E4 exit=0  Accuracy: 100.0%
E5 exit=0  Accuracy: 100.0%
```

### G2 — 负向对照（删掉 fixture）

```
DELETE 1200

E4 exit=2 (期望 2)
PRECONDITION FAILURE: demo relationship fixture missing or incomplete.
  demo:seed_relationships = 0 rows, expected 1200 (6 per demo PR).
  Refusing to run: an empty graph would produce a VACUOUS result.
  Fix: run `make seed` (canonical seed now restores relationships).

E5 exit=2 (期望 2)
（同上）
```

恢复后：`relationships=1200`。

> **G 的完整含义**：E4/E5 现在**既不再依赖人工补种**，也**不会对空图打分**。
> 修复前它们在空图上会给出 0%（E5）或落在 `[0, max]` 界内读成 PASS（E4 的 vacuous 模式）。

---

## 6. 全量测试结果（H）

```
uv run pytest -m "not eval and not eval_llm" -rs
→ 361 passed, 3 skipped, 3 deselected, 2 warnings in 40.02s     （exit=0）

SKIPPED ×3 均为 test_s5_5_real_llm.py（ECE_LLM_BASE_URL 未设置），与 R2 无关。
```

| 项 | 修复前（S1 基线） | 本刀 | 说明 |
|---|---|---|---|
| passed | 359 | **361** | +2 = 新增的 G5/G6 guard |
| skipped | 3 | 3 | 不变 |
| failed | 0 | **0** | — |

| 分项 | 结果 |
|---|---|
| 新增 guard `test_canonical_seed_completeness.py` | **2 passed** |
| FER guards `test_eval_asset_integrity.py`（G1–G4）| **6 passed** |

### 6.1 ⭐ 全套 pytest **跑完之后**的不变量

```
 entities | relationships | acl
----------+---------------+-----
      437 |          1203 |   3

 demo PRs deviating from 6 : 0
 demo:seed_relationships   : 1200
```

（437 / 1203 含测试自建的 fixture 实体与 `test_s4_5_temporal` in-process 播种的 3 条 HAS_ROLE；
关系 fixture 本身仍为完整 1200 条、零偏离。）

> **修复前的对照**：`test_s14_seed_idempotent` 的 wipe 会把关系图从 1204 打到 4，
> 靠测试自己的 `subprocess` 才恢复。现在 `make seed` 自身即完整。

### 6.2 附加：E1/E2/E3 回归确认（对照 S1 基线）

| 套件 | S1 基线 | 本刀（重置+canonical seed 后） | 结果 |
|---|---|---|---|
| E1 | 98.5% | **98.5%**（64/65） | ✅ 一致 |
| E2 | 0 exposures / 0 failures | **0 exposures / 0 failures**（61 例） | ✅ 一致 |
| E3 | 100% | **100%**（100/100） | ✅ 一致 |

**全库重置没有引入评测回归。**

---

## 7. 是否有任何超出批准范围的修改

### 7.1 代码层面：**没有**

```
git diff --name-only 8cb6824 -- \
  src/ece/permissions/ src/ece/context/ src/ece/entities/pipeline.py \
  src/domain_packs/ data/eval/ data/dataset/ src/ece/migrations/ Makefile .github/
→ （空输出）
```

| 禁止项 | 状态 |
|---|---|
| V3 PRD / V0 Execution Spec / Kernel Boundary | ✅ 未触碰（ece 仓外，且根仓 docs/ 未改） |
| `rules.py` / ontology / permission semantics | ✅ 未触碰 |
| E1–E5 数据集 | ✅ 未触碰（`git diff HEAD -- data/eval/` 为空） |
| evaluation threshold | ✅ 未触碰 |
| Context / Decision / Evidence | ✅ 未触碰 |
| 开始 S2 | ✅ 未开始 |
| 修 `D001..D004` display_id | ✅ 未修（代码内以 `R2-obs-2` 注释登记） |
| 处理 `seed_temporal_roles.py` | ✅ 未处理（仍为 `R2-obs-1`） |
| architecture refactor | ✅ 无（未新增 registry / abstraction / 依赖边） |

`lint-imports` 输出 `2 kept, 0 broken` —— 领域包隔离与引擎核心隔离契约均未破坏。

### 7.2 两项需你确认的边界判断

1. **`ece/README.md` 「快速开始」的一行修正**（`make setup` 描述）。属于 canonical seed
   的第三份错误定义，但字面上超出了「同步 canonical 链条」。
2. **G6 负向对照**。第 6 条要求未列出；无它则 precondition 未被验证。

两者都可单独裁掉，不影响 R2 正确性。

### 7.3 过程性动作（非代码修改，须记录）

| 动作 | 说明 |
|---|---|
| **全库重置清除了 S1 的 spike fixture** | 7 实体 + 1 关系被 `downgrade base` 抹除。已用其自带 seeder 恢复，self-check `PASSED`（PR display_id 仍为 `SPIKE-PR-001`，未占用 `PR###` 号段） |
| **未重跑 `make gen-eval-datasets`** | CI 会跑它，但它会**重写冻结数据集**，与「不得修改 E1–E5 数据集」冲突。数据集已在磁盘上且 G1 guard 验证全部引用有效，故不重生成 |
| `reports/r2-verification/` | 11 个原始输出文件 + 全量 patch，作为证据归档 |

---

## 8. 验证过程中的两次自我纠错（必须记录）

按本项目对「假绿」的一贯要求，这两次**我自己踩中同一模式**的过程必须留档：

### 8.1 幂等性比对第一次是假的

首次写比对脚本时用的是
`SELECT ... || count(*) FROM relationships GROUP BY 1,2 ORDER BY 1,2` ——
`ORDER BY 2` 引用了不在 select list 里的位置，**两个分布查询都报错**，
`diff` 比较的是两个**空文件**，于是输出了三个 `✅`。

**该次结果作废**，已用修正后 SQL 重跑（§4 即修正后的结果，行数 5/200/3 已核非空）。
归档文件内保留了该说明。

> 这正是 R2 要消灭的形态：**比对通过了，但比的是空的东西。**

### 8.2 `exit=$?` 取的是管道末端的状态

`uv run python ... | tail -8; echo "exit=$?"` 中 `$?` 是 `tail` 的退出码，不是 python 的。
若沿用，G2 的 `exit 2` 结论会完全不可信。已改为 `> file 2>&1` 后再取退出码（§5 即修正后结果）。

---

## 9. 全量 diff

```diff
diff --git a/README.md b/README.md
index 6ce4ae7..8a4e46f 100644
--- a/README.md
+++ b/README.md
@@ -32,9 +32,44 @@
 ## 快速开始（Sprint 0 完成后可用）
 
 ```bash
-make setup      # uv 同步依赖 + alembic 迁移 + seed 合成数据
+make setup      # uv 同步依赖
 make up         # docker compose 起 api + postgres
 make test       # unit/integration/security
 make eval       # 评测套件（需 ECE_LLM_* 环境变量）
 make demo       # 演示脚本：PR001 合理性分析 + 无权限用户对照
 ```
+
+## Canonical seed（唯一权威链条）
+
+> **R2**：在此之前，「canonical seed」在仓库里有三份互相不一致的定义 ——
+> `make seed`（无关系）、CI 链条（无关系）、以及测试自己的 `subprocess` 自愈。
+> 没有一份是完整的：`make seed` 建出 428 个实体但 **0 条关系**，于是任何
+> 「重置 → seed → 跑评测」的流程都在空关系图上打分。
+>
+> 下面这条链是**唯一权威**定义。
+
+```bash
+make gen-dataset        # data/dataset/demo.json（确定性，S0.6）
+make db-upgrade         # alembic upgrade head
+make seed               # 实体 + 测试用户 + ACL + 关系 —— 完整入口
+make gen-eval-datasets  # E1-E6 评测数据集（依赖 display_id，必须在 seed 之后）
+uv run python scripts/ingest_demo_docs.py
+```
+
+空库上 `make seed` 的产出：
+
+| 对象 | 期望 |
+|---|---|
+| entities | **428**（`demo:demo` 420 + `api:header` 4 + `demo:seed_departments` 4） |
+| relationships | **1200**（`demo:seed_relationships`，每个 demo PR 恰 6 条） |
+| acl_entries | **3**（`demo:cut-040-test-acl`） |
+
+**幂等**：第二次 `make seed` 与第一次逐字段相同（实体 `created=0`；关系
+delete-then-insert 回同样的 1200 条）。
+
+两点约定：
+
+- `scripts/seed_relationships.py` 保留为兼容 CLI wrapper，内部调用
+  `ece.seed.seed_demo_relationships()` —— **只有一份实现**。
+- E4/E5 runner 在关系 fixture 缺失或不完整时 **`exit 2` 拒绝运行**，
+  而不是对空图打分（那会产出 vacuous pass）。
diff --git a/scripts/run_e4_relationships.py b/scripts/run_e4_relationships.py
index 37e21b0..436b1b2 100644
--- a/scripts/run_e4_relationships.py
+++ b/scripts/run_e4_relationships.py
@@ -11,7 +11,10 @@ cut-040R-2 R40R2.7 (runner ↔ runtime contract fix):
   raised `AttributeError: 'ContextPackage' object has no attribute 'get'`.
   Fix: convert via `.to_dict()`. Test semantics and expectations unchanged.
 
-Note: E4 depends on the relationships table being seeded (scripts/seed_relationships.py).
+Note: E4 depends on the relationships table being seeded. That used to be a
+manual step (`scripts/seed_relationships.py`); `make seed` now performs it, and
+this runner asserts the fixture is present before scoring (R2 / C.3) — an empty
+graph would otherwise yield a VACUOUS pass.
 """
 from __future__ import annotations
 
@@ -22,6 +25,7 @@ from pathlib import Path
 
 from ece.context.assembly import assemble_context
 from ece.db import get_engine
+from ece.seed import demo_relationship_fixture_status
 
 
 def main() -> int:
@@ -30,6 +34,23 @@ def main() -> int:
     parser.add_argument("--base-url", default="http://127.0.0.1:8765")
     args = parser.parse_args()
 
+    # R2 (C.3): environment integrity precondition. Refuses to score against an
+    # empty graph — "0 relationships" would sit inside the E4 bounds and read as
+    # a pass. Does not change datasets, bounds or thresholds.
+    status = demo_relationship_fixture_status(get_engine())
+    if not status["complete"]:
+        print("PRECONDITION FAILURE: demo relationship fixture missing or incomplete.", file=sys.stderr)
+        print(
+            f"  demo:seed_relationships = {status['total']} rows, "
+            f"expected {status['expected_total']} (6 per demo PR).",
+            file=sys.stderr,
+        )
+        if status["deviating_prs"]:
+            print(f"  PRs not matching 6 relationships: {status['deviating_prs'][:8]}", file=sys.stderr)
+        print("  Refusing to run: an empty graph would produce a VACUOUS result.", file=sys.stderr)
+        print("  Fix: run `make seed` (canonical seed now restores relationships).", file=sys.stderr)
+        return 2
+
     data = json.loads(args.data.read_text(encoding="utf-8"))
     cases = data["cases"]
     total = len(cases)
diff --git a/scripts/run_e5_temporal.py b/scripts/run_e5_temporal.py
index 995c0f6..6995ef0 100644
--- a/scripts/run_e5_temporal.py
+++ b/scripts/run_e5_temporal.py
@@ -27,6 +27,7 @@ from pathlib import Path
 
 from ece.context.assembly import assemble_context
 from ece.db import get_engine
+from ece.seed import demo_relationship_fixture_status
 
 
 def main() -> int:
@@ -35,6 +36,24 @@ def main() -> int:
     parser.add_argument("--base-url", default="http://127.0.0.1:8765")
     args = parser.parse_args()
 
+    # R2 (C.3): environment integrity precondition. E5 asserts a per-PR count of
+    # 6; against an empty graph every case reports 0 and the suite scores 0% —
+    # or worse, a bounds-only case reads as a pass. Refuse rather than score.
+    # Does not change the dataset, expected_count or thresholds.
+    status = demo_relationship_fixture_status(get_engine())
+    if not status["complete"]:
+        print("PRECONDITION FAILURE: demo relationship fixture missing or incomplete.", file=sys.stderr)
+        print(
+            f"  demo:seed_relationships = {status['total']} rows, "
+            f"expected {status['expected_total']} (6 per demo PR).",
+            file=sys.stderr,
+        )
+        if status["deviating_prs"]:
+            print(f"  PRs not matching 6 relationships: {status['deviating_prs'][:8]}", file=sys.stderr)
+        print("  Refusing to run: an empty graph would produce a VACUOUS result.", file=sys.stderr)
+        print("  Fix: run `make seed` (canonical seed now restores relationships).", file=sys.stderr)
+        return 2
+
     data = json.loads(args.data.read_text(encoding="utf-8"))
     cases = data["cases"]
     total = len(cases)
diff --git a/scripts/seed_relationships.py b/scripts/seed_relationships.py
index 7e7df62..6d437a9 100644
--- a/scripts/seed_relationships.py
+++ b/scripts/seed_relationships.py
@@ -1,21 +1,17 @@
-"""Seed demo relationships (cut-009 path A — unlocks E4/E5 evaluation).
+"""Seed demo relationships — thin CLI wrapper over `ece.seed.seed_demo_relationships`.
 
-For each PR in demo seed, create 5 basic relationships:
-- BELONGS_TO department  (procurement/finance/sales/D01)
-- SUBMITTED_BY person
-- SELECTS supplier
-- CONTAINS product
-- SUBJECT_TO policy
+R2: this used to hold the ONLY implementation. `make seed` never called it, so
+rebuilding the DB produced 428 entities and ZERO relationships, and E4/E5 then
+measured an empty graph. The logic now lives in `src/ece/seed.py` so that
+`run_seed()` (the canonical entrypoint) and this script share ONE implementation
+instead of two copies that drift apart.
 
-Idempotent thanks to UNIQUE INDEX uq_relationships_triple
-(on src_entity_id, relation, dst_entity_id, COALESCE(valid_from, '0001-01-01'))
-from migration 0002. Re-runs skip existing triples via ON CONFLICT DO NOTHING.
-
-Also seeds 4 department entities (extracted from demo person attributes;
-no separate department entities exist in current demo seed).
-
-Run after `make seed`:
+Kept as a standalone command because existing callers and docs use it:
     uv run python scripts/seed_relationships.py
+and three integration tests shell out to it, depending on the exit-code contract
+(0 = seeded, 1 = could not seed) and on the `Total relationships in DB: N` line.
+
+Prefer `make seed`, which now performs this step automatically.
 
 Per DATA_MODEL.md §2 + ontology whitelist (ece/domain_packs/procurement/ontology.py).
 """
@@ -23,164 +19,37 @@ from __future__ import annotations
 
 import sys
 
-from sqlalchemy import text
-
 from ece.db import get_engine
-from ece.entities.pipeline import upsert_entity, upsert_relationship
-
-# Departments inferred from demo person attributes (seed.py)
-DEPARTMENTS = ["procurement", "finance", "sales", "D01"]
-
-
-# Explicit allowlist of the source_systems THIS fixture builds relationships on.
-#
-# cut-040R-2 S1 fix: `_fetch_display_ids` used to select by `entity_type` alone,
-# so it annexed ANY entity of the same type. Adding the V0 spike fixture (a
-# purchase_request) silently gave it six demo relationships and broke the
-# eval-asset guard G2. Scoping by an explicit allowlist expresses the intent
-# ("this fixture only touches its own entities") and cannot annex foreign
-# fixtures — same pattern as the wipe-predicate fix (precise predicate, never a
-# blacklist / LIKE sweep).
-_FIXTURE_SOURCE_SYSTEMS: dict[str, str] = {
-    "purchase_request": "demo:demo",
-    "supplier": "demo:demo",
-    "product": "demo:demo",
-    "policy": "demo:demo",
-    "department": "demo:seed_departments",
-    "person": "api:header",
-}
-
-
-def _fetch_display_ids(engine, entity_type: str) -> list[str]:
-    """Fetch display_ids for an entity type, SCOPED to this fixture's own
-    source_system (see _FIXTURE_SOURCE_SYSTEMS). Sorted.
-
-    Fails loudly on an unmapped entity_type rather than silently reverting to an
-    unscoped scan.
-    """
-    source_system = _FIXTURE_SOURCE_SYSTEMS.get(entity_type)
-    if source_system is None:
-        raise KeyError(
-            f"no fixture source_system mapped for entity_type={entity_type!r}. "
-            "Add it to _FIXTURE_SOURCE_SYSTEMS — do NOT fall back to an unscoped "
-            "scan (that annexes foreign fixtures)."
-        )
-    with engine.connect() as conn:
-        rows = conn.execute(
-            text(
-                "SELECT display_id FROM entities "
-                "WHERE entity_type = :t AND source_system = :s ORDER BY display_id"
-            ),
-            {"t": entity_type, "s": source_system},
-        ).fetchall()
-    return [r[0] for r in rows]
-
-
-def _seed_departments(engine) -> list[str]:
-    """Seed 4 department entities (no separate dept entities in demo)."""
-    for dept in DEPARTMENTS:
-        upsert_entity(
-            engine,
-            entity_type="department",
-            name=dept.capitalize() if dept != "D01" else "D01 Department",
-            source_system="demo:seed_departments",
-            source_id=f"dept:{dept}",
-            attributes={"name": dept},
-        )
-    return _fetch_display_ids(engine, "department")
+from ece.seed import seed_demo_relationships
 
 
 def main() -> int:
     engine = get_engine()
 
-    # 1. Seed departments first (needed for BELONGS_TO)
     print("Seeding 4 department entities...")
-    dept_ids = _seed_departments(engine)
-    if not dept_ids:
-        print("ERROR: failed to seed departments", file=sys.stderr)
-        return 1
+    result = seed_demo_relationships(engine)
 
-    # 2. Fetch PR + target entity display_ids
-    pr_ids = _fetch_display_ids(engine, "purchase_request")
-    if not pr_ids:
-        print("ERROR: no PRs found; run `make seed` first", file=sys.stderr)
+    if not result.get("ok"):
+        print(f"ERROR: {result.get('error')}", file=sys.stderr)
         return 1
 
-    people_ids = _fetch_display_ids(engine, "person")
-    supplier_ids = _fetch_display_ids(engine, "supplier")
-    product_ids = _fetch_display_ids(engine, "product")
-    policy_ids = _fetch_display_ids(engine, "policy")
-
-    if not (people_ids and supplier_ids and product_ids and policy_ids):
-        print(
-            "ERROR: missing entity types (need person/supplier/product/policy)",
-            file=sys.stderr,
-        )
-        return 1
+    removed = result["removed"]
+    if removed:
+        print(f"  Removed {removed} prior 'demo:seed_relationships' rows (canonical reseed)")
 
-    # 3. For each PR, create 6 relationships (cyclic selection for variety)
-    #
-    # NOTE (cut-040R-2 Final Evidence Repair): this list has SIX entries, not
-    # five — the 6th is the deliberate "2nd submitter for variety" added in
-    # cut-009. The old comment said "5", and that stale count propagated into
-    # `gen_eval_datasets.py` (E5 `expected_count`) and its docstring. The
-    # implemented contract is 6 non-temporal relationships per PR.
-    #
-    # The fixture is made CANONICAL below (delete-then-insert scoped to this
-    # script's own source_system): repeated runs, or runs interleaved with other
-    # tests that mutate the person/supplier lists, used to leave 7-8 rows behind
-    # and silently invalidate E5's expected count.
-    counters: dict[str, int] = {
-        "BELONGS_TO": 0,
-        "SUBMITTED_BY": 0,
-        "SELECTS": 0,
-        "CONTAINS": 0,
-        "SUBJECT_TO": 0,
-    }
-
-    with engine.begin() as conn:
-        deleted = conn.execute(
-            text("DELETE FROM relationships WHERE source_system = :s"),
-            {"s": "demo:seed_relationships"},
-        ).rowcount
-    if deleted:
-        print(f"  Removed {deleted} prior 'demo:seed_relationships' rows (canonical reseed)")
-
-    for i, pr_id in enumerate(pr_ids):
-        rel_specs = [
-            ("BELONGS_TO", dept_ids[i % len(dept_ids)]),
-            ("SUBMITTED_BY", people_ids[i % len(people_ids)]),
-            ("SELECTS", supplier_ids[i % len(supplier_ids)]),
-            ("CONTAINS", product_ids[i % len(product_ids)]),
-            ("SUBMITTED_BY", people_ids[(i + 1) % len(people_ids)]),  # 2nd submitter for variety
-            ("SUBJECT_TO", policy_ids[i % len(policy_ids)]),
-        ]
-        # Dedupe rel_specs in case of cyclic collisions
-        seen_targets: set[tuple[str, str]] = set()
-        for rel_type, target in rel_specs:
-            key = (rel_type, target)
-            if key in seen_targets:
-                continue
-            seen_targets.add(key)
-            inserted, reason = upsert_relationship(
-                engine,
-                src_display_id=pr_id,
-                relation=rel_type,
-                dst_display_id=target,
-                source_system="demo:seed_relationships",
-            )
-            if inserted:
-                counters[rel_type] += 1
-
-    # 4. Report
-    print(f"\nSeeded relationships from {len(pr_ids)} PRs:")
-    for rel, count in counters.items():
+    inserted: dict[str, int] = result["inserted_by_type"]  # type: ignore[assignment]
+    print(f"\nSeeded relationships from {result['prs']} PRs:")
+    for rel, count in inserted.items():
         print(f"  {rel}: {count} new insertions")
 
-    with engine.connect() as conn:
-        total = conn.execute(text("SELECT count(*) FROM relationships")).scalar()
-    print(f"Total relationships in DB: {total}")
+    rejected: list[str] = result["rejected"]  # type: ignore[assignment]
+    if rejected:
+        print(f"  REJECTED {len(rejected)} relationship(s):")
+        for r in rejected[:5]:
+            print(f"    {r}")
 
+    # Kept verbatim: existing tooling and archived stdout compare on this line.
+    print(f"Total relationships in DB: {result['total_in_db']}")
     return 0
 
 
diff --git a/src/ece/seed.py b/src/ece/seed.py
index 54262af..e9c7399 100644
--- a/src/ece/seed.py
+++ b/src/ece/seed.py
@@ -24,7 +24,7 @@ from pathlib import Path
 from sqlalchemy import text
 
 from ece.db import get_engine
-from ece.entities.pipeline import upsert_entity
+from ece.entities.pipeline import upsert_entity, upsert_relationship
 
 # Map from gen_dataset top-level key -> entity_type (per PRD §27).
 # Some lists contain str (name only), others contain dict (id + fields).
@@ -360,6 +360,237 @@ def _seed_entity_departments(engine) -> int:
     return total
 
 
+# ─────────────────────────────────────────────────────────────────────────────
+# Demo relationship fixture
+#
+# R2: the relationship seeding logic used to live ONLY in
+# `scripts/seed_relationships.py`, a standalone process-level script. `make seed`
+# therefore produced 428 entities and ZERO relationships, so any workflow that
+# rebuilt the DB and ran the eval suites measured an empty graph. The logic is
+# now a shared function here — `run_seed()` calls it, and the script is a thin
+# wrapper over it (one implementation, not two copies that drift).
+# ─────────────────────────────────────────────────────────────────────────────
+
+DEMO_RELATIONSHIP_SOURCE_SYSTEM = "demo:seed_relationships"
+
+# Departments inferred from demo person attributes (seed.py)
+DEMO_DEPARTMENTS = ["procurement", "finance", "sales", "D01"]
+
+# Canonical fixture contract: SIX relationships per demo PR. The 6th is the
+# deliberate "2nd submitter for variety" — see the rel_specs list below. This
+# count is what the frozen E4/E5 datasets assert (`expected_count`).
+EXPECTED_RELS_PER_DEMO_PR = 6
+
+# Explicit allowlist of the source_systems THIS fixture builds relationships on.
+#
+# cut-040R-2 S1 fix: `_fetch_display_ids` used to select by `entity_type` alone,
+# so it annexed ANY entity of the same type. Adding the V0 spike fixture (a
+# purchase_request) silently gave it six demo relationships and broke the
+# eval-asset guard G2. Scoping by an explicit allowlist expresses the intent
+# ("this fixture only touches its own entities") and cannot annex foreign
+# fixtures — same pattern as the wipe-predicate fix (precise predicate, never a
+# blacklist / LIKE sweep).
+_FIXTURE_SOURCE_SYSTEMS: dict[str, str] = {
+    "purchase_request": "demo:demo",
+    "supplier": "demo:demo",
+    "product": "demo:demo",
+    "policy": "demo:demo",
+    "department": "demo:seed_departments",
+    "person": "api:header",
+}
+
+
+def _fetch_display_ids(engine, entity_type: str) -> list[str]:
+    """Fetch display_ids for an entity type, SCOPED to this fixture's own
+    source_system (see _FIXTURE_SOURCE_SYSTEMS). Sorted.
+
+    Fails loudly on an unmapped entity_type rather than silently reverting to an
+    unscoped scan.
+    """
+    source_system = _FIXTURE_SOURCE_SYSTEMS.get(entity_type)
+    if source_system is None:
+        raise KeyError(
+            f"no fixture source_system mapped for entity_type={entity_type!r}. "
+            "Add it to _FIXTURE_SOURCE_SYSTEMS — do NOT fall back to an unscoped "
+            "scan (that annexes foreign fixtures)."
+        )
+    with engine.connect() as conn:
+        rows = conn.execute(
+            text(
+                "SELECT display_id FROM entities "
+                "WHERE entity_type = :t AND source_system = :s ORDER BY display_id"
+            ),
+            {"t": entity_type, "s": source_system},
+        ).fetchall()
+    return [r[0] for r in rows]
+
+
+def _seed_fixture_departments(engine) -> list[str]:
+    """Seed 4 department entities (no separate dept entities in demo).
+
+    NOTE (R2-obs-2, deliberately NOT changed by R2): `upsert_entity` is called
+    without an explicit `display_id`, so D001..D004 are still allocated by the
+    global max+1 allocator. No current consumer reads `D0xx` display_ids (E1–E5
+    never reference them), so this is latent, not live. Fixing it was ruled out
+    of R2's scope.
+    """
+    for dept in DEMO_DEPARTMENTS:
+        upsert_entity(
+            engine,
+            entity_type="department",
+            name=dept.capitalize() if dept != "D01" else "D01 Department",
+            source_system="demo:seed_departments",
+            source_id=f"dept:{dept}",
+            attributes={"name": dept},
+        )
+    return _fetch_display_ids(engine, "department")
+
+
+def seed_demo_relationships(engine) -> dict[str, object]:
+    """Seed the demo relationship fixture (canonical, idempotent, self-scoped).
+
+    For each demo PR, creates 6 relationships:
+    BELONGS_TO department / SUBMITTED_BY person / SELECTS supplier /
+    CONTAINS product / SUBMITTED_BY (2nd person) / SUBJECT_TO policy.
+
+    Idempotent via DELETE-then-INSERT scoped to THIS fixture's own
+    `source_system` (the `uq_relationships_triple` unique index is the backstop).
+    The delete MUST stay scoped: a previous version relied on ON CONFLICT alone
+    and leftover rows from interleaved tests silently invalidated E5's
+    per-PR expected count.
+
+    Prerequisite: entities (incl. `api:header` persons from `seed_test_users`)
+    must already exist — hence `run_seed()` calls `seed_test_users()` first.
+
+    Returns {"ok", "error"?, "departments", "removed", "inserted_by_type",
+             "rejected", "total_in_db"}.
+    """
+    dept_ids = _seed_fixture_departments(engine)
+    if not dept_ids:
+        return {"ok": False, "error": "failed to seed departments"}
+
+    pr_ids = _fetch_display_ids(engine, "purchase_request")
+    if not pr_ids:
+        return {"ok": False, "error": "no purchase_request entities; run `make seed` first"}
+
+    people_ids = _fetch_display_ids(engine, "person")
+    supplier_ids = _fetch_display_ids(engine, "supplier")
+    product_ids = _fetch_display_ids(engine, "product")
+    policy_ids = _fetch_display_ids(engine, "policy")
+
+    if not (people_ids and supplier_ids and product_ids and policy_ids):
+        return {
+            "ok": False,
+            "error": "missing entity types (need person/supplier/product/policy)",
+        }
+
+    counters: dict[str, int] = {
+        "BELONGS_TO": 0,
+        "SUBMITTED_BY": 0,
+        "SELECTS": 0,
+        "CONTAINS": 0,
+        "SUBJECT_TO": 0,
+    }
+    rejected: list[str] = []
+
+    with engine.begin() as conn:
+        deleted = conn.execute(
+            text("DELETE FROM relationships WHERE source_system = :s"),
+            {"s": DEMO_RELATIONSHIP_SOURCE_SYSTEM},
+        ).rowcount
+
+    for i, pr_id in enumerate(pr_ids):
+        rel_specs = [
+            ("BELONGS_TO", dept_ids[i % len(dept_ids)]),
+            ("SUBMITTED_BY", people_ids[i % len(people_ids)]),
+            ("SELECTS", supplier_ids[i % len(supplier_ids)]),
+            ("CONTAINS", product_ids[i % len(product_ids)]),
+            ("SUBMITTED_BY", people_ids[(i + 1) % len(people_ids)]),  # 2nd submitter for variety
+            ("SUBJECT_TO", policy_ids[i % len(policy_ids)]),
+        ]
+        # Dedupe rel_specs in case of cyclic collisions
+        seen_targets: set[tuple[str, str]] = set()
+        for rel_type, target in rel_specs:
+            key = (rel_type, target)
+            if key in seen_targets:
+                continue
+            seen_targets.add(key)
+            inserted, reason = upsert_relationship(
+                engine,
+                src_display_id=pr_id,
+                relation=rel_type,
+                dst_display_id=target,
+                source_system=DEMO_RELATIONSHIP_SOURCE_SYSTEM,
+            )
+            if inserted:
+                counters[rel_type] += 1
+            else:
+                rejected.append(f"{pr_id} -{rel_type}-> {target}: {reason}")
+
+    with engine.connect() as conn:
+        total = conn.execute(text("SELECT count(*) FROM relationships")).scalar()
+
+    return {
+        "ok": True,
+        "prs": len(pr_ids),
+        "departments": len(dept_ids),
+        "removed": deleted,
+        "inserted_by_type": dict(counters),
+        "rejected": rejected,
+        "total_in_db": int(total or 0),
+    }
+
+
+def demo_relationship_fixture_status(engine) -> dict[str, object]:
+    """Report whether the demo relationship fixture is present AND canonical.
+
+    R2 (C.3): consumers that would otherwise measure an EMPTY graph (E4/E5)
+    call this so a missing fixture fails loudly instead of producing a vacuous
+    result.
+
+    The per-PR deviation check alone is NOT sufficient: `HAVING count(*) != 6`
+    only sees PRs that HAVE relationship rows, so it silently ignores the worst
+    case (a PR with zero relationships). The total is therefore also reconciled
+    against `<demo PR entities> × EXPECTED_RELS_PER_DEMO_PR`.
+
+    Returns {"total", "expected_total", "deviating_prs", "complete"}.
+    """
+    with engine.connect() as conn:
+        total = conn.execute(
+            text("SELECT count(*) FROM relationships WHERE source_system = :s"),
+            {"s": DEMO_RELATIONSHIP_SOURCE_SYSTEM},
+        ).scalar_one()
+        demo_prs = conn.execute(
+            text(
+                "SELECT count(*) FROM entities "
+                "WHERE entity_type = 'purchase_request' AND source_system = 'demo:demo'"
+            )
+        ).scalar_one()
+        deviating = conn.execute(
+            text(
+                """
+                SELECT s.display_id, count(*) AS n
+                FROM relationships r
+                JOIN entities s ON s.id = r.src_entity_id
+                WHERE s.entity_type = 'purchase_request'
+                  AND s.source_system = 'demo:demo'
+                GROUP BY s.display_id
+                HAVING count(*) != :want
+                ORDER BY s.display_id
+                """
+            ),
+            {"want": EXPECTED_RELS_PER_DEMO_PR},
+        ).fetchall()
+
+    expected_total = int(demo_prs) * EXPECTED_RELS_PER_DEMO_PR
+    return {
+        "total": int(total),
+        "expected_total": expected_total,
+        "deviating_prs": [(r[0], r[1]) for r in deviating],
+        "complete": bool(demo_prs) and int(total) == expected_total and not deviating,
+    }
+
+
 def run_seed() -> dict[str, object]:
     """Entry: load demo.json, upsert all entities, return summary.
 
@@ -369,6 +600,13 @@ def run_seed() -> dict[str, object]:
       idempotent replay self-heals
     - seed_acl_entries() seeds 3 acl_entries for E2 'acl_explicit' cases
       (R40.1a)
+
+    R2 addition:
+    - seed_demo_relationships() — relationship seeding moved in from
+      scripts/seed_relationships.py, so this entrypoint now produces a COMPLETE
+      environment. Order matters: it must run after seed_test_users(), because
+      the fixture's SUBMITTED_BY edges target the `api:header` persons that
+      function creates.
     """
     engine = get_engine()
     out = seed_from_demo_json(engine, Path("data/dataset/demo.json"))
@@ -379,6 +617,15 @@ def run_seed() -> dict[str, object]:
     # re-injected here.
     # cut-040 R40.1a: seed 3 acl_entries for E2 explicit-acl cases
     out["acl_entries"] = seed_acl_entries(engine)
+    # R2: relationships. Fails loudly rather than leaving a half-built
+    # environment — a silent empty graph is what made E4/E5 vacuous.
+    relationships = seed_demo_relationships(engine)
+    if not relationships.get("ok"):
+        raise RuntimeError(
+            "canonical seed incomplete — relationship seeding failed: "
+            f"{relationships.get('error')}"
+        )
+    out["relationships"] = relationships
     return out
 
 
@@ -394,4 +641,18 @@ if __name__ == "__main__":
     if skipped_list:
         for s in skipped_list[:5]:
             print(f"  skipped: {s}")
+    # R2: report the relationship stage so `make seed` output shows the fixture
+    # is complete (this line is also what makes an incomplete seed auditable).
+    rels: dict[str, object] = result["relationships"]  # type: ignore[assignment]
+    inserted: dict[str, int] = rels["inserted_by_type"]  # type: ignore[assignment]
+    rejected_list: list[str] = rels["rejected"]  # type: ignore[assignment]
+    print(
+        f"Relationships: {inserted} "
+        f"(replaced {rels['removed']} prior rows, {rels['departments']} departments)"
+    )
+    print(f"Total relationships in DB: {rels['total_in_db']}")
+    if rejected_list:
+        print(f"  REJECTED {len(rejected_list)} relationship(s):")
+        for r in rejected_list[:5]:
+            print(f"    {r}")
     sys.exit(0)
```

---

## 附. 归档清单（`ece/reports/r2-verification/`）

| 文件 | 内容 |
|---|---|
| `00-pre-reset.txt` | 重置前三表计数 |
| `01-reset.txt` | alembic downgrade/upgrade 全量输出 + 空库确认 |
| `02-first-seed.txt` | gen-dataset md5 + 第一次 `make seed` |
| `03-invariants.txt` | B/C/D 不变量逐项 |
| `04-idempotency.txt` | 幂等性逐字比对（含 8.1 的作废说明）|
| `05-e4-e5-precondition.txt` | G1/G2 正反两面 |
| `06-pytest.txt` | 全量 pytest 原始输出 |
| `07-post-pytest.txt` | pytest 之后的 fixture 完整性 |
| `08-restore-spike.txt` | spike fixture 恢复 + self-check |
| `09-e1-e2-e3.txt` | E1/E2/E3 回归对照 |
| `10-diff-scope.txt` | 改动面 + 禁区零改动证明 |
| `11-full-diff.patch` | 全量 diff |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: R2 PASS —— 待审。**未进入 S2。**
