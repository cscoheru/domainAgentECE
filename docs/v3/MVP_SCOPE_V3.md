# MVP_SCOPE_V3.md — Kernel V0 最小范围

> Version: 1.0
> Date: 2026-09-20
> Status: **Active**
> 关联: `docs/v3/PRD_V3.md` §31/§32 · `docs/v3/KERNEL_ARCHITECTURE_V3.md` · `docs/adr/ADR-011.md`
> 上游: `docs/product/mvp-scope.md`（v1，EvidenceIQ 范围）· `docs/product_v2/reference-applications.md`

---

## 0. 本文件回答一个问题

> **如果只有 2–4 周工程能力，Kernel 最小可运行版本到底是什么？**

**答案不是"一个平台"，是一条闭环在窄切片上跑通。**

---

## 1. 一句话范围

> **一条 Kernel 闭环，跑在一个窄业务切片上，使用最朴素的进程内运行时，产出可追溯的业务结论。**

---

## 2. 最小闭环（V0 的核心）

```
User Goal
   ↓
Create Context            ← Context Layer
   ↓
Resolve Entities          ← Context Layer（跨系统归一）
   ↓
Retrieve Knowledge / Evidence   ← Semantic Layer + Provider
   ↓
Reason                    ← Judgment Layer（规则优先）
   ↓
Create Decision           ← Judgment Layer
   ↓
Create Domain Workflow    ← Orchestration Semantics（业务语言）
   ↓
Select Agent / Tool / Runtime   ← Orchestration Semantics（V0 固定）
   ↓
Execute                   ← In-Process Executor（V0）
   ↓
Collect Result
   ↓
Create Evidence           ← Evidence Layer
   ↓
Update Context            ← Evidence Layer（闭环）
   ↓
Return Business Outcome
```

**这个 Loop 是 V0 的全部。** 任何一个环节缺失，V0 不成立。

---

## 3. V0 范围内（IN SCOPE）

### 3.1 对象（最小集）

| 对象 | V0 要求 |
|---|---|
| **Context** | 结构化 + 显式生命周期（Create/Enrich/…/Persist） |
| **Entity** | 跨系统归一（渐进流水线，E1 ≥95%） |
| **Relation** | 含时态（`valid_from` / `valid_to`）+ provenance |
| **Ontology** | YAML Context Specification，单领域包 |
| **Knowledge** | 本地知识（文件 / DB），4 路召回 |
| **Evidence** | **V0 新增**：schema + 持久化 + 可追溯 |
| **Reasoning** | 规则引擎（纯代码）+ LLM 轻量叙述 |
| **Decision** | 含 `insufficient_context` 态 |
| **WorkflowSpec** | **V0 新增**：YAML 最小形态（业务步骤，不含 task 图） |
| **AgentRef** | 固定 1–2 个 Agent，code-first 定义 |
| **Policy** | 最小集（该切片的业务规则） |

### 3.2 接口（三类，各一实现）

| 接口 | V0 实现 | 说明 |
|---|---|---|
| `ProviderInterface` | `InProcessProvider` + `LocalKnowledgeProvider` | 直连 Kernel 自己的库 + 本地文件 |
| `AgentRuntimeInterface` | `InProcessAgent` | **一次 LLM 调用，无 loop、无 sandbox** |
| `ExecutionRuntimeInterface` | `InProcessExecutor` | **同步函数调用，无队列、无重试** |

**V0 不实现任何外部 Provider / Runtime 适配器**（Glean / Trigger.dev / DSH / PentAGI 全部留到 V1+）。

### 3.3 业务切片（一个，且只有一个）

V0 **只做一条业务切片**。切片候选（**未定，由客户验证决定**）：

