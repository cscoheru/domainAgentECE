# OEI-010 执行报告（cc）— v1

日期：2026-09-25 · 执行：cc（Worker 程序员）· 任务书：`onyx-lab/OEI-010/TASK.md`（v1）
提交：`ece` @ `a463658`（**未 push**）· 引擎模式：`ECE_CONTENT_ENGINE=mock` 全程

## 0. 结论

**PASS** — A0–A14 全部通过，全套件 **847 passed / 0 failed**（基线 806 / 0 failed）。

一句话：持久上下文记忆落成，写与读**都**过既有权限引擎；`check_permission`
的判定顺序、`_acl_in_window` 语义、`effect` 取值一律未动；写权限做成了
**数据**（`acl_entries` 里几行 `memory_scope` 行），不是代码分支。

## 1. 范围声明

**做了**（严格按 TASK §5 步骤 0–8）：

| 步骤 | 内容 | 证据 |
|---|---|---|
| 0 | 临时 PG + 迁移 0009 + seed 链 + 基线落盘 | `00-baseline.txt`、`00b-fresh-db-chain.txt` |
| 1 | `resolve_identity` 从 `attributes.org_id` 填 org；四态；增量写不覆盖 | `01-org-identity.json` |
| 2 | `_subject_matches` +org 一条；判定顺序未重排 | `02-subject-matches.txt` |
| 3 | 迁移 0010（可升可降 + 三条约束真违约） | `03-memory-migration.txt` |
| 4 | 写入过权限引擎（9 格矩阵） | `04-write-permission-matrix.json` |
| 5 | 读取在权限判定之后 + 逐条授权 | `05-read-matrix.json` |
| 6 | 失效与 ACL 时间盒 | `06-expiry-and-deleted.json` + `raw/06-*.json` |
| 7 | 合规面：查看 / 删除 / 可追溯 / SPA 零改动 | `07-audit-provenance.{json,txt}`、`08-compliance-delete.json` |
| 8 | 单测 / 集成 / 全套件 / 文档 / 提交 | `09`–`14` |

**没做**（TASK §8 明确排除，且我确实没碰）：LLM 自动抽取、审批流、多租户、
计费、K8s、ERP 写能力、检索调优、种子内容补全；`check_permission` 判定顺序；
`_acl_in_window` 语义；`effect='write'`；第二套权限机制；SPA 记忆展示；
新依赖；Onyx 上游 / compose / `.env`；任何容器的 restart/stop/down/rm。

## 2. 逐步实测结果

### 2.1 A1 — org 来源落地（PASS）

四态实测：procurement / finance / admin → `org:consulting-a`；engineering →
`org:consulting-b`；无 `org_id` 键的探针 → `None`；未知用户 → `None`。
后两态**用"键不存在"而非"键为空"**区分：无 org 探针的 `attributes` 里根本没有
`org_id` 这个键。

`upsert_identity` 的增量写用 JSONB `||` 合并，**前后对照**证明 `department` /
`roles` / `is_management` 一字未动，且**不带 `org_id` 的写入是 no-op**（向后兼容）。

### 2.2 A2 — org 分支（PASS）

`git diff` 证明 `_subject_matches` **只多一条规则**，`check_permission` 的
allow 侧仍是**对 `acl_entries` 按行序的单次遍历**，没有新增 pass、没有新增
优先级层。四态单测含 `org_id=None`、空串不命中、空 `subject_ref` 不命中、
org 行在时间窗外不命中，外加三条回归（user/role/department 仍匹配、
不匹配的 subject kind 仍拒绝、无 ACL 命中时分级矩阵仍运行）。

### 2.3 A3 — 迁移 0010（PASS）

升降往返：`downgrade -1` 后表数 0，`upgrade head` 后表数 1，约束与索引完整。
三条约束**真违约**验证，打印的是**数据库自己报的**约束名：
`uq_memories_scope_owner_ref_statement`、`ck_memories_scope`、`ck_memories_confidence`。

### 2.4 A4 — 写入过权限引擎（PASS，9 格 ≥ 要求的 6 格）

矩阵把**两道门**分开：主体门（`owner_ref` vs 凭据）与授权门（`memory_scope`
对象上的 `check_permission`）。9/9 符合预期：自写自 200、写他人 403（主体门）、
org 无角色 403（授权门）、org 有角色 200、**org_admin 写别的 org 403（主体门）**、
无 org 403、**无授权者写自己的 scope 也 403（fail-closed）**、无凭据 400。
8 次写入尝试只落 2 行，且每个新行恰好 1 条自动 allow ACL；重复创建返回
**同一行** `created=false`，行数不变。

