# Track B Execution Loop Plan — 逐刀执行 / 审验 / 签发

> **Date**: 2026-09-13
> **模式**: CC 执行一刀 → 用户带回 Cline 审验 → Cline 签发下一刀。**未经审验签发，不进下一刀。**
> **范围**: 仅覆盖 `docs/track_b/` 三文件建议 + `cline-review-trackb-spec.md` R1–R4 + Sprint 0。**Sprint 1 之后不预规划**（Sprint 0 验收后另拟）。
> **本文件取代**上一轮"指令 A + 指令 B"的一次性发放方式。

---

## 刀次规划（共 4 刀）

| 刀 | Session / 仓 | 任务 | 依据 | Cline 审验点 |
|---|---|---|---|---|
| **1** | Track A session（本仓） | track_b spec 修复 R1–R4 | 审阅报告 §4 | diff 仅限预期改动；5 处 ADR 引用与根 ADR 实际标题一致；命令修正；Robin 注记；commit/push |
| **2** | ECE session（`ece/` 仓） | TASKS.md 修订：S4.5 写入 + S4.2 措辞修正 + mcp 依赖注记 | README §6.2 建议 2 + 审阅报告 F3/F5 | S4.5 设计与 execution-plan §4 一致（含修正后命令）；S4.2 改"权限 SQL 下推"；编号体系不乱；ece 仓 commit |
| **3** | ECE session | Sprint 0 前半 S0.1–S0.3（uv+pyproject+Makefile / docker-compose+healthz / CI 四件套） | TASKS Sprint 0 | `make setup && make test` 绿；`docker compose up` 后 `/healthz` 200；CI 本地触发红则阻断；import-linter 配置就位 |
| **4** | ECE session | Sprint 0 后半 S0.4–S0.6（check_api_docs / alembic 初始迁移 / 合成数据生成器骨架） | TASKS Sprint 0 | 故意加路由不改文档 → CI 红（实测）；`alembic upgrade head` schema 与 DATA_MODEL §1–§5 一致；gen_dataset 统计打印正常 |

**Sprint 0（刀 3+4）验收后**：Cline 另拟刀 5+（届时按 README §6.2 建议 1 决定先 Sprint 1 还是 Sprint 2）。

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
| 1 | 🔵 已签发（见本次交付文本） |
| 2 | ⏳ 待刀 1 审验通过后签发 |
| 3 | ⏳ 待刀 2 审验通过后签发 |
| 4 | ⏳ 待刀 3 审验通过后签发 |
