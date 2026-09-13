# Glean × Domain Product Compatible Architecture
## PRD v0.1 — Glean Reverse Engineering & Product Architecture Discovery

> **项目性质**：研究型 PRD / Architecture Discovery  
> **第一阶段目标**：Reverse Engineer Glean → Capability Mapping → Product Boundary Definition → Glean-Compatible Architecture → MVP Technical Blueprint

---

## 1. 项目目标

本项目不是开发一个 Glean 的替代品，也不是开发一个通用 Agent 平台。

目标是：

> 基于 Glean 当前公开产品能力、Agent 架构、连接器体系、Enterprise Context、Search、Agent Runtime、Governance、Evaluation 和 Observability 能力，反向构建一套“Glean-compatible Domain Product Architecture”。

最终回答四个问题：

1. Glean 已经解决了什么？
2. Glean 没有解决、或者不适合解决什么？
3. 哪些能力应该直接依赖 Glean？
4. 哪些能力应该成为本产品自己的核心 IP？

最终形成一套可以指导后续产品设计、技术开发和商业化的参考架构。

---

# 2. 核心设计原则

## 2.1 不重新造 Glean

原则：

> Glean 已经成熟的基础设施，原则上不重复开发。

重点研究并优先复用：

- Enterprise Context
- Enterprise Search
- Knowledge
- People / Organization Context
- Permissions
- Connectors
- Agent Runtime
- Agent Builder
- Agent Orchestration
- Governance
- Observability
- Evaluation

---

# 3. 核心架构假设

第一版假设采用以下架构：

```text
                    USER
                      │
                      ▼
┌──────────────────────────────────────────────┐
│              DOMAIN PRODUCT                 │
│                                              │
│ Domain UI                                    │
│ Domain Agents                                │
│ Domain Ontology                              │
│ Domain Reasoning                             │
│ Domain Workflows                             │
│ Domain Playbooks                             │
│ Domain Evaluation                            │
│ Domain KPI / Outcome Model                   │
│                                              │
│              OUR IP                          │
└──────────────────────┬───────────────────────┘
                       │
                       │ API / Agent / Context
                       ▼
┌──────────────────────────────────────────────┐
│                    GLEAN                    │
│                                              │
│ Enterprise Context                           │
│ Enterprise Search                            │
│ Knowledge / People / Relationships           │
│ Permissions                                  │
│ Connectors                                   │
│ Agent Runtime                                │
│ Agent Builder                                │
│ Orchestration                                │
│ Governance                                   │
│ Observability                                │
│                                              │
│              GLEAN                          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             ENTERPRISE SYSTEMS              │
│                                              │
│ CRM / ERP / HR / BI / Email / Drive         │
│ Slack / Teams / Jira / Notion / etc.        │
└──────────────────────────────────────────────┘
```

该架构不是最终答案。

Claude Code 的任务是验证、修正并细化这个假设。

---

# 4. Research Task：Reverse Engineer Glean

必须基于 Glean 官方公开资料进行研究。

优先来源：

- Glean 官方网站
- Glean 官方产品文档
- Glean 官方开发者文档
- Glean 官方博客
- Glean 官方 Partner Network
- Glean 官方 API / SDK 文档
- Glean 官方案例

禁止仅根据二手文章推断 Glean 的内部架构。

对于无法确认的内容必须标记：

```text
CONFIRMED
INFERRED
UNKNOWN
```

不得把推测当成事实。

---

# 5. Glean Capability Map

## 5.1 Enterprise Context

研究：

- 企业知识
- People
- Organization
- Documents
- Relationships
- Permissions
- User context
- Entity context
- Enterprise graph / knowledge graph（如果公开资料可以确认）

回答：

> Glean 如何理解一个企业，而不仅仅是搜索文档？

---

## 5.2 Enterprise Search

研究：

- keyword search
- semantic search
- natural language search
- contextual search
- personalization
- permission-aware search
- search API
- retrieval
- ranking
- citation / grounding

回答：

> Search 在 Glean Agent 架构中的角色是什么？

---

## 5.3 Connectors

研究：

- connector 类型
- connector 数量
- ingestion
- indexing
- synchronization
- permissions synchronization
- real-time / batch
- custom connector
- API

建立：

```text
Source System
      ↓
Connector
      ↓
Index / Context
      ↓
Agent
```

分析 Connector 是否属于：

```text
Glean Core
Partner Extension
Customer Extension
Our Product Extension
```

---

# 6. Agent Architecture

重点研究 Glean Agent 的生命周期。

建立以下模型：

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

验证 Glean 是否支持：

- planning
- multi-step execution
- branching
- loops
- tool calling
- human approval
- model selection
- context retrieval
- agent-to-agent
- workflow execution
- scheduled execution
- event-triggered execution

每项能力标记：

```text
Glean Native
Glean Configurable
Glean API
Third-party
Unknown
```

---

# 7. Agent Builder

研究 Glean Agent Builder：

- Agent creation
- natural language creation
- visual builder
- workflow
- branching
- loops
- tools
- models
- context
- testing
- versioning
- deployment
- permissions

重点回答：

