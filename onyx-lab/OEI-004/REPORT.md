# OEI-004 执行报告 — 收尾与基线整理

> 执行:Claude Code(i9 / WSL / `fisher`)｜ 任务书:`OEI-004/TASK.md` v1 ｜ 报告时间:2026-09-24T16:43+08:00
> 状态:**主体 PASS**(按任务书 §4 步骤 1–8 全部完成,临时资源已清理)

---

## 0. 范围声明

按 OEI-004/TASK.md v1 §2 + §7(显式授权):

- ✅ **做**:删 2 个 `ece-*` 遗留容器;清 684 个 `._*` 垃圾;加 `._*` 到 `.gitignore`;回填 `TASKS.md`/`docs/API.md`;CE/EE 边界收敛;**起/删**临时 `ece-pg-tmp`;`git worktree` 起 baseline;**commit**(不 push)
- ❌ **不做**:不动 Onyx 容器 / compose / `.env`;不碰 swap / `.wslconfig`;不删 `data/` 真实数据;不 push

---

## 1. evidence 计数(命令 `ls evidence/ | wc -l` 真值)

```
13
```

文件:`01-containers-before.txt`、`02-containers-after.txt`、`03-appledouble-list.txt`、`04-appledouble-after.txt`、`05-gitignore-appledouble.txt`、`06-git-status-after-clean.txt`、`07-tasks-api-backfill.md`、`08-ce-ee-boundary.md`、`09-test-baseline-raw.txt`、`10-test-after-clean-raw.txt`、`11-test-post-commit-raw.txt`、`12-git-commit.txt`、`13-compliance-check.txt`

---

## 2. A1–A10 逐条验收

### A1 — 遗留容器已删 ✅ PASS

| 文件 | 内容 |
|---|---|
| `01-containers-before.txt` | `ece-db-1 Exited (1)` + `ece-api-1 Created` |
| `02-containers-after.txt` | 空(全部删除) |

Onyx 9 容器仍 **Up 22 hours** 连续(无重启)。

### A2 — `._*` 垃圾清零 ✅ PASS

- `03-appledouble-list.txt` = **684** 行(删除前清单)
- `04-appledouble-after.txt` = **0**

### A3 — `._*` 已进 `.gitignore`,`git status` 噪音大幅下降 ✅ PASS

- `05-gitignore-appledouble.txt`:diff 显示追加 `# macOS AppleDouble ...` 注释 + `._*` 模式
- `06-git-status-after-clean.txt`:
  - **改动前**: 500 entries(496 个 mode-bit-only `._*` + `M`)
  - **改动后**: 18 entries(其中 **14 个**是历史 dirty,属 OEI-004 范围外;**2 个 type change** 也属范围外)
  - 真实 OEI-004 改动:**`.gitignore` + `src/ece/main.py` + 新 `src/ece/api/engine_status.py` + 新 `src/ece/connectors/onyx/`**(`?? src/ece/connectors/onyx/` 展开后 6 文件)
  - **已 commit** 见 A8

### A4 — `TASKS.md` / `docs/API.md` 已回填 ✅ PASS

`07-tasks-api-backfill.md`:
- `TASKS.md` 增"附录 K — Onyx Enterprise Integration 后置交付登记(OEI-003 / OEI-004,2026-09-24)"含 K.1 能力登记 / K.2 验收证据 / K.3 收尾债
- `docs/API.md` 增"## 6. Engine Status(OEI-003,Engine Core 内部状态页)"含完整端点文档

**grep 验证**:`grep 'OEI-003\|/engine/status\|ContentEngine' TASKS.md` 命中 12 行;`docs/API.md` 命中 4 行。

### A5 — CE/EE 边界 5 项强制项收敛 ✅ PASS(4 项实测 + 1 项推断)

`08-ce-ee-boundary.md`(完整证据链):

| # | 能力 | 归属 | 依据类型 |
|---|---|---|---|
| 1 | 外部源权限同步 | **EE** | 本机实测:路由表(`/manage/admin/cc-pair/.../sync-permissions`)+ EE 路径存在 |
| 2 | 用户组 | **EE** | 本机实测:路由(`/manage/admin/user-group/*` 全套 CRUD) |
| 3 | SSO | **EE** | 本机实测:路由(`/auth/sso/*`) |
| 4 | SCIM | **EE** | 本机实测:`/scim/v2/*` 完整 SCIM v2 + 启动日志反向证明 `/app/ee/onyx/server/scim/api.py` 路径 |
| 5 | 高级审计 | **EE(INFERRED)** | api_server 启动日志 `tier_gate.py:62 Tier gate middleware registered (entries=18)` 显示 18 个 tier-gated 端点存在;**但**本机实测 api_server 路由表中 **`audit` 关键词路由 = 0 条**——无直接可观察的审计端点,只能依据 tier-gate 中间件存在做**推断**;如需升级为实测,需进入 Onyx UI 观察 SIEM 导出入口或对照官方文档(本刀未取得) |

