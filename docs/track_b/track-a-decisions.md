# Track A Decisions → Track B Engineering 审计链

> **Phase**: Track B 启动
> **Last Updated**: 2026-09-13
> **目的**: 把 Phase 4 8 个 Build 决策 ADR(ADR-003 ~ ADR-010)逐一映射到 ECE TASKS 任务,提供**可追溯 + 可质疑**的决策桥梁
> **消费者**: ECE v0 session(`github.com/cscoheru/ece`)

---

## 0. 审计链结构

每个 ADR 包含:
1. **ADR 摘要** — Track A 决策
2. **ECE TASKS 任务** — 对应 Track B 实现
3. **证据引用** — C01-C42
4. **ECE 工程铁律符合性**
5. **风险/备注** — Track B session 实施时需注意

---

## 1. ADR-003 → Permission Engine

### 1.1 ADR 摘要

**Build + Integrate(语义)**。Permission Engine 自建,实现 ACL 模型 + `PermissionScope` SQL 子查询层强制;E2 = 0 是 CI 一票否决门槛;Actions 写回 v0 关闭(双保险);Glean 语义借用(Phase 5+ 吸收 C36 Agent Identity 概念)。

### 1.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 2 | S2.1 Identity 解析(X-User-Id → person + roles + dept) | Identity 模型 |
| Sprint 2 | S2.2 Permission Engine(acl_entries + classification + 判定顺序 + PermissionScope SQL 过滤) | **核心实现** |
| Sprint 2 | S2.4 E2 安全套件 + 间接泄露用例 | **验证** |
| Sprint 4 | S4.2 Query Planner(Permission Filter 收口) | **集成** |
| Sprint 5 | S5.3 /actions/preview + /actions/execute(关闭) | 关闭 403 |
| Sprint 6 | S6.1 /audit/context/{id} | trace |

### 1.3 证据引用

| 证据 | 内容 |
|---|---|
| [C06] | "inherits and enforces source-system permissions" — 权限继承是 Glean 工程化形态 |
| [C07] | "real-time sync ... as soon as they happen" — 实时同步 |
| [C16] | Verification API — Glean 提供权限验证接口 |
| [C19] | Remote MCP Server tenant 级隔离 |
| [C36] | Agent Identity scoped credentials — Phase 5+ 借鉴 |

### 1.4 ECE 铁律符合性

- ✅ **Permission Before Intelligence**(P2):SQL 子查询层强制,不是 post-filter,不是 prompt
- ✅ **禁止 Demo 绕过核心抽象**:S6.2 Demo 必须走 /context(过 Permission),不走 raw DB

### 1.5 风险/备注

- **风险**:E2 间接泄露专项(EVALUATION §1)较新,S2.4 需新增测试用例
- **备注**:Phase 5+ 接 Glean Agent Identity 时,**不要替换** K1 自建实现,而是**叠加** Glean Identity 作为 Agent-to-System 凭证(K1 仍管用户身份)

---

## 2. ADR-004 → MCP Tool Layer

### 2.1 ADR 摘要

**Build + Integrate**。ECE Tool 层原生 MCP 化,自建 MCP server + 借 Glean MCP(Phase 4+)。

### 2.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 1 | S1.1 Connector Interface | 占位 `src/ece/mcp/` |
| **Sprint 4 NEW** | **S4.5 MCP Tool Layer** | **核心实现 — 详见 execution-plan.md §4** |

### 2.3 证据引用

| 证据 | 内容 |
|---|---|
| [C19] | Glean Remote MCP Server:tenant 级 / 权限感知 / OAuth DCR / 可 MDM 部署 |
| [C37] | Fall'25 矩阵:**remote MCP servers beta** |
| [C39] | Glean 官方运营 `developers.glean.com` MCP server,Claude Code / Cursor / Codex / Gemini CLI 一键集成(原文 `claude mcp add glean-developer-docs ...`) |

### 2.4 ECE 铁律符合性

