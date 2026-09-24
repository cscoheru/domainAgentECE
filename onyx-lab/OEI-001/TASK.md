# OEI-001 任务书（返工版）— Onyx CE 咨询知识库首验（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v4（返工）** ｜ 签发日期：2026-09-23
> 历史存档：`TASK.v2.md`、`TASK.v3.md`（均只读，不要改）
> 状态机：本文件 → cc 执行 → 删旧 `DONE` → 重建 `DONE` → codex 审验 → `VERDICT.md`

## v3 → v4 变更记录（codex，2026-09-23）

1. **返工范围由 `VERDICT.md`（21:44）第 5 节裁定**：R1 采用**方案 A**（为 Onyx 配置 default LLM 后原样重跑检索），R2/R3/R4 为报告与证据修正。
2. **A10 验收标准修正**（原表述有缺陷）：v3 让 cc 运行 `grep -rIl -E 'admin-cookies|...' OEI-001/` 并要求"无命中"，但该模式串本身写在 `TASK*.md` 与扫描记录里，**逻辑上不可能无命中**。v4 改为"只扫 cc 产出物 + 凭据值级模式"。
3. **新增 §1.4 LLM 配置 API 契约**（codex 只读反查确认），把"配 LLM"从模糊前置变成可执行步骤。
4. **新增强制前置校验（步骤 0）**：LLM 未就绪就停，不允许自己找替代路径或臆测。
5. A1–A4、A8、A9、A11 的**已通过结论与既有证据保持有效，不重做**；重跑只针对 A5/A6/A7。

---

## 0. 一句话目标

在写入侧已证（项目 / 上传 / 索引 / 状态）的基础上，**补齐查询侧**：为 Onyx 配置 default LLM 后，重跑检索验证，证明 Onyx CE 能真正被当作 ECE 的内容与检索引擎使用。

**架构定位（不可偏离）**：ECE 拥有身份/权限/来源/审计/领域对象/工作流；Onyx CE 只是可替换的内容与检索引擎。本刀只做引擎侧验证，不写任何 ECE 代码。

## 1. 环境事实（可直接信任）

- Onyx CE v4.7.8，community tier，`gpu_enabled=true`，`ee_features_enabled=false`
- 入口（WSL 本机）：`http://127.0.0.1:8080`；局域网：`http://192.168.5.237:8080`
- 9 个容器在跑，`/api/health` = 200
- 上游源码 `/home/codex/onyx-lab/src`：`fisher` 用户**无读权限**，不要尝试
- `OEI-001` 既有产物（**保留，不要覆盖、不要删**）：1 个 user project `id=1`（`OEI-001 Consulting Lab`）、3 份已 COMPLETED 的文件（user_file.id：`7bb48d46…` case / `1457df88…` methodology / `3b14b918…` play；chunk_count 3/4/4）、`evidence/` 中既有 25 个文件

### 1.1 真实 API 端点表（v3 已验，继续有效）

| 动作 | 方法 | 路径 | 契约 |
|---|---|---|---|
| 建 project | POST | `/api/user/projects/create?name=<URL编码>` | `name` 是 query 参数 |
| 列 project | GET | `/api/user/projects` | 数组 |
| 上传 | POST | `/api/user/projects/file/upload` | 表单字段名 **`files`**；`project_id` 为**整数** |
| 索引状态 | POST | `/api/user/projects/file/statuses` | body `{"file_ids":[...]}`，**必须传 `user_file.id`**（传底层 `file_id` 会返回 `[]`） |
| 项目内文件 | GET | `/api/user/projects/files/{project_id}` | — |
| 检索 | POST | `/api/search` | body `{"query":"..."}`（`query` 必填） |

路由自证命令（`/openapi.json`、`/docs` 在本部署均为 404）：

```bash
docker exec onyx-api_server-1 python -c \
  "from onyx.main import app; s=app().openapi(); [print(p) for p in sorted(s['paths'])]"
```

### 1.2 凭据事实

- 可复用会话：`codex@onyx-lab.example.com`（`is_superuser=false`、STANDARD、到期 2026-09-30），落在 `/home/fisher/.onyx-lab/.secrets/admin-cookies.txt`（600）。
- **实测该账号可直接调用 `/api/admin/llm/*` 管理端点**（空体 PUT 返回 422 校验错误而非 403），**本刀不需要管理员账号**。
- **任何 evidence / report / 日志不得出现 cookie 或 API key 原文**，一律 `<REDACTED>`。

### 1.3 脚本现状

- `bin/collect-diagnostics.sh` 可直接用。
- `bin/onyx-upload.sh` 已由 codex 修好（默认端点与字段名均已修正），本刀如需上传可直接用；**不要改它**。

