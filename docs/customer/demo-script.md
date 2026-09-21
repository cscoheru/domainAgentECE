# Demo Script — Procurement Agent Demo Flow

> **作者**: Claude（Opus 5）
> **日期**: 2026-09-21
> **场景**: 客户访谈 Gate 5 / 前 15 分钟 Demo（接 `interview-guide.md` §0）
> **基础**: V0 Spike S1–S6 PASS 后的真实 spike demo（`docs/v0/S5_REPORT.md` §11 六段输出）+ ECE/CLAUDE.md 铁律（Permission Before Intelligence / 垂直纪律 / 零 LLM 决策）
> **方向**: Procurement Pack（采购合规评估），与 V3 PRD 决策一致
> **依赖**: `make seed` + `scripts/ingest_demo_docs.py` 跑通；本地 PostgreSQL 已启

---

## 0. Demo 前 30 秒声明（必读，避免误解）

> "这个 Demo 是 V0 Spike 阶段的真实运行输出，**没有用 LLM 做决策**——所有判断是确定性 Python 规则。Demo 想让你们看到三件事：(1) AI 能在哪几处帮采购部**省时间** (2) 在哪些地方我们**坚决不替人做决定** (3) 客户自己数据接入后，能不能直接跑起来。"

---

## 1. Demo 场景设定（1 分钟）

### 1.1 角色

| 角色 | 姓名 | 部门 | 在 demo 中的动作 |
|---|---|---|---|
| **采购经理** | 张三 | 采购 | 提交一份采购申请 (PR001)，金额 128 万元 |
| **采购总监** | 用户002 | 采购 | 比价与审批 |
| **CFO** | 用户003 | 财务 | 终审 |

### 1.2 业务问题（PRD §4.3 Case First 原则）

> "张三提交了一份采购申请，金额 128 万元（**超过 100 万阈值**），只拿到了 **1 家供应商**的报价。采购政策 POL-2026-03 要求 100 万以上必须 **三家比价**。张三想知道：要不要直接走？还是先补比价？传统做法：手动对照政策（10-30 分钟）+ 找人签字（半天到 1 天）；Demo 想展示 ECE 把这个时间从「小时级」降到「分钟级」，**且每一步决策的依据都可追溯**。"

### 1.3 系统行为预期（**Demo 之前告诉客户，不要藏**）

ECE 会按 V0 spike 六步走：

1. **Context Assembly** — 把张三（采购部）能看到的 PR 详情 + POL-2026-03 政策 + 报价记录 + 历史比价数据**按权限**装配
2. **Rule Evaluation** — 跑确定性规则 `R_SPIKE_REVIEW`：金额阈值检查 + 报价家数检查 + 审批链完整性检查
3. **Decision** — 给出 `review_required`（必须人工复审）+ 触发原因（**三家比价不足**）
4. **Evidence** — 把决策依据写到 `evidence_records` 表（**反向可查**到原始 Context）
5. **Context Update** — 把 PR 状态从 `pending` 改为 `in_review`，**重读装配路径** 验证 Context 也反映了新状态
6. **Determinism** — 同一上下文重跑 10 次，**字节级一致**（**没有 LLM 噪声**）

---

## 2. Demo 执行（10 分钟，建议录屏）

### 2.1 第一刀：Context Assembly（2 分钟）

**操作**：
```bash
curl -sS -X POST http://localhost:8000/context \
  -H 'X-User-Id: 张三' \
  -H 'Content-Type: application/json' \
  -d @- <<'JSON' | jq .
{
  "intent": "evaluate_purchase_request",
  "requires": {
    "documents": [{"doc_type": "policy", "query": "采购政策"}],
    "entities": [{"entity_type": "purchase_request", "ref": "PR001"}]
  }
}
JSON
```

**给客户讲**：
- 我们看到张三（采购部）**能看到的** Context：1 份采购政策（POL-2026-03）+ 1 条采购申请（PR001：128 万，1 家报价）+ 张三的部门 ACL（采购部）放行的全部数据
- **关键点**：Context 不是"全公司所有数据"——**张三看不到也不应该看到财务部其他 PR**。这就是"Permission Before Intelligence"铁律

### 2.2 第二刀：Rule + Decision（2 分钟）

**操作**：跑 `python scripts/run_v0_loop.py --user 张三 --pr PR001`（按 S5 §11 输出格式）

**给客户讲**：
- 规则名 `R_SPIKE_REVIEW` 是确定性的，**不调 LLM**
- 输出 `decision_value: review_required` + **触发原因**：`quote_count=1 < 3`
- S6 验证：同一 ctx 跑 10 次，**字节级一致**——"不是 AI 一拍脑袋，是规则硬卡"

### 2.3 第三刀：Evidence 反查（2 分钟，重点）

**操作**：
```sql
-- 在 psql 跑，让客户看到
SELECT er.claim, er.threshold, er.actual, er.passed
FROM evidence_records er
WHERE er.decision_id = '<上一步的 decision_id>';
```

**给客户讲**：
- 每条 evidence 都反查到原始 Context：`decision → evidence → input_context_ref → context_requests 行`
- 审计师问"你这决策怎么来的？"——**审计师自己能在数据库里把链路走一遍**
- 这是 PRD §7 Evidence ≠ 工程 trace 的承诺：**审计能用**

### 2.4 第四刀：Context Update + 闭环（2 分钟）

