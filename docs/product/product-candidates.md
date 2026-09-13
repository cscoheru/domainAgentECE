# Product Candidates（10 个候选完整评估）

> Phase: Gate 3
> 每候选按 20 维评估；评分（1–5）见 product-ranking.md
> 创始人背景输入（2026-09-03 确认）：人脉主要在 **HR、采购、产品研发、安全合规、财务审计** 等 function 部门

---

## C1. 审计证据智能（SOC2/ISO 审计准备）⭐ 推荐 MVP

- **Target Customer**: 需维持 SOC2 Type II / ISO27001 的中型企业（200–2000 人）；已买 Glean 或有企业搜索的企业加分
- **Buyer**: CISO / 合规总监 / 内审负责人
- **User**: GRC 合规经理、内审专员
- **Pain**: 审计前证据收集 3–4 周；跨系统人工翻政策/工单/HR 记录；反复催控制责任人
- **Current Workflow**: Excel 控制矩阵 + 邮件催收 + 截图归档，现场审计被审计师问倒
- **AI Opportunity**: 检索+本体映射+充分性推理全自动，人工只做确认
- **Domain Intelligence**: 控制-证据本体 + 合格标准知识 + 推理规则
- **Domain Ontology**: ControlItem / EvidenceType / Gap / Owner（见 domain-product-layer.md）
- **Domain Reasoning**: 充分性/新鲜度/覆盖度/归因四类推理
- **Domain Workflow**: Ingest→Map→Retrieve→Reason→Act→Approve→Package
- **Business Outcome**: 审计准备 3–4 周→3 天；缺口提前 4–6 周暴露
- **Glean Fit**: 证据天然散落在 Confluence/Jira/HR/邮件 —— Context 层完美场景（C04/C06）
- **Technical Difficulty**: 3/5（本体与规则是功夫活，非技术难点）
- **Time to MVP**: 3–4 周
- **Demoability**: 4/5（埋缺口→现场发现→派工，戏剧张力强）
- **Commercial Potential**: 高（合规预算刚性；按框架/年订阅心智成熟）
- **Replicability**: 高（SOC2 控制项标准化，跨客户可复用 80%+）
- **Founder Fit**: 4/5（用户具备审计/合规领域知识，能写出专业控制项）
- **Customer Access**: **5/5（安全合规/审计人脉直接可访谈，2–4 周 5 场可达）**
- **Customer Learning Value**: 高（痛点频率高、量化容易、POC 边界清晰）
- **竞争检查**: Vanta/Drata 做 connector 自动化测试（云/infra 控制、SMB 市场）；**人工证据类控制 + 企业上下文证据推理 + 大企业内审/多框架**是空白

## C2. RFP / 投标应答智能（售前）— 战略备选

- **Target Customer**: B2B SaaS / 解决方案商（频繁投标）
- **Buyer**: VP Sales / 售前负责人；**User**: 投标经理 / 售前 SE
- **Pain**: 150–200 题 RFP 3 天截止；安全题反复找安全团队
- **Current Workflow**: 翻历史标书 + 群里求助 + 版本混乱
- **AI Opportunity**: 分类→权限感知检索→起草+引用→Gap→SME 派工
- **Domain Ontology**: 题型分类 / 答案资产 / 合规矩阵 / Gap
- **Domain Reasoning**: 题目分类、答案一致性、缺口路由
- **Business Outcome**: 应答时间 -80%、口径一致性、Gap 提前暴露
- **Glean Fit**: 5/5（权限感知检索安全答案是独门场景）
- **Time to MVP**: 3–4 周；**Demoability**: 5/5
- **Commercial Potential**: 高；**Replicability**: 高
- **Founder Fit**: 2/5（无售前网络）；**Customer Access: 2/5（够不到售前人群）**
- **竞争检查**: Responsive / Loopio / AutogenAI 等成熟玩家
- **结论**: 原始加权分最高（4.25），但按 PRD #17 访问规则降级为战略备选（详见 ADR-002）

## C3. 采购评标 / 供应商智能 — Top 3 #2

