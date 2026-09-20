# S1_REPORT.md — V0 Technical Spike S1 结果 + 阻塞报告

> Date: 2026-09-20
> 依据: `V0_EXECUTION_SPEC.md`（已审验通过）· Codex 裁定「S1 完成后提交 S1 结果」
> ece commit: `8dbdd6c`
> **结论: S1 交付物本身通过；但 S1 暴露了一个跨 fixture 隔离缺陷 → 按指令 STOP 报告，未自行重构。**

---

## 1. S1 交付物（已独立验证）

`scripts/seed_v0_spike_fixture.py`

```
TECHNICAL SPIKE FIXTURE
NOT CUSTOMER-VALIDATED
NOT PRODUCT REFERENCE WORKFLOW
```

| 要求（Codex 指令） | 状态 |
|---|---|
| `source_system = spike` | ✅ 实现为 `spike:v0-technical-fixture`（沿用仓库 `system:ref` 惯例；如需字面 `spike` 可一行改名） |
| 幂等 | ✅ 连跑两次：第二次删除 7 实体 + 1 关系 + 1 ACL 后重建 |
| DELETE-then-INSERT 仅作用于自身 source_system | ✅ 四处删除均 `WHERE source_system = :s`，无 `LIKE` 范围扫描 |
| 全部按 source_id 寻址 | ✅ |
| 不硬编码 display_id | ✅ `grep -E "PR4[0-9]{2}\|SUP4[0-9]{2}"` 无命中 |
| seed 后 self-check | ✅ 失败即 exit 1，不静默通过 |
| 三个供应商只建 1 条 SELECTS | ✅ |
| PR 初始 `review_status = pending` | ✅ |

### 1.1 独立 DB 侧复核（不依赖 self-check）

```
entity_type      | source_id               | display_id | review_status | amount  | dept
person           | spike-user-procurement  | U009       |               |         | procurement
person           | spike-user-unrelated    | U010       |               |         | sales
policy           | SPIKE-POL-001           | POL021     |               |         |
purchase_request | SPIKE-PR-001            | PR402      | pending       | 1280000 |
supplier         | SPIKE-SUP-A/B/C         | SUP1184-86 |               |         |
→ 7/7 存在

relationships:  SELECTS  SPIKE-PR-001 -> SPIKE-SUP-A   count = 1   ✅
acl_entries:    deny     spike-user-unrelated  on  entity/PR402  ✅
```

### 1.2 漂移韧性

wipe+replay 测试跑完后 fixture **存活 7/7**，且 ACL 的 `object_ref` 与当前 PR `display_id` **一致**。

---

## 2. 【阻塞】S1 暴露的两个跨 fixture 隔离缺陷

**同族缺陷第 8/9 例**（前 7 例：`attributes.department` 被洗 / R4 重名累积 / `seed_departments` 被删 / 关系 fixture 被毁 / 数据集因漂移过期 / display_id 漂移本身）。

### 缺陷 ① `seed_relationships.py` 按 entity_type 取全部实体

```python
# scripts/seed_relationships.py:35-45
def _fetch_display_ids(engine, entity_type: str) -> list[str]:
    SELECT display_id FROM entities WHERE entity_type = :t ORDER BY display_id
    #                                          ↑ 无 source_system 范围
```

→ demo 关系 fixture **吞并了 spike PR**：

```
relationships from SPIKE-PR-001:
  demo:seed_relationships   6
  spike:v0-technical-fixture 1     → 合计 7
```

→ FER guard **G2**（每 PR 恰 6 条）失败。

### 缺陷 ② `_next_display_id` 是**全局** max+1

```python
# src/ece/entities/pipeline.py:49  _next_display_id(engine, entity_type)
#   → 遍历该 entity_type 的**全部** display_id，取数值 max，+1
# src/ece/entities/pipeline.py:105  display_id = _next_display_id(engine, entity_type)
#   → upsert_entity() **不接受** 显式 display_id
```

**因果链**：

```
spike PR 拿到 PR402（幸存于 wipe，因它属于不同 source_system）
   ↓
下一次 demo wipe+replay：幸存者 max = PR402
   ↓
replay 分配 PR403..PR602（200 个 demo PR）
   ↓
E3/E4/E5 数据集引用的 PR201..PR230 **全部失效**（仅 PR201 幸存，属 r4test）
```

**实测 PR 号空间**：

```
source_system               count   min_d    max_d
demo:demo                   200     PR403    PR602      ← 原本 PR201..PR400
r4test                        1     PR201    PR201
spike:v0-technical-fixture    1     PR402    PR402
```

---

## 3. 影响范围

| 项 | 变化 |
|---|---|
| 全套 pytest | **359P / 3S / 0F → 356P / 3S / 3F** |
| 失败项 | `G1` ×2（E3 / E4+E5 数据集 display_id 全部失效）、`G2` ×1（PR402 有 7 条关系） |
| **冻结 eval 资产** | **E3 / E4 / E5 数据集失效** |
| PR 号空间 | PR201..PR601 **且每次 replay 继续增长**（K4 单调漂移） |

**为什么这阻塞 S2**：不能在「评测资产失效 + pytest 红」的状态上继续叠实现 —— 那正是前面几刀反复吃的「在被污染的地基上测出漂亮数字」。

---

## 4. 建议的最小修法（**未自行实施**，待裁定）

### 选项 A —— 修缺陷 ①（非架构，同族修法）

`seed_relationships.py` 改为按**显式 allowlist** 限定自身 fixture 的实体：

```
purchase_request / supplier / product / policy  →  source_system = 'demo:demo'
department                                       →  'demo:seed_departments'
person                                           →  'api:header'
```

- ✅ 表达意图（"这个 fixture 只在自己那批实体上建关系"）
- ✅ 与 wipe 谓词修复同一模式（精确谓词，非黑名单）
- ❌ **单独做不足以恢复绿**（缺陷 ② 仍使数据集失效）

### 选项 B —— 修缺陷 ②（K4 根因；**触及 Kernel 模块，需批准**）

`upsert_entity()` 增加**可选** `display_id: str | None = None` 参数（纯新增，既有调用行为不变）；
spike fixture 传 `display_id="SPIKE-PR-001"`。

- ✅ spike PR **不占用 `PR###` 号段** → demo replay 保持在自己号段 → 数据集不再失效
- ✅ 这是 K4（display_id 漂移）的**根因修法**，且对未来任何外来 fixture 都成立
- ⚠️ 触及 `src/ece/entities/pipeline.py`（Kernel 模块）—— 按指令需你批准

### 选项 C —— 兜底：重生成 E3/E4/E5 数据集

- ✅ 立即恢复绿
- ❌ **掩盖机制**：漂移随每次 replay 复发；且违背 FER 立的 "G1 必须响亮失败" 原则
- ❌ 不解决 K4

**我的建议**：**A + B**。A 是必须的（否则 demo fixture 会持续吞并外来实体）；B 是根因修法且改动最小。C 不可单独采用。

---

## 5. S2 是否启动

**否。** 按指令「如果任何阶段出现真实失败：停止该阶段，报告 failure / root cause / affected scope / proposed minimal fix」，
**S2 在阻塞解除前不启动**。

已做：提交 S1 产物（`8dbdd6c`）。**未做**：未改 `pipeline.py`、未改 `seed_relationships.py`、未重生成数据集、未跳步。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
