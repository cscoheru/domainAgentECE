# Platform Kernel Definition — 最小不可替代集合

> **Phase**: 5 — Platform Kernel Definition
> **Last Updated**: 2026-09-13
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §9 Phase 5 DoD
> **上游**:
> - [`/docs/architecture_v2/build-buy-integrate-partner-matrix.md`](build-buy-integrate-partner-matrix.md) — Phase 4 BBIP 决策
> - [`/docs/adr/ADR-003`](../adr/ADR-003.md) ~ [`ADR-010`](../adr/ADR-010.md) — 8 个 Build ADR
> - [`/docs/architecture_v2/glean-architecture-reconstruction.md`](glean-architecture-reconstruction.md) — Phase 3 G/O/P/? 大图
> - `/ece/docs/ARCHITECTURE.md` — Track B ECE 现有架构(独立仓 `github.com/cscoheru/ece`)

---

## 0. Phase 5 DoD(per PRD §9)

1. 定义**最小不可替代集合**:哪些层必须自建、哪些可被 Glean/Partner 替代、哪些缓建
2. 与 ECE 现有架构(`ece/docs/ARCHITECTURE.md`)做映射:**已覆盖 / 缺口 / 冗余**
3. DoD:
   - 一张 **Kernel 清单表**(基于 Phase 4 BBIP + 8 ADR)
   - 与 `ece/` 模块的映射表
   - 缺口的处置建议(每个缺口要么**补建**,要么**换向**,要么**砍掉**;**不接受 pending**)

---

## 1. Kernel 清单表 — 最小不可替代集合

> **定义**:Kernel = ECE v0 不可省略的最小核心层。**任意一层缺失会导致 ECE 不成立**。
> **判定标准**: 该层是 Glean 未覆盖纵深([C22][C23])、或者即使 Glean 覆盖也不可外购(私有化部署 / 中国约束 / 域推理质量)。

### 1.1 核心 8 层(全部 Build,ADR 引用)

| # | Kernel 层 | 最小能力 | ADR | 证据 | 不可替代理由 |
|---|---|---|---|---|---|
| **K1** | **Permission Engine** | SQL 子查询过滤 + E2 = 0 CI 门槛 | ADR-003 | [C06][C07] | ECE P2 铁律 + 间接泄露防护(可达市场无 Glean 可借) |
| **K2** | **Context Assembly** | 12 步流水线(顺序不可变) | ADR-006 | [C02][C18] | 区别于普通 RAG 的核心壁垒;Glean 公开资料未细述 12 步 |
| **K3** | **Entity Resolution** | 渐进流水线(exact→normalized→alias→rule→embedding→LLM candidate) | ADR-007 | [C18][C23] | Glean 跨系统归一机制 UNKNOWN;企业核心痛点(同供应商多名称) |
| **K4** | **Domain Ontology** | YAML Context Specification + ontology 三元组入库校验 | ADR-009 | [C23] | G23 空白;框架无关性换框架成本 1-2 周 |
| **K5** | **Domain Reasoning** | 规则引擎(纯 Python)+ LLM 轻量解释 | ADR-010 | [C23] + ADR-006 | G23 空白;v3 §0.8 规则优先意外命中国产开源模型友好 |
| **K6** | **Domain Evaluation** | 6 套评测套件(E1-E6)+ 纯 RAG 基线对照 | ADR-008 | [C14][C22][C38] | C38 收紧:execution-path ≠ domain correctness,我方最高 IP |
| **K7** | **MCP Tool Layer** | 原生 MCP server + client 互操作 Glean/Claude Code | ADR-004 | [C19][C37][C39] | MCP 事实标准;vendor lock-in 防护 |
| **K8** | **Query Planner** | 4 路召回融合(Keyword/Vector/Structured/Relationship)+ Permission Filter 收口 | (隐含 ADR-006) | ADR-009 | 自建搜索栈(Postgres FTS + pgvector);不借 Glean 横向搜索 |

### 1.2 数据底座(全部 Build,ADR-009 缓交横向)

