# OEI-014 任务书 — 咨询内容加深（行业深度 2→4 / 行业洞察补齐 / 锚点扫描防假阳性）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-26
> 前置：`OEI-011` 已 **PASS 关闭**（commit `c30e50e`）；本刀是 `OEI-011/VERDICT.md` §6 转出第 1 项（"内容深度"）的承接刀
> **编号说明（重要）**：本刀叫 **`OEI-014`**，**不是 012**。理由：编号纪律（`OEI-ROADMAP.md` 顶部 2026-09-24 起生效）明确**禁止"插入新刀 + 全体顺延"**，新工作一律取**下一个未占用序号**。`OEI-012`（检索质量）与 `OEI-013`（多域演示台）**保持原号**，只是本刀排在它们之前执行。
> 返工约定：本刀若需返工，一律标 **`OEI-014 R1` / `R2`**（不插新刀、不顺延既有编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## ✦ 开工指令（cc 必读：按序读完再动手）

> **`onyx-lab/` 顶层的一批文档已由用户并入 `onyx-lab/重启必读/`**（不是丢文件；`CODEX-ROLE.md` / `README.md` / `ASSET-INDEX.md` / `DECISION-ONYX.md` 仍在顶层）。

**① 按序必读（绝对路径，一份都别跳）**

```
1. /mnt/d/Projects/domainAgentECE/AGENTS.md                                  ← 项目总规则
2. /mnt/d/Projects/domainAgentECE/onyx-lab/README.md                          ← 入口索引 + 目录变更
3. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/CC-ROLE.md                 ← 你的角色任务书
4. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/LOCAL-AGENT-PROTOCOL.md    ← 共享规则 + §5.1 资源纪律
5. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/OEI-ROADMAP.md             ← 路线图（本刀条目 + 编号纪律）
6. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-011/VERDICT.md                  ← 上一刀裁定（#2 = PASS；§6 转出第 1 项 = 本刀；§7 的好做法 = 本刀的作业标准）
7. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-011/TASK.md                     ← **上一刀的任务书**：本刀沿用它的 §3.1（诚实性规则）与 §3.2（新增对象规则），只做加深
8. /mnt/d/Projects/domainAgentECE/ece/tests/unit/test_consulting_seed_discipline.py ← 内容纪律闸门（写新内容前先读）
9. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-014/TASK.md                     ← **本文件 = 唯一任务来源**
```

**② 开工前先核对状态（只读）**

```bash
cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-014 && ls -la     # 不该有 DONE / VERDICT.md
cd /mnt/d/Projects/domainAgentECE/ece && git log --oneline -2 && git status -sb | head -3
# 期望：HEAD = c30e50e（OEI-011），ahead 3，未 push
```

**③ 本刀一句话**

把咨询知识库的**行业深度**做上去：10 个具体行业从**各 2 条**加深到**各 ≥4 条**（总数 45 → 65–70，上限 70），补齐 `insurance` / `public_sector` / `technology` **三个行业缺失的 `industry_note`**，并把"行业锚点"做成**词边界安全、可机检**的依据——**不许硬贴行业**，也不许用 `ai` 命中 `supply_chain` 这类假阳性充当依据。

**④ 硬约束速查（违反即 FAIL，全文见 §8）**

- ✅ 本刀授权改：`src/ece/consulting/seed/consulting_objects.json`（**只新增**，既有 45 条一字不动）、`docs/API.md`、`docs/DATA_MODEL.md`、`TASKS.md`、`tests/**`（**本刀不需要改任何断言**；只有在新增测试文件时才算授权）
- ❌ **既有 45 条对象的所有字段逐字节不变**（A1 逐条哈希对照 `c30e50e`）；不删、不改、不重排
- ❌ **不改任何既有断言**（现在全是 `>= 36` 下限，见 §1.4）；**若你发现必须改 → 停手 + 报 BLOCKED**（本刀不给新的解冻授权）
- ❌ 不新增词表值（行业词表保持 10 个具体行业 + `cross_industry`）；不改 `ALLOWED_*`
- ❌ 不引入新依赖；不改 Onyx；不重启/停/删容器；不碰 `/mnt/c`；**不动 `ece/demos/spa/**`**
- ❌ **不伪造内容**：行业锚点必须落在该对象**自己的 title / summary** 里；不得编造真实客户名或精确数字
- ❌ 不得要求用户截图；验收一律机器可校验
- 📌 **本刀不需要真引擎**：全程 `ECE_CONTENT_ENGINE=mock`；临时 PG 只用于收尾全套件，**验完即释放**

