# OEI 路线图（新主线）

> 制定：2026-09-23 ｜ 编号规则：`OEI-00N`（Onyx Enterprise Integration）
> 铁律：**每一刀必须有"马上能看到 + 能测"的功能或 UI 改进**，让用户当刀就能提优化意见，避免若干刀之后才发现方向不对。
>
> **编号纪律（2026-09-24 起生效）**：① 一刀返工一律标 `OEI-00N R1` / `R2`，**不再插入新刀、不再全体顺延**；② 新工作取下一个未占用序号；③（历史说明）OEI-002/OEI-004/OEI-005 曾因顺序调整而插入并顺延过既有草案，该做法**自此停止**。
> **证据纪律（2026-09-24 起生效）**：① **验收标准不得要求用户产出截图**，UI 可见性一律用机器可校验证据（HTML 转储 + DOM 锚点断言 + 经同源代理的 API 原始输出）；② **取证必须用真实引擎（`ECE_CONTENT_ENGINE=onyx`）——失败路径同样不得用 mock 代替**（OEI-007 R1 的教训）。
> 说明：**OEI-001～OEI-008 已收束**（001 条件关闭、其余七刀 PASS）；OEI-009 之后为规划草案，逐刀由 codex 细化后再签发。

> **回归基线（更新于 OEI-008）**：全套件 `757 passed / 0 failed / 5 skipped`。**已知 flake**：`tests/integration/test_s20_audit_webhook.py::test_webhook_receives_event`（≈1/12，固定 `sleep(0.5)` 竞态）。**判断回归时：只允许这一条失败，出现任何其它失败都是真回归。**
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

### OEI-007 — 咨询文档入库管道（上传 → 引擎入库 → 咨询元数据 → 立即可召回）〔**已通过 PASS**（首轮 FAIL → `R1` 重取证据 → 二轮 PASS），见 `OEI-007/VERDICT.md` §7〕

- 任务书：`OEI-007/TASK.md`
- 做什么：给 `ContentEnginePort` 加**写路径**（`upload_document()` / `document_status()`，Onyx + Mock 双实现）→ ECE 侧新增 `POST /api/v1/consulting/documents`（multipart）→ 复用 36 个种子对象的**既有咨询词表**打元数据（确定性词典建议，N=5 一致）→ 索引状态可见 → **上传后立刻能被 Library 的 `engine_items` 召回**（闭环）
- **与草案的关键差异**：草案原写"ECE 侧做 docx/pdf/xlsx/pptx 文本抽取"，现改为 **抽取交给引擎**（Onyx 自带文件处理器）→ **不引入任何解析依赖**，二进制样本用 `zipfile`+XML 构造。理由：符合"不自研通用能力"红线，也避免依赖膨胀
- 步骤 0 收 OEI-006 两项尾巴（`make seed-fixtures` 补第 4 个 seeder；cut_045 守卫补"无 DB"）
- 边界：不做权限/审计（OEI-008）、不做检索质量调优、不扩种子内容、**LLM 自动打标不做**（不确定性无法验收）
- **证据纪律**：本刀起，UI 可见性一律**机器可校验**（HTML 转储 + DOM 锚点 + 经代理 API 原始输出），**不再要求用户截图**
- **实测结果（2026-09-24 23:5x，首轮 FAIL，返工 `OEI-007 R1`）**：**实质全部成立并经 codex 独立复现**——真实 onyx 模式下上传新文档 → `COMPLETED/chunk_count=1` → 用内容贴近的 query 在 `/library` 的 `engine_items` 里**召回到我自己刚上传的文档**；静态 36 对象零变化、`pyproject` 零 diff、737/0 无回归、可见性证据机器可校验。**唯一 FAIL**：`07-failure-paths.json` 里"引擎不可达上传"填了 **mock 的 happy path**、"status 502"记成了 **404**，与报告正文矛盾（**代码是对的、报告是对的、证据是错的**）→ 返工只需重取这 2 条原始响应
- **codex 独立复查发现（转出）**：`project id=1` 已被 **12 份测试产物**污染（叠加 Onyx `top-k≈2`，Library 引擎分组会显示探针垃圾）；`/api/search` 冷态 12–44s、索引传播 10–60s；"立即可召回"的准确表述是"**内容贴近的 query + 索引完成后约 1 分钟内**"