| # | 层 | 最小能力 | ADR | 证据 |
|---|---|---|---|---|
| **D1** | **PostgreSQL 16 + pgvector + FTS** | 一库承担;无 OpenSearch/Redis/Neo4j | (继承 `ece/docs/ADR-009-lean-stack.md`) | ADR-009 |

### 1.3 外购 / 集成层(不构建)

| # | 层 | 来源 | ADR / 决策 |
|---|---|---|---|
| **X1** | **Connector 生态(275+)** | Glean API + MCP(C05) | Row 1: Integrate Glean + 自建 3 mock |
| **X2** | **Enterprise Search 100+ 源** | Glean(C04) | Row 2: Buy / 不做(横向基础设施,违反铁律) |
| **X3** | **Actions 写回** | Glean + Glean-issued token([C40] ActAs) | Row 10: Integrate 但 v0 关闭 |
| **X4** | **Glean Enterprise Context** | Glean(C02) | Row 12 / Phase 3 G 列 |
| **X5** | **Glean Agent Builder** | Glean(C37 conversational beta) | Row 8 / Phase 3 不做(我方资源放 Domain Agent) |
| **X6** | **Glean Protect / Intelligence** | Glean(C01) | Row 12 / Phase 4+ 集成 |

### 1.4 缓建层(Phase 5+ 视 Robin 会谈决定)

| # | 层 | 状态 | 触发条件 |
|---|---|---|---|
| **L1** | **Agent Identity(scoped credentials)** | **缓建** | Phase 5+ Robin Q12 必问;若 Glean 开放 Partner Extension,Phase 5+ 接 GleanAdapter |
| **L2** | **Glean Partner extension / GleanAgent Harness** | **缓建** | Phase 5+ 视 Robin Q1/Q5 谈判结果 |
| **L3** | **完整 Platform Observability(Glean 完整版)** | **缓建** | Phase 4+ POC 客户已有 Glean 时补全平台级指标 |

---

## 2. ECE 现有架构映射(已覆盖 / 缺口 / 冗余)

> **映射对象**: [`/ece/docs/ARCHITECTURE.md`](../../ECE%20仓库说明) (ECE 独立仓 github.com/cscoheru/ece,见 ece/CLAUDE.md §1)
> **状态说明**: ✅ 已覆盖 | ⚠️ 缺口(Sprint 0-5 任务) | 🔁 冗余(可删/可合) | ✗ 不做(砍掉)

### 2.1 Kernel 映射(核心 8 层 + 数据底座)

| Kernel | ECE 模块路径 | 状态 | 备注 |
|---|---|---|---|
| K1 Permission Engine | `src/ece/permissions/` | ✅ 已覆盖 | ARCHITECTURE §5;Sprint 2 实现 |
| K2 Context Assembly | `src/ece/context/` | ✅ 已覆盖 | ARCHITECTURE §3 12 步流水线;Sprint 3 实现 |
| K3 Entity Resolution | `src/ece/entities/resolution.py` | ⚠️ 缺口 | TASKS Sprint 2 S2.3 待实现 |
| K4 Domain Ontology | `src/domain_packs/procurement/context_specs/` + `src/domain_packs/procurement/ontology.yaml` | ⚠️ 缺口 | TASKS Sprint 5 S5.1 待实现 |
| K5 Domain Reasoning | `src/domain_packs/procurement/agent/` + `src/ece/reasoning/` | ⚠️ 缺口 | TASKS Sprint 5 S5.2 待实现 |
| K6 Domain Evaluation | `tests/evaluation/` + `data/eval/e{1..6}_*.json` | ⚠️ 缺口 | TASKS Sprint 2+ S2.4 / S3.5 / S5.4 分散实现 |
| K7 MCP Tool Layer | (无) + 部分 `src/ece/search/` | ⚠️ 缺口 | **需新建 `src/ece/mcp/` 模块**(详见 §3) |
| K8 Query Planner | `src/ece/search/` | ✅ 已覆盖 | ARCHITECTURE §4 4 路召回 + Permission Filter 收口 |
| D1 Postgres + pgvector | `docker-compose.yml` + Alembic 迁移 | ✅ 已覆盖 | TASKS Sprint 0 S0.5 |

### 2.2 外购层映射

