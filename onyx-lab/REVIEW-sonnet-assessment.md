# 外部 review 评估：`sonnet给ece项目的建议.md`（codex 落档）

> 日期：2026-09-25 ｜ 评估人：codex（架构 + 审验） ｜ 原文：`OEI-007/sonnet给ece项目的建议.md`
> 结论摘要：**采纳 4 项；新增 1 项事实（context assembly 第 6 步是 stub，正好是 OEI 在做的事）**；对"记忆"给出明确架构立场。

---

## 1. 逐条核实（codex 实测，不是转述）

| # | review 的说法 | 核实结果 | 处理 |
|---|---|---|---|
| 1 | `ContentEnginePort` 没有 identity 参数 | **属实**：`port.py` 五个方法（`search`/`engine_status`/`list_projects`/`upload_document`/`document_status`）签名里都没有身份维度 | **采纳**：单开一刀做"身份穿透"（见 §3） |
| 2 | `engine_merge.py` 逐字复制了 selector 的判断逻辑 | **属实**：`engine_merge.py:50-58` 有注释写明"mirrors the switch in selector.get_content_engine()… we cannot add an `engine_name` descriptor to the port…"，并声明不做任何"优化"以防走样 | 采纳；该注释本身就是"范围锁副作用"的第一手证据 |
| 3 | 权限引擎成熟：deny > user > role > dept > classification 默认 > default deny；**SQL 子查询过滤而非后置过滤** | **属实**：`permissions/engine.py:4-5` 原文如此；且 `restricted` 默认值由 `allow_dept` 改为 **`deny`**，注释记录了真实越权（e2-025：procurement + PR001 + restricted 期望 deny 却被放行） | **采纳（重要）**：权限刀要"接线"而不是"从零做" |
| 4 | ACL 缺 classification 维度，是已登记的局限 | **属实**：`engine.py:42` 起有明确注释与后果说明 | 记录为已知局限，不改模型 |
| 5 | `context/assembly.py` 在权限判定之后跑 | **属实**：12 步里第 3 步定权限、第 5 步带权限过滤取关系；文件头注明 per ADR-004 + PRD §29，fail-closed | 采纳 |
| 6 | `TASKS.md` 的 Sprint 勾选率几乎全空、严重低估进度 | **属实**：Sprint 0 六项全是 `- [ ]`，而代码早已存在（`/ingest/runs`、ontology 校验、Alembic 0001–0008 等） | 采纳：作为下一刀步骤 0 对账 |
| 7 | "记忆系统"存在？ | **不存在**：`grep memory` 的命中都是无关词（in-memory 参数、配额等）；没有任何跨会话记忆实现 | 见 §2 |

### 1.1 codex 新增的一条关键事实（review 没提到）

`src/ece/context/assembly.py` 的 12 步里，**第 6 步"Retrieve authorized documents（FTS/vector + classification+ACL）"与第 7 步"structured data"至今是 stub**。

**我们 OEI-006/OEI-007 做的"引擎召回 + 上传入库"，正好就是给第 6 步补上真实实现**（只是走的是 Onyx 而不是 ECE 自研检索）。这条连接此前没有被任何文档写出来——它意味着：

- OEI 这条线**不是平行的新支线**，而是**在给既有 context pipeline 装第 6 步**；
- 后续把 Library 的召回接回 `context/assembly.py`（而不是停在 consulting 模块自用），才是"底座"真正合拢的时刻；
- 建议在 OEI-009（权限/审计接线）里一并评估：**让 context assembly 的第 6 步调用 `ContentEnginePort`**。

## 2. 关于"持久上下文记忆"——codex 的架构立场（回应 user 的问题）

### 2.1 先把三个被混用的概念拆开

| 层 | 是什么 | 现状 | 生命周期 |
|---|---|---|---|
| **会话凭据** | cookie / token：证明"这次请求是谁发的" | 用的是 **Onyx 的 session cookie**（借来的身份） | 短效、可撤销 |
| **身份 identity** | 用户是谁、属哪个组织/部门/角色 | ECE 有 `identity/parser.py`（`resolve_identity(x_user_id)`）+ `0007_user_orgs` 迁移；但**是 `X-User-Id` 头，不是登录** | 长期 |
| **持久上下文记忆** | 跨会话保存的、关于用户/组织/项目的事实与偏好，下次自动参与上下文组装 | **完全没有** | 长期（用户要求"一直保存"） |

