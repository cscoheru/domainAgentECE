# S2_REVIEW_BRIEF.md — 审验导航与重点（给能读取本仓库的审阅者）

> Date: 2026-09-21
> 对象: V0 Technical Spike **S2**（`evidence_records` 迁移 + `persist_evidence`）
> 配套: `docs/v0/S2_REPORT.md`（我的自述）· `docs/v0/V0_EXECUTION_SPEC.md`（规格）

---

## 0. 一句话

**这份文件不是证据，是指路 + 追问清单 + 判定要求。**

你能直接读本仓库，所以我没有把内容复制成"可粘贴包"。请**以代码和数据库为准**，
不要把 `S2_REPORT.md` 的结论当作已证事实 —— 那是一份**自述**，它的价值在于给出断言，
而验证是你的工作。

**本轮审验范围极小**：一张表、两个函数、7 个测试。请判 **PASS / PASS WITH CONDITIONS / HOLD**。

---

## 1. 你的角色与硬边界

你要做的是**外部独立、对抗性**的审验，不是代码审查风格的"提改进建议"。

**硬边界（越界即无效建议）**：

- **V3 架构已冻结**。不要建议修改 V3 PRD / KERNEL_BOUNDARY / KERNEL_ARCHITECTURE_V3 / V3_CLOSEOUT。
- **`V0_EXECUTION_SPEC.md` 已审验通过**（上一任审阅者已正式批准 S1–S6 顺序执行）。
  不要要求重写它 —— 但**§4 第 1 条**是它的一处内部缝隙，那一处**需要你裁定**。
- **本轮不是 S3**。不要要求 S2 里出现 rule / decision / context update。
- **不得通过修改 expected / threshold / fixture 迎合实现**。

**如果你发现真实问题**，按这套格式报（这是本项目既定的规格）：

```
failure / root cause / affected scope / proposed minimal fix
```

---

## 2. 读什么（路径地图）

| 你想知道 | 读这个 |
|---|---|
| 本轮改了哪些文件 | `git show --stat HEAD`（ece 仓，commit `afe72ff`） |
| 我的自述与断言 | `docs/v0/S2_REPORT.md` |
| **规格原文**（唯一权威） | `docs/v0/V0_EXECUTION_SPEC.md` §7（Evidence schema）·§9（调用关系）·§10.1（三个专项测试）·§14（S1–S6 顺序） |
| 本轮实现 | `src/ece/evidence/store.py` · `src/ece/evidence/__init__.py` |
| 本轮迁移 | `src/ece/migrations/versions/0008_evidence_records.py` |
| 本轮测试 | `tests/integration/test_v0_evidence_persistence.py` |
| Evidence 为何**不能**是工程 trace | `docs/v3/KERNEL_BOUNDARY.md` §5（四种产出的区分） |
| Evidence 为何是 Kernel 核心对象 | `docs/v3/V3_CLOSEOUT.md` §1.2 |
| Context 的真实形态（本轮依赖它） | `src/ece/context/assembly.py`（`ContextPackage` :43 · 实体构造 :234-240 · `package_id` 生成 :142） |
| 身份与 `X-User-Id` 的真实含义 | `src/ece/identity/parser.py`（`Identity.user_ref` :21） |

**复现命令**（请不要只读，实际跑）：

```bash
cd ece
make db-upgrade                                     # 应用 0008
uv run pytest tests/integration/test_v0_evidence_persistence.py -v
make test                                           # 全量回归
uv run ruff check src/ece/evidence/ && uv run mypy src/ece/evidence/
uv run lint-imports                                 # 架构契约
uv run alembic -c src/ece/migrations/alembic.ini downgrade 0007_user_orgs   # 回滚
uv run alembic -c src/ece/migrations/alembic.ini upgrade head               # 复原
```

---

## 3. 审验范围（本轮 = S2）

**规格 §14 对 S2 的定义**：`evidence_records 迁移 + persist_evidence`。
**上一任审阅者对 S2 的额外限定**：*"只实现 V0 所需字段和查询能力 …… 不要扩展成 Evidence Framework。不要做 ranking / search / graph / UI / versioning。"*

