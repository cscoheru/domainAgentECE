# Reference Applications v2 — Kernel 之上的应用重述

> **Phase**: 6 — Reference Applications + STOP Gate
> **Last Updated**: 2026-09-13
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §9 Phase 6 + §11 STOP Gate
> **上游**:
> - [`/docs/architecture_v2/platform-kernel-definition.md`](../architecture_v2/platform-kernel-definition.md) — K1-K8 Kernel
> - [`/docs/architecture_v2/build-buy-integrate-partner-matrix.md`](../architecture_v2/build-buy-integrate-partner-matrix.md) — Phase 4 BBIP
> - [`/docs/research/RED_TEAM_REVIEW.md`](../../RED_TEAM_REVIEW.md) — v3 Red Team
> - [`/docs/research_v2/capability-matrix-v2.md`](../research_v2/capability-matrix-v2.md) — Phase 2 16 能力
> - `/docs/product_v2/` — **本 Phase 新建目录**

---

## 0. Phase 6 DoD(per PRD §9)

1. 把 Reference Applications 重述为 Kernel 之上应用(每个含 Kernel 依赖图 + 验证假设)
2. 完成后停下汇报 → **STOP Gate §11 十问**

---

## 1. Reference Applications 选择(3 个)

| # | 候选 | 来源 | 选择理由 |
|---|---|---|---|
| **App 1** | **EvidenceIQ**(审计证据智能) | v3 Red Team §0.5 推荐 C1 | v0.1 之后最高 IP 价值域;Kernel 重负荷应用 |
| **App 2** | **Procurement Agent** | ECE v0 Sprint 5 领域包 | 我方已规划开发;直接验证 ECE 真实路径 |
| **App 3** | **HR Q&A** (C10) | v1 product-ranking C10 | 轻量级 reference;验证"minimum viable"声明 |

**未选**:**RFP 应答**(C2,v3 §0.5 降级为战略备选,CA=2)/ **TPRM 问卷**(C9,v3 §0.5 列为 C1 扩展)/ **事故复盘/项目健康/QBR 等**(C4-C8,Watchlist)。Phase 6 仅选 3 个作为 Kernel 验证样本,后续可扩。

---

## 2. App 1 — EvidenceIQ(审计证据智能)

### 2.1 Persona / Problem / Workflow

| 项 | 内容 |
|---|---|
| **Persona** | GRC 合规经理(NimbusWorks 的 Lin Chen,fictional) |
| **核心问题** | SOC2 Type II 续证 — 6 周内为 12 个 CC 控制项归集期间(H1/2026)证据 |
| **输入** | 审计范围三要素(框架 + 期间 + 系统范围) |
| **输出** | Audit-Ready Evidence Pack(Evidence Matrix + Gap List + 派工回执) |
| **Workflow** | Ingest→Map→Retrieve→Reason→Act→Approve→Package(7 步) |

### 2.2 Kernel 依赖图

| Kernel | 用法 | 关键作用 |
|---|---|---|
| **K1 Permission Engine** | ✓✓ | 安全类证据(评审/漏洞/供应商评估)仅 security/compliance 可见;E2 = 0 强制 |
| **K2 Context Assembly** | ✓✓ | 12 步流水线:identity → resolve → permissions → entities → relationships → documents → structured → temporal → rank → package → provenance → audit |
| **K3 Entity Resolution** | ✓✓ | 跨系统归一:Confluence + Jira + HRIS + Git 4 系统的"评审记录"统一 |
| **K4 Domain Ontology** | ✓✓✓ **CORE** | SOC2 CC 控制项 ↔ 证据类型映射(`soc2-cc.json`);本体驱动整应用 |
| **K5 Domain Reasoning** | ✓✓✓ **CORE** | 4 类规则推理:充分性(类型×数量×期间)/ 新鲜度(政策版本 ≤ 期间)/ 覆盖度(全部系统)/ 归因(责任人派工) |
| **K6 Domain Evaluation** | ✓✓✓ **CORE** | E1-E6 套件 + 纯 RAG baseline 对照(ECE 显著优于 RAG) — 客户付费决策核心证据 |
| **K7 MCP Tool Layer** | ✓ | 把 ECE search/get_record 暴露给 Claude Code / Cursor(审计师工具链) |
| **K8 Query Planner** | ✓✓ | 4 路召回融合:CC6.2 评审记录(多系统 keyword) + 政策版本(temporal) + 缺陷关联(structured) + 责任人(relationship) |

