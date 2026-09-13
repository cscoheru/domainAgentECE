# M08 — Platform / Developer Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M08
> **Linked Q**: Q1 / Q2 / Q5

## 1. 研究问题

1. Platform API(experimental preview, C15)当前状态:Agents / Chat / Search / Skills / Triggers 覆盖度
2. Client API 清单(C16)与官方 SDK(C20)
3. **Agent Definition API 化程度**(PRD §6 M08 重点问题)
4. Web SDK / Agent Toolkit 的 framework-agnostic 程度(C17)
5. 我们应自建 Platform 层还是 Integrate Glean?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C15 | Platform API(Agents/Chat/Search/Skills/Triggers)experimental preview | developers.glean.com 首页 | CONFIRMED |
| C16 | Client API 覆盖 Search/Chat/Documents/Entities/Tools/Verification/Insights/Governance | developers.glean.com 导航 | CONFIRMED |
| C17 | Agent Toolkit framework-agnostic(LangChain/CrewAI/OpenAI Agents SDK/Google ADK/MCP) | developers.glean.com 首页 | CONFIRMED |
| C20 | 官方 API 客户端:Python/TypeScript/Java/Go | developers.glean.com 首页 | CONFIRMED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Platform API 存在性 | ✓ (C15) | | |
| Platform API 状态(experimental) | ✓ (C15) | | |
| Client API GA 状态 | ✓ (C16 - 无 experimental 标注) | | |
| Agent Toolkit 多框架 | ✓ (C17) | | |
| MCP 集成 | ✓ (C17) | | |
| 官方 SDK 4 语言 | ✓ (C20) | | |
| Agent Definition as Code 程度 | | △ (C17 framework-agnostic 暗示部分支持) | |
| Platform API GA 时间表 | | | ✗ |
| IDE 集成(Claude Code / Cursor / Codex / Gemini CLI) | ✓ (C39 CONFIRMED,2026-09-13 — Glean 官方运营开发者文档 MCP server,支持一键 `claude mcp add`) | | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Platform API | **Integrate via Glean MCP/Client API** | 横向基础设施 |
| Agent Definition as Code | **MUST 自建**(ECE `domain_packs/<domain>/context_specs/*.yaml`) | PRD §6 M08 + ADR-010;与 Claude Code 工作方式契合 |
| SDK 多语言支持 | **不在 v0**(Python 优先) | solo 产能约束 |
| IDE 集成 | **自然继承**(Claude Code 原生支持) | 我方工作方式 |

### 4.2 关键判断 — Agent Definition as Code 的战略意义

PRD §6 M08 明确:
> Glean 没有把 Agent Builder 限制成封闭低代码平台;我们自己的 Platform Kernel 也**不应设计成"所有东西必须在我们的 UI 里构建"**

```text
              Agent Developer
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Claude Code   Cursor      Web UI
        │           │           │
        └───────────┼───────────┘
                    ↓
              Agent Definition (YAML, git-versioned)
                    ↓
                Runtime API
                    ↓
             Enterprise Context
```

(摘自 PRD §6 M08)

这与我方以 Claude Code / Cursor 为主的工作方式高度契合 —— Agent Definition 必须是版本化文件(code-first),不是锁在 UI 里的配置。

### 4.3 IP 价值

**中**。Platform API 是基础设施;差异化在 Agent Definition as Code 规范。

### 4.4 UNKNOWN 转 Robin 会谈必问

- Platform API GA 时间表(C15 / Q14)
- Agent Definition 是否可完全在 Builder UI 外管理(Q12)
- SDK 是否包括完整 Partner build 工具(测试 / sandbox)

## 5. References

- `docs/research/glean-capability-map.md` §3.5
- `RESEARCH_PRD_V2.md` §6 M08
- `ece/docs/ARCHITECTURE.md` §2.1(Context Specification 抽象)
- `ece/docs/ADR-010-domain-pack-isolation.md`
- `RESEARCH_PRD_V2.md` §6 M08 G/O/P/? 标注框架
