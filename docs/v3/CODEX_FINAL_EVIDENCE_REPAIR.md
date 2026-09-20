# CODEX_FINAL_EVIDENCE_REPAIR.md — Final Evidence Repair 报告

> Date: 2026-09-20
> 依据: Codex 最终判定（`blueprintECE/0920/codex最终判定no-go不是架构 NO-GO.md`）
> 判定: **NO-GO,但非架构 NO-GO** —— 架构 PASS/FREEZE;唯一阻塞是 E3/E4/E5 评测有效性
> 性质: **Final Evidence Repair**。只修评测资产 / 测试污染 / 时态语义。**未碰 V3 架构。**
> ece commit: `db24826`

---

## 1. 三个套件的真实根因（实测确认,非推断）

| 套件 | 原结果 | 真实根因 |
|---|---|---|
| **E3** | 15.0% | **数据集过期**。`_next_display_id` 按 `max+1` 分配,wipe+replay 推移 display_id;`e3_context.json` 仍引用 `PR001…` |
| **E4** | 100% | **vacuous**。边界 `[0,100]`,对象缺失(0 关系)也在带内。生成器原 `note` 明写 *"no relationships seeded; expect empty"* —— **它本来就是占位符** |
| **E5** | 0.0% | ① 数据集过期 ② **关系 fixture 被 wipe 摧毁且无人恢复** ③ `expected_count=5` **从未匹配实现(6)** |

---

## 2. 两项关键发现

### 2.1 E5 的 `expected_count` 一直是错的（三处陈旧副本）

`scripts/seed_relationships.py` 的 `rel_specs` **有六项**:

```python
("BELONGS_TO",   dept_ids[i % len(dept_ids)]),
("SUBMITTED_BY", people_ids[i % len(people_ids)]),
("SELECTS",      supplier_ids[i % len(supplier_ids)]),
("CONTAINS",     product_ids[i % len(product_ids)]),
("SUBMITTED_BY", people_ids[(i + 1) % len(people_ids)]),  # 2nd submitter for variety
("SUBJECT_TO",   policy_ids[i % len(policy_ids)]),
```

但代码注释写 "create **5** relationships"、生成器 docstring 写 5、数据集 `expected_count` 写 5。
**实现是 6,三处文档是陈旧副本。** E5 runner 从写出来那天就崩(0.0%),所以这个错配**从未被发现**。

> ⚠️ **请复核此判断**:我把 `expected_count` 由 5 改为 **6**。依据是实现的六项列表 + 第 6 项
> 的 `# 2nd submitter for variety` 注释(即**故意**建的),以及生成器 docstring 自己承认的
> "5 relationships (BELONGS_TO + SUBMITTED_BY + SELECTS + CONTAINS + SUBJECT_TO)"——**该枚举
> 本身就漏了第 6 项**。所以错的是文档/数据集,**不是实现**。若判定相反,请指正。

### 2.2 时态语义**没有问题**（未改任何实现）

- **契约有文档**:`docs/DATA_MODEL.md:67-68` — `valid_from date, -- NULL = -∞；区间 [from, to)` / `valid_to date, -- NULL = +∞`;第 78-79 行给出谓词。
- **实现逐字一致**:`src/ece/context/relationships.py:49-50`
  ```
  AND (r.valid_from IS NULL OR r.valid_from <= :as_of)
  AND (r.valid_to   IS NULL OR r.valid_to   >  :as_of)
  ```
- **结论**:`valid_from = valid_to = NULL` = `[-∞, +∞)` = **永久有效**,在每个 `as_of` 都命中。
  E5 的"0 条"**从来不是时态 bug** —— 是空的图。

> 我先前把这个误判为"时态语义异常",已更正。**未修改任何时态实现,也未修改任何 expected 以迎合它。**

---

## 3. 修复清单（8 项）

