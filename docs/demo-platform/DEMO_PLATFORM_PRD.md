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
- 硬约束: **两阶段部署**（cut-042R2 / cut-042R3 修订，supersedes 旧版"单 `docker compose up` 起全栈"）：API + DB 阶段 `docker compose up` 离线可演示；SPA 阶段由客户自有 nginx 反代 `/api/`，详见 [`DEPLOY_USER_PROXY.md`](./DEPLOY_USER_PROXY.md)。

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
Domain Packs: procurement ✅ · knowledge ✅(043R) · compliance ✅(044)
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
| **cut-043** | 知识管理 pack + 视图 A 多域切换 | scenarios/knowledge.yaml、KM 规则、seeder、UI 域切换 *(✅ 闭合 043R)* |
| **cut-043R2** | Codex R6 HOLD 返工：PRD 收敛 + 测试 anchor 锚定 + permission 反差保留 | PRD §5/§9 更新、tests/conftest.py 固化 anchor、smoke 4 项、报告口径核对 *(✅ R6-B1..B4 闭合；后续 R7/R8 cycle 在其基础上派生)* |
| **cut-043R3** | Codex R7 HOLD 返工：anchor 强制覆盖 + 非法 anchor 422 + PRD 结构/轨迹校正 | conftest 直接赋值、R7-B1/B2 binding test、PRD §8 列对齐、§11 轨迹校正 *(✅ R7-B1..B4 闭合 + R8-B1 进一步收紧)* |
| **cut-043R4** | Codex R8 HOLD 返工：strict YYYY-MM-DD anchor (canonical round-trip) + closure 报告口径收敛 | `api.py` canonical round-trip + 5 个 binding test (4 parametrize + 1 control); closure 用单一权威 diff stat + 测量时间点注 *(✅ R8-B1 + R8-B2 闭合)* |
| **cut-044** | 企业合规 pack + 视图 B 架构解释 + 视图 C live | scenarios/compliance.yaml、R-COMP-AUDIT 规则（evidence_count + system_coverage）、9 REQUIRES_SYSTEM 关系、视图 B 五区块（kernel 视角）、视图 C 三域徽章 + cut-045 时间线、视图 A 合规分支 *(✅ R0 PASS; 累计 512 passed; 详见 reports/cut-044-report.md)* |
| **cut-045** | 视图 C 蓝图 + 私有化一键包 + 整体验收 | 蓝图页（状态徽章）、私有化一键包（API+DB docker compose + SPA nginx 反代）、DoD 全验 |

## 9. DoD（整体验收，cut-045 后）

- 三域各 ≥1 个可运行场景，参数修改后实时重新生成并真实跑通。
- 三视图完整，蓝图徽章与实际代码状态一致（审验时抽查）。
- **两阶段部署**（cut-042R3 终版）：
  - **API + DB 阶段**：`docker compose up` 一键起 API + PostgreSQL，断网可演示。
  - **SPA 阶段**：SPA 由用户自有服务器托管（nginx 反代 `/api/` → `http://<api-host>:8765`），详见 [`DEPLOY_USER_PROXY.md`](./DEPLOY_USER_PROXY.md)。SPA 与 API 同源部署，规避 CORS preflight。
  - 推力 = 访谈-001 客户本地化部署约束（已 supersede 早期"单 `docker compose up` 起全栈"方案）。
- `make test` 全绿（cut-044 R0 实跑 `512 passed, 5 skipped, 3 deselected`，含 18 compliance tests = 8 boundary [4 truth-table + 4 422 zero-write] + 2 compliance discovery + 8 compliance unit），ruff / mypy 绿；cut-044 mutation runner 3/3 anchors RED→GREEN，same-origin smoke 4/4 PASS。
- `ECE_SERVER_TODAY_ANCHOR=2026-09-22` 在测试 conftest **强制覆盖**（cut-043R3 R7-B1：直接赋值，非 setdefault；外部 env 无法覆盖）；anchor 必须严格 `YYYY-MM-DD`（cut-043R4 R8-B1：canonical round-trip `parsed.isoformat() == raw_anchor`；basic `20260922` / week-date `2026-W38-2` / datetime / slash 形式均返回 422）。
- 业务语言检查表通过；权限反差演示三域齐备。
- quote_count 边界一致性：DB / Context / evidence / reason 四方一致（cut-042R3 R3-B1 黑盒覆盖 -1/0/1/2/3/4/999）。

## 10. 主要风险与对策

