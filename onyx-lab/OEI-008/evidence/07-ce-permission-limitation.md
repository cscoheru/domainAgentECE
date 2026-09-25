# 07 — Content Engine 无外部权限同步能力（架构事实 + 缓解方向）

> OEI-008 步骤 6 落地。本文件**只写、不实现**——把"CE 无法按用户下推权限 → 引擎召回必须事后过滤 → 侧信道风险"这一架构事实固化成证据，并把可考虑的缓解方向列出供后续刀评估。
> 适用对象：`/api/v1/consulting/library`、`/api/v1/consulting/documents`、`/api/v1/consulting/documents/{id}`、`/engine/status` 这四个调用引擎的端点。

---

## 1. 事实陈述（架构上不可绕过）

`ContentEnginePort` 的**所有方法**——`search` / `engine_status` / `list_projects` / `upload_document` / `document_status`——都**不接受**任何 per-user 权限过滤参数。`OnyxContentEngineAdapter` 调用的端点（`POST /api/search`、`GET /api/admin/llm/provider`、`GET /api/user/projects` 等）也**没有任何 ACL/identity 维度**。

- **Onyx CE 没有外部源权限同步能力**——它的权限模型是「per-credential 的 internal admin control」，不是「per-caller 的 data ACL」。这个结论在 OEI-001 §A9 / OEI-004 CE/EE 边界结论里有明确记录（EE 这边有 `acl_entries` + `PermissionScope` SQL 下推；CE 这边没有等价物）。
- ECE 的 `permissions/engine.py` 把权限**下推成 SQL 子查询**（`permissions/engine.py` 文件头注释明确："SQL subquery filter, NOT post-filter"），但**引擎召回这条路做不到**——`/api/search` 接受查询词返回结果，没有 user_ref / dept / role 之类的参数。
- **唯一可行的位置是 ECE 侧**：拿到引擎召回的结果后再做 per-row 过滤。但这一步**不是「下推」**，而是「事后过滤」——区别在于排序与计数**侧信道**。

## 2. 侧信道风险（具体怎么暴露）

如果「事后过滤」的执行者（CE 适配器 / ECE 路由 / 调用方）按以下方式做事，就会泄漏本不该暴露的信息：

1. **「找不到」枚举**：返回 `hits=N` 给前端，攻击者通过对比 `hits` 数量变化推断某文档是否存在 → 已知关键词命中本库 3 条；换个关键词命中 4 条 ⇒ 「有一条额外的」 ⇒ 文档存在。
2. **排序泄漏**：把 recall 按 `score` 排序后取前 N，再过滤掉 N 条 ⇒ 攻击者通过顺序变化推断哪些文档对该用户不可见（对比匿名 vs 已知 user_ref 看到的顺序）。
3. **内容摘要泄漏**：snippet 不做处理直接展示。即使 doc 整篇不可见，summary 里的字词可能反推出文档主题（这是 LLM 时代的"间接泄露"——cut-005R2 E2 子集中的「间接泄露用例」专门覆盖）。

`permissions/engine.py` 之所以安全（**没有**侧信道），是因为它下推到 SQL 子查询——SQL 层先 `WHERE acl_xxx @> ARRAY[user_ref]` 再排序/截断，过滤掉的数据**根本不参与统计**。CE 这条路拿不到这个保障。

## 3. 缓解方向（至少 3 条，未实现）