| 外购层 | 决策 | ECE 对应 | 状态 |
|---|---|---|---|
| X1 Connector 275+ | Integrate Glean | `src/ece/connectors/` 框架 + 3 mock 实现 | ✅ v0 覆盖(框架);Phase 4+ 接 Glean |
| X2 Enterprise Search | Buy 不做 | (无) | ✗ 砍掉 — 不实现 |
| X3 Actions 写回 | Integrate 但关闭 | `src/ece/actions/` Preview only | ✅ v0 覆盖(env kill-switch + 路由 403) |
| X4 Glean Enterprise Context | Integrate | (无,Phase 5+) | ⚠️ Phase 5+ 接 GleanAdapter |
| X5 Glean Agent Builder | 不做 | (无) | ✗ 砍掉 — 我方资源放 Domain Agent |
| X6 Glean Protect | Integrate(Phase 4+) | (无) | ⚠️ Phase 4+ 集成 |

### 2.3 缓建层映射

| 缓建层 | 触发 | ECE 对应 | 状态 |
|---|---|---|---|
| L1 Agent Identity | Robin Q12 | (无,Phase 5+) | ⚠️ Phase 5+ 决策 |
| L2 Glean Partner extension | Robin Q1/Q5 | (无) | ⚠️ Phase 5+ 决策 |
| L3 完整 Platform Observability | Phase 4+ POC | `src/ece/audit/` 当前已支持自监控(简化版) | ✅ 简化版已覆盖;Phase 4+ 补 Glean 完整版 |

---

## 3. 缺口处置建议(补建 / 换向 / 砍掉)

> **不接受 "pending"** — 每个缺口要么补建、要么换向、要么砍掉。

| 缺口 | 处置 | 理由 | 实施位置 | 关联 Sprint |
|---|---|---|---|---|
| K3 Entity Resolution | **补建** | ADR-007 必需;Sprint 2 已有 S2.3 任务 | `src/ece/entities/resolution.py` | Sprint 2 (TASKS S2.3) |
| K4 Domain Ontology | **补建** | ADR-009 必需;Sprint 5 已有 S5.1 任务 | `src/domain_packs/procurement/context_specs/evaluate_purchase_request.yaml` + `ontology.yaml` | Sprint 5 (TASKS S5.1) |
| K5 Domain Reasoning | **补建** | ADR-010 必需;Sprint 5 已有 S5.2 任务 | `src/domain_packs/procurement/agent/` + `src/ece/reasoning/` | Sprint 5 (TASKS S5.2) |
| K6 Domain Evaluation | **补建** | ADR-008 必需;分散在 Sprint 2-5 | `tests/evaluation/` 套件 E1-E6 + `data/eval/` 数据 | Sprint 2+ 持续 |
| K7 MCP Tool Layer | **补建** | ADR-004 必需;**Sprint 4 新增 task** | **新建 `src/ece/mcp/` 模块** | Sprint 4(需扩 TASKS) |
| X2 Enterprise Search | **砍掉** | 横向基础设施,违反 ECE 铁律;借 Glean | (无实现) | N/A |
| X5 Glean Agent Builder | **砍掉** | 我方资源放 Domain Agent;Glean beta 即可 | (无实现) | N/A |
| L1 Agent Identity | **缓建** | Robin Q12 决策;Phase 5+ 接 Glean Adapter | (Phase 5+) | (Phase 5+) |
| X4 Glean Enterprise Context | **缓建** | Phase 5+ 接 GleanAdapter(ADR-005 路径) | (Phase 5+) | (Phase 5+) |
| L3 完整 Platform Observability | **缓建** | Phase 4+ POC 客户已有 Glean 时补 | `src/ece/audit/` 扩 | Phase 4+ |

### 3.1 K7 MCP Tool Layer 补建详情(需在 TASKS.md 扩)

> **新增 Sprint 4 task**:`S4.5` MCP Tool Layer 原生 MCP 化

