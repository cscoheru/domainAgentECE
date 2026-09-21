# Validation Metrics — Procurement（采购合规方向验证指标）

> Phase: Gate 5
> 方向: **Procurement**（采购合规）——与 V3 PRD 决策 + ECE v0 Procurement Pack 一致
> 关系: **与 `validation-metrics.md`（GRC 方向）并列；Gate 5 阶段按场景选其一**
> 用途: 5 场访谈后统一评估，决定 POC / Pivot / 继续验证

## 1. 逐场记录指标（11 项，V0 Spike demo 三件证据对齐）

| 指标 | 记录方式 | 判读 |
|---|---|---|
| **Problem Severity** | 1–5（受访者自评 + 我们评估） | ≥4 为强信号 |
| **PR Frequency** | 100 万+ PR 数/年 | ≥30/年 |
| **Current Cost** | 人 × 时/单 PR × 时薪估算 | ≥30 分钟/PR |
| **Current Workaround** | Excel + 邮件 + 手工对照政策 | 越土越好 |
| **Policy Availability** | 采购政策是否成文 + 是否可数字化 | 成文 + 可读 = 强信号 |
| **AI Acceptance** | D12/D13 答案 | 有明确"可执行边界"为佳 |
| **eProc Status** | 现有 eProc 平台 / Excel / OA | 无 eProc = 切得动 |
| **Willingness to Pilot** | 三档：仅聊 / 脱敏 PR 快照 POC / 真数据 POC | 后两档为正信号 |
| **Willingness to Pay** | 三档：无 / 有条件 / 主动询价 | 主动询价为强信号 |
| **Decision Maker** | 是否受访者本人 | 否则要引荐 |
| **Next Step** | 是否落地为日历邀约 | 无 Next Step = 无效场 |

## 2. 需求优先级模型（访谈后评分）

```text
Score = 0.3×Severity + 0.2×Pilot意愿 + 0.2×Policy可得 + 0.15×Cost + 0.15×Pay信号
≥ 3.5  → POC 推进
2.5–3.5 → 补访谈（累计 ≥8 场）再判
< 2.5  → 回到 product-ranking.md 启动 C3/C4
```

**与 GRC 模型的差异**：把"Data 可得"换成"Policy 可得"——GRC 数据是审计证据（任意文档），Procurement 数据是采购政策（**必须成文 + 可数字化**）+ PR 流水。

## 3. POC 触发条件（全部满足）

- [ ] 至少 2 家客户确认相同痛点（Severity≥4 且痛点描述同源，如"比价完整性检查"）
- [ ] 至少 1 家愿意提供**脱敏真实 PR 流水**（单 PR 快照亦可）+ 现行采购政策 1 份
- [ ] 该客户愿意安排采购总监 + IT 各 1 名对接
- [ ] 双方共同定义成功指标（建议：单 PR 合规检查 ≤ 5 分钟人工介入；100 万+ 阈值识别召回 ≥ 95%）

## 4. 假设校准点（第 3 场后检查）

| 原假设 | 校准问题 | 若被推翻 |
|---|---|---|
| "100 万+ 比价检查是痛点" | 受访者是否主要痛在合同审批流？ | 转向合同合规 + 付款合规双线 |
| "PR 跑 1-3 天" | 实际小时数 | 修正 Business Outcome 模型 |
| "采购政策成文 + 可数字化" | 政策是否只口头/只 Excel | 调整 MVP 路线：先做"政策数字化辅助" |
| "愿意给脱敏 PR" | 实际 PR 数据政策（含供应商报价底价） | POC 改为客户环境内部署（ECE 在客户侧） |

## 5. 停止 / 转向条件（诚实执行）

- 连续 3 场 Severity<3 → 该方向降级，回到 GRC 方向或启动 C3 采购评标
- 5 场中 0 家愿 POC → 回到候选表，启动 C3（采购评标）验证
- 发现更强相邻痛点（如客户安全问卷 C9 / 内部审计 C2）→ 记录并评估并入 Roadmap，**不擅自扩 MVP 范围**

## 6. V0 Spike 验证证据（Procurement 方向已具备）

| 三件证据 | V0 Spike 验证状态 | 与本指标关系 |
|---|---|---|
| 确定性 (N=10 byte-equal) | S6 测试 #1 PASS | "规则没偏"（替代 LLM 一致性焦虑） |
| 权限不漏 (E2=0) | 61/61 cases PASS | "审计师问'系统是否越权'可直接答否" |
| Evidence 反查 (4-hop) | S6 测试 #2 PASS | "审计师问'决策依据'可一行 SQL 反查" |
| Permission denied 零副作用 | S6 测试 #3 PASS | "即使被越权访问，最坏也是 no-op" |

**访谈话术**：当客户问"你们怎么证明 X"——直接指 V0 spike 测试文件（不藏、不吹）。
