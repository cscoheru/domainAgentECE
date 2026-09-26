# OEI-012 任务书 — 检索质量（召回评测集 + 召回可复现 + 一项实测改进）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-26
> 前置：`OEI-001～011` 与 `OEI-014` 已全部收束；本刀是唯一**必须用真引擎取证**的检索质量刀
> 返工约定：本刀若需返工，一律标 **`OEI-012 R1` / `R2`**（不插新刀、不顺延既有编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## ✦ 开工指令（cc 必读：按序读完再动手）

> **`onyx-lab/` 顶层的一批文档已由用户并入 `onyx-lab/重启必读/`**；`CODEX-ROLE.md` / `README.md` / `ASSET-INDEX.md` / `DECISION-ONYX.md` 仍在顶层。

**① 按序必读（绝对路径，一份都别跳）**

```
1. /mnt/d/Projects/domainAgentECE/AGENTS.md                                  ← 项目总规则
2. /mnt/d/Projects/domainAgentECE/onyx-lab/README.md                          ← 入口索引 + 目录变更
3. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/CC-ROLE.md                 ← 你的角色任务书
4. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/LOCAL-AGENT-PROTOCOL.md    ← 共享规则 + §5.1 资源纪律（**本刀会长时间占用真引擎**）
5. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/OEI-ROADMAP.md             ← 路线图：本刀条目（已含 `/api/search` 是 agentic 管线的修正）
6. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/VERDICT.md                  ← 上一处管线发现（末尾 #3 §4 = 本刀的事实前提）
7. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/DEPLOYMENT-STATUS.md       ← 环境事实（已知问题 #5 = `/api/search` 管线；凭据窗口；swap 压力）
8. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-001/workspace/                 ← **三份演示文档源文本**（本刀评测集的 ground truth 出处）
9. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/TASK.md                     ← **本文件 = 唯一任务来源**
```

**② 开工前先核对状态（只读）**

```bash
cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012 && ls -la          # 不该有 DONE / VERDICT.md
cd /mnt/d/Projects/domainAgentECE/ece && git log --oneline -2 && git status -sb | head -3
# 期望：HEAD = a3d61cd（OEI-014），ahead 4，未 push
# ★ 凭据前置（本刀必须真引擎取证）：
CK=/home/fisher/.onyx-lab/.secrets/admin-cookies.txt
for p in /api/me /api/health; do printf '%s -> ' "$p"; curl -s -m 8 -b "$CK" -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8080$p"; done
# 两个都 200 才能开工；403 → 停手报 BLOCKED（刷新由用户做，绝不用 mock 顶替）
```

**③ 本刀一句话**

把"引擎检索质量"从主观印象变成**可复现的数字**：建一份**召回评测集**（query → 应命中的文档，ground truth 来自三份演示文档原文）、测出 **`/api/search` 在两种模式下的命中率与复现性**（query expansion 开 / 关），并**实现且实测至少一项改进**（首选 `skip_query_expansion` 接入），写清代价与决策。

**④ 硬约束速查（违反即 FAIL，全文见 §8）**

- ✅ 授权改：`src/ece/connectors/onyx/{port,onyx_adapter,mock_adapter}.py`（只加 `skip_query_expansion` 形参）、`tests/**`（新增文件；**既有断言不得改**）、`data/eval/retrieval/`（新增评测集）、`docs/API.md`、`TASKS.md`；可 `git commit`（**不 push**）
- ❌ **不改 Onyx 任何配置**（`auto_detect_filters` 是服务端设置，**不能**通过请求关掉；改 compose / `.env` 越界）；不重启/停/删容器
- ❌ 不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）；**不做 LLMPort / 换模型**（本刀没有云模型，也不自建）
- ❌ **不改 `ContentEnginePort.search` 的既有语义**（空结果仍 `[]`、错误仍 `EngineError`、审计仍记）；**不改 consulting library 的默认行为**，除非 A/B 实测支持且写成决策
- ❌ 不碰 `ece/demos/spa/**`；不得要求用户截图；密钥只写 `<REDACTED>`
- 📌 **本刀是唯一"必须真引擎"的刀**：代码/单测用 mock，**评测矩阵用 `ECE_CONTENT_ENGINE=onyx`**（失败路径同样不得用 mock 代替）。真引擎每查 **20–56s**，按 §5 的规模上限跑，跑完记录资源、**不得在评测中途增删语料**

**⑤ 收工与心跳**

