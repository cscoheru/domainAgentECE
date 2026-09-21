# Foundation Reuse Study — 合并包 3/3：代码级证据 B（Tier-2 与横切结论）

> **这是 3 份合并包中的第 3 份（证据层 B）。** 覆盖六个 Tier-2 候选与两个横切结论节。
> 正文与仓库内源文件**逐字节一致**。
>
> 仓库 `domainAgentECE` ｜ 目录 `docs/research/` ｜ 提交 `55a321d` ｜ 生成 2026-09-21

==============================================================================
==============================================================================
# 来源文件：`FOUNDATION_REUSE_CODE_NOTES.md`
> §4 OpenEAAP · §5 GSearchAI · §6 qKnow · §7 KnowledgeOps · §8 mcp-agent · §9 DataLogicEngine · §10 Tier-2 交叉结论 · §11 Evidence 字段级横切分析 · §12 九候选裁决汇总
==============================================================================

## 4. Candidate D — OpenEAAP (`turtacn/OpenEAAP`) → **CLOSE**

> 默认分支是 `master`（不是 `main`）。Go，1★。

**D-1 License = Apache-2.0，干净（CONFIRMED）**

`LICENSE` 全文为标准 Apache 2.0，含专利授权。商业使用 ✔ / 修改 ✔ / 再分发 ✔ / SaaS ✔，
无附加条件。**这是本批三个候选里唯一许可无歧义的**——但许可干净并不能救活下面的健康度与定位问题。

**D-2 仓库健康度 = 高风险（CONFIRMED）**

| 项 | 证据 | 结论 |
|---|---|---|
| 创建 / 最后提交 | 创建 2026-01-06；最后 commit **2026-01-21** `tuxudong init openEAAP from scratch by using ccs45` | **约 8 个月未更新** |
| 贡献者 | 2 人：`openhands-agent`（33 commits）、`turtacn`（1 commit） | 由 Agent 脚手架生成 |
| Releases | 0 | — |
| CI | `GET /repos/.../contents/.github/workflows` → **Not Found** | **无 CI** |
| 仓库卫生 | 树中存在 `internal/infrastructure/vector/milvus/milvus_client.go.orig` 与 `.rej`（**未解决的补丁冲突被提交**）、`SYNTAX_FIXES_SUMMARY.md`、`COMMIT_SUMMARY.md`、`test_output.log` | 调试中途被提交 |

测试目录存在（`test/unit/domain/*_test.go`、`test/integration/`、`test/e2e/`、`scripts/test.sh`），
但在上述健康度下不构成可信信号。

**D-3 它是什么（CONFIRMED）**

Go + DDD 分层的**企业 Agent 平台**：`internal/domain/{agent,knowledge,model,workflow}`
＋ `internal/platform/{orchestrator,runtime,rag,inference,training,learning}`
＋ `internal/governance/{audit,compliance,policy}`，基础设施适配 Postgres/Redis/MinIO/Milvus/Kafka。
重心在 `internal/platform/orchestrator/`（`orchestrator.go`/`executor.go`/`scheduler.go`/`parser.go`）
与 `internal/platform/runtime/{langchain,native,plugin}`。

→ **它是 Agent Runtime，不是 Kernel。**

**D-4 核心数据模型 = 缺席（CONFIRMED）**

Context / Ontology / Evidence / Provenance **均无一等对象**。

- `internal/domain/knowledge/entity.go:18` `type Document struct`（含 `Source` / `ContentHash` /
  `Version` / `ParentDocumentID`）—— 文档元数据，**不是 Evidence**。
- `migrations/001_init.up.sql:237,251,269` 有 `knowledge_graphs` / `kg_entities` / `kg_relations`
  **表**，但**没有对应的 Go 领域实体**（表与领域模型脱节）。
- `migrations/001_init.up.sql:27` `CREATE TYPE decision_type AS ENUM ('permit','deny','conditional')`；
  `:292-298` `policies (... rules JSONB, decision_default decision_type)`；对应
  `internal/governance/policy/pdp.go:19` `PolicyDecisionPoint.Evaluate(ctx, *AccessRequest) (*Decision, error)`。
  ⚠️ **这是授权 PDP（authorization），不是业务裁决**；`AccessRequest.Context` 是
  `map[string]interface{}` —— 一个 blob，**不是 Context 对象**。
- `migrations/001_init.up.sql:313` `audit_logs`（`action` / `decision` / `trace_id`）—— 审计轨迹，
  不是 Decision / Evidence 记录。

**D-5 Kernel vs Runtime / 耦合（CONFIRMED）** — `NOT A KERNEL CANDIDATE`。
耦合风险 **YES**：Go module + 固定 Postgres schema + Milvus + Kafka + Redis + MinIO + Prometheus，
取任何一块都会拖进整个平台。

**D-6 复用等级**：Context **0** · Ontology **0** · Rules **1**（PDP 的
「policy 对象 → evaluate → Decision」接口形状可作确定性求值器的概念参考） · Decision **1**
（同前，但那是授权决策不是业务决策） · Evidence **0** · Provenance **1**（`audit_logs.trace_id`
的关联思路）。

**裁决 `CLOSE`**：8 个月不更新、1★、Agent 生成且提交了未解决的补丁冲突残骸，
且架构上正是我们明确不做的东西。

---

------------------------------------------------------------------------------

## 5. Candidate E — GSearchAI (`GramosoftAI/GSearchAI`, 自称 "GRAG") → **CLOSE**

> ⚠️ 修正一条我先前的记录：GitHub API 把语言报为 TypeScript，**实际后端是 Python（FastAPI）**，
> TypeScript 是前端。默认分支 `main`。

**E-1 License = ⭐ 硬阻断：根本没有 LICENSE 文件（CONFIRMED）**

