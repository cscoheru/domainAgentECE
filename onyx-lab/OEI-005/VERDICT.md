# OEI-005 审验裁定（codex）

> 审验日期：2026-09-24 18:0x ｜ 审验对象：`REPORT.md` + `evidence/`（13 个文件）+ `DONE`（17:56:08）+ ECE commit `dd58297`
> 被审任务书：`TASK.md` v1（签发 2026-09-24 17:04）
> 审验方式：逐条核对 + 抽查原始证据 + 独立复现（pytest 汇总行、FAILED 行数、`ERROR` 出现次数、commit 与 diff、容器状态）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 证据指针 | 备注 |
|---|---|---|---|---|
| A1 | 起点复现，与"27"不一致要解释 | **PASS** | `02-repro-27-fail-raw.txt` | 独立复核：该文件 **恰好 48 行 `FAILED`**、汇总行 `48 failed, 633 passed, …`。"48 vs 27"的解释成立——本刀 baseline 刻意只跑 `alembic upgrade head`，缺 `make seed` 的 demo 实体，故多出 23 条；补 `make seed` 后落到 25（`04-*`），与 OEI-004 的 27 清单（减去自愈的 temporal 2 条）吻合 ✅ |
| A2 | 增量表完整 + 每步 raw 输出 | **PASS（有已声明的折衷）** | `03/04/05/06/07-*` | 每个 seeder 的 stdout 均落盘（03/05/06/07 尾部可见各自 self-check：`OK — all counts within tolerance`、`SELF-CHECK PASSED — all 8 fixture entities present`、`CTL-001 3 evidence / 3 systems …`）。缺点是 3 个 fixture seeder 的 pytest **合并成一次**，故 step2/3/4 的逐条归属是**推断**而非逐步实测 → 见 R3 |
| A3 | 48 条逐条有归属 + 最小复现命令 | **PASS** | `09-triage-table.md` 附录 A3 | 48 行明细表，每行 = nodeid + 分类 + 消解步骤 + `DATABASE_URL=$DB uv run pytest "<nodeid>"` ✅ |
| A4 | 残留红灯归类，且未改产品代码/测试 | **PASS** | `REPORT.md` §A4、`12-git-commit.txt` | 残留 1 条 = `test_cut_045_local_origin_smoke`（`_wait_for_http` 超时，需 nginx + `web/dist` 完整部署栈），归 **(a) 环境/范围外**，并给出两条最小修复方案但**未实施**。独立复核：`git diff --stat HEAD~1 HEAD -- src/ece tests` **为空** ✅ |
| A5 | Makefile 新目标 + README 前置链，未改既有语义 | **PASS** | `10-makefile-diff.txt`、`ece/Makefile:103,115` | 独立复核：`seed-fixtures:`(103) 与 `test-integration:`(115) 均存在；`git show` 的删除行**只有 `.PHONY` 那一行**（加目标必须改声明列表），**任何既有 recipe 未动** ✅ |
| A6 | 最终基线 raw + "27 → N" 真实数字与逐条去向 | **FAIL** | `11-final-baseline-raw.txt` | 数字本身全对（`1 failed, 680 passed`，独立复核一致），但 §A6 的句子**过计 1 条**：写"27 清单中 **25 条**被 `seed-fixtures` 消掉"，而其中 `cut_045` **并未消解**，真实是 **24 条**（与 §0 表的 `−24`、A3 表的"未消解"自相矛盾）→ R2 |
| A7 | 单变量纪律（主树 + 同 PG + 同环境，无 worktree） | **PASS** | 各 raw 的 traceback 路径 | 4 次运行 traceback 路径均为 `/mnt/d/Projects/domainAgentECE/ece/...`，**未使用 `git worktree`** ✅ |
| A8 | 改动已 commit、未 push、临时 PG 已删 | **PASS** | `12-git-commit.txt` | 独立复核：`dd58297 chore(OEI-005): make integration test fixture prerequisites discoverable`；`git status -sb` = `ahead 4`（未 push）；`docker ps -a` 中 **0 个 `ece-*`** ✅ |
| A9 | 合规 | **PASS** | `13-compliance-check.txt` | 扫描 0 真实凭据值；自己还把本文件纳入二次扫描并正确识别出 2 处"模式常量自匹配"（严谨）。**`/mnt/c` 只读探测已如实披露**（一次 `ls`、零写入、零复制、最终草稿已删该行）——对"确认 `.wslconfig` 未被修改"这个目的属合理最小动作，**接受** ✅ |
| A10 | 报告完整、无手写数字、明确回答真缺陷数 | **FAIL** | `REPORT.md`、`09-triage-table.md` | 报告明确回答"**0 个真缺陷**"✅，但 `09-triage-table.md` 的 `errors` 列在**四行全部写 5**，而四份 raw 的汇总行都是 `5 warnings`、且 `ERROR` 字符串在 02/04/08/11 中出现次数**均为 0**（即真实 errors = **0**）→ R1 |

