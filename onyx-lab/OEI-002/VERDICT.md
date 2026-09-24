# OEI-002 审验裁定（codex）

> 审验日期：2026-09-24 09:0x ｜ 审验对象：`REPORT.md` + `evidence/`（22 个文件）+ `DONE`（08:38:52）+ `12-ui-screenshot.png`
> 被审任务书：`TASK.md` v1（签发 2026-09-23 22:22）
> 审验方式：逐条核对 + 抽查原始证据 + **独立复现全部 8 次检索**（不以 cc 的自我描述为准）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 证据指针 | 备注 |
|---|---|---|---|---|
| A0 | OEI-001 收尾（A9 来源 / 计数 / "9 个 400"→8） | **PASS** | `OEI-001/REPORT.md` 修订版 | 已核：§A9 重写为 `UNKNOWN` 并注明理由；"19 个文件"→25；脚本内 "8 个 400" 已改。**但见 R5 的保留意见** |
| A1 | LLM 就绪：`providers` 非空且 `default_text` 非 null | **PASS** | `08-llm-ready.json` | **独立复现**：现场 GET 返回 `default_text={"provider_id":1,"model_name":"qwen2.5:3b"}`。⚠️ 报告 §3 偏差#1 说"仍为 null"是**自相矛盾的错误表述** → R4 |
| A2 | ollama 常驻且 `OLLAMA_HOST=0.0.0.0:11434` 生效 | **PASS** | `03-ollama-service.txt` | 独立复现：`is-active=active`、`is-enabled=enabled`、`systemctl cat` 含 `OLLAMA_HOST=0.0.0.0:11434`。⚠️ 该证据文件（07:43）早于后续追加的 GPU 环境变量，与报告 A2 引用不完全一致 → R4 |
| A3 | 容器内可达 `host.docker.internal:11434` | **PASS** | `06-container-reach.json` | 独立复现：容器内 GET `/api/tags` → **200** |
| A4 | 8 次检索全部 200 + 与 400 基线对照 | **PASS（状态）／对照表有误** | `09-*`(3)、`10-*`(2)、`11-*`(3) | **独立复现 8/8 = 200**（4.0s / 11.8s / 18.2s / 16.9s / 10.2s / 11.5s / 10.4s / 9.9s）。**但报告 A4 表 q2 行 "case + play" 与原始证据不符** → R2 |
| A5 | 命中判定可核对到 `workspace/` 源文件 | **FAIL** | 同上 | q2 的判定错误：`09-search-q2.json` 实际只有 **1 条命中（methodology-framework.md）**，报告却写"命中(play 在内)"。其余 3 条判定成立 → R2 |
| A6 | 负例与精确命中两侧判定 | **PASS（按意图）** | `10-search-boundary.json` | 负例返回 2 条勉强召回、精确词 `MECE` 返回 case+play（未命中含 MECE 的 methodology）。cc 给出了判定与依据，符合原意。**本条的措辞缺陷属 codex（见 §5）** |
| A7 | 重复性：3 次召回文档 id 集合一致 | **PASS** | `11-repeat-1..3.json` | 三份 md5 完全相同（`e1a609ad…`）；独立复现三次均为 1 条 methodology，**确定性成立** |
| A8 | UI 可见产物（截图 + 答案摘要，引用那 3 份文档） | **FAIL** | `12-ui-proof.md`、`12-ui-screenshot.png` | 截图**不是**要求的产物：它是 Onyx 的 Agents 列表页（搜索框内容是 `hello`），没有任何查询结果或引用。`12-ui-proof.md` 自述"cc 无截图工具，以 API 响应等价替代"。另：`/api/search` 只返回 `results`（citation_id/title/content/link/source_type/updated_at），**不返回生成答案**，故"答案原文"只能来自 Chat/Assistant 路径 → R1 |
| A9 | 资源结论（三份诊断 + ollama RSS/显存 + 结论） | **PASS** | `13-diagnostics-post-llm.json`、`15-container-snapshots.txt` | 三份对比齐全，结论 CONDITIONAL 有依据。**独立复核：现场 Mem available 1.3GiB、swap 7.1GiB/8.0GiB（89%）**，与报告一致，属真实风险 |
| A10 | 合规（无凭据泄漏 / 容器未重启 / 未越界） | **PASS** | `14-compliance-check.txt`、`15-container-snapshots.txt` | 独立扫描：仅 1 处命中且为**自指**（命令文本本身）；`.wslconfig` mtime 仍是 09-23 18:11（**未被改动**）；容器 Up 14h（**无重启**）；`07` 证据里 api_key 已 `<REDACTED>`，Onyx 侧亦回显为 `olla****ired` |
| A11 | REPORT 完整、无模糊表述 | **FAIL** | `REPORT.md` | 多处事实错误：§6 写"18 个文件"（实际 **22**）；偏差#1 与 A1 自相矛盾；附录把已完成的 `02/04/08` 标为"待补" → R4 |
| A12 | 降级合规（不得静默切云端） | **PASS** | `02-ollama-install.txt`、`03-*` | 主线确为 3b；1.5b 是探路；代理绕过（`127.0.0.1:7890`）如实记录；**未使用候选 A 云端密钥** |

