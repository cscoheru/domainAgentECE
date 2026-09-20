# CODEX_ROUND3_CLOSEOUT_REPORT.md — 大刀收口最终报告

> Date: 2026-09-20
> 依据: Codex 第三轮补充判词（`blueprintECE/0920/codex第三轮补充判词及签发第一刀.md`）
> 授权范围: 工程与证据收口（**非**架构再设计）
> ece 仓 commit: `32a0b92` → 本轮追加（见 §6）

---

## 1. 判定

# **PASS**

七项工作全部完成。**无架构变更**：未新增 Kernel 对象，未扩大 26 行矩阵，未写 V3.x/V4，未新增 Adapter/Runtime 抽象，未重写 PRD。

**已知问题 3 条**（§5），均**不阻塞** V0 与 A/C 推进。

---

## 2. 七项工作逐条状态

| # | 判词要求 | 状态 | 证据 |
|---|---|---|---|
| 一 | 允许大刀、边界明确 | ✅ 遵守 | §6 diff —— 全部落在测试/脚本/文档/注释 |
| 二 | **P1 dependency coverage** | ✅ **已完成** | `P1_DEPENDENCY_MATRIX.md` + `db_state_fingerprint.sql`(SHA-256) + `db_surface_dump.sql` |
| 三 | 不增加第三臂；A/B/C 三分口径 | ✅ 已落实 | `EXPERIMENT_RECORD.txt` 的 A/B/C 三段；停用"严格因果证明" |
| 四 | 清理文档漂移 | ✅ 已完成 | 见 §4 |
| 五 | Production Gate 正式记账 | ✅ 已登记 | `TASKS.md` **附录 J**（PG-1） |
| 六 | 全仓 stale-state sweep | ✅ 已完成 | 见 §4 |
| 七 | 最终工程验收 | ✅ 已执行 | `FINAL_ACCEPTANCE/acceptance.txt` |
| 八 | 完成后 STOP | ✅ | 无自主扩展 |

---

## 3. P1 最终证据

### 3.1 Dependency coverage（判词 §二 —— 本轮最重点）

**方法**：从 `/permissions/check` 端点出发沿调用链反向列出每一个 DB 读取点，对照指纹覆盖范围逐项判定。

| 读取点 | 表 | 列 / 属性 | 指纹覆盖 |
|---|---|---|---|
| `api/identity.py:114-120` | `acl_entries` | 全部 10 列（含 WHERE 的 `object_type`/`object_ref`） | ✅ |
| `identity/parser.py:44-53` | `entities` | `id`, `display_id`, `name`, `entity_type`, `source_id`, `attributes.department` / `roles` / `is_management` | ✅ |
| `identity/parser.py:75-83` | `entity_aliases` | 全 9 列（`created_at` 除外，见下） | ✅ |
| `permissions/engine.py:218-222` | `entities` | `display_id`, `attributes->>'department'` | ✅ |
| `run_e2_permission.py` | — | **无 DB 访问**（grep 计数 = 0） | n/a |
| `/permissions/check` 写操作 | — | **无**（函数体内仅 1 处 execute，即 ACL SELECT） | n/a |

**判定：E2 读取的状态 ⊆ 指纹覆盖的状态 ✅**

### 3.2 发现并修复的 3 处指纹遗漏（未使用"应该没问题"式论证）

| 遗漏 | 处置 |
|---|---|
| `entity_aliases` 整表 | **已加入**（`resolve_identity` 读它；不依赖"check_permission 不消费 aliases"的论证） |
| `entities.id` (uuid) | **已加入**（`resolve_identity` 的 SELECT 列） |
| `acl_entries.id` / `note` | **已加入**（超集原则，现覆盖全 10 列） |

**同时升级**: md5 → **SHA-256**；输出改为 `<sha256>|<entities_rows>|<aliases_rows>|<acl_rows>`。
**唯一排除**: `entity_aliases.created_at`（volatile、不在读取集、引入无关噪声）—— 在 SQL 注释中**显式声明**，非静默忽略。