```bash
echo "$(date -Iseconds) OEI-012 complete" > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/DONE
```

然后 **STOP**。心跳对象 = `onyx-lab/OEI-012/VERDICT.md`。

---

## 0. 一句话目标

产出三样东西：① **一份可提交、可复跑的召回评测集**（ground truth 可溯源）；② **一组真引擎上的命中率 + 复现性实测**（query expansion 开/关两档）；③ **至少一项实现并实测的改进**（首选给 `ContentEnginePort.search` 加 `skip_query_expansion`，或确定性客户端 query rewrite），附代价评估与决策。**核心是把"检索好不好"变成数字，且把"召回可复现"当成与"召回精度"同级的验收面。**

**为什么是这一刀**（`OEI-009/VERDICT.md` #3 §4 + `OEI-ROADMAP.md` 的 OEI-012 条目）：

1. `OEI-009` 实测发现 `/api/search` **不是向量 top-k**，而是 **chat 模式的 agentic 检索管线**（LLM `auto_detect_filters` + query expansion）：返回条数随 query 变（1/2/3/4/5）、单次 20–56s、无意义 query 也返回结果。此前 OEI-002/006 记的召回问题是**主观观察**（"q2 漏召 play"），没有数字。
2. 现在正是把主观换成客观的时机：语料已经稳定（3 份演示文档 + 1 份对照），权限/身份/记忆/内容都收束了，**检索质量是演示面最后一块没量化的短板**。
3. 这一刀只碰**检索接口**，不碰权限、身份、内容——风险边界小，但它直接决定 013（演示台）能讲得多可信。

---

## 1. 现状（codex 实测，可直接信任；每条都带"文件 + 符号 + 数值"）

### 1.1 ECE 侧的检索调用今天只发一个字段

`src/ece/connectors/onyx/onyx_adapter.py:157 search()`：

- body 只有 `{"query": query}`；
- 注释（`:166`）写"Onyx v4.7.8 /api/search does not accept top_k directly；client-side 切片"；
- **没传 `skip_query_expansion`** → 引擎侧该参数取默认 `False` → **query expansion 开着**。

`ContentEnginePort.search(query, *, top_k=None, caller=None)`（`port.py:211`）与 `mock_adapter.search`（`mock_adapter.py:141`，确定性、50ms 模拟延迟）都**没有**这个形参。

### 1.2 Onyx 侧 `/api/search` 请求模型（我读了容器内 `server/features/search/models.py`）

`SearchRequest` 字段：`query`（必填）、`sources`、`document_sets`、`tags`、`time_cutoff`、`persona_id`、`provider`+`model`（成对）、**`skip_query_expansion: bool = False`**、`message_history`。

**两个关键结论**（直接决定本刀怎么做）：

1. **`skip_query_expansion` 是唯一可由请求方控制的相关开关**；`api.py:167` 的 `auto_detect_filters=load_settings().auto_detect_search_filters is not False` 是**服务端设置**，**不能通过请求关掉**（要关 = 改 compose/.env，越界）→ 别浪费时间试。
2. **没有 `top_k`**（`api.py` 里没有这个字段），所以 ECE 现有的"client-side 切片"做法是对的；本刀**不新增 top_k 语义**。

### 1.3 语料（本刀评测对象）很小，且源文本可溯

Onyx 演示项目 `id=1` 现有 **4 份**文档：

```
case-management-consulting.md / methodology-framework.md / play-sales-delivery.md（3 份真文档）
ece-df16d19c9e7b-oei009-comparison-restricted.md（OEI-009 的对照文档，权限受限）
```

三份真文档的**源文本**在 `onyx-lab/OEI-001/workspace/{case-management-consulting,methodology-framework,play-sales-delivery}.md`——**评测集的 ground truth 必须从这三份原文推导**，不是拍脑袋。

### 1.4 已知的非确定性事实（本刀的验收前提）

`OEI-009/VERDICT.md` #3 §4（已录）：

- 返回条数是"相关性结果"不是固定 k；同一文档多 chunk 各占一条（要按 **title 去重**）；
- 无意义 query 也返回结果（所以"应不匹配"不能定义成"期望 0 条"，见 §3.1）；
- 单次 20–56s；向量删除异步；
- 当时对**选定的 query** 3/3 次召回一致——**"复现性到底多好/多差"正是本刀要量化的**。

### 1.5 现有评测装置与本刀的关系

