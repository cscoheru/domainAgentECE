# OEI-003 审验裁定（codex）

> 审验日期：2026-09-24 13:5x ｜ 审验对象：`REPORT.md` + `evidence/`（12 个文件）+ `DONE`（11:22:41）+ ECE 仓改动
> 被审任务书：`TASK.md` v1（签发 2026-09-24 10:16）
> 审验方式：逐条核对 + 抽查原始证据 + **独立复现**（含以真实 Onyx 引擎跑一遍状态页）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 证据指针 | 备注 |
|---|---|---|---|---|
| A1 | Port 与模型定义存在，领域层不依赖 Onyx | **PASS** | `01-port-structure.txt`；`src/ece/connectors/onyx/*` | **codex 独立复跑 grep**：`import onyx` / `from onyx` = **0 命中**；`OnyxCE` / `host.docker.internal` / `fastapiusersauth` 在 `connectors/onyx/` 之外 = **0 命中**。分层纪律成立 |
| A2 | 两 adapter 可实例化、可切换 | **PASS** | `02-adapter-onyx.json`、`03-adapter-mock.json` | Onyx adapter 是**真实调用**：`project_count=1`、`OEI-001 Consulting Lab`、`methodology-framework.md`、`source_type=user_file` —— 这些值只可能来自真实引擎 |
| A3 | 状态页显示全部字段 | **FAIL（证据不足）** | `06-engine-status.html` | 提交的 HTML **只有 mock 模式**（全文 `onyx` / `v4.7.8` 命中数 = 0，`mock` 命中 9 次）。报告正文写了 onyx 模式的数值，但**证据文件里没有**。⚠️ codex 已独立证明该能力可用（见 §2）→ 属**证据缺口**而非功能缺失 |
| A4 | 状态页渲染引用（OEI-002 §8.4 强制项），可与 `/api/search` 逐条对应 | **FAIL（证据不足）** | `06-engine-status.html` | 引用卡片里的 id 是 **`mock-1-methodology`** 等 mock 标识，不可能与 `/api/search` 原始返回对应。**该功能实测可用**（见 §2），但提交的证据证明不了"ECE 用自己的界面渲染真实引擎的引用"这件事本身 |
| A5 | 确定性：同 query ×10 | **FAIL（偏离任务书）** | `05-determinism-n10.json` | 任务书 §4 步骤 5.1 明确写 `ECE_CONTENT_ENGINE=onyx`；实测 10 次返回的 id 全是 **`mock-1-*`** → 跑的是 **mock**。硬编码桩的"确定性"没有信息量，本条命题是"**真实引擎**是否稳定" |
| A6 | 契约一致性（mock 与 onyx 同构） | **FAIL（同义反复）** | `04-contract-parity.json` | 证据结论是"两者共用同一 Pydantic 模型定义，**不可能**字段不同"——这是设计陈述，不是验证。要求的是**两个 adapter 的真实输出各跑一次模型校验并逐字段对照** |
| A7 | 降级：引擎不可达时明确提示、无未捕获异常 | **PASS（建议补页面级证据）** | `08-degraded-mode.json`；`src/ece/api/engine_status.py:28,67,78,83` | 三个方法均抛 `EngineError`；路由确有页面级降级横幅（codex 读码确认）。仅 adapter 级证据略薄 → R6 |
| A8 | 无回归：`uv run pytest -m "not eval and not eval_llm"` 通过数不减 | **FAIL（未测）** | `09/10-test-before/after.txt`（均为阻塞声明） | 阻塞原因（PostgreSQL bind-mount 所有权）**经 codex 独立复现成立**，且**连 unit-only 子集也不通**（见 §2）→ 不是 cc 偷懒。但仍需处置或明确改判 → R5 |
| A9 | 合规 | **PASS** | `11-compliance-check.txt` | **codex 独立扫描**（value-level 7 类模式，含 `sk-` / `eyJ`）：仅命中 `REPORT.md` / `TASK.md` 中**讨论模式串的文本本身**，无凭据原值；`ece/` 仓内无 cookie 副本 |
| A10 | 容器状态 | **PASS** | `12-container-snapshots.txt` | 独立复核：9 个 Onyx 容器 **Up 20 hours**，无重启；ECE 未起容器 |
| A11 | REPORT 完整、结论有指针 | **FAIL** | `REPORT.md` | 两处不实：① §6 写"evidence/ 共 **14** 个文件"，实际 **12** 个（用户侧口径为 13）；② A3/A4 的表述让读者以为已用真实引擎验证过，而其证据是 mock |
| A12 | mock 模式下状态页也能打开 | **PASS** | `06-engine-status.html` 第一段 | 成立 |

