# KERNEL_ARCHITECTURE_V3.md — Domain Intelligence Kernel 架构

> Version: 1.0
> Date: 2026-09-20
> Status: **Active — §3 推迟到 V1**
>
> ⚠️ **V3 收口修订（2026-09-20）**：本文件的 **§3（三类接口抽象）推迟到 V1**——V0 只保留具体实现
> （1 个 Local Provider + 1 个 InProcessExecutor，直接调用），**不建抽象层**。
> 五层架构与 §9 的 8 条不变式作为 **V1+ 的架构假设**保留。见 `V3_CLOSEOUT.md` §2.4。
> 关联: `docs/v3/PRD_V3.md` · `docs/v3/KERNEL_BOUNDARY.md` · `docs/adr/ADR-011.md`
> 前置: `docs/architecture_v2/platform-kernel-definition.md`（K1–K8 定义，V3 继承并扩展其边界）

---

## 1. 架构总览

```
┌──────────────────────────────────────────────────────────────────────┐
│                        ENTERPRISE APPLICATIONS                        │
│        Reference Apps: 审计证据 / 采购评估 / KM / 其他（未定 vertical）  │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  业务目标 + 任务
┌───────────────────────────────▼──────────────────────────────────────┐
│                       DOMAIN INTELLIGENCE KERNEL                      │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ ① CONTEXT LAYER                                                  │ │
│  │   Context · Entity · Relation · Temporal · Permission Scope      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ ② SEMANTIC LAYER                                                 │ │
│  │   Domain Ontology · Knowledge · Business Rules · Policy          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ ③ JUDGMENT LAYER                                                 │ │
│  │   Reasoning(规则优先) · Decision · Evaluation(业务正确性)          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ ④ EVIDENCE LAYER                                                 │ │
│  │   Evidence · Provenance · Trace · Context Update                 │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ ⑤ ORCHESTRATION SEMANTICS                                        │ │
│  │   Domain Workflow Specification · Agent/Tool/Runtime Selection    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌──────────────────────── ADAPTER BOUNDARY ───────────────────────┐ │
│  │  Provider Interface │ Agent Runtime Interface │ Execution I/F    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  Execution Intent
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
  Agent Runtimes        Execution Runtimes         Providers
  ─────────────         ──────────────────         ─────────
  DSH [C44]             Trigger.dev [C43]          Glean [C01–C42]
  PentAGI [C45]         In-process (V0)            Local Knowledge
  In-process (V0)       其他                       Enterprise API / MCP
        └───────────────────────┼───────────────────────┘
                                ▼
                       ENTERPRISE SYSTEMS
                                │
                                ▼
                    RESULT / STATE CHANGE / EVIDENCE
                                │
                                └──→ 回到 Kernel 的 Evidence Layer（闭环）
```

**五个内部层 + 一个适配器边界。** 层与层之间是单向依赖；适配器边界是 Kernel 与外部世界的**唯一通道**。

---

## 2. 五层职责

### 2.1 ① Context Layer

**职责**：把"当前业务情境"构造成结构化状态。

| 组件 | 内容 |
|---|---|
| **Context** | 见 `PRD_V3.md` §11.2 的 15 个构成要素 |
| **Entity** | 企业实体（人/组织/供应商/合同/采购申请/项目…） |
| **Relation** | 实体间关系，含 `valid_from` / `valid_to` / provenance / confidence |
| **Temporal** | 时态锚点（`as_of`）；业务有效期 |
| **Permission Scope** | 可访问边界的 SQL 子查询参数 |

**不变式**：**Permission 在数据访问层强制**（铁律 P2）。所有 Store 读方法必须接受 `PermissionScope`；禁止 post-filter。

**继承**：ECE v0 的 `src/ece/context/` / `src/ece/entities/` / `src/ece/permissions/`（K1 / K2 / K3 的一部分）。

**V3 新增**：Context Lifecycle 的显式化（Create → Enrich → … → Persist，见 `PRD_V3.md` §11.3）。

---

### 2.2 ② Semantic Layer

**职责**：定义"这个领域的业务语义"。

| 组件 | 内容 | 形态 |
|---|---|---|
| **Domain Ontology** | 实体类型、关系类型、业务判据 | YAML Context Specification（ADR-009） |
| **Knowledge** | 领域知识 / 企业知识 / 通用知识（三类分离，见 §13） | 结构化 + 文档 |
| **Business Rules** | 确定性判据（阈值、完整性、偏离带…） | **纯代码**（ADR-010） |
| **Policy** | 业务规则与合规策略 | YAML / 代码 |

**关键区别**（`KERNEL_BOUNDARY.md` §4）：Domain Ontology ≠ Glean Enterprise Graph。前者是"业务判据"，后者是"谁是谁"。

---

