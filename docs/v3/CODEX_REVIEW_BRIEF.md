# CODEX_REVIEW_BRIEF.md — PRD V3 独立审查任务书

> Date: 2026-09-20（v1.1，追加 §8 第二轮）
> 送审对象: Claude（Fable 5.1）交付的 V3 文档集
> 审查者: Codex（独立模型，无本会话上下文）
> 建议用法: 把本文件路径与对应轮次的「取证命令」一并交给 Codex，要求它**先读原文再下判词**
> 参考先例: `docs/research_v2/cline-review-brief.md`（红队自审 brief 格式）
>
> **两个轮次（按送审阶段选一节）**：
> - **第一轮 — 审 V3 本体**（§1–§7）：送审对象 = commit `96dd20d` 的 8 份 V3 文档。**已执行**（2026-09-20，判词见 `blueprintECE/0920/基于v3的codex反馈.md`）。
> - **第二轮 — 审 V3 收口**（§8–§9）：送审对象 = commit `e159f88` 的 `V3_CLOSEOUT.md` 与 6 个文件头部的收口标记。**待执行**。

---

## 1. 送审范围（三份核心 + 依据文件）

**必读（判词主要依据）**：

```
docs/v3/PRD_V3.md              1208 行 / 40 章 + 3 附录
docs/v3/KERNEL_BOUNDARY.md      255 行 / 26 行能力矩阵
docs/v3/RUNTIME_COMPARISON.md   275 行 / Kernel vs 6 类系统
```

**按需查证（判词引用依据）**：

```
docs/adr/ADR-011.md                        Kernel↔Runtime 边界决策
docs/v3/KERNEL_ARCHITECTURE_V3.md          五层架构 + 三类接口 + 8 条不变式
docs/v3/ARCHITECTURE_DECISION_V3.md        10 条决策
docs/v3/MVP_SCOPE_V3.md                    V0 范围
docs/v3/EVIDENCE_V3_ADDENDUM.md            C43–C48 新证据
docs/v3/SELF_REVIEW_V3.md                  作者自曝的 8 条弱点
```

**上游基线（判断"是否与既有决策冲突"时的对照物）**：

```
RESEARCH_PRD_V2.md                          V2 Master PRD
RED_TEAM_REVIEW.md                          红队 v3（战略约束）
docs/architecture_v2/platform-kernel-definition.md   V2 的 K1–K8 定义
docs/adr/ADR-001.md … ADR-010.md            既有 10 条 ADR（全部 Accepted）
docs/product/mvp-scope.md                   v1 的 MVP 范围（V3 声称部分推翻）
ece/CLAUDE.md                               工程五铁律
```

---

## 2. 背景（Codex 需要知道的三件事）

1. **本项目有一条强证据纪律**（`RESEARCH_PRD_V2.md` §4）：每条结论五要素 Claim / Source / Evidence / Confidence / Last Verified；置信度四级 `CONFIRMED` / `STRONGLY_INFERRED` / `INFERRED` / `UNKNOWN`；**UNKNOWN 不得作为设计前提**；禁止猜测外部系统内部实现。
2. **本项目有前科**：Track B（`ece/` 仓）已累计 **11 次完整性事故**，其中多次是"未实测就写断言""把推断写成事实""幻影 baseline 哈希"。因此**对未标注的过度声明要格外警惕**。
3. **V3 的核心宪法条文**：
   > Kernel 不是 Trigger.dev，不是 DeepSeek Harness，不是 PentaGI，也不是它们的竞争品；Kernel 位于这些执行能力之上，负责企业业务 Context、Domain Semantics、Reasoning、Decision 和 Agent/Workflow Selection。

---

## 3. 我要 Codex 回答的六个问题（按优先级）

### Q1（最重要）—— 有没有"偷偷把 Kernel 做成 Agent 平台 / 执行层"？

这是**首要判据**。请不要只看文档怎么自我声明，去看**实际写进去的职责与对象**。

**具体的越界判据（满足任一即判越界）**：

- [ ] Kernel 的 5 层里，是否存在一层**实质上属于执行层或 harness 层**？（对照 `KERNEL_BOUNDARY.md` §7 的禁止清单）
- [ ] `Domain Workflow Specification`（§16）与 `Agent / Tool / Runtime Selection`（§17）划归 Kernel —— 这两个是否**本就属于编排/执行层**？
- [ ] `ExecutionRuntimeInterface` 的 V0 默认实现是"**进程内执行器**"（`PRD_V3.md` §32.2 第 7 项、`ADR-011` §5）—— 这是否构成一个后门，让 Kernel **事实上实现了执行层**？"最朴素的进程内执行"与"自研 Runtime"的界线在哪里？
- [ ] Kernel 的 5 层是否在事实上**重新实现了 DSH 的能力**（agent loop / session / tool runtime），只是换了业务化的名字？
- [ ] `KERNEL_BOUNDARY.md` §8 的"Kernel 比 DSH 多了什么"表格 —— 是否每一条都经得起"这其实是 harness 该做的事"的反驳？

