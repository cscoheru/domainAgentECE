# DEMO_PLATFORM_PRD — ECE 多域实时演示平台

> Date: 2026-09-22
> 状态: **已签发（user 直接指令，需求立即生效）**
> 上游: V0 Spike S1–S6 闭合（410 tests，`docs/v0/`）· interview-001（仅本地部署 / 多域兴趣 / 可解释性需求）· track_b Kernel 定义（K1–K8）
> 性质: Track B 下一阶段工程规格。V3 架构与 Kernel 边界冻结不变，本 PRD 不新增 Kernel 对象，只做**实现与泛化**。

---

## 0. 一句话

把 V0 spike 的六步闭环从"采购单单一静态页"升级为**多行业、参数实时生成、三视图（应用演示 / 架构解释 / 扩展蓝图）的完整 Web 演示平台**——同一 Kernel，三个域，全部真实运行。

## 1. 背景与现状

| 资产 | 状态 |
|---|---|
| 六步闭环（assemble → rule → decision → evidence → update → re-read） | ✅ S1–S6 闭合，410 tests |
| 静态演示页 `ece/demos/procurement-review-demo.html` | ✅ 业务语言已验证（用户确认"直观多了"），保留为 fallback |
| 底座泛化 | ❌ evidence 硬编码 `purchase_request` subject；loop 硬编码 intent / RULE_ID / SPIKE_SOURCE_SYSTEM |
| 域包 | ❌ 仅 procurement 一个 |
| API 层 | ✅ FastAPI 已存在（`/context` 等），可扩展 `/demo/*` |
| 客户验证结论 | 仅本地部署可谈；对知识管理、企业合规有跨域兴趣；技术解释力是信任前提 |

## 2. 目标 / 非目标

**目标**
1. **视图 A · 应用演示**：选行业 → 调参数 → 实时生成场景 → 真实跑六步闭环 → 业务语言呈现（结论 / 依据凭证 / 状态变更 / 权限切换）。
2. **视图 B · 架构解释**：我们做了什么、为什么可以做到——六步闭环图、Kernel 各层职责、权限模型、确定性决策、证据链，全部业务语言。
3. **视图 C · 扩展蓝图**：企业 AI Agents 演进路线（Domain Pack → 多 Agent 编排 → 企业级治理），每个节点诚实标注 ✅已实现 / 🔨在途 / ⬜规划。
4. **三域**：采购（已有）、知识管理、企业合规，共用同一 Kernel，证明"换域不换底座"。
5. **底座完成度**：spike 硬编码泛化为 pack 驱动；规则注册表；场景引擎（spec YAML + 合成数据 + 参数化）。

**非目标（范围锁）**
- 不做 SaaS / 多租户 / 计费 / 真实企业连接器（OA、ERP 均不做）。
- 不引入 LLM 决策；LLM 仅允许辅助生成类能力且页面明确标注（D12/D13 边界）。
- 不做录屏、客户预约、访谈安排（user 自行负责）。
- 不做微服务 / K8s / 消息队列。

## 3. 用户与使用场景

- **主用户**: 创始人在客户现场或录屏时驱动演示。
- **次用户**: 客户技术人员在私有化环境里自助浏览（数据不出域）。
- 硬约束: **离线可运行**——前端零 CDN 零 build，单 `docker compose up` 起全栈。

## 4. 产品形态（信息架构）

单页应用，顶部三视图切换：

```
┌──────────────────────────────────────────────┐
│ ECE 智能底座演示   [应用演示] [架构解释] [扩展蓝图] │
├──────────────────────────────────────────────┤
│ 视图A: 行业卡片(采购/知识管理/企业合规)            │
│   → 场景参数(如金额/报价家数; 期间/控制项; 问题)    │
│   → [运行演示] → 六步业务呈现(同演示页语言体系)      │
│   → 权限切换 + 依据逐跳追溯                       │
│ 视图B: 六步闭环图 · K1-K8 每层"做了什么/为什么"     │
│   · 权限模型 · 确定性决策说明 · 证据链示例          │
│ 视图C: 演进蓝图时间线 + 诚实状态徽章                │
└──────────────────────────────────────────────┘
```

## 5. 技术架构

```
浏览器 (vanilla JS SPA, 零依赖, 中文业务语言)
   │ HTTP
FastAPI  /demo/*  ←── 新增应用层 src/ece/demo/
   │ 调用（不复制实现）
六步闭环 ← 泛化: intent / rule / subject / decision_key 全部由 pack 声明
   │
Domain Packs: procurement ✅ · knowledge ⬜(043) · compliance ⬜(044)
   │
PostgreSQL（合成 fixture，每域可独立重置）
```

