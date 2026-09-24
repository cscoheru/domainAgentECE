# OEI-001 任务书 — Onyx CE 咨询知识库首验（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v3** ｜ 签发日期：2026-09-23 ｜ v2 原文存档于同目录 `TASK.v2.md`（只读）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## v2 → v3 变更记录（codex，2026-09-23）

1. **修正失效的 API 事实来源**：v2 §1 指定 `GET http://127.0.0.1:8080/openapi.json` 为"唯一事实来源"，实测该路径以及 `/docs`、`/api/docs` **全部 404**（本部署 `ENABLE_PUBLIC_DOCS` 关闭）。已替换为 codex 只读反查出的真实端点表（见 §1.1）。
2. **消除"建 project"歧义**：v2 只写"创建 project"未给端点，cc 于 20:52 打到管理侧 `/api/manage/admin/document-set`，返回 400（`Cannot create a document set with no connectors`）。正确端点为 `/api/user/projects/create`。
3. **补齐编号验收标准 A1..A11 与心跳约定**，对齐 `CODEX-ROLE.md` §4「签发任务书的必备结构（缺项即视为无效任务书）」。
4. **补边界与重复性要求**（负例查询、精确命中查询、同查询 3 次一致性），原 v2 只有"检索命中文档正确"这类不可判定表述。
5. 目标、范围、部署前提**不变**。

---

## 0. 一句话目标

证明 Onyx CE 能作为 ECE 的"内容与检索引擎"承载咨询行业知识：建 project、传 3 类文档、确认索引、验证检索质量，并记录 CE/EE 能力边界。

**架构定位（不可偏离）**：ECE 拥有身份/权限/来源/审计/领域对象/工作流；Onyx CE 只是可替换的内容与检索引擎。本刀只做引擎侧验证，不写任何 ECE 代码。

## 1. 环境事实（已验证，直接信任，不要重新部署）

- Onyx CE v4.7.8，community tier，`gpu_enabled=true`，`ee_features_enabled=false`
- 服务入口（WSL 本机）：`http://127.0.0.1:8080`；局域网：`http://192.168.5.237:8080`
- 9 个容器在跑（api_server / background / web_server / relational_db / opensearch / cache / inference_model_server / indexing_model_server / nginx），`/api/health` 返回 200
- Compose 目录：`/home/codex/onyx-lab/src/deployment/docker_compose`（只读；实测 `fisher` 用户对该路径 **无读权限**，不要尝试）
- 账号凭据由你自行输入或从用户处获取，**不要写进任何文件**

### 1.1 真实 API 端点表（codex 于 2026-09-23 只读反查，替代 v2 的 `/openapi.json` 指针）

来源：运行中的 api_server 内 `app().openapi()`（533 条路由）+ 空 body 探针（422 表示路由存在且未被权限拦，**非 403**）。

| 动作 | 方法 | 路径 | 已验证的契约 |
|---|---|---|---|
| 建 project | POST | `/api/user/projects/create?name=<URL编码名称>` | `name` 是 **query 参数**（必填）；探测返回 422（缺 name），非 403 |
| 列 project | GET | `/api/user/projects` | 返回数组；探测时返回 `[]` |
| 上传文件 | POST | `/api/user/projects/file/upload` | `multipart/form-data`，文件字段名是 **`files`**（数组，可多文件）；另有可选字段 `project_id`（**整数**） |
| 文件索引状态 | POST | `/api/user/projects/file/statuses` | JSON body `{"file_ids": ["<uuid>", ...]}`（`file_ids` 必填） |
| 项目内文件 | GET | `/api/user/projects/files/{project_id}` | 列出该项目文件 |
| 文件详情/删除 | GET/DELETE | `/api/user/projects/file/{file_id}` | — |
| 检索 | POST | `/api/search` | JSON body `{"query": "<文本>"}`（`query` 必填，1..2048 字符）；可选 `sources` / `document_sets` / `tags` / `time_cutoff` / `persona_id` 等 |

**不要使用** `/api/manage/admin/document-set`（v2 误用并失败的那条）：它属于管理侧 document set，本刀不用。

需要自行核对路由时，用下面这条只读命令（**不要**再试 `/openapi.json`）：

```bash
docker exec onyx-api_server-1 python -c \
  "from onyx.main import app; s=app().openapi(); [print(p) for p in sorted(s['paths'])]"
```

### 1.2 凭据事实

- 磁盘上可复用的会话属于 `codex@onyx-lab.example.com`：`is_superuser=false`、`account_type=STANDARD`、`token_expires_at=2026-09-30`。
- 该账号对 `/api/user/projects*` 与 `/api/search` **均可通过**（codex 已用 200/422 探针验证）。**本刀不需要管理员账号**。
- 若某一步确实需要管理员权限，如实记 FAIL + 原因，不要自行提权、不要新建管理员账号。
- 会话 Cookie 只放 WSL 原生路径：`/home/fisher/.onyx-lab/.secrets/admin-cookies.txt`（`chmod 600`，你已于 20:50 建好）。**任何 evidence / report / 日志里不得出现 Cookie 或 token 原文**，一律写 `<REDACTED>`。

