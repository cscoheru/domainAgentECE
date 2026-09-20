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

## 10. R2.1 — Codex 唯一 MINOR CONDITION 的处置

### 10.1 裁定与条件

Codex 对 §0–§9 的裁定是 **R2 = PASS WITH MINOR CONDITIONS**：

| 裁定项 | 结论 |
|---|---|
| G6 负向对照 | **ACCEPT** —— 保留 |
| README 那一行 | **ACCEPT** —— 保留，不构成 scope creep |
| seed 原子事务边界 | **FOLLOW-UP** —— 明确不阻塞 R2、不建议扩大范围 |
| **`rejected` 是否应使 seed 失败** | ⚠️ **唯一代码级条件** |

条件原文给的是二选一：(a) 让 `rejected != []` 导致失败；或 (b) 证明
`upsert_relationship()` 的 rejected 分支在 canonical fixture 下不可能发生，并说明理由。

**取值：(a)。** (b) 不成立 —— 理由见 10.2，那正是不能选它的原因。

### 10.2 先回答一个更基础的问题：`ok=True` 究竟证明了什么

裁定问的是 `rejected` 的语义。但回答之前必须先问：**当前 `ok=True` 本身就可靠吗？**

实测（`11-probe-inserted-semantics.txt`，命令 `uv run python /tmp/probe_noop2.py`）：

```
probe triple: (PR001)-[SUBMITTED_BY]->(S24-P-001)
1st call -> inserted=True reason='ok'
2nd call -> inserted=True reason='ok'   <-- conflicts with the 1st
rows ACTUALLY tagged 'probe:noop': 1   <-- 2 calls reported inserted=True
```

**两次调用都报 `inserted=True`，库里只有一行。** 原因是两条独立的机制叠加：

1. `upsert_relationship()`（`src/ece/entities/pipeline.py:230`）在
   `ON CONFLICT DO NOTHING` 什么都没写的情况下，**仍然返回 `(True, "ok")`** ——
   而它的 docstring 写的是 `inserted=True: row written`。
2. `uq_relationships_triple`（migration `0002`）的键是
   `(src_entity_id, relation, dst_entity_id, COALESCE(valid_from, …))` ——
   **不含 `source_system`**。所以另一个 fixture 占住同一条 triple 时，我们的
   DELETE（按自身 `source_system` 限定）删不掉它，INSERT 静默 no-op。

后果：`inserted_by_type` 会**照常每 PR +1**，而库里我方的行数少一条。
**只看计数器，`rejected == []` 且"计数正确"完全可能与 fixture 不完整共存。**

所以正确的修复形态不是「再加一个 if」，而是**把判据从计数器换成库内实发行数**。

### 10.3 修复形态

`src/ece/seed.py::seed_demo_relationships()` 末尾新增两条彼此独立的判据：

```python
expected = len(pr_ids) * EXPECTED_RELS_PER_DEMO_PR

if rejected:                       # 条件①：被拒边就是失败
    problems.append(f"{len(rejected)} relationship(s) REJECTED …")

owned = SELECT count(*) FROM relationships
        WHERE source_system = 'demo:seed_relationships'

if int(owned) != expected:         # 条件②：以库内实况为准，不看计数器
    problems.append("fixture incomplete: {owned} rows … while {n} insert(s) were reported …")

result = { "ok": len(problems) == 0, …, }
if problems:
    result["error"] = " | ".join(problems)
```

①直接回应裁定；②把 10.2 发现的那条静默路径一并关掉 —— 两条都属于
「以"环境是否完整"为准，而不是以"函数是否跑完"为准」。

返回键集不变（只在不完整时多一个 `error`），因此 `run_seed()` 既有的
`if not relationships.get("ok"): raise RuntimeError(...)` **无需改动**即生效。

配套改动两处：

- `scripts/seed_relationships.py`：把 REJECTED 的打印**移到** `ok` 判断之前
  （否则失败路径上这些明细不可达，只剩一行 error），docstring 补充 exit 1 的新含义。