### 2.3 验证假设

| 假设 | 验证方式 | 关键证据 |
|---|---|---|
| **H1**: Domain Ontology (K4) + Domain Reasoning (K5) + Domain Evaluation (K6) 构成最高 IP 价值区 | EvidenceIQ 重负荷使用 K4-K6;v0.1 后只有 4 条规则 + 4 个金标准案例(RED_TEAM v3 §三 IP 解剖),真实客户数据滚过 2-3 轮才形成护城河 | Phase 2 §M07 + ADR-008/009/010 + EVALUATION.md §1 E1-E6 |
| **H2**: Permission Before Intelligence (K1) 是审计场景的**信任货币** — 没权限过滤,法务不接受 | EvidenceIQ 的"切用户重问"演示:同一 PR,合规经理看见安全证据,普通工程师被过滤 | ADR-003 + EVALUATION.md §1 E2 |
| **H3**: 跨框架扩展(SOC2 → ISO27001 → 等保)是**内容工作非架构工作** | 本体设计框架无关(ADR-009);换框架 = 12 个 CC 重新映射本体,不改引擎 | ADR-009 + ADR-010 |

### 2.4 Input/Output

**Input**:审计范围(framework=SOC2/ISO27001/等保, period=期间, systems=PROD-ERP/OSS/CRM/HR)
**Output**:Evidence Pack =
- Evidence Matrix(每个 CC:evidence list + sufficiency rating)
- Gap List(缺口 + 责任人 + 期限)
- 派工回执(Mock 工单系统)

---

## 3. App 2 — Procurement Agent(ECE v0 领域包)

### 3.1 Persona / Problem / Workflow

| 项 | 内容 |
|---|---|
| **Persona** | 采购经理 |
| **核心问题** | "PR001 这个采购申请合理吗?"(1,000 台设备 × 1,280 元 / 台,供应商 X) |
| **输入** | User Question + Context Package |
| **输出** | conclusion / reasoning_summary / risks[] / recommendation / evidence[] / confidence |
| **Workflow** | Question → Context → Agent → Answer → Evidence(单流) |

### 3.2 Kernel 依赖图

| Kernel | 用法 | 关键作用 |
|---|---|---|
| **K1 Permission Engine** | ✓✓ | 供应商可见性(本部门 vs procurement-only);价格透明度按角色过滤 |
| **K2 Context Assembly** | ✓✓ | 12 步:从 PR001 沿关系展开 supplier/product/contract/policy/historical |
| **K3 Entity Resolution** | ✓✓ | 供应商多名称归一(无限极 / Infinite / Infinite China / 无限极中国) |
| **K4 Domain Ontology** | ✓ | procurement 领域本体:PR→supplier→contract→policy→historical |
| **K5 Domain Reasoning** | ✓✓✓ **CORE** | 4 条规则:金额 ≥100 万触发三家比价 / 价格偏离带 vs 历史价(±10%)/ 审批链完整性 / 政策匹配 |
| **K6 Domain Evaluation** | ✓ | E6 端到端评测 + 纯 RAG baseline 对照 |
| **K7 MCP Tool Layer** | ✓ | search / get_record / create_task |
| **K8 Query Planner** | ✓✓ | 4 路召回:政策文本(keyword)+ 历史采购记录(structured)+ 合同(relationship)+ 产品文档(vector) |

### 3.3 验证假设