> Glean Agent Builder 到底是“Agent IDE”，还是“Workflow Builder”，还是二者的结合？

---

# 8. Governance

研究：

- permissions
- access control
- agent permissions
- data security
- governance
- approval
- audit
- compliance
- deployment control
- agent lifecycle

回答：

> 一个 Domain Product 在安全和权限方面，应该把什么交给 Glean？

---

# 9. Evaluation

研究 Glean 对 Agent Evaluation 的支持。

重点关注：

- agent testing
- evaluation
- quality measurement
- observability
- ROI
- success metrics
- production monitoring

然后定义：

> 哪些 Evaluation 属于 Glean 通用能力，哪些 Evaluation 必须由 Domain Product 自己定义？

例如：

```text
Glean Evaluation
        │
        ├── Agent reliability
        ├── Retrieval quality
        ├── Tool success
        └── Runtime metrics

Domain Evaluation
        │
        ├── Business correctness
        ├── Domain reasoning quality
        ├── Decision quality
        └── Business outcome
```

---

# 10. 建立 Glean Capability Matrix

必须输出一张表：

| Capability | Glean Native | Glean API | Partner Extension | Product Should Build | IP Potential |
|---|---|---|---|---|---|
| Enterprise Search | | | | | |
| Enterprise Context | | | | | |
| Permissions | | | | | |
| Connectors | | | | | |
| Agent Runtime | | | | | |
| Agent Builder | | | | | |
| Workflow | | | | | |
| Tool Calling | | | | | |
| Governance | | | | | |
| Observability | | | | | |
| Evaluation | | | | | |
| Domain Ontology | | | | | |
| Domain Reasoning | | | | | |
| Domain Workflow | | | | | |
| Domain Knowledge | | | | | |
| Domain KPI | | | | | |

每个单元格必须说明依据。

---

# 11. Domain Product Layer

研究完成以后，定义本产品应该存在于 Glean 哪一层之上。

目标模型：

```text
┌───────────────────────────────┐
│        Domain Product         │
│                               │
│ UI                            │
│ Agents                        │
│ Ontology                      │
│ Reasoning                     │
│ Workflow                      │
│ Playbooks                     │
│ Evaluation                    │
│ KPI                           │
└───────────────┬───────────────┘
                │
        Glean Interface
                │
┌───────────────▼───────────────┐
│             Glean             │
└───────────────────────────────┘
```

重点研究：

> Domain Product 与 Glean 的最小必要接口是什么？

---

# 12. Context Adapter

必须设计一个：

```text
Context Adapter
```

它负责把 Glean Enterprise Context 转换为 Domain Context。

例如：

```text
Glean Context
     │
     ▼
Context Adapter
     │
     ├── People
     ├── Organization
     ├── Documents
     ├── Projects
     ├── Customers
     ├── Financial Data
     └── Events
     │
     ▼
Domain Context
```

要求：

> Domain Product 不应该直接依赖 Glean 内部数据结构。

必须通过 abstraction layer / adapter 访问。

---

# 13. Domain Ontology

设计 Domain Ontology 层。

例如：

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

- ontology 与 Glean 解耦
- ontology 可以独立版本化
- ontology 可以迁移到其他 Enterprise Context Provider
- ontology 是本产品的重要 IP

---

# 14. Domain Agent

定义：

```text
Domain Agent
```

与 Glean Generic Agent 的区别。

例如：

```text
Generic Agent
    ↓
Can search / reason / execute

Domain Agent
    ↓
Understands domain ontology
    ↓
Uses domain reasoning
    ↓
Uses domain playbook
    ↓
Uses domain tools
    ↓
Produces domain-specific outcome
```

必须形成：

```text
Domain Agent Specification
```

至少包含：

- Role
- Goal
- Context
- Knowledge
- Ontology
- Tools
- Workflow
- Reasoning
- Guardrails
- Evaluation
- Output
- KPI

---

# 15. Tool Architecture

设计：

```text
Domain Agent
      │
      ├── Glean Search
      ├── Glean Context
      ├── Enterprise Tool
      ├── Domain Tool
      └── External API
```

要求 Tool abstraction 与 Glean 解耦。

例如：

```text
Tool Interface

search()
get_entity()
get_metric()
create_task()
send_message()
update_crm()
generate_report()
```

具体实现可以是：

```text
Glean Tool
API
MCP
REST
Function
Database
```

---

# 16. Workflow Architecture

Domain Product 的 Workflow 不应全部写死在 Agent Prompt 中。

建立：

```text
Agent
 ↓
Workflow
 ↓
Step
 ↓
Tool
 ↓
Observation
 ↓
Decision
 ↓
Next Step
```

支持：

- sequential
- branching
- loop
- approval
- exception
- retry
- rollback
- human-in-the-loop

---

# 17. Evaluation Architecture

建立两级 Evaluation：

```text
                    Evaluation
                        │
             ┌──────────┴──────────┐
             │                     │
       Platform Evaluation    Domain Evaluation
             │                     │
        Agent Quality         Business Quality
        Retrieval             Reasoning
        Tool Success          Decision
        Runtime               Outcome
```

这是未来产品非常重要的 IP。

---

