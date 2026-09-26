# OEI-010 任务书 — 持久上下文记忆 v1（用户级 + 组织级，读写都过权限引擎）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-25
> 前置：`OEI-009` 已 **PASS 关闭**（三轮审验，见 `OEI-009/VERDICT.md` 末尾 #3）；本刀是**第一把消费 org scope 的刀**
> 返工约定：本刀若需返工，一律标 **`OEI-010 R1` / `R2`**（不插新刀、不顺延既有编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## ✦ 开工指令（cc 必读：按序读完再动手）

> 你的会话记忆不可信任——**先按下面的清单读文件，再按本文档执行**。
> **`onyx-lab/` 顶层的一批文档已由用户并入 `onyx-lab/重启必读/`**（不是丢文件；`CODEX-ROLE.md` / `README.md` / `ASSET-INDEX.md` / `DECISION-ONYX.md` 仍在顶层）。

**① 按序必读（绝对路径，一份都别跳）**

```
1. /mnt/d/Projects/domainAgentECE/AGENTS.md                                  ← 项目总规则（角色、红线、Case First）
2. /mnt/d/Projects/domainAgentECE/onyx-lab/README.md                          ← 入口索引 + 目录变更 + "为什么 8080 看不到变化"
3. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/CC-ROLE.md                 ← 你的角色任务书
4. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/LOCAL-AGENT-PROTOCOL.md    ← 共享规则 + **§5.1 资源纪律**（本刀的取证模式与 008/009 不同，见 §8）
5. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/OEI-ROADMAP.md             ← 路线图：OEI-009 已 PASS；**本刀条目下的"签发前校正"五条必须读到**
6. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/VERDICT.md                  ← 上一刀裁定（末尾 #3 = PASS；§7 是你的转出项；§5 是我自己的教训）
7. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/DEPLOYMENT-STATUS.md       ← 环境事实（含已知问题 #5：`/api/search` 是 agentic 管线）
8. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/workspace/10-design-org-scope.md ← **本刀的 org scope 设计依据**（2.B = DB 来源；3.B.1 = `_subject_matches` 一行；写入权限候选 A/B/C/D）
9. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/TASK.md                     ← **本文件 = 唯一任务来源**
```

**② 开工前先核对状态（只读，别凭记忆判断进度）**

```bash
cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010 && ls -la     # DONE / VERDICT.md 都不该存在 = 正常开工
cd /mnt/d/Projects/domainAgentECE/ece && git log --oneline -3 && git status -sb | head -3
# 期望：HEAD = a884d41（OEI-009），ahead 1，未 push
docker ps --format '{{.Names}}\t{{.Status}}'                      # 9 个 Onyx 容器 Up，restarts 应仍为 0
```

**③ 本刀一句话（细节见 §5 步骤与 §6 验收）**

把"记忆"做成一等领域对象（用户级 + 组织级），**写入与读取都过既有权限引擎**；读取作为 `assemble_context` 的显式一步、**位于权限判定之后**；把 org scope 从"字段"变成"可判定"（补 `_subject_matches` 的 org 分支 + org 来源落库）；合规面（可查看 / 可删除单条与全量 / 可追溯）。**不做** LLM 自动抽取、不做审批流、**不在界面上展示"本次引用了哪几条记忆"**。

**④ 硬约束速查（违反即 FAIL，全文见 §8）**

- ✅ 本刀授权改：`src/ece/{permissions,identity,context,api,migrations/versions}/**`、`src/ece/seed.py`、`tests/**`（可新增文件、可改装配部分，**断言不得改、测试不得删**）、`docs/{API,DATA_MODEL}.md`、`TASKS.md`；可起临时 PG；可 `git commit`（**不 push**）
- ❌ 不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）；不改 Onyx 上游 / compose / `.env`；**不 restart / stop / down / rm 任何容器**；不碰 `/mnt/c`
- ❌ **不改 `check_permission` 的判定顺序**；不改 `_acl_in_window` 语义；**不发明 `effect='write'`**（只 allow/deny）；不新建第二套权限机制
- ❌ **不在 SPA 展示"本次用了哪几条记忆"**（用户已明确否决）；不改 36 个种子对象的既有内容与三域业务断言
- ❌ **验收不得要求用户截图**；一切可见性用机器可校验证据
- 📌 **本刀不需要真引擎**：记忆全在 ECE 侧 + 原生 documents；全程 `ECE_CONTENT_ENGINE=mock`（默认）。若你判断某条取证必须真引擎，**先在 REPORT §偏差 申报理由**——这是与 OEI-007 相反的默认（那条纪律针对引擎侧结论）
- 📌 资源纪律：临时 PG / uvicorn / 反代验完即释放，收尾三查写进 REPORT

