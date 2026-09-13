# Cline Red Team Review — Track B Spec（docs/track_b/）审验报告

> **Reviewer**: Cline（红队角色：目标为推翻结论，而非维护结论）
> **Date**: 2026-09-13
> **审查对象**: `docs/track_b/README.md`、`execution-plan.md`、`track-a-decisions.md`（commit `a10c75a`）
> **审查方法**: 三文件全读 + **上游交叉验证**（根仓 10 个 ADR 实际标题逐一对读；`ece/TASKS.md` 全文任务编号比对；`docs/architecture_v2/platform-kernel-definition.md` K1–K8 映射比对；上游资产存在性验证）

---

## 0. 结论速览

| 项 | 判定 | 一句话理由 |
|---|---|---|
| **track_b 三文件整体** | ✅ **PASS WITH CONDITIONS** | 结构清晰、任务编号与 ece/TASKS.md 完全对齐、K1–K8 映射正确、S4.5 缺口识别准确且 spec 详细度足够开工 |
| **审计链文件（track-a-decisions.md）** | ⚠️ **ADR 编号错位 5 处** | 恰好发生在"可追溯 + 可质疑"这个核心卖点的文件里，必须先修 |
| **S4.5 MCP spec** | ✅ 设计合格 | 工具清单/文件结构/测试/DoD 俱全；1 处接入命令错误 |
| **Track B 启动条件** | ⚠️ 完成 R1–R4 修复后即可启动 ECE session | 修复全部在本仓文档层，预计 20–30 分钟 |

---

## 1. 交叉验证记录（全部通过项）

1. ✅ **上游资产真实存在**：`docs/adr/ADR-001~010.md`、`docs/architecture_v2/`（3 文件）、`docs/product_v2/reference-applications.md`、`docs/diagrams/`（7 个 .mmd，含授权要求的 platform-kernel-architecture.mmd + glean-layers-v2.mmd）。
2. ✅ **任务编号 100% 对齐**：execution-plan §1 矩阵中 S0.1–S6.5 全部与 `ece/TASKS.md` 实际条目一一对应；S4.5 确实不存在于 TASKS —— 缺口判断正确。
3. ✅ **K1–K8 映射与 Phase 5 一致**：K1→ADR-003 / K2→ADR-006 / K3→ADR-007 / K4→ADR-009 / K5→ADR-010 / K6→ADR-008 / K7→ADR-004 / K8→(隐含 ADR-006)，与 platform-kernel-definition.md §1.1 完全一致。
4. ✅ **commit 引用准确**：b527574（Phase 2.5 修复）、49604b0（STOP Gate）、421dc06 / 713c083 / 03b096e 均与 git log 一致。
5. ✅ **"42 条证据"** 与 evidence-matrix（C01–C42）一致。
6. ✅ **两套 ADR 编号不混淆** 的原则声明正确（问题只是个别引用打错了，见 F1）。
7. ✅ **`ece/` 仓未被触碰**（仍仅初始 commit `0d3a008`，工作树干净）。

---

## 2. Findings

### F1【MEDIUM】ADR 编号错位 5 处（审计链核心卖点受损）

根仓 ADR 实际主题（已逐一对读）：ADR-003=Permission、ADR-004=MCP Tool、ADR-005=Graph 简化版、ADR-006=Context Assembly 12 步、ADR-007=Entity Resolution、ADR-008=Domain Evaluation、ADR-009=Domain Ontology、ADR-010=Domain Reasoning。

错位清单：

| # | 位置 | 现状 | 错误 | 应改为 |
|---|---|---|---|---|
| 1 | `README.md` §3.2 铁律表 "LLM 不可知" | "ADR-006(根)+ ece/ADR-006" | 根 ADR-006 是 Context Assembly，不是 LLM | "ece/ADR-006 + 根 ADR-010(仅'规则优先'维度)" |
| 2 | `README.md` §3.2 铁律表 "领域包隔离" | "ADR-010(根) + ece/ADR-010(独立)" | 根 ADR-010 是 Domain Reasoning，不是域包隔离 | 只留 "ece/ADR-010"（根仓无对应 ADR） |
| 3 | `track-a-decisions.md` §9.1 ece/ADR-010 行 | "根 ADR-010(根域包隔离…)" | 同上，根 ADR-010 不是域包隔离 | "(根目录无对应——领域包隔离是 ECE 工程决策)" |
| 4 | `track-a-decisions.md` §9.2 行 3 LLM Provider | "LLM 不可知 + 规则优先(根 ADR-010)" | "规则优先"引用正确，但"LLM 不可知"根仓无 ADR 支撑 | 拆开："规则优先(根 ADR-010)；LLM 不可知(ece/ADR-006)" |
| 5 | `track-a-decisions.md` §9.2 行 4 领域包隔离 | "O Build 决策(根 ADR-009 + ADR-010)" | 根 ADR-009 是 Domain Ontology；域包隔离不是这两者的主题 | "(根目录无对应，ece/ADR-010 独立承担)" |

**为什么必须修**：这份文件的价值主张就是"可追溯 + 可质疑"。ECE session 若按错误引用回查根 ADR-006/010，会发现内容对不上 → 对整条审计链的信任崩塌。

### F2【MEDIUM】execution-plan §4.4 Claude Code 接入命令错误

现状：`claude mcp add ece-context -- stdio -C /path/to/ece python -m ece.mcp.server`