### 3.3 单变量实验结果

| 项 | 值 |
|---|---|
| F0（两臂前） | `13f4b221…b2b6\|435\|1\|3` |
| F1（ARM A 后） | 逐字符相同 |
| F2（ARM B 后） | 逐字符相同 |
| baseline commit | `c92316370b87343ba76c5776f9d56eb05e3f7be3` |
| fixed commit | `32a0b920b014c50543c92d826b00c262f11def9b` |
| dataset sha256 | `7f82340adcbca4118aae51ad20090a0c40fd75f8301e1e7cd59c2a9d5ca9670c` |
| runtime（两臂相同） | 宿主 uvicorn，同一 venv |
| DATABASE_URL | `postgresql+psycopg://ece:ece@localhost:5432/ece` |
| ARM A exit | **2**（4 暴露 + 4 失败） |
| ARM B exit | **0**（0 / 0） |

**A（已证明）**：固定 DB state + 固定 dataset + 相同 runtime 下，baseline/fixed **runtime 代码**的差异使 E2 由 4/4 变为 0/0。
**B（未测量）**：seed/数据层修复（RC-6/7/9）各自贡献 —— 两臂**共享**而非**对照**，故贡献恒为 0。
**C（若需回答 B）**：增设第三臂（baseline 代码 + baseline seed 产出的 DB）。本轮不必要。

复现: `bash scripts/run_p1_single_variable_experiment.sh`

---

## 4. 文档漂移清理（判词 §四 / §六）

**按判词点名的短语全仓搜索**，区分两类：

| 类 | 处置 | 数量 |
|---|---|---|
| **引用旧文并就地标注已修正**（findings/errata 记录） | ✅ 保留 | 8 处 |
| **把旧状态当作当前状态陈述** | ✅ **已清除/改写** | 12 处 |

**清除清单**：

| 文件 | 旧表述 | 现表述 |
|---|---|---|
| `README.md` | "下一阶段三动作（**必须同时进入**）" | A ∥ C 关系图 + "旧表述已作废" |
| `README.md` | "权限硬门未通过 / 5 暴露 + 5 失败" | "已修复（61/61）"，旧数为 *historical* |
| `README.md` | "建议优先修 Permission 硬门" | "C 可立即启动" |
| `MVP_SCOPE_V3.md` §3.4 | "现状 ❌ 实测未通过" | "✅ 已通过（61/61）" |
| `MVP_SCOPE_V3.md` §6.2 | "☐ Permission 暴露 = 0 ← 当前未通过" | "☑ … 已通过" |
| `MVP_SCOPE_V3.md` §9 | "G-C ❌ 未通过 / 建议优先" | "✅ 已通过（已关闭）" |
| `PRD_V3.md` §10 / §35 T4 / §37 G-C / §38.1 / §38.2 | "权限硬门未通过 / 5 暴露 + 5 失败 / 实测未达成" | 全部改为 ✅ 已通过 + *historical* 标注 |
| `EVIDENCE_V3_ADDENDUM.md` C47 | 作为当前状态 | 加 **HISTORICAL / SUPERSEDED** 标注（内容不删） |
| `A_CUSTOMER_VALIDATION.md` | "后面的 B 和 C 都不许拍板" | "A 与 C 并行；B 等 A" |
| `V3_CLOSEOUT.md` §4 | "必须同时进入" | 推进关系图（A ∥ C / B 等 A） |

**历史结果一律保留**，改为明确的 historical / superseded —— 未删除任何旧数据。

---

## 5. Remaining known issues（3 条，均不阻塞）

| # | 问题 | 影响 | 处置 |
|---|---|---|---|
| **K1** | `/permissions/check` 的 `req.user_ref` 允许调用者指定授权主体 | V0 不阻塞；**Production 阻塞** | 已登记为 **TASKS.md 附录 J / PG-1**（V0 允许 / Production 禁止） |
| **K2** | E3 / E4 / E5 runner 仍崩（`ContextPackage.get` / `asOf isoformat`） | Context 闭环的实测数字缺失 | R40R2.7，**未修**（不在本刀授权范围；每处约 2 行） |
| **K3** | ACL 模型无 `classification` 维度 | 若产品需 classification 相关 ACL，必须改模型 | 已在 `engine.py` 就地标注（**不要**再靠改数据集绕过） |