- **Target Customer**: 有集中采购部的中大型企业
- **Buyer**: 采购总监；**User**: 采购经理 / 评标委员会
- **Pain**: 5–10 份标书对照加权评分表人工评估；澄清问题来回邮件；比价矩阵手工维护
- **Current Workflow**: Excel 评分表 + 供应商邮件 + 内部专家口头意见
- **AI Opportunity**: 标书解析→逐项对照评标标准→差异矩阵→澄清问题生成→风险提示
- **Domain Ontology**: 评标标准 / 供应商 / 应答项 / 澄清单
- **Domain Reasoning**: 应答符合度、承诺冲突检测、风险归因
- **Business Outcome**: 评标周期 -50%、评估一致性、留痕合规
- **Glean Fit**: 4/5（历史采购+供应商上下文）；**Time to MVP**: 4 周
- **Demoability**: 4/5（并排对比矩阵直观）
- **Commercial Potential**: 中-高；**Replicability**: 高（采购流程标准）
- **Founder Fit**: 4/5；**Customer Access: 5/5（采购人脉直接可访谈）**
- **风险**: 采购 SaaS 竞争（Zycus/Coupa 生态）—— 但 AI 评标推理仍是空白

## C4. 项目健康预警（PMO）— Watchlist

- **Target**: 交付型组织 / 产品研发 PMO；**Buyer**: PMO 总监 / 交付 VP；**User**: 项目经理
- **Pain**: 项目变红才被发现；周报滞后于现实
- **Ontology/Reasoning**: 风险信号本体（进度/范围/资源/依赖/客户信号）+ 多信号融合定级
- **Glean Fit**: 5/5（任务+文档+消息跨源）；**Time to MVP**: 3 周
- **Customer Access**: 3/5（产品研发网络可触达 PMO，但非直接）；竞争中等（Height 等）
- **结论**: 加权分 3.85，学习价值高，作为第二优先验证对象

## C5. 支持工单升级分析 — 备选

- **Target**: B2B SaaS 客服/技术支持；**Buyer**: 支持总监；**User**: 升级经理
- **Pain**: P1 升级时跨系统拼现场（工单+部署记录+近期变更+客户上下文）
- **Glean Fit**: 5/5；**Time to MVP**: 4 周；**Customer Access**: 2/5（无客服网络）→ 降级

## C6. 管理层经营评审（QBR/MBR）— 备选

- **Target**: 中型企业高管层；**Buyer**: CEO/COO；**User**: 商业分析/PMO
- **Pain**: 每季度 1–2 周准备评审材料
- **Demoability**: 5/5（自动生成评审包很惊艳）；**Time to MVP**: 5/5 难（指标口径跨系统混乱）
- **WTP**: 3/5（难挂预算）；**Customer Access**: 2/5 → 降级

## C7. 咨询项目知识复用 — 条件性备选

- **Target**: 咨询/专业服务公司；**Buyer**: 知识管理合伙人；**User**: 顾问
- **Pain**: 提案/交付物重复造轮子，知识在个人电脑里
- **Glean Fit**: 5/5；**Customer Access**: 2/5（用户无咨询网络）→ 降级

## C8. 工程事故复盘 — 备选

- **Target**: 技术组织 SRE/工程效率；**Glean Fit**: 5/5；**Customer Access**: 3–4/5（产品研发网络）
- **Pain 真实但 WTP 中等**（3/5）；Time to MVP 4 周 → Watchlist #2

## C9. 合规问卷双向往来（TPRM）— 潜在扩展

- 与 C1 同本体家族：安全问卷的"收到（评估供应商）+ 发出（回答客户）"双向场景
- **作为 C1 的第二阶段扩展记录在案**，不单独立项（避免第一版发散）

## C10. HR 入职知识问答 — 淘汰

- Glean Assistant 原生覆盖（C10/C21 领域模板风险直接命中）；WTP 2/5 → 淘汰

---

淘汰/降级规则依据：CLAUDE.md Gate 3 + PRD #17（无法 2–4 周获得访谈的候选降级）。
