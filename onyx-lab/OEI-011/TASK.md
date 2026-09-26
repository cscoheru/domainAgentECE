# OEI-011 任务书 — 咨询内容补全（行业轴补齐 + 有界增量 + facets 真正可用）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-25
> 前置：`OEI-010` 已 **PASS 关闭**（见 `OEI-010/VERDICT.md`）
> 返工约定：本刀若需返工，一律标 **`OEI-011 R1` / `R2`**（不插新刀、不顺延既有编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动
>
> **v1 → v1.1 修订（2026-09-25，由 cc 的 BLOCKED 报告触发）**：**任务书 v1 自相矛盾，判定成立，不判 cc 返工。**
> cc 在 §1 停下来并指出：`tests/unit/test_consulting_seed_count.py:34-50` 的
> `test_type_distribution_matches_documented_targets` 用 **`==`** 钉死了六种类型的**精确**分布
> （`sum(expected) == 36 == 当前总数`），因此 **§6 A4 要求的任何增量都会让它变假**；而该文件
> **既不在 §3.4 的授权清单里，又被 §6 A9 的"其余断言零改动"冻结** → 两条要求互斥。
> **归因在我**：§1.5 那张表我写成"我逐个核过"却**漏了这一处**（我只 grep 了 `36`/`count`，没读全文件）。
> 本修订做的唯一实质改动：**把该处纳入授权，并按"KC-001 基线是下限、不是上限"改写**（详见 §3.4 / §6 A9）。
> cc 已产出的 `workspace/draft-*.{json,py}`（24 条标注 + 9 条新增，自检 A1 36/36 通过、A4 全达标）
> **可以继续使用**，不必重做——但最终必须在**真实 seed 文件**上重跑闸门。

## ✦ 开工指令（cc 必读：按序读完再动手）

> 你的会话记忆不可信任——**先按下面的清单读文件，再按本文档执行**。
> **`onyx-lab/` 顶层的一批文档已由用户并入 `onyx-lab/重启必读/`**（不是丢文件；`CODEX-ROLE.md` / `README.md` / `ASSET-INDEX.md` / `DECISION-ONYX.md` 仍在顶层）。

**① 按序必读（绝对路径，一份都别跳）**

```
1. /mnt/d/Projects/domainAgentECE/AGENTS.md                                  ← 项目总规则（角色、红线、Case First）
2. /mnt/d/Projects/domainAgentECE/onyx-lab/README.md                          ← 入口索引 + 目录变更 + "为什么 8080 看不到变化"
3. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/CC-ROLE.md                 ← 你的角色任务书
4. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/LOCAL-AGENT-PROTOCOL.md    ← 共享规则 + §5.1 资源纪律
5. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/OEI-ROADMAP.md             ← 路线图：**本刀条目下的"签发前置"两条 = 你的步骤 0**
6. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/VERDICT.md                  ← 上一刀裁定（PASS；§6 转出第 1、2 项就是本刀步骤 0）
7. /mnt/d/Projects/domainAgentECE/docs/demo-platform/CONSULTING_CONTEXT_KERNEL_KC001_TASK.md ← **本刀内容的原始契约**（36 个对象来源、字段表、建议分布、内容纪律）
8. /mnt/d/Projects/domainAgentECE/ece/tests/unit/test_consulting_seed_discipline.py ← **内容纪律闸门**（中文占比 / 客户匿名 / 合成标记 / 禁竞品名 / 数字示意化）——写新内容前先读
9. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-011/TASK.md                     ← **本文件 = 唯一任务来源**
```

**② 开工前先核对状态（只读，别凭记忆判断进度）**

```bash
cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-011 && ls -la     # DONE / VERDICT.md 都不该存在 = 正常开工
cd /mnt/d/Projects/domainAgentECE/ece && git log --oneline -3 && git status -sb | head -3
# 期望：HEAD = a463658（OEI-010），ahead 2，未 push
docker ps --format '{{.Names}}\t{{.Status}}'                      # 9 个 Onyx 容器 Up，restarts 应为 0
```

**③ 本刀一句话（细节见 §5 步骤与 §6 验收）**