**本轮新发现并已修复（第 4 条，不遗留）**：

> **`demo:seed_departments` 被每个 pytest 运行静默删除且永不恢复。**
> 根因：wipe 谓词是 `LIKE 'demo:%'` 减一份**手工维护的豁免名单**（仅含 `demo:seed_temporal_roles`），
> 而 D001–D004 部门实体由 `scripts/seed_relationships.py` 创建 —— 被漏掉。
> **这是 RC-6 同一类缺陷的第 3 个实例**（前两个：`attributes.department` 被洗、R4 重名实体累积）。
> **修法**：谓词改为**精确匹配 `source_system = 'demo:demo'`**（即 `seed_from_demo_json` 实际写入的
> 来源），**豁免名单随之消失** —— 新的 `demo:*` 播种脚本不再可能被此测试破坏（自维护）。

---

## 6. 工程验收结果（判词 §七）

| # | 检查 | 结果 |
|---|---|---|
| 1 | 完整 pytest | **353 passed / 3 skipped / 0 failed**，exit 0（本地 live API） |
| 2 | E1 | **98.5%（64/65）**，PASS |
| 3 | E2 | **61/61，0 暴露 0 失败**，PASS |
| 4 | P1 单变量实验 | F0 == F1 == F2 ✅ |
| 5 | P1 dependency coverage | read-set ⊆ fingerprint ✅ |
| 6 | 实验前后 DB fingerprint | **E2 前后恒定**（[4b] before == after）✅<br>*跨 pytest 不恒定 —— 已归因：**100% 由 `entities.id` uuid 重生成解释**（[8] 聚焦实验：除 id 外内容完全一致）* |
| 7 | git diff | 无架构变更（见 §2 一） |
| 8 | 未提交临时文件/污染 | 重名实体 **0**；r4-test 残留仅保留的一对；pytest **幂等**（连跑实体数 439→439）✅ |
| 9 | 文档状态一致 | §4 清理后无已知冲突 |

原始输出：`ece/reports/eval-archive/2026-09-20-cut040R2/FINAL_ACCEPTANCE/acceptance.txt`
复现：`bash scripts/run_final_acceptance.sh`

> 关于检查 6 的诚实说明：`[0]` 与 `[4]` 两个指纹**必然不同**，因为 test_s14 与本轮的
> state-integrity 测试会 DELETE 全部 `demo:demo` 再重播，重播时 **uuid 重新生成**。
> 这不是缺陷（是该套件的既定设计），也**不影响** P1 —— P1 的恒定判定跨度是两次 **E2** 调用，
> 而 E2 runner 不写库（[4b] 已复验）。

---

## 7. git commit

| 仓 | commit | 内容 |
|---|---|---|
| `ece` | `32a0b92` → **本轮追加**（见提交记录） | P1'' SHA-256 指纹 + dependency matrix + 验收脚本 + 谓词修复 + TASKS 附录 J |
| `domainAgentECE` | **本轮追加** | 文档漂移清理 + 本报告 |

---

## 8. 是否 ready for independent audit

# **YES**

三项已知问题已全部登记或标注，不构成审计障碍。请按最终独立审验标准复核：

1. **P1 dependency coverage** 是否真的完备（`P1_DEPENDENCY_MATRIX.md` §2 的逐项判定）
2. **谓词修复**（`source_system = 'demo:demo'`）是否正确、有无副作用
3. **文档清理**是否彻底（有无我遗漏的旧表述）
4. **K1/K2/K3** 的处置是否恰当

审验目标（判词 §八）：**现有 V3 冻结架构 + V0 最小技术闭环，是否已达可正式进入 A 客户验证 + C Technical Spike 的状态。**

---

**Author**: Claude（Fable 5.1）
**Date**: 2026-09-20
