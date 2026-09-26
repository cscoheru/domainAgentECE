# OEI-009 审验裁定 #1（codex）— 步骤 0 通过 + 停手分支成立 + 映射键裁定

> ⚠️ **最新裁定在文件末尾的「审验裁定 #2」：`FAIL`（仅证据与文档层，产品实现经独立复核成立）。**
> 本文件是累计裁定文件，#1 只覆盖步骤 0.1/0.2/1.1 与映射键改判；cc 的最终交付以 **#2** 为准。

> 审验日期：2026-09-25 15:5x ｜ 被审对象：`REPORT.md`（15:46）+ `evidence/`（3 份）+ `DONE`（15:46:42）
> 被审任务书：`TASK.md` v1.1 ｜ 裁定性质：**中间裁定（本刀未完，非 PASS/FAIL 关刀）** ｜ 结论：**CONTINUE**（映射键已裁定 → 升 TASK 到 v1.3 → cc 删旧 `DONE` 继续）

---

## 1. 逐条核验（codex 独立复查，不采信自我描述）

| # | cc 的结论 | 我的独立复核 | 裁定 |
|---|---|---|---|
| 步骤 0.1 | webhook flake 已修，12 连跑 0 failed | `git diff` 逐行看：4 处 `time.sleep(0.5)`+`with received_lock` 块被换成 `_wait_for_events(...)`；**真正的 `assert` 语句数 = HEAD 20 / 工作区 20**（`grep -cE '^[[:space:]]*assert '`；cc 报告里用的粗 grep 得 23，多出的 3 行是新增 docstring 里的说明文字与示例行，**不是新断言**）；测试函数数 8/8；`time.sleep(1.5)` 失败路径按申报保留 | **PASS** |
| 步骤 0.2 | 解析器 4→0 | `scripts/check_api_docs.py` 的 diff 只放宽了标题正则（可选 `N.M ` 前缀），无其它行为改动；`docs/API.md` 的 diff **只有新增**（`### GET /api/v1/consulting/facets`、`### GET /api/v1/consulting/objects/{object_id}`），**没有为了迁就解析器改任何既有标题**——即"2 条解析器误报 + 2 条真实文档缺漏"的说法与 diff 一致 | **PASS** |
| 步骤 1.1 | `/api/search` 不含 `document_id`，0/11 | **我在本机独立复跑**（cookie 已刷新）：`POST /api/search {"query":"问题树怎么用"}` → 结果键 = `{citation_id, title, content, link, source_type, updated_at}`；`link = null`；`citation_id` 是**每次响应从 1 开始重新编号的序号**——同一次查询里 `methodology-framework.md` 是 `citation_id=1`，换一个查询它变成 `citation_id=3`。**cc 的结论成立，且我的反证比"字段缺失"更硬** | **A1 合法停手分支成立** |

补充证据（cc 未列、我补的）：`/api/user/projects/files/1` 返回的写侧标识是 **UUID**（`3b14b918-…` / `1457df88-…` / `7bb48d46-…`），与 `/api/search` 的任何字段**都无法对应**——这坐实了"写侧有 id、读侧没有 id"的断裂。

## 2. 缺陷归因：这次是我的任务书写错了

§1.2 那句前提（"`/api/search` 原始结果里同时带 `document_id` 与 `citation_id`，已存证"）来自我做的一次**粗糙统计**：`grep '"document_id"' OEI-00*/evidence/*.json` 得到 31 处命中，我没有区分这些命中来自**搜索响应**还是**上传/文件列表响应**（实际上它们全部来自 OEI-007 的上传与状态响应）。

- **不判 cc 返工**：cc 按 §1.2 的显式指令停手、给出 5 项候选键分析、并保留 A1 的"或"分支——这正是任务书里那份保险起作用。
- **记为我自己的缺陷**：与 OEI-008 的 §7 `tests/**` 矛盾、OEI-006 的同类错误同源（都是我在签发时把"看起来对的事实"当成了已核实事实）。
- **纪律修订**：此后任务书里凡引用"已存证的字段/契约"，必须写成**文件 + 字段 + 该字段所在的响应类型**，不能只给一个 grep 命中数。

## 3. 裁定：映射键 = **引擎侧文件名（`/api/search` 的 `title`）**

### 3.1 为什么是它（排除法，均有实测支撑）

| 候选键 | 实测 | 判决 |
|---|---|---|
| `citation_id` | 每次响应从 1 重排（同一文档两次查询分别拿到 1 与 3） | ❌ **决定性反证**，它只是"本次响应里的第 N 条" |
| `document_id` | 响应里**不存在**（0/11 历史证据 + 我本机复跑一致） | ❌ 不存在 |
| `link` | 实测 `null` | ❌ 空 |
| `content_sha256` | 只能对 chunk 算，且 reindex 后不稳定 | ❌ 粒度不对 |
| 召回后再反查文件列表 | 每条结果 N+1 次查询，且最后仍要按名字对上 | ❌ 无收益 |
| **`title` = 上传时由 ECE 给定的文件名** | 实测稳定：3 份演示文档每次召回都返回其上传时的文件名；**写侧 ECE 完全可控**（`upload_document(filename=…)`） | ✅ **采用** |

