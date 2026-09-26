# OEI-014 审验裁定（codex）— 最终裁定：**PASS**

> 审验时间：2026-09-26 08:5x ｜ 被审对象：`REPORT.md` + `evidence/`（18 份）+ `workspace/`（10 件）+ `DONE`（08:51）
> 被审任务书：`TASK.md` v1 ｜ 被审 commit：**`a3d61cd`**（3 文件、未 push）｜ 前序：`OEI-011` 已 PASS 关闭
> **裁定：`PASS` —— 本刀关闭。A0–A11 全部成立，核心数字我用独立脚本重算过，锚点纪律我逐条抽查过。这是到目前最干净的一刀。**

---

## 1. 逐条验收（codex 独立复核）

| # | 验收标准（摘要） | 结论 | 我的核实 |
|---|---|---|---|
| **A0** | 锚点扫描器有牙 + 4 条假阳性回归 | **PASS** | `anchor_scan.py` 有：**严规则具体词表** + **弱词表（数据化）** + `--loose` 对照 + `test_teeth()` 故障注入 + 回归样例断言。我读了弱词表：`ai` / `public` / `tech` / `制造(业)` / `供应链` / `运输` / `金融` **逐条带理由**（如"制造可作场景范围讲（'用于制造业与服务运营场景'）""供应链是通用概念"）。4 条回归样例在严规则下报"无锚点"；**我另核了这 4 条在新种子文件里仍为 `cross_industry` 且与 `c30e50e` 原值逐字相同** |
| **A1** | 既有 45 条零改动 | **PASS** | 我**自己写脚本**：对既有 45 条做**整对象**（全字段、sort_keys）规范化 JSON sha256，与 `git show c30e50e:…` 原值**逐条比较 → 0 处不一致、0 个旧 id 缺失**。种子 `git diff --numstat` = **713 插入 / 0 删除**（但 cc 明确说 numstat 不是主证据、哈希才是——这个区分做得对） |
| **A2** | 加深目标 | **PASS** | 我重算：总数 **65**；10 个具体行业**各 4**；`industry_note` **每个行业各 1**（补齐 insurance / public_sector / technology）；类型 case 20 / methodology 12 / proposal_play 8 / deliverable_template **7** / risk_check 9 / industry_note 9；`cross_industry` 26 —— 附录 Q 的每类型下限（10/10/6/4/4/2）**全部继续成立** |
| **A3** | 锚点纪律 | **PASS** | `03-anchor-basis.json` 20/20，每条 `anchors[]` 含 `anchor_keyword / anchor_field / anchor_sentence / is_substring_of_that_field / in_own_title_or_summary`。我**抽查了 manufacturing / logistics / insurance / technology 四类**：制造用"工厂/产线/良率/工单/设备综合效率"（**刻意避开了弱词"制造"**）、物流用"物流/仓储/仓配/运力"、保险用"保险/寿险/财险/核保/理赔"、科技用"软件"——全部是**具体词、落在自己的 title/summary、原句可定位**，**没有一条靠 `ai`/`public` 这类子串充数** |
| **A4** | 内容纪律 | **PASS** | 我**在真实文件（65 条）上独立跑** `test_consulting_seed_schema.py` + `test_consulting_seed_discipline.py` + `test_consulting_seed_count.py` + `test_consulting_service.py` → **24 passed / exit 0** |
| **A5** | facets / 过滤（每行业 ≥4 + 有 note） | **PASS** | 我**在进程内复算**（不经 cc 的 HTTP 脚本）：10 个具体行业各 4、`industry_note` 每行业 1。cc 另走了**真实 HTTP 面**（死端口 DSN + mock 引擎），并做了 **note-id 集合"API vs 种子"逐 id 交叉验证**——防"接口能查、内容其实没有" |
| **A6** | 断言零改动 | **PASS** | `git diff c30e50e a3d61cd -- tests/` = **空**（我亲自跑）。cc **自曝了一个坑**：`grep '== *36'` 误报 3 条（一条 `== 3600.0`、两条注释/docstring），于是改用 **AST** 判"代码层 `== 36` = 0 次"——这比"能匹配注释的 grep"可靠得多，且如实写进了证据 |
| **A7** | 契约不回归 + 全套件 | **PASS** | 键集合逐键相等（AST 字段名 + 运行时响应键两路对照）；全套件原始输出 **847 passed / 5 skipped / 3 deselected / 0 failed**，`-rs` 带出 5 条 skip 名单、与 OEI-011 收口逐字相同，**846/6 那次偏差没有复现**。另：chain 日志印的 `commit under test: c30e50e` 是"跑套件时还没 commit、`git rev-parse HEAD` 打的是旧 HEAD"——cc **用 seed sha256（d093562c == a3d61cd blob）证明真正被跑的是写入了 20 条新对象的工作区**，不是 c30e50e，这个澄清很关键 |
| **A8** | 文档 | **PASS** | `docs/API.md` 的**计数** `45` → `65` 已全改；剩下的 2 处裸 `45`（499 的"来历"历史、637 的 OEI-011 历史列）是**有意保留**；`TASKS.md 附录 R` 存在。我独立跑 `scripts/check_api_docs.py` → `App-only 0` |
| **A9** | 提交 | **PASS** | `a3d61cd` 只含 3 文件（seed + docs/API + TASKS），全部在授权白名单内；`ahead 4`；**不在任何远端分支** |
| **A10** | 合规与资源 | **PASS** | `pyproject.toml`/`uv.lock` 零 diff、`demos/spa` 零 diff、`metadata.py` **零 diff**（词表未动）、`tests/` 零 diff；无 ece 容器/进程残留；密钥值扫描零命中；未 push |
| **A11** | 证据纪律 | **PASS** | 全部 JSON / 哈希 / AST / 原始响应；`13-reproducibility.txt` 提供**可复现**的反证（喂一条无锚点 id → exit 1）；无不可判定表述、无"用户截图" |

