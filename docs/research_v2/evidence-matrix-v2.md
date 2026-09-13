# Evidence Matrix v2 — Glean Architecture Reverse Engineering

> **Phase**: 1 — Evidence Collection
> **Last Updated**: 2026-09-13 (Cline 红队审查后更新)
> **Status**: ⚠️ PARTIAL — claude.ai WebFetch 工具特定限制(非网络封锁);Cline 备用通道 2026-09-13 独立验证 6 个种子 URL 并带回 C35-C42
> **Baseline**: [`/docs/research/evidence-matrix.md`](../research/evidence-matrix.md) (C01–C25, last verified 2026-09-03)
> **PRD Reference**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §4 证据纪律 + §5 种子清单

---

## 0. 状态复核(2026-09-13 更新后)

### 0.1 网络访问状况(claude.ai 工具特定限制)

2026-09-13 我(Claude/claude.ai)的 WebFetch 对 glean.com + developers.glean.com 返回 "Unable to verify if domain" — 这是 **claude.ai WebFetch 的域安全策略**,**不是网络层屏蔽**。WebSearch 也返回错误。

**Cline 红队审查(2026-09-13)使用备用抓取通道,对其中 6 个种子 URL 全部验证成功**,带回 C35-C42 八条新证据(详见 §4)。

| 通道 | URL 数 | 结果 |
|---|---|---|
| claude.ai WebFetch | 12 | 全部 BLOCKED(**工具特定**) |
| Cline 备用通道 | 6 | 全部成功(带回 C35-C42) |

### 0.2 处置策略

用户原始决策:Option C(接受 v1 baseline,Phase 2 推进)。该决策**基于不完整信息**(当时不知道 claude.ai WebFetch 是工具特定限制,也不知道 Cline 备用通道可行)。

**补救结果**:Cline 已独立带回 C35-C42 八条新 CONFIRMED 证据,直接登记进 §4。Phase 2 capability matrix v2 已用 C35-C42 部分更新(M04/M05/M08/capability-matrix);剩余对 Phase 3/4/5 的影响在对应阶段处理。

---

## 1. 验证状态图例

- **CONFIRMED**: 官方原文已直接验证(WebFetch 成功)
- **STRONGLY_INFERRED**: 多份官方资料交叉印证,但 v2 重抓未直接验证
- **INFERRED**: 合理推断,无直接证据
- **UNKNOWN**: 无可验证证据;**不得作为设计前提**
- **BLOCKED_REVERIFY**: v1 baseline 维持有效,但 Phase 1 claude.ai WebFetch 工具 BLOCKED;后续 Phase 仍依赖原证据(可由 C35-C42 等新证据增强)
- **REVERIFIED**: v1 证据由新近抓取的更新条目(如 C35)再次验证
- **PARTIALLY_ANSWERED**: 仍部分 UNKNOWN,但已有新证据(C37 等)部分解答
- **INFERENCE_HOLDS / INFERENCE_TIGHTENED**: 推理性证据;后者表示被新证据(C38)收紧措辞
- **SUPERSEDED**: 被新近 C 编号(如 C29 被 C36)取代

---

## 2. v1 证据复核(C01–C25)

> **整体状态**: 大部分维持 v1 baseline(2026-09-03);C15 由 C35 复核;C11 由 C37 部分解答;C22 措辞按 C38 收紧。下表为 Phase 1 + Cline 红队审查后状态。