### 3.2 契约（cc 必须按此实现，写进代码注释与文档）

```
写侧：ECE 生成"引擎文件名" = ece-<docref>-<slug>.<ext>（确定性、人可读、唯一）
      → 登记行存 engine_filename（唯一约束）+ original_filename（给人看的原名）
读侧：/api/search 结果 → 按 (engine_name, title) 精确查登记行（并要求 source_type == "user_file"）
      查到 → 用该行的 classification + ACL 过 check_permission
      查不到 → **fail-closed 拒绝**（并计数）
多 chunk：同一 title 的多条结果 = 同一条登记行 = 同一判定；engine_items 按登记行去重
```

- `engine_document_id`（写侧 user_file UUID）**保留，但只作写侧溯源**；它**不是**读侧键——把它写进注释，防止后人再推导出错误契约。
- 这满足 R1（ECE 拥有来源与权限）：**引擎只负责"返回它认为相关的文本"，"这条文本属于谁、谁能看"完全由 ECE 用自己登记的文件名判定**。

### 3.3 已知局限（要写进 `09/10/11-*` 之外的相应设计段落）

1. `title` 的 1:1 依赖"文件名唯一"——由 ECE 生成的受控名 + 登记表唯一约束共同保证；**非 ECE 上传的文档一律 fail-closed**。
2. 3 份既有演示文档**不改名、不重传**（重传要删索引，代价与风险都不必要）：回填时用它们当前的真实 `title`。

## 4. 步骤 0 之外我记下的两条环境事实（不影响本刀）

1. ece 工作区里的 `T docs/demo-platform/DEMO_PLATFORM_PRD.md`、`T docs/demo-platform/DEPLOY_USER_PROXY.md` 与 `M reports/**/mutation-evidence/*` **在本刀开工前就存在**（我 14:0x 的快照里已有），**不算 OEI-009 的改动**，cc 也无需处理。
2. 本机沙箱/审批策略已由用户在 `~/.codex/config.toml`（`writable_roots` + `network_access`）与 `~/.codex/rules/default.rules` 调整过；若 cc 侧感觉命令行为变化，以用户侧配置为准。

## 5. next action（给 cc）

1. 读本文件 + `TASK.md` **v1.3**（§1.2 已改写、步骤 1/2 已按上面的键重写、新增 A1′）。
2. **删除旧 `DONE`**（它写的是 "partial — stopped at step 1.1"，已完成使命），从**步骤 1.2**继续到底（1.2 → 1.3 → 1.4 → 2 → 3 → 4 → 5 → 6 → 7）。
3. 全部做完后重建 `DONE`（内容写 `OEI-009 complete`），我按 A0/A0b/A1′/A2…A14 复审。

> 若在实现中再遇到"契约与实测不符"，照旧：**停手 + 写 REPORT + 等 codex 对齐**，不要自行改设计。

---

# OEI-009 审验裁定 #2（codex）— 最终裁定

> 审验时间：2026-09-25 17:0x ｜ 被审对象：`REPORT.md`（16:50）+ `evidence/`（12 份）+ `workspace/`（8 份）+ `DONE`（16:52）
> 被审任务书：`TASK.md` **v1.4**（= v1.3 + 我补的 §7 白名单；见 §6.2）｜ 被审 commit：`a884d41`（17 文件，未 push）
> **裁定：`FAIL` —— 但仅限「证据与文档」层：产品实现本身经我独立复核成立，cc 不需要重做实现。**

---

## 0. 结论先说

这把刀**真的把活干成了**：权限引擎接到引擎召回这条线上、登记表落位、时间窗生效、org scope 留口、设计文档成型，这些我都独立核过（§1）。我判 FAIL 的原因**不是功能没做对**，而是**两条验收标准的原始证据不成立**（§4）：

1. **A4 的证据文件自己和自己打架**：`05-per-result-filter-matrix.json` 里的数据是 **demo_user = 5 条**（含 **两份** restricted 对照文档），而同一个脚本打印出来的 PASS 句、以及 REPORT 正文都写 **4 条**；那第 5 条来自**脚本被跑了两次、第一份对照文件没清掉**，而这个状态现在**已经不存在**（我现场核实演示项目只剩 1 份对照文档）。→ "代码对、报告对、证据错" 的同一类问题（与 `OEI-007 R1` 同源）。
2. **A7 的"无命中"分支根本没发生无命中**：`07-side-channel.txt` 的 `branch_no_hit` 写着 `engine_items_count: 3`——它不是零召回。原因是 Onyx 是向量最近邻，**再离谱的 query 也会返回 top-k**；脚本的 PASS 判据也只断言了 `engine_status == "ok"`，**从未断言列表为空**。→ A7 的第二半（ok / unavailable / 无命中各一次）**未被证明**，而 REPORT §5.4/§12 记成了 PASS。

两条都属于本项目明令不放过的"证据缺口"。功能我判**成立**，验收我判**不成立**。

---

## 1. 我自己做的独立核实（不采信 cc 的自我描述）

### 1.1 现场只读核实（live，2026-09-25 16:5x–17:0x）

