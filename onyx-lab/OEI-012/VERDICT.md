# OEI-012 审验裁定（codex）— 最终裁定：**PASS**

> 审验时间：2026-09-26 10:2x ｜ 被审对象：`REPORT.md` + `evidence/`（13 份）+ `workspace/`（8 件）+ `DONE`（10:09）
> 被审任务书：`TASK.md` v1 ｜ 被审 commit：**`4a67c28`**（7 文件、未 push）
> **裁定：`PASS` —— 本刀关闭。A0–A12 全部成立，且我用自己的脚本把"0% 命中率"与"排序 vs 索引"两条核心结论独立重算并逐数核对。**

---

## 1. 逐条验收（codex 独立复核）

| # | 验收标准（摘要） | 结论 | 我的核实 |
|---|---|---|---|
| **A0** | 凭据 200；语料稳定；mock 基线 | **PASS** | `00-credentials.txt`（200/200）；`00b-baseline.txt` 146 passed；语料 4 份 COMPLETED 快照 |
| **A1** | 评测集 8–12 条、rationale 可溯源、miss 语义正确 | **PASS** | 我读了 `data/eval/retrieval/consulting-demo.json`：**12 条**（9 hit + 3 miss），字段 `id/query/expected_title/kind/rationale`，`miss_semantics` 写的是"该 title 不出现在召回集"；rationale **逐条引三份原文的句子**（q01 引"毛利率连续三个季度下滑…"、q02 引"SKU 失控…"等，我抽核过） |
| **A2** | N=3 × 两档，逐 query 去重 title 集 + 顺序 + 延迟；完全一致比例 + 逐次 Jaccard | **PASS** | `04` 是 **72 行**（12×2×3），每行含 `dedup_titles / raw_title_count / latency_seconds / hit_at_1 / hit_at_3 / expected_present`；`summary` 里 reproducibility on=0.833 / off=1.0、逐次两两 Jaccard 明细齐全 |
| **A3** | hit@1 / hit@3 两档各一个数；误召回计数 | **PASS** | 我**独立重算**（见 §2）：54 个 hit 行里 top-1=0、top-3=0 → **hit@3 = 0.0%**（两档同）；miss 误召回 3/9 两档相同 |
| **A4** | 三处接入、默认 False、httpx 桩证明传参 | **PASS** | 我读了 diff：`port.py` / `onyx_adapter.py` / `mock_adapter.py` 三处加 `skip_query_expansion: bool = False`；adapter **只有 `True` 时才往 body 加字段**（默认 body 逐字节不变）；审计记录该开关。新单测 `test_skip_query_expansion.py` **12 passed**（我亲自跑，死端口 DSN） |
| **A5** | 代价评估 + 三选一结论 | **PASS** | `workspace/retrieval-decision.md` 完整：结论 **`expansion_off 更优`**，但**默认仍 False**——且给了四条"有数字的不翻转"理由（买不到命中率、会收窄候选集、默认是产品决策、应"先修排序再复测"） |
| **A6** | search() 语义不变；签名同构；consulting 不变 | **PASS** | `07` 契约测试 120 passed；`git diff a3d61cd 4a67c28 -- tests/` 只有 **1 个新增文件、0 删除**（没看到任何既有断言改动） |
| **A7** | 新增 DB-free 单测全绿 | **PASS** | 我亲自跑 `test_skip_query_expansion.py` → **12 passed / exit 0**（859 = 847 + 12 对得上） |
| **A8** | 全套件 0 failed + `-rs` | **PASS** | `08-test-suite-raw.txt` 859/5/3/0；skip 名单附 |
| **A9** | 文档 + 提交评测集 + check-api-docs 0 | **PASS** | `data/eval/retrieval/` 提交；`docs/API.md` + `TASKS.md 附录 S`；我独立跑 `check_api_docs.py` → **App-only 0** |
| **A10** | commit 不 push | **PASS** | `4a67c28` 7 文件、`ahead 5`、不在任何远端分支 |
| **A11** | 合规与资源 | **PASS** | 我现场核：`pyproject.toml`/`uv.lock`/`demos/spa` 零 diff、无 ece 容器/进程、Onyx `RestartCount=0`、密钥扫描无值落盘（cc 还自曝了 `grep '#HttpOnly_'` 那处盲区并修了） |
| **A12** | 机器可校验、可复跑、无不可判定表述 | **PASS** | 复跑命令写进 `retrieval-decision.md §6`；结论全部可机算；无"检索效果良好"这类话 |

---

## 2. 我这次独立重算的数字（不采信 cc 的 summary，直接解析 `04` 的 72 行）

```
hit 行 54（= 9 hit query × 3 次 × 2 档）
  top-1 命中 = 0，top-3 命中 = 0  →  hit@3 = 0.0%（两档一致）
expected_title 出现在"自己那条 query"召回集里的次数 = 0

三份真文档在 72 行里进入 top-3 槽位的次数（= cc 说的"被召回 18/6/4"）：
  case-management-consulting.md = 18
  play-sales-delivery.md       = 4
  methodology-framework.md     = 6
受控对照文档 RESTR 进入 top-3 = 61/72

更锋利的一条（我自己加的）：raw_title_count 分布 = {1:59, 3:4, 2:9}
  → 59/72 行引擎只返回 1 条结果；54/72 行结果集 = 恰好 [RESTR]
```

