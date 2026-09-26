# OEI-010 审验裁定（codex）

> 审验时间：2026-09-25 21:0x ｜ 被审对象：`REPORT.md` + `evidence/`（22 项）+ `workspace/`（15 项）+ `DONE`（20:44）
> 被审任务书：`TASK.md` v1 ｜ 被审 commit：`a463658`（未 push）｜ 前序：`OEI-009` 已 PASS 关闭
> **裁定：`PASS` —— 本刀关闭。A0–A14 全部成立；两处"看起来像问题"的我都独立追到底，结论是其中之一为我的任务书用词所致、另一项按规矩转出。**

---

## 1. 逐条验收（codex 独立复核，不采信自我描述）

| # | 验收标准（摘要） | 结论 | 我的核实 |
|---|---|---|---|
| **A0** | 前置与基线；全程 mock | **PASS** | `00-baseline.txt`：pre-change `806 passed / 5 skipped / 3 deselected / **0 failed**`，HEAD 标 `a884d41`、alembic `0009`、`ECE_CONTENT_ENGINE` 未设→mock ✓ 与我 OEI-009 审验时记录的 806 基线一致；`00b-fresh-db-chain.txt` 另用**全新空库**跑通 `upgrade head`（到 `0010`）→ `gen-dataset` → `seed`（428 entities / 1200 relationships）→ 再 `seed` 幂等（created=0） |
| **A1** | org 来源落地 + 四态 | **PASS** | `01-org-identity.json`：procurement/finance/admin → `org:consulting-a`；engineering → `org:consulting-b`；**无 org 探针**（attributes 里没这个键）→ `None`；**未知用户**（stub 分支）→ `None`。我复读 `parser.py` diff：新增 `_coerce_org_id`（非字符串/空串→None）、`resolve_identity` 返回值补 `org_id`、`upsert_identity` 用 JSONB `||` 增量合并 + **自愈 UPDATE**（针对 `ON CONFLICT DO NOTHING` 导致老行拿不到 org_id 的情况）——这是我签发时没想到的坑，cc 自己发现并处理了 |
| **A2** | org 分支；判定顺序不重排 | **PASS** | `engine.py` diff：`_subject_matches` **只多一条规则** `if st == "org" and identity.org_id and sr == identity.org_id`；`check_permission` 主体、`_acl_in_window`、deny/allow 两次遍历、分类矩阵、default-deny 尾部**全部未动**（我逐行看过 diff）。`02-subject-matches.txt` 四态 + 三条回归；我另**独立跑**了 `tests/unit/test_check_permission_org.py`（13 例）绿 |
| **A3** | 迁移 0010 可升可降 + 三条约束真违约 | **PASS** | `0010_memories.py`：命名约束 `ck_memories_scope` / `ck_memories_confidence` / `uq_memories_scope_owner_ref_statement` + 三个索引 + `downgrade` DROP。`03-memory-migration.txt` 贴的是**数据库自己报的**约束名（UniqueViolation / CheckViolation ×2）+ 往返后索引完整 |
| **A4** | 写入过权限引擎（≥6 格） | **PASS** | `04-write-permission-matrix.json` **9 格**：自写自 200 / 写他人 403（**主体门**）/ org 无角色 403（**授权门**）/ org 有角色 200 / **org_admin 写别的 org 403** / 无 org 403 / **有权限者写自己 scope 外的 403** / 无凭据 400 / 重复创建 `created=false` 行数不变。我复读 `api/memory.py`：两道门顺序正确（先主体后授权）、`_authorize_write` 用 `memory_scope` 对象 + `classification='restricted'`（默认拒绝）、ACL 行与记忆行**同一事务**写入（不存在"存在但可见性未定义"的中间态） |
| **A5** | 读取在权限判定之后、逐条授权 | **PASS** | `05-read-matrix.json`：同 org 的 finance/procurement 共享 org 记忆但不共享 user 记忆；engineering（异 org）与两个无 org 身份都看不到 org 记忆。**泄漏断言是对整个响应体做子串检查**（不只是 `memory[]`），`forbidden_statement_hits_anywhere` 全空——这正是我要的那条。我复读 `context/memory.py`：候选集 SQL 只是收窄，**权威判定是每行 `check_permission`**；且**明确不复用** `assembly._load_acl_for`（它硬编码 entity 且把日期置 None），改为按 `memory` 载入并带**真实** `valid_from/valid_to`（我签发时点名的坑，已处置） |
| **A6** | 失效与时间盒 | **PASS** | `06-expiry-and-deleted.json`：过期/软删不注入（行仍在）；ACL `valid_to=昨天` 立即失权、改回恢复。**归因证据**做得比我要求的更细：关窗前后 candidates 都是 6、items 从 6→5 → 证明拒绝发生在**授权步**，不是被 SQL 提前滤掉或被删/过期 |
| **A7** | 确定性 | **PASS** | `09-determinism-n5.json`：N=5 逐字节一致（含顺序）；13 候选 → 恰好注入 10 → `memory_dropped=3`，且该 3 是**独立从库算出来的**，不是拿应用自己的计数器对照自己。排序规则与契约一致（org 优先，组内 `created_at DESC, id DESC`） |
| **A8** | 可追溯 + 无 UI | **PASS** | `07-audit-provenance.{json,txt}`：`context_items` 落 `item_kind='memory'`、`reason` 是**规则名而非记忆正文**、owner 可读 / 他人 403、软删后审计仍在；**SPA 3 个文件逐字节哈希等于 HEAD**（`git diff` 为空是必要不充分，所以做了内容哈希——这点做得对）。我另核对：`git show --name-only a463658` 里**没有任何 `demos/spa` 文件** |
| **A9** | 合规删除 | **PASS** | `08-compliance-delete.json` 14 条断言：单条软删 + 幂等；**删他人 403 且行未被改动**；自己的全量删只删自己的；**org 全量删无权限 → 403 且一条未删**；`include_inactive` 只放宽活跃度、不放宽跨 org |
| **A10** | 既有契约不回归 | **PASS** | `10-package-keys-diff.txt` 三方对照（pre-cut 源码 / 当前源码 / 运行时 `to_dict()`）：11 键为不变前缀、`memory` **追加在最后**、无重排；`metadata.counts` 仍 5 键、记忆走 `memory_count`/`memory_dropped`。`12a` 子集 55 例绿（**在 13 条活记忆存在下跑**，即更难的那种）；`12b` 全套件 **847 / 0 failed 跑两次**（memories 有数据 / 空表）。我**独立跑**了新增的两个单测文件（41 例）绿 → 与 806+41=847 对得上 |
| **A11** | 文档 | **PASS（附注）** | `docs/DATA_MODEL.md §4.2`、`docs/API.md §14`、`TASKS.md 附录 P`、`workspace/design-memory-policy.md` 均在。我**独立跑** `scripts/check_api_docs.py` → `Common 26 / App-only 0` ✓。API.md §14 明确写了"两道门""上限 10 + dropped 只算截断""审计 reason 不含正文"，以及**"明确不做：不展示本次答案引用了哪几条记忆"**并给了侧信道理由。**附注**：DATA_MODEL §4.2 的 `idx_memories_scope_owner` 列序写成 `(owner_ref, scope)`，迁移里是 `(scope, owner_ref)`——纯文档笔误（见 §6 转出） |
| **A12** | 提交 | **PASS** | `a463658` 存在、17→13 文件（含 2 个新单测 + 2 个新模块 + 迁移）；`git status` 干净；`pyproject.toml` / `uv.lock` **零 diff**；`origin/main = a9cee31`、`ahead 2`、**`a463658` 不在任何远端分支** |
| **A13** | 合规与资源 | **PASS** | 我现场复验：**无 `ece-*` 容器**、**无残留 pytest/uvicorn/alembic 进程**、9 个 Onyx 容器仍在、`RestartCount` = 0；密钥值扫描（含 `postgresql://ece:...@` 形态）**零命中**；`14-compliance-check.txt` 里 swap 6.8/8.0 GiB、MemAvailable ~1.4 GiB **照实写、没写成"没问题"**（这点我认可并记下） |
| **A14** | 证据纪律 | **PASS** | 全部为 HTTP 状态 + JSON + SQL 查表输出 + 单测原始输出；`11-test-db-free-raw.txt` 更狠——把 `DATABASE_URL` 指向**死端口**再跑，绿即证明该层确实不依赖 DB。无"用户截图"字样 |

