# OEI-008 审验裁定（codex）

> 审验日期：2026-09-25 09:5x ｜ 审验对象：`REPORT.md` + `evidence/`（17 个文件）+ `DONE`（09:18:44）+ ece commit `3fb0723`
> 被审任务书：`TASK.md` v1（签发 2026-09-25）｜ 返工约定：一律标 **`OEI-008 R1`**（不插新刀、不顺延编号）
> 审验方式：逐条核对 + 独立复现（Port 契约、审计路径、两个被改测试文件的 diff、**worktree 对照实验**）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 核对依据 |
|---|---|---|---|
| A0 | 步骤 0（R1 + TASKS 对账） | **PASS** | `OEI-007/DONE` 已于 00:01 重建且我已二轮判定 PASS；本提交含 `TASKS.md +110/−?` 对账改动，`00b-tasks-reconcile.txt` 有前后统计 |
| A1 | Port 五方法全部带身份、类型可缺省、docstring 说明 | **PASS** | `port.py` 头部逐条列出五方法签名含 `caller=None`；并写明"身份用于 **audit**，不是 enforcement；per-result 强制在 ECE 侧" ✓ |
| A2 | 调用方不再手抄引擎判断 | **PASS** | `engine_merge.py` 注释改为"reads `engine.engine_name` from the Port **rather than mirroring** `selector.get_content_engine()`'s switch"；镜像逻辑已删 ✓ |
| A3 | mock 身份可观测 + 确定性 | **PASS** | `02`：`engine_name=mock`、`caller_param_on_all_methods=True`、`audit_log_summary.rows=7` 覆盖 5 个方法、匿名上传被拒 ✓ |
| A4 | onyx 接受身份 + 每次调用留痕 + 记录 CE 限制 | **PASS** | 见 §2 D1（审计路径已补全，我独立读码确认）；CE 限制见 `07-*` ✓ |
| A5 | 四调用点接线 + 缺身份策略有明文且实测一致 | **PASS** | `05-*` 十种组合逐条实测：library/status/engine_status 匿名 200；**upload 匿名 403 `identity-required`**；`upload_bearer→403` 因本环境未配 `ECE_JWT_SECRET`（报告已说明，属预期）✓ |
| A6 | 审计留痕可用（who/what/when/result） | **PASS（附 D3 裁定）** | 审计现覆盖**成功与失败全部出口**（见 §2）；形态为**进程内** `audit_log`，非持久表 —— 见 §3 的 D3 裁定 |
| A7 | `07-ce-permission-limitation.md` 存在且含 ≥3 缓解方向 | **PASS** | 该文件有 M1–M3 缓解表（per-result filter + 严格 top_k + 一致性计数 / snippet 脱敏 / 等），并写明"只写不实现" ✓ |
| A8 | DB 无关单测通过 + 无回归 | **FAIL** | 新文件 `test_content_engine_identity.py` **确实 DB 无关**（我实测 20 passed）；但**被本刀改过的 `tests/unit/test_consulting_documents.py` 失去了 DB 无关属性**——见 §2 的对照实验 |
| A9 | 文档与提交 | **PASS** | `docs/API.md §13`（契约/匿名策略/CE 限制/审计形态/为何删镜像）+ `TASKS.md`；commit `3fb0723` 12 文件 +1054/−112；`ahead 2` 未 push ✓ |
| A10 | 合规 | **PASS** | `12-*`：凭据值级扫描（含正对照）、9 容器 `restarts=0`、`pyproject`/`uv.lock` **0 diff**（我复核 grep 为空）、`origin/main` 仍 `7ab17fc` 未推进 ✓ |
| A11 | 不使用用户截图 | **PASS** | 证据全部机器可校验；报告无"请用户截图" ✓ |

**汇总：10 项 PASS、1 项 FAIL（A8）。**

## 2. codex 独立复现

