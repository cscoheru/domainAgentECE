# OEI-014 收口报告 — 咨询内容加深（行业锚点 + 每行业 ≥4 + 行业说明补齐）

- **任务书**：`onyx-lab/OEI-014/TASK.md`（v1，A0–A11 共 12 条验收）
- **裁决者**：codex（架构/审验）；本报告作者：`cc`（Worker）
- **基线**：`c30e50e`（OEI-011 的收口 commit）
- **交付 commit**：`a3d61cd`（**未 push**）
- **日期**：2026-09-26
- **一句话**：把 10 个具体行业从各 2 条加深到各 **4** 条（45 → **65** 条），补齐
  `insurance` / `public_sector` / `technology` 缺失的 `industry_note`，并把"行业锚点"
  从"关键词表说它像"换成**词边界安全、可机检、有牙**的规则 —— 全程**只新增**，
  既有 45 条整对象逐条哈希不变，**一条既有断言都没改**。

---

## 0. 本刀实际改了什么（3 个文件）

| 文件 | 改动 | 证据 |
|---|---|---|
| `src/ece/consulting/seed/consulting_objects.json` | **只追加 20 条**（45 → 65）；既有 45 条**整对象**逐条 sha256 不变 | `01b`、`01c`、`04` |
| `docs/API.md` | 6 处计数 `45` → `65`、行业轴对照表加 OEI-014 列、可用性保证从 **≥2** 升为 **≥4 + note 覆盖** | `10`、`14` |
| `TASKS.md` | 新增 **附录 R** | `10` |

**没改**（本刀§8 明令冻结，全部机检为零 diff，见 `12-compliance-check.txt`）：
`src/ece/consulting/metadata.py`（词表一字未动）、`tests/**`（**一条既有断言都没改**）、
`pyproject.toml` / `uv.lock`（无新依赖）、`ece/demos/spa/**`（逐字节不变）、
引擎 / 检索 / 记忆 / 三域业务断言、Onyx 上游 / compose / `.env`。

---

## 1. 逐条验收（A0–A11）

### A0 — 锚点扫描器落盘且**有牙** ✅

`workspace/anchor_scan.py`。规则（§3.3）：①锚点必须落在对象**自己的 `title` 或
`summary`**；②ASCII 关键词用 `\b...\b`（大小写不敏感）；③只收具体行业词，
`ai` / `public` / `tech` / `制造(业)` / `供应链`·`supply_chain` / `运输` 一律不算判据。

**两类对照**（`00-anchor-scanner-and-false-positives.txt`）：

- **能报**：真实锚点命中，例如 `case-banking-credit-approval-014` → `banking@title←信贷`、
  `banking@summary←城商行`；20 条新增对象共报出大量命中。
- **能拒**：§1.3 的 4 条假阳性**全部**报"无锚点"：

| 对象 | 假阳性来源 | 严格扫描 |
|---|---|---|
| `methodology-value-chain-003` | `practice` 里的 `supply_ch**ai**n` | 无锚点 ✓ |
| `methodology-lean-waste-walk-005` | **`summary`** 里的"用于**制造业**与服务运营场景" | 无锚点 ✓ |
| `methodology-benchmarking-public-010` | `methods` 里的 `public_benchmark` | 无锚点 ✓ |
| `risk-check-data-availability-001` | `problem_types` 里的 `data_av**ai**lability` | 无锚点 ✓ |

**这条规则不是"限定 title/summary"就够了**：`lean-waste-walk-005` 的假命中**就在 summary 里**，
所以"具体词"规则（③）是必须的第二道。这点在 TASK 与附录 R.1 里都写明了。

**扫描器自检**（`test_teeth()`）：注入一个正例（"某城商行信贷审批" → 必须报 `banking`）
与一个反例（含 `supply_chai n` / `data_avai lability` 的串 → 严格模式必须**报不出**），
并断言 4 条回归样例仍无锚点。另有 `--loose` 对照模式，可**复现**附录 Q 的全部 4 条假阳性
——证明两个模式的差异确实来自词边界与词表，而不是实现坏了。

