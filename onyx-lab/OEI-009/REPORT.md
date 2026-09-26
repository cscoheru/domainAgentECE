# OEI-009 执行报告（cc）— R1–R4 返工版

> 日期：2026-09-25 ｜ 任务书：`OEI-009/TASK.md` **v1.4** ｜ 状态：**返工完成，等待 codex 第三轮审验**
> 依据：`OEI-009/VERDICT.md` **审验裁定 #2**（`FAIL` —— **仅证据与文档层**；产品实现经 codex 独立复核成立；返工项 R1–R4）
> 本文件取代 16:50 版。**本轮未改动任何产品代码**（复核见 §7）。

---

## 0. 一句话

按 R1–R4 完成返工：**只改证据与文档，产品实现一行未动**。四项全部处置，并额外定位到导致前两处 FAIL 的**共同技术根因**——`POST /api/search` 不是向量 top-k，而是 chat 模式那条 **LLM agentic 检索管线**，返回值是"相关性结果"而非固定条数——据此把 A4/A7 两个分支都改造成**可复现**的构造。

---

## 1. 返工总览

| 项 | codex 要求 | 结果 | 证据 |
|---|---|---|---|
| **R1** | `step26` 可安全重跑 + 重取 `05`，使数据/汇总句/报告三者一致 | **完成** | `05-per-result-filter-matrix.json`（cleanup 审计 + stale 轮询 + 矩阵，四处一致） |
| **R2** | 真·无命中（`assert len(items)==0`） | **完成** | `07-side-channel.txt`（`branch_no_hit` = 0 条，`engine_status=ok`） |
| **R3** | 补 `00c` / `02` / `12` 三份原始输出 | **完成** | `00c-scratch-project.txt`（重写，中间真跑测试）、`02-registry-migration.txt`（保留 + 只读复核）、`12-test-db-free-raw.txt`（重跑） |
| **R4** | `REPORT §10.2` 填真实 hash；`15` 的 author 行对齐 | **完成** | §10 + `15-git-commit.txt` |

**额外交付**（本轮新增）：

| 交付 | 作用 |
|---|---|
| `workspace/rebuild_demo_state.sh` + `17-rebuild-demo-state.txt` | codex §8.4 要求"下一刀或演示前必须能一条命令重建它"—— 提供**并实测跑通**（§9） |
| `workspace/check_evidence_consistency.py` + `19-evidence-consistency-check.txt` | **把本次 FAIL 的根因做成守卫**：重新解析 `05`/`07`/`08` 并断言其中每个数字都出现在本报告里。21 项全绿（§3.3） |
| `18-teardown-and-compliance.txt` | 收尾三查 + 合规的**原始**快照（可复现 §8 的每条结论） |

---

## 2. 共同根因：`/api/search` 是 agentic 管线，召回不确定（本轮新发现）

前两处 FAIL 表面上是两件事（`05` 数据自相矛盾、`07` 无命中其实命中），**底层是同一个假设错误**：把 `/api/search` 当成了"向量 top-k"。它不是。

只读复查容器内实现（`docker exec onyx-api_server-1 sed -n '1,200p' /app/onyx/server/features/search/api.py`）确认：

- `POST /api/search` 调 `SearchTool.run()`，**与 chat 模式同一条多阶段 agentic 检索**；
- 构造 `SearchTool` 时 `auto_detect_filters = load_settings().auto_detect_search_filters is not False` → **含 LLM 自动过滤器**；`skip_query_expansion` 由请求方给，ECE 不给 → **含 LLM 查询扩展**。

实测后果（本机，2026-09-25）：

| 现象 | 实测 |
|---|---|
| 单次检索延迟 | **20–56 s** |
| 返回条数是"相关性结果"，不是固定 k | 同一语料对不同 query 分别返回 **1 / 2 / 3 / 4 / 5** 条 |
| 无意义 query **不保证空** | 随机串 `ZQXJ9942KLVTLM` → 返回 **4** 条 |
| 同一 query 重复 3 次 | 所选的两条 query **3/3 完全一致**（故仍可构造确定性证据） |

这解释了 codex 的两处 FAIL：

1. **A4/`05`（demo_user = 5）**：既有"脚本重跑未清理自己上一轮产物"（真因，已修），也有"原始召回按 chunk 计数"——**同一文档的多个 chunk 各占一条**。v1 只记 `count`，没有记 `distinct`，于是 5 条看起来像 5 份文档。v2 的证据里两者都记（见 §3.3）。
2. **A7/`07`（"无命中"其实命中 3 条）**：v1 假设"无意义 query → 0 命中"，在该管线下不成立。R2 因此改为**用主题隔离**而非制造无意义查询（见 §4）。

