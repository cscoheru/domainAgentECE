# OEI-013 任务书 — 演示台 v1（咨询单域）+ 检索排序修复 + 移除对照文档

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-26
> 前置：`OEI-001～014` 与 `OEI-012` 已全部收束；本刀把 `OEI-012` 的"检索排序修复"与"移除对照文档"**并进来**（用户 2026-09-26 决策）
> 返工约定：本刀若需返工，一律标 **`OEI-013 R1` / `R2`**（不插新刀、不顺延既有编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## ✦ 开工指令（cc 必读：按序读完再动手）

> **`onyx-lab/` 顶层的一批文档已由用户并入 `onyx-lab/重启必读/`**；`CODEX-ROLE.md` / `README.md` / `ASSET-INDEX.md` / `DECISION-ONYX.md` 仍在顶层。

**① 按序必读（绝对路径，一份都别跳）**

```
1. /mnt/d/Projects/domainAgentECE/AGENTS.md                                  ← 项目总规则（MVP 要"Case First + 可演示"）
2. /mnt/d/Projects/domainAgentECE/onyx-lab/README.md                          ← 入口索引（含"为什么 8080 看不到变化"）
3. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/CC-ROLE.md                 ← 你的角色任务书
4. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/LOCAL-AGENT-PROTOCOL.md    ← 共享规则 + §5.1 资源纪律（本刀要**常驻 demo**，与既往"验完即释放"不同，见 §8）
5. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/OEI-ROADMAP.md             ← 路线图：本刀条目 + OEI-012 转出
6. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/VERDICT.md                  ← 检索 0% 的裁定（§6 转出第 1、2 项 = 本刀步骤 0/1）
7. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/DEMO-DATA-CLEANUP-2026-09-25.md ← **两步删除语义**（移除对照文档要用）
8. /mnt/d/Projects/domainAgentECE/docs/demo-platform/DEMO_PLATFORM_PRD.md      ← 演示平台 PRD（六步闭环的来源）
9. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-001/workspace/                 ← 三份演示文档源文本（demo 素材）
10. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-013/TASK.md                    ← **本文件 = 唯一任务来源**
```

**② 开工前先核对状态（只读）**

```bash
cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-013 && ls -la          # 不该有 DONE / VERDICT.md
cd /mnt/d/Projects/domainAgentECE/ece && git log --oneline -2 && git status -sb | head -3
# 期望：HEAD = 4a67c28（OEI-012），ahead 5，未 push
CK=/home/fisher/.onyx-lab/.secrets/admin-cookies.txt
curl -s -m 8 -b "$CK" -o /dev/null -w 'me=%{http_code}\n' http://127.0.0.1:8080/api/me   # 期望 200
```

**③ 本刀一句话**

把"引擎召回到底好不好"这个 012 挖出来的坑填掉（**移除霸榜的对照文档 + 重测**），然后把 ECE 的客户面从"dev 清单"改成**一个能在 10–15 分钟里讲完的咨询演示**：静态知识库（65 个对象、行业轴）+ 现场上传一个咨询案例 + 依据与下一步，并配一套演示脚本和一条**常驻 demo** 起链。

**④ 硬约束速查（违反即 FAIL，全文见 §8）**

- ✅ 授权改：`src/ece/consulting/**`（demo 叙事面）、`src/ece/api/**`（如需要新演示端点）、`src/ece/connectors/onyx/**`（检索修复仅在必要处）、`demos/spa/**`（**本刀是自 OEI-006 后第一把允许改前端的刀**）、`docs/API.md`、`TASKS.md`、`data/eval/retrieval/**`、`Makefile` / `onyx-lab/OEI-013/workspace/`（demo 起链脚本）、`tests/**`（新增文件；**既有断言不得改**）
- ❌ 不改 Onyx 配置（compose / `.env` / 服务端 settings）；不重启/停/删 Onyx 容器；不换模型 / 不建 LLMPort；不引入新依赖
- ❌ 不改权限/身份/记忆/内容（65 个对象一个不动）；不改三域业务断言
- ❌ **检索部分不许假装**：移除 + 重测的结论必须真实；`skip_query_expansion` 默认仍 `False`（除非重测后数字支持翻转）
- ❌ 不得要求用户截图；验收一律机器可校验（HTML 转储 + DOM 锚点 + API 原始输出）
- 📌 **本刀要常驻 demo**（与"验完即释放"相反）：demo 起链后**留在现场给用户看**，收尾只释放评测用的临时 PG、不拆 demo 链——但**结束前必须把"如何起/停/清"写进脚本与 REPORT**