### A1 — 既有 45 条零改动 ✅

`01b-existing-45-unchanged-hashes.txt`：既有 45 条**整对象**（全字段，sorted keys）
规范化 JSON 的 sha256 与 `c30e50e` **逐条相等 45/45**。
本刀是**纯新增刀**，所以要求的是**整对象**相等，不是附录 Q 那种"除某字段外相等"。

`01c-seed-diff-stat.txt`：`git diff --numstat` = **713 插入 / 0 删除**。
**但 diff 行匹配可能是巧合**（超行内容相同），所以它**不是**主证据 —— 主证据是上面的哈希。
本报告明确区分这两者，不拿"diff 看起来只有新增"当结论。

写盘前还有两道守卫（`workspace/apply_increment.py`）：
①种子文件必须能被它**自己的序列化器** `json.dumps(..., ensure_ascii=False, indent=2)`
**逐字节**复原（否则一次重写会顺手重排未改动的对象，哈希对照就失去意义）；
②开工前文件必须与 `c30e50e` **完全一致**（无其它漂移）。两道都通过才写的盘。

### A2 — 加深目标达成 ✅（`04-coverage-before-after.json`）

| 目标 | 阈值 | 前（45） | 后（65） | 达标 |
|---|---|---|---|---|
| 总数 | 65 ≤ N ≤ 70 | 45 | **65** | ✅ |
| 每个具体行业 | ≥ 4 | 全 = 2 | **全 = 4** | ✅ |
| 每个具体行业有 `industry_note` | ≥ 1 | **3 个行业为 0** | **10 个各 1** | ✅ |
| `deliverable_template` | ≥ 6 | 4 | **7** | ✅ |
| `cross_industry` | ≥ 10 | 26 | **26** | ✅ |

类型分布（后）：case **20** / methodology **12** / industry_note **9** / risk_check **9** /
proposal_play **8** / deliverable_template **7** —— 附录 Q 立下的每类型下限（10/10/6/4/4/2）
全部继续满足。

### A3 — 锚点纪律 ✅（`03-anchor-basis.json`、`06-anchor-scan-final.txt`）

每条新增对象都给出：**锚点词 + 所在字段 + 原句（anchor_sentence）**，
并机检该锚点是**该对象自身 `title`/`summary` 的子串**。**20/20 有锚点**。
10 个行业各有 2 条新增对象，每条都给出锚点（不止两个行业）。

机器可卡的门槛：`anchor_scan.py --require workspace/new-ids.txt` → 20/20，exit 0。
**这条门槛有牙**（反证见 `13-reproducibility.txt`）：喂一条没有锚点的 id 进去 →
`*** 缺: methodology-value-chain-003 ***`，**exit 1**。

### A4 — 内容纪律 ✅（`05-seed-gates-raw.txt`）

`test_consulting_seed_schema.py` + `test_consulting_seed_discipline.py`
在**真实文件**（65 条）上全绿，原始输出落盘。
交付后**重跑**，输出逐字节相同（`13-reproducibility.txt`）。

> 交付前先在**内存**里把"既有 45 + 草稿 20"过了一遍同样的闸门（`workspace/verify_draft.py`），
> 全绿才写盘 —— 避免"写错再回滚"。但内存预演**不算 A4 的证据**，A4 的证据是真实文件上的输出；
> 且 `verify_draft.py` 明确列出两个**读文件**的用例（`test_seed_bundle_is_valid_json`、
> `test_catalog_can_load_seed_without_error`）在内存校验里**跑不了**，不当作跑过。

### A5 — facets / 过滤 ✅（`07-facet-and-filter.json`）

走**真实 HTTP 面**（`fastapi.testclient`，DSN 指死端口、`ECE_CONTENT_ENGINE=mock`）：

| 保证 | 实测 |
|---|---|
| 每个取值命中 ≥ 1（无 0 匹配值） | 11/11 通过 |
| **每个具体行业命中 ≥ 4** | 10 个行业各 **4** |
| **每个具体行业命中 ≥ 1 条 `industry_note`** | 10/10 |
| **note id 集合：API vs 种子逐 id 相等** | 10/10 |

