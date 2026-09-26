# OEI-011 审验裁定 #1（codex）— 裁定：`CONTINUE`（BLOCKED 成立；任务书升 v1.1；不判返工）

> ⚠️ **最新裁定在文件末尾的「审验裁定 #2」：`PASS`（c30e50e 交付，A0–A14 全部成立）。**

> 审验时间：2026-09-25 21:2x ｜ 被审对象：`REPORT.md`（BLOCKED，21:14）+ `evidence/`（5 份）+ `workspace/`（6 件）
> 被审任务书：`TASK.md` **v1** → 已修订为 **v1.1** ｜ 仓库状态：`ece` HEAD 仍是 `a463658`、**零改动**、未 push、**未建 `DONE`**
> **裁定：`CONTINUE` —— cc 的停手完全正确；矛盾是我的任务书造成的，改任务书，不判 cc 任何返工。**

---

## 1. 我核实了什么（独立复核，不采信自我描述）

| 项 | 我的核实 | 结论 |
|---|---|---|
| 矛盾是否存在 | 我读全了 `tests/unit/test_consulting_seed_count.py`：`test_type_distribution_matches_documented_targets` 的 `expected` 六项之和 **`10+10+6+4+4+2 = 36`**，等于当前总数，且循环里是 **`assert actual[t] == n`**（不是 `>=`） | **矛盾成立** |
| 增量是否必然打破它 | §6 A4 要求 `industry_note ≥6`（现 2）、`risk_check ≥6`（现 4）→ **必然新增** → 该类型的 `actual[t]` 必 > `expected[t]` → `==` 必假 | **必然成立**（cc 的 `00-blocked-contract-conflict.json` 三个场景与此一致） |
| 该处是否真被冻结 | §3.4/§8/A9 的授权清单里只有 `test_consulting_documents.py:263`、`:315`、`test_consulting_engine_merge.py:339` 三处 | **确实未授权** |
| cc 的盘点是否完整 | 我重复了它的三条命令（`grep -rn '\b36\b' tests/`、`grep -rn 'Counter(' tests/`、`grep -rn 'client_industries' tests/`），并逐个看了命中处：**共 6 处与语料规模/分布耦合**，其中只有第 [6] 处会被增量打破；`test_consulting_service.py:46` 的右值是**从目录算出来的**（不硬编码）、`limit=5`/`limit=3` 的分页断言在增量后仍成立、facets 只钉**键集合**并仅要求每项非空 | **盘点完整，且比我的 §1.5 更全** |
| 仓库是否真的零改动 | `git log --oneline -2` = `a463658` / `a884d41`；`git status --porcelain`（排除开工前就有的噪声）= 空 | **零改动成立** |
| 停手是否符合协议 | TASK §3 前言明写"发现契约与实测不符 → 停手 + 写 REPORT + 等 codex 对齐"；cc **没有**自行放宽授权、**没有**改断言、**没有**建 `DONE`、**没有**留下半成品 | **完全符合，是正确动作** |

**额外认可**：cc 不是"卡住就交白卷"——它在**不写仓库**的前提下把整套执行计划做了出来并自检（`workspace/draft_*.json` + `draft_plan.py`）：24 条标注、9 条新增、`total_after=45`、**A1"除 `client_industry` 外字段逐字节相同"= 36/36 True**、A2 违规 0、A4 五项全达标、A7 无 0 匹配值 True。这些资产我核过结构，**可以继续用**（见 §3 第 3 条）。

---

## 2. 缺陷归因：这次是我的任务书写错（第 3 次同类）

- **直接原因**：§1.5 那张表我写成 **"我逐个核过（本刀只允许动 §3.4 点名的三处）"**，但当时我只 grep 了 `36` 与计数相关模式，**没有读全 `test_consulting_seed_count.py`**，于是漏掉了这个文件里**第二严格**的断言（六种类型的精确 `==`）。
- **后果**：A4（要求增量）与 A9（冻结断言）互斥，任务书**不可执行**。cc 停在第一步是对的；如果它"灵活处理"（自己把那条断言改成 `>=`），就会变成**擅自放宽授权**——那更糟。
- **同类历史**：`OEI-008` §7（`tests/**` 只许新增 vs 回归改造自相矛盾）、`OEI-009` §1.2（把 `document_id` 当成搜索响应字段）+ §7（白名单漏 `identity/**`）、现在 `OEI-011` §1.5。**根因一致：我在任务书里把"看起来核过"当成"已核过"，且写"清单完整"时没附可复现的盘点命令。**