| # | Claim | Source | v1 Confidence | v2 Last Verified | v2 Status | Notes |
|---|---|---|---|---|---|---|
| C01 | Glean 定位为企业 AI 平台,模块含 Context/Search/Assistant/Agents/Protect/Intelligence | glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 (2026-09-03) 维持 |
| C02 | Enterprise Context 由 Enterprise Graph / Personal Graph / System of Context 构成 | glean.com 首页导航 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C03 | Enterprise Graph 内部 schema 可否自定义/API 读写 | — | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | Robin 会谈必问 Q9 |
| C04 | Search 覆盖 100+ 连接源,ranked、permission-aware | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C05 | 开箱连接器数量 275+ (来自 connectors FAQ;首页写 "more than 250" — 两处口径并存,保留 C05) | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C06 | 连接器继承并强制源系统权限 | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C07 | 数据与权限支持实时同步 | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C08 | Actions:跨系统触发操作(写回) | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C09 | 自定义连接器用 Indexing SDK;自定义 Action 用 OpenAPI;可接 MCP Server | glean.com/connectors | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C10 | Agent Builder 支持 reasoning-based agents + 复杂 workflow | glean.com/product/agents | CONFIRMED (营销级) | 2026-09-13 | **BLOCKED_REVERIFY** | 营销级标注保留 |
| C11 | Agent Builder workflow 细节:分支/循环/人工审批/逐步模型选择 | — | UNKNOWN | 2026-09-13 | **PARTIALLY_ANSWERED** (C37) | C37: agent looping=beta; schedule agents=GA; agent version control=GA; conversational builder=beta. branching/HITL/per-step model 仍 UNKNOWN; Robin Q10 补 |
| C12 | Agent Orchestration:事件触发、Agent 间任务路由、连接外部系统 | glean.com/product/agents | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C13 | Agent Governance:rollout / share / certify / 规模化控制 | glean.com/product/agents | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C14 | Agent Observability:adoption、error rates、up/down votes、ROI | glean.com/product/agents | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C15 | Platform API(Agents/Chat/Search/Skills/Triggers)experimental preview | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **REVERIFIED by C35** | C35 引文(2026-09-13 Cline 独立通道): "Build search experiences and run Glean agents in your applications with our new Platform APIs — now rolling out in experimental preview." |
| C16 | Client API 覆盖 Search/Chat/Documents/Entities/Tools/Verification/Insights/Governance | developers.glean.com 导航 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | Cline 抓取发现 Client API 目录比 v1 C16 更宽:含 Activity / Announcements / Answers / Collections / Messages / Pins / Shortcuts / Summarize(详见 §4 附带观察) |
| C17 | Agent Toolkit 提供 search/employee_search,适配 LangChain/CrewAI/OpenAI Agents SDK/Google ADK/MCP | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C18 | Glean Agents "reason over the knowledge graph, not just a prompt window" | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C19 | Remote MCP Server:tenant 级、权限感知、OAuth(DCR)、可 MDM 部署 | developers.glean.com/guides/mcp | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持;C37 确认 remote MCP servers beta |
| C20 | 官方 API 客户端:Python/TypeScript/Java/Go | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C21 | Glean 官方向上做领域模板(8 个销售 Agent 套件) | glean.com/blog | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C22 | Glean Agent 观测不含**领域正确性/业务推理质量**评估 | 推断 + C38 收紧 | STRONGLY_INFERRED (C38) | 2026-09-13 | **INFERENCE_TIGHTENED** | C38 引文(2026-09-13): "Permission rules and policies apply on every request, while logs and evaluations provide visibility into execution paths and performance." — execution-path/performance 评估 ≠ domain correctness 评估;结论方向保留但措辞收紧 |
| C23 | Domain 层是 Glean 未覆盖的空白 | 推断 | STRONGLY_INFERRED | 2026-09-13 | **INFERENCE_HOLDS** | 推理性证据 |
| C24 | Glean 定价模式与最低合同额 | — | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | Robin 会谈必问 Q11 |
| C25 | Glean Agent Harness 与 Glean Transform 能力细节 | glean.com 首页导航 | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | C41: Harness 已入 PRODUCT 导航但无详情页;Transform 仍标 "Coming soon";Robin Q10/Q11 补 |

### 复核统计

| 状态 | 数量 | 含义 |
|---|---|---|
| BLOCKED_REVERIFY | 18 | v1 baseline 维持有效(2026-09-03);claude.ai WebFetch 工具 BLOCKED |
| REVERIFIED | 1 | C15 由 C35 再次验证 |
| PARTIALLY_ANSWERED | 1 | C11 由 C37 部分解答 |
| STILL_UNKNOWN | 3 | C03 / C24 / C25 仍无可验证证据 |
| INFERENCE_TIGHTENED | 1 | C22 由 C38 收紧措辞 |
| INFERENCE_HOLDS | 1 | C23 推理性,无需 URL 重抓 |

**Phase 1 + Cline 红队补充 净新增证据**: C35-C42 = **8 条**(详见 §4)。

---

## 3. Phase 0+ 内部证据(C26–C34)

> 以下条目已在 Phase 0 产出物(`partner-meeting-brief.md` + `research_v2/README.md`)中详细记录。本表作为完整性索引。