- `claude mcp add` **没有 `-C` flag**（那是 git 的语法）。ECE session 照抄会直接失败，且 DoD 里"`claude mcp list` 显示已连接"会卡住。
- 正确写法（在仓库根目录执行）：`claude mcp add ece-context -- python -m ece.mcp.server`；如需跨项目可用加 `-s user`。

### F3【MEDIUM】`ece/TASKS.md` S4.2 "权限后置过滤" 与根 ADR-003 存在铁律张力

- S4.2 原文："四路 + Entity Linking + **权限后置过滤** + merge/rank" —— 字面语义是 post-filter（先取回再过滤）。
- 根 ADR-003 / platform-kernel-definition K1 明确："SQL 子查询层强制，**不是 post-filter**"；S2.2 也写 "PermissionScope 注入所有 Store 读路径（SQL 子查询过滤）"。
- **裁定**：对 /search 的 4 路召回，正确实现是**每一路召回的 SQL 内做 PermissionScope 过滤（先过滤、后排序/截断）**，不是取回 top-k 后再丢。否则存在排序信号泄露（无权限内容影响了排序位置）与 limits 截断后权限内容挤占召回的风险。
- **修复位置**：措辞在 `ece/TASKS.md`（不在本仓）——已纳入 ECE session kickoff 指令（本报告 §5.2 任务 b），首刀处理。track_b 侧无需改（execution-plan 对 S4.2 的表述"Permission Filter 收口"是对的）。

---

## 3. Findings（低优先级）

### F4【LOW】"视 Robin 会谈" 触发条件表述已过时

Robin 路径已取消（用户决定，README §0 已声明），但三文件中仍多处出现 "Phase 5+ 视 Robin Q9 决定"（README §6.1 风险表、track-a-decisions §3.1、L1/L2 相关表述）。ECE session 读到会困惑"到底还要不要等 Robin"。

**修复**：在这些表述处统一加注："（Robin 路径已取消 2026-09-13；触发条件改为 Glean 期权重启，或 Phase 5+ POC 客户已有 Glean）"。Phase 5 历史文档（platform-kernel-definition.md）**不改**——Track A 已 STOP，保持历史原貌。

### F5【LOW】S4.5 的 `mcp` SDK 依赖未列入 S0.1 依赖清单

`ece/TASKS.md` S0.1 的依赖列表（fastapi/pydantic/sqlalchemy/alembic/psycopg/pgvector/pytest/ruff/mypy）不含 `mcp`。execution-plan §5 风险表提到用 `mcp[cli]` SDK，但未说明何时入 pyproject。

**裁定**：S0.1 **不加**（Sprint 0 保持最小地基），S4.5 动工时引入 `mcp` 依赖并锁版本。已写入 ECE kickoff 指令（§5.2 任务 a），无需改本仓文档（可在 execution-plan §4.3 补一句，随 R2 一起改）。

### F6【信息项】Robin 取消的战略合理性

红队职责所在，记录一句：取消 Robin 路径与此前全部决策链自洽（Phase 0 已把 Glean 定位为"非阻塞期权"、可达市场无 Glean 客户、v3 主路径 D 私有化）。Partner 文档保留作期权 ✅。此决定无审计问题。

---

## 4. Sign-off 条件（本仓修复，R1–R4，预计 20–30 分钟）

- [ ] R1：F1 五处 ADR 编号错位修正（README.md ×2、track-a-decisions.md §9.1 ×1、§9.2 ×2，按 §2 F1 表格的"应改为"列执行）
- [ ] R2：F2 execution-plan.md §4.4 命令修正 + §4.3 文件结构处补一句 "mcp SDK 依赖于 S4.5 动工时引入（S0.1 不加）"
- [ ] R3：F4 三处 "视 Robin" 表述加注（Glean 期权重启措辞）
- [ ] R4：commit + push，提交信息注明 "track_b spec fixes per cline-review-trackb-spec.md"

**完成 R1–R4 后，Track B 启动条件全部满足。**

---

## 5. 下一步

### 5.1 本仓（Track A session，CC）

执行 §4 R1–R4，完成后本仓 Track B 相关工作结束，仓库转入"战略基线 + 期权维护"模式（不再有常规任务；新证据出现时增量 ADR）。

### 5.2 ECE 仓（新 session，kickoff 指令已定稿）

用户在**新会话**（cwd = `/Users/kjonekong/projects/domainAgentECE/ece`）粘贴以下指令启动 Sprint 0（完整文本已随本次审阅交付给用户，要点）：

1. 按顺序读：ece/CLAUDE.md → ece/TASKS.md → ece/docs/ 五件套（重点 PRD §27/§35/§48）→ 根仓 docs/track_b/ 三文件（只读）
2. 首刀任务修订（写入 ece/TASKS.md 后再动工）：
   a. 新增 S4.5 MCP Tool Layer（设计照抄 execution-plan.md §4；create_task/send_message 仅 Preview；auth.py 强制 PermissionScope；修正确后的接入命令）
   b. S4.2 措辞修正："权限后置过滤" → "权限 SQL 下推（四路召回各自查询内过滤，先过滤后排序；denied 仅计数）"
3. 执行 Sprint 0（S0.1–S0.6，~2 天）
4. 纪律：每 Sprint 完成跑对应 E 套件 + commit + 停下汇报；铁律零容忍；M1/M2/M3 门槛不达不进下一阶段

---

**Reviewer**: Cline
**Sign-off 状态**: track_b 三文件 PASS WITH CONDITIONS（R1–R4）
**Repo**: github.com/cscoheru/domainAgentECE (main)