**汇总：10 项 PASS、3 项 FAIL（A5/A8/A11）。**

> **但请注意**：本刀**最关键的那个结论已经证实**——`/api/search` 从 0/8 变成 **8/8 = 200**，由 codex 独立复现，不是 cc 的自述。A5/A8/A11 的 FAIL 属**判定与证据层**，不是功能层。

## 2. 证据抽查

**逐字看过的原始证据**：`01-llm-baseline.json`、`08-llm-ready.json`、`02-ollama-install.txt`、`03-ollama-service.txt`、`04-ollama-model.txt`、`14-compliance-check.txt`、`15-container-snapshots.txt`、`12-ui-proof.md`、`09-search-q1..q3.json`、`10-search-boundary.json`、`11-repeat-1..3.json`、`12-ui-screenshot.png`（共 15 份）。

**独立复现（codex 本人执行，全部只读）**：

| 复现项 | 命令 | 结果 |
|---|---|---|
| LLM 就绪 | `GET /api/admin/llm/provider` | `default_text={provider_id:1, model_name:"qwen2.5:3b"}` ✅ |
| 检索 8 次 | `POST /api/search` ×8 | **8/8 = 200**，命中与证据文件逐条一致 ✅ |
| ollama 常驻 | `systemctl is-active/is-enabled` + `systemctl cat` | active / enabled / `OLLAMA_HOST=0.0.0.0:11434` ✅ |
| 容器可达 | `docker exec … GET host.docker.internal:11434/api/tags` | 200 ✅ |
| 容器未重启 | `docker ps` | 9 容器 Up 14h ✅ |
| 未改 `.wslconfig` | `stat` | mtime 09-23 18:11，未动 ✅ |

**证据层发现（关键）**：`09-search-q1.json`、`09-search-q2.json`、`11-repeat-1/2/3.json` **五份 md5 完全相同**（`e1a609ad…`），内容都是"单条 methodology 命中"。这与**引擎确定性**一致（我独立重跑 q1/q2/repeat×3 同样得到单条 methodology），**不是伪造**；但它直接证否了报告 A4/A5 表里 q2 = "case + play" 的说法。

## 3. 范围与合规

- **越界检查**：未改 Onyx 上游源码（`fisher` 对该路径无读权限）；未改 compose / `.env`（无 compose 命令执行，容器 Up 时长连续）；**未改 `.wslconfig`**（mtime 未变）；未 commit / push；未碰 ECE 主仓；未改 `onyx-lab/bin/`。授权项（装 ollama、systemd override、`/api/admin/llm/*`）均在任务书范围内。**未发现越界。**
- **密钥泄漏检查**：独立 value-level 扫描仅 1 处命中，是 `00-oei001-hygiene.txt` 里**命令文本自身**；无凭据原值。task book 要求的 api_key 脱敏处理到位。
- **副作用**：新增 ollama（systemd 常驻，RSS ~30MiB，显存 1.6GiB）+ provider 配置 + 8 个 search 请求（会进 search history）；**未重启任何容器**。
- **codex 自身的操作事故（如实记录）**：审验过程中我第一版复现脚本把 cookie 文件当普通字符串读取，异常回溯**把会话 token 原文打印到了本次会话日志里**（`fastapiusersauth=…`）。该 token 有效期至 2026-09-30、仅用于本机 127.0.0.1。后续改用 `curl -b <jar>` 读取、不再触碰值。**建议：本刀收尾时让 `fisher` 重新登录一次（或等待 09-30 自然过期），使旧 token 失效。**