**community tier 拦截实证**:`GET /api/admin/enterprise-settings` → `{"error_code":"FEATURE_NOT_AVAILABLE","required_tier":"business"}`(codex 独立复跑结果 HTTP 402)。

**4 项本机实测 + 1 项推断**(无 UNKNOWN);官方 URL 文献补全因 WebSearch 工具失败 + 沙箱网络受限,记录为"待后续刀在网络可达时补"。

### A6 — 测试基线为完整原始输出 + 含 `make seed` 前置 ✅ PASS(详见 R5 多变量备注)

**关键改进**(对比 OEI-003 VERDICT §7.3 第 1 轮):
- OEI-003 第 1 轮 baseline **未跑 `make seed`** → 库缺 fixture → 28 个集成失败(被误判为 OEI-003 影响)
- OEI-004 第 2 轮 baseline **正确跑 `make seed`**(先生成 `data/dataset/demo.json`,再 seed)→ 13 个集成测试转为通过

**三次 pytest 真值**:

| | baseline(worktree HEAD, 无 OEI-003 改动 + seed + cleanup) | current(OEI-003 + cleanup, 未 commit) | post-commit(已 commit) |
|---|---|---|---|
| **passed** | **647** | **654** | **654** |
| failed | 27 | 27 | 27 |
| errors | 7 | **0** | **0** |

**关键观察**:
- 647 → 654 (+7 passed):**那 7 个 `PRD missing` setup error 在主树里转为通过**(同一批 7 个测试,worktree 缺文件 → error;主树文件在位 → pass)。**OEI-003 / OEI-004 没有新增任何 pytest 用例**,不存在"collection 收益"
- 27 failed 持平:边界条件测试,与 OEI-003 无关
- **7 errors → 0 errors**:见 A7 的受控 A/B 证明

证据:
- `09-test-baseline-raw.txt`(1783 行,完整 pytest 输出)
- `10-test-after-clean-raw.txt`(861 行)
- `11-test-post-commit-raw.txt`(861 行,与 10 完全一致)

### A7 — 5 redaction error 状态 ✅ PASS(因果链已更正)

**重要说明**(VERDICT §2.1 指出的原报告错误已修正):

baseline 的 7 个 error **不是** redaction 失败。`git worktree` 只检出**已跟踪文件**,而 `._*` 是**未跟踪**的 macOS 垃圾——worktree 里**根本不存在**这些文件,也不可能因 `._*` 触发 `UnicodeDecodeError`。baseline 的 7 个 error 实为 **`Failed: PRD missing at /tmp/docs/demo-platform/DEMO_PLATFORM_PRD.md`**(worktree 的 `/tmp` 路径伪影),与 AppleDouble 无关。

**正确的受控 A/B 证据对**(同主树,只有垃圾有无变化):
- `OEI-003/evidence/10-test-after.txt`:主树、**有 684 个 `._*` 垃圾** → **5 个 redaction ERROR**
- `OEI-004/evidence/10-test-after-clean-raw.txt`:主树、**`._*` 已清理** → **0 个 redaction ERROR**
- 控制变量:**仅有垃圾清理**,代码与基线一致;**5 → 0 的差完全归因于清理**

**codex 独立复跑**:`tests/unit/test_ops_evidence_redaction.py` 在清理后 = **6 passed / 0 error** ✅

| 阶段 | redaction error 状态 |
|---|---|
| 主树 + `._*` 未清(OEI-003 第 1 轮) | **5 个 ERROR** |
| 主树 + `._*` 已清(OEI-004 本刀) | **0 个** ✅ |
| post-commit(已 commit) | **0 个** ✅ |

### A8 — ECE 真实改动已 commit ✅ PASS

`12-git-commit.txt` 记录两个 commit:

```
5878a26 docs(OEI-004): backfill TASKS.md Appendix K + docs/API.md §6 + ignore _._ files
03ee377 feat(OEI-003): Content Engine Port + Onyx/Mock adapter + /engine/status
```

- 03ee377: 7 文件(OEI-003 全部代码改动 + 接口)
- 5878a26: 3 文件(.gitignore + TASKS.md + docs/API.md)
- **未 push**(`git log --oneline -3` 显示本地,未出现 `origin/main`)

**commit 后工作区状态**: 14 entries 仍 dirty,但**全部是范围外历史 dirty**(`reports/cut-*/mutation-evidence/*` 12 个 + `docs/demo-platform/*.md` 2 个 type change)— 这些是 OEI-004 之前就存在的 dirty,任务书 §7 未授权 cc 处理。

### A9 — 合规 ✅ PASS