### OEI-008 — ContentEnginePort 身份穿透（identity threading）〔**已通过 PASS**（首轮 FAIL → `R1` 恢复 DB 无关单测 → 二轮 PASS），见 `OEI-008/VERDICT.md` §8〕

- 任务书：`OEI-008/TASK.md`
- 做什么：给 Port 的**五个方法**都加身份维度（`Identity` / 最小 `EngineCallerContext`，类型可缺省但边界必须显式解析）→ 用 **Port 引擎描述符**消掉 `engine_merge.py` 里"逐字复制 selector 判断"的债务 → 两端适配器实现（mock 身份可观测且确定；onyx 接受身份并留痕）→ 4 个调用点接线 → 审计留痕 → 把"**CE 无法下推权限 → 引擎召回只能事后过滤（有侧信道风险）**"写成文档
- 步骤 0：① ~~完成 `OEI-007 R1`~~ **已完成**（2026-09-25 00:01 重建 `OEI-007/DONE`，codex 二轮审验 PASS）；② `TASKS.md` 与真实代码对账（外部 review 第 3 条：checklist 勾选率几乎全空，严重低估进度）——**只剩②**
- 为什么现在做：外部 review 指出"identity 债务在变贵"，codex 核实为真——`port.py` 五方法确实无身份维度，`engine_merge.py:50-58` 确实手抄了 selector 逻辑，调用点已有 4 处
- 边界：**不做**权限过滤算法（009）、**不做**记忆（010）、不做多租户；不引入新依赖
- **实测结果（2026-09-25 09:5x，首轮 FAIL 一条）**：主干全部达标并经 codex 独立复核——Port 五方法带身份（类型可缺省）、**描述符消掉了 `engine_merge` 手抄 selector 的债务**、四调用点接线且有十种组合实测矩阵（upload 匿名 403 / 带身份 200）、CE 权限限制成文（M1–M3 缓解方向）、**零新依赖**、全套件 **757 passed / 0 failed**（+20 新增身份单测）。**亮点**：cc 用证据反推发现并修掉两个真实审计漏洞（`engine_status` 的 `ok` 审计写在 return 之后=死代码；`search` 成功路径完全无审计）——"只记失败的审计答不了'谁读了引擎'"。**唯一 FAIL（A8）**：被改过的 `tests/unit/test_consulting_documents.py` **失去 DB 无关属性**（无 DB 时挂在第 20 条附近，而 OEI-007 时它 5.5s 跑完 32 条），且**未申报**
- **基线 caveat（重要）**：`test_s20_audit_webhook.py::test_webhook_receives_event` 是**既有 flake（≈1/12，已用 worktree 对照量化）**，机制是固定 `sleep(0.5)` 的后台投递竞态 → **后续判断回归：只允许这一条失败**
- **codex 自身缺陷（已修订 TASK v1.1）**：§7 原写"`tests/**` 仅允许新增文件"与步骤 7 的回归改造自相矛盾，已改为"允许改装配部分、断言不得动"
- **转出**：引擎调用审计的**持久化设计**（现为进程内 `audit_log`，非 `src/ece/audit/` 表）→ 列为 009 交付项；`check_api_docs.py` 解析器误报 4 条 consulting 路由 → 随 009 处理

## 规划中（草案，未签发）

### OEI-009 — 权限与审计接线（复用既有 permission engine）

- 背景更新（外部 review + codex 核实）：ECE **已经有**成体系的权限引擎（`permissions/engine.py`：deny > user > role > dept > classification 默认 > default deny，**SQL 子查询过滤而非后置过滤**，且留有一次真实越权修复的记录）与审计基础（`0005_context_audit`）。因此本刀**不是从零做"最小闭环"，而是"接线"**：把既有引擎接到 OEI 这条线上
- 交付：① 检索/上传的**结果级权限过滤**（在 ECE 侧，因为 CE 无法下推）；② **org scope 权限骨架**（为组织级记忆预留，见 OEI-010）；③ 一次检索的"来源与审计"记录可查
- 测试：越权访问必须被拒（含负例）；审计字段完整；**事后过滤的侧信道（排序/计数）要有明确处理**

### OEI-010 — 持久上下文记忆 v1（用户级 + 组织级）

