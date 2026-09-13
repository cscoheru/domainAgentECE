# Agent Runtime（MVP 轻量运行时）

> 决策：MVP 自建**薄** runtime，不引入 Agent 框架，不押注 Glean Agent Builder（C11 UNKNOWN / C15 experimental）。
> 原则：runtime 是"领域工作流的执行器"，本身不是 IP；够用、可观测、可替换。

## 1. 为什么自建薄 Runtime

| 选项 | 判定 | 理由 |
|---|---|---|
| Glean Agent Builder 承载 workflow | ❌ | C11 UNKNOWN，不能作前提；且无法脱离 Glean 租户演示 |
| LangChain / CrewAI 等框架 | ❌ | MVP 工作流是**确定性管道 + 局部 LLM 推理**，框架抽象反而增加调试成本与锁定 |
| 自建 300 行级执行器 | ✅ | 完全可控；每步可观测（reasoning trace）；POC 时可整体迁到 Glean Orchestration |

## 2. 运行时结构

```text
WorkflowEngine（顺序步骤 + 显式状态）
   steps: [ingest, map, retrieve, reason, act, package]
   每步: input → handler(context) → output → trace 事件
Agent（LLM 节点）: prompt 模板 + ontology/knowledge 注入 + 结构化输出校验
ToolCall: 通过 ContextAdapter（唯一出口）
TraceStore: 每步的输入/输出/推理依据（Demo 的 Reasoning 面板直接消费）
```

## 3. Agent 规格（十二要素，MVP 实现标准）

### Control Intake Agent

```yaml
Role: 审计准备助手（控制项解析）
Goal: 把审计范围解析为"控制项 × 证据需求"清单
Context: 审计框架(SOC2) + 期间 + 系统范围（用户输入）
Ontology: ControlItem / EvidenceType / SystemScope（注入）
Knowledge: 每控制项的证据标准（注入）
Tools: [get_entity]（控制框架查询，可选）
Workflow: ingest → map
Reasoning: 控制项拆解 + 证据类型映射（本体驱动，LLM 校验边界）
Guardrails: 只允许输出本体定义过的 EvidenceType；无法识别的控制项标记 NEED_REVIEW 而非臆造
Output: ControlEvidenceRequirement[]（结构化）
KPI: 解析准确率（对照回归集）
```

### Evidence & Gap Agent

```yaml
Role: 证据侦探
Goal: 为每个证据需求找到证据并判定充分性，输出缺口
Context: ControlEvidenceRequirement[] + actingUser（权限）
Ontology: Evidence / EvidenceGap / ActionItem（注入）
Knowledge: 证据合格标准 + 新鲜度/覆盖度规则表
Tools: [search, get_record, get_person, create_task]
Workflow: retrieve → reason → act
Reasoning: 充分性 / 新鲜度 / 覆盖度 / 归因路由（规则优先，LLM 解释）
Guardrails: 证据必须带溯源字段；权限不足时明确提示而非绕过；缺口派工前必须有人工确认点
Output: EvidenceMatrix + GapList + ActionItem[]（结构化）
KPI: 缺口识别召回/精确率（对照回归集埋入的 4 个已知缺口）
```

## 4. 可观测性（薄层）

- TraceStore 记录每步：时间、输入摘要、输出摘要、工具调用、推理依据。
- Demo UI 的 "Reasoning" 面板直接渲染 trace —— 观测即演示。

## 5. LLM 使用边界

- LLM 只用于：非结构化文档理解、边界解释、自然语言输出组织。
- 确定性判断（过期/覆盖不足/类型缺失）用规则代码 —— 可测试、可解释、防幻觉。
- 模型供应商通过环境变量配置（OpenAI 兼容协议），不锁定单一厂商。