**⑤ 收工与心跳**

```bash
echo "$(date -Iseconds) OEI-013 complete" > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-013/DONE
```

然后 **STOP**。心跳对象 = `onyx-lab/OEI-013/VERDICT.md`。

---

## 0. 一句话目标

把 ECE 的客户面从"能看能测的工装"升级成"**能讲给潜在客户的咨询演示**"，并把 012 挖出的检索坑填掉：① **移除霸榜的对照文档**；② 在干净语料上**重测召回**（原始 + 过滤后）；③ 把视图 D 改写为**客户语言的演示叙事**（问题 → 检索 → 依据 → 下一步），配 10–15 分钟**演示脚本**；④ 提供一条**常驻 demo 起链**，让用户开浏览器就能看。

**为什么是这一刀**（用户三连问 + 012 的发现）：

1. 用户 2026-09-26 明确："12 刀做完还没有 UI，不需要上传咨询案例吗"——可见面被一路延后，这是对 `AGENTS.md`"尽早有可见产品"的直接纠偏。
2. OEI-012 实测：**引擎召回命中率 0%**，元凶是 OEI-009 的受控对照文档（72 次里 54 次是唯一结果）。不先移除它，任何"带引用的引擎召回"演示都是假的。
3. 用户已拍板：**移除该对照文档；检索排序修复并进本刀**（不单开）。

---

## 1. 现状（codex 实测，可直接信任；每条都带"文件 + 符号 + 数值"）

### 1.1 检索现状（承 OEI-012，已量化）

- 真引擎 `/api/search`：**hit@1 = hit@3 = 0%**（expansion 开/关两档同），且**排序问题不是索引问题**（三份真文档能被召回但从不为自己那条 query 排上来）。
- 霸榜者：`ece-df16d19c9e7b-oei009-comparison-restricted.md`（`员工报销政策与发票审核流程`），72 次运行里 **61 次进 top-3、54 次是唯一结果**（`OEI-012/evidence/04-retrieval-matrix.json`，我独立重算过）。
- 该文档是 `restricted` 档，在真实 consulting library 路径会被权限过滤滤掉；但原始引擎层它霸榜。
- **用户决策：移除它。**

### 1.2 移除要改的连带物

`onyx-lab/OEI-009/workspace/rebuild_demo_state.sh` 第 5 步（`step26_demo_falsifiable.py`）会**重建这个对照文档**。只删文件不删重建逻辑，等于白删。所以移除 = 两步删除 + **让重建脚本不再把它塞进演示项目**（OEI-009 的历史证据工具保留，但 013 的 demo 起链不得复建它）。

### 1.3 演示面现状

- `demos/spa/index.html` 四视图：A 六步闭环（`/api/v1/demo/*`，即当初"太技术化"的那个）、B 架构解释、C 扩展蓝图、D 咨询知识库（65 对象 + 筛选 + 引擎分组 + 上传 + 详情）。
- 前端自 OEI-006 起**冻结至今**（`git diff` 一直零），本刀是第一把被授权改它的刀。
- `make demo` = `python -m ece.demo`（CLI 演示，不是 SPA）。
- 三份真文档**都是咨询域**（case=零售供应链降本 / methodology=问题树·假设驱动·MECE / play=销售→交付五阶段），来源 `onyx-lab/OEI-001/workspace/`。

### 1.4 演示叙事的关键事实

