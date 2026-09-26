# OEI-012 步骤 4 — 代价评估 + 决策（A5）

> 数据来源：`evidence/04-retrieval-matrix.json`（真引擎，72 次调用）、
> `evidence/05-hit-repro-summary.txt`（由 04 机算）、`evidence/04b-run-log.txt`（原始 stdout）。
> 复跑命令见本文件末尾 §6。

## 0. 结论（§3.3 三选一）

> ### ✅ **`expansion_off 更优`**（关掉 query expansion 更优）
>
> 依据：在**复现性**、**延迟**、**LLM 调用代价**三条轴上 `expansion_off` **严格更优**；
> 在**命中率**轴上两档**完全相同**（都很差，见 §1）。`expansion_off` 在任何一条轴上都没有更差。
>
> **但决定：默认值仍保持 `False`（不翻转）。** 理由见 §4 —— 这是"有数字支撑的**不**翻转"，
> 不是"没有数字所以不翻转"。

---

## 1. 命中率（A3）—— 本刀最重要的负面发现

| 档位 | hit@1 | hit@3 | 误召回（miss query 里目标文档仍出现） |
|---|---|---|---|
| `expansion_on`  | **0.0%** | **0.0%** | 3 / 9 |
| `expansion_off` | **0.0%** | **0.0%** | 3 / 9 |

**9 条 hit query，两档各 27 次运行，目标文档一次都没进前 3。**

关键的是——**这不是"索引里没有"**。矩阵内三份目标文档都被实际召回过：

| 文档 | 矩阵内被召回次数 |
|---|---|
| `case-management-consulting.md` | 18 |
| `methodology-framework.md` | 6 |
| `play-sales-delivery.md` | 4 |
| `ece-…-oei009-comparison-restricted.md`（对照） | **61** |

再补一条独立佐证：q05 的原文 `MECE 的排他性和穷尽性怎么检验` 是 `methodology-framework.md`
里的**逐字标题句**，而该档返回的是 `CASE+RESTR`（`expansion_off`）/ `CASE+RESTR+PLAY`
（`expansion_on`）——**逐字查询也召不回原文**。

所以结论是**排序问题，不是索引问题**：文档在库里、能被召回，只是**排名与 query 语义不相关**。
`skip_query_expansion` 对这件事**没有任何帮助**（两档同等 0%）。

> **一句话**：本刀没能提升命中率，但**证明了命中率的现状是 0%**，并且把"0% 到底是索引坏了
> 还是排不上来"这个会决定后续所有工作的分岔口**判死了**（是排序）。

## 2. 复现性（A2）

| 档位 | N 次去重 title 集完全一致 | 完全一致比例 | 两两 Jaccard 均值 |
|---|---|---|---|
| `expansion_on`  | 10 / 12 | **0.833** | **0.926** |
| `expansion_off` | 12 / 12 | **1.000** | **1.000** |

`expansion_off` **完全可复现**（12/12，两两 Jaccard 全为 1.0）。
`expansion_on` 有**两条** query 不稳定（10/12），且症状完全相同 —— **第 1 次与后两次不一致**：

- **q09**（`交付 kickoff 会议要讲清哪三件事`）：
  `CASE+RESTR` / `CASE+METH` / `CASE+METH` → r1~r2 = r1~r3 = **0.333**，r2~r3 = 1.0；
  同一条 query 在 `expansion_off` 下三次全是 `CASE+METH`。
- **q11**（`研发团队 OKR 绩效考核办法`）：
  `METH+CASE+PLAY` / `CASE` / `CASE` → r1~r2 = r1~r3 = **0.333**，r2~r3 = 1.0；
  在 `expansion_off` 下三次全是 `CASE`。

（逐次两两 Jaccard 的完整明细见 `05-hit-repro-summary.txt` §A2 明细段。）

两点值得记：① 不稳定的**都是第 1 次**跑，后两次彼此一致 —— 与延迟上观察到的
**冷启动首调**同源，说明 `expansion_on` 的第一次调用走的路径与后续不同（LLM 侧缓存/预热）；
② 关掉 expansion 后这两条 query 也都稳定了。

也就是说：**不确定性来自 query expansion 那一步**（LLM 参与），关掉它就消除了。
这正是本刀把"召回可复现"当作与"召回精度"同级验收面的直接收获。

## 3. 代价：延迟与 LLM 调用

### 3.1 延迟（秒，仅成功行，n=36/档）

| 档位 | min | median | mean | max |
|---|---|---|---|---|
| `expansion_on`  | 3.33 | **5.02** | 10.67 | 46.63 |
| `expansion_off` | 1.35 | **1.47** | 2.25 | 27.27 |

**中位数加速比 3.41×，均值加速比 4.74×。**

### 3.2 LLM 调用代价（可测的口径）

`/api/search` 的响应体**不含** token usage 字段，引擎日志也不吐 token 数，
所以本刀**不报 token 数**（报不了就不编）。可测的是**延迟分布形状**，它足以区分
"每查都走 LLM" 与 "压根不走 LLM"：