**⑤ 收工与心跳**

```bash
echo "$(date -Iseconds) OEI-010 complete" > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/DONE
```

然后 **STOP**（不启动下一刀）。心跳对象 = `onyx-lab/OEI-010/VERDICT.md`；出现 PASS 即停，出现 FAIL 按 `R1..Rn` 返工（删旧 `DONE` → 修 → 重建 `DONE`）。

## 0. 一句话目标

给 ECE 加上**持久上下文记忆**：记忆是**领域对象**（`scope` = user|org，owner、statement、source、confidence、created_at、expires_at），**写入要过权限引擎、读取要在权限判定之后逐条过权限引擎**，org scope 真正可判定，并且满足合规要求（可查看 / 可删除单条与全量 / 可追溯）。

**为什么是这一刀**（`OEI-009/workspace/10-design-org-scope.md` + 我的实测）：

1. `AGENTS.md` §7 把 **Domain Knowledge / Domain Ontology** 列为我们的核心 IP；而"组织口径、术语、模板"这类知识的**唯一载体**就是记忆。`OEI-009` 只把 org 维度做成**字段**（`Identity.org_id` / `PermissionScope.org_id`），**没有任何地方产生或消费它** —— 没有记忆，这个字段就是死的。
2. 用户 2026-09-25 决策：**用户级与组织级都做**，且**界面上不展示"本次回答引用了哪几条记忆"**（可追溯走既有审计面）。
3. 依赖铁律（路线图）：**身份（008）→ 权限（009）→ 记忆（010）**。若记忆早于权限落地，就是又一个"后置过滤"式的越权风险 —— 所以本刀必须**复用 009 的结果级授权纪律**，而不是另起一套。

---

## 1. 现状（codex 实测，可直接信任；每条都带"文件 + 符号 + 行为"）

### 1.1 记忆**完全不存在**

`grep -rIn 'memory\|remember\|preference' src/ece` 只命中三类与"记忆"无关的东西：`api/quota.py` 与 `api/rate_limit.py` 的 **in-memory** 回退、`connectors/onyx/mock_adapter.py` 的 in-memory store、`consulting/metadata.py` 的注释。→ **没有 `memories` 表、没有记忆接口、没有 `object_type='memory'` 的 ACL 使用**。本刀从零建。

### 1.2 org 维度**只有字段，没有来源**（本刀要补的第一件事）

- `src/ece/identity/parser.py` 的 `@dataclass Identity` 在 OEI-009 已加字段 `org_id: str | None = None`（同文件还有 `Identity.anonymous()` / `Identity.from_engine_caller()`）。
- **但 `resolve_identity()` 的 `return Identity(...)` 里没有 `org_id`** —— 我逐行读过，只传 `user_ref / entity_id / display_id / name / department / roles / aliases / is_management`。**今天任何真实调用者的 `identity.org_id` 恒为 `None`**（`anonymous()` 也是 None）。
- `upsert_identity()` 写入的 `attrs` 只有 `{"department", "roles", "is_management"}`，**没有 org_id**。
- 迁移 `0007_user_orgs` **只**给 `context_requests` 加了 `org_id` 列；`entities` 表本身没有 org 列。
- ⇒ `10-design-org-scope.md` §2 里那句"`Identity.org_id` 由 `resolve_identity` 从 `entities.attributes.org_id` 填充"是**设计意图，尚未实现**。该文档已把来源**决策为 2.B（DB 可信属性）**，`X-Org-Id` 头**不进判定路径**。本刀负责落地。

### 1.3 权限引擎**没有 org 分支**

`src/ece/permissions/engine.py` 的 `_subject_matches(entry, identity)` 只认三种：`st == "user" and sr == identity.user_ref`、`st == "role" and sr in identity.roles`、最后一行 `return st == "department" and sr == identity.department`。→ `subject_type='org'` 的 ACL 行**永远不会命中**。

### 1.4 ACL 载体可以直接复用（**不要发明新机制**）

