# M04 — Permission / Security Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M04
> **Linked Q**: Q1 / Q2 / Q3 (真正壁垒)

## 1. 研究问题

1. Permission 模型(user/group/role/department × entity/document × allow/deny)
2. Permission filtering 执行时机(检索前 vs 检索后 vs LLM 输出后)
3. **Agent Identity** 与 scoped credentials(C29 — 2026 新概念)
4. Tool / Action 权限边界
5. Multi-tenant 隔离机制
6. 这是 Glean 的真正壁垒吗?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C06 | 连接器继承并强制源系统权限 | glean.com/connectors FAQ | CONFIRMED |
| C07 | 数据与权限实时同步 | glean.com/connectors FAQ | CONFIRMED |
| C16 | Client API 覆盖 Search/Chat/Documents/Entities/Tools/Verification/Insights/Governance | developers.glean.com 导航 | CONFIRMED |
| C19 | Remote MCP Server tenant 级、权限感知、OAuth(DCR)、可 MDM 部署 | developers.glean.com/guides/mcp | CONFIRMED |
| C29 | Glean Agent Identity 于 2026 年公开,Agent 可拥有独立 scoped credentials | glean.com/blog/introducing-agent-identity | STRONGLY_INFERRED (BLOCKED) |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| 源系统权限继承 | ✓ (C06) | | |
| 权限实时同步 | ✓ (C07) | | |
| Permission filtering 位置 | ✓ (C06 - 检索过程实时) | | |
| 跨层级 ACL(User/Role/Dept/Classification) | ✓ (C16 - Verification/Governance API) | | |
| Agent Identity(scoped credentials) | ✓ (C29 STRONGLY_INFERRED) | | |
| Tenant 级隔离(MCP) | ✓ (C19) | | |
| OAuth DCR 支持 | ✓ (C19) | | |
| MDM 部署支持 | ✓ (C19) | | |
| 写回权限(Action authorization) | ✓ (C16 - Verification API) | | |
| 间接泄露防护(Agent 推断拒绝内容) | | △ 推断 | ✗(C22 暗示无业务正确性评估) |
| 完整 RBAC 框架细节 | | △ | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| **Permission 过滤执行位置** | **检索前**(Permission Before Intelligence) | ADR-004 铁律;与 Glean 同模式(C06);E2=0 CI 门槛 |
| ACL 数据模型 | **自建**(acl_entries 表) | ECE 核心抽象,`DATA_MODEL.md` §3 |
| Classification 默认矩阵 | **自建**(seed 固化) | Glean 不公开语义 |
| Agent Identity(scoped credentials) | **Phase 5 后考虑** | C29 是 2026 新概念,ECE v0 actingUser 写死 |
| 间接泄露防护 | **自建评测 + 规则**(E2 专项) | C22 暗示 Glean 无业务正确性评估,我方最高 IP |
| 写回权限 | **关闭**(ADR-004 + env kill-switch) | /actions/execute v0 强制关闭 |

### 4.2 关键判断 — 这是 Glean 的真正壁垒吗?

**YES + NO**。

- **壁垒的"工程化形态"**(C06+C07)可被技术复制;
- **壁垒的"信任位置"**(v3 Red Team 七年爬梯)无法被时间复制;

对我方:
- **工程层**: Permission Before Intelligence + E2=0 评审集 = 与 Glean 同模式,可实现;
- **信任层**: 我方需要走"数据主权"路径(私有化部署)替代 Glean 式信任阶梯。

### 4.3 IP 价值

**极高**。Permission Engineering + 间接泄露评测 + Agent Identity 适配,是企业 AI 的最大痛点。

### 4.4 UNKNOWN 转 Robin 会谈必问

- 完整 RBAC 框架细节
- Agent Identity 在 Partner-built Agent 上的权限模型
- 写回权限(Agent→企业系统)的具体审计机制
- 间接泄露防护的官方态度

## 5. References

- `docs/research/glean-context-architecture.md` §2
- `RESEARCH_PRD_V2.md` §6 M04
- `ece/docs/ADR-004-permission-first.md`
- `ece/docs/DATA_MODEL.md` §3
- `ece/docs/ARCHITECTURE.md` §5
- `ece/docs/EVALUATION.md` E2
