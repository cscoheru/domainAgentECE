# OEI-013 — 演示台 v1（咨询单域）+ 检索重测 + 移除对照文档【暂缓】

- 任务书：`onyx-lab/OEI-013/TASK.md`（v1，A0–A12）
- 执行：cc（Worker）｜ 待验：codex
- 日期：2026-09-26
- commit：`16b4684`（**未 push**；`main` 领先 `origin/main` 6 个 commit）
- 证据：`onyx-lab/OEI-013/evidence/00`–`11`｜工作区：`onyx-lab/OEI-013/workspace/`

---

## 0. 先说三件必须写在最前面的事

### 0.1 A1 / A2 **未按原样完成** —— 这是用户在本刀执行中改的决定

TASK §3.1 记「用户已拍板：移除该对照文档」。cc 在执行这次**不可逆删除**前当面征询，
用户改选：

> **先不删，只做只读取证**

**因此本轮没有向 Onyx 发出任何 DELETE。** 项目 1 仍是 4 份文件（3 份真文档 + 对照文档）。
只读取证在 `evidence/00`、`evidence/01`（含未来若要删的**确切两步命令与两个 id**）。
`evidence/00` 里 `removal_performed: false`、`before_after_identical: true`。

**A2「起链不复建」这一半成立且已证**：`demo-up.sh` 不调 OEI-009 的
`step26_demo_falsifiable.py`（那个脚本才是创建对照文档的），所以起链不会复建它。
**A2「起链后仍 3 份」不成立** —— 因为 A1 没做。

→ 这两条按「**未按原样完成，因用户决定**」计，不按完成计。请 codex 以用户原话为准。

### 0.2 不删它，演示**也是干净的** —— 这条是本刀的实测副产品

对照文档是 `restricted` 且在本链的 `engine_documents` 里没有登记行，
OEI-009 的逐条过滤是 **fail-closed** 的（`no_registry` → 隐藏）。
本刀 86 行产品层观测里，**对照文档可见次数 = 0**。

所以它是**引擎层污染源**，但**已经不是产品层污染源**。
「先不删」因此**有据可依**，而不是把问题往后拖 —— 代价是引擎层排序仍被它挤占（见 §3）。

### 0.3 检索**没有**修好，本刀不假装修好

- **引擎层 hit@1 = hit@3 = 0%**（两档皆然），与 OEI-012 一致；
- **产品层原始路径也是 0%**；
- 加一层确定性关键词改写后，产品层 hit@3 抬到 **44.4%**（9 条 hit 查询口径），
  原始路径同期是 0%。**44.4% 不是可交付的召回质量**，只是从 0 抬起来了。

---

## 1. 交付了什么

| 交付物 | 位置 |
|---|---|
| 视图 D 三幕演示（① 一个问题 ② 知识库怎么答 ③ 你的文件） | `ece/demos/spa/{index.html,app.js,styles.css}` |
| 确定性关键词改写（49→48 词表，纯字符串规则，**改写结果对观众可见**） | `ece/demos/spa/app.js` |
| 10–15 分钟客户语言演示脚本（含三幕 + 我们做了什么/边界/下一步） | `workspace/demo-script.md`（证据 `05`） |
| 一条命令起常驻链（幂等 / 内置 `no_proxy` / 打印 URL） | `workspace/demo-up.sh`（证据 `06`） |
| 停 / 清 | `workspace/demo-down.sh`（`--all` 连带删演示 PG） |
| `make` 入口 | `ece/Makefile` → `make demo-up` / `make demo-down` |
| 检索模式开关（服务端环境变量，默认关） | `docs/API.md` §10 |

---

## 2. 如何起 / 如何停 / 如何清（§3.4.3）

```bash
# 起（幂等：连跑两次第二次不会重复起任何东西 —— 证据 06）
bash onyx-lab/OEI-013/workspace/demo-up.sh          # 或 cd ece && make demo-up
#   → 打印 http://127.0.0.1:8181/index.html   ← 客户演示入口（视图 D）

# 停（保留演示 PG，方便下一场接着看）
bash onyx-lab/OEI-013/workspace/demo-down.sh

# 清（连演示 PG 一起删）
bash onyx-lab/OEI-013/workspace/demo-down.sh --all
```

**现场状态**：写这份报告时 demo 链**正在运行**（按 §8「常驻是交付物」的要求留驻）：
PG `ece-pg-demo`:55433 → API :8765 → 同源起点 :8181。评测用临时 PG 已释放。

---

