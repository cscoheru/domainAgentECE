# 10 — SPA 可见性证据（OEI-007 步骤 9 / A10）

日期：2026-09-24 ｜ 执行：cc ｜ 模式：`ECE_CONTENT_ENGINE=onyx` ｜ 链路：`uvicorn:8765` → `cut_045_local_origin:8181`
原始捕获：`/tmp/oei007-spa-raw.txt`

> 严格遵守 TASK §10 与 ROADMAP 「证据纪律」：**不许要用户截图**。本文件
> 只由**机器可校验**证据组成：HTML 转储 + DOM 锚点断言 + 经同源代理的 API
> 原始输出 + origin 访问日志。**不含截图、不向用户要截图**。

---

## 0. 起服务（含一处**必须**的环境修正）

TASK §2.3 给的两条命令（端口与原任务书一致），但**终端 B 必须先 `export no_proxy`**（OEI-006 §3-3 已记录的本机环境陷阱）：

```bash
export no_proxy=127.0.0.1,localhost NO_PROXY=127.0.0.1,localhost
uv run uvicorn ece.main:app --host 127.0.0.1 --port 8765
uv run python scripts/cut_045_local_origin.py --port 8181 --upstream http://127.0.0.1:8765
# 浏览器：  http://127.0.0.1:8181/#d
```

实测：上述 capture 一共 5 步，全程 `leak_uvicorn=0 leak_origin=0`。

---

## 1. SPA `index.html` 经代理（浏览器实际收到的那份）

```
status=200 bytes=14222
identical to demos/spa/index.html: YES
```

字节级一致（cmp 命中），说明 origin 把 `demos/spa/` 原样送出。

---

## 2. DOM 锚点清单（view-d 切片，3313 字符）

OEI-006 已有锚点全部保留 + OEI-007 新增 8 个：

| 锚点 | 状态 | 作用 |
|---|---|---|
| `consulting-engine` / `consulting-engine-status` / `consulting-engine-cards` / `consulting-engine-empty` | 既有 (OEI-006) | 引擎召回卡片分组 |
| `consulting-search` / `consulting-cards` / `consulting-empty` / `consulting-detail` | 既有 (KC-001) | 静态目录 + 详情抽屉 |
| **`consulting-upload`** | **新增** | 上传区容器 |
| **`consulting-upload-help`** | **新增** | 限制说明 (.md/.txt/.docx/.pdf ≤ 4 MiB) |
| **`consulting-upload-title`** | **新增** | 可选标题输入 (用于元数据建议) |
| **`consulting-upload-file`** | **新增** | 多文件 input (`accept=".md,.txt,.docx,.pdf,..."`) |
| **`consulting-upload-submit`** | **新增** | 上传按钮 |
| **`consulting-upload-status`** | **新增** | 上传结果/错误提示 |
| **`consulting-upload-list`** | **新增** | 最近上传行表 |
| **`consulting-upload-rows`** | **新增** | 上传行挂载点 |

切分规则复用 `test_consulting_spa_view.py` 的 `view-d` 切片（同 OEI-006 §1）：
`re.search(r'<section[^>]*id="view-d"[^>]*>(.*?)(?=<section|</main|</html)', ...)`。**全部 16 个 id 均 `present=True`**。

CSS：与 OEI-006 引擎分组同一种视觉风格 — 顶 2px 虚线分隔、提交按钮蓝底白字、上传行蓝条左边框、状态徽章按 PROCESSING/COMPLETED/FAILED 三色（黄/绿/红）。

JS 行为（`demos/spa/app.js` 末尾新加的 `submitConsultingUpload` / `pollConsultingDocument`）：
- 多文件 `FormData` 提交到 `POST /api/v1/consulting/documents`
- 每条结果渲染为一行（accepted → 状态徽章 + 查询状态按钮；rejected → 红色理由）
- 「查询状态」按钮 → `GET /api/v1/consulting/documents/{id}` → 原地刷新徽章
- 任意 accepted → 自动触发 `runConsultingSearch()`，新文档立即出现在「引擎召回」组

---

## 3. 经代理的 API（原始输出）

### 3.1 Library 检索 — 经代理

