可以，而且我建议**把原来的 Research PRD 暂时“升版”，而不是继续让 Claude Code 按旧 PRD 往下跑**。

我刚看了你之前的 `RESEARCH_PRD.md`、`CLAUDE.md` 和已有 `recommended-mvp.md`。其中已经有很好的研究框架，但它有一个现在已经明显过时的前提：

> **原来的研究目标，是“Glean → Domain Product”。**

而我们现在的目标已经变成：

> **Glean → Reverse Engineering → Enterprise AI Platform Kernel → 再决定哪些自己做、哪些借助 Glean。**

你原来的 PRD 其实已经要求先做 Capability Matrix、Architecture Boundary、Evidence Matrix，并且明确禁止把未知的 Glean 内部实现当事实。  
所以**不用推倒重来**，而是把 Research Phase 升级成真正的 **Glean Architecture Research v2**。

---

# 一、先改变研究问题

原来的核心问题：

> Glean 做什么？我们做什么？

现在应该升级成 **5 个问题**：

### Q1. Glean 到底是什么？

不是产品功能列表，而是：

> **Glean 的 Enterprise AI Platform 是由哪些能力层组成的？**

---

### Q2. 这些能力之间是什么关系？

比如：

```text
Connectors
     ↓
Index / Knowledge
     ↓
Enterprise Graph
     ↓
Search / Retrieval
     ↓
Context
     ↓
Assistant / Agent
     ↓
Tools / Actions
```

我们要搞清楚：

**这是官方明确描述的架构，还是我们根据公开资料推导出来的架构？**

这个区别非常重要。

---

### Q3. Glean 的真正技术壁垒在哪里？

不是问：

> Glean 有什么功能？

而是问：

> **如果我今天重新做 Glean，最难复制的是什么？**

例如：

- Connector ecosystem
    
- Permission synchronization
    
- Entity resolution
    
- Enterprise Graph
    
- Search / ranking
    
- Context assembly
    
- Agent runtime
    
- Governance
    
- Evaluation
    
- Agent identity
    
- Memory
    

这些东西的技术含量完全不同。

---

### Q4. 哪些是 Glean 的规模优势，而不是 MVP 必需品？

这是我们现在最需要搞清楚的问题。

例如 Glean 有大量 connectors，但我们第一版绝对没必要复制。