`data/eval/e1_resolution.json … e6_agent.json` 是**权限/上下文**的评测集（E1–E6），**没有检索召回评测**；`make eval` = `pytest -m "eval or eval_llm"`。本刀的召回评测需要真引擎 + cookie + 每查 20–56s，**不接进 `make eval`**（否则默认评测套件会依赖 Onyx 栈），而是**独立 runner + 提交评测集**（见 §3.2）。

### 1.6 凭据与资源现状

- 凭据：`/api/me`、`/api/health` 当前 **200**（我实测）；cookie jar 约 **~10-02 过期**，本刀要在窗口内取完证。
- 资源：9 个 Onyx 容器常驻约 7.5GiB，swap 压力偏高；本刀真引擎取证**很耗时**，必须按 §5 的规模上限走、中途不增删语料、结束记录内存/swap 快照。

---

## 2. 范围锁

**做**：

1. **召回评测集**（提交）：query → 应命中 title + 依据（引原文）+ "应不匹配"对；
2. **复现性 + 命中率矩阵**（真引擎，N=3 × 两档 expansion）；
3. **一项实现并实测的改进**（首选 `skip_query_expansion` 接入 + 实测决策；或确定性客户端 rewrite）；
4. **代价评估 + 决策**写成 `workspace/retrieval-decision.md`；
5. 单测 + 契约不回归 + 全套件 + 文档 + 提交。

**不做**（做了即越界）：

- 不改 Onyx 配置（compose / `.env` / 服务端 settings）；**不试图关 `auto_detect_filters`**（请求级做不到）；
- 不新增模型 / LLMPort；不引入新依赖；
- **不改 `ContentEnginePort.search` 的既有语义**；**不改 consulting library 默认行为**（除非 A/B 支持且写决策）；
- 不改权限/身份/记忆/内容；不动前端；不碰三域业务断言；
- 不做"万能重排器/自研向量检索"这类平台级改造（那是过度工程）。

---

## 3. 契约（**本刀锁定**；发现契约与实测不符 → 停手 + 写 REPORT + 等 codex 对齐）

### 3.1 评测集怎么建（ground truth 必须可溯源）

1. **从三份演示文档原文**（§1.3 的路径）找**有辨识度**的段落，为每份文档写 **2–4 个"应命中它"的 query**，外加 **2–3 个"应不匹配某文档"的 query**。合计 **8–12 条**。
2. 每条记录：`id / query / expected_title / kind ∈ {hit, miss} / rationale`（`rationale` 引原文的那句话——**这是人工可复核的依据**）。
3. **"应不匹配"的语义**（重要，见 §1.4）：**不是"期望返回 0 条"**（Onyx 任何 query 都回结果），而是"**期望 `expected_title` 不出现在该 query 的召回集合里**"。
4. 评测集提交到 `data/eval/retrieval/consulting-demo.json`（或 `.jsonl`），格式稳定、可机检。

### 3.2 复现性与命中率怎么测

- 两个档：`expansion_on`（现状：不传 `skip_query_expansion`）与 `expansion_off`（`skip_query_expansion=true`）。
- **N=3**：每条 query 每个档各跑 3 次；记录**每次去重后的 title 集合 + 顺序 + 延迟**。
- 指标（口径写死）：
  - **hit@k**：`expected_title` 是否出现在召回集合**前 k 个去重 title** 里（k = 1 与 k = 3 各报一个数）；
  - **复现性**：逐 query，**N 次召回集合（去重 title 集）是否完全一致** + 逐次 Jaccard（两两），给出"完全一致的比例"；
  - **误召回**：`miss` query 中 `expected_title` 出现次数。
- 结果落 `workspace/retrieval-matrix.json`（机器可读）+ 一份可读摘要。

### 3.3 改进怎么定（**不做没有数字支撑的默认翻转**）

1. 实现 `skip_query_expansion` 接入：`ContentEnginePort.search(..., skip_query_expansion: bool = False)` → `onyx_adapter` 把它放进请求 body → `mock_adapter` 接受并忽略（契约同构）。
2. **默认值 = `False`（= 现状）**；**除非** A/B 表明 `expansion_off` 在"复现性显著更好 且 hit@k 不降（或降幅可接受）"时，才允许改默认或改调用点，**且必须在 `retrieval-decision.md` 写清数字理由**。
3. 若选做客户端 query rewrite：**必须确定性**（无 LLM；例如术语→文档词表的映射），且同样要有 before/after 数字。
4. 最终结论三选一（都要写）：`expansion_off 更优` / `expansion_on 更优` / `无显著差异（保持现状 + 提供开关）`。

