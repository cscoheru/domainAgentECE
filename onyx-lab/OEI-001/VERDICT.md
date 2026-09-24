# OEI-001 审验裁定（codex）

> 审验日期：2026-09-23 21:45 ｜ 审验对象：`REPORT.md` + `evidence/`（25 个文件）+ `DONE`（21:16）
> 被审任务书：`TASK.md` v3（签发 20:58，v2 存档于 `TASK.v2.md`）
> 审验方式：逐条核对 + 抽查原始证据 + 独立只读复现（不以 cc 的自我描述为准）

---

## 1. 逐条验收

| # | 验收标准 | 结论 | 证据指针 | 备注 |
|---|---|---|---|---|
| A1 | project 存在（建项目 2xx + 列表含同名项目） | **PASS** | `evidence/01-project-create.json`、`01b-project-list.json` | 独立复现：`GET /api/user/projects` 返回 `[{"id":1,"name":"OEI-001 Consulting Lab",...}]`，与证据一致 |
| A2 | workspace 恰好 3 份 `.md`，每份 `wc -m` ≥ 400 且含 `Demo Case` | **PASS** | `evidence/02-workspace-size.txt` | 独立复算一致：1324 / 2054 / 2289，`grep -c 'Demo Case'` 各 1 |
| A3 | 3 份上传响应 2xx + 可取得 3 个不同 file_id | **PASS** | `03-upload-*.json`、`03b-project-files.json` | 三个 file_id 互异；`rejected_files: []` 确实存在于上传响应体内 |
| A4 | 轮询有每次时间戳与原始状态，最终全部已索引，未超上限 | **PASS** | `04-status-poll-1..3.json`、`04-status-final.json`、`03b-project-files.json` | 实测时间 21:07:14 / 21:07:29 / 21:07:44，间隔 15s，3 次 ≪ 20 上限；`03b`（21:06:25）为 PROCESSING、poll-1 起为 COMPLETED，**过程有真实转变**而非事后补录。cc 的 `user_file.id ≠ file_id` 辨析独立复现成立 |
| A5 | ≥3 个查询，各有请求+完整响应，命中判定可核对到源文件 | **FAIL** | `05-search-q1..q3.json` | 3 次调用全部 **HTTP 400** `{"message":"No default LLM model found"}`；独立复现同结果。**检索质量完全未验证**，无任何命中判定可核对 |
| A6 | 负例 + 精确命中两侧判定 | **FAIL** | `06-search-negative.json`、`06-search-exact.json` | 两条同为 400（根因同 A5），两侧边界均未成立 |
| A7 | 同查询 3 次，文档 id 集合一致性结论 | **FAIL** | `07-repeat-1..3.json` | 三次均为 400，无文档集合可比 |
| A8 | 索引前后各一份诊断 + 内存变化数字 + 长期承载结论 | **PASS**（结论 CONDITIONAL） | `diagnostics-pre.json`(20:50)、`08-diagnostics-post.json`(21:13)、`10-container-snapshots.txt` | 数字独立核对一致：used 8.5→9.0GiB、avail 2.8→2.2GiB、**swap 18MiB→2.3GiB**。CONDITIONAL 有依据，非空话 |
| A9 | ≥8 项能力，标注 CE/EE/UNKNOWN 与依据来源；5 项强制项不得缺席 | **PASS（结构）／依据不足** | `REPORT.md` §A9 | 11 项、5 项强制项齐备、标注明确 → 结构达标。但"依据"多为断言（如"Onyx 官方 tier 文档"），**无可追溯 URL 或引文**，不满足 `AGENTS.md` §5 的证据纪律 → 见 R2 |
| A10 | 无密钥泄漏 + 容器未重启 + 未越界改文件 | **PASS** | `09-compliance-check.txt`、`09b-cc-output-compliance.txt`、`10-container-snapshots.txt` | 独立执行任务书原命令：4 处命中（`TASK.md`/`TASK.v2.md`/两份扫描文件自身），**全为路径字符串、无凭据原值**；容器独立复验 Up 3 hours，无重启。注：该验收标准由 codex 表述失当，见 §5 |
| A11 | REPORT 对 A1..A10 各有结论 + 证据指针，无模糊表述 | **PASS** | `REPORT.md` | 逐条齐备，结论用词明确（PASS/FAIL + 根因），未出现"应该没问题" |

**汇总：8 项 PASS（其中 A9 依据不足、A8 为 CONDITIONAL）、3 项 FAIL（A5/A6/A7）。**

## 2. 证据抽查