`GET /repos/GramosoftAI/GSearchAI/license` → **404 Not Found**。遍历完整 recursive tree（538 个 blob），
**零个**文件名匹配 `licen` / `copying` / `notice`。

而 `README.md:10` 挂着 "License: MIT" 徽章，`:57`/`:67`/`:254` 以 "MIT-licensed" 宣传，
`:286` 还写 *"See the `LICENSE` file for details"* —— **那个文件不存在。**

> 法律默认（伯尔尼公约）：**无许可 = 保留所有权利。**
> 商业使用 ✘ / 修改 ✘ / 再分发 ✘ / SaaS ✘。**README 上的 MIT 主张没有法律效力。**

**E-2 仓库健康度（CONFIRMED）**

创建 2026-01-27。`main` 上最后提交 **2026-07-04**；★注意：GitHub API 的 `pushed_at`
（2026-09-19）来源 **UNKNOWN**（其它分支未能枚举，API 中途限流）。
2 位贡献者（`girinath-ai` 130 / `girinath18` 5）、0 releases。
`tests/` 存在但 `tests/__init__.py` 只有一行 `"""Test suite"""`；真正的测试是根目录散落的脚本
（`test_pipeline.py` / `test_query.py` / `test_labels.py`）。
`.github/workflows/deploy.yml` **不是 CI** —— 它是在自托管 runner 上执行
`git reset --hard origin/backdev`，由推送到 `backdev` 分支触发，与 `main` 无关。
仓库内另有 `response.md`（3.7 MB）、`vector.zip`、`scratch.py`、`patch_db.py`、`apply_ui.py`、
`rewrite.py`、`mydmoviedb (1).csv`、`tester_zone/`。

**E-3 它是什么（CONFIRMED）** — FastAPI + Pydantic 后端，企业 AI 搜索 / Graph RAG，
Neo4j + pgvector，强多租户（`tenant_id` 贯穿每条 Cypher 查询）。模块含 `auth` / `users` / `tenants` /
`connectors/{google,sharepoint}` / `etl` / `knowledge_bases` / `rag` / `graphs` / `ontology` /
`agents` / `jobs/worker` / `analytics` / `billing` / `chats`。

→ **它是"横向企业搜索 + RAG 平台"，正是铁律 3 / 红队 v3 判为死亡陷阱的那一类。**

**E-4 核心数据模型（CONFIRMED）**

- **Ontology 部分存在，但在 Kernel 意义上很薄、且不是本体**：
  `app/modules/ontology/schemas.py:9` `OntologyClassCreate`、`:13` `OntologyRelationCreate`、
  `:24` `OntologyRuleCreate{source_class, relation, target_class}`、`:46` `OntologyResponse{classes,relations,rules}`；
  持久化为普通 Neo4j 节点 —— `app/modules/ontology/service.py:25`
  `MERGE (c:OntologyClass {tenant_id: $tenant_id, name: $name}) SET c.description, c.embedding`。
  **`OntologyRule` 是三元组模式，不是确定性业务规则；无公理、无约束、无推理。**
  `app/core/ontology_resolver.py:9` `OntologyResolver` 是**基于 embedding 的共指消解**
  （`vector.similarity.cosine > 0.92`）—— **实体去重，不是本体推理**。
- Context **NOT FOUND**（只有 chat/conversation context） · Decision **NOT FOUND** ·
  Evidence/Provenance **NOT FOUND**。最接近的是 `app/core/business_objects.py:3` `ENTITY_GROUPS`
  —— 一个硬编码的确定性字段组字典（vin/gstin/hsn_code）。
  （ontology 两文件为 CONFIRMED；其余为 INFERRED 缺席——依据是文件清单，非全文阅读。）

**E-5 Kernel vs Runtime / 耦合** — `NOT A KERNEL CANDIDATE`。耦合风险 **YES**：
Neo4j + pgvector + Postgres + 其租户中间件 + embedding 服务；ontology 模块无法脱离整套
Neo4j session / 租户栈被拿出去。

**E-6 复用等级**：Context **0** · Ontology **1**（仅概念：OntologyClass/Relation 作为独立的
租户作用域图节点） · Rules **1**（三元组模式的规则形状） · Decision **0** · Evidence **0** · Provenance **0**。

**裁决 `CLOSE`**：**无任何许可证文件** —— 法律上不可读、不可跑、不可复制；
且无论如何它都是搜索/RAG 应用。

---

------------------------------------------------------------------------------

## 6. Candidate F — qKnow (`qiantongtech/qKnow`) → **CLOSE**

> 默认分支 `develop`。Java / Spring Boot 3.5.8。

**F-1 License = ⭐ 不是 Apache-2.0，而是「Apache-2.0 + 附加条件」（CONFIRMED）**

`LICENSE` 真实存在但 GitHub 归类为 NOASSERTION。读原文后确认：
> *"qKnow is made available under the Apache License 2.0, **subject to the following additional conditions**"*

- **商业使用：明确允许** —— 条件是不移除/不隐藏/不修改 qKnow 的 logo、版权声明、许可声明与署名信息。
- 修改 / 再分发 / SaaS：允许，**但白标、OEM、rebranding、或"把 qKnow 作为另一个产品呈现"
  需向江苏千通科技有限公司另购商业许可**。
- **附加条款 2a 允许 Producer 单方面收紧或放宽条款。**
- 每个源文件头部都带该声明（例：`DynamicEntity.java:1-17`）。

> 由于 Apache-2.0 禁止附加限制，**这在 OSI 意义上不是开源**，
> 而是 **source-available + 必须署名**。
> 净效果：**可以用，但不能不带品牌地交付，且条款可被对方单方面变更。**

