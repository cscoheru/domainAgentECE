# MVP_SCOPE_V3.md — Kernel V0 最小范围

> Version: 1.0
> Date: 2026-09-20
> Status: **Active — §2/§3/§4/§7 已被取代**
>
> ⚠️ **V3 收口修订（2026-09-20）**：本文件的 **§2（13 步闭环）、§3（V0 范围内）、§4（范围外）、§7（规模红线）已被 `V3_CLOSEOUT.md` §2 取代**。
> V0 收缩为 **6 步最小闭环**（Context → Entity/Knowledge → 一个确定性 Business Rule → Decision → Evidence → Context Update），
> 且**不建三类接口抽象层**、**不实现任何 Adapter**。§5/§6/§8/§9 仍然有效。
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

### 3.2 运行时（**V0 不建三类接口抽象层**）

> ⚠️ **V3_CLOSEOUT §2.2 明确**：**V0 不建三类接口抽象层，不实现任何 Adapter。**
> V0 只保留**具体实现**，直接调用。

| V0 的三个具体件（**不是 interface**） | 说明 |
|---|---|
| **Local Provider** | 直连 Kernel 自己的库 + 本地文件 |
| **InProcessExecutor** | **同步函数调用，无队列、无重试** |
| **固定 Agent** | **单次 LLM 调用，无 loop、无 sandbox**；**无 Selection 概念** |

**V0 不实现任何外部 Provider / Runtime 适配器**（Glean / Trigger.dev / DSH / PentAGI 全部留到 V1+）。

> 📌 **HISTORICAL / V1+ DIRECTION**：`ProviderInterface` / `AgentRuntimeInterface` /
> `ExecutionRuntimeInterface` 三类接口的设计**曾出现在 V3 的早期草案**（`KERNEL_ARCHITECTURE_V3.md` §3、
> `docs/adr/ADR-011.md` §3），作为**可替换性设计**。`V3_CLOSEOUT.md` §2.4 已将其
> **降为 V1+ 方向**：V0 不建抽象层。**不得**把三类 interface 当成 V0 交付物。

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
| 现状 | ✅ **已通过**（E2 = 61/61，0 暴露 0 失败）。*历史*：曾为 5 暴露 + 5 失败（C47），已由 ece `037260b` 修复 |

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

> 当前状态（2026-09-20，R40R2.7 后）。**旧状态一律标注 *historical***，不作为当前引用。

| 套件 | 门槛 | 现状 |
|---|---|---|
| E1 实体消歧 | ≥95% | ✅ **98.5%** |
| E2 权限 | 暴露 = 0 | ✅ **61/61，0 暴露 0 失败**（*historical*：曾为 5 暴露 + 5 失败） |
| E3 Context 完整性 | ≥90% | ⚠️ **15.0%（runner 已不崩，暴露真实失败）** —— 见下方说明 |
| E4 Relationships | 0 错误关系 | ✅ 100%（30/30）—— **注意：边界 `[0,100]` 使对象缺失时也判定通过，属 vacuous pass** |
| E5 Temporal | ≥95% | ❌ **0.0%（runner 已不崩，暴露真实失败）** |
| E6 Agent | 人工可接受 | ⏸ 未跑（需 LLM） |
| **纯 RAG baseline 对照** | ECE 优于 baseline | ⏸ 未跑 |

**E3 / E5 真实失败的性质（R40R2.7 已定位，**未修**，待裁定）**：

1. **E3 的 85 个失败 = 数据集过期，不是 Kernel 逻辑失败。**
   `_next_display_id` 按"现有最大数字 +1"分配；`test_s14_seed_idempotent` 的 DELETE+重播
   会让 `display_id` **整体上移**（当前 PR 的 display_id 已是 `PR202–PR401`，`PR001` 已不存在）。
   而 `e3_context.json` 引用的正是 `PR001` 等旧 display_id。
   **诊断证据**：从当前 DB 重新生成数据集后，E3 = **100.0% PASS**。
   （诊断在 `/tmp` 进行，仓库数据集已还原 —— **未用改数据的方式让测试变绿**。）

2. **E5 有超越过期的真实问题**（即使数据集重新生成仍为 0.0%）：
   - `expected_count = 5`，实测 **6** —— 多出的一条来自**测试创建的**关系
     （`src.system = 'test:seed_relationships_test'`）。属测试污染。
   - `as_of=2024-01-01` 命中 6 条，而 `as_of=2024-12-31` / `2025-06-30` 命中 **0 条** ——
     关系行的 `valid = [None, None]`（无有效期），时态过滤对无窗口行的语义需明确。

3. **E4 的 100% 是 vacuous**：对象不存在 → 0 条关系 → 落在 `[0,100]` 内即判通过。

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
☐ 一条完整闭环可端到端跑通（§2 的 6 步，以 V3_CLOSEOUT §2 为准）
☐ Evidence 对象存在且每条结论可追溯
☐ Domain Workflow Specification 独立于执行图存在
☐ **V0 运行时三件就位**：Local Provider / InProcessExecutor / 固定 Agent
   （**不要求**三类 interface 抽象层 —— V3_CLOSEOUT §2.2）
☐ Kernel 核心零厂商标识（CI 断言）
☐ 切用户重问，数据隔离在 UI 可见
☐ 证据不足时输出 insufficient_context（不猜测）
```

### 6.2 质量验收

```
☑ Permission 暴露 = 0（硬门，一票否决）          ← **已通过**（61/61）
☑ E1 ≥ 95%                                      ← **98.5%**
⚠ E3 ≥ 90%                                      ← **15.0%**（runner 已不崩；失败为数据集过期，待裁定）
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
| Agent | **1**（固定，**无 Selection**） |
| Local Provider | **1** |
| InProcessExecutor | **1** |
| **接口抽象层** | **0**（V3_CLOSEOUT §2.2：V0 不建三类 interface） |
| 外部 Provider / Runtime 适配器 | **0** |
| 连接器 | **≤3**（mock） |
| 控制项/评估项 | **代表性最小集** |
| 新增外部依赖 | **0** |
| 工期 | **2–4 周**（Codex 判定：**可比 2–4 周更小**） |

**超出任一上限 = V0 范围失控**，应回退到 `PRD_V3.md` §32 重新裁剪。

---

## 8. V0 与 v1 `mvp-scope.md` 的关系

| v1 范围（EvidenceIQ） | V3 处置 |
|---|---|
| 1 Persona / 1 Problem / 1 Workflow / 1–2 Agents | ✅ 继承同样的规模纪律 |
| ContextAdapter 3 工具（search/get_record/create_task） | ✅ 继承为 **Local Provider 的 3 个方法**（V0 不建 interface 抽象层） |
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
| G-C | Permission 硬门 E2 = 0 | ✅ **已通过**（61/61，2026-09-20） | — |
| G-D | 业务切片选定 | ❌ 未定 | 依赖 G-A |

**G-C 已关闭**（原为唯一不依赖客户、可立即推进项；已由 ece `037260b` + `32a0b92` 完成）。
当前剩余前置：**G-A / G-B / G-D** 均依赖客户或外部模型实测。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