| 候选 | 已有资产 | Kernel 负载 | 备注 |
|---|---|---|---|
| **采购评估**（PR001 合理性分析） | ✅ ECE v0 已有可运行实现 + 评测套件 | K5 核心 | 满足度最高 |
| **审计证据准备**（EvidenceIQ） | ⚠️ 需从零构建 | K4/K5/K6 核心 | 痛点深度最强 |
| HR Q&A | ⚠️ 需构建 | 全轻 | 验证"minimum viable" |
| KM / 其他 | ⚠️ | 待定义 | — |

**V0 的硬约束**：切片必须在 **GO 之前**由客户验证选定（`PRD_V3.md` §37 G-A）。**不得由工程师自行决定。**

### 3.4 权限（硬门）

| 项 | V0 要求 |
|---|---|
| 强制点 | **数据访问层 SQL 子查询**（禁止 post-filter） |
| 硬门 | **Unauthorized Exposure = 0**（一票否决） |
| 演示 | 切用户重问，数据隔离可见（UI 明示"权限不足，未检索 N 条"） |
| 现状 | ❌ **实测未通过**（E2 = 5 暴露 + 5 失败，C47） |

### 3.5 证据与可追溯

| 项 | V0 要求 |
|---|---|
| 每条结论可追溯 | 100%（来源 + 主张 + 时间 + 行为人） |
| `execution_reference` | 可为空（V0 无外部运行时） |
| 不足时行为 | 输出 `insufficient_context`，**不猜测** |

### 3.6 私有化

| 项 | V0 要求 | 现状 |
|---|---|---|
| 离线可运行 | ✅ 必需 | 形态已具备 |
| 单容器 / 内网 | ✅ 必需 | compose 已具备 |
| 数据不外传 | ✅ 必需 | ⚠️ **无验收测试** |
| 模型可替换 | ✅ 必需（OpenAI 兼容端点） | ⚠️ **无验收测试** |

### 3.7 评测

| 套件 | 门槛 | 现状 |
|---|---|---|
| E1 实体消歧 | ≥95% | ✅ 98.5% |
| E2 权限 | 暴露 = 0 | ❌ 5 暴露 + 5 失败 |
| E3 Context 完整性 | ≥90% | ❌ runner 裸崩 |
| E4 Relationships | 0 错误关系 | ❌ runner 裸崩 |
| E5 Temporal | ≥95% | ❌ 0.0% |
| E6 Agent | 人工可接受 | ⏸ 未跑 |
| **纯 RAG baseline 对照** | ECE 优于 baseline | ⏸ 未跑 |

---

## 4. V0 范围外（OUT OF SCOPE）

```
❌ 外部运行时：Trigger.dev / DSH / PentAGI / 任何外部 Provider
❌ 动态 Runtime / Agent 选择（V0 固定）
❌ Agent Loop / Sandbox / Subagent / Session
❌ 队列 / 重试 / 调度 / 持久化执行
❌ 写回企业系统（Actions 保持关闭）
❌ 多租户 / 登录 / 计费 / Admin Console
❌ 多框架切换（单框架，切框架是内容工作非架构工作）
❌ 完整 SOC2 / 等保 控制项集（只做代表性最小集）
❌ 100+ 连接器 / 连接器平台
❌ 企业搜索 / 横向检索平台
❌ Agent Builder UI / Prompt 市场 / Skill 市场 / 可视化编排
❌ 自研向量库 / 图数据库 / 搜索引擎
❌ 移动端 / i18n
❌ 大规模 UI（只做最小演示台）
```

---

## 5. 技术栈约束（V0）

沿用 ECE 既有栈（ADR-002/003/006/009 + `ece/CLAUDE.md` §4）：

```
Python 3.12+ / FastAPI / Pydantic v2 / SQLAlchemy 2.0 / Alembic
PostgreSQL 16 + pgvector + FTS
LLM: OpenAI 兼容端点（支持 vLLM / Ollama 本地部署国产模型）
测试: pytest（unit / integration / security / evaluation 四类 marker）
部署: docker compose（api + postgres），完全离线可运行
```