- ✅ **LLM 不可知**:MCP 是 runtime 协议,模型无关
- ✅ **垂直纪律**:MCP 是工具层事实标准,非横向基础设施

### 2.5 风险/备注

- **真缺口**:Sprint 1-4 TASKS 无 MCP 实现,**S4.5 必须新增**
- **备注**:v0 MCP server 暴露 4 个工具(search / get_record / create_task / send_message);create_task/send_message 是 Preview 不执行(S5.3 Actions 关闭延伸)

---

## 3. ADR-005 → Enterprise Graph

### 3.1 ADR 摘要

**Build + Integrate**。ECE v0 自建简化版图谱(Postgres entities + relationships 表),Phase 5+ 视 Robin Q9(C03)决定是否接 GleanAdapter。

### 3.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 1 | S1.2 Entity/Relationship 入库 | entities + relationships + entity_revisions 三表 |
| Sprint 1 | S1.3 Entity/Relationship 只读 API | GET /entities/{id} 等 |
| Sprint 1 | S1.4 seed.py 幂等 | upsert |
| Sprint 2 | S2.3 Entity Resolution 流水线 | exact→normalized→alias→rule→embedding→LLM(ADR-007) |

### 3.3 证据引用

| 证据 | 内容 |
|---|---|
| [C02] | Enterprise Context = Enterprise Graph + Personal Graph + System of Context |
| [C03] | **UNKNOWN** — Enterprise Graph schema 可否自定义/API 读写 |
| [C18] | "reason over the knowledge graph" — Glean Agent 在图谱上推理 |

### 3.4 ECE 铁律符合性

- ✅ **领域包隔离**:图谱是引擎核心(`src/ece/entities/`),与 domain_packs 解耦
- ✅ **垂直纪律**:Postgres-only,不引入 Neo4j(ECE ADR-003 内部)

### 3.5 风险/备注

- **Phase 5+ 触发**:若 Robin Q9 确认 Glean schema 自定义 → 写 `src/ece/adapters/glean/graph_adapter.py`
- **备注**:v0 `entities` 表 + `attributes JSONB` 已能表达大多数企业对象;图遍历通过 SQL recursive query(ARCHITECTURE §7)而非 Cypher

---

## 4. ADR-006 → Context Assembly

### 4.1 ADR 摘要

**Build**。ECE 自建 12 步流水线(顺序不可变,fail-closed),Context Specification YAML 一级契约。

### 4.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 3 | S3.1 Context Spec 加载器(YAML→内存,版本化) | spec loader + registry |
| Sprint 3 | S3.2 Assembly Pipeline 12 步 | **核心实现** |
| Sprint 3 | S3.3 Provenance | context_items |
| Sprint 3 | S3.4 /context 完整实现 | API |
| Sprint 3 | S3.5 E3/E4/E5 评测 | **验证** |
| Sprint 4 | S4.4 性能基准 | seed 全量 p95 < 1.5s |
| Sprint 5 | S5.2 Procurement Agent | consume package |
| Sprint 6 | S6.4 迷你换域演练 | audit spec 走通 /context(验证 H5) |

### 4.3 证据引用

| 证据 | 内容 |
|---|---|
| [C02] | Glean Enterprise Context 是平台核心 |
| [C18] | "reason over the knowledge graph" — Agent 在 Context 上推理 |
| (推导) | 12 步结构为我方推测,Glean 官方未公开 |

### 4.4 ECE 铁律符合性

- ✅ **禁止 Demo 绕过核心抽象**:S6.2 Demo 必经 /context,不绕
- ✅ **领域包隔离**:spec 是契约,领域通过 spec 扩展不改引擎

### 4.5 风险/备注

- **风险**:12 步顺序固定,任何重构需严格 ADR
- **备注**:Context Specification YAML 是 Phase 6 EvidenceIQ / Procurement Agent 共享的契约,新领域 = 新 YAML

---

## 5. ADR-007 → Entity Resolution