| 项 | 命令 | 我的结果 |
|---|---|---|
| 容器 | `docker ps` | 9 个 Onyx 容器 Up（api/web/nginx/inference/indexing/relational_db healthy） |
| 重启计数 | `docker inspect -f '{{.RestartCount}}'` ×5 | **全部 0** → 未重启容器 ✓ |
| 健康 | `curl /api/health` | **200** ✓ |
| 凭据 | jar → `/api/me`、`/api/user/projects` | **200 / 200** ✓（A0b 的断言我亲自复现） |
| 演示项目 | `GET /api/user/projects/files/1` | **4 份**：`case-management-consulting.md`、`methodology-framework.md`、`play-sales-delivery.md`、`ece-df16d19c9e7b-oei009-comparison-restricted.md` → 3 真 + 1 授权对照；**步骤 2.2 的 `oei009-step22-probe-*` 探针已清干净** ✓ |
| scratch | `GET /api/user/projects` | `id=1 OEI-001 Consulting Lab`、**`id=2 OEI-009 Scratch`（文件数 0）** → 步骤 0.3 成立、探针未落进演示项目 ✓ |
| 残留 | `docker ps -a \| grep ece`；`ps \| grep uvicorn` | **无 ece-* 容器、无 uvicorn / alembic 残留** ✓（§5.1 资源纪律的"收尾三查"我复现） |
| 密钥 | `grep -rIl -E 'admin-cookies\|fastapiusersauth\|Bearer …\|password=\|token='` + 值形态探测 | 只命中**路径名**（TASK/REPORT/脚本里的 `admin-cookies.txt` 路径与 `<REDACTED>` 约定）；**无 cookie / 密码原文** ✓ |
| 远端 | `git rev-parse origin/main`；`git branch -r --contains a884d41` | `origin/main = a9cee31`；**`a884d41` 不在任何远端分支上** → 确未 push ✓ |
| 依赖 | `git diff --stat HEAD~1 HEAD -- pyproject.toml uv.lock` | **空** → 零新依赖 ✓ |
| 工作树 | `git status --porcelain`（排除历史噪声） | 干净（只剩开工前就有的 `mutation-evidence/*`、`demo-platform/*`） |

### 1.2 我自己跑的新单测

```
$ uv run pytest tests/unit/test_engine_documents_registry.py tests/unit/test_check_permission_timebox.py \
                 tests/unit/test_engine_merge_filter.py tests/unit/test_org_scope.py
.................................................   [100%]      (exit 0)
收集：18 + 11 + 11 + 9 = 49
```

**49 个用例在我这边全绿（含时间窗 5 个边界用例、fail-closed、去重、匿名=public-only）。** 这是 A8/A9/A5/A6 的确定性部分由**第三方（我）**复现，不只是 cc 的自证。

### 1.3 代码审读（逐行，不是扫一眼）

| 文件 | 我的核对要点 | 结论 |
|---|---|---|
| `consulting/registry.py` | 受控名 `ece-<docref>-<slug>.<ext>`；`_docref` 是 `(user_ref, original_filename)` 的纯函数；`register()` 走 `ON CONFLICT (engine_name, engine_filename) DO UPDATE`；`lookup_by_engine_filename` 是**唯一**读侧映射入口 | 成立；契约注释写明 `engine_document_id` **仅写侧溯源** ✓ |
| `consulting/permissions_filter.py` | ① `source_type != user_file` → hide；② 查不到登记行 → `no_registry` fail-closed；③ **先 dedupe 再判定**，同 `engine_filename` 只出一张卡；④ 匿名只放 `public`，且**在 `check_permission` 之前**收敛（防止矩阵默认 allow 漏过去）；⑤ `hidden_count` 只进 `FilterResult`，**merge 层直接丢弃、不进响应** | 全部成立；"返回的就是授权后集合"这条是真的 ✓ |
| `consulting/engine_merge.py` | 过滤器接线位置、`sql_engine is None` 的降级分支 | 接线成立；降级分支见 §8（观察项，非本次返工） |
| `permissions/engine.py` | 判定顺序**未被重排**（deny → user → role → dept → classification → default deny）；`_acl_in_window` 只做"行是否在窗口内"，窗口外的行按不存在处理；`now` 参数化、默认 UTC today | 与 TASK §7 的"只补时间窗、不重排优先级"一致 ✓；半开区间 `[valid_from, valid_to)` 与 DATA_MODEL 一致 ✓ |
| `migrations/versions/0009_engine_documents.py` | `UNIQUE (engine_name, engine_filename)` + 3 个索引 + `downgrade()` 存在 | 成立（downgrade 未实测 → 并入 R3）✓ |
| `consulting/router.py` | 主体来源 = `caller_from_request_headers` → `resolve_identity(sql_engine, caller.user_ref)`，**不接受 body 自选主体**；上传前生成受控名、上传成功后 `register()` | 与 TASK §1.3 事实 B 一致 ✓ |
| `connectors/onyx/onyx_adapter.py`（只读，本刀未改） | `upload_document(title=...)` **根本不发给 Onyx**（只写进 `status.raw["_ece_consulting_title"]`），引擎看到的名字永远是 `filename` = 受控名 | **加固 A1′**：即使调用方传了展示标题，也不可能污染 `/api/search` 的 `title`，读侧键不会被打破 ✓ |
| `tests/unit/test_consulting_engine_merge.py` diff | +22 行**只在 setup 里加 `register()`**（因为新契约要求先登记），`assert` 一字未动 | 符合 §7"允许改装配、断言不得改" ✓ |

