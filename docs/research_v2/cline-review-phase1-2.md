# Cline Red Team Review — Phase 0/1/2 审阅报告与下一刀签发

> **Reviewer**: Cline（红队角色：目标为推翻结论，而非维护结论——per ROOT `CLAUDE.md` / `RED_TEAM_REVIEW.md` 角色定义）
> **Date**: 2026-09-13
> **审查对象**: `cline-review-brief.md` 所列 Phase 0/1/2 全部交付物（15 文件 + 4 commits）+ git 迹 + **独立网络验证**
> **审查方法**: 文件全读 / git diff 验证 v1 未改动 / **用独立抓取通道实测 6 个种子 URL**（关键差异：CC 用 claude.ai WebFetch 全部 BLOCKED，我用备用通道全部成功）

---

## 0. 结论速览

| Phase | 判定 | 一句话理由 |
|---|---|---|
| **Phase 0**（Partner 会谈准备） | ✅ **PASS**（小修后可用） | questions-for-glean.md 质量高（red line / 优先级 / 收尾动作俱全）；brief 战略定位清晰、与主路径 D 关系处理正确 |
| **Phase 1**（Evidence Collection） | ❌ **核心前提被推翻，需轻量重做** | "全网 BLOCKED" 为**工具特定问题**（claude.ai WebFetch 域安全策略），非真实网络封锁——本报告 §2 已带回 8 条新证据 |
| **Phase 2**（Capability Map） | ✅ **PASS WITH CONDITIONS** | 结构合规（每格挂 C 编号）、决策方向成立；但 4 处结论需按新证据更新（见 §3 F3） |

**下一刀（已签发）**：见 §5。修复 + 证据整合后进入 Phase 3。

---

## 1. 独立验证：推翻 Phase 1 的"BLOCKED"定性

### 1.1 实测结果（2026-09-13，Cline 独立通道）

| URL | CC (claude.ai WebFetch) | Cline (独立通道) |
|---|---|---|
| https://www.glean.com | ❌ BLOCKED | ✅ 成功（716KB） |
| https://developers.glean.com | ❌ BLOCKED | ✅ 成功（87KB） |
| https://www.glean.com/blog/glean-partner-network | ❌ BLOCKED | ✅ 成功 |
| https://www.glean.com/blog/introducing-agent-identity | ❌ BLOCKED | ✅ 成功 |
| https://www.glean.com/ai-agent-builder | ❌ BLOCKED | ✅ 成功 |
| https://www.glean.com/blog/live-fall-25-main | ❌ BLOCKED | ✅ 成功 |

### 1.2 定性

- BLOCKED 是 **claude.ai WebFetch 的域安全策略**，不是"网络策略屏蔽 glean.com 整个域"。
- `evidence-matrix-v2.md` 头部 "⚠️ BLOCKED — All glean.com + developers.glean.com URLs blocked by network policy" **表述过强，必须修正**为：工具特定限制；已由备用通道完成部分重验证。
- 用户选 Option C（接受 v1 baseline）时的决策依据不完整——当时不知道备用通道可行。现在补救成本极低（本报告已带回证据）。

---

## 2. 新证据登记（C35–C42，供 CC 原样整合进 evidence-matrix-v2.md）

> **来源标注规范**：`Source` 列统一写 `URL (independently fetched by Cline, 2026-09-13)`。引文为官方页面原文，CC 不得改写引文本身。

