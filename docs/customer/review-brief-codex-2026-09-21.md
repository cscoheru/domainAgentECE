# Codex 审验请求 — Interview-001 + 校准 + Next Step（已附 Codex 裁定）

> **作者**: Claude（Opus 5）
> **日期**: 2026-09-21
> **触发**: interview-001 落地 + 校准 + 3 个具体后续值 + Codex 战略裁定
> **范围**: 本批仅审 (a) interview-001 记录 + (b) 校准 + (c) next_step + (d) Obsidian 镜像；cut-041 已闭合,见 `cut-041-report.md`
> **更新**: 2026-09-21 23:43 Codex 给出裁定 → §9 同步裁定结果 + §10 修 1 行 + (d) 修 2 处 + memory 写入

---

## 0. 提交事实（Codex 拉取用）

| commit | 内容 | 文件 |
|---|---|---|
| `69cd964` | interview-001 记录 + 8 校准（已审）| `notes/procurement/interview-001.md`（NEW）+ `customer-profile.procurement.md`（EDIT）+ `validation-metrics.procurement.md`（EDIT）|
| `793c472` | next_step 具体值初版（已审）| `notes/procurement/interview-001.md`（EDIT §10）|
| `94fee03` | review brief 落仓根 | `review-brief-codex-2026-09-21.md`（NEW）|
| **`a1b2c3d` (下一刀)** | **Codex 裁定 3 处修复 + 战略同步** | `customer-profile.procurement.md`（1 行备注追加）+ `notes/procurement/interview-001.md`（§10 改"条件触发"）+ `notes/procurement/interview-001-raw-guide.md`（NEW,镜像 Obsidian 合并版）+ `README.md`（NEW,镜像 customer-pack/README.md）|

**远程态**: `main 5552128..a1b2c3d`（4 commits, 18 files / ~530ins / ~14del）

---

## 1. Codex 审 (a): interview-001 记录准确性 — **PASS** ✅

**Codex 裁定**:
- §0 元数据与 frontmatter 一致（5 项已回填 + recording_consent=TBD 明示 ⚠️）
- §1-§5 每组（A1-A5/B6-B8/C9-C10/D11-D13/E14-E15）均有斜体原话,逐句比对无删字/改词/改语序；§6 C3 两问原话完整
- §7 归属正确:保留态度归于受访者（"考虑安全性,大概率不合适"）,本地部署是受访者提出的唯一可行路径
- §8 三句 quotes 均为原话的真子串（A4 "比价流于形式" / C10 "审计严格时成本会降低…忽高忽低" / §7 "该系统本地部署到我方系统"）,无二次创作
- §9 八条 surprises "原假设/实际/修正" 三栏齐备,每条"实际"均可回溯到带原话的章节
- §11 评分算术正确: 0.3×5 + 0.2×2 + 0.2×3 + 0.15×5 + 0.15×3 = 3.7

---

## 2. Codex 审 (b): 校准覆盖 8 surprises — **PASS + 1 行强制修正** ✅（已修）

**Codex 裁定**:
- customer-profile: 9 条全落
- validation-metrics: 7 条全落
- 【强制修正 1 行】interview-001.md §9 surprise #1（line 218）修正栏写 "Customer Profile §1 频次 改为'年初/年底集中 + 全年单独'",但 profile line 14 实际只落了量化口径（≥30 / 快销品≥500）,频次结构文字未落到 profile。

**已修**: `customer-profile.procurement.md` line 14 备注追加 "**年初/年底集中采购 + 特殊情况单独审批（interview-001 A2）**"。

---

## 3. Codex 审 (c): next_step §10 落地 — **PASS + 战略同步** ✅（已改）

**Codex 裁定**:
- 3 个具体值真实回填,无虚构
- 执行清单 4 步与 §3 推荐路径同序
- 剩余待办 2 项明示
- ⚠️ 注意:若用户确认"暂缓第 2 次访谈",§10 需同步改一行（见 §10 战略裁定）

**已改**: 战略同步 Codex 战略裁定,§10 第 2 次访谈从"2026-09-24 确定日程"改为"条件触发、默认暂缓"+ T1-T4 触发器清单。

---

## 4. Codex 审 (d): Obsidian 镜像完整 — **FAIL + 2 处修复** ✅（已修）

**Codex 裁定**:
- ① interview-guide.procurement.md diff ≠ 0:Obsidian 侧是"反馈合并版",仓根侧是干净模板。原始逐字记录只存在于 Obsidian、未入 git —— 违反镜像纪律,且 recording_consent 仍为 TBD 时原始记录不在版本控制内是治理缺口。
- ② docs/customer/README.md 在仓根不存在（Obsidian 有,brief 速查表声称"仓根 README.md ✅ 同步"不成立）