把咨询知识库的**行业轴变成真的**：给 36 个既有对象补齐 `client_industry`（只加标注、**不改既有内容**），按**有界规则**新增 ~8–12 个对象把最薄的行业与类型补到可用，加一个 `cross_industry`（通用/跨行业）词表值让"通用方法"不必硬贴行业，并让 `GET /facets` 的行业下拉真正有东西可选。**不做** UI 改动（下拉是数据驱动的）、不改检索质量、不动引擎。

**④ 硬约束速查（违反即 FAIL，全文见 §8）**

- ✅ 本刀授权改：`src/ece/consulting/seed/consulting_objects.json`（补标注 + 新增对象）、`src/ece/consulting/metadata.py`（**只允许**给 `ALLOWED_INDUSTRIES` 加 `cross_industry` 一项）、`docs/API.md`、`docs/DATA_MODEL.md`、`TASKS.md`、`tests/**`（**只允许** §3.4 点名的那三处 + 步骤 0.1 那一处 + 新增文件）
- ❌ **不改 36 个既有对象的任何字段**（除 `client_industry` 的填充）；不改 id / title / summary / practice / engagement_phase / problem_types / methods / deliverables / outcomes / source_origin / confidence / review_state
- ❌ 不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）；不改 Onyx；不重启/停/删容器；不碰 `/mnt/c`
- ❌ **不动 SPA / UI**（`ece/demos/spa/**` 逐字节不变——行业下拉是数据驱动的）；不做检索调优（OEI-012）；不做客户验证材料
- ❌ 不得为了"凑满行业轴"给通用方法硬贴具体行业（见 §3.1）；**不得编造具体客户结果或精确数字**
- ❌ 验收不得要求用户截图；一切可见性用机器可校验证据
- 📌 **本刀不需要真引擎**：全程 `ECE_CONTENT_ENGINE=mock`（静态目录 + 词表，与引擎无关）；**不得**为了"日志上有 onyx"而开真引擎
- 📌 收尾跑一次全套件（需临时 PG），**验完即释放**；收尾三查写进 REPORT

**⑤ 收工与心跳**

```bash
echo "$(date -Iseconds) OEI-011 complete" > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-011/DONE
```

然后 **STOP**（不启动下一刀）。心跳对象 = `onyx-lab/OEI-011/VERDICT.md`；出现 PASS 即停，出现 FAIL 按 `R1..Rn` 返工（删旧 `DONE` → 修 → 重建 `DONE`）。

---

## 0. 一句话目标

让 `GET /api/v1/consulting/facets` 的**行业轴可用**：36 个既有对象的 `client_industry` 从 **24 个空**补到 **0 个空**，按**有界规则**新增对象把最薄的行业与类型补到可用阈值，并新增 `cross_industry`（通用/跨行业）词表值——**同时不伪造内容**：通用方法就标通用，案例必须落在真实行业。

**为什么是这一刀**（`AGENTS.md` §9 + 路线图阶段目标 + 我的实测）：

1. **用户常设约束第 3 条**：阶段目标以"**把咨询行业做实做透**"为准。行业轴是咨询知识库最直观的"做实"体现，而现在它是**空的**。
2. 我的实测（§1.1–§1.2）：36 个对象里 **24 个 `client_industry` 为空**；10 个行业里 **7 个只有 1 个对象**；`industry_note` 只有 2 条 → facets 的行业下拉**基本选不出东西**。
3. 这是**内容刀**，不是代码刀：它产出的正是 `AGENTS.md` §7 点名的自有 IP（**Domain Knowledge / Domain Ontology**），而且**不需要碰引擎**，是当前资源约束下性价比最高的一刀。

---

## 1. 现状（codex 实测，可直接信任；每条都带"文件 + 符号 + 数值"）

### 1.1 空缺**只在 `client_industry`**

`src/ece/consulting/seed/consulting_objects.json`（我逐条统计）：

| 字段 | 空值数 |
|---|---|
| **`client_industry`** | **24 / 36** ← 唯一的缺口 |
| `practice` / `engagement_phase` / `problem_types` / `methods` / `deliverables` / `outcomes` | **0 / 36** |
| `title` / `summary` / `id` / `type` / `source_origin` / `confidence` / `review_state` | **0 / 36** |

