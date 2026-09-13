# Research V2 — Progress Tracker

> **Master PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md)
> **Evidence Baseline (v1)**: [`/docs/research/evidence-matrix.md`](../research/evidence-matrix.md) (C01–C25, last verified 2026-09-03)
> **Evidence Updates (v2)**: this file + `/docs/research_v2/evidence-matrix-v2.md` (正式登记在 Phase 1)
> **Last Updated**: 2026-09-13

---

## Phase Status

| Phase | 内容 | 状态 | 完成日 | Notes |
|---|---|---|---|---|
| **0** | Partner 会谈准备 | ✅ DONE | 2026-09-13 | Deliverables: [`partner-meeting-brief.md`](../partner/partner-meeting-brief.md) + [`questions-for-glean.md`](../partner/questions-for-glean.md). Evidence C26-C34 added. WebFetch/WebSearch blocked by network policy; v1 evidence still valid. |
| 1 | Evidence Collection | ⏳ PENDING | — | Awaiting user confirmation |
| 2 | Capability Map | ⏳ PENDING | — | — |
| 3 | Architecture Reconstruction | ⏳ PENDING | — | — |
| 4 | Build/Buy/Integrate/Partner | ⏳ PENDING | — | — |
| 5 | Platform Kernel Definition | ⏳ PENDING | — | — |
| 6 | Reference Applications | ⏳ PENDING | — | — |

---

## Phase 0 Deliverables

| 文件 | 路径 | 状态 |
|---|---|---|
| Partner 会谈准备稿 | [`/docs/partner/partner-meeting-brief.md`](../partner/partner-meeting-brief.md) | ✅ |
| Glean 必问清单 | [`/docs/partner/questions-for-glean.md`](../partner/questions-for-glean.md) | ✅ |

---

## Evidence Updates (C26+)

> **⚠️ BLOCKED 状态说明**: Phase 0 期间 Glean 官方页面(WebFetch/WebSearch)被网络策略屏蔽,**新增证据条目的 CONFIDENCE 标记为 STRONGLY_INFERRED**,以 v1 抓取(2026-09-03)的草稿引用为来源。Phase 1 将重抓 C01-C34 的所有原始 URL 并正式登记到 `evidence-matrix-v2.md`。

| # | Claim | Source | Source Type | Confidence | Last Verified | Notes |
|---|---|---|---|---|---|---|
| **C26** | Glean Partner Network 于 2026-08-25 公开亮相 | glean.com/blog/glean-partner-network | 官方博客 | STRONGLY_INFERRED | 2026-09-03 | Phase 0 复核 BLOCKED (网络策略) |
| **C27** | Partner Network 4 pathways: Referral / Commercial / Services & Solutions / Technology | glean.com/blog/glean-partner-network | 官方博客 | STRONGLY_INFERRED | 2026-09-03 | Phase 0 复核 BLOCKED |
| **C28** | Partner 可在 Build / Sell / Deliver / Operate / Innovate 多个方向参与 | glean.com/blog/glean-partner-network | 官方博客 | STRONGLY_INFERRED | 2026-09-03 | Phase 0 复核 BLOCKED |
| **C29** | Glean Agent Identity 于 2026 年公开,Agent 可拥有独立 scoped credentials | glean.com/blog/introducing-agent-identity | 官方博客 | STRONGLY_INFERRED | 2026-09-03 | Phase 0 复核 BLOCKED |
| **C30** | ECE v0 技术栈:PostgreSQL 16 + pgvector + OpenAI-compatible LLM;无 OpenSearch/Redis/Neo4j | `ece/docs/ADR-009-lean-stack.md` | 内部 ADR | CONFIRMED | 2026-09-04 | — |
| **C31** | ECE Permission Before Intelligence 是产品 P2 原则;E2 Unauthorized Context Exposure = 0 是 CI 一票否决门槛 | `ece/docs/ADR-004-permission-first.md` + `ece/docs/EVALUATION.md` §1 | 内部 ADR | CONFIRMED | 2026-09-04 | — |
| **C32** | ECE 领域包隔离(ADR-010):换领域包成本上限 1-2 周;`src/ece/` 引擎零领域 import | `ece/docs/ADR-010-domain-pack-isolation.md` | 内部 ADR | CONFIRMED | 2026-09-04 | — |
| **C33** | ECE ADR-006 强制 LLM Provider Independence:OpenAI-compatible 端点;支持 vLLM/Ollama 部署国产开源模型 | `ece/docs/ADR-006-llm-independence.md` | 内部 ADR | CONFIRMED | 2026-09-04 | — |
| **C34** | ECE Sprint 0 已规划 2 天工程地基;Sprint 6 末离线 demo 验收 | `ece/TASKS.md` | 内部 Task | CONFIRMED | 2026-09-04 | — |