| # | Claim | Source | Confidence | Last Verified |
|---|---|---|---|---|
| **C26** | Glean Partner Network 博客存在性(**拆分**:存在性 CONFIRMED;2026-08-25 日期保留 v1 草稿口径) | glean.com/blog/glean-partner-network (Cline 独立通道 2026-09-13 确认存在性;发布日期字段未捕获) | **拆分**: 存在性 CONFIRMED / 日期 INFERRED | 2026-09-13 |
| C27 | Partner Network 4 pathways: Referral / Commercial / Services & Solutions / Technology | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| C28 | Partner 可在 Build / Sell / Deliver / Operate / Innovate 多个方向参与 | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| **C29** | Glean Agent Identity 于 2026 年公开,Agent 可拥有独立 scoped credentials | glean.com/blog/introducing-agent-identity | **SUPERSEDED by C36** | 2026-09-13 |
| C30 | ECE v0 技术栈:PostgreSQL 16 + pgvector + OpenAI-compatible LLM;无 OpenSearch/Redis/Neo4j | `ece/docs/ADR-009-lean-stack.md` | CONFIRMED | 2026-09-04 |
| C31 | ECE Permission Before Intelligence 是 P2 原则;E2 = 0 是 CI 一票否决门槛 | `ece/docs/ADR-004-permission-first.md` + `ece/docs/EVALUATION.md` §1 | CONFIRMED | 2026-09-04 |
| C32 | ECE 领域包隔离(ADR-010):换领域包 1-2 周;`src/ece/` 零领域 import | `ece/docs/ADR-010-domain-pack-isolation.md` | CONFIRMED | 2026-09-04 |
| C33 | ECE ADR-006 LLM Provider Independence:OpenAI-compatible 端点;支持 vLLM/Ollama 国产开源 | `ece/docs/ADR-006-llm-independence.md` | CONFIRMED | 2026-09-04 |
| C34 | ECE Sprint 0 已规划 2 天工程地基;Sprint 6 末离线 demo 验收 | `ece/TASKS.md` | CONFIRMED | 2026-09-04 |

---

## 4. 2026-09-13 补充证据(Cline 独立通道)

> **来源标注规范**: `Source` 列统一写 `URL (independently fetched by Cline, 2026-09-13)`。引文为官方页面原文,未改写。

| # | Claim | Source | Evidence(原文引文) | Confidence | Last Verified |
|---|---|---|---|---|---|
| **C35** | Platform API(Agents/Chat/Search/Skills/Triggers)仍为 experimental preview(复核 C15) | developers.glean.com (independently fetched by Cline, 2026-09-13) | "Build search experiences and run Glean agents in your applications with our new Platform APIs — now rolling out in experimental preview." | CONFIRMED | 2026-09-13 |
| **C36** | Agent Identity:scoped service credentials + 审计归属 agent 自身账户 + admin 可轮换/吊销;状态 **beta**(升级 C29) | glean.com/blog/introducing-agent-identity (independently fetched by Cline, 2026-09-13) | "agents act through their own scoped service credentials — visible in the audit trail, and governed by the people responsible for governing access: admins can rotate or revoke any credential, for one system or all of them, at any time." / "Every action lands in the audit trail under the agent's own account, with the person or schedule that triggered it recorded alongside." / "The feature is now available in beta for our Glean customers." | CONFIRMED | 2026-09-13 |
| **C37** | Glean:LIVE Fall'25 官方可用性矩阵(部分解答 C11;细化 C19) | glean.com/blog/live-fall-25-main (independently fetched by Cline, 2026-09-13) | "Generally available: Enterprise Graph, personal graph, Agentic Engine 2 (Assistant only), third-generation Glean Assistant, Deep Research*, all knowledge queries, fast and extended thinking modes, contextual image understanding, schedule agents*, agent version control, agents respond to user inputs, featured agents, enhanced Chat API (Agentic Engine 2)*." / "Beta: Personalized writing, conversational agent builder, agent looping, Assistant routes requests to agents automatically, agents toolkit, and remote MCP servers." / "Coming soon: Glean Canvas, 100+ new actions, Agents (Agentic Engine 2), LLM model choice in Assistant, and an MCP directory." | CONFIRMED | 2026-09-13 |
| **C38** | Agent Builder 治理文案出现 "evaluations" 一词(指向执行路径与性能)— **收紧 C22 措辞的依据** | glean.com/ai-agent-builder FAQ (independently fetched by Cline, 2026-09-13) | "Permission rules and policies apply on every request, while logs and evaluations provide visibility into execution paths and performance." | CONFIRMED | 2026-09-13 |
| **C39** | Glean 官方运营开发者文档 MCP server,官方支持 Claude Code / Cursor / Codex / Gemini CLI 等 IDE 接入(强化 M08 "IDE 集成"行) | developers.glean.com (independently fetched by Cline, 2026-09-13) | "Bring Glean to your IDE — Claude Code, Cursor, Codex, and any MCP host." + `claude mcp add glean-developer-docs https://developers.glean.com/mcp --transport http --scope user` | CONFIRMED | 2026-09-13 |
| **C40** | 鉴权模式:OAuth 优先(per-user Client/Platform),Glean-issued token 用于 Indexing / global **ActAs**(M04 代理身份相关) | developers.glean.com Quickstart (independently fetched by Cline, 2026-09-13) | "Prefer OAuth for per-user Client and Platform work in Authentication. Use a Glean-issued token for Indexing, global ActAs, or when no OAuth path exists." | CONFIRMED | 2026-09-13 |
| **C41** | Agent Harness 已进入 glean.com 页脚 PRODUCT 导航(仍无详情页);Transform 导航仍标 "Coming soon"(细化 C25) | glean.com (independently fetched by Cline, 2026-09-13) | 页脚 PRODUCT 列表含 "…Agent Library Agent Harness Enterprise Context…";主导航 "Coming soon — Glean Transform" | CONFIRMED | 2026-09-13 |
| **C42** | 市场语境:Gartner 新兴市场象限 "Market Shaper"(No-Code Agent Builders);官方竞品对比页(vs ChatGPT Enterprise / M365 Copilot / Claude Enterprise) | glean.com (independently fetched by Cline, 2026-09-13) | "Glean Named a Market Shaper in the Gartner Emerging Market Quadrant for No-Code Agent Builders";COMPARISONS 导航三页 | CONFIRMED | 2026-09-13 |

