# M05 — Agent Runtime Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M05
> **Linked Q**: Q1 / Q2 / Q5

## 1. 研究问题

1. Agent 完整生命周期(Planning / Tool / Loop / Branch / Verification / Action)
2. **Workflow 型 vs Reasoning 型 Agent 官方区分**(C21 暗示)
3. Agent-to-Agent(Orchestration / 任务路由) / 事件触发 / 调度
4. Memory 模型(Agent memory / User memory / Personal Graph)
5. **Independent Agents**(AI coworkers,2026 新概念)
6. Agent Harness(C25,coming soon)
7. 我们应该自建 Runtime 还是用 Glean Agent Builder?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C10 | Agent Builder reasoning-based agents + 复杂 workflow | glean.com/product/agents | CONFIRMED (营销级) |
| C11 | Agent Builder workflow 细节(分支/循环/人工审批/逐步模型选择) | — | **UNKNOWN** |
| C12 | Orchestration:事件触发、Agent 间任务路由、连接外部系统 | glean.com/product/agents | CONFIRMED |
| C13 | Agent Governance:rollout / share / certify | glean.com/product/agents | CONFIRMED |
| C17 | Agent Toolkit framework-agnostic(LangChain/CrewAI/OpenAI Agents SDK/Google ADK/MCP) | developers.glean.com 首页 | CONFIRMED |
| C18 | Agents "reason over the knowledge graph, not just a prompt window" | developers.glean.com 首页 | CONFIRMED |
| C25 | Glean Agent Harness(新产品)与 Glean Transform(coming soon) | glean.com 首页导航 | UNKNOWN |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Agent Builder 存在性 | ✓ (C10) | | |
| Reasoning-based Agent | ✓ (C10, C18) | | |
| Event Trigger / 任务路由 | ✓ (C12) | | |
| Agent Governance(rollout/share/certify) | ✓ (C13) | | |
| Framework-agnostic(外部 SDK) | ✓ (C17) | | |
| Workflow 细节(branching/looping/HITL/per-step model) | | △ (C11 部分解答 by C37: agent looping=beta, schedule agents=GA, agent version control=GA, conversational builder=beta) | branching / HITL / per-step model 仍 UNKNOWN |
| Per-step model selection | | | ✗ (C11) |
| Agent-to-Agent 标准化协议(A2A) | | △ 推断(2026 趋势) | |
| Memory 模型细节 | | △ | |
| Independent Agents(AI coworkers) | | △ 推断(产品页提到) | |
| Agent Harness(新产品) | | | ✗ (C25 coming soon) |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Agent Runtime(通用) | **Partner/Integrate**(用 Glean Agent Builder 或 MCP) | 横向基础设施,ADR-009 |
| **Domain Agent(Procurement v0)** | **自建**(ADR-007) | 领域包隔离铁律,ECE 核心 IP |
| Workflow 编排(branching/looping) | **自建轻量**(Sprint 5) | v0 范围窄,不需要完整 Agent Builder |
| Reasoning Engine | **规则优先 + LLM 轻量**(ADR-006) | 意外命中中国约束(v3 §0.8) |
| Agent Definition as Code | **MUST 自建**(PRD §6 M08) | Glean v2 趋势,我方 code-first 工作方式 |
| Memory / State 持久化 | **不在 v0 范围** | 复杂度高 |
| Independent Agents / Agent Harness | **不在 v0 范围** | C25 coming soon,等 Glean 落地 |

### 4.2 关键判断 — Workflow Agent vs Reasoning Agent

**Glean 似乎在做两件事**:
- **Workflow Agent**(C10 营销级):无代码构建复杂 workflow,普通员工可上手
- **Reasoning Agent**(C18):在图谱上推理,需要专业知识与编排

对我方启示:
- **不在 v0 做 Workflow Agent Builder**(那是 Glean 的横向规模优势)
- **做深 Domain Reasoning Agent**(领域包 + 规则优先),这是 IP 价值最高的方向

### 4.3 IP 价值

**高**(Reasoning + Domain)+ **低**(Workflow Builder)。

### 4.4 UNKNOWN 转 Robin 会谈必问

- Agent Builder workflow 完整规范(C11: branching/HITL/per-step model 仍 UNKNOWN;**agent looping=beta / agent version control=GA / schedule agents=GA / conversational builder=beta — 已由 C37 部分解答** / Q10 补)
- Agent-to-Agent 标准化协议
- Agent Harness 时间表与定位(C25 → **C41**: Harness 已入 PRODUCT 导航但无详情页;Transform 仍 Coming soon)

## 5. References

- `docs/research/glean-capability-map.md` §3.4
- `RESEARCH_PRD_V2.md` §6 M05
- `ece/docs/ARCHITECTURE.md` §8
- `ece/TASKS.md` Sprint 5
- `ece/docs/ADR-007-procurement-first-domain.md`
- `ece/docs/ADR-006-llm-independence.md`
