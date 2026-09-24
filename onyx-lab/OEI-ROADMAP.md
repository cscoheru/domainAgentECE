# OEI 路线图（新主线）

> 制定：2026-09-23 ｜ 编号规则：`OEI-00N`（Onyx Enterprise Integration）
> 铁律：**每一刀必须有"马上能看到 + 能测"的功能或 UI 改进**，让用户当刀就能提优化意见，避免若干刀之后才发现方向不对。
> 说明：**OEI-001～OEI-006 已收束**（001 条件关闭、其余五刀 PASS）；OEI-007 之后为规划草案，逐刀由 codex 细化后再签发。
>
> **修订记录（2026-09-23 22:2x）**：原 OEI-002（ECE ↔ Onyx 连接器）整体后移为 **OEI-003**，原 003～006 顺延为 004～007。原因是 OEI-001 证明了"写入侧"可用、但"查询侧"（`/api/search`）因本部署无 default LLM 而 8 次全 400，而**引擎能否被检索是 ECE 适配器的前提**。经用户决策，该阻断改由新 OEI-002 承接执行。

---

## 阶段目标

把"命令行六步闭环"升级成客户看得懂的演示系统：**咨询行业为第一个真实案例，知识管理/企业合规随后复用同一底座**。

## 已签发

### OEI-001 — Onyx CE 引擎侧验证〔条件关闭（CONDITIONAL CLOSE），见 `OEI-001/VERDICT.md`〕

- 任务书：`OEI-001/TASK.md`
- 做什么：建 project → 造 3 份咨询文档 → 上传+索引 → 3 个检索查询 → 索引前后资源诊断 → CE/EE 边界清单
- 验收要点：3 份文件全部 indexed；检索命中文档正确且引用可追溯；资源结论（i9 能否长期承载标准档）；证据全部落盘
- 为什么先做它：任何"基于 Onyx 的底座"都先得证明这台机器、这个版本能真的存、真的检、真的索引
- **实测结果**：A1–A4、A8、A9、A11 PASS；**A5/A6/A7 FAIL**（`/api/search` 8 次全 400，根因：`providers: []`，零 LLM）
- **处理**：经用户决策，R1 不在本刀返工，**移交 OEI-002 执行**；本刀以条件关闭收束，其"查询侧可用"的结论在 OEI-002 PASS 之前**视为未证实**

### OEI-002 — 本地 LLM 部署与检索侧解封〔**已通过 PASS**，见 `OEI-002/VERDICT.md` §8〕

- 任务书：`OEI-002/TASK.md`
- 做什么：装 ollama + Qwen2.5:3b（常驻 systemd 服务、`OLLAMA_HOST=0.0.0.0:11434`）→ 接成 Onyx default LLM（`openai_compatible` + `host.docker.internal:11434`）→ 重跑 OEI-001 那 8 次检索 → 在 UI 上看到引用咨询文档的答案
- 可见产出：Onyx 界面上"提问 → 引用那 3 份咨询文档 → 给答案"的截图 + 8 次 200 的原始响应
- 验收要点：`default_text` 非空；容器内可达宿主机 11434；8 次检索全部 200 且命中判定可追溯到源文档；UI 可见产物存在
- 为什么先做它：在引擎"查询侧"未被证实之前设计 ECE 适配器，等于在未验证的能力上做接口
- **实测结果（2026-09-24）**：本地 ollama + Qwen2.5:3b 部署成功，`default_text` 生效，容器可达；**`/api/search` 8/8 由 400 转 200（codex 独立复现）**，重复性确定
- **三轮审定结果（2026-09-24 10:2x）**：A1–A12 全部达成（A8 按修正后的可达标准判定；A11 残留已修）→ **PASS**
- **转出到 OEI-003 的两项**：①（**强制项**）Onyx CE 自带 UI 不渲染引用、答案未 grounding，ECE 必须自己渲染引用；②（收尾项）`12-ui-proof.md` §1.2 的画面描述需按实际改写
- **遗留风险**：**swap 已用 7.7/8.0GiB**（演示前需处置）；热态单查询 10–18s；3B 召回质量不足（q2 漏召 play、MECE 未命中源头文档）

### OEI-003 — ECE 侧 Content Engine Port 与引擎状态页〔**已通过 PASS**，见 `OEI-003/VERDICT.md` §7〕

