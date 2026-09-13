# RESEARCH_PRD.md

# Glean × Domain Product
## Research → Product Framework → MVP → Customer Validation

Version: 0.2
Status: Executable Research & MVP Discovery PRD

---

# 1. 项目目标

本项目不是为了研究 Glean 本身，也不是为了复制 Glean。

真正目标是：

> 以 Glean 为潜在 Enterprise AI Infrastructure / Context Layer，快速寻找一个具有真实商业价值的 Domain Product，并在尽可能短的时间内形成可演示 MVP，用于约真实客户进行产品验证。

因此必须同时解决：

### Problem A：技术问题

Glean 到底提供了什么？

我们的产品应该建立在哪一层？

### Problem B：商业问题

我们到底应该做什么？

什么产品可以最快获得：

- 客户兴趣
- 客户访谈
- POC
- 真实数据
- 首批案例
- 商业收入

---

# 2. 核心原则

## 2.1 Research is not the Goal

研究 Glean 的目的，是减少我们重复建设基础设施的成本。

不是为了形成一份漂亮的 Glean 分析报告。

## 2.2 MVP is mandatory

研究完成后必须形成一个 MVP。

允许 MVP 很窄。

不允许没有 MVP。

## 2.3 Customer-facing from Day 1

所有产品设计都必须回答：

> “两周后能不能拿给一个真实企业的人看？”

如果不能，需要说明为什么。

---

# 3. 目标产出

至少产生：

```text
01 Glean Capability Map
02 Capability Matrix
03 Glean Architecture Hypothesis
04 Product Boundary
05 Context Adapter Specification
06 Domain Product Architecture
07 5–10 Product Candidates
08 Top 3 Product Candidates
09 Recommended MVP
10 Reference Case
11 MVP Product Spec
12 Demo Script
13 Customer Interview Guide
14 Customer Validation Metrics
```

---

# 4. Research Phase

## 4.1 Glean Capability Research

### Enterprise Context

研究：

- Enterprise Knowledge
- People
- Organizations
- Documents
- Relationships
- Permissions
- Context
- Entity Understanding
- Knowledge Graph / Enterprise Graph（如果官方资料确认）

核心问题：

> Glean 如何让 Agent 理解“企业”，而不仅仅是搜索文档？

### Enterprise Search

研究：

- Keyword Search
- Semantic Search
- Natural Language Search
- Personalized Search
- Permission-aware Search
- Search API
- Retrieval
- Ranking
- Citations / Grounding

核心问题：

> Search 在 Glean Agent Architecture 中到底是什么角色？

### Connectors

研究：

- Connector 数量
- 数据源类型
- Indexing
- Sync
- Permission Sync
- Real-time / Batch
- Custom Connector
- API
- MCP

判断：

```text
Glean Core
Partner Extension
Customer Extension
Domain Product Extension
```

### Agent Architecture

研究：

```text
User
 ↓
Intent
 ↓
Agent
 ↓
Context
 ↓
Planning
 ↓
Tool
 ↓
Action
 ↓
Observation
 ↓
Reasoning
 ↓
Verification
 ↓
Answer / Action
```

逐项判断：

| Capability | Glean Native | Configurable | API/SDK | Third Party | Unknown |
|---|---|---|---|---|---|

重点研究：

- Planning
- Reasoning
- Branching
- Looping
- Tool Calling
- Human Approval
- Model Selection
- Workflow
- Agent-to-Agent
- Scheduling
- Event Trigger
- Memory
- Verification

---

# 5. Agent Builder Research

重点研究 Glean Agent Builder：

- Natural Language creation
- Visual builder
- Workflow
- Steps
- Branching
- Loops
- Tools
- Models
- Context
- Preview
- Debug
- Versioning
- Deployment
- Permissions
- Import / Export
- Agent Library

核心问题：

> Agent Builder 是 Agent IDE、Workflow Builder，还是两者结合？

更重要的是：

> 如果我们做 Domain Product，哪些能力完全没有必要自己做？

---

# 6. Governance

研究：

- Permissions
- Data access
- Agent access
- Approval
- Audit
- Governance
- Security
- Compliance
- Deployment
- Lifecycle