**⑤ 收工与心跳**

```bash
echo "$(date -Iseconds) OEI-014 complete" > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-014/DONE
```

然后 **STOP**。心跳对象 = `onyx-lab/OEI-014/VERDICT.md`。

---

## 0. 一句话目标

让**行业轴从"能用"变成"能撑演示"**：10 个具体行业**各 ≥4 条**对象、**每个行业都有 ≥1 条 `industry_note`**、`deliverable_template` 从 4 补到 ≥6，全部靠**有锚点、可机检**的新增内容实现——**既有 45 条一个字不动**。

**为什么是这一刀**（`OEI-011/VERDICT.md` §4.2 + 我的实测）：

1. OEI-011 把行业轴从"废的"救成"能用的"，但**每个具体行业只有 2 条**、26/45 是 `cross_industry`——我当时的原话是"**能用但还浅**，真正做实还需每行业 4–6 条"。
2. 用户 2026-09-24 常设约束第 3 条：阶段目标以"**把咨询行业做实做透**"为准。行业深度是这条目标最直接的落点。
3. 本刀**不碰引擎、不碰权限、不碰前端**，纯内容 + 词表 + 依据纪律，是当前性价比最高、风险最低的一刀。

---

## 1. 现状（codex 实测，可直接信任；每条都带"文件 + 符号 + 数值"）

### 1.1 行业深度：10 个具体行业**各恰好 2 条**

`src/ece/consulting/seed/consulting_objects.json`（我用项目 venv 的 Python 直接统计）：

```
total 45 | types {'case': 13, 'deliverable_template': 4, 'industry_note': 6,
                  'methodology': 10, 'proposal_play': 6, 'risk_check': 6}
per-industry: banking 2 / consumer_goods 2 / energy 2 / healthcare 2 / insurance 2 /
              logistics 2 / manufacturing 2 / public_sector 2 / retail 2 / technology 2
cross_industry: 26 条对象
```

### 1.2 `industry_note` 覆盖：**3 个行业是 0**

每条 `industry_note` 携带的行业（现 6 条）：

```
banking 1（industry-note-cn-banking-2026-001）
consumer_goods 1 + retail 1（industry-note-cn-consumer-2026-002 —— 历史遗留的双行业，
                              OEI-011 未改动它，见 OEI-011/VERDICT.md §4.1）
manufacturing 1 / logistics 1 / healthcare 1 / energy 1
```

⇒ **`insurance` / `public_sector` / `technology` 三个行业没有任何 `industry_note`**，这是本刀必须补的三个洞。

### 1.3 `cross_industry` 里**没有可重标的对象**（所以加深只能靠新增）

26 条 `cross_industry` 里，按权威关键词表 `metadata.py:298 _INDUSTRY_KEYWORDS` 扫描，只有 4 条"命中"行业词——**而这 4 条全是假阳性**，我逐条看过：

| 对象 | 假命中的关键词 | 真因 |
|---|---|---|
| `methodology-value-chain-003` | `technology` ← `"ai"` | 命中的是 `practice` 里的 **`supply_chain`**（`ch-ai-n`） |
| `methodology-lean-waste-walk-005` | `manufacturing` ← `"制造"` | 文本讲的是"精益/浪费"，不是制造业对象 |
| `methodology-benchmarking-public-010` | `public_sector` ← `"public"` | 命中的是**"公开"对标**（公共信息），不是公共部门 |
| `risk-check-data-availability-001` | `technology` ← `"ai"` | 同 `supply_chain` 子串问题 |

⇒ **结论：没有"本来有行业锚点、被错标成通用"的对象**（这反过来说明 OEI-011 的映射是对的）。**加深必须靠新增对象**，不能靠重标。

