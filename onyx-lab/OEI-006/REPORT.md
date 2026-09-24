# OEI-006 REPORT — Consulting Library 接真实检索（引擎合并）

执行：cc（programmer-executor，按 `onyx-lab/CC-ROLE.md`）
日期：2026-09-24 18:15–19:05 (+08:00)
提交：`ece` @ **7ab17fc**（main，**未 push**）
套件：**705 passed / 0 failed**（基线 681 passed / 0 failed，增量 = 本刀新增 24 条单测）

---

## 0. 一句话结论

在 `/api/v1/consulting/library` 上**新增**了第二个来源：来自已索引真实文档的**引擎召回**，
与 36 个静态种子对象**并列展示**，带来源标签、详情抽屉复用、降级与空态；
**静态侧零改变**（`01` 与 `04` 的静态载荷 sha256 完全一致），引擎结果只走新增字段。

---

## 1. 交付内容

| 文件 | 变更 |
|---|---|
| `src/ece/consulting/engine_merge.py` | **新增**：`merge_engine()` 四态策略 + `to_engine_items()` 纯映射，`DEFAULT_TOP_K=8` |
| `src/ece/consulting/models.py` | 新增 `EngineItem` / `EngineMergeStatus`，`LibraryResponse` 新增两个字段（既有字段未动） |
| `src/ece/consulting/router.py` | `get_library` 改 `async`；静态结果**先算**，再 `model_copy(update=...)` 追加重载 |
| `demos/spa/{index.html,app.js,styles.css}` | 视图 D 新增「引擎召回」分组、卡片与状态文案、详情抽屉复用 |
| `tests/unit/test_consulting_engine_merge.py` | **新增** 24 条 DB 无关单测（映射/合并/四态/异常/契约同构/端点级静态隔离） |
| `tests/integration/test_cut_045_local_origin_smoke.py` | 修子进程泄漏 + 部署栈缺失改显式 skip（§7 唯一授权改动的测试文件） |
| `docs/API.md` §11 / `TASKS.md` 附录 L | 契约文档 + 交付登记 |

---

## 2. 逐条验收（A0–A12）

### A0 — 步骤 0 三项 ✅
- **游离进程清零**：`00a`（改前）→ `00b`（改后，连续两轮套件后 `leak=0`）；`09` 第三轮套件后仍 `leak_uvicorn=0 / leak_origin=0`。
- **根因**：`urlopen` 超时抛出的 `TimeoutError` 是 `OSError` 但**不是** `URLError`，从就绪探测函数逃逸到旧 `try:` 之前，`finally` 从未执行。现改为 `except OSError` + `_reclaim()` + 单个 `try/finally` 同时兜住两个子进程；取值分支先回收再 `stdout.read()`（子进程持有管道写端）。
- **部署栈缺失改 skip**：显式前置检查 `demos/spa/index.html` 与 `.venv/bin/uvicorn`，缺失则 `pytest.skip`；本机两者都在，故实际**真跑 10/10**（非被 skip 掩盖）。证据 `00c`。
- ⚠️ **事实更正**：残留的那 1 条失败**不是**部署栈缺失（与 TASK §1.4 的归因不同），而是**第 4 个 fixture 未播种**（`scripts/seed_v0_spike_fixture.py`）。详见 §3-1。

### A1 — 静态侧零变化 ✅
- `01`（改前基线）与 `04`（改后、onyx 降级态、**同一 query**）的静态载荷
  `items/total/limit/offset/facets` **sha256 完全一致**：`9dd0f1917b1941ae`，同一组 3 个 id。
- 结构性佐证：`git diff HEAD~1 HEAD -- src/ece/consulting/service.py src/ece/consulting/data` **为空**（静态检索逻辑与 36 个种子数据本刀未触碰）。
- 端点级：`test_library_static_fields_are_identical_when_the_engine_dies` 断言引擎死/活两态静态字段逐字段相等。
- 既有 consulting 测试全部仍通过（含 `test_consulting_spa_view.py` 9 条护栏）。

### A2 — 新契约清晰 ✅
`docs/API.md` §11 给出 `engine_items`（6 字段类型 + 语义 + 判别字段 `source="engine"`）与
`engine_status`（四态语义表）说明、降级保证、分页语义、实测示例；`10` 贴 diff。
实测响应（`02`）与文档逐字段相符。