### 2.5 A5 — 读取在权限判定之后（PASS）

同一条 `POST /api/v1/context` 发给 5 个身份：

| 调用者 | org | 注入的 user-scope | 注入的 org-scope |
|---|---|---|---|
| finance | A | 自己的 | A 的 |
| procurement | A | 自己的 | A 的 |
| engineering | B | — | B 的 |
| 无 org 探针 | — | — | — |
| 未知用户 | — | — | — |

**泄漏断言是对整个响应体做子串检查**，不是只看 `memory[]`——一条不该出现的
statement 出现在 `documents` / `sources` / 错误串里同样算失败。5 个身份
`forbidden_statement_hits_anywhere` 全为 `[]`。另外证明：org 记忆在两个 A 用户
之间**共享**，user 记忆在同 org 两人之间**不共享**，不同 org 的集合**不相交**。

### 2.6 A6 — 失效与时间盒（PASS）

- `expires_at` 已过 → 不注入；`deleted_at` 非空 → 不注入，且**行仍在**
  （`deleted_at` 已写，软删而非硬删）。
- ACL `valid_to = 昨天` → org 记忆**立即失权**，改回 `NULL` → **恢复**（两次
  原始响应落 `evidence/raw/06-*.json`）。

关键的**归因证据**：关窗前后 `select_memory` 的 `candidates` **都是 6**，
而 `items` 从 6 降到 5。候选数不变、注入数减一 → 拒绝发生在**授权步**，
不是被 SQL 提前滤掉，也不是因为行被删/过期（实测该行 `deleted_at` 与
`expires_at` 均为 `NULL`）。

### 2.7 A8 — 可追溯 + 无 UI（PASS）

被注入记忆在 `context_items` 落 `item_kind='memory'`、`decision='allowed'`、
`reason='acl:allow-user'`（**规则名，不是记忆正文**）；`GET /api/v1/audit/context/{request_id}`
owner 可读、他人 403。**软删之后审计仍在**（条数不变，trace 仍查得到）。
`ece/demos/spa/**` **3 个文件逐字节哈希等于 HEAD**（`git diff` 为空是必要条件，
不是充分条件，所以做了内容哈希对照）。

### 2.8 A9 — 合规删除（PASS）

单条软删 + 幂等（`already_deleted=true`）；**删他人 403 且行未被改动**；
自己的全量删只删自己的；**org 全量删无权限 → 403 且一条都没删**（负例）；
`include_inactive=true` 放宽的**只是活跃度**，engineering 在该模式下也看不到
finance 的记忆。

### 2.9 A7 — 确定性（PASS）

N=5 次同请求，`memory[]` 的 sha256 **完全一致**（含顺序）。13 条候选 → 注入
**恰好 10** 条 → `memory_dropped=3`，与**独立从库算出**的截断数一致（不是拿
应用自己的计数器对照自己）。被保留的 10 条是规则选出的那 10 条
（org 优先，组内 `created_at DESC, id DESC`）。

### 2.10 A10 — 既有契约不回归（PASS）

`ContextPackage.to_dict()` 三方对照（pre-cut 源码 / 当前源码 / **运行时**）：
pre-cut 的 **11 键是不变前缀**、顺序未变、**只追加** `memory` 在最后；
`metadata.counts` 仍是原来的 **5 键**（`entities/relationships/documents/rows/denied`），
记忆条数走 `metadata.memory_count` / `memory_dropped`，**没有混进 `counts`**。

全套件 **847 passed / 5 skipped / 3 deselected / 0 failed**，跑了**两次**：
memories **有数据** 与 **空表** 各一次，都是 0 failed（对照基线 806 passed）。
847 = 806 + 41 条新增 DB-free 单测。DB-free 层另在**不可达的 `DATABASE_URL`**
下跑（`127.0.0.1:1`）仍 **50 passed** —— 这比"没连库"的说法更硬。

### 2.11 A11 — 文档（PASS）

`docs/DATA_MODEL.md §4.2`（表 + 两个 scope 的可见性规则 + `memory_scope`
写权限对象）、`docs/API.md §14`（4 个端点 + 注入语义 + 合规删除 + **明确写
"不展示用了哪几条记忆"**）、`TASKS.md 附录 P`（P.1–P.8）。
`make check-api-docs`：**App-only 0**。`scripts/check_schema.py` 退出码 0，
`memories` 表与 3 个索引与库一致。

### 2.12 A12 — 提交（PASS）

`ece` @ **`a463658`**，13 个文件（5 新增 + 8 修改），**未 push**
（`main...origin/main [ahead 2]` = 本刀 + 上一刀的 `a884d41`）。