### 3.4 契约不回归

- `search()` 空结果仍返回 `[]`、错误仍 `EngineError`、审计仍记（OEI-008 语义）；
- `mock_adapter` 与 `onyx_adapter` 的 `search` 签名**同构**（新形参两端都有）；
- consulting library 的 `engine_items` / 静态侧 / 权限过滤**不变**（本刀只动检索开关，不动合并与过滤）。

---

## 4. 工作区与证据命名

```
onyx-lab/OEI-012/
├── TASK.md      ← 本文件（只读）
├── workspace/   ← 源文件/素材（retrieval-matrix.json、retrieval-decision.md、runner）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

建议证据文件：`00-credentials.txt`、`00b-baseline.txt`、`01-evalset.json`（引用提交路径）、`02-plumbing-diff.txt`、`03-unit-test-raw.txt`、`04-retrieval-matrix.json`、`05-hit-repro-summary.txt`、`06-decision.md`（引用 `workspace/retrieval-decision.md`）、`07-contract-regression.txt`、`08-test-suite-raw.txt`、`09-git-commit.txt`、`10-compliance-check.txt`、`11-check-api-docs.txt`

## 5. 任务步骤

### 步骤 0 — 前置（凭据 / 语料稳定 / 基线）

1. 凭据 200（§开工指令 ②）；若不 200 → **停手报 BLOCKED**，不降级。
2. 确认项目 1 语料稳定（4 份、索引 COMPLETED），**评测全程不增删**；记录文档清单。
3. `ECE_CONTENT_ENGINE=mock` 跑 consulting/onyx 相关单测基线，落盘 `00b-baseline.txt`。
4. 记录 `git log --oneline -1` / `git status` 快照。

### 步骤 1 — 建评测集（A1）

1. 读三份原文，按 §3.1 产出 8–12 条，提交到 `data/eval/retrieval/consulting-demo.json`；落盘 `01-evalset.json`（引用 + 逐条 rationale）。

### 步骤 2 — `skip_query_expansion` 接入（A4 的实现面）

1. `port.py` / `onyx_adapter.py` / `mock_adapter.py` 三处加形参（默认 `False`）；onyx adapter 把它放进 body；mock 接受并忽略。
2. 单测：用 httpx 桩证明 `skip_query_expansion=true` 时请求 body 含该字段（原始输出落 `03`）；既有单测不破。
3. 落盘 `02-plumbing-diff.txt`（三文件 diff）。

### 步骤 3 — 真引擎评测矩阵（A2/A3，**本刀的核心取证**）

1. `ECE_CONTENT_ENGINE=onyx` + cookie；按 §3.2 跑 N=3 × 两档 × 8–12 query；**中途不增删语料**。
2. 记录每次去重 title 集合 + 顺序 + 延迟；落 `04-retrieval-matrix.json` + `05-hit-repro-summary.txt`。
3. 记录开始/结束时间与内存/swap 快照（写进 `10-compliance-check.txt`）。

### 步骤 4 — 代价评估 + 决策（A5）

写 `workspace/retrieval-decision.md`：两档的 hit@k / 复现性 / 延迟 / LLM 调用代价，并给 §3.3 的三选一结论；若改默认，写清数字理由。落 `06-decision.md`（指向它）。

### 步骤 5 — 契约不回归 + 全套件（A6/A7/A8）

1. `search()` 语义、mock/onyx 同构、consulting library 不变：`07-contract-regression.txt`。
2. 新增 DB-free 单测（adapter 传参 + mock no-op）；`03-unit-test-raw.txt`。
3. 收尾**一次**全套件（临时 PG + 完整前置链 + `-rs`），落 `08-test-suite-raw.txt`；期望 847 + 新增、0 failed、skipped=5（否则 `-rs` 名单解释）。

### 步骤 6 — 文档 + 提交 + 合规

1. `docs/API.md`（`/engine/status` 或 search 相关段补 `skip_query_expansion` 语义 + "检索可复现"的已知结论）、`TASKS.md` **附录 S**、`data/eval/retrieval/` 提交；
2. `git add` + `git commit`（**不 push**）；落 `09-git-commit.txt`；
3. `make check-api-docs`（`11`）；收尾三查 + 密钥扫描 + 内存快照（`10`）。

---

## 6. 验收标准（codex 将逐条核对；**每条都必须能被 evidence 证明**）

- [ ] **A0** 前置：凭据 200；语料稳定（4 份、评测中途零增删，给出清单）；mock 基线单测落盘
- [ ] **A1** 评测集：提交到 `data/eval/retrieval/`，8–12 条；每条含 `query / expected_title / kind ∈ {hit,miss} / rationale`，**rationale 引三份原文、可人工复核**；`miss` 语义正确（= `expected_title` 不在召回集，**不是**期望 0 条）
- [ ] **A2** 复现性矩阵：N=3 × 两档，逐 query 记录去重 title 集 + 顺序 + 延迟；给出**每档"完全一致比例"**与逐次 Jaccard；原始数据落 `04`
- [ ] **A3** 命中率：`hit@1` 与 `hit@3` 两档各一个数（口径写死）；`miss` query 的误召回计数
- [ ] **A4** 改进实现：`skip_query_expansion` 三处接入（port / onyx / mock），默认 `False`；**无没有数字支撑的默认翻转**；httpx 桩证明传参（原始输出）
- [ ] **A5** 代价评估 + 决策：`workspace/retrieval-decision.md` 含 hit@k / 复现性 / 延迟 / LLM 调用代价 + §3.3 的三选一结论；若改默认有数字理由
- [ ] **A6** 契约不回归：`search()` 空/错/审计语义不变；mock 与 onyx 签名同构；consulting library 的 `engine_items`/静态侧/过滤不变（键集合对照）
- [ ] **A7** 单元测试：新增 DB-free 单测全绿；既有 consulting/onyx 单测不破
- [ ] **A8** 全套件 **0 failed**（847 + 新增），`-rs` 附 skip 名单
- [ ] **A9** 文档：`docs/API.md`、`TASKS.md 附录 S`、`data/eval/retrieval/` 已提交；`make check-api-docs` 仍 `App-only 0`
- [ ] **A10** 提交：`git commit`（**不 push**）+ 短 hash 与文件清单落盘
- [ ] **A11** 合规与资源：未碰 Onyx config / compose / `.env`；容器 `RestartCount=0`；无新依赖；`demos/spa` 零 diff；密钥只 `<REDACTED>`；评测前后内存/swap 快照；无残留进程；未 push
- [ ] **A12** 证据纪律：全部机器可校验（JSON / 原始响应 / 单测输出）；评测**可复跑**（附复跑命令）；无"检索效果良好"这类不可判定表述；无用户截图

## 7. 完成后的动作（严格按序）

1. 自检目录与证据完整性、无密钥泄漏、临时资源已清理（收尾三查）
2. `echo "$(date -Iseconds) OEI-012 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭；FAIL → 按 `R1/R2…` 返工后重建 `DONE`