---

## 2. 我这次独立做了什么（不是读 cc 的结论）

- **独立跑测试**：`pytest tests/unit/test_check_permission_org.py tests/unit/test_memory_policy.py` → 41 例全绿（exit 0），与 `806 + 41 = 847` 自洽。
- **独立跑文档一致性检查**：`scripts/check_api_docs.py` → `App-only 0`。
- **独立读码**：`permissions/engine.py`（org 一行 + 未动其它）、`context/memory.py`（候选收窄 + 逐行授权 + 真实 ACL 日期 + 确定性排序 + 上限）、`context/assembly.py`（`memory` 追加在最后 + 两条返回路径都走 `_memory_step` + `metadata` 只增键）、`api/memory.py`（两道门 + 同事务写 ACL + 命名约束上 `ON CONFLICT`）、`0010_memories.py`、`identity/parser.py`、`main.py`、`seed.py`。
- **现场**：`git log/status`、`origin/main`、`branch -r --contains a463658`、容器与进程、`RestartCount`、密钥形态扫描。
- **追了一条可疑线索**：`12b` 的抬头写"commit under test = `3e4b1e8`"，而交付的 HEAD 是 `a463658` → 我用 `git diff 3e4b1e8 a463658` 核实：**全树只差 `TASKS.md` 16 行**（`src/`、`tests/` 逐字节相同），即那是同内容的一次 amend 前的 hash。**结论：不是证据错位**，但以后请直接标最终 hash（已记入 §5）。

