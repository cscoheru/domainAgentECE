# OEI-012 REPORT — 检索质量：召回评测集 + 召回可复现 + 一项实测改进

> 任务书：`onyx-lab/OEI-012/TASK.md`（v1，A0–A12 共 13 条验收）
> commit：`4a67c28`（本地，**未 push**）
> 日期：2026-09-26
> 证据：`onyx-lab/OEI-012/evidence/` ｜ 决策：`workspace/retrieval-decision.md`

---

## 0. 一句话结论

**把"检索好不好"变成了数字，而数字说的是一件我们之前不知道的事：**
`/api/search` 的召回命中率是 **0%**（hit@1 = hit@3 = 0%，两档皆然），
**且这是排序问题不是索引问题** —— 三份目标文档在同一批实验里都被实际召回过，
连**逐字查询**都召不回自己的原文。

本刀**没有**修好召回，但交付了三样东西：① 一份可复跑的 12 条评测集；
② 两档（query expansion 开/关）在真引擎上的命中率 + 复现性 + 延迟实测；
③ 一项**实现并实测**的改进 —— `skip_query_expansion` 接入（三处，默认 `False`）。
实测结论：**`expansion_off` 更优**（复现性 1.000 vs 0.833、延迟中位数 1.47s vs 5.02s、
不走 LLM），**但命中率两档同为 0%，所以默认值不翻转**。

---

## 1. 验收对照（A0–A12）

| # | 验收 | 结论 | 证据 |
|---|---|---|---|
| A0 | 凭据 200；语料稳定（4 份）；mock 基线单测 | ✅ 200/200；4 份 COMPLETED 快照；基线 **146 passed** | `00-credentials.txt`、`00b-baseline.txt` |
| A1 | 评测集 8–12 条，含 rationale，miss 语义正确 | ✅ **12 条**（9 hit + 3 miss），rationale 逐条引三份原文 | `data/eval/retrieval/consulting-demo.json`、`01-evalset.json` |
| A2 | N=3 × 两档，逐 query 去重 title 集 + 顺序 + 延迟；完全一致比例 + 逐次 Jaccard | ✅ 72 次调用；含**逐 query 逐次两两 Jaccard** | `04`、`05`、`04b-run-log.txt` |
| A3 | hit@1 / hit@3 两档各一个数；误召回计数 | ✅ 两档均 **0.0% / 0.0%**；误召回 3/9 两档相同 | `05` |
| A4 | 三处接入，默认 False，httpx 桩证明传参 | ✅ port/onyx/mock；**线上请求体逐字节不变**；桩抓真实 body | `02`、`03` |
| A5 | 代价评估 + 三选一结论 | ✅ 结论 **`expansion_off 更优`**；默认仍 False（有数字理由） | `workspace/retrieval-decision.md`、`06` |
| A6 | search() 空/错/审计语义不变；签名同构；consulting 不变 | ✅ 既有契约测试 **120 passed**；tests/ 删除行 **0** | `07` |
| A7 | 新增 DB-free 单测全绿 | ✅ **12 passed**（死端口 DSN 下）；扫描器有牙 | `03` |
| A8 | 全套件 0 failed，`-rs` 附 skip 名单 | ✅ **859 passed / 5 skipped / 3 deselected / 0 failed** | `08` |
| A9 | 文档 + `data/eval/retrieval/` 提交；check-api-docs 仍 App-only 0 | ✅ API.md + 附录 S；**App-only: 0**，exit 0 | `11` |
| A10 | commit（不 push）+ 短 hash + 文件清单 | ✅ `4a67c28`，7 文件，ahead 5 未 push | `09` |
| A11 | 合规：未碰 Onyx 配置；RestartCount=0；无新依赖；demos 零 diff；密钥；内存快照；无残留 | ✅ 全部零 diff；RestartCount=0 ×9；cookie 扫描 0 泄漏 | `10` |
| A12 | 机器可校验、可复跑、无不可判定表述、无截图 | ✅ 复跑命令见决策文档 §6；全部数字可机算 | 全部 |

---

## 2. 核心发现（按重要性排序）

### 2.1 召回命中率 = 0%，且这是排序问题（A3）