核心问题：

> 哪些东西应该直接交给 Glean，而不是自己重新实现？

---

# 7. Evaluation

分成：

```text
Platform Evaluation
        ↓
Domain Evaluation
```

## Platform

- Retrieval
- Agent reliability
- Tool success
- Runtime
- Errors

## Domain

- Business correctness
- Reasoning quality
- Decision quality
- Action quality
- Outcome

核心问题：

> 哪一部分 Evaluation 最可能形成我们的长期 IP？

---

# 8. Evidence System

每一个重要判断记录：

| Claim | Source | Evidence | Confidence | Last Verified |
|---|---|---|---|---|

Confidence：

- CONFIRMED
- STRONGLY INFERRED
- INFERRED
- UNKNOWN

禁止：

```text
网上有人说
所以 Glean 一定……
```

---

# 9. Capability Matrix

必须形成：

| Capability | Glean Native | Glean API | Partner Extension | Product Should Build | IP Potential | Evidence |
|---|---|---|---|---|---|---|
| Enterprise Search | | | | | | |
| Enterprise Context | | | | | | |
| Permissions | | | | | | |
| Connectors | | | | | | |
| Agent Runtime | | | | | | |
| Agent Builder | | | | | | |
| Workflow | | | | | | |
| Tool Calling | | | | | | |
| Governance | | | | | | |
| Observability | | | | | | |
| Evaluation | | | | | | |
| Domain Ontology | | | | | | |
| Domain Reasoning | | | | | | |
| Domain Workflow | | | | | | |
| Domain Knowledge | | | | | | |
| Domain KPI | | | | | | |

---

# 10. Architecture Boundary

最终形成：

```text
┌──────────────────────────────────────────┐
│              DOMAIN PRODUCT              │
│                                          │
│ Domain UI                                │
│ Domain Agents                            │
│ Domain Ontology                          │
│ Domain Reasoning                         │
│ Domain Workflows                         │
│ Domain Playbooks                         │
│ Domain Evaluation                        │
│ Domain KPI                               │
└───────────────────┬──────────────────────┘
                    │
             Context Adapter
                    │
┌───────────────────▼──────────────────────┐
│                   GLEAN                  │
│                                          │
│ Enterprise Context                       │
│ Enterprise Search                        │
│ Permissions                              │
│ Connectors                               │
│ Agent Infrastructure                     │
│ Governance                               │
│ Observability                            │
└───────────────────┬──────────────────────┘
                    │
             Enterprise Systems
```

必须验证，而不是预设。

---

# 11. Domain Product Layer

Domain Product 至少研究：

```text
UI
Agents
Ontology
Reasoning
Workflow
Playbooks
Evaluation
KPI
```

---

# 12. Domain Ontology

初始假设：

```text
Enterprise
 ├── Organization
 ├── Person
 ├── Customer
 ├── Product
 ├── Project
 ├── Process
 ├── KPI
 ├── Decision
 ├── Problem
 └── Action
```

要求：

- 与 Glean 解耦
- 独立版本管理
- 可迁移
- 可测试
- 可扩展

---

# 13. Context Adapter

设计统一接口：

```text
search()
get_entity()
get_person()
get_organization()
get_customer()
get_project()
get_metric()
create_task()
send_message()
update_record()
```

底层可以：

```text
Glean
MCP
REST
API
Database
Mock
Other Platform
```

---

# 14. Domain Agent

标准：

```text
Role
Goal
Context
Ontology
Knowledge
Tools
Workflow
Reasoning
Guardrails
Evaluation
Output
KPI
```

不要做 Generic Agent。

要做：

> Narrow + Deep + Demonstrable Agent

---

# 15. Product Candidate Discovery

研究结束后至少提出 5 个候选。

可以探索：

- Management Intelligence
- Sales Intelligence
- Customer Intelligence
- Consulting Intelligence
- Operations Intelligence
- HR Intelligence
- Project Intelligence
- Finance Intelligence
- Procurement Intelligence
- Industry-specific Intelligence

也可以提出完全不同的方向。

---

# 16. Candidate Scoring

每个候选 1～5 分：

