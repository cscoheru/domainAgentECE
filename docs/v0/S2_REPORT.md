# S2_REPORT.md — V0 Technical Spike S2 结果

> Date: 2026-09-21
> 上游: `docs/v0/V0_EXECUTION_SPEC.md` §7（Evidence 最小 schema）+ §14（S2 行）·
> Codex 对该 spec 的审验裁定（批准 S1–S6 顺序执行，并单独授权 S2 实现 `evidence_records` + `persist_evidence`）
> 范围: `evidence_records` 迁移 + `persist_evidence()` + 最小 persistence test

---

## 0. 结论

**S2 完成。未出现失败，未扩大范围，未触碰禁区。**

按 Codex 指定的节奏（"每完成一个 S 就回来验一次"），**S2 到此 STOP，等审阅后再进入 S3**。

有一处**规格内部缝隙**必须上报（§3），我已按最小侵入方式解决，但它是一个需要你确认的判断。

---

## 1. S2 交付物

| 文件 | 行数 | 内容 |
|---|---|---|
| `src/ece/migrations/versions/0008_evidence_records.py` | 62 | `evidence_records` 表（纯 SQL，与既有迁移风格一致） |
| `src/ece/evidence/store.py` | 180 | `persist_evidence()` + `get_evidence_for_decision()` |
| `src/ece/evidence/__init__.py` | 10 | 模块出口 |
| `tests/integration/test_v0_evidence_persistence.py` | 256 | 4 个正向测试 + **3 个负向对照** |

**改动面 = 恰好 3 个新路径**，无任何既有文件被修改（`git status` 仅 3 条 `??`）。

### 1.1 表结构（实测 `information_schema`）

```
evidence_records 列数 = 12
   evidence_id        text                     ← ev_<uuid>
   decision_id        text NOT NULL            ← dec_<uuid>
   rule_id            text NOT NULL
   claim              text NOT NULL
   source_system      text NOT NULL            ← §7 的 source.system
   source_record_id   text NOT NULL            ← §7 的 source.record_id
   observed_value     numeric
   threshold_value    numeric
   actor_user_ref     text NOT NULL
   input_context_ref  text NOT NULL            ← ctx 的 package_id
   evidence_timestamp timestamptz NOT NULL
   created_at         timestamptz NOT NULL DEFAULT now()
索引: ['evidence_records_pkey', 'idx_evidence_decision']
```

**两处列名与 §7 的 JSON key 不同，都在迁移 docstring 里写明了理由**：

- `source` 拆成 `source_system` / `source_record_id` —— 因为 §10.1 的反查要按它过滤；
- `threshold` / `timestamp` → `threshold_value` / `evidence_timestamp` ——
  这两个在 PostgreSQL 里都是**类型名**，作为列名会引入歧义。

---

## 2. 独立验证（不用函数自己的返回值当证据）

这是本报告最重要的一节。`persist_evidence` 返回它写入了什么 —— 那是**自述**，不是证据。
所以测试里所有"行存在"的断言都走**一条不经过 `ece.evidence` 的独立 SELECT**
（`_rows_in_db()`，直接 `text()` 查表）。

| 验证项 | 做法 | 结果 |
|---|---|---|
| 每条 **passed** 条件产出一条 Evidence | 3 条条件（2 passed / 1 failed）→ 查表 | **2 行**，且 claim 集合恰为两条通过项 ✅ |
| 返回值与库内一致 | `len(returned) == len(rows_in_db)` | 一致 ✅ |
| 反查链 `decision → evidence → source → context` | 逐跳断言 `decision_id` / `source_system` / `source_record_id` / `input_context_ref` | 四跳全部可查，`input_context_ref == ctx.package_id` ✅ |
| Evidence 按 decision 隔离 | 两个 decision 各写一次，互相不可见 | 1 / 2 行，互不串台 ✅ |
| 无 passed 条件 | 只传 failed 条件 | 返回 `[]`，**库内 0 行**，且不报错 ✅ |
| `evidence_id` 形状 | 逐行断言前缀 | `ev_` ✅ |
| 测试自清理 | 跑完后 `count(*)` | **0 行** ✅ |

### 2.1 三个负向对照（guard 必须真的会咬）

`store.py` 里每个 `raise` 都有一个测试让它**实际触发** —— 没被触发过的 guard
与本项目此前那些"看起来在检查"的断言同型。

| 负向对照 | 断言 |
|---|---|
| passed 条件缺 `claim` | `pytest.raises(ValueError)` 且**库内不留半成品行** |
| Context 里有 2 个 `purchase_request` | `pytest.raises(ValueError, match="exactly one")` |
| 实体缺 `src` provenance | `pytest.raises(ValueError, match="provenance")` |

**7 passed**（4 正向 + 3 负向）。这 3 个 `raises` 通过，即证明那三处 guard 确实会拒绝写入。

---

## 3. ⚠️ 规格的一处内部缝隙（需你确认）

**这是本轮唯一需要判断的地方。**

`V0_EXECUTION_SPEC.md` §6 给出的 `evaluated_conditions` 元素形状只有四个键：

```jsonc
{"name": "amount_gte_threshold", "expr": "amount >= 1000000",
 "actual": 1280000, "passed": true}
```