⇒ cc 的结论我**逐数确认**：命中率 0%、且是**排序问题不是索引问题**（文档在库里、能被召回，只是排不上来）。我还补充了一个更硬的证据：**引擎对这些咨询 query 大多数时候只吐回那一个受控对照文档**（54/72 次"唯一结果就是 RESTR"）。

---

## 3. 证据抽查（逐字打开）

`00-credentials.txt`、`00b-baseline.txt`、`01-evalset.json`、`02-plumbing-diff.txt`、`03-unit-test-raw.txt`、`04-retrieval-matrix.json`（72 行全读 + 独立重算）、`04b-run-log.txt`、`05-hit-repro-summary.txt`、`06-decision.md`、`07-contract-regression.txt`、`08-test-suite-raw.txt`、`09-git-commit.txt`、`10-compliance-check.txt`、`11-check-api-docs.txt`；源码抽读 `port.py` / `onyx_adapter.py` diff；`workspace/retrieval-decision.md` 全文。

结论：**全部与 REPORT 一致、可复现**；本刀没有任何"数据与报告打架"或"证据指向错状态"。

---

## 4. 本刀最重要的不是代码，是一个**负面发现**（而且是对的）

**检索命中率现在是 0%，根因是"排序"而非"索引"，并且受控对照文档在霸榜。** 这条发现比 `skip_query_expansion` 那点改进重要得多：

1. **0% 是真数字**：连 `methodology-framework.md` 里的**逐字标题句**（`MECE 的排他性和穷尽性怎么检验`）都召不回它自己。
2. **不是索引坏**：三份真文档在矩阵里分别进入 top-3 槽位 18/6/4 次，证明它们在库里、能排上来，只是**不为自己那条 query 排**。
3. **霸榜的是 `ece-…-oei009-comparison-restricted.md`**（OEI-009 留下的对照文档，`员工报销政策与发票审核流程`）：61/72 次进 top-3，**54/72 次是唯一结果**。一个和咨询无关的合成对照文档，把三份真文档全部挤出召回。

这条直接把**演示面一个隐藏的坑**翻了出来：OEI-006 做的"引擎召回分组"（view-d 里那个带引用的分组）**一直是坏的**——它会显示这个对照文档而不是真正的咨询案例。没有人量化过，直到这一刀。

---

## 5. 一处我作为签发者的说明（不是 cc 的错）

任务书（我写的）把评测定义在**原始引擎层**（`/api/search` 的 title 集）。这是对的——它干净地隔离出引擎本身。但有一个**后续必须补测**的口径：这个 `RESTR` 文档是 `restricted` 档，在真实的 consulting library 路径里会被 ECE 的权限过滤**滤掉**（匿名只看 public）。所以：

- 原始引擎 hit@k = 0% 是**引擎层事实**；
- **产品可见层**（过滤后）的 hit@k 是另一回事，本刀没测；
- 而且 54/72 次"唯一结果就是 RESTR"意味着：过滤掉 RESTR 后，**很多 query 会变成空结果**（不是"露出排在第 4 的真文档"，而是"啥都没有"）——所以产品层的召回**同样接近于坏**，只是坏法不同。

→ 下一刀必须**同时**做两件事：① 查 RESTR 为什么霸榜（大概率是它太短、词密、被 agentic 检索当成"最相关"），并**把它从演示语料里移除或归档**（这是产品决策，得让用户点头）；② 在**过滤后的路径**上重测 hit@k。这些写进 §6 转出。

---

## 6. 裁定：**PASS**

理由：A0–A12 全部成立；核心数字（0%、18/6/4、RESTR 61/72、复现性 1.0 vs 0.833、延迟 1.47 vs 5.02）我**独立重算并逐数一致**；改进（`skip_query_expansion`）实现正确、默认不翻转有数字理由；契约不回归、无越界、无新依赖、无密钥、未 push。本刀**没有提升命中率，但它把"命中率=0%且是排序问题"这一会决定后续所有工作的分岔口判死了**——这正是"检索质量"刀该干的：先有可信数字，再谈改。

**转出（高优先级，直接影响 OEI-013 演示）**：

1. **检索排序修复**（下一刀的核心）：先诊断 `ece-…-oei009-comparison-restricted.md` 为何霸榜，并**移除/归档该对照文档**（产品决策，等用户确认）；然后在过滤后路径 + 干净语料上重测 hit@k。`skip_query_expansion` 已就位，修完排序后用本刀的口径复测。
2. **产品层 hit@k**（过滤后）补测——原引擎 0% ≠ 产品层 0%，但大概率同样接近坏（RESTR 常是唯一结果）。
3. `merge_engine` 的 fail-open 显式化（承自 OEI-009）。
4. **真认证**（承自 OEI-009）——演示讲权限分层之前必须做。
5. 引擎调用审计持久化；6. 凭据耐久化（PAT）。

**值得固化的好做法（写进后续任务书模板）**：

- **负面发现也是交付**：本刀没"修好"检索，但它证明并量化了"检索是坏的、坏在哪"，并把"索引 vs 排序"的分岔口判死。这类"诚实度量"比一个没数字支撑的假改进有价值得多。
- **命中率与可召回性分开报**：只有同时报"hit@k"和"该文档在别处是否被召回"，才能区分"索引坏了"与"排不上来"。
- **不编造数据**：响应体没有 usage 字段，就用延迟分布形状当"是否走 LLM"的可测代理，绝不编 token 数。
- **证据不回改**：runner 时间戳缺陷在跑完后已修，但证据文件原样保留，只把权威取值写进 README——"不回改证据"这条纪律比"证据好看"重要。