- `tests/integration/test_canonical_seed_completeness.py`：新增 **G7 / G8** 两个负向对照。

### 10.4 ⭐ 负向对照：新 guard 对旧代码确实失败

把 `src/ece/seed.py` `git stash` 回改动前，只跑 G7/G8（`04-guards-bite-old-code.txt`）：

```
G7（旧码）AssertionError: … got {'ok': True, 'prs': 200, 'departments': 4,
    'removed': 1200,
    'inserted_by_type': {'BELONGS_TO': 199, 'SUBMITTED_BY': 400, …},
    'rejected': ['PR001 -BELONGS_TO-> D001: ontology rejected: forced by test_g7'],
    'total_in_db': 1203}
  assert True is False

G8（旧码）AssertionError: … got {'ok': True, 'removed': 1199,
    'inserted_by_type': {'BELONGS_TO': 200, …},   ← 计数器说 200
    'rejected': [], 'total_in_db': 1204}
  assert True is False
```

这两段**旧代码的输出本身就是缺陷的证据**：

- **G7**：`rejected` 里明明躺着那条被拒边，`ok` 是 `True`，`BELONGS_TO` 只有 199 条
  —— 即裁定所担心的「1200 期望 / 1199 交付 / `make seed` 仍显示成功」，**实测复现**。
- **G8**：`inserted_by_type.BELONGS_TO = 200`，而实际只写入 199 条
  —— **计数器撒谎，seed 说成功**。

没有这一步，「`ok is False`」之类的断言就只是"看起来在检查"。

### 10.5 验证（全部为本次实测）

| 项目 | 结果 |
|---|---|
| `scripts/seed_relationships.py`（健康环境） | **exit 0**，`Total relationships in DB: 1204` |
| 同上，外部 fixture 占走 1 条 triple | **exit 1**，`ERROR: fixture incomplete: 1199 rows tagged … expected 1200 (200 PRs x 6) while 1200 insert(s) were reported. A shortfall with no rejections means a foreign source_system already owns those triples.` |
| `make seed` | **exit 0**；`Relationships: {BELONGS_TO: 200, SUBMITTED_BY: 400, SELECTS: 200, CONTAINS: 200, SUBJECT_TO: 200}` = 1200；0 rejected |
| **全量 pytest** | **363 passed, 3 skipped, 0 failed**（R2 基线 361 + G7/G8 两条） |
| G5/G6/G7/G8 单独跑 / 整模块跑 | 均通过（新增模块级前置，见 10.7 说明） |
| E4 / E5 | 各 30/30 = **100.0%**，exit 0（未手工补种） |
| E1 / E2 / E3 | **98.5% / 0 暴露 0 失败（61 cases）/ 100.0%** —— 与 R2 基线逐项一致 |
| `ruff` + `mypy` | `All checks passed!` / `Success: no issues found in 2 source files` |
| `lint-imports` | **Contracts: 2 kept, 0 broken** |
| 改动范围 | **恰好 3 个文件**（`src/ece/seed.py`、`scripts/seed_relationships.py`、`tests/integration/test_canonical_seed_completeness.py`） |

数据面未变（关系仍是 1200、每 PR 恰 6 条、幂等），E1/E2/E3 逐项复现 R2 基线 ——
所以 R2.1 只改了**失败语义**，没有改成功路径的任何产出。

### 10.6 新登记的观察：R2-obs-3（`upsert_relationship` 的返回契约）

`pipeline.py:174` 写的是 `inserted=True: row written`，实测（10.2）不成立：
no-op 的冲突插入与真正写入**返回值相同**。

**本次刻意不改**，理由：

- `upsert_relationship` 是共享基础设施，有多处调用者（`test_s12`、`test_s24_e2`、
  `test_s4_5_temporal`、`seed_temporal_roles.py`、`seed_v0_spike_fixture.py`）。
- 正确的修法是三态返回（inserted / already-present / rejected），属重构，
  落在裁定「不要为了 FOLLOW-UP 扩大 R2」的边界之外。
