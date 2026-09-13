# Portability（可移植性）

> 原则：第一版只实现 Mock + GleanAdapter 骨架，但架构上避免不可逆锁定。
> 验证顺序与切换成本是本文的核心交付。

## 1. 抽象层

```text
        Domain Product（EvidenceIQ）
                │
        ContextAdapter（接口契约，见 context-adapter.md）
                │
  ┌──────┬──────┬──────┬──────┐
  │      │      │      │      │
Glean   MCP    REST   DB     Mock
(API)  (C/S)  (直连) (只读)  (MVP)
```

## 2. 各后端定位

| 后端 | 阶段 | 覆盖接口 | 成本预估 | 备注 |
|---|---|---|---|---|
| Mock | MVP（现在） | 全部 | — | 内置 Mock Enterprise，接口语义与其他实现完全一致 |
| Glean API | POC | search/get_person/create_task/send_message 优先 | 中 | Client API + Actions（C04/C08/C16）；entity 细节待验证 |
| Glean MCP | POC 备选 | search 等 | 中 | Remote MCP Server 权限感知（C19）；MCP 是通用出口 |
| REST 直连 | 客户无 Glean 时的 POC | search（客户文档库）/get_record（工单系统） | 中-高 | 仅在客户明确无 Glean 时启用 |
| DB 只读 | 评估用 | get_record/metric | 低 | 用客户脱敏快照做评估演示 |

## 3. 防锁定规则

1. Domain 层只 import ContextAdapter 接口类型（CI grep 检查 `glean`/`mcp` 等关键字不得出现在 `src/domain/`）。
2. 适配器工厂在 application 层注入，UI/Agent 不得感知具体后端。
3. Mock 数据 schema 与"规范化企业上下文"对应，不与任何厂商结构耦合。
4. 演示话术对外统一为"Enterprise Context Layer"，客户问起才展开 Glean/直连两种部署路径。

## 4. 切换验收（进入 POC 前跑一遍）

```text
同一次审计准备运行：
  Mock 后端 → 产出 EvidencePack A
  Glean 后端 → 产出 EvidencePack B
验收：A/B 的结构与推理路径一致（证据条目允许不同，推理与缺口逻辑必须一致）
```