**请给出明确的 是/否 + 证据位置 + 如果为是的具体越界点。**

---

### Q2 —— Kernel 的边界是否**自洽**？

逐条检查 `KERNEL_BOUNDARY.md` 的 26 行矩阵：

- 是否有某一行**同时**给 Kernel 标了 PRIMARY，又在禁止清单里禁止 Kernel 做同一件事？
- 是否有某两行**互相矛盾**（例如某能力既说"Provider 提供"又说"Kernel PRIMARY"）？
- 那一列标 `UNKNOWN` 的（Glean Domain Ontology 行）是否被后续章节**当作已知使用**？
- 我自行**补了 11 行**（指令草表 15 行 → 26 行）。请判断：补的行里有没有**不该给 Kernel** 的？特别是 `Permission Enforcement`（行 1）、`Temporal Context`（行 24）、`Private Deployment`（行 25）。

---

### Q3 —— 证据强度是否支撑得起结论？

- `ADR-011` 的核心决策（Kernel MUST NOT 实现队列/重试/调度/持久化执行/agent loop）建立在 **C43（Trigger.dev，仅检索面摘要，原文抓取被工具限制拒绝）** 与 **C44（DSH，仅二手来源）** 之上。这个证据强度够不够支撑一个 Accepted ADR？
- 作者在 `EVIDENCE_V3_ADDENDUM.md` 给 C43 = `CONFIRMED`、C44 = `STRONGLY_INFERRED`。**分级是否诚实？有没有该降级而未降的？**
- 全文是否有**把 `STRONGLY_INFERRED` 当 `CONFIRMED` 使用**的地方（尤其是 C22/C23 相关的"Glean 空白"论述）？
- 是否**混入了新的未标注断言**？（例：`RUNTIME_COMPARISON.md` §3.2 关于 DSH 的 session 语义、§7 关于 RAG 失败模式的论述 —— 有无来源？）

---

### Q4 —— 与既有决策的一致性

作者声称"**不推翻任何 V2 决策，全部为新增或扩展**"（`ARCHITECTURE_DECISION_V3.md` §1）。请核验：

- 逐条比对 `docs/adr/ADR-001` … `ADR-010`，找出**实质冲突**（不是措辞冲突）。
- 重点：`docs/adr/ADR-001` 定义单一 `ContextAdapter`，V3 扩展为三类接口 —— 这是**超集**还是**语义变更**？
- 重点：V3 §2 明确说"推翻 v0.1 的 Glean 边界划分"、"推翻 v1 `mvp-scope.md` 把权限外推给 Glean"（见 `MVP_SCOPE_V3.md` §8）。作者在 `ARCHITECTURE_DECISION_V3.md` §1 写"**被推翻的 v0.1 决策：1 条**"。**这个计数对吗？** 请数一遍。
- `docs/architecture_v2/platform-kernel-definition.md:174` 说"Glean 集成作为**可选 Adapter**"；V3 说"Glean 是 **Provider 之一**"。这是泛化还是**降级**？降级会不会使 V2 的 K1–K8 论证失去前提？

---

### Q5 —— V0 范围是否真的可执行？

- `MVP_SCOPE_V3.md` §2 的 **13 步闭环** + §7 的规模红线，与"**2–4 周**"（`PRD_V3.md` §32.1）是否匹配？
- `MVP_SCOPE_V3.md` §6.2 的质量验收里，**权限暴露 = 0** 是硬门，而 `EVIDENCE_V3_ADDENDUM.md` C47 记录实测为 **5 暴露 + 5 失败**。作者是否**充分披露**了这个差距，还是淡化了？
- `PRD_V3.md` §37.1 的 GO 条件是否**可机械判定**？还是模糊到无法作为闸门（例如"Product thesis 不成立"由谁判定）？

---

### Q6 —— 有没有**更狠的**对 V3 的攻击？

作者在 `SELF_REVIEW_V3.md` §4 自曝了 8 条弱点，其中 R1 是"**用抽象回避验证**"（把产品定义上移到足够高，以至于任何质疑都打不中）。

**请找出作者没想到的。** 特别是：