## 3. 检索重测（A3/A4）—— 本刀的数字全在这里

**口径**：`OEI-012/workspace/retrieval_runner.py` + 同一评测集，N=3 × 两档。
产品层用 `workspace/filtered_runner.py`（匿名调 `/api/v1/consulting/library`，
记**过滤后**的 `engine_items` title 集）。改写词由 `workspace/rewrite_probe.js`
**从发版 `app.js` 里读出来**，不是重写的。

### 3.1 一个前提落空（如实记录）

TASK §3.2.1 要求「去掉针对对照文档的 miss 行」。**这个前提是空的**：
评测集 12 条里 `expected_title` **没有任何一条**指向对照文档。
唯一相关的是 **q10**，它的 *query 文本*与对照文档同题，但它是 **miss 行**、
目标是 `play-sales-delivery.md`。**一行都没删**，评测集与 012 **逐字节相同**
（sha256 `9e5ef6f…5bf6c`，见证据 `07` 第 3 节）。q10 保留并在下表标出。

### 3.2 原始引擎层（`evidence/02-retrieval-rematrix.json`，72 次调用，wall 307.9s）

| 指标 | `expansion_on` | `expansion_off` |
|---|---|---|
| hit@1 / hit@3 | 0.0% / 0.0% | 0.0% / 0.0% |
| 3 次完全一致 | 11/12 = 0.917 | **12/12 = 1.000** |
| 两两 Jaccard 均值 | 0.944 | 1.000 |
| 延迟 median / mean | 4.567s / 6.99s | **1.518s / 1.57s** |
| miss 误召回 | 2/9 | 3/9 |

与 012 的差别本身值得记：012 的不稳定查询是 **{q09, q11}**，本刀是 **{q11}** ——
**「哪些查询不可复现」这件事自己就不稳定**。两刀唯一一致的是 **q11**。

### 3.3 产品可见层（`03` 默认档 / `03b` 确定性档）

| 路径 | 档位 | hit@1 | hit@3 | 召回组为空 | 对照文档可见 | 可复现 |
|---|---|---|---|---|---|---|
| 原始问句 | 默认 | 0.0% | 0.0% | 21/36 | **0** | 0.917 |
| 原始问句 | 确定性 | 0.0% | 0.0% | 21/36 | **0** | 1.000 |
| 关键词改写 | 默认 | **40.0%** | **80.0%** | 1/5 | **0** | — |
| 关键词改写 | 确定性 | 0.0% | 0.0% | **5/5** | **0** | — |

### 3.4 演示实际走的路径，逐条（这是唯一该对外引用的口径）

演示逻辑：有可改写词就用改写，否则用原始问句。

| id | kind | 目标文档 | 原始 h@3 | 改写词 | 演示 h@3 |
|---|---|---|---|---|---|
| q01 | hit | case-management-consulting.md | ✗ | 零售 | ✅ |
| q02 | hit | case-management-consulting.md | ✗ | （不改写） | ✗ |
| q03 | hit | case-management-consulting.md | ✗ | 库存周转 | ✅ |
| q04 | hit | methodology-framework.md | ✗ | 拆解 | ✗ |
| q05 | hit | methodology-framework.md | ✗ | （不改写） | ✗ |
| q06 | hit | methodology-framework.md | ✗ | （不改写） | ✗ |
| q07 | hit | play-sales-delivery.md | ✗ | 交付 | ✅ |
| q08 | hit | play-sales-delivery.md | ✗ | （不改写） | ✗ |
| q09 | hit | play-sales-delivery.md | ✗ | 交付 | ✅ |
| q10 | miss | play-sales-delivery.md | ✗ | 流程 | ✗ |
| q11 | miss | case-management-consulting.md | **✓（误召回）** | 绩效 | ✗ |
| q12 | miss | methodology-framework.md | ✗ | （不改写） | ✗ |

⇒ **9 条 hit 上：演示路径 hit@1 = 2/9 = 22.2%，hit@3 = 4/9 = 44.4%**（原始 0% / 0%）。

**四条边界，不许读成「修好了」**：

1. 44.4% 仍不可演示级，只是从 0 抬起来了；
2. 抬起来**有一部分不是检索变好**，而是权限过滤把对照文档挡掉，真文档从第 2、3 位浮上来
   —— 这是 OEI-012 VERDICT §5 预告过的效应，本刀量到了；
3. **5 条查询不会触发改写**（问句里没有词表里的业务词），它们仍是 0%；
4. 词表 + 固定规则改写是**兜底**，不是检索能力本身；API 层对其它调用方仍做整串匹配。

