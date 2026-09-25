# OEI-008 任务书 — ContentEnginePort 身份穿透（identity threading）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1.1**（2026-09-25 首轮审验后修订 §7） ｜ 签发日期：2026-09-25
> 返工约定：本刀若需返工，一律标 **`OEI-008 R1` / `R2`**（不插新刀、不顺延既有编号）

> **v1 → v1.1 变更（codex，2026-09-25，由首轮 D4 触发）**：§7 原写"`tests/**` 仅允许新增文件"，与步骤 7 要求的"回归改造"自相矛盾（cc 不得不改 2 个既有测试文件的 fixture/stub，已逐行核实**断言一条未改**）。现改为：**允许新增文件**，且**允许修改既有测试文件的装配部分（fixture / stub / 依赖注入 / import）**，但**断言不得改动、测试不得删除**，改动原因必须写进 REPORT 偏差段。同类错误此前在 OEI-006 出现过一次。
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## 0. 一句话目标

让 **"谁在问"** 成为 `ContentEnginePort` 的一等输入：把 ECE 的身份（现有 `Identity`）显式穿透到 Port 的每个方法与适配器，**消除"调用方手抄引擎类型判断"这类债务**，并把"CE 无法下推权限"这一事实固化成文档与审计。

**为什么是这一刀**（外部 review 的判断 + codex 复核一致）：`port.py` 五个方法的签名里**都没有身份维度**（已核实）；`engine_merge.py:50-58` 因为写权限范围锁，**逐字复制**了 selector 的判断逻辑，并在注释里写明"无法给 Port 加 `engine_name` 描述符"。调用方已有两处（`api/engine_status.py`、`consulting/engine_merge.py`，加上 `consulting/router.py` 两处共 **4 个调用点**），**再往下拖只会更贵**。

## 1. 现状（codex 实测，可直接信任）

### 1.1 身份在 ECE 里已有的形态

- `src/ece/identity/parser.py`：`Identity` 数据类（`user_ref` / `entity_id` / `display_id` / `name` / `department` / `roles` / `aliases` / `source_system` / `is_management`）+ `resolve_identity(engine, x_user_id)` + `upsert_identity(...)`
- 入口约定：`X-User-Id` 头（`api/actions.py:27,42,68`），且 `api/audit.py:86-87` 已升级为 **`Authorization` (JWT) 优先于 `X-User-Id`**（`resolve_caller_user_ref`）
- **注意**：`is_management` 是"显式种子属性，绝不从角色名推导"（cut-040R-2 R40R2.3 的注释）

### 1.2 引擎侧（Port）现状

- `ContentEnginePort` 五方法：`search(query, *, top_k)` / `engine_status()` / `list_projects()` / `upload_document(filename, content, *, project_id, title, metadata)` / `document_status(document_id)` —— **全部没有身份维度**
- 4 个调用点：`src/ece/api/engine_status.py:119`、`src/ece/consulting/engine_merge.py:109`、`src/ece/consulting/router.py:182,278`
- `OnyxContentEngineAdapter` 用**单一服务凭据**（`ECE_ONYX_COOKIE_FILE` 指向的 STANDARD 账号）访问引擎；**CE 没有外部源权限同步能力**（该能力在 EE，见 `OEI-001/REPORT.md` §A9 与 `OEI-004` 的 CE/EE 边界结论）
- `MockContentEngineAdapter` 用**模块级 store**（`reset_mock_engine_store()` 可重置），写状态跨实例存活

### 1.3 本刀要固化的一个架构事实（重要）

`permissions/engine.py` 之所以安全，是因为它把权限**下推成 SQL 子查询**（file 头注释：SQL subquery filter, NOT post-filter）。但**引擎召回这条路做不到**：CE 无权限同步能力 → ECE **只能对引擎返回的结果做事后过滤**，而事后过滤天然带排序/计数侧信道风险。**本刀必须把这个限制写成文档**，并给出缓解方向（不是本刀实现）。

## 2. 范围锁

**做**：Port 契约加身份 → 两端适配器实现 → 4 个调用点接线 → 用 Port 的引擎描述符消掉 `engine_merge` 的手抄逻辑 → 审计记录 → 文档与测试。
**不做**：不做权限过滤算法（那是 OEI-009）、不做记忆（010）、不改 Onyx 任何东西、不引入新依赖、不扩种子内容、不做多租户。