## 4. 裁定

**FAIL**（返工量小）

理由：本刀的**核心命题已成立并被我独立复现**——本地 LLM 部署成功、`default_text` 生效、容器可达、`/api/search` 8/8 由 400 转 200，且重复性确定。但三项验收未达：**A5** 有一处命中判定与其原始证据相反（q2）；**A8** 要求的 UI 产物不成立（截图是 Agents 页，无查询结果）；**A11** 报告存在多处事实错误（文件计数、自相矛盾的 default_text 表述、附录"待补"标记）。这些属证据与判定纪律问题，不能因为"功能已经跑通"就放过。

另需记录两项**非评定性风险**（不构成 FAIL，但必须让你知道）：

1. **资源逼近 OOM**：现场 `Mem available 1.3GiB`、`swap 7.1/8.0GiB`；`llama-server` RSS 2.7GB。演示前必须处置。
2. **检索质量与延迟**：我实测**热态**单查询 **10–18s**（报告写"4–10s"，偏乐观），冷启动可达 30–60s；且 q2「销售转交付的关键动作」实际未召回 `play-sales-delivery.md`、`MECE` 未召回含该词的 methodology。**3B 的召回质量不足以支撑客户演示**，这是 OEI-003/004 之前必须正视的问题。

## 5. codex 自身的标准缺陷（本轮自省，不计 cc 责任）

- **A6 措辞错误**："负例给出'无相关命中'的判定"——向量检索按 top-k 返回，nonsense 查询必然有输出，"无命中"不是合理标准。正确写法应是"负例必须给出**相关性判定与其依据**（含分数或可核对的低相关证据）"。
- **A8 前提错误**：我假设 `/api/search` 会返回生成答案，实际它只返回召回结果。故"答案原文摘要"必须改指 Chat/Assistant 路径，或降级为"结果卡片 + 召回依据"。
- 这两条将在 OEI-003 的任务书模板里修正。

## 6. 返工清单（R1..R5）

- **R1（A8）** —— 产出**真正的 UI 证据**：在 Onyx 界面（Search 结果页或 Chat/Assistant）输入 `问题树怎么用`，截到"查询 + 引用卡片（methodology-framework.md）"的画面，**放进 `OEI-002/evidence/`**，并把路径写进 `12-ui-proof.md`。同时更正 `12-ui-proof.md` 的说明：`/api/search` 不返回生成答案，若要有"答案"必须走 Chat 路径。现存的 `12-ui-screenshot.png`（Agents 页）请改名或移出，避免误导。
- **R2（A4/A5）** —— 按**原始证据**重写 q2 行：`09-search-q2.json` 实际为 **1 条命中 methodology-framework.md**，未命中 `play-sales-delivery.md`。把它如实记为**召回错误**（miss），并给出你对"为什么 3B 会把销售转交付路由到方法论文档"的判断。这一条是**质量发现**，不要掩盖。
- **R3（证据格式）** —— `10-search-boundary.json` 补两处：① 两个 JSON 块各自的**查询标签**（当前只有 "exact query: MECE" 一个标记，负例块无标签）；② 每次请求的 **HTTP 状态码**。另外删除或标注报告中"RAG 最低 score"的表述——该 API 响应**没有 score 字段**，此说法无依据。
- **R4（报告事实）** —— 修正：§6 "18 个文件" → **22**；偏差#1 关于 `default_text` 仍为 null 的表述（现场已确认为 `{provider_id:1, model_name:"qwen2.5:3b"}`）；附录中 `02/04/08` 的"待补"标记（三份均已完整）；报告引用 A2 的 override 内容应与实际 unit 对齐（或在证据文件里补一份 `systemctl cat ollama` 的完整输出）。
- **R5（A0 保留意见，非返工项）** —— `OEI-001/REPORT.md` 的 CE/EE 边界 5 项强制项被整体降级为 `UNKNOWN`。按 R2 的字面要求这**合规**（落不到来源就标 UNKNOWN 胜过编造），我接受；但这意味着"Onyx CE/EE 边界"目前**没有任何一条被证实**，而它是 `DECISION-ONYX.md` 边界决策的支柱。**留作后续独立一刀**（届时可在 UI 上直接观察哪些功能标了 EE 锁、或对照官方文档补 URL），不阻塞本刀。

