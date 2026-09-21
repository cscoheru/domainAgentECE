# Codex 审验请求 — Interview-001 + 8 项校准 + Next Step 收口

> **作者**: Claude（Opus 5）
> **日期**: 2026-09-21
> **触发**: interview-001 落地 + 校准 + 3 个具体后续值（demo 录屏 09-23 / 第 2 次访谈 09-24 / 制造业引荐）
> **范围**: 本批仅审 (a) interview-001 记录 + (b) 校准 + (c) next_step；cut-041 不再审（已闭合,见 `cut-041-report.md`）

---

## 0. 提交事实（Codex 拉取用）

| commit | 内容 | 文件 |
|---|---|---|
| `69cd964` | interview-001 记录 + 8 项校准 | `docs/customer/notes/procurement/interview-001.md`（NEW）+ `customer-profile.procurement.md`（EDIT）+ `validation-metrics.procurement.md`（EDIT）|
| `793c472` | next_step 具体值 | `docs/customer/notes/procurement/interview-001.md`（EDIT §10）|

**远程态**: `main 5552128..793c472`（2 commits, 14 files / 314ins / 14del 累计）

---

## 1. Codex 审 (a): interview-001 记录准确性

**审验目标**: 严格保留受访者原话（§5 纪律）+ 8 surprises 与假设对齐 + 评分口径正确。

**Codex 操作**: 读 `/Users/kjonekong/projects/domainAgentECE/docs/customer/notes/procurement/interview-001.md`（仓根 git 追踪版）

**审验清单**:
1. **§0 元数据** vs frontmatter 一致（5 字段）
2. **§1-§5 答案**: 是否完整保留原话斜体（不删字、不改词、不改语序）
3. **§6 C3 顺带探询**: 2 问 + 原话是否完整
4. **§7 POC 意愿**: 原话是否被正确归属（受访者对云端持保留 vs ECE 接受本地）
5. **§8 quotes**: 3 句是否真实出自受访者原话（不二次创作）
6. **§9 surprises 8 项**: 每条"原假设 / 实际 / 修正"三栏是否真实存在原假设与原话支撑
7. **§11 评分**: 0.3×5 + 0.2×2 + 0.2×3 + 0.15×5 + 0.15×3 = 3.7 是否正确（POC 推进门槛 ≥3.5）

**裁定标准**: 任何一处**改了受访者原话**或**surprises 无原话支撑** → FAIL。

---

## 2. Codex 审 (b): 校准是否完整覆盖 8 surprises

**Codex 操作**: 读 2 文件 diff（按 commit `69cd964`）

### 2.1 `customer-profile.procurement.md` 校准对齐表

| Surprise | 原假设 | 校准落点（行号） |
|---|---|---|
| #7 规模上限 | ICP 200-2000 人 | §1 line 11: **200-3000 人** + ⚠️"超大客段需个案评估"批注 |
| #8 行业缺快销品 | 仅制造/工程/IT/国资 | §1 line 12: 加 **快销品** + 多 SKU 批注 |
| #1 PR 时长 | 1-3 天（隐含） | §1 line 14: 频次结构"年初/年底集中 + 全年单独"（注释化）|
| 双线结构 | 单线流程 | §1 line 18: 加 **双线采购结构**列 |
| #6 本地部署 | 不强制 | §1 line 19: **本地部署接受度 = 必填** |
| OA portal 误判 | "OA = 完整 eProc" | §1 line 16: **OA portal 不算完整 eProc** 批注 |
| #5 组织阻力 | 阻力弱 | §2 line 31: 新增 **P6 被影响部门代表** |
| #3 决策人 | CFO / 采购总监 | §2 line 27: P2 从 CFO 改为 **IT 负责人** |
| #8 频次差异 | Person 单一 | §2 line 26: 新增 **P1b 快销品采购经理** |

**审验标准**: 9 条校准全部覆盖；不存在 surprise 漏校。

### 2.2 `validation-metrics.procurement.md` 校准对齐表

| Surprise | 原假设 | 校准落点（行号） |
|---|---|---|
| #2 / #5 AI 边界 | "比价检查可以" | §1 line 17: **生成类 vs 判断类** 二分法 + 组织阻力维度 |
| #6 POC 路径 | "脱敏 PR 快照" | §1 line 19: **本地部署 POC（脱敏快照）** = 主流约束 |
| #1 PR 时长 | 1-3 天 | §4 line 48: **1-3 周** 实测 + Business Outcome 模型重算（80 人小时/PR 基线）|
| #6 数据政策 | 公有云路径假设 | §4 line 50: POC 改为**客户环境内部署** |
| #2 / #5 AI 边界 | "AI 替代 = 比价检查可以" | §4 line 51: 重写 §1 AI Acceptance |
| #3 决策人 | CFO / 采购总监 | §4 line 52: P2 → IT 负责人 |
| #5 组织阻力 | 弱 | §4 line 53: Persona 加 P6 + MVP 加变革管理 |
| #6 POC 触发 | 公有云可接受 | §3 line 39: POC 触发条件硬约束**本地部署** |