### 3.5 与任务书 §3.2.2 相反的一条结论（本刀最重要的负面发现）

TASK §3.2.2 建议「优先用 `skip_query_expansion=true` 的确定性路径」。

**实测不支持这个优先级。** 确定性档更可复现（1.000 vs 0.917）也更快（1.518s vs 4.567s median），
但在产品层是**净负**：改写路径召回组 **5/5 全空**，hit@3 **0% vs 默认档 80%**。
机制清楚：确定性档候选集更窄，这些问句下它唯一返回的就是对照文档，而被 fail-closed 挡掉 → 用户看空。

→ **`demo-up.sh` 默认 `ECE_LIBRARY_SKIP_QUERY_EXPANSION=0`**（引擎默认档）。
开关按 §3.2.2 接了进来，**但默认值是按数字选的，不是按任务书建议选的**；
理由与数字写在 `demo-up.sh` 的注释和 `docs/API.md` §10 里。Port 自身默认仍为 `False`（§8）。

### 3.6 演示面另一处**没被预告**的抖动

`evidence/04` 快照里 `诊断 → 1 条` 引擎结果；写报告时现场复测同一问句得到 **3 条**。
这不是新问题，就是 §3.2 量到的 0.917 复现性在演示面上的样子。
已加进 `demo-script.md` 的「演示者必读」与 FAQ：**不要预告条数**，空召回组也照实说。

---

## 4. 契约不回归 + 全套件（A8）

### 4.1 契约（`evidence/07`，PASS）

- `src/ece/consulting/models.py` 相对 `4a67c28` **零 diff**；AST 逐模型核对
  `LibraryResponse`(7) / `KnowledgeObject`(14) / `EngineItem`(6) / `FacetsResponse`(2) 字段集合相同；
  `_FACET_KEYS` 6 个 slug 未变；
- **线上**（评测库实例）三级键集合全对：`/library` 顶层 7 键、`items[]` 14 键、
  `engine_items[]` 6 键；`/facets` 顶层 2 键、`facets` 6 键且每列非空；
- consulting/demo/onyx/SPA **既有子集 204 passed / 0 failed**；
- `pyproject.toml` / `uv.lock` **零 diff**（无新依赖）；
- 三域业务断言与 65 个种子对象（`consulting_objects.json`）、评测集 **零 diff**。

### 4.2 全套件（`evidence/08`）

**894 passed / 3 skipped / 0 failed / 3 deselected**（全新库 + 完整前置链 + `-rs`，230s）。

与基线（859 / 5）的差额**从日志算出来**，不写死：

| 项 | Δ | 说明 |
|---|---|---|
| 本刀新增测试 | **+33** | `test_library_recall_mode.py`(23) + `test_consulting_demo_rewrite.py`(10) |
| `test_e2_permission.py:50/:103` | +2 | 由 skip 转 PASS —— 基线理由是「env not ready」，本轮 fixture 已 seed |
| `test_cut_045_local_origin_smoke.py` | ± | **环境抖动**，见下 |

**`test_cut_045_local_origin_smoke.py:213` 是不稳定测试**：它自己在随机端口冷起 uvicorn、
10 秒超时。本刀三次连跑观测到 **893/4** 与 **894/3** 两种结果，差别只在这一条。
该文件相对基线零 diff，且它 skip 时理由原样打在 `-rs` 列表里。如实报，不粉饰。

### 4.3 新增的 33 条测试在测什么

- `test_library_recall_mode.py`：本刀新增的**两闸 AND**
  （`library_deterministic_recall()` **且** `engine.supports_skip_query_expansion`）。
  两闸各自单独都会是 bug：只有闸一 → 窄引擎（含套件里的测试替身）收到意外关键字而 TypeError；
  只有闸二 → 确定性路径默认开，违背 §3.5 的数字。还钉住「env 在**调用时**读而不是 import 时读」
  —— 第一版是 import 时缓存，那样切换模式必须重启进程，且不 reload 就没法测。
- `test_consulting_demo_rewrite.py`：钉住**每条词表词都能命中 ≥1 个目录对象**
  （49 词手写，匹配不到的词是死重量而不是覆盖）、每个 chip 问句都含 ≥1 个词表词
  （否则该 chip 静默失去改写）、词表无重复、改写提示可见性。
  **这条测试当场抓到一个真 bug：`定价` 在词表里写了两次**，已修（49→48）。

---

## 5. 文档 / 提交 / 合规（A9/A10/A11）