---

## 3. 证据抽查（逐字打开过的原始文件）

`00-baseline.txt`、`00b-fresh-db-chain.txt`、`01-org-identity.json`、`02-subject-matches.txt`、`03-memory-migration.txt`、`04-write-permission-matrix.json`、`05-read-matrix.json`、`06-expiry-and-deleted.json`、`07-audit-provenance.{json,txt}`、`08-compliance-delete.json`、`09-determinism-n5.json`、`10-package-keys-diff.txt`、`11-test-db-free-raw.txt`、`12a`、`12b`（含两轮与"断言未改"声明）、`12c`、`13`、`14`；外加源码抽读（见 §2）。

结论：**全部与 REPORT 描述一致、可复现**；本刀没有 OEI-007/009 那类"数据与报告打架"的问题。

---

## 4. 两处"看起来像问题"的，我追到底了

### 4.1 `test_s32_assembly.py:92` 的封闭 `item_kind` 集合 —— **不是本刀缺陷，是必须带走的脆弱性**

cc 不仅没掩盖，还**主动复现**了它（`12c`）：给 `demo-user-procurement` 造一条可见记忆后，`assert r[0] in ("entity", "relationship")` 立刻红；而全套件今天仍是绿，只因为当时库里剩下的记忆都属 finance（procurement 看不到）。**根因**：这条断言枚举了 `item_kind` 的封闭集合，而本刀**按设计**往 `context_items` 里加了 `item_kind='memory'`。

**为什么我判它不构成 FAIL**：① 该断言是**既有文件**，TASK §8 明令"断言不得改动"，cc 正确地**没有**去改（`git diff a884d41 HEAD -- tests/` 只剩两个新文件）；② 它今天确实不误报（两轮 847/0，我另独立跑了新增 41 例）；③ 断言的"过窄"是**新特性暴露出来的既有脆弱**，不是本刀写错了东西。**但它必须尽快修**——任何未来刀只要给 procurement 或 consulting-a 造出可见记忆，就会**假红**。→ §6 转出第 1 项。

### 4.2 `org:org:consulting-a` 的双前缀 —— **是我的任务书用词造成的**