**F-2 仓库健康度 = 本批三个中唯一健康的（CONFIRMED）**

280★ / 65 forks / 6 位贡献者（`yv597` 124、`guchunxiao` 66、`ld0621` 66、`chenjinyao424` 33、
`zilaeu` 27、`wangming1114` 1）。最后提交 **2026-09-11**（约 9 天前），**活跃**。
**0 个 GitHub Releases**，但版本是真实的（`版本更新为v2.4.3`、`sql/mysql/qknow-v2.4.0.sql`）。
**无 CI**（`.github/workflows` → Not Found）。测试树存在（`qknow-server/src/test/java/tech/qiantong/...`），
**存在性 CONFIRMED，覆盖深度 UNKNOWN**。仓库 181 MB。

**F-3 它是什么（CONFIRMED）** — RuoYi 风格多模块 Maven 企业知识 + Agent 平台：
`qknow-framework/{qknow-ai,neo4j,mybatis,redis,security,quartz,websocket,generator,file,thirdparty}`、
`qknow-module-{ai,app,dm,ext,kb,kg,kmc,system}`（各拆 `-api`/`-biz`）、Spring AI 作 LLM 抽象、
Vue 3/Vite 前端。kg = Neo4j 图；kmc = 摄取/切分/向量化；ext = 结构化+非结构化抽取；
kb = bots/agents/flows/skills/MCP/tools；ai = 模型市场。

**F-4 核心数据模型 —— 决定性发现（CONFIRMED）**

- **Ontology：NOT FOUND。** 存在的是**刻意的 schema-free 模型**：
  `DynamicEntity.java:37` `@Node class DynamicEntity extends BaseNeo4jEntity`，带
  `@DynamicLabels Set<String> labels` 与 `@CompositeProperty Map<String,Object> dynamicProperties`。
  另有 `ExtSchema` / `ExtSchemaAttribute` / `ExtSchemaRelation` —— 那是**数据库表→图 schema 的映射**，
  **不是本体**（无公理、无约束、无推理）。
- **Rules：NOT FOUND（作为可执行代码）。** "领域规则"只以 Markdown 散文形式出现
  （`fault-rules.md`，即 "Domain rules & thresholds, decision logic"），位于技能包
  `uploads/skills/pump-fault-detector/` 内。
- **Decision / Evidence / Provenance：NOT FOUND** 作为一等对象。
- **Context：存在，但含义是错的** —— `KbRuntime` 是**流程执行的变量表**
  （flow engine 里的 "Runtime Context & Traversal Engine"），
  即 **runtime context，不是 Kernel Context**。⚠️ 这是一个**命名陷阱**：
  名字重合会让人误以为它提供企业上下文。

**F-5 Kernel vs Runtime / 耦合** — `NOT A KERNEL CANDIDATE`。它拥有流程编排
（`KbFlowServiceImpl`、节点 BO、`POST /kb/flow/executeFlow`）、MCP 工具集成、技能注册表、
bots/agents、Spring AI 模型路由、RAG、Neo4j 存储、Quartz 调度、websockets ——
**覆盖我们拒绝拥有的一切 RUNTIME 项，外加我们只打算消费的大部分能力**。
耦合风险 **YES，且是最大的一档**：Java/Spring beans、MyBatis-Plus + MySQL + Neo4j + Redis、
RuoYi 安全约定、Maven 多模块、Flyflow 画布（Vue）。与 Python Kernel **无运行时交集**。

**F-6 复用等级**：Context **0** · Ontology **1**（仅概念：`@DynamicLabels` + composite-property
的 schema-flexible 图建模思路可参考） · Rules **0** · Decision **0** · Evidence **0** · Provenance **0**。

**裁决 `CLOSE`** —— 直接回答指令 §7「能不能复用」：**Python Kernel 在这里除概念参考外什么都拿不到**，
没有**任何一个类**能在没有 Spring 容器、MyBatis mapper、Spring Data Neo4j repository 与 RuoYi 认证的
情况下被 import；且许可证要求任何被采纳的产物**必须保留 qKnow 品牌可见**，同时对方**可单方面改条款**。
我们关心的 Kernel 概念（Ontology / Rule / Decision / Evidence / Provenance）在代码里是**缺席**，
不是不成熟。

------------------------------------------------------------------------------

## 7. Candidate G — KnowledgeOps Agent → **REFERENCE ONLY**

> ⚠️ **坐标由我推断**：指令未给仓库路径，GitHub 上无同名仓库。
> 本记录的对象是 `however-yir/knowledgeops-agent`（194★ Java MIT）。
> **若指令所指另有其库，本节作废。**

**G-1 License = MIT，干净（CONFIRMED）**
`LICENSE` 21 行标准 MIT，"Copyright (c) 2026 however-yir"。
商业使用 ✔ / 修改 ✔ / 再分发 ✔ / 再许可 ✔ / SaaS ✔。无专利授权（MIT 的常规注意点）。

**G-2 仓库健康度 = 意外地扎实（CONFIRMED）**

| 信号 | 值 |
|---|---|
| 最后提交 | **2026-09-07（约 13 天前）——活跃，未停更** |
| Stars / forks | 194★ / **仅 4 位贡献者**（`however-yir` 136、`Randycarteronion` 29） |
| Releases | `v1.0.0`、`ai-matrix-baseline-2026-05`、`maintenance-2026-08-23` |
| CI | ⭐ **异常严格**：`ci.yml` 含强制静态分析 + **JaCoCo 覆盖率门禁** + CycloneDX SBOM，
  外加一个 **evaluator-contract job**，断言 **citation-hit ≥ 0.70 且 hallucination ≤ 0.05**；
  另有 `nightly-regression.yml`、`baseline-ci.yml`、`ragproof-external.yml` |
