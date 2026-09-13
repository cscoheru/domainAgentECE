# Evidence Matrix v2 — Glean Architecture Reverse Engineering

> **Phase**: 1 — Evidence Collection
> **Last Updated**: 2026-09-13
> **Status**: ⚠️ **BLOCKED** — All glean.com + developers.glean.com URLs blocked by network policy on 2026-09-13
> **Baseline**: [`/docs/research/evidence-matrix.md`](../research/evidence-matrix.md) (C01–C25, last verified 2026-09-03)
> **PRD Reference**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §4 证据纪律 + §5 种子清单

---

## 0. Phase 1 状态:BLOCKED

### 0.1 网络访问状况

2026-09-13 Phase 1 抓取结果(共尝试 12 个 URL,9 个种子 + 3 个补充):

| URL | 类型 | 抓取状态 |
|---|---|---|
| https://www.glean.com | 产品首页 | ❌ BLOCKED — "Unable to verify if domain www.glean.com is safe to fetch" |
| https://www.glean.com/connectors | 连接器页 | ❌ BLOCKED |
| https://www.glean.com/ai-agent-builder | Agent Builder | ❌ BLOCKED |
| https://www.glean.com/blog/live-fall-25-main | Enterprise Graph 公告 | ❌ BLOCKED |
| https://www.glean.com/blog/introducing-independent-agents | AI coworkers 公告 | ❌ BLOCKED |
| https://www.glean.com/blog/introducing-agent-identity | Agent Identity 公告 | ❌ BLOCKED |
| https://www.glean.com/blog/glean-partner-network | Partner Network 公告 | ❌ BLOCKED |
| https://developers.glean.com | 开发者文档首页 | ❌ BLOCKED |
| https://developers.glean.com/guides/mcp | Remote MCP Server | ❌ BLOCKED |
| https://www.glean.com/partners | Partners 落地页 | ❌ BLOCKED |
| https://www.glean.com/blog/glean-agents-go-2026 | Agents 2026 公告 | ❌ BLOCKED |
| https://www.glean.com/pricing | 定价页 | ❌ BLOCKED |

**结论**: 网络策略屏蔽 claude.ai 对 glean.com 整个域的访问(包括 www 子域、blog 子域)。WebSearch 在 2026-09-13 也返回错误。

### 0.2 处置策略

按 PRD §14(§4 证据纪律延伸)允许显式标 BLOCKED。Phase 1 本轮**未能产出 C35+ 新增证据**,所有 C01-C34 维持 **2026-09-03 v1 baseline 验证日期**。Phase 2 启动前需要解决:

#### 选项 A — 用户代理抓取
用户在本机浏览器手动访问上述 URL,把关键段落/截图贴回给我 → 我整理为 C35+ 证据。

#### 选项 B — 解除网络限制
解除 claude.ai 对 glean.com 域的封锁(若用户有该权限)→ 重跑 Phase 1 抓取。

#### 选项 C — 接受 v1 baseline
v1 证据(C01-C25,2026-09-03 抓取)距今 10 天,在 Glean 没有重大产品线变化的前提下**仍然有效**。Phase 2-6 可基于 v1 baseline 推进,**每个 Capability Matrix 格子显式标注 "Last Verified 2026-09-03 baseline; live re-verify deferred pending network access"**。

#### 选项 D — 暂停 Phase 1
完全暂停,等网络访问恢复后再启动。

**Phase 1 文档本身已完成**(本文件 + README 进度更新),可独立 commit/push 作为诚实的工作记录。

---

## 1. 验证状态图例

- **CONFIRMED**: 官方原文已直接验证(WebFetch 成功)
- **STRONGLY_INFERRED**: 多份官方资料交叉印证,但 v2 重抓未直接验证
- **INFERRED**: 合理推断,无直接证据
- **UNKNOWN**: 无可验证证据;**不得作为设计前提**
- **BLOCKED**: URL 访问被网络策略屏蔽;重试待定
- **BLOCKED_REVERIFY**: v1 baseline 维持有效,但 Phase 1 重抓未成功;后续 Phase 仍依赖原证据
- **INFERENCE_HOLDS**: 推理性证据,无 URL 依赖,无需重抓