### 1.4 断言现状：**全是对照下限，新增不会再撞**（本刀不改任何断言）

我重跑了 `OEI-011/TASK.md §1.5` 定的三条盘点命令（原样照抄，输出见 §8 硬约束）：

- `grep -rn '\b36\b' tests/` → 命中的都是 **`>= 36`**（`test_consulting_documents.py:267`、`:320`、`test_consulting_engine_merge.py:342`、`test_consulting_seed_count.py:29`、`test_consulting_api_contract.py:55`）＋注释文字；
- `test_consulting_seed_count.py` 的类型分布已在 OEI-011 从 `==` 改为 **`>=`**（六个下限）；
- `grep -rn 'client_industries' tests/` → 只钉 **facets 的键集合**，**没有任何测试钉住行业取值或每行业条数**。

⇒ **本刀新增 20 条左右不会撞任何断言**；但你必须**自己重跑一遍**并把输出落盘（§5 步骤 1）——这是 OEI-011 v1.1 立下的纪律：穷尽性断言必须附可复现命令。

### 1.5 其它现场事实

- 词表：`metadata.py` 的 `ALLOWED_TYPES`（6）/ `ALLOWED_PHASES`（5）/ `ALLOWED_INDUSTRIES`（**11** = 10 具体 + `cross_industry`）/ `ALLOWED_PROBLEM_TYPES` / `ALLOWED_METHODS`；`deliverables` / `outcomes` 是**自由文本**（不在词表校验范围内）。
- 枚举：`models.py` 的 `TypeT`（6 值）、`SourceOriginT`（4 值）、`ConfidenceT = Literal["high","medium","synthetic"]`、`ReviewStateT = Literal["approved","draft"]`。
- **行业锚点关键词表有子串陷阱**（`_INDUSTRY_KEYWORDS` 里的 `"ai"`、`"public"`）——见 §3.3，这是本刀要正面解决的。
- 基线：`c30e50e` 上全套件 **847 passed / 5 skipped / 3 deselected / 0 failed**。
- 文档里需同步的现值：`docs/API.md` 有 **6 处**写着 `45`（第 495 / 499 / 531 / 604 / 635 / 717 行附近，另有 732 行"45 条对象"）。

---

## 2. 范围锁

**做**：

1. **词边界安全的锚点扫描器** + 4 个已知假阳性的回归样例（§5 步骤 0）；
2. **重盘断言**并落盘（§5 步骤 1）；
3. **新增 ~20 条对象**，把 10 个具体行业各补到 **≥4 条**，其中补 **3 条 `industry_note`**（insurance / public_sector / technology）、**≥2 条 `deliverable_template`**；
4. **锚点依据表**（每条新增对象：锚点词 + 它出现在自己 title/summary 的哪一句）；
5. facets / 过滤的加深实测；
6. 契约不回归 + 全套件（带 `-rs`）；
7. 文档（`docs/API.md` 六处 + `TASKS.md 附录 R`）与提交。

**不做**（做了即越界）：

- **不改既有 45 条的任何一个字段**（本刀只新增）；不删任何对象；
- **不改任何断言**（现有全是下限，够用）；不新增词表值；不改 `ALLOWED_*`；
- 不做检索调优（`OEI-012`）、不做多域演示台（`OEI-013`）、不动引擎/权限/记忆；
- 不改前端（`ece/demos/spa/**` 逐字节不变——facets 下拉是数据驱动的）；
- 不引入新依赖。

---

## 3. 契约（**本刀锁定**；发现契约与实测不符 → 停手 + 写 REPORT + 等 codex 对齐）

### 3.1 加深目标（硬门槛，全部机检）

| 目标 | 阈值 | 现状 |
|---|---|---|
| 每个**具体行业**的对象数 | **≥ 4** | 各 2 |
| 每个**具体行业**的 `industry_note` | **≥ 1** | insurance / public_sector / technology = 0 |
| 总数 | **65 ≤ N ≤ 70**（上限防膨胀） | 45 |
| `deliverable_template` | **≥ 6** | 4 |
| `cross_industry` 对象 | **≥ 10**（不要求变化） | 26 |

