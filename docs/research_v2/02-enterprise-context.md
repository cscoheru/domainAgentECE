# M02 — Enterprise Context Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M02
> **Linked Q**: Q1 / Q2 (能力间关系) / Q3 (真正壁垒) / Q5 (若不用 Glean,我们该做哪层)
> **状态**: **整个研究的中心**

## 1. 研究问题

1. Glean 的 Enterprise Graph 是否 = Knowledge Graph?还是 = KG + Search Index + Entity System + Permission + Context Assembly?
2. Enterprise Graph schema 可否自定义?可否 API 读写?
3. Entity / Relationship 模型细节?
4. Personal Graph 与 Enterprise Graph 的关系?
5. Context Assembly 的时序(权限随行 vs 检索后过滤)?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C02 | Enterprise Context = Enterprise Graph + Personal Graph + System of Context | glean.com 首页导航 | CONFIRMED |
| C03 | Enterprise Graph 内部 schema(实体/关系类型)可否自定义/API 读写 | — | **UNKNOWN** |
| C04 | Search 100+ 源权限感知 | developers.glean.com 首页 | CONFIRMED |
| C06 | 权限随行检索 | glean.com/connectors FAQ | CONFIRMED |
| C18 | Agents "reason over the knowledge graph, not just a prompt window" | developers.glean.com 首页 | CONFIRMED |
| C19 | Remote MCP Server tenant 级、权限感知 | developers.glean.com/guides/mcp | CONFIRMED |
| C23 | Domain 层(领域本体/推理/评估)是 Glean 未覆盖的空白 | 推断 | STRONGLY_INFERRED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Enterprise Graph 存在性 | ✓ (C02) | | |
| Personal Graph 存在性 | ✓ (C02) | | |
| System of Context 概念 | ✓ (C02) | | |
| Agent 在图谱上推理(非仅 prompt) | ✓ (C18) | | |
| 权限随行检索 | ✓ (C06) | | |
| Entity/Relationship 类型 schema 可自定义 | | | ✗ (C03) |
| Enterprise Graph API 读写接口 | | △ 部分(Indexing API 推送) | |
| 内部图数据库选型 | | | ✗ 禁止猜测 |
| Cross-system entity resolution | | △ 推断(C18 + 检索示例) | |
| Temporal context 支持 | | △ 推断(产品页提及) | |
| Personal vs Enterprise 隔离机制 | | △ | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Enterprise Graph schema 自定义能力 | **必问 Glean**(C03 UNKNOWN) | 决定我方 Domain Ontology 能否映射进 Glean |
| 跨系统 Entity Resolution | **自建**(高 IP 价值) | G23+C23 显示这是 Glean 模糊地带,我方领域优势 |
| 领域 Ontology | **自建**(极高 IP 价值) | C23 显示 Domain 层是 Glean 空白 |
| Context Assembly 模式 | **自建** | ECE 核心抽象,ADR-001 |
| Personal Graph | **不在 v0 范围** | 复杂度高,与"企业 Context"主轴偏离 |

### 4.2 终极问题

> Glean 的 Enterprise Graph 到底是不是 "Knowledge Graph"?
> 还是 = KG + Search Index + Entity System + Permission + Context Assembly?

**答**(基于 C02 + C18 + C19 + C23 综合推断):
Glean 的 Enterprise Context **大于**传统 Knowledge Graph。它包含:
- 知识图谱(实体+关系)
- 搜索引擎(检索 + 排名)
- 权限层(跨层级 ACL 继承)
- Context Assembly(per-task 动态组装)
- 隐式 Personal Graph(per-user 个性化)

**对我方的启示**: ECE 的 "Enterprise Context Engine" 思路与 Glean 的 Enterprise Context **概念同构**,只是实现路径不同。这是 Path D(自建 Platform Kernel)的技术基础。

### 4.3 IP 价值

**极高**。跨系统 Entity Resolution + 领域 Ontology + Context Assembly 是 Glean 未充分覆盖的纵深。

### 4.4 UNKNOWN 转 Robin 会谈必问

- Enterprise Graph schema 完整自定义能力(C03 / Q9)
- Cross-system entity resolution 是否可作为 Partner Extension(C23)
- Personal Graph 与 Enterprise Graph 数据隔离机制

## 5. References

- `docs/research/glean-context-architecture.md`(v1 M02 deep dive)
- `docs/research/glean-capability-map.md` §3.1
- `RESEARCH_PRD_V2.md` §6 M02
- `ece/docs/ARCHITECTURE.md` §1-3
- `ece/docs/ADR-004-permission-first.md`
- `ece/docs/EVALUATION.md` §1 E1-E3