**类型分布**（= KC-001 任务书 `docs/demo-platform/CONSULTING_CONTEXT_KERNEL_KC001_TASK.md:97` 的"建议分布"，即现状就是基线，**不是上限**）：

| type | 现有 |
|---|---:|
| `case` | 10 |
| `methodology` | 10 |
| `proposal_play` | 6 |
| `deliverable_template` | 4 |
| `risk_check` | **4** |
| `industry_note` | **2** |

**其它维度现状**：`review_state` 全为 `approved`；`confidence` = high 22 / synthetic 9 / medium 5；`source_origin` = methodology_note 22 / synthetic_variant 9 / licensed_public 3 / founder_case 2；`engagement_phase` = diagnosis 25 / delivery 10 / proposal 8 / qualification 5 / implementation 4；`practice` 共 17 个取值（consulting_delivery 9 / operations 8 / strategy 7 / sales 6 / …）。

### 1.2 行业标注现状：10 个行业里 **7 个只有 1 个对象**

现有 13 个行业标注分布在 12 个对象上：`retail` 2 / `banking` 2 / `consumer_goods` 2 / `manufacturing` 1 / `technology` 1 / `public_sector` 1 / `logistics` 1 / `insurance` 1 / `energy` 1 / `healthcare` 1。

⇒ 在 facets 下拉里选"制造业"，只会命中 **1** 条。这就是"行业轴基本是废的"的具体含义。

### 1.3 词表封闭，且**没有"通用/跨行业"这一档**

- `src/ece/consulting/metadata.py:121` `ALLOWED_INDUSTRIES` = 10 个具体行业（banking / consumer_goods / energy / healthcare / insurance / logistics / manufacturing / public_sector / retail / technology）。
- `metadata.py:225+` 的 `_validate()` 对越界值**静默丢弃**并回 `_dropped`（上传路径用它兜底）。
- `docs/API.md:713` 写"`client_industry` | `ALLOWED_INDUSTRIES`（10 个）"；`docs/API.md:662` 写"必须落在既有 36 个种子对象的取值集合内（越界静默丢弃）"。
- ⇒ **今天无法诚实地标注"这条是通用方法"**：要么硬贴一个具体行业（伪造），要么留空（轴更空）。这就是要新开 `cross_industry` 的原因（§3.3）。

### 1.4 facets 是"值集合"（无计数）；前端是数据驱动的

- `src/ece/consulting/service.py:239` `_compute_facets()`：按 `_FACET_KEYS` 聚合**去重排序的值集合**（**不含计数**）；`_FACET_FIELD_MAP` 里有 `client_industries → client_industry`。
- `GET /api/v1/consulting/facets` → `{facets: {...}, total: int}`（`models.py:143 FacetsResponse`）。
- 前端 `demos/spa/app.js:261` 拉 `/api/v1/consulting/facets` 填充 `<select id="filter-industry">`（`demos/spa/index.html:192`）→ **数据驱动**：内容补齐后下拉自然变有用，**不需要改前端**。

### 1.5 数量断言：**四处硬钉死，两处 `>= 36`**（v1.1 已补第 [6] 处）

**v1 的这张表漏了最严格的一处**（由 cc 的 BLOCKED 报告指出，见 `OEI-011/evidence/00b-assertion-inventory.txt`）；下面是补齐后的**完整清单**，并附**可复现的盘点命令**（以后凡任务书写"清单完整"，都必须附命令）：

```bash
grep -rn '\b36\b' tests/            # 找硬编码的语料规模
grep -rn 'Counter(' tests/ --include=*.py   # 找对语料做计数的断言
grep -rn 'client_industries' tests/ --include=*.py   # 确认没有测试钉住行业取值（只钉 key 集合）
```

