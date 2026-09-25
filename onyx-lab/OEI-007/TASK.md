# OEI-007 任务书 — 咨询文档入库管道（上传 → 引擎入库 → 咨询元数据 → 立即可召回）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-24
> 返工约定：本刀若需返工，一律标 **`OEI-007 R1` / `R2`**（不插新刀、不顺延编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## 0. 一句话目标

让**一份咨询文档从"拖进来"到"能在 Consulting Library 里被检索、被引用、被业务维度过滤"这条链路真正打通**：真实文件进得来、进来就被打上咨询元数据、索引完成后**立刻可被召回**。

**为什么是这一刀**：阶段目标已收敛为"把咨询行业做实做透"。而"做实"的第一硬指标是**知识从哪来**——现在引擎里只有 3 份 Demo 文档，且 ECE 侧**根本没有上传入口**，只能手工调 API 塞内容。语料上不去，检索质量、领域覆盖、演示说服力都无从谈起。

## 1. 现状与范围锁

### 1.1 现状（codex 已核实）

- **ECE 侧无上传入口**：`/api/v1/ingest/runs` 是"服务端读目录"的连接器（`csv:/json:/docs:folder`），**不是文件上传**；全仓 `UploadFile` / multipart 相关代码为 0
- `ContentEnginePort` 已有只读三方法（`search()` / `engine_status()` / `list_projects()`），**没有写路径**
- 咨询静态目录 36 个对象，类型分布 case 10 / methodology 10 / proposal_play 6 / deliverable_template 4 / risk_check 4 / industry_note 2；**`client_industry` 有 24/36 为空**（"做透"的另一个缺口，见 §1.3）
- 引擎侧：project `id=1` 内有 3 份文档；**文本抽取由引擎负责**（Onyx 自带文件处理器）
- 环境已有 `python-multipart 0.0.32` → **上传不需要新依赖**

### 1.2 本刀做

上传入口 → 引擎写路径（Port 扩展）→ 咨询元数据（复用既有词表）→ 索引状态可见 → **立即可召回** → 失败/幂等/降级 → 机器可校验的可见性证据 → 文档与提交。

### 1.3 本刀**不做**（明确划界，避免又混变量）

- 不做批量历史导入、不做目录同步/定时任务
- 不做权限与审计（**OEI-008**）
- 不做检索质量调优（rerank / 换更大模型 / query rewrite）——它是"做透"的另一条线，单独成刀
- 不扩写 36 个种子对象的内容（`client_industry` 24/36 为空的问题**登记为下一刀候选**，本刀不动）
- 不做 LLM 自动打标（LLM 打标不确定，无法做确定性验收；**本刀只做确定性词典建议**，LLM 辅助留后）

## 2. 环境事实（codex 实测，可直接信任）

### 2.1 引擎侧写路径（已验证存在）

| 用途 | 方法 | 路径 | 契约 |
|---|---|---|---|
| 上传文档 | POST | `/api/user/projects/file/upload` | `multipart/form-data`；文件字段名 **`files`**（可多文件）；可选 `project_id`（**整数**） |
| 索引状态 | POST | `/api/user/projects/file/statuses` | body `{"file_ids":[<**user_file.id**>]}` → status `PROCESSING/COMPLETED` + `chunk_count`（传底层 `file_id` 会返回 `[]`） |
| 项目内文件 | GET | `/api/user/projects/files/1` | 列出 project 1 的文件 |

凭据：`ECE_ONYX_COOKIE_FILE` → `/home/fisher/.onyx-lab/.secrets/admin-cookies.txt`（600）；`ECE_ONYX_BASE` 默认 `http://127.0.0.1:8080`；`ECE_CONTENT_ENGINE=onyx|mock`（默认 mock）。

### 2.2 咨询元数据词表（**必须复用，不得另造**）

来源：`src/ece/consulting/seed/consulting_objects.json` 的 36 个对象，字段 `type` / `engagement_phase` / `client_industry` / `problem_types` / `methods`。
**硬要求**：新文档写入的元数据取值必须落在这些既有取值集合内（否则 `facets` 聚合会裂成两套）。若确实缺某取值，**先在报告里提出**，不要私自扩词表。

### 2.3 本地可见性链路（端口 8181；8080 被 Onyx 占用）