| 假设 | 验证方式 | 关键证据 |
|---|---|---|
| **H1**: v3 §0.8 "规则优先架构意外命中中国约束" 在 Procurement 场景成立 | 纯 Python 规则 vs LLM 全权推理;DeepSeek / Qwen 双模型对照(E6 评测) | ADR-010 + EVALUATION §5 H4 |
| **H2**: 12 步流水线在窄切片(Procurement)同样适用,不退化为普通 RAG | Context Assembly 严格走 12 步,Procurement Context Spec 仅需 60 entities / 30 chunks | ADR-006 + ARCHITECTURE §3 |
| **H3**: Phase 5 Kernel 与 ECE v0 Sprint 5 任务 1:1 映射 | 全部 8 个 Kernel 在 Sprint 5 都有对应实现任务 | Phase 5 §2 映射表 + TASKS Sprint 5 |

### 3.4 Input/Output

**Input**:"PR001 这个采购申请合理吗?"
**Output**:
```json
{
  "conclusion": "存在采购价格偏高风险",
  "reasoning_summary": "① 报价高于历史价 11.3%;② 高于市场参考价 8.5%;③ 金额触发三家比价;④ 未见完整比价记录",
  "risks": [{"type": "price_deviation", "detail": "1280 vs 历史均价 1150", "evidence_sid": "s4"}],
  "recommendation": "补充三家比价材料后再进入下一审批阶段",
  "evidence": [{"sid": "s1", "fact": "采购金额 128 万元", "src": {"system": "erp", "record_id": "PR001"}}],
  "confidence": 0.86
}
```

---

## 4. App 3 — HR Q&A(C10)

### 4.1 Persona / Problem / Workflow

| 项 | 内容 |
|---|---|---|
| **Persona** | 公司员工(普通 HR 用户) |
| **核心问题** | "我还有多少年假?"(单问题快速查询) |
| **输入** | User Question + User Identity(actingUser) |
| **输出** | Answer + Evidence(HRIS 记录 + 政策引用) |
| **Workflow** | Question → Identity Resolve → Context → Answer(单流,无派工) |

### 4.2 Kernel 依赖图

| Kernel | 用法 | 关键作用 |
|---|---|---|
| **K1 Permission Engine** | ✓ | Self-only visible(不能查别人的 PTO) |
| **K2 Context Assembly** | ✓ | 简化版:identity + entities + documents + provenance |
| **K3 Entity Resolution** | — | 单 HRIS 系统,无需跨系统归一(本 App 不重度依赖) |
| **K4 Domain Ontology** | ✓ | HR 政策本体(年假规则 + 法定假日 + 公司福利) |
| **K5 Domain Reasoning** | ✓ | 规则:工龄×年假天数 + 法定扣除 + 公司额外 |
| **K6 Domain Evaluation** | ✓ | 简化版评测(回答准确性 + 权限隔离) |
| **K7 MCP Tool Layer** | ✓ | Connect HRIS via MCP |
| **K8 Query Planner** | ✓ | 政策文档 + HRIS records 双路召回 |

### 4.3 验证假设

| 假设 | 验证方式 | 关键证据 |
|---|---|---|
| **H1**: 即使轻量级 App,Kernel 仍提供"minimum viable"价值 | HR Q&A 不需要 K3 (跨系统) 但仍用 K1/K2/K4-K8;**所有 Kernel 在不同负载下都有价值** | Phase 5 §1 (K1-K8 不可替代论证) |
| **H2**: K4 Domain Ontology 即使小本体也提供 framework-agnosticism | HR 政策可类比 Procurement 走 YAML 路径;换公司 = 换本体 | ADR-009 |
| **H3**: C10 评分 3.05 最低,Kernel 能否补足 | Kernel 提供低 CA 候选的**结构性可行性** — 技术降风险但不替代市场验证 | ADR-007 + ADR-008 + RED_TEAM §0.5 |