- 交付：记忆作为**一等领域对象**（owner / scope(user|org) / statement / source / created_at / confidence / expires_at）→ 写入过权限引擎 → 读取进 `context/assembly.py` 的显式一步（**位置在权限判定之后**）→ 自动注入
- 范围（用户 2026-09-25 决策）：**用户级偏好与事实** 与 **组织级记忆（口径/术语/模板）** 都做；因此权限骨架必须一开始支持 org scope
- **明确不做**：LLM 自动抽取（不确定性无法验收）；第一版只做**显式记忆**
- **明确不做**（用户决策）：界面上不展示"本次回答引用了哪几条记忆"——太机械刻意；可追溯走既有 `context/provenance.py` 审计面
- 合规前提：可查看 / 可删除（单条+全量）/ 可追溯

### OEI-011 — 咨询内容补全（行业轴与覆盖度）

- 背景：36 个种子对象里 **`client_industry` 有 24/36 为空**，facets 的行业轴基本是废的——这是"**把咨询行业做透**"在内容维度上的直接缺口
- 交付：补全行业/阶段/方法等维度标签，提升类型覆盖（case 仅 10 / methodology 10 / risk_check 4 / industry_note 2）；并让 Library 的 facets 真正可用
- 测试：标签完成度阈值 + facets 聚合可核对（machine-checkable）

### OEI-012 — 检索质量（召回精度）

- 背景：3B 模型召回有偏（OEI-002/006 已记录：q2 漏召 play、MECE 未命中源头）；Onyx 是**向量最近邻 + 小 top-k≈2**；冷态检索 12–44s
- 交付：可量化的召回评测集 + 至少一项改进（query rewrite / rerank 参数 / 更大模型三者择一，需先做代价评估）
- 测试：评测集上的命中率前后对比（确定性、可复现）

### OEI-013 — 多域演示台（咨询 / 知识管理 / 企业合规）

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
                                      └─► OEI-007（真实文件进得来）✔ PASS
                                             └─► OEI-008（身份穿透：谁在问）✔ PASS
                                                    └─► OEI-009（权限与审计接线 + org scope 骨架）
                                                           └─► OEI-010（持久上下文记忆 v1：用户级 + 组织级）
                                                                  ├─► OEI-011（咨询内容补全：行业轴与覆盖度）
                                                                  ├─► OEI-012（检索质量：召回精度）
                                                                  └─► OEI-013（对外演示台，三域复用）
```

**依赖铁律**：身份（008）→ 权限（009）→ 记忆（010）。记忆若早于权限落地，就是又一个"后置过滤"式的越权风险；组织级记忆（010）所需的 **org scope 权限骨架必须在 009 一次做到位**，否则 010 会被迫改权限模型。**OEI-001～008 已全部收束**（001 条件关闭、其余七刀 PASS）；**下一刀是 OEI-009（权限与审计接线）**。

> **修订记录（2026-09-25）**：外部 review（见 `REVIEW-sonnet-assessment.md`）+ 用户决策后重排：**新增 OEI-008 身份穿透**（吸收"identity 债务在变贵"的判断，codex 已逐条核实）；原 008 权限壳层顺延为 **009** 并改定位为"**接线而非重造**"（复用既有 permission engine）；新增 **010 持久上下文记忆 v1（用户级+组织级）**、**011 咨询内容补全**、**012 检索质量**；原 009 多域演示台顺延为 **013**。

> **修订记录（2026-09-24 17:0x）**：为在接 Library 之前先把"回归信号"变可信，插入 **OEI-005（集成测试红灯归零）**；原 OEI-005 Consulting Library 后移为 **OEI-006**，原 006～008 顺延为 **007～009**。

> **修订记录（2026-09-24 16:0x）**：为结清前三刀累积的收尾债，插入 **OEI-004（收尾与基线整理）**；原 OEI-004 Consulting Library 后移为 **OEI-005**，原 005～007 顺延为 **006～008**。

## 明确的非目标（本阶段不做）

- 不做客户私有化部署包（那是很远的不确定事件；当前只需要方便演示）
- 不做多租户、计费、高可用、Kubernetes
- 不自研向量库/检索/通用 RAG
- 不做通用 Agent 平台；只做窄而深的领域 Agent