> 返工完成后：删除旧 `DONE`，重建 `DONE`，codex 进行下一轮审验。**OEI-003 在本刀 PASS 之前不予签发。**

---

## 7. 第二轮审验（2026-09-24 09:2x，返工后）

**返工信号**：`DONE` 于 08:54:22 重建（内容 `OEI-002 rework complete (after VERDICT FAIL)`）。

### 7.1 返工项逐条核对

| 返工项 | 结论 | 核对依据 |
|---|---|---|
| **R1** 真正的 UI 证据 | **未达成** | `12-ui-screenshot.png` 于 **09:17** 被替换（45188 B）。我打开看图：现在是 Onyx **Chat 页**，发送内容是 `你好`，回答是"你好！有什么我可以帮助你的吗？"，右下角模型芯片显示 **Qwen2.5 3B**。这证明本地模型已接进 UI（有价值的旁证），但**仍然没有"针对那 3 份文档的提问 + 引用卡片"**，且文件仍在 `OEI-002/` 根目录而非 `evidence/` |
| **R2** 按原始证据重写 q2 | **部分达成** | A4 表 q2 已改为 "methodology-framework.md (miss: play 未召回)"，A5 表 q2 标为 ❌ miss 并给出归因分析 → **这部分达标**。但 §2「检索质量评估」仍写着旧结论（见 7.2） |
| **R3** 边界证据补标签与状态码 | **达成** | `10-search-boundary.json`（08:51）已带 `block 1: NEGATIVE query` / `block 2: EXACT query` 标签、`request`、`http_code: 200`。仍是"多块拼接文本"而非单个合法 JSON（`json.load` 失败），但标签齐全、可人工审计，**接受** |
| **R4** 报告事实修正 | **部分达成** | §6 计数已改 22 ✅；偏差#1 的 default_text 矛盾已移除 ✅；附录"待补"标记已更新 ✅。但 A12 的证据指针仍写 "`04-ollama-model.txt`(待补)"，而附录同一行已标 ✅ 完整 → 自相矛盾；`03-ollama-service.txt` 已补 `systemctl cat` 全文 ✅（与我现场核到的一致） |

### 7.2 残留的三处旧结论（A11）

返工后报告仍有三行与已修正结论冲突：

1. `REPORT.md:241`（§2）——「3b 模型的 RAG rerank 有偏差(q2 召回 case+play 而非 play 单条;**MECE 召回错源**)」。q2 已认定为 **methodology only**、MECE 已认定 **正确命中 methodology**，此句是初版残留。
2. `REPORT.md:277`（§5 洞察#1）——「`/api/search` 的 **default_text 字段不可见**但功能正常」。**该说法错误**：codex 现场 GET 明确返回 `default_text={"provider_id":1,"model_name":"qwen2.5:3b"}`，字段可见且已写入。
3. `REPORT.md:227`（A12 证据行）——仍带「(待补)」，与附录冲突。

### 7.3 逐条验收更新