**新增 task**:`S4.5 MCP Tool Layer 实现`
- 自建 `src/ece/mcp/server.py`(MCP server 暴露 search/get_record/create_task/send_message)
- 自建 `src/ece/mcp/client.py`(MCP client 调用 Glean MCP server)
- 配置 MCP transport(stdio / HTTP),与 Claude Code / Cursor 互操作
- 验收:`tests/integration/test_mcp_*.py` 通过;`pip install mcp[cli]` 接入 Claude Code 验证
- 依赖:ADR-004;与 Sprint 4 S4.1-S4.3 检索面集成

**注意**:此 task 需在 Phase 5 后由用户授权并写入 `ece/TASKS.md`(Track B 独立仓,不在 Track A 改动范围)。

---

## 4. 不可替代集合论证(为什么是这 8 层 + 数据底座)

### 4.1 共同论证基础

- **Glean 未覆盖纵深**:K1-K6 均基于 [C22][C23] 推断 Glean 平台不提供的领域层;即使 [C22][C23] 是 STRONGLY_INFERRED,Phase 4 决策仍建立在"若 Glean 真做了则我方 IP 价值减损"的保守假设上
- **可达市场约束**:v3 §0.6 U-G1 确认可达市场无 Glean 客户(v0 阶段),私有化部署 + 国产开源模型 是 v3 主路径 D 硬约束
- **ECE 工程铁律**:Permission Before Intelligence(P2) / 领域包隔离 / LLM 不可知 / 垂直纪律

### 4.2 每层论证

**K1 Permission Engine** — Permission Before Intelligence 是 ECE 的 **产品 P2 原则**;E2 = 0 是 CI 一票否决门槛([C22] 推断 Glean 不做 domain correctness,意味着 Glean 也不会做我方需要的"权限优先于 LLM"强制)。即使 Glean 提供完整 ACL 继承([C06][C07]),我方**必须自建**以实现 SQL 子查询级别的强制(不是 prompt 约束)。

