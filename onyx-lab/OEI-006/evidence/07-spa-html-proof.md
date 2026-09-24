# 07 — SPA 可见性自查（OEI-006 步骤 6 / A10）

日期：2026-09-24 · 执行：cc · 模式：`ECE_CONTENT_ENGINE=onyx`
原始输出：`/tmp/oei006-07-raw.txt`（本文所有引用均逐字来自该文件）

---

## 0. 起服务（含一处**必须**的环境修正）

TASK §1.3 给的两条命令（端口与原任务书一致）：

```bash
# 终端 A：ECE API
uv run uvicorn ece.main:app --host 127.0.0.1 --port 8765
# 终端 B：同源 SPA + /api 反代
uv run python scripts/cut_045_local_origin.py --port 8181 --upstream http://127.0.0.1:8765
# 浏览器
http://127.0.0.1:8181/#d
```

### ⚠️ 终端 B 必须额外设置 `no_proxy`（否则**必然** 502，与本刀代码无关）

本机 shell 导出了 `http_proxy=http://127.0.0.1:7890`，且 `no_proxy` 里写的是 **`127.*`**。实测：

```
proxy_bypass('127.0.0.1:8765') = False
proxy_bypass('127.0.0.1')      = False
proxy_bypass('localhost:8765') = True
```

`scripts/cut_045_local_origin.py` 用 **`urllib.request.urlopen`（第 143 行）**转发上游，而 Python 的 `proxy_bypass` **不认 `127.*` 这种通配**（只认精确名、`*`、`.domain` 后缀）。后果：反代把上游这一跳发给了 7890 代理，代理回一个**无 body 的 502**，反代原样转出。curl 认通配所以直连正常 —— 这正是"直连 200 / 经代理 502"的原因。

修正（只影响终端 B 的子进程，不改任何仓库文件）：

```bash
export no_proxy=127.0.0.1,localhost NO_PROXY=127.0.0.1,localhost
```

实测：修正前经代理 `status=502 bytes=0`；修正后 `status=200 bytes=3578 time=4.22s`，与直连**字节数完全一致**。

---

## 1. 引擎分组所需 DOM 锚点（浏览器实际收到的那份 HTML）

取自**经代理取回**的 `index.html`（`status=200 bytes=12842`，`sha256=6f0a70bcfdde45a6…`，
与 `demos/spa/index.html` **逐字节相同：YES**），按 `test_consulting_spa_view.py` 的同款
view-d 切分规则取 `view-d` 切片（`slice_chars: 2219`）：

| 锚点 | 状态 | 说明 |
|---|---|---|
| `consulting-engine` | **新增** | 引擎分组容器（`<div>`，非嵌套分节） |
| `consulting-engine-status` | **新增** | 分组级状态提示（`ok/unavailable/disabled/skipped` 文案） |
| `consulting-engine-cards` | **新增** | 引擎卡片挂载点 |
| `consulting-engine-empty` | **新增** | 引擎侧空态提示 |
| `consulting-search` / `consulting-filters` / `consulting-total` / `consulting-cards` / `consulting-empty` | 既有 | 全部 present=True（静态侧未动） |
| `consulting-detail` | 既有 | **仍在切片内**（详情抽屉复用，未被挤出扫描区） |

关键回归点：`group is a <div>, not a nested section: True`。
（嵌套分节标签会让 `test_consulting_spa_view` 的 `(?=<section|</main|</html)` 前瞻把
详情抽屉切出扫描区，因此这里刻意用 `<div>`。）

新增 CSS 选择器（`demos/spa/styles.css`）：`#consulting-engine`(413)、`#consulting-engine h3`(419)、
`#consulting-engine-status`(425)、`#consulting-engine-cards`(430)、`.consulting-card-engine`(436)、
`.consulting-card-engine .consulting-snippet`(441)、`#consulting-engine-empty`(452)。

前端符号（`demos/spa/app.js`，提交给浏览器的同一文件）：`renderConsultingEngine` /
`openConsultingEngineDetail` / `CONSULTING_ENGINE_STATUS_COPY` 共 6 处出现；三条状态文案逐字：

```
unavailable": "内容引擎暂时不可用 — 以下仅为静态目录."
disabled":    "本环境未接入内容引擎 — 以下仅为静态目录."
skipped":     "输入关键词即可同时检索已索引文档."
```

---

## 2. 经代理的 API 调用（原始输出，逐字）

```
=== [3] PROXIED API CALL: GET /api/v1/consulting/library?q=问题树怎么用  (no_proxy hop fixed) ===
status=200 bytes=3578 time_total=4.225184
--- raw response body (first 400 bytes) ---
{"items":[],"total":0,"limit":24,"offset":0,"facets":{"types":["case","deliverable_template","industry_note","methodology","proposal_play","risk_check"],"practices":["change_management","consulting_delivery","governance","growth","industry_analysis","operations","organization_design","performance_management","pricing","process_redesign","procurement","risk_management","sales","sales_effectiveness"
--- end raw ---
engine_status : ok
static total  : 0
engine_items  : 1
   - 1 | methodology-framework.md | user_file | 2026-09-23T13:06:16Z | source= engine
```

