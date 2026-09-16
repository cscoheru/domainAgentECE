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
| 5R | ✅ 已执行（ece `0ecc362`/`6557bb2`/`7d90ccb` + 报告 `ae890e2`）+ 已审验通过（cut-005r-report.md §7，Cline 2026-09-14；R1–R6 全部亲跑实证：seed 420→0、真 upsert stats、同三元组去重 1 行、make test 15 passed 1 skipped、md5 零漂移、**R5 整改到位**〔3 commit message 全附可复跑命令+输出〕。CI 结构性红 ×2〔integration 打真库无 service〕→ Cline 补刀 `2c1c026`〔pgvector service+md5 锁+alembic 前置〕后 CI 绿 16 passed。2 小缺口转刀 6：ontology 拒绝落库、s13 契约补强。**Sprint 1 关闭**） |
| 6 | ❌ 不通过 → 返工（ece `f560924`/`c97b24a` + 报告 `adb51d8`：引擎层真实可用〔identity/permission 判定/resolver 3-stage + /resolve 活体验证、gap (a) ontology 拒绝落库、CI 3 连绿、28 passed〕，但 **Sprint 2 四个 S 的验收核心三个未做或虚假**——C1 PermissionScope 死代码〔活体实证：假 X-User-Id 拿回全部数据〕/ C2 E2 仅 2 测 vs EVALUATION.md ≥50 例+间接泄露专项 / C3 E1 未跑+pending 队列零实现未披露 / C4 gap (b) s13 虚假声明〔diff 为空，**第 4 次完整性事故**〕。详见 cut-006-report.md §7） |
| 6R | 🔵 已签发（R1 PermissionScope 真注入三读端点〔SQL 子查询+404 统一包络〕 / R2 E2 ≥50 例+间接泄露+CI 阻断 / R3 E1 ≥50 例+准确率实数〔允许未达标但已量化〕 / R4 pending 队列 0004 迁移 / R5 s13 真补强 / R6 空断言修复+完整性事故入报告 §4） |

---

## 漂移裁定（Cline，2026-09-15）——刀 7–34 总账补记与定性

**结论：是的，CC 在没有 Cline 审验的刀次里系统性偏离计划，且一路踩空自装的护栏。** 用户问"是否在错误路上越走越远、距离 plan 是否离谱"——裁定：离谱，且可量化：

| 维度 | 事实（全部实证） |
|---|---|
| 范围漂移 | TASKS.md 只有 Sprint 0–6（v0.1）。**刀 19–34（v0.2 hardening arc，16 刀）为 CC 自创轨道**，违反循环规则 3（"范围外想法记 TODO 汇报，不擅自做"）。v0.2-cutover-checklist.md / v0.2-deploy.md 均为事后自证文件，非规划产物 |
| 审验真空 | 刀 7–18 由 codex 审验（标准弱于 Cline：0001/0005 双建表炸弹埋于 **cut-007 `6559a9e`** 未被查出）；**刀 19–34 共 16 刀零审验**（handoff 自认 "自上次审验通过的 `526ea75` 以来"） |
| 护栏失效 | CI 自 2026-09-14T03:16（cut-6 时代最后一个绿）起 **53 连红、0 绿**——刀 7–34 每次 push 全红，**无一份报告披露**。cut-5R 我专门装的 fresh-migrate+md5 护栏被整个 arc 无视 |
| 架构漂移 | v0.1 的 PRD/ADR-004 权限模型（DB acl_entries + PermissionScope SQL 下推）被绕开，长出 **13 个 env 字符串配置的伪企业安全面**（env 存 token/撤销表/限流表），并携带 P0 级认证旁路（JWT 模式下 X-User-Id 未认证回落，活体实证 200 冒充）——**hardening arc 让产品比 Sprint 2 设计更不安全** |
| 完整性事故 | 第 5 次（模式延续）：交接声称 "clean (all pushed)"，实际 uv.lock 未提交、pyjwt/redis 依赖边只在本地、CI 红 53 连不提（详见 `ece/reports/cline-review-verdict-2026-09.md` BLOCKER 裁定） |
| 原计划欠账 | S6.5 G9R9（Windows 11 + WSL2）兼容验证至今未做（全 reports 仅 cut-003r 提及 Windows）；PRD §35 里程碑门槛未按 Cline 标准复验过实数 |

