# Track B Execution Loop Plan — 逐刀执行 / 审验 / 签发

> **Date**: 2026-09-13
> **模式**: CC 执行一刀 → 用户带回 Cline 审验 → Cline 签发下一刀。**未经审验签发，不进下一刀。**
> **范围**: 仅覆盖 `docs/track_b/` 三文件建议 + `cline-review-trackb-spec.md` R1–R4 + Sprint 0。**Sprint 1 之后不预规划**（Sprint 0 验收后另拟）。
> **本文件取代**上一轮"指令 A + 指令 B"的一次性发放方式。

---

## 0. 来源对齐（Obsidian 笔记 → 仓库现状，2026-09-13 补录）

上游战略笔记：`/Users/kjonekong/Documents/Obsidian Vault/blueprintECE/下一步：CC 完成 Glean Architecture Research v2 后.md`（四阶段路线：Research Audit → Architecture Decision → Kernel MVP → Reference App）。

| 笔记主张 | 仓库现状 | 结论 |
|---|---|---|
| ① V2 Research Audit | Cline 三次红队审阅 + STOP Gate `49604b0` | ✅ 已完成 |
| ② Architecture Decision | Phase 3/4/5（BBIP 矩阵 + 根 ADR-001~010 + K1–K8） | ✅ 已完成 |
| §六 7 份交付物（ARCHITECTURE_DECISION_V1 等） | 同等内容已存在（capability-matrix-v2 / build-buy-integrate-partner-matrix / platform-kernel-definition / ece PRD / reference-applications / 根 ADR） | ✅ 不按笔记文件名重做，避免重复 |
| 10 条要求（Provider-neutral / Mock 跑通 / 不做大 UI…） | 已落入 ADR-001/006、X1–X6、S6.1 | ✅ 已满足 |
| ③ Kernel MVP **on G9R9** | 未开始 = 本计划刀 2–4 | 🔵 本计划执行中 |
| Robin 线并行 | 用户 2026-09-13 取消（期权保留） | ⚪ 已被用户决定取代 |
| **G9R9 开发环境（Windows 11 + WSL2）** | 用户已决策：Mac 先行，G9R9 于 S6.5 做 Windows 兼容验证 | ✅ 已决策 |

**刀 3 开发机决策（用户已定，2026-09-13）**：**Mac 先行开发**（本机，`/Users/kjonekong/projects/domainAgentECE/ece`）；G9R9（Windows 11 + WSL2）推迟到 **S6.5 私有化验收阶段做 Windows 兼容验证**——届时在 Sprint 6 规划中作为验收项之一，不提前做。刀 1、刀 2 为纯文档，不受影响。

---


## 刀次规划（共 4 刀）

| 刀 | Session / 仓 | 任务 | 依据 | Cline 审验点 |
|---|---|---|---|---|
| **1** | Track A session（本仓） | track_b spec 修复 R1–R4 | 审阅报告 §4 | diff 仅限预期改动；5 处 ADR 引用与根 ADR 实际标题一致；命令修正；Robin 注记；commit/push |
| **2** | ECE session（`ece/` 仓） | TASKS.md 修订：S4.5 写入 + S4.2 措辞修正 + mcp 依赖注记 | README §6.2 建议 2 + 审阅报告 F3/F5 | S4.5 设计与 execution-plan §4 一致（含修正后命令）；S4.2 改"权限 SQL 下推"；编号体系不乱；ece 仓 commit |
| **3** | ECE session | Sprint 0 前半 S0.1–S0.3（uv+pyproject+Makefile / docker-compose+healthz / CI 四件套） | TASKS Sprint 0 | `make setup && make test` 绿；`docker compose up` 后 `/healthz` 200；CI 本地触发红则阻断；import-linter 配置就位 |
| **4** | ECE session | Sprint 0 后半 S0.4–S0.6（check_api_docs / alembic 初始迁移 / 合成数据生成器骨架） | TASKS Sprint 0 | 故意加路由不改文档 → CI 红（实测）；`alembic upgrade head` schema 与 DATA_MODEL §1–§5 一致；gen_dataset 统计打印正常 |