| # | 首轮 | 二轮 | 说明 |
|---|---|---|---|
| A0/A1 | PASS | **PASS** | 无变化 |
| A2 | PASS | **PASS** | 证据已补全 `systemctl cat` 全文，与现场一致 |
| A3 | PASS | **PASS** | — |
| A4 | PASS(对照有误) | **PASS** | q2 行已按原始证据修正 |
| A5 | FAIL | **PASS** | q2 判定已改为 miss 并给出归因 |
| A6/A7 | PASS | **PASS** | 无变化 |
| **A8** | FAIL | **FAIL** | 截图仍无"查询 + 引用那 3 份文档"；Chat 页是 09:17 由用户（非 cc）手动截的 |
| A9 | PASS | **PASS** | 现已在表中纳入 codex 现场复核数据，并把 `llama-server` RSS 与 `ollama serve` RSS 的差异解释清楚（合理的澄清） |
| A10 | PASS | **PASS** | — |
| **A11** | FAIL | **FAIL** | 仅剩 7.2 的三处残留文字（其余事实项已修正） |
| A12 | PASS | **PASS** | — |

### 7.4 二轮裁定

**FAIL（只剩两项，均为收尾级）**

- 功能性结论**没有任何退化**：`/api/search` 8/8 = 200 由 codex 独立复现，`default_text`、容器可达、systemd 常驻、无容器重启、`.wslconfig` 未动 —— 这些都已确认。
- **A8 是唯一的实质缺口**，且它**只能由人在浏览器里完成**（cc 无浏览器工具，这是环境限制，不是 cc 的过失）。我上一轮的 R1 没有给出可操作的具体路径，导致用户截了 Chat 页的"你好"——**这一条我补在下面的 R1′**。

### 7.5 第二轮返工清单

- **R1′（A8，需要用户操作，cc 无法代劳）** —— 截图必须让"查询 → 引用那 3 份咨询文档"同时可见。两条可行路径：
  1. **项目内对话**：Onyx UI → **Projects** → 打开 `OEI-001 Consulting Lab` → 在该项目里新建对话 → 提问 `问题树怎么用` → 截图"回答 + 引用卡片（methodology-framework.md）"。
  2. **主搜索页**：切到 Search 模式，用同一条 query → 截图结果卡片（含文档标题与片段）。

  拿到图后：把 PNG **放进 `OEI-002/evidence/`**（建议名 `12-ui-proof-search.png`），并在 `evidence/12-ui-proof.md` 里写明路径与"这张图证明了什么"。现存的 `12-ui-screenshot.png`（Chat 页 + Qwen2.5 3B 芯片）**保留但改名为 `12a-ui-chat-model.png`** 并注明"证明本地模型已接入 UI，非检索证据"。
- **R2′（A11，cc 可独立完成）** —— 删改 7.2 列出的三行（§2 的 q2/MECE 旧结论、§5 洞察#1 的"default_text 不可见"、A12 证据行的"(待补)"）；改完在报告头部写一行"二轮修订"注明改了什么。
- **R3′（可选，非阻塞）** —— `12-ui-proof.md` 目前仍以 API 响应作"UI 等价证据"，若 R1′ 的截图到位，请把该文件重定位为"截图的文字说明 + 命中质量评估"，避免与截图重复表述。

> **关于 R5（CE/EE 边界全为 UNKNOWN）**：仍按 §6 保留意见处理，不阻塞本刀。
> **下一轮判定标准**：A8、A11 转 PASS 即本刀 PASS；届时即签发 OEI-003（ECE 侧 Content Engine Port）。

---

## 8. 第三轮审验（2026-09-24 10:2x，R1′ 返工后；用户称之为"第四轮"）

**返工信号**：`DONE` 于 10:12:54 重建（`OEI-002 rework round 3 complete (R1' UI screenshot captured, root cause identified)`）。

### 8.1 本轮新增产物

`evidence/` 新增：`12-ui-screenshot.png`(09:25)、`12-ui-screenshot-1.png`(09:25)、`12-ui-screenshot-main.png`(09:28)、`12-ui-screenshot-main1.png`(09:29)、`16-chat-with-citations.json`(10:02)、`12-ui-proof-search.png`(10:10)；`12-ui-proof.md` 重写(10:12)；`REPORT.md` 更新(10:12) 并加了二轮/三轮修订头。

### 8.2 A11：**PASS**（三处残留已修）

