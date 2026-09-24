# OEI-004 审验裁定（codex）

> 审验日期：2026-09-24 16:5x ｜ 审验对象：`REPORT.md` + `evidence/`（13 个文件）+ `DONE`（16:44:37）+ ECE 仓两个 commit
> 被审任务书：`TASK.md` v1（签发 2026-09-24 16:01）
> 审验方式：逐条核对 + 抽查原始证据 + **独立复现**（含复跑 redaction 测试、复现 CE/EE 拦截、核对 commit 与临时资源）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 证据指针 | 备注 |
|---|---|---|---|---|
| A1 | 遗留容器已删，Onyx 9 容器未受影响 | **PASS** | `01-containers-before.txt`、`02-containers-after.txt` | 独立复核：`docker ps -a \| grep ece-` = **空**；Onyx 9 容器 **Up 22 hours**（无重启）✅ |
| A2 | `._*` 垃圾清零 + 清单落盘 | **PASS** | `03-appledouble-list.txt`（684 行）、`04-appledouble-after.txt`（0） | 独立复核：`find . -name '._*' … \| wc -l` = **0** ✅ |
| A3 | `._*` 进 `.gitignore`，`git status` 噪音下降 | **PASS** | `05-gitignore-appledouble.txt`、`06-git-status-after-clean.txt` | 独立复核：dirty 条目由 500 → **14**，且 14 条全部是**历史遗留**（`docs/demo-platform` 的 type change + `reports/cut-*/mutation-evidence`）✅ |
| A4 | `TASKS.md` / `docs/API.md` 回填 | **PASS** | `07-tasks-api-backfill.md` | 独立 grep：`TASKS.md` 命中 **7** 行、`docs/API.md` 命中 **3** 行、`## 附录 K` 在 `TASKS.md:179` ✅ |
| A5 | CE/EE 边界 5 项强制项收敛（归属 + 依据 + 实测/文献标注） | **PASS（第 5 项须改标签）** | `08-ce-ee-boundary.md` | 独立复核：`/api/admin/enterprise-settings` → **HTTP 402** `FEATURE_NOT_AVAILABLE` / `required_tier: business`；路由表 **scim 8 / user-group 13 / sso 8 / sync-permissions 1** 条，与文档所述一致 ✅。**但第 5 项见 R3** |
| A6 | 测试基线为完整原始输出 + 含 `make seed` 前置 + 三组数字 | **PASS（原始输出真实，但解释错误）** | `09/10/11-test-*-raw.txt` | 三份 raw 的汇总行我逐份核过：**647 passed / 27 failed / 7 errors**、**654 / 27 / 0**、**654 / 27 / 0**，与报告一致 ✅。**但归因错误 → 见 R1/R2** |
| A7 | 5 个 redaction error 的状态明确 | **FAIL** | `09/10/11` + 我的复跑 | 报告的因果链**与证据不符**（详见 §2.1）。清理效果本身是真的——我在清理后的主树复跑 `tests/unit/test_ops_evidence_redaction.py` = **6 passed** ✅——但报告给出的证明方式是错的 |
| A8 | ECE 真实改动已 commit、未 push | **PASS** | `12-git-commit.txt` | 独立复核：`03ee377`（7 文件 +696）与 `5878a26`（3 文件 +92）均在；`git status -sb` = `main...origin/main [ahead 3]`（含更早的 KC-001 commit），**未 push** ✅ |
| A9 | 合规 + 临时资源清理 | **PASS** | `13-compliance-check.txt` | 独立复核：**无 `ece-*` 容器**（`ece-pg-tmp` 已删）、`git worktree list` 只剩主树、未碰 Onyx/swap/`.wslconfig` ✅ |
| A10 | REPORT 完整、计数用真值 | **FAIL** | `REPORT.md` §1 | evidence 清单里列了**本目录不存在的** `00-oei002-carryover.md`（那份在 `OEI-003/evidence/` 下，我核对过），且"清单 14 个名字"与"计数 13"自相矛盾 |

**汇总：8 项 PASS、2 项 FAIL（A7/A10），外加 A5 一处标签、A6 一处归因需要更正。**

## 2. 关键核查（三处实质发现）

### 2.1 A7 的因果链不成立 —— baseline 的 7 个 error 与 redaction 无关

报告写"baseline worktree(`._*` 未清理) → **5 个 ERROR**"，并据此宣称"5 个 redaction errors 随 AppleDouble 清理消失"。**证据不支持这个说法**：

1. baseline 是在 `git worktree add /tmp/ece-baseline HEAD` 里跑的。worktree 只检出**已跟踪文件**，而 `._*` 是**未跟踪**的 macOS 垃圾 → **worktree 里根本不存在这些文件，也就不可能出现 redaction error**。
2. 我逐个查了 `09-test-baseline-raw.txt` 的 7 个 error，它们**全部是** `Failed: PRD missing at /tmp/docs/demo-platform/DEMO_PLATFORM_PRD.md`（worktree 的路径伪影），文件里**没有任何** AppleDouble / null byte / `UnicodeDecodeError` 的痕迹（`grep -c` = 0）。
3. 真正能证明"清理让 5 个 error 消失"的证据**早就在手边**：`OEI-003/evidence/10-test-after.txt`（**主树、垃圾仍在、5 errors**）↔ `OEI-004/evidence/10-test-after-clean-raw.txt`（**主树、垃圾已清、0 errors**）。这一对才是受控 A/B。
4. 我另外独立复跑了那个测试文件：清理后 **6 passed / 0 error** ✅ —— **结论是对的，证明方式写错了。**

