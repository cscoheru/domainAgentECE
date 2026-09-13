# Build / Buy / Integrate / Partner 四向决策矩阵

> **Phase**: 4 — Build/Buy/Integrate/Partner
> **Last Updated**: 2026-09-13
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §9 Phase 4 DoD
> **上游**: [`/docs/research_v2/capability-matrix-v2.md`](../research_v2/capability-matrix-v2.md) + [`glean-architecture-reconstruction.md`](glean-architecture-reconstruction.md) + [`/docs/research_v2/evidence-matrix-v2.md`](../research_v2/evidence-matrix-v2.md)
> **下游输出**: 本文件 + `/docs/adr/ADR-003~010` 共 8 个 Build 决策 ADR

---

## 0. Phase 4 DoD(per PRD §9)

1. 逐能力四向决策 + 理由,产出本文件 ✅
2. 每个 Build 决策写 ADR(`/docs/adr/ADR-003~010`)✅
3. **无 "undecided" 项遗留**;影响 Track B(ECE)的决策全部成文为 ADR ✅(Row 13 已裁决,见 §3)

---

## 1. 决策总览

**四向定义**:
- **Build (自建)**:我方团队实现(高 IP + Glean 未覆盖纵深)
- **Buy (采购)**:完全外包,自己不写
- **Integrate (集成)**:通过 API/SDK/MCP 借用 Glean 能力
- **Partner (借 Partner 通道)**:通过 Glean Partner Program 联合客户做

**16 能力决策分布**:

| 决策 | 数量 | 含义 |
|---|---|---|
| **Build** | 8 | Domain Ontology / Domain Reasoning / Domain Evaluation / Context Assembly / Entity Resolution / Permission Engine / Query Planner / Postgres |
| **Build + Integrate** | 3 | MCP Tool Layer / Connectors / Enterprise Graph |
| **Integrate** | 3 | Actions(关闭)/ Glean Enterprise Context / Glean Agent Builder / Governance |
| **Buy / 不做** | 2 | Enterprise Search / Agent Builder UI |
| **Later / Phase 5+** | 1 | Agent Identity (C36 beta) |
| **裁决(原本 undecided)** | 1 | Row 13 Platform Observability → Build 简化版 + Integrate Glean 完整版 |

---

## 2. 逐能力四向决策详表

| # | 能力 | 决策 | ADR | 证据 | ECE 铁律符合 | 备注 |
|---|---|---|---|---|---|---|
| 1 | Connector Ecosystem | **Integrate (Glean API/MCP) + 自建框架** | — | C05, C09 | ADR-010 领域包隔离 | v0 自建 3 mock;Phase 4+ 借 Glean API/MCP |
| 2 | Enterprise Search | **Buy / 不做** | — | C04 | ADR-008 LLM 不可知 | 横向基础设施,违反铁律;借 Glean |
| 3 | Enterprise Graph | **Build (简化版) + Integrate** | ADR-005 | C02, C03, C18 | ADR-009 技术栈瘦身 | Phase 5 视 [C03] 决定是否接 GleanAdapter |
| 4 | Entity Resolution | **Build** | ADR-007 | C18 + C23 | ADR-010 | 跨系统实体归一,Glean 模糊地带 |
| 5 | Permission Engine | **Build + Integrate (语义)** | ADR-003 | C06, C07, C16, C19, C36 | ADR-004 Permission Before Intelligence | ECE P2 铁律;E2 = 0 CI 门槛 |
| 6 | Context Assembly | **Build** | ADR-006 | C02 + C18 | ADR-001 ECE 定位 | 12 步流水线,ECE 核心 |
| 7 | Agent Runtime | **Partner/Integrate + 自建 Domain Agent** | (继承 8/9/10) | C10, C37 | ADR-006 | Glean Agent Builder beta;我方做 Domain Agent |
| 8 | Agent Builder UI | **Partner / 不做** | — | C37 | — | 我方资源放 Domain Agent 而非 Builder UI |
| 9 | MCP Tool Layer | **Build + Integrate** | ADR-004 | C19, C37, C39 | ADR-008 | MCP 事实标准;与 Claude Code/Cursor 互操作 |
| 10 | Actions 写回 | **Integrate + v0 关闭** | — | C08 | ADR-004 | env kill-switch + 路由硬编码;Phase 5+ 开放 |
| 11 | Agent Identity | **later / Phase 5+** | — | C36 beta | — | Robin Q12 必问 |
| 12 | Governance | **Integrate (Glean Protect/Intelligence)** | — | C01 | — | v0 单租户不需要;Phase 4+ 集成 |
| 13 | Evaluation (Platform Observability) | **Build (简化版) + Integrate (Glean 完整版)** | — | C14, C22, C38 | ADR-009 | **Phase 4 裁决**(见 §3) |
| 14 | Evaluation (Domain/Business Correctness) | **Build** | ADR-008 | C22 + C38 | — | 业务正确性评估,Glean 空白 |
| 15 | Domain Ontology | **Build** | ADR-009 | C23 | — | G23 空白,核心 IP |
| 16 | Domain Reasoning | **Build** | ADR-010 | C23, ADR-006 | ADR-006 | 规则优先 + LLM 轻量 |

---

## 3. Row 13 Platform Observability 裁决(Phase 4)

### 3.1 背景

