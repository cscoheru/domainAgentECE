# V0_EXECUTION_SPEC.md — V0 Technical Spike 执行规格

> Date: 2026-09-20
> Status: **DRAFT — 待审。审阅通过前不写 V0 实现代码。**
> 上游: `docs/v3/V3_CLOSEOUT.md` §2（6 步闭环）· `docs/v3/MVP_SCOPE_V3.md` §6（DoD）· 用户执行指令（2026-09-20）
> 性质: **工程可执行定义**，不是架构文档。V3 架构已冻结，本文件不新增任何 Kernel 对象。

---

## 0. 一句话

> 用**已有的确定性规则** + **已有的权限强制路径**，把
> `Context → Entity/Knowledge → Rule → Decision → Evidence → Context Update`
> 跑成一条**每步都有可检查产物**的闭环，且第六步**真的改变业务状态**。

**这不是 PMF 验证，不是完整 Kernel，不是最终产品。**

---

## 1. Technical Spike Fixture 是什么

**一个最小的合成采购评审场景**，`source_system = 'spike:v0-technical-fixture'`。

```
TECHNICAL SPIKE FIXTURE
NOT CUSTOMER-VALIDATED
NOT PRODUCT REFERENCE WORKFLOW
```

| 对象 | source_id | 关键属性 |
|---|---|---|
| 采购申请 | `SPIKE-PR-001` | `amount = 1_280_000`；`review_status = "pending"`；`approvals = []` |
| 供应商 A/B/C | `SPIKE-SUP-A/B/C` | 三个，**但只有 1 条 SELECTS 关系** |
| 政策 | `SPIKE-POL-001` | 采购政策占位 |
| 用户（有权限） | `spike-user-procurement` | `department = "procurement"`, `roles = ["buyer"]` |
| 用户（无权限） | `spike-user-unrelated` | `department = "sales"` |

**关系**：`SPIKE-PR-001 -SELECTS-> SPIKE-SUP-A`（仅 1 条 → 触发比价规则）。

**寻址纪律**：fixture 一律用 **`source_id`** 寻址，运行时解析 `display_id`。
**不得**在代码/测试里硬编码 `PR4xx` 这类 display_id —— FER 已证明它会漂移并使资产静默过期。

**Seed**：`scripts/seed_v0_spike_fixture.py`，幂等（**DELETE-then-INSERT 限于自身 source_system**）。

---

## 2. Domain Pack 是什么

**复用现有的 `src/ece/domain_packs/procurement/`，1 个 pack，不新建。**

已存在且直接复用：
- `context_specs/evaluate_purchase_request.yaml`（**1 个固定 WorkflowSpec**）
- `agent/rules.py` —— **纯 Python 确定性规则**（`check_price_comparison_required` / `check_approval_chain`）
- `agent/agent.py` —— LLM 仅作辅助（本 spike 的 Decision **不经过 LLM**）

**本 spike 不新增 Domain Pack，不新增 WorkflowSpec。**

---

## 3. Context 最小 schema

**直接复用现有 `ContextPackage` 的形态，不发明新结构**（`src/ece/context/assembly.py`）：

| 字段 | 本 spike 用到的部分 |
|---|---|
| `package_id` | 作为 `input_context_ref`（Evidence / Decision 回指） |
| `user` | `{id, display_id, department, roles, is_management}` |
| `entities[]` | `{ref, type, name, attrs, src}` —— `attrs.amount` / `attrs.review_status` 是本 spike 的关键输入 |
| `relationships[]` | `{from, rel, to, valid, src}` —— `SELECTS` 的条数即"报价家数" |
| `denied[]` | `{ref, reason}` —— 非空即代表权限拦截发生 |
| `sources[]` | provenance |
| `metadata` | `{generated_at, as_of, counts, insufficient_context}` |

**不新增字段。** `review_status` 放在既有 `entities[].attrs` 内（它是实体属性，不是新对象）。

---

## 4. Entity / Knowledge 从哪里进入 Context

**走现有 12 步流水线，不新开路径。**

