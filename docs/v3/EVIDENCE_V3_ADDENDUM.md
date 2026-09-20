# Evidence Addendum V3 — 新增证据 C43–C48

> Version: 1.0
> Date: 2026-09-20
> Status: **Active**
> 上游: `docs/research_v2/evidence-matrix-v2.md`（C01–C42）
> 用途: PRD V3 引入 Kernel 与 **执行运行时 / Agent Harness** 的边界比较，涉及三个此前**从未进入本项目证据库**的外部系统（Trigger.dev / DSH / PentAGI）。按 `RESEARCH_PRD_V2.md` §4 证据纪律，任何新引入的外部系统必须有 C 编号，否则不得作为设计前提。

---

## 0. 为什么需要本文件

`RESEARCH_PRD_V2.md` §4.6 规定：证据编号承接 C01–C25，新增从 C26 起；所有文档引用 Glean 能力必须标 C 编号。V2 阶段已用至 **C42**。

V3 阶段的核心新增论述是：

> **Kernel 位于 Trigger.dev / DSH / PentaGI / Glean 等执行与上下文能力之上。**

这句话引入了四个外部系统与一条用户陈述。其中：

| 系统 | 在 C01–C42 中的存在 |
|---|---|
| Glean | 已充分覆盖（C01–C42） |
| Glean Agent Harness | C25 / C41 — **STILL_UNKNOWN**（导航有此名，无详情页） |
| Trigger.dev | **零引用**（全仓 grep 无命中） |
| DeepSeek Harness (DSH) | **零引用** |
| PentAGI / PentaGI | **零引用** |
| Video Factory | **零引用** |

因此新开 **C43–C48**。**本文件不修改 `docs/research_v2/evidence-matrix-v2.md`**（V2 交付物冻结），C43+ 独立成册。

---

## 1. 置信度定义（沿用项目既有四级 + 状态标签）

| 级别 | 含义 |
|---|---|
| `CONFIRMED` | 官方原文 / 一手可复现 |
| `STRONGLY_INFERRED` | 多来源交叉印证，但非官方原文直述 |
| `INFERRED` | 合理推断 |
| `UNKNOWN` | 无法确认；**不得作为设计前提** |

附加状态标签（沿用 V2）：`TOOL_BLOCKED`（抓取工具被限制）、`SECONDARY_ONLY`（仅有二手来源）、`FIRST_HAND`（本机一手核验）。

---

## 2. 新增证据

### C43 — Trigger.dev 是 Durable Workflow / Execution Runtime

| 项 | 内容 |
|---|---|
| **Claim** | Trigger.dev 是一个开源（Apache 2.0）的**持久化工作流 / 后台任务执行平台**，面向 TypeScript/JS。核心能力是 Tasks / Runs / Queues & Concurrency / 自动重试 / Waits & Waitpoints（human-in-the-loop 暂停）/ 调度（cron）/ 持久化（redeploy、crash 后存活）/ 完整 tracing 与实时订阅（Realtime API）。支持 Cloud 与自托管。 |
| **Source** | trigger.dev 官网 + `trigger.dev/docs/introduction` + `github.com/triggerdotdev/trigger.dev`，经 WebSearch 检索面（2026-09-20） |
| **Evidence** | 官方自述 "build and deploy durable AI agents and workflows"；文档描述 "no timeouts"、tasks "inherently durable, surviving refreshes, redeploys, and crashes"、`retry` 配置对象（maxAttempts / minTimeoutInMs / factor / randomize）、batch triggering up to 1,000 payloads、OpenTelemetry spans 级 tracing。 |
| **Confidence** | `CONFIRMED`（多个官方面交叉一致） |
| **Status** | `TOOL_BLOCKED` — 直接原文抓取被 claude.ai WebFetch 拒绝（与 v2 F1 同类的工具特定限制，非网络封锁）。上述结论来自检索面摘要，**未逐字核验原文段落**。 |
| **Last Verified** | 2026-09-20 |