---

## 3. 处置（已做完，不需要 cc 返工）

1. **任务书升到 v1.1**（`TASK.md`）：
   - 顶部加 **v1 → v1.1 修订块**（说明矛盾成立、归因在我、不判返工、草稿可继续用）；
   - §1.5 表格**补齐第 [6] 处**，并把标题从"三处硬钉死"改为"**四处硬钉死**"，同时**把三条盘点命令写进任务书**（以后"清单完整"必须有命令支撑）；
   - §1.5 增加"已确认不受影响"的清单（`service:46`、分页断言、facets 键集合、`suggest_metadata` 单测）；
   - §3.4 授权**四处**，并给出统一原则：**KC-001 的分布是下限基线，不是"永远不许增长"**；第 [6] 处的六个 `==` → `>=`（保留六个数作为**每类型下限**），**docstring 同步改写**（原文的"（exact）"不再成立），**不许删掉这条测试**（它的原意"别把某一类悄悄做没"必须留住）；建议补一行 `sum(expected) <= len(objects)` 自洽断言；
   - **`docs/demo-platform/CONSULTING_CONTEXT_KERNEL_KC001_TASK.md` 不许改**（历史契约），新分布写进 `TASKS.md 附录 Q`；
   - §5 步骤 5 增加第 2 步：**改完后重跑盘点命令**并落盘 `09b-assertion-inventory-after.txt`（证明没有第七处）；
   - §6 **A9 重写**为"四处 + 步骤 0.1 一处"，并要求附 `git diff` **与**改后盘点输出；
   - §6 **A5 加注**：草稿里那两条 `kc001_schema::…` 名义失败是**夹具/路径造成的假失败**，最终证据必须来自**真实 seed 文件**上的全绿原始输出。
2. **本文件（裁定 #1）= cc 的心跳信号**：`CONTINUE`。
3. **cc 的下一步**：**不要删任何东西**（本来就没有 `DONE`），重读 `TASK.md` v1.1，从**步骤 1**继续（草稿资产直接复用，但落盘与取证必须在真实文件上重做一遍）。

---

## 4. 未决 / 待第三轮判定的点（先记下来，免得后面跑偏）

1. **`cross_industry ≥10` 的实现方式**：cc 的草稿把不特定行业的 methodology / proposal_play / deliverable_template / risk_check 标为 `cross_industry`。审验时我要逐条看依据列**是否真的能从对象自身文本定位**（A3），不接受"为了凑到 10 而批量标注"。
2. **行业词的"多值"语义**：允许一个对象有多个行业（现有 `case` 里就有多值）。审验时会检查：`industry_note` **恰好 1 个**具体行业这一条是否被严格执行。
3. **`facets` 无计数**：本刀不改 `_compute_facets()`（它只聚合值集合），所以"每个值命中 ≥2"必须靠 `/library?client_industry=<v>` 的 `total` 来证明——这是 A7/A8 的取证方式，**不要**顺手给 facets 加计数（那会改 `/facets` 的响应形状，触犯 A10）。
4. **`metadata.py` 词表新增的影响面**：`ALLOWED_INDUSTRIES` 是上传路径 `_validate()` 的白名单 → 加 `cross_industry` 后，**上传也能标通用**（这是想要的效果）；但 `docs/API.md:662` 那句"必须落在既有 36 个种子对象的取值集合内"措辞要一并改准，别留下"词表=种子取值"的误导。

---

## 5. 给用户的一句话

`OEI-011` 在第一步就停住了，**原因是我签的任务书自相矛盾**（有一处类型分布的精确断言被我漏在授权清单外）；cc 停手写 `BLOCKED`、零改动、没建 `DONE`，**行为完全正确**。我已把任务书修到 v1.1（补齐第 6 处断言并说明"KC-001 是下限不是上限"），cc 可直接从步骤 1 继续。**这不是 FAIL，是任务书返修。**

---

# OEI-011 审验裁定 #2（codex）— 最终裁定：**PASS**

> 审验时间：2026-09-25 22:2x ｜ 被审对象：`REPORT.md` + `evidence/`（22 份）+ `workspace/`（11 件）+ `DONE`（22:15）
> 被审任务书：`TASK.md` **v1.1** ｜ 被审 commit：**`c30e50e`**（9 文件，未 push）
> **裁定：`PASS` —— 本刀关闭。A0–A14 全部成立，且核心数字我用独立脚本重算过一遍。**

---

## 1. 逐条验收（codex 独立复核）

