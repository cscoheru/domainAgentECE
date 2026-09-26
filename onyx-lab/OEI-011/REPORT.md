# OEI-011 收口报告 — 咨询内容补全（行业轴补齐 + 有界增量 + facets 真正可用）

- 状态：**已完成**，等 `VERDICT.md`（PASS → 关闭；FAIL → R1 返工）
- 任务书：`onyx-lab/OEI-011/TASK.md`（**v1.1**）
- 提交：`c30e50e`（父 `a463658` = OEI-010 的 HEAD），**未 push**
- 日期：2026-09-25
- 一句话：36 个既有对象的行业轴从 24 个空值补到 **0 个空值**，按有界规则新增 **9** 条到 **45** 条，
  词表加 `cross_industry`（**只加这一个**），facets 的每个值都有 ≥2 命中，`/library` 与 `/facets`
  的**键集合一字未改**。

> 本报告先前的版本是 **BLOCKED**（v1 任务书自相矛盾）。v1.1 解冻了第四处断言点，本报告是
> 真实执行后的收口。BLOCKED 的复现材料**保留**在 `evidence/00-blocked-contract-conflict.json`
> 与 `evidence/00b-assertion-inventory.txt` —— TASK v1.1 §1.5 本身就是引用它们的。

---

## 0. 本刀实际改了什么

| 文件 | 改动 | 授权 |
|---|---|---|
| `src/ece/consulting/seed/consulting_objects.json` | 36 → 45 条；24 条补 `client_industry`；9 条新增 | §8 |
| `src/ece/consulting/metadata.py` | `ALLOWED_INDUSTRIES` **只加** `cross_industry` 一项（+ 7 行注释） | §8 |
| `docs/API.md` | §11（36→45 的来历 + 行业轴语义小节）、§12（词表 11 项） | §8 |
| `docs/DATA_MODEL.md` | `idx_memories_scope_owner` 列序订正（步骤 0.2） | §8 |
| `TASKS.md` | 附录 Q（Q.1–Q.6） | §8 |
| `tests/integration/test_s32_assembly.py` | 步骤 0.1（item_kind 断言） | 步骤 0.1 |
| `tests/unit/test_consulting_documents.py` | 2 处 `== 36` → `>= 36` | §3.4 |
| `tests/unit/test_consulting_engine_merge.py` | 1 处 `== 36` → `>= 36` | §3.4 |
| `tests/unit/test_consulting_seed_count.py` | 6 处 `==` → `>=` + docstring + 自洽断言 | §3.4 |

`git diff --stat a463658 HEAD` = **9 files, +593 −41**。零 diff：`pyproject.toml`、`uv.lock`、
`demos/`（SPA）、`src/ece/migrations/`。工作区另有 **14 项与本刀无关的既有脏文件**（2 个
`docs/demo-platform/*.md` 符号链接类型变更 + 12 个 `reports/cut-04*/mutation-evidence/*.md`），
**刻意排除在提交之外**（`evidence/14-compliance-check.txt` 用"9 文件"这个数把它们挡在门外）。

---

## 1. 逐条验收（A0–A14）

### A0 — 步骤 0 两笔转出已清 ✅

1. **`test_s32_assembly.py` 的 `item_kind` 断言**：原来是闭集 `r[0] in ("entity","relationship")`，
   自 OEI-010 往同一张表写 `item_kind='memory'` 起就过窄。**本刀解冻并改写**（TASK 明确给了二选一，
   我选"断言它真正的不变量"）：每行 `kind` 非空字符串、`decision ∈ {allowed,denied}`（闭集）、
   `reason` 非空。**声明：此断言在 OEI-010 被冻结，由本刀解冻并改动。**
2. **`docs/DATA_MODEL.md §4.2` 列序**：`idx_memories_scope_owner` 由误写的 `(owner_ref, scope)`
   订正为迁移 0010 实际的 `(scope, owner_ref)`。