### 2.3 ③ Judgment Layer

**职责**：产出业务裁决。

```
Reasoning（规则优先）
   │
   ├── 确定性判断 → 纯代码规则引擎
   ├── 理解与叙述 → LLM（轻量，不裁决）
   └── 不足时     → insufficient_context（一等输出）
   ▼
Decision { conclusion, rules_fired[], evidence[], risks[], confidence, status }
   │
   ▼
Domain Evaluation（业务正确性，独立于检索质量）
```

**铁律**：LLM 不做确定性业务裁决（ADR-010）。

**继承**：ECE v0 的 `src/domain_packs/procurement/agent/`（K5）+ `tests/evaluation/`（K6）。

---

### 2.4 ④ Evidence Layer（V3 新增）

**职责**：让每个结论可追溯。

```
Evidence { source, claim, timestamp, actor, agent?, runtime?,
           input_context, decision, execution_reference }
   │
   ├── Provenance    来源链
   ├── Trace         决策链（可复现）
   └── Context Update 闭环：Evidence 回写 Context
```

**硬不变式**：

> Kernel 产出的每一条业务结论，必须能回答"它是怎么产生的"，且**该回答不依赖任何一个特定运行时的存续**。

**继承**：ECE v0 有 `context_requests` / `context_items` 审计表（K1 的一部分）+ `src/ece/audit/trace.py`。**V3 将其提升为一级业务对象**，而非仅工程审计。

---

### 2.5 ⑤ Orchestration Semantics（V3 新增）

**职责**：描述业务上应该怎么做，并选择执行者。

| 组件 | 内容 |
|---|---|
| **Domain Workflow Specification** | 业务步骤 + 判据 + 责任人（**不是 task 图**） |
| **Agent Selection** | 依据任务与评估记录选择 Agent |
| **Tool Selection** | 依据任务需要选择工具（MCP 归一） |
| **Runtime Selection** | 依据任务特征选择运行时（**V0 留空**） |

**继承**：ECE v0 的 `WorkflowEngine`（薄执行器，`architecture/agent-runtime.md`）在 V3 中**降级为 V0 的默认 Executor 实现**，而非 Kernel 的组成部分。

---

## 3. 适配器边界（V3 核心抽象）

### 3.1 三类接口