| Dimension | Weight |
|---|---:|
| Customer Pain | 20% |
| Willingness to Pay | 15% |
| Demoability | 15% |
| Time to MVP | 15% |
| Domain IP | 10% |
| Glean Fit | 10% |
| Replicability | 5% |
| Founder Fit | 5% |
| Customer Access | 5% |

输出：

```text
Score
Ranking
Reason
Risks
Unknowns
```

---

# 17. Customer Access

不要只评价：

> “这个市场很大。”

必须评价：

> “我们能不能在 2～4 周内找到 5 个愿意聊的人？”

Customer Access 分析：

- Founder network
- Existing professional network
- Industry contacts
- Communities
- Professional relationships
- Public company contacts
- Consulting relationships
- Partner ecosystem

如果市场很大，但无法获得客户访谈机会，应降低优先级。

---

# 18. MVP Selection

最终选择标准不是 Market Size 最大，而是：

> Customer Learning Velocity 最大。

优先考虑：

```text
Time to MVP
×
Demo Quality
×
Customer Access
×
Problem Pain
×
Learning Value
```

---

# 19. MVP Definition

MVP 不超过：

```text
1 Core Persona
1 Core Problem
1 Core Workflow
1–2 Domain Agents
1 Reference Dataset
1–3 Tools
1 Core Output
1 Business Outcome
```

如果需要更多才能 Demo，说明范围过大。

---

# 20. Reference Case

必须设计一个 Reference Case。

格式：

```text
Case Name

Customer:
某类企业

Persona:
某个具体岗位

Problem:
一个明确业务问题

Before:
传统工作方式

Input:
企业输入数据

Context:
企业背景

Agent:
Domain Agent

Reasoning:
领域分析

Workflow:
执行步骤

Output:
最终结果

Action:
下一步动作

Business Value:
节省时间 / 提高质量 / 降低风险 / 增加收入
```

必须明确：

> Reference Case / Demo Case

不能冒充真实客户。

---

# 21. MVP Demo

Demo 必须在 10～15 分钟完成。

建议：

### 0–2 min
客户背景

### 2–4 min
传统工作方式

### 4–9 min
Agent 实际运行

### 9–12 min
输出 + Reasoning + Evidence

### 12–15 min
下一步 Action + Business Value

最后自然引出：

> “如果接入你们自己的数据，这个场景对你们有没有价值？”

---

# 22. Demo 必须展示“实力”

不能只是：

```text
输入问题
 ↓
LLM
 ↓
漂亮答案
```

至少展示：

```text
Enterprise Context
      ↓
Domain Ontology
      ↓
Domain Reasoning
      ↓
Workflow
      ↓
Tool
      ↓
Evidence
      ↓
Business Output
```

客户看到的应该是：

> “这不是一个 ChatGPT 套壳。”

而是：

> “它理解我的业务，并且能够把知识转化成工作。”

---

# 23. MVP 技术架构

第一版：

```text
Frontend
   ↓
Application API
   ↓
Domain Agent
   ↓
Domain Reasoning
   ↓
Context Adapter
   ↓
┌───────────────┐
│ Glean Adapter │
│ Mock Adapter  │
└───────────────┘
```

Domain 层不得依赖 Glean SDK。

---

# 24. Mock Enterprise Context

如果暂时没有真实 Glean：

```text
Mock Enterprise
├── People
├── Organizations
├── Documents
├── Projects
├── Customers
├── Metrics
├── Tasks
└── Events
```

Mock 数据必须足够真实，可以支持完整 Demo。

所有 Mock API 必须遵循 Context Adapter 接口。

---

# 25. MVP Evaluation

建立至少 10～20 个测试案例：

```text
Input
Expected Behavior
Expected Output
Evaluation Criteria
Actual Output
Score
```

评价：

- Accuracy
- Reasoning
- Evidence
- Tool correctness
- Workflow correctness
- Business usefulness

---

# 26. Customer Interview

MVP 完成后必须进入客户访谈。

核心问题：

