# M03 — Search / Retrieval Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M03
> **Linked Q**: Q1 / Q2 / Q3

## 1. 研究问题

1. 检索管线各阶段能力(Query Understanding / Entity Linking / 4 路召回 / Ranking / Permission Filtering / Context Assembly)
2. 多路召回机制(Keyword / Semantic / Graph / Structured)
3. Ranking 算法精确细节(已知 partial,精确算法 UNKNOWN)
4. Permission filtering 的执行位置(检索前 vs 检索后)
5. 我们应自建 Search 还是 Integrate Glean?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C04 | Search 100+ 源 ranked、permission-aware | developers.glean.com 首页 | CONFIRMED |
| C06 | 权限随行检索(过滤在检索过程) | glean.com/connectors FAQ | CONFIRMED |
| C17 | Agent Toolkit 提供 search / employee_search 工具 | developers.glean.com 首页 | CONFIRMED |
| C18 | Agents "reason over the knowledge graph, not just a prompt window" | developers.glean.com 首页 | CONFIRMED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Keyword Search | ✓ (C04) | | |
| Semantic / Vector Search | ✓ (C04 + 营销级声明) | | |
| Hybrid (Keyword + Semantic) | ✓ (C04 营销级) | | |
| Entity-aware 检索 | | △ (C18 推断) | |
| Graph traversal | ✓ (C18) | | |
| Permission-aware ranking | ✓ (C04, C06) | | |
| 精确 Ranking 算法 | | | ✗ |
| 4 路召回管线顺序 | | △ (C04 + C18 推导) | |
| Personalized ranking(per-user) | ✓ (C02 - Personal Graph) | | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Search Engine(横向) | **不重建**(Integrate via Glean) | C04 + 横向基础设施铁律(ADR-009) |
| Keyword 检索(FTS) | **Postgres FTS 自建** | 业务量级(E3 评测集 < 5×10⁵ chunks),ADR-009 触发条件不满足 |
| Vector Search | **pgvector 自建** | 默认 bge-small-zh-v1.5(512d),ECE EMBED_PROVIDER 切换 |
| Entity Linking | **自建**(高 IP) | Glean 这块模糊(C23 空白) |
| 4 路召回融合 | **自建** | ECE Query Planner 核心抽象,ARCHITECTURE §4 |
| Personalized Ranking | **不在 v0 范围** | 复杂度高,v0 actingUser 写死 |

### 4.2 检索管线(ECE 自建)

```text
Query/Spec → Query Planner
   ├─ Keyword(FTS)   → doc_chunks.tsv (simple + bigram 兜底)
   ├─ Vector         → doc_chunks.embedding (pgvector cosine, top-k 后过滤)
   ├─ Structured     → entities.attributes JSONB + 业务数据 SQL
   └─ Relationship   → relationships 多跳 SQL
        ↓ Entity Linking(命中文本 → canonical entity)
        ↓ Permission Filter(统一收口于 Permission Engine)
        ↓ Merge & Rank → Context Assembly
```

(摘自 `ece/docs/ARCHITECTURE.md` §4)

### 4.3 IP 价值

**中**。Search 本身是横向基础设施;差异化在 Entity Linking + 4 路融合 + Permission Filter 顺序。

### 4.4 UNKNOWN 转 Robin 会谈必问

- 精确 Ranking 算法(已知未知)
- Entity-aware 检索细节(C18 未展开)
- Personalized ranking 实现方式

## 5. References

- `docs/research/glean-capability-map.md` §3.2
- `RESEARCH_PRD_V2.md` §6 M03
- `ece/docs/ARCHITECTURE.md` §4
- `ece/docs/ADR-009-lean-stack.md`
- `ece/docs/EVALUATION.md` E3 (检索评测)