```bash
uv run uvicorn ece.main:app --host 127.0.0.1 --port 8765
uv run python scripts/cut_045_local_origin.py --port 8181 --upstream http://127.0.0.1:8765
# 必须：export no_proxy=127.0.0.1,localhost   （urllib 不认 127.* 通配，否则 502）
```

### 2.4 回归基线

OEI-006 后：**`705 passed / 0 failed`**。注意 `make seed-fixtures` 目前**缺第 4 个 seeder**（`scripts/seed_v0_spike_fixture.py`）→ 见步骤 0。**任何多于基线失败数的结果都是真回归。**

## 3. 工作区与证据命名

```
onyx-lab/OEI-007/
├── TASK.md      ← 本文件（只读）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

`00a-step0-makefile.txt`、`00b-step0-skip-guard.txt`、`01-port-write-path.json`、`02-upload-endpoint.json`、`03-metadata-determinism.json`、`04-index-status.json`、`05-recall-after-upload.json`、`06-facets-filter.json`、`07-failure-paths.json`、`08-idempotency.json`、`09-binary-format.json`、`10-visibility-dom-proof.md`、`11-test-before-raw.txt`、`12-test-after-raw.txt`、`13-docs-backfill.txt`、`14-git-commit.txt`、`15-compliance-check.txt`

## 4. 任务步骤

**步骤 0 — 收 OEI-006 转出的两项尾巴**

1. `ece/Makefile` 的 `seed-fixtures` 补上 `scripts/seed_v0_spike_fixture.py`（**或**把 `ece/README.md` 的"期望数字"改成带前提的写法）——二选一，在报告里说明你选哪个及理由；目标是**让文档化的命令跑出来就是 0 failed**。
2. `tests/integration/test_cut_045_local_origin_smoke.py` 的 skip 守卫**补"无 DB"判断**：codex 实测不设 `DATABASE_URL` 时它仍 FAIL 而非 SKIP。

**步骤 1 — 给 Port 加写路径**

- 新增 `upload_document(filename, content: bytes, *, project_id, title=None, metadata=None) -> EngineDocument` 与 `document_status(engine_doc_id) -> EngineDocumentStatus`
- `OnyxContentEngineAdapter` 走 §2.1 真实端点；`MockContentEngineAdapter` 提供离线确定性实现（**mock 必须能在无网络、无引擎时跑通全部单测**）
- 分层纪律不变：领域层不 import 任何 Onyx 专有物

**步骤 2 — ECE 上传端点**

- `POST /api/v1/consulting/documents`（`multipart/form-data`）：`file`（可多个）+ `title`（可选）+ 咨询元数据字段（可选）
- 扩展名白名单 + 单文件/总量大小上限明确写进 `docs/API.md`；**白名单只做"是否接受"判断，文本抽取交给引擎**
- 返回：每个文件的 `document_id` / `accepted|rejected` / `reason`

**步骤 3 — 咨询元数据（确定性）**

- 词表复用 §2.2；提供**基于文件名+标题的词典建议**（`suggested_metadata`），同输入连跑 **N=5** 必须逐字段一致
- 调用方显式传入的元数据**优先于**建议值

**步骤 4 — 状态可见 + 上传入口可见**

- `GET /api/v1/consulting/documents/{document_id}`：`PROCESSING → COMPLETED`（含 `chunk_count`）或 `FAILED + reason`
- Library 视图（`demos/spa` 视图 D）里加**上传区与状态区**（沿用 OEI-006 的分组风格；DOM 锚点命名清晰）

**步骤 5 — 闭环验证（本刀的核心）**

上传一份**新**咨询文档（建议做成"某行业某阶段某方法"的真实感内容）→ 轮询索引状态到 COMPLETED → 然后用一个**只可能命中它**的 query 调 `/api/v1/consulting/library` → 断言 `engine_items` 里出现它，并与 `POST /api/search` 的原始返回**逐条对应**。

**步骤 6 — 失败与边界（每类都要留原始响应）**

① 不支持的扩展名；② 0 字节文件；③ 超过上限的大文件；④ 引擎不可达（`ECE_ONYX_BASE=http://127.0.0.1:9`）；⑤ 多文件中部分成功。**要求**：明确 HTTP 码 + 结构化原因，无未捕获异常；静态目录行为不受影响。

**步骤 7 — 幂等**

同名同内容重复上传：给出明确策略（覆盖更新 / 去重跳过，**你定但要写清**），并证明**不会在 Library 里产生重复卡片**。

**步骤 8 — 测试**

