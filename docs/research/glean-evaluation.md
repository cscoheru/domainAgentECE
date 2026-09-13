# Glean Evaluation（研究）与两层评估结论

> Phase: Gate 1
> Last Verified: 2026-09-03
> 关联证据：C14, C22

## 1. Glean 自带的评估/观测能力

| 维度 | Glean 提供 | 置信度 |
|---|---|---|
| Agent 采纳率 | adoption 指标 | CONFIRMED (C14) |
| Agent 错误率 | error rates | CONFIRMED (C14) |
| 用户反馈 | upvotes / downvotes | CONFIRMED (C14) |
| ROI | ROI 视图 | CONFIRMED（营销级） |

## 2. Glean 不提供的（= 我们的机会）

Glean observability 的全部指标都是**平台健康度**指标。以下维度公开资料中完全缺失（STRONGLY_INFERRED，C22）：

- 业务正确性（这个证据包能否通过审计？）
- 领域推理质量（充分性判断是否专业？）
- 决策质量（缺口该派给谁的判断对不对？）
- 业务结果（审计准备时间是否下降？发现缺口的提前期？）

## 3. 两层评估框架（结论：验证了"第二层是长期 IP"的判断）

### Layer 1: Platform Evaluation（薄实现，够用即可）

- Retrieval 命中率（Mock 阶段：检索命中目标文档的比例）
- Tool 成功率（create_task 等调用成功率）
- 运行时长 / 错误率
- 实现：运行日志 + 简单统计，不建评估平台

### Layer 2: Domain Evaluation（重点投入，形成 IP）

以审计证据场景为例，构建**回归测试集**（10–20 个案例）：

```text
Case: CC6.2 访问评审控制项
Input: 审计期间 H1/2026 + NimbusWorks mock 数据
Expected: 识别 3 份证据中 1 份过期；判定 partial coverage；缺口派给 IT 负责人
Score 维度: 业务正确性 / 推理质量 / 证据引用正确性 / 行动正确性
```

评估维度：业务正确性、推理质量、证据质量、行动正确性、业务有用性。

**判断依据**：

1. Glean 明确只做平台指标（C14）；
2. Domain 评估集 = 领域知识沉淀（每个测试案例都是审计专家知识）；
3. 评估集是可复制、可销售（POC 验收标准）、可防御的资产；
4. 平台若向上侵蚀，会提供"跑 Agent 的地方"，但**不会替我们知道"什么是好的审计证据"**。

## 4. MVP 落地

- `evaluation/cases/*.json`：每个案例含 Input / Expected Behavior / Expected Output / Criteria。
- 运行脚本输出 Score 报告（accuracy / reasoning / evidence / action / usefulness 五维）。
- 每次修改 Domain 规则必须跑回归 → 这是我们的"领域 CI"。