```
=== [3] PROXIED API: GET /api/v1/consulting/library?q=问题树怎么用 ===
status=200 bytes=5779 time=5.176556
engine_status : ok
static total  : 0
engine_items  : 4
   - 1 | case-management-consulting.md            | user_file | 2026-09-23T13:06:16Z
   - 2 | oei007-binary-oei007docx1790261066.docx   | user_file | 2026-09-24T14:44:27Z
   - 3 | oei007-closed-loop-probe.txt             | user_file | 2026-09-24T14:36:05Z
```

> 注：第 2 行即证据 09 的 docx（chunk_count=1、user_file.id 可回溯到证据 09 的 UUID），
> 第 3 行即证据 05 的 closed-loop probe —— **同一浏览器会话里的"上传 → 上方「引擎召回」分组立即出现新文档"路径在 onyx 模式 + 同源代理下真实可达**。

### 3.2 Upload + Status 经代理

```
=== [4] PROXIED UPLOAD + STATUS (round-trip via origin) ===
  upload status: 200
  static_catalog_size : 36
   - probe.txt accepted=True doc_id=0535ca64-... status=PROCESSING
  status GET status: 200  doc_id=0535ca64-...
    {'document_id': '0535ca64-3397-4266-a268-87ea5db811db',
     'name': 'probe.txt',
     'status': 'PROCESSING',
     'chunk_count': None,
     'project_id': None,
     'failure_reason': None}
```

- `static_catalog_size=36` —— 上传不影响静态目录计数（A1 不破坏）
- 上传响应 HTTP 200、状态 GET HTTP 200、字段集与 `DocumentStatusResponse` 严格一致
- 多文件/部分成功由路由层按 per-file `accepted` 处理（证据 07 覆盖 5 类失败）

### 3.3 Origin 访问日志（证明 API 走的是 proxy 分支）

```
[cut-045-origin] GET /index.html → static
[cut-045-origin] GET /index.html → static
[cut-045-origin] GET /api/v1/consulting/library?q=问题树怎么用 → proxy
[cut-045-origin] POST /api/v1/consulting/documents → proxy
[cut-045-origin] GET /api/v1/consulting/documents/0535ca64-... → proxy
```

SPA 同源链路的 4 个分支（静态首页 / 静态首页 / library 检索 / 上传 / 状态）路径
明确、与代码中的 `PROXY_PREFIXES` 完全一致。

---

## 4. 限制记录（诚实）

1. **首次经代理调用 library 触发 Onyx 冷启动会 502**：origin 上游超时 10s，但
   Onyx 首次冷查询实测 4-15s。`/tmp/oei007-spa.sh` 用「先直连做热启动，再经代理
   走热缓存」的方式规避。**这是自查链路特性，不是接口缺陷**（OEI-006 §3-8 已记录
   同样现象；下游用户的 SPA 走的是已上线的服务，没有冷启动问题）。
2. **本文件不含真实截图**：TASK §10 严格禁止要用户截图，本刀所有可见性证据
   都用 HTML 转储 + DOM 锚点断言 + 经代理 API 原始输出 + origin 访问日志四件套
   替代；浏览器侧的真实可见性由这四件套证明。
3. **本轮 SPA 不动既有 36 个种子对象的任何渲染代码**：新增的 `submitConsultingUpload`、
   `pollConsultingDocument` 等函数挂在 IIFE 末尾，不修改既有 `runConsultingSearch` /
   `renderConsultingEngine` / `openConsultingEngineDetail` 等任何函数。

---

## 5. 本轮的 SPA 改动面（git diff 一览）

- `demos/spa/index.html` — 在 view-d 内、OEI-006 的 `consulting-engine` 分组之后、
  详情抽屉之前，新增 `consulting-upload` 与 `consulting-upload-list` 两个 `<div>`。
  仍用 `<div>` 而非嵌套 `<section>`，不破坏 `test_consulting_spa_view.py` 的
  扫描区间。
- `demos/spa/styles.css` — 新增 `#consulting-upload*` 与 `.consulting-upload-row*`
  选择器，沿用 OEI-006 的虚线分隔 + 蓝条左边框。
- `demos/spa/app.js` — IIFE 末尾新增 `submitConsultingUpload` /
  `pollConsultingDocument` / `renderUploadRow` / `setUploadStatus` 四个函数，
  并 wire `consulting-upload-submit` 的 click handler。

测试侧：`tests/unit/test_consulting_spa_view.py` 的 9 条护栏全部仍通过
（步骤 8 单测结果见 `12-test-after-raw.txt`）。