```python
pkg = assemble_context(
    engine      = get_engine(),
    user_ref    = "spike-user-procurement",
    intent      = "evaluate_purchase_request",
    entities    = [{"type": "purchase_request", "id": <PR-SPIKE-001 的 display_id>}],
    pack        = "procurement",
)
```

- **Entity** 由流水线的实体解析 + 关系扩展填充（`SELECTS` → 供应商）。
- **Knowledge** 本 spike 取 `relationships[]` + `sources[]`；文档/结构化数据不在 V0 范围。
- **权限在此路径内强制**（见 §10）。

---

## 5. 一个确定性 Business Rule

**规则 ID：`R-SPIKE-REVIEW`**（纯 Python，无 LLM）

```
required_quotes = 3
threshold       = 1_000_000           # 复用 rules.py 的 PRICE_COMPARISON_THRESHOLD

IF  pr.amount >= threshold
AND quote_count(pr, rel="SELECTS") < required_quotes
THEN decision_value := "review_required"
ELSE decision_value := "auto_approved"
```

- 数据来源：`pr.amount` ← `entities[purchase_request].attrs.amount`；`quote_count` ← `relationships` 中 `rel == "SELECTS"` 的条数。
- **不使用 LLM**。同样输入必须得到同样 Decision（见 §10 的确定性测试）。
- 复用现有阈值常量，**不新造阈值**。

---

## 6. Decision 输入 / 输出

**输入**：`ContextPackage`（只读；rule 不得写库）

**输出**：

```jsonc
{
  "decision_id": "dec_<uuid>",
  "rule_id": "R-SPIKE-REVIEW",
  "decision_key": "review_status",
  "decision_value": "review_required",          // 或 "auto_approved"
  "evaluated_conditions": [
    {"name": "amount_gte_threshold", "expr": "amount >= 1000000",
     "actual": 1280000, "passed": true},
    {"name": "quote_count_lt_required", "expr": "quote_count < 3",
     "actual": 1, "passed": true}
  ],
  "reason": "金额 1,280,000 ≥ 1,000,000（100万阈值）且仅 1 家报价（需 3 家）→ 需人工复核",
  "input_context_ref": "ctx_<24hex>",           // = package_id
  "request_id": "<context_requests.request_id>"
}
```

**`evaluated_conditions` 是必需的** —— 它让"为什么是这个 Decision"可复核，而不是一句 LLM 叙述。

---

## 7. Evidence 最小 schema

```jsonc
{
  "evidence_id": "ev_<uuid>",
  "decision_id": "dec_<uuid>",
  "rule_id": "R-SPIKE-REVIEW",
  "claim": "金额 1,280,000 ≥ 1,000,000（100万阈值）",
  "source": {"system": "spike:v0-technical-fixture", "record_id": "SPIKE-PR-001"},
  "observed_value": 1280000,
  "threshold": 1000000,
  "actor_user_ref": "spike-user-procurement",
  "timestamp": "2026-09-20T…Z",
  "input_context_ref": "ctx_<24hex>"
}
```

**每个 `passed` 条件产出一条 Evidence**（本 fixture 两条）。

**落点**：新增最小表 `evidence_records`（alembic 迁移）。

> ⚠️ **请审阅此判断**：这不是"新增 Kernel 对象"——**Evidence 是 V3 Kernel 五项核心之一**，本表是**实现已定义对象**，不是引入新概念。
> 我**没有**复用 `context_items`：该表是**工程审计**（`item_kind` / `score`），而 `KERNEL_BOUNDARY.md` §5 明确要求
> **业务 Evidence ≠ 工程 trace**。若审阅认为新增表仍属架构变更，请指出 —— 那将是本轮唯一可能的 architecture blocker。

---

## 8. Context Update 修改哪个状态

**修改 `entities.attributes`（同一条 `SPIKE-PR-001` 行）**：

| key | before | after |
|---|---|---|
| `review_status` | `"pending"` | **`"review_required"`** |
| `review_decision_id` | 无 | `dec_<uuid>` |
| `review_evidence_id` | 无 | `ev_<uuid>` |
| `review_updated_at` | 无 | ISO 时间戳 |

