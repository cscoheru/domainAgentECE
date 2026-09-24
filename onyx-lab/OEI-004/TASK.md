# OEI-004 任务书 — 收尾与基线整理（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-24 ｜ 插入刀：原 OEI-004（Consulting Library）后移为 **OEI-005**，其后各刀顺延（见 `OEI-ROADMAP.md`）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## 本刀为什么插在这里

OEI-001/002/003 三刀已经把"引擎能存 → 引擎能检 → ECE 能用上引擎"这条主线打通。但连锁累积了三类**收尾债**，它们不解决就会污染后面的每一刀：

1. **仓库脏**：`ece/` 里 **684 个 `._*` AppleDouble 垃圾文件**（Mac 同步遗物）已经在**真实地破坏测试**（5 个 redaction 用例直接报 `UnicodeDecodeError`），且未提交的真实改动与噪音混在一起，导致"无回归"无法建立干净基线。
2. **流程脏**：测试基线一直跑在"未跑 `make seed`"的库上，28 个集成失败里有相当一部分是这个原因，长期掩盖真问题。
3. **账没结**：OEI-001 遗留的 **CE/EE 边界 5 项强制项全是 `UNKNOWN`**；`ece/TASKS.md` 与 `docs/API.md` 未回填；首轮失败的 2 个遗留容器还挂在那。

**前置（用户侧，不在本刀范围）**：swap 已 100% 占满（见 `OEI-003/VERDICT.md` §7.4），由用户按 codex 给的 runbook 处置。cc **不要**碰 swap / `.wslconfig`。

---

## 0. 一句话目标

把"临时能跑"变成"有干净基线"：清掉垃圾文件与遗留容器、补回文档、把 CE/EE 边界从 `UNKNOWN` 收敛到有据可查、并按 Makefile 的正确前置**重跑一次真实的测试基线**（落盘完整原始输出）。

## 1. 环境事实（codex 已实测，可直接信任）

- `ece/` 仓：Python 3.12 + `uv`；测试命令 `uv run pytest -m "not eval and not eval_llm"`
- **`Makefile:66,71` 明确规定**：集成测试前置为 `make pull-db` + `docker compose up -d db` + `uv run alembic upgrade head` + **`make seed`**。**本刀必须按此前置跑**，否则重演 OEI-003 的 28 个集成失败
- 临时 Postgres 走 `DATABASE_URL` 环境变量覆盖即可（`src/ece/db.py:16-21`），**不需要也不允许改 ECE 的 `docker-compose.yml`**（bind mount 在 WSL 上会因 uid 999 chown 失败）
- `._*` 垃圾文件：**684 个**，mtime 全为 **2026-09-23 17:31**（Mac 同步遗物），其中 `.mypy_cache/` 下最多；已确认是 5 个 redaction 测试报错的直接原因
- 遗留容器（首轮 bind-mount 失败产物，**均未运行**）：`ece-db-1`（Exited (1)，10:57）、`ece-api-1`（Created，10:54）
- Onyx 侧：9 容器在跑（`fisher` 对 `/home/codex/onyx-lab/src` 无读权限）；codex 已确认容器在 OEI-003 全程未重启

## 2. 范围锁

- **做**：清理 2 个遗留容器；ECE 仓垃圾清理 + 提交；回填 `TASKS.md` / `docs/API.md`；CE/EE 边界收敛；按正确前置重跑真实测试基线
- **不做**：不改 Onyx 上游 / compose / `.env`；不 restart/stop/down/rm **任何 Onyx 容器**；不碰 swap / `.wslconfig`；不动 `onyx-lab/bin/`；不 push；不做 OEI-005 及以后的功能

## 3. 工作区