⇒ 达成路径（供参考，不强制）：**+20 条**、每条带 1 个具体行业、按"每行业 +2"铺开；其中 3 条是上述三个行业的 `industry_note`。

### 3.2 新增对象规则（沿用 `OEI-011/TASK.md §3.2`，外加两条）

1. 过两个闸门：`test_consulting_seed_schema.py` + `test_consulting_seed_discipline.py`（中文为主、客户匿名"某+行业+规模"、**合成内容 `source_origin="synthetic_variant"`**、禁竞品名、数字示意化）。
2. id 沿用既有约定 `<type 短名>-<slug>-<3 位序号>`，不得与既有 id 冲突（现有最大序号可参考 `case-*-013`、`risk-check-*-006`、`industry-note-*-006`）。
3. 每个字段填满，且 `type` / `engagement_phase` / `client_industry` / `problem_types` / `methods` **必须落在 `metadata.py` 的词表内**；`deliverables` / `outcomes` 是自由文本（中文、示意性即可）。
4. **（新增）行业标注默认恰好 1 个具体行业**；只有在"该对象确实同时属于两个行业"时才允许 2 个，且**必须为每一个行业各给一个锚点**（§3.3）与一句依据。
5. **（新增）每条 `industry_note` 恰好 1 个具体行业**，不得 `cross_industry`（沿用 OEI-011 规则；历史遗留的 `consumer-2026-002` 是**祖父对象，别动它**）。
6. `case` 不得 `cross_industry`（沿用）；`case` 的行业必须是"案例真正发生的行业"。

### 3.3 行业锚点必须**词边界安全**（本刀正面解决的假阳性问题）

**规则**：每条新增对象（以及它携带的每个行业）都要有一个**锚点**，锚点必须满足：

1. 出现在**该对象自己的 `title` 或 `summary`** 里（**不接受**只出现在 `practice` / 关键词表推导里）；
2. **词边界安全**：ASCII 关键词必须用词边界匹配（例如 `"ai"` 不能命中 `supply_chain`，`"public"` 不能命中 `"公开"`）；**长度 ≤2 的 ASCII 关键词（`ai`）与可作普通词义的关键词（`public`、`tech`）不得单独作为锚点判据**，必须配合更具体的中文词（`人工智能` / `政务` / `事业单位` / `软件` 等）；
3. **回归样例**：扫描器必须把 §1.3 那 **4 个已知假阳性**报为"**无锚点**"。这 4 条是：

```
methodology-value-chain-003 / methodology-lean-waste-walk-005
methodology-benchmarking-public-010 / risk-check-data-availability-001
```

> 这条不是为了好看：OEI-011 的锚点表里已经**如实记录**过一次 loose 假命中（`technology:ai` 其实是 `supply_chain`）。本刀要求把同类陷阱**固化成回归样例**，否则"有锚点"这个结论就不可信。

### 3.4 断言边界（**零改动**）

- 本刀**不改任何既有断言**（§1.4 已证现有全是 `>= 36` 下限）。
- 若新增测试文件：允许，但**不得**为了让它过而修改既有测试。
- **若你发现某处断言必须改 → 停手 + 报 BLOCKED**（本刀**不提供**新的解冻授权；需要解冻由我改任务书）。

### 3.5 `facets` / 过滤的"加深后可用"标准

- `GET /api/v1/consulting/facets` 的 `client_industries` 仍为 **11 个值**（10 具体 + `cross_industry`）；
- 对**每个**具体行业值，`GET /api/v1/consulting/library?client_industry=<v>` 命中 **≥4**；
- **不存在 0 匹配的值**；给出"值 → 命中数"聚合表；
- 每个具体行业那 ≥4 条里**至少 1 条是 `industry_note`**（可机检：按该行业的 note id 列表核对）。

---

## 4. 工作区与证据命名

