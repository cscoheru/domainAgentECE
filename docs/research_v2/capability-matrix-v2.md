# Capability Matrix v2 — Build / Buy / Integrate / Partner 决策框架

> **Phase**: 2 — Capability Map
> **Last Updated**: 2026-09-13
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §7
> **Last Verified**: v1 baseline 2026-09-03; live re-verify deferred pending network access
> **Baseline**: [`evidence-matrix-v2.md`](evidence-matrix-v2.md) (C01-C34)

---

## 0. 矩阵使用说明

每行的"我们需要自建"列 + "IP 价值"列联合产生 **Build / Buy / Integrate / Partner** 四向决策:

- **Build(自建)**: 横向非优势 + 极高 IP 价值 + 不重建 Glean 已有能力
- **Buy(采购)**: 横向规模优势 + 不在 MVP 范围
- **Integrate(集成)**: 通过 API/SDK/MCP 借用 Glean 能力
- **Partner(借 Partner 通道)**: Glean 官方鼓励 Partner 做长尾领域(C21)

**v0 baseline 注解**: 2026-09-13 网络抓取全数 BLOCKED,所有 CONFIRMED 项维持 v1 (2026-09-03) 验证日期。新证据从 C35 起编号 — 暂无。

---

## 1. 能力矩阵(8 列 × 16 能力)

| # | Capability | Glean Native | API / SDK | Partner Extension | 我们需要自建 | IP 价值 | MVP 范围 | 决策 |
|---|---|---|---|---|---|---|---|---|
| 1 | **Connector Ecosystem** (275+) | ✓ (C05) | ✓ Indexing SDK (C09) | ✓ Custom | △ 框架 + 3-5 mock | 低 | 3 (CSV/JSON/docs) | **Integrate**(Glean) + 自建框架 |
| 2 | **Enterprise Search** | ✓ (C04) | ✓ Client/Platform API (C16) | | × | 低 | × | **Buy/Integrate**(不做横向) |
| 3 | **Enterprise Graph** | ✓ (C02) | ✓ 部分(C03 UNKNOWN) | | △ | 高 | ✓ 简化版 | **Build + Integrate**(schema 自定义必问) |
| 4 | **Entity Resolution** (跨系统) | ✓/? (C18 暗示) | ? (C03 UNKNOWN) | ? (C23 空白) | ✓ | **高** | ✓ exact→normalized→alias→rule | **Build**(核心 IP) |
| 5 | **Permissions / ACL 继承** | ✓ (C06) | ✓ Verification API (C16) | | △ 客户端实现 | **极高** | ✓ Permission Before Intelligence | **Build + Integrate** |
| 6 | **Context Assembly** | ✓/? (C02 + C18) | ? | | ✓ | **极高** | ✓ 12 步流水线 | **Build**(核心架构) |
| 7 | **Agent Runtime** | ✓ (C10) | ✓ Platform API (C15) | ✓ | △ 轻量 | 高 | ✓ Procurement Agent | **Partner/Integrate + 自建 Domain Agent** |
| 8 | **Agent Builder UI** | ✓ (C10) | ✓ | ✓ | × | 中 | × | **Partner**(不做 Builder UI) |
| 9 | **MCP Tool Layer** | ✓ (C19) | ✓ Client API (C17) | ✓ | ✓ | 中 | ✓ 原生 MCP | **Build + Integrate**(MCP 是事实标准) |
| 10 | **Actions 写回** | ✓ (C08) | ✓ OpenAPI spec (C09) | ✓ | ✓ | 高 | × (v0 关闭) | **Integrate + 关闭**(ADR-004) |
| 11 | **Agent Identity** (scoped credentials) | ✓ (C29) | ? | ? | ✗ | 高 | × | **later**(Phase 5+) |
| 12 | **Governance** (rollout/share/certify) | ✓ (C13) | ✓ Verification API (C16) | ✓ | △ | 高 | △ 基础 | **Integrate**(Phase 4+) |
| 13 | **Evaluation (Platform Observability)** | ✓ (C14) | ? | ? | ✓ 简化版 | 中 | ✓ context_requests/items | **Build**(简化版)+ 集成 Glean 完整版 |
| 14 | **Evaluation (Domain / Business Correctness)** | ✗ (C22 确认空白) | ? | ? | **✓** | **极高** | ✓ E1-E6 | **Build**(核心 IP,最高价值) |
| 15 | **Domain Ontology** (领域本体) | ✗ (C23 空白) | | ✓ | **✓** | **极高** | ✓ Procurement 控制项-证据映射 | **Build**(核心 IP) |
| 16 | **Domain Reasoning** (规则 + 推理) | ✗ (C23 空白) | | ✓ | **✓** | **极高** | ✓ 规则优先 + LLM 轻量 | **Build**(核心 IP) |