9 条 hit query × 3 次 × 2 档 = **54 次，目标文档一次都没进前 3**。

**排除了"索引坏了"这个解释**（否则 0% 是废话）：

| 对照 | 数字 |
|---|---|
| `case-management-consulting.md` 在矩阵内被召回 | 18 次 |
| `methodology-framework.md` | 6 次 |
| `play-sales-delivery.md` | 4 次 |
| 受限对照文档 | 61 次 |

三份目标文档**都在库里、都能被召回**，只是**排不上来**。最锋利的一条：
q05 的 query `MECE 的排他性和穷尽性怎么检验` 是 `methodology-framework.md` 里的
**逐字标题句**，两档都召不回它（`expansion_on` 给 `CASE+RESTR+PLAY`，
`expansion_off` 给 `CASE+RESTR`）。

> 这条把后续所有工作的分岔口**判死了**：要修的是**排序**，不是重建索引、
> 不是换 embedding。`skip_query_expansion` 对此毫无帮助。

### 2.2 关掉 query expansion 让召回**完全可复现**（A2）

| 档位 | 3 次完全一致 | 两两 Jaccard 均值 |
|---|---|---|
| `expansion_on` | 10/12 = **0.833** | **0.926** |
| `expansion_off` | 12/12 = **1.000** | **1.000** |

不稳定的两条（q09、q11）症状完全相同：**只有第 1 次不同**，后两次彼此一致
（r1~r2 = r1~r3 = 0.333，r2~r3 = 1.0）。这与延迟上观察到的冷启动首调同源 ——
`expansion_on` 的第一次调用走的是不同路径。关掉 expansion，两条都稳定了。

### 2.3 改进实测：`expansion_off` 三轴更优（A4/A5）

| 轴 | `expansion_on` | `expansion_off` |
|---|---|---|
| hit@1 / hit@3 | 0.0% / 0.0% | 0.0% / 0.0%（**持平**） |
| 复现性 | 0.833 | **1.000** |
| 延迟 median / mean | 5.02s / 10.67s | **1.47s / 2.25s**（3.41× / 4.74×） |
| LLM 往返 | **36/36 次**（无一次 <2s） | **2/36 次**（34 次 <2s） |

**结论 `expansion_off 更优`**；**默认值保持 `False`**。
理由（数字）：翻转能买到复现性与延迟，**买不到命中率**（两档同 0%），
却会改变所有调用方行为，且让候选集**变窄**（q05 3→2、q11 3→1）。
正确顺序是**先修排序，再复测**。详见 `workspace/retrieval-decision.md` §4。

---

## 3. 实现（改了哪些代码）

`ContentEnginePort.search()` 新增 `skip_query_expansion: bool = False`，三处接入：

| 文件 | 改动 |
|---|---|
| `src/ece/connectors/onyx/port.py` | Protocol 声明 + 语义文档 |
| `src/ece/connectors/onyx/onyx_adapter.py` | **真发到请求体**；审计记录该开关 |
| `src/ece/connectors/onyx/mock_adapter.py` | 同构接受 + 审计记录 |

两个刻意的设计决定：

1. **`False` 时字段整体不发送**（不是发 `false`）—— 默认路径的请求体与改动前
   **逐字节一致**，老引擎不会看到未知字段。有单测断言这一点。
2. **`mock` 不装作有行为差异** —— 它是与语料无关的固定 fixture，
   为它编一个"关掉 expansion 就少几条"的行为就是造假。mock 只负责同构 + 审计可见。

**扫描器有牙**：`workspace/mutation_check.sh` 把真正的接线挖掉 → 必须变红 →
还原 → 必须变绿。三段都记进 `03-unit-test-raw.txt`。

---

## 4. 局限（写在明处，别让后面的刀误用）

- **样本小**：12 query、单一语料（项目 1 的 4 份文档）、N=3。足以**定性**
  （0% vs 0%、1.000 vs 0.833），不足以给置信区间。
- **冷启动污染**：每档第 1 次调用显著偏慢（off 27.3s、on 46.6s）。原始数据不剔除，
  但结论一律以 **median** 为准。
