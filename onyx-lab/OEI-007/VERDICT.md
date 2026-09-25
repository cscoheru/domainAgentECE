# OEI-007 审验裁定（codex）

> 审验日期：2026-09-24 23:5x ｜ 审验对象：`REPORT.md` + `evidence/`（17 个文件）+ `DONE`（23:18:43）+ ece commit `caa69e8`
> 被审任务书：`TASK.md` v1（签发 2026-09-24 22:06）
> 返工约定：本刀返工一律标 **`OEI-007 R1`**（不插新刀、不顺延编号）
> 审验方式：逐条核对 + **独立复现核心链路**（真实上传→索引→召回）+ 独立复现失败路径

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 核对依据 |
|---|---|---|---|
| A0 | 步骤 0 两项 + 文档化命令 0 failed | **PASS** | `00a`：Makefile `seed-fixtures` 真加了第 4 个 seeder（diff 可见 recipe 行 + 注释）；`00b`：skip 守卫加了 `if not os.environ.get("DATABASE_URL"): return (…)` ✓ |
| A1 | 上传端点可用 + 白名单/上限明文 | **PASS** | `02` + `docs/API.md §12`；①②③⑤ 四类拒绝原因精确（扩展名 / 0 字节 / 超 4MiB / 多文件部分成功）✓ |
| A2 | 引擎写路径真实生效（onyx） | **PASS（独立复现）** | 我自己传了一份新文档 → `document_id=9b702a96-…`、轮询 10s 后 `COMPLETED, chunk_count=1`；`GET /api/user/projects/files/1` 里能看到它 ✓ |
| A3 | 咨询元数据落在既有词表 + N=5 确定性 | **PASS** | `03`：8 组输入 × N=5 `all_deterministic=true`；`vocab_sizes={types:6, phases:5, industries:10}`；我独立跑 `tests/unit/test_consulting_documents.py` = **32 passed（无 DB）** ✓ |
| A4 | **立即可召回（核心）** | **PASS（独立复现，附精度说明）** | 我用**内容贴近**的 query `OEI-007 Closed-Loop Probe` 打 `/library` → **命中我自己刚上传的 `o7-en.txt`**；另一 query 命中 `verify-doc.md`。⚠️ 见 §3.1 关于"什么算召回"的边界 |
| A5 | facets 生效 | **PASS** | `06`：`engine_status=ok`、6 个 facet 轴齐全，engine_items 与静态 items 共存 ✓ |
| A6 | 失败路径 5 类各有原始响应 + 明确原因 | **FAIL** | ①②③⑤ 精确 ✓；**④"引擎不可达"的原始数据是 mock 模式的 happy path（`mock-000001`/`COMPLETED`）**，`status_502_engine_down` 记录的是 **404** 而非 502 → 与报告正文互相矛盾。详见 §2 |
| A7 | 幂等策略 + 证据 | **PASS** | `08`：重复上传产生独立 `document_id`（mock 单调递增 / onyx 各自 UUID），策略与理由写明；SPA 按 `engine_doc_id` 去重 ✓ |
| A8 | 二进制格式 + 零新依赖 | **PASS** | `09`：stdlib `zipfile+xml` 构造 docx（1454 B）→ COMPLETED → 可召回；`git show caa69e8 -- pyproject.toml` **为空**（我复核）✓ |
| A9 | 无回归 | **PASS** | 我读了两份原始汇总行：`11` = `737 passed, 5 skipped, 0 failed`、`12` 同；基线 705 → +32（本刀新增单测），无其他增减 ✓ |
| A10 | 可见性证据机器可校验、不得要用户截图 | **PASS** | `10`：HTML 转储与 `demos/spa/index.html` 字节一致、16 个 DOM 锚点 `present=True`、经代理 API 原始输出、leaks 0/0；报告全文**无"请用户截图"** ✓ |
| A11 | 合规 | **PASS（附注）** | `15`：凭据值级扫描（含正对照）、9 容器 `restarts=0`、`/mnt/c` 0 触碰、`origin/main` 未推进（`ahead 1`，我复核）、`pyproject`/`uv.lock` 0 diff、14 个文件全在授权清单内 ✓。**但报告 §A6 的陈述与其证据不符 → 并入 R1** |
| A12 | 报告完整 | **FAIL（窄）** | 结构完整，但 §A6 写了"status 502（引擎 down）"与"`engine rejected: transport failure`"，而提交的证据文件里**没有**这两条内容（见 §2）。**注意：这两句话在事实层面是对的，错的是证据文件** |

**汇总：11 项 PASS、2 项 FAIL（A6/A12，同一处证据错配）。**

## 2. 关键核查：代码是对的，证据是错的（附我的复现）