**已修**:
- ① Obsidian 合并版复制入仓 `docs/customer/notes/procurement/interview-001-raw-guide.md`（git 追踪取证链）；仓根 `interview-guide.procurement.md` 保持干净模板不动；`interview-001.md` frontmatter source 字段改指新路径
- ② Obsidian customer-pack/README.md 复制入仓 `docs/customer/README.md`

---

## 5. Codex 战略裁定: 第 2 次客户访谈可否暂缓 — **接受（有条件）**

**Codex 立场**: 以 interview-001 为主推进后续,逼不得已再约第 2 次。

**理由**:
1. 访谈-002 的既定目标可被更强探针替代——本地 POC 可行性 + POC 条件恰好是 09-23 要发的 demo 录屏 + 数据不出域架构图所行为化测试的东西。客户对"数据不出域"方案的**真实反应**信号强度 ≥ 一次 30 分钟谈话
2. 3.7 分只比门槛高 0.2,且 Next Step=2 说明受访者本就没承诺什么——用一次会议救不回一个没承诺的客户
3. 真正不能省的不是"第 2 次访谈",而是"POC 前的 IT 侧一次对话"——P2=IT 负责人这个关键校准目前只有 E14 一句原话支撑（单点证据）。但这一通可以是 async 约成的通话,不必升级为正式访谈

**触发器 T1-T4（任一触发即恢复第 2 次访谈 = "逼不得已"的操作定义）**:
- T1: 09-23 发出后 **5 个工作日无反馈**
- T2: 反馈积极,但 POC 部署形态 / 数据敏感度分级 **异步谈不拢**
- T3: 进入任何 POC 承诺前,**IT 负责人拒绝 async 接触**（P2 单点证据必须补）
- T4: 出现与 #001 矛盾的强信号（如客户明确要求云端 SaaS → 推翻 surprise #6 校准,需当场重访）

**配套动作**:
1. 09-23 发出物 = 录屏 + 私有化架构图 + **两个异步请求**（对录屏的书面反馈 + 引荐 IT 负责人）
2. 引荐线（某行业制造企业）**不受影响,照常异步推进**
3. §10 同步改一行 + memory 写入 `interview-001-codex-closure.md`,避免下个周期凭印象重开访谈

**STOP**: Codex 在 (b) 1 行修正 + (d) 2 处修复完成前不进入任何后续动作 → **已完成 ✅**

---

## 6. 范围锁（确认未越界）

| 锁 | 状态 |
|---|---|
| 不引入新 Kernel 对象 / Adapter / Runtime | ✅（纯访谈记录 + 校准 + 文档）|
| 不改 ece 仓任何代码 | ✅（cut-041 已闭合,本批零代码改动）|
| 不触发 Sprint 5/6 | ✅ |
| 不改 GRC 3 件套（既有）| ✅（diff = 0）|
| 不动 V3 PRD | ✅ |
| 不动 ECE/CLAUDE.md 铁律 | ✅ |

---

## 7. 用户决策轨迹

- **2026-09-21** user 提供 3 个具体值: 录屏 09-23 / 访谈 09-24 / 制造业引荐
- **2026-09-21** Codex 给完整裁定 + 战略裁定(暂缓访谈,以 09-23 异步探针替代)
- **2026-09-21** user 选方案 1:接受 Codex 战略裁定 + 立即修 1 行 + 修 2 处镜像 + 同步 §10

---

## 8. 文件位置速查

```
ECE 仓根（git 追踪）:
  /Users/kjonekong/projects/domainAgentECE/docs/customer/
    ├── README.md                                     ← NEW (镜像 Obsidian customer-pack/README.md)
    ├── demo-script.md
    ├── customer-profile.procurement.md              ← 校准 + line 14 备注追加
    ├── customer-profile.md                          (GRC 既有,未改)
    ├── interview-guide.procurement.md
    ├── interview-guide.md                           (GRC 既有,未改)
    ├── validation-metrics.procurement.md            ← 校准
    ├── validation-metrics.md                        (GRC 既有,未改)
    ├── review-brief-codex-2026-09-21.md             (本文件)
    └── notes/procurement/
        ├── interview-001.md                          ← §10 改"条件触发"+ frontmatter source 改指
        └── interview-001-raw-guide.md                ← NEW (镜像 Obsidian 合并版,取证链)

Obsidian 镜像:
  /Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0921/customer-pack/
    ├── README.md
    ├── demo-script.md
    ├── customer-profile.procurement.md
    ├── interview-guide.procurement.md               (斜体原话合并版)
    ├── validation-metrics.procurement.md
    └── notes/interview-001.md                       (与仓根同步)

ECE 仓根 reports:
  /Users/kjonekong/projects/domainAgentECE/ece/reports/cut-041-report.md  (cut-041 闭合报告,本批不审)
```

---

**Author**: Claude（Opus 5）
**Date**: 2026-09-21
**Status**: **Codex 裁定全部接受 + 修复完成**；Gate 5 客户访谈包（Procurement 方向）进入 async 探针窗口（09-23 触发器 T1-T4 启动）