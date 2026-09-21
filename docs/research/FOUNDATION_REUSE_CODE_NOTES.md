# FOUNDATION_REUSE_CODE_NOTES.md

> 本文件是 `FOUNDATION_REUSE_STUDY.md` 的**证据附录**：逐仓库的**代码级**考察记录
> （文件路径:行号 + 原文片段）。STUDY 给结论，本文件给结论的出处。
>
> **本阶段纪律（指令 §19）**：NO PRODUCTION CODE CHANGE / NO ARCHITECTURE CHANGE /
> NO DEPENDENCY INSTALL / NO OSS VENDOR-IN / NO FORK / NO MIGRATION / NO DATABASE CHANGE /
> NO V0 CHANGE / NO PRD CHANGE。本文件与另两份研究文档是**唯一**产出。
>
> Last Verified: 2026-09-20

---

## 0. 方法与可复现性

### 0.1 证据分级

沿用仓库既有体例（`docs/research/evidence-matrix.md` 表头）：

| 级别 | 含义 |
|---|---|
| **CONFIRMED** | **读过源码**并给出 path:line / URL 与原文片段 |
| **STRONGLY_INFERRED** | 多处官方来源交叉印证，但未定位到具体代码行 |
| **INFERRED** | 只有 README / 文档 / 项目自述支持 |
| **UNKNOWN** | 证据不足。**不得作为设计前提** |

本文件的目标是让每一条 CONFIRMED 都能被第三人复现；凡只能从 README 得到的结论，
一律降为 INFERRED，**不因为项目宣传语而升级**。这是指令 §17 的硬要求。

### 0.2 访问通道（复现用）

三个 Tier-1 仓库与 qKnow 已在 zread 索引中，可直接读文件：

```
mcp__zread__get_repo_structure(repo_name="<owner>/<repo>", dir_path="/")
mcp__zread__read_file(repo_name="<owner>/<repo>", file_path="<path>")
```

`turtacn/OpenEAAP`、`GramosoftAI/GSearchAI`、`lastmile-ai/mcp-agent`、
`however-yir/knowledgeops-agent`、`kherrera6219/DataLogicEngine` **不在** zread 索引
（前两个调用返回 `repo not found`）——注意这是**索引缺失，不是仓库不存在**：
经 GitHub API 核实六个仓库全部真实存在（见 §0.3）。这几个仓库改用原始文件通道：

```bash
# 默认分支
curl -s https://api.github.com/repos/<owner>/<repo> | python3 -c "import json,sys;print(json.load(sys.stdin)['default_branch'])"
# 文件清单
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1"
# 单文件
curl -s https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>
```

### 0.3 候选仓库坐标核实（第一步，before any code reading）

指令给出的候选里，**两个仓库坐标在 GitHub 上无法直接命中**，三个**根本没有给坐标**。
下表是核实结果——这是本研究的第一个发现：**候选清单本身需要先修正**。

| 指令中的名称 | 核实结果 | 说明 |
|---|---|---|
| Candidate A `ZJU-REAL/HugAgentOS` | ✅ 存在 | 1,109★ Python，pushed 2026-09-20 |
| Candidate B `semantica-agi/semantica` | ✅ 存在 | 13,310★ Python，pushed 2026-09-20 |
| Candidate C `trustgraph-ai/trustgraph` | ✅ 存在 | 2,736★ Python，pushed 2026-09-20 |
| Candidate D `turtacn/OpenEAAP` | ✅ 存在（zread 未索引） | **1★，Go，pushed 2026-01-21**，默认分支 `master`，Apache-2.0（干净） |
| Candidate E `GramosoftAI/GSearchAI` | ✅ 存在（zread 未索引） | 26★，pushed 2026-09-19（来源 UNKNOWN），**后端实为 Python/FastAPI**（前端 TS），**无 LICENSE 文件** |
| Candidate F `qiantongtech/qKnow` | ✅ 存在 | 280★ Java，pushed 2026-09-11，默认分支 `develop`，**非 OSI 开源**（Apache+附加条件） |
| Candidate G "KnowledgeOps Agent" | ⚠️ **坐标缺失** | 无同名仓库；最接近者为 `however-yir/knowledgeops-agent`（194★ Java MIT） |
| Candidate H "mcp-agent-framework" | ⚠️ **坐标缺失** | **不存在**同名仓库；最接近者为 `lastmile-ai/mcp-agent`（8,549★ Python Apache-2.0，pushed **2026-01-25**） |
| Candidate I "DataLogicEngine" | ⚠️ **坐标缺失** | 最接近者为 `kherrera6219/DataLogicEngine`（**6★** Python，**NOASSERTION license**） |

### 0.3.1 逐候选裁决（随研究推进更新）

| 候选 | 裁决 | 依据 |
|---|---|---|
| A HugAgentOS | **REFERENCE ONLY** | §1 —— 唯一有真实 ontology 表 + **零 LLM 确定性闸门**的候选，但：**无 Entity / 无 Business Evidence / 无 Context Update / 无领域语义扩展接口**；闸门与 AgentScope 中间件**结构性耦合**；是**只读下游镜像**（`CONTRIBUTING.md:9-13`）；后端**无 CI**；ontology 表**不在任何迁移里**。许可证另有条件（见 §1.1） |
| B Semantica | ⏳ 深潜进行中 | — |
| C TrustGraph | **REFERENCE ONLY** | §3 —— Apache-2.0 干净，但 **不可嵌入**（broker 强制，`pubsub.py:29-38`）；`Context/Rules/Decision/Evidence/Context Update` **全部 NOT FOUND**；provenance 是**事实血缘**不是业务证据；**agent trace 与业务事实同表**（存储层不可区分）；IAM 自述"信任总线"，与铁律 1 正相反 |
| D OpenEAAP | **CLOSE** | §4 —— 8 个月停更、1★、Agent 脚手架生成且提交了未解决的补丁冲突残骸；架构上是 Agent Runtime |
| E GSearchAI | **CLOSE** | §5 —— **无 LICENSE 文件**（README 自称 MIT 无效）；横向企业搜索 + RAG 平台 |
| F qKnow | **CLOSE** | §6 —— 与 Python Kernel 无运行时交集；许可证要求保留品牌且条款可被单方面变更；Kernel 概念在代码里缺席 |
| G KnowledgeOps Agent | **REFERENCE ONLY** | §7 —— MIT 干净、CI 意外扎实，但 Evidence 不是一等对象；可借鉴 `ActionPolicyGuard` 拒绝码与 `WorkflowState.canTransitionTo` |
| H mcp-agent-framework | **REFERENCE ONLY** | §8 —— Apache-2.0 干净但**已休眠 8 个月**（138 未关 issue）；占据的正是我们的 RUNTIME 边界 |
| I DataLogicEngine | **CLOSE** | §9 —— **PolyForm Noncommercial 1.0.0 硬阻断商业复用**；但它是**唯一**把 Business Evidence 做成一等对象的样本（只可读，不可用） |

> ⚠️ **本条必须由 Codex 确认**：G/H/I 三个候选的坐标是我按名称推断的。
> 若指令所指另有其库，这三项结论需重做。**不要把我推断的坐标当成既定事实。**

### 0.4 与既有文档的关系（避免重复劳动与自相矛盾）

- `docs/v3/RUNTIME_COMPARISON.md` 已完成 **Kernel vs Trigger.dev / DSH / PentAGI / Glean /
  Generic Agent Platform / RAG Platform** 的对照（§2–§8）。本研究**不重做**这部分，
  只新增「开源底座可否复用」这一维度。
- 仓库内此前**从未提及**本研究的任何一个候选项目（已逐一 grep `docs/` 确认）。
  因此本研究不存在与既有结论冲突的问题——它是新增面，不是修正面。
- 本次使用的最新 ADR 编号为 **ADR-011**；若最终需要立 ADR，编号应为 **ADR-012**。

---

## 1. Candidate A — HugAgentOS (`ZJU-REAL/HugAgentOS`)

### 1.1 License = **Apache-2.0 + 四条补充条款，冲突时补充条款优先**（CONFIRMED，独立核验）

**这是本次许可审查中最重要的一条，因为它对第一候选的采用条件是决定性的。**

```bash
curl -s https://raw.githubusercontent.com/ZJU-REAL/HugAgentOS/main/LICENSE | head -6
```

原文：

> **HugAgentOS Community Edition License**
> This software is licensed under the Apache License, Version 2.0 (reproduced in full below),
> supplemented by the Additional Terms set forth after the Apache License text.
> **In the event of a conflict between the Apache License and the Additional Terms,
> the Additional Terms prevail.**

`LICENSE` 共 214 行：第 1–188 行为标准 Apache-2.0 全文，**第 189 行起为 `ADDITIONAL TERMS`
（supplementing the Apache License, Version 2.0）**，正文如下（逐条原文摘录）：

> **1. Multi-tenant SaaS restriction.** You may NOT operate the Work, or any Derivative Work,
> as a multi-tenant Software-as-a-Service offering that is substantially similar to, or competes
> with, the hosted commercial offering of the Work provided by the Licensor, without a separate
> commercial license from the Licensor. **Operating the Work for the internal use of a single
> organization (including its affiliates) is expressly permitted.**
>
> **2. Attribution preservation.** You may NOT remove, hide, or obscure the "Powered by"
> attribution displayed in the user interface of the Work, except with a commercial
> white-label license from the Licensor.
>
> **3. Commercial edition components.** Features, source files, and components that ship only
> with the commercial edition of the Work are NOT covered by this License and may not be used
> except under a separate commercial agreement with the Licensor.
>
> **4. No other restrictions.** Except as expressly modified by these Additional Terms, all use,
> reproduction, and distribution of the Work is governed by the Apache License, Version 2.0.