3. 证据：`evidence/00-step0-transfer-fixes.txt`（两处 diff + 说明）。

### A1 — 既有 36 个对象只加了 `client_industry` ✅

对每个对象取"**去掉 `client_industry` 之后其余全部字段**"的规范化 JSON（sort_keys + 紧凑分隔符）
sha256，逐条对照 `git show a463658:...`：**36/36 EQUAL**。

- 证据：`evidence/02-existing-36-unchanged-hashes.txt`（36 条逐条 hash + `RESULT: other fields identical in 36/36`）
- 该文件还含**序列化器往返证明**：`json.dumps(cur, ensure_ascii=False, indent=2)` 能逐字节复原
  原文件 → 所以"其余字段没变"是**内容**层面的结论，不是排版层面的。脚本先验证这条才允许写盘。
- 脚本**幂等**（`apply_seed.py`：已存在的新 id 原地替换而非二次追加），重跑后文件 sha256 不变。
- 文件最终 sha256：`b6e7045bc626bccd3cfee6cbf81b9d15878d7759ccf11121f7fb6550b24f87a4`

### A2 — 覆盖率与词表 ✅

`evidence/` 侧：`workspace/02a-a2-violation-scan.txt`（在**真实 seed 文件**上跑）

| 检查 | 结果 | 期望 |
|---|---|---|
| `client_industry` 为空的官方对象 | **0** | 0 |
| 值落在词表外的 | **0** | 0 |
| `case` / `industry_note` 带 `cross_industry` | **0** | 0 |

**这个扫描有牙**：注入 3 个故障（空值 / 越界值 / 类型违禁）后三项分别报 `(1, 1, 1)`
—— 所以上面那三个 0 是"没找到"，不是"没找"。

### A3 — 依据可查 ✅

- `evidence/01-industry-annotation-basis.json`：24 条逐条 `id / type / title / 原值 / 新值 /
  依据字段 / 依据原句 / 扫描范围`，并带一个**机器判据** `basis_quote_is_substring_of_own_fields`
  —— 依据必须能在**该对象自己的** title/summary/practice/problem_types/methods 里定位到，
  24/24 为 `true`。
- 规则（写在文件里）：对象自身字段里**没有**具体行业锚点的，就是通用方法/模板/风险清单 → `cross_industry`；
  没有锚点却硬贴一个具体行业，正是 §3.1.5 禁止的"硬贴"。

### A4 — 覆盖目标 ✅（前后对照见 `evidence/04-coverage-targets.json`）

| 目标 | 前 | 后 | 达成 |
|---|---|---|---|
| 总数 ≥ 44 | 36 | **45** | ✅ |
| 每个具体行业 ≥ 2 | 7 个行业只有 1 | **10 个行业各 2** | ✅ |
| `industry_note` ≥ 6 | 2 | **6** | ✅ |
| `risk_check` ≥ 6 | 4 | **6** | ✅ |
| `cross_industry` ≥ 10 | — | **26** | ✅ |

类型分布 36→45：`case` 10→13、`industry_note` 2→6、`risk_check` 4→6（`methodology` 10、
`proposal_play` 6、`deliverable_template` 4 不变）。

### A5 — 内容纪律 ✅

- 两个闸门 + 数量 + service 测试**在真实 seed 文件上全绿**：`24 passed in 3.34s`
  （schema 6 + discipline 5 + count 4 + service 9），原始输出在 `evidence/08-seed-gates-raw.txt`。
- 9 条新增对象**逐条过闸门**，每条 6 项全 PASS（同一文件，9/9）。
- **关于 v1.1 提醒的那两条"名义失败"**：那是草稿夹具/路径导致的假失败。本刀的最终证据
  **不是**草稿上的，而是在真实文件上跑出来的全绿原始输出（`08` + `11`）。