Glean 官方现在甚至进一步把 Enterprise Graph + Personal Graph 作为 Search、Assistant、Agents 的共同 context foundation。([Glean](https://www.glean.com/ai-agent-builder?utm_source=chatgpt.com "AI Agent Builder – Create No-Code Agents for Enterprise Work | Glean"))

所以我们要区分：

```text
必须有
核心壁垒
规模优势
成熟度优势
商业生态优势
暂时没必要
```

---

### Q5. 如果不用 Glean，我们自己最应该做哪一层？

这才是最终问题。

最终不是得到：

> “Glean 很牛。”

而是：

> **“如果明天 Glean 不允许我们使用，我们仍然可以独立构建 Enterprise AI Platform 的哪些核心部分？”**

---

# 二、Research v2 我建议分成 8 个模块

我会把原来的 7 层研究稍微重新组织。

```text
01 Data / Connector Layer
02 Enterprise Context Layer
03 Search / Retrieval Layer
04 Security / Permission Layer
05 Agent Runtime Layer
06 Action / Tool Layer
07 Governance / Evaluation Layer
08 Platform / Developer Layer
```

然后增加一个非常重要的：

```text
09 Glean Business / Partner Boundary
```

因为现在你马上要和 Robin 谈 Partner。

---

# 三、Module 1：Data / Connector

先研究：

```text
Enterprise Sources
       ↓
Connector
       ↓
Ingestion
       ↓
Normalization
       ↓
Index
       ↓
Permission
```

重点不是统计“Glean 有多少 connector”。

而是搞清楚：

### Connector 到底负责什么？

例如：

- authentication
    
- crawling
    
- incremental sync
    
- metadata
    
- document extraction
    
- ACL
    
- user/group mapping
    
- deletion
    
- freshness
    
- structured data
    

Glean 自己也明确把“连接企业数据、近实时更新、chunk、embedding、ranking、security”作为 enterprise context 的基础工作。([Glean](https://www.glean.com/blog/live-fall-25-main?utm_source=chatgpt.com "Accelerating the journey to the superintelligent enterprise: New Enterprise Graph, Third-generation Assistant, and Agent superpowers in Glean"))

### 最终输出

```text
glean-data-architecture.md
```

里面不要写：

> Glean 内部使用 Kafka / Elasticsearch / Neo4j……

除非有证据。

只能写：

> Confirmed / Strongly inferred / Unknown

你原来的 Evidence System 已经明确规定这一点，这个原则应该保留。

---

# 四、Module 2：Enterprise Context —— 这是整个研究的核心

我认为这一部分应该成为 **Research v2 的中心**。

因为 Glean 现在越来越明确地把自己定义为：

> **Context Layer**

2025 年 Glean 已经明确把 Enterprise Graph 描述成把企业数据转换成 context 的基础，并让 Search、Assistant、Agents 使用同一企业上下文。([Glean](https://www.glean.com/blog/live-fall-25-main?utm_source=chatgpt.com "Accelerating the journey to the superintelligent enterprise: New Enterprise Graph, Third-generation Assistant, and Agent superpowers in Glean"))

2026 年 independent agents 又进一步建立在这个 context layer 上。([Glean](https://www.glean.com/blog/introducing-independent-agents?utm_source=chatgpt.com "Glean independent agents: AI coworkers for the enterprise"))

所以我们要把：

```text
Enterprise Context
```

拆开研究：

### Entity

- Person
    
- Organization
    
- Team
    
- Document
    
- Customer
    
- Supplier
    
- Project
    
- Ticket
    
- Product
    
- etc.
    

### Relationship

```text
Person → belongs_to → Team
Person → works_on → Project
Project → has_document → Document
Customer → has_activity → Opportunity
```

### Semantic understanding

### Enterprise Graph

### Personal Graph

### Context assembly

### Temporal context

### Permissions

---

## 最终要回答一个问题：

> **Glean 的 Enterprise Graph 到底是不是“Knowledge Graph”？**

还是：

> Knowledge Graph + Search Index + Entity System + Permission + Context Assembly

如果是后者，那么我们的 Enterprise Context Engine 思路就有了非常明确的技术基础。

---

# 五、Module 3：Search / Retrieval

这里不要再简单研究：

> Glean 支持 keyword + semantic search。

太浅。

应该画出：

```text
User Query
    ↓
Query Understanding
    ↓
Intent / Entity
    ↓
Candidate Retrieval
    ├── Keyword
    ├── Semantic
    ├── Graph
    └── Structured
    ↓
Ranking
    ↓
Permission Filtering
    ↓
Context Assembly
    ↓
Answer / Agent
```

然后逐项判断：

|能力|Confirmed|Inferred|Unknown|
|---|--:|--:|--:|
|Keyword|✓|||
|Semantic|✓|||
|Hybrid|✓|||
|Entity-aware||✓||
|Graph retrieval|✓|||
|Personalized ranking|✓|||
|Permission-aware|✓|||
|Context assembly||✓||
|Exact ranking algorithm|||✓|

这样才能真正研究架构。

---

# 六、Module 4：Permission / Security

**这一层的重要性甚至可能超过 Search。**

因为 Enterprise AI 与普通 RAG 最大的差别之一就是：

> **谁可以看到什么？**

我们需要研究：

```text
Identity
   ↓
User / Group / Role
   ↓
Source ACL
   ↓
Document ACL
   ↓
Entity ACL
   ↓
Search
   ↓
Context
   ↓
Agent
   ↓
Action
```

特别研究：

### 1. Search permission

### 2. Agent permission

### 3. Tool permission

### 4. Action authorization

### 5. Agent identity

这里有一个非常新的变化。

Glean 在 2026 年已经推出 Agent Identity：Agent 可以拥有自己的 scoped credentials，而不是简单继承运行它的用户权限。([Glean](https://www.glean.com/blog/introducing-agent-identity?utm_source=chatgpt.com "Agent Identity for Autonomous Enterprise AI Agents | Glean"))

这意味着我们之前的架构研究如果只停留在：

> User → Permission → Agent

已经不够了。

现在应该研究：

```text
Human Identity
       │
       ▼
User Agent
       │
       │
       └──────► Independent Agent Identity
                         │
                         ▼
                  Scoped Credentials
                         │
                         ▼
                    Enterprise Tools
```

**这是 Research v2 必须新增的研究点。**

---

# 七、Module 5：Agent Runtime

这里是第二个核心。

不要只研究 Agent Builder UI。

我们真正要反推：

```text
Agent Definition
       ↓
Trigger
       ↓
Context
       ↓
Planning
       ↓
Execution
       ↓
Tool
       ↓
Observation
       ↓
Reasoning
       ↓
Loop / Branch
       ↓
Verification
       ↓
Action
```

Glean 现在已经支持：

- conversational / visual agent building
    
- branching
    
- looping
    
- scheduled triggers
    
- version control
    
- per-step model selection
    
- Agent2Agent interoperability
    
- agent evals
    
- agent governance
    

这些已经不是简单的“Agent Builder”了，而是一个完整的 **Agent Runtime + Development Environment + Governance Layer**。([Glean](https://www.glean.com/blog/glean-agents-go-2026?utm_source=chatgpt.com "Glean Agents can now work independently, build faster, and stay governed at scale"))

所以这里要重点回答：

> **Glean Agent 到底是 Workflow Engine + LLM Runtime，还是更复杂的 Agent Operating Environment？**

---

# 八、Module 6：Tools / Actions

这一部分以前我们的研究其实不够深。

要区分：

```text
READ
Search
Query
Retrieve
Analyze
        ↓
WRITE
Create
Update
Send
Approve
Execute
```

并研究：

### Tool

### MCP

### API

### Action

### Human approval

### Preview

### Execute

### Rollback / emergency stop

尤其是：

> **Agent 如何从“知道”变成“做”？**

这实际上是 Glean 从 Search → Answer → Action 的关键。

---

# 九、Module 7：Governance + Evaluation

这是我们应该特别关注的地方。

因为 Glean 最近的发展方向已经非常明显：

> **Agent 越来越 autonomous → Governance 越来越重要。**

2026 年 8 月 Glean 新增的 Agent scanning、governance policies、skills scanning、agent evals 都说明它正在把治理和 evaluation 做成平台基础设施。([Glean](https://www.glean.com/blog/glean-agents-go-2026?utm_source=chatgpt.com "Glean Agents can now work independently, build faster, and stay governed at scale"))

所以研究：

```text
Agent Registry
       ↓
Permission
       ↓
Policy
       ↓
Evaluation
       ↓
Approval
       ↓
Deployment
       ↓
Monitoring
       ↓
Audit
       ↓
Rollback
```

---

# 十、Module 8：Platform / Developer Layer

这部分要研究：

- Agent Builder
    
- API
    
- SDK
    
- MCP
    
- Agent Toolkit
    
- Git
    
- Claude Code
    
- Cursor
    
- A2A
    
- external agents
    

这里有一个**非常重要的新信息**：

Glean 现在已经支持在 Claude Code、Cursor 等开发工具里构建 Agent，并通过 Git 同步；同时支持 A2A interoperability。([Glean](https://www.glean.com/blog/glean-agents-go-2026?utm_source=chatgpt.com "Glean Agents can now work independently, build faster, and stay governed at scale"))

这意味着：

> **Glean 并没有把 Agent Builder 限制成自己的封闭低代码平台。**

这对我们自己的架构影响很大。

我们未来自己的 Platform Kernel 也不应该设计成：

> “所有东西必须在我们的 UI 里面构建。”

而应该：

```text
              Agent Developer
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Claude Code   Cursor      Web UI
        │           │           │
        └───────────┼───────────┘
                    ↓
              Agent Definition
                    ↓
               Runtime API
                    ↓
             Enterprise Context
```

这个方向与你一直在使用 Claude Code / Cursor 的工作方式也非常契合。

---

# 十一、最后增加一个 Module 9：Partner Boundary

这是因为现在你马上要和 Robin 通话。

研究：

> **Glean 希望 Partner 在哪里创造价值？**

官方刚发布的 Partner Network 已经明确：

```text
Build
Sell
Deliver
Operate
Innovate
```

并且明确提到：

- Agent Building
    
- Custom Connectors
    
- Embedded Experiences
    

这些 Partner competencies。([Glean](https://www.glean.com/blog/glean-partner-network?utm_source=chatgpt.com "Introducing the Glean Partner Network | Glean"))

所以我们需要反向研究：

```text
                    GLEAN
 ┌────────────────────────────────────┐
 │ Enterprise Context                 │
 │ Search                             │
 │ Permissions                        │
 │ Connectors                         │
 │ Agent Runtime                      │
 │ Governance                         │
 └──────────────────┬─────────────────┘
                    │
              Partner API
                    │
 ┌──────────────────▼─────────────────┐
 │              PARTNER               │
 │ Domain Solution                    │
 │ Custom Agent                       │
 │ Custom Connector                   │
 │ Integration                        │
 │ Industry Workflow                  │
 │ Deployment                         │
 │ Managed Service                    │
 └────────────────────────────────────┘
```

这将直接帮助你回答 Robin：

> **“我到底应该成为哪一种 Partner？”**

---

# 十二、然后才做真正的 Capability Matrix

我建议把你原来的 Matrix 升级成下面这样：

|Capability|Glean Native|API/SDK|Partner Extension|我们需要自建|IP价值|MVP|
|---|---|---|---|---|---|---|
|Connectors|✓|✓|✓|△|中|3个|
|Enterprise Search|✓|✓||×|低|×|
|Enterprise Graph|✓|✓||△|高|✓|
|Entity Resolution|✓/？|？|？|✓|**高**|✓|
|Permissions|✓|✓||△|**极高**|✓|
|Context Assembly|✓/？|✓/？||✓|**极高**|✓|
|Agent Runtime|✓|✓|✓|△|高|✓|
|Agent Builder|✓|✓|✓|×|中|×|
|MCP|✓|✓|✓|✓|中|✓|
|Actions|✓|✓|✓|✓|高|✓|
|Agent Identity|✓|？|？|later|高|×|
|Governance|✓|✓|✓|△|高|基础|
|Evaluation|✓|？|？|**✓**|**极高**|✓|
|Domain Ontology|||✓|**✓**|**极高**|✓|
|Domain Reasoning|||✓|**✓**|**极高**|✓|

这里最重要的不是“填表”。

而是最后产生：

> **Build / Buy / Integrate / Partner**

四种决策。

---

# 十三、最终我们要得到一张真正有用的图

我现在建议把旧的：

> Glean × Domain Product

暂时放到后面。

先做：

```text
                Enterprise Applications
                         │
                    Domain Agents
                         │
                  Agent Runtime
                         │
              ┌──────────┴──────────┐
              │                     │
          Context API            Actions
              │                     │
       Enterprise Context      Tool / MCP
              │
     ┌────────┼─────────┐
     │        │         │
   Search   Graph   Permission
     │        │         │
     └────────┼─────────┘
              │
        Enterprise Data
              │
       Connectors / APIs
```

然后对每一层标：

```text
G = Glean
O = Our Product
P = Partner / Integration
? = Unknown
```

这张图完成以后，**我们才真正知道自己应该做什么。**

---

# 十四、而且现在有一个很大的变化

你之前的 Research PRD 最终目标是：

> 找一个 Domain Product。

现在我建议把最终目标改成：

> **找到 Enterprise AI Platform Kernel 的最小不可替代集合。**

即：

```text
Glean Research
       ↓
Capability Map
       ↓
Architecture Reconstruction
       ↓
Build / Buy / Integrate Matrix
       ↓
Platform Kernel
       ↓
Reference Applications
       ↓
Demo
       ↓
Customer Validation
```

而不是：

```text
Glean Research
       ↓
Procurement Agent
```

---

# 十五、具体怎么让 Claude Code 做

我建议**不要直接让 Claude Code“重新研究 Glean”**。

而是给它一个新的：

### `RESEARCH_PRD_V2.md`

并要求它严格完成：

```text
PHASE 1
Evidence Collection
        ↓
PHASE 2
Capability Map
        ↓
PHASE 3
Architecture Reconstruction
        ↓
PHASE 4
Build / Buy / Integrate
        ↓
PHASE 5
Platform Kernel Definition
        ↓
PHASE 6
Reference Applications
```

每一个结论必须：

```text
Claim
Source
Evidence
Confidence
Last Verified
```

而且明确：

> **不要猜 Glean 内部技术实现。**

你之前 `CLAUDE.md` 已经把这个原则写得很好了。

---

# 十六、我建议现在不要碰原来的 EvidenceIQ

这个结论也很明确。

你现在的 `recommended-mvp.md` 已经把 EvidenceIQ 选成推荐 MVP，而且理由是 Customer Access、WTP、Domain IP 等。

但这个决策是建立在**旧问题定义**上的。

现在我们已经确定：

> **平台本身才是我们真正要验证的战略方向。**

所以：

**EvidenceIQ 不删除，但降级为历史候选。**

采购 Agent 也是一样。

都作为：

> Reference Application Candidates

而不是：

> Product Direction

---

# 十七、Research v2 的停止条件

这一点尤其重要。

研究不是无限进行。

我们必须在最终能够回答下面 **10 个问题**时 STOP：

1. **Glean 的核心架构是什么？**
    
2. **Enterprise Graph 到底承担什么角色？**
    
3. **Context 是如何形成的？**
    
4. **Permission 在哪里进入整个链路？**
    
5. **Agent Runtime 需要哪些基础能力？**
    
6. **Action / MCP / Tool 是如何进入 Agent 的？**
    
7. **Governance / Evaluation 在哪里？**
    
8. **Glean 哪些能力是它真正的壁垒？**
    
9. **我们自己的 Platform Kernel 最少需要什么？**
    
10. **第一版 Demo 应该证明什么？**
    

回答完：

> **STOP RESEARCH → ARCHITECTURE → BUILD**

不要再继续写 50 篇研究文档。

---

## 我认为现在最合理的下一步

**不是我继续给你讲理论，也不是马上写代码。**

而是我可以直接基于你刚才检索出来的旧 `RESEARCH_PRD.md` 和 `CLAUDE.md`，结合 **2026 年 9 月 Glean 最新能力**，给你重新设计一份：

> **`RESEARCH_PRD_V2.md — Glean Architecture Reverse Engineering & Enterprise AI Platform Kernel`**

它可以直接丢给 Claude Code 执行，里面我会把：

- 9 个 Research Modules
    
- 每个模块的具体研究问题
    
- 官方资料优先级
    
- Evidence Matrix
    
- Capability Matrix
    
- Architecture Reconstruction 方法
    
- Build / Buy / Integrate / Partner 判断框架
    
- ADR
    
- 最终 Mermaid 图
    
- STOP Gate
    
- 最终输出文件结构
    

全部写进去。

**这样你现有 `/docs` 不用推倒重来，而是从旧版 Research → V2 Research 升级。**这才是我认为目前最稳妥的推进方式。