Phase 2 Capability Matrix v2 Row 13 标"不确定(简化版 or 集成?)"。Phase 4 必须裁决。

### 3.2 证据

- **[C14]** (CONFIRMED): Glean Agent Observability — adoption、error rates、up/down votes、ROI
- **[C22]** (STRONGLY_INFERRED, **C38 收紧**): Glean 平台观测**不含业务正确性/领域推理质量评估**;execution-path ≠ domain correctness
- ECE EVALUATION.md §5 H3: "Context 显著优于纯 RAG" — 需要 ECE 自建对照组

### 3.3 裁决

**Build (简化版) + Integrate (Glean 完整版)**:

| 阶段 | 决策 | 理由 |
|---|---|---|
| **ECE v0** | Build 简化版(`context_requests` + `context_items` 表,DATA_MODEL §5) | v0 自监控必需;离线运行;EVALUATION §1 E1-E6 已设计 |
| **Phase 4+ POC** | Integrate Glean 完整版(`adoption/error/votes/ROI` 指标) | 客户已有 Glean 时,补全平台级指标 |
| **永不** | Build Glean 同款业务正确性评估 | [C22] 推断为我方 IP 价值,放弃模仿 Glean |

### 3.4 后果

- ✅ v0 自监控完整(审计 trace + debugger)
- ✅ Phase 4+ 可选接 Glean 完整指标
- ✅ Domain Evaluation 保持我方最高 IP 价值([C22] + [C38])
- ⚠️ ECE v0 评估指标与 Glean 完整指标口径不一致,需在 Phase 5 写明映射

---

## 4. ECE 铁律符合性(逐 ADR 校验)

| ECE 铁律(根 CLAUDE.md) | 关联 ADR | 符合性 |
|---|---|---|
| **Permission Before Intelligence** (P2) | ADR-003 | ✓ Permission Engine 强制 SQL 子查询过滤 |
| **禁止 Demo 绕过核心抽象** (铁律 2) | (整体) | ✓ 所有 Build 决策保持 4 件套抽象 |
| **垂直纪律** (铁律 3) | (整体) | ✓ 不引入横向基础设施;Postgres-only |
| **领域包隔离** (ECE ADR-010,独立编号) | ADR-005, ADR-007, ADR-009, ADR-010 | ✓ engine/core 零领域 import |
| **LLM 不可知** (ECE ADR-006,独立编号) | ADR-004, ADR-009 | ✓ OpenAI 兼容端点;不锁厂商 |

---

## 5. Track B 影响声明

**Phase 4 决策对 ECE v0(Sprint 0-6,独立仓 github.com/cscoheru/ece)的影响**:

| 决策 | 影响 ECE 哪部分 |
|---|---|
| ADR-003 Permission Engine | `src/ece/permissions/`(已存在,Phase 4 验证与 v2 一致性) |
| ADR-004 MCP Tool Layer | `src/ece/search/` + 新增 `src/ece/mcp/`(Sprint 4) |
| ADR-005 Enterprise Graph | `src/ece/entities/` + `src/ece/relationships/`(Sprint 2,Phase 5 接 Glean Adapter) |
| ADR-006 Context Assembly | `src/ece/context/`(Sprint 3) |
| ADR-007 Entity Resolution | `src/ece/entities/resolution.py`(Sprint 2) |
| ADR-008 Domain Evaluation | `tests/evaluation/`(Sprint 2+ 持续) |
| ADR-009 Domain Ontology | `src/domain_packs/procurement/context_specs/`(Sprint 5) |
| ADR-010 Domain Reasoning | `src/domain_packs/procurement/agent/` + `src/ece/reasoning/`(Sprint 5) |

**注**:ECE 仓库为独立仓,Phase 4 ADR 仅为 Track A 战略决策,Track B 由 ece/CLAUDE.md + ece/TASKS.md 独立推进(per ROOT CLAUDE.md §16 双轨架构)。

---

## 6. Phase 5 输入

Phase 5 (Platform Kernel Definition) 将:

1. 基于本 BBIP 矩阵 + 8 个 Build ADR,产出 `/docs/architecture_v2/platform-kernel-definition.md`
2. 与 ece/docs/ARCHITECTURE.md 做映射(已覆盖 / 缺口 / 冗余)
3. 缺口处置建议(补建 / 换向 / 砍掉)
4. 完成后停下汇报 → Phase 6(Reference Applications)

---

## 7. 治理说明

- ✅ Phase 4 DoD 全部满足:**无 undecided 项遗留**(Row 13 已裁决)
- ✅ 8 个 Build 决策全部成文为 ADR(`/docs/adr/ADR-003~010`)
- ✅ 每个 ADR 含理由 + 关联 C 编号 + ECE 铁律符合性 + 备选否决
- ✅ v1 文档(`/docs/research/`)不修改不删除
- ✅ ece/ 子目录未触碰(Track B 独立推进)
- ✅ 与 `ece/docs/adr/` 编号独立(无混淆)

---

## 8. 下一步

Phase 5 (Platform Kernel Definition) 启动(待用户确认):

1. 产出 `/docs/architecture_v2/platform-kernel-definition.md`
2. 与 `ece/docs/ARCHITECTURE.md` 做映射
3. 缺口处置建议(补建 / 换向 / 砍掉)
4. 完成后停下汇报,等确认 → Phase 6 (Reference Applications)
