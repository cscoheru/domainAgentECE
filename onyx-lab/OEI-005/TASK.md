# OEI-005 任务书 — 集成测试红灯归零（fixture 前置与真缺陷分辨）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-24 ｜ 插入刀：原 OEI-005（Consulting Library）后移为 **OEI-006**，其后各刀顺延（见 `OEI-ROADMAP.md`）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## 本刀为什么插在这里

`uv run pytest -m "not eval and not eval_llm"` 现在稳定报 **27 failed**，且三次运行数字完全一致（OEI-003/004 均有落盘），说明**不是偶发**。它们集中在 compliance / knowledge / three-domain / temporal 这些**权限与边界断言**上——如果不查清，后续每一刀都要在 27 个红灯的噪音里判断"我这次改坏了没有"，等于**没有回归信号**。

**关键前提：这大概率不是产品缺陷。** codex 在本刀签发前做了侦察（见 §1.2），高度怀疑根因是"**集成测试的 fixture 前置步骤没跑**"——因为失败信息要的实体，恰好由仓里两个专用 seeder 负责写入。

> ⚠️ **本刀的第一目标是"查清"，不是"变绿"。** 如果最终发现某个红灯是**真缺陷**，**不许修**（那要另开一刀），但必须给出最小复现与影响面。

---

## 0. 一句话目标

把 27 个红灯**逐个归因**（环境步骤缺失 / 测试过时 / 真缺陷），能靠"补跑前置"解决的**真正跑绿**，并把"本地跑集成测试的完整前置链"做成 **`Makefile` 里可发现的一步**（现在它只藏在 `deploy/` 文档里，所以本地才会漏跑）。

## 1. 环境事实与预备知识

### 1.1 环境（codex 已实测，可直接信任）

- `ece/` 仓：Python 3.12 + `uv`；测试命令 `uv run pytest -m "not eval and not eval_llm"`
- **临时 Postgres 用 `DATABASE_URL` 覆盖即可**（`src/ece/db.py:16-21`），**不要改 `docker-compose.yml`**（bind mount 在 WSL 上会因 uid 999 失败）
- `._*` 垃圾已清零（OEI-004），`.gitignore` 已加规则；`data/` 下 `pgdata` 是历史目录
- 工作区状态：两个已在 HEAD 的 commit（`03ee377` OEI-003 代码、`5878a26` OEI-004 文档），**未 push**；另有 14 条历史 dirty（范围外）
- Onyx 侧 9 容器在跑，**本刀不碰 Onyx**；swap 已加 8GB 缓冲，但 `.wslconfig` 14GB 配额**尚未重启生效**

### 1.2 codex 侦察到的线索（**假设，需你证实/证伪**）

**失败清单（来自 `OEI-004/evidence/10-test-after-clean-raw.txt`，27 条按文件聚类）**：

| 文件 | 条数 |
|---|---|
| `tests/integration/test_knowledge_boundary.py` | 9 |
| `tests/integration/test_compliance_boundary.py` | 7 |
| `tests/integration/test_three_domain_acceptance.py` | 6 |
| `tests/integration/test_s4_5_temporal.py` | 2 |
| `tests/integration/test_knowledge_domain_discovery.py` | 1 |
| `tests/integration/test_cut_045_local_origin_smoke.py` | 1 |
| `tests/integration/test_compliance_domain_discovery.py` | 1 |

**典型报错**：`422 invalid_scenario_spec: no entity with source_id='COMP-CTL-001' source_system='comp:v0-compliance-fixture'`（knowledge 侧同构，`KM-POL-001` / `km:v0-knowledge-fixture`）。

**仓里存在对应 seeder，且契约与报错一字不差**：

- `scripts/seed_compliance_fixture.py` — docstring 写明 `source_system = comp:v0-compliance-fixture`，含 `COMP-CTL-001/002/003` 三个 control
- `scripts/seed_knowledge_fixture.py` — docstring 写明 `source_system = km:v0-knowledge-fixture`
- **另有** `scripts/seed_temporal_roles.py`（OEI-004 侦察中在 `reports/cut-043R/closure.md` 见到）——可能对应 `test_s4_5_temporal.py::test_seed_temporal_roles_populated` 那两条
- 可能还涉及 `scripts/seed_relationships.py`、`scripts/seed_v0_spike_fixture.py`（同族 seeder）