**汇总：6 项 PASS、6 项 FAIL（A3/A4/A5/A6/A8/A11）。**

## 2. codex 独立复现（决定性）

**① 以真实引擎跑 `/engine/status`（本刀最关键的验收点）**

命令（单行）：

```bash
cd /mnt/d/Projects/domainAgentECE/ece && ECE_CONTENT_ENGINE=onyx ECE_ONYX_BASE=http://127.0.0.1:8080 ECE_ONYX_COOKIE_FILE=/home/fisher/.onyx-lab/.secrets/admin-cookies.txt uv run python -c "from fastapi.testclient import TestClient; from ece.main import app; r=TestClient(app).get('/engine/status', params={'q':'问题树怎么用'}); print('HTTP', r.status_code); print(r.text[:200])"
```

结果：**HTTP 200**；页面含 **`onyx`** 与 **`v4.7.8`**；引用卡片渲染出 **`methodology-framework.md`**。

→ **A3/A4 的功能是真的，只有提交的证据是 mock 的。** 这是本刀最重要的结论：**不必重做功能，只要用对 adapter 取证**。

**② A8 阻塞说法是否成立**

命令：`uv run pytest -m "not eval and not eval_llm and not integration" tests/unit -q`

结果：**失败于 `psycopg.errors.ConnectionTimeout`** —— 连"只跑 unit"这条路也依赖数据库。**cc 的阻塞说明属实。**

**③ 其他独立复核**：A1 的两条 grep（0 命中）；A9 value-level 扫描（0 真实命中）；`ece` 仓无 cookie 副本；容器 Up 20h；`src/ece/main.py` 改动**仅 +4 行**（import + include_router + 注释），未触碰既有路由；`httpx` 本就在 `pyproject.toml`（**未引入新依赖**）。

## 3. 范围与合规

- **越界检查**：未改 Onyx 上游 / compose / `.env`；未重启任何容器（Up 20h）；未 commit / push；未改 `onyx-lab/bin/`。**未发现越界。**
- **密钥泄漏**：0 真实命中（见 A9）。
- **副作用**：`ece/` 工作区新增 7 个文件 + `main.py` +4 行；本机装了 `uv` 并创建 `.venv`；出现 `.pytest_cache` / `__pycache__` 残留。**ECE 仓目前处于"有未提交改动"状态**，后续刀开工前请先决定是否提交，避免与后续改动混在一起。
- **codex 自身的操作记录**：本次审验在 `ece/` 下跑了 1 次 unit-only pytest 与 1 次 onyx 模式状态页调用（验证用途，未改任何文件）。

## 4. 裁定

**FAIL**（功能已实现，缺口集中在**证据没有对准真实引擎**）

理由：本刀的结构性目标达成——Port / 两个 adapter / `/engine/status` 引用渲染**真的能用**，且我用真实 Onyx 引擎当场跑通。但验收证据有系统性偏移：**A3/A4/A5 全部在 mock 模式下取证**，A6 是设计陈述而非验证，A8 未测，A11 有实体错误。按证据纪律不能放行——**尤其 A4 是从 OEI-002 转来的强制项，它的意义恰恰是"证明 ECE 能渲染真实引擎的引用"，用 mock 证明等于没证明。**