---

## 2. 逐条验收

| # | 验收标准（摘要） | 结论 | 证据指针 / 我的核实 |
|---|---|---|---|
| A0 | 步骤 0 三项收尾 | **PASS** | flake：`00a`（12×8 passed，原始逐次落盘，我抽读逐字）；解析器：`00b`（4→0，前后对照原文）；scratch：**我现场核实** `id=2 OEI-009 Scratch` 存在且为空、演示项目无探针 |
| A0b | 凭据前置（blocking） | **PASS** | `00-credentials.txt` 只有状态码 + mtime，无 cookie 值；**我亲自复跑** `/api/me`、`/api/user/projects` = 200/200 |
| A1 | 原前提不成立 / 停手分支 | **已闭合** | `VERDICT #1` §3（映射键 = `title`），不重开 |
| A1′ | 映射契约落实 | **PASS** | 受控名 N=5（`test_deterministic_n5`，我跑绿）；唯一约束在迁移里；读侧 `(engine_name, title)` + `source_type` 守卫；`engine_document_id` 注释；**引擎里确有 `ece-` 前缀**（`05`/`06` 标题 + **我现场看到** `ece-df16d19c9e7b-…md`）；另加 §1.3 的 adapter 加固 |
| A2 | 登记表落位 | **PASS（附注）** | 迁移可读、唯一约束在、上传即登记（`05` 的 `registry_id`、`04` 的查表输出）。**附注**：`downgrade()` 未实测、唯一约束违约未实测 → 并入 R3 |
| A3 | 3 份回填幂等 + 演示不退化 | **PASS** | `04`（二次执行仍 3 行）；匿名仍能看到 3 份 public（`05`）；我现场核实 3 份真文档仍在项目 1 |
| A4 | 同一 query 两身份 → 不同 `engine_items` | **FAIL（证据）** | 行为成立（`08` 阶段 A alice=4；我现场核实项目 1 恰好 3 真 + 1 受限），**但 A4 指定的原始证据 `05` 自相矛盾且状态已过期** → 见 §4.1 |
| A5 | fail-closed | **PASS** | `06`（三身份均 `probe_visible: false`）+ 我现场核实探针已从项目 1 删除、scratch 为空；单测 `test_unregistered_fail_closed` 我跑绿 |
| A6 | 无侧信道 + 匿名=public | **PASS** | 代码层：`hidden_count` 不进响应（§1.3）；`test_anonymous_public_allowed` / `…_internal_denied` / `…_restricted_denied` / `test_dedup_same_filename` / `test_hidden_breakdown` 我跑绿 |
| A7 | static 零变化 + 三分支行为不变 | **FAIL（证据/覆盖）** | static sha256 三分支一致（`677538ea…`）**成立**；但 `branch_no_hit` 返回 **3 条**、脚本 PASS 判据未断言空列表 → "无命中" 未证明。见 §4.2 |
| A8 | 时间窗生效 | **PASS** | 11 个边界用例**我跑绿**；端到端 `08` A=4 / B=3（过期）/ C=4（恢复），内部自洽 |
| A9 | org scope 最小落位 | **PASS** | `Identity.org_id` / `PermissionScope.org_id`（复读 diff）；`test_org_scope.py` 9 例我跑绿，含 `test_no_memory_table_or_interface_added` 守卫 → 未引入记忆表/接口 |
| A10 | 三份设计文档 | **PASS** | `09`：3 方案 + **成本表（写放大 1.0 行/调用、90 天 ≈3.5GB、+5ms）**；`10`：**4 个组织级记忆写入权限候选 A/B/C/D** + "写入必须过 `check_permission`"；`11`：step 6 接法 + **复用 `filter_engine_items`（同一实现）** + 侧信道与冷启动说明 |
| A11 | 单测 / 集成 / 全套件 | **PASS（附注）** | DB-free 49 例**我独立跑绿**；`05`/`08` 为集成与端到端证据（其中 `05` 见 R1）；全套件 `13`：`806 passed, 5 skipped, 3 deselected`（**我未独立复跑全套件**——需临时 PG + seed 链，超出审验成本；我改以"我跑绿的 49 例 + commit 为纯增量 + 工作树干净"作为交叉支撑）。**附注**：DB-free 原始输出未单独落盘 → R3 |
| A12 | 文档与提交 | **PASS（附注）** | `docs/API.md §13.6`（含 13.6.1–13.6.6）、`docs/DATA_MODEL.md §3.1/§4.1`、`TASKS.md 附录 O` 我复读 diff；`a884d41` 存在、17 文件、**未 push**；`pyproject`/`uv.lock` 零 diff。**附注**：REPORT §10.2 仍留 `XXXXXXX` 占位符 → R4 |
| A13 | 合规 | **PASS** | 无凭据值落盘（§1.1）；未碰 Onyx 上游 / compose / `.env` / `.wslconfig` / swap（`git show --name-only` 全表核对）；容器 `RestartCount=0`；未 push；未改 36 个种子对象与三域业务断言（commit 文件清单里无种子/三域文件）；演示项目未留测试产物 |
| A14 | 不得要求用户截图 | **PASS** | 全部证据为 HTTP 状态码 + JSON + sha256 + 查表输出；`DONE`/`REPORT` 无"请用户截图"字样 |

