# Track B Strategic Spec — ECE v0 Engineering Execution

> **Phase**: Track B 启动(POST-Track A STOP Gate)
> **Last Updated**: 2026-09-13
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §16(双轨架构)+ ROOT `CLAUDE.md` §1(Track B 独立)
> **上游**:
> - [`/docs/architecture_v2/platform-kernel-definition.md`](../architecture_v2/platform-kernel-definition.md) — K1-K8 Kernel + D1 + X1-X6 + L1-L3
> - [`/docs/architecture_v2/build-buy-integrate-partner-matrix.md`](../architecture_v2/build-buy-integrate-partner-matrix.md) — Phase 4 BBIP
> - [`/docs/adr/ADR-003`](../adr/ADR-003.md) ~ [`ADR-010`](../adr/ADR-010.md) — 8 个 Build 决策 ADR
> - [`/docs/product_v2/reference-applications.md`](../product_v2/reference-applications.md) — 3 Reference Applications + STOP Gate
> **下游消费者**: ECE v0 仓 `github.com/cscoheru/ece`(由独立 session 实施)

---

## 0. 背景

**Track A 已 STOP**(per PRD §11 + §13.3,commit `49604b0`)。Robin Glean Partner 会谈路径取消(用户决定)。**Track B 全速推进**:ECE v0 工程实施。

**关键约束(本仓外)**:
- ECE v0 代码必须在独立仓 `github.com/cscoheru/ece` 写
- 本仓(`domainAgentECE`)只能产出战略 spec + ADR + 决策审计
- Track A 与 Track B 互不阻塞(per ROOT CLAUDE.md §16)

**本目录产出的战略 spec 是给 ECE session 的输入文档**,不替代 ECE CLAUDE.md / PRD / TASKS / ARCHITECTURE 的内容。

---

## 1. 文件结构

```
docs/track_b/
├── README.md              # 本文件 — 概述 + 状态 + 入口
├── execution-plan.md      # Sprint 0-6 × Phase 5 K1-K8 映射 + K7 S4.5 详细 spec
└── track-a-decisions.md   # Phase 4 ADR → ECE TASKS 审计链 + 证据 + 铁律检查
```

---

## 2. Track B 状态(2026-09-13)

| 项 | 状态 |
|---|---|
| **Track A STOP Gate** | ✅ 通过(commit 49604b0,42 条证据,15 个文档) |
| **Robin Glean Partner 路径** | ❌ 取消(用户决定) |
| **ECE 仓 git 状态** | ECE 仓独立 git 仓(`github.com/cscoheru/ece`),初始 commit 仅;**Sprint 0 任务尚未开始** |
| **Phase 5 §3.1 K7 缺口** | ⚠️ Sprint 4 需新增 S4.5 MCP Tool Layer(本 spec 给出详细设计) |
| **Track B 启动条件** | ✅ Track A 完成 + 用户授权 + ECE 仓可访问 |

---

## 3. Track B 战略输入(从 Track A)

### 3.1 关键决策摘要

| 决策 | 来源 | 对 ECE v0 的影响 |
|---|---|---|
| **8 个 Build 决策**(ADR-003 ~ ADR-010) | Phase 4 | ECE v0 必须实现:K1-K8 + D1 Postgres |
| **Glean 路径降级为非阻塞期权** | Phase 0+2.5+3 | ECE v0 不接 Glean Adapter(v0);Phase 5+ 视情况 |
| **Agent Identity 缓建**(C36 beta) | Phase 2.5 + Phase 3 | ECE v0 actingUser 写死;Phase 5+ 吸收 Glean Agent Identity 概念 |
| **Actions 写回 v0 关闭** | ADR-003 + ADR-004 | ECE v0 `/actions/execute` 必须 403(env kill-switch) |
| **Postgres-only + OpenAI-compatible LLM** | Phase 3 + ADR-009(ECE 内部) | ECE v0 不引入 OpenSearch/Redis/Neo4j;支持 vLLM/Ollama |
| **MCP Tool Layer(NEW S4.5)** | Phase 5 §3.1 | ECE v0 Sprint 4 新增任务 |

### 3.2 必守 ECE 工程铁律(来自 ece/CLAUDE.md §2)

| 铁律 | Track A 验证 |
|---|---|
| **Permission Before Intelligence**(P2) | ADR-003 + Phase 6 §2 EvidenceIQ H2 验证 |
| **禁止 Demo 绕过核心抽象** | Phase 6 §2 EvidenceIQ 演示依赖完整 4 件套 |
| **垂直纪律**(不引入横向基础设施) | Phase 4 X1-X6 外购决策 + ADR-009 |
| **领域包隔离** | ADR-010(根) + ece/ADR-010(独立) |
| **LLM 不可知** | ADR-006(根)+ ece/ADR-006 + Phase 6 §3 Procurement H1 |

---

## 4. Track B 执行阶段(高层)