- 竞品名 / 真实客户名 / 精确数字：纪律闸门覆盖，全绿。**但见 §4.3 的一笔转出**（既有对象的 id 里
  有一个小写竞品名，闸门不扫 id，且改它要动非 `client_industry` 字段 → 越界，故不动）。

### A6 — 词表只加 `cross_industry` ✅

- `metadata.py` 的 `ALLOWED_INDUSTRIES` 加 `cross_industry`（**唯一新增值**；`ALLOWED_TYPES` /
  `ALLOWED_PHASES` / `ALLOWED_PROBLEM_TYPES` / `ALLOWED_METHODS` 一字未动），并写明语义与
  "为什么需要它"（诚实：否则通用方法只能硬贴行业=伪造，或留空=轴更空）。
- 文档两处写明：`metadata.py` 注释 + `docs/API.md §12`。
- **上传路径校验行为不变**，两层证明（`evidence/07-vocabulary-cross-industry.txt`）：
  - HTTP 层：`cross_industry` → `ok`、`manufacturing` → `ok`、`made_up_industry` → `dropped`、
    `not_a_type` → `dropped`（越界仍静默丢弃）。
  - 机制层：把 `git show a463658:src/ece/consulting/metadata.py` 载入为独立模块，对 8 组探针
    逐例比较 `validate_metadata`。**除含 `cross_industry` 的两个探针外 100% 一致** ——
    而那两个**应当**不同（若相同，说明词表压根没加成功）。

### A7 — facets 可用 ✅

`evidence/05-facet-value-match-counts.json`：`client_industries` = **11 个值**
（10 个具体行业 + `cross_industry`），**不存在 0 匹配的值**，"值 → 命中数"聚合表齐全。

### A8 — 过滤实测 ✅

`evidence/06-library-filter-per-industry.json`：对**每个**行业值各跑一次真实的
`GET /api/v1/consulting/library?client_industry=<v>`，全部 **200 且命中 ≥2**，并记录每条的
`first_ids`（证明返回的是**筛过的子集**，不只是一个总数）。抽样 `GET /objects/{id}` 取新增对象
`industry-note-cn-manufacturing-2026-003` 成功。

### A9 — 数量断言有界解冻 ✅

被改动的**只有** TASK 点名的四处 + 步骤 0.1 那一处：

| # | 位置 | 改动 |
|---|---|---|
| 1 | `test_consulting_documents.py:263` | `== 36` → `>= 36` + 注释 |
| 2 | `test_consulting_documents.py:315` | `== 36` → `>= 36` + 注释 |
| 3 | `test_consulting_engine_merge.py:339` | `== 36` → `>= 36` + 注释 |
| 4 | `test_consulting_seed_count.py:34-50` | 6 处 `==` → `>=` + docstring 重述为 **FLOORS** + 新增自洽断言 |
| 5 | `test_s32_assembly.py:92`（步骤 0.1） | 闭集 → 真正的不变量 |

- 第 4 处的原意（"不许把某一类悄悄做没"）**留住了**：六类各自仍是下限断言，并新增
  `assert sum(expected.values()) <= len(catalog.objects)` —— 下限之和必须装得进目录。
- 证据：① `git diff` → `evidence/09-count-assertion-diff.txt`；② **改后重跑盘点命令** →
  `evidence/09b-assertion-inventory-after.txt`（三条 grep 的输出与原清单逐条对照，**没有第七处**）。

**声明：除此之外，本刀零断言改动。**

### A10 — 契约不回归 ✅

- `evidence/10-contract-regression.txt`：用 AST 从**改前源码**（`a463658`）取 `LibraryResponse`
  / `FacetsResponse` / `KnowledgeObject` 的字段名，与 `HEAD` 源码、与**运行时真实响应**的
  key 集合三方对照：**键集合完全一致**。变化的只有**值集**（`client_industries` 10 → 11 个值；
  `total` 36 → 45），这正是本刀的目的。