| # | Claim | Source | Evidence（原文引文） | Confidence | Last Verified |
|---|---|---|---|---|---|
| **C35** | Platform API（Agents/Chat/Search/Skills/Triggers）仍为 experimental preview（复核 C15） | developers.glean.com (independently fetched by Cline, 2026-09-13) | "Build search experiences and run Glean agents in your applications with our new Platform APIs — now rolling out in experimental preview." | CONFIRMED | 2026-09-13 |
| **C36** | Agent Identity：scoped service credentials + 审计归属 agent 自身账户 + admin 可轮换/吊销；状态 **beta**（升级 C29） | glean.com/blog/introducing-agent-identity (independently fetched by Cline, 2026-09-13) | "agents act through their own scoped service credentials — visible in the audit trail, and governed by the people responsible for governing access: admins can rotate or revoke any credential, for one system or all of them, at any time." / "Every action lands in the audit trail under the agent's own account, with the person or schedule that triggered it recorded alongside." / "The feature is now available in beta for our Glean customers." | CONFIRMED | 2026-09-13 |
| **C37** | Glean:LIVE Fall'25 官方可用性矩阵（部分解答 C11；细化 C19） | glean.com/blog/live-fall-25-main (independently fetched by Cline, 2026-09-13) | "Generally available: Enterprise Graph, personal graph, Agentic Engine 2 (Assistant only), third-generation Glean Assistant, Deep Research*, all knowledge queries, fast and extended thinking modes, contextual image understanding, schedule agents*, agent version control, agents respond to user inputs, featured agents, enhanced Chat API (Agentic Engine 2)*." / "Beta: Personalized writing, conversational agent builder, agent looping, Assistant routes requests to agents automatically, agents toolkit, and remote MCP servers." / "Coming soon: Glean Canvas, 100+ new actions, Agents (Agentic Engine 2), LLM model choice in Assistant, and an MCP directory." | CONFIRMED | 2026-09-13 |
| **C38** | Agent Builder 治理文案出现 "evaluations" 一词（指向执行路径与性能）——**收紧 C22 措辞的依据** | glean.com/ai-agent-builder FAQ (independently fetched by Cline, 2026-09-13) | "Permission rules and policies apply on every request, while logs and evaluations provide visibility into execution paths and performance." | CONFIRMED | 2026-09-13 |
| **C39** | Glean 官方运营开发者文档 MCP server，官方支持 Claude Code / Cursor / Codex / Gemini CLI 等 IDE 接入（强化 M08 "IDE 集成"行） | developers.glean.com (independently fetched by Cline, 2026-09-13) | "Bring Glean to your IDE — Claude Code, Cursor, Codex, and any MCP host." + `claude mcp add glean-developer-docs https://developers.glean.com/mcp --transport http --scope user` | CONFIRMED | 2026-09-13 |
| **C40** | 鉴权模式：OAuth 优先（per-user Client/Platform），Glean-issued token 用于 Indexing / global **ActAs**（M04 代理身份相关） | developers.glean.com Quickstart (independently fetched by Cline, 2026-09-13) | "Prefer OAuth for per-user Client and Platform work in Authentication. Use a Glean-issued token for Indexing, global ActAs, or when no OAuth path exists." | CONFIRMED | 2026-09-13 |
| **C41** | Agent Harness 已进入 glean.com 页脚 PRODUCT 导航（仍无详情页）；Transform 导航仍标 "Coming soon"（细化 C25） | glean.com (independently fetched by Cline, 2026-09-13) | 页脚 PRODUCT 列表含 "…Agent Library Agent Harness Enterprise Context…"；主导航 "Coming soon — Glean Transform" | CONFIRMED | 2026-09-13 |
| **C42** | 市场语境：Gartner 新兴市场象限 "Market Shaper"（No-Code Agent Builders）；官方竞品对比页（vs ChatGPT Enterprise / M365 Copilot / Claude Enterprise） | glean.com (independently fetched by Cline, 2026-09-13) | "Glean Named a Market Shaper in the Gartner Emerging Market Quadrant for No-Code Agent Builders"；COMPARISONS 导航三页 | CONFIRMED | 2026-09-13 |

**附带观察**（并入相应模块即可，不单独立 C 编号）：

1. 首页导航连接器口径为 "more than 250"（v1 C05 的 275+ 来自 connectors FAQ——两处官方口径并存，保留 C05 并加注）。
2. developers.glean.com 新增 "Cookbooks — Recipes: Runnable patterns that go from problem to working demo to scaffolded starter code — auth and permissions laid out for each"（Partner enablement 信号，Q6 可引用）。
3. Web SDK："one npm package, two components"（renderSearchBox / renderChat）。
4. Client API 目录比 v1 C16 更宽：含 Activity / Announcements / Answers / Collections / Messages / Pins / Shortcuts / Summarize。

---

## 3. 逐项 Findings

### F1【CRITICAL】Phase 1 "全网 BLOCKED" 定性错误
见 §1。修复：`evidence-matrix-v2.md` 头部表述、§0 网络访问状况表、README Phase 1 行的 Notes——统一改为"claude.ai WebFetch 工具特定限制；2026-09-13 已由 Cline 备用通道完成 6 URL 重验证 + C35–C42 新增"。

### F2【HIGH】C22 措辞必须收紧（否则撑不住 Phase 4/5）
C22 原文"Glean Agent 观测不含业务正确性/领域推理质量评估"标记 INFERENCE_HOLDS。但 C38 显示官方 Agent Builder FAQ 已使用 "logs and **evaluations** provide visibility into execution paths and performance"。
**裁定**：execution-path/performance 评估 ≠ domain correctness 评估，**结论方向保留**，但措辞必须改为：
> "未见 Glean 提供领域正确性/业务推理质量评估的公开证据；官方 Agent 治理文案出现 'evaluations'（语义指向执行路径与性能，C38），不构成 domain evaluation 的证据。"
影响文件：evidence-matrix-v2.md（C22 行）、capability-matrix-v2.md 行 13/14 注脚、07-governance-evaluation.md。