`13-compliance-check.txt`:
- 7 个 value-level pattern(`connect.sid=` / `fastapiusersauth=` / `eyJ…` / `password=` / `Authorization: Bearer` / `token=` / `api_key=` / `sk-…`)扫描范围:`OEI-004/evidence/` + `ece/src/ece/connectors/onyx/` + `ece/.gitignore` + `ece/TASKS.md` + `ece/docs/API.md` + 三个历史 REPORT.md → **0 命中,STATUS: PASS**
- ECE 仓内**无 cookie 副本**(`find ece/ -name '*cookie*'` 仅命中 venv 第三方)
- `ECE_ONYX_COOKIE_FILE` 字符串仅在 `connectors/onyx/` 内(2 个文件 4 处)
- 临时 PG `ece-pg-tmp` 已 `docker rm -f`
- `git worktree /tmp/ece-baseline` 已 `git worktree remove --force`
- Onyx 9 容器 Up 22h 无影响
- **未碰** swap / `.wslconfig` / Onyx compose / Onyx `.env`

### A10 — REPORT 完整性 ✅ PASS

- ✅ evidence 计数 **13**(命令 `ls evidence/ | wc -l` 真值,贴出实际输出)
- ✅ A1–A9 每条有结论 + 证据指针,无"应该没问题"
- ✅ 全部 pytest 数字来自 `tail -3 /tmp/...-raw.log` 真实输出,非手写
- ✅ file count 全部用 `wc -l` 真值

---

## 3. 文件改动总览(本刀 = OEI-004 commit)

```
03ee377  feat(OEI-003):    src/ece/connectors/onyx/__init__.py     (新增)
                           src/ece/connectors/onyx/port.py         (新增)
                           src/ece/connectors/onyx/mock_adapter.py (新增)
                           src/ece/connectors/onyx/onyx_adapter.py (新增)
                           src/ece/connectors/onyx/selector.py     (新增)
                           src/ece/api/engine_status.py             (新增)
                           src/ece/main.py                         (+4 行)

5878a26  docs(OEI-004):    ece/.gitignore                           (+3 行 _._ rule)
                           ece/TASKS.md                             (+30 行 Appendix K)
                           ece/docs/API.md                          (+59 行 §6)
```

**未 push**(本地 HEAD only);**未触碰 Onyx** 容器 / compose / `.env` / 上游;**未修改 `data/` 真实数据**(已 `make gen-dataset` 生成 demo.json 是测试 fixture,任务书 §1 明确授权)。

---

## 4. 已知限制 / 留待后续刀

### 方法学备注(R5):用 `git worktree` 跑 baseline 在本仓不可靠(VERDICT §6 #R5)

三次 pytest 运行之间同时变化了**三个变量**(worktree vs 主树、垃圾有无、seed 有无),**不构成受控 A/B**。可信部分:

- **27 failed 三次完全一致**(边界测试,与 OEI-003 无关)
- **最终树 654 passed / 0 errors**(已 commit)
- **改动为纯增量**(7 新文件 + `main.py` +4 行)

**用 `git worktree` 跑 baseline 的具体不可靠之处**:本仓部分集成测试依赖 worktree 路径之外的 `/tmp/docs/...`,导致 worktree 里出现 `PRD missing at /tmp/docs/demo-platform/...` 的伪 error——这与真实代码改动无关,是 worktree 的路径伪影。

**若将来需要真正的"改动前"基线**(推荐做法,单变量 A/B):在主树用 `git revert` 而非 worktree,环境变量与路径全部不变:

```bash
# 在主树 /mnt/d/Projects/domainAgentECE/ece/
git revert --no-commit 03ee377 5878a26   # 撤掉两个新 commit 的改动
# 此时 DATABASE_URL 与 .venv 都保留,跑 pytest
DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece' \
  uv run alembic upgrade head && \
  uv run python -m ece.seed && \
  uv run pytest -m "not eval and not eval_llm" > baseline-clean.txt
# 撤掉 revert(不 commit,只 reset stage 即可)
git revert --abort
```

这样**只有代码改动**一个变量,**垃圾清理 / seed / 路径**全部不变,得到干净的受控 baseline。

### 其他已知限制

| 项 | 留待 |
|---|---|
| 27 failed + 0 errors(原 7 errors 全消) | 大部分 failed 是 integration 边界测试(compliance / knowledge boundary / three domain acceptance);与 OEI-003/004 无关,**单独排查** |
| 14 entries dirty(reports/cut-*/mutation-evidence + docs/demo-platform type change) | 历史 dirty,**本刀范围外**,留用户手动处理 |
| Onyx UI 引用渲染缺陷 + 3b 召回质量问题 | 留 OEI-005 |
| 资源紧张(swap 已 100% 满) | 用户侧按 VERDICT §7.4 runbook 处置,cc 不碰 |
| CE/EE 边界文献 URL 补全 | WebSearch 工具失败 + 沙箱网络受限;**4 项本机实测 + 1 项 INFERRED**(高级审计),后续网络可达时补官方 URL |
| `tests/unit/test_content_engine_port.py` (DB 无关的 adapter 单测) | VERDICT §6 强建议,留后续刀 |

---

## 5. 完成动作

1. ✅ evidence/ **13** 个文件
2. ⏳ 待执行:`echo "$(date -Iseconds) OEI-004 complete" > DONE`
3. ⏳ STOP — 等待 codex 写 VERDICT.md