| 位置 | 断言 | 本刀是否可动 |
|---|---|---|
| `tests/unit/test_consulting_documents.py:263` | `static_catalog_size == 36` | ✅ 允许（声明式解冻） |
| `tests/unit/test_consulting_documents.py:315` | `static_catalog_size == 36` | ✅ 允许（同上） |
| `tests/unit/test_consulting_engine_merge.py:339` | `total == 36` | ✅ 允许（同上） |
| **`tests/unit/test_consulting_seed_count.py:34-50`** | **`actual[type] == expected[type]`（六种类型全 `==`）** | ✅ **v1.1 新增授权**（这是**唯一**会被增量打破的冻结点：`sum(expected) == 36`） |
| `tests/unit/test_consulting_seed_count.py:29` | `len(catalog.objects) >= 36` | ❌ 保持原样（本来就是加法式） |
| `tests/integration/test_consulting_api_contract.py:55` | `total >= 36` | ❌ 保持原样 |

**已确认不受影响（cc 另外核过，我复核过）**：`test_consulting_service.py:46`（`resp.total == methodology_count`，右值是**从目录算出来**的，不是硬编码）、`test_consulting_service.py:92`（`limit=5` 分页，增量后仍成立）、`test_consulting_api_contract.py:139-140`（`limit=3` 两页各 3 条，增量后仍成立）、`test_consulting_service.py:110/118`（只钉 facets 的**键集合**，并要求每个 facet 非空）、`test_consulting_documents.py:88-90`（`suggest_metadata` 单测，与语料规模无关）。**没有任何测试钉住行业取值本身**（只有 key 集合）。

### 1.6 内容纪律有**现成闸门**（新内容必须过）

- `tests/unit/test_consulting_seed_schema.py`：JSON 可解析、每条过 `KnowledgeObject` Pydantic 绑定、`type` ∈ 6 值、`source_origin` ∈ 4 值、`title`/`summary` 非空、id 唯一、`ConsultingCatalog.from_seed_path()` 可加载。
- `tests/unit/test_consulting_seed_discipline.py`：文案以中文为主；客户名必须脱敏（"某 + 行业 + 规模"这类）；**合成内容必须 `source_origin=synthetic_variant`**；禁竞品专有内容（麦肯锡/BCG/贝恩/埃森哲/德勤/PwC/EY/KPMG 等；公开框架名如 SWOT/Porter/7S/Lean/RACI 允许）；数字必须是示意性而非"精确结果"。

> **写新内容前先把这两个文件读完**——它们是本刀的客观裁判，不是"参考"。

### 1.7 回归基线

`OEI-010` 收尾时全套件 = **`847 passed / 0 failed / 5 skipped / 3 deselected`**（`OEI-010/evidence/12b-test-suite-raw.txt`）。**本刀基线是 0 failed，不允许出现任何失败。**

---

## 2. 范围锁

**做**：

1. **步骤 0**：清掉 `OEI-010` 转出的两项（§5 步骤 0）；
2. **给 36 个既有对象补齐 `client_industry`**（只加标注，不改其它字段）；
3. **有界新增对象**（≥8、总数 ≥44），把最薄的行业与类型补到可用；
4. **新增 `cross_industry` 词表值**（通用/跨行业）并同步文档；
5. **让 facets 的行业轴机检可用**（覆盖率 + 每个值 ≥2 命中 + 过滤实测）；
6. **有界解冻** §1.5 那三处数量断言；
7. 文档与提交。

**不做**（做了即越界）：

- **不收窄也不替换** 36 个既有对象的任何字段（**只允许填 `client_industry`**）；
- 不做 UI / SPA 改动（§1.4 已证明不需要）；不做检索调优（OEI-012）；不动引擎与记忆；不做客户验证材料；
- 不新增**第二个**词表值（`cross_industry` 是唯一一个）；不改 `ALLOWED_TYPES` / `ALLOWED_PHASES` / `ALLOWED_PROBLEM_TYPES` / `ALLOWED_METHODS`；
- 不引入新依赖；不改 Onyx。

---

## 3. 契约（**本刀锁定**：cc 按此实现；发现契约与实测不符 → 停手 + 写 REPORT + 等 codex 对齐）

### 3.1 既有 36 个对象的标注规则（**诚实性第一**）

1. 只允许修改 `client_industry` 一个字段；**其余字段逐字节不变**（A1 用哈希证明）。
2. 值的来源：`ALLOWED_INDUSTRIES ∪ {"cross_industry"}`（§3.3）。
3. **必须落在具体行业的**：
   - `type='case'`（案例发生在某个行业）→ 具体行业，**不得** `cross_industry`；
   - `type='industry_note'`（行业洞察）→ **恰好 1 个**具体行业，**不得** `cross_industry`。