- 静态知识库 = `src/ece/consulting/seed/consulting_objects.json` **65 个对象**（OEI-011/014），`/api/v1/consulting/{facets,library,objects}` 数据驱动、确定性、**不需要引擎**。
- 引擎召回 = 上传到 Onyx 的文件（上传路径 OEI-007 已闭环）；权限过滤（OEI-009）在 ECE 侧 fail-closed。
- 记忆（OEI-010）与权限/审计（OEI-009）是"更深一层"的演示素材，但**本刀演示以知识库为主**，不强行塞全部。

---

## 2. 范围锁

**做**：

1. **移除对照文档** + 让重建逻辑不复建（两步语义 + 归档说明）；
2. **检索重测**：干净语料（3 份真文档）上重跑 012 的口径，含**过滤后路径**；
3. **演示 UI**：视图 D 改写为咨询演示叙事（问题 → 检索 → 依据 → 下一步），保留上传演示；
4. **演示脚本**（10–15 分钟，客户语言）+ **常驻 demo 起链脚本**；
5. 文档与提交。

**不做**（做了即越界）：

- **不做三域演示**（本刀只做**咨询单域**；"三域复用"是架构解释里的一句话，不是本刀要建三个 demo）；
- 不改 Onyx 配置 / 不换模型 / 不建 LLMPort / 不引入新依赖；
- 不改权限/身份/记忆/内容（65 个对象一个不动）；不重做完整的六步闭环引擎；
- 不把引擎召回当成演示的"承重墙"（见 §3.2：演示以静态目录为主、引擎召回为辅）。

---

## 3. 契约（**本刀锁定**；发现契约与实测不符 → 停手 + 写 REPORT + 等 codex 对齐）

### 3.1 移除对照文档（用户已拍板）

1. 用 `DEMO-DATA-CLEANUP-2026-09-25.md` 的**两步语义**（`unlink` 204 → `delete` 200）从 Onyx 项目 1 删除 `ece-…-oei009-comparison-restricted.md`；删除前先只读快照（项目 1 文件清单 + 该项目登记行，若有）。
2. **更新重建/起链逻辑**：013 的 demo 起链**不得复建**它；`rebuild_demo_state.sh` 是 OEI-009 的**历史证据工具**，要么改掉第 5 步、要么在本刀新增一个不含它的 demo 起链脚本（二选一，写清理由）。
3. 归档说明写进 `workspace/removal-note.md`：删的是什么、为什么（霸榜污染检索）、原用途（OEI-009 权限演示）、如何恢复（历史脚本仍在）。

### 3.2 检索修复边界（**诚实优先，不许假装**）

1. 移除后，用 `OEI-012` 的评测集（`data/eval/retrieval/consulting-demo.json`，去掉针对对照文档的 miss 行）在**干净语料**上重测：**原始引擎** + **过滤后**（`skip_query_expansion` 两档都跑，N=3）。
2. 结论必须真实。若命中率改善到可演示 → 用之；若仍差 → **本刀检索部分只做到"把确定性、可复现的路径接进演示"**：优先用 `skip_query_expansion=true` 的确定性向量路径，必要时加**确定性**客户端 query rewrite（无 LLM），**不改 Onyx 配置、不换模型**。
3. 无论结果如何，**演示叙事的承重墙是静态目录**（65 对象、确定性、行业轴），引擎召回只作为"你上传的文件"的 live demo——这条不因重测结果改变。

### 3.3 演示 UI（视图 D 改写）

1. 把视图 D 从"dev 清单"改成**咨询演示叙事**，至少三个可见段：**① 一个问题**（输入框，默认一句真实业务问题）、**② 知识库怎么答**（静态目录命中 + 行业/类型筛选 + 详情依据）、**③ 你的文件**（上传一个案例 → 出现在引擎召回组，带来源与片段）。
2. 保留既有 DOM 锚点（`#consulting-search` / `#consulting-filters` / `#consulting-cards` / `#consulting-engine*` / `#consulting-upload*` / `#consulting-detail`）或**等价替换并更新任何引用它们的测试**——**不得为了迁就 UI 改既有测试断言**，要改就改装配/新增。
3. 可访问性/可见性证据一律**机器可校验**（HTML 转储 + DOM 锚点 + 经同源代理的 API 原始输出），**不许要求用户截图**。