### 1.4 LLM 配置 API 契约（codex 只读反查，v4 新增）

| 动作 | 方法 | 路径 | 要点 |
|---|---|---|---|
| 写入 provider | PUT | `/api/admin/llm/provider` | body 字段：`provider`(必填) / `name` / `api_key` / `api_base` / `api_version` / `custom_config` / `deployment_name` / `is_public` / `model_configurations[]` |
| 列出 provider | GET | `/api/admin/llm/provider` | 返回 `{providers, default_text, default_vision, default_chat_naming}` |
| 设默认模型 | POST | `/api/admin/llm/default` | 把已写入的 provider/model 设为 default |
| 连通性测试 | POST | `/api/admin/llm/test` | 配置后必须先测通再重跑检索 |
| 列可用模型 | POST | `/api/admin/llm/openai-compatible/available-models` | OpenAI 兼容端点用；同族还有 `ollama/available-models`、`litellm/available-models` 等 |

支持的 provider 取值（实测自源码常量）：`openai`、`openai_compatible`、`anthropic`、`azure`、`bedrock`、`vertex_ai`、`ollama_chat` 等。**`openai_compatible` + `api_base` 可指向任意 OpenAI 兼容服务**（本机在国内网络下这是首选路径）。

**前置由用户在 Web UI 配置（用户决策 2026-09-23 22:0x）**：在管理面板的 LLM/模型配置页写入 provider 与模型，并**务必设为 default（文本模型）**——UI 若未自动设默认，用 `POST /api/admin/llm/default` 补上。cc 只做步骤 0 的只读验证，不代配、不改 provider。

## 2. 工作区

```
/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-001/
├── TASK.md            ← 本文件（v4，只读）
├── TASK.v2.md / TASK.v3.md  ← 历史存档（只读）
├── VERDICT.md         ← codex 裁定（只读，返工依据）
├── workspace/         ← 3 份源文档（已完成，不改）
├── evidence/          ← 新增证据一律用 11.. 之后的新序号，不要覆盖旧文件
├── REPORT.md          ← 更新为 v2（覆盖同一文件即可，但需在头部写明 v2 与变更点）
└── DONE               ← 返工完成后重建
```

**证据命名（新增）**：`11-llm-precondition.json`、`12-search-q1.json`…、`12-search-q2.json`、`12-search-q3.json`、`13-search-negative.json`、`13-search-exact.json`、`14-repeat-1..3.json`、`15-diagnostics-post-llm.json`、`16-compliance-check.txt`。

> 注意：**不要覆盖或删除 v3 时代的 `05-*` / `06-*` / `07-*` 证据**——它们是"配 LLM 之前失败"的历史证据，R1 的对照基线。

## 3. 返工步骤

**步骤 0 — 前置校验（不满足即停）**

```bash
curl -s -b "$HOME/.onyx-lab/.secrets/admin-cookies.txt" \
  http://127.0.0.1:8080/api/admin/llm/provider -o evidence/11-llm-precondition.json -w '%{http_code}\n'
```

判定：`providers` 非空 **且** `default_text` 非 null → 继续；否则**立即停**，把原始响应留档并在 REPORT 写明"前置未就绪，等待用户配置"，**不要自行新增 provider、不要用猜测的 key、不要绕路**。

> 前置由用户负责完成（用户在 Onyx Web UI 或按 §1.4 的 API 配置 provider + default model）。cc 只验证，不代配。

**步骤 1–4 — 已通过，不重做**。既有 evidence 保持原位；如你出于完整性重跑，请**新增**文件而非覆盖。

**步骤 5 — 重跑检索验证（对应 A5）**：原样重跑 v3 的 3 个查询（`问题树怎么用` / `销售转交付的关键动作` / `咨询项目的交付物清单`），每个保存完整响应到 `evidence/12-search-q*.json`。响应里若同时含生成答案与召回文档，**把召回文档的字段名和内容一并保留**（长文本可截断但须注明截断位置）。每个查询给出命中判定，判定必须能核对到 `workspace/` 源文件（文件名 + 片段或行号）。

**步骤 6 — 两侧边界（对应 A6）**：负例 `zzz-nonexistent-topic-9371` → `evidence/13-search-negative.json`；精确命中词 → `evidence/13-search-exact.json`；各自给出判定与依据。

**步骤 7 — 重复性（对应 A7）**：同一查询连续 3 次 → `evidence/14-repeat-1..3.json`，比较**召回文档 id 集合**（顺序可不同），给出"一致 / 不一致 + 差异明细"。注意：生成本身可能不逐字稳定，**判定基准是文档集合**，不是答案文本。