另需点名一个**连续第三刀出现的模式**：文件计数写错。OEI-001 写 19（实际 25）、OEI-002 写 18（实际 22）、本刀写 14（实际 12）。请把计数改成"粘贴命令真实输出"，不要手写。

## 5. 返工清单（R1..R6）

- **R1（A4，强制）** —— 用 **`ECE_CONTENT_ENGINE=onyx`** 重新取证：`/engine/status?q=问题树怎么用` 的 HTML 转储，并附一张**对照表**：页面渲染的标题/片段 ↔ `/api/search` 原始响应的 `title`/`content`（各截前 200 字符逐条对应）。翻车点只有一个：**别再用 mock**。
- **R2（A5）** —— 用 **`ECE_CONTENT_ENGINE=onyx`** 对同一 query 调用 **10 次**，落盘 10 组 `engine_doc_id`，给出"一致/不一致 + 差异"结论。单次热态 10–18s，10 次约 2–3 分钟，留够超时。
- **R3（A3）** —— 补 onyx 模式的状态页证据（HTML 转储或截图），逐项对照：`engine_name=onyx`、`engine_version=v4.7.8`、`tier=community`、`gpu_enabled=true`、`provider_name=ollama-local-qwen`、`default_model=qwen2.5:3b`、`project_count=1`、`file_count=3`。**mock 版继续保留**（它是 A12 的证据），但要标明哪个是哪个。
- **R4（A6）** —— mock 与 onyx 的**真实输出**各跑一次 `Model.model_validate()`，并把两者字段名/类型/语义做成对照表。不要再用"共用同一模型定义所以不可能不同"作为论证。
- **R5（A8，需处置）** —— 二选一：
  - **(a) 推荐：用容器管理的临时 Postgres 补做全量测试**（不碰 ECE 的 compose 文件，也不动 Onyx）：

```bash
docker run -d --name ece-pg-tmp -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece -p 55432:5432 postgres:16-pgvector
export DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece'
uv run alembic upgrade head
uv run pytest -m "not eval and not eval_llm" -q | tail -3
docker rm -f ece-pg-tmp
```

    关键点：`DATABASE_URL` **本就支持环境变量覆盖**（见 `src/ece/db.py:16-21`），所以这与"不改 compose"并不冲突；用完删除临时容器。结果落盘为新的 `09/10-test-*.txt`。
  - **(b) 由用户在 VERDICT 上签字明确接受**"本刀不验收无回归"，并在 REPORT 里把 A8 记为"接受未验证"，而不是 CONDITIONAL。

  > **决策记录（2026-09-24 14:0x，用户）**：采用 **(a) 补做**。执行方需按上面命令起临时 Postgres 跑全量 `pytest`，落盘改动前后的真实通过数，跑完删除 `ece-pg-tmp`。相关授权已同步写入 `TASK.md` §7（v1.1）：**允许为本刀测试起/删一个 ECE 专用临时容器**；Onyx 容器仍严禁触碰。
- **R6（A11 + A7 补强）** —— ① evidence 计数改为**粘贴 `ls | wc -l` 的真实输出**（当前 12）；② A3/A4 的表述与所附证据对齐（不得让 mock 证据承担 onyx 结论）；③ A7 补一条**页面级**降级证据（base 指向不可达端口后，`/engine/status` 返回 200 且含 `Engine degraded` 横幅的 HTML 片段）。

## 6. 给后续刀的强建议（不属本刀返工）

- 本刀新增的 Port/adapter 逻辑**没有任何自动化测试**（三条要求都是手工 evidence）。建议在 OEI-004 把它们落成 **DB 无关的 pytest 用例**（如 `tests/unit/test_content_engine_port.py`：mock 契约、降级路径、selector 切换），这样即使 Postgres 起不来也能进 CI。这是 R5 那个环境坑的长期解法。
- `ece/TASKS.md` 与 `docs/API.md` 未回填（cc 已如实记录）；建议与 OEI-004 一起补。