- 任务书：`OEI-003/TASK.md`
- 做什么：在 ECE 侧定义自有接口 `ContentEnginePort`（`search()` / `engine_status()` / `list_projects()`）+ `OnyxContentEngineAdapter` + `MockContentEngineAdapter`（env 切换）→ 交付 `GET /engine/status` 引擎状态页，真实显示版本/tier/provider/default model/项目数/检索耗时，**并由 ECE 自己渲染"查询 → 召回文档 → 片段"的引用**
- 可见产出：能打开的引擎状态页（含引用区），mock 模式下也能打开
- 测试：确定性（同 query ×10 逐次一致）、契约一致性（mock 与真实 adapter 同构）、降级路径（引擎不可达时明确提示不裸崩）、无回归（`uv run pytest -m "not eval and not eval_llm"` 通过数不减）
- 为什么是它：OEI-002 已证"引擎能检索"，本刀回答"ECE 怎么用上它"，并把 Onyx UI 的引用缺陷用自有界面绕过去
- 边界：**ECE 领域层不得直接依赖 Onyx**；只读调用 Onyx `/api/*`，不改 Onyx 任何配置
- **首轮（13:5x）**：功能全部落地可用，但证据**全在 mock 模式**下取 → FAIL，签发 R1–R6
- **二轮（15:5x）**：R1–R6 全部处置——引用渲染/确定性/契约**改用真实 Onyx 引擎**取证（codex 现场独立复跑确认：HTTP 200、`onyx`、`v4.7.8`、渲染出 `methodology-framework.md`）；A8 全量 `pytest` **634→634**，28 failed + 5 errors 经 codex 独立根因核查确认为环境所致（684 个 `._*` Mac 垃圾文件 + 未跑 `make seed`）→ **PASS，本刀关闭**
- **遗留（非阻塞）**：`ece/` 仓改动未提交（建议先提交以建立干净基线）；`ece/TASKS.md` / `docs/API.md` 未回填；2 个未运行的遗留容器 `ece-db-1`(Exited) / `ece-api-1`(Created) 待清理

### OEI-004 — 收尾与基线整理〔**已通过 PASS**，见 `OEI-004/VERDICT.md` §7〕

- 任务书：`OEI-004/TASK.md`
- 做什么：① 删 2 个遗留容器；② 清掉 `ece/` 里 **684 个 `._*` Mac 垃圾文件**（它们正在真实破坏 5 个测试）+ 加 `.gitignore` + 消模式位噪音；③ 回填 `ece/TASKS.md` / `docs/API.md`；④ 把 CE/EE 边界 5 项强制项从 `UNKNOWN` 收敛；⑤ 按 **Makefile 正确前置（含 `make seed`）**重跑真实测试基线（baseline / after-clean / post-commit 三组）+ 提交 ECE 改动
- 可见产出：干净的 `git status`、可复现的三组测试数字、回填后的文档、CE/EE 边界证据
- 为什么插入它：前三刀累积了"仓库脏 + 流程脏 + 账没结"三类债，不结清会污染后面每一刀；尤其 `._*` 已经在造成假失败
- 为何先做它而不是直接接 Library：Consulting Library（原 OEI-004）依赖一个**可信的测试基线**，否则改完无法判断是否回归
- **实测结果（2026-09-24 16:5x）**：**实体工作全部达标且经 codex 独立复核**——684 个 `._*` 垃圾清零（我复跑 redaction 测试 = 6 passed）、5 个 error 确实消失、2 个遗留容器删净、`TASKS.md`/`docs/API.md` 回填到位、CE/EE 边界前 4 项有本机实证、2 个 commit 干净未 push（`ahead 3`）、临时 PG 与 worktree 已清
- **二轮（16:5x）**：实体工作全部达标，但 A7/A6 归因错误、A5 第 5 项证据强度高估、evidence 清单有误 → FAIL（仅文档更正）→ 签发 R1–R5
- **三轮（17:0x）**：R1–R5 全部处置。**承重 A/B 经 codex 独立验证**：左 `OEI-003/10-test-after.txt`（主树有垃圾）= 5 errors 且正是那 5 个 redaction 用例；右 `OEI-004/10-test-after-clean-raw.txt`（主树已清理）= 0 errors。A5 收敛为"4 项本机实测 + 1 项 `EE(INFERRED)`"（`audit` 路由 0 条）→ **PASS，本刀关闭**
- **可信结论**：**无回归成立**（27 failed 三次一致 + 最终树 654 passed / 0 errors + 纯增量改动），但三组数字间同时变了三个变量（worktree/主树、垃圾有无、seed 有无），**不构成受控 A/B**——报告已如实这样写，并给出单变量基线做法（主树 `git revert --no-commit`）
- **遗留**：27 个集成边界测试失败**仍无人解释**（三次一致，属独立问题，建议单开一刀）；CE/EE 官方文档 URL 待网络可达时补；`swap`/`.wslconfig` 待用户重启生效