| 复现项 | 方法 | 结果 |
|---|---|---|
| **D1 缺陷是否真存在、是否真修好** | 读 `onyx_adapter.py` 的 `engine_status` / `search` 全函数，看 `_audit` 与 `return` 的先后 | **确认修好**：`engine_status` 的 `ok` 审计在 87 行、`return` 在 89 行（此前是 `return` 之后再审计 = 死代码）；`search` 成功路径在 48 行写 `result="ok", hits=N`、50 行才 return；失败分支 5 条齐全 ✓ |
| 审计写到哪、是否持久 | 读 `_audit` 实现 + `git log -S 'def _audit'` | 写 `self.audit_log`（**进程内 list**）；`def _audit` **由本提交首次引入**（非"适配器既有"）→ 影响 D3 的表述准确性（见 §3） |
| **A8：那 32 条单测还 DB 无关吗** | `env -u DATABASE_URL pytest tests/unit/test_consulting_documents.py` ×2 次 | **失败/挂住**：19 条通过后卡住，100s / 120s 两次都被 timeout 杀掉（一次出现 `F`） |
| 对照：改动前是不是 DB 无关 | 我在 OEI-007 的记录（同一命令） | 当时 **32 passed in 5.50s** ✓ → **本刀把这 32 条从"DB 无关"变成了"必须连 PG"** |
| 机制定位 | 读该文件 fixture（235–250 行） | `os.environ.setdefault("DATABASE_URL", "…@127.0.0.1:55432/ece")` —— 指向临时 PG；**PG 不在时既不 skip 也不 fail-fast，而是挂住** |
| D4：两个测试文件到底改了什么 | `git show HEAD -- <两个文件>` 逐行看增删 | **属实且只改装配**：`test_consulting_documents.py` = `import os` + `DATABASE_URL` setdefault + fixture 加 `X-User-Id`；`test_consulting_engine_merge.py` = 加 `EngineCallerContext` import + stub 加 `engine_name` + 三方法签名加 `caller` + 非 onyx 用例改设 `stub.engine_name="mock"`。**断言一条未改、测试一个未删** ✓ |
| A9/no-regression 原始输出 | 读 `08/09-test-*-raw.txt` | 两次都是 `757 passed, 5 skipped, 3 deselected`（0 failed）；`09` 里另附一行 `# 1 failed, 756 passed` 记录 flake 那次 ✓ |

### 2.1 A8 的具体结论（本刀唯一 FAIL）

- **事实**：`tests/unit/test_consulting_documents.py` 的 32 条测试在 `DATABASE_URL` 未设置时**无法跑完**（挂在第 20 条附近）。
- **影响**：① 该文件名义上仍是 `tests/unit/`，实际已变成"必须连 PG"的测试；② 它破坏了我们从 OEI-003 起一直依赖的**"DB 无关单测可快速独立验证"**这条路径（我在 OEI-003/006/007 各刀都用它交叉验证过）；③ **cc 未申报这个副作用**（D4 只申报了"改了 2 个文件"，没说"这 32 条从此需要 PG"）。
- **判据**：A8 写的是"**DB 无关**单测通过"——对新增文件成立，对被改的既有文件**不成立**。

## 3. 对 D1–D6 的裁定

