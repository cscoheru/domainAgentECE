# Recommended MVP — EvidenceIQ（审计证据智能）

> Phase: Gate 3→4
> 决策记录：ADR-002（为何选它而非分数更高的 RFP 应答）
> 一句话：**把 SOC2 审计准备中的"证据收集与充分性判断"从 3–4 周人工压缩到 3 天，缺口提前 6 周暴露并自动派工。**

## 1. 为什么是它（决策摘要）

1. **Customer Access = 5/5**：GRC/合规/内审/采购人群正是创始人网络 → 2–4 周 5 场访谈可达（用户最高优先级）
2. **WTP = 5/5**：合规预算刚性，"过不了审计"是可量化的商业风险
3. **Domain IP = 5/5**：控制-证据本体 + 四类推理 + 回归评估集 —— 三层可防御资产，Glean 不覆盖（C22/C23）
4. **Glean Fit = 4/5**：证据天然散落 Confluence/Jira/HR/邮箱 —— Context 层完美场景（C04/C06）
5. **不是 RAG 套壳**：核心是充分性/新鲜度/覆盖度推理与缺口派工，检索只是输入
6. **窄而深**：1 Persona / 1 问题 / 1 Workflow / 2 Agents —— 完全符合 PRD #19 的 MVP 上限

## 2. 产品定义

- **Persona**: GRC 合规经理（NimbusWorks 的 Lin Chen，详见 reference-case.md）
- **核心问题**: SOC2 Type II 续证审计在 6 周后开始，本期间（H1/2026）证据必须齐全
- **核心输入**: 审计范围三要素（框架 + 期间 + 系统范围）
- **核心输出**: Audit-Ready Evidence Pack = Evidence Matrix（每控制项：证据+引用+充分性评级）+ Gap List（含责任人+期限）+ 派工回执
- **Business Outcome**: 审计准备 3–4 周 → ≤3 天；缺口暴露提前 4–6 周；单控制项归集 30–60 分钟 → 分钟级

## 3. 与竞品的差异化（诚实版）

| 维度 | Vanta/Drata | 通用 AI 助手 | **EvidenceIQ** |
|---|---|---|---|
| 覆盖控制 | 云/infra 自动化测试 | 无控制概念 | **人工证据类控制（政策/评审/培训/工单）** |
| 证据来源 | 预置 connector | 用户上传文档 | **企业上下文（权限感知检索）** |
| 充分性判断 | 无（通过/未通过测试） | 无 | **覆盖度/新鲜度/类型完整性推理** |
| 缺口处理 | 提醒 | 无 | **归因→责任人→派工→回执闭环** |
| 目标市场 | SMB | 个人 | **中大型企业 + 内审/多框架** |
| 部署形态 | SaaS 独立 | 独立 | **跑在客户 Context 层之上（Glean-ready）** |

## 4. 成功标准（MVP Gate，Gate 4）

- [ ] 15 分钟完整 Demo（含现场发现埋入缺口）
- [ ] 回归集 10–20 案例，五维评分可运行
- [ ] Domain 层零 Glean 依赖（CI 检查）
- [ ] Evidence 每条可溯源（source/url/updatedAt）
- [ ] 缺口识别召回 4/4（Mock 埋入的 4 个缺口全部命中）

## 5. 完成后动作

**STOP 开发，进入客户验证**（Gate 5）：

1. 用 demo-script.md 约谈 5 位 GRC/内审/采购联系人
2. 按 interview-guide.md 记录，按 validation-metrics.md 评估
3. POC 触发条件满足（PRD #28）→ 启动 GleanAdapter 实接