- 现有的 `tests/integration/test_seed_relationships.py:150` 断言是
  `assert ins1 or not ins2` —— 在 `ins1=True` 时**恒真**，与它自己上方
  「Only one should return True」的注释矛盾，因此**测不出**这个问题。
  这一条同样只登记、不改：它属于既有的弱断言，改它需要先动共享基础设施。

**影响面**：canonical seed 侧已由 10.3 的判据②覆盖（`owned` 对账）；
残余风险限于其他直接读 `inserted` 返回值的调用点。

### 10.7 测试自足性的一处补强

`test_canonical_seed_completeness.py` 新增模块级前置：若 fixture 不完整则先 `run_seed()`。

这不是被 R2 否定的「测试自愈」—— 那次否掉的是 **E4/E5 runner 在评测中途修图再打分**。
这里是**断言之前**建立前置，断言本身仍然检验环境状态；环境真的坏掉时
`run_seed()` 会 raise 而非返回半成品。动机是仓库自己的教训
（`reports/cut-013-report.md`：「autouse fixtures must be SELF-SUFFICIENT」）：
G8 需要先存在一条 demo BELONGS_TO 边，单独跑时不应因别的测试文件洗过库而假失败。

### 10.8 Codex §9 的架构边界观察（建议纳入 closeout）

裁定 §9 指出 R2 证明了三个东西**必须各自独立、不再互相偷偷修复**：

```
Dataset            ── 定义「测什么」
Canonical Seed     ── 定义「测试环境是什么」
Evaluation Runner  ── 定义「怎么测」
```

E4/E5 runner 现在的职责被收窄为「检查环境 → 不满足则拒绝评分（exit 2）」，
而不再是「发现关系没了 → subprocess 补种 → 自己修好环境 → PASS」。

**本报告按 §9 的要求把它作为 closeout 候选条目记录在此，未改写任何仓库文档**
（README 的 canonical seed 一节已含 E4/E5 拒绝运行的表述；是否要在 closeout 里
正式固化这条边界，留给 R2 终审后的 closeout 决定）。

### 10.9 本次未改动（明确）

- `run_seed()` 的事务边界（裁定 §6 明确列为 **follow-up / hardening**，不扩大范围）
- `R2-obs-1`（`scripts/seed_temporal_roles.py` 孤儿脚本）与
  `R2-obs-2`（`department` 的 `D001..D004` 仍走全局 max+1）—— 状态不变
- `upsert_relationship()` 的返回契约（见 10.6）
- 任何禁区文件：V3 PRD / V0 Execution Spec / Kernel Boundary / `rules.py` /
  ontology / permission semantics / E1–E5 数据集 / evaluation threshold /
  Context / Decision / Evidence —— 全部 `git status` 为空

### 10.10 R2.1 归档（`ece/reports/r2-verification-r21/`）

| 文件 | 内容 |
|---|---|
| `01-cli-wrapper-ok.txt` | wrapper CLI 正常路径 exit 0 |
| `02-cli-wrapper-incomplete.txt` | 外部占位下 CLI exit 1 + 诊断 |
| `03-make-seed.txt` | `make seed` 输出（1200 / 0 rejected） |
| `04-guards-bite-old-code.txt` | ⭐ 新 guard 对改动前代码的失败输出 |
| `05-pytest-full.txt` | 全量 pytest 原始输出 |
| `06-e4.txt` / `07-e5.txt` | E4 / E5 |
| `08-e1.txt` / `09-e2.txt` / `10-e3.txt` | E1 / E2 / E3 回归 |
| `11-probe-inserted-semantics.txt` | ⭐ `inserted=True` 语义探针 |
| `12-r21-diff.patch` | 本次全量 diff |
| `13-scope.txt` | 改动范围（3 个文件） |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: R2 PASS WITH MINOR CONDITIONS —— 唯一代码级条件已处置（§10）。
事务边界按裁定列为 follow-up。**未进入 S2。**