**汇总：8 项 PASS、2 项 FAIL（A6/A10）。**

## 2. 独立复现（codex 自己跑的核对）

| 核对项 | 结果 |
|---|---|
| 四次运行的汇总行 | `02`: 48 failed / 633 passed；`04`: 25 / 656；`08`: 1 / 680；`11`: 1 / 680 ✅ 与报告表格一致 |
| `02` 的 FAILED 行数 | **48** 行 ✅（与汇总行一致，非手写） |
| 四份 raw 中 `ERROR` 出现次数 | **0 / 0 / 0 / 0** ⚠️ 与 triage 表的 `errors=5` 矛盾 → R1 |
| 残留失败 | 仅 `test_cut_045_local_origin_smoke::test_deployment_smoke_passes_against_local_origin` ✅ |
| 三步骤 seeder 确实各自写了 fixture | `05` 有 `Total temporal relationships in DB: 3`；`06` 有 `SELF-CHECK PASSED — all 8 fixture entities present … KM-POL-001 valid+requires_hr`；`07` 有 `CTL-001 3 evidence / 3 systems … DENY acl on comp-eve` ✅ |
| 产品代码 / 测试是否被动过 | `git diff --stat HEAD~1 HEAD -- src/ece tests` = **空** ✅ |
| Makefile 既有 recipe | 删除行只有 `.PHONY` 一行 ✅ |
| 现场容器 | 9 个 Onyx 容器在跑、`ece-*` 残留 **0** ✅ |

**算术自洽性检查（我算的）**：`48 = 23（make seed 消掉）+ 24（3 个 fixture seeder 消掉）+ 1（cut_045 未消解）` ✅；对应 OEI-004 的 27 清单：`24 被 fixture seeder 修掉 + 1（cut_045）未消解 + 2（temporal）本刀未复现 = 27` ✅。

## 3. 范围与合规

- **越界检查**：未改产品代码、未改测试（`git diff` 为空，独立复核）；未改 Onyx 上游 / compose / `.env`；未 restart/stop/down/rm 任何 Onyx 容器；未碰 swap / `.wslconfig`（只读探测已披露）；未 push。**未发现越界。**
- **密钥泄漏**：0 真实命中。
- **副作用**：新增 `ece/Makefile` 两个目标 + `README.md` 一段（commit `dd58297`，+72/−1）；临时 PG 与 worktree 均已清理。

## 4. 裁定

**FAIL（返工仅需改两处数字 + 补一句归属性质的澄清，不需重跑任何东西）**

理由：**本刀是迄今质量最高的一刀**——根因判断（"红灯全部来自前置未跑"）被分步实验证实：48 → 25 → 1，且残留那条被准确定性为部署栈缺失、给出修复方案但守住"不改测试"的边界；`0 真缺陷` 这个结论我完全采信。**但有两处数字与原始证据不符**（triage 表的 `errors=5`、§A6 的"25 条被消掉"），且都与我自己写的验收条款（A6/A10）直接冲突；按既定纪律，数字对不上不能放行——尤其本刀的**全部价值就是这个数字链条**。

## 5. 返工清单（R1..R3，全部为文档更正）

- **R1（A10）** —— `09-triage-table.md` 的 `errors` 列：四行**全部改为 `0`**（true value），并加一行说明"初版误把汇总行里的 `5 warnings` 读成了 errors；四份 raw 中 `ERROR` 出现次数均为 0"。同时把该列的来源写成"引自各 raw 的 pytest 汇总行"。
- **R2（A6）** —— `REPORT.md` §A6 的"27 清单中 **25 条**被 `seed-fixtures` 消掉"改为 **24 条**，并明确 `cut_045` 属"未消解（范围外）"；确保与 §0 表的 `−24`、`09-triage-table.md` 的"未消解(范围外,不改测试)"三处一致。
- **R3（A2 澄清）** —— 在 §A2 的偏差说明与 `09-triage-table.md` 的注里补一句：**step 2/3/4 的逐条归属是基于"失败测试所需的 `source_system` 与各 seeder 的 self-check 输出"做的推断**（`km:v0-knowledge-fixture` → knowledge seeder；`comp:v0-compliance-fixture` → compliance seeder），**不是**每个 seeder 后单独跑 pytest 实测所得——避免读者把 A3 明细里的"消解于 步骤3-5 (05/06/07)"误读为三次分别实测。

> 返工完成后：删除旧 `DONE`，重建 `DONE`，codex 进行下一轮审验。**OEI-006 在本刀 PASS 之前不予签发。**

## 6. 备注与后续建议（不属返工）