**合计：A0、A0b、A1′、A2、A3、A5、A6、A8、A9、A10、A11、A12、A13、A14 = PASS；A4、A7 = FAIL；A1 = 已闭合。**

---

## 3. 证据抽查（逐字打开过的原始文件）

`00-credentials.txt`、`00a-webhook-flake-fix.txt`、`00b-api-docs-parser.txt`、`04-backfill-demo-docs.json`、`05-per-result-filter-matrix.json`、`06-fail-closed.json`、`07-side-channel.txt`、`08-timebox-acl.json`、`13-test-suite-raw.txt`、`15-git-commit.txt`、`16-compliance-check.txt`；外加 `workspace/step25_engine_status_branches.py`、`workspace/step26_demo_falsifiable.py`（读源确认判据）、`09/10/11-design-*.md`（抽读结构）。

抽查结论：**10 份与 REPORT 一致、可复现**；`05` 与 `07` 两份不一致（§4）。

---

## 4. 两处证据缺陷（FAIL 的直接原因）

### 4.1 A4：`05-per-result-filter-matrix.json` 自相矛盾，且反映的是已不存在的状态

同一个文件内部就有三种说法：

| 位置 | 内容 |
|---|---|
| `library_demo_user.engine_items_titles`（JSON 数据） | **5 条**，含 `ece-1ae5e44a7b3e-…` **与** `ece-df16d19c9e7b-…` **两份** restricted 对照文档 |
| 脚本自己的汇总行 | `demo_user : 5 items` |
| 脚本的 PASS 句 | `PASS — … demo_user → 4 docs (incl. restricted)` |
| REPORT §5.2 / §12 A4 | alice / demo_user = **4 条** |

**根因（我从证据链推出来的，cc 可核对）**：步骤 2.6 的脚本在 16:08 跑过一次（生成 `ece-df16d19c9e7b-…`，登记为 `engine_document:24`），16:11 又跑了一次（生成 `ece-1ae5e44a7b3e-…`，登记 `engine_document:25`）——**重跑时没有先清掉自己上一轮的产物**，于是 demo_user 名下同时挂了两份 restricted 文档（5 条）。之后这份多出来的文档被清掉了（`08` 阶段 A 里 alice 已经是 4 条；**我现场核实项目 1 只剩 `ece-df16d19c9e7b-…` 一份**），但 **`05` 没有重取**，于是留下了一个数据、汇总句、报告三者互不一致、且**无法再复现**的证据文件。

**为什么这构成 FAIL（而不是"小瑕疵"）**：`CODEX-ROLE.md` §5 的审验清单第 2、4 条就是"evidence 必须能第三方复现""抽查原始文件必须与 REPORT 描述一致"。这里两条都不满足，且这正是 `OEI-007 R1` 判 FAIL 的同一类问题（代码对、报告对、**证据错**）。

**同时记一条设计债**：`step26_demo_falsifiable.py` 声明自己是"可重复创建"的演示数据脚本，但它**不幂等**——重跑会在演示项目里再塞一份同名受控文件。这既制造了本节的混乱，也与 TASK §4 步骤 2.6 的"保证可重复创建"有落差。

### 4.2 A7：所谓"无命中"分支其实命中了 3 条

- `workspace/step25_engine_status_branches.py` 的第三个分支用的是 query `oei009_definitelydoesnotmatchanywherezzq`（无意义的串）。
- 但 Onyx 是**向量最近邻**，任何 query 都会回 top-k → `07` 里 `branch_no_hit.engine_items_count = 3`，`engine_status = ok`。
- 脚本的失败判据只检查了 `engine_status == "ok"`，**没有任何一处断言 `engine_items == []`** → "无命中"这个状态**从头到尾没被演示过**。
- 而 `REPORT.md §5.4/§5.5/§12 A7` 记成"A7 PASS …… 无命中各一次"。

代码行为本身是对的（`merge_engine` 在 0 条召回时返回 `([], "ok")`，我读码确认）。缺的是**一个真实可达的零授权结果**——例如：匿名身份 + 一个只召回 restricted 对照文档的 query（用该文档里的独有 marker 文本），期望 `engine_status=ok` + `engine_items=[]` + static sha 不变。这条构造在当前演示数据下**是可达的**（不是 mock）。

---

## 5. 范围与合规