### 4.4 Input/Output

**Input**:"我还有多少年假?"
**Output**:
```json
{
  "answer": "您还有 12.5 天年假(截至 2026-09-13)。本年度已用 5 天。",
  "evidence": [
    {"fact": "工龄 3 年,法定年假 10 天", "src": {"policy_id": "POL-HR-001"}},
    {"fact": "公司额外福利 +2 天(满 3 年)", "src": {"policy_id": "POL-HR-005"}},
    {"fact": "本年度已用 5 天", "src": {"hris": "PTO-2026-U001"}}
  ],
  "as_of": "2026-09-13"
}
```

---

## 5. Reference Applications 对比矩阵

| 维度 | EvidenceIQ | Procurement Agent | HR Q&A |
|---|---|---|---|
| Kernel 重负荷 | K4/K5/K6 CORE | K5 CORE | 全部轻量 |
| Domain 本体复杂度 | 高(12 CC 控制项) | 中(procurement 流程) | 低(HR 政策) |
| 跨系统归一 | 高(K3 重度) | 中(K3 中度) | 无(K3 不依赖) |
| Permission 复杂度 | 高(角色门控 6 类) | 中(部门 + 角色) | 低(self-only) |
| Demo 时长(目标 15 分钟) | 15 分钟 | 10 分钟 | 5 分钟 |
| Sprint 5 优先级 | (未来 Phase 5+) | P0(v0 必须) | P2(Phase 5+) |
| 行业可移植性 | 审计/合规/法务 | 采购/供应链 | HR / 多行业 |

---

## 6. STOP Gate 十问回答(per PRD §11)

> **PRD §11**:"当且仅当以下 10 问全部有证据支持的答案时 STOP"