TASK §5 步骤 1.3 我写的示例 org id 是 `org:consulting-a`，而 §3.3 规定 `object_ref = 'org:<org_id>'` → 渲染成 `org:org:consulting-a`。cc 主动申报了这一点并说明"不做静默重命名，因为 org id 取值是任务书定的"。我认可这个处置：**值一致即正确**，双前缀只是难看。→ 记入 §5 我的缺陷。

---

## 5. 我自己（架构师）的缺陷记录

1. **org id 示例里带了 `org:` 前缀**，导致 `org:org:` 双前缀（§4.2）。教训：任务书给"示例值"时不能与"格式模板"叠前缀。下一刀若要重整 org 命名，**作为数据变更一次性做**，不要零敲碎打。
2. **§3.4 只写了主路径，没写 `insufficient_context` 早退路径**。cc 出于"不让策略分叉"把记忆步骤也挂到那条路径上（并在 API.md §14 写明）。我**追认**这个决定：记忆只取决于调用者，与 root entity 无关；两条路径走同一个 helper 比"一条有记忆一条没有"更安全。
3. **§3.5 把"被拒候选是否进审计"写成"可"**，留下了歧义。cc 选了**不记**（理由：把"memory:7 被拒"写进可被读的审计面，等于给出存在性侧信道），并在代码注释里写明权衡——这是比我的原文更好的取舍，我认可。
4. **证据抬头写中间 hash**（`3e4b1e8` 而非最终的 `a463658`）。内容无差异（§2 已核），但**以后请在最终 commit 之后再跑一次取证或直接改正抬头**，避免审验方每次都去追这条线。

---

## 6. 裁定：**PASS**

理由：A0–A14 全部成立，且关键项由我独立复核（41 个新单测我亲自跑绿；org 分支的 diff 我逐行看过、判定顺序未动；读取路径确认"逐行授权 + 真实 ACL 日期 + 确定性排序 + 上限 10"；合规删除的负例齐备；SPA 逐字节未变；无越界、无密钥、无残留、未 push）。**两处可疑点都不是本刀的实现缺陷**（一处是我用词、一处按规矩转出）。

**转出（移交下一刀 / 需尽快处理）**：

1. **`tests/integration/test_s32_assembly.py:92` 的封闭 `item_kind` 集合必须修**（二选一：把 `"memory"` 加进集合，或改断言其真正的不变量——"每行 decision ∈ {allowed,denied} 且 reason 非空"）。**任何再往 `context_items` 加 item kind 的刀都会踩它**，且它现在会**假红**。→ 我把它写进下一刀的步骤 0。
2. **`docs/DATA_MODEL.md §4.2` 的 `idx_memories_scope_owner` 列序笔误**（文档 `(owner_ref, scope)` vs 迁移 `(scope, owner_ref)`；三处索引名一致）。纯文档，随下一刀一起订正。
3. **`merge_engine` 的 fail-open 降级分支**（承自 OEI-009 §8.1）仍未显式化。
4. **真认证入口**（`X-User-Id` 可自选）——演示讲"同一 query 两个身份不同结果"前必须有。
5. **引擎调用审计持久化**（设计已备，独立小刀）。
6. **凭据耐久化**（PAT 取代 cookie jar）。
7. **OEI-012 的"召回可复现"**（承自 OEI-009 的技术发现）。
8. **演示状态一条命令重建**：`OEI-009/workspace/rebuild_demo_state.sh`（已实测）；本刀新增的记忆演示数据没有对应重建脚本，若将来要在演示里展示记忆，需要一并纳入（下一刀视需求定）。

**值得固化的好做法（写进后续任务书模板）**：

- **DB 无关性用"死端口 `DATABASE_URL`"证明**，而不是靠"我觉得它不连库"（`11` 的做法）。
- **全套件在有数据 / 空表两种状态下各跑一次**（`12b`），把"表状态"当成显式变量。
- **泄漏断言扫整个响应体**，不只扫新字段（`05`）。
- **资源快照照实写**（`14` 写明 swap 6.8/8.0 而非"无问题"）。