---

## 8. 硬约束（违反即 FAIL）

- ✅ **授权改**：`src/ece/connectors/onyx/{port,onyx_adapter,mock_adapter}.py`（只加 `skip_query_expansion`）、`tests/**`（新增文件；**既有断言不得改**）、`data/eval/retrieval/**`（新增）、`docs/API.md`、`TASKS.md`；可起临时 PG；可 `git commit`（**不 push**）
- ❌ **不改 Onyx 配置**（`auto_detect_filters` 是服务端设置，**请求级关不掉**）；不改 compose / `.env`；不 restart / stop / down / rm 任何容器
- ❌ 不新增模型 / LLMPort / 新依赖（`pyproject.toml` / `uv.lock` 零 diff）
- ❌ **不改 `ContentEnginePort.search` 的既有语义**；**不改 consulting library 默认行为**（除非 A/B 支持且写决策）；不改权限/身份/记忆/内容
- ❌ 不动 `ece/demos/spa/**`；不改三域业务断言；不删既有测试；不得要求用户截图
- 📌 **真引擎纪律**：评测矩阵必须 `ECE_CONTENT_ENGINE=onyx`（失败路径同样不得用 mock 代替）；**中途不增删语料**；每查 20–56s，按 §5 规模上限跑，跑完记录资源
- 📌 **凭据不可用不得降级**：`/api/me` 非 200 → 停手报 BLOCKED，不 mock 顶替
- 📌 穷尽性断言必须附可复现命令（OEI-011 立的规矩）

## 9. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-012/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-012/DONE`
- 无新文件则静默，不重复执行、不打扰用户