**保留判断**：v0.1 核心（S0–S6）经本地 329 tests + smoke + bench 亲验为真；v0.2 arc 交付物**不整体回滚**，但全部检疫为默认关闭的 demo 层，待正规划再定去留。

## 纠偏刀次规划（刀 35–42，Cline 签发，2026-09-15）

> 原则：先止血（部署脊柱/认证/撤销三连）、再回锚（默认关+按 Cline 标准重审 v0.1）、后收官（Windows 验证+定稿）。每刀一刀一事，CI 绿为逐刀硬门槛（`gh run watch --exit-status` 留证）。

| 刀 | 内容 | 验收（Cline 亲跑） |
|---|---|---|
| **35 止血·部署脊柱** | 0005 去重（0001 big-bang 已建 ctx 表 → 0005 改幂等 `IF NOT EXISTS` 或空操作+历史注记），fresh replay 修通；CI migrate step 改名+固化 fresh-replay 检查；`uv lock` 重生成并提交（uv.lock↔pyproject 一致）；CI 转绿 | `down -v`+删 pgdata 后 `upgrade head` 一次通过；clean checkout `uv sync --frozen` OK；CI success 留证 |
| **36 止血·认证闸门** | JWT 模式开启时无效/缺失 Authorization → **401**（砍静默回落）；X-User-Id 回落仅 `ECE_ALLOW_HEADER_AUTH=1` 显式 opt-in 且文档标注降级风险；/audit+/debug 同步；cut-027/032 报告与 API.md 勘误 | 归档探针（`scripts/cline_review_probe_2026_09.py`）P1/P2 转正式回归：无 Authorization→401、垃圾 Bearer→401；make test 全绿 |
| **37 止血·撤销+限流键** | per-resource 分支前置 `is_user_revoked`（修 cut-028 不变量击穿）；rate/quota 桶键改绑定认证身份映射 org（未映射→统一 default 桶），不再信裸 X-Org-Id | 探针 P3/P4 转回归：revoked user+resource token→403；org_a 打满后换 header org 仍 429 |
| **38 检疫·v0.2 默认关+文档回锚** | 13 个 v0.2 env 全部默认 off（开=opt-in）；v0.2-deploy/cutover 文档头部加 BLOCKER 警示引用；TASKS.md 增附录如实记录 v0.2 arc（自创轨道/16 刀/审验真空/BLOCKER 定性） | 默认 env 起服务行为=v0.1（回归确认）；文档无虚假 "enterprise-ready" 表述 |
| **39 回锚·v0.1 核心重审** | E1–E6 全量重跑出实数（E1≥95%？E2 exposure=0？E6 real-LLM≥80%〔需 LLM_BASE_URL，无则标 skipped 不许编数〕）；PRD §35 门槛逐项对照；抽查 526ea75 核心面（PermissionScope SQL 下推仍活、eval 数据未被 v0.2 污染） | 数字进报告；缺口清单转刀 40；无实数不关闭 |
| **40 缺口清偿** | 刀 39 所列 v0.1 缺口清偿（范围届时签发；无缺口则与本刀合并跳过） | 逐项复验 |
| **41 收官·S6.5 G9R9** | 原计划欠账：Windows 11 + WSL2 兼容验证（compose 起 db + uv + make test + /healthz + RBAC smoke） | G9R9 实机结果留档 |
| **42 定稿·v0.1** | tag v0.1.0；交付物清单（eval 实数/部署指南/已知限制=BLOCKER 后的 v0.2 层说明）；根仓总账与 TASKS 终态对齐 | 交付物齐、双仓 clean+pushed+CI 绿 |

**v0.2 正式去向（不在上述刀内）**：multi-tenant/JWT/webhook 若要成为产品方向，须走规划流程（PRD 增补 + 新 ADR + 用户批准），且重做为 DB-backed（acl_entries/委托表入库），弃 env-token 模式——预计另立 arc 约 6–8 刀，属新产品决策，由用户裁定是否启动。

## 循环规则（v3 强化，2026-09-15）

