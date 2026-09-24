# OEI-003 任务书 — ECE 侧 Content Engine Port 与引擎状态页（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1.1（返工授权更新）** ｜ 签发日期：2026-09-24 ｜ v1 正文未改动，仅 §7 增加一条返工授权
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动
>
> **v1 → v1.1 变更（2026-09-24 14:0x）**：首轮审验判 FAIL（`VERDICT.md`），返工项 R1–R6 已签发。针对 R5（A8 无回归），用户选定 **(a) 补做**——为该测试**显式授权起/删一个 ECE 专用临时 Postgres 容器**（详见 §7 新增条）。其余验收标准与范围不变。

## 本刀怎么来的

1. **前置已关闭**：`OEI-002` 判定 **PASS**（见 `OEI-002/VERDICT.md` §8）——本地 LLM 部署成功，`/api/search` 由 0/8 转为 **8/8 = 200**，由 codex 独立复现。
2. **本刀是 OEI 主线上第一刀 ECE 侧开发**：把"Onyx 是可替换的内容与检索引擎"这句话从口号变成代码——ECE 定义自己的接口，Onyx 只做一个可替换的实现。
3. **从 OEI-002 强制转出的一项**：Onyx CE 自带 UI **不渲染引用、答案未 grounding**（证据：`OEI-002/evidence/12-ui-screenshot-main.png` 的"蛋糕"例子、`16-chat-with-citations.json` 对照）。**ECE 必须自己渲染引用**，这条是本刀的硬验收项，不是可选项。

---

## 0. 一句话目标

在 ECE 侧建立 `ContentEnginePort`（自有接口）+ Onyx adapter（可替换实现，含 mock），并交付一个**能打开的引擎状态页**：页面上能看到引擎真实状态（版本 / tier / provider / default model / 项目数 / 检索耗时），**并且能看到"查询 → 召回文档 → 引用片段"**——引用由 ECE 自己渲染，不依赖 Onyx UI。

**架构红线（不可偏离）**：ECE 拥有身份 / 权限 / 来源 / 审计 / 领域对象 / 工作流；Onyx 只是可替换的内容与检索引擎。**ECE 的领域层不得直接 import Onyx 相关内容**。

## 1. 环境事实（codex 实测，可直接信任）

### 1.1 Onyx 侧（只读使用，本刀不得改动）

- 入口 `http://127.0.0.1:8080`，9 容器在跑，`/api/health` = 200
- 凭据：`/home/fisher/.onyx-lab/.secrets/admin-cookies.txt`（`chmod 600`）。**cookie 不得进入 ECE 仓、不得写进任何产出物**，只能运行时通过 `ECE_ONYX_COOKIE_FILE` 环境变量读取
- 已验证的只读端点：

  | 用途 | 方法 | 路径 | 返回要点 |
  |---|---|---|---|
  | 版本 | GET | `/api/version` | 版本对象 |
  | 档位 | GET | `/api/settings` | `tier=community`、`gpu_enabled=true` |
  | LLM 状态 | GET | `/api/admin/llm/provider` | `providers[]`、`default_text={provider_id,model_name}` |
  | **检索** | POST | `/api/search` | body `{"query":"..."}` → `{"results":[{citation_id,title,content,link,source_type,updated_at}]}` |
  | 项目列表 | GET | `/api/user/projects` | 数组；当前 1 个：`id=1` `OEI-001 Consulting Lab` |
  | 项目文件 | GET | `/api/user/projects/files/1` | 3 份文档（`play-sales-delivery.md` / `methodology-framework.md` / `case-management-consulting.md`） |
  | 索引状态 | POST | `/api/user/projects/file/statuses` | body `{"file_ids":[<user_file.id>]}`，**必须传 user_file.id**（传底层 file_id 返回 `[]`） |

- 路由自证（`/openapi.json`、`/docs` 均为 404）：

```bash
docker exec onyx-api_server-1 python -c \
  "from onyx.main import app; s=app().openapi(); [print(p) for p in sorted(s['paths'])]"
```

- ⚠️ **一致性注意**：`/api/search` 是确定性召回（同 query 多次结果一致），**不返回生成答案**。Chat 路径（`/api/chat/send-chat-message` + `project_id` + `forced_tool_id`）能召回的可行性已由 `OEI-002/evidence/16-chat-with-citations.json` 证明，但那条路有会话状态，**留到后续刀**，本刀只接 `/api/search`。
- ⚠️ 单次检索**热态约 10–18s**（现场实测 12.5s），超时要设够（建议 ≥60s）。

### 1.2 ECE 仓侧（本刀**显式授权修改**）