| 测试 | 38 个测试类，含 WebMvc、**Testcontainers**、**租户隔离测试** |
| 工程卫生 | `CHANGELOG` "Unreleased" 记录了 MCP 适配器的 **SSRF 加固**、**跨租户任务劫持修复**、SQL `LIKE` 注入修复 |

> 这是我们考察过的**全部 9 个候选里 CI/安全工程最像样的一个**。
> 值得单独记下：**它把"citation 命中率 ≥0.70 / 幻觉率 ≤0.05"写成了 CI 契约** ——
> 这与我们 E1–E6 的评测门禁是同一种思路，可作为"评测即门禁"的外部佐证。

**G-3 它是什么（CONFIRMED）** —— 生产导向的**企业 RAG + ReAct Agent 平台**，不是 kernel。
Java 17 / Spring Boot + MyBatis-Plus、pgvector 混合检索（向量+关键词+图+web，带 reranker）、
Redis-Stream/RabbitMQ 摄取队列（带 DLQ 与重试）、JWT + API-key + RBAC + 多租户、
Prometheus/Loki/Tempo、Vue3 控制台、Helm chart。

**G-4 核心数据模型（CONFIRMED）**

- **规则/策略：真实存在** —— `agent/harness/ActionPolicyGuard.java:22`
  `evaluate(AgentAction)` 返回**带类型的拒绝原因**（`unsupported_action` / `tenant_action_denied` /
  `invalid_action_input`），由 `ActionSchema`/`ActionSchemaRegistry` 支撑。
- **工作流状态：真实存在** —— `agent/workflow/WorkflowState.java:3` 枚举，带**显式的
  `canTransitionTo` 转移表**（`JUDGING` / `REFLECTING` / `NEED_MORE_EVIDENCE` …），
  在 `AgentWorkflowEngine.java:107` 强制执行。
- **本体：浅** —— `kg_entity`/`kg_relation`/`kg_fact`（`V11__knowledge_graph_tables.sql`）、
  `graph/KgFactRecord.java` 带 `validFrom`/`validTo`/`confidence`：
  一个**带时态的三元组存储，没有类、没有公理**。
- **Decision：NOT FOUND** 作为持久化一等对象。
- **Context：仅会话/记忆记录**（`V12__memory_system_tables.sql`）。
- **Audit：`domain/AuditLog.java` 是 HTTP 访问日志**（`method`/`path`/`statusCode`/`durationMs`），
  **不是决策溯源**。

**G-5 ⭐ Evidence 不是一等对象 —— 这是决定性的一条（CONFIRMED）**

`retrieval/EvidenceItem.java` 是**从 RAG chunk 临时构造的内存 DTO**；
`retrieval/EvidenceJudgeService.java` 用**硬编码权重**给它打分
（`RELEVANCE_WEIGHT = 0.50`、`AUTHORITY_WEIGHT = 0.30`、`TIMELINESS_WEIGHT = 0.20`），
并把内容**截断到 180 字符的摘要**。任何迁移里都**没有 `evidence` 表**
（V1/V8/V10/V12 零命中；V11 只在 `kg_relation` 上有一个可空的 `evidence_id VARCHAR` 列）。
Evidence 只以字符串形式存活在 observation map 里（`service/ReactAgentService.java:73-74`）。

> 所以它实现的是**重新打分的 RAG 引用**，**不是受治理的业务证据**。
> 这与我们 `KERNEL_BOUNDARY.md:188-195` 的 Business Evidence 定义不相交。

**G-6 Kernel vs Runtime / 耦合** —— 主体是 **Runtime**（ReAct 循环、工具执行、摄取队列、
重试/DLQ、调度、workspace 沙箱）。与 Kernel 沾边的只有确定性规则/决策（那个 guard），
而它的状态机属于**工作流执行**，即我们的 RUNTIME 边界。
耦合风险 **YES**：抽取任何部分都会拖进 Spring Boot、MyBatis-Plus、MySQL schema，
以及一个**贯穿每个 mapper 的租户/权限模型**。

**G-7 复用等级**：Business Rules / Decision **1–2**（guard 很小且概念上可移植，但 Spring 绑定） ·
Workflow state **1** · Ontology/KG **1**（过浅） · Security/audit **1** · Evidence **0**。

**裁决 `REFERENCE ONLY`** —— 可复用的是**两个想法**：
`ActionPolicyGuard` 的**带类型拒绝码**模式，与 `WorkflowState.canTransitionTo` 的**显式转移表**。
（对我们自己的问题：指令问"Workflow State / Security / Evidence 是否有可复用实现"——
**Workflow State 与 Security 确实有，Evidence 没有**。）

---

------------------------------------------------------------------------------

## 8. Candidate H — mcp-agent-framework → **REFERENCE ONLY**

> ⚠️ **坐标由我推断**：**GitHub 上不存在**名为 `mcp-agent-framework` 的仓库。
> 本记录的对象是 `lastmile-ai/mcp-agent`（8,549★ Python Apache-2.0）。
> **若指令所指另有其库，本节作废。**

**H-1 License = Apache-2.0，干净（CONFIRMED）**
`LICENSE` 201 行完整标准文本（11,357 字节）。商业使用 ✔ / 修改 ✔ / 再分发 ✔ / SaaS ✔，
含专利授权，无 copyleft。

**H-2 仓库健康度 = 已休眠（CONFIRMED）**
**最后 push 2026-01-25 → 约 8 个月未更新**，**138 个未关 issue**，实质上已休眠。
其他指标本不错：60 位贡献者（`saqadri` 342、`evalstate` 108）、8,549★、891 forks、
release 到 `v0.2.4`、真实 `tests/`、CI 完备
（`checks.yml`/`main-checks.yml`/`pr-checks.yml`/`publish-pypi.yml`/`release-drafter.yml`）。