- 推论：SPA 的 `app.js` 数据驱动，**不需要改** —— 且实测 `demos/spa/**` 逐字节未变（`git diff` = 0 行）。
- `${...}` 相关子集全绿；**全套件 0 failed**（见下节，含 `evidence/12-test-suite-raw.txt`）。

### A11 — 文档 ✅

`docs/API.md §11`（`36`→`45` 的来历写成"`>= 36` 是下限"、新增"`client_industries`（行业轴）的语义"
小节，含前后对照表）、`§12`（`ALLOWED_INDUSTRIES` **11 个** = 10 具体 + `cross_industry`）、
`TASKS.md 附录 Q`。`make check-api-docs` → `Common: 26 | Docs-only (planned): 0 | App-only: 0` ✅。

### A12 — 提交 ✅

`evidence/13-git-commit.txt`：短 hash **`c30e50e`** + 9 文件清单 + 授权归属映射 + 未 push 证明
（`git log @{u}..HEAD` 显示本地领先 3 个提交，含本刀）。

### A13 — 合规与资源 ✅

`evidence/14-compliance-check.txt`（**收尾三查**）：
- **CHECK 1 进程**：无 uvicorn / 反代 / 残留 pytest-uv；55432 端口无人监听。
- **CHECK 2 容器**：`ece-*` 容器 **0**（临时 PG `ece-pg-oei011` 已 `docker rm -f`）；Onyx 9 个容器
  全部在跑，**uptime 均长于本次会话**；无遗留 volume。
- **CHECK 3 内存/swap**：**照原样报**，不写"正常"——swap 占用 7.0Gi/8.0Gi、`MemAvailable` 1.6Gi
  偏低。这是 Onyx 栈**既有**的压力；本刀只起过一个 PG 容器且快照是在它**删除之后**取的。
- `pyproject.toml` / `uv.lock` 零 diff；未碰 Onyx 上游（`/home/codex` 权限层面就不可达：mode 750
  owner codex，当前 fisher 既不可读也不可写）/ compose / `.env`；未 restart/stop/down/rm 任何
  onyx 容器；未 push。
- **无密钥值落盘**：两种形状分两次问，命中全部**打码**并逐条分类：
  1. **关键字形状**（`password` / `token` / `secret` …）：命中 1 处 —— `fresh_db_chain.sh:52`
     的**临时容器一次性口令**，已打码为 `<REDACTED-THROWAWAY>`。
  2. **URL 内嵌形状**（`scheme://user:pass@host`）：关键字扫描**看不见**这种，所以单列一次 ——
     命中 4 处，全部是本地临时库的 DSN（`…@127.0.0.1:1/…` 死端口与 `…@127.0.0.1:55432` 临时库），
     已打码为 `:<REDACTED-THROWAWAY>@`。

  两者都是**一次性、只存在于 127.0.0.1、容器已删除**的凭据，不是项目凭据；与 OEI-010 证据里
  同一形状的值一致（OEI-010 自己在其 compliance 文件里也是打码成 `ece:***@` 的，且已通过审验）。
  本刀全程 `ECE_CONTENT_ENGINE=mock`，**从未需要真引擎，也未向用户索取过任何凭据**。
  （记录这一条本身也是纪律的一部分：一个只 grep 关键字、对 `user:pass@` 视而不见的扫描，
  会给出"没有泄漏"的假象。）

### A14 — 证据纪律 ✅

全部证据是机器可校验的（JSON / sha256 / 计数 / 原始响应 / 原始 pytest 输出）。**未使用**
"内容更丰富""看起来更专业"这类不可判定表述。**未要求用户截图**。

---

## 2. 全套件（收口跑次）

`evidence/12-test-suite-raw.txt` —— **全新库 + 完整文档化前置链**上的原始输出：

```
847 passed, 5 skipped, 3 deselected, 5 warnings in 200.02s
```