| 条目 | 裁定 | 说明 |
|---|---|---|
| **D1**（抓到并修掉两个审计漏洞） | **接受 + 记录为亮点** | 这是一次**用证据反推代码缺陷**的漂亮案例：`03` 的 `audit_log_total=2` vs 实际 3 次调用 → 顺藤摸到"`ok` 审计写在 return 之后（死代码）"与"`search` 成功路径完全无审计"。我独立读码确认修法与位置正确。**这条不修，A6 的"每次调用留痕"就是假的**——判断准确 |
| **D2**（对账脚本重复写 3 遍标记） | 接受 | 幂等守卫按行匹配导致的重复追加；已去重，无语义变化 |
| **D3**（审计未接进 `src/ece/audit/`） | **接受偏离，但要求两件事** | ① 理由成立：引擎调用是 per-request 高频路径，per-call 落库=每次检索一次 DB 写；且 `0005_context_audit` 的生命周期是 `context_request` 级，粒度确实不同。② **但"复用适配器既有 `_audit` 机制"的表述不准确**——`def _audit` 由**本提交首次引入**，实际是"新建了一个进程内审计"。③ 要求：(a) 文档如实标注**进程内/非持久/不跨 worker**（`docs/API.md §13.4` 已写明"这是进程内日志，不是 src/ece/audit/ 那张表"，**已达标**）；(b) **把"引擎调用审计的持久化设计（采样/批量写入，或接入 0005_context_audit）"写成 OEI-009 的明确交付项**，附代价评估。→ **不作为 R 项** |
| **D4**（改了 2 个既有测试文件 = §7 违规） | **接受改动 + 判任务书缺陷在我** | 我逐行看过 diff：**只改装配（fixture / stub / 依赖注入 / import），断言一条未改、测试一个未删**，且不改就 30+ 测试全红——这是**必要且最小**的改动。**这是我任务书 §7 的缺陷**："`tests/**` 仅允许新增文件"与步骤 7 要求的"回归改造"自相矛盾（与 OEI-006 那次同一类错误）。**处置**：把 §7 改为"**允许修改既有测试文件的装配部分（fixture / stub / 依赖注入），断言不得改动；新增测试走新文件**"（见 §5 的任务书修订）。**不判 R** |
| **D5**（既有 flake，未修，已量化） | **接受** | 方法可信：同 venv / 同 DB / `-p no:randomly`，HEAD 侧用 worktree + `PYTHONPATH` 且**验证过重定向生效**（`ece.audit.webhook.__file__` 指向 worktree）；两侧都是 12 次 1 次失败。机制我也读到了：`test_s20_audit_webhook.py:96-111` 后台线程投递 + 固定 `time.sleep(0.5)` → 负载一高就翻车。**未修是对的**（§7 未授权改 `src/ece/audit/**`）。**但基线必须记这个 caveat**（见 §6.1） |
| **D6**（`check_api_docs.py` 误报 4 条 consulting 路由） | 接受为已知问题 | 解析器只认 `^### (GET\|POST…)` 形式的标题，而 §11/§12 用了带编号标题；HEAD 与工作区解析结果一致（非本刀引入）。**归入 009 或单独小刀**，不阻塞 |

## 4. 裁定

**FAIL（唯一 R 项：恢复那 32 条单测的 DB 无关属性）**

理由：本刀的**主干交付全部达标且质量很高**——Port 五方法带身份、描述符消掉了手抄债务、四调用点接线并有十种组合的实测矩阵、CE 权限限制文档化、无新依赖、无回归（757/0）、合规无瑕。**D1 是难得的高质量自发现**（用证据反推代码缺陷）。唯一不合格的是 A8：**本刀把一个原本 DB 无关的单测文件变成了"必须连 PG"，而且没有申报**——它破坏的是我们后续每一刀都要用的快速验证路径，所以必须修，不能放过。

## 5. 返工清单（`OEI-008 R1`，一条）

- **R1（A8）** —— 恢复 `tests/unit/test_consulting_documents.py` 的 DB 无关属性。二选一（推荐前者）：
  1. **注入式身份**：在 fixture 里用 FastAPI 的 `dependency_overrides` 把"解析调用者身份"替换成一个**桩 caller**，使这些测试不再依赖 `resolve_identity()` 去打 DB；同时移除 fixture 里那行 `os.environ.setdefault("DATABASE_URL", …)`。
  2. 若确实需要真实 DB：**显式 `pytest.skip`（带原因）** 而不是挂住，并把该文件的归类与前置条件写进 `README`/`TASKS.md`。
  - **约束**：**断言一条不得改**；不得删测试；改完必须能给出 `env -u DATABASE_URL pytest tests/unit/test_consulting_documents.py` 的**完整通过输出**（这是我的复核条件）。
  - 顺带把 §5 的任务书修订落地（见下）。

## 6. 任务书修订（`OEI-008 TASK.md` → v1.1，codex 自身缺陷）

§7 的 `tests/**` 条款改为：

> `tests/**` **允许新增文件**；**允许修改既有测试文件的"装配部分"**（fixture / stub / 依赖注入 / import），但**断言不得改动、测试不得删除**；改动原因必须写进 REPORT 的偏差段。

（该修订由本刀 D4 触发；同类错误此前在 OEI-006 出现过一次。）

## 7. 转出（不属返工）

1. **基线 caveat（重要）**：全套件基线从 `737/0` 变为 **`757 passed / 0 failed`（+20 新增身份单测）**，但其中 `tests/integration/test_s20_audit_webhook.py::test_webhook_receives_event` 是**已知 flake（≈1/12）**。**后续刀判断回归时：只允许这一条失败；出现任何其它失败都是真回归。** 建议在 OEI-009 顺手把固定 `sleep(0.5)` 改成"轮询等待事件（带超时）"，这条 flake 本来就是审计链路的。
2. **引擎调用审计持久化** → 写进 OEI-009 交付项（见 §3 D3）。
3. **`check_api_docs.py` 的解析器**（D6）→ 同上，随 009 或单独小刀。
4. **演示项目仍待清理**：`project id=1` 现含 **21 份文件**（本刀又加了 `o8-test.md`×3 等）。清理计划我已备好（保留 3 份真文档），**等 OEI-008 R1 复审通过、推送前执行**。

