# Track B Execution Plan — Sprint × Phase 5 Kernel 映射 + K7 MCP 详细 spec

> **Phase**: Track B 启动
> **Last Updated**: 2026-09-13
> **目的**: 把 Phase 5 的 8 个 Kernel(K1-K8)+ D1 数据底座映射到 ECE Sprint 0-6,并给出 Phase 5 §3.1 识别的真缺口(K7 MCP Tool Layer)的详细 spec
> **消费者**: ECE v0 session(`github.com/cscoheru/ece`)

---

## 0. 速读

ECE TASKS.md 当前 Sprint 0-6 任务**大部分已覆盖 K1-K8**,**真缺口是 K7 MCP Tool Layer**——需要新增 Sprint 4 S4.5 任务(详见 §4)。

---

## 1. Sprint × Kernel 映射矩阵

| Sprint | ECE TASKS 任务 | K1 Permission | K2 Context Assembly | K3 Entity Resolution | K4 Domain Ontology | K5 Domain Reasoning | K6 Domain Evaluation | K7 MCP Tool | K8 Query Planner | D1 Postgres |
|---|---|---|---|---|---|---|---|---|---|---|
| **0** | S0.1 uv + pyproject | — | — | — | — | — | — | — | — | (基础) |
| 0 | S0.2 docker-compose + pgvector | — | — | — | — | — | — | — | — | ✅ |
| 0 | S0.3 CI(ruff + mypy + pytest + import-linter) | — | — | — | — | — | — | — | — | — |
| 0 | S0.4 check_api_docs.py | — | (间接) | — | — | — | — | — | — | — |
| 0 | S0.5 Alembic 初始迁移 | — | — | — | — | — | — | — | — | ✅ |
| 0 | S0.6 合成数据集生成器 | — | — | — | — | — | — | — | — | (data) |
| **1** | S1.1 Connector Interface + CSV/JSON/docs | — | — | — | — | — | — | △ partial | — | — |
| 1 | S1.2 Entity/Relationship 入库 | — | — | (下游) | — | — | — | — | — | ✅ |
| 1 | S1.3 Entity/Relationship 只读 API | — | — | (下游) | — | — | — | — | — | — |
| 1 | S1.4 seed.py 幂等 | — | — | — | — | — | — | — | — | ✅ |
| **2** | S2.1 Identity 解析(X-User-Id → person + roles + dept) | ✅ partial | — | — | — | — | — | — | — | — |
| 2 | S2.2 Permission Engine(acl_entries + classification + 判定顺序 + PermissionScope SQL 过滤) | ✅ | — | — | — | — | — | — | — | ✅ |
| 2 | S2.3 Entity Resolution 流水线(exact→normalized→alias→rule→embedding→LLM) | — | — | ✅ | — | — | — | — | — | ✅ |
| 2 | S2.4 E2 安全套件 + 间接泄露用例 | ✅ verification | — | — | — | — | (准备) | — | — | — |
| **3** | S3.1 Context Spec 加载器(YAML→内存模型,版本化) | — | ✅ partial | — | (下游) | — | — | — | — | — |
| 3 | S3.2 Assembly Pipeline 12 步(fail-closed + temporal + limits + denied) | — | ✅ | — | — | — | — | — | — | — |
| 3 | S3.3 Provenance(每项 source + context_items) | — | ✅ partial | — | — | — | — | — | — | ✅ |
| 3 | S3.4 /context 完整实现 | — | ✅ | — | — | — | — | — | — | — |
| 3 | S3.5 E3/E4/E5 评测 | — | — | — | — | — | ✅ | — | (验证) | — |
| **4** | S4.1 文档 ingestion(分块 + tsv + embedding) | — | — | — | — | — | — | — | ✅ partial | ✅ |
| 4 | S4.2 Query Planner(4 路召回 + Entity Linking + Permission Filter + merge/rank) | ✅ integration | — | — | — | — | — | — | ✅ | — |
| 4 | S4.3 /search | — | — | — | — | — | — | — | ✅ | — |
| 4 | S4.4 性能基准(seed 全量下 /context p95 < 1.5s) | — | ✅ performance | — | — | — | — | — | (perf) | ✅ |
| **4 NEW** | **S4.5 MCP Tool Layer(ADR-004)** | — | — | — | — | — | — | **✅ FULL** | — | — |
| **5** | S5.1 领域规则库(比价 / 价格偏离 / 审批链 / 政策匹配) | — | — | — | (数据) | ✅ partial | — | — | — | — |
| 5 | S5.2 Procurement Agent(Package+Question→结构化输出) | — | ✅ consume | — | ✅ | ✅ | — | — | — | — |
| 5 | S5.3 /actions/preview + /actions/execute(关闭) | ✅ (写回 disable) | — | — | — | — | — | — | — | — |
| 5 | S5.4 E6(50 问)+ 纯 RAG baseline 对照 | — | — | — | — | — | ✅ | — | (验证) | — |
| **6** | S6.1 /audit/context/{id} + Debugger UI | ✅ verification | — | — | — | — | (visualization) | — | — | ✅ |
| 6 | S6.2 Demo script 固化(PR001 + U002) | ✅ demo | ✅ demo | — | — | — | — | — | — | — |
| 6 | S6.3 make eval-report | — | — | — | — | — | ✅ | — | — | — |
| 6 | S6.4(选做)迷你换域演练(audit spec 走通 /context) | — | ✅ | — | ✅(新 spec) | — | — | — | — | — |
| 6 | S6.5 私有化验收(断网 + 本地 Ollama + 国产模型 + Demo 数据集) | (offline) | — | — | — | (offline) | (offline) | (offline) | — | — |