### OEI-005 — 集成测试红灯归零（fixture 前置与真缺陷分辨）〔**已通过 PASS**，见 `OEI-005/VERDICT.md` §7〕

- 任务书：`OEI-005/TASK.md`
- 做什么：把稳定的 **27 个集成失败**逐个归因（环境步骤缺失 / 测试过时 / 真缺陷）→ 分步补前置（`gen-dataset` → `seed` → `seed_temporal_roles` → `seed_knowledge_fixture` → `seed_compliance_fixture`）并**记录每步消掉哪几条** → 把完整前置链做成 `Makefile` 里可发现的一步
- 可见产出：`27 → N` 的真实数字 + 逐条去向表 + `Makefile` 新目标与 `README` 前置链说明
- codex 侦察结论（待证实）：**大概率不是产品缺陷**——失败要的实体（`comp:v0-compliance-fixture` / `km:v0-knowledge-fixture`）恰好由仓里两个专用 seeder 写入，而这两个 seeder **只写在 `deploy/` 文档里、`Makefile` 完全没有**，所以按 Makefile 前置跑必然缺 fixture
- 铁律：**不改产品代码、不改测试断言、不删测试**；若发现真缺陷 → 不修，只交最小复现与影响面（另开一刀）
- 为什么插在 Library 之前：后续每一刀都要靠测试信号判断"我这次改坏了没有"，27 个红灯不消，等于没有回归信号
- **实测结果（2026-09-24 18:0x）**：**真缺陷 = 0 个**。分步实验证实红灯全部来自"前置未跑"：`48 failed →（gen-dataset+seed）25 →（3 个 fixture seeder）1`；残留 1 条 = `test_cut_045_local_origin_smoke`（需 nginx + 前端构建产物的部署栈，范围外）。每个 seeder 的 self-check 输出均落盘；`git diff --stat src/ece tests` 为空（未改产品代码/测试）；commit `dd58297` 未 push
- **二轮（18:1x）**：R1–R3 全部处置——`errors` 列改为真实值 **0**（并贴出四份汇总行原文解释误读）、"25 条"更正为 **24** 并与 §0/A3 三处对齐（附 `24+1+2=27` 对账）、补上"归属为推断而非逐步实测"的澄清。raw 文件 mtime 未变（**确未重跑 pytest**）→ **PASS，本刀关闭**
- **本刀最大产出**：把"27 个说不清的红灯"变成可复现的前置链 —— `Makefile` 新增 `seed-fixtures` / `test-integration` 目标 + `README.md` 前置链段落；**回归基线 = 1 failed / 680 passed，任何多于 1 的失败都是真回归**

### OEI-006 — Consulting Library 接真实检索〔**已通过 PASS**，见 `OEI-006/VERDICT.md`〕

- 任务书：`OEI-006/TASK.md`
- 做什么：把 KC-001 的 Consulting Library 从"纯静态目录"变成"**静态目录 ∪ 引擎召回**"——`/api/v1/consulting/library` 新增 `engine_items` + `engine_status`（**静态字段零变化**），SPA 的 view-d 渲染"静态 vs 引擎"两组卡片，引擎卡带来源元数据与片段，三种状态（ok / unavailable / 无命中）都有可见反馈
- 可见产出：Local Library 页同时出现静态卡片与引擎召回卡片（`http://127.0.0.1:8181/#d`，启动链路 codex 已实测跑通）；API 层 onyx 模式的 `engine_items` 可追溯到 `OEI-001/workspace/` 原文
- 测试：**DB 无关单元测试**（映射/合并/`engine_status` 三分支/异常路径）+ mock 与 onyx 契约同构 + 静态侧零变化 + 无回归（≤1 failed）
- 为什么是它：前五刀把地基铺完（能存 / 能检 / ECE 用上引擎 / 仓库干净 / 回归信号可信），**这是第一刀"客户能看懂"的东西**——也正是 `AGENTS.md` 里"Case First + 可追溯"的第一版落地
- 关键教训已写进任务书：证据**必须在 `ECE_CONTENT_ENGINE=onyx` 下产生**（OEI-003 的 mock 取证教训）；源码查看端口用 **8181**（8080 被 Onyx 占用）
- **codex 签发前发现的附带问题（已并入本刀步骤 0）**：`test_cut_045_local_origin_smoke` **每跑一次泄漏一个 uvicorn 子进程**——现场查出 **10 个游离进程、RSS 合计 558MB**，启动时间与四次套件运行一一对应。本刀步骤 0 = 清掉游离进程 + 在该测试里无条件回收子进程 + 本地无部署栈时改为显式 `skip`（预期回归基线由 `1 failed / 680 passed` 变为 `0 failed / 680 passed / 6 skipped`）
- **实测结果（2026-09-24 19:1x，PASS）**：真实 onyx 模式下 `/api/v1/consulting/library?q=问题树怎么用` → **200 / `engine_status=ok` / 命中 `methodology-framework.md`**（codex 独立复现）；降级 → **200 / `unavailable` / 静态 3 条零变化**（独立复现）；**静态载荷 sha256 两侧一致**（`9dd0f1917b1941ae`）；DB 无关单测 **24 passed**；套件 **705 passed / 0 failed**（基线 681 / 0）；**进程泄漏已修**（跑完残留 0）；commit `7ab17fc`（10 文件）未 push
- **本刀自曝并修复的真实 bug**：`EngineItem.updated_at` 类型不符导致 **onyx 模式 500**（mock 模式永远测不出）——再次印证"必须用真实引擎取证"
- **转出（下刀步骤 0）**：① `make seed-fixtures` 未含 `seed_v0_spike_fixture.py`，导致 README 文档化的命令仍显示 `1 failed`，与真实基线不一致；② cut_045 smoke 的 skip 守卫未覆盖"无 DB"（我实测不设 `DATABASE_URL` 时仍 FAIL 而非 SKIP）