- **测量用 client timeout = 180s**（产品默认仍 60s 未改）。不放大它，
  冷启动的 `expansion_on` 会被 60s 截断成"失败"，把"慢"错记成"没数据"。
- **LLM token 代价未量化**：`/api/search` 响应体无 usage 字段，引擎日志不吐 token 数。
  本刀用**延迟分布形状**作为"是否走 LLM"的可测替代，**不编 token 数**。
- **`auto_detect_filters` 关不掉**（服务端设置，请求级不可控），所以"两种模式"
  就是 `skip_query_expansion` 开/关两档，**不是**"agentic 全开 vs 纯向量"。
- **`04-retrieval-matrix.json` 的 `started_at` == `finished_at`**：runner 时间戳记录缺陷
  （都写在了收尾时刻），跑完后已在 `retrieval_runner.py` 修正；**该证据未回改**
  （不回改证据）。权威起始时刻取 `04b-run-log.txt` 首行 `09:46:22`。

---

## 5. 资源与合规（收尾三查）

- **内存如实记录**：72 次调用期间 **swap 打到 `SwapFree=0 kB`**（耗尽），
  `MemAvailable` 一度降到 ~873 MB。这是 OEI-009 已警告过的 Onyx 栈既有压力，
  被 ~8 分钟连续 agentic 检索放大。**未归因为本刀泄漏**（runner 是一次性 CLI 已退出；
  除临时 PG 外未加容器，且快照取自拆除之后）。**没有**为回收而停任何 Onyx 容器。
- **收尾三查**：无残留进程（按 `/proc` cgroup + cmdline 归属，非 `pgrep` 文本匹配）；
  `ece-*` 容器 **0** 个；9 个 `onyx-*` 全部 `RestartCount=0`。
- **密钥**：cookie 只读使用，未刷新/未改写/未索取；**0 个 cookie 值出现在任何产出物**。
  扫描器**有牙证明**：用合成 canary 验证检出机制（真值绝不落盘），
  并记下第一版扫描 `grep -vE '^#'` 把 `#HttpOnly_` 行一并滤掉导致
  "报 0 tokens 却看起来像通过"的**盲区**——实测旧过滤器 0 个 token、新过滤器 1 个。
- **未碰**：Onyx 配置 / compose / `.env` / `demos/` / 迁移 / consulting 库 —— 全部零 diff。
- **未 push**：`ahead 5`，全部 commit 留在本地。

---

## 6. 复跑

```bash
# 1) 评测矩阵（真引擎，72 次调用，本次 wall 465.4s）
cd /mnt/d/Projects/domainAgentECE/ece
ECE_CONTENT_ENGINE=onyx uv run python \
  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/retrieval_runner.py \
  --eval data/eval/retrieval/consulting-demo.json \
  --out  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/evidence/04-retrieval-matrix.json

# 2) 由 04 机算 05（不打引擎）
python3 /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/summarize_matrix.py \
  --matrix /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/evidence/04-retrieval-matrix.json \
  --out    /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/evidence/05-hit-repro-summary.txt

# 3) 扫描器有牙 / 新单测 / 契约 / 全套件
bash /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/mutation_check.sh
cd /mnt/d/Projects/domainAgentECE/ece && ECE_CONTENT_ENGINE=mock \
  uv run pytest tests/unit/test_skip_query_expansion.py -v
bash /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/fresh_db_chain.sh
bash /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/compliance_check.sh
```

---

## 7. 转出给下一刀

1. **排序问题是最大遗留**。hit@k = 0% 而文档明明可召回；唯一请求级开关就是
   `skip_query_expansion`。要真修排序得动 Onyx 服务端配置或换检索路径 ——
   **超出本刀授权**（本刀明令不碰 Onyx 配置）。建议下一刀先定性排序成因。
2. **`skip_query_expansion` 只在连接器层**，未提升到 ECE HTTP API
   （`docs/API.md` §10 有显式说明）。这是刻意的。
3. **复测时机**：排序修好后，用本刀的口径（`retrieval_runner.py` + 评测集）
   重新测两档 —— 那时复现性/延迟优势才有意义。