## 3. 确定性 / 重复性

- **N=5 逐字节一致**（A7），断言含顺序。
- **同一脚本重复跑**：`step4` 每次先删自己的探针行再跑，两次运行结果一致；
  `step3` 的违约探针全程在**回滚事务**里，无副作用、可重跑。
- **种子收敛**：`make seed` 第二次 `Total created: 0`，428 实体 / 1200 关系不变；
  4 个演示身份的 `org_id` 与角色、6 条 `memory_scope` ACL 行均收敛到声明态。
- 确定性顺序用**全序键** `(created_at, id)` 实现，不依赖 Postgres 的行返回顺序。

## 4. 资源与副作用

- **临时 PG 已释放**：`ece-pg-oei010` 已 `docker stop` + `docker rm`；端口 55432
  不再监听；无遗留卷。
- **三查落盘** `14-compliance-check.txt`：
  1. **进程**：无非本刀进程。用 **cgroup** 归因（不看 cmdline 文字）——两个
     `python -m model_server` 落在 `docker-*.scope` 里，是 Onyx 的。
  2. **容器**：9 个 Onyx 容器仍 `Up 7 hours`（uptime 未变）；5 个 Exited 容器
     （postgres/redis/qdrant/2×hello-world）早于本会话 8–9 天，未触碰。
  3. **内存 / swap**：**如实报数**——swap 6.8/8.0 GiB、MemAvailable ≈1.4 GiB。
     这是**既有**压力：宿主 Ollama llama-server 3.9 GB、OpenSearch 2.0 GB、
     Onyx 两个模型服务各 1.7 GB。本刀临时 PG 已释放，贡献为 0。
- **无凭据落盘**：本刀**全程 `mock`，从未调用真引擎**，因此没有读取、刷新或
  向用户索取任何凭据；`/home/fisher/.onyx-lab/.secrets/admin-cookies.txt` 存在
  但**未被本刀读写**；本刀产物内**无凭据值**（扫描见 `14-compliance-check.txt`）。
- **Onyx 上游未碰**：`/home/codex` 是 `mode=750`、属另一用户，本会话
  **不可读也不可写**（无免密 sudo），这是**权限层面的保证**而非声明；
  Onyx 容器只挂数据/日志卷，**没有源码 bind-mount**；`docker inspect` 已验证。
- **compose / `.env` 未碰**：`ece/docker-compose.yml`（09-14）、
  `ece/deploy/docker-compose.demo.yml`（09-23）mtime 均为本会话之前。
- **种子既有内容未改**：`pyproject.toml` / `uv.lock` **零 diff**；
  `src/ece/seed.py` 155 增 3 删，3 处删除是 `["admin"]` → `["admin","org_admin"]`
  与 `seed_test_users` 内部两行重构；**420 个 `demo:demo` 对象与 1200 关系在
  全新库上原样复现**，三域业务断言由全套件 0 failed 覆盖。
- **未 push**（两个仓库都未 push；外层 `onyx-lab/` 未提交，与既往各刀一致）。

## 5. 与任务书的偏差

**无功能性偏差。** 三处**判断记录**如下，均为"任务书未规定、我做了选择并留痕"：

1. **记忆步骤在两条返回路径上都执行**（含 root entity 为空时的
   `insufficient_context` 早退路径）。TASK §5 步骤 5 说"在 documents / structured
   之后、rank/truncate 之前"，而空 root 时 `assemble_context` 会**提前返回**、
   绕过那一段。我让记忆走共享的 `_memory_step`，两条路径都跑，理由：记忆只取决
   于调用者，与 root entity 是否解析成功无关；若只在主路径跑，"无 root 实体"
   会变成一条**偷偷关掉记忆**的侧信道。已在代码注释与 `docs/API.md §14.0` 写明。

2. **被权限拒绝的候选不写入审计**。TASK 没规定拒绝是否入审计。我选择不入，
   理由：把"存在一条你看不见的记忆"写进 `context_items` 就是**存在性侧信道**，
   与 OEI-009 反探测的立场矛盾。另外这也避免污染
   `tests/integration/test_s32_assembly.py` 的 `item_kind` 断言。`dropped` 因此
   **只算被上限截断的条数**，不含被拒绝的——已在 `docs/API.md §14.0` 明确写出。