> **休眠是对 RUNTIME 层候选的实质扣分**：我们的 Runtime 会被 Kernel 长期依赖，
> 选一个停止维护的宿主是把自己锁死在别人的停止线上。

**H-3 它是什么（CONFIRMED）** —— Agent Runtime + MCP 客户端/服务端框架。
代码证据：`src/mcp_agent/agents/agent.py`（62KB）、`executor/workflow.py`（32KB）、
**`executor/temporal/`（durable execution）**、`workflows/`（orchestrator / router / swarm /
parallel / evaluator-optimizer / intent-classifier / `deep_orchestrator/`）、
`mcp/mcp_aggregator.py`（59KB）、`server/app_server.py`（**129KB**），
以及一个**还能把应用部署到厂商云**的 CLI（`cli/cloud/commands/deploy/`、`docs/cloud/`）。

**H-4 核心数据模型 = 无任何 Kernel 形状的对象（CONFIRMED）**
- `core/context.py:66 class Context(MCPContext)` —— **是 server 注册表 + 配置容器，不是领域上下文**
- 最接近的是 runtime 作用域的：`workflows/deep_orchestrator/models.py:41 KnowledgeItem`
  （`key, value, source, confidence, category`）、`models.py:26 PolicyAction`
  = `CONTINUE | REPLAN | FORCE_COMPLETE | EMERGENCY_STOP`
- **Rules / Evidence / Ontology：NOT FOUND**

**H-5 ⭐ Evidence 不是一等对象（CONFIRMED）**
在 `core/context.py` 与 `deep_orchestrator/knowledge.py` 全库搜 "evidence"：**0 命中**。
所谓 "policy engine"（`workflows/deep_orchestrator/policy.py:24`）决定的是
**何时重规划或停止** —— 是 runtime 控制，不是业务规则，且**不产生持久化决策记录**。

**H-6 Kernel vs Runtime / 耦合** —— `NOT A KERNEL CANDIDATE`。
它占据的正是我们的 **RUNTIME 边界**（agent loop、工具执行、工作流执行、重试、subagents、
Temporal durable execution），且不提供我们六项 KERNEL 能力中的任何一项。
耦合风险 **YES**：采用 `executor/` + `workflows/` 会拖进 **Temporal**、MCP session/aggregator 栈，
以及**厂商云 CLI 面**。

**H-7 复用等级**：MCP 消费 **2**（成熟的独立客户端） · 模型网关
（`workflows/llm/augmented_llm_*`，覆盖 Anthropic/OpenAI/Google/Bedrock/Azure）**2** ·
Context / Rules / Decision / Evidence **0** · agent-loop 与 workflows **0**（越界）。

**裁决 `REFERENCE ONLY`** —— 如指令所预测，它是 **Agent Runtime reference 而非 Kernel foundation**；
可选地借鉴其 MCP 客户端，但它不提供任何 kernel 形状的东西。

---

------------------------------------------------------------------------------

## 9. Candidate I — DataLogicEngine → **CLOSE**（但见 I-5：它是**唯一的 Evidence 正面样本**）

> ⚠️ **坐标由我推断**：指令未给仓库路径。本记录的对象是
> `kherrera6219/DataLogicEngine`（**6★** Python）。**若指令所指另有其库，本节作废。**

**I-1 ⭐ License = PolyForm Noncommercial 1.0.0 —— 商业复用硬阻断（CONFIRMED，独立核验）**

指令特别要求："尤其注意 LICENSE 是否允许商业产品直接使用。**如果许可证存在商业限制，必须明确标记。**"
—— **存在，且是硬阻断。** 我独立拉取 LICENSE 前 25 行，原文：

```
NOTICE: DATA LOGIC ENGINE LICENSE CHANGE
Effective 2026-01-15, this project has moved from the MIT License to the
PolyForm Noncommercial License 1.0.0.

Personal and educational use remains free.
Commercial use, production deployment in a business environment, or
integration into a paid product requires a separate commercial license
agreement.

Contact: kherrera3250@gmail.com for commercial licensing inquiries.
```

- GitHub 报 `NOASSERTION` 只是因为 **PolyForm 在 SPDX API 里没有条目**，文件文本毫无歧义。
- 商业使用、**在企业环境中的生产部署**、作为商业产品的托管/管理访问、
  **支持营收性业务的内部使用**、以及**打包进售卖产品** —— **全部需要另签付费商业许可**
  （`COMMERCIAL_LICENSE.md`，实测 HTTP 200）。
- 1.4.0 及更早版本仍是 MIT（追溯效力），**对当前代码无效**。
- ⚠️ **MIT 的 SDK 不是漏洞**：`sdk/UKG_Python_SDK`、`DataLogicEngine_TypeScript_SDK` 是
  **只调用已安装 gateway 的薄客户端**，且 `sdk/LICENSE_NOTICE.md`（HTTP 200）明文说明
  再分发由 **应用许可** 而非 SDK 的 MIT 条款管辖。

> **判定：未经谈判取得商业许可，不可用于商业产品。**

**卫生红旗（CONFIRMED）**：版本号三处互相矛盾 —— `pyproject.toml` `version = "4.4.3"`、
LICENSE 写 "1.5.0 and later"、仓库**唯一一个 tag 是 `V1.0.4`**。

**I-2 仓库健康度 = 活跃但画像很差（CONFIRMED）**

