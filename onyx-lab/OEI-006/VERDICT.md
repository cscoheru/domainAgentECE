# OEI-006 审验裁定（codex）

> 审验日期：2026-09-24 19:1x ｜ 审验对象：`REPORT.md` + `evidence/`（13 个文件）+ `DONE`（19:01:27）+ ece commit `7ab17fc`
> 被审任务书：`TASK.md` v1（签发 2026-09-24 18:15）
> 审验方式：逐条核对 + 抽查证据 + **独立复现**（真实 onyx 模式调用 / 降级调用 / DB 无关单测 / 泄漏复查 / 静态载荷 sha256）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 核对依据 |
|---|---|---|---|
| A0 | 步骤 0 三项（清泄漏 / 修泄漏 / 改 skip） | **PASS** | 独立复核：① 我签发前查到的 **10 个游离 uvicorn 已清零**；② **我亲自跑了一遍 `test_cut_045_local_origin_smoke`，跑完 `pgrep` 残留 uvicorn = 0、origin 代理 = 0**（此前每跑一次泄漏一个）；③ 修的是根因——`except urllib.error.URLError` → `except OSError`（`TimeoutError` 是 `OSError` 但不是 `URLError`，旧代码里它逃出就绪探测、`finally` 从未执行）+ `_reclaim()` 无条件 terminate→wait→kill→wait ✓ |
| A1 | 静态侧零变化 | **PASS** | **我自己算的 sha256**：`01`（改前基线）与 `04`（改后降级态、同 query）的静态载荷 `items/total/limit/offset/facets` 均为 **`9dd0f1917b1941ae`**、同为 3 条 ✓ |
| A2 | 新契约清晰 | **PASS** | `docs/API.md:527-560` 有 `engine_items` / `engine_status` 的字段表与四态语义（`ok/unavailable/disabled/skipped`）与降级保证；实测响应与之相符 ✓ |
| A3 | **onyx 模式**取证 | **PASS** | **我独立复现**：`ECE_CONTENT_ENGINE=onyx` 起真实服务后 `GET /api/v1/consulting/library?q=问题树怎么用` → **HTTP 200 / engine_status=ok / engine_items=1**，条目为 `methodology-framework.md`（`source_type=user_file`），片段开头即该文档正文——可回溯到 `OEI-001/workspace/` ✓ |
| A4 | 逐条对齐 | **PASS** | `03` 左=ECE library（onyx 模式），右=`POST /api/search` 原始返回，逐项 `engine_doc_id ↔ citation_id`、title、source_type、updated_at、snippet ↔ content ✓ |
| A5 | 降级 | **PASS** | **我独立复现**：`ECE_ONYX_BASE=http://127.0.0.1:9` → **HTTP 200 / engine_status=unavailable / engine_items=0 / 静态 items=3 原样保留**，无未捕获异常 ✓ |
| A6 | 空态 | **PASS** | `05` 含四态矩阵与两来源空态文案，并说明 `skipped`（无 q 时不自动打引擎）的理由 ✓ |
| A7 | DB 无关单测 | **PASS** | **我独立复跑**：`env -u DATABASE_URL uv run pytest tests/unit/test_consulting_engine_merge.py` → **24 passed**（4.65s，无 Postgres）✓ |
| A8 | 契约同构 | **PASS** | `06`：mock 与**真实 Onyx 命中**经同一映射函数、同一 `EngineItem` 模型校验；并列出引擎内部字段 `citation_id/content/link` **被丢弃**（`A8_engine_internal_fields_dropped`）✓ |
| A9 | 无回归 | **PASS** | 原始汇总行我核对过：`08` = `681 passed, 5 skipped, 3 deselected`、`09` = **`705 passed, 5 skipped, 3 deselected`**，两次 **0 failed**；`+24` = 本刀新增单测，无其他增减 ✓ |
| A10 | SPA 可见性自查 | **PASS** | `07` 有新增 DOM 锚点清单、经代理 API 原始输出、**60 秒用户自查清单**与截图请求（S1/S2/S3），且**明确声明不含真实截图、未用 API 响应冒充** ✓ |
| A11 | 合规 | **PASS** | `12` 的做法值得肯定：扫描前先**验证扫描器有效性**（`secret values: 1` + **正对照命中**），再报 0 命中——避免"空 pattern 匹配一切"的假阴性；Onyx 9 容器 `restarts=0`、`started` 早于工作时段；`origin/main` 仍在 `08cbeff`（**未 push**）✓ |
| A12 | 报告完整 | **PASS** | A0–A11 每条有结论 + 证据指针；§3 主动列了 9 条偏差与诚实记录 ✓ |

**汇总：A0–A12 全部 PASS。**

## 2. codex 独立复现汇总