### A3 — onyx 模式取证 ✅
`02` 产生于 `ECE_CONTENT_ENGINE=onyx`（真实 Onyx，非 mock）：`engine_status="ok"`，
`engine_items` 非空，标题 `methodology-framework.md`、`source_type=user_file`、
`updated_at=2026-09-23T13:06:16Z`、片段内容可回溯到 `OEI-001/workspace/` 原文。

### A4 — 逐条对齐 ✅
`03` 给出 `engine_items` ↔ `POST /api/search` 原始返回的 1:1 对照表：
`engine_doc_id`↔`citation_id`、`title`、`source_type`、`updated_at`、`snippet`↔`content[:800]+"…"`
全部 `*_match: true`。

### A5 — 降级 ✅
`04`：上游不可达时 **HTTP 200** + 静态载荷与健康态**逐字段一致** + `engine_status="unavailable"`
+ `engine_items=[]` + **无 traceback / 无未捕获异常**。

### A6 — 空态 ✅
`05`：区分两个来源的空态（目录侧「目录无命中」vs 引擎侧提示），并给出四态矩阵
（`ok/unavailable/disabled/skipped`）与前端文案。含一条诚实发现（见 §3-7）。

### A7 — DB 无关单测 ✅
`tests/unit/test_consulting_engine_merge.py`，**24 条全部通过**，**在 `DATABASE_URL` 未设置、
无 Postgres 的情况下**运行（4.7s）。原始输出见 `06-contract-parity.json` 的 `A7_db_free_unit_test`
（含命令行、退出码与输出尾部）。覆盖：映射、四态、`EngineError` 异常路径、`updated_at` 回归、
`raw`/`link` 不泄漏、端点级静态隔离。

### A8 — 契约同构 ✅
`06`：mock 侧用**真实 `MockContentEngineAdapter`**，onyx 侧用**真实捕获的 Onyx `/api/search` 命中**
经真实 `_result_to_engine_document`，两者经**同一** `EngineItem` 模型校验通过；
字段集相同、值类型仅 `str|null`；引擎内部字段 `citation_id/content/link` **被丢弃且零泄漏**。

### A9 — 无回归 ✅
| | passed | failed | skipped | deselected |
|---|---|---|---|---|
| `08` 基线 | 681 | **0** | 5 | 3 |
| `09` 改后 | **705** | **0** | 5 | 3 |

- `failed 0 ≤ 1` ✅（也不劣于基线）。
- 差异**逐条说明**：`+24 passed` = 本刀新增的 24 条单测，**无其他增减**；skipped 数与基线一致（5）。
- ⚠️ 基线口径说明：`08` 是**先补第 4 个 fixture 播种**后的 681/0；补种前为 680/1（那 1 条即 `test_cut_045_local_origin_smoke`）。详见 §3-1。

### A10 — SPA 可见性自查 ✅
`07` 含：新增 DOM 锚点清单（`consulting-engine` / `-status` / `-cards` / `-empty`，并证明用 `<div>` 而非嵌套分节、详情抽屉仍在扫描区内）、经代理的 API 原始输出、**60 秒用户自查清单**、**截图请求**（S1/S2/S3，明确属用户协助项）。
> 本文件**不含真实截图**，只有请求与文本/JSON 证据 —— 未用 API 响应冒充截图。

### A11 — 合规 ✅
`12`：凭据**值级**扫描（先断言取值 ≥1 + **正对照命中**，避免"空 pattern 匹配一切"的假阴性）；
结论：证据目录 / 提交 diff / 10 个改动文件 **0 处**含 secret 值；Onyx **9 容器 `restarts=0`**、
`started` 均为 2026-09-23T11:0x（本刀工作时段为 09-24 18–19 点，未被重启）；未触碰 `/mnt/c`；
`origin/main` 仍为 `08cbeff`（HEAD 不在任何远程分支，**未 push**）；未新增依赖；
36 个种子对象与三域业务逻辑未改；未改 Onyx 上游 / compose / `.env` / swap / `.wslconfig`。

### A12 — 本报告 ✅
A0–A11 每条均有结论 + 证据指针，无模糊表述。

---

## 3. 偏差与诚实记录（需 codex 知悉）