1. **DB 无关单测**（新文件，如 `tests/unit/test_consulting_documents.py`）：白名单、大小上限、元数据建议确定性、幂等策略、错误映射、Port 写路径的 mock 实现
2. **端点级**：multipart 上传 → 状态查询 → 静态字段不受影响
3. **无回归**：`705 passed / 0 failed` 不劣化（落盘原始汇总行）

**步骤 9 — 可见性证据（机器可校验，不许要用户截图）**

- 经同源代理取上传页/状态区的 **HTML 转储**，列出新增 DOM 锚点并断言其存在
- 贴一次**经代理的 API 原始输出**（上传 + 状态 + 召回）
- 可选：请用户**登录看一眼有没有**（一次是非题，**不作为验收必要条件**）

**步骤 10 — 文档与提交**：`docs/API.md` 补新端点与元数据词表；`ece/TASKS.md` 登记；`git add` + `git commit`（**不 push**）

## 5. 验收标准（codex 将逐条核对）

- [ ] **A0** 步骤 0 两项处置完成（Makefile 或 README 之一 + skip 守卫补 DB 判断），且文档化命令跑出来是 `0 failed`
- [ ] **A1** 上传端点可用：多文件 multipart 成功，返回每个文件的 accepted/rejected 与原因；白名单与大小上限在 `docs/API.md` 有明文
- [ ] **A2** 引擎写路径**真实生效**（onyx 模式）：新文档出现在 `GET /api/user/projects/files/1`，索引状态可达 `COMPLETED` 且带 `chunk_count`
- [ ] **A3** 咨询元数据：取值全部落在 §2.2 既有词表内（给出集合包含证明）；`suggested_metadata` 同输入 **N=5** 逐字段一致
- [ ] **A4** **立即可召回（核心）**：上传后，`library` 的 `engine_items` 命中该新文档，且与 `/api/search` 原始返回逐条对应（标题 + doc_id + 片段）
- [ ] **A5** facets 生效：新文档的元数据能在 `facets` 里聚合出来，并可据此过滤
- [ ] **A6** 失败路径：5 类场景各有原始响应 + 明确原因 + 无未捕获异常
- [ ] **A7** 幂等：重复上传不产生重复卡片（策略 + 证据）
- [ ] **A8** 二进制格式：≥1 个非文本样本（建议 docx，用 `zipfile`+XML 构造）能入库并被召回；**未引入任何解析库**（`pyproject.toml` diff 为空或只含必要注释）
- [ ] **A9** 无回归：`12-test-after-raw.txt` 的 failed 数 ≤ 基线（0）
- [ ] **A10** 可见性证据为**机器可校验**（HTML 转储 + DOM 锚点断言 + 经代理 API 原始输出）；**报告中不得出现"请用户截图"作为验收项**
- [ ] **A11** 合规：无凭据值落盘；未碰 Onyx 上游/compose/`.env`/swap/`.wslconfig`；36 个种子对象与三域业务逻辑未改；既有测试断言语义未改；未 push
- [ ] **A12** `REPORT.md` 对 A0..A11 每条有结论 + 证据指针，无模糊表述

## 6. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏、临时资源已清理
2. `echo "$(date -Iseconds) OEI-007 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭；FAIL → 按 `R1/R2…` 返工（**编号不变**）

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：改 `src/ece/consulting/**`、`src/ece/connectors/onyx/**`、`src/ece/api/**`、`demos/spa/**`、`docs/API.md`、`TASKS.md`；`Makefile` **仅限步骤 0 那一处**；`tests/**` **仅允许新增文件 + 步骤 0 的 cut_045 守卫**；可起临时 `ece-pg-tmp` 跑套件；可 `git commit`（**不 push**）；可只读调用 Onyx `/api/*`
- ❌ **不引入新依赖**（`pyproject.toml` 除注释外不得改）——文本抽取交给引擎，二进制样本用 `zipfile` 构造
- ❌ 不改 36 个种子对象内容；不改采购/知识/合规三域业务逻辑与其测试断言
- ❌ 不 restart/stop/down/rm 任何 Onyx 容器；不改 Onyx 上游/compose/`.env`；不碰 swap/`.wslconfig`
- ❌ **不得以"用户截图"作为任何验收项或证据**
- ❌ 不做 OEI-008 及以后的权限/审计/演示台内容

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-007/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-007/DONE`
- 无新文件则静默，不重复执行、不打扰用户