### 3.4 演示脚本 + 常驻 demo

1. `workspace/demo-script.md`：10–15 分钟、客户语言，至少三幕（问题 → 知识库 → 上传你的文件），并把"我们做了什么 / 边界 / 下一步"讲清；**不推进客户验证材料**（那是另一阶段）。
2. `workspace/demo-up.sh`：一条命令起整条链（PG → migrate → seed → 回填 → uvicorn 8765 → 反代 8181），**内置 `no_proxy` 处理**（OEI-006 的教训），并打印浏览器 URL。脚本**可重复执行**（幂等：已起则不重复起）。
3. 演示期间**常驻**；REPORT 写清"如何起 / 如何停 / 如何清"。

---

## 4. 工作区与证据命名

```
onyx-lab/OEI-013/
├── TASK.md      ← 本文件（只读）
├── workspace/   ← demo-up.sh / demo-script.md / removal-note.md / 检索重测 runner
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

建议证据文件：`00-corpus-before-after.json`、`01-removal-two-step.txt`、`02-retrieval-rematrix.json`、`03-retrieval-filtered.json`、`04-ui-dom-proof.md`、`05-demo-script.md`（指向 workspace）、`06-demo-up-idempotent.txt`、`07-contract-regression.txt`、`08-test-suite-raw.txt`、`09-git-commit.txt`、`10-compliance-check.txt`、`11-check-api-docs.txt`

## 5. 任务步骤

### 步骤 0 — 移除对照文档（A1/A2 前置）

1. 只读快照项目 1（文件清单 + 登记行）→ `00-corpus-before-after.json`；
2. 两步删除该文档 → `01-removal-two-step.txt`（含状态码）；
3. 改/新增起链逻辑使其不复建 → `workspace/removal-note.md`。

### 步骤 1 — 检索重测（A3/A4）

1. 用 012 的 runner + 评测集（去掉针对对照文档的 miss 行）在干净语料上重跑：`skip_query_expansion` 两档 × N=3，**原始引擎层**；
2. **过滤后路径**再测一次（走 consulting library 的匿名调用，记 `engine_items` 的 title 集）；
3. 落 `02-retrieval-rematrix.json` + `03-retrieval-filtered.json`；结论写进 REPORT（改善/仍差，如实）。

### 步骤 2 — 演示 UI（A5）

1. 按 §3.3 改写视图 D（三可见段 + 保留/等价锚点 + 不迁就测试改断言）；
2. 机器可校验的 DOM 证据 → `04-ui-dom-proof.md`。

### 步骤 3 — 演示脚本 + 常驻起链（A6/A7）

1. `workspace/demo-script.md`（§3.4）；
2. `workspace/demo-up.sh`（幂等 + no_proxy + 打印 URL）→ `06-demo-up-idempotent.txt`（连跑两次，第二次不重复起）；
3. **把 demo 链起起来留给用户看**（常驻）。

### 步骤 4 — 契约不回归 + 全套件（A8）

1. consulting / demo / onyx 相关子集 + 键集合对照 → `07-contract-regression.txt`；
2. 收尾一次全套件（临时 PG + 完整前置链 + `-rs`）→ `08-test-suite-raw.txt`；期望 859 + 新增、0 failed。

### 步骤 5 — 文档 + 提交 + 合规（A9/A10/A11）

1. `docs/API.md`（如新增演示端点/语义）、`TASKS.md 附录 T`、`Makefile` 若加 `demo-up` 目标；
2. `git add` + `git commit`（**不 push**）→ `09-git-commit.txt`；
3. `make check-api-docs`（`11`）+ 收尾三查 + 密钥扫描 + 内存快照（`10`）；**不拆 demo 链**（那是交付物）。

---

## 6. 验收标准（codex 将逐条核对；**每条都必须能被 evidence 证明**）

- [ ] **A0** 前置：凭据 200；语料快照（4 份）落盘；HEAD=a4a67c28→4a67c28 前的基线单测落盘
- [ ] **A1** 移除对照文档：两步删除（`unlink` 204 → `delete` 200）原始状态码；移除后项目 1 只剩 3 份真文档；`removal-note.md` 说明归档与恢复方式
- [ ] **A2** 不复建：demo 起链逻辑不再创建该文档（给出脚本 diff + 一次起链后项目 1 仍 3 份的实测）
- [ ] **A3** 检索重测：干净语料上 N=3 × 两档（原始 + 过滤后）各跑一遍，hit@1/hit@3/复现性/延迟**如实**落盘；口径与 012 一致
- [ ] **A4** 检索结论诚实：若改善给出数字；若仍差，明确写"本刀不假装修复"，并按 §3.2 把确定性路径接进演示（`skip_query_expansion=true` ± 确定性 rewrite），不改 Onyx 配置/不换模型
- [ ] **A5** 演示 UI：视图 D 三段（问题/知识库/你的文件）可见且机器可校验（HTML 转储 + DOM 锚点 + API 原始输出）；**未迁就 UI 改既有测试断言**
- [ ] **A6** 演示脚本：`workspace/demo-script.md` 客户语言、10–15 分钟、含三幕与"我们做了什么/边界/下一步"
- [ ] **A7** 常驻起链：`demo-up.sh` 一条命令、幂等（连跑两次不重复起）、内置 no_proxy、打印 URL；**demo 链起好留给用户看**
- [ ] **A8** 契约不回归：consulting/demo/onyx 子集全绿；`/library`、`/facets` 键集合不变（UI 改动不得破坏 API 契约）；全套件 0 failed（859 + 新增）
- [ ] **A9** 文档：`docs/API.md`、`TASKS.md 附录 T`、`Makefile`（如加目标）；`make check-api-docs` 仍 `App-only 0`
- [ ] **A10** 提交：`git commit`（**不 push**）+ 短 hash 与文件清单
- [ ] **A11** 合规与资源：未碰 Onyx 配置/compose/.env；容器 RestartCount=0；无新依赖；未改 65 个对象与三域断言；密钥只 `<REDACTED>`；收尾三查（**不拆 demo 链**，但评测临时 PG 释放）；未 push
- [ ] **A12** 证据纪律：全部机器可校验；无"看起来更专业"这类不可判定表述；无用户截图；demo 起链可复现（附命令）

## 7. 完成后的动作（严格按序）

1. 自检目录与证据完整性、无密钥泄漏、评测临时资源已清（demo 链除外）
2. `echo "$(date -Iseconds) OEI-013 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭；FAIL → 按 `R1/R2…` 返工后重建 `DONE`