最后 push **2026-08-31（约 20 天）**，但：6★；3 位贡献者**实际是一个人**
（`kherrera6219` 1117 + `KevinHerrera21` 232）外加 `claude`（77，AI 辅助提交）；
**3,074 个文件 / 386 MB**；只有一个 tag。
CI 存在（`ci.yml`/`security.yml`/`deploy.yml`/`code-signing-governance.yml`/`release-installer-signing.yml`）。
**文档体量压倒代码**：`HANDOFF.md` 110KB、`TODO.md` 115KB、
`PRODUCTION_COMPLETION_PLAN_2026.md` **378KB**、`CHANGELOG.md` 133KB、
`docs/FILE_INVENTORY.csv` 227KB，外加 20 个阶段的 `reports/production-readiness/` 目录树。

> 指令 §17 的精神在这里适用：**"17-Axis / 10-Layer Truth Engine" 这类框架叙事，
> 在代码说话之前应视为营销。**

**I-3 它是什么（CONFIRMED）** —— 单体 Flask + Next.js/Electron "企业 AI 平台"，
架在自述的 Universal Knowledge Graph 上，含 GraphRAG 管道、MCP server、治理/合规模块、
本地优先的桌面部署。真实代码：根 `app.py`（90KB）、`models.py`（**164KB，87 个 SQLAlchemy 模型**）、
`backend/ukg_db.py`（46KB）、`core/coordinate_system.py`（41KB）、
`backend/truth_engine/{truth_core,truth_gate,truth_link,truth_memory}` 等。

**I-4 核心数据模型 —— 我们考察过的全部候选里最丰富（CONFIRMED）**

- **Evidence**：`models.py:1825 TraceEvidence`，带 `run_id`、`source_type`/`source_id`/`source_title`、
  `authority`、`captured_at`/`effective_at`/`retrieved_at`、`permissions`、`transformation_chain`、
  `locator`（page/section/line_range）、**`content_hash`（sha256）**、`retrieval_method`、
  五个评分含 **`provenance_completeness`**，以及 `used_by_claims`/`personas`/`stages`
- **Claim**：`models.py:1928 TraceClaim`（`answer_span_start/end`、
  `status = supported|partial|unsupported|contested`、`evidence_ids`）
- **Claim↔Evidence 链接**：`models.py:2189 ClaimEvidenceLink`（**一等的关系对象**）
- **证据冲突**：`models.py:2386 EvidenceConflict`（`evidence_a_id`、`evidence_b_id`、`resolution`）
- **Decision**：`models.py:2090 TracePolicyDecision`
  （`policy_id`、`rule_id`、`decision = allow|block|flag|redact`、`rationale`、`modifications`）、
  `models.py:2259 TraceQualityDecision`
- **Audit/治理**：`models.py:2844 TruthAuditEvent`、`models.py:1021 AIAuditEvent`

**I-5 ⭐ Evidence 是一等对象 —— 本次研究中唯一的正面样本（CONFIRMED）**

除 `TraceEvidence` 外，`backend/compliance/evidence.py` **强制执行硬契约**：
```python
REQUIRED_FIELDS = {control_id, claim_type, check_version, executed_at,
                   scope, result, evidence_ref, source_record}
```
当展示出的合规结论缺少证据时**抛 `ComplianceEvidenceError`**。

并且它有**真实的规则引擎**：`policies/truthgate.rego`（**OPA/Rego**）规定
`critical_domain`（医疗/金融/法律/安全）要求 **confidence ≥ 0.995 且必须有 human-review 闸门**；
经 `backend/truth_engine/truth_gate/opa_policy.py` 的 `OPAPolicyEvaluator` 求值
（subprocess 调 OPA，**带确定性 Python 回退**），并折算进 `confidence_calculator.py`
（权重 0.35/0.30/0.20/0.15）。

> ⭐ **这是本研究里最重要的一条正面证据**：它是唯一一个**把 Business Evidence 做成一等的、
> 带溯源的对象**——有 content hash、有 locator（页码/章节/行范围）、有 authority、
> 有 `provenance_completeness` 评分、有独立的 Claim 对象和 Claim↔Evidence 关系、
> 甚至建模了**证据冲突**（`EvidenceConflict`）。
> 这直接对应我们**尚未存在**的 Evidence 层（见 `FOUNDATION_REUSE_MATRIX.md` §2 的"现有实现状况"列）。
>
> **但它的许可证禁止商业复用。** 所以结论只能是：
> **读它的数据模型，然后自己写。** 这不是遗憾，而是一个清晰的结论——
> Evidence 的形状是**可借鉴的（Level 1）**，代码是**不可用的（Level 0）**。

**I-6 Kernel vs Runtime / 耦合** —— 它**确实含有 Kernel 形状的素材**
（Evidence、Decision、Rules、Governance、Audit、axis/time Context），
但它们以**不可分割的 Agent + RAG + 桌面平台**形态交付，正是我们**绝不能变成**的通用企业平台。
**不是可导入的底座。** 耦合风险 **YES，严重**：386MB / 3,074 文件的单仓、
87 模型的单体、单厂商许可、Flask + Electron + Neo4j + Postgres + Redis + Chroma，
且过程产物（文档）体量压倒代码。

**I-7 复用等级**：Evidence **1**（**概念级——许可阻断代码**） · Decision/Governance **1** ·
Rule engine **1**（那个 Rego 闸门很小且可读） · Ontology/Context **0–1**。

**裁决 `CLOSE`** —— PolyForm Noncommercial **排除了任何商业代码复用**（除非另签付费协议），
因此**没有一行进入代码库**；值得在关掉标签页之前读一遍的只有
`TraceEvidence`/`TraceClaim`/`EvidenceConflict` 的 schema 与那个 Rego truth-gate。

---

------------------------------------------------------------------------------

## 10. Tier-2 六个候选的交叉结论（不是排名）

把 D–I 放在一起，出现一条规律，它比任何单个候选的优劣都重要：