`NOTICE` 另有两条与采用相关的信息（原文）：

> Commercial-licensed components (e.g. `@univerjs/preset-sheets-advanced`) and proprietary cloud
> SDKs (`oss2`, `opensandbox`) are **NOT part of this distribution**; they ship only with the
> commercial edition.

**逐项判定（对我们的使用方式）**：

| 许可维度 | 判定 | 依据 |
|---|---|---|
| 商业使用 | ✅ 允许 | 补充条款 4：除上述修改外，一切使用仍由 Apache-2.0 管辖 |
| 修改 | ✅ 允许 | 同上；且明确覆盖 **Derivative Works** |
| 再分发 | ✅ 允许 | 同上 |
| **单组织内部私有化部署** | ✅ **明文允许** | 补充条款 1 末句 *"internal use of a single organization (including its affiliates) is expressly permitted"* |
| **多租户 SaaS（与我们托管形态竞争）** | ❌ 禁止（除非另购商业许可） | 补充条款 1 |
| **白标 / 去掉 "Powered by" 署名** | ❌ 禁止（除非另购 white-label 商业许可） | 补充条款 2 |
| 商业版组件 | ❌ 不在许可内 | 补充条款 3 + `NOTICE` |
| CLA | 未在 LICENSE 中出现 | — |

> ⚠️ **这不是"Apache-2.0，随便用"。** 对我们的含义是**双向**的：
> - **相容的一面**：红队 v3 主路径（数据不出域、单企业私有化部署）**被明文允许**；
> - **必须决策的一面**：若产品要以**自有品牌**交付（去掉 "Powered by"），
>   或未来要做成**多租户 SaaS**，**必须取得商业许可**。这条需要业务方决策，不是工程能绕过的。
>
> 另注：社区版是**功能受限版**（商业版组件不随分发），所以"社区版能力"≠"项目 README 展示的全部能力"。

### 1.2 ⭐ 一个必须先说的结构性事实：这是一个**只读下游镜像**