**底座泛化（cut-042 核心）**
- `evidence.store`: subject 实体类型从 scenario/pack spec 读，删除 `_SUBJECT_ENTITY_TYPE` 硬编码。
- `v0.loop`: 泛化为 `run_demo_loop(engine, user_ref, root_source_id, scenario_spec)`；RULE_ID / intent / source_system 由 spec 注入；`run_v0_loop` 保留为 procurement 薄封装（既有测试锁死行为不变）。
- 规则注册表: pack 内声明规则（纯函数，签名同 S3），spec 引用规则名。
- 场景引擎: `scenarios/<domain>.yaml`（root entity / 规则 / 参数定义 / fixture seeder 引用）+ 参数化 seeder（金额、报价数、期间、文档数…）。

## 6. 三域场景定义（v1 演示深度）

| 域 | 场景 | 输入参数 | 确定性规则（示例） | 结论形态 |
|---|---|---|---|---|
| 采购 | 采购合规审查（现有） | 金额、报价家数 | ≥100万 且 <3家 → 需人工复核 | review_required + 2 凭证 |
| 知识管理 | 制度知识审查 | 员工提问、制度版本 | 政策版本在有效期内 ∧ 员工有权限 → 有据回答；过期/无权限 → 提示提供有效版本 | 回答 + 出处链（证据同构） |
| 企业合规 | 审计证据归集（EvidenceIQ-lite） | 控制项、审计期间 | 期间内证据数 ≥ N ∧ 覆盖全部系统 → 充分；否则缺口清单 | 证据包清单 + 缺口列表 |

每域包含：1 个 WorkflowSpec、1–2 条确定性规则、合成 fixture（含权限反差用户）、独立重置。

## 7. 纪律（不可违反）

1. **无 LLM 决策**；确定性规则与 S3 同标准（N=10 逐字段一致）。
2. **Permission Before Intelligence**：权限检查在数据读取路径（S6 口径），每域必须有 denied 用户演示。
3. **所有数字真实运行生成**；页面标注运行时间戳；蓝图必须区分已实现/在途/规划。
4. 既有 410 测试零退化；每刀**测试先行**（红→绿可见）+ ≥3 变异证据；每刀 STOP 回审，通过才进下一刀。
5. 业务语言零技术词（沿用演示页检查口径：不得出现 ctx / evidence / decision_id / SQL 等）。

## 8. 实施路径（签发顺序）

| 刀 | 内容 | 关键产物 |
|---|---|---|
| **cut-042** | 底座泛化 + `/demo/*` API + UI 骨架（采购域 live 跑通） | 泛化 pipeline、demo 应用层、SPA 骨架、API 契约测试 |
| **cut-043** | 知识管理 pack + 视图 A 多域切换 | scenarios/knowledge.yaml、KM 规则、seeder、UI 域切换 |
| **cut-044** | 企业合规 pack + 视图 B 架构解释 | scenarios/compliance.yaml、证据归集规则、架构解释内容页 |
| **cut-045** | 视图 C 蓝图 + 私有化一键包 + 整体验收 | 蓝图页（状态徽章）、docker compose 单命令、DoD 全验 |

## 9. DoD（整体验收，cut-045 后）

- 三域各 ≥1 个可运行场景，参数修改后实时重新生成并真实跑通。
- 三视图完整，蓝图徽章与实际代码状态一致（审验时抽查）。
- **两阶段部署**（cut-042 修订）：
  - **API + DB 阶段**：`docker compose up` 一键起 API + PostgreSQL，断网可演示。
  - **SPA 阶段**：SPA 由用户自有服务器托管（nginx 反代 `/api/` → `http://<api-host>:8765`），详见 [`DEPLOY_USER_PROXY.md`](./DEPLOY_USER_PROXY.md)。SPA 与 API 同源部署，规避 CORS preflight。
  - 原 PRD §7 单 `docker compose up` 全栈方案已被访谈-001 客户本地化部署约束推翻（记录于 `DEPLOY_USER_PROXY.md`）。
- `make test` 全绿（≥421 基线 + 新增），ruff / mypy / lint-imports 绿。
- 业务语言检查表通过；权限反差演示三域齐备。

## 10. 主要风险与对策

| 风险 | 对策 |
|---|---|
| 泛化破坏 spike 稳定性 | 421 既有测试原样锁死；`run_v0_loop` 薄封装不动 |
| UI 完成度不足 | 复用已验证的静态演示页设计语言（用户已认可） |
| 范围膨胀（连接器/SaaS 诱惑） | 每刀范围锁 + 非目标清单；Future 只记录不实现 |
| 三域规则变玩具 | 每域规则必须来自真实访谈/政策语义（采购=interview-001；KM/合规=研究线 App1/App3 假设） |
| 跨域部署与 CORS（cut-042 修订风险） | SPA 与 API 同源部署 + nginx 反代；CORS env var 留待 cut-045 引入 |

---

**Author**: Codex
**Date**: 2026-09-22
**Status**: 已签发 · cut-042 同步生效