---

## 2. v1 证据复核(C01–C25)

> **整体状态**: 维持 v1 baseline(2026-09-03),Phase 1 重抓 BLOCKED。下表为 Phase 1 复核尝试结果。

| # | Claim | Source | v1 Confidence | v2 Last Verified | v2 Status | Notes |
|---|---|---|---|---|---|---|
| C01 | Glean 定位为企业 AI 平台,模块含 Context/Search/Assistant/Agents/Protect/Intelligence | glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 (2026-09-03) 维持 |
| C02 | Enterprise Context 由 Enterprise Graph / Personal Graph / System of Context 构成 | glean.com 首页导航 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C03 | Enterprise Graph 内部 schema 可否自定义/API 读写 | — | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | Robin 会谈必问 Q9 |
| C04 | Search 覆盖 100+ 连接源,ranked、permission-aware | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C05 | 开箱连接器数量 275+ | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C06 | 连接器继承并强制源系统权限 | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C07 | 数据与权限支持实时同步 | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C08 | Actions:跨系统触发操作(写回) | glean.com/connectors FAQ | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C09 | 自定义连接器用 Indexing SDK;自定义 Action 用 OpenAPI;可接 MCP Server | glean.com/connectors | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C10 | Agent Builder 支持 reasoning-based agents + 复杂 workflow | glean.com/product/agents | CONFIRMED (营销级) | 2026-09-13 | **BLOCKED_REVERIFY** | 营销级标注保留 |
| C11 | Agent Builder workflow 细节:分支/循环/人工审批/逐步模型选择 | — | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | Robin 会谈必问 Q10 |
| C12 | Agent Orchestration:事件触发、Agent 间任务路由、连接外部系统 | glean.com/product/agents | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C13 | Agent Governance:rollout / share / certify / 规模化控制 | glean.com/product/agents | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C14 | Agent Observability:adoption、error rates、up/down votes、ROI | glean.com/product/agents | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C15 | Platform API(Agents/Chat/Search/Skills/Triggers)experimental preview | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C16 | Client API 覆盖 Search/Chat/Documents/Entities/Tools/Verification/Insights/Governance | developers.glean.com 导航 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C17 | Agent Toolkit 提供 search/employee_search,适配 LangChain/CrewAI/OpenAI Agents SDK/Google ADK/MCP | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C18 | Glean Agents "reason over the knowledge graph, not just a prompt window" | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C19 | Remote MCP Server:tenant 级、权限感知、OAuth(DCR)、可 MDM 部署 | developers.glean.com/guides/mcp | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C20 | 官方 API 客户端:Python/TypeScript/Java/Go | developers.glean.com 首页 | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C21 | Glean 官方向上做领域模板(8 个销售 Agent 套件) | glean.com/blog | CONFIRMED | 2026-09-13 | **BLOCKED_REVERIFY** | v1 维持 |
| C22 | Glean Agent 观测不含业务正确性/领域推理质量评估 | 推断 | STRONGLY_INFERRED | 2026-09-13 | **INFERENCE_HOLDS** | 推理性证据,无 URL 依赖 |
| C23 | Domain 层是 Glean 未覆盖的空白 | 推断 | STRONGLY_INFERRED | 2026-09-13 | **INFERENCE_HOLDS** | 推理性证据 |
| C24 | Glean 定价模式与最低合同额 | — | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | Robin 会谈必问 Q11 |
| C25 | Glean Agent Harness 与 Glean Transform 能力细节 | glean.com 首页导航 | UNKNOWN | 2026-09-13 | **STILL_UNKNOWN** | 标注 "Coming soon",无详情 |

### 复核统计

| 状态 | 数量 | 含义 |
|---|---|---|
| BLOCKED_REVERIFY | 20 | v1 baseline 维持有效(2026-09-03);Phase 1 重抓未成功 |
| STILL_UNKNOWN | 4 | C03 / C11 / C24 / C25 仍无可验证证据 |
| INFERENCE_HOLDS | 2 | C22 / C23 推理性,无需 URL 重抓 |