```sql
UPDATE entities
SET attributes = COALESCE(attributes,'{}'::jsonb) || jsonb_build_object(
      'review_status',      CAST(:value AS text),
      'review_decision_id', CAST(:dec   AS text),
      'review_evidence_id', CAST(:ev    AS text),
      'review_updated_at',  CAST(:ts    AS text))
WHERE id = :entity_id;
```

**验证方式（§7 要求 —— 必须是"真的"）**：

```python
before = reassemble(...)["entities"][0]["attrs"]["review_status"]   # "pending"
run_loop(...)                                                        # Decision + Evidence + Update
after  = reassemble(...)["entities"][0]["attrs"]["review_status"]   # "review_required"  ← 必须
```

**不得**的做法：把 Decision 原样塞回 Context 冒充更新（例如写 `decision` 字段）。判据是
**"下一次 assemble 能读到变化后的业务状态"**。

---

## 9. 六步之间的实际调用关系

```
scripts/run_v0_loop.py :: run_v0_loop(user_ref, pr_source_id) -> V0LoopResult
│
├─ [1] ctx = assemble_context(engine, user_ref, "evaluate_purchase_request",
│                             [{"type":"purchase_request","id": resolve(pr_source_id)}],
│                             pack="procurement")
│        └─ 权限在此路径内强制 (12 步流水线步骤 3)
│
├─ [2] pr   = ctx.entities 中 type=="purchase_request" 的那条
│      quotes = [r for r in ctx.relationships if r["rel"] == "SELECTS"]
│      ── 若 1) ctx.denied 非空 且 2) pr is None → 判定"无可用 Context"，
│          decision = None，**不进入 [3]**，直接返回 reason="no permitted context"
│
├─ [3] cond = evaluate_rule_R_SPIKE_REVIEW(pr.attrs["amount"], len(quotes))   # 纯函数
│
├─ [4] dec  = build_decision(cond, ctx)          # 见 §6 schema
│
├─ [5] evs  = persist_evidence(engine, ctx, dec) # 见 §7 schema；每条 passed 条件一条
│
├─ [6] apply_context_update(engine, pr.entity_id, dec, evs)   # 见 §8
│
└─ re-read: assemble_context(...) → assert attrs.review_status == dec.decision_value
```

**用到的现有件**：`assemble_context` / `check_permission`（经流水线）/ `rules.py` 阈值常量。
**本 spike 新增的代码**：`evaluate_rule_R_SPIKE_REVIEW`（~15 行纯函数）、`build_decision`、`persist_evidence`、`apply_context_update`、`run_v0_loop`。

**不新增**：Adapter / Interface 抽象 / Agent 编排 / 队列 / Runtime 选择。

---

## 10. 如何验证每一步的 output

`scripts/run_v0_loop.py` 逐步打印并断言：

| 步 | 可检查产物 | 断言 |
|---|---|---|
| 1 Context | `ctx.package_id` + `ctx.entities` / `ctx.relationships` 条数 | `package_id` 非空；PR 在 `entities` 内 |
| 2 Entity/Knowledge | 归一后的 PR `ref` + `attrs.amount`；`SELECTS` 关系列表 | `amount == 1280000`；`len(quotes) == 1` |
| 3 Rule | `rule_id` + `evaluated_conditions[]`（逐条 expr/actual/passed） | 两条条件均 `passed == True` |
| 4 Decision | `decision_id` / `decision_key` / `decision_value` / `reason` | `decision_value == "review_required"` |
| 5 Evidence | `evidence_id[]` + 每条 `source.system` / `record_id` / `timestamp` / `input_context_ref` | 条数 == `passed` 条件数；可反查 |
| 6 Context Update | `entities.attrs.review_status`（更新前后） | **更新后 == "review_required"**，且重读仍是 |
| 闭环 | `V0LoopResult` 全字段 | 六步产物齐备 |

### 10.1 三个专项测试（用户指令 §八 / §九 / §十）

