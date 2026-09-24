# onyx-lab — 本地开发主线（i9 / WSL2 工作副本）

> 建立时间：2026-09-23
> 用途：把此前在 Mac 侧 Codex 会话里累积的**决策背景、部署实况、任务签发状态**全部落到项目文件夹内，使 `codex` 与 `claude` 都能在 i9 本地开箱续作。
> 状态：**工作副本已迁移到 i9**。此后以 `/mnt/d/Projects/domainAgentECE` 为唯一权威副本，Mac 侧副本会过期。

---

## 0. 一句话现状

ECE v0（cut-041～045）已闭环并部署，但客户视角的演示"看不懂、太技术化"。据此确定新主线：**ECE 拥有身份/权限/来源/审计/领域对象/工作流，Onyx CE 作为可替换的内容与检索引擎**。Onyx CE v4.7.8 已在 i9 的 WSL2 Docker 中跑通并通过健康检查；第一刀 `OEI-001`（引擎侧验证）任务书已签发，等待本地 agent 执行。

## 1. 这个目录里有什么

| 文件 | 作用 |
|---|---|
| `README.md` | 入口索引（本文件） |
| `CODEX-ROLE.md` | **codex 的角色任务书**：架构师/计划与审验——读什么、守什么红线、下一步做什么 |
| `CC-ROLE.md` | **cc 的角色任务书**：worker 程序员——读什么、怎么做证据、下一步做什么 |
| `DECISION-ONYX.md` | 为什么放弃 Dify、为什么选 Onyx、边界如何划分、还有哪些未决 |
| `DEPLOYMENT-STATUS.md` | i9 硬件/WSL/GPU 实测数据、容器清单、端口、资源占用、运维命令、已知问题 |
| `LOCAL-AGENT-PROTOCOL.md` | codex CLI 与 Claude Code 的轮转协议：谁签发、谁执行、谁审验、目录约定、硬约束 |
| `OEI-ROADMAP.md` | 新主线路线图：已签发的刀 + 规划中的刀，每刀必须"马上能看到、能测" |
| `ASSET-INDEX.md` | 全项目关键资产索引（PRD、历史审验记录、ECE 代码仓、报告与 memory） |
| `OEI-001/TASK.md` | 已签发的第一刀任务书（引擎侧验证） |
| `templates/` | 后续每刀的任务书与审验书模板 |
| `bin/` | 调用 Onyx 的受限包装脚本（API / 上传 / 资源采集） |

## 2. 角色分工（本目录之后默认按此运行）

```
codex CLI（i9 本地）         = 架构 + 签发任务书 + 审验成果 + 写 VERDICT.md
Claude Code（i9 本地, fisher）= 按 TASK.md 执行 + 产出证据 + 写 REPORT.md + 建 DONE
```

两边都不需要跨机器操作。工作产物全部落在 `/mnt/d/Projects/domainAgentECE/onyx-lab/` 下（该目录对两个用户都可读写）。

## 3. 如何开始（给 codex CLI 的第一条指令）

```
你是架构师。先读 /mnt/d/Projects/domainAgentECE/AGENTS.md，
再读 /mnt/d/Projects/domainAgentECE/onyx-lab/CODEX-ROLE.md（你的角色任务书），
然后照它 §2 的清单按序读完资料，并按 §8「你的下一步任务」执行。
```

cc 侧对应的一句话：

```
你是 worker。先读 /mnt/d/Projects/domainAgentECE/CLAUDE.md，
再读 /mnt/d/Projects/domainAgentECE/onyx-lab/CC-ROLE.md（你的角色任务书），
然后照它执行 OEI-001。
```

## 4. 迁移提示（重要）

- 旧位置 `/srv/onyx-lab/` 下曾放过任务书与受限脚本；该目录对 `codex` 用户不可读（权限受限），**已废弃，不再作为工作区**。
- 新的权威位置就是本目录。`bin/` 里的三支脚本是本目录内重新落地的版本，可直接使用。
- 密钥/会话 Cookie 不再放在 `/srv`；约定位置见 `DEPLOYMENT-STATUS.md` §6，且**不得进入 git**。
