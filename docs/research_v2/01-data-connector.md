# M01 — Data / Connector Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M01
> **Linked Q**: Q1 (Glean 是什么) / Q4 (规模优势 vs MVP 必需)

## 1. 研究问题

1. Connector 职责边界(auth / crawling / incremental sync / metadata / extraction / ACL / user-group mapping / deletion / freshness)
2. 数据归一化流程(ingestion → normalization → index)
3. 自定义 Connector 路径(Indexing SDK / OpenAPI / MCP)
4. Connector 平台是否值得自建?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C04 | Search 覆盖 100+ 连接源 | developers.glean.com 首页 | CONFIRMED |
| C05 | 开箱连接器 275+ | glean.com/connectors FAQ | CONFIRMED |
| C06 | 连接器继承并强制源系统权限 | glean.com/connectors FAQ | CONFIRMED |
| C07 | 数据与权限实时同步 | glean.com/connectors FAQ | CONFIRMED |
| C08 | Actions 跨系统写回 | glean.com/connectors FAQ | CONFIRMED |
| C09 | 自定义 Connector 用 Indexing SDK;自定义 Action 用 OpenAPI;MCP 接入 | glean.com/connectors | CONFIRMED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| 连接器数量(275+) | ✓ (C05) | | |
| 权限继承与强制 | ✓ (C06) | | |
| 实时同步 | ✓ (C07) | | |
| Actions 写回 | ✓ (C08) | | |
| 自定义 Connector | ✓ (C09) | | |
| MCP 集成 | ✓ (C09, C19) | | |
| 内部数据栈(Kafka/ES/...) | | | ✗ 禁止猜测 |
| 数据新鲜度 SLA | | | ✗ |
| Document extraction(表格/图片) | | △ | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Connector Platform | **不重建**(Integrate via Glean/MCP) | 275+ 是规模优势(C05),MVP 不复制 |
| 权限继承语义 | **借用 Glean** | C06 是 Glean 工程化护城河 |
| 写回能力 | **Integrate via MCP/Actions** | C08/C19 提供标准化通道 |
| 自定义 Connector 框架 | **自建** | ECE 核心抽象,ADR-007 |

### 4.2 ECE v0 Connector 范围

按 `ece/TASKS.md` Sprint 1:CSV / JSON / 本地文档(分块 + tsv + embedding);**不连真实 ERP/OA**。

### 4.3 IP 价值

**低**。Connector ecosystem 是规模优势,非核心壁垒。

### 4.4 UNKNOWN 转 Robin 会谈必问

- Connector 内部数据流架构(Kafka / ES) — **禁止猜测**(PRD §4)
- 数据新鲜度 SLA
- Document extraction 高级能力(表格/图片 OCR)

## 5. References

- `docs/research/glean-capability-map.md` §3.3
- `RESEARCH_PRD_V2.md` §6 M01
- `ece/docs/ARCHITECTURE.md` §1
- `ece/TASKS.md` Sprint 1