4. **可以且应该**用 `cross_industry` 的：`methodology` / `proposal_play` / `deliverable_template` / `risk_check` 中**确实是通用方法/通用模板/通用风险清单**的对象。
5. **诚实性硬要求**：**不得**为了"把行业轴填满"而给通用方法硬贴具体行业。判断不了 → `cross_industry`。
6. **每个标注都要有依据**：依据必须能在该对象自己的 `title` / `summary` / `practice` / `methods` / `problem_types` 里定位（例：标题里写着"零售渠道" → `retail` 成立）。依据要落盘成表（§4 证据 `01`），**人可复核、机器可统计**。

### 3.2 新增对象规则（有界增量）

新增对象是 **KC-001 基线的增量**（不是替换）。硬目标（A4 机检）：

| 目标 | 阈值 | 现状 |
|---|---|---|
| 总数 | **≥ 44**（= 36 + ≥8） | 36 |
| 每个**具体行业**的对象数 | **≥ 2** | 7 个行业只有 1 |
| `industry_note` | **≥ 6** | 2 |
| `risk_check` | **≥ 6** | 4 |
| 标注了 `cross_industry` 的对象 | **≥ 10** | 0（词表里还没有这个值） |

新增对象必须：

- 过 §1.6 的两个闸门（schema + discipline）；**合成内容一律 `source_origin="synthetic_variant"`**；
- id 遵循既有约定 `<type 短名>-<slug>-<3 位序号>`（现有样例：`case-retail-procurement-diagnosis-001`、`methodology-swot-quick-001`、`industry-note-cn-banking-2026-001`），**不得与既有 id 冲突**；
- 每个字段都填满（`practice` / `engagement_phase` / `client_industry` / `problem_types` / `methods` / `deliverables` / `outcomes` 至少各 1 项，且全部落在既有词表内）；
- 不得编造真实客户名、真实结果或精确数字（§1.6）。

### 3.3 词表新增 `cross_industry`（唯一一项，且必须写清语义）

- `src/ece/consulting/metadata.py:121` 的 `ALLOWED_INDUSTRIES` 增加 `"cross_industry"`，并在其注释里写明语义：**通用 / 跨行业**（不针对特定行业的方法、模板、风险清单）。
- **不新增第二个值**；不改其它词表常量。
- 同步文档：`docs/API.md`（§11 facets 说明 + §12 上传词表那张表，含 `docs/API.md:662` 与 `:713` 两处措辞）。
- 上传路径的词表校验**行为不变**（仍"越界静默丢弃 + `_dropped`"）：给一次实测（合法值通过、越界值仍被丢弃）。

### 3.4 数量断言的解冻边界（**只有这四处，且必须声明**；v1.1 补入第 4 处）

- 允许改（**四处，不多不少**）：
  1. `tests/unit/test_consulting_documents.py:263` — `static_catalog_size == 36`
  2. `tests/unit/test_consulting_documents.py:315` — `static_catalog_size == 36`
  3. `tests/unit/test_consulting_engine_merge.py:339` — `total == 36`
  4. **`tests/unit/test_consulting_seed_count.py:34-50`** — 六种类型的 `actual[t] == expected[t]`
- **改法（统一原则：KC-001 的分布是"下限基线"，不是"永远不许增长"）**：
  - 前三处：`== 36` → **`>= 36`**，并写明"OEI-011 后实际为 N 条；`>=36` 是守住 KC-001 基线的下限，不是钉死数量"。
  - 第 4 处：六个 `==` → **`>=`**（保持那六个数作为**每个类型的下限**），**并同步改 docstring**：原写"（exact）"要改成"floors（KC-001 基线）"，再补一句"OEI-011 之后实际为 {…}"。**不得**删掉这条测试——它的原意（"不许把某一类悄悄做没"）必须留住。
  - 建议在这条测试里再加一行**自洽断言**（可选但推荐）：`assert sum(expected.values()) <= len(catalog.objects)`，把"下限之和不得超过总数"显式化。