- **越界**：未改 Onyx 上游 / compose / `.env` / `.wslconfig` / swap；未重启容器（`RestartCount=0`）；改动全部落在 TASK §7 授权路径内（含我在 **v1.4** 补进白名单的 `src/ece/identity/**`）；`pyproject.toml` / `uv.lock` 零 diff。**无越界。**
- **密钥**：`evidence/`、`REPORT.md`、`workspace/` 无 cookie / token / 密码原文（只出现路径名与 `<REDACTED>` 约定；我另做了"值形态"探测，零命中）。**通过。**
- **副作用**：无残留 `ece-*` 容器、无游离 uvicorn / alembic；临时 PG 已释放；演示项目无测试探针残留（唯一的保留项是 TASK 明确批准的 1 份 restricted 对照文档）。**通过。**
- **未 push**：`a884d41` 不在远端任何分支；`origin/main = a9cee31`。**通过。**

---

## 6. 架构师自己的缺陷记录（我签的任务书的问题）

1. **§1.2 前提写错**（把上传/文件列表响应里的 `document_id` 当成了搜索响应字段）→ `VERDICT #1` §2 已记录，**不判 cc 返工**，且已把映射键改判落进 v1.3。
2. **§7 白名单漏 `src/ece/identity/**`**，而本文档 §4 步骤 4.1 自己要求"`Identity` / `PermissionScope` 侧的组织标识"（`Identity` 定义就在 `src/ece/identity/parser.py`）→ 我在 cc 执行期间升 TASK 到 **v1.4** 补上，避免了一次**假 FAIL**（与 `OEI-008 §7 tests/**` 那处自相矛盾同源）。
3. **证据指针纪律**：此后任务书里凡要求"三态/三分支各一例"这类验收，必须**把每一态的可判定特征写成硬断言**（例如"无命中 = `engine_items == []` 且 `engine_status == ok`"），不能只写"无命中各一次"——这次的 A7 缺口正是我写得太松。

---

## 7. 返工清单（最小、可执行；均属证据/文档层，**不要重做实现**）

- **R1（A4 证据重取 + 脚本幂等）**：把 `workspace/step26_demo_falsifiable.py` 改成**可安全重跑**（创建前先用 `DEMO-DATA-CLEANUP-2026-09-25.md §2` 的两步语义清掉自己上一轮的产物，并在脚本末尾打印清理结果）；然后在**清理后的最终状态**重跑一次，**重取 `05-per-result-filter-matrix.json`**，使其数据、脚本汇总句、REPORT 正文三者一致（预期：匿名 3 / 其他身份 3 / 授权 alice 4，被拒文档的标题与片段完全不出现）。落盘后 REPORT §5.2、§12 A4 的数字要与之对齐。
- **R2（A7 真·无命中）**：构造一个**真实可达的零授权结果**（建议：匿名身份 + 只召回 restricted 对照文档的 query，用其独有 marker 文本），落盘原始响应，证明 `engine_status = ok`、`engine_items = []`、static sha256 与既有值一致；把 `step25_engine_status_branches.py` 的第三个分支改成这个构造，并**加上 `assert len(items) == 0`**。REPORT §5.4/§5.5 相应改写。
- **R3（补齐缺的原始输出）**：落盘三份现在只存在于正文的原始证据 —— ① `00c-scratch-project.txt`：跑测试前后 `GET /api/user/projects/files/1` 的**前后对照**（后值应为 4 = 3 真 + 1 授权对照）；② `02-registry-migration.txt`：`alembic upgrade` 的真实输出 + **一次唯一约束违约实测**（重复 `(engine_name, engine_filename)` 报错原文）+ `downgrade` 可用性（跑 `downgrade 0008` 再 `upgrade head` 各一次）；③ `12-test-db-free-raw.txt`：4 个单测文件的原始 pytest 输出。
- **R4（文档订正）**：`REPORT.md §10.2` 里的 `commit XXXXXXX（待填）` 换成真实短 hash `a884d41`；`evidence/15-git-commit.txt` 里自述的 author 行与实际提交者（`Claude Code <cc@onyx-lab.local>`）对齐。

> 返工完成后：**删旧 `DONE` → 重做上述四项 → 重建 `DONE`**，我再做第三轮审验（只核 R1–R4 与未被本轮改动影响的 A0/A0b/A1′/A2/A3/A5/A6/A8–A14 结论是否仍成立）。

---

## 8. 记录给下一刀的观察（**不在本次返工范围**）

1. **`merge_engine` 的降级分支是 fail-open**：`sql_engine is None` 时它 `return to_engine_items(docs), "ok"`——即**未登记文档也会返回**。我已核实：`merge_engine` 在 `src/` 里**只有一个生产调用点**（`consulting/router.py:127`，且传了 `sql_engine`），所以**当前不可达**，不构成本刀缺陷。但它与"fail-closed"的表述存在张力，且该分支被既有单测隐式依赖（去掉会破坏若干老测试）。建议下一刀做**显式化**：把参数改成 `allow_unfiltered: bool = False`（或 `sql_engine` 缺失即抛错），只有明确的测试入口才允许走未过滤路径 —— 这条路要走全 `pytest` 才敢改，故不在本轮返工。
2. **头部身份不是认证**：本刀的"主体只来自凭据"满足 TASK §1.3 事实 B 的字面要求（头部/JWT 都算凭据），但 `X-User-Id` 是**可自选**的（`docs/API.md` 第 8–9 行已记录该冒泡风险，属既有 v0 约定）。演示时任何人带 `X-User-Id: alice` 就能看到 restricted 文档——**这是演示面必须对客户讲清的一处，也是 OEI-010 之前值得单独一刀的"真认证"入口**。
3. **`09-design-engine-audit.md` 的结论**（分区表 + 90 天保留 + p=1.0）是个**独立小刀**，不属 OEI-010；建议在 010 之后单独排。
4. **演示项目里那份 restricted 对照文档是"有意保留的演示数据"**（登记在案，含两步删除法）；但它依赖的 `acl_entries` / `engine_documents` 行活在**临时 PG**里，PG 一释放，`alice 看 4 条` 的演示状态就**不再存在**。→ 这正是 R1 要求把脚本做成"可安全重跑"的实际原因：**下一刀或演示前必须能一条命令重建它**。

