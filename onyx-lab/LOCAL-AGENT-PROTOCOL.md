# 本地双 Agent 协作协议（codex CLI × Claude Code）

> 生效时间：2026-09-23 ｜ 适用范围：`onyx-lab/` 下的所有 OEI-* 刀具
> **角色任务书（先读这两份）**：[`CODEX-ROLE.md`](CODEX-ROLE.md) — 架构师/计划与审验；[`CC-ROLE.md`](CC-ROLE.md) — worker 程序员。
> 本文件只放两边共享的流程与硬约束；各自"读什么、注意什么、下一步做什么"在角色任务书里。

---

## 1. 角色

| 角色 | 运行位置 | 职责 | 禁止事项 | 详细任务书 |
|---|---|---|---|---|
| **codex CLI** | i9 / WSL | 架构设计、签发 `TASK.md`、审验成果、写 `VERDICT.md`、签发下一刀 | 不代替执行方跑任务、不越过审验直接进下一刀 | [`CODEX-ROLE.md`](CODEX-ROLE.md) |
| **Claude Code（cc）** | i9 / WSL，`fisher` 用户 | 按 `TASK.md` 执行、产出 `evidence/`、写 `REPORT.md`、建 `DONE` | 不自行开下一刀、不改任务范围、不动上游源码 | [`CC-ROLE.md`](CC-ROLE.md) |

用户只负责把 TASK 交给 cc（或由本地 agent 间直接约定），不需要跨机器操作。

## 2. 目录约定（每刀一个目录）

```
onyx-lab/
├── OEI-00N/
│   ├── TASK.md        ← codex 签发（cc 只读）
│   ├── workspace/      ← cc 的源文件/素材
│   ├── evidence/       ← 每条命令的请求/响应、诊断、截图路径清单
│   ├── REPORT.md       ← cc 的收口报告
│   ├── DONE            ← cc 完成信号（内容写完成时间）
│   └── VERDICT.md      ← codex 审验结果（PASS / FAIL + 理由 + 返工项）
├── bin/                ← 受限包装脚本
├── templates/          ← 任务书 / 审验书模板
└── *.md                ← 本目录的背景与状态文档
```

## 3. 状态机（严格单向）

```
codex 写 TASK.md
        │
        ▼
cc 执行 ──► 产出 evidence + REPORT.md ──► 建 DONE
        │
        ▼
codex 审验 ──► 写 VERDICT.md
        │
        ├── PASS ──► 本刀关闭；codex 才可签发下一刀（新目录 OEI-00N+1）
        └── FAIL ──► VERDICT.md 写 R{n} 返工项
                      └─► cc 删旧 DONE、返工、重新建 DONE ──► 再复审
```

心跳建议：cc 侧心跳看 `VERDICT.md` 是否出现；codex 侧心跳看 `DONE` 是否出现。**没有新文件就不动作、不打扰用户。**

## 4. 什么算"完成"

一刀只有在下列全部成立时才算完成：

1. `TASK.md` 里每一项都在 `REPORT.md` 有对应结果（PASS / FAIL + 证据文件指针）；
2. `evidence/` 里放的是**真实执行输出**，可被第三方复现；
3. 有**可见/可测**的产出（UI 变化、接口返回、检索命中），不是只有文字描述；
4. 跑过确定性测试（同输入多次结果一致）或至少跑过可重复的 smoke；
5. `DONE` 已创建。

## 5. 硬约束（违反即 FAIL）

- 不改 Onyx 上游源码；不改 compose / `.env`；不重启、不停、不重建容器（除任务书明确授权）。
- 不 commit / 不 push，除非任务书明确写明允许。
- 不改 ECE 主仓代码，除非任务书本刀范围就是 ECE 侧。
- 不在任何产出物中出现密码、Cookie、token 原文；evidence 里必须脱敏。
- 不触碰 `/mnt/c`；密钥不进 git。
- 范围锁：任务书没写的功能不做；发现必须做的额外事项，写进 `REPORT.md` 的"建议"段，不要顺手实现。

## 5.1 资源纪律（2026-09-25 起生效，双方共同遵守）

> 背景：本机是 i9 / 16GB 物理内存 / WSL 上限 12GB（已改 14GB 待重启生效）的开发机。实测 Onyx 九容器约占 **7.5 GiB**、本地 `llama-server` 再占 **约 2.5 GiB**，**空载即接近上限、靠 swap 兜**。资源是这台机器上最稀缺的东西，因此把负载分层当成纪律，而不是"遇到再说"。

1. **日常开发不常驻真栈。** 改 ECE 自己的逻辑（permissions / context / consulting 等）时用 `ECE_CONTENT_ENGINE=mock`，**不要**为了顺手而长期开着真 Onyx + ollama。
2. **真引擎只用于取证与验收。** 每刀在"该取证的那一步"用 `ECE_CONTENT_ENGINE=onyx`（失败路径同样不得用 mock 代替），验完即释放：临时 Postgres 容器、后台 uvicorn / 反代进程、临时 worktree **一个都不许留**（教训：OEI-005 抓到 10 个泄漏的 uvicorn 子进程共 558MB）。
3. **收尾三查**（写进 `REPORT.md`）：① `pgrep` 无残留探测进程；② `docker ps -a` 无残留 `ece-*`；③ 内存/swap 快照（`bin/collect-diagnostics.sh`）。
4. **不再默认"重跑全套件"来确认无回归。** 单测（DB 无关）+ 该刀相关子集优先；全套件只在收尾跑一次并落盘。注意基线含一个已知 flake（`test_s20_audit_webhook`，≈1/12）。
5. **需要整套真栈做重集成验证时**，优先考虑按需开一台便宜云 VM 跑完即关，而不是把负载硬塞进这台开发机（该实践将来对客户部署也有复用价值）。

## 6. 与历史体系的关系

- 旧编号 `cut-041`～`cut-045` 及 `KC-001` 属于上一阶段（ECE v0 演示平台 + 咨询知识库种子），**已完结，不再使用 cut 前缀续号**。
- 新主线统一使用 `OEI-00N`（Onyx Enterprise Integration）。第一刀为 `OEI-001`。
- 历史审验记录与报告仍在原位置（见 `ASSET-INDEX.md`），作为证据链保留，不迁移、不改写。

## 7. 报告要求（cc）

`REPORT.md` 至少包含：范围声明 → 逐步实测结果（含命令与证据文件）→ 确定性/重复性验证 → 资源与副作用说明 → 与任务书的偏差说明 → 建议（不实现）。结论用 PASS / FAIL 明写，不写"应该没问题"这类模糊表述。

## 8. 审验要求（codex）

`VERDICT.md` 至少包含：逐条验收结论 → 证据是否与结论匹配（抽查原始 evidence）→ 是否越界 → 是否可复现 → PASS/FAIL 裁定 → FAIL 时的最小返工清单（编号 R1、R2…）。审验以文件证据为准，不以 cc 的自我描述为准。