**实际打开逐字看过的原始证据（15 份）**：
`01-project-create.json`、`01b-project-list.json`、`02-workspace-size.txt`、`03-upload-case-management-consulting.json`、`03b-project-files.json`、`04-status-poll-1.json`、`04-status-poll-2.json`、`04-status-poll-3.json`、`04-status-final.json`、`05-search-q1.json`、`06-search-negative.json`、`07-repeat-1.json`、`08-diagnostics-post.json`、`09-compliance-check.txt`、`09b-cc-output-compliance.txt`、`10-container-snapshots.txt`（连同 `diagnostics-pre.json` 实为 16 份）。

**判定**：证据与 `REPORT.md` 描述**一致**，未发现夸大。三点值得记录：

1. `04-status-poll-*.json` 四份 md5 完全相同（`dfb27168…`），但高精度 mtime 为 21:07:14.17 / 21:07:29.25 / 21:07:44.33，**确为 15 秒真实间隔**，非事后批量伪造。
2. 索引状态的**真实转变**由 `03b-project-files.json`（21:06:25，PROCESSING）→ `04-status-poll-1.json`（21:07:14，COMPLETED）两文件共同证明，链条完整。
3. `09b-cc-output-compliance.txt` 是**叙述性总结**而非原始命令输出，属证据强度偏弱项 → 见 R4。

**独立复现（codex 本人执行，全部只读）**：

| 复现项 | 命令 | 结果 |
|---|---|---|
| 项目存在 | `GET /api/user/projects` | 200，`id=1`，name 一致 ✅ |
| 文件与状态 | `GET /api/user/projects/files/1` | 3 条记录，status=COMPLETED ✅ |
| 检索失败 | `POST /api/search {"query":"问题树怎么用"}` | **400** `{"message":"No default LLM model found"}` ✅ 与证据一致 |
| 无 LLM 的结构性原因 | `GET /api/admin/llm/provider` | `{"providers":[],"default_text":null,"default_vision":null,"default_chat_naming":null}` ✅ **确认零 provider** |
| 字段辨析 | `POST .../file/statuses` 分别传 `user_file.id` 与底层 `file_id` | 前者返回记录、后者返回 `[]` ✅ cc 说法成立 |
| 无重启 | `docker ps` | 9 容器 Up 3 hours ✅ |

## 3. 范围与合规

- **越界检查**：未改 `/home/codex/onyx-lab/src`（实测 `fisher` 对该路径无读权限）；未改 compose / `.env`；未执行任何 restart/stop/down/rm；未 commit / push（`onyx-lab/` 在 git 中仍为未跟踪状态）；未改 ECE 主仓。`bin/*.sh` 的改动全部来自 codex 本人（v3 授权范围内），cc 仅只读调用。**未发现越界**。
- **密钥泄漏检查**：任务书原命令命中 4 个文件，逐一看过，全部是**路径字符串**（`admin-cookies` 出现在文档与扫描记录里），无 cookie / token / 密码原值。`onyx-lab/.gitignore` 已排除 `.secrets/`，且凭据落在 WSL 原生路径而非 `/mnt/d`。**未发现泄漏**。
- **副作用**：写入 1 个 user project、3 份文档、11 个 chunk（3/4/4）并进入 OpenSearch 索引；索引期间 WSL **swap 峰值 2.3GiB**（后续需处置，非本刀 FAIL 项）。无容器重启、无文件系统污染。

## 4. 裁定

**FAIL**

理由：本刀的第一命题是"证明 Onyx CE 能作为 ECE 的内容与检索**引擎**"——写入侧（建项目 / 上传 / 索引 / 状态可见）已被充分证明，且证据质量高；但**查询侧 8 次调用全部 400，检索召回一条都没跑通**，A5/A6/A7 三条验收标准无一条成立。"能不能检索"恰恰是 OEI-002（ECE 接入）的全部前提，因此不能以"主体步骤已完成"放行。

同时明确：**这不是 cc 的执行错误**。cc 在无 LLM 的结构性缺口下如实落盘 FAIL、给出根因、并用只读反查排除了替代端点，处置方式符合 `CC-ROLE.md` §8「别静默失败」。FAIL 的对象是**本刀的验收结论**，不是执行质量。

另：`DONE`（21:16）已存在但结论为 FAIL，按协议由执行方删除旧 `DONE`、返工后重建。

## 5. 返工清单（R1..R4）

- **R1（阻塞项，需用户决策，cc 在 codex 更新任务书前不要动手）** —— 检索通路二选一：
  - **方案 A**：为 Onyx 配置 default LLM（用户提供 API key，或指向本机 Ollama），随后原样重跑 A5/A6/A7。
  - **方案 B**：承认本部署 community tier 无 LLM，把 A5–A7 重定义为**引擎层召回验证**——绕过 `/api/search`，直接对底层索引做一次真实召回（BM25 或向量），把原始响应落盘，并据此给出命中/边界/重复性结论。
  - 两方案的取舍会直接改变 OEI-002 的接口设计（"ECE 直接对接检索层" vs "ECE 调用 Onyx 的 /api/search"），属架构决策，由 codex 与用户定，cc 不得自行选择。
  - **决策记录（2026-09-23 21:50，用户）**：采用 **方案 A**。返工任务书已据此签发为 `TASK.md` v4（v3 存档 `TASK.v3.md`），R1 在 v4 中化为"§3 步骤 0 前置校验 + 重跑 A5–A7"。