- `acl_entries`（迁移 `0001_initial`）列：`id / subject_type / subject_ref / object_type / object_ref / effect / valid_from / valid_to / source_system / note`。
- `effect` 列**没有 CHECK 约束**（是自由文本），但 `check_permission` 只识别 `"deny"`（规则 1）与 `"allow"`（规则 2–4）。→ **"可读/可写"必须表达为 `effect='allow'` 的 ACL 行**；`10-design-org-scope.md` §4 里提过的 `effect: 'write'` **本刀不采用**（那会让 `check_permission` 需要改判定逻辑，触犯"不改判定顺序"）。
- `check_permission(identity, object_type, object_ref, classification, acl_entries, engine, now=...)` 的 `now` 形参由 OEI-009 参数化（`_acl_in_window`，半开区间 `[valid_from, valid_to)`）。→ 记忆的授权**天然可时间盒**。
- 分类矩阵 `DEFAULT_CLASSIFICATION_MATRIX`（同文件）现有键：`public / internal / department / restricted / management / confidential / finance / procurement`，其中 **`restricted → default deny`**、`public → allow`。

### 1.5 装配管线现场（本刀要插一步的地方）

`src/ece/context/assembly.py`：

- 入口签名：`assemble_context(engine, user_ref, intent, entities, as_of=None, pack="procurement") -> ContextPackage`，文档串写明是 **12 步**管线。
- 已有步骤（按代码注释）：**Step 1+2** Identify + Resolve identity（约 145 行）→ **Step 4** 解析 root entities，其中**每个实体隐式做 Step 3 权限判定**（`check_permission(object_type="entity", classification="public")`，约 216 行）→ **Step 5** 关系（逐条 `check_permission`，约 261 行）→ **Step 6** 文档（`get_documents`，原生 FTS）→ **Step 7** 结构化数据（`get_structured_data`）→ **Step 9** rank/truncate → **Step 10+11** `build_sources` + `_finalize`。
- **没有记忆这一步**，也没有任何 memory 相关字段。

### 1.6 ⚠️ 装配里的 ACL 载入器**不能复用**（这是个坑，别踩）

同文件的 `_load_acl_for(engine, object_ref)`：SQL 硬编码 `WHERE object_type = 'entity' AND object_ref = :oref`，且**返回字典里 `valid_from` / `valid_to` 恒为 `None`**。→ 用它去查记忆会**查错对象类型**、并且**丢掉时间窗**（等于让 OEI-009 的时间盒在这条路上失效）。记忆路径必须自己按 `object_type='memory'` 载入、**带真实日期列**。

### 1.7 返回包是"逐键输出"的固定形状（只许加键）

`ContextPackage`（同文件 `@dataclass`）现有键：`package_id / request_id / task / user / entities / relationships / documents / business_data / denied / sources / metadata`，`to_dict()` 逐键显式输出。→ **本刀只允许新增一个键（`memory`）**，既有 11 个键的形状与语义**不得变**（有既有测试与消费者）。

### 1.8 可追溯面已经在（不需要新造审计）

`src/ece/context/provenance.py`：`build_sources(items)`（items 形如 `{kind, ref, source, decision, reason}`）+ `record_package(...)` → 落进 `context_requests` / `context_items`（迁移 `0005_context_audit`），由既有 `GET /api/v1/audit/context/{request_id}`（`src/ece/api/audit.py`）读。→ **记忆的可追溯 = 把记忆放进 `items_for_audit`**，不新建审计面。

### 1.9 迁移与种子现场

- 迁移最新是 **`0009_engine_documents`** → 本刀的新迁移**必须**是 `0010_*`（`down_revision = "0009_engine_documents"`）。
- `src/ece/seed.py` 的 `_TEST_USERS` 现有 **4 个**演示身份：`demo-user-procurement`（dept `procurement`，roles `["procurement_manager","buyer"]`）、`demo-user-finance`（dept `finance`）、`demo-user-engineering`（**dept 是 `sales`**，roles `["buyer"]`）、`demo-user-admin`（dept `it`，roles `["admin"]`，**故意非 management**）。**四人都没有 org_id**。
- 注意：OEI-009 证据里的 `alice` / `bob` 是**临时 PG 里现造的探针身份**，不在 `_TEST_USERS` 里，也不在正式种子里 —— 别把它们当成既有事实。

### 1.10 回归基线（供你对照）