### 1.3 脚本现状（不要改脚本）

- `bin/collect-diagnostics.sh` 可直接用；注意它在缺少 GPU 工具时会尝试 `docker run --rm --gpus all ...`，若失败请按 `gpu info unavailable` 如实记录，**不要**因此改脚本。
- `bin/onyx-upload.sh` **不适用本刀**：其默认端点 `/api/management/admin/connector/file/upload` 在本机不存在，且表单字段名是 `file` 而真实 API 要 `files`。本刀上传**直接手写 curl**，并在 `REPORT.md` 的"建议"段记录该缺陷（**只记录，不修改**）。

## 2. 工作区（所有产出物写到这里）

```
/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-001/
├── TASK.md            ← 本文件（v3，只读，不要改）
├── TASK.v2.md         ← v2 存档（只读，不要改）
├── workspace/         ← 你生成的 3 份 Markdown 源文件
├── evidence/          ← 所有请求/响应 JSON、检索结果、资源诊断（按 01.. 序号命名）
├── REPORT.md          ← 收口报告
└── DONE               ← 全部完成后创建（内容写完成时间）
```

**已有产物（保留，不要删）**：`evidence/diagnostics-pre.json`（20:50，有效）、`evidence/project-create.json`（20:52，v2 失败尝试，保留作为纠错证据）。`workspace/` 目前为空，从下面步骤 2 继续。

**证据命名**（与步骤对应）：`01-project-create.json`、`01b-project-list.json`、`02-workspace-size.txt`、`03-upload-<name>.json`、`03b-project-files.json`、`04-status-poll-<n>.json`、`05-search-q1.json`…、`06-search-negative.json`、`06-search-exact.json`、`07-repeat-1..3.json`、`08-diagnostics-post.json`、`09-compliance-check.txt`、`10-container-snapshots.txt`。

## 3. 任务步骤

**步骤 1 — 建 project**

```bash
curl -sS -b "$HOME/.onyx-lab/.secrets/admin-cookies.txt" \
  -X POST 'http://127.0.0.1:8080/api/user/projects/create?name=OEI-001%20Consulting%20Lab' \
  -o evidence/01-project-create.json -w '%{http_code}\n'
curl -sS -b "$HOME/.onyx-lab/.secrets/admin-cookies.txt" \
  'http://127.0.0.1:8080/api/user/projects' \
  -o evidence/01b-project-list.json -w '%{http_code}\n'
```

记录返回的 project id（整数），后续上传要用。

**步骤 2 — 造文档**：在 `workspace/` 生成 3 份有实质内容的 Markdown（中文，每份 ≥ 400 字，**每份必须含字面量 `Demo Case`** 明确标注为演示案例）：

- `case-management-consulting.md` — 管理咨询案例（背景/问题/方法/交付/结果）
- `methodology-framework.md` — 咨询方法论（问题树 / 假设驱动 / MECE 的应用说明）
- `play-sales-delivery.md` — 销售→交付衔接 play（阶段、动作、产出物、责任人）

把字符数证据落盘：`wc -m workspace/*.md > evidence/02-workspace-size.txt`

**步骤 3 — 上传**：逐份上传（字段名必须是 `files`）：

```bash
curl -sS -b "$HOME/.onyx-lab/.secrets/admin-cookies.txt" \
  -F "files=@workspace/case-management-consulting.md" \
  -F "project_id=<project_id>" \
  'http://127.0.0.1:8080/api/user/projects/file/upload' \
  -o evidence/03-upload-case.json -w '%{http_code}\n'
```

三份都上传后，拉一次项目文件清单确认三份都在：`GET /api/user/projects/files/<project_id>` → `evidence/03b-project-files.json`。从响应中取 3 个 file_id（uuid）。

**步骤 4 — 轮询索引状态**：用 `POST /api/user/projects/file/statuses`，body `{"file_ids": [...]}`，**每次轮询都单独落盘一份** `evidence/04-status-poll-<n>.json` 并在 REPORT 记录时间戳。上限：最多 20 次、每次间隔 15 秒；超限即记 FAIL 并写明原因。最终状态另存 `evidence/04-status-final.json`。

> 状态字段名与取值以你实际读到的响应为准，写入 REPORT 时请写明字段名与含义，**不要套用预期词**。

**步骤 5 — 检索验证（≥3 个查询）**：例如「问题树怎么用」「销售转交付的关键动作」「咨询项目的交付物清单」。每个查询保存完整响应：`evidence/05-search-q1.json` 等。每个查询给出**命中判定**，且判定必须能核对到 `workspace/` 源文件（引用文件名 + 片段或行号）。

**步骤 6 — 两侧边界**：

- 负例：一个与三份文档无关的主题（如 `zzz-nonexistent-topic-9371`）→ `evidence/06-search-negative.json`
- 正例：一个与某份文档标题/专有词精确一致的词 → `evidence/06-search-exact.json`

**步骤 7 — 重复性**：挑一个查询连续执行 3 次 → `evidence/07-repeat-1..3.json`，比较 3 次返回的**文档 id 集合**（顺序可不同）是否一致。