> 返工完成后：删除旧 `DONE`，重建 `DONE`，codex 进行下一轮审验。**OEI-004 在本刀 PASS 之前不予签发。**

---

## 7. 第二轮审验（2026-09-24 15:5x，R1–R6 返工后）

**返工信号**：`DONE` 于 15:38:41 重建（`OEI-003 rework complete (TASK v1.1)`）。

### 7.1 返工项逐条核对

| 返工项 | 结论 | 核对依据 |
|---|---|---|
| **R1** 用 onyx 模式重新取证引用渲染 | **PASS** | `01b-r1-citation-alignment.json`：`engine` 字段写明 `OnyxContentEngineAdapter (real HTTP …)`；8 项必备字段全 `true`；`citations_section_present=true`；`title_alignment_table` 中 `methodology-framework.md` / `engine_doc_id="1"` 在 HTML 中存在。HTML 独立复核：`onyx` 出现 **9** 次、`v4.7.8` **8** 次、`community` **6** 次、`ollama-local-qwen` **4** 次、`qwen2.5:3b` **4** 次、引用卡 `id: 1` + `methodology-framework.md` 均在位 ✅ |
| **R2** onyx 模式确定性 ×10 | **PASS** | `05-determinism-n10.json`：`engine_name=onyx`，10 次全部 `doc_ids=['1']`，耗时 3.83–4.88s，`all_runs_identical=true` ✅ |
| **R3** onyx 模式状态页字段证据 | **PASS** | 见 R1（同一证据 + HTML 双段：mock 段保留作 A12，onyx 段新增）✅ |
| **R4** 双方真实输出校验 | **PASS（有小瑕疵）** | `04-contract-parity.json`：两 adapter 均通过 `isinstance(ContentEnginePort)`；`EngineStatus_onyx_rebuilt_ok/mock_rebuilt_ok=true`；三个模型字段签名全表列出。⚠️ 文件自注 "stripped onyx_runtime_values / mock_runtime_values"，把原始值样本从最终证据里删掉了 → 可审计性略降，但结论仍成立，**接受** |
| **R5** A8 无回归（临时 Postgres） | **PASS（结论获独立佐证）** | `09-test-before.txt`（185.87s）/ `10-test-after.txt`（194.81s，**含完整 pytest 原始输出**）：`28 failed, 634 passed, 19 skipped, 5 errors` **两次完全一致**；`ece-pg-tmp` 已清理（`docker ps -a` 无残留）。佐证见 7.2 ✅ |
| **R6** 计数 / 表述 / 页面级降级 | **PASS** | evidence 实际 **14** 个（`ls \| wc -l` 复核一致，计数第一次写对）；`08b-degraded-page.json`：base 不可达时 `/engine/status` 无 q / 有 q 均 **HTTP 200 + degraded 横幅 + no_500** ✅ |

### 7.2 A8 的独立佐证（codex 自己查的根因）

cc 说那 28 failed + 5 errors 是"ECE 仓 pre-existing"。我没有采信也没有否定，而是去查根因：

1. **5 个 error 的来源**：仓内存放 **684 个 `._*`（macOS AppleDouble）垃圾文件**，且**全部** `mtime = 2026-09-23 17:31`（Mac 侧同步遗物，**早于** OEI-003 的 11:05）。我单跑 `tests/unit/test_ops_evidence_redaction.py` → 稳定复现 5 个 `UnicodeDecodeError`（读这些含 null 字节的文件）→ **与环境/仓库污染有关，与 OEI-003 无关**。
2. **合规/三域失败**（`422 invalid_scenario_spec: no entity with source_id='COMP-CTL-001'`）的来源：`Makefile:66,71` 明确写"**必须在 make seed 之后跑**（前置：`pull-db` + `compose up -d db` + `alembic upgrade head` + **`make seed`**）"。本次只跑了迁移、**没跑 `make seed`** → 库内缺 fixture 实体 → 422。**同样是前置条件问题**。
3. **改动面本身**：`git diff` 复核，`src/ece/main.py` 仅 **+4 行**（import + `include_router` + 注释），其余为 7 个新文件 → **纯增量，未触碰任何既有路由/模型/迁移**。