1. **§1.4 基线归因有误**：那 1 条失败**不是**「部署栈缺失」，而是**第 4 个 fixture 未播种**。
   `scripts/seed_v0_spike_fixture.py` 未包含在 `make seed-fixtures` 中。补跑后 10/10 通过，
   套件从 `1 failed / 680 passed` → `0 failed / 681 passed`。
   该脚本已核验安全：`DELETE` 精确限定 `source_system='spike:v0-technical-fixture'`（无 LIKE 扫描）、
   `SPIKE-*` display_id 不在共享数字命名空间、幂等、自带自检。
2. **`Makefile` 未修**：把该 seeder 加入 `seed-fixtures` 的**一行修复不在 §7 授权清单**内，故**仅登记不实施**（见 `TASKS.md` 附录 L.4）。
3. **§1.3 自查链路需要 `no_proxy`**：本机 shell 导出 `http_proxy=http://127.0.0.1:7890` 且
   `no_proxy` 写作 `127.*`，而 **Python `urllib` 不认这个通配**（`proxy_bypass('127.0.0.1')=False`，
   仅 `localhost` 为 True）。反代脚本 `cut_045_local_origin.py` 用 `urllib` 转发上游，因此
   **按 §1.3 原样起服务必然 502**（实测 `status=502 bytes=0`）。修正：终端 B 先
   `export no_proxy=127.0.0.1,localhost`。已在 `07` §0 写明，请务必转达给用户自查清单。
   （codex §1.3 的实测通过，推测其当时的 shell 无 `http_proxy`。）
4. **§1.4 的链路描述与实机不符**：本机**没有** `nginx` / `web/dist`；真实链路是
   `demos/spa/`（静态）+ `.venv/bin/uvicorn` + 纯 Python 反代脚本。
5. **新增测试文件**：`tests/unit/test_consulting_engine_merge.py` 是**新文件**（§4 步骤 5.1 要求新增 DB 无关单测）；
   §7「`tests/**` 只允许改一个文件」应理解为**不得改动他人测试文件的断言语义** —— 本刀未改任何既有测试的断言。
6. **我自己引入并自查出的 bug**：`EngineItem.updated_at` 初版写成 `str | None`，而端口模型是 `datetime | None`，
   导致 **onyx 模式下接口 500**（mock 模式永远测不出）。已改为 `datetime | None` 并补回归测试
   `test_updated_at_accepts_a_real_datetime_from_the_live_mapping`。**这正是"必须用 onyx 取证"的价值**。
7. **Onyx 是语义召回而非相关性过滤**：无意义 query 也会返回整库前 N 条（`05` 的 A 例：随机串仍返回 3 条），
   因此"引擎零命中"在已索引项目上**不可自然到达**，该分支由单测确定性覆盖。建议 UI 文案表述为
   「相关文档」而非「命中」。
8. **反代 10s 超时 vs Onyx 冷启动**：反代上游超时 10s，ECE 适配器 60s；Onyx 冷启动首查实测可达 15s
   （稳态 4.2s）。自查时首查可能得到 502（重试即可），**非本刀代码缺陷**。详见 `07` §5。
9. **临时资源**：本刀自查用的临时 Postgres 容器 `ece-pg-tmp`（127.0.0.1:55432）**已回收**；
   后续要重跑套件需重新创建并播种 fixture。

---

## 4. 未做 / 移交

- **未 push**（§7 只授权 commit）。
- **未做**：上传管道（OEI-007）、权限壳层（OEI-008）、LLM Chat 生成答案。
- **未改**：36 个种子对象、三域业务逻辑与其测试、既有测试断言语义、Onyx 任何东西。
- **建议移交**：`Makefile` 补第 4 个 seeder；UI 文案改用「相关文档」；如需长期稳定自查，考虑反代上游超时调整（均不在本刀授权内）。

---

## 5. 证据指针

| 文件 | 对应 |
|---|---|
| `00a` / `00b` / `00c` | A0 泄漏前后 / 修复 diff 与两轮验证 |
| `01` / `04` | A1 静态零变化（sha256 `9dd0f1917b1941ae` 一致） |
| `02` | A3 onyx 模式响应 |
| `03` | A4 逐条对照表 |
| `05` | A6 空态 + 四态矩阵 |
| `06` | A7 单测原始输出 + A8 契约同构 |
| `07` | A10 DOM 锚点 / 经代理原始输出 / 60 秒清单 / 截图请求 |
| `08` / `09` | A9 基线 vs 改后 |
| `10` | A2 文档 diff |
| `11` | commit（未 push） |
| `12` | A11 合规与清理 |