**审验标准**: 7 条校准全部覆盖；§4 假设校准点表扩到 7 行（原 5 行）。

---

## 3. Codex 审 (c): next_step §10 是否落地为可执行

**Codex 操作**: 读 `interview-001.md` §10（commit `793c472`）

**审验清单**:
1. **3 个具体值**是否真实回填:
   - demo 录屏发送日期 = 2026-09-23
   - 第 2 次访谈时间 = 2026-09-24
   - 引荐人 = 某行业制造企业（缺具体姓名/联系方式但 user 已确认）
2. **执行清单 4 步**是否与 §3 推荐路径一致（录屏 → 架构图 → 第 2 次访谈 → 引荐接触）
3. **剩余待办**2 项是否明示（引荐人具体信息 / 第 2 次访谈议程）

**裁定标准**: 任何一处**虚构具体值**或**日期不对齐 09-23 / 09-24** → FAIL。

---

## 4. Codex 审 (d, 如需): 5 件套 Obsidian 镜像完整性

**Codex 操作**: 读 `/Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0921/customer-pack/` 整批

**审验清单**（可选,Codex 时间紧可跳）:

| 仓根文件 | Obsidian 镜像 | 同步状态 |
|---|---|---|
| `docs/customer/demo-script.md` | `demo-script.md` | ✅ 同步（cut-041 后未改）|
| `docs/customer/customer-profile.procurement.md` | `customer-profile.procurement.md` | ✅ 同步（本次校准）|
| `docs/customer/interview-guide.procurement.md` | `interview-guide.procurement.md` | ✅ 同步（cut-041 后未改）|
| `docs/customer/validation-metrics.procurement.md` | `validation-metrics.procurement.md` | ✅ 同步（本次校准）|
| `docs/customer/notes/procurement/interview-001.md` | `notes/interview-001.md` | ✅ 同步（本次 commit `793c472`）|
| README.md（仓根）| README.md（Obsidian）| ✅ 同步 |

**审验标准**: 6 文件全部 diff = 0（mirror 纪律）；README.md 行 39 状态描述 = "草稿完成,等 commit + push" 已过时 → 校准为 "cut-041 push + interview-001 + 8 校准 + next_step 全闭合,3 后续值待执行"。

---

## 5. 范围锁（Codex 务必检查未越界）

| 锁 | 状态 |
|---|---|
| 不引入新 Kernel 对象 / Adapter / Runtime | ✅（纯访谈记录 + 校准）|
| 不改 ece 仓任何代码 | ✅（cut-041 报告与 ece 仓 main 可读,但本次 commit 不动 ece 仓）|
| 不触发 Sprint 5/6 | ✅ |
| 不改 GRC 3 件套（既有）| ✅（diff = 0）|
| 不动 V3 PRD | ✅ |
| 不动 ECE/CLAUDE.md 铁律 | ✅ |

---

## 6. 裁定格式（Codex 答复请用）

```text
(a) interview-001 记录准确性: PASS / FAIL（理由）
(b) 校准覆盖 8 surprises: PASS / FAIL（理由）
(c) next_step §10 落地: PASS / FAIL（理由）
(d) Obsidian 镜像完整（如审）: PASS / FAIL（理由）

如有 FAIL: 列出具体行号 + 修正建议
```

---

## 8. 文件位置速查

```
ECE 仓根（git 追踪）:
  /Users/kjonekong/projects/domainAgentECE/docs/customer/
    ├── README.md
    ├── demo-script.md
    ├── customer-profile.procurement.md              ← 校准
    ├── customer-profile.md                          (GRC 既有,未改)
    ├── interview-guide.procurement.md
    ├── interview-guide.md                           (GRC 既有,未改)
    ├── validation-metrics.procurement.md            ← 校准
    ├── validation-metrics.md                        (GRC 既有,未改)
    └── notes/procurement/
        └── interview-001.md                          ← NEW + §10 具体值

Obsidian 镜像:
  /Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0921/customer-pack/
    ├── README.md                                     (状态行待校准)
    ├── demo-script.md
    ├── customer-profile.procurement.md
    ├── interview-guide.procurement.md
    ├── validation-metrics.procurement.md
    └── notes/interview-001.md

ECE 仓根 reports:
  /Users/kjonekong/projects/domainAgentECE/ece/reports/cut-041-report.md  (cut-041 闭合报告,本批不审)
```

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
**Status**: 等待 Codex 裁定（a）+（b）+（c）；cut-041 报告已闭合