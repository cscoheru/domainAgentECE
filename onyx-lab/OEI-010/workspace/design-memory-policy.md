# OEI-010 — 记忆写权限策略（选型 + 换政策改哪几行数据）

> 依据：`OEI-009/workspace/10-design-org-scope.md` §4（四候选 A/B/C/D）+
> `OEI-010/TASK.md` §3.3（本刀锁定 A）。
> 本文档**只记录决策与改法**，不新增机制；实现见
> `src/ece/seed.py::seed_memory_acl_entries` 与 `src/ece/api/memory.py`。

---

## 1. 问题

"谁能写一条**组织级**记忆"（组织口径 / 术语 / 模板这类"我们一律这么说"的知识）。
用户级记忆没有这个问题——所有者恒为本人。组织级必须有一个**判定**，而不是
"谁都行"。

关键约束（来自 OEI-009 的教训）：记忆的读与写都必须走**既有权限引擎**，
不得另起一套；`effect` 只有 `allow` / `deny`（**不发明** `effect='write'`，
那会迫使改 `check_permission` 的判定顺序）；判定的事实来源只能是**凭据 + DB**，
不能是调用方自报。

## 2. 四个候选（`10-design-org-scope.md` §4）

| 候选 | 谓词 | 优点 | 代价 |
|---|---|---|---|
| **A 管理员** | 拥有 `org_admin` 角色 | 最紧；与 ECE 既有"admin 独有路径"一致 | 管理员未必懂业务口径 |
| B 组织负责人 | `is_management=True`（per-org） | 尊重领域所有权（销售口径归销售负责人） | 需要 per-org 的 management 标记 → schema churn |
| C 同行评审 | 组织内任意人 + 异步评审 | 知识在源头被捕获 | "评审"本身是一条**工作流**；TASK §2 明确本刀不做审批流 |
| D 版本化任意写 | 组织内任意人，可回滚 | 最简单 | 垃圾口径在被发现前就已经进入组织级可见范围 |

## 3. 本刀决策：**候选 A**

`TASK.md §3.3` 锁定 A。落地方式**不是**在代码里写 `if "org_admin" in roles`，
而是**策略即数据**：

> 写记忆前先对**范围对象**做一次 `check_permission`。
> 范围对象 = `object_type='memory_scope'`，
> `object_ref = 'user:<user_ref>'` 或 `'org:<org_id>'`，
> `classification='restricted'`（既有分类矩阵里 → **default deny**）。
> 谁能写，就取决于 `acl_entries` 里有没有一行 `effect='allow'` 命中他。

于是"政策"完全落在 ACL 数据上，`check_permission` 的判定顺序一行都不用改。

### 3.1 本刀实际种下的 ACL 行

| 行 | subject | object | 含义 |
|---|---|---|---|
| 用户级写 | `role=org_admin` | `memory_scope` / `org:org:consulting-a` | 管理员可写 A 组织的组织级记忆 |
| 用户级写 | `role=org_admin` | `memory_scope` / `org:org:consulting-b` | 同上（B 组织） |
| 用户级写 | `user=<本人>` ×4 | `memory_scope` / `user:<本人>` | 四位演示用户可写**自己的**用户级记忆 |

> `org_id` 取值沿用 `TASK.md §5 步骤 1.3` 的字面量 `org:consulting-a` /
> `org:consulting-b`；按 §3.3 的公式 `'org:<org_id>'` 拼出的 `object_ref`
> 因此是 `org:org:consulting-a`。这层双前缀**只是观感问题**（命名，不是语义），
> 已在 `REPORT.md §观察` 记为可选的后续改名项；本刀不动，以免与任务书
> 的字面量分叉。

### 3.2 与"主体只来自凭据"的关系（两道独立闸门）

写路径上有**两道**独立的闸门，缺一不可：

1. **主体闸门（路由层）**：`scope='user'` 时 `body.owner_ref` 必须等于
   `identity.user_ref`；`scope='org'` 时必须等于 `identity.org_id`；
   `identity.org_id` 为空 → 直接拒绝。**不一致就拒绝，不静默改写**
   （TASK §5 步骤 4.2）。