- `docs/API.md`：新增 `supports_skip_query_expansion` 能力表与 `ECE_LIBRARY_SKIP_QUERY_EXPANSION`
  环境变量表（写明它**不是** HTTP 参数，以及默认关是产品层实测选出来的）；
- `TASKS.md 附录 T`：本刀全量结论；
- `Makefile`：`demo-up` / `demo-down` + help 两行；
- `make check-api-docs` → **`App-only: 0`**，exit 0（`evidence/11`）；
- `git commit 16b4684`（**未 push**，`evidence/09`）；
- 合规（`evidence/10`）：demo 链**留驻**、评测临时 PG **已释放**、9 个 Onyx 容器
  **RestartCount=0**、冻结面全零 diff、`tests/` 仅新增（既有断言 0 删除）、
  cookie 只读且 0 个值进制品（扫描器经 canary 证明有牙）。

---

## 6. 需要 codex 关注的四件事

### 6.1 验收偏差

| # | 验收 | 状态 |
|---|---|---|
| **A1** | 两步删除 + 删后项目 1 只剩 3 份 | ❌ **未按原样完成**（用户改选「先不删，只做只读取证」；未发出任何 DELETE） |
| **A2** | 起链不复建 + 起链后仍 3 份 | ⚠️ 一半：**不复建成立且已证**；「仍 3 份」因 A1 未做而不成立 |
| A3 | 两档 × 原始 + 过滤后如实落盘 | ✅（`02`/`03`/`03b`，口径与 012 逐字节一致） |
| **A4** | 结论诚实；若不改善则接确定性路径 | ✅ **但结论与 §3.2.2 相反** —— 见 §3.5，故**不接进演示** |
| A5–A12 | | ✅（逐条见 §1/§4/§5 与对应证据） |

### 6.2 工作区里有**不属于本刀**的既有改动 —— 提交时**刻意排除**了

`git status` 仍会看到 14 项脏状态。**本刀一个字节都没写过它们**：

- `docs/demo-platform/*.md`（**typechange**）：/mnt/d（WSL2 DrvFs）把 tree 里的符号链接
  落成 `XSym` 重解析点，git 看到 1067 字节常规文件 vs tree 里 51 字节链接。mtime **2026-09-22**，
  该目录末次提交 `03662da`(cut-042R)。§8 未授权该目录，本刀不改它。
- `reports/cut-042R3|043|044/mutation-evidence/*.md`（12 个）：diff 是 208 增 / 208 删，
  **逐行只差 ANSI 颜色转义被剥掉**，内容一字未变。mtime 全是 **2026-09-23**，
  比本刀早三天。

**提交只显式 add 了本刀的 12 个文件**，用 `git add -A` 会把这 14 项一并带上、造成错误归属
（见 `evidence/09` 第 2、5 节）。请 codex 核对时不要把它们算进本刀。

### 6.3 `scripts/` 不在授权面 → 同源起点脚本写在 workspace

`cut-045_local_origin.py` 硬编码 10 秒上游超时，对引擎冷启动不够；
但 §8 未授权 `scripts/`，所以本刀把同源起点写在 `workspace/demo_origin.py`
（`--upstream-timeout` 默认 120s），**没有**改 `scripts/` 下任何文件。
`workspace/` 是任务书给的落地位置（§4）。

### 6.4 已知残留风险：谁跑 `step26` 谁就会重建对照文档

`onyx-lab/OEI-009/workspace/step26_demo_falsifiable.py` **仍在**，它**创建**对照文档。
§8 未授权 `onyx-lab/OEI-009/`，本刀无权改。这是**已知残留**，请后续刀处理
（或在该文件顶部加一行警告）。

---

## 7. 转出（下一刀的候选）

1. **对照文档去留**：产品层已不受影响，引擎层排序仍被它挤占。数字在此，等你定
   （`evidence/00` 备好了两步删除的确切命令与两个 id）。
2. **排序问题是最大遗留**：产品层靠「过滤 + 改写」抬到 44.4%，但**引擎本身仍是 0%**。
   要真修得动 Onyx 服务端配置或换检索路径 —— 超出本刀授权。
3. **目录检索语义化**：现在靠 48 词表 + 固定规则兜底；换整串匹配是 API 契约级改动。
4. **真认证**（承 OEI-009）：讲「两种身份、不同召回」之前必须先做。
5. `merge_engine` 的 fail-open 显式化（承 OEI-009）。
6. `test_cut_045_local_origin_smoke.py` 的 10 秒冷启动超时 —— 建议提高或改成轮询。