`OEI-009` 收尾时全套件 = **`806 passed / 5 skipped / 3 deselected`，0 failed**；已知 flake `test_s20_audit_webhook.py::test_webhook_receives_event` **已被 OEI-009 步骤 0.1 修掉**（12 连跑 0 failed），所以**本刀基线是 0 failed，不允许出现任何失败**。

---

## 2. 范围锁

**做**：

1. **org 来源落库**（`resolve_identity` / `upsert_identity` 读写真 `attributes.org_id`）+ 演示身份的 org 种子；
2. **`_subject_matches` 的 org 分支**（一行）+ 单测；
3. **记忆表与迁移 0010**（`memories`）；
4. **写入过权限引擎**（范围对象 `memory_scope` + 默认拒绝 + 策略=数据）；
5. **读取在权限判定之后**（`assemble_context` 显式一步 + 逐条 `check_permission` + 确定性排序与上限）；
6. **失效语义**（`expires_at` / `deleted_at` / ACL 时间盒）；
7. **合规面**（查看 / 删除单条 / 全量删除 / 审计可追溯）；
8. 文档与提交。

**不做**（做了即越界）：

- **不做 LLM 自动抽取**（不确定性无法验收；第一版只做**显式记忆**）；
- **不做审批流 / 授权签发流程**（模型留口在 §3.3，实现后置到单独一刀）；
- **不在界面上展示"本次回答引用了哪几条记忆"**（用户明确否决）——可追溯走既有审计面；
- 不做多租户 SaaS / 计费 / K8s / ERP 写能力；
- 不做检索调优（OEI-012）、不补种子内容与行业标签（OEI-011）；
- 不改 Onyx 任何东西；不引入新依赖；**不改 `check_permission` 判定顺序**。

---

## 3. 契约（**本刀锁定**：cc 按此实现，不要自行发挥；发现契约与实测不符 → 停手 + 写 REPORT + 等 codex 对齐）

### 3.1 记忆对象模型（新表 `memories`）

| 列 | 类型/约束 | 语义 |
|---|---|---|
| `id` | `bigserial PK` | 稳定标识；`object_ref = 'memory:<id>'` |
| `scope` | `text NOT NULL CHECK (scope IN ('user','org'))` | 用户级 / 组织级 |
| `owner_ref` | `text NOT NULL` | **user scope → `user_ref`**；**org scope → `org_id`** |
| `statement` | `text NOT NULL` | 记忆正文（显式写入，非模型抽取） |
| `classification` | `text NOT NULL DEFAULT 'restricted'` | 走既有分类矩阵；**默认 `restricted` = 默认拒绝** |
| `source` | `text NOT NULL` | 来源标记，如 `explicit:api` |
| `source_ref` | `text NULL` | 可选外部引用（如某个 `request_id` / 文件） |
| `confidence` | `numeric(3,2) NULL CHECK (0 ≤ c ≤ 1)` | 显式给出，可空 |
| `created_at` / `updated_at` | `timestamptz NOT NULL DEFAULT now()` | |
| `expires_at` | `timestamptz NULL` | 空 = 不过期 |
| `deleted_at` | `timestamptz NULL` | **软删除**（合规要求"可追溯"，不物理删） |

约束与索引：**`UNIQUE (scope, owner_ref, statement)`**（幂等创建的前提）+ `(scope, owner_ref)` + `(deleted_at)`。

### 3.2 可见性 = 既有 ACL 数据（**两种 scope 都只用 ACL 表达，不加新机制**）

每条记忆都是一个被 ACL 治理的对象：`object_type='memory'`、`object_ref='memory:<id>'`、`classification='restricted'`（默认拒绝）。

- **user scope**：种子 `(subject_type='user', subject_ref=<owner_ref>, object_type='memory', object_ref='memory:<id>', effect='allow')` → 只有本人能读。
- **org scope**：种子 `(subject_type='org', subject_ref=<org_id>, object_type='memory', object_ref='memory:<id>', effect='allow')` → **同 org 的所有人**能读，异 org 与无 org 的人都不能。

⇒ 判定完全复用 `check_permission(..., now=<today>)`；**`_subject_matches` 只多一行**：

```python
if st == "org" and sr == identity.org_id:
    return True
```

`identity.org_id` 为 `None`/空串时**不得命中**。

### 3.3 写权限 = 对"范围对象"的判定（策略=数据，改政策只改 ACL 行）

