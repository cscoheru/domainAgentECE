# Reference Case — NimbusWorks SOC2 Type II 续证

> ⚠️ **REFERENCE CASE / DEMO CASE** —— 本案例为演示用途构建的虚构企业，数据为高可信模拟。
> **不是真实客户案例。任何对外展示必须保留本声明。**
> 用途：15 分钟客户演示（见 demo-script.md）+ MVP 回归测试数据基座

---

## 1. Case 概要

| 字段 | 内容 |
|---|---|
| Case Name | NimbusWorks SOC2 Type II 续证证据准备 |
| Customer | NimbusWorks（虚构）：450 人 B2B SaaS（零售数字化中台），ARR ¥2.1 亿，已通过 SOC2 Type I，首次 Type II 续证 |
| Persona | **Lin Chen**，GRC 合规经理（1 人团队，向 CISO 汇报） |
| Problem | Type II 审计 6 周后开始；审计期间 H1/2026（2026-01-01 ~ 06-30）；需为 12 个 CC 域控制项归集期间证据；去年 Type I 靠 4 周人工 + 300+ 封邮件 |
| Before | Excel 控制矩阵 + 逐个系统截图 + 催 7 位控制责任人 + 审计现场被问倒（政策版本对不上） |
| Input | 审计范围三要素：SOC2 Type II + H1/2026 + 生产系统域（ERP/OSS/CRM/HR 四系统） |
| Agent | Control Intake Agent + Evidence & Gap Agent（见 agent-runtime.md） |
| Reasoning | 充分性（类型×数量×期间）/ 新鲜度 / 覆盖度 / 归因路由 |
| Workflow | Ingest→Map→Retrieve→Reason→Act→Approve→Package |
| Output | Audit-Ready Evidence Pack（Evidence Matrix + Gap List + 派工回执） |
| Action | 4 个缺口自动建任务派给责任人（Mock 工单系统回执） |
| Business Value | 审计准备 3–4 周→≤3 天；缺口提前 4–6 周暴露（vs 审计现场发现）；单控制项归集 30–60 分钟→分钟级 |

## 2. Mock Enterprise 数据规格（`/mock/enterprise`）

> 要求：内部关系一致、可支撑推理、规模足以展示价值。角色门控：安全类证据仅 security/compliance 可见。

### 2.1 People & Organization（18 人，关键 8 人）

| 人 | 角色 | 部门 | 备注 |
|---|---|---|---|
| Lin Chen | GRC 合规经理 | Security | **actingUser（默认演示视角）** |
| David Wu | CISO | Security | Buyer persona |
| Emma Zhao | IT 运维负责人 | IT | CC6.1/6.2 控制责任人 |
| Frank Liu | 高级运维工程师 | IT | 访问评审执行人（证据署名） |
| Grace Wang | HR 总监 | People | CC1.4 培训控制责任人 |
| Henry Sun | 研发 VP | Engineering | 变更管理控制责任人 |
| Iris Li | 法务顾问 | Legal | 政策文档 owner |
| Jack Mo | 采购经理 | Procurement | 供应商管理责任人（访谈线索） |

其余 10 人：工程/客服/销售各若干，用于工单署名与组织树完整性。

### 2.2 Systems（SystemScope 本体实例）

`PROD-ERP`、`PROD-OSS`（运营支撑）、`PROD-CRM`、`PROD-HR` 四个生产系统 + `CORP-Wiki`、`TICKET-Jira`、`HRIS`、`GIT` 四个支撑系统。

### 2.3 Documents（40+ 篇，关键 12 篇）

| 文档 | 类型 | updatedAt | 权限 | 用途 |
|---|---|---|---|---|
| 《访问控制政策 v3.2》 | policy | 2026-02-10 | all | CC6.1 证据 ✅ |
| 《访问控制政策 v3.1》 | policy | 2024-11-03 | all | 过期版本（干扰项） |
| 《信息安全总体政策 v2.0》 | policy | **2024-08-15** | all | **缺口#1：审计期间前已过期 16 个月** |
| 《Q1-2026 访问评审记录-ERP》 | review | 2026-04-02 | security | CC6.2 证据 ✅ |
| 《Q1-2026 访问评审记录-OSS》 | review | 2026-04-05 | security | CC6.2 证据 ✅ |
| 《Q1-2026 访问评审记录-CRM》 | review | 2026-04-08 | security | CC6.2 证据 ✅ |
| 《HR 访问评审记录》 | review | — | — | **缺口#2：缺失（HRIS 评审未做）→ 覆盖度 3/4** |
| 《Q2-2026 访问评审计划》 | review-plan | 2026-06-20 | security | 计划≠证据（干扰项） |
| 《安全意识培训记录-H1》 | training-record | 2026-05-30 | hr+security | CC1.4 证据（**仅 412/448 人完成 → 缺口#3 覆盖率 92%**） |
| 《变更管理程序 v1.8》 | policy | 2026-03-01 | all | CC8.1 证据 ✅ |
| 《漏洞扫描月报 2026-06》 | report | 2026-07-02 | security | CC7.1 证据 ✅ |
| 《供应商安全评估-NovaCloud》 | assessment | 2026-01-20 | security+procurement | CC9.2 证据 ✅ |