**验收点**：

| # | 断言 | 在哪验 |
|---|---|---|
| 1 | 表存在且字段与 §7 一致 | `information_schema.columns`（12 列） |
| 2 | 每个 **passed** 条件产出一条 Evidence，failed 不出 | 测试 `test_persist_evidence_writes_one_row_per_passed_condition` |
| 3 | 反查链 `decision → evidence → source → input_context_ref` 每一跳可查 | 测试 `test_reverse_chain_...` |
| 4 | Evidence 按 decision 隔离 | 测试 `test_evidence_is_scoped_to_its_own_decision` |
| 5 | **没有**ranking / search / graph / versioning / UI | 读 `store.py` 全文（180 行，一分钟读完） |
| 6 | 既有文件零改动（范围锁） | `git show --stat HEAD` + `git status` |

---

## 4. ⭐ 重点盯这 6 处（按价值排序）

### 第 1 处 —— 规格 §6/§7 的**内部缝隙**（**需要你裁定**）

- §6 的 `evaluated_conditions` 元素只有 4 个键：`name` / `expr` / `actual` / `passed`；
- §7 要求每条 Evidence 带 `claim` 与 `threshold`；
- **两者无法同时满足**：`claim = "报价家数 1 < 3"` 推不出自 `expr = "quote_count < 3"`；
- 而 §9 把 `persist_evidence(engine, ctx, dec)` 的输入限定为 `dec`，信息必须随 `dec` 到达。

**我的处置**：规则在每条条件上**额外**给 `claim` / `threshold`（6 键，是 §6 那 4 键的**超集**），
业务措辞留在规则层。`persist_evidence` 把 `claim` 视为 passed 条件的必需键，缺失即报错。

**请裁定这一处置是否可接受。** 另外两条路（改 §6 规格 / 在持久化层放 rule→claim 映射表）我判断都更差，
理由在 `S2_REPORT.md` §3 —— 若你不同意，请说明。

### 第 2 处 —— ⚠️ **我承认一处没验证到位：§10.1 的最后一跳**

规格 §10.1 要求反查链是 `decision → evidence → source → input_context_ref → **原始 context package**`，
判据是"**链路每一跳可查**"。

**我的测试只断言了 `evidence["input_context_ref"] == ctx.package_id`** ——
那证明的是"这个值被正确持久化并读回"，**不是"从它真的能查回原始 Context"**。
这是**自证**：我把自己传进去的值当成了验证对象。

事实（已核实，请复核）：

- `package_id = f"ctx_{request_id.hex[:24]}"`（`assembly.py:142`）——**从 request_id 派生**；
- `context_requests` 表里**没有 `package_id` 列**（列清单：`request_id, user_ref, intent, spec_version,
  root_entities, as_of, counts, latency_ms, llm_model, status, created_at, org_id`）；
- 因此 `input_context_ref` **能**推导回 `request_id`（取前 24 位 hex 前缀匹配），
  但那是**前缀匹配**，不是等值 join，且**全库没有一处代码或测试真的走过这一跳**。

**请你判断并按项目格式给出处置意见**：这是规格实现问题，还是仅有测试缺口？
若需要在 S2 补（而不是留到 S6），最小修法是什么？（例如给 `evidence_records` 加 `request_id`，
使这一跳成为等值 join —— 但那会偏离 §7 的字段集，所以我**没有自行决定**。）

### 第 3 处 —— Evidence **不复用** `context_items` 的判断

我判定：Evidence 必须新表，**不能**复用 `context_items`，理由是后者是**工程审计**
（`item_kind` / `score` / request 记账），而 `KERNEL_BOUNDARY.md` §5 明文要求
**Business Evidence ≠ 工程 trace**（四种产出的区分：Execution Reference / Agent Output /
Business Evidence / State Change）。

这是**架构性判断**，若你不同意，属于 blocker 级。请直接判。