---

## 8. 第二轮审验（`OEI-008 R1` 返工后）

**返工信号**：commit `a9cee31 fix(consulting): restore DB-free unit tests via FastAPI dependency override (OEI-008 R1)`。

### 8.1 R1（我给的显式复核条件）—— 通过

| 复核项 | 我的实测 | cc 的申报 | 结论 |
|---|---|---|---|
| `env -u DATABASE_URL pytest tests/unit/test_consulting_documents.py` | **32 passed, 1 warning in 4.87s**（exit=0；进度线 32 点 + `[100%]`） | 32 passed in 5.58s | **PASS**（与 OEI-007 的 5.50s 基线持平，DB 无关属性恢复） |
| 三个单测文件同条件 | **76 passed, 1 warning in 7.17s** | 76 passed in 5.19s | **PASS** |
| 修法是否为"注入式身份" | diff 显示：删掉 `import os` 与 `DATABASE_URL` setdefault 那段，改为 `from ece.consulting.router import get_upload_caller` 并用 `dependency_overrides` 注入桩 caller | 同 | **PASS**（正是 R1 推荐首选方案） |
| 断言是否被动 | `git show HEAD \| grep -E '^[-+]' \| grep -c assert` = **0** | 一条未改 | **PASS** |
| 提交范围 | `a9cee31` = 2 文件 / **+53 −29**（`src/ece/consulting/router.py`、`tests/unit/test_consulting_documents.py`）；`ahead 3` 未 push | 同 | **PASS** |

### 8.2 D7（优先级变化的诚实披露）—— 我实测确认，裁定"接受"

| 场景 | 实测 | 说明 |
|---|---|---|
| **匿名** + 零文件 | **HTTP 403** `identity-required (upload endpoints require an authenticated caller)` | 身份依赖 (`get_upload_caller`) 现在**先于** body 校验执行 |
| **带身份** + 零文件 | **HTTP 422**（由 `test_upload_zero_files_is_422` 覆盖，且该测试在 DB 无关运行里通过） | 原有语义**未变** |

**裁定：接受。** 理由：① 两者都是 4xx，detail 文案未变；② 对未认证调用者**不泄露请求校验细节**其实更稳妥；③ 无测试断言依赖旧优先级（cc 已核实，我复核 diff 未见相关断言）。
**但记录一处证据漂移**：`OEI-007/evidence/07-failure-paths.json` 的"⑥ request-level: zero files（HTTP 422）"是在**带身份**的 TestClient 下采集的，因此**仍然成立**；只有"**匿名**零文件"这一未采集的组合从 422 变成了 403。该漂移已由本刀记录，**不需要回改 OEI-007**。

### 8.3 裁定

**PASS —— OEI-008 关闭。**

理由：首轮唯一 FAIL（被改的 32 条单测失去 DB 无关属性、且未申报）已按推荐的 `dependency_overrides` 方案修复，**我的显式复核条件通过（4.87s / 32 passed）**，且只动装配、断言零改动。D7 这个由 R1 引入的优先级变化已诚实披露并经我实测确认，语义可接受。本刀的主干（Port 身份穿透、消掉手抄债务、四调用点接线、CE 权限限制成文、零新依赖、757/0 无回归）在首轮已逐条成立，D1（自发现并修掉两个真实审计漏洞）是本刀亮点。

### 8.4 转出（不变，供下一刀）

1. **引擎调用审计持久化设计**（现为进程内 `audit_log`）→ OEI-009 明确交付项，附代价评估。
2. **`test_s20_audit_webhook` 的固定 `sleep(0.5)` 竞态**（≈1/12 flake）→ 建议随 009 改成"轮询等待事件 + 超时"。
3. **`check_api_docs.py` 解析器**误报 4 条 consulting 路由（D6）→ 随 009 或单独小刀。
4. **演示项目清理**：`project id=1` 现 **21 份**（3 真文档 + 18 测试产物）→ 复审通过后、推送前执行。