另 28+ 篇：无关业务文档（零售客户案例、营销物料、研发设计稿）作为检索干扰项。

### 2.4 Records（业务记录 30+ 条，关键 6 条）

| 记录 | 系统 | 时间 | 关联 | 用途 |
|---|---|---|---|---|
| CHG-2026-0412 | GIT/变更 | 2026-04-12 | Henry 审批 | CC8.1 变更证据 ✅ |
| CHG-2026-0530 | GIT/变更 | 2026-05-30 | 双人审批 | CC8.1 证据 ✅ |
| TERM-2026-017 | HRIS | 2026-05-18 | 离职员工 Raj | CC6.3 证据：离职当日权限回收工单 ✅ |
| TERM-2026-022 | HRIS | 2026-06-25 | 离职员工 Sara | **缺口#4：权限回收工单在离职后 5 天才建 → 新鲜度违规** |
| TASK-旧审计整改项 | Jira | 2025-12 | 已关闭 | 历史干扰项 |
| 其余 | — | — | — | 培训完成明细（448 人×完成状态）支撑覆盖率计算 |

### 2.5 Ontology 实例（`/src/domain/ontology/soc2-cc.json`）

12 个控制项，示例（CC6.2）：

```json
{
  "id": "CC6.2",
  "title": "定期访问权限评审",
  "evidenceTypes": ["access_review_record"],
  "requires": { "frequency": "quarterly", "minCount": 2, "period": "H1/2026" },
  "appliesTo": ["PROD-ERP", "PROD-OSS", "PROD-CRM", "PROD-HR"],
  "ownerRole": "IT_OPS_LEAD",
  "sufficiencyRule": "每系统每季度≥1 份含完整用户清单+审批人+日期的评审记录"
}
```

### 2.6 埋入缺口（回归测试的"标准答案"）

| # | 缺口 | 类型 | 期望推理 | 期望 Action |
|---|---|---|---|---|
| G1 | 《信息安全总体政策》2024-08 过期 | 新鲜度 | 判定 expired，期间外 | 派 Iris（法务）更新，2 周 |
| G2 | HR 系统访问评审缺失 | 覆盖度 | 4 系统仅 3 有记录 → partial | 派 Emma 补做 HRIS 评审，1 周 |
| G3 | 培训完成率 412/448=92% | 覆盖度 | 低于阈值 95% → partial | 派 Grace 追 36 人，2 周 |
| G4 | 离职权限回收延迟 5 天 | 新鲜度 | 违反"当日回收"规则 | 派 Emma 补救+整改说明，1 周 |

### 2.7 权限门控规则（演示"权限感知"用）

| 数据 | 可见角色 |
|---|---|
| 安全评审记录/漏洞报告/供应商评估 | security, compliance |
| HR 记录/培训明细 | hr, security, compliance |
| 政策/变更记录 | all |

演示切换：actingUser=Lin Chen(compliance) 可见安全证据；切到普通工程视角则安全证据被过滤并在 UI 明示"权限不足，未检索 N 条"。

## 3. 运行结果样例（Evidence Pack 节选）

```text
CC6.2 定期访问权限评审 — ⚠️ PARTIAL
 ├─ 证据 1: Q1 访问评审-ERP (2026-04-02, Frank Liu 签发) ✅ 充分
 ├─ 证据 2: Q1 访问评审-OSS (2026-04-05) ✅ 充分
 ├─ 证据 3: Q1 访问评审-CRM (2026-04-08) ✅ 充分
 ├─ 推理: 覆盖度 3/4 系统（HRIS 无评审记录；检索到《Q2 评审计划》但计划≠记录）
 └─ GAP-G2 → 已创建任务 #TK-1024 → Emma Zhao（IT）→ 截止 2026-07-10 ✅回执
```