- 路径 `/mnt/d/Projects/domainAgentECE/ece/`；Python 3.12 + `uv`；治理文件 **`ece/CLAUDE.md`（必须先读，冲突时以它为准）**
- 结构：`src/ece/{api,context,connectors,audit,auth,identity,permissions,evidence,entities,consulting,llm,mcp,...}`；没有任何现成的"内容引擎适配"抽象（本刀新建）
- 测试：`uv run pytest -m "not eval and not eval_llm"`（Makefile `test` 目标）；历史上该命令通过约 512 条用例，**本刀不得引入回归**
- 其他可用目标：`make setup` / `make up` / `make seed` / `make demo`

## 2. 范围锁

- **做**：ECE 侧 Port 定义 + Onyx adapter + mock adapter + 引擎状态页（含引用渲染）+ 确定性/契约/降级测试 + 文档
- **不做**：不改 Onyx 上游源码 / compose / `.env`；不重启任何容器；不接 Chat 路径；不做上传管道（那是 OEI-005）；不做权限壳层（OEI-006）；不碰 `onyx-lab/bin/`；不 commit / push
- **产出物只对本刀负责**：ECE 代码改动是本刀交付物，但**是否 commit 由用户/架构师决定**，cc 不自行提交

## 3. 工作区

```
onyx-lab/OEI-003/
├── TASK.md      ← 本文件（只读）
├── evidence/    ← 逐项证据（按 01.. 序号命名）
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

**证据命名**：`00-oei002-carryover.md`、`01-port-structure.txt`、`02-adapter-onyx.json`、`03-adapter-mock.json`、`04-contract-parity.json`、`05-determinism-n10.json`、`06-engine-status.html`、`07-engine-status.png`、`08-degraded-mode.json`、`09-test-before.txt`、`10-test-after.txt`、`11-compliance-check.txt`、`12-container-snapshots.txt`

## 4. 任务步骤

**步骤 0 — 收尾项（来自 OEI-002）**

更正 `OEI-002/evidence/12-ui-proof.md` §1.2 的事实描述：`12-ui-proof-search.png` 实际是**项目页（Files 区三张文件卡 + 空输入框）**，不是"输入框下方的引用卡片区域"；并补一句如实记录：**Onyx UI 的对话答案是泛化的、未引用上传文档**（依据 `12-ui-screenshot-main.png` 的"蛋糕"例子）。结论写入 `evidence/00-oei002-carryover.md`。

**步骤 1 — 读 `ece/CLAUDE.md` 与 `ece/README.md`**，确认既有分层与命名习惯后再动手；把"读到什么约束"记录进 REPORT。

**步骤 2 — 定义 Port（ECE 自有接口）**

- 在 ECE 侧新增 `ContentEnginePort`（`typing.Protocol` 或 ABC），至少三个方法：
  - `search(query: str, *, top_k: int | None = None) -> list[EngineDocument]`
  - `engine_status() -> EngineStatus`（版本 / tier / provider / default model / 项目数）
  - `list_projects() -> list[EngineProject]`
- 统一返回模型（Pydantic）：`EngineDocument{engine_doc_id, title, snippet, source_type, updated_at, raw}`、`EngineStatus{...}`、`EngineProject{...}`
- **分层纪律**：`EngineDocument` 等模型与 Port 定义**不得** import 任何 Onyx 专有模块；Onyx 专有字段只能活在 adapter 内部（用 `raw` 承载）

**步骤 3 — 两个实现 + 可切换**

- `OnyxContentEngineAdapter`：真实调用 §1.1 的端点（cookie 从 `ECE_ONYX_COOKIE_FILE` 读，默认路径见 §1.1；base URL 可用 `ECE_ONYX_BASE` 覆盖，默认 `http://127.0.0.1:8080`）
- `MockContentEngineAdapter`：离线可跑的固定实现
- 选择器：`ECE_CONTENT_ENGINE=onyx|mock`（默认 `mock`，避免无引擎时 CI 挂掉）

**步骤 4 — 引擎状态页（可见产出，本刀的重头）**

- 新增 `GET /engine/status`（HTML 页；若 ECE 已有 SPA，则在其上挂一个可见条目，并在 REPORT 说明位置）
- 页面必须显示：引擎名与版本、tier、GPU 开关、provider 与 default model、项目数与文件数、**最近一次检索的耗时**
- 页面必须显示**引用**：`/engine/status?q=问题树怎么用` 触发一次检索，渲染"查询 → 召回文档标题 → 片段（截断）→ 来源类型"。这是对 OEI-002 转出的强制项的直接回应
- 保存 HTML 转储 `06-engine-status.html` 与截图 `07-engine-status.png`（截图由用户协助，若无法截图则 HTML 转储 + 说明必须齐全，并在 REPORT 注明）

**步骤 5 — 测试**