最后一行是防"接口能查、内容其实没有"的交叉验证：把
`GET /library?client_industry=<v>&type=industry_note` 返回的 id 集合，与直接从种子文件
按同条件筛出的 id 集合比较，**逐 id 相等**。`cross_industry` 26 条不计入"≥4"（它是通用档），
但计入"≥1"。

### A6 — 断言零改动 ✅（`01d-assertion-inventory-after.txt`）

硬判据：`git diff c30e50e HEAD -- tests/` = **零 diff**（diff 行数 0，改动文件数 0）。
既没有改断言，也没有新增测试文件。
另附 §1.4 三条盘点命令在**交付态**的原始输出（`\b36\b` / `Counter(` / `client_industries`）。

**这里有一处必须先自曝的坑**：我最初想用 `grep -rn '== *36' tests/` 判断"有没有 `==36` 断言"，
它返回 **3** 条，于是脚本打印出"必须为 0"却显示 3 —— 看上去像本刀违规。实际这 3 条
**没有一条是断言**：一条是 `assert _period_to_seconds("h") == 3600.0`（被当成 `== 36` 子串），
另两条是**注释和 docstring** 里在引用旧写法。**能匹配注释的 grep 不算判据** ——
改用 AST（只看真正的 `==` 比较，操作数是常量 36）：

```
CODE-level `== 36`: (none)
```

复现命令已写进 `01d-assertion-inventory-after.txt`。结论：**代码层面 `== 36` 出现 0 次**，
本刀新增 20 条**没有撞到、也不需要改任何断言** → **无 BLOCKED**。

### A7 — 契约不回归 + 全套件 ✅（`08-contract-regression.txt`、`09-test-suite-raw.txt`）

`/library`、`/facets` 的**键集合**与 `c30e50e` 的 `LibraryResponse` / `FacetsResponse` /
`KnowledgeObject` 字段**逐键相等**（AST 取字段名 + 运行时取真实响应键，两路对照）；
`items[0]` 的键集合与 `KnowledgeObject` 一致。变化的是**值集**（`total` 45 → 65），不是键集。

全套件（全新 PG + 完整文档化前置链 + `-rs`）：

```
847 passed, 5 skipped, 3 deselected, 5 warnings in 243.79s (0:04:03)
```

`0 failed`；5 条 skip **全部带名字**，且与 OEI-011 收口时**逐字相同**
（2 × `test_e2_permission.py` 的 e2 runner 退出码 3；3 × `test_s5_5_real_llm.py` 缺
`ECE_LLM_BASE_URL`）—— 都是本机既有环境缺口。**OEI-011 那次 846/6 的偏差没有复现。**
本刀不新增测试文件，故 passed 与基线同为 847，符合 §1.7。

> **链日志里有一行会骗人，必须点名**：`chain.txt` 第 3 行印的是
> `commit under test: c30e50e...`。那是因为脚本用 `git rev-parse HEAD` 打印，而**跑套件时
> 本刀还没 commit**。真正被跑的是**工作区**——即写入 20 条新对象之后的内容。
> 这不是"我觉得"：跑套件时工作区 seed 的 sha256 = `d093562c…`，与交付 commit `a3d61cd`
> 的 blob **同一个哈希**，与 `c30e50e` 的 `b6e7045b…` 不同。详见 `09` 末尾那一节。

### A8 — 文档 ✅（`10-docs-changes.txt`、`14-check-api-docs.txt`）

`c30e50e` 版 `docs/API.md` 里带计数的 `45` 共 **6 处**（行 495 / 499 / 531 / 604 / 717 / 732），
**全部** → `65`；另加第 635 行对照表加 OEI-014 列、§11 补"OEI-014 加深到 65 条 / 每行业 ≥4 /
每行业 ≥1 条 `industry_note`"的说明，并把可用性保证从 **≥2** 升级为 **≥4 + note 覆盖 + id 一致**。