| # | 问题 | 答案 | 证据 |
|---|---|---|---|
| **1** | Glean 的核心架构是什么? | **4 大模块 + 9 层堆叠**:Context / Access / Agent / Governance 四大产品模块;Enterprise Applications → Domain Agents → Agent Runtime → Context API → Enterprise Context → Search/Graph/Permission → Connectors 9 层 | [C01] 4 大模块 CONFIRMED + [C10][C18][C19] + Phase 3 §1-2 推导 |
| **2** | Enterprise Graph 到底承担什么角色? | **不是单纯 KG**;是 = Knowledge Graph + Search Index + Entity System + Permission + Context Assembly 之综合 | [C02] CONFIRMED(Enterprise Graph 存在性)+ [C18] "reason over KG" CONFIRMED + 推导;详见 Phase 2 §M02 + Phase 3 §2.1 |
| **3** | Context 是如何形成的? | **Connector→Indexing→Enterprise Graph→Search/Retrieval→Permission Filter→Context Assembly→Provenance→Audit** 8 阶段流水线 | [C02][C04][C06][C18][C19] 综合 + 推导(具体管线 INFERRED);Phase 2 §M02 + §M03 |
| **4** | Permission 在哪里进入整个链路? | **检索过程实时**(非取回后过滤,非 prompt 约束);Glean 用 [C06] 源系统 ACL 继承 + [C07] 实时同步 + [C36] Agent Identity scoped credentials;**我方 ECE 用 K1 Permission Engine 在 SQL 子查询层强制** | [C06][C07][C36] CONFIRMED;Phase 2 §M04 + ADR-003 |
| **5** | Agent Runtime 需要哪些基础能力? | **Planning / Tool / Loop / Branch / Verification / Action + Memory + A2A + Trigger + GA/Beta 矩阵**:[C37] 官方 GA(schedule agents / version control)+ Beta(conversational builder / agent looping)+ Coming soon(Glean Canvas / 100+ actions) | [C10][C12][C17][C18][C37] CONFIRMED;Phase 2 §M05 + Phase 3 §1.2 |
| **6** | Action / MCP / Tool 是如何进入 Agent 的? | **Glean 三通道**:Agent Toolkit (C17,内置 search/employee_search) + MCP (C19,Remote MCP Server) + OpenAPI 自定义 Action (C09);**我方 ECE 用 K7 MCP Tool Layer**(ADR-004)原生 MCP 化,**[C39] 验证**与 Claude Code/Cursor/Codex 一键集成 | [C08][C09][C17][C19][C39] CONFIRMED;Phase 2 §M06 + ADR-004 |
| **7** | Governance / Evaluation 在哪里? | **Glean**:Glean Protect/Intelligence (C01) + Agent Governance (C13) + Observability 平台级 (C14);**我方差异化**:**[C22] + [C38 收紧]** Glean 无业务正确性评估 — 我方 K6 自建 Domain Evaluation (极高 IP) | [C14][C22][C38] CONFIRMED+INFERENCE_TIGHTENED;Phase 2 §M07 + ADR-008 |
| **8** | Glean 哪些能力是它真正的壁垒? | **不是功能清单,是 7 年企业信任阶梯 + 数据主权**:[C06][C07] 工程化形态 + RED_TEAM v3 §0.2 信任阶梯理论;**规模优势**:275+ Connectors (C05);**核心壁垒**:Permission 同步 + Enterprise Graph + Trust Position | [C05][C06][C07] CONFIRMED + RED_TEAM v3 §0.2 论证;Phase 2 §M04 + §0.6 |
| **9** | 我们自己的 Platform Kernel 最少需要什么? | **8 个 Kernel(K1-K8)+ D1 Postgres 数据底座**:Permission / Context Assembly / Entity Resolution / Domain Ontology / Domain Reasoning / Domain Evaluation / MCP Tool Layer / Query Planner + Postgres+pgvector+FTS;**Glean 不覆盖的部分**:K3/K4/K5/K6 (Domain 三件套 + Entity Resolution) 是我方最高 IP | Phase 5 §1 完整论证 + ADR-003 ~ ADR-010 |
| **10** | 第一版 Demo 应该证明什么? | **三件事**:(a) Permission Before Intelligence — 切用户重问数据隔离;(b) Domain Reasoning — 规则优先 vs 纯 LLM;[C22] 差异显著;(c) Domain Evaluation — ECE 优于纯 RAG baseline (EVALUATION §5 H3) | Phase 6 §2-4 Reference Applications + EVALUATION.md §5 |

### 6.1 STOP Gate 状态

**所有 10 问均有证据支持的答案** ✅

按 PRD §11:
> "回答完:`STOP RESEARCH → ARCHITECTURE → BUILD`。**不要再继续堆研究文档。** 剩余未知项全部转入 `questions-for-glean.md` 由会谈裁决。"

→ **STOP Track A 研究阶段,进入 Track B 工程实施**(ECE v0 Sprint 0-6 by ece/CLAUDE.md + ece/TASKS.md)。

### 6.2 已转入 questions-for-glean.md 的剩余 UNKNOWN

- **[C03]** Enterprise Graph schema 可否自定义/API 读写 — Q9
- **[C11]** Agent Builder workflow 细节(branching/HITL/per-step model)— Q10
- **[C24]** Glean 定价与最低合同额 — Q11
- **[C25]** Agent Harness / Transform 详情 — Q10 / 未来 Q

---

## 7. 治理 + 下一步

### 7.1 Phase 6 DoD 全部满足

- ✅ 3 个 Reference Applications(EIR / Procurement / HR Q&A)重述为 Kernel 之上应用
- ✅ 每个含 Kernel 依赖图(8 Kernel × 3 App = 24 个依赖点)
- ✅ 每个含验证假设(共 9 个 H1-H3)
- ✅ STOP Gate §11 十问全部有证据支持答案
- ✅ v1 文档(`/docs/research/`、`/docs/product/`)不修改不删除
- ✅ `ece/` 子目录未触碰(Track B 独立推进)

### 7.2 STOP Gate 后动作(per PRD §13)