**为什么本地会漏跑**：这两个 seeder **只在 `deploy/README.md:84-85` 与 `deploy/SERVER_DEPLOYMENT_CHECKLIST.md:349,353,696,698` 被提到**，**`Makefile` 里完全没有**，也没有任何 `make test` 相关注释指向它们 → 按 Makefile 前置（`pull-db` + `compose up -d db` + `alembic upgrade head` + `make seed`）跑，必然会缺这些 fixture。

**待你判定的两类存疑项**：

- `test_cut_045_local_origin_smoke.py::test_deployment_smoke_passes_against_local_origin` — 可能依赖**已部署的本地 origin**（公网 526 那条链路的问题），大概率属环境/范围外
- `*_domain_discovery.py` 两条 — 名字看是"域发现"，可能与 pack 自注册（`reports/cut-043R/closure.md` §5 提到"每个 entry point 必须显式触发 pack 自注册"）有关

## 2. 范围锁

- **做**：复现红灯 → 逐步补前置、**记录每一步消掉哪几个失败** → 逐个归因 → 让前置链在 Makefile 里可发现 → 最终基线 raw → 报告
- **不做**：**不改产品代码、不改测试断言、不删测试、不把期望值改成"过"**；不改 Onyx 任何东西；不 push；不碰 swap / `.wslconfig`
- **判据**：如果为了让红灯变绿必须改产品行为或测试语义 → **立即停止该类动作**，把它记为"真缺陷/需单独一刀"，只交证据

## 3. 工作区