1. 你们现在怎么做？
2. 谁负责？
3. 多久做一次？
4. 一次需要多少时间？
5. 最大痛点是什么？
6. 哪一步最需要判断？
7. 哪些数据需要查？
8. 哪些系统需要操作？
9. 如果 AI 能完成 70～80%，价值多大？
10. 什么情况下你们愿意让 AI 真正执行？
11. 什么情况下必须人工审批？
12. 如果接入真实数据，你愿意做 POC 吗？
13. 谁是决策人？
14. 谁预算？
15. 如果 POC 成功，什么条件下愿意付费？

---

# 27. Customer Validation Metrics

记录：

```text
Problem Severity
Frequency
Current Cost
Current Workaround
Data Availability
AI Acceptance
Security Concern
Willingness to Pilot
Willingness to Pay
Decision Maker
Next Step
```

---

# 28. POC Trigger

出现以下情况即可考虑 POC：

- 至少 2 个客户确认相同痛点
- 客户愿意提供脱敏真实数据
- 客户愿意安排技术/业务人员
- 客户愿意共同定义成功指标

---

# 29. 长期架构

```text
                 DOMAIN PRODUCT
                       │
              ┌────────┴────────┐
              │                 │
       Domain Intelligence   Domain UX
              │
        ┌─────┴─────┐
        │           │
      Agents     Workflows
        │           │
        └─────┬─────┘
              │
       Context Adapter
              │
            GLEAN
              │
      Enterprise Systems
```

长期原则：

> Glean 可以替我们解决 Enterprise AI Infrastructure，但不能替我们解决 Domain Intelligence。

---

# 30. Portability

```text
Domain Product
      │
Abstraction Layer
      │
 ┌────┼────────┐
 │    │        │
Glean Other   OSS
```

第一版不要求真正支持多平台，但架构上避免不可逆锁定。

---

# 31. 禁止事项

第一阶段禁止：

1. Glean Clone
2. Generic Agent Platform
3. Generic RAG
4. Generic Search
5. Connector Platform
6. 大规模 UI
7. 大规模 SaaS
8. 复杂多租户
9. 大规模基础设施
10. 没有客户问题的 Demo
11. 没有案例的“平台展示”
12. 把未知的 Glean 内部实现当成事实

---

# 32. 第一阶段执行顺序

严格按照：

```text
STEP 1
Glean Research

STEP 2
Capability Matrix

STEP 3
Architecture Boundary

STEP 4
Identify Product Opportunity

STEP 5
Score 5–10 Candidates

STEP 6
Select Top 3

STEP 7
Recommend 1 MVP

STEP 8
Define Reference Case

STEP 9
Define MVP Scope

STEP 10
Define Demo Flow

STEP 11
Define Customer Interview

STEP 12
STOP
```

---

# 33. 第一阶段最终输出文件

```text
/docs
  /research
    glean-capability-map.md
    glean-agent-architecture.md
    glean-context-architecture.md
    glean-governance.md
    glean-evaluation.md
    evidence-matrix.md

  /architecture
    glean-x-product.md
    domain-product-layer.md
    context-adapter.md
    agent-runtime.md
    portability.md

  /product
    product-candidates.md
    product-ranking.md
    recommended-mvp.md
    mvp-scope.md

  /cases
    reference-case.md
    demo-script.md

  /customer
    customer-profile.md
    interview-guide.md
    validation-metrics.md

  /adr
    ADR-001.md
    ADR-002.md

  /diagrams
    glean-capability.mmd
    glean-x-product.mmd
    agent-runtime.mmd
    context-ontology.mmd
    portability.mmd
```

---

# 34. 第一阶段结束条件

必须回答：

### Glean
> Glean 到底是什么？

### Boundary
> Glean 做什么？我们做什么？

### Product
> 我们到底可能做什么？

### MVP
> 第一个 MVP 是什么？

### Case
> 客户能看到什么案例？

### Demo
> 15 分钟能不能演示？

### Customer
> 第一批客户从哪里来？

### Validation
> 我们要向客户验证什么？

---

# 35. 最终原则

> Research enough to decide.
>
> Build enough to demonstrate.
>
> Demo enough to get customer truth.
>
> Customer truth decides what to build next.

真正的成功标准：

```text
Glean Understanding
        +
Domain Product Hypothesis
        +
Working MVP
        +
Reference Case
        +
Customer Conversation
        ↓
Real Product Evidence
```