> 这条发现对下一刀有直接影响，已写进 §10 建议（OEI-012 应把"召回可复现"作为显式目标）。

---

## 3. R1 — `step26` 幂等化 + `05` 重取

### 3.1 修复的三个缺陷（v1 的真实成因）

| # | v1 缺陷 | 后果 | v2 修复 |
|---|---|---|---|
| a | 清理时的 `DELETE` **不带会话 cookie**，且 `except: pass` 吞掉所有异常 | 删除静默 401/403 → **每轮重跑都留下一个孤儿对照文档** | DELETE 带 cookie；**记录真实状态码**；非 2xx 一律响亮失败（`delete_failures`） |
| b | 待删文件 id **只来自自己的登记行**（`engine_document_id`） | 登记行一旦先被删掉，引擎里的文件就再也找不回 | 增加**按名称模式兜底扫描**项目 1：任何 `ece-*…oei009-comparison-restricted*` |
| c | marker **基于时间**（`sha256(time_ns())`） | 每次重跑文件名不同 → 召回行为不同 → **证据不可复现** | marker 固定为 `oei009step26comparisonmarker` → 受控文件名恒定 `ece-df16d19c9e7b-oei009-comparison-restricted.md` |

**兜底扫描（b）在本次从零重建中被实证触发**：新 PG 里没有任何登记行（`registry_deleted = 0`），但演示项目里仍有**上一 PG 生命周期遗留**的对照文档；脚本靠名称扫描找到并删除：

```json
"cleanup": {"registry_deleted": 0, "acl_deleted": 0, "files_deleted": ["0ab96c3f-…"],
            "delete_failures": [], "files_found_by_name": ["ece-df16d19c9e7b-oei009-comparison-restricted.md"]}
```

这正是 v1 会漏掉的孤儿 —— 仅带 cookie 还不够，必须同时按名字兜底。

### 3.2 新增：stale-index 轮询（把非确定性钉死）

Onyx 的向量删除是**异步**的：两步删除返回 200 后，旧 chunk 仍可能被 `/api/search` 召回一段时间。**这正是 v1 `05` 出现 5 条的第二个机制**。v2 在清理后增加 `_wait_for_stale_clear()`：轮询直到引擎不再召回该文件名（上限 240 s，历史全部落盘）。

本次实测（`05.stale_clear`）：

```
poll 1: raw_count=4, stale_matches=1      ← 旧 chunk 仍在
poll 2: raw_count=3, stale_matches=0      ← cleared
```

并新增硬断言：`raw_recall.titles.count(CONTROLLED_FILENAME) == 1`（不得有重复）。

### 3.3 最终矩阵（`05`，与脚本汇总句、断言、本报告四处一致）

原始召回（过滤器的**输入**，现在也记入证据）：

| query | raw count | raw distinct |
|---|---|---|
| `oei009step26comparisonmarker`（demo） | 4 | **4** |
| `员工报销政策与发票审核流程`（isolation） | 1 | 1 |

授权后集合（`engine_items`，过滤器的**输出**）：

| 身份 | demo query | isolation query |
|---|---|---|
| anonymous | **3** | **0** |
| `demo_user`（alice，持 ACL） | **4**（含受限对照文档） | **1** |
| `other_user`（bob，无 ACL） | **3** | **0** |

- 受限对照文档的标题与片段对**非授权者完全不出现**（`restricted_visible=false`，两条 query 均然）；
- `engine_status` 三态语义未被借用为泄露通道（`hidden_count` 只在 `FilterResult` 内，不进响应）。

### 3.4 演示 ACL 窗口：1 天 → **7 天**（本轮调整，理由如下）

原窗口 `[2026-09-25, 2026-09-26)` 会在**次日审验时静默过期**（`valid_to` 为开区间右端），届时 "alice 看 4 条" 将不可复现 —— 那会制造一个**由时间而非代码引起的假 FAIL**。现改为 `[2026-09-25, 2026-10-02)`（`ACL_VALID_DAYS = 7`）。

这仍是**有界时间盒**：step 3.3 照旧演示"过期即失权、恢复即复现"，只是恢复目标同步为 `today+7`（`step33` 从 `step26` 导入同一常量，杜绝两处漂移）。