### 5.1 ADR 摘要

**Build**。ECE 自建渐进流水线 6 级(exact→normalized→alias→rule→embedding→LLM candidate),LLM 猜测不得直接成为企业事实。

### 5.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 2 | S2.3 Entity Resolution 流水线 | **核心实现** |
| Sprint 6 | S6.1 /audit/context/{id} | trace 引用 |
| Sprint 6 | S6.2 Demo script | PR001 supplier 归一演示 |

### 5.3 证据引用

| 证据 | 内容 |
|---|---|
| [C18] | Glean Agent 在图谱上推理 — 隐含 Glean 有此能力 |
| [C23] | Domain 层是 Glean 未覆盖的空白 — 跨系统归一为我方纵深 |

### 5.4 ECE 铁律符合性

- ✅ **LLM 不可知**:LLM 只是流水线的最后一步(candidate),不替代规则
- ✅ **垂直纪律**:不重建 Glean 的 ER(基于其模糊机制),自建渐进流水线

### 5.5 风险/备注

- **强制规则**:`method='llm'` 一律 `status='pending'`;`confidence < 0.9` 进人工队列(ADR-007 + DATA_MODEL §1)
- **风险**:embedding 阈值 τ=0.92 需实际数据校准;v0 数据集可能不够代表性

---

## 6. ADR-008 → Domain Evaluation

### 6.1 ADR 摘要

**Build**。ECE 自建 6 套评测 + 纯 RAG baseline 对照,**永不模仿 Glean 同款 execution-path 评估**(C38 收紧:execution-path ≠ domain correctness)。

### 6.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 2 | S2.4 E2 安全套件 + 间接泄露专项 | E2 间接泄露专项 |
| Sprint 3 | S3.5 E3/E4/E5 评测 | E3 (Context Completeness ≥90%) / E4 (错连=0) / E5 (期间 ≥95%) |
| Sprint 5 | S5.4 E6 + 纯 RAG baseline | E6 (结论方向 ≥80%, evidence 真实率 100%) + baseline 对照(EVALUATION §5 H3) |
| Sprint 6 | S6.3 make eval-report | 6 套件汇总报告 |

### 6.3 证据引用

| 证据 | 内容 |
|---|---|
| [C14] | Glean 平台级指标(adoption/error/votes/ROI)— 平台级 |
| [C22] | STRONGLY_INFERRED — Glean 无业务正确性评估 |
| **[C38]** | **收紧** — Glean 官方 "evaluations" 语义指向 execution-path / performance,**≠ domain correctness** |

### 6.4 ECE 铁律符合性

- ✅ **禁止 Demo 绕过核心抽象**:EVALUATION 是核心模块(PRD §13 "没有测试的功能不算完成")
- ✅ **LLM 不可知**:E6 双模型对照证明规则优先架构在国产开源上可用

### 6.5 风险/备注

- **ECE v0 评测集规模有限**:E1 ≥50 / E2 ≥50 / E3 ≥100 / E4 ≥30 / E5 ≥30 / E6 ≥50(EVALUATION §1);v0 实测数据需 ≥ 门槛
- **关键对照**:EVALUATION §5 H3 必须做(同 E6 问题集跑纯向量 RAG baseline,证明 ECE 显著优于)

---

## 7. ADR-009 → Domain Ontology

### 7.1 ADR 摘要

**Build**。ECE 自建 YAML Context Specification,允许三元组 ontology 入库校验;跨框架扩展(SOC2 → ISO27001 → 等保)是**内容工作不是架构工作**(ADR-010 领域包隔离铁律)。

### 7.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 3 | S3.1 Context Spec 加载器(部分) | spec YAML 加载 |
| Sprint 5 | S5.1 领域规则库 + ontology | `src/domain_packs/procurement/context_specs/evaluate_purchase_request.yaml` + `ontology.yaml` |
| Sprint 6 | S6.4 迷你换域演练 | audit spec 走通 /context(验证 H5) |

