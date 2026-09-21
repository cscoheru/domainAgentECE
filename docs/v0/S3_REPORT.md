# S3_REPORT.md — V0 Technical Spike S3 结果

> Date: 2026-09-21
> 上游: `docs/v0/V0_EXECUTION_SPEC.md` §5 / §6 / §9 step [3]+[4] ·
> Codex 对 V0 spec 的审验裁定（批准 S1–S6）·
> 审验者（Gemini）给出的 binding acceptance criteria（8 条，本报告逐条对应）
> 范围: `evaluate_rule_R_SPIKE_REVIEW` + `build_decision`

---

## 0. 结论

**S3 完成。所有 8 条 binding acceptance criteria 实测通过。** 等审验后进入 S4。

按 Codex 指定的"每完成一个 S 就回来验一次"节奏，**到此 STOP，等审阅**。

---

## 1. S3 交付物

| 文件 | 行数 | 内容 |
|---|---|---|
| `tests/unit/test_v0_rule_and_decision.py` | 219 | **测试先写**，含 8 个测试 + 15 格参数化矩阵 |
| `src/ece/domain_packs/procurement/agent/v0_rules.py` | 138 | `evaluate_rule_R_SPIKE_REVIEW` + `build_decision` |

**改动面 = 恰好 2 个新路径**。既有文件零改动（`rules.py`、`agent.py`、`agent/rules.py` 都未触碰）。

### 1.1 函数签名（spec §9 step [3]/[4]，严格）

```python
evaluate_rule_R_SPIKE_REVIEW(amount: int, quote_count: int) -> list[dict[str, Any]]
build_decision(conditions: list[dict[str, Any]], ctx: ContextPackage) -> dict[str, Any]
```

### 1.2 常量

| 名称 | 值 | 来源 |
|---|---|---|
| `REQUIRED_QUOTES` | `3` | 新增本地常量（`rules.py` 没有）；spec §5 |
| `RULE_ID` | `"R-SPIKE-REVIEW"` | spec §5/§9 |
| `DECISION_KEY` | `"review_status"` | spec §6 |
| `DECISION_ID_PREFIX` | `"dec_"` | spec §6（与 Evidence 的 `ev_` 对称） |
| `PRICE_COMPARISON_THRESHOLD` | `1_000_000` | **从 `rules.py` 复用**，未另写 `1_000_000` 字面量参与比较 |

---

## 2. 红 → 绿 → Mutation 证据（criterion 1）

### 2.1 红（实现前）

```
ERROR tests/unit/test_v0_rule_and_decision.py
ModuleNotFoundError: No module named 'ece.domain_packs.procurement.agent.v0_rules'
1 error in 0.30s
```

### 2.2 绿（实现后）

```
23 passed in 0.18s
```

### 2.3 Mutation 测试 —— 4 个变异，全部实测咬

| # | 变异 | 期望 | 实测 |
|---|---|---|---|
| **M1** | `decision_value` 永为 `"auto_approved"` | 至少边界矩阵的 5 个 RR 单元格失败 | ✅ 7 失败（含 schema + 边界矩阵） |
| **M2** | 删去第二条 condition，只发 `amount_gte_threshold` | "两条条件恒在"失败 + 全部边界矩阵失败 | ✅ **21 失败**（both_conditions + 全部矩阵项） |
| **M3** | `input_context_ref = ""`（写死，不读 ctx） | schema 测试咬 | ✅ `test_decision_schema_keys` 失败 |
| **M4** | 在 `reason` 中注入 `time.time()` | reason 的时间正则 + 字节相等双断言都咬 | ✅ `test_reason_is_deterministic_and_free_of_timestamps` 失败 |

**全部还原后 23 / 23 通过**。

---

## 3. 8 条 binding acceptance criteria 逐条对账

| # | 判据 | 自测方式 | 状态 |
|---|---|---|---|
| **1** | 测试先写；红→绿证据；变异测试证明覆盖有效 | §2 三步全部实测 | ✅ |
| **2** | 边界矩阵 5×3=15 格全覆盖；阈值引用常量 `PRICE_COMPARISON_THRESHOLD` | `test_boundary_matrix_decision_value` 参数化 15 例 + 显式断言 `by_name[...]["threshold"] == PRICE_COMPARISON_THRESHOLD` | ✅ |
| **3** | N=10 确定性，**不含 `decision_id`**（含 `reason`） | `test_n_10_determinism_excluding_decision_id` + `test_reason_is_deterministic_and_free_of_timestamps`（含时间正则） | ✅ |
| **4** | 两条条件恒在；每条 6 键 | `test_both_conditions_always_present` + 边界矩阵内的 `len==2` 与 `set(keys)==EXPECTED_CON_KEYS` | ✅ |
| **5** | 纯函数硬边界（无 sqlalchemy / Engine / LLM；不写库；不新增 abstraction） | `test_module_purity_no_sqlalchemy_no_engine`（源文 substr 检查）+ `test_does_not_call_llm`（同）+ 源文 `grep sqlalchemy` = 0 | ✅ |
| **6** | Decision schema 全 8 键 + `decision_key="review_status"` + `rule_id="R-SPIKE-REVIEW"` + `decision_id` 以 `dec_` 起头 | `test_decision_schema_keys` 显式断言全部 8 键 + 值 | ✅ |
| **7** | 既有 procurement rules 零行为改动；既有文件只允许 additive；不引入 LLM / 新 Kernel / Adapter / Runtime | `make test` = **394 passed**（既有测试原样通过）；改动面 = 2 个新路径；§5 两条 guard 测试 + 源文 substr 检查 | ✅ |
| **8** | S2 条件测试（subject 类型过滤负向对照）已落地 | 已在 `4254418`（S2 审验闭合时）独立 commit | ✅ |