| Sprint | 主题 | 主要产出 | Track A Kernel 覆盖 |
|---|---|---|---|
| 0 | 工程地基 | uv + docker compose + CI + alembic + scripts + 合成数据集 | (setup) |
| 1 | 数据层 | Connector Interface + Entities/Relationships schema + Entity/Relationship API | K7 partial + K8 partial |
| 2 | 身份 + 权限 + 消歧 | Identity + Permission Engine + Entity Resolution + E2 安全套件 | K1 + K3 |
| 3 | Context 核心 | Context Spec + Assembly Pipeline + /context + E3/E4/E5 | K2 |
| 4 | 检索面 + **MCP** | FTS + vector + structured + relation + **NEW S4.5 MCP Tool Layer** | K8 + K7 |
| 5 | Procurement Agent + 评测 | 领域规则 + Agent + E6 + Actions Preview | K4 + K5 + K6 partial |
| 6 | Debugger + 演示 + 定稿 | Audit/Debugger + Demo script + eval report + mini audit exercise + 私有化验收 | K6 + 演示 + 部署验证 |

**详见 `execution-plan.md`**。

---

## 5. Track A 决策 → Track B 工程映射(审计链)

详见 `track-a-decisions.md`。

每个 Phase 4 ADR(003-010)→ 对应 ECE TASKS 任务 → 证据(C01-C42)→ ECE 铁律符合性。**这是 Track A → Track B 的"可追溯 + 可质疑"桥梁**。

---

## 6. 风险与建议

### 6.1 风险

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| Phase 5 §3.1 K7 MCP 缺口被忽略,Sprint 4 不实现 | 中 | MCP 互操作缺失,失去与 Claude Code/Cursor 集成能力 | 本 spec + ADR-004 强制要求 |
| ECE TASKS.md 与 Phase 5 决策不一致 | 低 | Track A 研究结论未传导 | `track-a-decisions.md` 提供审计链 |
| Track A 重新迭代(网络恢复后新证据) | 低 | Track B 决策需修订 | Phase 5 §3 路径已设计,Robin Q9 决定 |
| solo 产能不足(Sprint 0-6 共 ~30 天) | 高 | 进度拖延 | 严格垂直纪律(砍掉横向诱惑);Phase 4 BBIP 锁定范围 |
| 国产开源模型实测掉档(E6) | 中 | Domain Reasoning 验证失败 | 架构调整(规则承担更多);不杀方向 |

### 6.2 关键建议(给 Track B session)

1. **优先 Sprint 0 + Sprint 2**——Sprint 0 是基础设施(uv + docker + alembic + CI),Sprint 2 是 K1/K3(权限 + 实体消歧)的实现,**没有它们后续 Sprint 都跑不起来**。
2. **ECE TASKS.md S4.5 MCP Tool Layer 新增任务**——本 spec 给出详细设计,直接写入 TASKS。
3. **每 Sprint 完成后跑对应 E 套件**——EVALUATION.md §1 设计了 E1-E6 与 Sprint 的映射(S2 跑 E1/E2,S3 跑 E3-E5,S5 跑 E6),不要跳过。
4. **CI 必须含 ruff + mypy + pytest + import-linter**——`ece/CLAUDE.md §6` 已规定;import-linter 强制 ece/ 与 domain_packs/ 隔离。
5. **私有化部署验收(S6.5)**是 v3 主路径 D 的**技术关门**——必须真实跑"断网 + 本地 Ollama + 国产模型 + Demo 数据集"全流程。

---

## 7. 下一步

**Track B 启动流程**:
1. 在另一会话打开 `github.com/cscoheru/ece` 仓(独立 git 仓,初始 commit 状态)
2. 读取本目录 3 个 spec 文档作为输入
3. 按 `ece/CLAUDE.md` + `ece/TASKS.md` + 本 spec 启动 Sprint 0
4. 关键新增任务:**Sprint 4 S4.5 MCP Tool Layer**(本 spec §execution-plan.md 给出)
5. 每 Sprint 完成后 commit + 汇报(本仓不再过问 Track B 工程 commit)

**本仓(`domainAgentECE`)的角色**:
- 战略 spec 提供方
- Track A 历史基线(Stop Gate 证据)
- Robin 会谈文档(虽然取消,但保留作为期权)
- 任何后续 Track A 维度修订(新证据出现时)→ ADR 增量

---

## 8. 引用(Track A 已 commit 全部资产)

| 资产 | Commit | 用途 |
|---|---|---|
| Track A STOP Gate | `49604b0` | STOP Gate §11 十问 + 13 commits 总览 |
| Phase 5 Kernel Definition | `421dc06` | K1-K8 不可替代集合 |
| Phase 4 BBIP + 8 ADRs | `713c083` | 8 Build 决策审计链 |
| Phase 3 G/O/P/? 大图 | `03b096e` | Glean 分层架构 + Platform Kernel |
| Phase 2.5 R1-R7 修复 | `b527574` | Cline 红队审查后证据基线 |
| Phase 0 Partner 会谈稿 | `c1dd32b` | (备用,Glean 路径降级后) |