**附带观察**(并入相应模块即可,不单独立 C 编号):

1. 首页导航连接器口径为 "more than 250"(v1 C05 的 275+ 来自 connectors FAQ——两处官方口径并存,保留 C05 并加注)。
2. developers.glean.com 新增 "Cookbooks — Recipes: Runnable patterns that go from problem to working demo to scaffolded starter code — auth and permissions laid out for each"(Partner enablement 信号,Q6 可引用)。
3. Web SDK:"one npm package, two components"(renderSearchBox / renderChat)。
4. Client API 目录比 v1 C16 更宽:含 Activity / Announcements / Answers / Collections / Messages / Pins / Shortcuts / Summarize。

---

## 5. 复核状态(2026-09-13 更新后)

| 项 | 状态 |
|---|---|
| 用户决策 | Option C 接受 v1 baseline,Phase 2 已完成(commit 9f3a5cb) |
| Phase 1 网络限制 | claude.ai WebFetch 工具特定限制,非网络封锁;Cline 备用通道 2026-09-13 已验证 6 URL,带回 C35-C42 |
| 待 Phase 1 复核的 UNKNOWN | C03/C11/C24/C25 → C11 已由 C37 部分解答;C03/C24/C25 仍待 Robin 会谈(详见 `partner/questions-for-glean.md` Q9/Q10/Q11) |
| 下一步 | Phase 3 — Architecture Reconstruction(需用户确认) |

---

## 6. 治理说明

本文件遵循 PRD §4 证据纪律:

- ✅ 每条 Claim 带 Source / Evidence / Confidence / Last Verified
- ✅ BLOCKED / BLOCKED_REVERIFY / REVERIFIED / PARTIALLY_ANSWERED / INFERENCE_TIGHTENED 等状态显式标注
- ✅ STRONGLY_INFERRED 与 UNKNOWN 严格区分
- ✅ 不得用 UNKNOWN 作为设计前提
- ✅ 不猜测 Glean 内部实现(仅基于公开资料)
- ✅ v1 文档(`/docs/research/evidence-matrix.md`)**不修改不删除**,作为基线被本文件引用
- ✅ Cline 红队报告 §2 提供的 C35-C42 八条证据,引文**未改写**,原样登记

---

## 7. 下一步:Phase 3 — Architecture Reconstruction

按 `RESEARCH_PRD_V2.md` §9 Phase 3 DoD:

1. 分层架构重建:**官方明确描述的架构** 与 **公开资料推导的架构** 分开成图,逐层标注证据
2. 产出 G/O/P/? 大图(§8)+ mermaid 入 `/docs/diagrams/platform-kernel-architecture.mmd` + `glean-layers-v2.mmd`
3. DoD: 图上每层可追溯;推导处标 INFERRED 及依据;**C35-C42 新证据可在图上引用**

Cline 红队报告(commit 040c04e)已签发 Phase 2 验收通过(条件:R1-R7 全部完成)。完成 R1-R7 后用户授权即可启动 Phase 3。