---

## 4. R2 — 真·零命中（`07`）

### 4.1 构造：主题隔离，而非制造无意义查询

新增固定 query `ISO_QUERY = 员工报销政策与发票审核流程`，并给对照文档加入一段**主题与咨询方法论完全无关的内部内容**（员工报销/发票审核）。由于该主题在整个语料里**只存在于这一份文档**，召回必然只返回它；而它对 anonymous / bob 会被权限过滤掉 → **零授权结果**。

这是"真实可达、可解释"的状态，而不是 v1 那种"赌一个随机串什么都不匹配"。

### 4.2 断言（`step25`，硬断言已加上）

```python
if nh["engine_items_count"] != 0:   # ← R2 要求的断言，v1 完全没有
    print("FAIL: no-hit branch returned N items (expected 0) …")
```

### 4.3 实测四个分支（`07`）

| 分支 | query | `engine_status` | items | static sha256 |
|---|---|---|---|---|
| `branch_static_baseline`（新） | `问题树` | ok | 2 | `677538eaf608…` ← **与历史值一致** |
| `branch_ok` | marker | ok | 3 | `677538eaf608…` |
| `branch_unavailable` | marker（引擎置为不可达） | **unavailable** | 0 | `677538eaf608…` |
| `branch_no_hit` | isolation | **ok** | **0** | `677538eaf608…` |

- `static_determinism.equal = true`（ok 与 unavailable 同 query → 静态侧逐字节相同 = 引擎正交）；
- `baseline_matches_historical = true` —— 新增这条与**已验收的历史 sha** 的比对，把"静态侧零变化"从"本次三分支互等"升级为"跨版本未退化"。

---

## 5. R3 — 补齐三份原始输出

### 5.1 `00c-scratch-project.txt`（**重写**）

v1 版本只是在开头和结尾各列一次项目 1 的文件，**中间什么都没跑**，等于没证明任何事。v2 在两次列目录之间**真的执行**：

1. **4 个 DB-free 单测文件**（原始 summary 落盘）；
2. **`step22_fail_closed.py`**（TASK §4 步骤 2.2 明文授权、并自行两步删除的探针）→ `PASS — fail-closed`；
3. **scratch project 往返**：upload → 项目 2 出现 1 份 → 两步删除（`unlink=204 / delete=200`）→ 项目 2 归零。

结果：

```
demo project id=1 : before=4 files, after=4 files
项目 1 前后一致            : True
项目 1 无测试/探针残留      : True
scratch 事后为空            : True
```

### 5.2 `02-registry-migration.txt`（**保留 + 只读复核**）

该文件（17:03 产出）已含 codex 要求的三项：`alembic downgrade 0008` 与 `upgrade head` 的真实输出、**唯一约束违约实测**（`UniqueViolation … engine_documents_engine_name_engine_filename_key`）、往返后的 schema 检查。

迁移文件 `0009_engine_documents.py` 自 commit `a884d41` 起**未改动**，故该证据仍然有效；本轮另做**只读**复核，逐字比对它的 schema 声明与当前 DB：

```
表存在            : 1
唯一约束          : engine_documents_engine_name_engine_filename_key   ← 与证据同名
索引（5 个）       : engine_documents_engine_name_engine_filename_key,
                    engine_documents_pkey, idx_engine_docs_lookup,
                    idx_engine_docs_project, idx_engine_docs_uploader    ← 与证据逐项一致
```

> 未重跑 downgrade/upgrade 的理由：它会 drop 掉表、销毁当前演示态，而它证明的（迁移可升可降）与 PG 实例无关。为避免"为取证而破坏证据"，采用"保留 + 只读逐字复核"。**若 codex 仍要求现场重跑，可在重建脚本之后单独执行**（`rebuild_demo_state.sh` 已把 PG 重建做成一条命令）。

### 5.3 `12-test-db-free-raw.txt`（**重跑**）

4 个单测文件的原始 pytest 输出：`18 + 11 + 11 + 9 = 49 passed`。

---

## 6. R4 — 文档订正

1. **`REPORT §10.2` 的 `XXXXXXX` 占位符** → 真实短 hash **`a884d41`**（见 §10）。
2. **`15-git-commit.txt` 的 author 行**：原写 `Claude Code <noreply@anthropic.com> via cc@onyx-lab.local` ≠ 实际提交者。实测：

   ```
   $ git log -1 --format='%an <%ae>%n%cn <%ce>' a884d41
   Claude Code <cc@onyx-lab.local>
   Claude Code <cc@onyx-lab.local>
   ```

   已改为实际值，并附上验证命令。