| # | 方向 | 工程成本 | 缓解什么 |
|---|---|---|---|
| **M1** | **ECE 侧 per-result filter + 严格 top_k + 一致结果计数** | 低 | 对召回结果做 `if subject in acl_users else skip`；`top_k` 严格上限（不暴露真实命中数）—— 但这条路只**缓解「枚举 / 排序」**，snippet 仍然会泄漏。 |
| **M2** | **按 classification 拆 project + Onyx 多 project 模型** | 中 | Onyx 已经支持 `project_id`，每个 project 配一个不同的 demo cookie；ECE 按 user_ref → classification 决定该把 query 打到哪个 project。**这是当前最接近 v0 + 演示场景的方案**：可以在不上 EE 的前提下把不同敏感级别的文档物理隔离。但要求 Onyx 那边支持 multi-tenant 配置，对演示 demo 的"开箱即用"是个权衡。 |
| **M3** | **snippet 端做 classification-aware 脱敏** | 中 | recall 后做 snippet 红线扫描（敏感字段模式匹配 → 替换为 `[REDACTED]`）—— 缓解 snippet 泄漏，但分类逻辑要靠词表或 LLM，开销与漏判都需评估。 |
| **M4** | **升级到具备外部权限同步能力的引擎** | 高 | 等 Onyx（或自建 EE-onyx-bridge）实现"按 caller ACL 过滤召回"——那是 OEI-009/010/之后的某刀。**不在本刀范围**。 |
| **M5** | **审计 + 红队 + 速率限制** | 低（短期） | `audit_log` 已经在每次引擎调用后留 `caller` + `query`（OEI-008 §A6）；可以加 per-user 的查询速率限制（已有的 `rate_limit.py`）。这**不缓解侧信道**，但**让攻击者更难枚举**。 |

## 4. 现状决策（OEI-008 范围内）

- **不做**：引擎召回的 per-row per-user 过滤。理由：本刀范围只到「身份穿透到 Port + 审计留痕」。过滤算法是 OEI-009。
- **做**（本刀范围）：
  - 每次引擎调用把 `EngineCallerContext` 传给适配器，适配器写一行 audit（who/what/when/result）。
  - 在 `docs/API.md` 明确"引擎召回目前**不做**事后 per-user 过滤，调用方需自行评估；这是 CE 自身能力上限"。
  - 给静态目录的过滤链路（`/library` 的 `type/practice/...` filter）**不受影响**——它走的是 ECE 自己的 SQL 下推（`consulting/service.py` 的 `ConsultingCatalog.search`），不是引擎路径。
- **不是 bug，是事实**：`engine_status="ok" + engine_items=[]` 这种"引擎有召回但 ECE 侧看到 0 条"的情形**可能**对应 per-user filter（未实现但将来会），也可能对应「引擎真的没召回」—— 调用方必须自己区分。**文档必须说明这一点**（见 `docs/API.md` §11 OEI-008 修订）。

## 5. 给后续刀的移交

- **OEI-009**（权限与审计接线）：本刀搭好了 `EngineCallerContext` 通道 + audit_log，下一刀可以直接在路由层加 per-result filter + 速率限制。
- **OEI-010+**（记忆/多租户）：如果走 M2 路线，需要 ECE 侧增加 `ECE_USER_ORGS`-类似的多 project 路由层——但**禁止**静默引入，详见 §6。

## 6. 一处硬约束（不允许的捷径）

- **绝不**通过把 `acl_entries` 的 SQL 拼接到 `/api/search` 的 query 字符串（`/api/search?q=...`）来"下推"过滤 —— 这是注入漏洞，不是下推。如果以后真要下推到引擎，要么引擎侧加专用端点，要么走 EE（cut-042 / OEI-001 §A9）。

---

**相关证据**：`06-audit-trail.json`（audit 留痕实测）；`01-port-identity-contract.json`（Port 五方法签名）；`02-adapter-identity-mock.json` / `03-adapter-identity-onyx.json`（适配器实现 + 留痕）；`05-callers-updated.txt`（4 个调用点接线）。

**代码锚点**：

- `src/ece/connectors/onyx/port.py` — `ContentEnginePort.engine_name` 描述符 + 5 方法的 `caller` 参数；模块 docstring 第 28-32 行明文「CE has no external-source permission sync; per-result filtering happens on the ECE side」。
- `src/ece/connectors/onyx/onyx_adapter.py` — `engine_name = "onyx"`；`_audit()` 记录每次调用的 `caller`；`upload_document` 在 `caller is None` 时抛 `EngineError("identity-required …")`（写路径硬禁止匿名，与路由的 401/403 一致）。
- `src/ece/consulting/router.py:upload_documents` — 调用 `caller_from_db_identity(_get_db(), ...)`，匿名 → 403。