2. **授权闸门（引擎层）**：范围对象的 `check_permission`。默认拒绝。

第 1 道挡"我替你写"，第 2 道挡"我没权限写"。两者是不同的问题，
不能合并——把第 1 道去掉，`org_admin` 就能替别人写用户级记忆；
把第 2 道去掉，任何登录用户都能改组织口径。

### 3.3 默认拒绝的可见后果（产品语义，不是缺陷）

因为范围对象 `classification='restricted'` 且**没有**"所有登录用户"
的兜底行，一个**没有**被种下 `user:<自己>` allow 行的身份，**写不了自己的
用户级记忆**。这是"策略即数据"的必然结果：新用户入职 = 发一行 ACL。
本刀把这一行为写进 `docs/API.md`，并在 `REPORT.md §观察` 标明
"若将来要改成'注册即可写自己的'，加一行 `subject_type='role'` 的通配即可，
不必改代码"。

## 4. 想换政策时，改哪几行数据

**全部只需改数据，不动一行 Python。**

### 4.1 换到候选 B（组织负责人）

```sql
-- 1) 删掉 A 的两行（按本刀自己的 source_system 标签精确定位，不做 LIKE 扫描）
DELETE FROM acl_entries
WHERE source_system = 'seed:oei010-memory'
  AND subject_type = 'role' AND subject_ref = 'org_admin';

-- 2) 改为按"组织负责人"判定：把组织负责人身份放进一个角色
INSERT INTO acl_entries
  (subject_type, subject_ref, object_type, object_ref, effect, source_system, note)
VALUES
  ('role', 'org_manager', 'memory_scope', 'org:org:consulting-a', 'allow',
   'seed:oei010-memory', 'policy B — org owner');
```

并让 B 组织的负责人在 `entities.attributes.roles` 里带上 `org_manager`。
**注意**：B 需要"哪个用户是哪个组织的负责人"这一事实；本刀用角色的原因
正是它已经存在于 `attributes.roles`，不需要新 schema。

### 4.2 换到候选 C（同行评审）

C 是**两段**：写 + 复核。第一段可以直接用本刀的机制表达
（把 `subject_type='org'` 的 allow 行加到范围对象上，即"组织内人人可写"）：

```sql
INSERT INTO acl_entries
  (subject_type, subject_ref, object_type, object_ref, effect, source_system, note)
VALUES
  ('org', 'org:consulting-a', 'memory_scope', 'org:org:consulting-a', 'allow',
   'seed:oei010-memory', 'policy C stage 1 — anyone in org may write');
```

第二段（复核 / pending 状态 / 通过后才对同 org 可见）**是一条工作流**，
本刀明确不做（TASK §2）。真要做得单独一刀，并需要给 `memories` 加
`review_state` 列 —— 那是**模型变更**，不是数据变更，本表不覆盖。

### 4.3 换到候选 D（版本化任意写）

与 C 第一段同解（同上那条 SQL），另外需要"可回滚"→ 需要 `memories`
的历史表或 `version` 列 + 保留策略。同样属于**模型变更**，本表不覆盖。

### 4.4 只收紧到候选 A 的"合规敏感词"子集

若只想让某几类口径更紧（例如合规相关术语仍归管理员），做法是**不加**宽行，
并对那些记忆把 `classification` 提到更严的取值——分类矩阵已经把
`restricted` 定为 default-deny，因此"不加行"就是"最紧"。

## 5. 本刀**不做**的事（明确记录，避免后来者误以为漏了）

- 不做审批流 / 复核状态机（候选 C 第二段）。
- 不做"组织负责人"字段的 per-org management 标记（候选 B 所需的 schema）。
- 不做记忆版本化与回滚（候选 D 的"可回滚"）。
- 不做 `effect='write'`（会迫使改 `check_permission` 判定顺序，TASK §8 明禁）。
- 不做 LLM 自动抽取（TASK §2）。
