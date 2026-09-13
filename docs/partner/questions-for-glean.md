# Questions for Glean Partner Manager (Robin, Asia Channel Ecosystem)

> **Phase**: 0 — Partner 会谈准备
> **Last Updated**: 2026-09-13
> **Format**: 14 个问题,按优先级排序;每题含 Question / Why Ask / What We Hope to Learn / Red Line / Evidence Ref
> **上游**: `RESEARCH_PRD_V2.md` §6 M09 + Phase 0 DoD 必问清单

---

## 使用规则

1. **优先问开放性问题**,不要引导 Robin 给我们想要的答案
2. **关键问题至少给 Robin 10 秒回答时间**,不要替他说
3. **听到"不"也要微笑**,记录答案即可;3 个必问答案"不" → 优雅退出
4. **不确定答案时追问具体案例**, 例: "Can you give me an example of..."

---

## Q1 — Glean 的中国/亚洲市场战略

> **Question**: How is Glean thinking about the China and broader Asia market at the moment?

**Why ask**: 路径级判断。v3 Red Team U-G1 已确认可达市场在中国大陆无 Glean 客户,但 Glean 自身是否有进入意图 / 时间表 / 路径未明。

**What we hope to learn**:
- Glean 是否有专门的中国/亚洲市场策略
- 是否有专门负责 Asia channel 的人(Robin 的角色范围)
- 中国/亚洲在 Glean 全球版图的优先级

**Red line**: 如果答案是"暂无中国计划且不会短期内进入" → Glean Partner 路径在可达市场价值有限,需强化 Phase 5 Platform Kernel 自建倾向。

**Evidence ref**: C26 (Partner Network launch), C29 (Agent Identity 2026)

---

## Q2 — Glean 现在希望什么类型的 Partner

> **Question**: What type of partners are you currently looking for in Asia? Are you primarily looking for resellers, implementation partners, technology partners, or partners who can build agents and industry solutions?

**Why ask**: 决定我方应该走哪条 pathway(Referral / Commercial / Services & Solutions / Technology)。

**What we hope to learn**:
- Glean 在 Asia 的 partner 组合现状
- 是否接受个人/小团队(无公司主体)
- 是否优先有现成客户的申请者

**Red line**: 如果答案是"只接受有 SaaS 销售团队 + 现有客户漏斗的 Partner" → 我方当前 profile 不匹配,记录并退出。

**Evidence ref**: C27 (4 pathways), C28 (Build/Sell/Deliver/Operate/Innovate)

---

## Q3 — 我方的 profile 适合哪条路线

> **Question**: Based on what I've shared, where do you think I would fit best within the Glean Partner Network?

**Why ask**: 让 Robin 来定位我方,比主动推销更可信。

**What we hope to learn**:
- Glean 视角的"ideal partner profile"
- 与我方(管理咨询 + 工程师 + 中国企业 access)匹配度

**Red line**: 如果 Robin 不能明确指出 pathway → 暗示我方不在 Glean 优先候选名单,记录后决定是否继续。

**Evidence ref**: C27, C28

---

## Q4 — 中国/亚洲大型企业引入 Glean 的最大障碍

> **Question**: From your experience across Asia, what are the biggest barriers you see when introducing Glean into large enterprises?

**Why ask**: 收集一手情报,为我方 POC 准备与主路径 D 决策提供输入。

**What we hope to learn**:
- Security / organizational boundaries / deployment / data sovereignty / IT resistance 的真实优先级
- Glean 在亚洲遇到的具体失败案例(若有)

**Red line**: 不存在 hard red line,所有答案都是有用情报。

**Evidence ref**: 通用 Glean capability map

---

## Q5 — Partner 技术自由度

> **Question**: How much technical freedom do partners have when building custom agents, connectors and integrations around Glean? Can partners build substantial industry-specific solutions on top of Glean?

**Why ask**: 决定我方 Build + Innovate 方向的天花板。若自由度低 → 与我方"领域 Agent 自主 IP"目标冲突。

**What we hope to learn**:
- Agent 定义是否可完全在我方控制下(Agent Definition as Code)
- 是否需要 Glean UI 才能创建/管理 Agent
- MCP / Agent Toolkit / Platform API 的边界

**Red line**: 如果答案是"所有 Agent 必须 Glean UI 创建,Partner 无代码化路径" → 与我方 code-first 工作方式冲突。