```
onyx-lab/OEI-004/
├── TASK.md      ← 本文件（只读）
├── evidence/    ← 逐项证据（按 01.. 序号命名）
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

**证据命名**：`01-containers-before.txt`、`02-containers-after.txt`、`03-appledouble-list.txt`、`04-appledouble-after.txt`、`05-gitignore-appledouble.txt`、`06-git-status-after-clean.txt`、`07-tasks-api-backfill.md`、`08-ce-ee-boundary.md`、`09-test-baseline-raw.txt`、`10-test-after-clean-raw.txt`、`11-test-post-commit-raw.txt`、`12-git-commit.txt`、`13-compliance-check.txt`

## 4. 任务步骤

**步骤 1 — 清理遗留容器**

```bash
docker ps -a --format '{{.Names}}\t{{.Status}}' > evidence/01-containers-before.txt
docker rm ece-db-1 ece-api-1
docker ps -a --format '{{.Names}}\t{{.Status}}' > evidence/02-containers-after.txt
```

**只删这两个名字**；删完确认 9 个 Onyx 容器仍在且 Up 时长连续。

**步骤 2 — 清掉 AppleDouble 垃圾（先存清单，再删）**

```bash
find . -name '._*' -not -path './.venv/*' -not -path './.git/*' | sort > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-004/evidence/03-appledouble-list.txt
find . -name '._*' -not -path './.venv/*' -not -path './.git/*' -delete
find . -name '._*' -not -path './.venv/*' -not -path './.git/*' | wc -l > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-004/evidence/04-appledouble-after.txt
```

- 删除是有意为之且**有清单可追溯**：它们全是 macOS 元数据（含 null 字节），不是仓库内容，且正在破坏测试。
- 同时把 `._*` 加入 `ece/.gitignore`（`evidence/05-gitignore-appledouble.txt` 贴出 diff）。
- **不要**动 `data/` 下的真实数据文件；只删 `._*` 模式。

**步骤 3 — 让 `git status` 只剩真实改动**

- 处理模式位噪音（`core.fileMode` 或 `.gitattributes`），使 Windows 挂载导致的 `100644→100755` 不再刷屏
- 落盘：`git status --short` 结果 → `06-git-status-after-clean.txt`，并在 REPORT 中给出**真实改动清单**（应只有 `src/ece/connectors/onyx/*`、`src/ece/api/engine_status.py`、`src/ece/main.py`、`ece/.gitignore` 等）

**步骤 4 — 回填文档**（`07-tasks-api-backfill.md` 记录改了什么）

- `ece/TASKS.md`：补 OEI-003 条目（Content Engine Port + Onyx/Mock adapter + `/engine/status`）
- `ece/docs/API.md`：补 `/engine/status` 段落（路径、参数 `q`、返回内容、降级行为、示例）

**步骤 5 — CE/EE 边界收敛**（`08-ce-ee-boundary.md`）

把 `OEI-001/REPORT.md` §A9 的 5 项强制项（**外部源权限同步 / 用户组 / SSO / SCIM / 高级审计**）从 `UNKNOWN` 往前推：

1. **本机可复现证据优先**：例如 api_server 镜像内是否存在 `/app/ee/...` 路径、tier gate 中间件日志、UI 上 EE 功能是否显示锁定徽章（若你能访问 UI 就截图，不能就记录"未取得"）
2. **官方文档**：网络可达时补 URL + 引文（`ollama.com` 可达，Onyx 官方域名请自行尝试；**不可达就如实记为不可达**）
3. 每项最终给一个明确归属：`CE` / `EE` / `UNKNOWN`，**并写明依据与"这是本机实测还是文献"**；仍为 `UNKNOWN` 的要写清"尝试过哪三种方式都没拿到证据"

**步骤 6 — 真实测试基线（本刀的重头）**

1. 起临时 PG（**任务书显式授权**）：

```bash
docker run -d --name ece-pg-tmp -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece -p 55432:5432 postgres:16-pgvector
export DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece'
uv run alembic upgrade head
uv run python -m ece.seed          # Makefile 要求的 make seed 等价步骤
```

2. **干净树基线**：用 `git worktree add /tmp/ece-baseline HEAD`（不动当前工作区）在 HEAD 版本上跑一次，落盘**完整原始输出**（含进度行与汇总行）→ `09-test-baseline-raw.txt`
3. **当前树复测**：在当前树跑一次 → `10-test-after-clean-raw.txt`
4. 对比并解释差异：**重点确认 5 个 redaction error 是否随垃圾文件清理消失**，以及 `make seed` 是否让集成失败减少
5. 跑完 `docker rm -f ece-pg-tmp` 清理（`git worktree remove /tmp/ece-baseline` 一并清理）

**步骤 7 — 提交 ECE 改动**（**本刀显式授权 commit，禁止 push**）

- `git add` 真实改动（不含垃圾、不含 `.venv`）、`git commit`，message 写清"OEI-003: Content Engine Port + Onyx/Mock adapter + /engine/status（含引用渲染）"
- 落盘 `git show --stat HEAD` → `12-git-commit.txt`
- 提交后再跑一次 `pytest` 作为**提交后基线** → `11-test-post-commit-raw.txt`

**步骤 8 — 合规扫描** → `13-compliance-check.txt`（value-level 模式，含 `connect.sid=` / `fastapiusersauth=` / `eyJ…` / `sk-…`）

## 5. 验收标准（codex 将逐条核对）

- [ ] **A1** 遗留容器已删：`ece-db-1` / `ece-api-1` 从 `docker ps -a` 消失，且 9 个 Onyx 容器仍 Up（时长连续，无重启）
- [ ] **A2** `._*` 垃圾清零：`04-appledouble-after.txt` = **0**；清单 `03-appledouble-list.txt` 已落盘（含删除前计数）
- [ ] **A3** `._*` 已进 `.gitignore`，且 Report 中给出真实改动清单，`git status --short` 噪音大幅下降（贴出前后对比）
- [ ] **A4** `ece/TASKS.md` 与 `ece/docs/API.md` 已回填，且能在文件中 grep 到 OEI-003 与 `/engine/status`
- [ ] **A5** CE/EE 边界 5 项强制项**每项都有明确归属 + 依据来源 + "实测/文献"标注**；仍为 UNKNOWN 的必须写明尝试过的方式
- [ ] **A6** 测试基线为**完整原始输出**（不得再用手写摘要），且明确含 `make seed` 前置；给出 baseline / after-clean / post-commit 三组数字
- [ ] **A7** 5 个 redaction error 的状态在报告中明确（消失 / 仍存在 + 原因）
- [ ] **A8** ECE 真实改动已 commit（`git log -1` 可见），**未 push**；提交后工作区干净（或只剩预期噪音）
- [ ] **A9** 合规：无凭据泄漏；未碰 Onyx 容器/配置；未碰 swap / `.wslconfig`；临时 PG 与 worktree 已清理
- [ ] **A10** `REPORT.md` 对 A1..A9 每条有结论 + 证据指针，无模糊表述；无"手写数字"

## 6. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏、临时资源已清理
2. `echo "$(date -Iseconds) OEI-004 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并签发 OEI-005（Consulting Library 接真实检索）；FAIL → 按 R{n} 返工

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：① `docker rm ece-db-1 ece-api-1`（**仅这两个名字**）；② `docker run` / `docker rm -f` 临时 `ece-pg-tmp`；③ 删除 `._*` 垃圾文件（先落清单）；④ `git add` + `git commit`（**不 push**）；⑤ `git worktree add/remove /tmp/ece-baseline`；⑥ 写 `ece/.gitignore`、`ece/TASKS.md`、`ece/docs/API.md`
- ❌ 不 restart / stop / down / rm **任何 Onyx 容器**；不改 Onyx 上游 / compose / `.env`
- ❌ 不碰 swap、`/proc/sys/vm/*`、`.wslconfig`（swap 由用户处置）
- ❌ 不删 `data/` 下的真实数据；不删 `.venv` 之外无法解释的文件（凡删除必须先在证据里列清单）
- ❌ 不 push；不碰 `onyx-lab/bin/`、不改历史 `TASK.v*.md` / `VERDICT.md`
- ❌ 不做 OEI-005 及以后的功能

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-004/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-004/DONE`
- 无新文件则静默，不重复执行、不打扰用户