1. **确定性**：同一 query 调 adapter 10 次（`ECE_CONTENT_ENGINE=onyx`），把 10 次返回的 `engine_doc_id` 规范化集合落盘到 `05-determinism-n10.json`，结论写"逐次一致/不一致 + 差异"
2. **契约一致性**：mock 与 onyx 两个 adapter 的同一方法输出都能通过同一 Pydantic 模型校验，且**关键字段名与语义一致**（`04-contract-parity.json`）
3. **降级路径**：把 base 指向一个不可达地址（例如 `ECE_ONYX_BASE=http://127.0.0.1:9`）→ Port 必须返回明确错误、状态页显示"引擎不可用"的降级提示，**不得 500 裸崩、不得抛未捕获异常**（`08-degraded-mode.json`）
4. **无回归**：改动前后各跑一次 `uv run pytest -m "not eval and not eval_llm"`，把两次汇总数字落盘（`09-test-before.txt` / `10-test-after.txt`），后者的通过数不得少于前者

**步骤 6 — 合规与收口**

- `11-compliance-check.txt`：value-level 扫描（`connect.sid=` / `fastapiusersauth=` / `eyJ…` / `sk-…`），并确认 ECE 仓内**没有** cookie 文件、没有 `ECE_ONYX_COOKIE_FILE` 指向文件的副本
- `12-container-snapshots.txt`：`docker ps` 的 Up 时长（证明未重启容器）
- 写 `REPORT.md`

## 5. 验收标准（codex 将逐条核对）

- [ ] **A1** Port 与模型定义存在，且**领域层不依赖 Onyx**：给出文件路径 + 一条可复现的检查（例如对相关目录 `grep -rn "onyx"` 无命中，或一条断言 import 隔离的测试）
- [ ] **A2** 两个 adapter 均可实例化，`ECE_CONTENT_ENGINE` 可切换（各自一次真实调用证据：`02-adapter-onyx.json` / `03-adapter-mock.json`）
- [ ] **A3** 引擎状态页可打开且显示 §4 步骤 4 要求的**全部字段**（HTML 转储或截图 + 字段清单核对）
- [ ] **A4** 状态页**渲染引用**：查询 → 召回文档标题 → 片段，内容与 `/api/search` 原始返回可逐条对应（这是 OEI-002 转出的强制项）
- [ ] **A5** 确定性：10 次调用的文档标识集合给出"一致/不一致 + 差异"结论
- [ ] **A6** 契约一致性：mock 与 onyx 输出同构（同一模型校验通过）+ 字段名/语义对照表
- [ ] **A7** 降级：引擎不可达时状态页给出明确降级提示，无未捕获异常（原始日志/响应为证）
- [ ] **A8** 无回归：`uv run pytest -m "not eval and not eval_llm"` 通过数 ≥ 改动前（两次输出落盘）
- [ ] **A9** 合规：无凭据原值泄漏、ECE 仓内无 cookie 副本、容器未重启、未改 Onyx 上游/compose/`.env`、未 commit / push
- [ ] **A10** `REPORT.md` 对 A1..A9 每条都有结论 + 证据指针，无模糊表述；含步骤 0 的收尾结论
- [ ] **A11** 状态页在**默认 mock 模式**下也能打开（换机器/无 Onyx 时演示不塌）——若做不到，必须在 REPORT 说明原因并给替代方案

## 6. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏
2. `echo "$(date -Iseconds) OEI-003 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭本刀并签发下一刀；FAIL → 按 R{n} 返工

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：可读写 `ece/` 仓（本刀范围就是 ECE 侧）；可只读调用 Onyx 的 `/api/*`
- ✅ **返工授权（v1.1 新增，仅限 R5）**：允许 `docker run` 起一个 **ECE 专用临时 Postgres 容器**（建议名 `ece-pg-tmp`，镜像 `postgres:16-pgvector`，端口 `55432:5432`，用容器自管存储而**非** bind mount），跑完 **必须 `docker rm -f ece-pg-tmp` 清理**；测试通过 `DATABASE_URL` 环境变量指向它（`src/ece/db.py:16-21` 支持覆盖）。此授权**不包含**：改动 ECE 的 `docker-compose.yml`、触碰 Onyx 的任何容器或配置
- ❌ 不改 Onyx 上游源码 / compose / `.env`；不 restart / stop / down / rm 任何容器
- ❌ 不接 Onyx Chat 路径（有状态）；不写任何 ECE 之外的业务代码
- ❌ 不把 cookie / token 写进 ECE 仓或任何产出物；不在命令行参数里传密钥；不改 `.wslconfig`
- ❌ 不 commit / push；不改 `onyx-lab/bin/`、不改历史 `TASK.v*.md` / `VERDICT.md`
- ❌ 不做范围外功能；额外发现写进 REPORT 的"建议"段

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-003/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-003/DONE`
- 无新文件则静默，不重复执行、不打扰用户