### 1.1 覆盖率统计

| Kernel | Sprint 覆盖 |
|---|---|
| K1 Permission Engine | Sprint 2(S2.1+S2.2)+ Sprint 4(S4.2 集成)+ Sprint 6(S6.1 验证) |
| K2 Context Assembly | Sprint 3(全部)+ Sprint 5(S5.2 consume)+ Sprint 6(S6.2 demo) |
| K3 Entity Resolution | Sprint 2(S2.3) |
| K4 Domain Ontology | Sprint 3(下游)+ Sprint 5(S5.1 data)+ Sprint 6(S6.4 换域) |
| K5 Domain Reasoning | Sprint 5(S5.1 + S5.2) |
| K6 Domain Evaluation | Sprint 2(S2.4)+ Sprint 3(S3.5)+ Sprint 5(S5.4)+ Sprint 6(S6.3) |
| **K7 MCP Tool Layer** | **Sprint 1(S1.1 partial)+ Sprint 4(NEW S4.5 FULL)** |
| K8 Query Planner | Sprint 4(S4.1 + S4.2 + S4.3) |
| D1 Postgres | Sprint 0(S0.2 + S0.5)+ Sprint 1(S1.2 + S1.4)+ Sprint 3(S3.3)+ Sprint 6(S6.1) |

**结论**:ECE TASKS Sprint 0-6 + Sprint 4 NEW S4.5 = **完整覆盖 K1-K8 + D1**。Phase 5 §3.1 识别的真缺口(K7)通过 S4.5 补齐。

---

## 2. Sprint 详细建议

### 2.1 Sprint 0(2 天)—— 工程地基

**目标**:ECE v0 能跑起来 + 测试 CI 闭环

**ECE TASKS S0.1-S0.6 全部保留**。新增验收点(基于 Phase 5):

| Task | 现有 | 新增验收 |
|---|---|---|
| S0.1 uv + pyproject | ✓ | (无新增) |
| S0.2 docker-compose + pgvector | ✓ | Postgres 镜像必须含 pgvector 扩展(ADR-009) |
| S0.3 CI | ✓ | 新增:**import-linter** 强制 `src/ece/` 不 import `src/domain_packs/`(ADR-010 领域包隔离铁律) |
| S0.4 check_api_docs.py | ✓ | (无新增) |
| S0.5 Alembic | ✓ | (无新增) |
| S0.6 合成数据集生成器 | ✓ | 数据集必须含**对抗性用例**(同名人员/同供应商多名称/历史组织变更/权限边界/不完整资料)(DATA_MODEL § 末段) |

### 2.2 Sprint 1(4 天)—— 数据层

**目标**:3 个 mock connector + entities/relationships schema + 只读 API

**ECE TASKS S1.1-S1.4 保留**。新增验收点:

| Task | 现有 | 新增验收 |
|---|---|---|
| S1.1 Connector Interface | ✓ | 包含 `src/ece/mcp/` 子目录占位(S4.5 占位)(避免后期改 import) |
| S1.2 入库 | ✓ | ontology.yaml 三元组校验(拒绝未声明组合)(DATA_MODEL §2) |
| S1.3 只读 API | ✓ | 404 防探测一致性(API.md §3) |
| S1.4 seed.py 幂等 | ✓ | (无新增) |