---

## 2. 我这次独立做了什么（不采信自我描述）

- **重算种子**（自己的脚本，不经 cc 中间产物）：45→65、类型分布、每行业 4、note 每行业 1、cross 26、**A1 整对象哈希 45/45**、新 id 清单。
- **抽查锚点**：读了 `anchor_scan.py` 的词表/弱词表/回归样例，并抽查 4 个行业的新对象锚点原句。
- **独立跑测试**：4 个 consulting 单测文件 → 24 passed；`check_api_docs.py` → App-only 0。
- **逐字核对**：`tests/` 零 diff、`docs/API.md` 的 45→65、`metadata.py`/`demos/`/`pyproject` 零 diff、`git show --name-status`、容器/进程、密钥扫描。

---

## 3. 证据抽查（逐字打开）

`00-anchor-scanner-and-false-positives.txt`、`01b-existing-45-unchanged-hashes.txt`、`01c-seed-diff-stat.txt`、`01d-assertion-inventory-after.txt`、`02-new-objects-list.json`、`03-anchor-basis.json`、`04-coverage-before-after.json`、`05-seed-gates-raw.txt`、`06-anchor-scan-final.txt`、`07-facet-and-filter.json`、`08-contract-regression.txt`、`09-test-suite-raw.txt`、`10-docs-changes.txt`、`11-git-commit.txt`、`12-compliance-check.txt`、`13-reproducibility.txt`、`14-check-api-docs.txt`；源码抽读 `workspace/anchor_scan.py`（词表 + 弱词表 + 回归 + teeth）。

结论：**全部与 REPORT 一致、可复现**；本刀没有任何"数据与报告打架""证据指向错状态""断言偷偷被改"的情况。

---

## 4. 三处需要说明的判断（都不构成返工）

### 4.1 弱词表里 cc 比我的任务书**更严**——这是对的收紧，不是越界