---

## 2. 决策分布统计

| 决策 | 数量 | 占比 | 说明 |
|---|---|---|---|
| **Build**(自建核心 IP) | 6 | 37.5% | Entity Resolution, Context Assembly, MCP Tool Layer, Domain Evaluation, Domain Ontology, Domain Reasoning |
| **Build + Integrate** | 2 | 12.5% | Enterprise Graph, Permissions |
| **Integrate** | 3 | 18.75% | Connector, Actions, Governance |
| **Partner / Integrate + 自建 Domain Agent** | 1 | 6.25% | Agent Runtime |
| **Integrate / Buy** | 1 | 6.25% | Enterprise Search(不做) |
| **Partner (不做)** | 1 | 6.25% | Agent Builder UI |
| **later** | 1 | 6.25% | Agent Identity |
| **不确定** | 1 | 6.25% | Evaluation (Platform Observability) - 简化版 or 集成? |

---

## 3. Glean 不覆盖的纵深(ECE 高 IP 价值区)

**最高 IP 价值 4 项**(全部 **Build**):
- **Domain Ontology**(能力 15) — Glean 无领域本体
- **Domain Reasoning**(能力 16) — Glean 无领域推理
- **Domain Evaluation**(能力 14) — C22 确认 Glean 观测停留在平台级
- **Permissions Engineering**(能力 5) — Glean 实现 + 我方叠加(中国私有化场景)

**共同特征**: 这些都是 **Glean 通用平台无法覆盖的纵深**, 是 v0 阶段最高 ROI 的自建方向。

---

## 4. ECE v0 实施映射(Sprint 0-6)

| Sprint | 关联能力 | 交付 |
|---|---|---|
| Sprint 0 | 工程地基 | uv + docker compose + alembic + CI |
| Sprint 1 | 1, 9 | Connector Interface + CSV/JSON/docs 实现;MCP 集成基础 |
| Sprint 2 | 4, 5 | Entity Resolution 流水线;Permission Engine (E1+E2 验证) |
| Sprint 3 | 6, 13 | Context Assembly 12 步;context_requests/items 审计 |
| Sprint 4 | 3, 9 | 检索面 (FTS + vector + structured + relationship) |
| Sprint 5 | 7, 15, 16 | Procurement Agent + 领域规则库 + E6 评测 |
| Sprint 6 | 11, 12, 14 | Audit/Debugger UI;E1-E6 评测汇总 |

---

## 5. Phase 3 (Architecture Reconstruction) 输入

Capability Matrix v2 是 Phase 3 输入。Phase 3 产出:
- 分层架构重建(官方 vs 推导两类标注)
- G/O/P/? 大图
- mermaid 入 `/docs/diagrams/`

**已识别 Phase 3 关键决策**:
- Build 6 项的层级边界
- Integrate 3 项的接口契约(Glean MCP / Client API)
- Partner 1 项的合作模式

---

## 6. 治理说明

本文件遵循 PRD §4 证据纪律:

- ✅ 每格挂 C 编号证据或显式标 `?`(UNKNOWN)
- ✅ 决策列每格有理由(基于 IP 价值 + ECE 工程铁律)
- ✅ 不猜测 Glean 内部实现
- ✅ v1 文档(`docs/research/`)不修改不删除
- ✅ `docs/partner/` 是 Phase 0 行动视角;本文件是研究视角

---

## 7. 下一步

- [ ] Phase 3: Architecture Reconstruction(基于本矩阵生成 G/O/P/? 大图)
- [ ] Phase 4: Build/Buy/Integrate/Partner 四向决策每个写 ADR
- [ ] Phase 5: Platform Kernel Definition(与 ECE 现有架构映射)