**对本项目的含义**：Trigger.dev 的能力集合（queue / retry / scheduler / durable execution / worker runtime / concurrency）**正好落在 ECE `CLAUDE.md` 铁律 3「垂直纪律」明令禁止自研的清单上**。这使"自研编排层"与"集成 Trigger.dev"成为一对必须由 ADR 裁决的选项（见 `docs/adr/ADR-011.md`）。

---

### C44 — DeepSeek Harness (DSH) 是插件化 Agent Runtime

| 项 | 内容 |
|---|---|
| **Claim** | DeepSeek Harness（`dsh`）是 DeepSeek 于 2026-08-13 开源的 Agent Runtime（MIT）。设计口号 "Everything is a Plugin"，构建于开源插件运行时 **Cordis** 之上——model / tool / skill / session / sandbox / storage / agent loop / scheduling / UI 皆为插件。既开箱提供 coding agent（Standard preset），也可作为构建自有 agent 的底盘（替换 sandbox / model router / loop 只需换插件）。无强制模型供应商；`llm-pi-ai` 适配任意 OpenAI 兼容端点。每次运行写入 append-only session log（zstd 压缩 JSONL），提供 Trajectory 视图（按来源检视 / resume / fork / search / replay）。Subagent 可作为完整 DSH runtime 在子进程中运行。 |
| **Source** | npm `@deepseek-ai/dsh-agent`；`github.com/salathleizhang/dsh-agent-sdk`；多篇第三方评测（deepinfra / modellix / orcarouter / withone）经 WebSearch（2026-09-20） |
| **Evidence** | 多处独立来源对下述结构描述一致：Cordis 插件底座、四预设（Standard / Code-PTC / Minimal / Creator）、`npx @deepseek-ai/dsh web` 本地 3080 端口、`$DSH_HOME`（默认 `~/.dsh`）配置。 |
| **Confidence** | `STRONGLY_INFERRED` |
| **Status** | `SECONDARY_ONLY` — **未取得原始仓库 README 逐字核验**。来源包含大量教程/评测类二手内容；DeepSeek 官方一手表述未核。发布两年内可能有破坏性变更（来源自述为 developer preview）。 |
| **Last Verified** | 2026-09-20 |

**对本项目的含义**：DSH 的能力集合（agent loop / tool runtime / session / sandbox / subagent runtime）同样落在铁律 3 禁止自研的清单上。DSH 是 **Agent Harness** 的实例，而 Kernel 必须位于其**之上**。

**旁证（本机）**：用户 `fish-harness` 项目留有向后兼容常量 `DEFAULT_DSH_BIN = "dsh"`（标注 "never spawned"），说明 DSH 曾被评估/试用过但未被采用。此为本机一手观察，`FIRST_HAND`，但不构成能力证据。

---

### C45 — PentAGI 是自主渗透测试 Agent 平台

| 项 | 内容 |
|---|---|
| **Claim** | PentAGI（"Penetration testing Artificial General Intelligence"）是一个开源的**自主渗透测试 Agent 平台**：多 Agent 监督（researcher / developer / executor 等角色分工与自我修正）、沙箱化执行（Docker 隔离，agent 拿 Docker 而不交出宿主机）、模型供应商无关（Ollama / OpenAI / Anthropic / Gemini / Bedrock / DeepSeek / GLM / Kimi / Qwen / MiniMax 等）、Web UI + API、可选集成 Langfuse 追踪与可观测栈。支持多实例（tenant_id）部署。 |
| **Source** | 本机仓库 `/Users/kjonekong/projects/pentAGI`（README + 目录树 + docker-compose 文件族） |
| **Evidence** | README 首行自述定位；目录含 `backend` / `frontend` / `observability/` / `langfuse-clickhouse-init/` / `docker-compose-langfuse.yml` / `docker-compose-observability.yml`；LLM Provider 配置章节逐一列出上述供应商。 |
| **Confidence** | `CONFIRMED` |
| **Status** | `FIRST_HAND`（本机一手核验） |
| **Last Verified** | 2026-09-20 |

