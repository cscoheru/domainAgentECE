# CODEX_ROUND2_FINDINGS.md — 第二轮判词落实记录

> Date: 2026-09-20
> 判词原文: `/Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0920/Codex 第二轮正式判词.md`
> 送审对象: 8.A 收口(`e159f88`) + 8.B 矩阵修复(`17c08cc`) + 8.C A/C 执行(ece `037260b`)
> 性质: **落实记录 + 第三轮送审范围**。*不是*架构迭代 —— `V3_CLOSEOUT.md` §5.1 已冻结架构。

---

## 1. 判词总表(Codex 原文 → 落实状态)

| 项 | Codex 判定 | 落实 |
|---|---|---|
| 8.A 收口 | **PASS** | — |
| 8.B 26 行矩阵 | **PASS** | — |
| Kernel 没重新变成 Agent Platform | **PASS** | — |
| V0 规模 | **PASS** | — |
| Permission E2 0/0 | **PASS，但不是纯代码变量实验** | → **P1 已补做** |
| RC-7 数据集修正 | **PASS**（不是改考题） | — |
| RC-8 is_management | **PASS** | — |
| RC-11 未知身份 | **PASS，未发现该侧信道** | — |
| E1 掉分归因 | **高可信 PASS** | — |
| **E1 hermeticity** | **FAIL / backlog** | → **P2 已修** |
| Customer Validation | **PASS WITH ONE CORRECTION** | → **P3 已改** |
| 整体是否文档循环 | **PASS，已进入执行阶段** | — |

**GO / NO-GO**:V3 架构 **GO（可封版）** · V3 PRD **STOP** · Glean Research **STOP** ·
Kernel Architecture **FREEZE** · Customer Validation **GO** · V0 **GO（可开始 Technical Spike）**

---

## 2. P1 — 严格单变量实验（已完成）

**Codex 要求**：「用**同一份新 E2 dataset**：baseline code vs `037260b`。不要再同时改变 dataset。」

**执行**：固定新 `e2_permission.json`，只变源码。

| 组 | 源码 | 结果 | 退出码 |
|---|---|---|---|
| 对照 | `037260b~1`（宿主 uvicorn :8766） | **4 暴露 + 4 失败**（13.1%） | 2 |
| 处理 | `037260b`（docker :8765） | **0 暴露 + 0 失败** | 0 |

原始 stdout: `ece/reports/eval-archive/2026-09-20-cut040R2/single-variable/`

**顺带产出 —— 该实验把「代码修复」与「数据修复」分离了**（这是原对照做不到的）：

| 在 baseline 代码上消失的 case | 根因 | 性质 |
|---|---|---|
| e2-025 | RC-10 `restricted` 语义 | **代码** |
| e2-029 / e2-030 / e2-055 | RC-8 `is_management` 派生 | **代码** |
| e2-004 / e2-008 / e2-044 / e2-048 | RC-11 未知身份提前 deny | **代码** |

而 **e2-059 / e2-060 / e2-061（ACL 案）在 baseline 代码上同样通过** —— 因为 ACL 数据已由修后的
seed 写成域类型。→ **RC-9 是数据/seed 修复，不是代码修复**。

**证据等级**：由「可信」提升为 **严格因果证明**（单变量，数据集恒定）。

---

## 3. P2 — E1 hermeticity（已完成）

**Codex 要求**：「修掉 R4-Acme / R4-Globex 测试污染。让 E1 hermetic。只是测试卫生。」

**根因**：`tests/integration/test_s11_connector_ingestion.py` 为断言 `stats.created == 2`，
每轮生成 `csv:r4-test-<uuid>` 唯一来源并写入两个同名供应商，**跑完不清理**。

**修复**：保留唯一 source_system（断言需要），在 `finally` 删除本轮创建的关系 / 别名 / 实体，
并加自检断言「本轮残留 = 0」。

**历史污染清理**：删 8 个累积实体（含 32 条关系），保留 `SUP052` / `SUP053` 一对
（已提交的 E1 数据集引用这两个名字，且 `SUP052` 被 E2 的 ACL 引用）。

**验证**：

| 检查 | 结果 |
|---|---|
| 连跑 test_s11 两次 | 无新增重名，零残留 |
| **全套 pytest 后重名查询** | **0 行**（修复前 8 行）→ **E1 已 hermetic** |
| **E1** | **98.5%**（64/65）—— 回到基线值 |
| 全套 pytest | 353 passed / 3 skipped / 0 failed |
| E2 | 仍 61/61 |

> 残留的 `e1-054`（mention `无限极`）**修复前即存在**，与本轮无关。

---

## 4. P3 — Customer Validation 判定门改写（已完成）

**Codex 修正**：「`<5 人应约` 不能作为产品 Kill Criteria。它测的是你的**客户访问能力**，
不是**问题是否存在**。」

**改动**（`A_CUSTOMER_VALIDATION.md`）：

| 项 | 原 | 现 |
|---|---|---|
| 名称 | 48 小时 Customer Access **冒烟** | **Customer Access Test（48 小时）** |
| `<5 人应约` 的判定 | **产品 Kill Criterion #1 → 停止，重新选题** | **Access 假设失败 → 换触达策略，不杀产品方向** |
| Kill Criteria 列表 | 6 条（含上述） | **5 条**（移除该条，保留测「问题本身」的判据） |