`07-failure-paths.json` 里两条记录与标签/正文不符：

| 条目 | 证据文件里写的 | 事实（我复现的） |
|---|---|---|
| ④ engine unreachable | `{"name":"good.md","accepted":true,"document_id":"mock-000001","status":"COMPLETED"}` —— **这是 mock 模式的 happy path**，根本没走失败路径 | 真实 onyx 模式 + 坏 base：`accepted=false, reason="engine rejected: Onyx upload transport failure: timed out"` |
| status_502_engine_down | `http_status: 404, detail="document_id='anything' not found"` | 真实：`HTTP 502, {"detail":"engine status unavailable: Onyx status transport failure: timed out"}` |

**我的复现命令（可原样重跑）**：

```bash
ECE_CONTENT_ENGINE=onyx ECE_ONYX_BASE=http://127.0.0.1:9 no_proxy=127.0.0.1,localhost \
  uv run uvicorn ece.main:app --host 127.0.0.1 --port 8767 &
curl -s -X POST 'http://127.0.0.1:8767/api/v1/consulting/documents' -F "file=@/tmp/o7-down.md"
# → accepted=false + "engine rejected: Onyx upload transport failure: timed out"
curl -s 'http://127.0.0.1:8767/api/v1/consulting/documents/anything'
# → HTTP 502 + "engine status unavailable: ..."
```

结论：**产品行为正确、报告正文准确，只有那两条证据是错的**（很可能是拼装证据时把 mock 运行的响应与 404 查询的响应填错了位置）。按既定证据纪律，证据与结论不符不能放行——但返工量极小：**重取这两条原始响应即可，代码一行不用改**。

## 3. 独立复现汇总（codex 自己跑的）

| 复现项 | 结果 |
|---|---|
| 上传 → 索引 → 召回（核心闭环） | 上传 `verify-doc.md` → `COMPLETED/chunk=1` → 用内容贴近 query 命中我自己新传的 `o7-en.txt` ✅ |
| 失败路径 ④（引擎不可达） | `accepted=false` + transport failure 原因；status → **502**（与报告一致，与证据文件不一致） |
| 新增单测（无 DB） | `32 passed`（5.5s）✅ |
| 无回归原始输出 | 737 / 0 / 5 skipped，两次一致 ✅ |
| 提交面 | `caa69e8` 14 文件；`pyproject.toml` 0 diff；seed/domain_packs 0 diff；`ahead 1` 未 push ✅ |
| 容器 | 9 个 Onyx 容器 Up 28 小时、`restarts=0` ✅ |

### 3.1 A4 的精度说明（属"边界"，不是缺陷）

Onyx 的 `/api/search` 是**向量最近邻 + 小 top-k**（我实测多次只返回 **2 条**）。因此"立即可召回"的准确表述是：

> 上传完成后（**COMPLETED**，索引传播实测 10–60s），**用一个与该文档内容足够接近的 query**，该文档会出现在召回里。

反例（我实测）：仅用文档里的**唯一标记**去搜，未必命中它自己——标记词与正文的向量并不近，而 top-k 只有 2，容易被别的文档挤掉。**这不影响本刀验收**（cc 的 A4 证据用的是内容贴近 query），但**必须写进文档**，否则下次容易误判成"召回坏了"。

## 4. 裁定

**FAIL（仅一处证据错配；代码与报告正文均无需改）**

理由：本刀的**实质全部成立且我已独立复现**——上传 → 引擎抽取索引 → Library 立即可召回这条闭环真的通了，而且跑在**真实 Onyx 引擎**上而非 mock；静态 36 个对象零变化、无新依赖、737/0 无回归、可见性证据机器可校验（不再要求用户截图）。唯一不合格的是 `07-failure-paths.json` 里**两条失败路径的原始数据与标签不符**（④ 填了 mock 的 happy path、status 填了 404），而报告正文写的却是真实行为。按证据纪律必须重取，但**返工成本约 2 分钟**。

## 5. 返工清单（R1，仅一条）

- **R1（A6/A12）** —— 重新采集并替换失败路径证据：
  1. 在 **onyx 模式 + `ECE_ONYX_BASE` 指向不可达地址**下，重采"引擎不可达"上传的**完整原始响应**（期望：`accepted=false` + `reason` 含 `transport failure`）；
  2. 同环境下重采 `GET /documents/{任意 id}` 的**完整原始响应**（期望：**HTTP 502** + `engine status unavailable`）；
  3. **原地替换** `07-failure-paths.json` 里这两条（保持文件结构），并在 `REPORT.md` §A6 标注"④ 与 status-502 已于 R1 重取"。
  > 可直接用 §2 给的命令复现；**不要把 mock 模式的响应混进 onyx 场景**。