> PRD §13.3:"禁止为研究而研究。STOP Gate 之后再写新研究文档 = 违规。"

**Track A STOP**:
- ✅ Phase 0-6 全部完成,共 13 commits
- ✅ 42 条证据(C01-C42),15 个文档(/docs/research_v2/ + /docs/architecture_v2/ + /docs/product_v2/ + /docs/partner/ + /docs/adr/ + /docs/diagrams/)
- ✅ STOP Gate 通过 → **Track A 研究阶段正式结束**

**Track B 启动**(ECE v0 工程实施):
- 由 `ece/CLAUDE.md` + `ece/TASKS.md` 独立推进(Sprint 0-6,~30 工作日)
- Phase 5 §3.1 已建议 Track B 在 Sprint 4 新增 **S4.5 MCP Tool Layer** 任务(需用户授权后由 Track B 写入 ece/TASKS.md)

### 7.3 完整 Track A 进度(13 commits)

```
<Phase 6 commit> Phase 6 — Reference Applications + STOP Gate(本 commit)
421dc06       Phase 5 — Platform Kernel Definition
713c083       Phase 4 — BBIP 矩阵 + 8 ADRs
03b096e       Phase 3 — Architecture Reconstruction
b527574       R1-R7 fixes (Cline review)
040c04e       Cline 红队审阅报告
b166061       Cline review brief
9f3a5cb       Phase 2 — Capability Map
f5d4d0e       Phase 1 — Evidence Collection
c1dd32b       Phase 0 — Partner meeting prep
f28472e       (initial)
```

---

## 8. 总结报告(给用户)

**Track A — Glean Architecture Reverse Engineering & Enterprise AI Platform Kernel**

### 8.1 已交付

- **Phase 0**(c1dd32b): Partner 会谈准备稿 + 14 题必问清单 + C26-C34
- **Phase 1**(f5d4d0e + b527574): Evidence Matrix v2 + C35-C42(Cline 红队独立通道 8 条新证据)+ R1-R7 修复
- **Phase 2**(9f3a5cb): 9 模块研究文档 + 16 能力 Capability Matrix v2
- **Phase 2.5**(b527574 内): Cline 红队审查 + R1-R7 修复
- **Phase 3**(03b096e): Glean 分层架构 + Platform Kernel G/O/P/? 大图(2 mermaid)
- **Phase 4**(713c083): BBIP 矩阵 + 8 个 Build 决策 ADR(ADR-003 ~ ADR-010)
- **Phase 5**(421dc06): 8 个 Kernel 层 + 数据底座 + ECE 架构完整映射
- **Phase 6**(本 commit): 3 个 Reference Applications + STOP Gate §11 十问 ✅

### 8.2 核心结论

| 维度 | 结论 |
|---|---|
| **Glean 真正壁垒** | 不是功能清单,是 7 年企业信任阶梯 + 数据主权 |
| **可达市场约束** | 中国大陆(U-G1)→ 私有化部署 + 国产开源模型(v3 主路径 D) |
| **我方最高 IP** | Domain 三件套(Ontology / Reasoning / Evaluation) + Entity Resolution |
| **ECE Kernel 最小集** | K1-K8 + D1(Postgres),缺一不可 |
| **Agent Identity 状态** | Glean [C36] beta — 视 Robin Q12 决定是否吸收 |
| **不可降级** | Permission Before Intelligence / 间接泄露防护 / 业务正确性评估 |

### 8.3 剩余未决议

- Robin 会谈(下周):14 题必问清单,3 题是 UNKNOWN 必答(C03/C11/C24)
- Track B Sprint 4 是否新增 S4.5 MCP Tool Layer(待用户授权)

### 8.4 STOP

按 PRD §11 + §13.3:**Track A 研究阶段正式 STOP**。剩余未知全部转入 `partner/questions-for-glean.md` 由 Robin 会谈裁决。**不再继续堆研究文档**。