| # | 验收标准（摘要） | 结论 | 我的核实 |
|---|---|---|---|
| **A0** | 步骤 0 两笔转出 | **PASS** | `test_s32_assembly.py` 的闭集断言已按"断言真正的不变量"改写（`kind` 非空字符串 + `decision ∈ {allowed,denied}` + `reason` 非空）——正是 v1.1 给的二选一之一，且 REPORT **明确声明了"此断言由本刀解冻"**；`docs/DATA_MODEL.md:252` 的 `idx_memories_scope_owner` 已订正为 `(scope, owner_ref)`，**与迁移 `0010_memories.py:86` 逐字一致**（我直接比对了两处） |
| **A1** | 既有 36 个对象只加了 `client_industry` | **PASS** | 我**自己写脚本**对比 `git show a463658:…` 与当前文件：36 个既有 id 全在、无缺、无改；**"除 `client_industry` 外全部字段"逐个比较 → 差异 0 条**。另：种子文件 sha256 = `b6e7045b…`，与 REPORT 声明一致（脚本还做了序列化往返证明，比我要求的更严） |
| **A2** | 覆盖率 + 词表 + 类型禁令 | **PASS** | 我重算：**空 `client_industry` = 0**；**`case` / `industry_note` 带 `cross_industry` = 0**；所有值 ∈ 词表（11 个）。cc 的扫描脚本还**注入 3 个故障自证"有牙"**（三项分别报 1,1,1）——这条我认可并打算固化到后续任务书 |
| **A3** | 依据可查 | **PASS** | `01-industry-annotation-basis.json`：24 条，每条含 `依据字段 / 依据原句 / 扫描范围 / basis_quote_is_substring_of_own_fields`，`unlocatable_basis=[]`、24/24 true；其中一条还**如实记下 loose 扫描的假命中**（`technology:ai` 其实是 `supply_chain` 的子串 `ch-ai-n`）。**新增 9 条**在 `03` 里各有 `rationale`，且我逐条查了行业锚点：`制造业/物流/医疗健康/能源/科技（数据平台）/保险（核保）` **都能在各自 title/summary 里定位**；`case-public-sector-service-window-012` 的锚点是 **"事业单位"**（公共部门），成立 |
| **A4** | 覆盖目标 | **PASS** | 我重算：总数 **45**（36+9）；六个类型 = case 13 / methodology 10 / proposal_play 6 / deliverable_template 4 / risk_check **6** / industry_note **6**；**10 个具体行业各 2**；`cross_industry` 对象 **26** —— 五项阈值全部达标 |
| **A5** | 内容纪律 | **PASS** | 我在**真实 seed 文件**上独立跑 `test_consulting_seed_schema.py` / `test_consulting_seed_discipline.py` / `test_consulting_seed_count.py` / `test_consulting_service.py` → **24 passed / exit 0**（即 45 条全过 schema + 中文占比 + 客户脱敏 + 合成标记 + 禁竞品名）。v1.1 里我担心的"草稿假失败"没有出现在最终证据里 |
| **A6** | 词表只加 `cross_industry` 一项 | **PASS** | `metadata.py` diff 只有那一个值 + 一段语义注释；**没有第二个新值**；`docs/API.md:687/:732/:738` 措辞已改准（"必须落在词表内（`ALLOWED_*`，由种子对象取值集合派生）"、"11 个 = 10 个具体行业 + `cross_industry`"），不再有"词表=36 个种子取值"的误导 |
| **A7** | facets 可用（无 0 匹配） | **PASS** | 我**不依赖 cc 的脚本**，直接 `ConsultingCatalog.from_seed_path()` 在进程内算：`facets.total=45`、`client_industries` = 10 个具体行业 + `cross_industry`；**每个值 `search(client_industry=[v]).total` 都 = 2（cross=26），没有任何 <2 的值** |
| **A8** | 过滤实测 | **PASS** | 同上（我走的是目录层，等价于 `/library?client_industry=<v>` 的静态侧）；另有 `/objects/{id}` 抽样证据 |
| **A9** | 数量断言**有界**解冻 | **PASS** | `git diff --stat a463658 c30e50e -- tests/` = **4 文件 / +41 / −9**，与我授权的**四处 + 步骤 0.1 一处**一一对应（`documents.py` 两处、`engine_merge.py` 一处、`seed_count.py` 一处六个 `==`、`s32` 一处）；`09b-assertion-inventory-after.txt` 用**改后重跑的三条盘点命令**证明"没有第七处"；REPORT 明写"除此之外零断言改动"；第 [6] 处按我要求保留了测试、改成下限、docstring 同步改写 |
| **A10** | 既有契约不回归 | **PASS** | `10-contract-regression.txt` 三方对照（pre-cut 源码 / HEAD 源码 / **真实运行时的响应键**）：`FacetsResponse` / `KnowledgeObject` / `LibraryResponse` **键集合 identical: True**，只有**值集**变了（`client_industries` 10→11 个值、`total` 36→45）——正是本刀目的。全套件原始输出 `847 passed / 5 skipped / 3 deselected / 0 failed`，与 §1.7 基线一致 |
| **A11** | 文档 | **PASS** | `docs/API.md §11/§12`（45 的来历 + 下限契约 + 11 个词表值）、`TASKS.md 附录 Q`（含"24 条全是 `cross_industry` 且依据可机检"的说明）、`docs/DATA_MODEL.md` 列序订正。我**独立跑** `scripts/check_api_docs.py` → `Common 26 / App-only 0` |
| **A12** | 提交 | **PASS** | `c30e50e` 存在、9 文件、工作区干净、`pyproject.toml`/`uv.lock` **零 diff**、`ahead 3`、**不在任何远端分支** |
| **A13** | 合规与资源 | **PASS** | `demos/spa` 零 diff（`git diff --stat` 空 → 前端逐字节未变，符合"数据驱动、不需要改"）；无 `ece-*` 容器、无残留 pytest/uvicorn/alembic；Onyx 容器 `RestartCount=0`；密钥值扫描零命中；未 push |
| **A14** | 证据纪律 | **PASS** | 全部为 JSON / 哈希 / 计数 / 原始响应；无"内容更丰富"这类不可判定表述；无"用户截图" |