3. **额外更正（本轮自查发现）**：原报告 §11 把 `onyx-lab/OEI-009/workspace/*.py` 列为 commit `a884d41` 的"新增"文件 —— **不成立**。`onyx-lab/` 不在 ECE 仓内（`git ls-files | grep -c '^onyx-lab'` = 0）；这些脚本位于**父仓**检出中，而父仓里 `onyx-lab/OEI-009/` 目前是**未跟踪**状态（`?? onyx-lab/OEI-009/`）。已在 `15-git-commit.txt` 写明，并说明未在父仓提交（TASK §7 授权的是 ECE 提交，不是文档仓提交）。

---

## 7. "产品实现未改动"的复核声明

本轮所有改动都落在 `onyx-lab/OEI-009/workspace/`（取证脚本）与 `evidence/`、本报告。ECE 产品代码零漂移：

```
$ git diff --stat a884d41 HEAD -- src tests docs scripts TASKS.md
(空)
$ git status -sb
## main...origin/main [ahead 1]
 T docs/demo-platform/DEMO_PLATFORM_PRD.md      ← 开刀前即存在（OEI-008 VERDICT §4）
 T docs/demo-platform/DEPLOY_USER_PROXY.md      ← 同上
```

因此：

- **A11 的 `806 passed / 0 failed` 结论不受影响**（全套件 `13` 本轮未重跑；依据 = 产品代码零漂移 + 49 个新单测已由 **codex 本人独立跑绿** + 本轮 4 个单测文件的原始输出已落盘 `12`）；
- **A0 / A0b / A1′ / A2 / A3 / A5 / A6 / A8–A14 的结论不受本轮影响**（这些项的证据文件除下列三份外**未被本轮改动**）：

| 被本轮刷新的证据 | 原因 | 仍然成立的验收项 |
|---|---|---|
| `04-backfill-demo-docs.json` | 登记 id 随 PG 重建变化；顺带记录白名单修复 | A3 |
| `05-per-result-filter-matrix.json` | R1 点名重取 | A4、A6 |
| `06-fail-closed.json` | 用重建后的同一状态重取 | A5 |
| `07-side-channel.txt` | R2 点名重写 | A6、A7 |
| `08-timebox-acl.json` | 窗口常量调整后重取 | A8 |
| `12-test-db-free-raw.txt` | R3 点名落盘 | A11 |
| `00c-scratch-project.txt` | R3 点名重写 | A0 |
| `15-git-commit.txt` | R4 点名订正 | A12 |
| `17-rebuild-demo-state.txt` | 新增（本轮交付） | §9 |
| `18-teardown-and-compliance.txt` | 新增（收尾三查原始快照） | §8 |
| `19-evidence-consistency-check.txt` | 新增（一致性守卫输出） | §3.3 |

**未改动**：`00-credentials.txt`、`00a-webhook-flake-fix.txt`、`00b-api-docs-parser.txt`、`01-engine-doc-key-mapping.json`、`02-registry-migration.txt`、`09/10/11-design-*.md`、`13-test-suite-raw.txt`、`16-compliance-check.txt`。

**一致性守卫**（`19`，21 项全绿）：`check_evidence_consistency.py` 重新解析三份引擎侧证据并断言其中的每个数字都出现在本报告里，包括：

- `05` 六格矩阵（3/4/3 与 0/1/0）、`raw count == distinct`、cleanup 零失败、stale 已清、受限标题不外泄；
- `07` no-hit 为真 0 条、unavailable 分支、四分支 sha 全等、baseline 仍等于历史值；
- `08` 三阶段 4/3/4；
- 本报告确实引用了 "alice 4 / bob 3"、no-hit 0 条、A=4/B=3/C=4 与 commit `a884d41`。

→ 这正是 §4.1 那处 FAIL 的**防复发装置**：今后任一侧被改动而另一侧没跟上，这条命令会失败而不是静默矛盾。

---

## 8. 合规与收尾三查