| 测试 | 做法 | 通过判据 |
|---|---|---|
| **确定性** | 同一 `ctx` 连跑 `evaluate_rule_R_SPIKE_REVIEW` **N=10** 次 | `decision_value` 与 `evaluated_conditions` **逐字段一致** |
| **Evidence 可反查** | `decision_id → evidence_id[] → (source.system, source.record_id, input_context_ref) → 原始 context package` | 链路每一跳可查；**不接受只存一段自然语言解释** |
| **Permission 在数据访问路径** | 用 `spike-user-unrelated`（`department=sales`）再跑一次 | PR **不出现在 `ctx.entities`**；**`decision is None`**（规则未被求值）；`ctx.denied` 非空 |

> Permission 测试的判据是"**未授权 Context 不进入 Business Rule**"，**不是**"先全读、UI 再隐藏"。

---

## 11. 端到端 example（本 fixture 的实际期望输出）

```
INPUT
  user_ref = spike-user-procurement
  root     = SPIKE-PR-001

[1] CONTEXT
  package_id = ctx_<24hex>
  counts     = {entities: …, relationships: …}

[2] ENTITY / KNOWLEDGE
  pr.ref        = PR4xx            (由 source_id 运行时解析)
  pr.attrs.amount = 1280000
  quotes        = [SUP-SPIKE-A]    → len = 1
  knowledge     = 1 条 SELECTS 关系 + sources[]

[3] RULE  R-SPIKE-REVIEW
  amount_gte_threshold   : 1280000 >= 1000000  → passed=true
  quote_count_lt_required: 1 < 3               → passed=true

[4] DECISION
  decision_key   = "review_status"
  decision_value = "review_required"
  reason         = "金额 1,280,000 ≥ 1,000,000（100万阈值）且仅 1 家报价（需 3 家）→ 需人工复核"

[5] EVIDENCE
  ev_1  claim="金额 1,280,000 ≥ 1,000,000"  source={spike:v0-technical-fixture, SPIKE-PR-001}
  ev_2  claim="报价家数 1 < 3"               source={spike:v0-technical-fixture, SPIKE-PR-001}

[6] CONTEXT UPDATE
  SPIKE-PR-001.attrs.review_status : "pending" → "review_required"
  + review_decision_id / review_evidence_id / review_updated_at

RE-READ
  assemble_context(...).entities[0].attrs.review_status == "review_required"   ✅
```

---

## 12. 范围锁（不得越界）

**只允许**：1 Domain Pack · 1 固定 WorkflowSpec · 1 固定 Agent · 1 Local Provider · 1 InProcessExecutor · 最小 Permission Enforcement · 最小 Evidence。

**禁止**（如认为"以后可能需要" → 记为 Future，不实现）：
Dynamic Agent/Runtime Selection · Trigger.dev/DSH/Glean Adapter · Multi-Agent · Generic Connector ·
Builder UI · Generic RAG · Workflow Engine · 三类 interface abstraction · SaaS/multi-tenancy ·
大规模 connector · **新的 Kernel object**。

---

## 13. 待审阅的 2 个判断（本轮唯一可能的分歧点）

1. **§7 新增 `evidence_records` 表** —— 我判定它**不是**新增 Kernel 对象（Evidence 是 V3 五项核心之一，这是实现它）。若审阅不同意，请指出。
2. **§8 写 `entities.attributes`** —— 判定式写入企业实体状态。V3 的 `Context Update` 要求"改变业务状态"；`attributes.review_status` 是业务状态而非事实篡改。若审阅认为 Kernel 不应写 `entities`，请给出替代落点（那会是一个 ADR 级问题）。

---

## 14. 实现顺序（审阅通过后）

```
S1  seed_v0_spike_fixture.py（幂等）+ fixture 自检
S2  evidence_records 迁移 + persist_evidence
S3  evaluate_rule_R_SPIKE_REVIEW + build_decision（纯函数，先写确定性测试）
S4  apply_context_update + re-read 断言
S5  run_v0_loop.py 串六步 + 逐步断言输出
S6  三个专项测试（确定性 / 证据反查 / Permission）
```

**S1–S6 全部完成前不进入任何其它工作。**

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: DRAFT — 等审阅。**审阅通过前不写实现代码。**