## 3. 工作区与证据命名

```
onyx-lab/OEI-008/
├── TASK.md      ← 本文件（只读）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

`00a-oei007-r1-recapture.txt`、`00b-tasks-reconcile.txt`、`01-port-identity-contract.json`、`02-adapter-identity-mock.json`、`03-adapter-identity-onyx.json`、`04-port-engine-descriptor.txt`、`05-callers-updated.txt`、`06-audit-trail.json`、`07-ce-permission-limitation.md`、`08-test-before-raw.txt`、`09-test-after-raw.txt`、`10-docs-backfill.txt`、`11-git-commit.txt`、`12-compliance-check.txt`

## 4. 任务步骤

**步骤 0 — 两项前置（先做，做完即重建 OEI-007 的 DONE）**

1. **`OEI-007 R1`**：按 `OEI-007/VERDICT.md` §5 重取两条失败路径证据（引擎不可达的上传 + status 502），原地替换进 `OEI-007/evidence/07-failure-paths.json`，并在 `OEI-007/REPORT.md` §A6 标注已重取。完成后**删除旧 `OEI-007/DONE` 并重建**（内容写 `OEI-007 R1 complete`）。**只重取证据，不改代码。**
2. **`TASKS.md` 对账**（外部 review 第 3 条建议）：`TASKS.md` 的 Sprint 0–6 checklist 勾选率几乎全空，而代码早已实现（`/ingest/runs`、ontology 校验、Alembic 0001–0008 等）。**逐项核对并更新勾选状态**，让这份文件不再发出错误的进度信号。产出：改动前/后的勾选统计对比 → `00b`。

**步骤 1 — 定义身份契约（Port 层）**

- 为 Port 引入显式的调用身份。**两种做法都可以，但要写清选择理由**：
  - (a) 直接把现有 `Identity` 传进去；或
  - (b) 在 Port 模块定义一个最小值对象（如 `EngineCallerContext{user_ref, roles, department, is_management, org_id?}`），并提供 `from_identity(Identity)` 的转换
- **硬要求**：
  1. 身份参数在**类型层面可缺省**（`None` 合法），避免一次改动把所有既有调用/测试打爆；但**在 API 边界必须显式解析并传入**（见步骤 4）
  2. Port **不得** import 任何 Onyx 专有物；领域层不依赖 Onyx 的红线不变
  3. 五个方法**全部**带上身份维度（不是只给 search）

**步骤 2 — 用 Port 描述符消掉手抄逻辑**

- 在 Port 上暴露引擎描述符（如 `engine_name`），两端适配器各自实现
- `consulting/engine_merge.py` **删除**那段"逐字复制 selector 判断"的代码，改为读 Port 描述符；保留或改写其注释（说明债务已消除）
- 产出：`04-*` 给出"删除的手抄代码"与"替换后的实现"对照

**步骤 3 — 两端适配器实现**

- `MockContentEngineAdapter`：身份要可观测（例如按 `user_ref` 分域，或至少在文档/状态里回显），且**保持确定性**；`reset_mock_engine_store()` 行为要写清
- `OnyxContentEngineAdapter`：**接受**身份；**每次调用记录身份到审计/来源**；**明确文档化**"CE 无法按用户下推权限，per-user 强制在 ECE 侧"（与 §1.3 呼应）

**步骤 4 — 4 个调用点接线**

- `api/engine_status.py`、`consulting/engine_merge.py`、`consulting/router.py`(两处) 全部改为：**解析调用者身份 → 传进 Port**
- 身份来源沿用既有约定：`Authorization`(JWT) 优先，其次 `X-User-Id`；**缺身份时的策略要明确**（建议：`/engine/status` 与 library 允许匿名但标注 `anonymous`；上传端点建议要求身份 —— 你定，但要写清并落进 `docs/API.md`）

**步骤 5 — 审计与来源**

- 每次引擎调用留痕：`who`（身份）、`what`（方法/参数摘要）、`when`、`result`（成功/失败/命中数）→ `06-*`
- 复用既有审计能力（`src/ece/audit/`、`0005_context_audit`），**不要新造一套**

**步骤 6 — 文档化那条限制**

`07-ce-permission-limitation.md`：写清"CE 无权限下推 → 引擎召回必须事后过滤 → 侧信道风险"这一事实，并列出至少 **3 条缓解方向**（例如：按 classification 拆 project / 收紧 top_k 并做结果计数保护 / 升级 EE 以启用外部权限同步）。**只写，不实现。**

**步骤 7 — 测试**

1. **DB 无关单测**（新文件，如 `tests/unit/test_content_engine_identity.py`）：Port 五方法的身份可缺省；mock 按身份分域且确定性；缺身份策略；`engine_name` 描述符两端一致
2. **调用点回归**：断言 `engine_merge` 不再包含 selector 的复制逻辑（例如一条 grep/import 断言测试）
3. **无回归**：跑全套件（基线 `737 passed / 0 failed`），落盘原始汇总行

**步骤 8 — 文档与提交**：`docs/API.md` 补身份约定与缺省策略；`TASKS.md` 补本刀条目；`git add` + `git commit`（**不 push**）

## 5. 验收标准（codex 将逐条核对）

- [ ] **A0** 步骤 0 完成：`OEI-007/evidence/07-failure-paths.json` 的 ④ 与 status-502 已被真实 onyx 模式响应替换（我复审）；`OEI-007/DONE` 重建；`TASKS.md` 勾选状态与代码事实对齐（给出前后统计）
- [ ] **A1** Port 五个方法**全部**带身份维度，且类型可缺省；`port.py` 里有明确 docstring 说明"身份用于什么、CE 这一层能/不能做什么"
- [ ] **A2** 调用方**不再手抄**引擎类型判断：`engine_merge.py` 的镜像逻辑已删除并由 Port 描述符替代（给出删除/替换对照）
- [ ] **A3** mock 适配器：身份可观测 + 确定性保持（给出同输入 N=5 或等价证明）
- [ ] **A4** onyx 适配器：接受身份并在每次调用留痕；**明确记录"CE 无法按用户下推权限"**（代码注释 + `07-*`）
- [ ] **A5** 4 个调用点全部接线；缺身份策略在 `docs/API.md` 有明文，且实测行为与文档一致（给出各端点缺/带身份两种实测）
- [ ] **A6** 审计留痕可用：至少一次真实 onyx 调用可在审计面查到 `who/what/when/result`
- [ ] **A7** `07-ce-permission-limitation.md` 存在，且"事后过滤的侧信道风险 + ≥3 条缓解方向"写清
- [ ] **A8** DB 无关单测通过（落盘输出）；**无回归**（failed ≤ 基线 0）
- [ ] **A9** 文档与提交：`docs/API.md` + `TASKS.md` 已更新；commit（**不 push**）
- [ ] **A10** 合规：无凭据值落盘；未碰 Onyx 上游/compose/`.env`/swap/`.wslconfig`；未改 36 个种子对象与三域业务逻辑；既有测试断言语义未改；未 push
- [ ] **A11** **不使用"用户截图"作为任何验收项**；可见性/行为证据一律机器可校验

## 6. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏、临时资源已清理
2. `echo "$(date -Iseconds) OEI-008 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并签发 OEI-009（权限与审计接线）；FAIL → 按 `R1/R2…` 返工

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：改 `src/ece/connectors/onyx/**`、`src/ece/api/**`、`src/ece/consulting/**`、`src/ece/identity/**`（只读复用优先）、`src/ece/audit/**`（复用）、`docs/API.md`、`TASKS.md`；`tests/**` **允许新增文件，且允许修改既有测试文件的装配部分（fixture / stub / 依赖注入 / import）——断言不得改动、测试不得删除**；可起临时 `ece-pg-tmp` 跑套件；可 `git commit`（**不 push**）；可为 `OEI-007 R1` 重取证据并重建 `OEI-007/DONE`
- ❌ 不引入新依赖；不改 `pyproject.toml` / `uv.lock`
- ❌ 不改 36 个种子对象内容；不改采购/知识/合规三域业务逻辑与其测试断言
- ❌ 不 restart/stop/down/rm 任何 Onyx 容器；不改 Onyx 上游/compose/`.env`；不碰 swap/`.wslconfig`
- ❌ 不做权限过滤算法、不做记忆、不做多租户（分别是 OEI-009/010/非目标）
- ❌ 不得要求用户截图

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-008/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-008/DONE`（以及 `OEI-007/DONE` 的重建）
- 无新文件则静默，不重复执行、不打扰用户