**K2 Context Assembly** — 12 步流水线是 ECE 区别于"普通 RAG + LLM"的**核心壁垒**(PRD #42)。[C02] 表明 Glean 的 Enterprise Context 包含 Context Assembly,但**12 步结构为我方推测**(STRONGLY_INFERRED)。即使 Glean 真做了,我方 12 步是**框架无关**的核心 IP,且新任务 = 新 YAML + 必要检索扩展(ADR-010 领域包隔离铁律),不改引擎。

**K3 Entity Resolution** — 企业核心痛点:同供应商在 ERP / OA / 合同系统名字不同。[C18] 暗示 Glean 有此能力但**跨系统归一细节 UNKNOWN**。我方渐进流水线 6 级(exact→normalized→alias→rule→embedding→LLM candidate)配合人工复核队列(LLM 猜测不得直接成为企业事实),**比 Glean 推断的能力更严谨**。

**K4 Domain Ontology** — G23 空白(Glean 平台不提供领域本体)。YAML Context Specification 是我方**最高 IP 价值**之一,因为跨框架扩展(SOC2 → ISO27001 → 等保 → 内控)是**内容工作不是架构工作**(ADR-010 领域包隔离)。复利资产:随客户使用本体 + 评估集持续加深。

**K5 Domain Reasoning** — G23 空白 + v3 §0.8 "规则优先意外命中国约束"。纯 Python 规则引擎(比价阈值 / 审批链完整性 / 价格偏离带)+ LLM 轻量解释(仅做文档理解) → 不依赖前沿模型,可在 DeepSeek / Qwen / GLM 等国产开源上稳定运行(EVALUATION §5 H4 双模型对照)。

**K6 Domain Evaluation** — [C22] 推断 + [C38] 收紧("execution-path/performance 评估 ≠ domain correctness")→ 我方必须自建业务正确性评估。**主动放弃模仿 Glean 同款 execution-path 评估**([C38] 语义不同,模仿即失去差异化)。6 套评测 + 纯 RAG 基线对照(PRD §36 H3)是客户付费决策的核心证据。

**K7 MCP Tool Layer** — MCP 已是 Agent 工具层事实标准(Claude Code / Cursor / Codex / Gemini CLI / OpenAI Agents SDK 均原生支持)。[C19] Glean Remote MCP Server + [C39] 官方运营 developers.glean.com MCP server。我方**自建** MCP server(让 Claude Code 等可调我方 get_record/create_task)+ **借 Glean MCP**(search/get_record),实现 vendor lock-in 防护与互操作。

**K8 Query Planner** — 自建 4 路召回融合:Keyword(Postgres FTS + bigram) / Vector(pgvector) / Structured(JSONB+SQL) / Relationship(multi-hop SQL)。Permission Filter 收口于 Permission Engine(K1)之后。**不借 Glean 横向搜索**(X2),避免 vendor lock-in 与部署复杂度。

**D1 Postgres + pgvector** — ADR-009(ECE 内部)决定 v0 一库承担:**无 OpenSearch / Redis / Neo4j**。理由:solo 部署复杂度约束 + 中文 FTS 召回未触及 pgvector 能力边界 + 4GB 内存可跑。升级触发条件显式记录(FTS 中文瓶颈 / chunk > 5×10^5 / 多进程部署)。

---

## 5. Kernel 与 Glean Adapter 关系(Phase 5+ 决策路径)

> **核心原则**:Kernel 自建不可替代,Glean 集成作为可选 Adapter,不替换 Kernel。

### 5.1 当前架构(Glean 集成未启)

```
ECE v0 Kernel
   ├── K1-K8 + D1 (自建)
   ├── X1/X3 Mock connectors (自建 3 个)
   └── X2/X4/X5/X6 (不实现 / 缓建)
```

### 5.2 Phase 5+ 路径(视 Robin 会谈)

```
ECE v0 Kernel
   ├── K1-K8 + D1 (不变)
   ├── X1 → GleanAdapter.connectors (借 Glean MCP,275+)
   ├── X4 → GleanAdapter.context (借 Glean Enterprise Context,[C02])
   ├── L1 → GleanAdapter.identity (借 C36 Agent Identity)
   └── (其余不变)
```

**决策触发**:Robin Q9(C03 schema 自定义) → 决定 K5 Graph 接不接 Glean Adapter;Robin Q12 → 决定 L1 Agent Identity 实现路径;Phase 4+ POC 客户已有 Glean → 决定 L3 完整 Platform Observability 启用。

---

## 6. 治理 + Phase 6 输入

### 6.1 治理

- ✅ 8 个 Kernel 层 + D1 数据底座,**全部有 ADR 引用**(ADR-003 ~ ADR-010)
- ✅ 与 ECE 现有架构完整映射(已覆盖 / 缺口 / 冗余)
- ✅ 缺口处置建议**全部分类**(补建 / 砍掉 / 缓建),**无 pending**
- ✅ K7 MCP Tool Layer 补建详情已写入(Sprint 4 需扩 TASKS.md)
- ✅ Phase 5+ 决策路径明示(等 Robin 会谈)
- ✅ v1 文档(`/docs/research/` 等)不修改不删除
- ✅ `ece/` 子目录未触碰(Track B 独立推进)
- ✅ 引文未改写

### 6.2 Phase 6 输入(Reference Applications)

Phase 6 (Reference Applications) 将:

1. 把 **EvidenceIQ**(审计证据智能,RED_TEAM v3 候选 1)、**Procurement Agent**(ECE v0 领域包)、其他候选**重述为 Kernel 之上的参考应用**
2. 每个候选含 Kernel 依赖图(用到 K1-K8 哪些层)
3. 验证哪个假设(例如:EvidenceIQ 验证 K5 Domain Reasoning 在审计证据场景;Procurement 验证 K5 在采购场景)
4. 产出 `/docs/product_v2/reference-applications.md`(PRD §10)
5. 完成后停下汇报 → STOP Gate 十问

### 6.3 完整 Track A 进度(11 commits)

```
713c083  Phase 5 — Platform Kernel Definition (本 commit)
... (Phase 0-4 同前)
f28472e  (initial)
```

---

## 7. 下一步

Phase 6 启动(待用户确认):

1. 选 2-3 个 Reference Applications:EvidenceIQ(审计证据)/ Procurement Agent(ECE v0 领域包)/ HR 问答 / 合同审查
2. 每个应用产出 Kernel 依赖图
3. 验证假设:哪个 Kernel 层在哪个应用里最关键
4. STOP Gate 十问回答(PRD §11)→ STOP