而 §7 要求每条 Evidence 带 **`claim`** 与 **`threshold`**：
`claim = "报价家数 1 < 3"`、`threshold = 3`。

**两者无法同时满足** —— `claim` 不能从 `expr` 推出来：
`"quote_count < 3"` 推不出 `"报价家数 1 < 3"`（后者含中文业务措辞与实际值）。
而 §9 把 `persist_evidence(engine, ctx, dec)` 的输入限定为 `dec`，
所以这些信息**必须**随 `dec` 一起到达。

### 我的解决方式（最小侵入）

让规则在每条条件上**额外**给出 `claim` 与 `threshold`（即 6 键，是 §6 那 4 键的超集）：

```jsonc
{"name": "quote_count_lt_required", "expr": "quote_count < 3",
 "actual": 1, "threshold": 3, "passed": true, "claim": "报价家数 1 < 3"}
```

`persist_evidence` 把 `claim` 视为 **passed 条件的必需键**，缺失就报错（§2.1 的负向对照）。

**如果你不同意**，另外两条路都更差，列出来供判断：

| 替代 | 代价 |
|---|---|
| 改 §6，把 claim/threshold 写进规格 | 改规格；但 §6 是已审验文档，且这属于补漏不是改语义 |
| 在 `persist_evidence` 里放一张 rule→claim 的映射表 | **更差**：把业务措辞硬编码到持久化层，规则与证据隐式耦合 |

**我的判断是"条件带 6 键"**：它不新增 Kernel 对象、不改 §6 已列的四个字段、
把业务措辞留在规则层（它本来就该在那里）。（规格 §13 原本那 2 个待审判断，
Codex 在 V0 spec 裁定里已分别回答：新增表 = 实现既有对象；`entities.attributes` 写入被 S4 明确要求。）

---

## 4. 范围锁自查（Codex 明令"不要扩展成 Evidence Framework"）

| 禁止项 | 自查结果 |
|---|---|
| ranking / search / graph / versioning / UI | 全库 `grep -niE "rank\|search\|graph\|version\|ui\|embedding\|vector"` 只命中 **docstring 里声明"没有这些"的那两行** ✅ |
| 新增 Kernel 对象 | 无。Evidence 是 V3 五项核心之一（`V3_CLOSEOUT.md` §1.2），本表是**实现既有对象** ✅ |
| 复用 `context_items` 充当 Evidence | **刻意没有**。该表是工程审计（`item_kind`/`score`），而 `KERNEL_BOUNDARY.md` §5 要求 **Business Evidence ≠ 工程 trace** ✅ |
| 触碰禁区目录 | `domain_packs/` `context/` `permissions/` `entities/` `identity/` `api/` `audit/` `data/` —— **全部零改动** ✅ |

**证据分层**：`store.py` 只做 **最小 persistence + 那一条反查**。
没有为"以后可能需要"预留任何东西。

---

## 5. 回归与静态检查

| 项 | 结果 |
|---|---|
| **全量 pytest** | **370 passed, 3 skipped, 0 failed**（S2 前 363 → +7 新测试） |
| `ruff` | `All checks passed!`（5 处自动修复：`collections.abc.Mapping`、`datetime.UTC` 等） |
| `mypy` | `Success: no issues found in 2 source files` |
| `lint-imports` | **Contracts: 2 kept, 0 broken**（新增 `ece.evidence` 未破坏领域包/引擎隔离） |

---

## 6. 迁移可逆性（实测，不是"应该可以"）

| 步骤 | 实测 |
|---|---|
| 回滚前 | `evidence_records 存在=True 行数=0` |
| `alembic downgrade 0007_user_orgs` | `存在=False` ✅ |
| `alembic upgrade head` | `存在=True 行数=0` ✅ |
| `alembic current` | `0008_evidence_records (head)` ✅ |

未测试的回滚与未验证的断言同型，所以回滚路径也实测了一遍。

---

## 7. S3 的前置

S3 是 `evaluate_rule_R_SPIKE_REVIEW` + `build_decision`（**先写确定性测试**）。按 Codex 指令：

- 规则：纯 Python · 不调用 LLM · 不写数据库 · 复用现有 `PRICE_COMPARISON_THRESHOLD`（`1_000_000`）·
  不改变既有 procurement rules；
- Decision 必须保留 `rule_id` / `evaluated_conditions` / `actual` / `passed` / `reason` /
  `input_context_ref` / `request_id`；
- **不为了 `request_id` 新增 abstraction** —— 使用现有 context request contract。

S2 已就位的是：`persist_evidence(engine, ctx, dec)` 的输入契约（§3 的 6 键条件形状）、
`input_context_ref` 的来源（`ctx.package_id`）、`request_id` 的来源（`ctx.request_id`）。

---

## 8. 本阶段**未做**的事

- 未实现 `evaluate_rule_R_SPIKE_REVIEW` / `build_decision`（那是 S3）
- 未实现 `apply_context_update`（S4）
- 未实现 `run_v0_loop`（S5）
- 未跑三个专项测试（S6）
- 未引入 LLM（Codex 明令本次 spike 不得引入 LLM 决策）
- 未改 V3 / V0 spec / PRD / Business Rules / Evaluation 标准
- 未新增 Adapter / Interface abstraction / Runtime

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-21
**Status**: S2 完成，等审阅。**审阅通过前不进入 S3。**