---

## 2. 我这次独立做了什么（不采信自我描述）

- **重算种子数据**（自己的脚本，不经 cc 的中间产物）：总数 45、类型分布、每行业计数、空值数、类型禁令违规数、**A1"其余字段逐条相等"36/36**、新 id 清单、旧 id 无缺失。
- **进程内复算 facets 与过滤命中数**（不启服务、不用 cc 的脚本）：每个行业值命中 2，无 0 匹配值。
- **独立跑测试**：4 个 consulting 相关单测文件 → 24 passed；`check_api_docs.py` → App-only 0。
- **逐字比对关键文档/迁移**：`DATA_MODEL.md:252` vs `0010_memories.py:86`；`metadata.py` diff；`docs/API.md` 三处措辞。
- **现场**：`git log/status`、`branch -r --contains HEAD`、`--stat` 改动面、容器/进程/`RestartCount`、密钥扫描、种子 sha256 对照 REPORT 声明。

---

## 3. 证据抽查（逐字打开）

`00-step0-transfer-fixes.txt`、`01-industry-annotation-basis.json`、`02-existing-36-unchanged-hashes.txt`、`03-new-objects-list.json`、`04-coverage-targets.json`、`05-facet-value-match-counts.json`、`06-library-filter-per-industry.json`、`07-vocabulary-cross-industry.txt`、`08-seed-gates-raw.txt`、`09-count-assertion-diff.txt`、`09b-assertion-inventory-after.txt`、`10-contract-regression.txt`、`11-test-db-free-raw.txt`、`12-test-suite-raw.txt`、`12b-suite-skip-discrepancy-probe.txt`、`13-git-commit.txt`、`14-compliance-check.txt`；外加 `workspace/02a-a2-violation-scan.txt`。

结论：**全部与 REPORT 一致、可复现**；本刀没有出现"数据与报告打架"或"证据指向错状态"的问题。

---

## 4. 三处需要说明的判断（**都不构成返工**）

### 4.1 `industry-note-cn-consumer-2026-002` 带了 2 个行业（`consumer_goods` + `retail`）

我的 §3.1.3 写的是"`industry_note` **恰好 1 个**具体行业"，而这一个**是历史遗留**：我直接对比了 `a463658`，它的原值就是 `["consumer_goods","retail"]`，**本刀没动过**（old == new）。

**为什么我判它不算违规**：① 它**不是本刀引入**的；② "修"它意味着**删掉一个既有行业标签**，这与本刀更高优先级的约束（"不收窄也不替换既有内容"）直接冲突，属于**破坏性**动作；③ 该规则的本意是"行业洞察必须落在具体行业、不得标通用"——一条 `consumer_goods + retail` 的洞察仍然是**具体的**。→ **接受**，并把真实不变量修正为"`industry_note` **至少 1 个**具体行业且不得 `cross_industry`（历史对象允许携带多个）"。这是我的规则缺了"祖父条款"，记入 §5。