### 7.3 证据引用

| 证据 | 内容 |
|---|---|
| [C23] | STRONGLY_INFERRED — Domain 层是 Glean 未覆盖的空白 |

### 7.4 ECE 铁律符合性

- ✅ **领域包隔离**(ADR-010 内部):ontology 在 `src/domain_packs/<domain>/`,`src/ece/` 不 import
- ✅ **垂直纪律**:v0 仅 12 CC 控制项(后续扩 ISO27001/等保)

### 7.5 风险/备注

- **v3 Red Team §0.7**:重做 Reference Case 中国皮肤(框架=访谈确认的 ISO/等保/个保/内控,人名/系统本土化);Sprint 6.4 之前需用户访谈确认
- **关键提醒**:**ECE v0 本体为 SOC2 12 CC**;中国本土化是 v0 之后的事;Sprint 5 实施时**直接用 SOC2 本体**,不要试图"先等访谈再决定"

---

## 8. ADR-010 → Domain Reasoning

### 8.1 ADR 摘要

**Build**。ECE 自建规则引擎(纯 Python)+ LLM 轻量解释;不依赖前沿模型,国产开源友好(v3 §0.8)。

### 8.2 ECE TASKS 任务

| Sprint | 任务 | 实现 |
|---|---|---|
| Sprint 5 | S5.1 领域规则库 | 比价阈值 / 审批链 / 价格偏离带 |
| Sprint 5 | S5.2 Procurement Agent | Rule findings 注入 prompt + structure output |

### 8.3 证据引用

| 证据 | 内容 |
|---|---|
| [C23] | Domain 层是 Glean 未覆盖的空白 |
| (ECE ADR-006 内部) | LLM Provider Independence |
| (ECE ADR-009 内部) | Lean Stack(Postgres-only) |

### 8.4 ECE 铁律符合性

- ✅ **LLM 不可知**:规则确定判断,LLM 仅做文档理解
- ✅ **禁止 Demo 绕过核心抽象**:S5.2 输出 schema 强制结构化(conclusion / reasoning / risks / recommendation / evidence / confidence)

### 8.5 风险/备注

- **Sprint 6.5 私有化验收是 K5 关键验证**:断网 + 本地 Ollama + 国产模型 + Demo 数据集全流程通过 → v3 §0.8 规则优先架构成立
- **风险**:若国产模型在充分性推理解释上掉档 → 架构调整(规则承担更多);**不杀方向**

---

## 9. 决策一致性验证(ECE 仓 vs Track A 决策)

### 9.1 ECE 仓内部 ADR 编号(独立)

ECE 仓 `ece/docs/adr/` 已有 ADR-001 ~ ADR-010(从最初 ls 看到):

| ECE ADR | 主题 | 与 Track A 根目录 ADR 对应 |
|---|---|---|
| ece/ADR-001 | Why Enterprise Context Engine | (根目录无对应 — 是 ECE 立项) |
| ece/ADR-002 | Why PostgreSQL as initial Entity/Relationship Store | (根目录无对应) |
| ece/ADR-003 | Why not Neo4j in MVP | (根目录无对应) |
| ece/ADR-004 | Permission Before Context Assembly | 根 ADR-003(同一主题,不同视角) |
| ece/ADR-005 | Context API as Agent Boundary | (根目录无对应) |
| ece/ADR-006 | LLM Provider Independence | (根目录无对应 — ECE 自己的 LLM 决策) |
| ece/ADR-007 | Procurement Context as First Domain | (根目录无对应 — ECE 自己的领域选择) |
| ece/ADR-008 | Synthetic Enterprise Dataset for MVP | (根目录无对应) |
| ece/ADR-009 | Lean Stack | (根目录无对应) |
| ece/ADR-010 | Domain Pack Isolation | 根 ADR-010(根域包隔离,ECE ADR-010 也是域包隔离,视角略不同) |