```
onyx-lab/OEI-005/
├── TASK.md      ← 本文件（只读）
├── evidence/    ← 逐项证据（按 01.. 序号命名）
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

**证据命名**：`01-pg-and-migrate.txt`、`02-repro-27-fail-raw.txt`、`03-step-gen-dataset-raw.txt`、`04-step-seed-raw.txt`、`05-step-seed-temporal-raw.txt`、`06-step-seed-knowledge-raw.txt`、`07-step-seed-compliance-raw.txt`、`08-remaining-failures-raw.txt`、`09-triage-table.md`、`10-makefile-diff.txt`、`11-final-baseline-raw.txt`、`12-git-commit.txt`、`13-compliance-check.txt`

> 每一步都落**完整 pytest 原始输出**（含进度行与末尾汇总行），不要手写摘要——本刀的价值全在"哪一步消掉哪几条"。

## 4. 任务步骤

**步骤 1 — 起临时 PG 并建基线**

```bash
docker run -d --name ece-pg-tmp -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece -p 55432:5432 postgres:16-pgvector
export DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece'
uv run alembic upgrade head
```

先按 Makefile 现有前置跑到"当前状态"并落盘 `02-repro-27-fail-raw.txt`（**先复现 27 failed，作为本刀的对照起点**）。

**步骤 2 — 逐步补前置，每步跑一次并记录增量**（本刀的核心动作）

按 §1.2 的顺序**一次只加一步**，每步后跑一次完整套件并落盘：

1. `uv run python scripts/gen_dataset.py --out data/dataset/demo.json`（等价 `make gen-dataset`）→ `03-*`
2. `uv run python -m ece.seed`（等价 `make seed`）→ `04-*`
3. `uv run python scripts/seed_temporal_roles.py` → `05-*`
4. `uv run python scripts/seed_knowledge_fixture.py` → `06-*`
5. `uv run python scripts/seed_compliance_fixture.py` → `07-*`

（若第 1.2 节推测的脚本名/参数与实际不符，以 `--help` 与脚本 docstring 为准，并在报告里说明偏差。）

**记录表**：每步之后 `passed / failed / errors` 各是多少、**哪几条从 FAILED 变 PASS**、**哪几条纹丝不动**。这张表就是本刀最重要的产出。

**步骤 3 — 剩余失败逐个归因**

到 `08-remaining-failures-raw.txt` 时若仍有红灯，**逐条**给出：

- 最小复现命令（尽量是单条 `pytest <nodeid>`）
- 根因分类：**(a) 环境步骤缺失 / (b) 测试过时（断言或路径与现状不符）/ (c) 真实缺陷**
- 若为 (b) 或 (c)：给出**最小修复方案**（写在报告里），**但不实施**
- 特别注意 `test_cut_045_local_origin_smoke.py` 与两条 `*_domain_discovery.py`，它们最可能是 (a) 之外的类别

**步骤 4 — 让前置链可发现（本刀的交付物）**

在 `ece/Makefile` 增加一个目标（建议名 `seed-fixtures`），把集成测试所需的**全部** seeder 串起来；并在 `Makefile` 注释与 `ece/README.md` 的测试段落里写明**完整前置链**（`alembic upgrade head → gen-dataset → seed → seed-fixtures → pytest`）。**只允许新增目标/注释/文档段落，不得改动既有目标的语义、不得改产品代码与测试**。落盘 diff → `10-makefile-diff.txt`。

**步骤 5 — 最终基线与提交**

- 最终跑一次完整套件 → `11-final-baseline-raw.txt`
- 把本刀改动（Makefile / README）**commit（不 push）** → `12-git-commit.txt`
- 若步骤 4 之外的代码一行未改，请在报告里明确写"本刀未改产品代码一行"

**步骤 6 — 清理与合规**

`docker rm -f ece-pg-tmp`；`13-compliance-check.txt`（value-level 模式）落盘。

## 5. 验收标准（codex 将逐条核对）

- [ ] **A1** 起点复现：`02-repro-27-fail-raw.txt` 的 failed 数与本刀书 §1.2 的 27 条清单一致（不一致要解释）
- [ ] **A2** 增量表完整：每个前置步骤都有 raw 输出，且明确列出"该步消掉的失败条目"
- [ ] **A3** 27 条**逐条有归属**（环境/过时/真缺陷 三类之一），每条带最小复现命令；不得有一句"其余同前"
- [ ] **A4** 若最终仍有红灯：属 (c) 真实缺陷的必须写清影响面与最小修复方案，且**产品代码与测试断言未经修改**（用 `git diff` 证明）
- [ ] **A5** `Makefile` 新增前置目标 + 注释，`ece/README.md` 写清完整前置链；diff 落盘；**未改既有目标语义**
- [ ] **A6** 最终基线为完整 raw 输出，且给出"27 → N"的真实数字与逐条去向
- [ ] **A7** 单变量纪律：本刀所有 pytest 都在**主树 + 同一 PG + 同一环境**下跑（**不许再用 `git worktree`**，理由见 `OEI-004/VERDICT.md` §4/R5）
- [ ] **A8** 改动已 commit、未 push；临时 PG 已删
- [ ] **A9** 合规：无凭据泄漏；未碰 Onyx / compose / `.env` / swap / `.wslconfig`
- [ ] **A10** `REPORT.md` 对 A1..A9 每条有结论 + 证据指针；无手写数字；**明确回答"27 个红灯里有几个是真缺陷"**

## 6. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏、临时资源已清理
2. `echo "$(date -Iseconds) OEI-005 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并签发 OEI-006（Consulting Library 接真实检索）；FAIL → 按 R{n} 返工

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：① `docker run`/`docker rm -f` 临时 `ece-pg-tmp`；② 改 `ece/Makefile`（**仅新增目标与注释**）、改 `ece/README.md`（**仅测试前置段落**）；③ `git add` + `git commit`（**不 push**）；④ 执行仓内既有 seeder 脚本
- ❌ **不改产品代码**（`src/ece/**` 一行都不许动）、**不改测试**（`tests/**` 一行都不许动）、**不删测试**、**不放宽断言**
- ❌ 不 `git worktree`（OEI-004 已证其在本仓不可靠）
- ❌ 不 restart/stop/down/rm **任何 Onyx 容器**；不改 Onyx 上游 / compose / `.env`
- ❌ 不碰 swap / `.wslconfig`；不 push；不碰 `onyx-lab/bin/`
- ❌ 不做 OEI-006 及以后的功能

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-005/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-005/DONE`
- 无新文件则静默，不重复执行、不打扰用户