写记忆前先判定**范围对象**：`object_type='memory_scope'`，`object_ref = 'user:<user_ref>'` 或 `'org:<org_id>'`，`classification='restricted'`（默认拒绝），ACL 由种子给出：

- **user scope 写**：`(subject_type='user', subject_ref=<本人>, effect='allow')` → **本人可写自己的**。
- **org scope 写**：**采用 `10-design-org-scope.md` §4 的候选 A（管理员）**：`(subject_type='role', subject_ref='org_admin', object_type='memory_scope', object_ref='org:<org_id>', effect='allow')`，并给管理员身份补 `org_admin` 角色（`demo-user-admin` 现只有 `['admin']`）。

候选 B（组织负责人）/ C（同行评审）/ D（版本化任意写）**本刀都不实现**，只在 `workspace/design-memory-policy.md` 记录取舍与"想换政策时改哪几行数据"。

### 3.4 读取位置（**必须在权限判定之后**）

`assemble_context` 新增**显式一步**（建议注释名 `Step 6.9 memory`），位置在 documents/structured **之后**、rank/truncate **之前**；实现放新模块 `src/ece/context/memory.py`：

1. 候选集：`deleted_at IS NULL` AND (`expires_at IS NULL` OR `expires_at > now`) AND（`scope='user' AND owner_ref=identity.user_ref`）OR（`scope='org' AND owner_ref=identity.org_id`）；
2. **逐条** `check_permission(identity, object_type='memory', object_ref='memory:<id>', classification=<行.classification>, acl_entries=<按 'memory' 载入且带真实日期>, now=<today>)`；**不得复用 `assembly._load_acl_for`**（§1.6）；
3. 排序与预算（**确定性**）：**org scope 优先**，组内 `created_at DESC, id DESC`；**上限 10 条**；被截断条数写进 `metadata.memory_dropped`（整数，无截断则 0）。

### 3.5 注入形状与可追溯

- `ContextPackage` **新增一个键 `memory`**：`[{ref, scope, statement, source, confidence, created_at, expires_at}]`（`ref` = `memory:<id>`）。**既有 11 个键逐键不变**。
- 每条被注入的记忆必须进 `items_for_audit`（`kind='memory'`, `decision='allowed'`）；被拒的候选可记 `decision='denied'` + `reason`，但**不得把 statement 内容写进审计**（只记 ref/reason）。

### 3.6 失效

`expires_at` 已过 → 不注入（也不出现在 `GET /memory` 默认列表）；`deleted_at` 非空 → 同上；ACL `valid_to` 过期 → 授权自动失效（复用 009 语义，**不改** `_acl_in_window`）。

---

## 4. 工作区与证据命名