```
onyx-lab/OEI-014/
├── TASK.md      ← 本文件（只读）
├── workspace/   ← 源文件/素材（anchor_scan.py、草稿对象、覆盖统计脚本）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

建议证据文件：`00-anchor-scanner-and-false-positives.txt`、`01-assertion-inventory-c30e50e.txt`、`02-new-objects-list.json`、`03-anchor-basis.json`、`04-coverage-before-after.json`、`05-seed-gates-raw.txt`、`06-anchor-scan-final.txt`、`07-facet-and-filter.json`、`08-contract-regression.txt`、`09-test-suite-raw.txt`、`10-docs-diff.txt`、`11-git-commit.txt`、`12-compliance-check.txt`

## 5. 任务步骤

### 步骤 0 — 锚点扫描器 + 假阳性回归（先做，它决定后面所有"有锚点"结论是否可信）

1. 写 `workspace/anchor_scan.py`：对种子里的每个对象，输出它携带的行业**锚点证据**（`industry / 落在 title 还是 summary / 命中的词 / 匹配方式`）。
2. **词边界安全**（§3.3 第 2 条），且必须把 §3.3 第 3 条的 4 条假阳性报为"无锚点"。
3. 先对**今天这 45 条**跑一遍（既有对象的锚点结果仅作参考，不改它们），落盘 `00-anchor-scanner-and-false-positives.txt`：含扫描器源码路径、4 条假阳性的对照输出、以及"扫描器能报出锚点"的正例（避免"永远报无"）。

### 步骤 1 — 重盘断言（纪律要求）

1. 照抄并运行 §1.4 的三条命令（`\b36\b` / `Counter(` / `client_industries`），把**原始输出**落盘 `01-assertion-inventory-c30e50e.txt`。
2. 在 REPORT 里写明："本刀将新增 N 条对象；上述盘点的结论是**没有任何断言与语料规模/分布精确耦合**"。

### 步骤 2 — 写新增对象（本刀的主体）

1. 按 §3.1 铺开：每个具体行业 +2（共 ~20 条），其中 3 条是 `insurance` / `public_sector` / `technology` 的 `industry_note`，另 ≥2 条 `deliverable_template`。
2. 每条都要有 §3.3 的锚点；产出 `03-anchor-basis.json`（`id / type / industry / 锚点词 / 锚点所在字段 / 锚点原句`）。
3. 产出 `02-new-objects-list.json`（`id / type / industry / 目标理由`）与 `04-coverage-before-after.json`（前后：总数 / 每行业 / 类型 / note 覆盖）。

### 步骤 3 — 写入 + 闸门

1. **只新增**，既有 45 条一字不动（写入脚本必须先做"既有条目逐字节不变"校验，再落盘——OEI-011 的 `apply_seed.py` 可复用其思路）。
2. 在**真实文件**上跑两个闸门 + 新的锚点扫描，落盘 `05-seed-gates-raw.txt`、`06-anchor-scan-final.txt`。

### 步骤 4 — facets / 过滤加深实测

按 §3.5 落盘 `07-facet-and-filter.json`（每个行业值命中数 + 该行业的 note id 列表）。

### 步骤 5 — 契约不回归 + 全套件

1. `/library` 与 `/facets` 的**键集合**逐键对照（只允许值集变化），落盘 `08-contract-regression.txt`。
2. 收尾跑**一次**全套件（临时 PG + 完整前置链），**带 `-rs`**（OEI-011 教训：skip 名单必须留痕），落盘 `09-test-suite-raw.txt`；期望 `passed = 847 + 新增测试数`、`failed = 0`、`skipped = 5`（若不是 5，差额必须能由 `-rs` 名单解释）。

### 步骤 6 — 文档与提交

1. `docs/API.md`：**6 处 `45` → 新总数**（第 495 / 499 / 531 / 604 / 635 / 717 行附近）＋ 第 732 行"45 条对象"＋ §11 补一句"OEI-014 加深到 N 条 / 每行业 ≥4"；`TASKS.md` **附录 R**；`docs/DATA_MODEL.md` 若涉及再改。
2. `git add` + `git commit`（**不 push**）；落盘 `10-docs-diff.txt`、`11-git-commit.txt`。
3. 收尾三查（`pgrep` / `docker ps -a` 无残留、内存快照）→ `12-compliance-check.txt`。

---

## 6. 验收标准（codex 将逐条核对；**每条都必须能被 evidence 证明**）

- [ ] **A0** 锚点扫描器落盘且**有牙**：把 §1.3 的 4 条假阳性报为"无锚点"，同时能对真实锚点报出命中（给出两类对照）
- [ ] **A1** **既有 45 条零改动**：逐条规范化哈希与 `c30e50e` 原值**逐条相等**（45/45），且**文件 diff 只含新增条目**（给出 diff 摘要 + 哈希对照）
- [ ] **A2** 加深目标达成：总数 **65–70**；**每个具体行业 ≥4**；**每个具体行业 `industry_note` ≥1**；`deliverable_template ≥6`；`cross_industry ≥10`（前后对照表）
- [ ] **A3** **锚点纪律**：每条新增对象都有锚点，锚点**出现在自己 title 或 summary** 里、**词边界安全**、并在 `03-anchor-basis.json` 里给出原句；两个行业的对象各给锚点
- [ ] **A4** 内容纪律：`test_consulting_seed_schema.py` + `test_consulting_seed_discipline.py` 在**真实文件**上全绿（原始输出）
- [ ] **A5** facets / 过滤：每个具体行业值命中 **≥4**、无 0 匹配值、且该行业至少有 1 条 `industry_note`（聚合表 + note id 列表）
- [ ] **A6** **断言零改动**：附 §1.4 三条命令的原始输出，证明没有任何断言被改（`git diff --stat -- tests/` 只允许出现新增文件）
- [ ] **A7** 契约不回归：`/library` 与 `/facets` 键集合不变；全套件 **0 failed**（847 + 新增），`skipped = 5`（否则用 `-rs` 名单解释）
- [ ] **A8** 文档：`docs/API.md` 六处 `45` 全部更新 + §11 加深说明；`TASKS.md 附录 R`；`make check-api-docs` 仍 `App-only 0`
- [ ] **A9** 提交：`git commit`（**不 push**）+ 短 hash 与文件清单落盘
- [ ] **A10** 合规与资源：`pyproject.toml` / `uv.lock` 零 diff；未碰 Onyx / compose / `.env`；`ece/demos/spa/**` 逐字节不变；临时 PG 已释放；收尾三查落盘；无密钥值；未 push
- [ ] **A11** 证据纪律：机器可校验（JSON / 哈希 / 计数 / 原始响应）；**无"内容更丰富""看起来更专业"这类不可判定表述**；不要求用户截图

## 7. 完成后的动作（严格按序）

1. 自检目录与证据完整性、无密钥泄漏、临时资源已清理（收尾三查）
2. `echo "$(date -Iseconds) OEI-014 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭；FAIL → 按 `R1/R2…` 返工后重建 `DONE`

---

## 8. 硬约束（违反即 FAIL）

- ✅ **授权改**：`src/ece/consulting/seed/consulting_objects.json`（**只新增**）、`docs/API.md`、`docs/DATA_MODEL.md`、`TASKS.md`、新增测试文件（可选）；可起临时 PG 跑套件；可 `git commit`（**不 push**）
- ❌ **不改既有 45 条的任何字段**；不删对象；**不改任何既有断言**（必须改 → 停手报 BLOCKED）
- ❌ 不新增词表值；不改 `ALLOWED_*`；不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）
- ❌ 不动 `ece/demos/spa/**`；不改 Onyx 上游 / compose / `.env`；不 restart / stop / down / rm 任何容器
- ❌ **不伪造内容与锚点**：不得用 `ai`/`public` 这类子串充当行业锚点；不得编造真实客户名或精确数字
- 📌 **资源纪律**：不需要真引擎（全程 `ECE_CONTENT_ENGINE=mock`）；临时 PG 验完即释放；收尾三查进 REPORT
- 📌 **穷尽性断言必须附命令**（OEI-011 v1.1 立的规矩）：本刀凡写"没有第七处""没有其它耦合"，都要附**可复现的命令与原始输出**

## 9. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-014/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-014/DONE`
- 无新文件则静默，不重复执行、不打扰用户