反代访问日志证实该次请求确实走了 proxy 分支：

```
[cut-045-origin] GET /index.html → static
[cut-045-origin] GET / → static
[cut-045-origin] GET /api/v1/consulting/library?q=%E9%97%AE%E9%A2%98%E6%A0%91%E6%80%8E%E4%B9%88%E7%94%A8 → proxy
```

子进程回收：`leak_uvicorn=0`、`leak_origin=0`。

> 说明：该 query 静态目录 0 命中、引擎 1 条 —— 恰好是"两个来源可独立存在"的样例：
> 页面会显示引擎卡片组 + 目录侧"目录无命中"文案，两者互不覆盖。
> 静态命中样例见 `01-*`（36 条）与 `05-*`（空态）。

---

## 3. 给用户的 60 秒自查清单

1. **终端 A**（仓库根 `ece/`）：
   `ECE_CONTENT_ENGINE=onyx ECE_ONYX_COOKIE_FILE=<你的 cookie 文件> uv run uvicorn ece.main:app --host 127.0.0.1 --port 8765`
2. **终端 B**：先 `export no_proxy=127.0.0.1,localhost NO_PROXY=127.0.0.1,localhost`（**必须**，见 §0），再
   `uv run python scripts/cut_045_local_origin.py --port 8181 --upstream http://127.0.0.1:8765`
3. 浏览器打开 **`http://127.0.0.1:8181/#d`** → 应停在 **视图 D · 咨询知识库**。
   （直接开 `http://127.0.0.1:8181/` 是视图 A，点导航第 4 个按钮"视图 D · 咨询知识库"即可。）
4. **什么都不输入时**：页面**不应出现**"引擎召回"分组（空 query 走 `skipped`，不发检索）。
   底部应显示目录共 **36** 条。
5. 在"关键词搜索"里输入 **`KPI`**（或 `采购诊断`）→ 等约 **4–15 秒**（Onyx 实测 4.2s 稳态、首查约 15s）
   → 应同时看到：
   - 上方**目录卡片**（蓝色/实线卡片，"来源"标注为静态目录）；
   - 下方**新分组「引擎召回 (来自已索引文档)」**，卡片为**虚线边框 + 左侧蓝条**，
     每张卡带 `引擎召回` 徽章、文件类型徽章（如 `user_file`）与 `更新 2026-09-23…` 时间。
6. 点任意**引擎卡片** → 右侧**同一个详情抽屉**滑出（复用既有抽屉，不新开面板），
   标题与摘要取自引擎召回文档；点"关闭"可收起。
7. **降级自查**：把终端 A 停掉 → 再搜一次 → 页面**不应崩溃**：目录卡片照常显示，
   引擎分组只显示一行"内容引擎暂时不可用 — 以下仅为静态目录."，且无卡片。
   （与 API 侧 `04-*` 的 `engine_status=unavailable` 对应。）

---

## 4. 请你协助截图的清单（cc 无浏览器工具，截图属用户协助项）

> 明确：**我不拿 API 响应冒充截图**。以下三项需你实际打开浏览器截图：

- **S1**：`http://127.0.0.1:8181/#d` 搜 `KPI` 后的**整页**（要能同时看到上方目录卡片组
  与下方「引擎召回」分组标题 + 至少一张虚线蓝条引擎卡片）。
- **S2**：点击一张引擎卡片后**详情抽屉打开**的状态（要能看出用的是同一个右侧抽屉）。
- **S3**：把终端 A 停掉后同样搜索的**降级状态**（引擎分组只剩一行灰字提示，目录不受影响）。

---

## 5. 诚实记录的两条限制（不掩盖）

1. **经代理的上游超时是 10 秒**（`cut_045_local_origin.py:143`，`timeout=10`），而 ECE 适配器
   的超时是 60 秒（`onyx_adapter.py:36`）。Onyx 冷启动首个检索实测可达 **15.2s**（稳态 4.2s），
   此时**经代理**会得到 `502`（实测 `status=502 bytes=0 time=10.024084`，即恰好卡在 10s），
   而**直连** API 仍是 200 + 正常降级。这是自查链路的超时特性，**不是本刀代码缺陷**；
   自查时若首次搜索 502，重试一次即可（稳态 4.2s）。
2. 本文件**没有**真实截图，只有 §4 的截图请求与 §1–§2 的实测文本/JSON。

---

## 6. 本轮未纳入的一次尝试（一并记录）

我用一个矩阵脚本（一次起栈、连续 4 个 query）取"两个来源同时非空"的对比，
该次**失败**：`q="采购诊断"` 等全部返回 `http=000`，同时刻**直连**同一批 query 为
`15.2s / 14.8s / 42.8s`（Onyx 该时段明显变慢），即经代理的 10s 上游超时被打穿。
随后复测 Onyx 直连恢复为 `15.06s(冷) / 4.18s / 4.18s`，9 个容器 `Up 24 hours (healthy)`，
无重启。因此该失败归因于**冷启动时延**，非代码问题；正式证据改用首轮成功的单次经代理调用（§2）。