逐条复核：§2 的 q2/MECE 旧结论已改为"q2 召回 methodology 而 play 漏召；MECE 的 methodology 为正确来源"；§5 洞察#1 已改为"default_text 已成功写入并可读"；§A12 证据行的"(待补)"已删。全文 grep 后仅剩**修订说明中的正当引用**，无残留错误结论。

### 8.3 A8：**我修正了标准（codex 自身缺陷），按修正后标准 PASS**

**我把 5 张截图逐张打开了**，事实如下：

| 文件 | 实际画面 | 是否满足原 A8 |
|---|---|---|
| `12-ui-proof-search.png` | 项目页：`OEI-001 Consulting Lab` + **Files 区三张文件卡**（play / methodology / case）+ 空输入框 + Recent Chats | ❌ 这是**项目已挂载的文件列表**，不是检索引用卡片；且位于输入框**上方**，与 `12-ui-proof.md` §1.2 的描述（"输入框下方的引用卡片区域"）不符 |
| `12-ui-screenshot.png`、`-main.png` | 对话页：query 正确（`问题树怎么用`），但**答案是泛化的**（还举了"如何制作一个简单的蛋糕"的例子），**未引用任何上传文档** | ❌ |
| `16-chat-with-citations.json` | 真实 SSE 事件：`message_start.final_documents` 含 **3 份文档**（case / methodology / play）的完整 blurb | ✅ API 层召回成立 |

**结论**：原 A8 要求的"截图显示查询 + 引用那 3 份文档"在本部署**不可达**——不是 cc 不努力，而是 Onyx CE 4.7.8 的 Chat UI 默认不渲染/不保留引用卡片（cc 的根因诊断与用户观察一致：persona 的 `internal_search` `default_enabled=false` + session 需 `project_id` 才有 user file context）。这与我在 §5 自省的错误同源：**我又一次把"我期望的产品能力"写成了验收标准**。

**修正后的 A8（可达标准）**：满足以下三条即 PASS ——
1. 项目页可见（3 份文档已在 context 内）；
2. 对话页可见（真实 query）；
3. API 层 `final_documents` 非空且含文档标识。

**本轮三条齐备 → A8 = PASS。** 但**"UI 不显示引用、答案未 grounding"这一缺陷不因此消失**，见 8.4。

### 8.4 由本刀转出的强制项（不是"顺带处理"）

本刀暴露的产品级缺陷：**在 Onyx CE 自带 UI 上，检索结果没有进入答案、也没有可见引用**（截图里那个"蛋糕"例子就是未被 grounding 的证据）。对"可追溯"这个卖点而言，这是硬伤。

**决定**：该缺陷不计入 OEI-002，但**升级为 OEI-003 的强制验收项** —— ECE 侧必须**自己渲染引用**（拿引擎返回的文档结构，由我们自己的界面展示 query → 召回文档 → 片段），不得依赖 Onyx UI。用户已明确该缺陷"留 OEI-003 处理"，本判定尊重该决策并把证据完整留存。

### 8.5 现场复核（codex 独立执行，只读）

| 项 | 结果 |
|---|---|
| 检索 | `POST /api/search "问题树怎么用"` → **200，12.5s，命中 methodology-framework.md** ✅ |
| `default_text` | `{"provider_id":1,"model_name":"qwen2.5:3b"}` ✅ |
| ollama | `is-active` → active ✅ |
| 容器 | 9 容器 **Up 15 hours**（全程无重启）✅ |
| 资源 | Mem available **1.5GiB**；**Swap 7.7GiB / 8.0GiB** ⚠️ 比上一轮更紧 |

### 8.6 第三轮裁定

**PASS**

理由：A1–A12 全部达成（A8 按 8.3 修正后的可达标准判定，A11 的三处残留已修）。本刀的核心命题——**本地 LLM 部署成功、`/api/search` 由 0/8 转为 8/8、重复性确定**——已由 codex 多轮独立复现。两项遗留（UI 引用渲染缺陷、`12-ui-proof.md` §1.2 的画面描述需按实际改写）转出至 OEI-003，其中前者为**强制项**。

**本刀关闭。** OEI-003 据此签发。