| 风险 | 对策 |
|---|---|
| 泛化破坏 spike 稳定性 | 421 既有测试原样锁死；`run_v0_loop` 薄封装不动 |
| UI 完成度不足 | 复用已验证的静态演示页设计语言（用户已认可） |
| 范围膨胀（连接器/SaaS 诱惑） | 每刀范围锁 + 非目标清单；Future 只记录不实现 |
| 三域规则变玩具 | 每域规则必须来自真实访谈/政策语义（采购=interview-001；KM/合规=研究线 App1/App3 假设） |
| 跨域部署与 CORS（cut-042 修订风险） | SPA 与 API 同源部署 + nginx 反代；CORS env var 留待 cut-045 引入 |
| quote_count 边界不一致 (cut-042R3 R3-B1) | loop step [3c-refresh] 无条件从 re-read 刷新 effective_params；API 422 拒绝负数；边界矩阵黑盒验证 |

---

## 11. 文档 supersession 轨迹（不是新增契约 — 仅为历史可追溯）

**纪律**: 本节只记录"何时、因何、由谁"对正文的修改；不引入新规则、新 DoD、新边界。
读者看正文第 1–10 节即可获取全部契约；本节是 git log 的文档镜像。

| 日期 | 刀 | 修订要点 |
|------|----|---------|
| 2026-09-22 | cut-042 | 首次签发本 PRD |
| 2026-09-22 | cut-042R | F1–F8 修正；同源 smoke 与两阶段部署作为范围调整记录 |
| 2026-09-22 | cut-042R2 | loop 重排 (R2-F1) + pack-owned materializer (R2-F2) + 同源脚本 + canonical symlinks；§11 修订附录（旧版） |
| 2026-09-22 | **cut-042R3** | (1) §3 硬约束改写为两阶段部署，supersede 旧"单 docker compose up 起全栈"（Codex R3-B2 阻断）(2) §8 cut-045 行的 "docker compose 单命令" 改为 "私有化一键包" (3) §9 DoD 第 3 条精简, 删掉"原 PRD §7"残留引用, 改为"已 supersede 早期方案" (4) §9 计数更新为 R3 实跑 `463 passed, 5 skipped, 3 deselected` (5) §9 加 quote_count 边界一致性条款 (6) §10 加 R3-B1 风险对策 (7) §11 自身从"修订附录"改为 supersession 轨迹（Codex R3-B2: 附录不能替代原文） |
| 2026-09-22 | **cut-043** | (1) §5 域行 `knowledge ⬜(043)` 仍为"在途"（cut-043 当刀未闭合，待 R5 复审）(2) §9 baseline 沿用 R3 实跑计数 |
| 2026-09-22 | **cut-043R** | Codex R5 HOLD 返工通过：(1) 修复 R5-B1..B5 五项（today server-owned、needs_valid_policy 零证据 allowlist、inverted resolver 零 pack import、root_source_id 422 拒收、报告口径收敛）(2) 新增 `reports/cut-043R/closure.md`；闭锁报告 §6 Gate 写"PRD §5/§9 更新待 cut-044"——本刀未做 PRD 改动（与代码变更同范围锁） |
| 2026-09-22 | **cut-043R2** | Codex R6 HOLD 返工：(1) §5 域行 `knowledge ⬜(043)` → `knowledge ✅(043R)` (2) §9 测试基线更新为 `487 passed, 5 skipped, 3 deselected` (cut-043R2 实跑 = cut-043R 486 + R6-B3 = +1 truth-table case；含 14 KM tests = 12 boundary + 2 discovery) (3) §8 cut-043 行追加状态注 (4) §11 收编 cut-043/043R/043R2 历史轨迹 |
| 2026-09-22 | **cut-043R3** | Codex R7 HOLD 返工：(1) §8 cut-043/cut-043R2 行修复 4 列问题，恢复 3 列表格结构（追加 cut-043R3 行）(2) §11 轨迹校正：cut-043R 误把 PRD 更新归到自己名下，实际是 cut-043R2 R6-B1 修的；本刀 §11 重新归因 (3) §9 测试基线更新为 `489 passed` (cut-043R3 实跑 = cut-043R2 487 + R7-B1 + R7-B2 = +2 binding tests；含 16 KM tests = 14 boundary + 2 discovery) (4) §9 KM 测试拆分校正为实际结构（cut-043R2 误写"22 KM boundary + 4 binding + 1 permission"） |
| 2026-09-22 | **cut-043R4** | Codex R8 HOLD 返工：(1) §9 测试基线更新为 `494 passed` (cut-043R4 实跑 = cut-043R3 489 + R8-B1 5 binding tests = +5; 含 31 KM tests = 19 boundary + 2 discovery + 10 unit — cut-043R3 closure 漏算 `tests/unit/test_knowledge_rule_and_decision.py` 的 10 个 unit test) (2) §9 anchor 校验条款升级为严格 `YYYY-MM-DD` (cut-043R4 R8-B1 canonical round-trip) (3) **注意**: cut-043R4 closure 曾声称"§8 新增 cut-043R4 行"——但实际该动作发生在 cut-043R6 R10-B1; cut-043R4 closure 这一笔归因错, 已由 cut-043R7 收口 |
| 2026-09-22 | **cut-043R5** | Codex R9 HOLD 返工（docs-only）：(1) §9 baseline 489 → 494 (Codex R9 校正 cut-043R3 漏算 unit test, 实际 KM = 19 boundary + 2 discovery + 10 unit = 31); §8 cut-043R3 行追加"✅ R7-B1..B4 闭合 + R8-B1 进一步收紧"状态注 (2) cut-043R4 closure Header/§2.1/§2.2 文件口径统一为 1+5=6; §3 verification 草稿注释清理 (3) R9 累计 tracked diff 与 cut-043R4 终态一致 (`+861/-221`), 零业务代码改动 |
| 2026-09-22 | **cut-043R6** | Codex R10 HOLD 返工（docs-only）：(1) **§8 新增 cut-043R4 行**（cut-043R4 closure 声称做了但实际没做；R6 实际执行 R10-B1） (2) **§8 cut-043R2 状态注** 从"⏳ R6 复审中"更新为"✅ R6-B1..B4 闭合；后续 R7/R8 cycle 在其基础上派生" (3) **§11 新增 cut-043R5 trail 行**（cut-043R5 closure 声称做了但实际没做；R6 实际执行 R10-B3） (4) R10 累计 tracked diff 与 cut-043R5 终态一致 (`+861/-221`), 零业务代码改动 |
| 2026-09-22 | **cut-043R7** | Codex R11 HOLD 返工（docs-only）：(1) **§11 新增 cut-043R6 trail row**（cut-043R6 closure 声称做了但实际没做；R7 实际执行 R11-B1） (2) **§11 cut-043R4 归因校正注**："已由 cut-043R6 收口"→"已由 cut-043R7 收口"（R6 只改了 §8，§11 归因校正本身由 R7 执行） (3) **cut-043R6 closure §1 R10-B2 false claim 移除**：删除"同步更新 cut-043R5 closure §5.1" bullet，替换为"(注: 已存在, 本刀无需改动)" (4) R11 累计 tracked diff 与 cut-043R6 终态一致 (`+861/-221`), 零业务代码改动 |
| 2026-09-22 | **cut-043R8** | Codex R12 HOLD 返工（docs-only）：(1) **§11 新增 cut-043R7 trail row**（R7 曾漏留痕；R8 实际执行 R12-B1） (2) **§11 cut-043R4 归因注** 从"已由 cut-043R6 收口"修正为"已由 cut-043R7 收口"（R12-B2） (3) 修正 R7 closure "校truth" 和 R6 closure 两处 "Coex"（R12-B3） (4) R12 累计 ece tracked diff 保持 `+861/-221`，零业务代码改动 |
| 2026-09-22 | **cut-044** | Codex R0 PASS: 第三域 compliance pack (R-COMP-AUDIT + `evidence_package_sufficient` / `gap_list` English constants + gap_list zero-evidence allowlist per R5-B2 + inverted registration per R5-B3 + route_root_via_params per R5-B4) + 视图 B kernel 架构内容页 (5 区块: 整体架构 / 六层职责 / 权限模型 / 确定性决策 / 域包隔离) + 视图 C live (三域徽章 + cut-042..cut-045 时间线) + 视图 A compliance payload 分支. 累计 512 passed (= 494 baseline + 18 compliance tests = 8 boundary + 2 discovery + 8 unit); 3/3 mutation anchors RED→GREEN; 4/4 same-origin smoke PASS. **PRD §9 DoD 三视图 + 三域 主体闭合**, 仅余 cut-045 收口 (蓝图诚实状态徽章 + 私有化部署包 + 整体验收). 详见 reports/cut-044-report.md. |

**变更验证**:
```bash
grep -nE "单 `?docker compose up`? 起全栈|docker compose 单命令|原 PRD §7" \
  docs/demo-platform/DEMO_PLATFORM_PRD.md
# 期望: 0 hits
```

---

**Author**: Codex
**Date**: 2026-09-22
**Status**: 已签发 · cut-042 同步生效