```
许可干净的那三个（mcp-agent Apache-2.0 / knowledgeops-agent MIT / OpenEAAP Apache-2.0）
        → 都不是 kernel 形状：一个是已休眠的 Agent Runtime，
          一个是 RAG 平台，一个是 1★ 且停更的 Agent 平台

把 Evidence 当一等对象的那个（DataLogicEngine）
        → 许可证（PolyForm Noncommercial）禁止商业复用；且它自己是不可分割的平台

Kernel 概念真正缺席的那三个（GSearchAI / qKnow）
        → 一个根本没有 LICENSE、一个与 Python 无运行时交集
```

**在 Tier-2 里，"许可证可用"与"形状像 kernel"没有同时出现过一次。**

（该规律在 Tier-1 出现了一个明确破例 —— **Semantica**，见 §12.1。）

---

------------------------------------------------------------------------------

## 11. 横切分析（指令清单外的补充发现）：Evidence 字段级覆盖

> ⚠️ **这一节不是指令要求的**，是我在完成候选考察后做的一次横切比对，
> 因为它直接服务指令 §20 的结论 D（"哪些部分必须自己拥有"）。
> **Codex 可以接受或否决这一节，它不影响主报告的其他结论。**

`KERNEL_BOUNDARY.md:190` 定义 Business Evidence 至少要能表达 8 个字段
（指令 §九 列的是同一组）：**来源 / 主张 / 时间 / 行为人 / 触发 Agent / 所用 Context / 决策 / 执行引用**。

把全部候选的**代码**（不是文档）逐字段比对，结果是：

| V3 Evidence 字段 | DataLogicEngine<br>（许可阻断） | TrustGraph | HugAgentOS | W3C PROV-O |
|---|---|---|---|---|
| **来源 source** | ✅ `source_type`/`source_id`/`source_title` + **`locator`(page/section/line_range)** + **`content_hash`(sha256)** | ✅ 抽取血缘（document/chunk/model） | ⚠️ 仅 `citations` blob（截断 2000） | ✅ `prov:wasDerivedFrom` / `prov:Entity` |
| **主张 claim** | ✅ `TraceClaim`（`answer_span_start/end`、`status = supported\|partial\|unsupported\|contested`） | ❌ | ❌ | ❌ **无对应概念** |
| **时间 time** | ✅ **三个时间**：`captured_at` / `effective_at` / `retrieved_at` | ❌ 全库**无任何时态谓词** | ❌ | ✅ `prov:atTime` / `generatedAtTime` |
| **行为人 actor** | ⚠️ 仅有 `permissions`，未单列 actor 字段 | ❌ | ❌ | ✅ `prov:Agent` + `prov:wasAttributedTo` |
| **触发 Agent triggering agent** | ❌ | ⚠️ agent 轨迹层，**与证据不关联** | ❌ | ✅ `prov:Agent` 可承载 |
| **所用 Context context** | ⚠️ `used_by_claims` / `personas` / `stages` | ❌ | ❌ | ✅ `prov:used` |
| **决策 decision** | ✅ `TracePolicyDecision`（`policy_id`/`rule_id`/`decision = allow\|block\|flag\|redact`/`rationale`/`modifications`） | ❌ | ⚠️ `ontology_enforcement_events.decision` —— 但那是**门禁裁决，不是业务决策** | ❌ **无对应概念** |
| **执行引用 execution reference** | ⚠️ `run_id` | ⚠️ 检索图 / agent 轨迹 | ⚠️ trace | ✅ `prov:Activity` |
| **合计覆盖** | **≈6/8（最高）** | 1.5/8 | 0.5/8 | **6/8，但缺的正是最关键的 2 个** |

### 11.1 三条结论

**结论一：没有任何一个项目把 8 个字段都建模了。**
覆盖最高的 DataLogicEngine 约 6/8，**而它的许可证禁止商业复用**（§9）。
第二高的 PROV-O 是**标准**，不是实现。

**结论二：⭐ PROV-O 是必要条件，但不是充分条件。**
PROV-O 恰好覆盖**溯源那一半**（来源 / 时间 / 行为人 / 触发 Agent / 所用 Context / 执行引用），
**但没有 `Claim` 概念，也没有 `Decision` 概念。**

> 这给出一条**成本为零、收益长期**的建议：
> **Evidence 的溯源子模型对齐 PROV-O（Level 1，借鉴标准而非项目），
> 而 Claim 与 Decision 的语义必须由 Kernel 自己定义。**
> 对齐标准不需要引入任何依赖、不需要改架构——只是**字段命名与关系形状**的选择。
> 反过来，若 Kernel 自创一套与 PROV-O 不兼容的溯源词汇，未来接任何企业治理/审计工具都要做映射。

**结论三：两个字段在**所有候选**里都没有被建模 —— 它们必然是自建。**

- **`triggering agent`（触发 Agent）**：**没有任何一个项目把"哪个 Agent 触发了这条证据"
  与证据对象关联起来**（TrustGraph 有 agent 轨迹，但轨迹与证据不挂钩）。
- **`claim`（主张）**：**只有 DataLogicEngine 把它做成了一等对象**，而它许可阻断。

> 这正是 `KERNEL_BOUNDARY.md:195` 那句话在代码层面的印证：
> "**企业场景里真正被追问的是前者：「你为什么得出这个结论？依据在哪？谁批准的？」**——
> DSH 的 Trajectory 回答不了这个问题，Trigger.dev 的 tracing 也回答不了。"
> **实测结论：开源的 tracing / trajectory / lineage 也都回答不了。**

### 11.2 一条值得借用的具体设计（非显而易见）

DataLogicEngine 在 Evidence 上放了**三个时间戳**，而不是一个：

```
captured_at    —— 我们是什么时候采集到它的
effective_at   —— 它在现实世界里是什么时候成立的
retrieved_at   —— 我们是什么时候把它取回来的
```