**操作**：跑同一个 `run_v0_loop.py` 第二次，让 PR 状态 `pending → in_review`

**给客户讲**：
- 第六步**真的**改了数据库，不是返回了就忘
- 第二次重读 Context，**PR 的状态字段已经变了**——这是闭环
- V0 spike 验证过："重读走第二次 `assemble_context`（调用计数守住的）"，不是字面 cache 复述

### 2.5 第五刀：Denied 用户（2 分钟，**安全演示**）

**操作**：换成用户004（**无权限**）跑同一个 query

```bash
python scripts/run_v0_loop.py --user 用户004 --pr PR001
```

**给客户讲**：
- **不返回 PR 数据**（Context 里就没这条）
- `decision: None`（规则不跑）
- `evidence_records` 表**没有新行**（denied 分支零副作用）
- "如果 AI 系统被越权访问，**最坏的情况也是 no-op**——这是 CEGR 的安全边界"

### 2.6 第六刀：E2 Permission 自动验证（30 秒）

**操作**：
```bash
python scripts/run_e2_permission.py
# → Total cases: 61, Failures: 0, Exposures: 0
```

**给客户讲**：
- 61 个权限负向用例自动跑过、零泄露
- 这是 PRD §6 "Unauthorized Context Exposure = 0" 的 CI 硬门槛

---

## 3. Demo 后 5 分钟过渡到访谈（接 `interview-guide.md` §1）

过渡话术（**不要引导**）：

> "Demo 是 V0 Spike 的真实输出，**接入你们自己的数据要重跑规则库和种子**。在我们聊之前，我想问几个问题帮我理解你们的真实工作流……"

然后进入 `interview-guide.md` §1 的 15 问。

---

## 4. Demo 备份方案（应对客户环境跑不动）

| 失败场景 | 备份 |
|---|---|
| 本地 PostgreSQL 没起来 | 改用 `S6_REPORT.md` 的截图 + `scripts/run_v0_loop.py` 历史输出（V0 spike 实跑结果） |
| 网络不通 | 离线 Demo：纯文字+截图，不演示命令 |
| demo seed 没注入 | 跑 `make seed`，1 分钟；如果 seed 失败，改用预录屏 |

---

## 5. Demo 边界声明（**重要**，避免过度承诺）

我们**能**演示的：

- 确定性规则 + Context 装配 + Evidence 反查
- Permission 在数据访问层强制（denied 零副作用）
- 中文 FTS 检索 + ACL 过滤
- V0 spike 六步闭环真实可跑

我们**不**演示的（**v0 还没做**，PRD 标注）：

- LLM 自由生成（v0 用确定性规则；Sprint 5 引入 LLM）
- `/actions/execute` 真执行（v0 关闭，仅 preview）
- 多租户 SaaS / 计费 / 完整 RBAC（PRD §12 明确不做）
- 真实 ERP/HR/财务系统 connector（v0 用 CSV/JSON/本地文档）

**对客户的话术**：

> "我们 V0 不做 LLM 决策，是故意。原因是采购合规这件事，**你不能让 AI 替你判断要不要补比价**——规则就是规则，确定性可追溯。等你们接进来，我们可以选：(a) 纯规则（最快上线） (b) 规则 + LLM 解释（更友好） (c) 规则 + LLM 起草（执行前必须人批）。"

---

## 6. Demo 验收口径

| 客户问"你们怎么证明 X" | 答 |
|---|---|
| "证明规则没偏？" | S5_REPORT §11 + S6_REPORT §2.1 byte-equal |
| "证明权限没漏？" | E2 61/61 + V0 spike denied 测试 + S6 T-P 四断言 |
| "证明 audit 能查？" | S6_T-T 反查链路 + `evidence_records` 表结构展示 |
| "证明我们能接进来？" | Context Spec YAML 自描述 + Connector 接口（CSV/JSON/本地） |
| "证明不是 LLM 拍脑袋？" | V0 spike 全程零 LLM + 规则评估日志 |

---

## 7. 已知 V0 Spike 遗留（不藏，对客户诚实）

Codex S6 裁定（`Obsidian Vault/blueprintECE/0921/codex给s6的裁定.md`）记入"已知疣子"4 项：

1. `package_id` 编码用纯 hex 而 PG uuid 标准形带 dash —— 已 `replace()` 桥接，**不影响客户**
2. S5 Z1/Z2 fixture 形状过滤 —— **不影响客户**
3. spec §11 三处示意文案与实现的偏差 —— 文档瑕疵
4. demo 客户化三缺口（**这是真实缺口**，**必须坦白**）：
   - demo 数据集是合成中国采购场景，不是客户真实数据
   - 规则库覆盖 1 个场景（SPIKE-REVIEW），未覆盖客户全套采购政策
   - 没有真实采购 ERP 接入（仅 CSV/JSON/本地文档）

> **POC 推进承诺**（访谈中用）：如果客户愿意提供脱敏真实数据 + 1 份真实采购政策，**我们 2 周内能跑出针对该客户的 demo**——不是 V0 spike 的"张三 POL-2026-03"，而是"你们的采购员 + 你们的政策"。

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
**Status**: 写完；与仓根 `customer-profile.md` / `interview-guide.md` / `validation-metrics.md` 并列；Obsidian 镜像见 `blueprintECE/0921/customer-pack/`