---

## 8. 硬约束（违反即 FAIL）

- ✅ **授权改**：`src/ece/consulting/**`、`src/ece/api/**`（如需要）、`src/ece/connectors/onyx/**`（检索修复必要处）、`demos/spa/**`（**本刀起解冻前端**）、`docs/API.md`、`TASKS.md`、`data/eval/retrieval/**`、`Makefile`、`tests/**`（新增；**既有断言不得改**）；可起临时 PG；可 `git commit`（**不 push**）
- ❌ **不改 Onyx 配置**（compose / `.env` / 服务端 settings）；不重启/停/删 Onyx 容器；不换模型 / 不建 LLMPort；不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）
- ❌ 不改 65 个种子对象与三域业务断言；不改权限/身份/记忆的实现
- ❌ **检索不假装**：重测结论必须真实；`skip_query_expansion` 默认仍 `False`（除非重测数字支持翻转且写决策）
- ❌ 不得要求用户截图；密钥只 `<REDACTED>`
- 📌 **常驻 demo 是交付物**：起链后留在现场；收尾只释放评测临时 PG，不拆 demo 链；REPORT 写清起/停/清
- 📌 穷尽性断言必须附可复现命令；真引擎取证不得用 mock 顶替

## 9. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-013/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-013/DONE`
- 无新文件则静默，不重复执行、不打扰用户