## 规划中（草案，未签发）

### OEI-007 — 上传管道（真实文件进得来）

- 交付：上传页 + 后台处理（docx/pdf/md/xlsx/pptx → 文本抽取 → 结构化标签 → 入 Onyx project），带进度与失败原因
- 可见产出：用户拖一个文件进去，能看到"解析中 → 已索引 → 可被检索"的完整状态
- 测试：每种格式至少 1 个样本的端到端用例；坏文件（加密/超大/乱码）必须给出明确失败原因

### OEI-008 — 权限与审计壳层

- 交付：ECE 侧的身份/角色/来源/审计最小闭环（谁能看哪个 project、哪次检索被谁触发、证据从哪来）
- 可见产出：角色切换开关 + 一次检索的"来源与审计"面板
- 测试：越权访问必须被拒（含负例）；审计记录字段完整且不可改

### OEI-009 — 多域演示台（咨询 / 知识管理 / 企业合规）

- 交付：同一底座上可切换行业 pack 的演示台，把六步闭环改写成客户语言的业务叙事（输入真实问题 → 取上下文 → 给结论 + 依据 → 下一步动作）
- 可见产出：一个能在 10～15 分钟内讲完的演示页（含架构解释：我们做了什么、为什么做得到、未来企业 Agent 蓝图）
- 测试：三个场景各跑一遍全流程；断网/引擎不可用时页面有明确提示

## 依赖与顺序约束

```
OEI-001（引擎能否存：写入侧，已证）
   └─► OEI-002（引擎能否检：查询侧，待证）
          └─► OEI-003（ECE 怎么接）
                 └─► OEI-004（收尾：干净基线 + 文档 + CE/EE 收敛）
                        └─► OEI-005（测试信号可信化：27 红灯归因）
                               └─► OEI-006（接进来给人看）
                                      ├─► OEI-007（真实文件进得来）
                                      └─► OEI-008（谁来管权限与审计）
                                             └─► OEI-009（对外演示台，三域复用）
```

OEI-008 与 OEI-007 可以并行推进，但都必须在 **OEI-003** 的接口稳定之后，避免接口反复导致返工。**OEI-001～006 已全部收束**（001 条件关闭、其余五刀 PASS），测试回归信号已可信（**当前真实基线 705 passed / 0 failed**；注意 `make seed-fixtures` 还差第 4 个 seeder，见 OEI-006 VERDICT §6.1）；**下一刀为 OEI-007（上传管道）**。

> **修订记录（2026-09-24 17:0x）**：为在接 Library 之前先把"回归信号"变可信，插入 **OEI-005（集成测试红灯归零）**；原 OEI-005 Consulting Library 后移为 **OEI-006**，原 006～008 顺延为 **007～009**。

> **修订记录（2026-09-24 16:0x）**：为结清前三刀累积的收尾债，插入 **OEI-004（收尾与基线整理）**；原 OEI-004 Consulting Library 后移为 **OEI-005**，原 005～007 顺延为 **006～008**。

## 明确的非目标（本阶段不做）

- 不做客户私有化部署包（那是很远的不确定事件；当前只需要方便演示）
- 不做多租户、计费、高可用、Kubernetes
- 不自研向量库/检索/通用 RAG
- 不做通用 Agent 平台；只做窄而深的领域 Agent