1. **回归信号现在真的可用了**：期望基线 = `1 failed / 680 passed`（那 1 条是部署 smoke）。**任何多于 1 的失败都是真回归** —— 这句话建议同时写进 `ece/README.md` 的前置链段落，后续每刀都按它判断。
2. **建议单独开一小刀收尾那条部署 smoke**（属"测试与环境不匹配"类）：或加 `pytest.skip` 前置检查，或在部署流水线里跑。**不要塞进 OEI-006**，避免又一次混合变量。
3. `test_s4_5_temporal` 的"in-process 自愈 fixture"与新增的显式 `seed_temporal_roles` 前置存在语义重叠，建议在后续刀里评估保留哪一个（本刀不动测试是对的）。
4. 用户侧待办不变：`wsl --shutdown` 让 14GB 配额生效（不阻塞）；CE/EE 官方文档 URL 待网络可达时补。

---

## 7. 第二轮审验（2026-09-24 18:1x，R1–R3 返工后）

**返工信号**：`DONE` 于 18:06:41 重建（`OEI-005 complete (rework R1-R3 done, docs only)`）。

### 7.1 返工项逐条核对

| 返工项 | 结论 | 核对依据 |
|---|---|---|
| **R1** `errors` 列改 0 + 说明误读 | **PASS** | 三个有数值的单元格（baseline / 2.1+2.2 / 2.5）已全部改为 **`0`**；表下新增来源说明块，写明"初版把汇总行末尾的 `5 warnings` 误读成 errors，四份 raw 中 `ERROR` 行数与 `errors` 词频均为 0"，并逐条列出四份 raw 的汇总行原文 ✅ |
| **R2** "25 条" → 24 + 标明 `cut_045` 未消解 | **PASS** | §A6 已改为 **24 条**并给出 `9+7+6+1+1 = 24` 的分解；紧接着写明"**1 条 `cut_045` 属未消解（范围外）**"；并补对账 **`24 + 1 + 2 = 27`** ✅。三处口径已一致：§0 表 `−24` / §A6 `24` / `09-triage-table.md` 的"未消解(范围外,不改测试)" |
| **R3** 补归属性质澄清 | **PASS** | §A2 新增「归属性质澄清(VERDICT R3)」块：明确那 24 条是**推断归属**，依据三条独立线索（失败报错要求的 `source_system` ↔ seeder 契约、各 seeder 的 self-check 输出、`04 → 08` 的 `FAILED` 集合差），并说明**无法再细分到单个 seeder**（2.3/2.4/2.5 之间无中间态）✅ |

### 7.2 独立复核

- **未重跑 pytest 属实**：`02`(17:10) / `04`(17:16) / `08`(17:21) / `11`(17:29) 四份 raw 的 mtime **未变**；返工只碰了 `REPORT.md`(18:06)、`evidence/09-triage-table.md`(18:05)、`evidence/13-compliance-check.txt`(18:06)、`DONE`(18:06) ✅
- **合规重扫合规**：`13` 为返工后重扫（0 命中），并主动记录了"REPORT.md 命中行号由 105 变 112（§A2/§2/§5 增补后下移），命中性质不变"——这是我在多刀里见过最细的一次证据自洽处理 ✅
- **全文残留扫查**：`grep '25 条'` 只命中两处"更正说明"本身；`errors = 5` 残留 **0** 处 ✅

### 7.3 逐条验收更新

| # | 首轮 | 二轮 | 说明 |
|---|---|---|---|
| A1–A5 | PASS | **PASS** | 无变化 |
| **A6** | FAIL | **PASS** | "25 条"已更正为 24，并与 §0/A3 三处对齐，附 27 的对账式 |
| A7–A9 | PASS | **PASS** | 无变化 |
| **A10** | FAIL | **PASS** | `errors` 列更正为真实值 0，且把误读原因写清 |

### 7.4 裁定

**PASS —— OEI-005 关闭。**

理由：本刀的实质结论与证据链全部成立，且我在两轮里都独立复核过：**48 → 25 → 1 的分步实验真实、每个 seeder 的 self-check 输出在案、`git diff src/ece tests` 为空（产品代码与测试一行未动）、commit `dd58297` 未 push、临时 PG 已清**。首轮的两处数字错误（把 `5 warnings` 读成 errors、"25 条被消掉"）已按原始证据更正，且更正方式是"贴出四份汇总行原文 + 给出对账式"，不是简单改数。

**本刀最重要的一句话（后续每刀都按它判断）**：

> **回归基线 = `1 failed / 680 passed`。那 1 条是 `test_cut_045_local_origin_smoke`（部署栈缺失，与环境有关）；任何多于 1 的失败都是真回归。**

### 7.5 遗留（不阻塞）

1. **`cut_045` 部署 smoke**：属"测试与环境不匹配"，最小修复已记录（加 `skip` 前置检查或 CI 里 `--ignore`）。**建议与将来那刀"公网 526 / VPS 部署"合并处理**，不要单独为它插一刀。
2. `test_s4_5_temporal` 的 in-process 自愈 fixture 与新增的显式 `seed_temporal_roles` 前置语义重叠——留待后续刀评估保留哪一个（本刀不动测试是对的）。
3. 用户侧：`wsl --shutdown` 让 14GB 配额生效（不阻塞）；CE/EE 官方文档 URL 待网络可达时补。