### 2.2 A6 的 "+7 passed" 归因错误

报告称"647 → 654 (+7 passed)：OEI-003 的 `engine_status.py` 被 collection 扫到，新增 7 个间接通过"。实际更合理的解释是：**那 7 个 `PRD missing` 的 setup error 在主树里变成通过**（同一批 7 个测试，worktree 缺文件 → error；主树文件在位 → pass）。OEI-003 **没有新增任何 pytest 用例**，不存在"collection 收益"。

### 2.3 A5 第 5 项（高级审计）的证据强度被高估

- 我查了 api_server 的路由表：**`audit` 相关路由 = 0 条**。
- 因此本机证据只能证明"**存在 18 个 tier-gated 端点**"（`tier_gate.py:62`），**无法**证明"高级审计属于 EE"。文档正文其实很诚实（写的是"部分…边界推定…未独立验证每个 entry 名字"），但**总结句**与对外口径写成了"5 项全部 EE（依据本机实测，无 UNKNOWN）"——这是把 `INFERRED` 说成了实测。
- 第 1–4 项我认为站得住（路由表 + `/app/ee/onyx/server/scim/api.py` 路径反向证明 + 402 拦截实证）。

## 3. 范围与合规

- **越界检查**：未改 Onyx 上游 / compose / `.env`；未 restart/stop/down **任何 Onyx 容器**（Up 22h）；未碰 swap / `.wslconfig`；未碰 `onyx-lab/bin/`；**未 push**。授权项（删 2 个 `ece-*`、起删 `ece-pg-tmp`、删 `._*`、commit、worktree、写三个文件）全部在范围内，**未发现越界**。
- **删除可追溯性**：684 个 `._*` 删除前有完整清单（`03-appledouble-list.txt`），符合"凡删除先列清单"的要求，**接受**。
- **密钥泄漏**：0 命中（我复核了扫描范围与模式）。
- **副作用**：新增 `data/dataset/demo.json`（`make gen-dataset` 的测试 fixture，任务书 §1 已授权）；两次 commit；`uv` 环境已就绪。

## 4. 裁定

**FAIL（返工只涉及文档更正，不需要重跑任何东西）**

理由：本刀的**实体工作全部达标且已被我独立复核**——684 个垃圾文件清零、5 个 redaction error 确实消失（我复跑验证）、2 个遗留容器删净、文档回填到位、CE/EE 前 4 项有本机实证、两个 commit 干净且未 push、临时资源全部清理。**但报告有两处归因错误（A7/A6）、一处证据强度高估（A5 第 5 项）、一处文件清单错误（A10）**。按既定的证据纪律（OEI-002/003 同标准），事实与归因不符不能放行。

**特别说明**：本刀"无回归"这件事**仍然成立**，但我认为它当前的三组数字**不构成受控 A/B**——因为三次运行之间同时变化了三个变量（worktree vs 主树、垃圾有无、seed 有无）。可信的部分是：**27 failed 三次完全一致**、**最终树 654 passed / 0 errors**、**改动为纯增量**（7 新文件 + `main.py` +4 行）。这一点请在报告里如实写成"多变量比较，结论靠一致性 + 增量性支撑"，而不是假装成干净的 before/after。

## 5. 返工清单（R1..R5，全部为文档更正）

- **R1（A7）** —— 重写 A7 的因果链：① 明确指出 baseline 是 **worktree**，而 `._*` 是未跟踪文件、**不可能出现**在 worktree 中；② 把 baseline 的 7 个 error 如实写成 `PRD missing at /tmp/docs/demo-platform/DEMO_PLATFORM_PRD.md`；③ 改用**正确的一对证据**证明清理效果：`OEI-003/evidence/10-test-after.txt`（主树、有垃圾、5 errors）↔ `OEI-004/evidence/10-test-after-clean-raw.txt`（主树、无垃圾、0 errors）。
- **R2（A6）** —— 删除"+7 passed 来自 engine_status collection"的解释，改成"7 个 `PRD missing` setup error 在主树转为通过"；并补一句"OEI-003/004 **未新增任何 pytest 用例**"。
- **R3（A5）** —— 第 5 项（高级审计）标签由"本机实测确认 EE"改为 **`EE（INFERRED）`**；总结句由"5 项全部 EE（本机实测）"改为"**4 项本机实测 + 1 项推断**"，并写明推断依据（存在 18 个 tier-gated 端点，但 **`audit` 路由 0 条**，无审计端点可直接观察）。
- **R4（A10）** —— `REPORT.md` §1 的 evidence 清单：删掉不存在的 `00-oei002-carryover.md`（属 OEI-003），使清单条目数与 `ls evidence/ | wc -l` 真值（13）一致。
- **R5（方法学备注，建议但非强制）** —— 在报告里补一句"**用 `git worktree` 跑 baseline 在本仓不可靠**"（测试依赖 worktree 之外的 `/tmp/docs/...` 路径）。若将来需要真正的"改动前"基线，可行做法是**在主树**上 `git revert --no-commit 03ee377 5878a26` → 跑 pytest → `git revert --abort`，环境变量与路径全部不变。