---

## 4. 范围锁自查（criterion 7 落地）

| 禁止项 | 自查 |
|---|---|
| 改动既有 procurement rules 文件 | `git show --stat` —— `rules.py` **未在变更集中** |
| 新增 Kernel object | 无。`v0_rules.py` 是规则层（Domain IP），与 `rules.py` 同层 additive |
| Adapter / Interface abstraction | 无。`build_decision(conditions, ctx)` 严格按 spec §9，**直接**从 `ctx.request_id` / `ctx.package_id` 取值 |
| 引入 LLM | 源文 `grep -i "openai\|anthropic\|provider\|llm"` = **0**（测试夹具显式保证） |
| 走既有 `agent.py` 的 LLM 路径 | Decision **不经** `agent.py`；S5 才在 orchestrator 里把它们拼起来 |

---

## 5. 静态检查

| 项 | 结果 |
|---|---|
| **ruff** | `All checks passed!`（N802 在 `evaluate_rule_R_SPIKE_REVIEW` 定义处明示 spec 来源；其余自动 + 手工清过） |
| **mypy** | `Success: no issues found in 1 source file` |
| **lint-imports** | （v0_rules 在 domain pack 侧，不新增 engine 模块；架构契约未触发——上一次变更已 keep，本轮也无新增 cross-layer import） |

---

## 6. 全量回归（criterion 7）

```
make test  →  394 passed, 3 skipped, 3 deselected, 0 failed
```

基线（S2 闭合作业 `4254418`）= 371 passed → S3 增加 23 个测试 = 394 passed。**零失败、零退化**。

---

## 7. S4 的前置

S4 = `apply_context_update`，spec §8：
- 修改 `entities.attributes`：从 `pending` → `review_required`，并写入 `review_decision_id` / `review_evidence_id` / `review_updated_at`
- 验证方式（**S3 已经在 `evaluate_rule_R_SPIKE_REVIEW` 的决策里产出了 `decision_value="review_required"`**，S4 拿走它去更新同一行的 attributes）
- ⚠️ **判据是"重新 assemble 能读到变化"** —— 禁止"把 Decision 塞进 Context 冒充更新"

S3 已就位给 S4 的契约：`decision_value="review_required"` 与 `decision_id` / `evidence_id` 对接关系（均以持久化为 S2/S3 的责任）。

---

## 8. 本阶段**未做**的事

- 未实现 `apply_context_update`（S4）
- 未实现 `run_v0_loop`（S5）
- 未跑三个专项测试（S6；其中证据反查的第四跳按裁定留 S6）
- 未引入 LLM（criterion 5 + 7 双重守住）
- 未改既有 `rules.py` 或既有 files
- 未在 `decision_id` 上加任何确定性（必须 `dec_<uuid>`，每次新生成）

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-21
**Status**: S3 完成，等审验。**审验通过前不进入 S4。**

---

## 9. 审验后追加（2026-09-21）

**裁定**: **PASS**（来源: `Obsidian Vault/0921/codex给s3的裁定.md`）—— GO S4。

审验者额外跑了 **5 个不与本报告重叠的独立变异**，全咬：
- A. `>=` → `>`（off-by-one）：边界格 `[1000000-1]`、`[1000000-2]` 红
- B. `<` → `<=`：quote 边界 `[1000000-3]`、`[1000001-3]` 红
- C. 决策 `AND` → `OR`：红
- D. `claim` 键改名：6 键断言咬
- E. `request_id` 写死 `""`：schema 测试咬

**5 个独立变异 + 本报告的 4 个 = 9 个变异全部咬合**（最大覆盖面：AND/OR、边界 off-by-one、键名去重、`request_id` 与 `input_context_ref` 隔离、6 键完整性、Decision 字典化前 vs 后）。还原后 **23/23 绿**。

**两个非阻塞观察（已记录，不在本轮行动）**：
- criterion 2 的"引用常量"无变异可咬（同值字面量会通过），但**防漂移机制由边界矩阵自身承担**——若 `PRICE_COMPARISON_THRESHOLD` 漂移，过时字面量立刻被矩阵测试抓住。
- `build_decision` 按 `name` 索引条件 —— 传入非本规则输出的条件列表会 `KeyError`；S5 接线时真实规则输出无此风险，属 spike 可接受。

**全量 `make test`**: 394 passed, 3 skipped, 3 deselected, 0 failed。
**commit**: ece `abf08af` / root `08e6c58`。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-21
**Status**: **S3 + 审验 PASS。可以进入 S4（`apply_context_update`，写回 `entities.attributes` 并以重读为判据）。**