**步骤 8 — 资源诊断（索引后）**：`bin/collect-diagnostics.sh OEI-001/evidence/08-diagnostics-post.json`（`diagnostics-pre.json` 已存在于 20:50，作为"索引前"基线，不要覆盖它）。再取一次容器快照 `evidence/10-container-snapshots.txt`（含 `docker ps` 的 Up 时长，用于证明容器未被重启）。

**步骤 9 — 写 `REPORT.md`**，必须含：

- 范围声明
- 逐步实测结果（每步 PASS/FAIL + 证据文件指针）
- 检索质量评估（命中准确度 / 引用可追溯性）
- 资源结论（索引前后内存变化数字；i9 + WSL 能否长期承载标准档，给 YES/NO/CONDITIONAL + 依据）
- CE/EE 边界清单（≥8 项能力；其中**外部源权限同步 / 用户组 / SSO / SCIM / 高级审计** 5 项必须出现，标注 CE 或 EE 或 UNKNOWN 及依据来源；UNKNOWN 不得写成结论）
- 与任务书的偏差说明
- 建议（只写建议，不实现；含 §1.3 的脚本缺陷）

## 4. 验收标准（codex 将逐条核对，每条都必须能被 evidence 证明）

- [ ] **A1** project 存在：`evidence/01-project-create.json` 为 2xx 且含 project id；`evidence/01b-project-list.json` 中出现 `name` = `OEI-001 Consulting Lab`
- [ ] **A2** workspace：恰好 3 份 `.md`，每份 `wc -m` ≥ 400（证据 `02-workspace-size.txt`），每份含字面量 `Demo Case`
- [ ] **A3** 上传：3 份文件的原始上传响应全部落盘且为 2xx；能从上传响应或 `03b-project-files.json` 取到 **3 个不同的 file_id**
- [ ] **A4** 索引：轮询记录含**每次的时间戳与原始状态**（至少首次与最终两次快照），最终 3 个 file_id 全部达到"已索引"；轮询未超过上限（20 次 × 15 秒），超限即 FAIL
- [ ] **A5** 检索：≥3 个查询，每个都有请求（脱敏）+ 完整响应落盘；每个查询给出命中判定，判定引用了 `workspace/` 源文件中的可核对片段（文件名 + 片段或行号）
- [ ] **A6** 边界两侧：负例查询与精确命中查询的响应均落盘，并各给出判定（负例不得声称"命中正常"而不给依据）
- [ ] **A7** 重复性：同查询 3 次响应落盘，给出文档 id 集合"一致/不一致 + 差异明细"的结论；不一致时必须量化哪几项稳定、哪几项漂移
- [ ] **A8** 资源结论：索引前（`diagnostics-pre.json`）与后（`08-diagnostics-post.json`）各一份；给出内存变化数字；对"能否长期承载标准档"给出 YES/NO/CONDITIONAL 及依据
- [ ] **A9** CE/EE 边界清单：≥8 项能力，每项标注 CE / EE / UNKNOWN 与依据来源；5 项强制项（外部源权限同步、用户组、SSO、SCIM、高级审计）不得缺席
- [ ] **A10** 合规：`grep -rIl -E 'admin-cookies|Bearer |token=|password' OEI-001/ || echo clean` 的输出落盘（`09-compliance-check.txt`），且无命中；容器未被重启/停止（`10-container-snapshots.txt` 中 Up 时长合理）；未改上游源码 / compose / `.env` / ECE 主仓 / 本目录脚本
- [ ] **A11** `REPORT.md` 对 A1..A10 每条都有明确结论 + 证据指针，且不含"应该没问题"这类模糊表述

## 5. 完成后的动作（严格按序）

1. 确认 §2 目录结构与 `evidence/` 齐全、无密钥泄漏
2. `echo "$(date -Iseconds) OEI-001 complete (TASK v3)" > DONE`
3. **STOP**：不要开始任何下一刀工作
4. 等 codex 在本目录写 `VERDICT.md`：
   - `PASS` → 本刀关闭，等 codex 签发 OEI-002
   - `FAIL` → 按 `VERDICT.md` 的 R{n} 项返工；删旧 `DONE`、重做、重建 `DONE`

## 6. 硬约束（违反即 FAIL）

- ❌ 不 commit、不 push
- ❌ 不修改 Onyx 上游源码；不读改 `/home/codex/onyx-lab/src`（实测无读权限，不要尝试绕过）
- ❌ 不 restart / stop / down / rm 任何容器；不改 compose 与 `.env`；不启动 code-interpreter
- ❌ 不触碰 `/mnt/c`
- ❌ 不改 `onyx-lab/bin/` 下的脚本、不改 `TASK.v2.md`、不删已有 evidence
- ❌ 不做任务书范围外的功能；发现必须做的额外事项，写进 `REPORT.md` 的"建议"段

## 7. 心跳约定

- 你（cc）的心跳检查对象：`onyx-lab/OEI-001/VERDICT.md`。未出现则静默等待，不重复执行、不打扰用户。
- codex 的心跳检查对象：`onyx-lab/OEI-001/DONE`。无新文件则静默。