**有意保留、未改的 `45`（4 处）**：499 行的"来历"叙述（历史）、637 行 OEI-011 那一列
（`0 / 45` 是历史事实）、609 / 804 行的脚本名 `cut_045_local_origin.py`（**不是计数，是文件名**，
改了就是改错）。这 4 处**逐条判定过**，不是漏改。

`TASKS.md` 新增**附录 R**。`make check-api-docs` 仍 `App-only: 0`（`14`）。
`docs/DATA_MODEL.md` 本刀**未涉及**，零 diff（任务书写的是"若涉及再改"）。

### A9 — 提交 ✅（`11-git-commit.txt`）

`a3d61cd`，**只含 3 个文件**（= §8 白名单），短 hash 与文件清单落盘。
冻结面逐路径核对为 0（`pyproject.toml` / `uv.lock` / `demos/` / `src/ece/migrations/` /
`metadata.py` / `tests/` / `reports/` / `docs/demo-platform/`）。
**未 push**：`git log @{u}..HEAD` 显示 4 个 commit 全在本地。

### A10 — 合规与资源 ✅（`12-compliance-check.txt`）

- `pyproject.toml` / `uv.lock` **零 diff**（无新依赖）。
- 未碰 Onyx / compose / `.env`：`/home/codex` 对本用户 `readable=NO writable=NO`；
  9 个 `onyx-*` 容器 uptime 19 小时，**长于本会话**，即"未重启"的机检形式。
- `ece/demos/spa/**` 逐字节不变（零 diff）。
- 临时 PG `ece-pg-oei014` 已 `docker rm -f` 释放；`docker ps -a` 里 `ece-*` 计数 **0**。
- 收尾三查（进程 / 容器 / 内存快照）落盘：无残留 uvicorn、无反代、无遗留 pytest/uv，
  55432 未在监听。
- 无密钥值：关键词扫描**有牙**（命中即分类并**遮蔽**，命中的是那个一次性临时库口令，
  非项目凭据）；另有第二条 URL 形态扫描（`scheme://user:pass@host`），
  4 处命中全部是 127.0.0.1 临时库的 DSN，值已遮蔽。
- **内存快照如实报，不粉饰**：`Mem: 13Gi total / 184Mi free / 1.6Gi available`、
  `Swap: 7.4Gi used`。这是 Onyx 栈的既有压力，本刀只贡献了一个已删除的 PG 容器；
  快照是**删除之后**取的。报告写"干净"而数字不是这样，比不做检查更糟。

### A11 — 证据纪律 ✅

全部证据是机器可校验的：JSON（`02`/`03`/`04`/`07`）、规范化 sha256（`01b`）、
计数（`04`）、原始 HTTP 响应（`07`/`08`）、原始测试输出（`05`/`09`）、
`git` 原始输出（`10`/`11`）、`docker`/`ps`/`free` 原始输出（`12`）。
**没有**"内容更丰富""看起来更专业"这类不可判定表述；**未要求用户提供任何截图**。

---

## 2. 全套件（收口跑次）

```
$ uv run pytest -m "not eval and not eval_llm" -rs        # = make test 的确切命令 + -rs
847 passed, 5 skipped, 3 deselected, 5 warnings in 243.79s (0:04:03)
```

环境：全新 `postgres:16-pgvector`（127.0.0.1:55432），走完整文档化前置链
（`alembic upgrade head` → `gen_dataset.py` → `make seed` → 四个 fixture seeder），
`ECE_CONTENT_ENGINE=mock`。容器跑完即删。

**`make seed-fixtures` 仍未使用**：它的 recipe 里 `@echo` 的反引号未转义，
shell 会做命令替换，导致该 target **顺带把整套测试跑一遍**（预先存在的 Makefile 缺陷，
非本刀引入，本刀未修）。四个 seeder 直接调用 —— Makefile 注释与 `README.md:79`
都写明两者等价。

---

## 3. 过程中值得记下的三件事

### 3.1 `-q` 会把汇总行吞掉（第二次踩到同一个坑）