```
┌──────────────────────── ADAPTER BOUNDARY ────────────────────────┐
│                                                                    │
│  ProviderInterface              原料：数据与知识                    │
│    context.search(query, acting_user, permission_scope)           │
│    context.fetch_entity(ref)                                      │
│    context.fetch_relationships(ref, depth, as_of)                 │
│    knowledge.retrieve(query, scope)                               │
│                                                                    │
│  AgentRuntimeInterface          执行者：Agent 能力                  │
│    agent.invoke(intent, context_ref) → AgentResult               │
│    agent.capabilities() → CapabilitySet                           │
│                                                                    │
│  ExecutionRuntimeInterface      可靠执行                            │
│    execution.submit(intent, context_ref) → ExecutionHandle        │
│    execution.status(handle) → ExecutionStatus                     │
│    execution.result(handle) → ExecutionResult                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 硬规则

1. **命名用业务语义**，禁止出现厂商标识符（`glean` / `trigger` / `dsh` / `pentagi`）。

   ❌ `gleanClient.search()` ✅ `provider.search()`

2. **每类接口在 V0 必须有一个最朴素实现**：

   | 接口 | V0 实现 |
   |---|---|
   | ProviderInterface | `LocalKnowledgeProvider`（本地文件/DB）+ `InProcessProvider`（直连 ECE 库） |
   | AgentRuntimeInterface | `InProcessAgent`（一次 LLM 调用，无 loop） |
   | ExecutionRuntimeInterface | `InProcessExecutor`（同步函数调用，无队列） |

3. **CI 门禁**：Kernel 核心源码中不得出现厂商标识符。

   ```bash
   # 沿用 mvp-scope.md:33/71 的做法，扩展到 provider/runtime
   ! grep -rEi 'glean|triggerdev|trigger\.dev|deepseek.?harness|dsh|pentagi' \
       src/kernel/ src/domain_packs/
   ```

4. **接口稳定优先于功能完整**：V0 只实现接口的最小方法集；方法可增，签名不宜改。

### 3.3 与 ADR-001 的关系

ADR-001 定义单一 `ContextAdapter`。V3 **推广**为三类接口——ADR-001 不被推翻，是其超集。原有的 11 方法（`search` / `get_entity` / `get_person` / …）归入 **ProviderInterface.context.\***。

---

## 4. Execution Intent（Kernel → 运行时的契约）

Kernel 向执行运行时发出的不是函数调用，而是**业务意图**：

```
ExecutionIntent
├── workflow_spec_ref      Domain Workflow Specification 引用
├── context_ref            本次执行所用 Context 引用（可复现）
├── evidence_requirements  期望产出哪些证据
├── permission_scope       执行边界（不可越权）
├── approval_required      是否需要人工审批
└── proposed_steps[]       建议步骤（业务语言）
```

**运行时返回**：

```
ExecutionResult
├── status                 succeeded | failed | waiting_approval | partial
├── execution_ref          执行轨迹引用（不构成业务证据）
├── outputs[]              原始产出
└── evidence_candidates[]  候选证据 → 必须由 Kernel 转为正式 Evidence
```

**关键约束**：

> **运行时无权直接写入企业事实。** 一切"业务事实"必须经 Kernel 的 Evidence Layer 转换与记录。

**理由**：这是"运行时不可信"原则的直接体现——外部运行时可以替换、可以失败、可以消失，但企业事实的完整性不能依赖它。

---

## 5. 数据模型（V3 版）

### 5.1 对象清单与阶段归属

| 对象 | identifier | lifecycle | provenance | permission | 阶段 |
|---|---|---|---|---|---|
| Context | `ctx_<uuid>` | 请求内 | ✅ | ✅ | **V0** |
| Entity | `display_id` | 长期 | ✅ | ✅ | **V0** |
| Relation | `id` | 含时态 | ✅ | ✅ | **V0** |
| Ontology | `spec:version` | 版本化 | ✅ | n/a | **V0** |
| Knowledge | `doc_id` | 长期 | ✅ | ✅ | **V0** |
| Evidence | `ev_<uuid>` | **长期** | ✅ | ✅ | **V0** |
| Reasoning | `rs_<uuid>` | 随 Context | ✅ | 继承 | **V0** |
| Decision | `dec_<uuid>` | **长期** | ✅ | ✅ | **V0** |
| WorkflowSpec | `wf:version` | 版本化 | ✅ | n/a | **V0** |
| Action | `act_<uuid>` | 长期 | ✅ | ✅ | **V0**（建议） |
| AgentRef | `agent:version` | 版本化 | ✅ | n/a | **V0** |
| Policy | `pol:version` | 版本化 | ✅ | n/a | **V0**（最小） |
| RuntimeRef | `runtime:<name>` | 配置 | ✅ | n/a | V1 |
| ExecutionRef | `exec_<id>` | 外部 | ✅ | 继承 | V1 |

### 5.2 关系图

```
Context ──1:N──> Evidence
Context ──1:1──> Decision
Context ──N:M──> Entity（经由 Relation）
Decision ──1:N──> Evidence（支撑）
Decision ──1:N──> Action（建议）
Evidence ──0:1──> ExecutionRef（外部运行时轨迹，仅引用）
Decision ──1:1──> WorkflowSpec（本次采用）
Context ──N:1──> Ontology（spec 版本）
```

**关键**：`Evidence → ExecutionRef` 是 **0:1 且仅引用**。ExecutionRef 消失不影响 Evidence 的完整性与可追溯性。

### 5.3 持久化

- **V0/V1**：PostgreSQL（单库承担结构化 + FTS + pgvector + JSONB）—— 铁律 3 垂直纪律，不引入 OpenSearch / Redis / Neo4j。
- **Evidence 必须与 Context 同库**：业务证据的存续不能外包给运行时。

---

## 6. 与 ECE v0 的映射

| Kernel 层 | ECE v0 模块 | 状态 |
|---|---|---|
| Context Layer | `src/ece/context/` · `src/ece/entities/` · `src/ece/permissions/` | ✅ 已覆盖（K1/K2/K3） |
| Semantic Layer | `src/domain_packs/procurement/context_specs/` · `agent/` | ⚠️ 部分（K4/K5） |
| Judgment Layer | `src/domain_packs/.../agent/` · `tests/evaluation/` | ⚠️ 部分（K5/K6） |
| **Evidence Layer** | `src/ece/audit/` | ⚠️ **有审计表，无业务 Evidence 对象** → V0 需扩展 |
| **Orchestration Semantics** | `architecture/agent-runtime.md` 的 WorkflowEngine | ⚠️ **无 Workflow Specification 概念** → V0 需新增 |
| Adapter Boundary | `ContextAdapter`（单一） | ⚠️ 需推广为三类接口 |
| Query Planner | `src/ece/search/` | ✅ 已覆盖（K8） |
| MCP Tool Layer | — | ❌ **不存在**（K7 缺口，V2 已识别） |
| Data Store | PostgreSQL + pgvector | ✅ 已覆盖（D1） |

**V3 对 Track B 的新增要求**（V0 范围）：

```
NEW-1  Evidence Object 一级化（从 audit 表提升为业务对象）
NEW-2  Domain Workflow Specification（YAML 最小形态）
NEW-3  Adapter 三类接口抽象（Provider / Agent Runtime / Execution Runtime）
NEW-4  Context Update 闭环（Evidence 回写 Context）
NEW-5  CI 门禁扩展到 provider/runtime 厂商标识
```

---

## 7. 能力矩阵（K1–K8 的继承与扩展）

V2 定义 K1–K8 + D1。V3 **全部继承**，并作如下扩展：

| V2 | 名称 | V3 处置 |
|---|---|---|
| K1 | Permission Engine | ✅ 继承（`KERNEL_BOUNDARY.md` 行 1） |
| K2 | Context Assembly | ✅ 继承，增加 Context Lifecycle |
| K3 | Entity Resolution | ✅ 继承 |
| K4 | Domain Ontology | ✅ 继承 |
| K5 | Domain Reasoning | ✅ 继承 |
| K6 | Domain Evaluation | ✅ 继承 |
| K7 | MCP Tool Layer | ✅ 继承（归入 Adapter Boundary 的 Tool 部分） |
| K8 | Query Planner | ✅ 继承（归入 Provider Interface 的内部实现） |
| D1 | PostgreSQL + pgvector | ✅ 继承 |
| **E1（新）** | **Evidence Model** | 🆕 V3 新增 |
| **E2（新）** | **Domain Workflow Specification** | 🆕 V3 新增 |
| **E3（新）** | **Adapter Trio**（Provider / Agent / Execution） | 🆕 V3 新增（ADR-001 的超集） |

> 编号提示：为避免与评测套件 E1–E6 混淆，本文档中新增项用 **E1/E2/E3** 前缀仅在 §7 本表出现，正式称呼一律用名称（Evidence Model / Domain Workflow Specification / Adapter Trio）。

---

## 8. 私有化部署形态

```
Customer Environment（无外网）
┌──────────────────────────────────────────────┐
│  ┌────────────────┐    ┌──────────────────┐  │
│  │  Kernel        │    │  Local Model     │  │
│  │  (single proc) │───▶│  (vLLM / Ollama) │  │
│  └───────┬────────┘    └──────────────────┘  │
│          │                                    │
│  ┌───────▼────────┐    ┌──────────────────┐  │
│  │  PostgreSQL    │    │  Local Knowledge │  │
│  │  + pgvector    │    │  (files / DB)    │  │
│  └────────────────┘    └──────────────────┘  │
│          │                                    │
│          ▼                                    │
│   Enterprise Systems (只读优先)                │
└──────────────────────────────────────────────┘
```

**V0 形态**：两个容器（api + postgres），本地端口映射，无 SaaS 控制面。ECE v0 的 `docker-compose.yml` 已满足此形态。

**可选外接**：Customer 若已有 Glean 等 Provider，可外接——**但 Kernel 的必需层不得依赖它**。

---

## 9. 架构不变式（Architectural Invariants）

以下 8 条为**可被机械检验**的不变式，建议纳入 CI：

```
INV-1  Permission 在数据访问层强制（SQL 子查询），无 post-filter 路径
INV-2  Kernel 核心与领域包中不出现任何厂商标识符（provider/runtime 厂商）
INV-3  LLM 调用只经 OpenAI 兼容端点；无厂商 SDK 依赖、无模型名硬编码
INV-4  每个业务结论可追溯到 Evidence；每条 Evidence 可追溯到来源
INV-5  Evidence 的完整性不依赖任何外部运行时的存续（ExecutionRef 仅引用）
INV-6  证据不足时输出 insufficient_context，不猜测
INV-7  确定性业务判断不调用 LLM
INV-8  运行时无权直接写入企业事实
```

**与铁律的关系**：INV-1/3 直接对应 ECE 铁律 P2/铁律 5；INV-2 对应领域包隔离（铁律 4）；INV-6/7 对应 ADR-010 与评估模型；INV-4/5/8 为 V3 新增。

---

## 10. 待解决的架构问题

| # | 问题 | 影响 | 优先级 |
|---|---|---|---|
| 1 | ExecutionRef 的引用形式——运行时不可达时，引用如何保持可读？ | Evidence 完整性 | 中 |
| 2 | Workflow Specification → Execution Workflow 的映射规则（谁写 mapper？） | Adapter 设计 | 中 |
| 3 | Evidence 的保留期与客户合规要求的对齐（GDPR / 个保法 / 等保） | 企业交付 | 高 |
| 4 | Context 跨 Agent 共享的 Scope 边界的具体实现（V0 以 Task 为界） | 多 Agent 场景 | 中 |
| 5 | K7 MCP Tool Layer 的实现（V2 已识别为真缺口） | 工具层 | 高 |
| 6 | 动态 Runtime Selection 的判据（V0 留空，何时填） | 编排 | 低（V1 之后） |

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