- 是否存在一个**单点问题**，一旦成立，V3 的整个产出作废？（不是"论证不够强"，而是"结论错了"）
- V3 的抽象层级是否高到**无法指导任何具体工程决策**？（即：读完 3610 行，工程师仍然不知道该写什么代码）
- 与红队 v3 的判定"**当前 MVP 范围内，护城河假设不成立**"相比，V3 是否真的回应了这个判定，还是**绕开了**它？

---

## 4. 我知道的弱点（**不必重复发现，请直接往下挖**）

以下问题作者已在 `SELF_REVIEW_V3.md` 披露，**请勿把"发现了这些"当作主要产出**：

| 已披露 | 位置 |
|---|---|
| R1 抽象回避验证 | `SELF_REVIEW_V3.md` §4 |
| R2 三类接口可能违反铁律 3 精神 | 同上 |
| R3 Evidence / Workflow Spec 商业价值未验证 | 同上 |
| R4 "Glean 是 Provider"过度简化（C03 UNKNOWN） | 同上 |
| R5 C43/C44 证据强度不足 | 同上 |
| R6 与 V2 STOP Gate 未机械核验 | 同上 |
| R7 8 文件交叉引用不一致风险 | 同上 |
| R8 "Kernel"命名未论证 | 同上 |
| 客户验证为零 | `PRD_V3.md` §30.1 / `README.md` §4 |
| 权限硬门实测未通过 | `EVIDENCE_V3_ADDENDUM.md` C47 |
| Test E（模型无关）质量待验 | `PRD_V3.md` 附录 B |

**如果 Codex 的产出主要是复述上表，本次审查视为失败。** 请把精力放在 Q1/Q2/Q6。

---

## 5. 我要的反馈格式

请**逐条**输出，按下列 schema：

```
[严重度] 类型 | 位置 | 一句话问题
  证据: <原文引用 + file:line 或 §编号>
  为什么会伤害项目: <一句话，说清后果，不要说"论证不充分">
  如果成立，V3 需要怎么改: <具体的、可执行的修改，不要泛泛>
```

**严重度**：
- `BLOCKER` — 结论错误 / 边界不成立 / 会误导后续工程
- `MAJOR` — 需要重写或大改某个章节
- `MINOR` — 措辞、一致性、引用问题

**类型**（必须选一）：
- `事实错误` — 与可核验的事实矛盾
- `证据不足` — 结论强度超过证据
- `越界` — Kernel 做了不该做的事（Q1 专用）
- `逻辑断裂` — 推论不成立
- `不一致` — 与既有决策或自身其它章节冲突
- `不可执行` — 无法指导工程

**结尾必须给三段**：

```
1. 判词: PASS / CONDITIONAL PASS / FAIL（FAIL 请直说，本项目历史上 FAIL 是常态且有价值）
2. 三个必改项（按重要性排序，每条一句话）
3. 你认为 V3 **不该做**的一件事（反向建议 —— 有没有哪个部分应当直接删掉而不是修）
```

**不要做的事**：
- 不要复述文档内容
- 不要写"建议加强论证"这类无操作性的意见
- 不要因为文档很长就只读摘要 —— 判词必须基于原文

---

## 6. 取证命令（Codex 应自行运行核验，不要信任本文的转述）

```bash
cd /Users/kjonekong/projects/domainAgentECE

# 1. 确认交付范围与体量
git show --stat 96dd20d

# 2. 确认"v1/v2 零修改"是否为真（作者的核心声明之一）
git diff --stat f28472e..96dd20d -- docs/research docs/architecture docs/product \
  docs/cases docs/customer docs/research_v2 docs/architecture_v2 docs/product_v2
# 预期: 空。非空则作者声明为假。

# 3. 确认 ece/ 未被触碰
git show --stat 96dd20d -- ece/

# 4. 核验"Glean 空白"论断的证据基础（应为无 URL 的推断）
grep -n "C22\|C23" docs/research_v2/evidence-matrix-v2.md

# 5. 核验 V2 的 Kernel 定义原文（V3 声称继承的那句）
sed -n '170,195p' docs/architecture_v2/platform-kernel-definition.md

# 6. 核验既有 ADR 编号与状态（冲突检查）
for f in docs/adr/ADR-0*.md; do echo "== $f"; head -4 "$f"; done

# 7. 核验 v1 mvp-scope 中"权限外推给 Glean"的原文（V3 声称推翻的那条）
grep -n "Glean\|权限" docs/product/mvp-scope.md

# 8. 核验 ECE 权限硬门的实测状态（C47 的原始依据）
cat ece/reports/eval-archive/2026-09-20-cut040R2/baseline-seeded/E2.txt 2>/dev/null || \
  echo "归档未提交，需向作者索取"

# 9. 反厂商耦合门禁是否被真正规定（V3 声称的核心机制）
grep -n "grep -" docs/v3/KERNEL_ARCHITECTURE_V3.md docs/v3/PRD_V3.md
```

