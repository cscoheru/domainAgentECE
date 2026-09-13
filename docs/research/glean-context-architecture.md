# Glean Context Architecture（研究）

> Phase: Gate 1
> Last Verified: 2026-09-03
> 关联证据：C02, C03, C04, C06, C07, C18

## 1. Enterprise Context 是什么

Glean 官方将 "Enterprise Context" 定义为平台的根基能力，由三个概念组成（CONFIRMED，导航原文）：

| 概念 | 官方描述 | 置信度 |
|---|---|---|
| **Enterprise Graph** | 企业级知识图谱（跨系统实体与关系） | CONFIRMED（存在性）；schema 细节 UNKNOWN (C03) |
| **Personal Graph** | 个人级上下文（个人文档、行为、关系） | CONFIRMED（存在性） |
| **System of Context** | 官方新提法：Glean 作为企业的"上下文系统" | CONFIRMED（存在性）；定义细节 UNKNOWN |

核心叙事："Ground AI in company context"（让 AI 接地于公司上下文）+ "agents reason over the knowledge graph"（C18）。

## 2. Context 的来源与治理

```text
275+ Connectors（数据 + 权限实时同步 C06/C07）
        ↓ Indexing（标准/自定义连接器/自定义数据源）
Enterprise Graph（图谱化索引，权限随行）
        ↓
Search / Chat / Assistant / Agents（全部消费同一 Context 层）
```

- 权限是 Context 的一等公民：检索结果按源系统权限过滤（C06）。
- 我们通过 Indexing API 也可以推送**自定义数据源**（如合规控制矩阵），使其进入同一 Context 层（CONFIRMED，Indexing API 存在 Datasources/Custom Metadata 能力）。

## 3. Search 在 Agent 架构中的角色

**结论**：Search 是 Glean 的 **context retrieval service**，服务于人（搜索框）和 Agent（工具调用）两种消费者。它不是独立产品，而是 Context 层的查询接口。

对我们的意义：

- 我们的 `search()` Context Adapter 方法在 Glean 侧天然映射到 Client/Search API（带权限）。
- 引用/接地（citations）由 Search 层提供 → 我们的 Evidence（证据链）可以站在 Glean 引用机制之上，再叠加**领域级证据推理**（Glean 给"文档在哪"，我们判断"证据是否充分、新鲜、覆盖完整"）。

## 4. 关键空白（我们的机会）

1. Glean 理解"文档、人、团队"，但**不理解"审计控制项"、"证据充分性"、"控制责任人"**这类领域语义 —— Domain Ontology 由我们构建。
2. Glean 检索返回"相关文档"，但不做"这组证据能否支撑 CC6.2 控制项通过审计"的推理 —— Domain Reasoning 由我们构建。
3. Glean 不知道"证据缺口应该派给谁、多久补齐" —— Domain Workflow 由我们构建。

## 5. 未验证事项（进入 POC 前必须确认）

| 事项 | 影响 | 状态 |
|---|---|---|
| Enterprise Graph 实体/关系 schema | 决定我们的本体能否映射进图谱 | UNKNOWN (C03) |
| Custom Metadata 能力边界 | 决定控制矩阵能否作为结构化数据源推送 | 部分 CONFIRMED（存在 Custom Metadata API，语义边界 UNKNOWN） |
| Search API 对自定义数据源的支持质量 | 决定控制-证据检索精度 | UNKNOWN |