**禁止**：微服务 / K8s / 消息队列 / Redis / Neo4j / OpenSearch / 任何厂商 SDK。

---

## 6. V0 验收（DoD）

### 6.1 功能验收

```
☐ 一条完整闭环可端到端跑通（§2 的 13 步）
☐ Evidence 对象存在且每条结论可追溯
☐ Domain Workflow Specification 独立于执行图存在
☐ 三类接口各有进程内实现，Kernel 核心零厂商标识（CI 断言）
☐ 切用户重问，数据隔离在 UI 可见
☐ 证据不足时输出 insufficient_context（不猜测）
```

### 6.2 质量验收

```
☐ Permission 暴露 = 0（硬门，一票否决）          ← 当前未通过
☐ E1 ≥ 95%                                      ← 当前 98.5% ✅
☐ E3 ≥ 90%                                      ← 当前裸崩
☐ Provenance = 100%
☐ ECE 优于纯 RAG baseline                        ← 未跑
☐ 确定性判断零 LLM 调用（可检）
```

### 6.3 部署验收

```
☐ 断网环境可启动（无外网依赖）
☐ 本地模型（国产开源）可替换（OpenAI 兼容端点）
☐ 数据不外传（无出站网络调用，可检）
☐ 审计日志本地留存
```

### 6.4 演示验收

```
☐ 10–15 分钟完整演示
☐ 演示中明确展示：权限隔离 / 规则推理 / 证据可追溯
☐ 所有输出标注 "Reference Case / Demo Case"，不冒充真实客户
```

---

## 7. V0 的规模红线

| 维度 | 上限 |
|---|---|
| 业务切片 | **1** |
| 领域包 | **1** |
| 框架 | **1** |
| Agent | **1–2** |
| Provider 实现 | **2**（进程内 + 本地知识） |
| Runtime 实现 | **1**（进程内） |
| 连接器 | **≤3**（mock） |
| 控制项/评估项 | **代表性最小集** |
| 新增外部依赖 | **0** |
| 工期 | **2–4 周** |

**超出任一上限 = V0 范围失控**，应回退到 `PRD_V3.md` §32 重新裁剪。

---

## 8. V0 与 v1 `mvp-scope.md` 的关系

| v1 范围（EvidenceIQ） | V3 处置 |
|---|---|
| 1 Persona / 1 Problem / 1 Workflow / 1–2 Agents | ✅ 继承同样的规模纪律 |
| ContextAdapter 3 工具（search/get_record/create_task） | ✅ 继承，归入 ProviderInterface |
| MockAdapter + GleanAdapter 骨架 | ✅ 继承 Mock-first；Glean 适配器**推迟到 V1** |
| CI 断言 `src/domain/**` 无 `glean|mcp` | ✅ 继承并扩展到 provider/runtime 厂商标识 |
| 排除 ISO27001 多框架 | ⚠️ **需重新评估**——红队 G2 指出这可能排除了可达市场的主流框架 |
| 排除真权限系统（"留给 Glean 继承"） | ❌ **推翻**——V3 中权限是 Kernel 一级职责，不可外推 |

**关键差异**：v1 把权限外推给 Glean；V3 把权限作为 Kernel 的第一硬门。这是 V3 最重要的范围变化。

---

## 9. 前置条件（V0 开工前必须满足）

| # | 条件 | 现状 | 可并行 |
|---|---|---|---|
| G-A | 客户验证 Step 0（48h CA）+ Step 0.6（中国三问） | ❌ 未执行 | 是 |
| G-B | 国产开源模型实测 | ❌ 未执行 | 是 |
| G-C | Permission 硬门 E2 = 0 | ❌ 未通过 | 是（**建议优先**） |
| G-D | 业务切片选定 | ❌ 未定 | 依赖 G-A |

**G-C 是唯一不依赖客户的**，可立即推进。已有明确根因清单与修复单。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