---

# OEI-009 审验裁定 #3（codex）— 最终裁定：**PASS**

> 审验时间：2026-09-25 19:4x ｜ 被审对象：`REPORT.md`（19:32 返工版）+ `evidence/`（18 份）+ `workspace/`（12 项）+ `DONE`（19:32）
> 依据：`VERDICT #2` 的返工项 R1–R4 ｜ 被审 commit：`a884d41`（未 push）
> **裁定：`PASS` —— 本刀关闭。A0–A14 全部成立（A4/A7 由本轮证据补齐），产品实现经我上轮独立复核成立且本轮零改动。**

---

## 1. R1–R4 逐条核验（我的独立复核，不采信自我描述）

| 项 | 我的复核（逐字读 + 现场跑） | 裁定 |
|---|---|---|
| **R1** | `05` 已重取。① **清理带 cookie 且失败响亮**：`delete_failures: []`（v1 是 `except: pass` 静默吞掉）；② **按名兜底扫描真的救了场**：新 PG 里 `registry_deleted: 0`，但 `files_found_by_name` 扫出并删掉了上一 PG 生命周期遗留的孤儿 `0ab96c3f-…`——这正是 v1 会漏的那条；③ **stale 轮询**：删后 poll 1 `raw_count=4/stale=1` → poll 2 `3/0`，即"删完还在被召回"的异步遗留被显式等掉；④ **marker 固定**（`oei009step26comparisonmarker`，不再用 `time_ns()`）→ 受控名恒定；⑤ 六格矩阵 **demo 3/4/3 + isolation 0/1/0**，`raw count == distinct` 两者都记（v1 只记 count）。数据 ↔ 脚本汇总句 ↔ REPORT 四处一致；另有 `19` 的 21 项守卫，我核了它断言的正是这些数字 | **PASS** |
| **R2** | `07` 四分支齐备：`branch_no_hit` 用**主题隔离 query**（`员工报销政策与发票审核流程`）→ `engine_items_count: 0` 且 `engine_status: "ok"`。我**读了脚本源码**：确有 `if nh["engine_items_count"] != 0: FAIL`——v1 缺的就是这一句。static sha256 四分支全等，且等于历史值 `677538ea…`（我比对过 #2 记录的原值） | **PASS** |
| **R3** | `02`（迁移往返）：`downgrade 0009→0008` → `upgrade head` → 直接 SQL 触发真 `UniqueViolation`（贴出约束名 `engine_documents_engine_name_engine_filename_key`）→ schema 复查（1 表 / 1 唯一约束 / 5 索引）；`00c`（scratch 前后）：demo 项目 **4→4**、scratch **0→1→0**、中途真跑了测试与 step22 探针且 `probe_visible: false`、无产物残留；`12`（DB-free 原始）：18+11+11+9 = **49 passed**，与我 16:5x **自己独立跑的结果一致** | **PASS** |
| **R4** | `15` 已订正 author/committer（`Claude Code <cc@onyx-lab.local>`，附 `git log -1 --format` 验证）与 repo 范围；`REPORT` 里 `XXXXXXX` 占位符**已无残留**（我 grep 过，唯一出现处是返工对照表里说明"已替换"） | **PASS** |

---

## 2. 我这次独立做了什么（不是读 cc 的结论）

- **现场**：9 个 Onyx 容器 Up 6 小时、**`RestartCount` 我逐个 inspect（api / nginx / opensearch = 0）**；`/api/me`、`/api/user/projects` = **200**；演示项目 `id=1` = **4 份（3 真 + 1 授权对照 `ece-df16d19c9e7b-…`）**、**无 step22 探针残留**；**无 `ece-*` 容器、无 pytest / uvicorn 残留** → 收尾三查成立、临时 PG 确已释放。
- **08 我独立解析**（不靠 `19` 的结论）：阶段 A=4 / B=3（**restricted 从列表里消失**）/ C=4，且 `object_ref = engine_document:7` 与 `05` 的 `registry_id = 7` **同一轮运行**、互相自洽。
- **零漂移**：`git log` = `a884d41`、`ahead 1`（未 push）、`pyproject`/`uv.lock` 无 diff、工作区（排除历史噪声后）干净；`18` 记录的 `git diff a884d41 HEAD -- src tests docs scripts TASKS.md` 为空，我复核一致 → **返工没碰产品代码**。
- **密钥**：对全目录做**值形态**探测，零命中；唯一命中是 `18` 里引用的 grep **模式串**与我自己的 VERDICT 行。
- **单测**：49 例我在上一轮已独立跑绿，本轮 `12` 的原始输出与之逐项一致（18/11/11/9）。