链路：`docker run postgres:16-pgvector`（全新空库）→
`alembic -c src/ece/migrations/alembic.ini upgrade head` → `gen_dataset.py` → `make seed` →
四个 fixture seeder → `pytest -m "not eval and not eval_llm" -rs`。
与 §1.7 基线 **847 passed / 5 skipped / 0 failed** **逐项一致，0 failed**；五条 skip 各自的理由
都打印在该文件里（2 条 `test_e2_permission.py` 的 `e2 runner returned unexpected exit 3`，
3 条 `test_s5_5_real_llm.py` 的 `ECE_LLM_BASE_URL not set`）。

**本报告要主动交代的一件事**：在这之前，同一条链还跑出过一次 **846 passed / 6 skipped / 0 failed**。
差的那一条 skip 我**没能归因，也不打算猜**。做了的排查（全部记录在
`evidence/12b-suite-skip-discrepancy-probe.txt`）：

- `846+6 = 847+5 = 852`：恰好**一条用例由 passed 变 skipped**，失败数两边都是 0。
- 仓库**没有** pytest-randomly / xdist / order 插件 → 顺序确定、串行 → 差异只能来自用例内部的
  超时/环境守卫，不能来自顺序或并发。
- **已排除**：`test_s35_eval_suites.py` 的三个 `env-not-ready` 守卫（同一库上连跑 3 次，6 passed / 0 skip）。
- **已排除**：`test_e2_permission.py` 的两条出口（超时跳 / 换码跳，是同一个用例的互斥出口，**skip 数不变**）。
- 那次跑次发生在给脚本加 `-rs` **之前**，日志已被后续跑次覆盖 → **名字不可追**。
- 已把 `-rs` **固化进 `fresh_db_chain.sh`**，此后不会再出现"有 skip 数、无 skip 名"的情况。

我把它写出来是因为：**一个只在报告里留下好数字、把不好看的跑次删掉的收口，比这个差额本身更糟。**
结论能支撑到什么程度就写到什么程度：`0 failed` 在**全部 5 次跑次**里都成立，收口跑次与基线逐项一致。

---

## 3. 过程中的两笔意外（都不是本刀引入）

### 3.1 第一次全套件 48 failed —— 是我的 setup 缺失，不是回归

首次跑全套件得 **48 failed / 799 passed**，全部集中在三域集成测试，报的都是
`no entity with source_id='KM-POL-001' source_system='km:v0-knowledge-fixture'`。
根因：**我漏跑了 `make seed-fixtures`**（Makefile 注释自己写着这个 target 缺失会让 27 个测试失败）。
我没有把它当"环境噪音"糊过去，而是先证明它是 setup 缺失（单跑这些用例是过的、错误信息是缺 fixture 实体），
再从**全新库**走完整链复跑 → 0 failed。判断依据留在了 `05`/`06`/`12` 的证据链里。

### 3.2 预先存在的 Makefile 缺陷（顺带发现，未修）

`seed-fixtures` 的 recipe 里有 ``@echo "All fixtures seeded. Now `make test` should reach baseline (0 failed)."``
—— **反引号未转义**，shell 会做命令替换，于是这个 target **顺带把整套测试跑一遍**。
这是我最初看到 `847 passed` 的地方（`make[1]: Leaving directory ... should reach baseline (0 failed).` 后面挂着测试汇总）。
**这是既有缺陷、与本刀无关**，且 §8 未授权改 Makefile，所以**不修**，只记录：
`fresh_db_chain.sh` 因此**直接调那四个 seeder**，并把原因写进脚本注释。

---

## 4. 转出（不在本刀范围内，明确交出去）

详细版在 `TASKS.md 附录 Q.6`。三笔：

1. **`industry-note-cn-consumer-2026-002` 带 2 个具体行业**（§3.1.3 说 `industry_note` "恰好 1 个"）。
   **我没有收窄它**：§2 禁止改既有对象除 `client_industry` 以外的字段，而收窄正是改这个字段的
   *取值集合*；A2 只禁止该类型带 `cross_industry`（它没带）。→ 请 codex 裁定"恰好 1 个"是否要
   由本刀回溯执行。