### 2.3 Sprint 2(5 天)—— 身份 + 权限 + 消歧

**目标**:E1 + E2 评测可跑,Permission Before Intelligence 铁律生效

**ECE TASKS S2.1-S2.4 保留**。新增验收点:

| Task | 现有 | 新增验收 |
|---|---|---|
| S2.1 Identity | ✓ | (无新增) |
| S2.2 Permission Engine | ✓ | **`PermissionScope` 必须 SQL 子查询层强制**(不是 post-filter,不是 prompt);**E2 = 0** 是 CI 阻断门槛(ADR-003);`/actions/execute` 必须 403(env kill-switch) |
| S2.3 Entity Resolution | ✓ | `method='llm'` 一律 `status='pending'`,不参与 Assembly(ADR-007 LLM 猜测不得直接成为企业事实) |
| S2.4 E2 安全套件 | ✓ | 新增**间接泄露专项**(被拒对象的内容/存在推断);Cline 红队对 RBAC 完整性的关注 |

### 2.4 Sprint 3(6 天)—— Context 核心

**目标**:E3/E4/E5 评测通过,Context Assembly 12 步流水线运行

**ECE TASKS S3.1-S3.5 保留**。新增验收点:

| Task | 现有 | 新增验收 |
|---|---|---|
| S3.1 Context Spec | ✓ | YAML 必须有 `version`;spec 变更走 git 评审;评测集与 spec_version 绑定(EVALUATION §3) |
| S3.2 Assembly 12 步 | ✓ | **fail-closed**(任何步骤失败返回错误或 insufficient_context,不降级为无权限过滤) |
| S3.3 Provenance | ✓ | (无新增) |
| S3.4 /context | ✓ | (无新增) |
| S3.5 E3/E4/E5 评测 | ✓ | E4 错连 = 0;E5 期间准确率 ≥ 95% |

### 2.5 Sprint 4(4 天 + 1 NEW task)—— 检索面 + MCP

**目标**:E3 检索子集 ≥90%;MCP Tool Layer 原生 MCP 化,Claude Code / Cursor / Codex 可调

**ECE TASKS S4.1-S4.4 保留**。**新增 S4.5 MCP Tool Layer**(详见 §4)。

| Task | 现有 | 新增验收 |
|---|---|---|
| S4.1 ingestion | ✓ | FTS 用 `simple + bigram` 兜底(zhparser 可选);embedding 默认 `bge-small-zh-v1.5` (512d);ECE_EMBED_PROVIDER=local\|api 切换 |
| S4.2 Query Planner | ✓ | 4 路召回顺序:Keyword → Vector → Structured → Relationship;Permission Filter 在 merge 后;`PermissionScope` 复用 S2.2 |
| S4.3 /search | ✓ | meta.denied_count 暴露(API.md §2) |
| S4.4 性能基准 | ✓ | seed 全量下 /context p95 < 1.5s;不达标 → 加索引/物化(ADR-009 触发),不引 Redis |
| **S4.5 NEW** | — | **详见 §4 MCP Tool Layer 详细 spec** |

### 2.6 Sprint 5(5 天)—— Procurement Agent + 评测

**目标**:E6 ≥50 问,通过;Procurement Agent 跑通"PR001 合理性"

**ECE TASKS S5.1-S5.4 保留**。新增验收点:

| Task | 现有 | 新增验收 |
|---|---|---|
| S5.1 领域规则库 | ✓ | 纯 Python 函数(可单测);规则 findings 注入 prompt(不替代规则判断) |
| S5.2 Procurement Agent | ✓ | temperature=0;evidence[] 每条 sid 必须存在 package sources |
| S5.3 Actions | ✓ | /actions/execute 必须 403(双保险) |
| S5.4 E6 + 纯 RAG baseline | ✓ | (EVALUATION §5 H3)ECE 显著优于纯向量 RAG baseline |

### 2.7 Sprint 6(4 天)—— Debugger + 演示 + 定稿

**目标**:15 分钟 Demo 跑通;Sprint 6.5 私有化验收通过

**ECE TASKS S6.1-S6.5 保留**。新增验收点:

| Task | 现有 | 新增验收 |
|---|---|---|
| S6.1 Audit/Debugger UI | ✓ | 3 页 UI:Ask / Context Explorer / Debugger(服务端渲染,禁重型前端) |
| S6.2 Demo script | ✓ | 含**PR001 合理性(有权限)→ U002(无权限)→ insufficient_context** 完整路径 |
| S6.3 eval-report | ✓ | README 指标表更新 |
| S6.4 迷你换域演练 | ✓ | **验证 H5**(PRD §36):audit spec 走通 /context = 领域包隔离铁律生效 |
| S6.5 私有化验收 | ✓ | **断网 + 本地 Ollama + 国产模型 + Demo 数据集** 全流程通过(v3 §0.8 技术要求) |

---

## 3. Phase 5 §3.1 缺口识别复盘

Phase 5 §3.1 列出 5 个缺口:
- K3 Entity Resolution(Sprint 2 覆盖)
- K4 Domain Ontology(Sprint 5 覆盖)
- K5 Domain Reasoning(Sprint 5 覆盖)
- K6 Domain Evaluation(分散 Sprint 2-6 覆盖)
- K7 MCP Tool Layer(**真缺口——Sprint 1 partial + Sprint 4 无任务**)

**K7 是真缺口**——ECE TASKS Sprint 4 只有 S4.1-S4.4(检索面),没有 MCP server/client 实现。

**新增 S4.5** 修补 K7 缺口(详见 §4)。

---

## 4. S4.5 MCP Tool Layer 详细 spec(Phase 5 §3.1 + ADR-004)

### 4.1 任务定义

| 项 | 内容 |
|---|---|
| **任务 ID** | S4.5 |
| **名称** | MCP Tool Layer 原生 MCP 化 |
| **目标** | ECE 自建 MCP server + MCP client,实现与 Glean/Claude Code/Cursor/Codex 等 MCP-compatible runtime 互操作 |
| **Phase 5 锚定** | K7 MCP Tool Layer + ADR-004 |
| **证据** | [C19] Glean Remote MCP Server(tenant 级 / 权限感知 / OAuth DCR);[C37] Fall'25 矩阵 remote MCP servers beta;[C39] Glean 官方运营 developers.glean.com MCP server,Claude Code / Cursor / Codex / Gemini CLI 一键集成 |

### 4.2 接口设计(最小集)

**MCP Server 暴露**(ECE 作为 server,被 Claude Code 等调用):

```python
# 最小工具集
TOOLS = [
    Tool(
        name="search",
        description="Search ECE Context (4-lane retrieval + Permission filtered)",
        input_schema={
            "query": str,           # 用户问题
            "kinds": list[str],     # ["keyword", "vector", "structured", "relationship"]
            "top_k": int,
            "filters": dict | None, # entity_type / doc_type 等
        },
        handler=ece.handlers.search,
    ),
    Tool(
        name="get_record",
        description="Get entity by display_id (Permission filtered)",
        input_schema={
            "entity_type": str,
            "display_id": str,
        },
        handler=ece.handlers.get_record,
    ),
    Tool(
        name="create_task",
        description="Create task in mock ticket system (Preview only, not execute)",
        input_schema={
            "title": str,
            "assignee": str,
            "due": str,  # ISO date
            "context_ref": str | None,
        },
        handler=ece.handlers.create_task_preview,
    ),
    Tool(
        name="send_message",
        description="Send message (Preview only)",
        input_schema={
            "channel": str,
            "body": str,
            "context_ref": str | None,
        },
        handler=ece.handlers.send_message_preview,
    ),
]
```

**MCP Client 调用 Glean**(ECE 作为 client,使用 Glean MCP server):

```python
# Phase 4+ POC 时启用
# 当前 v0 阶段不实现(可借 Glean API + Indexing API 替代)
```

### 4.3 文件结构

```
src/ece/mcp/
├── __init__.py
├── server.py           # MCP server 实现,启动时注册 TOOLS 列表
├── client.py           # MCP client(Phase 4+ POC 启用)
├── transport.py        # stdio + HTTP transport
├── auth.py             # 与 Permission Engine 集成(每个 tool call 强制 PermissionScope)
└── README.md           # 集成指南 + Claude Code 接入命令
```

> **依赖注记**: `mcp` SDK 在 **S4.5 动工时** 才引入 pyproject(Sprint 0 不加,S0.1 依赖列表保持最小地基 fastapi/pydantic/sqlalchemy/alembic/psycopg/pgvector/pytest/ruff/mypy)