### 第 4 处 —— 三处 `raise` 的松紧

`store.py` 里三处拒绝：① passed 条件缺 `claim`；② Context 里 `purchase_request` 不**恰好**一个；
③ 实体缺 `src` provenance。

**问**：有没有哪一处**过严**（会把合法输入挡掉）或**过松**（该挡没挡）？
特别是 ② —— 它是 spike 假设（fixture 只有 1 个 PR）。它在 S5/S6 会不会变成限制？

### 第 5 处 —— 这些测试**真的能抓错吗**

请**动手验证**，不要只读：

1. 把 `store.py` 里 `if not condition.get("passed"): continue` **删掉** → 测试应变红；
2. 把 `_SUBJECT_ENTITY_TYPE` 的匹配改成不检查类型 → 应变红；
3. 把 `input_context_ref` 写死成 `""` → 应变红。

若某一步改坏实现后测试**仍然全绿**，那就是一个**未被覆盖的断言** —— 请报出来。
（本项目此前多次栽在"测试通过，但通过得没有意义"上，这是最值得花时间的一处。）

### 第 6 处 —— 反查的排序选择

`get_evidence_for_decision` 用 `ORDER BY evidence_timestamp, claim`。
理由：§7 的最小字段集里**没有序号列**，而在同一事务内 `now()` 相同，
所以按时间排不出稳定顺序。请判断这是否可接受，或应改为其他方式（加序号列会偏离 §7）。

---

## 5. 判定与输出要求

请给出 **PASS / PASS WITH CONDITIONS / HOLD** 之一。

其中 **HOLD** 的用法请沿用本项目约定：
> **只要存在一个"进入下一阶段前必须解决"的问题，就不能 GO。**

输出请包含：

1. **你实际跑了什么命令、看到什么输出**（与"你只读了代码"区分开）；
2. 每一处重点的裁定（§4 的 6 处）；
3. 若有 failure：`failure / root cause / affected scope / proposed minimal fix`；
4. **明确列出你认为"必须由我（用户）决定"的事项**（若有）。

---

## 6. 明令禁止的建议（提了等于无效）

- ❌ 修 V3 PRD / KERNEL_BOUNDARY / KERNEL_ARCHITECTURE_V3 / V3_CLOSEOUT
- ❌ 重写 `V0_EXECUTION_SPEC.md`（只有 §4 第 1 处缝隙需你裁定）
- ❌ 在 S2 里实现 rule / decision / context update（那是 S3 / S4）
- ❌ Evidence Framework 类能力：ranking / search / graph / versioning / UI
- ❌ 引入 LLM —— **本次 spike 明令 Decision 必须是确定性规则，不得引入 LLM 决策**；
  也不得为了满足"1 Agent + Local Provider"的名义范围新增 Agent/Provider abstraction
- ❌ 新增 Kernel object / Adapter / Interface abstraction / Trigger.dev / DSH / Glean /
  Multi-Agent / Generic RAG / Generic Connector / Builder UI / SaaS / Workflow Engine
- ❌ 修改 business rules / evaluation 标准 / fixture 以迎合实现

---

## 7. 项目当前冻结状态（供你定位，不要再重开）

```
V3 架构冻结
  → V0_EXECUTION_SPEC.md（S1–S6）已审验通过
  → S1 spike fixture PASS（曾因 R2 canonical seed 缺陷被 HOLD，已修复）
  → R2 / R2.1 canonical seed 完整性修复 PASS
  → Foundation Reuse Study 关闭（结论：不存在可整体采用的 OSS Kernel foundation；
     Evidence 与 Deterministic Business Rules 必须自建）—— 已归档，勿重开
  → **S2 本轮（evidence_records + persist_evidence）** ← 你在这里
  → S3 rule + decision → S4 context update → S5 串六步 → S6 三个专项测试
```

**每个 S 完成后回来验一次**是既定的节奏。S2 到此为止，**未实现 S3**。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-21
**Status**: 待审验。