**Evidence ref**: C17 (framework-agnostic), C18 (reason over knowledge graph)

---

## Q6 — Glean 对 Partner 的技术支援

> **Question**: If a partner has its own technical capabilities and wants to build custom solutions around Glean, what kind of technical support and enablement does Glean provide? (API / SDK / MCP / Connector / Agent Builder / Technical Support / Sandbox / Partner Enablement)

**Why ask**: 评估 onboarding 难度与 Partner 经济学。

**What we hope to learn**:
- Sandbox 环境是否可用
- 技术 support channel(Slack / 邮件 / Partner success manager)
- 是否提供 go-to-market 支援(联合销售 / co-marketing)

**Red line**: 如果答案是"自助 + 文档为主,无 dedicated support" → 时间成本需重估。

**Evidence ref**: C16, C17, C19; also: developers.glean.com 新增 **"Cookbooks — Recipes: Runnable patterns that go from problem to working demo to scaffolded starter code — auth and permissions laid out for each"**(Cline 2026-09-13 验证) — **Partner enablement 信号**,值得直接问:Cookbooks 是否会开放 Partner 参与贡献?

---

## Q7 — Partner 的商业模式

> **Question**: How do successful partners typically build their business with Glean? Is the main opportunity software resale, implementation services, managed services, custom solutions, or a combination?

**Why ask**: 商业可行性验证。

**What we hope to learn**:
- 是否接受 Services & Solutions-led 模式(我方首选)
- Partner 抽成 / 注册机会 / 联合销售机制
- 与 Glean first-party 产品(垂直 Agent 模板)的竞争边界

**Red line**: 如果答案是"以 resale 为主,服务性 Partner 经济上不可行" → 不签。

**Evidence ref**: C21 (Glean 自己做领域模板 → first-party 竞争风险)

---

## Q8 — 下一步

> **Question**: If we think there is a good fit, what would you suggest as the next step?

**Why ask**: 关闭会谈,确定具体 follow-up。

**What we hope to learn**:
- Partner application 流程时长
- 是否需要提交正式 partner proposal
- 下一次 call 的可能议程(demo / technical deep dive / customer intro)

**Red line**: 如果 Robin 不能给具体 next step → 信号偏弱,可保留期权但不投入额外动作。

**Evidence ref**: N/A

---

## Q9 — Enterprise Graph schema 与可扩展性(对应 v1 C03 UNKNOWN)

> **Question**: For partners building domain-specific ontologies (e.g., audit/compliance control-evidence mappings), can the Enterprise Graph schema be customized or extended via API? Can partners read/write entity and relationship types?

**Why ask**: C03 是 v1 UNKNOWN 项,决定我方 Domain Ontology 能否映射进 Glean 图谱。

**What we hope to learn**:
- Enterprise Graph 是否暴露 schema API
- Custom entity/relationship types 的支持程度
- Indexing API 是否可用于推送自定义数据源

**Red line**: 如果答案是"schema fixed,不支持自定义" → Domain Ontology 必须自建,Glean 图谱仅为检索载体。

**Evidence ref**: C03 (UNKNOWN)

---

## Q10 — Agent Builder workflow 细节(对应 v1 C11 UNKNOWN)

> **Question**: For partners building complex workflow agents (with branching, looping, human approval steps, per-step model selection), can you share the Agent Builder workflow specification — particularly how branching and human-in-the-loop are expressed?

**Why ask**: C11 是 v1 UNKNOWN 项;**C37(Cline 2026-09-13) 已部分解答** — Fall'25 矩阵列出 agent looping=beta、schedule agents=GA、agent version control=GA、conversational agent builder=beta。**仍需 Robin 回答**:branching 复杂条件分支、HITL 人工审批步骤、per-step model selection 详细机制。决定我方 Agent Runtime 与 Glean Agent Builder 的边界。

**What we hope to learn**:
- Agent workflow 是否支持 branching / looping
- Human approval 步骤的实现方式
- Per-step model selection 是否支持

**Red line**: 不存在 hard red line,信息仅供 Phase 5 Platform Kernel 决策。

**Evidence ref**: C11 (UNKNOWN), C21 (vertical templates)

---

## Q11 — Glean 定价模式与 Partner 商务条款(对应 v1 C24 UNKNOWN)