**Phase 1 净新增证据**: C35+ = **0**(网络访问受阻)。

---

## 3. Phase 0+ 内部证据(C26–C34)

> 以下条目已在 Phase 0 产出物(`partner-meeting-brief.md` + `research_v2/README.md`)中详细记录。本表作为完整性索引。

| # | Claim | Source | Confidence | Last Verified |
|---|---|---|---|---|
| C26 | Glean Partner Network 于 2026-08-25 公开亮相 | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| C27 | Partner Network 4 pathways: Referral / Commercial / Services & Solutions / Technology | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| C28 | Partner 可在 Build / Sell / Deliver / Operate / Innovate 多个方向参与 | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| C29 | Glean Agent Identity 于 2026 年公开,Agent 可拥有独立 scoped credentials | glean.com/blog/introducing-agent-identity | STRONGLY_INFERRED (BLOCKED) | 2026-09-03 |
| C30 | ECE v0 技术栈:PostgreSQL 16 + pgvector + OpenAI-compatible LLM;无 OpenSearch/Redis/Neo4j | `ece/docs/ADR-009-lean-stack.md` | CONFIRMED | 2026-09-04 |
| C31 | ECE Permission Before Intelligence 是 P2 原则;E2 = 0 是 CI 一票否决门槛 | `ece/docs/ADR-004-permission-first.md` | CONFIRMED | 2026-09-04 |
| C32 | ECE 领域包隔离(ADR-010):换领域包 1-2 周;`src/ece/` 零领域 import | `ece/docs/ADR-010-domain-pack-isolation.md` | CONFIRMED | 2026-09-04 |
| C33 | ECE ADR-006 LLM Provider Independence:OpenAI-compatible 端点;支持 vLLM/Ollama 国产开源 | `ece/docs/ADR-006-llm-independence.md` | CONFIRMED | 2026-09-04 |
| C34 | ECE Sprint 0 已规划 2 天工程地基;Sprint 6 末离线 demo 验收 | `ece/TASKS.md` | CONFIRMED | 2026-09-04 |

---

## 4. Phase 1 本轮新增证据(C35+)

**无新增**。

所有 12 个尝试抓取的 URL 均被网络策略 BLOCKED;v1 baseline(C01-C25)与 Phase 0 内部证据(C26-C34)已穷尽可达范围。

---

## 5. Phase 2 启动条件

Phase 2 (Capability Map)启动前必须解决以下之一:

1. **网络访问恢复** → 重跑 Phase 1,产出 C35+ 新增证据
2. **用户提供关键文本/截图** → 整理为 C35+ 证据
3. **用户接受 v1 baseline** → Phase 2 直接基于 C01-C34 baseline 推进,每个 Capability Matrix 格子显式标注 "Last Verified 2026-09-03 baseline; live re-verify deferred pending network access"
4. **Robin 会谈后** → Phase 2 利用会谈答案填补 C03/C11/C24(必问 3 项)

---

## 6. 治理说明

本文件遵循 PRD §4 证据纪律:

- ✅ 每条 Claim 带 Source / Evidence / Confidence / Last Verified
- ✅ BLOCKED 状态显式标注 + 重试策略记录
- ✅ STRONGLY_INFERRED 与 UNKNOWN 严格区分
- ✅ 不得用 UNKNOWN 作为设计前提
- ✅ 不猜测 Glean 内部实现(仅基于公开资料)
- ✅ v1 文档(`/docs/research/evidence-matrix.md`)**不修改不删除**,作为基线被本文件引用

---

## 7. 下一步动作(待用户决定)

- [ ] **A. 提供关键 URL 文本/截图** → 我整理为 C35+ 证据
- [ ] **B. 解除网络限制后重跑 Phase 1**
- [ ] **C. 接受 v1 baseline** → 推进 Phase 2(每条目显式标注 deferred 状态)
- [ ] **D. 暂停 Phase 1** → 等网络恢复
- [ ] **E. 其它**(用户指定)