---

## 8. 第二轮：V3 收口审验（2026-09-20 追加）

**背景**：第一轮审查（判词见 `blueprintECE/0920/基于v3的codex反馈.md`）判定「Kernel 职责有向 Agent Platform 膨胀的风险；V0 与 2–4 周不匹配」，要求只做一次收口。作者已交付 **`docs/v3/V3_CLOSEOUT.md`**（commit `e159f88`）。本轮审验**该收口本身**，不是重审 V3 全部。

### 8.1 送审文件清单

**必读（本轮判词的主要依据）**：

```
docs/v3/V3_CLOSEOUT.md        142 行 —— 收口裁定本体
docs/v3/CODEX_REVIEW_BRIEF.md §8 —— 本节（轮次范围与问题定义）
```

**必对照（用于核对"收口是否真的回应了上一轮的三点"）**：

```
/Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0920/基于v3的codex反馈.md
    ↑ 仓库外路径。上一轮你自己的判词原文。
docs/v3/KERNEL_BOUNDARY.md                26 行矩阵本体（§2 需逐行核验自洽性）
```

**按需查阅（只在判断"收口覆盖是否完整"时读）**：

```
docs/v3/PRD_V3.md             仅读文件头部的收口标记 + §16.2 / §17 / §32 三处被点名章节
docs/v3/MVP_SCOPE_V3.md       仅读头部标记 + §2 / §3 / §4 / §7
docs/v3/KERNEL_ARCHITECTURE_V3.md  仅读头部标记 + §3
docs/adr/ADR-011.md           仅读头部 Amended 行 + 文末修订记录 + §3 / §5
```

**不必重读（收口未改动其正文）**：

```
docs/v3/RUNTIME_COMPARISON.md
docs/v3/ARCHITECTURE_DECISION_V3.md
docs/v3/EVIDENCE_V3_ADDENDUM.md
docs/v3/SELF_REVIEW_V3.md
（这四份的正文零修改；若发现收口与其中某条冲突，再按需查证）
```

### 8.2 本轮必答的五个问题

**Q1（最重要）—— 这次收口本身，是不是又一次「用文档回应文档」？**

上一轮你的要求里有明确一条：**"不要再通过增加抽象、增加对象、增加接口来解决这个问题"**。而作者的回应是交付了一份**新文档**（`V3_CLOSEOUT.md`）。

请判定：**这是同一种病的复发，还是必要的裁定记录？** 判据建议 —— 该文件是否**真的减少了**后续要做的事（收窄边界、缩小 V0、删减内容），而不是**增加了**概念。请注意 §1.4 作者又新引入了一个概念（"非功能约束"的分类修正）。

**Q2 —— 五项裁决是否每一项都判对了？**

`V3_CLOSEOUT.md` §1.1 给出了逐项裁决。请逐条攻击：

- **Permission Enforcement「保留收窄」**：作者的理由是"去掉则企业不可交付 → 不成立"。这是否是把**交付前提**误当成**Kernel 核心能力**？"policy 来源可以是 Provider"是否已经足够，以至于 Kernel 只需保留一个 **enforcement hook** 而非一项能力？
- **Agent Selection「降级为接口声明」**：降级后它还算不算"V3 最终边界"的一部分？**声明一个不实现的接口，与不声明，区别是什么？**
- **Domain Workflow Specification「保留但硬收窄」**：作者划的界线是"含执行顺序即移出"。但**业务上强制的顺序**（如法规要求的先后）算业务判据还是执行编排？这条界线是否可操作？
- **Knowledge / Retrieval「拆分」**：拆完之后，"Knowledge 作为 Context 要素"与"Context 本身"是否已经无法区分？即 —— 拆出来的是不是一个空集？

**Q3 —— 收窄后的 Kernel 是否**过度**收窄，以至于无法产出完整业务判断？**

作者把 Kernel 核心收窄为 5 项（Context / Ontology / Deterministic Business Rules / Decision / Evidence）。请反向攻击：