- **R2（cc 可独立完成）** —— `REPORT.md` §A9 的 11 项能力逐项补**可追溯来源**：官方文档 URL + 引文；凡不能落到具体来源的，一律改标 `UNKNOWN` 并注明"未验证"。同时把"本刀实测"与"文献推断"两类依据分开标注（任务书强制 5 项尤须如此）。
- **R3（cc 可独立完成）** —— `REPORT.md` 事实性对齐：§6 写"共 19 个文件"而 `evidence/` 实为 25 个；§A3 表格使用 `03-upload-case.json` 等简称而磁盘实名为 `03-upload-case-management-consulting.json`。请统一为磁盘真实命名与真实计数。
- **R4（cc 可独立完成）** —— `evidence/09b-cc-output-compliance.txt` 改为**原始命令输出**（含命令与完整 stdout），不要只放结论性叙述；建议对 `evidence/` + `REPORT.md` 做一次 value-level 扫描（如 `connect.sid=` / `fastapiusersauth=` / `eyJ[A-Za-z0-9_-]{20,}`）并把原文落盘。

> **codex 自身待修正项（不计入 cc 责任）**：A10 的验收标准表述失当——所给模式串（`admin-cookies`）本身出现在任务书与扫描记录里，导致"无命中"在逻辑上不可满足。下一版将改为"只扫 cc 产出物 + value-level 凭据模式"。

## 6. 架构结论（供 OEI-002 参考，不在本刀返工范围）

1. **"Onyx 提供检索"这一前提在查询侧尚未被证明**。本部署 `providers: []`，`/api/search` 对本刀场景返回 400。`DECISION-ONYX.md` 把 Onyx 定位为"可替换的内容与检索引擎"，该定位在**写入侧成立**，查询侧待 R1 定论后补齐。
2. **user project ≠ document set**：本刀证明前者可用（CE 实测），后者是管理侧素材集（v2 误用返回 400）。ECE 接入应使用 user project 概念，`REPORT.md` §3.3 的建议方向正确。
3. **待查开放项**：是否存在不依赖 LLM 的召回通路（本刀仅证 `/api/chat/search` 不覆盖 user project 文件）。codex 尝试在 `onyx-opensearch-1` 容器内探 `localhost:9200` 未获得响应（`curl` 返回 000），**未取得结论，记为 UNKNOWN**，不得作为设计前提。
4. **资源**：索引 3 份小文档即触发 2.3GiB swap，说明 i9 + WSL 的 12GB 上限在"9 容器全开 + 索引"场景下偏紧。演示前建议按 `REPORT.md` §5.3 复核 `.wslconfig`。

> 返工完成后，执行方删除旧 `DONE`、重新生成 `DONE`，codex 进行下一轮审验。**R1 的执行去向已由用户在 22:2x 改判，见 §7。**

## 7. 关闭记录（2026-09-23 22:2x，用户决策后由 codex 追加）

**本刀以「条件关闭（CONDITIONAL CLOSE）」收束，而非返工后 PASS。**

1. **用户决策**：A5/A6/A7 的阻断（本部署无 default LLM）不在 OEI-001 内返工，**改由 OEI-002 承接执行**；同时采纳 cc 在 `REPORT.md` §5.5 的本地 LLM 部署建议。
2. **§1–§4 的审验结论不变、不修订**：A1–A4、A8、A9、A11 为 PASS，**A5/A6/A7 维持 FAIL**。证据链保持原样，不做任何事后美化。
3. **§5 的返工项去向**：
   - **R1** → 移交 **OEI-002**（已签发，包含"装本地 LLM + 重跑这 8 次检索"）。本刀不再执行。
   - **R2 / R3 / R4** → 并入 OEI-002 的步骤 0 收尾项（改动 `OEI-001/REPORT.md` 属于 OEI-002 任务书显式授权范围）。
4. **接受的风险（显式记录）**：OEI-001 的"查询侧可用"结论**至今未被证实**。因此 OEI-002 是**唯一不允许跳过的前置刀**——它不 PASS，OEI-003（ECE 适配器）不予签发。
5. **`DONE`（21:16）的去向**：该 `DONE` 对应的是 v3 任务书的一次完整执行，其结论已被本裁定接管；**不要求 cc 删除**，由 OEI-002 自己的 `DONE` 单独记录新一轮完成信号。