我任务书 §3.3 只点名 `ai` / `public` / `tech` 三个陷阱；cc 把弱词表扩展到 `制造(业)` / `供应链` / `运输` / `金融`，并**每条写清理由**。这把我任务书里那句"必须有具体行业锚点"落到更实处：`制造` 能作"场景范围"（"用于制造业与服务运营场景"），`供应链` 是任何行业都有的概念。**我追认**，并记下它的副作用（见 §6 第 7 条）：`metadata.py._INDUSTRY_KEYWORDS` 仍是旧松词表（含这些弱词），它服务的是**上传建议路径**，与 seed 锚点判定是两条线——这本身没错，但建议器仍可能给含 `supply_chain` 的上传文档建议 `manufacturing`。属**遗留小债**，不属本刀。

### 4.2 交付 commit 的 diff 有 15 行删除——全部在 `docs/API.md`

15 删 = 6 处计数 `45`→`65` 的改写行（改旧行、删旧计数）。种子文件是 **713 插入 / 0 删除**，`tests/`、`metadata.py`、`demos/`、`pyproject` 都是零 diff。**不存在"顺手改了既有 45 条"的嫌疑**，A1 整对象哈希已把这一点钉死。

### 4.3 `deliverable_template` 补到 7、`case` 到 20——超出"≥6"一点点，完全在目标内

每类型下限来自 KC-001/附录 Q（10/10/6/4/4/2），本刀只设了 `deliverable_template ≥6` 一个补充下限；实际 7 与 20 都只是"达标"而非"超标跑偏"。总数 65 也落在任务书的 **65 ≤ N ≤ 70** 下沿。

---

## 5. 裁定：**PASS**

理由：A0–A11 全部成立；**核心数字（65、每行业 4、note 每行业 1、类型分布、A1 整对象哈希 45/45）我用自己的脚本重算过**；锚点纪律我逐条抽查，确认是**具体词 + 落在自己 title/summary + 原句可定位**，没有一条靠子串假阳性充数；断言零改动有 `git diff` + AST 双证；无越界、无新依赖、无密钥、无残留、未 push。

**转出（移交后续刀）**：

1. `/api/search` 的**召回可复现**（OEI-012 显式目标，承自 OEI-009 技术发现）。
2. `merge_engine` 的 **fail-open 显式化**（承自 OEI-009 §8.1）。
3. **真认证**（`X-User-Id` 可自选）——演示讲权限分层之前必须做。
4. **引擎调用审计持久化**（设计已备，独立小刀）。
5. **凭据耐久化**（PAT 取代 cookie jar）。
6. **内容深度已达标**（每行业 4 + 每行业 1 条 note）；行业轴"能用且够厚"。后续内容动作只在 OEI-013 需要更多演示素材时再定。
7. **上传建议器的弱词收紧**（见 §4.1）：`metadata.py._INDUSTRY_KEYWORDS` 仍含 `ai`/`public`/`制造`/`供应链`/`运输`/`金融` 等弱词，与 `anchor_scan` 的严词表已分叉——建议后续刀把建议表的弱词也收紧，否则上传时仍可能把"供应链/公开"内容建议成"制造业/公共部门"。

**值得固化的好做法（写进后续任务书模板）**：

- **"有牙"要可复现**：`--loose` 对照 + `test_teeth()` 注入 + 反证跑法（`13` 里喂无锚点 id → exit 1），三者齐了才叫"扫描器有牙"。
- **断言判断用 AST，不用能匹配注释的 grep**（`01d` 的教训：`grep '== *36'` 把 `== 3600.0` 也抓进来）。
- **"commit under test" 必须用 blob 哈希澄清**（`09` 的教训：`git rev-parse HEAD` 在未 commit 时会指向旧 HEAD）。
- **内存预演不算证据**：`verify_draft.py` 明确标注"那两个读文件的用例跑不了、不当作跑过"，真实文件上的输出才是 A4。
- **交叉验证防"接口能查、内容没有"**：note-id 集合 API vs 种子逐 id 相等（`07`）。
