# M09 — Partner Boundary

> **Phase**: 2 — Capability Map(research 视角;会谈行动视角见 `docs/partner/`)
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M09
> **Linked Q**: Q5 (若不用 Glean,我们该做哪层)

## 1. 研究问题

1. Glean Partner Network 五角色(Build / Sell / Deliver / Operate / Innovate)的边界(C28)
2. 三种 Partner competencies(Agent Building / Custom Connectors / Embedded Experiences)的具体含义
3. 我方适合哪种 Partner 角色?
4. Partner 与 Glean 的技术/商务接口
5. v3 Red Team 主路径 D 与 Partner 路径的关系

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C26 | Glean Partner Network 于 2026-08-25 公开亮相 | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) |
| C27 | Partner Network 4 pathways: Referral / Commercial / Services & Solutions / Technology | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) |
| C28 | Partner 可在 Build / Sell / Deliver / Operate / Innovate 多个方向参与 | glean.com/blog/glean-partner-network | STRONGLY_INFERRED (BLOCKED) |
| C21 | Glean 官方向上做领域模板(8 个销售 Agent 套件) | glean.com/blog | CONFIRMED |
| C30 | ECE v0 技术栈(私有化兼容) | `ece/docs/ADR-009-lean-stack.md` | CONFIRMED |
| C31 | ECE Permission Before Intelligence | `ece/docs/ADR-004-permission-first.md` | CONFIRMED |
| C32 | ECE 领域包隔离 | `ece/docs/ADR-010-domain-pack-isolation.md` | CONFIRMED |
| C33 | ECE LLM Provider Independence(开源模型友好) | `ece/docs/ADR-006-llm-independence.md` | CONFIRMED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Partner Network 存在性 | ✓ (C26) | | |
| 5 角色框架 | ✓ (C28) | | |
| 4 pathways | ✓ (C27) | | |
| 3 competencies | ✓ (营销级声明,产品页) | | |
| Glean 自己做领域模板(first-party 竞争风险) | ✓ (C21) | | |
| 我方资产(ECE 技术栈) | ✓ (C30-C33) | | |
| Partner 抽成 / 定价 | | | ✗ (C24) |
| Partner 技术 on-boarding SLA | | | ✗ |
| 客户需求传导机制 | | | ✗ |

## 4. 对 Platform Kernel 的含义

### 4.1 我方 Partner 定位推荐

**Primary**: Services & Solutions + Technology 双轨 Partner,聚焦 Build + Innovate 方向

**详细分析见 `docs/partner/partner-meeting-brief.md` §1**

### 4.2 v3 Red Team 主路径 D 与 Partner 路径的关系

**关键关系**:
- Partner 路径 ≠ 取代主路径 D
- Partner 路径 = **可选双路径**(若 Glean Partner 准入有意义)
- 主路径 D = **基线**(私有化垂直 Context+Agent)

**决策树**:
```
┌────────────────────────────────────────┐
│ Robin 会谈后:                          │
├────────────────────────────────────────┤
│ 若 Partner 准入有意义                  │
│   → 双路径并行                         │
│   → ECE + Glean Adapter(Phase 4 决策)  │
│                                        │
│ 若 Partner 实质受阻                    │
│   → 回归主路径 D                       │
│   → 全部自建 + 私有化部署              │
└────────────────────────────────────────┘
```

### 4.3 我方独特资产(Glean 不能从 Partner 处拿到的)

| 资产 | 价值 | Glean 是否能做 |
|---|---|---|
| **私有化部署 + 数据主权** | 极高 | ❌(中国市场未运营) |
| **国产开源模型友好**(Qwen/DeepSeek) | 高 | △ 部分(MCP 兼容) |
| **领域包隔离**(换领域不改引擎) | 高 | △ 部分(Partner Extension) |
| **Permission Before Intelligence 工程化 + 评测集** | 极高 | ✓ Glean 也有,但 Partner 可叠加 |

### 4.4 IP 价值

**Partner 路径**: 中(取决于 Glean Partner 经济学)
**主路径 D**: 极高(数据主权 + 开源模型 + 私有化)

### 4.5 UNKNOWN 转 Robin 会谈必问

完整 14 题见 `docs/partner/questions-for-glean.md`。M09 重点:
- Q1: Asia 市场战略
- Q2: Partner 类型期待
- Q3: 我方 profile 适合哪条路线
- Q7: 商业模式 + first-party 竞争风险
- Q11: 定价模式(C24)
- Q13: 中国区部署与数据主权

## 5. References

- `docs/partner/partner-meeting-brief.md`(Phase 0 产出)
- `docs/partner/questions-for-glean.md`(Phase 0 产出)
- `RESEARCH_PRD_V2.md` §6 M09
- `RED_TEAM_REVIEW.md` v3 §0.6-0.7(中国市场落定 + 主路径 D)
- `docs/research/Glean Partner Manager Call 战略准备稿.md`(v1 草稿)
- `RESEARCH_PRD_V2.md` §6 M09 Glean-Partner 边界图