| # | 检查 | 结果 |
|---|---|---|
| 1 | 残留探测进程（`pgrep -af 'step2N_\|step33\|r3_evidence\|rebuild_demo'`） | **无** |
| 2 | 残留 `ece-*` 容器（`docker ps -a`） | **无**（临时 PG `ece-pg-oei009r1` 已 stop + rm） |
| 3 | 内存 / swap 快照 | `Mem: 13Gi total, 11Gi used, 1.3Gi available`；`Swap: 8.0Gi total, 6.5Gi used` —— ⚠️ **内存偏紧**（见下） |
| 4 | Onyx 容器 | 9 个 Up，**RestartCount 全为 0**（未重启任何容器） |
| 5 | 凭据 | 两个 jar 打 `/api/me`、`/api/user/projects` 均 **200**（mtime `2026-09-25 15:20:16`）；**无 cookie 值落盘** |
| 6 | 未 push | `origin/main = a9cee31`；`a884d41` 不在任何远端分支；`git status` = `ahead 1` |
| 7 | 未触碰 | Onyx 上游源码 / compose / `.env` / `.wslconfig` / swap 文件 —— 均未改（只读 `docker exec` 读源码与 `psql` 查表） |

> ⚠️ **内存如实记录**：本刀跨数小时、跑了多轮真引擎取证（每轮含 6–10 次 agentic 检索，单次 20–56 s），收尾时 `available` 仅 **1.3 GiB**、**swap 已用 6.5 / 8.0 GiB**。这是长时间连续取证的代价，不是新泄漏（**无游离进程、无残留容器**）。若后续刀要连续做真引擎取证，建议按 `LOCAL-AGENT-PROTOCOL §5.1` 第 5 条考虑云 VM，或分批之间让 OpenSearch / llama-server 冷下来。

---

## 9. 演示态重建：一条命令（codex §8.4 的落地）

`workspace/rebuild_demo_state.sh` —— 从**零**重建演示态：

```bash
bash /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/workspace/rebuild_demo_state.sh <evidence_dir>
```

它依次做：① 删掉同名旧容器并**新建**临时 PG（`pgvector/pgvector:pg16`）→ ② 等 `pg_isready` → ③ `alembic upgrade head`（cwd 必须是 ECE 根，`alembic.ini` 的 `script_location` 是相对路径）→ ④ `backfill_demo_docs.py` → ⑤ `step26_demo_falsifiable.py` → ⑥ `step33_timebox_e2e.py`，并把 ④⑤⑥ 的输出 tee 进对应证据文件。

**实测**（`17-rebuild-demo-state.txt`，全程 `exit=0`）：

```
PG 新建 → ready → alembic upgrade head → backfill(3 行, 幂等) →
step26 PASS → step33 PASS
```

重建后的状态与证据完全一致：登记 `1,2,3`（public）+ `7`（restricted）；ACL `engine_document:7` 窗口 `[2026-09-25, 2026-10-02)`；demo query → anon 3 / alice 4 / bob 3；isolation query → anon 0 / alice 1 / bob 0。

> **给下一位使用者的提示**：`engine_documents.id` 随 PG 生命周期变化，**不是稳定标识**；稳定标识是**受控文件名** `ece-<docref>-<slug>.<ext>`（本演示固定为 `ece-df16d19c9e7b-oei009-comparison-restricted.md`）。所以证据里的 `registry_id` 只需与**同一次运行**内部自洽，不必跨运行相等。
> 演示结束记得释放：`docker stop ece-pg-oei009r1 && docker rm ece-pg-oei009r1`（本轮已释放）。

---

## 10. 提交记录（A12）

- commit：**`a884d41`** —— `feat(OEI-009): engine-document registry + per-result permission filter + ACL time-box`
- 仓：`/mnt/d/Projects/domainAgentECE/ece`（ECE 产品仓）；分支 `main`；**17 文件，+2424/-57**
- author / committer：`Claude Code <cc@onyx-lab.local>`（实测值，见 §6）
- **未 push**（TASK §7）；`origin/main = a9cee31`
- 详细清单与仓范围说明：`evidence/15-git-commit.txt`

---

## 11. 验收逐条（A0–A14，按本轮返工后的证据更新）

