# 07-tasks-api-backfill.md
# scan_time: 2026-09-24T16:18:29+08:00
# purpose: OEI-004 step 4 — TASKS.md / docs/API.md 回填

# ----- TASKS.md diff (last 35 lines added) -----

## added section:


### J.3 明确不做

- ❌ 不在本刀内重构权限架构
- ❌ 不新增 IAM / 身份目录 / 凭据轮换能力（Kernel 只拥有 **enforcement point + scope contract**，见 `docs/v3/KERNEL_BOUNDARY.md` §3.1）

---

## 附录 K — Onyx Enterprise Integration 后置交付登记（OEI-003 / OEI-004，2026-09-24）

> 本附录登记已交付但**不属于 v0 PRD 主线**的能力，与 OEI 主线（`../onyx-lab/OEI-*`）一一对应。
> 受 CLAUDE.md §2 铁律约束；本附录不是新 PRD 来源。

### K.1 Onyx / ECE 连接器（OEI-003）

| 能力 | 位置 | 状态 | 备注 |
|---|---|---|---|
| `ContentEnginePort` Protocol | `src/ece/connectors/onyx/port.py` | 已交付 | 3 个方法：`search` / `engine_status` / `list_projects` |
| `EngineStatus` / `EngineDocument` / `EngineProject` Pydantic 模型 | 同上 | 已交付 | 领域层零 Onyx 依赖（grep `import onyx` = 0 命中） |
| `MockContentEngineAdapter`（离线确定性） | `mock_adapter.py` | 已交付 | `ECE_CONTENT_ENGINE=mock` 时使用（默认） |
| `OnyxContentEngineAdapter`（真实 HTTP） | `onyx_adapter.py` | 已交付 | 调用 Onyx `/api/admin/llm/provider` / `/api/user/projects` / `/api/user/projects/files/{id}` / `/api/search` / `/api/version` |
| `get_content_engine()` selector | `selector.py` | 已交付 | 读 `ECE_CONTENT_ENGINE` + `ECE_ONYX_BASE` + `ECE_ONYX_COOKIE_FILE` |
| `GET /engine/status` 状态页（含引用渲染） | `src/ece/api/engine_status.py` + `main.py` | 已交付 | `?q=` 触发 search + ECE 自己渲染引用卡片（绕开 Onyx UI 不渲染引用的 bug） |

### K.2 验收证据（OEI-003 VERDICT.md §7.3 二轮）

- A1 / A2 / A3 / A4 / A5 / A6 / A7 / A8 / A9 / A10 / A11 / A12 全部 PASS
- A8 无回归：`634 passed / 28 failed / 5 errors` baseline vs after 一致（28+5 是 ECE 仓 pre-existing，非 OEI-003 引入）
- A4 真实 Onyx 引用渲染：HTML 含 `v4.7.8` + `methodology-framework.md`（独立由 codex 复跑确认）

### K.3 收尾债（移交 OEI-004 / 用户）

- [ ] `docs/API.md` 新增 `/engine/status` 章节 — **OEI-004 step 4 完成**
- [ ] `tests/unit/test_content_engine_port.py`（DB 无关的 adapter 单测）— 留给后续刀，避免 OEI-003 pytest 环境坑
- [ ] `ece/` 仓真实改动 commit（不含 `._*` 垃圾、`.mypy_cache`、mutation-evidence 历史 dirty）— **OEI-004 step 7 完成**

===== diff summary (TASKS.md) =====
 TASKS.md | 30 ++++++++++++++++++++++++++++++
 1 file changed, 30 insertions(+)

# ----- docs/API.md diff (last 55 lines added) -----

## added section:


### GET /engine/status

返回 Engine 状态快照 + 可选检索引用（HTML 页面，浏览器直接打开）。

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `q` | string | 否 | 若提供，触发一次 `ContentEnginePort.search(q)` 并把召回文档渲染为引用卡片（`source_type` / `engine_doc_id` / snippet） |

**HTML 内容**（无 `q`）：

- 引擎名 + 版本
- tier / GPU 开关
- LLM provider + default model
- 项目数 + 文件数
- 最近一次检索耗时（秒；首次为 None）

**HTML 内容**（带 `q`）：