### F3【MEDIUM】4 处模块结论需按新证据更新
1. **M04**：C29 升级为 C36（CONFIRMED, beta, 审计归属细节）；新增 C40 ActAs。§3 能力判断表 "Agent Identity" 行改挂 C36。
2. **M05**：C11 从 STILL_UNKNOWN 改为**部分解答**（C37：agent looping=beta、conversational agent builder=beta、agent version control=GA、schedule agents=GA）；branching/HITL/per-step model selection 仍 UNKNOWN。"Workflow 细节" 行从 ✗ 改为 △(beta 证据 C37)。
3. **M08**：§3 "IDE 集成" 行从 "△ 推断" 改 "✓ CONFIRMED (C39)"——Glean 官方运营 MCP server 并发布 Claude Code/Cursor 一键配置。
4. **capability-matrix-v2.md**：行 11 Agent Identity 加注 "beta (C36)"；行 9 MCP 加注 "remote MCP servers beta (C37)"；行 8 Agent Builder 加注 "conversational builder beta (C37)"。

### F4【LOW】卫生问题清单
1. `README.md` Phase Status 表有**重复的 Phase 2 行**（一行 DONE 一行 PENDING）——删除 PENDING 行。
2. `evidence-matrix-v2.md` §5 "Phase 2 启动条件" 与 §7 "下一步动作(待用户决定)" 是 Phase 1 时代的过期内容（用户已决策、Phase 2 已完成）——改写为 §5 "复核状态（2026-09-13 更新后）" 与 §7 "下一步：Phase 3"。
3. `partner-meeting-brief.md` §11 遗留未勾选框（git commit/push 已完成、Phase 1 已发生）——更新为完成态 + 指向本报告。
4. C26 的"2026-08-25 公开亮相"日期：我的抓取未捕获发布日期字段，**日期保留 v1 草稿口径**，但 Partner Network 博客存在性已由我确认——C26 置信可升 CONFIRMED（日期子项标 INFERRED）。

### F5【确认项】CC 自查中的疑点已验证清白
1. ✅ v1 文档未改动：`git diff f28472e..HEAD -- docs/research docs/architecture docs/product docs/cases docs/customer docs/diagrams docs/adr` 输出为空。
2. ✅ `ece/` 独立仓库未触碰（log 仅初始 commit）。
3. ✅ `09-partner-boundary.md` 引用的 `docs/research/Glean Partner Manager Call 战略准备稿.md` 真实存在。
4. ✅ Capability Matrix 16 行每格挂 C 编号或 `?`，Phase 2 DoD 形式合规；行 13 "不确定" 允许保留，但须在 Phase 4 裁决。

---

## 4. Sign-off 条件（全部完成 = Phase 1/2 正式验收通过）

- [ ] R1：F1 修复——evidence-matrix-v2.md 头部与 §0 表述更正 + README Phase 1 Notes 更正
- [ ] R2：C35–C42 原样登记进 evidence-matrix-v2.md §4（"Phase 1 本轮新增证据"重写为"2026-09-13 补充证据（Cline 独立通道）"）
- [ ] R3：C29→C36 升级、C15→C35 复核标注、C11 部分解答标注、C22 措辞收紧（F2 定稿措辞）
- [ ] R4：F3 四处模块/矩阵更新（M04/M05/M08/capability-matrix）
- [ ] R5：F4 卫生修复四项
- [ ] R6：partner 两份文档趁热升级——Q10/Q12/Q14 引用新锚点（如 "We noticed agent looping is in beta and agent version control is GA per your Fall'25 announcement — how do partners…?"），Q6 可引用 Cookbooks 信号；brief §10.2 的 BLOCKED 注记同步更正
- [ ] R7：commit + push（提交信息注明 "Phase 1/2 review fixes per cline-review-phase1-2.md"）

---

## 5. 下一刀（Phase 2.5 证据整合 → Phase 3 启动）

**执行顺序**：

1. **Phase 2.5（本轮）**：完成 §4 R1–R7。全部为文档更新，预计 0.5–1 小时。完成后停下汇报。
2. **Phase 3（Architecture Reconstruction）**：按 RESEARCH_PRD_V2.md §9 Phase 3 DoD 执行——官方描述 vs 推导分层成图、G/O/P/? 大图、mermaid 入 `/docs/diagrams/platform-kernel-architecture.mmd` + `glean-layers-v2.mmd`。此时证据基线已含 C35–C42，图上标注可引用新证据。
3. Phase 3 完成后照例停下汇报等确认，再进入 Phase 4。

**禁令提醒**：本阶段仍不写产品代码、不动 `ece/`、不改 v1 文档；引文不得改写。

---

**Reviewer**: Cline
**Sign-off 状态**: Phase 0 ✅ / Phase 1 有条件（R1–R3）/ Phase 2 有条件（R4–R6）
**Repo**: github.com/cscoheru/domainAgentECE (main)