3. **org-B 的读用例用 SQL fixture 构造**。候选 A 下写 org 记忆需要"**属于该 org
   的** `org_admin`"，而种子里只有属 org A 的 `demo-user-admin`，**没有任何身份
   能写 org-B 的记忆**。我**没有**为了测试放宽政策（那会让 A4 的负例失去意义），
   而是把 org-B 的读 fixture 直接用 SQL 造好并在证据里标注来源。这是**种子/政策
   的缺口**，已列为转出项（附录 P §P.8）。

### 5.1 一处**已撤销**的越界改动（自我纠正，记录在案）

第一版我改了 `tests/integration/test_s32_assembly.py:92` 的**断言**
（`item_kind` 封闭集加 `"memory"`），并给 `tests/unit/test_org_scope.py` 改了
docstring 与一个测试函数名。重读 TASK §8 后发现：对既有测试文件，只授权改
**装配部分（fixture / stub / 依赖注入 / import）**，且明写"**断言不得改动**"。
两处**均已撤销**，这两个文件现在与 `a884d41` **逐字节相同**
（`git diff a884d41 HEAD -- tests/` 只剩两个新增文件）。

被撤销的那个改动想解决的**问题是真实的**，所以我没有把它埋掉，而是**复现并
转出**：给 `demo-user-procurement` 造一条活跃记忆后，该断言**因正确行为而变红**
（`AssertionError: assert 'memory' in ('entity','relationship')`，见
`12c-s32-item-kind-fragility.txt`）。当前全套件绿灯是**靠 fixture 运气**
（活跃记忆都属于 `demo-user-finance`，而该测试装配的是 procurement），
**不是**因为该断言仍然正确。下一刀应处理它。

## 6. 建议（不实现）

1. **先修 `test_s32_assembly.py:92`**：把封闭集加上 `"memory"`，或改成断言它
   真正关心的不变量（每行 `decision ∈ {allowed, denied}` 且 `reason` 非空）
   而不枚举 kind。**这是当前唯一的已知红灯地雷**，触发条件与本刀无关。
2. **合并 org 的两条来源**：`Identity.org_id`（`entities.attributes.org_id`）与
   `PermissionScope.org_id`（`ECE_USER_ORGS`）仍是两套，`context_requests.org_id`
   写的是后者。合并前 `tests/integration/test_s7_orgs.py` 的断言不能动。
3. **给 org 分域派管理员**：现在 org-B 的记忆没人能写。若下一刀引入多 org 管理员，
   `seed.py` 与 `docs/DATA_MODEL.md §4.2` 的"谁能写"表要同步。
4. **清掉 `tests/unit/test_org_scope.py` 的过时 docstring**（它仍宣称
   "`org_id` 不参与 `check_permission`"，已不成立）与名不副实的测试名
   `test_org_id_does_not_affect_check_permission_for_now`。本刀**无权**改
   （"断言不得改动"外也没授权改注释），更正只写进了 `docs/API.md §13.6.5` 与
   `docs/DATA_MODEL.md §4.2`。
5. **记忆的淘汰策略**：目前只有 `expires_at` + 软删，没有"新记忆取代旧记忆"或
   冲突消解；上限 10 是**按时间**的硬截断，不是相关性排序。若要真正当"偏好"
   用，需要相关性/时序的合成策略。
6. **`DELETE /api/v1/memory/{id}` 的 403/404 差异**是弱存在性预言机。删除需猜
   bigint id，本刀判为可接受；若要严格，可让"不是你的"也返回 404。
7. **org-B 读 fixture** 应在下一刀换成真实路径（见 §5.3）。

## 7. 证据索引

`evidence/`：`00-baseline.txt`（基线）、`00b-fresh-db-chain.txt`（全新库整链）、
`01-org-identity.json`、`02-subject-matches.txt`、`03-memory-migration.txt`、
`04-write-permission-matrix.json`、`05-read-matrix.json`、
`06-expiry-and-deleted.json` + `raw/06-*.json`（4 份**完整原始响应体**）、
`07-audit-provenance.json`、`07-audit-provenance.txt`（SPA 哈希对照）、
`08-compliance-delete.json`、`09-determinism-n5.json`、`10-package-keys-diff.txt`、
`11-test-db-free-raw.txt`、`12a-context-permission-subset.txt`、
`12b-test-suite-raw.txt`、`12c-s32-item-kind-fragility.txt`、
`13-git-commit.txt`、`14-compliance-check.txt`。

`workspace/`：可重跑的工装（`_client.py` + `step1`…`step14`），
`design-memory-policy.md`（写权限候选 A 的选择依据 + "换政策要改哪几行数据"
的确切 SQL）。

全部证据为 **HTTP 状态 + JSON + SQL 查表输出 + 单测原始输出**，
**未使用任何用户截图**（A14）。