### 4.2 26/45 是 `cross_industry`，行业轴"可用但浅"

24 条补齐的标注**全部**是 `cross_industry`（原本就没有行业锚点的方法/模板/风险清单），10 个具体行业各只有 **2** 条。这说明：**轴从"废的"变成"能用的"，但还谈不上"厚"**。A4 的阈值（≥2）是我定的，达标即算过；但作为架构师我要如实写下这个天花板——**真正"把咨询行业做实做透"还需要一轮内容加深**（每行业 4–6 条、行业洞察覆盖全部 10 个行业），这一条转出给后续内容刀（见 §6）。

### 4.3 全套件 skip 数出现过一次 846/6（vs 基线 847/5）——cc 的处置我认可

`12b-suite-skip-discrepancy-probe.txt` 记录了：早期一次跑批是 846 passed / 6 skipped / **0 failed**，后续四次都是 847/5/0。cc **没有**用"大概是某某"糊过去，而是说明"那次没开 `-rs`、日志已被覆盖、**无法事后归因**"，并给出结构性排查。**所有跑批 failed 均为 0**，收口证据是全新库上的 847/5/3deselected/0failed。→ **接受**，并把"跑测试默认带 `-rs`"作为后续任务书的要求（见 §7）。

---

## 5. 我自己（架构师）的缺陷记录（第 4 次同类，但本刀没造成停手）

1. **§3.1.3 缺"祖父条款"**：写"恰好 1 个具体行业"时没想到**历史对象已经**有 2 个的情况（§4.1）。教训：给既有语料定规则时，必须区分"**新增对象**的规则"与"**既有对象**的规则"，后者要么祖父化、要么显式允许收窄（并说明代价）。
2. **v1 的穷尽性清单漏项**（本刀 #1 已记）：`§1.5` 漏了最严格的第 [6] 处 → 已修，并在 v1.1 里把**三条盘点命令**写进任务书。这条流程改进本刀已生效（`09`/`09b` 就是按它交付的）。
3. **口径类的隐性期待**：我在 §3.5 写"每个值命中 ≥2"，但没写"**不许给 `/facets` 加计数**"（我在 #1 裁定 §4.3 才补上）。cc 自己没去动 facets 结构——**是我在任务书里补晚了**。

---

## 6. 裁定：**PASS**

理由：A0–A14 全部成立；**核心数字（45 条、每行业 2、类型分布、A1 其余字段 36/36、facets 无 0 匹配值）我用自己的脚本与进程内目录全部重算过**；四次断言的解冻严格落在授权清单内且有"改后重盘"证明；键集合未变、SPA 未变、依赖未变、未 push、无残留、无密钥。两处需要解释的地方（历史遗留的双行业、行业轴仍浅）都不构成本刀缺陷——前者是**我的规则缺祖父条款**，后者是**如实的能力边界**。

**转出（移交后续刀）**：

1. **内容深度**（§4.2）：每行业 2 条是下限而非目标；建议一轮"行业加深"（每行业 4–6 条 + 10 个行业各有 `industry_note`），可并入 OEI-013 或单独一刀。
2. `/api/search` 的**召回可复现**（承自 OEI-009，仍是 OEI-012 的显式目标）。
3. `merge_engine` 的 **fail-open 显式化**（承自 OEI-009 §8.1）。
4. **真认证**（`X-User-Id` 可自选）——演示讲权限分层之前必须做。
5. **引擎调用审计持久化**（设计已备，独立小刀）。
6. **凭据耐久化**（PAT 取代 cookie jar）。
7. `TASKS.md` 里 KC-001/OEI-008 时代的两处"36 个种子对象"表述是**历史附录**（按约定不改），但读者要知道**现值以 `附录 Q` 为准**。

**值得固化的好做法（写进后续任务书模板）**：

- **扫描要"有牙"**：主动注入故障证明扫描能发现问题（`02a` 的做法）——否则"0 违规"可能只是"没扫"。
- **依据要可机检**：`basis_quote_is_substring_of_own_fields` 这种**自校验的标注依据**，比人工说明强得多；连 loose 假命中都如实记下。
- **序列化往返证明**：要断言"其余字段未变"，先证明序列化器能逐字节复原原文件，否则"没变"可能只是排版巧合（`02` 的做法）。
- **跑测试默认带 `-rs`**，让 skip 名单永远留痕（`12b` 的教训）。