这正好对应我们 `KERNEL_BOUNDARY.md:88` 行 24 的 **Temporal Context** 要求
（审计/合规场景里"这条政策在审计期内是否有效"是必须回答的），
也解释了为什么单时间戳不够：**"采集时间"与"事实成立时间"不是同一件事**。

> 建议：**Kernel 的 Evidence 至少建模这三个时间**。
> 这是本研究里少数几条"可以直接抄的设计"之一 —— 而且**不需要引入它的任何代码**。

---

------------------------------------------------------------------------------

## 12. 结论：全部九个候选的裁决汇总

| # | 候选 | License | 裁决 | Kernel 六项能力的最大可得等级 |
|---|---|---|---|---|
| A | HugAgentOS | Apache-2.0 **+ 附加条款**（多租户 SaaS / 白标受限） | **REFERENCE ONLY** | Domain Ontology / Business Rules = **2**（带重要保留） |
| **B** | **Semantica** | **MIT（纯，无 CLA）** | ⭐ **CONSUME PIECES**（不是整体嵌入） | **Provenance = 3 · Context Update = 3 · Context Model = 3（带保留）**；**Evidence = 0 · Business Rules = 1** |
| C | TrustGraph | Apache-2.0（干净；CLA 正文 UNKNOWN） | **REFERENCE ONLY** | Provenance = **2**（事实血缘，非业务证据） |
| D | OpenEAAP | Apache-2.0（干净） | **CLOSE** | 全部 0–1 |
| E | GSearchAI | **无 LICENSE**（法律阻断） | **CLOSE** | Ontology / Rules = 1 |
| F | qKnow | Apache-2.0 **+ 附加条件**（必须署名、条款可变） | **CLOSE** | Ontology = 1 |
| G | KnowledgeOps Agent | MIT（干净） | **REFERENCE ONLY** | Rules / Decision = 1–2 |
| H | mcp-agent | Apache-2.0（干净，**已休眠**） | **REFERENCE ONLY** | MCP / Model Gateway = 2 |
| I | DataLogicEngine | **PolyForm Noncommercial**（商业阻断） | **CLOSE**（但唯一 Evidence 正样本） | Evidence = **1**（概念，代码不可用） |

> ⚠️ **再次强调（指令 §4 禁令）**：本表**不是排名**。
> "最大可得等级"列比较的是**不同层的能力**（Ontology vs MCP vs Evidence），
> 把它们横向比大小没有意义，只是为了让 Codex 一眼看到"哪个候选对我们哪一项有用"。

### 12.1 贯穿性规律的**成立与破例**

先看规律。把九个候选并排看：

```
许可干净的项目            → 多数不是 kernel 形状（Runtime / 平台 / 搜索 / 已休眠）
形状像 kernel 的项目      → 多数许可被阻断（DataLogicEngine 是典型）
Kernel 概念真正缺席的项目 → 要么停更（OpenEAAP 1★）、要么根本没有 LICENSE（GSearchAI）、
                            要么与 Python 无运行时交集（qKnow）
```

**但这条规律有一个明确的破例，而且它是本研究最重要的正面结果：**

> ⭐ **Semantica（候选 B）同时满足"许可可直接商用（纯 MIT）"与"形状像内核"。**
> 它在 **Provenance、Context Update、Context Model** 三项上达到 **Level 3（Foundation reuse）**，
> 且基础安装**零必需基础设施**（纯内存 + rdflib/networkx，重依赖全在 extras）。

**所以结论不是"不存在可用的 OSS"，而是"可用的 OSS 只覆盖 Kernel 六项里的三项，
且覆盖的恰好不是我们最难的两项"** —— 见 §12.2。

### 12.2 ⭐ 六项 Kernel 能力 × 最佳可得（本研究的核心结论表）

| Kernel 能力（`V3_CLOSEOUT.md:29-35`） | 全候选最佳 | 出处 | 我们是否仍需自建 |
|---|---|---|---|
| **Context**（含 Entity/Relation/Temporal/Permission scope） | **Semantica Level 3**（结构化 + 双时态部分） | §2.4 / §2.12 | ⚠️ **部分** —— **Permission scope 必须自建**（Semantica 权限只有 REST auth，Level 1） |
| **Domain Ontology** | HugAgentOS **2** / Semantica **1** / TrustGraph **1** | §1.9 / §2.12 / §3.12 | ⚠️ **基本自建** —— 现有三者要么是演示模板、要么是 LLM 抽取词表、要么是基础设施自描述 |
| **Deterministic Business Rules** | Semantica **1**（引擎确定性、规则语言是桩） | §2.8 | ✅ **必须自建**（引擎可借作推理后端） |
| **Decision** | Semantica **2/3** | §2.4 / §2.12 | ⚠️ **形状可借，语义自建** |
| **Evidence** | DataLogicEngine **1**（概念；代码许可阻断）· Semantica **0** | §9 / §2.5 | ✅ **必须完全自建** —— **全部九个候选里没有一个把 Business Evidence 建成了可用的一等对象** |
| **Context Update** | **Semantica Level 3**（时态撤回 + `state_at()` + 快照恢复） | §2.6 | ⚠️ **设计可借**；但决策变更与证据累积的 API **不存在**，须自建 |

> **一句话**：**开源能替我们做"上下文与溯源"，做不了"证据与规则"。**
> 而 `V3_CLOSEOUT.md:101-102` 说得很清楚 —— 判一个 Kernel 不是规则引擎 + RAG 的，
> 正是链尾的 Context Update；而 Evidence 与 Deterministic Business Rules 是 Kernel 的核心资产。
> **换句话说：开源最好的那部分，正好不是我们的差异化所在。**

------------------------------------------------------------------------------