# 18. Glean Dependency Boundary

必须输出一张：

> Glean Dependency Boundary

明确哪些组件：

## Strong Dependency

例如：

```text
Enterprise Context
Permissions
Connectors
Enterprise Search
```

## Soft Dependency

例如：

```text
Agent Runtime
Workflow
Observability
Evaluation
```

## No Dependency

例如：

```text
Domain Ontology
Domain Reasoning
Domain Playbook
Domain KPI
Domain UI
Domain Evaluation
```

---

# 19. Portability Architecture

必须回答一个战略问题：

> 如果未来不使用 Glean，本产品能否迁移？

设计：

```text
                Domain Product
                      │
              Abstraction Layer
                      │
        ┌─────────────┼─────────────┐
        │             │             │
      Glean        Alternative    Open Source
        │             │             │
    Context         Context       Context
    Search          Search        Search
    Agent           Agent         Agent
```

目标不是现在就支持多个平台。

目标是：

> 架构上避免不可逆锁定。

---

# 20. 最终架构图

最终必须生成至少以下 5 张 Mermaid Architecture Diagram：

### Diagram 1
Glean Capability Architecture

### Diagram 2
Glean × Domain Product Architecture

### Diagram 3
Agent Runtime Architecture

### Diagram 4
Context / Knowledge / Ontology Architecture

### Diagram 5
Glean Dependency & Portability Architecture

要求：

- Mermaid
- 可以直接放入 Markdown
- 层次清晰
- 每个组件有明确职责
- 不得为了画图而虚构 Glean 不公开的内部组件

---

# 21. Architecture Decision Record

所有重大架构判断建立 ADR：

```text
ADR-001
Decision:
Why:
Evidence:
Alternatives:
Trade-offs:
Confidence:
```

例如：

```text
ADR-001

Decision:
Enterprise Search should be delegated to Glean.

Why:
Glean already provides enterprise-aware search and context.

Alternatives:
Build proprietary retrieval layer.

Trade-offs:
Less infrastructure control but dramatically lower duplication.

Confidence:
High
```

---

# 22. Research Evidence

所有 Glean 能力必须记录：

```text
Capability
Source URL
Source Type
Evidence
Confidence
Last Verified
```

优先：

```text
Official Glean Documentation
Official Glean Product Page
Official Glean Blog
Official Glean Developer Documentation
```

不要引用没有依据的“Glean 内部架构”。

---

# 23. 最终 Deliverables

Claude Code 完成后必须生成：

```text
/docs
    /research
        glean-capability-map.md
        glean-agent-architecture.md
        glean-context-architecture.md
        glean-governance.md
        glean-evaluation.md

    /architecture
        glean-x-product.md
        domain-product-layer.md
        context-adapter.md
        agent-runtime.md
        portability.md

    /adr
        ADR-001.md
        ADR-002.md
        ...

    /diagrams
        glean-capability.mmd
        glean-x-product.mmd
        agent-runtime.mmd
        context-ontology.mmd
        portability.mmd

    /product
        domain-product-boundary.md
        domain-agent-spec.md
        domain-tool-spec.md
        domain-evaluation.md

README.md
ARCHITECTURE_PRD.md
```

---

# 24. 不允许做的事情

第一阶段严禁：

1. 开发完整 Agent 平台
2. 开发 Glean Clone
3. 自建 Enterprise Search
4. 自建通用 RAG
5. 自建 Connector 平台
6. 先做 UI Demo
7. 先确定产品名称
8. 先写大量业务代码
9. 把 Glean 内部未知机制当成事实
10. 因为“技术上可以自己做”而重复 Glean 已经成熟的能力

---

# 25. Phase 1 的成功标准

Phase 1 完成后，我应该能够用一张图回答：

> “如果 Glean 是底座，我的产品到底是什么？”

并且能够明确指出：

```text
Glean owns:
Enterprise Context
Search
Permissions
Connectors
Agent Infrastructure
Governance
Observability

Our Product owns:
Domain Ontology
Domain Intelligence
Domain Reasoning
Domain Agents
Domain Workflows
Domain Playbooks
Domain Evaluation
Domain KPI
Domain UX
```

如果上述边界仍然模糊，则 Phase 1 不算完成。

---

# 26. Phase 2 的入口

只有 Phase 1 完成后，才进入：

> Domain Product Selection

候选方向暂不预设。

Claude Code 应根据 Phase 1 的研究结果，提出：

- 5–10 个可能的 Domain Product
- 每个产品的目标客户
- 核心工作流
- Domain IP
- Glean 依赖程度
- 技术难度
- 商业价值
- 可复制性
- 与用户现有能力的匹配度

然后再选择一个作为 MVP。

---

# 27. 最重要的产品哲学

本项目最终追求的不是：

> “用 Glean 做几个 Agent。”

而是：

> **把 Glean 变成 Enterprise AI Infrastructure，把 Domain Intelligence 变成自己的产品资产。**

因此长期架构应该趋向：

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

最终判断标准：

> **没有 Glean，你的产品仍然应该具有价值；有了 Glean，你的产品应该可以用更低成本、更快速度、更高安全性进入企业生产环境。**