重跑种子闸门时，我给了命令行一个 `-q`，而 `pyproject.toml:50` 的 `addopts` 已经有 `-q`
→ 变成 `-qq` → **汇总行消失，只剩点号进度条**。当下我差点把"一行点号"当成通过。
改用 `-o addopts="" -q` 才拿到 `15 passed`。
**这是 OEI-011 那条教训（"看不到汇总行的通过不算证据"）在另一个地方的复现。**

### 3.2 交付后重跑，四个证据文件**逐字节相同**

`05`/`06`/`07`/`08` 是在 **commit 之前**生成的。commit 不改文件内容，所以它们"理应"仍然成立
—— 但**"理应"不是证据**。commit 之后重跑生成命令，与已落盘文件 `cmp` 逐字节比对：
4/4 IDENTICAL（`13-reproducibility.txt`）。若任何一个不同，那份证据会打印 `*** DIFFERS ***`
与前 12 行差异 —— 这个检查不会在失败时保持沉默。

### 3.3 严规则在**既有对象**上有两处假阴性（必须自曝）

扫描器对全部 65 条做体检时打印出：**2 条既有对象带了具体行业，但严格规则在
title/summary 里找不到锚点**——

- `case-manufacturing-supply-resilience-003`：title 是"某**制造业**客户供应链韧性评估"。
  `制造业` 被 §3.3.2 明令排除（因为它可以是在讲"**用于**制造业与服务运营场景"这种**范围**）。
  但在这一条里，"某制造业客户"**就是**在说客户的行业。**同一个词，一处是范围、一处是所属
  —— 纯字符串规则区分不了。**
- `case-public-sector-org-redesign-005`：title 是"某**公共部门**组织架构梳理"。
  `公共部门` **根本不在**我的 public_sector 词表里（收的是 政府/政务/事业单位/国企/机关/
  公共服务/一网通办/政务大厅/财政）。这是**词表覆盖不足**，不是规则本身的问题。

**这两条本刀不能改**（纯新增刀，既有 45 条一个字段都不许动），也不该假装没看见。它们
**不是本刀引入的问题**：OEI-011 的标注依据规则允许依据落在 `practice`/`methods`/`problem_types`，
严格度本来就低于本刀对**新增对象**的要求。

**更该说的是**：新增 20 条做到 20/20 有锚点，**部分是因为我拿着锚点词表写的**（说白了有点"应试"）。
所以 20/20 的正确读法是"**没有一条新增对象越过了我设的这道下限**"，
**不是**"扫描器是一个可信的行业分类器"。它有已知假阴性（上两条），也有已知的假阳性空间
（不在词表里的具体行业词如"教育"/"地产"根本不会被任何行业认领）。

---

## 4. 转出（不在本刀范围内，明确交出去）

1. **`test_consulting_seed_count.py` 的 docstring 仍描述 OEI-011 的现值（45）**。
   §8/A6 明令不得改任何既有测试文件，故未同步。**它不影响判定**（下限断言 `>=` 对 65 条
   依然成立，全绿），但**现值以 `TASKS.md 附录 R` 与 `04-coverage-before-after.json` 为准**。
2. **附录 Q.6 的三条遗留原样带过来**：
   - `industry-note-cn-consumer-2026-002` 带 2 个具体行业（§3.1.3 说 `industry_note` 应"恰好 1 个"）
     —— 收窄既有对象需**显式授权**；
   - `methodology-mckinsey-7s-004` 的 **id 里含竞品名**（小写 `mckinsey`），内容纪律闸门不扫 id
     故不违规，但 id 不体面；改 id 属改既有对象，本刀无权；
   - 行业轴仍只有 10 个具体行业 + 1 个通用档；扩 `ALLOWED_INDUSTRIES` 是**第二项词表变更**，
     本刀明令不做。
3. **`case` 已 20 条、`industry_note` 已 9 条**，都显著高于 KC-001 的建议分布。
   下一刀若继续加深，需先想清楚"加深到什么程度算够"，否则内容会开始注水。