| 复现项 | 命令/方式 | 结果 |
|---|---|---|
| 引擎合并（真实引擎） | `ECE_CONTENT_ENGINE=onyx` + `GET .../library?q=问题树怎么用` | 200 / `ok` / 1 条 `methodology-framework.md` ✅ |
| 降级 | `ECE_ONYX_BASE=http://127.0.0.1:9` | 200 / `unavailable` / 静态 3 条不变 ✅ |
| DB 无关单测 | `env -u DATABASE_URL pytest tests/unit/test_consulting_engine_merge.py` | 24 passed ✅ |
| 静态载荷零变化 | 自算 sha256（`01` vs `04`） | 两侧均 `9dd0f1917b1941ae` ✅ |
| 泄漏修复 | 跑 `test_cut_045_local_origin_smoke` 后 `pgrep` | 残留 uvicorn 0 / origin 0 ✅ |
| 提交面 | `git show --stat 7ab17fc` | 10 文件，全部落在授权范围内（见 §3）✅ |

## 3. 范围与合规

- **改动面**：`src/ece/consulting/{engine_merge,models,router}.py`、`demos/spa/{app.js,index.html,styles.css}`、`docs/API.md`、`TASKS.md`、`tests/integration/test_cut_045_local_origin_smoke.py`、**新增** `tests/unit/test_consulting_engine_merge.py`。
- **既有测试的断言语义**：未改（只改了 cut_045 那一个文件的子进程回收与 skip 前置）✓
- 未改 36 个种子对象、未改三域业务逻辑、未新增依赖、未碰 Onyx 上游 / compose / `.env` / swap / `.wslconfig`、**未 push** ✓
- 凭据：值级扫描 0 命中（含正对照）✓

## 4. 裁定

**PASS —— OEI-006 关闭。**

理由：A0–A12 全部达成，且**本刀最关键的两条我都亲自复现过**——真实 onyx 模式下的引擎合并（`ok` + 真实文档命中）与降级路径（`unavailable` + 静态零变化）。静态侧零变化有双向证据（我自算的 sha256 + 端点级断言）。DB 无关单测 24 条在无数据库环境下通过。此外本刀顺手修掉了 OEI-005 遗留的进程泄漏（我跑测试后确认零残留），并**自己发现并修复了一个只会在 onyx 模式暴露的 bug**（`EngineItem.updated_at` 类型不符导致 500）——这恰好证明"必须用真实引擎取证"这条纪律的价值。

## 5. codex 自身的任务书缺陷（本轮自省，不计 cc 责任）

1. **§7 与 §4 自相矛盾**：§7 写"`tests/**` 只允许改 `test_cut_045_local_origin_smoke.py` 一个文件"，而 §4 步骤 5.1 又要求"新增 DB 无关单元测试"——新增测试文件本就必须新建文件。cc 在 §3-5 主动指出并按合理语义执行（**未改任何既有测试的断言语义**）。正确写法应为"不得改动既有测试的断言语义；新增测试文件允许"。
2. **§1.3 的自查链路漏了 `no_proxy`**：本机 shell 同时存在 `no_proxy=…,127.*,…`（**Python `urllib` 不认这种通配**）与 `NO_PROXY=localhost,127.0.0.1` 两套变量，谁生效取决于环境字典顺序，因此按我给的命令可能得到 502。cc 实测并纠正（显式 `export no_proxy=127.0.0.1,localhost`），写进了 `07` §0。**这是我的疏漏。**

## 6. 遗留与转出（不阻塞本刀）

1. **回归基线的"文档口径"仍不一致（建议下一刀步骤 0 处理）**：`make seed-fixtures` **不含** `scripts/seed_v0_spike_fixture.py`（第 4 个 fixture），而本刀的真实基线 `681 passed / 0 failed` 是在补跑它之后取得的。因此按 `ece/README.md` 里文档化的命令跑，仍会看到 **1 failed**。cc 已登记在 `TASKS.md` 附录 L.4，但**未改 Makefile**（不在本刀授权内，处理正确）。建议下一刀二选一：把该 seeder 纳入 `seed-fixtures`，或把 README 的"期望数字"改成带前提的写法。
2. **cut_045 smoke 的 skip 守卫只覆盖"部署栈"，不覆盖"无 DB"**：我在**不设 `DATABASE_URL`** 的情况下单独跑该测试，它仍然 **FAIL** 而不是 SKIP（跳过了部署栈检查，但 smoke 里的 API 检查需要数据库）。建议后续刀把 DB 可用性也纳入守卫。
3. **Onyx 是语义召回、不是相关性过滤**：无意义 query 也会返回整库前 N 条，故"引擎零命中"不可自然到达（该分支由单测覆盖）。UI 文案建议用「相关文档」而非「命中」——cc 已提出，属文案层面。
4. **用户协助项（截图）**：`07` 请求的三张图 S1/S2/S3 仍需人来截（cc 无浏览器工具）。**不计入 cc 的验收失败**。
5. `wsl --shutdown` 让 14GB 内存配额生效（用户侧，仍待做，不阻塞）；CE/EE 官方文档 URL 待网络可达时补。

> 本刀 PASS；下一刀为 OEI-007（上传管道）。**git 处置（推 ece 的 5 个提交 + 把 `onyx-lab/` 纳入根仓）待用户确认后执行。**