```
onyx-lab/OEI-010/
├── TASK.md      ← 本文件（只读）
├── workspace/   ← 源文件/素材（含 design-memory-policy.md）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

建议证据文件（命名沿用既往刀）：

`00-baseline.txt`、`01-org-identity.json`、`02-subject-matches.txt`、`03-memory-migration.txt`、`04-write-permission-matrix.json`、`05-read-matrix.json`、`06-expiry-and-deleted.json`、`07-audit-provenance.json`、`08-compliance-delete.json`、`09-determinism-n5.txt`、`10-package-keys-diff.txt`、`11-test-db-free-raw.txt`、`12-test-suite-raw.txt`、`13-git-commit.txt`、`14-compliance-check.txt`

## 5. 任务步骤

### 步骤 0 — 前置与基线（先做）

1. 起临时 PG（本机 `pgvector/pgvector:pg16` 已在用）；`alembic -c src/ece/migrations/alembic.ini upgrade head`（应到 `0009`）；按 `Makefile` 正确前置跑 `gen-dataset → seed → seed-fixtures`（见 `LOCAL-AGENT-PROTOCOL.md` §5.1 与 `ece/README.md` 的前置链）。
2. 跑 **一次** 全套件 `uv run pytest -m "not eval and not eval_llm"`，把**原始汇总**落盘 `evidence/00-baseline.txt`（期望 `806 passed / 0 failed`，与 §1.10 对照）。
3. 记录 `git log --oneline -1`、`git status --porcelain`（排除开工前就存在的 `mutation-evidence/*` 与 `docs/demo-platform/*` 噪声）快照。
4. **全程 `ECE_CONTENT_ENGINE=mock`**（本刀不涉及引擎召回；见 §8 资源纪律）。若你认为某条取证必须真引擎 → 先在 REPORT §偏差 申报理由。

### 步骤 1 — org 来源落库（A1）

1. `resolve_identity()`：从 `entities.attributes` 读 `org_id`（字符串且非空 → 用；缺失/非字符串/空串 → `None`），填进返回的 `Identity`。
2. `upsert_identity()`：增加 `org_id: str | None = None` 形参，写进 `attrs`。**向后兼容**：不传即不写该键；`attributes` 是 JSONB，**增量更新、不得覆盖既有键**（department/roles/is_management 必须保留）。
3. 演示身份的 org 种子（**幂等，可重复执行**）：建议 `demo-user-procurement` / `demo-user-finance` → `org:consulting-a`，`demo-user-engineering` → `org:consulting-b`，`demo-user-admin` → `org:consulting-a` 且补 `org_admin` 角色。必须覆盖四态：**同 org 两人 / 异 org 一人 / 无 org 一人 / 未知用户**（未知用户走 `resolve_identity` 的 stub 分支 → `org_id=None`）。
4. 证据 `01-org-identity.json`：四个（+未知）身份的实测输出（`user_ref / department / roles / org_id`）。

### 步骤 2 — 权限引擎 org 分支（A2）

1. `_subject_matches()` 增加 §3.2 那一行（`org_id` 为 None/空不命中）。
2. **不得重排** `check_permission` 的规则顺序（deny > user > role > dept > classification 默认 > default deny），**不得改** `_acl_in_window`。
3. DB 无关单测：同 org 命中 / 异 org 不命中 / `org_id=None` 不命中 / 空串不命中 + "既有 user/role/department 行为不变"的对照。
4. 证据 `02-subject-matches.txt`：diff 片段 + 单测原始输出。

### 步骤 3 — 记忆表与迁移 0010（A3）

1. 新迁移 `0010_*`（`down_revision="0009_engine_documents"`），按 §3.1 建表；`downgrade()` 干净回滚。
2. 证据 `03-memory-migration.txt`：`upgrade` 输出 + **唯一约束违约实测**（贴约束名原文）+ schema 复查（列/约束/索引）+ `downgrade`→`upgrade` 往返各一次。

### 步骤 4 — 写入过权限引擎（A4）

1. 写路径先按 §3.3 判定范围对象；**默认拒绝**，只有显式 allow 才通过。
2. API：`POST /api/v1/memory`，body 至少 `{scope, owner_ref, statement, confidence?, expires_at?, source_ref?}`。
   - 主体**只来自凭据**（`X-User-Id` 头 / 既有 JWT 约定解析出的 identity）；**body 里的 `owner_ref` 必须与凭据一致**，不一致 → **拒绝**（不得静默改写）；
   - `scope='org'` 时 `owner_ref` 必须是 `identity.org_id`（否则拒绝）；`identity.org_id` 为 None → 拒绝；
   - `scope='user'` 时 `owner_ref` 必须等于 `identity.user_ref`。
3. 幂等：同 `(scope, owner_ref, statement)` 重复创建 → **不新建**，返回既有行并明确标注（例如 `created: false`）。
4. 证据 `04-write-permission-matrix.json`（≥6 格）：本人写 user（允）/ 他人写 user（拒）/ 无 `org_admin` 写 org（拒）/ 有 `org_admin` 写 org（允）/ body 谎报 owner（拒）/ 重复创建（`created=false` 且行数不变）。

### 步骤 5 — 读取：在权限判定之后、逐条授权（A5）

1. 新模块 `src/ece/context/memory.py`，按 §3.4 实现候选集 + 逐条判定 + 排序/上限。
2. `assemble_context` 插入这一步（§3.4 位置），把结果放进 `ContextPackage.memory`（§3.5 形状），并写入 `items_for_audit`。
3. `metadata` 增加 `memory_dropped`（整数）与 `memory_count`（整数）——**只增键**，不改既有 metadata 键。
4. 证据 `05-read-matrix.json`：同一 `POST /api/v1/context`（同 intent、同 entities）下至少四格：
   - 同 org 的 A 用户 → 看到 A-org 记忆 + 自己的 user 记忆；
   - 异 org 的 B 用户 → **看不到** A-org 记忆（**statement 文本完全不出现**）；
   - 无 org 用户 → 看不到任何 org 记忆；
   - 他人 → 看不到 A 的 user 记忆。

### 步骤 6 — 失效与时间盒（A6）

1. `expires_at` 已过 / `deleted_at` 非空 → 不注入（原始响应为证）。
2. 给一条 org 记忆的 allow ACL 设 `valid_to = 昨天` → 该用户立即失权；改回未来 → 恢复（两次原始响应）。
3. 证据 `06-expiry-and-deleted.json`。

### 步骤 7 — 合规面：查看 / 删除 / 可追溯（A8/A9）

1. `GET /api/v1/memory`：默认返回**调用者可见**（本人 user-scope + 同 org 的 org-scope，未删未过期）；`?include_inactive=true` 额外返回**自己的**已删/已过期记忆（仍受权限约束）。
2. `DELETE /api/v1/memory/{id}`：**软删**（写 `deleted_at`）。删除权：本人 user-scope 记忆 = 本人；org-scope 记忆 = 需 §3.3 的写权限。
3. 全量删除：`DELETE /api/v1/memory?scope=user` = 删**调用者自己的**全部 user-scope 记忆；`scope=org` 需 org 写权限（**给出无权限者的负例**）。
4. 可追溯：删除后 `context_items` 里的历史记录**仍在**，`GET /api/v1/audit/context/{request_id}` 仍能查到该记忆曾被注入（`kind='memory'`）。
5. **SPA 零改动**：给 `git diff --stat` 或 `grep` 证据证明 `ece/demos/spa/**` 未新增任何记忆展示。
6. 证据 `08-compliance-delete.json`、`07-audit-provenance.json`。

### 步骤 8 — 测试、文档、提交

1. **DB 无关单测**（新文件，不依赖 PG）：org 四态、写权限矩阵（stub ACL）、过期/软删过滤、排序与上限截断、注入形状、`ContextPackage.to_dict()` 既有键不变。
2. **集成实测**（临时 PG + mock 引擎）：步骤 5 / 6 / 7 的端到端。
3. **无回归**：先跑 context / permission 相关子集，收尾**跑一次**全套件并落盘原始汇总（对照 §0.2 基线）。
4. **文档**：`docs/DATA_MODEL.md`（`memories` 表 + 两个 scope 的可见性规则 + `memory_scope` 写权限对象）、`docs/API.md`（三个端点 + 注入语义 + 合规删除 + **明确写"不展示用了哪几条记忆"**）、`TASKS.md`（附录 P）。
5. **提交**：`git add` + `git commit`（**不 push**），落盘短 hash 与文件清单（`13-git-commit.txt`）。
6. **收尾三查**（写进 REPORT）：无残留探测进程（`pgrep`）、无残留 `ece-*` / PG 容器（`docker ps -a`）、内存/swap 快照。临时 PG 必须释放。

---

## 6. 验收标准（codex 将逐条核对；**每条都必须能被 evidence 证明**）

- [ ] **A0** 前置与基线：临时 PG 起、迁移到 `0009`、seed 链跑通、基线套件原始汇总落盘（`00-baseline.txt`）；**全程 `ECE_CONTENT_ENGINE=mock`**（若用真引擎须在 REPORT 申报理由 + 状态码）
- [ ] **A1** org 来源落地：`resolve_identity` 从 `attributes.org_id` 填充；四态实测（同 org / 异 org / 无 org / 未知用户）；`upsert_identity` 增量写不覆盖既有属性键（前后 JSONB 对照）
- [ ] **A2** org 分支：`_subject_matches` 只多一行；四态单测（含 `org_id=None` 与空串不命中）；**判定顺序未重排**（diff 证据）
- [ ] **A3** 迁移 0010：可升可降 + `scope` CHECK + `UNIQUE (scope, owner_ref, statement)` + 索引；违约实测原文
- [ ] **A4** 写入过权限引擎：≥6 格矩阵；默认拒绝；**主体只来自凭据**（body 谎报 owner → 拒）；重复创建 `created=false` 且行数不变
- [ ] **A5** 读取在权限判定之后 + 逐条授权：同 query 两个身份 → **不同 `memory` 集合**；异 org / 无 org 者**完全看不到** org 记忆（statement 不出现）；他人看不到 user 记忆
- [ ] **A6** 失效：`expires_at` 过期与 `deleted_at` 非空 → 不注入；ACL `valid_to` 过期即失权、恢复即复现（两次原始响应）
- [ ] **A7** 确定性：同输入 **N=5 次**注入结果逐字节一致（含排序）；上限 **10** 条生效；`metadata.memory_dropped` 与实际被截断数一致
- [ ] **A8** 可追溯 + 无 UI：被注入记忆出现在 `context_items` 与 `GET /api/v1/audit/context/{request_id}`；**`ece/demos/spa/**` 零改动**（grep/diff 证据）
- [ ] **A9** 合规删除：单条删除 + 自己的全量删除；org 全量删除需权限（负例）；删除后不注入但审计仍在
- [ ] **A10** 既有契约不回归：`ContextPackage.to_dict()` 既有 11 键**逐键对照**（只多 `memory`）；context / permission 相关测试全绿；**全套件 0 failed**（≤ 基线）
- [ ] **A11** 文档：`docs/DATA_MODEL.md` / `docs/API.md` / `TASKS.md` 更新；另有 `workspace/design-memory-policy.md` 记录写权限候选选择（A）与"换政策要改哪几行数据"
- [ ] **A12** 提交：`git commit`（**不 push**）+ 短 hash 与文件清单落盘
- [ ] **A13** 合规与资源：无密钥/凭据值落盘；未碰 Onyx 上游 / compose / `.env`；未改 36 个种子对象既有内容与三域业务断言（允许**新增** org/memory 种子与 ACL 行）；临时 PG 已释放；收尾三查落盘；**未 push**
- [ ] **A14** 证据纪律：全部机器可校验（HTTP 状态 + JSON + SQL 查表输出 + 单测原始输出）；**不使用"用户截图"**；DB-free 与集成证据均落盘

## 7. 完成后的动作（严格按序）

1. 自检目录结构与证据完整性、无密钥泄漏、临时资源已清理（收尾三查）
2. `echo "$(date -Iseconds) OEI-010 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并等 codex 签发下一刀；FAIL → 按 `R1/R2…` 返工后重建 `DONE`

---

## 8. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：改 `src/ece/permissions/**`（仅 `_subject_matches` 一行 + 单测）、`src/ece/identity/parser.py`（org 读写）、`src/ece/context/**`（新增 `memory.py` + assembly 插一步 + `ContextPackage` 增键）、`src/ece/api/**`（memory 端点）、`src/ece/migrations/versions/**`（新增 0010）、`src/ece/seed.py`（org/角色种子）、`tests/**`（**允许新增文件，且允许修改既有测试文件的装配部分（fixture / stub / 依赖注入 / import）——断言不得改动、测试不得删除**）、`docs/API.md`、`docs/DATA_MODEL.md`、`TASKS.md`；可起临时 PG 跑套件；可 `git commit`（**不 push**）
- ❌ **不改 `check_permission` 的判定顺序**（deny > user > role > dept > classification 默认 > default deny）；**不改 `_acl_in_window` 语义**；**不发明 `effect='write'`**；不新建第二套权限机制
- ❌ 不引入新依赖；不改 `pyproject.toml` / `uv.lock`
- ❌ 不改 Onyx 上游源码 / compose / `.env`；不 restart / stop / down / rm 任何容器
- ❌ 不做 LLM 自动抽取 / 审批流 / 多租户 / 计费 / K8s / ERP 写能力 / 检索调优 / 种子内容补全
- ❌ **不在 SPA（`ece/demos/spa/**`）新增任何"本次引用了哪几条记忆"的展示**
- ❌ 不改 36 个种子对象的既有内容与三域业务断言；不删既有测试
- ❌ 不得要求用户截图；密钥/凭据只写 `<REDACTED>`
- 📌 **资源纪律**：本刀**不需要真引擎**——全程 `ECE_CONTENT_ENGINE=mock`；临时 PG / uvicorn / 反代 **验完即释放**；**不得**为了"日志上有 onyx"而开真引擎
- 📌 **演示数据脚本（若你新增）幂等四条**（教训来自 `OEI-009 R1`）：① 删除**必须带凭据**且失败要响亮；② 按**名称模式兜底**扫描自己的产物（不能只依赖自己的登记行）；③ **marker 固定**（不得用时间戳，否则证据不可复现）；④ **等索引传播**（轮询直到引擎不再召回旧内容）。并且**同时记录 `count` 与 `distinct`**——同一文档多 chunk 会各占一条

## 9. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-010/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-010/DONE`
- 无新文件则静默，不重复执行、不打扰用户