**关键集成**:
- `auth.py` 调用 `src/ece/permissions/` 的 `PermissionScope`
- `server.py` 在 `src/ece/main.py` FastAPI app 启动时注册
- 不绕过 Context Assembly / Permission Before Intelligence 铁律

### 4.4 集成命令(用户手册)

**Claude Code 接入**(在 ece 仓库根目录执行;如需全局再加 `-s user`):
```bash
claude mcp add ece-context -- python -m ece.mcp.server
```

**Cursor 接入**(~/.cursor/mcp.json):
```json
{
  "mcpServers": {
    "ece-context": {
      "command": "python",
      "args": ["-m", "ece.mcp.server"],
      "cwd": "/path/to/ece"
    }
  }
}
```

**Codex 接入**(类似)。

### 4.5 测试要求

```python
# tests/integration/test_mcp_server.py
def test_search_tool_permission_enforced():
    """调用 search tool 必须经 PermissionScope 过滤"""
    # U001 看 PR001,U002 不看 → 验证

def test_get_record_returns_404_for_missing():
    """get_record 不存在/无权限时统一 404(API.md 防探测)"""

def test_create_task_is_preview_only():
    """create_task 必须不真正创建工单(Preview 模式)"""
```

### 4.6 验收 DoD

- [ ] `python -m ece.mcp.server` 启动成功,注册 4 个工具
- [ ] Claude Code 中 `claude mcp list` 显示 `ece-context` 已连接
- [ ] 在 Claude Code 中调用 `search("PR001")` 返回权限过滤后的结果
- [ ] `tests/integration/test_mcp_*.py` 全部通过
- [ ] E2 安全套件 E2 仍 = 0(MCP 不能绕过权限)
- [ ] 离线模式可用(stdio transport,无外部依赖)

### 4.7 为什么这是 Phase 5 真缺口

PRD §6 M06 + Phase 2 §M06 + ADR-004 + [C19][C37][C39] 多重证据表明:
- MCP 是 Agent 工具层事实标准
- Glean 官方已实现 + 官方支持 Claude Code/Cursor/Codex 一键集成
- 我方如果不实现 MCP = 与 Claude Code/Cursor 集成缺失 = 失去 demo 与开发的便利
- ECE MCP server 让开发工具可直接调 ECE search/get_record = 开发体验提升 + 演示流畅

---

## 5. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| S4.5 MCP 实现延期 | 中 | Track A K7 决策失效 | S4.1-S4.4 检索面先完成,S4.5 推迟到 Sprint 5 头 |
| MCP spec 2025-2026 仍在变 | 中 | 兼容性问题 | 用 `mcp[cli]` Python SDK 跟进官方版本 |
| ECE domain_packs 隔离被破坏 | 低 | 违反 ADR-010 | import-linter CI 强制 |
| Sprint 6 私有化验收失败(模型掉档) | 中 | v3 主路径 D 受挫 | Sprint 2 即用 DeepSeek/Qwen 双模型实测(规则优先架构已对此设计) |
| Phase 5 §3.1 其他缺口(S4.5 之外)被忽略 | 低 | K3-K6 部分未达 DoD | 已有 Sprint 2/5 任务覆盖 |

---

## 6. ECE 工程铁律符合性验证

| 铁律 | Sprint 验证 |
|---|---|
| Permission Before Intelligence(P2) | S2.2 + S4.2(SQL 子查询层)+ S2.4(E2=0 CI 阻断) |
| 禁止 Demo 绕过核心抽象 | S6.2(Demo 必须走 /context API,不走 raw DB) |
| 垂直纪律 | Sprint 0-6 全部 Postgres-only(ADR-009);无 OpenSearch/Redis/Neo4j |
| 领域包隔离 | S0.3(import-linter CI)+ S6.4(迷你换域演练) |
| LLM 不可知 | S5.2(temperature=0)+ S5.4(双模型对照)+ S6.5(本地 Ollama + 国产模型) |

**全部铁律通过 Sprint 覆盖验证**。

---

## 7. 下一步(给 ECE session)

1. 把本 spec 中"新增 Sprint 4 S4.5 MCP Tool Layer"任务写入 `ece/TASKS.md`(用户授权后)
2. 按 `ece/TASKS.md` Sprint 0 启动
3. 每 Sprint 完成后跑对应 E 套件(EVALUATION.md §1)
4. 每 Sprint commit + 汇报(ECE 仓,不回本仓)
5. 完成所有 Sprint 后产出 v0 Demo,做 Track A 验证(15 分钟)