2. **`methodology-mckinsey-7s-004` 的 id 里含竞品名**（小写）。纪律闸门的竞品扫描**不扫 id**，
   所以闸门是绿的；而改 id 就是改非 `client_industry` 字段 → 越界。**是否要单开一刀清理，交出去。**
3. **facets 仍只返回值集合、不返回计数**。本刀只要求"值 → 命中数"能被机器算出来（已做到，
   `05` 里有聚合表）；要不要让 `/facets` 直接返回计数，是接口变更，**不在本刀**。

---

## 5. 证据索引

```
00-blocked-contract-conflict.json / .stderr.txt  v1 自相矛盾的机器复现（保留，v1.1 §1.5 引用它）
00b-assertion-inventory.txt                      6 处断言点完整盘点 + 三条 grep 命令
00c-seed-gates-baseline.txt                      改前闸门基线（证明复现没被既有失败污染）
00-step0-transfer-fixes.txt                      A0 两处转出 diff
01-industry-annotation-basis.json                A3 24 条依据表（含"依据可在自身字段定位"判据）
02-existing-36-unchanged-hashes.txt              A1 36/36 逐条 hash + 序列化器往返证明
03-new-objects-list.json                         9 条新增对象（id/type/行业/理由/source_origin）
04-coverage-targets.json                         A4 前后对照 + A4 五项判定
05-facet-value-match-counts.json                 A7 值 → 命中数聚合表
06-library-filter-per-industry.json              A8 每个行业一次真实 /library 调用
07-vocabulary-cross-industry.txt                 A6 HTTP 层 + 机制层两层证明
08-seed-gates-raw.txt                            A5 两闸门 + 数量 + service 全绿原始输出；9/9 过闸门
09-count-assertion-diff.txt                      A9 ① git diff
09b-assertion-inventory-after.txt                A9 ② 改后重跑盘点（无第七处）
10-contract-regression.txt                       A10 键集合三方对照
11-test-db-free-raw.txt                          A14 DB 无关层（死端口 DSN 仍全绿）
12-test-suite-raw.txt                            全套件原始输出（含每一条 skip 的理由）
12b-suite-skip-discrepancy-probe.txt             846/6 vs 847/5 的如实记录与已做的排查
13-git-commit.txt                                A12 短 hash + 文件清单 + 未 push
14-compliance-check.txt                          A13 收尾三查 + 仓库足迹 + 密钥扫描
workspace/02a-a2-violation-scan.txt              A2 违规扫描（含"有牙"证明）
```

`workspace/` 是工具与素材（`blocked_repro.py` / `draft_plan.py` / `apply_seed.py` /
`verify_seed.py` / `verify_api.py` / `fresh_db_chain.sh` / `compliance_check.sh` +
三份 draft JSON），全部可重跑。

---

## 6. 结论

A0–A14 **全部达成**，且每条都有机器可校验的证据落盘。核心声明汇总：

1. 既有 36 个对象**只动了 `client_industry`**（36/36 规范化 hash 相等）。
2. 新增 9 条是**有界**的：过两条闸门、无竞品名、无真实客户名、无精确数字。
3. 词表**只加了 `cross_industry` 一个值**，上传路径越界丢弃的机制一字未改。
4. facets 无 0 匹配值、每个值 ≥2 命中；`/library` 与 `/facets` **键集合不变**。
5. 数量断言**有界解冻**：四处 + 步骤 0.1 一处，**其余零改动**（改后盘点命令为证）。
6. 全套件 **0 failed**（847/5/3deselected 与基线逐项一致）；唯一一处 skip 数出入已如实交代，未归因即写未归因。
7. 零新依赖、SPA 逐字节未变、未 push、临时资源已释放（收尾三查落盘）。