- 在上述快照之上加 `<h2>Citations for query: {q}</h2>` 段
- 每条召回文档渲染为：`<div class="doc">` 块，含 `<h3>{title}</h3>` + `<div class="meta">`（source_type / engine_doc_id / updated_at）+ `<pre>`（snippet，截断 800 字符）

**降级行为**：当 `ECE_ONYX_BASE` 不可达或 cookie 失效时：

- HTTP 仍为 **200**（不返回 500）
- 页面顶部显示 `Engine degraded: <reason>` 黄色横幅
- 快照字段区显示空集；citations 段显示 "Recall failed (see degraded banner above)"

**选择器**（`ECE_CONTENT_ENGINE`）：

- `mock`（默认）— 离线固定数据，演示/CI 用
- `onyx` — 真实 Onyx 引擎，需配 `ECE_ONYX_BASE` + `ECE_ONYX_COOKIE_FILE`

**示例**：

```bash
# 默认 mock 模式
curl -s 'http://127.0.0.1:8000/engine/status' | less

# 真实 Onyx 模式
ECE_CONTENT_ENGINE=onyx \
ECE_ONYX_BASE=http://127.0.0.1:8080 \
ECE_ONYX_COOKIE_FILE=/home/fisher/.onyx-lab/.secrets/admin-cookies.txt \
uv run uvicorn ece.main:app --port 8000

# 含检索
curl -s 'http://127.0.0.1:8000/engine/status?q=问题树怎么用' | less
```

**安全注意**：

- cookie **不**进 ECE 仓；运行时通过 `ECE_ONYX_COOKIE_FILE` 环境变量读取
- 该端点**不**走权限 / 审计层——只用于内部演示，**不应**对外暴露

===== diff summary (docs/API.md) =====
 docs/API.md | 59 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 59 insertions(+)

===== verify grep =====
TASKS.md OE references:
179:## 附录 K — Onyx Enterprise Integration 后置交付登记（OEI-003 / OEI-004，2026-09-24）
184:### K.1 Onyx / ECE 连接器（OEI-003）
188:| `ContentEnginePort` Protocol | `src/ece/connectors/onyx/port.py` | 已交付 | 3 个方法：`search` / `engine_status` / `list_projects` |
190:| `MockContentEngineAdapter`（离线确定性） | `mock_adapter.py` | 已交付 | `ECE_CONTENT_ENGINE=mock` 时使用（默认） |
191:| `OnyxContentEngineAdapter`（真实 HTTP） | `onyx_adapter.py` | 已交付 | 调用 Onyx `/api/admin/llm/provider` / `/api/user/projects` / `/api/user/projects/files/{id}` / `/api/search` / `/api/version` |
193:| `GET /engine/status` 状态页（含引用渲染） | `src/ece/api/engine_status.py` + `main.py` | 已交付 | `?q=` 触发 search + ECE 自己渲染引用卡片（绕开 Onyx UI 不渲染引用的 bug） |
195:### K.2 验收证据（OEI-003 VERDICT.md §7.3 二轮）
198:- A8 无回归：`634 passed / 28 failed / 5 errors` baseline vs after 一致（28+5 是 ECE 仓 pre-existing，非 OEI-003 引入）
203:- [ ] `docs/API.md` 新增 `/engine/status` 章节 — **OEI-004 step 4 完成**
204:- [ ] `tests/unit/test_content_engine_port.py`（DB 无关的 adapter 单测）— 留给后续刀，避免 OEI-003 pytest 环境坑

docs/API.md OE references:
431:## 6. Engine Status（OEI-003，Engine Core 内部状态页）
433:> ⚠️ 本端点**不在 `/api/v1/` 前缀下**——它是 Engine Core 内部状态页，由 `ContentEnginePort` 抽象支撑，**不**走 JWT / 权限层。用于演示与排障，**不进**外部 v1 契约。
435:### GET /engine/status
443:| `q` | string | 否 | 若提供，触发一次 `ContentEnginePort.search(q)` 并把召回文档渲染为引用卡片（`source_type` / `engine_doc_id` / snippet） |
473:curl -s 'http://127.0.0.1:8000/engine/status' | less
482:curl -s 'http://127.0.0.1:8000/engine/status?q=问题树怎么用' | less