---

## 5. 代码侧修正（随 P1/P2 提交，ece `93ed0e3`）

### 5.1 「V0: 固定 Agent」——消除 Selection 概念

Codex §3：「V0 已经规定一个固定 Agent。那 V0 根本不存在 Selection。工程上最好理解成
**V0: Fixed Agent**，而不是 **Agent Selection Interface**，**否则 CC 很容易又造一个 selector**。」

→ `KERNEL_BOUNDARY.md` 行 10 已改：`**V0: 固定 Agent**（**无 Selection 概念**）`，
并注明动态选择推迟到 V1 且届时须另写 ADR。

### 5.2 Permission 的概念名 —— Enforcement Boundary，不是 IAM

Codex §3：「概念应该理解成 **Enforcement Boundary**，而不是 IAM」；
并指出 `V3_CLOSEOUT` §1.1 的「企业不可交付」把**交付前提**与**核心能力**混在一起说。

→ `KERNEL_BOUNDARY.md` §3.1 已加：Kernel 拥有 **enforcement point + scope contract**，
身份目录 / 组同步 / 凭据轮换 / 策略库**都可以外部提供**。

### 5.3 V0 成功判据 —— 不证明 PMF

Codex §5：「『证明能够形成真实业务价值闭环』这句话太强。它最多证明 **Kernel technical loop 成立**。
真实业务价值必须由 **A Customer Validation** 来证明。**V0 不负责证明 PMF。**」

→ `V3_CLOSEOUT.md` §2.3 已改。并补：判定「不是规则引擎 + RAG」的关键是链尾的 **Context Update**，
V0 必须真的实现这一步。

### 5.4 架构冻结点

Codex §1：「**V3_CLOSEOUT 应成为架构冻结点。不要再出现 V3.1 / V3.2 / V4 架构迭代。**『但这是最后一次。』」

→ `V3_CLOSEOUT.md` 新增 §5.1 冻结点声明：允许执行与 errata 级修正；
**不允许新增架构层级 / 核心对象 / 接口族，不允许 V3.x / V4 架构重写，不允许再写 PRD**。
若发现架构错误，走**新增 ADR**，不重写 PRD。

---

## 6. 记录在案的两条 Codex finding（非本轮 blocker，未修）

### 6.1 `/permissions/check` 的授权主体可被调用者指定

Codex §9 原话：「`user_ref = req.user_ref or x_user_id`……**body 中的 `user_ref` 可以决定检查哪个身份**。
……如果这个 endpoint 被当成真正的授权接口……客户端理论上可以提交别人的 `user_ref` 来询问
『这个人能不能访问这个对象？』……**不是本轮 blocker**。但如果未来它进入生产授权链：**必须改**。
**授权主体不能由调用者自己在 request body 中指定。**」

→ 已在 `ece/src/ece/api/identity.py` 中的该行上方就地标注 SECURITY FINDING 与修改条件。

### 6.2 ACL 模型无 classification 维度

Codex §7：「如果未来产品真正要求：**同一个 object 对同一个 user 在不同 classification 下有不同 ACL**，
那么当前 ACL 模型确实不够。**那时应该改 ACL 模型。**」

→ 已在 `ece/src/ece/permissions/engine.py` 的矩阵下方就地标注 KNOWN MODEL LIMITATION
与"不要再用改数据集绕过"的警告。

---

## 7. 第三轮送审范围（供 Codex 核验本轮落实）

**必读**

```
docs/v3/CODEX_ROUND2_FINDINGS.md     ← 本文件
docs/v3/A_CUSTOMER_VALIDATION.md     ← P3
docs/v3/KERNEL_BOUNDARY.md           ← 5.1 / 5.2
docs/v3/V3_CLOSEOUT.md               ← 5.3 / 冻结声明
codex 判词原文（仓库外）
```

**ece 仓（8.C 部分）**

```
ece/ commit 93ed0e3                  ← P1 + P2 的全部改动
ece/reports/eval-archive/2026-09-20-cut040R2/README.md            ← 落实说明
ece/reports/eval-archive/2026-09-20-cut040R2/single-variable/*.txt ← P1 原始 stdout
ece/reports/eval-archive/2026-09-20-cut040R2/fixed/E1.txt          ← P2 后 E1 = 98.5%
ece/tests/integration/test_s11_connector_ingestion.py              ← P2 的修复本体
```

**建议的核验问题**

1. **P1 是否真的单变量？** 数据集是否在两臂中完全相同？4/4 → 0/0 的因果链是否闭合？
   「RC-9 是数据修复而非代码修复」这个推论是否成立？
2. **P2 是否真的让 E1 hermetic？** 清理是否会在断言失败时也执行（`finally` 正确性）？
   保留 `SUP052`/`SUP053` 是否属于"留了个尾巴"？
3. **P3 是否改对了？** 移除该条后，剩下的 5 条 Kill Criteria 是否真的都测「问题本身」？
4. **三处修正（5.1/5.2/5.3）是否是 errata 而非架构迭代？** 有无越界改写？
5. **冻结声明是否可执行？** 什么算 errata、什么算架构迭代，界线是否清楚？

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