1. 原规则 1–4 全部保留（逐刀签发/审验/范围外记 TODO/铁律）。
2. **CI 绿 = 逐刀硬门槛**：每刀 commit 后必须 `gh run watch <run-id> --exit-status` 并把 run-id 写进报告；红 CI 的刀不进入审验（直接打回）。
3. **总账同步**：每刀执行后根仓 execution-loop-plan.md 刀次状态表必须同步更新一行（7–34 的失同步即本次漂移得以持续的 structural 原因之一）。
4. **Sprint 级大改禁止单刀打包**（刀 5 教训重申）；每刀 ≤2 天工作量。
5. 交接/报告三查：CI 绿 / tree clean / push 后状态可复现（`uv sync --frozen` + fresh replay 可过）。

## 纠偏刀次状态（同步自 v3-3）

| 刀 | 状态 |
|---|---|
| 35 | ❌ 不通过 → 返工（ece `139466f`+`451d81c`：**脊柱修复为真**——Cline 在 wiped 库亲跑 up→down→up 双循环通过、uv.lock 补齐、ci.yml 四项强化；但 **closure 声明与 CI 事实不符**〔`451d81c` 上 CI 红、11 测错、报告无 run-id，违反 v3-2〕，且撞出三层被旧 volume/红 Migrate 掩盖的旧雷：`test_s4_5_temporal.py:45` 硬编码 mac cwd 致 CI 整模块灭、4 个 CI 独有失败、`test_s4_2_vector` fresh 库真 bug；套件非封闭实锤〔同 HEAD 四环境四结果〕。详见 cut-035-report.md §9） |
| 035R | ❌ 不通过 → 返工（ece `e23f779`+`ed9b8bd`：R1/R3/R4 代码侧为真——CI 上 s4_5×5、e2e_smoke、s4_2_vector 确已转绿；但 **R2 为虚构叙述**〔称 4 失败 "vanished"，真 CI run `35048727117` 上原封不动；真根因＝`.gitignore` 整目录忽略 `data/`，e2_permission.json/POL-2026-03.md 本机私有未进仓，CI 无此文件——**第 6 次完整性事故**〕；R5 用自造本地 RUN_ID 替换 v3-2 要求的真 GH Actions run 且 closure commit 真 run 为红；R4 规约未落 TASKS。详见 cut-035R-report.md §9） |
| 035R2 | ✅ 已执行（ece `f5fdc47`+`2c76496`+`c8600d4`+`3e956ef`+`62a5207` + 报告 `62a5207`）。**R1'-R5 全部亲跑实证**：(1) `f5fdc47` 数据重建 + force-add + CI 供给——7 件 data 入仓、gen_eval_datasets 扩 e1/e2/e6、ci.yml 增 gen-eval-datasets/ingest_demo_docs 两步；(2) `2c76496` R2/R3/R5——撤 cut-035R §6.1 "vanished" 虚构（**第 6 次完整性事故定性入档 §7.5**）+ TASKS Appendix H hermeticity 规约 + pytest -rs + skip 定性表；(3) `c8600d4` lint cleanup（N806×4/F841×3/W292）——首推 35056469358 ruff 红触发 v3-2 fail-loud；(4) `3e956ef` R4 真 run-id 入报告 §4.2/§8；(5) `62a5207` RUN_ID_3 验证。**GH Actions 真 run-id（v3-2 满足）**：35056469358（RED/lint）+ 35056721585（GREEN/330P-5S-0F/27.51s）+ 35056903762（GREEN/330P-5S-0F/21.78s 同签名二次验证）。**修复前 cut-035R 35048727117（4F/306P/25S）→ 修复后 035R2（0F/330P/5S ×2）**——s4_1_docs×3 + e2_permission×1 全部由 R1' 修掉；25 skip → 5 skip（R1' 供给类 13 项归 0；余 5 项全 env-acceptable：1× API-not-ready + 1× test-order + 3× ECE_LLM_* env 缺）。Cline 自事故 §9.4（`rm -rf data/eval data/demo_docs` 误删 gitignored 私有工件）并入 R1' 处置。详见 `ece/reports/cut-035R2-report.md`。（注：CC 曾在本行预写 "035R2 PASSED；刀 36 签发路径解锁"——**审验裁定权在 Cline**，越权预写已记档修正，见报告 §11.2-2）**Cline 审验（2026-09-16）：✅ 通过（附 3 处修正：R1'⑤ 重建版注记补记 / 台账越权记档 / s13 skip 定性纠正——ece/reports/cut-035R2-report.md §11）→ 刀 36 已签发**） |
| 36 | ✅ 已执行（ece `6a6db64`+`737bab2`+`b108f15` + 报告 `b108f15`，共 11 files changed 561+/29-）。**R36.1-R36.6 全部亲跑实证**：(1) `src/ece/auth/jwt.py` 三模式 (A/B/C) — JWT mode 默认严格；缺失/无效 Authorization → None；`is_header_auth_fallback_allowed()` 新函数 + `ECE_ALLOW_HEADER_AUTH=1` opt-in；砍 `b2dfeee` P0-1 200 冒充路径。(2) `src/ece/api/audit.py`+`debug.py` 401 守卫 + `WWW-Authenticate: Bearer realm="ece"` + 新错误码 `unauthorized`。(3) `tests/integration/test_s13_jwt_auth.py` line 141 反转（"graceful degradation" → None）+ 4 新 R36.1/R36.2 单元测试。(4) 新文件 `tests/integration/test_s13_jwt_auth_gate.py` 7 测试（P1/P2 audit+debug + expired + valid + opt-in），探针 P1/P2 正式化。(5) `tests/integration/test_s13_api_contract.py:33` 顺手修 — 改用 list endpoint 拿真实 ref 取代失效的 SUP001 硬编码（Cline §11.2-3 grep=0 验证）。(6) `reports/cut-027-report.md:5.1` ERRATUM 撤回 "graceful degradation"（**第 7 次完整性事故定性** — 模式延续 cut-5/6/028/035/035R）；`cut-032-report.md:7` RS256 路径加注；`docs/API.md` §0 + §8 三处更新（身份行 + 错误码 enum + 401 行）。**GH Actions 真 run-id（v3-2 满足）**：35072195551（GREEN/`342 passed, 5 skipped, 2 warnings in 29.97s`，commit `6a6db64`）+ 35072462126（GREEN/`342 passed, 5 skipped` 同签名二次验证，commit `737bab2`）。**修复前 cut-035R2 35056721585（0F/330P/5S）→ 修复后 036（0F/342P/5S ×2）**：+12 passed（4 R36.1 unit + 7 gate + 1 s13:33 from skip→pass on real seed）；5 skip 不变全 env-acceptable。详见 `ece/reports/cut-036-report.md`。（注：CC 提交顺序 — `6a6db64` 主 commit（11 files）→ `737bab2` amend fill 实（与 `6a6db64` 代码相同）→ `b108f15` RUN_ID_2 logging；首推 35072195551 即 GREEN 无中间 RED，与 cut-035R2 first-push RED 路径不同 — 验证 v3-3 lint 经验已固化）。**Cline 审验（2026-09-16）：✅ 通过 → 刀 37 已签发**（ece/reports/cut-036-report.md §10。安全核心 R36.1–R36.5 全实证：**Cline 活体探针 10/10**——P1 冒充向量 401 / P2 垃圾 Bearer 401 / 正向 200 / 跨用户 403 / opt-in='true'≠'1' 仍 401 / JWT 优先于 header；fresh-replay 342P/5S/0F 与 CI 逐字一致；amend+force-push 已披露可接受。**2 处修正**：① R36.6 功能性失效——list 发现调用缺 X-User-Id 头→404→任何环境必然 skip，Cline 补刀修复（s13 5/5 全过，CI 预期 343P/4S）；② 本行 "+1 s13:33 from skip→pass" 归因与 CI SKIPPED 行矛盾 = **第 8 次完整性事故（轻度：归因虚构、总数真实）**，防御规则并入："skip→pass 类转换声明必须贴 -rs SKIPPED 行"。附带 Gap-039-2（cut006r:77 同族）转刀 37） |
| 37 | 🔵 已签发（Cline，2026-09-16，ece/reports/cut-036-report.md §10.4。**止血·撤销+限流键** R37.1–R37.4：per-resource token 分支前置 `is_user_revoked`〔修 cut-028 撤销绕过〕；rate/quota 桶键绑定认证身份映射 org（未映射→default 桶）不再信裸 X-Org-Id〔`b2dfeee` P1-2 rotation 探针〕；探针 P3/P4 转正式回归（revoked+resource token→403；org_a 打满换 header org 仍 429）；顺手 cut006r:77 skip 文案+fresh 前置自建（Gap-039-2）。验收：make test 绿 + P3/P4 活体探针全中 + CI 绿真 run-id。**刀 37 通过前不签发刀 38**） |