> **Question**: What's Glean's pricing model and minimum contract size? How does partner economics work — referral fees, revenue share, or discount structure? Are there minimum annual commitments for partners?

**Why ask**: C24 是 v1 UNKNOWN 项,商业可行性核心。

**What we hope to learn**:
- 客户合同金额区间
- Partner 抽成比例
- 是否有年度最低要求

**Red line**: 如果最低合同 > $100K USD / 年 且 Partner 抽成 < 10% → 主路径 D 价值更高。

**Evidence ref**: C24 (UNKNOWN)

---

## Q12 — Agent 定义 API 化程度

> **Question**: How much of agent definition can be created and managed outside of the Builder UI — via Platform API or as-code definitions? Can partners use tools like Claude Code or Cursor to author agents, with Glean providing the runtime?

**Why ask**: 与我方 code-first 工作方式匹配度。**已知(C37)** — 部分 agent features(agent version control、schedule agents) 已 GA,部分(conversational builder) 仍 beta。Agent Definition 的边界已部分可观察;**Partner 视角** 需要知道:哪些 GA 能力已开放 Partner 自定义,哪些仍只走 Glean UI。

**What we hope to learn**:
- Agent Definition as Code 的支持程度
- Platform API 对 agent lifecycle 的覆盖(create / update / version / deploy)
- IDE 集成的可能性

**Red line**: 如果答案是"所有东西必须在 Glean UI 中" → 我方工作方式不匹配。

**Evidence ref**: C15 (Platform API experimental), C17 (framework-agnostic)

---

## Q13 — 中国区部署与数据主权立场

> **Question**: For large Chinese enterprises with strict data sovereignty requirements (private deployment, no data leaving the domain), does Glean support a private deployment model? What's Glean's position on data sovereignty in the China context?

**Why ask**: 中国大型企业的硬需求,决定路径可行性。

**What we hope to learn**:
- 是否提供 private deployment 版本
- 是否支持 BYOK (Bring Your Own Key) / BYOL (Bring Your Own LLM)
- 中国大陆数据中心的可用性

**Red line**: 如果答案是"仅 SaaS,无 private deployment" → 中国大型企业不可达,Glean 路径在可达市场失效,回到主路径 D。

**Evidence ref**: 通用(无具体 Glean 公开声明支持/反对 private deployment)

---

## Q14 — Platform API GA 时间表

> **Question**: When do you expect Platform API (Agents / Chat / Search / Skills / Triggers) to graduate from experimental preview to GA? What's the SLA target?

**Why ask**: **C15 → C35(Cline 2026-09-13 独立通道再验证)** 仍标 experimental preview,我方若依赖 Platform API 构建长期方案,需要 GA 承诺与 breaking change 政策。Robin 的 "experimental" 持续时间预期是关键信号 — 已知 platform API 涉及 Agents/Chat/Search/Skills/Triggers(C15/C35),GA 时间表决定我方是否能以此为长期基础。

**What we hope to learn**:
- GA 时间表(具体日期或季度)
- GA 前的 SLA / 兼容性承诺
- breaking change 政策

**Red line**: 如果"experimental" 状态将持续 > 12 个月 → 不应以 Platform API 为核心依赖。

**Evidence ref**: C15 (Platform API experimental)

---

## 收尾:Concrete Next Step

不管上面答案如何,会谈结束时尝试锁定一个具体动作:

> "Can we identify one concrete customer opportunity — perhaps a joint introduction to a prospect who's already evaluating Glean or considering a Chinese enterprise AI platform — and explore how we could work together?"

**判断标准**:
- ✅ Robin 同意 → 进入 Partner application / 联合客户探索
- ⚠️ Robin 模糊 → 记录 + 等邮件 follow-up
- ❌ Robin 拒绝 → 优雅退出,启动主路径 D

---

## 优先级排序(通话时间不足时使用)

### 必问(30 分钟也不能跳过)

- **Q1** (Asia strategy)
- **Q2** (Partner type)
- **Q3** (Our fit)
- **Q9** (Graph schema / C03)
- **Q11** (Pricing / C24)

### 应问(45 分钟争取)

- **Q5** (Technical freedom)
- **Q6** (Support)
- **Q13** (China deployment)

### 可问(若时间充裕)

- Q4, Q7, Q8, Q10, Q12, Q14
