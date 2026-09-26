# OEI-013 — 视图 D 三段演示叙事的机器可校验证据

- 演示起点（同源）: `http://127.0.0.1:8181`  — 浏览器打开 `http://127.0.0.1:8181/index.html`
- **无截图**：本文件全部结论可由下面的命令与原始输出复算。

## 1. 起点实际吐出的文件（不是仓库里的文件）

| 资源 | HTTP | 字节 | sha256 |
|---|---|---|---|
| `/index.html` | 200 | 17044 | `42e831babf8a032f…` |
| `/app.js` | 200 | 38200 | `f4b9a0da6f37624b…` |
| `/styles.css` | 200 | 13954 | `7627d2f6571d1987…` |
| `/healthz` | 200 | — | — |

## 2. 视图 D 切片（用 `test_consulting_spa_view` 的同一个正则切出来的）

```
regex: <section[^>]*id=["\']view-d["\'][^>]*>(.*?)(?=<section|</main|</html)
slice length: 4849 chars
nested <section> inside slice: 0   (必须为 0 — 测试以「下一个分节标签」为切片终点)
```

### 三幕

| 锚点 | 标题 | 切片内存在 |
|---|---|---|
| `#consulting-act-1` | ① 一个问题 | ✅ |
| `#consulting-act-2` | ② 知识库怎么答 | ✅ |
| `#consulting-act-3` | ③ 你的文件 | ✅ |

### 既有测试钉住的锚点（一个都不能少）

| 锚点 | 切片内存在 |
|---|---|
| `#consulting-search` | ✅ |
| `#filter-type` | ✅ |
| `#filter-practice` | ✅ |
| `#filter-phase` | ✅ |
| `#filter-industry` | ✅ |
| `#filter-problem` | ✅ |
| `#filter-source` | ✅ |
| `#consulting-reset` | ✅ |
| `#consulting-total` | ✅ |
| `#consulting-cards` | ✅ |
| `#consulting-empty` | ✅ |
| `#consulting-detail` | ✅ |

- `#consulting-search` 的 `type="search"`: ✅
- PRD §9 禁用技术词出现在切片里: 无 ✅
- **结论: PASS**

## 3. 幕一 — 一个问题

- 视图 D 首次打开时预填的问句（读自 `app.js` 的 `CONSULTING_DEMO_QUESTION`）:
  > 客户想做一次采购成本诊断, 该从哪下手
- 这句问句**不是**一个关键词 —— 这正是幕二要讲的东西。

## 4. 幕二 — 知识库怎么答

### 4a. 原样投喂这句问句（用户真实会做的事）

- `GET /api/v1/consulting/library?q=%E5%AE%A2%E6%88%B7%E6%83%B3%E5%81%9A%E4%B8%80%E6%AC%A1%E9%87%87%E8%B4%AD%E6%88%90%E6%9C%AC%E8%AF%8A%E6%96%AD%2C%20%E8%AF%A5%E4%BB%8E%E5%93%AA%E4%B8%8B%E6%89%8B` → HTTP 200
- **`total = 0`**  (目录命中 0 条)
- `engine_status = 'ok'`
- `engine_items = []`  (0 条)

### 4b. 确定性关键词改写（无模型；词表与规则都在 `app.js` 里）

- `node rewrite_probe.js` 读出**实际发版代码**的改写结果: `['采购成本', '诊断']`
- 确定性: PASS: 5/5 runs identical for every case

| 检索词 | HTTP | total | engine_status | engine_items（权限过滤后） |
|---|---|---|---|---|
| `采购成本` | 200 | 1 | `ok` | [] |
| `诊断` | 200 | 11 | `ok` | ['methodology-framework.md'] |

- 合并去重后目录命中: **11 条**（原样投喂是 0 条）
- 观众会看到的那行说明（按 `setConsultingRewriteNote` 的文案）:
  > 这句话不是一个关键词, 知识库没直接命中. 已按其中的业务词检索: 采购成本 / 诊断 — 合并去重后 11 条.

## 5. 幕三 — 你的文件

- 上传入口锚点: ✅  `#consulting-upload` / `#consulting-upload-file` / `#consulting-upload-submit`
- 召回组锚点: ✅  `#consulting-engine` / `#consulting-engine-cards` / `#consulting-engine-status`

- 以 `诊断` 为例的真实召回（匿名，权限过滤后）:
  `engine_status = 'ok'` → `engine_items = ['methodology-framework.md']`

## 6. 复算命令

```bash
curl -s http://127.0.0.1:8181/index.html | grep -c 'consulting-act-'
curl -s http://127.0.0.1:8181/api/v1/consulting/library | python3 -c 'import json,sys; print(json.load(sys.stdin)["total"])'
node /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-013/workspace/rewrite_probe.js   # 改写结果
python3 ui_dom_proof.py --base http://127.0.0.1:8181 --out <same file>
```