---

## 待 Phase 1 复核证据(C03 / C11 / C24)

按 v1 证据矩阵,以下三项仍为 UNKNOWN,**会谈必问 + Phase 1 优先补齐**:

| # | Claim | Source | Confidence | 行动 |
|---|---|---|---|---|
| C03 | Enterprise Graph schema 可否自定义/API 读写 | — | UNKNOWN | Robin Q9 |
| C11 | Agent Builder workflow 细节(分支/循环/人工审批/逐步选模型) | — | UNKNOWN | Robin Q10 |
| C24 | Glean 定价模式与最低合同额 | — | UNKNOWN | Robin Q11 |

---

## STOP Gate 进度(回答完即停,共 10 问)

| # | 问题 | 状态 |
|---|---|---|
| 1 | Glean 的核心架构是什么? | ⏳ 待 Phase 3 |
| 2 | Enterprise Graph 到底承担什么角色? | ⏳ 待 Phase 2/3 |
| 3 | Context 是如何形成的? | ⏳ 待 Phase 2 |
| 4 | Permission 在哪里进入整个链路? | ⏳ 待 Phase 2 |
| 5 | Agent Runtime 需要哪些基础能力? | ⏳ 待 Phase 2 |
| 6 | Action / MCP / Tool 是如何进入 Agent 的? | ⏳ 待 Phase 2 |
| 7 | Governance / Evaluation 在哪里? | ⏳ 待 Phase 2 |
| 8 | Glean 哪些能力是它真正的壁垒? | ⏳ 待 Phase 4 |
| 9 | 我们自己的 Platform Kernel 最少需要什么? | ⏳ 待 Phase 5 |
| 10 | 第一版 Demo 应该证明什么? | ⏳ 待 Phase 5/6 |

---

## Phase 1 启动条件

**用户确认 Phase 0 完成后,按以下顺序启动 Phase 1**:

1. 用户回复"OK 进入 Phase 1"或类似指令
2. 我开始执行 Phase 1: Evidence Collection
3. Phase 1 DoD:
   - 种子 URL 全量抓取(RESEARCH_PRD_V2 §5 清单)
   - 复核 C01-C34 原始来源
   - 新增证据从 C35 起编号
   - 产出 `docs/research_v2/evidence-matrix-v2.md`(含 C01-C34 复核结论列)
   - 所有 URL 注明抓取日期
4. Phase 1 完成后停下汇报 → 等用户确认 → 进入 Phase 2

---

## 治理规则(贯穿所有 Phase)

1. **每 Phase 完成后停下汇报**,不擅自进入下一 Phase
2. **每条结论带证据**: Claim / Source / Evidence / Confidence / Last Verified
3. **禁止猜测 Glean 内部技术实现**;无证据标 UNKNOWN
4. **架构描述分两类标注**: 官方明确描述 vs 公开资料推导
5. **v1 文档不修改不删除**(`/docs/research/`、`/docs/architecture/`、`/docs/product/` 下文件)
6. **不写产品代码**,只产出文档 + ADR
7. **不操作 `ece/` 子目录**(独立仓库,ECE v0 由 `ece/CLAUDE.md` 与 `ece/TASKS.md` 另行推进)
8. **ADR 回写** 写入 `/docs/adr/`(沿 ADR-002 编号追加,**注意与 `ece/docs/adr/` 是两套编号,不要混淆**)
