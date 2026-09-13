# M07 — Governance / Evaluation Layer

> **Phase**: 2 — Capability Map
> **Last Verified**: 2026-09-13 (v1 baseline 2026-09-03)
> **PRD**: [`/RESEARCH_PRD_V2.md`](../../RESEARCH_PRD_V2.md) §6 M07
> **Linked Q**: Q3 (真正壁垒) / Q5 (若不用 Glean,我们该做哪层)

## 1. 研究问题

1. Glean Protect(安全合规)与 Intelligence(模型路由/Model Hub/AI Gateway/用量控制)能力边界
2. Agent Governance:rollout / share / certify / 权限控制(C13)
3. Agent Observability 指标(C14)是否含**业务正确性**(C22 暗示不含)
4. Domain Evaluation 是不是我方最高 IP 价值的空白层?
5. 我们应自建 Governance 还是 Integrate Glean?

## 2. 证据表

| # | Claim | Source | Confidence |
|---|---|---|---|
| C01 | Glean 平台含 Protect(安全合规)与 Intelligence(模型路由/AI Gateway)模块 | glean.com 首页 | CONFIRMED |
| C13 | Agent Governance rollout/share/certify | glean.com/product/agents | CONFIRMED |
| C14 | Agent Observability adoption、error rates、up/down votes、ROI | glean.com/product/agents | CONFIRMED |
| C22 | Glean Agent 观测不含业务正确性/领域推理质量评估 | 推断(C14 指标全平台级) | STRONGLY_INFERRED |
| C23 | Domain 层(领域本体/推理/评估)是 Glean 未覆盖的空白 | 推断 | STRONGLY_INFERRED |

## 3. 能力判断

| 能力维度 | Confirmed | Inferred | Unknown |
|---|---|---|---|
| Platform Observability 指标齐全 | ✓ (C14) | | |
| 业务正确性评估 | | ✗ (C22 不含,**C38 收紧**:execution-path/performance 评估 ≠ domain correctness;Glean 官方 "evaluations" 语义指向执行路径与性能,不构成 domain evaluation 证据) | |
| 领域推理质量评估 | | ✗ (C22 不含) | |
| Agent Governance(rollout/share/certify) | ✓ (C13) | | |
| Glean Protect 安全合规 | ✓ (C01) | | |
| Glean Intelligence 模型路由 | ✓ (C01) | | |
| Model Hub / AI Gateway | ✓ (C01) | | |
| 用量控制 | ✓ (C01) | | |
| Approval / Rollout 机制细节 | | △ (C13 暗示存在) | |

## 4. 对 Platform Kernel 的含义

### 4.1 Build / Buy / Integrate / Partner 决策

| 决策项 | 决策 | 理由 |
|---|---|---|
| Platform Observability(adoption/error/ROI) | **Integrate Glean**(或 Phase 4 决策) | 横向指标,非核心 IP |
| **Domain Evaluation(业务正确性)** | **必自建,极高 IP** | C22 + C23 双确认 Glean 空白;ECE EVALUATION E1-E6 |
| **Domain Reasoning 评估** | **必自建** | C23 空白 |
| Approval / Rollout | **Phase 5 后**(非 v0) | 复杂度高 |
| 安全合规(Glean Protect) | **不在 v0**(v0 单租户) | 多租户才需要 |

### 4.2 关键判断 — Domain Evaluation 是我方最高 IP 空白层

v3 Red Team 已识别(v1 §0 + v3 §0.8):
> 若 Glean 观测仍停留在平台级指标(平台指标 vs 业务正确性的二分),则 **Domain Evaluation 是我们最高 IP 价值的空白层**
>
> **C38(2026-09-13 Cline 抓 Agent Builder FAQ) 定稿措辞**: "未见 Glean 提供领域正确性/业务推理质量评估的公开证据;官方 Agent 治理文案出现 'evaluations'(语义指向执行路径与性能,C38),不构成 domain evaluation 的证据。"

具体表现:
- Glean 给"用了多少次、采纳率多少"——**平台级**
- 我方需要"判断对不对、控制项映射是否充分、推理是否漏条件"——**业务正确性**

### 4.3 IP 价值

**Domain Evaluation: 极高**
**Platform Observability: 中**(横向)

### 4.4 UNKNOWN 转 Robin 会谈必问

- Glean 内部是否在做 Domain Evaluation(若做则我方 IP 价值受损)
- Agent Governance 的 Approval 流是否开放给 Partner
- 用量控制是否包括 Per-Agent Token 配额

## 5. References

- `docs/research/glean-capability-map.md` §3.5
- `RESEARCH_PRD_V2.md` §6 M07
- `ece/docs/EVALUATION.md`(E1-E6 套件)
- `RED_TEAM_REVIEW.md` v3 §0.8(技术与产品要求新增)
- `RESEARCH_PRD_V2.md` §10(治理/Evaluation 是核心 IP)