- **KC-001 的历史任务书 `docs/demo-platform/CONSULTING_CONTEXT_KERNEL_KC001_TASK.md` 不要改**（那是历史契约）；新的实际分布写在 `TASKS.md 附录 Q` 里。
- 其余断言**一律不得改**（含 §1.5 表格里标 ❌ 的两处）。

### 3.5 facets 的"可用"定义（机检）

- `GET /api/v1/consulting/facets` 的 `client_industries` **包含全部 10 个具体行业 + `cross_industry`**（前提是每个值确有对象）；
- **不存在"0 匹配"的值**：对 `client_industries` 里的**每一个**值，`GET /api/v1/consulting/library?client_industry=<v>` 都必须命中 **≥2** 个对象（这就是"拉出来能选"）；
- 每个对象 `client_industry` **非空**（36 + 新增）；
- 给"facets 值 → 命中数"的聚合表（机器可算，落盘）。

---

## 4. 工作区与证据命名

```
onyx-lab/OEI-011/
├── TASK.md      ← 本文件（只读）
├── workspace/   ← 源文件/素材（标注依据表、新增对象草稿、统计脚本）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

建议证据文件：`00-step0-transfer-fixes.txt`、`01-industry-annotation-basis.json`、`02-existing-36-unchanged-hashes.txt`、`03-new-objects-list.json`、`04-coverage-targets.json`、`05-facet-value-match-counts.json`、`06-library-filter-per-industry.json`、`07-vocabulary-cross-industry.txt`、`08-seed-gates-raw.txt`、`09-count-assertion-diff.txt`、`10-contract-regression.txt`、`11-test-db-free-raw.txt`、`12-test-suite-raw.txt`、`13-git-commit.txt`、`14-compliance-check.txt`

## 5. 任务步骤

### 步骤 0 — 清 `OEI-010` 的两笔转出（先做）

1. **`tests/integration/test_s32_assembly.py:92`**：`assert r[0] in ("entity", "relationship")` 已因 OEI-010 往 `context_items` 加 `item_kind='memory'` 而**过窄**（复现见 `OEI-010/evidence/12c-s32-item-kind-fragility.txt`）。二选一：把 `"memory"` 加入集合，或改断言其**真正的不变量**（每行 `decision ∈ {allowed,denied}` 且 `reason` 非空）。**该断言在 OEI-010 被冻结，现由本刀解冻**；改了要在 REPORT 里声明。
2. **`docs/DATA_MODEL.md §4.2`**：`idx_memories_scope_owner` 的列序写成 `(owner_ref, scope)`，迁移 `0010_memories` 实际是 `(scope, owner_ref)` → 订正文档。
3. 证据：`00-step0-transfer-fixes.txt`（两处 diff + 说明）。

### 步骤 1 — 补齐既有 36 个对象的 `client_industry`（A1/A2/A3）

1. 逐个判断并填写（规则见 §3.1）。**只动这一个字段。**
2. 产出**依据表**：每条 = `id / type / title / 原值 / 新值 / 依据（引对象内哪个字段的哪句话）`。落盘 `01-industry-annotation-basis.json`。
3. 产出**"既有 36 个对象只加了这一个字段"的哈希证明**：对每个对象，除 `client_industry` 外的所有字段做规范化 JSON 哈希，**对照 `git show a463658:src/ece/consulting/seed/consulting_objects.json` 的原值**，逐条相等。落盘 `02-existing-36-unchanged-hashes.txt`。

### 步骤 2 — 有界新增对象（A4/A5）

1. 按 §3.2 的目标新增（建议 8–12 条），优先补：**只有 1 个对象的 7 个行业**（manufacturing / technology / public_sector / logistics / insurance / energy / healthcare）与 **`industry_note` / `risk_check`** 两个薄类型。
2. 每条新增对象都要过 §1.6 的两个闸门；逐条通过记录落盘 `08-seed-gates-raw.txt`。
3. 落盘 `03-new-objects-list.json`（id / type / industry / 目标理由）与 `04-coverage-targets.json`（每个目标的前后对照：总数、每行业数、类型数、cross_industry 数）。

### 步骤 3 — 词表加 `cross_industry`（A6）

1. 按 §3.3 改 `metadata.py` + 两处文档。
2. 实测上传路径的词表校验行为不变（合法值通过 / 越界仍丢弃），落盘 `07-vocabulary-cross-industry.txt`。

### 步骤 4 — facets 与过滤的可用性实测（A7/A8）

1. `GET /api/v1/consulting/facets` → 落盘 `client_industries` 全量值 + 每个值的命中数（`05-facet-value-match-counts.json`）；
2. 对**每个**行业值跑一次 `GET /api/v1/consulting/library?client_industry=<v>`，记录命中数（`06-library-filter-per-industry.json`），**每个 ≥2**；
3. 抽样验证 `GET /api/v1/consulting/objects/{id}` 对一条新增对象仍可取。

### 步骤 5 — 数量断言有界解冻（A9）

1. 按 §3.4 改那**四处**（含 `test_consulting_seed_count.py:34-50` 的类型分布，六个 `==` → `>=` + docstring 同步）→ 落盘 diff（`09-count-assertion-diff.txt`）。
2. **改完后重跑你的盘点命令**（§1.5 的三条 grep），把输出与原清单对照，证明**没有第七处**、且只动了清单里的四处；把这次重跑落盘（`09b-assertion-inventory-after.txt`）。
3. 在 REPORT 声明"除此之外零断言改动"。

### 步骤 6 — 契约不回归（A10）

1. `/library` 的既有键集合（`items/total/limit/offset/facets` + 既有对象字段）与 `/facets` 的键集合**逐键对照**：只允许**值集变化**，不允许**键变化**；落盘 `10-contract-regression.txt`。
2. 先跑相关子集（consulting 相关单测 + API 契约），再收尾跑**一次**全套件并落盘原始汇总（对照 §1.7 的 847 基线）。

### 步骤 7 — 文档与提交

1. `docs/API.md`（§11 facets 语义 + §12 词表含 `cross_industry`）、`TASKS.md`（附录 Q）、必要时 `docs/DATA_MODEL.md`；
2. `git add` + `git commit`（**不 push**），落盘短 hash + 文件清单（`13-git-commit.txt`）；
3. 收尾三查（`pgrep` / `docker ps -a` 无残留、内存快照），落盘 `14-compliance-check.txt`。

---

## 6. 验收标准（codex 将逐条核对；**每条都必须能被 evidence 证明**）

- [ ] **A0** 步骤 0 两项转出已清（s32 断言 + DATA_MODEL 列序），改动有 diff 与说明，且在 REPORT 明确声明
- [ ] **A1** **既有 36 个对象只加了 `client_industry`**：逐对象"除该字段外全部字段"的规范化哈希与 `a463658` 原值**逐条相等**（给出 36/36 的对照输出）
- [ ] **A2** 覆盖率：36 + 新增对象的 `client_industry` **全部非空**，且值 ∈ `ALLOWED_INDUSTRIES ∪ {cross_industry}`；`case` 与 `industry_note` **没有** `cross_industry`（脚本主动扫一遍并报 0 违规）
- [ ] **A3** **依据可查**：每个新填/新增的行业标注都有依据列，且依据能在该对象自身字段里定位（给出依据表 + 抽样若干条人工可核对的原文）
- [ ] **A4** 覆盖目标达成：总数 **≥44**；每个**具体行业 ≥2**；`industry_note ≥6`；`risk_check ≥6`；`cross_industry ≥10`（前后对照表）
- [ ] **A5** 内容纪律：`test_consulting_seed_schema.py` 与 `test_consulting_seed_discipline.py` **全绿**；新增对象逐条过闸门（原始输出落盘）；**无竞品名 / 无真实客户名 / 无精确数字**。（⚠️ 你 `00-draft-plan-verification`/`01-draft-plan-verification.txt` 里那两条 `kc001_schema::…` 名义失败是**草稿夹具/路径导致的假失败**，不是内容问题——但最终证据必须是在**真实 seed 文件**上跑出来的全绿原始输出，不接受"草稿里过了"）
- [ ] **A6** 词表：`cross_industry` 已加入 `ALLOWED_INDUSTRIES` 且在 `metadata.py` 注释与 `docs/API.md` 两处写明语义；**未新增第二个值**；上传路径词表校验行为不变（合法/越界各一次实测）
- [ ] **A7** facets 可用：`client_industries` 含全部 10 个具体行业（+`cross_industry`），**不存在 0 匹配的值**，且给出"值 → 命中数"聚合表
- [ ] **A8** 过滤实测：**每个**行业值各跑一次 `/library?client_industry=<v>`，均 200 且命中 **≥2**（原始响应摘要落盘）；抽样验证新增对象可经 `/objects/{id}` 取到
- [ ] **A9** 数量断言**有界**解冻：只有 §3.4 点名的**四处**（三处 `== 36` → `>= 36`；`test_consulting_seed_count.py:34-50` 六个 `==` → `>=` + docstring 同步）与步骤 0.1 的 `test_s32_assembly.py:92` 一处被改，且每处都带注释说明"为何是下限不是钉死"；**其余断言零改动**——给出 ① `git diff`、② **改后重跑的盘点命令输出**（`09b-assertion-inventory-after.txt`，证明没有第七处）
- [ ] **A10** 既有契约不回归：`/library` 与 `/facets` 的**键集合不变**（只允许值集变化）；consulting 相关子集全绿；**全套件 0 failed**（≤ 847 基线 + 新增测试）
- [ ] **A11** 文档：`docs/API.md`（§11 + §12）、`TASKS.md 附录 Q` 已更新，且 `make check-api-docs` 仍为 `App-only 0`
- [ ] **A12** 提交：`git commit`（**不 push**）+ 短 hash 与文件清单落盘
- [ ] **A13** 合规与资源：`pyproject.toml` / `uv.lock` **零 diff**；未碰 Onyx / compose / `.env`；**未改三域业务断言**（除 A9 三处）；`ece/demos/spa/**` **逐字节不变**；临时 PG 已释放；收尾三查落盘；无密钥值落盘；未 push
- [ ] **A14** 证据纪律：全部机器可校验（JSON / 哈希 / 计数 / 原始响应）；**不使用"内容更丰富""看起来更专业"这类不可判定表述**；**不得要求用户截图**

## 7. 完成后的动作（严格按序）

1. 自检目录结构与证据完整性、无密钥泄漏、临时资源已清理（收尾三查）
2. `echo "$(date -Iseconds) OEI-011 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并等 codex 签发下一刀；FAIL → 按 `R1/R2…` 返工后重建 `DONE`

---

## 8. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：改 `src/ece/consulting/seed/consulting_objects.json`（补标注 + 新增对象）、`src/ece/consulting/metadata.py`（**只加 `cross_industry` 一项**）、`docs/API.md`、`docs/DATA_MODEL.md`、`TASKS.md`、`tests/**`（**只允许** §3.4 那**四处** + §5 步骤 0.1 那一处 + 新增文件）；可起临时 PG 跑套件；可 `git commit`（**不 push**）
- ❌ **不改 36 个既有对象的除 `client_industry` 外的任何字段**（A1 逐条哈希对照）；不删既有对象
- ❌ 不新增第二个词表值；不改 `ALLOWED_TYPES` / `ALLOWED_PHASES` / `ALLOWED_PROBLEM_TYPES` / `ALLOWED_METHODS`
- ❌ **不动 `ece/demos/spa/**`**（逐字节不变）；不做检索调优 / 记忆 / 引擎改动；不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）
- ❌ 不改 Onyx 上游 / compose / `.env`；不 restart / stop / down / rm 任何容器
- ❌ **不伪造内容**：通用方法不得硬贴具体行业；不编造真实客户名或精确结果；合成内容必须 `source_origin="synthetic_variant"`
- ❌ 不改三域业务断言；不删既有测试；不得要求用户截图
- 📌 **资源纪律**：本刀**不需要真引擎**（全程 `ECE_CONTENT_ENGINE=mock`，不得为了"日志上有 onyx"而开真引擎）；临时 PG / uvicorn / 反代**验完即释放**；收尾三查写进 REPORT

## 9. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-011/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-011/DONE`
- 无新文件则静默，不重复执行、不打扰用户
