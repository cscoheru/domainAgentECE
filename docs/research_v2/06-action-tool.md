# M06 — Action / Tool Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M06
> **Linked Q**: Q1 / Q2 / Q5

## 1. 研究问题

1. Agent Toolkit 内置工具清单与边界
2. Remote MCP Server 集成模式(C19)
3. OpenAPI 自定义 Action 的能力
4. 写回安全模型(权限 / 审批 / 审计)
5. 我们应自建 Tool/MCP 层还是 Integrate Glean?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C08 | Actions 跨系统写回 | glean.com/connectors FAQ | CONFIRMED |
| C09 | 自定义 Action 用 OpenAPI spec | glean.com/connectors | CONFIRMED |
| C17 | Agent Toolkit 内置 search / employee_search | developers.glean.com 首页 | CONFIRMED |
| C19 | Remote MCP Server tenant 级、权限感知、OAuth(DCR)、可 MDM 部署 | developers.glean.com/guides/mcp | CONFIRMED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Agent Toolkit 内置工具 | ✓ (C17 - search, employee_search) | | |
| OpenAPI 自定义 Action | ✓ (C09) | | |
| MCP 集成 | ✓ (C09, C19) | | |
| 权限感知 Tool 调用 | ✓ (C19 - MCP tenant 级) | | |
| OAuth(DCR)认证 | ✓ (C19) | | |
| MDM 部署 | ✓ (C19) | | |
| Tool 调用审批流(HITL) | | △ 推断(Glean Trust 文档未确认) | |
| 写回审计/回滚 | | △ (Verification API 暗示) | |
| Actions 失败重试/幂等性 | | △ | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Tool 接口规范 | **原生 MCP 化**(自建) | MCP 是事实标准(v3 + PRD §6 M06);与 Glean/Claude Code 互操作 |
| 内置工具集 | **最小集**(自建 get_record / create_task / send_message) | ECE Context Adapter 抽象,`ARCHITECTURE.md` §8 |
| Actions 写回 | **关闭**(v0 强制 403,ADR-004) | env kill-switch + 路由硬编码双保险 |
| OpenAPI 自定义 Action | **不在 v0**(Phase 4 决策) | 复杂度高,MVP 不需要 |
| 审计/trace | **自建**(context_items + audit endpoint) | ECE 核心能力 |

### 4.2 关键判断 — MCP 是事实标准

**MCP 已成工具层事实标准**(C19 + 2026 行业趋势)。ECE 的 Tool 层**必须原生 MCP 化**,这样:
- 可以与 Glean、Claude Code、任何 MCP-compatible runtime 互操作
- 我们自建的 get_record/create_task 也能被 Claude Code 等直接调用
- 减少自定义集成工作

### 4.3 IP 价值

**中**。Tool 接口本身无壁垒;差异化在 **Tool 编排 + 权限感知**。

### 4.4 UNKNOWN 转 Robin 会谈必问

- Tool 调用审批流(HITL)在 Glean 内的具体实现
- Actions 写回失败回滚机制
- Partner-built Tools 是否享有与原生 Tools 同等的 MCP 暴露

## 5. References

- `docs/research/glean-capability-map.md` §3.5
- `RESEARCH_PRD_V2.md` §6 M06
- `ece/docs/ARCHITECTURE.md` §1 (Actions 块)
- `ece/docs/API.md` §6
- `ece/docs/ADR-004-permission-first.md`