**Sprint 0（刀 3+4）已验收关闭（2026-09-14）**：刀 5 起按 TASKS 顺序进 Sprint 1（数据面先行——S2 身份/权限/消歧依赖实体数据在库，"README §6.2 建议 1"出处已佚，以结构性依赖为准裁定）。

---

## 循环规则

1. 每刀指令由 Cline 签发（含：任务、依据、自检命令、禁止事项）；CC 执行完 commit + 汇报。
2. CC 汇报后用户回 Cline session 触发审验；审验通过 → 签发下一刀；不通过 → 修复重验。
3. 范围外的想法（新功能、新依赖、改架构）一律记 TODO 汇报，不擅自做。
4. 铁律始终生效：不动 `ece/` 之外仓的工程文件（Track A session）/ Permission Before Intelligence / 垂直纪律 / 领域包隔离 / LLM 不可知。

---

## 刀次状态

| 刀 | 状态 |
|---|---|
| 1 | ✅ 已执行（`c2625db`）+ 已审验通过（cut-001-report.md §7，Cline 2026-09-13） |
| 2 | ✅ 已执行（ece `5534dc9`）+ 已审验通过（ece/reports/cut-002-report.md §7，Cline 2026-09-13；报告 4 处修正转刀 3 步骤 0） |
| 3 | ⚠️ 部分通过（ece `f88ccd6`/`3eb1516`/`74e73a5`：S0.1 ✅ S0.3 ✅ / **S0.2 ❌ 返工**——uvicorn 缺依赖 + healthcheck 用了镜像里不存在的 curl + 8000 端口冲突；详见 cut-003-report.md §7） |
| 3R | ❌ 不通过（ece `9c6efa4`：R2/R3 只在未提交的魔改文件上验过、跑完还原——被验收状态≠被提交状态；R4 验收无效；hash 占位符×7；R1/R5 ✅。Cline 补刀 ece `ffd1f07` 落地 compose 修复并亲跑全栈验收通过 → S0.2 提交物 ✅。详见 cut-003r-report.md §7） |
| 3R2 | ✅ 已执行（ece `5e440df`）+ 已审验通过（cut-003r2-report.md §7，Cline 2026-09-14；Cline 在 HEAD 亲跑全栈验收同绿；治理修正 2 处：§7 被 sed 误改恢复 + 流程惯例 v2 固化〔报告自身 hash 不自引〕。**S0.1–S0.3 全 ✅，Sprint 0 前半收官**） |
| 4 | ❌ 不通过 → 返工（ece `d120a27`/`a56ea90`/`c93fc20`/`5fd441c`：三件功能全实证可用，但 **push 红 CI ×2 未披露**〔ruff 12 错〕+ S0.4 CI 步骤未加 + 迁移§注释错 + PRD §27 偏差未声明；详见 cut-004-report.md §7） |
| 4R | ✅ 已执行（ece `fac53d2`+`4fe270f`）+ 已审验通过（cut-004r-report.md §7，Cline 2026-09-14；CI 实际回绿〔fac53d2 success〕+ ruff 12→0 + md5 零回归；R4 修反/R6 未做 → Cline 补刀 `5aa5ddd`。**Sprint 0 全部关闭**） |
| 5 | ❌ 不通过 → 返工（ece `2a4c02d`/`e06b40c`/`3a51e2b`/`4ba282d` + 报告 `d2796ee`：骨架合规〔API 形状/分页/404 包络/temporal + check_api_docs 双 bug 修复〕，但 **4 处运行时断裂全部"从未对真库跑过"**——ontology.yaml 装 Python 导致 import 即炸、`:x::jsonb` SQL 绑定 bug ×2、seed 不适配 demo.json 真实形态；`e06b40c` commit message 伪造"ontology gate 验收"声明〔**第 3 次完整性事故**〕；TASKS 四验收零测试对应物。Cline 补刀 `9b40870`（rename + CAST×2 + SIM110）后亲跑实证矩阵全绿。详见 cut-005-report.md §7） |
| 5R | 🔵 已签发（R1 seed 记录形态适配+双跑 created=0 / R2 run_ingestion created 语义虚标二选一 / R3 relationships 唯一索引迁移+拒绝落库记录 / R4 四验收测试补齐 / R5 完整性整改〔commit message"验收:"必须附可复跑命令〕/ R6 connector 标签保留资源段） |