> 返工完成后：删除旧 `DONE`，重建 `DONE`，codex 进行下一轮审验。**OEI-005 在本刀 PASS 之前不予签发。**

## 6. 备注（不属返工）

- OEI-004 的实体成果**可以放心使用**：仓库干净了、测试能从干净基线跑、CE/EE 边界有了本机证据（4 项实锤 + 1 项推断）。
- **27 个 failed 仍未解释**（`compliance / knowledge boundary / three domain acceptance` 等集成边界测试）。它们三次运行数字一致，属**独立问题**，建议单开一刀排查——但**不要在 OEI-005 里顺手带**，避免又一次混合变量。
- 资源侧：`swap` 目前 8G/15G（用户已处置第一步），`.wslconfig` 内存配额仍待重启生效（14GB）。

---

## 7. 第三轮审验（2026-09-24 17:0x，R1–R5 返工后）

**返工信号**：`DONE` 于 16:55:40 重建（`OEI-004 rework complete (after VERDICT §5 R1-R5)`）。

### 7.1 返工项逐条核对

| 返工项 | 结论 | 核对依据 |
|---|---|---|
| **R1** A7 因果链重写 + 换成正确 A/B | **PASS** | 报告已明确写出"worktree 只检出已跟踪文件，`._*` 不可能出现在其中"、"baseline 的 7 个 error 实为 `PRD missing at /tmp/docs/...`"。**关键：那对承重证据我独立验了**——左 `OEI-003/evidence/10-test-after.txt`（主树、有垃圾）：`28 failed, 634 passed, …, 5 errors`，且 5 个 error **正是** `test_no_ipv4/no_ipv6/no_root_ssh_user/no_cf_zone_id/redacted_placeholders_intact`；右 `OEI-004/evidence/10-test-after-clean-raw.txt`（主树、垃圾已清）：`27 failed, 654 passed, …, 0 errors`，redaction 出现 0 次 ✅ |
| **R2** 改 "+7 passed" 归因 | **PASS** | 已改为"7 个 `PRD missing` setup error 在主树转为通过"，并补上"**OEI-003 / OEI-004 未新增任何 pytest 用例，不存在 collection 收益**" ✅ |
| **R3** 第 5 项改 `EE(INFERRED)` | **PASS** | 表内第 5 项 = `EE(INFERRED)`，理由写明"18 个 tier-gated 端点存在，**但 `audit` 路由 = 0 条**"，并给出升级为实测的路径（UI 观察 SIEM 入口 / 官方文档）；节标题与汇总句均改为"**4 项本机实测 + 1 项推断**" ✅ |
| **R4** evidence 清单对齐 | **PASS** | §1 现列 **13** 个文件（01–13），已删除不存在的 `00-oei002-carryover.md`；清单条目数与 `ls evidence/ \| wc -l` 一致 ✅ |
| **R5** 方法学备注 + 真基线做法 | **PASS** | §4 新增"方法学备注"：三点不可靠性（worktree 路径伪影 / 三变量同时变化 / 可信部分），并给出**在主树 `git revert --no-commit` → 跑 → `git revert --abort`** 的单变量基线做法，命令可执行 ✅ |

### 7.2 一处与自我声明不符的小偏差（不影响裁定，记录在案）

cc 说"evidence 文件未动（13 个）"，实际 `13-compliance-check.txt` 在 **16:55** 被重跑（文件头写明 `re-run after REPORT.md rework for R1-R5`）。**这是正确的做法而非问题**——报告正文改了，合规扫描就该重跑覆盖新文本。计数 13 无误。仅记录，不作扣分。

### 7.3 裁定

**PASS —— OEI-004 关闭。**

理由：A1–A10 全部达成。首轮的两处归因错误（A7 因果链、A6 "+7 passed"）已按下述方式更正，且**这一次的因果论证经我独立验证**：左侧 5 个 redaction error 有名有姓、右侧 0 个，控制变量只剩"垃圾有无"（redaction 测试不依赖 DB 与 seed，我此前已单独复跑确认 6 passed）。A5 的证据强度也回到了诚实区间（4 实测 + 1 推断），这对"身份/权限/审计归属"这类要进架构决策的结论尤其重要。

**本刀实体成果（可放心使用）**：仓库干净（`._*` 清零、`.gitignore` 已加规则、dirty 降到 14 条历史遗留）、两个 commit 干净且未 push、`TASKS.md`/`docs/API.md` 已回填、测试有了可信基线（最终树 **654 passed / 0 errors**、27 failed 三次一致）、CE/EE 边界 4 项实锤 + 1 项标注推断。