| 档位 | < 2s 占比 | ≥ 10s 占比 | 分布形态 |
|---|---|---|---|
| `expansion_on`  | **0%**（0/36） | 28%（10/36） | 3.3 → 46.6s 长尾；**没有一次快过** |
| `expansion_off` | **94%**（34/36） | 3%（1/36） | 紧贴 1.4–1.6s；唯一离群点是**冷启动首调**（27.3s） |

`expansion_on` **36 次调用没有一次低于 3.3s** → 每一次都在付 query expansion 的 LLM 往返；
`expansion_off` **36 次里 34 次在 2s 内**且几乎常量 → 走的是**不经 LLM 的向量路径**。
（`expansion_off` 的那个 27.3s 离群点是本档第 1 次调用，属冷启动，不代表稳态。）

> 稳态口径建议取 **median**：`3.2s` 与 `1.4s` 的差距(去掉冷启动后约 1.4–1.6s)，比均值更能代表稳态。

## 4. 决策：默认值**不翻转**（A4）

三选一的结论是 `expansion_off 更优`，但**默认值仍为 `False`**。这是有数字支撑的主动选择：

1. **翻转买不到本刀要的东西。** 这条刀的目的是"检索质量"。`expansion_off` 在
   复现性/延迟/成本上更优，但在**命中率上是 0% — 和 `expansion_on` 一模一样**。
   把默认翻成 `True`，会让所有调用方（含 consulting library）的行为改变（A6 明令除非
   A/B 实测支持且写成决策才可改），却**换不来任何一条 query 的召回改善**。
2. **`expansion_off` 会让候选集变窄。** q05：`expansion_on` 3 条 → `expansion_off` 2 条；
   q11：3 条 → 1 条。当前没有任何一条说"窄掉的正是该丢的"——反而 q05 窄掉的是 `PLAY`，
   而库里三份目标文档本来就都该有机会出现。在排序问题解决前先把候选集收窄，
   是**用一个未验证的假设去换一个已量化的收益**。
3. **默认值是产品决策，不是一个性能开关。** 正确顺序是：先解决排序（让 hit@k 不再是 0%），
   再在**有效的**排序之上重新测两档——那时的复现性/延迟优势才有意义。现在翻转，
   等于把"最有价值的实测发现"（复现性 1.0 vs 0.833）挂在一个用不了的检索上。

**因此本刀的交付是：把开关接出来（默认 `False`，无默认翻转）+ 把两档数字钉死 + 把排序
问题定性。** 后续刀应优先处理排序，处理完再回来用本刀的口径复测。

## 5. 局限（写清楚，别让后来的刀误用这些数）

- **样本小**：12 条 query、单一语料（项目 1 的 4 份文档）、N=3。足以**定性**
  （0% vs 0%、1.0 vs 0.833），不足以给**置信区间**。
- **冷启动污染**：每档第 1 次调用显著偏慢（`expansion_off` 27.3s、`expansion_on` 46.6s）。
  本刀保留原始数据不剔除，但**结论一律以 median 为准**。
- **测量用 client timeout = 180s**（`04` 的 `client_timeout_seconds`）。
  产品默认仍是 60s 未改；不放大这一项的话，冷启动的 `expansion_on` 会被 60s 截断成
  "失败"，把"慢"错记成"没有数据点"。
- **`04-retrieval-matrix.json` 的 `started_at` 与 `finished_at` 相同**：runner 的
  时间戳记录缺陷（两个都写在了收尾时刻），跑完后已在 `retrieval_runner.py` 修正。
  该文件**未回改**（不回改证据）。**权威起始时刻取 `04b-run-log.txt` 首行
  `09:46:22`，加上 `wall_seconds=465.4` 可得结束时刻**。
- **`auto_detect_filters` 关不掉**：它是服务端设置，请求级不可控。所以本刀能测的
  "两种模式"就是 `skip_query_expansion` 开/关两档，**不是**"agentic 全开 vs 纯向量"。

## 6. 复跑命令（A12）

```bash
# 全量矩阵（真引擎；12 query × 2 档 × 3 次 = 72 次调用，本次 wall 465.4s）
cd /mnt/d/Projects/domainAgentECE/ece
ECE_CONTENT_ENGINE=onyx uv run python \
  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/retrieval_runner.py \
  --eval data/eval/retrieval/consulting-demo.json \
  --out  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/evidence/04-retrieval-matrix.json

# 由 04 机算 05（不再打引擎）
python3 /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/summarize_matrix.py \
  --matrix /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/evidence/04-retrieval-matrix.json \
  --out    /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/evidence/05-hit-repro-summary.txt
```

> 注：`retrieval_runner.py` 依赖 `OnyxContentEngineAdapter.search(..., skip_query_expansion=)`
> 这一形参——即本刀步骤 2 的接入物。若不接入，复跑命令会直接 `TypeError`，
> 这本身就是"插件确实接上了"的负向证明。