**Claim**：本 GitHub 仓库**不是**开源协作主仓，而是从上游主仓按版本自动生成的**只读镜像**。
**Source**：`CONTRIBUTING.md:9-13`
**Evidence**（原文）：
```
1. **`src/**`、`mcp_servers/**` 等生成代码** —— 由上游主仓按版本自动生成、
   对外只读。直接对这些文件提 PR 无法被合并；请改提 Issue
```
**Confidence**：CONFIRMED

**为什么这条影响重大**：所有源码级考察（§1.4–§1.8）读的都是**生成产物**。
因此：

1. 任何 **Level 3（fork/扩展）** 的设想意味着**fork 一棵生成出来的树**；
2. 修改 `src/**` 在协作意义上**不可能回流**（CONTRIBUTING 明文拒绝该类 PR）；
3. 许可证随本仓库 LICENSE 走，但**上游主仓的许可状态在本研究中为 UNKNOWN**——
   而我们打算复用的正是上游生成的东西。

> ⚠️ 这一条把 HugAgentOS 的**可行形态收窄为"整栈采用"或"只做概念参考"**，
> 中间的"拿它的 ontology 模块嵌进我们的 Kernel"这条路径在证据上不成立（详见 §1.7）。

### 1.3 许可证元数据自相矛盾（CONFIRMED）

**Claim**：`pyproject.toml` 声明 MIT，而 `LICENSE` 实为 Community Edition License。**以 LICENSE 为准。**
**Source**：`pyproject.toml` vs `LICENSE:191-214`（另见 §1.1 的独立核验）
**Evidence**：`pyproject.toml` 中 `license = {text = "MIT"}`。
**Confidence**：CONFIRMED —— 该仓库的许可证元数据**不可信**，必须以 LICENSE 正文为准。
（这也是"不能凭 README/元数据判断"的一个直接实例。）

### 1.4 仓库健康度

| 信号 | 值 | 出处 |
|---|---|---|
| 最后提交 | 2026-09-18（merge PR #160） | GitHub API |
| 创建 | 2026-07-19（**仅约 2 个月**） | API |
| 最新 release | `desktop-v1.0.2`，2026-09-11 | API |
| Releases | **5 个，全是 desktop tag —— 后端/EE 无发布列车** | API |
| 贡献者 | **2 位真实贡献者**（Luhaozhu 244 / tricktreat 6） | API |
| CI | **仅桌面端**（`.github/workflows/desktop-ci.yml`、`desktop-release.yml`） | tree |
| **后端 CI** | **NOT FOUND** —— 没有任何 workflow 在 `src/backend` 上跑 pytest | tree |
| 测试规模 | `src/backend/tests/` 下 436 个 `.py` | tree |

**Claim**：后端测试规模大但**无 CI 强制**，且 ontology 区域覆盖极薄。
**Source**：tree 计数；`src/backend/tests/ontology/` **只有 3 个文件**
（`test_ontology_reviewer.py`、`test_ontology_revision_accept.py`、`test_ontology_workflow_evidence.py`），
而对应实现是 4,761 行 ORM 模型 + 4,000+ 行的 `orchestration/workflow.py`。
**Confidence**：CONFIRMED

### 1.5 架构与包结构

`pyproject.toml:52-56`（`package-dir = {"" = "src/backend"}`）确认 import 根是 `src/backend`：

- `api/` —— FastAPI 路由/中间件
- `core/` —— "类内核"桶：`ontology/`、`db/`(+`models/`,`repository/`)、`llm/`、`memory/`、
  `kb/`、`auth/`、`sandbox/`、`evolution/`、`storage/`、`services/`、`content/`、`chat/`、
  `channels/`、`agent_skills/`
- `orchestration/` —— `workflow.py`（**3,536 行**）、`autonomous_loop.py`、`subagents/`、`schedulers/`
- `mcp_servers/` —— 8 个内置 MCP server
- `agent_bundles/`、`plugin_bundles/`、`skill_bundles/` —— **内容清单，不是代码层**

**Confidence**：CONFIRMED。
⚠️ **没有 `kernel/` 包**。"core" 是"非 HTTP 且非编排"的剩余集合 ——
LLM 管道、KB/RAG、sandbox、channels 与领域本体共用**同一个 import 根**。

### 1.6 ⭐ 核心数据模型 —— README 主张逐条验证

`core/db/models/*.py` 共 **89 个 `__tablename__`**。指令 §三 列出的概念逐条核验结果：

| 概念 | 结论 | 出处 |
|---|---|---|
| **Ontology（Domain Pack）** | ✅ **真实、一等对象** | `core/db/models/ontology.py:22` `ontology_packs`、`:60` `ontology_pack_versions`、`:112` `ontology_enforcement_events`、`:180` `ontology_review_runs`、`:228` `ontology_drafts` |
| **Concept** | ⚠️ 真实，但**只存在于 JSONB 内** | `core/ontology/schemas.py:27` `class Concept` —— 存于 `ontology_pack_versions.content`，**无自己的表** |
| **Relationship（Relation）** | ⚠️ 真实，同样**只存在于 JSONB 内** | `core/ontology/schemas.py:38` `class Relation` |
| **Rule（Constraint）** | ⚠️ 真实，**只存在于 JSONB 内** | `core/ontology/schemas.py:95` `class Constraint`（`schema_` = JSON Schema 2020-12、`mode: Literal["log","enforce"]`、`requires_citations`） |
| **Workflow** | ⚠️ 真实，只存在于 JSONB 内 | `core/ontology/schemas.py:124` `class Workflow` |
| **Decision** | ❌ **仅瞬态，未持久化为领域对象** | `core/ontology/validator.py:44` `@dataclass OntologyGateDecision`；verdict 落进 `ontology_enforcement_events.decision` |
| **Evidence** | ❌ 仅 runtime-trace / citation（见 §1.7） | `ontology_enforcement_events`；`core/evolution/evidence_contract.py` |
| **Entity** | ❌ **NOT FOUND** | `core/db/models/` 中无 `entities` 表、无 `Entity` 类 |
| **Relationship 作为领域边** | ❌ NOT FOUND（只有 Neo4j L3 记忆边） | `core/memory/graph.py`，且是通用谓词 |
| **Invariant** | ❌ **NOT FOUND 作为对象** | `Invariant` 在 Python 中出现 25 次，**在 `core/db/models/` 中出现 0 次**（全在 docstring/注释） |
| **Provenance** | ❌ NOT FOUND 作为模型 | 无表；`core/llm/context_ir.py` 的 "provenance" 指 **prompt 条目标记** |
| **Permission / Role** | ❌ 仅基础设施级（见 §1.8） | `core/auth/permissions_iface.py`、`core/auth/capabilities.py` |
| **Context** | ❌ **NOT FOUND 作为领域对象** | `core/llm/context_ir.py` 是 **prompt IR**，不是企业上下文 |
| **Action Contract** | ❌ **NOT FOUND in code** | 全库搜 `ActionContract`/`action_contract`：**0 命中**；只出现在 `README.md`、`document/en/architecture/overview.md` 与一张架构 SVG |

**对指令 §三初步观察的逐条裁定**（指令原文列出 11 项）：

```
Concepts            ✓ 真实  (schemas.py:27)
Relationships       ✓ 真实  (schemas.py:38)
Workflows           ✓ 真实  (schemas.py:124)
Evidence Requirements  ~ 部分真实 (Constraint.requires_citations: bool, schemas.py:100)
Roles / Permissions ✗ 仅 prompt 级 (reviewer personas, orchestration/subagents/ontology_reviewer.py:26-30)
Invariants          ✗ NOT FOUND
Action Contracts    ✗ 仅营销文案
```

> ⭐ **这是本次研究对 Codex 最重要的一条回馈**：指令 §三 说 HugAgentOS
> "**概念与我们当前 Kernel 非常接近**，包括 Domain Pack / Concepts / Relationships /
> **Invariants** / **Action Contracts** / Workflows / Roles / Permissions / Evidence Requirements /
> Enterprise Agent / Ontology-Grounded Enterprise Trust Plane"。
> 逐条核验后：**Invariants 与 Action Contracts 在代码里不存在**；
> Roles/Permissions 只是 prompt 里的 reviewer 人设；Concepts/Relations/Workflows 真实
> 但**只是 JSONB 里的 Pydantic 结构，没有自己的表**。
> "表面很像"这一判断在源码层面**不成立**——这是"README Research 会得出错误结论"的直接实例。

**另一条仓库质量风险（CONFIRMED）**：ontology 相关表**不在任何 Alembic 迁移里**。
`alembic/versions/` 下 14 个迁移（`ce_0001`…`ce_0014`）**零处**引用 `ontology_packs`；
它们由启动时的 `Base.metadata.create_all`（`core/db/engine.py:172`）与
`ce_0001_initial.py:30` 的 `ce_create_all(op.get_bind())` 创建。

### 1.7 Evidence / Context Update / 耦合 / 扩展点（四个决定性问题）

**1.7.1 Evidence 是 runtime trace + citation，不是业务证据（CONFIRMED）**

`core/db/models/ontology.py:112-127`：
```python
class OntologyEnforcementEvent(Base):
    """Append-only evidence emitted by the deterministic gate and reviewers."""
    stage = Column(String(24), nullable=False)   # tool|checkpoint|output|evolution|build
    decision = Column(String(24), nullable=False)  # pass|log|deny|revise|escalate|error
```
`orchestration/subagents/ontology_reviewer.py:50-56`：
```python
def _review_evidence_payload(trace, citations):
    return {"trace": _tail_with_json_budget(trace, 8000),
            "citations": _tail_with_json_budget(citations, 2000)}
```

即：Evidence = (a) append-only 的强制/轨迹日志，(b) 截断后的 `trace` + `citations` blob 喂给 LLM reviewer。
**没有任何带业务主体、主张、事实来源指针、有效期的 `Evidence` 模型。**

对照 `KERNEL_BOUNDARY.md:188-195` 的四种产出区分：
HugAgentOS 实现的是 **Execution Reference / Agent Output**，
**不是 Business Evidence**（"这个业务结论是怎么产生的"）。
最接近的 `EvolutionEvidencePack`（`core/db/models/evolution.py`，内容寻址）管的是**技能编译**，不是决策。

**1.7.2 Context Update：NOT FOUND（CONFIRMED）**

- `ProfileMemory`（`core/db/models/memory.py:29`）—— **在会话开始时冻结**的有界 markdown，
  按 `(user_id, workspace_id)` 分；`revision` 在压缩时自增。**是 persona/profile blob，不是业务上下文状态。**
- `MemoryOutbox`（`:44`）—— 响应后记忆写入的**幂等副作用队列**；更新语义是给
  memory effects 的，不是给领域状态的。
- `core/memory/graph.py` —— Neo4j L3 "entity—predicate—entity"，带
  `_MAX_RELATIONS_PER_TURN = 12`、`_MIN_CONFIDENCE = 0.65`。
- **无 decision-update、无 entity-state-change、无时态/双时态上下文。**
  唯一的时间版本化是 `OntologyPackVersion.status IN ('draft','active','retired')`。

> 对照 `V3_CLOSEOUT.md:101-102`：**链尾的 Context Update 正是"判一个 Kernel 不是规则引擎+RAG"的关键**。
> 这一项该仓库**没有**。

**1.7.3 本体是"业务语义声明 + 通用引擎"，且规则只能约束工具调用（CONFIRMED）**

`core/ontology/schemas.py:1-8` 自述：
```python
"""...A Domain Pack is an operational contract for an agent harness, not an OWL
reasoner: concepts and relations make the vocabulary explicit, constraints are
executable JSON-Schema fragments, and workflows decide which gates/review levels
apply to a task."""
```
`Concept`（`:27`）带 `id/name/aliases/definition/parent_id/closed_values/tags/risk`，
有层级与环路校验（`:186 _validate_parent_cycles`）—— **是真实的领域词表**。
`Relation`（`:38`）是 SPO 且带 `min_cardinality`/`max_cardinality`/`forbidden`。

**但决定性的限制在这里**（`:58`）：
```python
ConstraintTarget.kind: Literal["tool", "tool_parameter", "output"]
```
> **约束只能作用于工具调用与答案文本，不能作用于领域业务对象。**
> 也就是说：它是 **tool-call governance harness**，不是 domain rule engine。
> 我们需要的"供应商资质判据 / 合同有效期 / 财务逾期"这类**业务对象**上的规则，它表达不了。

（对照：`core/memory/graph.py:32-58` 的 `PREDICATE_LABELS` / `ALLOWED_ENTITY_TYPES`
是**硬编码的通用中英文词表**：`person/organization/team/project/system/document/metric/concept/place/other`
—— 那一层是通用的，与领域无关。）

**1.7.4 ⭐ `ARCHITECTURAL COUPLING RISK` = 结构性风险（CONFIRMED）**

**执行模型**：纯 **asyncio + AgentScope 2.0**（无 DBOS / Temporal / Celery）。
`orchestration/workflow.py:5` `import asyncio`、`:2196` `asyncio.create_task(`、`:2213` `await asyncio.wait_for(`；
`requirements.txt` 钉死 `agentscope==2.0.0`、`mcp>=1.0.0,<2.0.0`、`redis[asyncio]`、`fakeredis`。
"持久化执行"是手搓的：`jobs`/`job_items`/`job_calls` + `MemoryOutbox` 的 lease/attempt 状态机。

**ontology 闸门不是一个可分离的服务**，它是 AgentScope 中间件并硬编码在 3,536 行的 workflow 里
（`core/llm/middlewares.py:597-652, :695`）：
```python
class OntologyGateMiddleware(MiddlewareBase):
    ...
    from core.ontology.validator import evaluate_tool_call
    decision = evaluate_tool_call(...)
    from core.services.ontology_evolution_service import schedule_ontology_evolution
```
`orchestration/workflow.py:32-49` 在**同一模块**里同时 import `core.ontology.revision`、
`core.ontology.validator`、`orchestration.citation_anchor`、`orchestration.streaming.StreamingAgent`、
`core.llm.mcp_manager`。

**具体耦合链**：
- `Constraint` → `ConstraintTarget` → **工具名与工具 JSON Schema**
  （`validator.py:63-100` 需要 `tool_schemas`/`known_tools`）—— **没有工具注册表就无法求值业务规则**
- `Workflow` → `required_tools`/`forbidden_tools`/`asset_triggers` → **Agent 工具目录**
- Decision → `OntologyGateMiddleware` → **AgentScope `AgentState`**（`middlewares.py:451`）
- 修复回路 → `workflow.py:579 _run_ontology_repair_round` → **SSE 流式层**
- 本体演化 → `core/evolution/ontology_bridge.py` → **演化/晋升平面**

> **结论**：采用 ontology 层 = 采用 AgentScope（精确版本钉死）+ 中间件管道 + SSE 契约
> + 工具注册表 + 演化平面。**Domain Pack 无法独立使用。** 这是结构性的，不是偶然的。

**1.7.5 扩展点：没有"领域语义"扩展接口（CONFIRMED）**

`core/ontology/__init__.py` 的全部公开面只有三项：
```python
from core.ontology.schemas import OntologyPackDocument
from core.ontology.validator import DomainPackValidator, OntologyGateDecision
__all__ = ["DomainPackValidator", "OntologyGateDecision", "OntologyPackDocument"]
```
真实扩展点：`OntologyPackDocument`（Pydantic，`extra="forbid"`）、
`StorageBackend`（ABC，7 个抽象方法，`core/storage/protocol.py:6-42`）、
`plugin.json`/`mcp.json` 清单（3 种兼容格式）、`SKILL.md`、`agent_bundles/*/agent.json`、8 个内置 MCP server。

**直接回答指令 §7.5「能不能把我们的 Domain Semantics 插进去？」**：
> **能加载，但只能落在它已定义的形状里**（concepts / relations / 针对工具参数与答案文本的
> JSON-Schema constraints / 词法触发 workflows）。
> 一旦需要**我们自己的决策求值、我们自己的 Evidence 模型、我们自己的 Context Update 语义**，
> 就必须改 `core/ontology/validator.py` + `core/llm/middlewares.py` + `orchestration/workflow.py`
> —— **即 fork `src/**`，而 CONTRIBUTING 明文规定该树对外只读。**
> **不存在** "decision evaluator" / "evidence provider" / "context updater" 的 `Protocol` 或 ABC。

### 1.8 存储 / 部署（本仓库对我们最强的一面）

出处：`docker-compose.yml`、`requirements.txt`
- **必需**：PostgreSQL 15（用 `JSONB`）、Redis 7（`SESSION_STORE=redis`，无 Docker 时 `fakeredis` 兜底）
- **可选（profile `mem0`）**：etcd、MinIO、**Milvus v2.5.4**、**Neo4j 5.15-community**（APOC）；
  向量库是 Milvus，集合 `hugagent_kb_private`
- **对象存储**：默认 `STORAGE_TYPE=local`；S3 兼容经 `botocore` + `StorageBackend` ABC
- **Docker/K8s**：`docker-compose.yml` 7+ 服务；**树中无 K8s manifest**
- **LLM**：OpenAI 兼容为基座（`OPENAI_API_KEY`/`OPENAI_API_BASE`），另有 `MODEL_URL` 自定义网关、
  `DIFY_URL`，以及 Anthropic / DashScope / Gemini / **Ollama** 原生通道（全部懒加载）
- **私有化/离线（CONFIRMED）**：仓库自带 Tauri 桌面应用（`desktop/src-tauri/`）与
  **离线安装路径**（"the no-Docker installer"、`docker/scripts/build-offline-runtime.mjs`、`install.sh`）

> ⭐ **这是该仓库与本项目契合度最高的一点**：**气隙/离线部署是它第一等的、在维护的目标**，
> 正对红队 v3 主路径 D（数据不出域）。这一点是它的**真实优势**，不是宣传。

### 1.9 复用等级（源码级判定）

| 能力 | Level | 一句话依据 |
|---|---|---|
| Context Model | **0** | `context_ir.py` 是 prompt 组装 IR，不是业务上下文状态 |
| Domain Ontology | **2** | `Concept`/`Relation`/`Constraint`/`Workflow` 的模式与校验器可作独立模块看待，但**受工具调用形状限制**且嵌在 JSONB 无独立表 |
| Entity / Relationship | **0/1** | 无 `Entity`/`Relationship` 领域模型；只有通用 Neo4j 记忆边 |
| Business Rules | **2**（**带重要保留**） | `Constraint` + `evaluate_tool_call`/`evaluate_output` 确实**零 LLM**、用 JSON Schema 求值（`validator.py:559`）—— 但**只能约束工具参数与答案文本**，不能约束业务对象 |
| Decision | **1** | `OntologyGateDecision` 是瞬态 dataclass；verdict 只以日志行持久化 |
| Evidence | **0/1** | Evidence = 截断 trace + citations 交给 LLM reviewer；**它实现的是 Runtime Trace，不是 Business Evidence** |
| Provenance | **0** | 无模型；"provenance" 仅指 prompt 条目标记 |
| Context Update | **0** | NOT FOUND；`ProfileMemory` 会话开始即冻结 |
| Knowledge Retrieval | **2** | `core/kb/`（切分、Milvus 混合检索、可选 rerank）是干净的独立组件，有 HTTP/MCP 边界 |
| Graph Storage | **1** | `core/memory/graph.py` 是薄 Neo4j 包装 + 硬编码谓词，不是图存储抽象 |
| Vector Search | **2** | `kb_vector.py` 自足可搬，但带硬编码集合 schema |
| Agent Runtime | **1** | 依赖 `agentscope==2.0.0` 精确钉死；采用即接受该 pin |
| Workflow Execution | **1** | 3,536 行 `workflow.py`，且 `Workflow` 一词在库中**指两个不同东西**（`schemas.py:124` 的工具白名单 vs chat 流状态机） |
| Permission Enforcement | **0** | owner-only + 布尔 feature flag + `super_admin`；团队/权限矩阵是 EE 专属 |
| Observability | **2** | `structlog` JSON 日志 + `HarnessEventLog`/`ToolCallLog`/`EvolutionTraceEvent`；**无 OTel/Langfuse/LangSmith（0 命中）** |
| Domain Evaluation | **2** | `core/evolution/evaluator.py` + `benchmark.py` + `EvolutionEvaluation`（成对统计、`effect_size`、`p_value`、冻结数据集快照）；真实且独立，但**面向技能/Agent 晋升，不是领域决策正确性** |

**对 Kernel 边界的总结**：ontology 层是真实的、非平凡的、闸门处**确实零 LLM** 的 ——
但它是一个 **tool-call governance harness，不是 domain decision kernel**。
它没有 Entity、没有 Business Evidence、没有 Context Update、没有领域语义扩展接口。


## 2. Candidate B — Semantica (`semantica-agi/semantica`)

> 默认分支 `main`。考察于 2026‑09‑20。

### 2.1 License = **纯 MIT，无 CLA，仓内无双许可**（CONFIRMED）

`LICENSE:1-3`：
```
1: MIT License
3: Copyright (c) 2026 Semantica
```
`docs/project-license.md:41-44` 逐项明列：
> "Use Semantica commercially: **free for business use** / Modify the source code /
> Distribute copies or derivatives / **Use in proprietary software**"

`CONTRIBUTING.md` 全文 grep `CLA|contributor license|DCO|sign-off` → **零命中**（CONFIRMED）。
无 copyleft、无附加条款、树中无商业版目录。
**UNKNOWN**：`pyproject.toml:99` 的 homepage `getsemantica.ai` 是否存在托管/企业版 —— 仓内不可验证。

> **这是全部九个候选里许可证最干净的一个**（对比：HugAgentOS 有附加条款、qKnow 必须署名、
> DataLogicEngine 商业阻断、GSearchAI 根本没有许可证）。

### 2.2 仓库健康度（CONFIRMED）

| 信号 | 值 |
|---|---|
| 最后提交 | **2026‑09‑20（当天）**；创建 2025‑06‑25 |
| Stars / forks / open issues | 13,310★ / 1,500 / 79 |
| 版本 | `pyproject.toml:7` → `0.7.0`；⚠️ **`RELEASE_NOTES.md` 标题仍写 "Semantica 0.5.0 Release Notes"（陈旧）** |
| CI | `.github/workflows/{ci,codeql,release,security,security-scan,docs,benchmark,verify-action-pins}.yml` + CodeQL 配置 + Dependabot + **hash-pinned `requirements-ci.txt`** → **确实做了加固** |
| 测试 | `tests/` 下 245 个 `.py`、77 个子目录 |
| 贡献者 | `CONTRIBUTORS.md` 的 all-contributors 区块**是空的**（START/END 相邻）→ 实质是少数几位维护者 |

**测试性格：混合，且偏向"模拟"（CONFIRMED）** ——
`tests/verify_context_sync.py:12` 打了 `pytestmark = pytest.mark.integration`，
却在 `:21` 自己定义了 `class MockVectorStore`。
> 即：这里的 "integration" 含义是**"需要一个 mock fixture"**，不是"需要真实服务"。
> 真正的 `integration` marker 另有一套（`pyproject.toml:378-380`），但那部分是少数。
> （这两个文件为 CONFIRMED；**全套的模拟/真实比例 = UNKNOWN**。）

### 2.3 ⭐ 它是一个**独立产品/平台**，不是一个可嵌入的库

**消费模型是"运行我们的平台"，不是"import 我们的类型"** —— `pyproject.toml:352-358`：
```
[project.scripts]
semantica          = "semantica.cli:main"
semantica-server   = "semantica.server:main"
semantica-worker   = "semantica.worker:main"
semantica-explorer = "semantica.explorer:main"
semantica-mcp      = "semantica.mcp_server:main"
```
**并且 Explorer 的 React 构建产物被打进 Python wheel 里** —— CI 断言
（`.github/workflows/ci.yml:164-179`）：
```
assert "semantica/static/index.html" in names, "Explorer index.html missing from wheel"
assert any(name.startswith("semantica/static/assets/") for name in names), "Explorer assets missing from wheel"
```

**但依赖方向是正确的**（CONFIRMED）：`semantica/server.py:22` 与 `semantica/worker.py:11`
import `from .core.orchestrator import Semantica`；而
`context/`、`kg/`、`ontology/`、`reasoning/`、`provenance/` 这六个模块
**没有一个** import `server`/`explorer`/`worker`（grep 零命中）。
> **server → core，从不 core → server。** 这为"只取其中几个包"提供了真实的可能性。

**⚠️ 一个命名陷阱**：`semantica/core/` **不是**我们的 kernel，它是**编排管道**。
`semantica/core/__init__.py:2` 自述：
> `"""Core Orchestration Module … framework initialization, knowledge base construction,
> pipeline execution, configuration management, lifecycle management, and plugin system integration."""`

其内容是 `config_manager` / `lifecycle` / `methods` / `orchestrator` / `plugin_registry` / `registry`。
**真正的数据模型在扁平兄弟包 `context/`、`ontology/`、`reasoning/`、`provenance/` 里。**

### 2.4 核心数据模型（真实定义）

| 概念 | 位置 | 置信 |
|---|---|---|
| **Context** | 无 `class Context`。`context/context_graph.py:563 ContextGraph`；`ContextNode:419`（`node_id, node_type, content, metadata, properties, valid_from, valid_until`）；`ContextEdge:462`；决策域上下文 `context/decision_models.py:151 DecisionContext`（`context_id, decision_id, entity_snapshots: Dict[str, Dict], risk_factors, cross_system_inputs`） | CONFIRMED |
| **Entity** | `utils/types.py:165`（`id, text, type, confidence, start, end, metadata, relations`）；另有 `semantic_extract/types.py:22`。⚠️ **图节点是通用的 `ContextNode`，图中没有一等 Entity** | CONFIRMED |
| **Relationship** | `utils/types.py:191`（`id, source_id, target_id, type, confidence, metadata, properties`）；图边是 `ContextEdge` | CONFIRMED |
| **Ontology** | ❌ **无 `class Ontology`** —— 字典形状：`ontology/domain_ontologies.py` `create_domain_ontology()` 返回 `{"name","uri","version","classes","properties","metadata"}`；引擎在 `ontology/engine.py:17` | CONFIRMED |
| **Rule** | `reasoning/reasoner.py:325` `Rule(rule_id, name, conditions, conclusion, rule_type, confidence, priority, handler, actions, metadata)`；Horn 子句 `reasoning/datalog_reasoner.py:30 DatalogRule(head_predicate, head_args, body: List[BodyAtom])`；策略规则是字典 `decision_models.py:193 rules: Dict[str, Any]` | CONFIRMED |
| **Reasoning / Inference** | `reasoner.py:23 RuleType{IMPLICATION, EQUIVALENCE, CONSTRAINT, TRANSFORMATION}`；`reasoner.py:349 InferenceResult(conclusion, rule_used, premises, confidence)`；`DatalogReasoner` / `ReteEngine` / `SPARQLReasoner` / `TruthMaintenanceSession` | CONFIRMED |
| **Decision** | `context/decision_models.py:87` —— `decision_id, category, scenario, reasoning, outcome, confidence, timestamp, decision_maker, valid_from, valid_until, metadata` | CONFIRMED |
| **Decision Record** | ❌ 无 `class DecisionRecord`；写入者是 `context/decision_recorder.py:89 DecisionRecorder.record_decision()`（`:116`） | CONFIRMED |
| **Evidence** | ❌ **NOT FOUND 作为类**（见 §2.5） | CONFIRMED |
| **Provenance** | ⭐ `provenance/schemas.py:37 ProvenanceEntry`（**W3C PROV-O**）：`entity_id, entity_type, activity_id, agent_id, agent_type, is_automated, role, source_document, source_location, source_quote, timestamp, first_seen, last_updated, confidence, checksum, sequence_id, previous_checksum, parent_entity_id, used_entities` | CONFIRMED |
| **Temporal / validity** | `context_graph.py:427-428` `valid_from`/`valid_until` + `is_active()`；**双时态** `kg/temporal_model.py:28 BiTemporalFact(valid_from, valid_until, recorded_at, superseded_at)` —— **`superseded_at` 是独立的系统时间轴** | CONFIRMED |

> 另注：`context/` 下有 `DecisionRecorder` 与先例/因果链的查询路径
> （MCP 工具已注册 `record_decision`、decision query/precedent/causal-chain）。

### 2.5 ⭐ Evidence：**不是一等对象 —— 完全不存在**（CONFIRMED）

**全仓库 class 定义扫描 + 全文 grep：`evidence` 有 117 处字符串命中，类型定义为 0。**

Evidence 只以三种形态出现：
- **临时 metadata key**：`kg/community_summarizer.py:1492 if "evidence" in attrs and attrs["evidence"]`
- **LLM 生成的叙述**：`context/global_retriever.py:1013 if "Sources / Evidence:" in response_text`
- **运行时轨迹**：`reasoning/explanation_generator.py:76 supporting_evidence: List[Any]`，
  由 `step.input_facts`（`:370`）填充 —— 这是**推导追踪**，即 Runtime Trace / Agent Output

**判定**：它有的是 **Provenance（血缘/保管链）+ Runtime Trace（推导）**，
**没有 Business Evidence。** `ProvenanceEntry` 带 source（`source_document/location/quote`）、
time（`timestamp`）、actor（`agent_id/agent_type/role`、`is_automated`）——
**但没有 claim、没有 decision 引用、没有 execution reference、没有 context 引用。**

最接近"支撑某个决策的证据"的是 `DecisionContext.entity_snapshots` —— 一个**普通字典快照，
不带任何来源或溯源链接**。

> **缺口是真实的。** 这与 §11 的横切结论一致：`claim` 与 `triggering agent`
> 在所有候选里都没有被建模。

### 2.6 ⭐ Context Update：**支持 —— 但形态是"时态闭合"，不是原地修改**（CONFIRMED）

`context/context_graph.py:2706 retract_node`、`:2812 retract_edge`、`:3744 state_at`：
```
2739:         at_iso = _normalize_temporal_input(at) or datetime.now(timezone.utc).isoformat()
2748:             node.valid_until = _closing_valid_until(node.valid_until, at_iso)
2749:             record = {"entity_id": node_id, "entity_kind": "node",
2752:                       "retracted_at": at_iso, "reason": reason}
```
```
3744:     def state_at(self, timestamp) -> Dict[str, Any]:
3748:             active_nodes = [node for node in self.nodes.values() if node.is_active(at_time)]
3759:         decisions_payload = [ ... for node in active_nodes if node.node_type.lower() == "decision"]
```
这是一个**真正的双时态撤回模型**：
- 记录**保留**，只**关闭有效期窗口**；
- `state_at()` 可重建任意时点的状态；
- `_closing_valid_until`（`:288`）**只会收窄**（"retraction only ever closes a validity window,
  never widens one"），并发出 `UPDATE_NODE` 审计事件。

配套：属性级更新 `add_node_attribute():944`；
版本化快照/比较/恢复 `change_management/managers.py:120 create_snapshot`、`:196 compare_versions`、
`:424 record_mutation`、`:480 restore_snapshot`，另有 `OntologyVersionManager:515`；
策略版本化 `context/policy_engine.py:168 update_policy`、`:548 get_policy_history`。

**NOT FOUND**：决策变更（decision-mutation）与证据累积（evidence-accumulation）的 API。

> ⚠️ **一条必须记住的限制**：`ContextGraph` 是**内存实现**
> （`context_graph.py:4` "In-memory GraphStore implementation"）。持久化需要图后端或
> `SEMANTICA_KG_PATH`。

### 2.7 Ontology：**薄 —— 演示级模板注册表**（CONFIRMED）

`ontology/domain_ontologies.py` 的 `_load_domain_templates()` **硬编码恰好两个域** ——
`healthcare` 与 `finance`，**而模块 docstring 宣称支持 "healthcare, finance, legal, research,
and cybersecurity"（五个）**。类只是 `{"name","comment"}`；属性是 `{"name","type","domain","range"}`。

**但周边机器是真实的**：`ontology/engine.py:9-13` 组合了 `OWLGenerator`、`OntologyValidator`、
`OntologyQualityGate`、`LLMOntologyGenerator`；`:200 to_shacl()`、`:313 validate_graph()`（pyshacl extra）；
`:53 from_text(text, provider, model)` 是 **LLM 抽取**。RDF/OWL/SKOS 经 `rdflib`
（`pyproject.toml:58`）。

**没有不变式/约束/公理（除 SHACL shapes 外），没有业务规则↔本体的绑定。**
扩展点：`domain_ontologies.register_domain_template()`。

### 2.8 ⭐⭐ 确定性推理：**是真的确定性**（CONFIRMED）

在 `reasoning/reasoner.py`、`reasoning/explanation_generator.py`、`reasoning/deductive_reasoner.py`、
`context/policy_engine.py` 中 grep `llms|LLM|openai|anthropic|provider` → **零命中**。

```
datalog_reasoner.py:4:  "native Datalog engine using bottom-up semi-naive fixpoint evaluation.
                         It supports recursive rules, multi-hop inference, and guarantees termination"
datalog_reasoner.py:109: raise ValueError(f"Facts must be constants only. Found variable '{arg}' in {fact}")
rete_engine.py:2:       "Rete algorithm implementation ... alpha and beta nodes for pattern matching"
```
`SPARQLReasoner` 有原生路径 + rdflib 回退（`sparql_reasoner.py:554`）。
策略合规是**纯粹确定性比较**（`policy_engine.py:916-959`）：
```
922:             if rule_key.startswith("min_"):
927:                 if field_value < rule_value: return False
939:             elif rule_key.startswith("required_"):
945:                     if not all(item in field_value for item in rule_value): return False
```

> ⚠️ **但必须同时记住这个保留**：**引擎是确定性的，业务规则语言不是。**
> 决策路径上的规则 DSL 只是一个基于 `decision.metadata` 的浅层
> `min_/max_/required_` 谓词 —— **没有表达力强的规则语言、没有规则↔本体的一等绑定、
> 没有逐决策的规则版本化（只有 `Policy.version`）。**
> `reasoner.py` 里的 `Rule` 更丰富，但那是 **KG 推理路径，不是决策路径**。

### 2.9 Kernel vs Runtime 耦合 = **中等**（CONFIRMED，且弱于其他候选）

一个 wheel、五个 console script、Explorer 静态资源在 wheel 内 —— 采用该包意味着接受
`server.py`（FastAPI/uvicorn）、`worker.py`、`explorer/`、`mcp_server/`、`integrations/`、
`deploy/{helm,kubernetes,gcp,azure,fly,railway,render}`、`docker-compose.yml`。
RUNTIME 关切确实存在：管道执行（`core/orchestrator.py:454 run_pipeline`）、
资源分配/调度（`:922 _allocate_resources`）、队列
（`pyproject.toml:223-229` 的 `infra` extra = `redis, celery, kafka-python, pulsar-client, pika`）。

**三条缓解事实（CONFIRMED）**：
1. **每一个 runtime 依赖都在 optional extras 里** —— 基础 `dependencies`
   （`pyproject.toml:49-96`）是 22 个纯库包（numpy/pandas/scipy/sklearn/rdflib/networkx/
   pydantic/loguru/structlog/pyarrow…），**没有 FastAPI、没有 celery、没有 broker**；
2. `core/orchestrator.py` 只 import `..utils` 与 core 子模块，重层是在**属性里懒加载**的
   （`:100 ..provenance`、`:127 ..embeddings`、`:146 ..reasoning`、`:163 ..kg`、`:182 ..parse`、
   `:201 ..ingest`、`:220 ..pipeline`），且都包在 try/except 里；
3. `context/`/`kg/`/`ontology/`/`reasoning/`/`provenance/` 都不 import server/explorer/worker。

**⚠️ 修正一个我先前的假设**：`tests/test_issue_1513_slim_core.py` **不是**关于
"能否单独 import `semantica/core/`"。它断言的是**依赖数量**：
```python
def test_core_dependencies_count():
    """pyproject.toml must contain exactly 22 unique core dependencies."""
    assert normalized_names == expected_22
```
CI 把它与 `.github/workflows/ci.yml:116-122` 配对：
在 `pip install --no-deps --no-build-isolation -e .`（`:113`）之后跑该测试。
> **所以 "slim core" = "基础安装不含重依赖、且 `import semantica` 仍然工作"** ——
> 这是一个**打包保证，不是一个解耦出来的 kernel 产物**。
> **不存在可单独构建的 `semantica-core` 发行包。**

### 2.10 扩展点：**存储层可以，语义层很弱**

**唯一的真 ABC（CONFIRMED）**：`provenance/storage.py:22 from abc import ABC, abstractmethod`
→ `:35 class ProvenanceStorage(ABC)` 带 5 个 `@abstractmethod`，
实现 `:191 InMemoryStorage`、`:391 SQLiteStorage`；`change_management/version_storage.py` 同构。

**不是正式接口的**：`graph_store/graph_store.py:525 class GraphStore` 是**具体门面**，
`__init__` 收 `backend: Any` 并转发 —— **无 ABC、无 Protocol**；
`vector_store/vector_store.py:102 class VectorStore(backend="faiss")` 同样。
> 即：可插拔后端的契约是**约定的鸭子类型，没有可供实现的接口**。

**可用后端**：图 —— `Neo4jStore`/`FalkorDBStore`/`AmazonNeptuneStore`/`ApacheAgeStore`；
向量 —— faiss/qdrant/weaviate/pinecone/milvus/pgvector/sqlite-vec；
triplet/RDF —— oxigraph/blazegraph/jena/rdf4j/anzo。
（注意：BigQuery/Snowflake/Redshift/Databricks 是**摄取源**，不是图或向量后端。）

**领域语义的插入面**：`MethodRegistry`（`core/registry.py`，各包另有 `registry.py`）、
`PluginRegistry`（`core/plugin_registry.py`）、`DomainOntologies.register_domain_template()`、
`OntologyModule`/`ModuleManager`，以及一整套编辑器插件清单
（`plugins/.claude-plugin/`、`.cursor-plugin/`、`.codex-plugin/`、`.vscode-plugin/`、
`.windsurf-plugin/`、`.continue-plugin/`、`.cline-plugin/`、`.openclaw-plugin/`）
与 `plugins/skills/{decision,policy,provenance,reason,ontology,explain,causal,change}/SKILL.md`、
`plugins/agents/{decision-advisor,explainability,kg-assistant}.md`。

> ⚠️ **但不存在"自定义领域本体 + 规则集"的一等扩展清单** ——
> 你可以注册一个模板字典并提供自己的规则，**但那是在采用它的决策语义，不是在扩展它。**

### 2.11 存储 / 部署（对私有化最友好的一条）

- **必需后端：无。** 基础安装完全可跑在内存里（`ContextGraph`）+ rdflib/networkx。
  其余全在 extras。**这是全部候选里唯一一个"零强依赖基础设施"的。**
- 部署清单很完整（Dockerfile、compose、helm、kubernetes、gcp/azure/fly/railway/render）
  —— 即**项目期望被当服务部署**。
- LLM：openai/groq/gemini/anthropic/ollama/deepseek/novita/litellm/instructor，全部 optional。
- **私有化/离线现实（CONFIRMED）**：`llm-ollama` + `embeddings-local`
  （sentence-transformers/fastembed/onnxruntime/tokenizers）+ `nlp-spacy`
  + `tripletstore-oxigraph` + `vectorstore-sqlite` 即可覆盖零云路径。
  **`infra` extra 会拉 Kafka/Pulsar/RabbitMQ —— 可以避开。**
- MCP：`semantica-mcp` console script；工具含 `record_decision`、decision query/precedent/causal-chain、
  实体/关系抽取、`get_graph_summary`，资源 `semantica://decisions/list`、`semantica://schema/info`。

### 2.12 复用等级（源码级判定）

| 能力 | Level | 依据 |
|---|---|---|
| **Context Model** | **3 — Foundation reuse**（**带保留**） | `ContextGraph` + `ContextNode/Edge` + 双时态 `valid_from/valid_until` 是真实、有测试、直接映射 Context 的。⚠️ **但它的 Context 不含 Permission scope**（Semantica 的权限只有 Explorer 的 REST auth），而那一项是我们的 Kernel PRIMARY + 铁律 1 → **结构化/时态部分 Level 3，权限域必须自建** |
| Domain Ontology | **1** | 两个硬编码演示模板（healthcare/finance）；无约束/不变式；`from_text()` 是 LLM 抽取 |
| Entity / Relationship | **2** | `utils/types.py` 里的普通 dataclass；简单但可直接搬。图节点是通用 `ContextNode` |
| Business Rules | **1** | `Policy.rules` DSL 只是 `min_/max_/required_` 元数据谓词；无规则语言、无规则↔本体绑定 |
| **Decision** | **2/3** | `Decision` + `DecisionRecorder` + 政策/先例 + 因果链确实建成了；记录形状接近我们的 Decision + Decision Record |
| **Evidence** | **0** | `class Evidence` 不存在。最近的是 `ProvenanceEntry`（血缘）与 `supporting_evidence`（运行时轨迹）。**Business Evidence 必须自建** |
| **Provenance** | **3 — Foundation reuse** | W3C PROV-O 的 `ProvenanceEntry`、`ProvenanceManager`（1,521 行）、**哈希链 `verify_chain()`**、SQLite/InMemory 的 ABC 存储、`export_prov()` 到 Turtle。**本仓对我们最有价值的资产** |
| **Context Update** | **3 — Foundation reuse** | `retract_node/retract_edge` + `_closing_valid_until` + `state_at()` + `restore_snapshot()` 构成一条连贯、带审计的更新路径 |
| Knowledge Retrieval | **2** | `ContextRetriever`/`TemporalGraphRetriever`/`GlobalRetriever`；可用，但与 LLM 叙述路径缠在一起 |
| Graph Storage | **2** | 多后端门面（Neo4j/FalkorDB/Neptune/AGE），但鸭子类型 `backend: Any`，无 ABC |
| Vector Search | **2** | 一个门面后七个后端；同样的鸭子类型注意点 |
| Agent Runtime | **1** | `integrations/{agno,crewai,langchain,google_adk}` + MCP server；我们不拥有这个，也不会采用它作运行时 |
| Workflow Execution | **1** | `pipeline/` + `worker.py` + celery/kafka/pulsar extra；明确在我们的边界之外 |
| Permission Enforcement | **1** | 只有 Explorer 的 REST 认证（`SEMANTICA_API_KEY`、`SEMANTICA_ALLOW_ANONYMOUS`、`server.py:45-57`）；**没有覆盖决策或工具的策略/权限模型** |
| Observability | **2** | `monitoring` extra（Prometheus、OpenTelemetry SDK + instrumentation）+ 经 provenance/撤回事件形成的**不可变审计轨迹**；标准栈，不新颖 |
| Domain Evaluation | **1**（**INFERRED / UNKNOWN**） | `evals/runner.py:258` 报告通过率与逐例判定，但**深度与是否存在领域专用评估器未经核实 = UNKNOWN** |

**总结**：这是**一个我们可以从中取零件的平台，不是一个可以整体嵌入的库，也不是一个内核**。
对我们可复用的核心是 `provenance/` + `context/context_graph.py`（时态撤回、时点状态）
+ `context/decision_models.py`/`decision_recorder.py` + `change_management/` ——
**这几处对 server/worker/explorer 都是 import 干净的**。

**对我们的边界有两条硬阻断**：
1. **Evidence 完全没有建模** → 必须我们自己拥有；
2. **确定性规则语言只是一个元数据谓词桩** → "Deterministic Business Rules" 必须是我们的，
   尽管底下那套 Datalog/Rete/SPARQL 引擎**确实确定性**，可以充当**推理后端**。

## 3. Candidate C — TrustGraph (`trustgraph-ai/trustgraph`)

> 默认分支 `master`。考察于 2026‑09‑20。

### 3.1 License = Apache-2.0，干净；CLA 是「许可授予」而非版权转让（CONFIRMED / 部分 UNKNOWN）

- `LICENSE` = Apache-2.0（GitHub API `spdx_id: Apache-2.0`），**树中无 `ee/` 目录、无双许可文件、
  无 `NOTICE` 式附加限制** → 商业使用 ✔ / 修改 ✔ / 再分发 ✔ / SaaS ✔。
- `docs/contributor-licence-agreement.md` 自述（原文）：
  > "The CLA does **not** transfer copyright — you keep full ownership of your work. It simply
  > grants the TrustGraph project a perpetual, royalty-free licence to distribute your
  > contribution under the project's Apache 2.0 licence"
- ⚠️ **UNKNOWN**：CLA 正文**在仓外**（命名为 *Fiduciary* Contributor License Agreement），
  **我没有读到该文书本身**。"不转让版权"是项目自己的摘要，未经原文核验。
  若该文书含再许可/转让条款，则存在商业版的可能性 → 记为待核项。
- 商业层：README 宣传 "consumed as a fully managed SaaS"，且有托管 UI
  （`config-ui.demo.trustgraph.ai`）。**本仓内无许可门控的企业模块**（CONFIRMED 于树中缺失）；
  **付费 SaaS 的存在属 INFERRED**。
- 注：Apache-2.0 的授权对我们已取得的代码**不可撤销**，故此为低阶风险。

### 3.2 仓库健康度（CONFIRMED）

| 信号 | 值 |
|---|---|
| 最后 push / `master` 最后提交 | 2026‑09‑20 / **2026‑09‑03**（"Merge branch 'release/v2.9'"） |
| 最新 release | `v2.8.17`（2026‑09‑08），tag 已到 `v2.9.10` |
| Stars | 2,736 |
| 贡献者 | 28，但**极度集中**：`cybermaggedon` 982、`JackColquitt` 432、其余 ≤9 → **实质单厂商项目** |
| CI | `.github/workflows/{cla.yml, pull-request.yaml, release.yaml}` |
| 测试 | `tests/unit` 304 文件、`tests/contract` 12、`tests/integration` 30；另有 `test-api/` 32 个 HTTP 探针、`tests.manual/` 37 |

提交形态（如 `fix(cli): preserve datatype and language tag in parse_nquads (#1095) (#1111)`）
显示是**真实的 RDF 边界情形工作**，不是空转。

### 3.3 ⭐ 决定性事实：**它不可嵌入（not embeddable）**

**`pip install trustgraph` 装到的是客户端（`trustgraph.api`），不是内核。**

**消息总线是强制的** —— `trustgraph-base/trustgraph/base/pubsub.py:29-38`：
```python
def get_async_pubsub(**config: Any) -> Any:
    backend_type = config.get('pubsub_backend', 'pulsar')
    if backend_type == 'pulsar': ... AsyncPulsarBackend(host=config.get('pulsar_host', DEFAULT_PULSAR_HOST), ...
    elif backend_type == 'rabbitmq': ...
    elif backend_type == 'kafka': ...
    else: raise ValueError(f"Async backend not yet supported for: {backend_type}.")
```
默认 `pulsar://pulsar:6650`。**没有进程内总线。**
`base/processor_group.py:1-10` 的 `ProcessorGroup` 只是把多个 processor 放进同一进程**共享一个
pub/sub backend 池** —— 减少进程数，**但仍必须有 broker**。

**消费模型**：Docker 容器 + `:8888` 上的 API gateway。每个队列都是 broker topic
（`schema/core/topic.py`：`flow:tg:<topic>` / `request:tg:<topic>` / `notify:tg:<topic>`）。

> **裁决：无法嵌入。只能"部署在旁"并经 HTTP 调用。**
> 对照本研究 §2.7 的结论（V0 是"单进程 + 单 PostgreSQL"），**这条事实本身已足以把它排除在
> V0 之外**；而对 V1+ 而言，它是一个**平台承诺**而非一个依赖。

### 3.4 核心数据模型

| 概念 | 结论 | 出处 / 证据 |
|---|---|---|
| Triple/Quad | ✅ 存在 —— RDF quad + RDF-star | `schema/core/primitives.py`：`class Triple: s; p; o; g  # Graph name (IRI), None = default graph` |
| Entity / Node | ❌ **不是类型** —— 实体就是一个 `Term(type=IRI)` | `Term` 的 `type ∈ {IRI, BLANK, LITERAL, TRIPLE}`，带 `iri`/`id`/`value`/`datatype`/`language`/`triple` |
| Relationship / Edge | ❌ **不是类型** —— 就是 `Triple` 里的一个谓词 | 同上 |
| **Hypergraph** | ❌ **NOT FOUND 作为类型** | README 说 "leverages RDF 1.2 and Named Graphs as N-Quads to achieve a cutting-edge hypergraph architecture"；机制是 `knowledge/defs.py` 的 `class QuotedTriple: """RDF-star quoted triple (reification)"""` |
| **Provenance** | ✅ 存在 —— **W3C PROV-O**，落在专用命名图 | `provenance/namespaces.py`：`GRAPH_DEFAULT = ""  # Core knowledge facts`、`GRAPH_SOURCE = "urn:graph:source"  # Extraction provenance (which document/chunk a triple came from)`、`GRAPH_RETRIEVAL = "urn:graph:retrieval"` |
| Document / Chunk / Embedding | ✅ 存在 | `schema/knowledge/document.py`：`Document`/`Chunk`；`schema/knowledge/embeddings.py`：`ChunkEmbeddings`/`EntityEmbeddings` |
| **Context** | ❌ **NOT FOUND 作为领域对象** | 只有 `schema/knowledge/graph.py` 的 `EntityContext(entity, context, chunk_id)` —— "实体关联的文本上下文" |
| Workspace | ⚠️ 不在 schema 模块 —— 一个字符串作用域字段 + IAM 记录 | `schema/services/iam.py`：`class WorkspaceRecord: id; name; enabled; created`；`base/workspace_processor.py`：`WORKSPACES_NAMESPACE = "__workspaces__"` |
| Collection | ⚠️ 仅元数据，无语义 | `schema/services/collection.py`：`class CollectionMetadata: collection; name; description; tags: list[str]` |

**"Hypergraph" 判定**：是**基于 reification 的 n 元编码**（RDF-star `<<s p o>>` + 命名图分组），
**不是**带一等 n 元边对象的原生 hypergraph。
> **你得到的是 n 元"建模能力"，不是可用来挂规则的 hyperedge 类型。**
> 指令 §三 把 "Hypergraph" 列为 Candidate C 的检查项 —— 这里给出明确回答：
> **它是一个措辞，不是一个一等类型。**

### 3.5 ⭐ Evidence：它是**数据血缘**，不是业务证据（CONFIRMED）

`provenance/triples.py:document_triples()`：
```python
triples = [
    _triple(doc_uri, RDF_TYPE, _iri(PROV_ENTITY)),
    _triple(doc_uri, RDF_TYPE, _iri(TG_DOCUMENT_TYPE)),
]
if source:  triples.append(_triple(doc_uri, DC_SOURCE, _iri(source)))
```
`provenance/namespaces.py` 中的 `TG_LLM_MODEL`、`TG_ONTOLOGY`、`TG_CHUNK_INDEX`、
`TG_CHAR_OFFSET`、`TG_SOURCE_TEXT` 全是**抽取**元数据 —— 即
"**哪一块 chunk、哪个模型、哪份本体产出了这条 triple**"。

三层 provenance 分别是：
1. **抽取血缘** —— document→page→chunk→subgraph→triple（`GRAPH_SOURCE`）
2. **查询期可解释性** —— `Question → Grounding → Exploration → Focus → Synthesis`，
   带 `TG_REASONING`/`TG_SCORE`（`GRAPH_RETRIEVAL`）
3. **Agent 轨迹** —— `Thought`/`Observation`/`Plan`/`Finding`/`StepResult`，
   `TG_TERMINATION_REASON`/`TG_TOOL_ERROR`/`TG_IN_TOKEN`

> **这三层里没有任何一层是"附着于某个决策的证据"。**
> 没有 decision id、没有 actor/trigger/claim/asserted-time、没有规则引用、没有 context 快照。
>
> **"哪份文档产出了这条 triple" ≠ "这个决策为什么这样下"。**
>
> 最接近的钩子是 `schema/services/agent.py` 的 `AgentResponse.explain_triples: list[Triple]`
> —— 挂在 agent 消息上的一包 triple。

**这条直接回答指令 §九 的决定性问题**：
> "Evidence 是否是一等 domain object？还是只是日志 / trace / citation？"
> **TrustGraph 两样都不是 —— 它是 fact lineage（事实血缘）。**
> 它既不是我们的 Business Evidence，也不是 Execution Reference，
> 而是第三种东西：**知识事实的抽取溯源**。

### 3.6 Context Core / Workspace / Collection = 多租户文档命名空间，不是业务上下文（CONFIRMED）

- **Workspace** = 隔离边界。README："Ensure that an HR agent cannot read financial data…"；
  由 IAM + 配置分区强制（`on_collection_config(self, workspace, config, version)`，
  "config is already partitioned by workspace"）。
- **Collection** = 带 `name`/`description`/`tags` 的存储分区，是 triple/embedding 的**物理 keyspace**
  （`CollectionConfigHandler.create_collection(...)` → `create_collection` 是
  由各**存储后端**实现的 `NotImplementedError` 桩）。
- **"Context Core"** = **可移植的 dump/restore 打包，不是有状态的 context**。
  `cores/knowledge.py`：`put_kg_core` / `get_kg_core` / `delete_kg_core`，
  底层是 `KnowledgeTableStore`（Cassandra），持有 `Triples`/`GraphEmbeddings`/`DocumentEmbeddings`/库 blob。

> **三者都没有生命周期、没有状态、没有语义。**

### 3.7 Context Update：**不支持**（CONFIRMED by absence）

它是**一次写摄取 + 只读检索 + 管理性删除**。
- 写路径纯增量：`put_kg_core` → `self.table_store.add_triples(workspace, request.triples)`。
  **无 update/upsert、无 supersede、无 retract。**
- 删除是粗粒度的：`delete-kg-core`、`delete-collection`、librarian 经 `parent_id` 的文档级联删除。
  **删除一份"文档"是唯一的"变更"原语 —— 那是批量移除，不是状态转移。**
- **NOT FOUND**：时态有效期、`valid_from`/`valid_to`、双时态 triple、实体状态变更、
  证据累积、置信度修订、context 的快照/差异。
  在 `provenance/namespaces.py` 与 `specs/ontology/trustgraph.ttl` 中**不存在任何时态谓词**。
- 唯一可变状态是**配置**（config service 版本化、workspace 增删）。

> **明的说：摄取 + 检索。我们的 `Context Update` 这一步在它这里没有可复用的对应物。**

### 3.8 本体：三个不同的东西，不要混为一谈

**(a) `specs/ontology/trustgraph.ttl`（415 行）是项目自己的内部词表，不是业务本体。**
```turtle
<https://trustgraph.ai/ns/> a owl:Ontology ;
    rdfs:comment "Vocabulary for TrustGraph provenance, extraction metadata, and explainability." ;
    owl:versionInfo "2.3" .
tg:Chunk a owl:Class ; rdfs:subClassOf prov:Entity .
```
类目是 `Document, Page, Section, Chunk, Image, Subgraph, Question, GraphRagQuestion, Thought,
Observation, Plan, Finding…` —— **基础设施自描述**。

**(b) BYOO（Bring-Your-Own-Ontology）是真实的、声明的、确定性的。**
`trustgraph-flow/trustgraph/extract/kg/ontology/ontology_loader.py`：
```python
@dataclass
class OntologyProperty:
    uri: str; type: str; domain: Optional[str]; range: Optional[str]
    inverse_of; functional: bool; min_cardinality; max_cardinality; cardinality
```
经**配置推送**加载（`OntologyLoader` 通过事件驱动配置系统接收本体定义，**从不直接访问数据库**）
—— 即**声明式，不是运行时发现**。

**(c) 但本体只用来"约束 LLM 抽取"，事实本身是概率性的。**
`ontology-prompt.md` 是**摄取期提示词**：
```
You are a knowledge extraction expert. Extract structured triples from text using ONLY the provided ontology elements.
- **{{class_id}}**... classes.items()
1. Only use classes defined above for entity types
Return ONLY a valid JSON array
```

> ⭐ **决定性**：**schema 是声明的（类 OWL 的 JSON，带 domain/range/cardinality）；
> 实例是 LLM 生成的。** 且抽取是可选的（`extract/kg/` 下有纯模式和本体模式两套）。
> **摄取之后没有对图做任何约束检查 —— 约束是提示词文本。**
>
> 对我们的含义：**我们的 Kernel 要求"确定性业务规则"与"被强制的本体"；
> 这是"本体约束的 LLM 抽取词表管道"。两者不是同一件事。**
> 没有规则、没有不变式、没有推导、没有 ingest 后的合规校验。

### 3.9 ⭐ `ARCHITECTURAL COUPLING RISK` = HIGH

**Agent Runtime 在同一栈内，写进同一张图，接同一个 broker。**
（`trustgraph-flow/trustgraph/agent/` → `react/`、`orchestrator/`、`mcp_tool/`、`tool_filter.py`；
`schema/services/agent.py`：`AgentRequest(pattern, subagent_goal, parent_session_id, expected_siblings)`、
`PlanStep(goal, tool_hint, depends_on, status, result)`、
`AgentStep(thought, action, arguments, observation, step_type)`。）

**具体耦合链**：
1. **Agent loop ↔ 知识图**：Agent provenance **写进与业务事实相同的 triple store**，
   落在 `GRAPH_RETRIEVAL`（`urn:graph:retrieval`），且 `AgentRequest` 带
   `collection: str = "default"  # Collection for provenance traces`。
   > ⚠️ **我们的 Evidence 层与他们的 agent trace 会共用表，在存储层无法区分。**
2. **Agent loop ↔ 工具执行 ↔ MCP**：`base/tool_service.py`、`base/dynamic_tool_service.py`、
   `agent/mcp_tool/` —— **工具执行是他们的，而那是我们明确不拥有的。**
3. **一切 ↔ broker**：gateway / IAM / metering / librarian / flow service / 每个 processor
   只经 pub/sub topic 通信。
4. **Client ↔ gateway**：`trustgraph.api`（`Api(url="http://localhost:8888/")`）是 HTTP 客户端，
   不是进程内 API。

**后果**：采用其 provenance/evidence 层 = 采用 flow runtime + 检索栈 + gateway + IAM +
librarian + agent runtime。**不存在一个能把 "Evidence" 单独切下来的接缝。**

**另有一条与铁律 1 直接冲突的记录**（`schema/services/iam.py`）：
> IAM 服务自身声明 *"the IAM service trusts the bus per the enforcement-boundary policy
> (no per-request auth against the caller)"*。

即**强制点是"总线客户端"的属性，不是数据访问层的保证** ——
与 `KERNEL_BOUNDARY.md:132`「Kernel 必须在**数据访问层**（SQL 子查询）强制」正相反。

### 3.10 扩展点：后端/处理器层干净，**知识对象模型不可扩展**

**真实扩展点（CONFIRMED）**：
- **Broker 抽象**：`base/backend.py` —— `@runtime_checkable class Message(Protocol)`、
  `BackendProducer`、`BackendConsumer`；实现有 `async_pulsar_backend.py` /
  `async_rabbitmq_backend.py` / `async_kafka_backend.py`
- **Processor 契约**：`base/spec.py`、`consumer_spec.py`、`producer_spec.py`、
  `parameter_spec.py`、`request_response_spec.py`；`FlowProcessor.register_specification(spec)`、
  `on_configure_flows(workspace, config, version)`。**注意：flow 状态是从配置做期望态对账，
  不是命令式 start/stop** —— 这一点设计上值得称赞。
- **存储后端**：triples → Cassandra（默认）/ Neo4j / FalkorDB / Memgraph；
  vectors → Qdrant（默认）/ Milvus；blobs → Garage（S3）
- **Tool service / MCP**；**消息翻译器**：`messaging/registry.py`
  `register_request/register_response(service_name, translator)`

**不可插拔的是"知识对象模型"**：固定为 `Triple(s,p,o,g)` + `Term`。
> **没有任何扩展点能让你引入一个新的"内核对象种类"（Decision / Rule / Evidence / Context-version）。**
> 你可以把它们编码成命名图里的 triple —— 但那就继承了它的查询模型、它的存储、
> 以及它（缺席的）更新语义，**且拿不到任何类型层契约**。

### 3.11 存储与部署重量（这是采用成本的真正所在）

**必需的有状态服务（在任何 kernel 逻辑运行之前）：** Pulsar（默认）或 RabbitMQ/Kafka、
Cassandra（默认图存储）、Qdrant（向量）、Garage S3（blob）。
外加 API gateway、librarian、config service、flow service、IAM、metering，
以及**每个 flow processor 一个进程**。
Processor Group 文档自己承认：*"primarily for dev workstations and edge deployments where
running 15+ containers is impractical."*

**部署**：Docker/Podman compose 或 Kubernetes（`resources.yaml`）；README："TrustGraph deploys as
a set of Docker containers."
**LLM**：OpenAI 兼容、Ollama、Bedrock、VertexAI、vLLM、TGI、LM Studio、llamafile。
**私有化/离线**：原理上现实（自称 "totally self-hosted (air-gapped on-premise)"；开放 LLM 栈；
本地 embedding 经 `fastembed`）。
> ⚠️ **问题不是可行性，是重量**：Cassandra + Pulsar + Qdrant + Garage 的足迹是**平台承诺**，
> 不是一个依赖。（"air-gap" 是营销表述，未经验证 → INFERRED。）

### 3.12 复用等级

| 能力 | Level | 依据 |
|---|---|---|
| Context Model | **0** | 不存在 `Context` 类型；只有 `EntityContext(entity, str, chunk_id)` |
| Domain Ontology | **1** | `OntologyLoader`/`OntologyClass`/`OntologyProperty`（domain/range/cardinality）是干净的**声明式**类 OWL schema 模型，值得读；但它为提示 LLM 而生、**ingest 后不强制**、且不含规则 |
| Entity / Relationship | **2** | `Term`/`Triple(s,p,o,g)` + RDF-star `QuotedTriple` 是健全、完备、标准符合的**表示法**，可独立于其运行时复用 |
| Business Rules | **0** | NOT FOUND。全库无 rule / condition / invariant / derivation 类型 |
| Decision | **0** | NOT FOUND。无决策对象、无身份、无生命周期 |
| Evidence | **0** | Provenance 是抽取/查询血缘（§3.5），不是附着于决策的证据；无 actor/claim/trigger/rule 关联 |
| **Provenance** | **2** | 命名图中的 PROV-O（`GRAPH_SOURCE`）是**真正优秀的"事实血缘"设计**（哪份文档/哪块 chunk/哪个模型产出了这条 triple）；可作组件复用，**但不是业务证据** |
| Context Update | **0** | 一次写摄取 + 只读检索 + 管理性删除；无时态有效期、无实体状态变更、无证据累积 |
| Knowledge Retrieval | **2** | GraphRAG / DocRAG / SPARQL / 结构化查询作为 flow processor —— 真实可消费，**前提是部署他们的栈** |
| Graph Storage | **2** | Cassandra/Neo4j/FalkorDB/Memgraph 在 `CollectionConfigHandler` 之后；可作后端用，但要继承其 schema |
| Vector Search | **2** | Qdrant/Milvus，两个 embedding 空间（文档块、图实体）；独立组件 |
| Agent Runtime | **0 / 不要** | 栈内 ReAct + plan-then-execute + supervisor + subagents + MCP tools；且**与其余部分不可分离**（§3.9） |
| Workflow Execution | **0 / 不要** | 经配置期望态 + pub/sub 的 flow/blueprint 编排；强大，且**正是我们排除的 RUNTIME** |
| Permission Enforcement | **1** | workspace 作用域 IAM + 角色，但 IAM 自述"信任总线"（§3.9）—— **强制点是客户端属性，不是内核保证** |
| Observability | **2** | 每 processor 的 Prometheus 指标（`base/metrics.py`、`docs/metrics-guide.md`）+ audit publisher + 查询期可解释图；可复用 |
| Domain Evaluation | **0** | NOT FOUND。无对抽取事实的评估/打分/与本体的符合性检查；`TG_SCORE` 是 reranker 分数，不是评测 |

**总结**：TrustGraph 是一个 **摄取 → 抽取 → 存储 → 检索 → agent 的平台**，
经**强制的 pub/sub broker** 端到端耦合。
真正可复用的是 **RDF/quad 表示**、**事实血缘 provenance 设计**、**存储/处理器后端抽象**（Level 2，组件级）；
而 **Context / Rules / Decision / Evidence / Context Update —— 即我们冻结的 Kernel 边界 —— 全部 NOT FOUND**。
READM 里的 "hypergraph" 指 RDF-star 在命名图上的 reification，不是一等 n 元边对象；
"provenance" 指抽取 triple 的数据血缘，不是附着于决策的证据。
**这是基础设施，不是内核。**


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
