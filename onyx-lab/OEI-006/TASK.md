# OEI-006 任务书 — Consulting Library 接真实检索（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-24
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## 本刀为什么是它

前五刀把地基铺完了：引擎能存（OEI-001）、能检（OEI-002）、ECE 能用上引擎并自己渲染引用（OEI-003）、仓库与基线干净（OEI-004）、回归信号可信（OEI-005，基线 `1 failed / 680 passed`）。

**本刀是第一个"客户能看懂"的东西**：把 KC-001 的 Consulting Library 从"纯静态目录"变成"**静态目录 ∪ 引擎召回**"——用户搜一个词，页面上既有目录里的方法论/模板卡片，也有**从真实上传文档里检索出来的**卡片，且能点开看到**来源与片段**。这正是 `AGENTS.md` 里"Case First / 可追溯"那条要求的第一版落地。

---

## 0. 一句话目标

让 Consulting Library 页面同时展示两个来源——**静态种子目录**（36 个对象）与**引擎召回**（Nyox 已索引的真实文档）——每组卡片标注来源，引擎卡片点开能看到标题、片段与来源元数据；引擎不可用时页面降级但不崩。

**架构红线**：ECE 拥有身份/权限/来源/审计与领域对象；Onyx 只是可替换的内容与检索引擎。**领域层不得直接依赖 Onyx**（沿用 OEI-003 的 `ContentEnginePort`）。

## 1. 环境事实（codex 于 2026-09-24 18:0x-18:1x 实测，可直接信任）

### 1.1 KC-001 现状（本刀要改的东西）

- 后端：`src/ece/consulting/{router,service,models}.py`，路由前缀 **`/api/v1/consulting`**
  - `GET /library`（`LibraryResponse`，返回 `{items,total,limit,offset,facets}`，支持 `q` 关键词过滤）
  - `GET /facets`、`GET /objects/{object_id}`
- 种子：`src/ece/consulting/seed/consulting_objects.json` —— **36 个对象**，字段含 `id/type/title/summary/practice/engagement_phase/client_industry/problem_types/methods/deliverables/outcomes/source_origin/confidence/review_state`
- 前端：`demos/spa/{index.html,app.js,styles.css}`，视图 **view-d**，DOM 锚点：`#consulting-search`、`#consulting-filters`、`#consulting-total`、`#consulting-cards`、`#consulting-empty`、`#consulting-detail`（详情抽屉）
- 实测静态目录命中：`采购`→3、`诊断`→8、`风险`→6、`交付`→1；**`问题树`/`MECE`→0**（静态目录里没有这些方法论词）

### 1.2 引擎侧（本刀的数据来源）

- 直接用 OEI-003 的 `src/ece/connectors/onyx/`（`ContentEnginePort` + `OnyxContentEngineAdapter` + `MockContentEngineAdapter` + `selector.get_content_engine()`）
- 开关：`ECE_CONTENT_ENGINE=onyx|mock`（**默认 mock**）；onyx 模式需 `ECE_ONYX_COOKIE_FILE` 指向 `/home/fisher/.onyx-lab/.secrets/admin-cookies.txt`（600）
- 真实引擎实测：`问题树怎么用` → 命中 `methodology-framework.md`（`source_type=user_file`）；项目 `id=1` 下有 3 份已索引文档（`user_file.id`：`7bb48d46…` case / `1457df88…` methodology / `3b14b918…` play）

### 1.3 本地"看得见"的链路（codex 已实测跑通，**端口 8080 被 Onyx 占用，必须换端口**）

```bash
# 终端 A：ECE API
uv run uvicorn ece.main:app --host 127.0.0.1 --port 8765
# 终端 B：同源 SPA + /api 反代（脚本参数是 --upstream <base-url>）
uv run python scripts/cut_045_local_origin.py --port 8181 --upstream http://127.0.0.1:8765
# 浏览器
http://127.0.0.1:8181/#d
```

实测结果：`/healthz` 200、SPA 首页 200、经代理的 `/api/v1/consulting/facets` 200 ✅

### 1.4 回归基线（OEI-005 建立）