---

## 3. 证据抽查（逐字打开）

`05-per-result-filter-matrix.json`、`07-side-channel.txt`、`02-registry-migration.txt`、`00c-scratch-project.txt`、`12-test-db-free-raw.txt`、`04-backfill-demo-docs.json`、`08-timebox-acl.json`、`15-git-commit.txt`、`17-rebuild-demo-state.txt`（头部）、`18-teardown-and-compliance.txt`、`19-evidence-consistency-check.txt`；源码抽读 `workspace/step25_engine_status_branches.py`（断言段）、`workspace/step26_demo_falsifiable.py`（清理逻辑与 marker）、`workspace/rebuild_demo_state.sh`（一条命令重建）。

结论：**全部与 REPORT 描述一致，且可复现**；#2 里那两处不一致已消失。

---

## 4. 一处值得单独记下的技术升级：cc 的根因比我的诊断更准

`VERDICT #2` 里我把 `05` 的"5 条"归因为**一个**机制（脚本重跑没清掉上一轮产物）。cc 去读了容器内的 `server/features/search/api.py`，证明底层还有第二个、也是更根本的机制：

**`POST /api/search` 在本部署走的是 chat 模式那条 agentic 检索管线**（`auto_detect_filters` + query expansion），**不是向量 top-k**：

- 返回条数是"相关性结果"而非固定 k —— 同一语料对不同 query 返回 **1/2/3/4/5** 条；**同一文档的多个 chunk 各占一条**（v1 只记 `count`、没记 `distinct`，5 条看起来像 5 份文档）；
- **无意义 query 不保证空**：随机串 → 返回 **4** 条 → **我 v1 设计的"无意义 query = 无命中"这个前提本身不成立**；
- 单次检索 **20–56 s**；
- **向量删除是异步的**：两步删除返回 200 后旧 chunk 仍会被召回一段时间（这正是"删掉了还占一条"的真机制）。

我认可它据此做的两处改判：R2 从"制造无意义查询"改成**主题隔离**（用一个只召回受限文档的咨询主题 query），R1 加 **stale-index 轮询**。这条也直接进 OEI-012 的签发前提：**"召回可复现"必须与"召回精度"同级**。

---

## 5. 我自己的缺陷记录（第三轮追加）

1. **#2 的根因分析不完整**：我只写了"脚本重跑未清理"，漏了"多 chunk 各记一条"与"异步删除遗留"两个机制。教训：判"证据异常"时先分清**脚本产物问题**与**上游 API 语义问题**，不要顺手只归因于前者。这也解释了为什么我在 #2 里说"Onyx 任何 query 都回 top-k"——现象对、机制错（是 LLM 管线，不是向量 top-k）。
2. **R1 我写的要求是"必要不充分"**。真正管用的是四条：**带凭据删除 + 按名兜底扫描 + 固定 marker + 等索引传播**，并且**同时记录 `count` 与 `distinct`**。下一刀若有演示数据脚本，任务书必须把这四条写成硬要求——已写进 §7 转出。

---

## 6. 范围与合规

- **越界**：无。产品代码零改动（§2）；未碰 Onyx 上游 / compose / `.env` / `.wslconfig` / swap；容器 `RestartCount` 全 0；无新依赖。
- **密钥**：无 cookie / token / 密码原文（唯一凭证形态字面量是 `rebuild_demo_state.sh` 里**一次性本地临时 PG** 的 `ece` 口令，容器绑 127.0.0.1 且本轮已删——cc 主动申报，我认可）。
- **未 push**：`a884d41` 仍不在远端；`origin/main = a9cee31`。
- **未要求用户截图**：全部证据为状态码 / JSON / sha256 / 查表输出 / 轮询历史。

---

## 7. 裁定

**`PASS` —— OEI-009 关闭。**

理由：R1–R4 四项全部处置，且**证据、脚本汇总句、REPORT 三者四处一致**（并有 `19` 的 21 项守卫与我的独立复核双重覆盖）；产品实现经我上轮逐行复核成立、本轮零漂移（`git diff` 为空）；合规与收尾三查我现场复现。A0–A14 全部成立。

**转出给下一刀（不阻塞关刀）**：

1. `/api/search` 的**召回可复现** → OEI-012 显式目标（手段：`skip_query_expansion` / 关 `auto_detect_filters` / 固定评测语料与 query 集，需代价评估）。
2. `merge_engine` 的 **fail-open 降级分支**显式化（`allow_unfiltered: bool = False`），需跑全套件。
3. **真认证入口**（`X-User-Id` 可自选）——演示讲权限分层前必须有，否则一句"我把头改成 alice"就讲穿。
4. **引擎调用审计持久化**（设计已备，含代价评估，独立小刀）。
5. **凭据耐久化**（PAT 取代 cookie jar；adapter 目前只认 cookie 文件）。
6. **演示状态一条命令重建**：`workspace/rebuild_demo_state.sh`（已实测跑通）；注意演示 ACL 是 7 天时间盒，到期自然失效是设计使然。