**无冲突**:ECE ADR 编号 001-010 是 ECE 自己治理的 ADR(技术决策);根目录 ADR 001-010 是 Track A 战略决策。**两套独立编号不混淆**(per PRD §13.5)。

### 9.2 关键决策交叉验证

| 决策维度 | ECE 仓(技术) | 根目录(战略) | 一致性 |
|---|---|---|---|
| 数据存储 | PostgreSQL + pgvector(ECE ADR-002/009) | D1 Postgres(根 Phase 5 §1.2) | ✅ 完全一致 |
| 权限前置 | Permission Before Intelligence(ECE ADR-004) | K1 Permission Engine(根 ADR-003) | ✅ 完全一致 |
| LLM Provider | OpenAI-compatible + 国产开源(ECE ADR-006) | LLM 不可知 + 规则优先(根 ADR-010) | ✅ 完全一致 |
| 领域包隔离 | src/domain_packs/ 与 src/ece/ 解耦(ECE ADR-010) | O Build 决策(根 ADR-009 + ADR-010) | ✅ 完全一致 |
| 不引入 Neo4j | ECE ADR-003 明文禁止 | 根 ADR-009 Lean Stack 缓交横向基础设施 | ✅ 完全一致 |

**结论**:ECE 仓已有 ADR 与 Track A 根目录 ADR 完全一致,**无决策冲突**。Track B session 可放心按 `ece/TASKS.md` 推进。

---

## 10. ECE 现有 Sprint 0-6 任务交叉验证

### 10.1 ECE TASKS.md Sprint 任务(从早期 ls)

| Sprint | 任务数 | 关键产出 |
|---|---|---|
| 0 | 6 | uv + docker + alembic + CI + scripts + 合成数据集 |
| 1 | 4 | Connector + Entity/Relationship 入库 + API + seed |
| 2 | 4 | Identity + Permission + Entity Resolution + E2 |
| 3 | 5 | Context Spec + Assembly + Provenance + /context + E3-E5 |
| 4 | 4 | Ingestion + Query Planner + /search + 性能 |
| 5 | 4 | 领域规则 + Agent + Actions + E6 |
| 6 | 5 | Debugger + Demo + eval-report + 换域演练 + 私有化验收 |

### 10.2 K1-K8 + D1 覆盖验证(详见 execution-plan.md §1)

**结论**:ECE TASKS Sprint 0-6 覆盖 K1-K8 + D1 **除 K7 MCP Tool Layer**——后者需要新增 S4.5(详见 execution-plan.md §4)。

---

## 11. 总结

### 11.1 8 个 Build ADR 审计链全部一致

| ADR | ECE TASKS 覆盖 | 一致性 |
|---|---|---|
| ADR-003 Permission | S2.2, S2.4, S4.2, S5.3, S6.1 | ✅ |
| ADR-004 MCP Tool | **S4.5 NEW**(真缺口) | ⚠️ 需新增 |
| ADR-005 Graph | S1.2-S1.4, S2.3 | ✅ |
| ADR-006 Context Assembly | S3.1-S3.5, S4.4, S5.2, S6.4 | ✅ |
| ADR-007 Entity Resolution | S2.3, S6.1, S6.2 | ✅ |
| ADR-008 Domain Evaluation | S2.4, S3.5, S5.4, S6.3 | ✅ |
| ADR-009 Domain Ontology | S3.1, S5.1, S6.4 | ✅ |
| ADR-010 Domain Reasoning | S5.1, S5.2 | ✅ |

### 11.2 唯一真缺口

**K7 MCP Tool Layer** — 需新增 S4.5 任务,详见 `execution-plan.md §4`。

### 11.3 ECE 仓 ADR 与根目录 ADR 无冲突

两套独立编号,主题有重叠(ECE ADR-004 ↔ 根 ADR-003 Permission,ECE ADR-010 ↔ 根 ADR-010 域包隔离)但内容互补(ECE 是技术实现,根是战略决策)。**Track A → Track B 决策链清晰,无矛盾**。