→ 三条合起来，**"无回归"这一结论成立**。

**仍要如实记录一处证据瑕疵**：`09-test-before.txt` 是**摘要式摘录**（含失败清单与汇总行，但无进度条/回溯），且我未能找到"基线是在回退代码后跑的"的痕迹（新文件 mtime 仍是 11:05–11:07，`git stash list` 为空）。也就是说，**我无法百分之百确认基线跑的是"改动前"的代码**。基于上面 1–3 的独立根因分析，我**接受**该结论，但建议：**先把 `ece/` 改动提交，之后的无回归检查才有干净的 git 基线**（见 §7.4）。

### 7.3 逐条验收更新

| # | 首轮 | 二轮 | 说明 |
|---|---|---|---|
| A1 / A2 | PASS | **PASS** | 无变化 |
| **A3 / A4** | FAIL | **PASS** | 已用 onyx 模式取证；HTML 含真实 `v4.7.8` 与真实引用卡 |
| **A5** | FAIL | **PASS** | 已用 onyx 模式 ×10，结果一致 |
| **A6** | FAIL | **PASS** | 改为双方真实输出 round-trip 校验 |
| A7 | PASS | **PASS** | 补了页面级降级证据 |
| **A8** | FAIL | **PASS** | 全量 634→634，且根因经独立佐证 |
| A9 / A10 | PASS | **PASS（A10 附注）** | A10 的 "无 `ece-*` 容器" 表述**不准确**：实存 2 个**未运行**的遗留容器（`ece-db-1` Exited(1) 10:57、`ece-api-1` Created 10:54），来自**首轮**失败的 bind-mount 尝试；不影响资源，但建议清理 → 见 §7.4 |
| **A11** | FAIL | **PASS** | 计数 14 正确、表述与证据对齐 |
| A12 | PASS | **PASS** | — |

### 7.4 二轮裁定与遗留

**PASS —— OEI-003 关闭。**

理由：A1–A12 全部达成。首轮的核心问题（**证据全在 mock 模式下取**）已彻底纠正：引用渲染、确定性、字段清单、契约校验全部改为**真实 Onyx 引擎**取证，并且由 codex 现场独立复跑确认（HTTP 200 / `onyx` / `v4.7.8` / 渲染出 `methodology-framework.md`）。A8 的"无回归"结论也经根因独立佐证。**ECE 至此真的把 Onyx 用起来了，并且用自己的界面绕过了 Onyx UI 不渲染引用的缺陷。**

**两项非阻塞遗留（交给下一刀或用户）**：

1. **清理残留容器**：`ece-db-1`（Exited 1）、`ece-api-1`（Created）——首轮 bind-mount 失败留下的尸体。删除属容器操作，cc 未被授权 rm，故保留；建议由用户或下一刀授权清理。
2. **`ece/` 仓有未提交改动**（940 个 modified/untracked 条目，其中绝大多数是 `._*` 垃圾与模式位变化，真实内容改动只有新模块 + `main.py` +4 行）。**建议提交**，理由：① 后续无回归检查才有干净基线；② 避免与 OEI-004 改动混淆。
3. **`ece/TASKS.md` / `docs/API.md` 未回填**（cc 已如实记录，留待后续刀）。

**资源警告（演示前必须处置）**：现场 **Swap 8.0GiB / 8.0GiB 已用满（剩余 16MiB）**，Mem available 1.5GiB。占用者全是 Onyx 自身栈：`llama-server` 2.46GB、OpenSearch JVM 2.10GB、两个 `model_server` 各 1.78GB（无 ECE 残留进程）。建议演示前 `swapoff -a && swapon -a` 清一次，并考虑把 `.wslconfig` 提到 16GB。