**对本项目的含义**：PentAGI 是一个**领域 Agent 应用**（安全测试领域），而非 Kernel 的竞争品。它在 V3 架构中应被定位为 **Kernel 可以调用的 Agent Runtime / Capability 之一**——即"某类任务交给 PentAGI 执行"。同时它也是"领域 Agent 应用长什么样"的一个真实参照物。

---

### C46 — Video Factory 使用 Trigger.dev 做编排（用户陈述）

| 项 | 内容 |
|---|---|
| **Claim** | 用户正在开发的 Video Factory 使用 Trigger.dev 做整体编排；它被提出作为 Kernel 架构的**真实验证场**（technical spike），而非 Kernel 的最终产品。 |
| **Source** | 用户指令文件 2026-09-20（`codex基于v2和新的讨论给cc的指令.md` §Part IX / §34） |
| **Evidence** | 用户原述；本机未找到对应仓库（`~/projects` 下无 video factory 目录）。 |
| **Confidence** | `UNKNOWN`（作为技术事实）；**用户意图层面为 CONFIRMED** |
| **Status** | `USER_STATED` |
| **Last Verified** | 2026-09-20 |

**对本项目的含义**：Video Factory 可作 V0 之后的 technical spike 候选，但**在本 PRD 中不作为既成事实使用**，也不作为 V0 范围。

---

### C47 — ECE v0 实现现状实测（本机一手）

| 项 | 内容 |
|---|---|
| **Claim** | 截至 2026-09-20，ECE v0（Track B 参考实现）的实测状态为：基线 pytest **349 passed / 5 skipped / 3 deselected**（与 CI 签名一致）；**E1 实体消歧 = 98.5%（64/65，达标 ≥95%）**；**E2 权限套件 = 5 Unauthorized Exposure + 5 Failure（16.4%，未达标，硬门 Unauthorized Context Exposure = 0 未满足）**；**E3 / E4 runner 裸崩**（`'ContextPackage' object has no attribute 'get'`）；**E5 = 0.0%**（`'str' object has no attribute 'isoformat'`）。 |
| **Source** | 本机亲跑，归档 `ece/reports/eval-archive/2026-09-20-cut040R2/baseline-seeded/`（E1.txt–E5.txt，raw stdout） |
| **Evidence** | 5 个 runner 的原始 stdout 已落盘；E2 输出逐行列出 5 暴露（e2-025/029/030/055/061）与 5 失败（e2-004/008/044/048/060）。 |
| **Confidence** | `CONFIRMED` |
| **Status** | `FIRST_HAND` |
| **Last Verified** | 2026-09-20 |

**对本项目的含义**：这是 V3 "Implementation Boundary" 一章的**唯一可引用实测基线**。任何"Kernel 已实现 X"的表述必须以本行为准。**Permission Before Intelligence 是铁律，而该铁律对应的硬门在实测中未通过**——V3 不得声称 Kernel 已达成该不变式，只能声称架构上已强制、实现上尚在收敛。

---

### C48 — ECE 测试套件会破坏 seed 注入的实体状态（RC-6）

| 项 | 内容 |
|---|---|
| **Claim** | `ece/tests/integration/test_s14_seed_idempotent.py` 在**每次 pytest 运行**中执行 `DELETE FROM entities WHERE source_system LIKE 'demo:%'` 后仅重放 `seed_from_demo_json()`；而部门属性注入 `_seed_entity_departments()` 只在 `run_seed()` 中调用、**不在** `seed_from_demo_json()` 中。因此每次跑全套测试都会**清除 `entities.attributes.department` 且不自愈**，导致 E2 评测的部门判定在被洗过的库上运行。 |
| **Source** | 代码阅读 `ece/tests/integration/test_s14_seed_idempotent.py:26-47` + `ece/src/ece/seed.py:124-164, 222-283`；实测复现（C47 基线与 Cline 受控实验数字吻合） |
| **Evidence** | 文件行号可核；Cline 2026-09-17 受控实验（手工恢复 department 后重跑 E2）得 5E/5F vs 洗库后 6E/14F，差异与洗库假设一致。 |
| **Confidence** | `CONFIRMED` |
| **Status** | `FIRST_HAND` |
| **Last Verified** | 2026-09-20 |

