# Glean Governance（研究）

> Phase: Gate 1
> Last Verified: 2026-09-03
> 关联证据：C06, C07, C13, C19

## 1. 权限（Permissions）

| 问题 | Glean 的回答 | 置信度 |
|---|---|---|
| 权限模型？ | 继承并强制源系统 ACL（"inherits and enforces source-system permissions"） | CONFIRMED (C06) |
| 权限更新时效？ | 实时同步（数据与权限变更即时反映） | CONFIRMED (C07) |
| 检索是否权限过滤？ | 是，Search/Chat/Agents 均权限感知 | CONFIRMED (C04/C18) |
| MCP 出口是否权限感知？ | 是，Remote MCP Server "tenant-specific and permission-aware"，每人用自己的 Glean 访问 | CONFIRMED (C19) |

**对我们的意义**：审计证据场景高度敏感（HR 记录、安全评审、访问日志）——"不同角色看到不同证据"必须成立。MVP 阶段用 Mock Adapter 模拟角色门控；POC 阶段直接继承 Glean 权限，**不自建权限系统**。

## 2. Agent 治理（Agent Governance）

- Rollout / share / certify（发布、共享、认证）机制存在（CONFIRMED C13）。
- Admin 可控制 MCP 开关、DCR 白名单、MDM 部署（CONFIRMED C19）。
- **UNKNOWN**：Agent 审批流（人工 approval step）具体能力（C11 关联）。

## 3. 安全与合规

- 产品模块：Glean Protect（"Safely scale AI at work"）—— CONFIRMED 存在，内部能力（DLP、数据驻留、审计日志细节）未逐项验证。
- Trust Portal 存在（官网页脚链接）。
- **结论**：安全合规叙事上"Glean 已覆盖平台层"，我们的产品文档只需声明"继承底层平台治理"，把开发资源留给 Domain 层。

## 4. 我们必须自己做的治理（薄层）

即使 Glean 覆盖平台治理，产品仍需：

1. **领域级授权语义**：哪个控制项的证据允许哪类角色看（领域规则，不是系统 ACL）。
2. **人工审批点**：Evidence Pack 提交给审计师前的合规经理确认（workflow 步骤，非平台功能）。
3. **审计追踪（领域事件）**：Agent 做了什么判断、依据什么证据 → 供客户内审回溯。

以上三点是 Domain Workflow 的一部分，薄实现即可（MVP：日志 + 状态字段）。