> 返工完成后：删除旧 `DONE`、重建 `DONE`（建议写 `OEI-007 R1 complete`），codex 复审。

## 6. 转出与建议（不属返工）

1. **⚠️ 演示项目已被测试产物污染（建议尽早处理）**：`project id=1` 现有 **15 份文件**，其中 **12 份是测试产物**（`probe.txt`、`oei007-08-repeat.txt` ×2、`oei007-port-probe.txt` ×2、`oei007-closed-loop-probe.txt` ×2、`oei007-probe.md`、`oei007-binary-*.docx` ×2，以及**我审验时上传的 `verify-doc.md`/`o7-en.txt`**）。叠加 **top-k=2**，现在 Library 的"引擎召回"分组**大量显示探针垃圾**。建议：① 测试改用独立 project（上传端点已支持 `project_id`），或 ② 做一次清理。**不阻塞本刀，但直接影响下次演示观感。**
2. **检索延迟与传播**：`/api/search` 冷态实测 12–44s；索引 COMPLETED 后仍需 10–60s 才进检索面。SPA 文案建议写成"已索引（可能需约 1 分钟）"。
3. **SPA 文案**：引擎分组建议由「相关文档」改为「已索引文档」（Onyx 是最近邻，不是相关性过滤）。
4. **本刀自曝并修掉的 bug 值得记一笔**：初版把"0 字节"判成请求级 413，破坏了多文件 partial-succeed 设计，cc 自行拆分 `check_single_size` / `check_aggregate_size` 修好。
5. **给后续刀的流程修正（codex 自身疏漏）**：本刀 A6 没写明"**失败路径也必须在 onyx 模式下取证**"——这正是 R1 的来源。建议此后任务书的取证条款统一加一句"**失败路径同样不得用 mock 代替**"，与 OEI-003 的"真实引擎取证"合成一条通则。

---

## 7. 第二轮审验（`OEI-007 R1` 返工后）

**返工信号**：`OEI-007/DONE` 于 **2026-09-25 00:01:32** 重建（内容 `OEI-007 R1 complete`）。

### 7.1 R1 逐项核对（codex 实测）

| 项 | 期望 | 实际 | 结论 |
|---|---|---|---|
| ④ engine unreachable | 真实 onyx 模式 + 坏 base 的原始响应 | 文件里已是 `o7-r1-down.md` / `accepted=false` / `reason="engine rejected: Onyx upload transport failure: timed out"` | **PASS** |
| status 502 | HTTP **502** + `engine status unavailable` | `{"http_status":502,"detail":"engine status unavailable: Onyx status transport failure: timed out"}`，并附 `_r1_note` 标明重取环境 | **PASS** |
| 其余场景未被改坏 | ①②③⑤ + 两条 request-level 原样 | 7 个 scenarios 全在，① 1 拒 / ② 1 拒 / ③ 1 拒 / ⑤ 1 收 2 拒 / ⑥ 422 / ⑦ 413 —— 与首轮一致 | **PASS** |
| 代码一行未改 | HEAD 仍 `caa69e8` | `git log -1` = `caa69e8`；`ahead 1`（未 push） | **PASS** |
| 报告标注 | §A6 标注已重取 | `REPORT.md:74` 标题与 76–85 行有 R1 修订记录，写明"仅做证据重取、代码一行未改" | **PASS** |

### 7.2 裁定

**PASS —— OEI-007 关闭。**

理由：首轮唯一不合格项（两条失败路径证据与标签/正文不符）已按原样重取并原地替换，**代码分支未动、其余证据未受影响**。本刀的核心命题——**"一份咨询文档从上传到能被 Library 召回"这条链路真实可用**——首轮已由 codex 独立复现（真实 onyx 模式下上传新文档 → COMPLETED/chunk=1 → 内容贴近的 query 召回到该文档），本轮回合不再重复。

**本刀交付（可放心使用）**：`ContentEnginePort` 写路径（`upload_document` / `document_status`，Onyx + Mock 双实现）、`POST/GET /api/v1/consulting/documents`、确定性咨询元数据建议（词表复用 36 个种子对象）、失败矩阵、幂等策略、**零新依赖**（docx 用 stdlib 构造）、737/0 无回归、机器可校验的可见性证据（无用户截图）。

### 7.3 与 OEI-008 的衔接

`OEI-008/TASK.md` 步骤 0.① 就是本 R1 —— **现已完成**，因此 OEI-008 执行时只剩步骤 0.②（`TASKS.md` 与真实代码对账）需要做。

**仍未处理的转出项**（见 §6，不阻塞）：`project id=1` 被 12 份测试产物污染（叠加 `top-k≈2` 会影响演示观感）；SPA 文案与检索延迟说明。