**步骤 8 — 资源诊断（LLM 配置 + 检索之后）**：`bin/collect-diagnostics.sh OEI-001/evidence/15-diagnostics-post-llm.json`，与 `diagnostics-pre.json`、`08-diagnostics-post.json` 三者对比，更新资源结论。

**步骤 9 — 合规扫描（按 v4 修正后的标准）**：

```bash
grep -rInE 'connect\.sid=|fastapiusersauth=|eyJ[A-Za-z0-9_-]{20,}|api_key\"?\s*[:=]\s*\"?[A-Za-z0-9_-]{20,}' \
  OEI-001/evidence OEI-001/workspace OEI-001/REPORT.md > OEI-001/evidence/16-compliance-check.txt || echo "no credential values found"
```

**步骤 10 — 更新 `REPORT.md`（v2）**，必须含：

- 头部写明 v2 与本次变更点（R1 方案 A / R2 / R3 / R4）
- A5/A6/A7 的**新结论**（PASS 或 FAIL + 原始证据指针 + 与 v3 失败基线的对照）
- 修正 R3 的两处事实错误：v1 报告 §6 的"共 19 个文件"应改为实际计数；`03-upload-*` 表格名称须与磁盘实名一致
- 修正 R2：A9 的 11 项能力逐项补**可追溯来源**（官方文档 URL + 引文）；无法落源的改标 `UNKNOWN`；并区分"本刀实测"与"文献依据"
- 修正 R4：合规证据必须是**原始命令输出**
- 资源结论更新（三份诊断对比）
- 建议（只写建议，不实现）

## 4. 验收标准（codex 将逐条核对）

- [ ] **A1–A4** 沿用 v3 结论（PASS），证据仍有效；抽查若发现与 v3 不符即整体重判
- [ ] **A5** 检索：≥3 个查询，每个有请求（脱敏）+ **完整响应**落盘，HTTP 200；每个给出命中判定，判定引用 `workspace/` 源文件可核对片段
- [ ] **A6** 边界两侧：负例与精确命中各有响应与判定；负例不得在没有依据的情况下声称正常
- [ ] **A7** 重复性：3 次响应落盘，给出召回文档 id 集合"一致/不一致 + 差异明细"的结论
- [ ] **A8** 资源结论更新：三份诊断（pre / post / post-llm）对比 + 内存变化数字 + 长期承载结论（YES/NO/CONDITIONAL + 依据）
- [ ] **A9** CE/EE 边界清单：≥8 项，每项标注 CE/EE/UNKNOWN **且给出可追溯来源**（URL 或引文）；5 项强制项（外部源权限同步、用户组、SSO、SCIM、高级审计）不得缺席
- [ ] **A10**（v4 修正）合规：`16-compliance-check.txt` 为**原始命令输出**且**无凭据值命中**；容器未被重启/停止（新增快照 Up 时长连续）；未改上游源码 / compose / `.env` / ECE 主仓 / `onyx-lab/bin/`
- [ ] **A11** `REPORT.md`（v2）对 A1..A10 每条都有结论 + 证据指针，无模糊表述
- [ ] **A12**（v4 新增）返工合规：未覆盖/删除 v3 时代证据；未新增 Onyx provider（前置由用户配置）；API key 未出现在任何产出物中

## 5. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏
2. **删除旧 `DONE`**（v3 时代的），然后重建：`echo "$(date -Iseconds) OEI-001 rework complete (TASK v4)" > DONE`
3. **STOP**
4. 等 codex 复审并更新 `VERDICT.md`：PASS → 本刀关闭、等签发 OEI-002；FAIL → 按新 R{n} 返工

## 6. 硬约束（违反即 FAIL）

- ❌ 不 commit / 不 push
- ❌ 不修改 Onyx 上游源码；不尝试绕过 `/home/codex/onyx-lab/src` 的读权限
- ❌ 不 restart / stop / down / rm 任何容器；不改 compose 与 `.env`；不启动 code-interpreter
- ❌ 不触碰 `/mnt/c`
- ❌ 不自行新增 / 修改 LLM provider（前置由用户完成；cc 只验证）
- ❌ 不把 API key、cookie 写入任何产出物；不在命令行里回显 key
- ❌ 不覆盖或删除 v3 时代 evidence；不改 `TASK.v2.md` / `TASK.v3.md` / `VERDICT.md` / `onyx-lab/bin/`
- ❌ 不做范围外功能；额外发现写进 REPORT 的"建议"段

## 7. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-001/VERDICT.md`（复审后会被更新）。
- codex 心跳对象：`onyx-lab/OEI-001/DONE`（重建后时间戳应晚于本任务书）。
- 无新文件则静默，不重复执行、不打扰用户。