`make test-integration`（或对已有 PG 跑 `make seed-fixtures && make test`）期望 **`1 failed / 680 passed`**，那 1 条是 `test_cut_045_local_origin_smoke`（部署栈缺失，环境类，**不是本刀要修的**）。**任何多于 1 的失败都是真回归。**

## 2. 范围锁

- **做**：在 `/api/v1/consulting/library` 的响应里**新增引擎合并结果**；SPA 在 Library 视图里渲染"静态 vs 引擎"两组卡片；引擎卡片可见来源与片段；降级与空态；DB 无关的单元测试 + 契约/降级测试；补 `docs/API.md` 与 `TASKS.md`
- **不做**：不改 36 个种子对象的内容；不改三个既有领域（采购/知识/合规）的业务逻辑；不做上传管道（OEI-007）、不做权限壳层（OEI-008）、不做 LLM Chat 生成答案；不引入新依赖；不改 Onyx 任何东西
- **接口纪律**：**静态侧的既有行为与字段不得改变**（既有测试与消费者必须继续通过）。引擎结果走**新增字段**，不使用破坏性改动

## 3. 工作区

```
onyx-lab/OEI-006/
├── TASK.md      ← 本文件（只读）
├── evidence/    ← 逐项证据（按 01.. 序号命名）
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

**证据命名**：`00a-leaked-uvicorn-before.txt`、`00b-leaked-uvicorn-after.txt`、`00c-test-leak-fix.txt`、`01-library-baseline-raw.json`、`02-library-with-engine-onyx.json`、`03-search-alignment.json`、`04-degraded-engine.json`、`05-empty-state.json`、`06-contract-parity.json`、`07-spa-html-proof.md`、`08-test-baseline-raw.txt`、`09-test-after-raw.txt`、`10-docs-backfill.txt`、`11-git-commit.txt`、`12-compliance-check.txt`

## 4. 任务步骤

**步骤 0 — 环境与测试卫生（前置；codex 签发前发现了真实问题）**

codex 扫描发现：**`test_cut_045_local_origin_smoke` 每次运行都会泄漏一个 uvicorn 子进程**。现场证据：**10 个游离进程**，启动时间与四次 pytest 运行一一对应（15:16 / 15:19 / 15:24 / 15:28 / 16:30 / 16:38 / 17:08 / 17:14 / 17:19 / 17:27），参数为 `--log-level warning`（该测试的 spawn 风格），**无任何连接**，**RSS 合计 558 MB**。在 swap 吃紧的机器上这是实打实的浪费，且每跑一次就多一个。

1. **清掉现有游离进程**：先 `pgrep -af 'uvicorn ece.main:app'` 落盘 → `00a-leaked-uvicorn-before.txt`；再 `pkill -f 'uvicorn ece.main:app'`；然后再落盘 → `00b-leaked-uvicorn-after.txt`（应为空）。**只允许匹配这一条命令模式**；完成后核对 9 个 Onyx 容器与 ollama 未受影响。
2. **修掉泄漏（本刀唯二允许改 `tests/**` 的地方，且仅限此文件）**：在 `tests/integration/test_cut_045_local_origin_smoke.py` 里，确保 `subprocess.Popen` 拉起的 uvicorn / origin 代理子进程**在 try/finally 中被无条件 `kill()` + `wait()`**（当前失败路径下没有被回收）。
3. **把"环境不满足"变成显式 skip**：该测试需要完整部署栈（nginx + `web/dist` 静态产物）；本地没有时应 `pytest.skip(reason=...)`，**而不是先等 10 秒超时再 FAIL**。

- [ ] **A0.1** 游离进程清零（`00b-*` 为 0），Onyx 9 容器与 ollama 状态未变
- [ ] **A0.2** 连续跑两次完整套件后 `pgrep -af 'uvicorn ece.main:app'` **仍为 0**（证明泄漏已修）
- [ ] **A0.3** 该测试由 `FAILED` 变为 `SKIPPED`（本地无部署栈时）且原因文案明确；**不得删除该测试、不得把断言改成"永远通过"**

**步骤 1 — 记录静态侧基线（改前）**

`GET /api/v1/consulting/library?q=采购` 的**原始响应**落盘（`01-*`）。这是"静态行为不许变"的对照起点。

**步骤 2 — 后端：合并引擎结果（新增字段，不改既有字段）**

建议契约（**你可以按实现调整，但必须写清并落盘**）：

```jsonc
{
  "items": [ ... ],              // 静态目录，行为不变
  "total": 3, "limit": ..., "offset": ..., "facets": {...},   // 不变
  "engine_items": [              // 新增
    { "engine_doc_id": "1", "title": "methodology-framework.md",
      "snippet": "...", "source_type": "user_file", "updated_at": "...",
      "source": "engine" }
  ],
  "engine_status": "ok"          // 新增：ok | unavailable | disabled
}
```

- `engine_items` 由 `get_content_engine().search(q)` 映射而来；映射函数要能**独立单元测试**（不依赖 DB、不依赖网络）
- `engine_status` 必须能区分 **引擎不可达**（`unavailable`）与 **`ECE_CONTENT_ENGINE=mock`**（`disabled` 或明确标注 mock，二者语义你定但要写清）
- **`q` 为空时**：静态侧行为不变；引擎侧不要自动发起检索（避免每次打开页面都打引擎），`engine_status` 给 `skipped` 或同等语义

**步骤 3 — 前端：Library 视图渲染两组卡片**

- 保留既有静态卡片渲染逻辑**不变**
- 新增"引擎召回（来自已索引文档）"分组：每张卡显示 `title` + `snippet`（截断）+ 来源标签（`user_file` / 更新时间）
- 点开走**既有详情抽屉**（`#consulting-detail`）或等价面板，展示完整片段与来源元数据
- **三种状态都要有可见反馈**：`engine_status=ok`（显示分组）、`unavailable`（显示"引擎暂时不可用，以下仅为静态目录"提示）、无命中（空态文案区分"目录无命中"与"引擎无命中"）

**步骤 4 — 取证（**这一步是本刀的核心，别偷懒**）**

1. **onyx 模式**下取 `GET /api/v1/consulting/library?q=问题树怎么用` 的**完整原始响应** → `02-*`
   - ⚠️ **必须是 `ECE_CONTENT_ENGINE=onyx`**（OEI-003 的教训：用 mock 取证等于没证）。响应里 `engine_items` 的标题/片段要能在 `OEI-001/workspace/` 找到对应原文
2. 把 `engine_items` 与 `POST /api/search`（同一 query）的原始返回做**逐条对照表** → `03-*`（标题 + doc_id + 片段前 80 字）
3. **降级证据**：把上游指到不可达地址（如 `ECE_ONYX_BASE=http://127.0.0.1:9`）→ 再取一次 `library` 响应 → `04-*`（要求：HTTP 200、静态 `items` 不变、`engine_status=unavailable`、**不裸崩**）
4. **空态证据**：一个静态与引擎都无命中的 query（可用随机串）→ `05-*`

**步骤 5 — 测试**

1. **DB 无关单元测试**（这是 OEI-003 VERDICT §6 强建议的落地）：映射与合并逻辑、`engine_status` 三种取值、异常路径（引擎抛 `EngineError` 时静态结果不受影响）
2. **契约测试**：mock 与 onyx 两种模式下 `engine_items` 的字段名/类型同构（同一 Pydantic 模型校验通过）
3. **接口不破坏**：既有 consulting 相关测试全部仍通过（静态字段未变）
4. **无回归**：跑 `make test-integration` → `08/09-*` 落盘原始输出，与基线 `1 failed / 680 passed` 对比

**步骤 6 — SPA 可见性自查（`07-spa-html-proof.md`）**

按 §1.3 起两条命令，然后：

- `curl -s http://127.0.0.1:8181/#d` 或直接取 `demos/spa/index.html`，证明**引擎分组所需 DOM 锚点已存在**（列出新增的 id/class）
- 跑一次经代理的 API 调用并贴原始输出
- 写一份**给用户的 60 秒自查清单**（起服务 → 打开哪个 URL → 点哪个视图 → 搜什么词 → 应看到什么）
- **截图由用户协助**（cc 无浏览器工具）：把"请截什么"写清楚放进 `07-*`。**截图属用户协助项，不计入你的验收失败，但不许用 API 响应冒充截图**

**步骤 7 — 文档与提交**

- `docs/API.md`：补 `engine_items` / `engine_status` 的字段说明与示例（`10-*` 贴 diff）
- `ece/TASKS.md`：补 OEI-006 条目
- `git add` + `git commit`（**不 push**）→ `11-*`

**步骤 8 — 清理与合规** → `12-*`（value-level 模式扫描）

## 5. 验收标准（codex 将逐条核对）

- [ ] **A0** 步骤 0 三项完成（见 §4 步骤 0 的 A0.1/A0.2/A0.3）：游离进程清零、连续两轮套件后仍为 0、该测试改为显式 skip
- [ ] **A1** 静态侧零变化：`01-*`（改前）与改后同一 query 的静态字段（`items/total/facets`）**逐字段一致**；既有 consulting 测试全部仍通过
- [ ] **A2** 新契约清晰：`engine_items` 与 `engine_status` 的字段/语义在 `docs/API.md` 有文档，且响应实测与之相符
- [ ] **A3** **onyx 模式**取证：`02-*` 由 `ECE_CONTENT_ENGINE=onyx` 产生，`engine_items` 非空且标题/片段与 `OEI-001/workspace/` 原文可对应
- [ ] **A4** 逐条对齐：`03-*` 给出 `engine_items` ↔ `/api/search` 原始返回的对照表（标题 + doc_id + 片段）
- [ ] **A5** 降级：`04-*` 证明引擎不可达时 **HTTP 200 + 静态结果不变 + `engine_status=unavailable` + 无未捕获异常**
- [ ] **A6** 空态：`05-*` 证明无命中时的响应与页面文案（区分两个来源）
- [ ] **A7** **DB 无关单元测试**存在且通过（映射/合并/`engine_status` 三分支/异常路径），落盘运行输出
- [ ] **A8** 契约同构：mock 与 onyx 的 `engine_items` 通过同一模型校验（`06-*`）
- [ ] **A9** 无回归：`09-*` 的 failed 数 **≤ 1**（即不劣于基线），且逐条说明与基线的差异
- [ ] **A10** SPA 可见性自查：`07-*` 含新增 DOM 锚点清单 + 经代理的 API 原始输出 + 给用户的 60 秒自查清单
- [ ] **A11** 合规：无凭据值落盘（cookie 只从 env 路径读）；未碰 Onyx / compose / `.env` / swap / `.wslconfig`；未 push；未改 36 个种子对象与三域业务逻辑
- [ ] **A12** `REPORT.md` 对 A1..A11 每条有结论 + 证据指针，无模糊表述

## 6. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏
2. `echo "$(date -Iseconds) OEI-006 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并签发下一刀；FAIL → 按 R{n} 返工

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：可改 `src/ece/consulting/**`（新增引擎合并路径）、`demos/spa/**`（Library 视图新增分组）、`src/ece/api/**`（如需新端点）、`ece/docs/API.md`、`ece/TASKS.md`；可起本地 uvicorn + `cut_045_local_origin.py` 用于自查；可只读调用 Onyx `/api/*`；可 `git commit`（**不 push**）
- ❌ **不改静态 36 个种子对象的内容**；**不改既有静态字段的语义**（只允许新增）
- ❌ 不改采购/知识/合规三域业务逻辑与其测试；**`tests/**` 只允许改 `test_cut_045_local_origin_smoke.py` 一个文件**（且只改子进程回收与 skip 前置），其余测试的断言语义一律不动
- ❌ 不引入新依赖；不做上传/权限/LLM Chat
- ❌ 不 restart/stop/down/rm 任何 Onyx 容器；不改 Onyx 上游/compose/`.env`；不碰 swap/`.wslconfig`
- ❌ 不把 cookie/token 写进任何产出物；不 push

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-006/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-006/DONE`
- 无新文件则静默，不重复执行、不打扰用户