| ID | 验收 | 状态 | 证据（本轮更新项已标注） |
|---|---|---|---|
| **A0** | 步骤 0 三项收尾 | PASS | `00a`（12×0 failed）、`00b`（4→0）、**`00c`（重写：真跑测试 + scratch 往返）** |
| **A0b** | 凭据前置（blocking） | PASS | `00-credentials.txt`（三端点 200，无 cookie 值） |
| **A1** | 原前提不成立 / 停手分支 | 已闭合 | `VERDICT #1 §3` |
| **A1′** | 映射契约落实 | PASS | 受控名 N=5、`(engine_name, engine_filename)` 唯一、读侧 `(title, source_type)` 匹配、`engine_document_id` 注释；**引擎侧确有 `ece-` 前缀**（`05` 原始召回标题） |
| **A2** | 登记表落位 | PASS | `02`（迁移往返 + 唯一约束实测）+ §5.2 只读复核 |
| **A3** | 3 份回填幂等 | PASS | **`04`（重取）**：登记 3 行、白名单跳过对照文档、二次执行零新增 |
| **A4** | 同一 query 两身份 → 不同 `engine_items` | **PASS（重取）** | **`05`**：demo query → anon 3 / bob 3 / **alice 4**；受限文档标题与片段对无权者**完全不出现**；数据/汇总句/报告四处一致 |
| **A5** | fail-closed | PASS | **`06`（重取）**：未登记探针对三个身份均不可见 |
| **A6** | 无侧信道 + 匿名=public | PASS | `05`（hidden 不进响应、匿名仅 public）+ `07`（四分支 static sha 全等） |
| **A7** | static 零变化 + 三分支不变 | **PASS（重写）** | **`07`**：ok / unavailable / **真·无命中（0 条）** 三分支齐备；static sha 四分支全等，且**与历史值一致** |
| **A8** | 时间窗生效 | PASS | **`08`（重取）**：A=4 / B=3（过期）/ C=4（恢复）；11 个边界单测未改 |
| **A9** | org scope 最小落位 | PASS | `test_org_scope.py`（9 例，含"未引入记忆表/接口"守卫） |
| **A10** | 三份设计文档 | PASS | `09/10/11-design-*.md`（未改动） |
| **A11** | 单测 / 集成 / 全套件 | PASS | **`12`（重跑，49 passed）** + `05`/`08` 集成与端到端 + `13`（806/0，产品代码零漂移故仍成立，见 §7） |
| **A12** | 文档与提交 | PASS | `15`（**author 已订正**）+ `docs/API.md` / `docs/DATA_MODEL.md` / `TASKS.md`；commit `a884d41` 未 push |
| **A13** | 合规 | PASS | §8 七项；容器 restarts=0；未 push；未碰上游/compose/`.env`；演示项目未留测试产物 |
| **A14** | 不得要求用户截图 | PASS | 全部证据为 HTTP 状态码 + JSON + sha256 + 查表输出 + 轮询历史 |

---

## 12. 遗留与建议（不实现）

1. **`/api/search` 的非确定性应在下一刀显式治理**（本轮新发现，§2）：OEI-012（检索质量）建议把"**召回可复现**"列为与"召回精度"同级的验收目标；可选手段：`skip_query_expansion`、关闭 `auto_detect_filters`、或固定评估语料与 query 集。当前 ECE 侧的**结果级授权与去重已经对上游不确定性免疫**（这正是本次把它做成确定性的意义）。
2. **`merge_engine` 的降级分支是 fail-open**（codex §8.1）：`sql_engine is None → return to_engine_items(docs), "ok"`，即未登记文档也会返回。当前生产调用点唯一且都传了 `sql_engine`，**不可达**；但建议下一刀显式化（`allow_unfiltered: bool = False`）。
3. **头部身份不是认证**（codex §8.2）：`X-User-Id` 可自选 —— 演示时须对客户讲清；"真认证"值得单独一刀。
4. **引擎调用审计的持久化**（`09-design-engine-audit.md`）：仍是进程内 `audit_log`；设计文档已含代价评估（分区表 + 90 天 + 写放大 1.0 行/调用），**本刀不实现**。
5. **演示 ACL 窗口是时间盒（7 天）**：过期后 alice 看 4 条不再成立 —— 这是**设计使然**（时间盒授权的意义），不是缺陷。重建方式见 §9；或直接改 `ACL_VALID_DAYS` 后重跑 `step26`。
6. **内存**：长时间连续真引擎取证会把 `available` 压到 ~1.3 GiB、swap 用掉 6.5 GiB（§8）。后续刀建议分批，或按 §5.1 第 5 条改用按需云 VM。

---

## 13. 心跳

本轮返工已完成，`DONE` 已重建。心跳对象 = `onyx-lab/OEI-009/VERDICT.md`（第三轮审验）。