4. **锚点扫描器仍只是证据工具**（在 `onyx-lab/OEI-014/workspace/`，未进 `ece/`，无新依赖）。
   要把它变成**长期内容闸门**，至少需要：补词表覆盖（`公共部门` 一类）、
   为"范围义 vs 所属义"设计比字符串更强的判据、以及给既有对象一次**显式授权**的复核。
   本刀的任务书虽允许新增测试文件，但 A0–A11 未要求，故**未擅加**。

---

## 5. 证据索引（`onyx-lab/OEI-014/evidence/`）

| 文件 | 对应 |
|---|---|
| `00-anchor-scanner-and-false-positives.txt` | A0 两类对照 + `--loose` 复现 4 条假阳性 |
| `01-assertion-inventory-c30e50e.txt` | 步骤 1 断言重盘（`c30e50e` 上） |
| `01b-existing-45-unchanged-hashes.txt` | **A1** 45/45 整对象哈希相等 |
| `01c-seed-diff-stat.txt` | **A1** `713 / 0` numstat |
| `01d-assertion-inventory-after.txt` | **A6** 交付态重盘 + AST `== 36` 判据 + `tests/` 零 diff |
| `02-new-objects-list.json` | 20 条新增（id/type/行业/理由） |
| `03-anchor-basis.json` | **A3** 每条的锚点词 + 字段 + 原句 + 子串机检 |
| `04-coverage-before-after.json` | **A2** 前后对照 + 五项硬门槛机检 |
| `05-seed-gates-raw.txt` | **A4** 两个闸门在真实文件上的原始输出 |
| `06-anchor-scan-final.txt` | **A3** 最终扫描（含 65 条的完整体检与两处假阴性） |
| `07-facet-and-filter.json` | **A5** 逐行业命中数 + note id 列表对照 |
| `08-contract-regression.txt` | **A7** 键集合逐键对照（pre-cut vs HEAD） |
| `09-test-suite-raw.txt` | **A7** 全套件原始输出 + 5 条 skip 名单 + `c30e50e` 误导行澄清 |
| `10-docs-changes.txt` | **A8** 改动面清单 + 完整 diff + 开工前脏文件的分离 |
| `11-git-commit.txt` | **A9** commit、文件清单、冻结面 0、未 push |
| `12-compliance-check.txt` | **A10** 收尾三查 + 仓库足迹 + 密钥扫描 |
| `13-reproducibility.txt` | 交付后重跑逐字节相同 + `--require` 反证 + 两处假阴性自曝 |
| `14-check-api-docs.txt` | **A8** `App-only: 0` |

工作区脚本：`anchor_scan.py`（扫描器 + 自检）、`draft_new_objects.py` / `draft-new-objects.json`
（内容草稿）、`verify_draft.py`（内存预演）、`apply_increment.py`（带守卫的写盘）、
`verify_api.py`（真实 HTTP 面实测）、`fresh_db_chain.sh`（完整前置链 + 全套件）、
`compliance_check.sh`（收尾三查）、`new-ids.txt`。

---

## 6. 结论

A0–A11 **12 条全部达成**。总数 45 → **65**；10 个具体行业**各 4 条**；
`insurance` / `public_sector` / `technology` 的 `industry_note` **已补齐**（10/10）；
锚点规则**词边界安全、有牙、可机检**，4 条已知假阳性全部被正确拒掉；
**既有 45 条整对象哈希逐条不变**，**一条既有断言都没改**，**契约键集合不变**，
全套件 **847 passed / 5 skipped / 3 deselected / 0 failed**，无新依赖，
临时资源已释放，**未 push**。

两处必须留在纸面上的诚实：①链日志里那行 `commit under test: c30e50e` 是**时序造成的显示错误**，
真正被测的是交付内容（哈希对得上）；②严规则在**两条既有对象**上有假阴性（`制造业`/`公共部门`），
且新增对象的 20/20 部分源于"拿着词表写"——它是一道**下限**，不是一个可信的分类器。

**STOP** — 本刀到此结束，不启动下一刀。
