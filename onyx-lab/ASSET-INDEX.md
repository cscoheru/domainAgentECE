# 项目资产索引（以 `/mnt/d/Projects/domainAgentECE/` 为根）

> 用途：本地 agent 接手时先看这张表，避免重复研究或找错文件版本。

---

## 1. 项目规则（两个 agent 都必须遵守）

| 文件 | 说明 |
|---|---|
| `AGENTS.md` | 项目总规则：角色定位（研究员/架构师/MVP PM/技术负责人）、Stop Gate、禁止过度工程化、双轨执行 |
| `CLAUDE.md` | 与 AGENTS.md 同内容，供 Claude Code 读取 |
| `ece/AGENTS.md`（若存在）、`ece/CLAUDE.md`、`ece/TASKS.md` | ECE 代码仓的独立规则与任务清单 |

## 2. PRD 与研究主线

| 文件 | 说明 |
|---|---|
| `RESEARCH_PRD_V2.md` | Track A 主线 PRD（Glean 逆向 & 企业 AI 平台内核）；**保留 §11 STOP Gate 十问** |
| `RESEARCH_PRD.md` | v0.2，已降级为历史输入，保留不删 |
| `Enterprise Context Engine.md` | 底座概念的原始长文（背景材料） |
| `RED_TEAM_REVIEW.md` | 红队评审记录 |
| `Glean_x_Domain_Product_Architecture_PRD_v0.1-作废.md` | 已作废，仅历史参考 |

## 3. 演示平台 / 知识管理主线

| 文件 | 说明 |
|---|---|
| `docs/demo-platform/DEMO_PLATFORM_PRD.md` | 演示平台 PRD（§5/§8/§9/§11 经 R6-B1 收敛） |
| `docs/demo-platform/CONSULTING_CONTEXT_KERNEL_PRD_V2.md` | 咨询行业上下文底座 / 知识管理 PRD（KC-001 来源） |
| `docs/demo-platform/CONSULTING_CONTEXT_KERNEL_KC001_TASK.md` | KC-001 任务书（Consulting Library，view-d，36 个种子对象） |
| `docs/demo-platform/DEPLOY_USER_PROXY.md` | 服务器与用户代理部署说明（含 cut-042R 的两阶段部署约束） |
| `docs/demo-platform/CUT_*_REVIEW_*.md` | 历史审验裁定（cut-042R 起，含 PASS / HOLD 全记录） |
| `docs/customer/` | 客户访谈与 demo script 相关材料 |

## 4. ECE 代码仓（`ece/`）

| 路径 | 说明 |
|---|---|
| `ece/TASKS.md` | 开发任务清单（历史 cut 序列） |
| `ece/src/` | 内核代码（domain / adapters / application / infrastructure / ui） |
| `ece/tests/` | 测试（最近一次全量：512 passed / 5 skipped / 3 deselected） |
| `ece/reports/` | 逐刀报告：`cut-0NN-report.md`、`KC001-report.md`、`cut-043/`~`cut-045/` 证据目录 |
| `ece/reports/cut-045-report.md` | 最后一刀（扩展蓝图 + 部署包 + 整体验收）收口报告 |
| `ece/demos/`、`ece/deploy/`、`ece/docs/` | 演示、部署与文档资产 |

## 5. 本目录（`onyx-lab/`）

| 文件 | 说明 |
|---|---|
| `README.md` | 入口索引 |
| `CODEX-ROLE.md` | codex 角色任务书（架构师：计划与审验） |
| `CC-ROLE.md` | cc 角色任务书（worker 程序员：执行与证据） |
| `DECISION-ONYX.md` | Onyx 选型与边界决策 |
| `DEPLOYMENT-STATUS.md` | i9 部署实况与运维信息 |
| `LOCAL-AGENT-PROTOCOL.md` | 双 agent 协作协议 |
| `OEI-ROADMAP.md` | 新主线路线图 |
| `OEI-001/TASK.md` | 第一刀任务书 |
| `templates/` | 任务书 / 审验书模板 |
| `bin/` | Onyx 受限包装脚本（API / 上传 / 诊断） |

## 6. 不在本仓库内的资产（在 i9 上）

| 位置 | 说明 |
|---|---|
| `/home/codex/onyx-lab/src` | Onyx CE v4.7.8 源码与 compose（只读） |
| Docker volumes | Onyx 的 Postgres / OpenSearch / Redis 数据（持久化） |
| `/srv/onyx-lab/` | 旧任务区，**已废弃**；对 codex 用户不可读 |
| `~/.claude/projects/-Users-kjonekong/memory/` | Claude Code 的 memory 索引（`MEMORY.md` 等，跨会话记忆） |

## 7. 版本与副本纪律

- 本目录（i9 的 `/mnt/d/Projects/domainAgentECE/`）**是唯一权威工作副本**；Mac 侧副本从 2026-09-23 起会过期。
- 如需把成果带回 Mac，请在 i9 上 commit 后由用户侧同步，不要在两台机器上并行编辑同一文件。
- 历史 cut 与 KC-001 的 evidence 属于证据链，**只读不迁移**（除非任务书明确要求归档整理）。