**对本项目的含义**：这是"**评测基线必须可复现**"这条纪律的一个真实反例。写入 V3 作为 Evidence 模型与 Evaluation 章节的教训：**被评测的状态本身必须受不变式保护**，否则评测数字不构成证据。

---

## 3. 必须随 V3 一并携带的既有脆弱性（不得在 V3 中被掩盖）

以下三项来自 `docs/research_v2/` 的自审与 Cline 审查，**不新增编号**，但 PRD V3 引用时必须保留其限定语：

| 项 | 事实 | 对 V3 的约束 |
|---|---|---|
| **C22 / C23 无来源 URL** | 两条均为 `STRONGLY_INFERRED`，"Domain 层是 Glean 空白" 与 "Glean 观测不含业务正确性" 的 source 列写明"推断"，**无 URL**。 | V3 **不得**把"Glean 不覆盖领域本体/推理/评估"写成事实；只能引用 `07-governance-evaluation.md:57` 已批准的反证式措辞。 |
| **C03 / C24 / C25 永久 UNKNOWN** | Enterprise Graph schema 可定制性、定价与最小合同、Agent Harness/Transform 细节，均 `STILL_UNKNOWN`；原定由 Robin 会谈裁决，但**会谈已取消**（`research_v2/README.md:21`）。 | V3 不得以这三项为设计前提；任何依赖须写成 ASSUMPTION + 验证方式。 |
| **18/25 条 v1 证据未复验** | `evidence-matrix-v2.md:82` 自述 BLOCKED_REVERIFY = 18。 | V3 引用 v1 证据时须保留"最后直接验证 2026-09-03"的时间戳限定。 |

---

## 4. 检索面限制的诚实声明

本轮 C43/C44 的抓取遇到与 V2 Phase 1 **完全同类**的工具限制：

- claude.ai WebFetch 对 `trigger.dev` 返回 "Unable to verify if domain is safe to fetch"（本机实测 2026-09-20）。
- 因此 C43/C44 结论来自 **WebSearch 检索面摘要**，而非逐字原文抓取。

按 V2 的 F1 教训（"不要把工具特定限制表述为网络层封锁"），本文件明确：**这是工具特定限制，不是网络封锁，也不是证据不存在**。若后续需要把 C43/C44 提升至逐字核验级，可用与 Cline 相同的备用通道补验。

---

## 5. 后续证据需求（V3 之后）

| 待补 | 用途 | 优先级 |
|---|---|---|
| Trigger.dev 自托管部署要求（内存 / 依赖 / 是否需要其 Cloud） | 决定"私有化部署优先"约束下 Trigger.dev 适配器是否可行 | **P0** |
| DSH 的 Kernel 可注入点（是否可自定义 context provider / tool provider） | 决定 DSH 适配器接口形态 | **P1** |
| PentAGI 的 API 表面（是否可被外部编排调用） | 决定它能否作为 Kernel 可调用的 Agent Runtime | **P1** |
| Glean Agent Harness 详情（C25/C41） | 若 Glean 路径复活 | **P2** |

---

## 6. 编号占用总表

```
C01–C25   v1 baseline（docs/research/evidence-matrix.md），最后直接验证 2026-09-03
C26–C42   v2（docs/research_v2/evidence-matrix-v2.md），C35–C42 由 Cline 2026-09-13 独立抓取
C43–C48   本文件（V3），2026-09-20
下一可用编号：C49
```

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
**Status**: Active