user 要的是第三层。**而第三层要求第二层先成立**——"从第一次登录后"意味着 ECE 得有自己的登录与会话，而不是继续借 Onyx 的 cookie。这与 review 指出的"identity 穿透"债务是**同一个问题的两端**。

### 2.2 立场：记忆必须归 ECE，不能放 Onyx

- Onyx 侧确实有 `personalization.memories` / `enable_memory_tool`（`GET /api/me` 可见），但它是**引擎侧、无来源、无审计、不可迁移**的。
- 把用户上下文放在可替换引擎里，等于**把"用户上下文"这个核心 IP 交给可替换件**：换引擎即丢，且与 `AGENTS.md` §6 / CODEX-ROLE R1（ECE 拥有身份/权限/来源/审计）直接冲突。
- **可考虑的例外**：将来若需要，ECE 可以把**自己记忆里的子集**下发给引擎做个性化（单向、可撤销），但**系统 of record 永远是 ECE**。

### 2.3 形态建议（第一版）

1. **记忆是一等领域对象**：`owner`（user/org/team）、`scope`、`statement`、`source`、`created_at`、`confidence`、`expires_at`。复用 `context/provenance.py` 的来源追踪思路。
2. **写入过权限引擎**：谁能写/读/删谁的记忆，走既有 `permissions/engine.py`（不是新造一套）。
3. **读取进 context assembly**：作为管道里的显式一步，**位置必须在权限判定之后**（否则重蹈"后置过滤"的侧信道坑）。
4. **合规三件套是前提而非附加项**：可查看、可删除（单条 / 全量）、可追溯（来源 + 时间 + 谁写的）。没有这三件，"永久保存"是负债而不是资产。
5. **第一版不做 LLM 自动抽取**：自动抽取不确定，无法做确定性验收（沿用 OEI-007 立下的规矩）。第一版做**显式记忆**（用户/管理员显式声明）+ 自动注入 + "本次回答用到了哪几条记忆"的可见性。

## 3. 采纳后的排期建议（编号不变、不插刀、不顺延）

```
OEI-007 R1   重取 2 条失败路径证据（进行中）
   └─► OEI-008  ContentEnginePort 身份穿透
                步骤 0：TASKS.md 与真实代码对账
                （吸收 review 的"债务在变贵"判断）
          └─► OEI-009  权限与审计接线（复用既有 permission engine）
                        含：记忆的权限/审计骨架；评估 context assembly 第 6 步改调 Port
                 └─► OEI-010  持久上下文记忆 v1（显式记忆 + 注入 + 三件套）
```

**依赖理由**：记忆若早于权限落地，就是又一个"后置过滤"式越权风险；因此顺序是 identity → 权限/审计 → 记忆。

## 4. 待 user 决策

### 4.1 决策记录（2026-09-25，用户）

1. **按 §3 顺序推进** —— identity → 权限/审计 → 记忆。据此签发 **`OEI-008`（身份穿透）**；原 008 权限壳层顺延为 **009**，记忆为 **010**。
2. **记忆范围：用户级 + 组织级都做** —— 用户级偏好与事实、组织级口径/术语/模板都要。**对 OEI-009 的影响**：权限骨架必须一开始就支持 **org scope**（组织级记忆的可见性/可写性不能事后补），否则第 010 刀会被迫改权限模型。
3. **不做"本次回答引用了哪几条记忆"的可见性** —— 用户判断"太机械刻意"。**执行约束**：memory v1 的验收里**不得**出现该条款；记忆的生效方式应是**静默注入**（若有可追溯需求，走已有的 `context/provenance.py` 审计面，而不是在回答区展示"引用了几条记忆"）。

### 4.2 仍待澄清

- 组织级记忆的**写入权限**（谁能改组织口径：管理员？领域负责人？）——留待 OEI-009 设计时定。

1. 是否按 §3 的顺序推进（即先签 OEI-008 身份穿透）？
2. 记忆的**范围**：第一版只做"用户级偏好与事实"，还是同时做"组织级记忆"（口径、术语、模板）？后者价值更高但权限模型更复杂。
3. 记忆的**可见性面**：是否要求"本次回答引用了哪几条记忆"在界面上可见（我建议要求——它是可追溯性的直接体现，也是演示亮点）。