- 只有 **5 项**的 Kernel，能否产出一个**能在客户面前演示**的业务结论？
- **`Evidence` 去掉后 Kernel 是否仍成立？** —— 这一项是作者自己收进去的、你上一轮**未曾点名**的。（若答案是"仍成立"，则它不该在核心 5 项里。）
- 收窄后的边界，是否已与"一个普通的规则引擎 + 文档检索"难以区分？**Kernel 的不可替代性还剩多少？**

**Q4 —— 收口覆盖是否完整？**

作者在 6 个文件头部加了"已被取代"的标记。请核验：

- 标记里列的章节号（`PRD_V3` §16.2/§17/§32；`MVP_SCOPE_V3` §2/§3/§4/§7；`KERNEL_ARCHITECTURE_V3` §3；`ADR-011` §3/§5）**是否有遗漏**？即：原文档里还有哪些章节与新边界冲突但**未被标记**？
- `KERNEL_BOUNDARY.md` 只改了 **4 行 + 作废 1 行**（行 5/10/20/25），但 §1.3 声称把 4 类能力"移出 Kernel"。**26 行矩阵现在是否仍然自洽？** 特别是有没有某行仍写着 Kernel PRIMARY，而 §1.3 已把它移出。
- `ADR-011` 的 Amended 声称"决策不变，只改 V0 义务"。§3（三类接口）从 V0 推迟到 V1 —— 这**真的**只是义务变更而非决策变更吗？

**Q5 —— V0 的 6 步闭环是否真能构成"真实业务价值闭环"？**

`V3_CLOSEOUT.md` §2 的成功判据是"证明 Context + Domain Semantics + Deterministic Reasoning + Evidence 能形成真实业务价值闭环"。请判定：

- 6 步里只有 **"一个确定性 Business Rule"**。**单条规则**能否构成"业务价值"？还是只够证明"管道通了"？
- 6 步闭环与"2–4 周"是否**这次真的**匹配？（上一轮你说不匹配，作者缩了，请再判一次。）
- 若 6 步仍然偏大，**最小可信子集**是什么？

### 8.3 不要求你做的事

- 不要重读 PRD_V3 全文（1208 行）—— 收口只改了它的头部标记与三处被点名章节
- 不要重审 C43–C48 的证据强度（上一轮 Q3 已判，结论未变）
- 不要重新评估 Glean 定位（未被收口触及）
- 不要复述 `V3_CLOSEOUT.md` 的内容

### 8.4 反馈格式

沿用 §5 的 schema（严重度 + 类型 + 证据 + 后果 + 具体改法）。结尾三段改为：

```
1. 收口判词: 收口有效 / 收口不足 / 收口本身跑偏
2. 若仍有必改项，列出（最多 3 条，每条一句话）
3. V3 是否可以就此封版进入下一阶段（客户验证 + V0 spike）？
```

**特别要求**：如果 Q1 的答案是"这是同一种病的复发"，请直说，并给出**不用写文档**的替代收口方式。

### 8.5 取证命令

```bash
cd /Users/kjonekong/projects/domainAgentECE

# 1. 收口 commit 的完整改动范围
git show --stat e159f88

# 2. 收口只改了文件头部吗？（正文是否被动过）
git show e159f88 -- docs/v3/PRD_V3.md | head -40
git show e159f88 -- docs/v3/MVP_SCOPE_V3.md | head -30

# 3. 核验 26 行矩阵是否有"仍写 Kernel PRIMARY 但已被移出"的行
sed -n '/^## 2. 主边界矩阵/,/^## 3\./p' docs/v3/KERNEL_BOUNDARY.md

# 4. 对照上一轮判词原文（是否真的回应了三点）
cat "/Users/kjonekong/Documents/Obsidian Vault/blueprintECE/0920/基于v3的codex反馈.md"

# 5. 收口后 Kernel 核心 5 项的出现位置
grep -n "Context（含\|Domain Ontology\|Deterministic Business Rules" docs/v3/V3_CLOSEOUT.md

# 6. V0 6 步 vs 原 13 步的对照
sed -n '/^## 2. V0 最小闭环/,/^## 3\./p' docs/v3/V3_CLOSEOUT.md
sed -n '/^## 2. 最小闭环/,/^## 3\./p' docs/v3/MVP_SCOPE_V3.md
```

---

## 9. 一句话交给 Codex（第二轮）

> 作者按你的三点反馈做了一次收口，并把收口**也写成了一份文档**。请先判断**这件事本身是否又是"用文档回应文档"**；再逐条攻击它的五项边界裁决是否判对，尤其是收窄后的 Kernel 是否**过度收窄到与普通规则引擎难以区分**。项目历史上红队判 FAIL 多次且救回过真问题，请照同样标准审。

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