| # | 修复 | 文件 |
|---|---|---|
| 1 | 关系 fixture **canonical 化**:DELETE-then-INSERT 限于自身 `source_system` —— 反复运行不再累积 | `scripts/seed_relationships.py` |
| 2 | 陈旧注释 "create 5" → 6,并说明第 6 项是刻意的 | 同上 |
| 3 | E5 `expected_rels_per_pr` 5 → **6**;E4 边界 `[0,100]` → `[6,6]` | `scripts/gen_eval_datasets.py` |
| 4 | 数据集重生成,固化为**正式 repository artifact** | `data/eval/*.json` |
| 5 | ACL 对象由 DB **派生**(与生成器同算法:`supplier_ids[1]` / `pr_ids[2]` / `contract_ids[1]`)—— 硬编码 `"PR003"` 在 display_id 位移后即失效,两侧同算则永不漂移 | `src/ece/seed.py` |
| 6 | `test_seed_relationships_test` 加 `finally` cleanup（污染源之一） | `tests/integration/test_seed_relationships.py` |
| 7 | 两个 wipe 测试**恢复它们毁掉的 fixture**（另一污染源:之前只有 `test_s4_5_temporal` 局部绕过） | `test_s14_*` / `test_cut040r2_state_integrity.py` |
| 8 | **4 类 guard / 6 个测试** | `tests/integration/test_eval_asset_integrity.py` |

**未修改**:Kernel 架构 / Permission Engine / 关系 API 契约 / 时态实现 / 任何 expected 以迎合代码。

---

## 4. Guards（Codex 要求的三类 + 一类）

| ID | Guard | 防的是什么 |
|---|---|---|
| **G1** | 数据集引用的 `display_id` 必须存在（`expect=ok` 用例;`insufficient_context` 负例豁免） | **stale reference** —— 失败时列出缺失 id 与受影响 case |
| **G2** | 关系 fixture 必须 canonical（每 PR 恰 6 条）+ **不得有 `test:*` 来源** | **测试污染** |
| **G3** | `valid_from = valid_to = NULL` 必须在**每个** `as_of`（1990 / 2024 / 2026 / 2099）都命中同样条数 | **时态契约回归** |
| **G4** | 数据集 expected 必须与 fixture 一致;E4 下界必须 `> 0` | **dataset↔fixture 错配 + vacuous** |

---

## 5. 结果

| 套件 | 修复前 | **修复后** |
|---|---|---|
| E1 | 98.5% | **98.5%** |
| E2 | 61/61（0/0） | **61/61（0 暴露 0 失败）** |
| **E3** | 15.0%（exit 1） | **100.0%（exit 0）** |
| **E4** | 100%（vacuous） | **100.0%（exit 0,非 vacuous:下界 6）** |
| **E5** | 0.0%（exit 1） | **100.0%（exit 0）** |
| 全套 pytest | 353P / 3S / 0F | **359P / 3S / 0F（+6 guards）,exit 0** |
| P1 | F0 == F1 == F2 | **F0 == F1 == F2（无回归）** |

**所有数字来自仓库中的正式 artifact + 正式 evaluator。** 本轮 `/tmp` 只用于**诊断**
（证明 E3 的 15% 是数据集过期），**未**用临时生成的结果作为 PASS 证据。

原始 stdout: `ece/reports/eval-archive/2026-09-20-cut040R2/FER/`

---

## 6. Remaining Issues

| # | 问题 | 影响 | 处置 |
|---|---|---|---|
| **K1** | `/permissions/check` 的 `req.user_ref` 允许调用者指定授权主体 | Production 阻塞 | 登记 `TASKS.md` 附录 J / PG-1 |
| **K3** | ACL 模型无 `classification` 维度 | 若产品需要则须改模型 | 已在 `engine.py` 标注 |
| **K4** | `display_id` 在 wipe+replay 后**可**漂移（本次观察未漂移,但机制仍在） | 以 display_id 为键的资产可能过期 | **已由 G1 变成"响亮失败"**;根治需改 display_id 生成机制,Codex 要求先证明"最小必要" —— **未做,待裁定** |

---

## 7. 架构状态（未变）

```
V3 架构          FREEZE（无变更）
Glean Research   STOP
Kernel Boundary  PASS
E2 Permission    PASS
P1 单变量证据     PASS
E1 Hermeticity   PASS
E3 / E4 / E5     修复后达门槛,且有 guard 守护
V4               未启动
```

**STOP** —— 等待最终独立审验（GO / NO-GO）。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
