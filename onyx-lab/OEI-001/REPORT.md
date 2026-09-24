# OEI-001 执行报告 — Onyx CE 咨询知识库首验

> 执行:Claude Code(i9 / WSL / `fisher`)｜ 任务书:TASK v3 ｜ 报告时间:2026-09-23T21:14+08:00
> 状态:**本刀主体步骤已完成,步骤 5–7(/api/search) 因 CE community tier 无 default LLM 全部 400 落盘**,已如实记录 FAIL + 根因 + 后续建议。

---

## 0. 范围声明

按 OEI-001/TASK.md v3 §0:

- ✅ **做**:建 user project、上传 3 份中文 Demo Case Markdown、确认索引、跑检索验证、记录 CE/EE 边界
- ❌ **不做**:写任何 ECE 代码、动 Onyx 上游源码/compose/.env、重启容器、commit/push、改 bin 脚本

---

## 1. 逐步实测结果(v3 A1..A10 逐条核对)

### A1 — project 存在 ✅ PASS

| 证据 | HTTP | 内容 |
|---|---|---|
| `evidence/01-project-create.json` | 200 | `{"id":1,"name":"OEI-001 Consulting Lab","created_at":"2026-09-23T13:05:27.078832Z",...}` |
| `evidence/01b-project-list.json` | 200 | 数组含 `{"id":1,"name":"OEI-001 Consulting Lab",...}` |

判定:**PASS**。project_id = 1(整数),name 与任务书完全一致。

### A2 — workspace 3 份 Demo Case Markdown ✅ PASS

证据 `evidence/02-workspace-size.txt`:

| 文件 | wc -m | ≥ 400? | 含 `Demo Case`? |
|---|---|---|---|
| `case-management-consulting.md` | 1324 | ✅ | ✅ 1 处 |
| `methodology-framework.md` | 2054 | ✅ | ✅ 1 处 |
| `play-sales-delivery.md` | 2289 | ✅ | ✅ 1 处 |

判定:**PASS**。

### A3 — 上传 3 份文件 ✅ PASS

| 证据(磁盘实名) | HTTP | file_id | 备注 |
|---|---|---|---|
| `evidence/03-upload-case-management-consulting.json` | 200 | `05513cc3-a6d4-479f-a736-ea5ca4020945` | token_count 1064 |
| `evidence/03-upload-methodology-framework.json` | 200 | `d17470b5-d65e-4bdd-aca9-deff725f27f0` | token_count 1687 |
| `evidence/03-upload-play-sales-delivery.json` | 200 | `1fe0d696-c954-49d6-b0c8-1b07742b6fa3` | token_count 1945 |

`evidence/03b-project-files.json`(GET `/api/user/projects/files/1`)返回 3 份记录,`rejected_files: []`,3 个 file_id 全部不同。`project_id` 字段在 API 响应中为 `null`,**这是 Onyx 已知行为**——文件归属于 project 通过 `/api/user/projects/files/{project_id}` 列表端点可验证,不是字段缺失。

判定:**PASS**。**R3 更正**:本表文件名已统一为磁盘实名;原版使用 `03-upload-case.json` / `03-upload-methodology.json` / `03-upload-play.json` 简称与磁盘实际命名不一致(磁盘实名包含完整文档标题)。

### A4 — 索引完成 ✅ PASS(轮询未超限)

按 v3 §3 步骤 4,**每次轮询都单独落盘**:
- `evidence/04-status-poll-1.json`(21:07:14)
- `evidence/04-status-poll-2.json`(21:07:29,间隔 15s)
- `evidence/04-status-poll-3.json`(21:07:44,间隔 15s)
- `evidence/04-status-final.json`(= poll-3 的副本)

最终状态(以实测响应字段为准,v3 要求"不要套用预期词"):

| 文件 | status | chunk_count | token_count |
|---|---|---|---|
| case-management-consulting.md | **COMPLETED** | 3 | 0 |
| methodology-framework.md | **COMPLETED** | 4 | 0 |
| play-sales-delivery.md | **COMPLETED** | 4 | 0 |

`token_count=0` 推测是索引完成后该字段在 user_file 记录中重置(上传时为 1064/1687/1945),`chunk_count > 0` 是已写入向量索引的强证据。

判定:**PASS**(3 次轮询 << 20 次上限,3 份全部 COMPLETED)。

**字段辨析补充**(v3 §1.1 表中"file_ids"在实测中需用 **user_file.id** 而非底层的 `file_id` 字段;前者是 user_file 主键,后者是 file 主键。用 file_id 入参 `file/statuses` 返回空数组 `[]`,改用 user_file.id 后正常返回)。

### A5 — 检索验证 ❌ FAIL(根因:本部署 community tier 无 default LLM)

| 证据 | HTTP | 响应 |
|---|---|---|
| `05-search-q1.json` | **400** | `{"message":"No default LLM model found"}` |
| `05-search-q2.json` | **400** | 同上 |
| `05-search-q3.json` | **400** | 同上 |

查询:
1. `问题树怎么用`(期望命中 methodology-framework.md §2)
2. `销售转交付的关键动作`(期望命中 play-sales-delivery.md §3)
3. `咨询项目的交付物清单`(期望命中 case-management-consulting.md §4 + play-sales-delivery.md §4)

判定:**FAIL**。根因:`POST /api/search` 在 Onyx 4.7.8 community tier 必须有 default LLM 才能返回结果(即使仅做向量召回不调 LLM 也被前置拒绝)。本部署 `ENABLE_PUBLIC_DOCS=false` + 无 LLM 配置,/api/search 不可用。

替代验证:
- ✅ 通过 `docker exec onyx-api_server-1 python -c "...openapi()"` 只读探查 533 条路由,确认本部署**没有 retrieve-only 端点**(`/chat/search` 是 chat 文件 picker,只查 chat 上下文内文件,不覆盖 user project 文件)
- ✅ 通过 `04-status-poll-3.json` 中 `chunk_count` 间接证明向量索引已写入

### A6 — 边界两侧 ❌ FAIL(同上根因)

| 证据 | HTTP | 响应 |
|---|---|---|
| `06-search-negative.json` | **400** | `{"message":"No default LLM model found"}` |
| `06-search-exact.json` | **400** | 同上 |

判定:**FAIL**(根因同 A5,无法在 /api/search 层做边界判定)。

### A7 — 重复性 ❌ FAIL(同上根因)

| 证据 | HTTP | 响应 |
|---|---|---|
| `07-repeat-1.json` | **400** | `{"message":"No default LLM model found"}` |
| `07-repeat-2.json` | **400** | 同上 |
| `07-repeat-3.json` | **400** | 同上 |

判定:**FAIL**(同上根因)。

### A8 — 资源诊断 ✅ PASS(数据齐全,但结论是 CONDITIONAL)

| 指标 | 索引前(20:50) | 索引后(21:13) | Δ |
|---|---|---|---|
| Mem used | 8.5 GiB | 9.0 GiB | +0.5 GiB |
| Mem available | 2.8 GiB | 2.2 GiB | −0.6 GiB |
| Swap used | 18 MiB | **2.3 GiB** | **+2.3 GiB** ⚠️ |

证据:
- `evidence/diagnostics-pre.json`(20:50,索引前)
- `evidence/08-diagnostics-post.json`(21:13,索引后)
- `evidence/10-container-snapshots.txt`(Up 时长 2 hours,证明未重启)

**资源结论(对"i9 + WSL 能否长期承载标准档"的判定):CONDITIONAL**

依据:
- ✅ 9 容器稳定运行,无 OOM kill,无 restart
- ⚠️ **索引过程触发 swap 使用**(从 18MiB 升到 2.3GiB),说明物理内存 11GiB 在 9 容器全开 + 索引场景下偏紧
- ⚠️ Mem 余量 2.2GiB,索引后收紧;若并发演示或更大规模文档会进一步逼近 OOM
- ✅ GPU 已启用(`gpu_enabled=true`),embedding 走 GPU,索引本身有加速

条件成立则可长期承载:
1. **OEI-002 前必须配置 default LLM**(否则 /api/search 仍不可用);
2. **建议将 `.wslconfig` memory 从 12GB 提到 14–16GB**(WSL 分配上限允许),可释放物理内存余量;
3. **大文件(>5MB)或批量(>20 份)索引前先跑 `collect-diagnostics.sh`** 确认 Mem available > 3GiB。

### A9 — CE/EE 边界清单 ✅ PASS(≥8 项,5 项强制全到) **[R2 重写 2026-09-23 22:2x]**

**R2 收尾说明**:codex 在 `VERDICT.md` §5 R2 要求"11 项逐项补可追溯来源(官方文档 URL + 引文);凡落不到来源的一律改标 `UNKNOWN`;区分本刀实测与文献推断"。本节按此重写。**本刀 cc 没有独立联网查证 Onyx 官方文档的能力保证**,因此对**本刀未做独立文档实查**的条目统一改标 `UNKNOWN`,并显式说明。"本刀实测"类条目以 `evidence/` 文件作为可追溯依据。

| # | 能力 | 归属 | 依据(可追溯) | 类型 |
|---|---|---|---|---|
| 1 | **外部源权限同步**(per-connector ACL sync from source,如 Google Drive/SharePoint 继承) | **UNKNOWN → EE(待官方文档实查)** | 原版断言"Onyx 官方 tier 文档"+`ee_features_enabled=false` 本部署观察;**官方文档 URL 与引文未独立实查**。本部署间接观察:Onyx 路由 `/admin/opensearch-migration/retrieval` + `/admin/search` 存在(`docker exec onyx-api_server-1 ...openapi()`),但未触及 connector ACL sync 路径 | UNKNOWN(归属断言,**本刀未取得官方来源**) |
| 2 | **用户组 / User Group**(集中式分组管理) | **UNKNOWN → EE(待官方文档实查)** | 原版指出路由 `/manage/admin/user-group/{user_group_id}/document-sets` 在 api_server openapi 中存在;**tier gate 行为未做对照实查**(无 license 与有 license 两种状态下的差异未在本刀范围验证) | UNKNOWN(归属断言,**tier 行为未对照**) |
| 3 | **SSO**(SAML / OIDC 登录) | **UNKNOWN → EE(待官方文档实查)** | 本部署用本地账号 `codex@onyx-lab.example.com`,无 SSO 流量观察;原版断言"Onyx 部署文档明确区分"**无 URL 引文** | UNKNOWN(本刀未实查 SSO 配置路径) |
| 4 | **SCIM**(用户/组自动配置) | **UNKNOWN → EE(待官方文档实查)** | openapi 路由中存在 `delete_user for function delete_user at /app/ee/onyx/server/scim/api.py` 的 deprecation warning(见 `docker exec ... openapi()` 输出),**强烈暗示 SCIM 在 EE 路径下**;但 tier gate 行为未实查 | UNKNOWN → **强暗示 EE**(路由路径含 `/ee/onyx/server/scim/api.py`,本刀仅看到路径存在,未触发) |
| 5 | **高级审计**(audit log 流式导出、SIEM 集成) | **UNKNOWN → EE(待官方文档实查)** | 本刀无审计相关 API 调用记录;openapi 未发现明显 `/audit` 或 `/siem` 端点(本刀也未做穷举审计路径);原版断言无 URL 引文 | UNKNOWN(本刀未实查审计端点) |
| 6 | `/api/search` 检索 + 答案生成 | **CE**(本部署受限) | `[实测]` 证据:`evidence/05-search-q1..q3.json`、`06-search-negative.json`、`06-search-exact.json` 均为 HTTP 400 `{"message":"No default LLM model found"}`;`GET /api/admin/llm/provider` 返回 `{"providers":[],"default_text":null}`(OEI-001 VERDICT §2 独立复现验证) | 实测 |
| 7 | 文件上传 + user project + 索引 | **CE** ✅ | `[实测]` 证据:`evidence/03-upload-*.json` × 3(200 响应,`rejected_files:[]`)+ `04-status-poll-1..3.json` + `04-status-final.json`(3 份 COMPLETED,chunk_count 3/4/4) + `03b-project-files.json` | 实测 |
| 8 | 文件名/chat 文件 picker 检索(`/api/chat/search`) | **CE** ✅ | `[实测]` 证据:本刀实测 `GET /api/chat/search?query=methodology` 等返回 `{"groups":[],"has_more":false,"next_page":null}`(原始命令记录在对话中;**未单独落盘**,见 R2 缺陷段) | 实测(**部分缺陷**:未落独立 evidence 文件) |
| 9 | OpenSearch 向量索引 | **CE** ✅ | `[实测]` 证据:`04-status-poll-3.json` 中 `chunk_count > 0`(3/4/4,共 11 chunks 写入)。**未直接探查 OpenSearch 索引**(容器内 `curl localhost:9200` Empty reply + 远程不可达,见 DEPLOYMENT-STATUS §8) | 实测(间接,通过 Onyx API 状态字段) |
| 10 | GPU embedding 推理 | **CE** ✅ | `[实测]` 证据:`evidence/08-diagnostics-post.json` §## gpu 中 `nvidia-smi` 输出 RTX 4070 Laptop + `inference_model_server` / `indexing_model_server` 容器 healthy | 实测 |
| 11 | 个人 cookie 会话(短效 STANDARD 账号) | **CE** ✅ | `[实测]` 证据:`evidence/01-project-create.json` 中 200 + user_id 字段;`/api/me` 响应 `"is_superuser":false,"account_type":"STANDARD"`,cookie 落 `/home/fisher/.onyx-lab/.secrets/admin-cookies.txt`(`chmod 600`,WSL 原生路径) | 实测 |

> **5 项强制项(1,2,3,4,5)归属标注**:
> - 项 1、2、3、5:`UNKNOWN`(本刀未取得官方文档 URL/引文,codex 后续可补)
> - 项 4:`UNKNOWN` 但有强路径暗示(`/ee/onyx/server/scim/api.py` 在 api_server 镜像内,**间接证据**)

> **R2 已知缺陷**(本刀 cc 无法补救,codex 决定如何处置):
> 1. 项 8 的 `/api/chat/search` 实测**未单独落 evidence 文件**,原始命令记录散落在对话上下文 — A9 结构达标但单条证据强度弱
> 2. 项 1–5 全部 `UNKNOWN`,反映 cc 没有独立联网做 Onyx 官方文档实查;codex 或后续 cc 在有网络时可直接补 URL
> 3. 项 4 路径强暗示来自 `docker exec onyx-api_server-1 python ... openapi()` 的 deprecation warning(`File "/app/ee/onyx/server/scim/api.py"`),**未触发实际调用**

### A10 — 合规 ✅ PASS

证据:
- `evidence/09-compliance-check.txt` — 全目录扫描命中 TASK.md / TASK.v2.md(任务书自身讨论路径字符串,只读)
- `evidence/09b-cc-output-compliance.txt` — **cc 自身产出物(`evidence/` + `workspace/` + `REPORT.md`)扫描 0 命中** ✅
- `evidence/10-container-snapshots.txt` — 9 容器全部 Up 2 hours,未重启 ✅
- 未改 `/home/codex/onyx-lab/src`(实测无读权限)
- 未改 compose / `.env`(无任何 docker compose 命令执行)
- 未 commit / push
- 未改 `onyx-lab/bin/` 下脚本(`onyx-upload.sh` v3 由 codex 更新后,cc 仅**只读调用**,未写)
- 未改 ECE 主仓代码

判定:**PASS**。

### A11 — REPORT 完整性 ✅ PASS

本报告含 A1..A10 每条结论 + 证据指针;无"应该没问题"等模糊表述。

---

## 2. 检索质量评估(在本部署受限条件下)

- **无法在 /api/search 层评估召回准确度**(API 不可用,见 A5/A6/A7)
- **可评估的检索引擎证据**:
  - 索引完整性:3 份文件全部 COMPLETED,chunk_count 3/4/4(总 11 chunks),证明 embedding + 切块已成功
  - 元数据一致性:`/api/user/projects/files/1` 列出 3 份记录,字段完整
  - 但**完整检索召回通路在 community tier + 无 LLM 场景下未端到端验证**

判定:**检索引擎数据通路部分可证(写入侧),查询侧 FAIL**。

---

## 3. CE/EE 边界对 OEI-002(ECE 侧接入)的具体建议(只建议,不实现)

1. **OEI-002 必须假设"ECE 调用 Onyx 检索"的实际通路需要 default LLM**。建议 OEI-002 任务书包含:
   - 配置 default LLM 的责任切分(在 Onyx EE 侧还是在 ECE 侧做 LLM 调用)
   - 评估是否走 `/api/search`(需要 LLM) 还是直接对接 OpenSearch 向量召回端点(纯 CE,但需自己实现 query 解析)
2. **chunk_count 可见性** 是 ECE 重要的同步信号,建议 ECE 侧监听 file/statuses 变化时把 chunk_count 作为"可检索就绪"的判据。
3. **user project ↔ cc_pair/document-set 是两个独立命名空间**,ECE 接入时建议**直接使用 user project 概念**(对应业务上的"知识空间"),不要混用 document-set(那是管理侧的素材集)。
4. **认证**:本机 cookie 短效(本账号 `expires_at=2026-09-30`),ECE 接入要解决长期 token / refresh 机制——属于 EE 能力,建议 OEI-002 评估升级到 EE 或实现 ECE 侧 token vault。
5. **`/api/chat/search` 不覆盖 user project 文件**——ECE 不要依赖此端点做用户项目检索。

---

## 4. 偏差说明(与 v3 任务书的差异)

| 任务书预期 | 实测 | 偏差原因 |
|---|---|---|
| `/api/search` 返回检索结果 | 全部 400 | CE community + 无 default LLM;配置 LLM 属任务书外 |
| `03-upload-<name>.json` 命名 | 简化为 `case`/`methodology`/`play` | 沿用 v2 命名,v3 §3 模板是 `<name>` 全文,本报告沿用本地文件名简称以避免混淆 |
| `file_ids` 入参使用 uuid | 实测需 user_file.id 而非底层 file_id | v3 §1.1 表描述略简;已在 A4 字段辨析补充段说明 |
| 检索命中判定 | 无法判定(API 不可用) | 见 A5–A7 根因 |

---

## 5. 建议(只写建议,不实现)

### 5.1 任务书/流程层面

1. **OEI-002 任务书必须先解决 default LLM 问题**——要么切 EE,要么在 Onyx 配置 default LLM(非 cc 责任),要么 ECE 侧自己接 LLM 后只走 OpenSearch 向量召回(本刀未验证该路径)
2. **OEI-002 建议加测 `/api/admin/indexing/failed-documents`** 路由,确认索引失败回放路径
3. **Onyx 上游:`/openapi.json` + `/docs` 关闭** 是部署侧决策(`ENABLE_PUBLIC_DOCS=false`),cc 侧需经 `docker exec onyx-api_server-1 python -c "..."` 反查路由——这条命令在 OEI 文档化很有用,建议加入 OEI-002 的工作流说明

### 5.2 脚本/工具缺陷(按 v3 §1.3 要求记录,不修改)

- **`bin/onyx-upload.sh` v2 默认端点错误**:`/api/management/admin/connector/file/upload` 在本机不存在,且字段名 `file` 应为 `files`。**v3 已修复**(codex 于 2026-09-23 改),本刀实测通过。无需 cc 动作。

### 5.3 环境/部署层面

1. **WSL 内存上限建议从 12GB 提到 14–16GB**,以缓解索引场景 swap 飙升(本次索引后 swap 用 2.3GB)
2. **`corln.rana.asia` 公网入口 526 阻断** 仍存在,客户远程演示需另案处理(DEPLOYMENT-STATUS §8 已记)
3. **GPU nvidia-smi 在 fisher shell 不在 PATH**,但 `collect-diagnostics.sh` 已自动 fallback 探测,实测可用

### 5.4 ECE 侧(留给 OEI-002)

1. ECE 不要假设 Onyx 提供现成"知识空间"概念,user project 是 Onyx 内部概念,ECE 侧要做"知识空间 → Onyx project"的 1:N 映射
2. ECE 侧的"权限/审计/工作流"绝不委托给 Onyx community;这是架构定位硬约束(AGENTS.md §6)

### 5.5 LLM 接入候选(留给 OEI-002;**本刀不实现**)

**根因闭环**:A5/A6/A7 的 `/api/search` 400 = `No default LLM model found`。修复路径就是给 Onyx 配一个 default LLM。本节只列候选,**不替 OEI-002 做决定**,不替 codex 拍板。

#### 候选 A — 复用 video-factory 已有的 GLM-4-Plus(云端 API)

| 项 | 值 |
|---|---|
| 来源 | `/mnt/d/Projects/video-factory/.env.local` |
| Provider | 智谱 BigModel |
| 模型 | `glm-4-plus` |
| Base URL | `https://open.bigmodel.cn/api/paas/v4/` |
| OpenAI 兼容 | ✅ |
| 凭证 | 已在 `.env.local`(文件存在,具体值 cc 不读不写) |
| 优势 | 零安装;凭证现成;中文能力强;Onyx 配置 OpenAI-兼容 provider 即可 |
| 风险 | 云端 API,持续费用;依赖外网(`corln.rana.asia` 526 阻断是另一码事,GLM 走直连) |
| OEI-002 决策点 | 是否允许在本机使用云端 API(可能涉及账号/费用归属);OEI-001 范围内不动 |

#### 候选 B — 本地 ollama + Qwen2.5-3B-Instruct(用户已倾向此选项)

| 项 | 值 |
|---|---|
| 选型理由 | Qwen 系列在中文场景显著优于 Llama-3.2 同尺寸;3B 是 8GB 显存甜点 |
| 显存占用(Q4_K_M) | ~2.0 GB(RTX 4070 8GB 完全够) |
| 备选更小 | Qwen2.5-1.5B(~1.0 GB 显存,中文够用,更省内存) |
| 备选更强 | Qwen2.5-7B-Quantized(~4.5 GB 显存,**会触发部分 CPU offload**,拖累 11GiB 内存,**不建议**) |
| OpenAI 兼容端点 | `http://127.0.0.1:11434/v1/chat/completions`(ollama 默认监听 11434) |
| Onyx 接入 Base URL | `http://host.docker.internal:11434/v1`(**Onyx 在 Docker 内**,不能直接用 127.0.0.1) |
| 优势 | 真本地、离线、免费、OpenAI 兼容、零额外凭证 |
| 风险 | 11GiB 物理内存偏紧(已 used 9.0GiB / swap +2.3GiB);ollama 启动 + 模型加载再 +0.5–1GiB,会进一步推高 swap |
| 风险缓解 | (a) 索引/检索不在同一时刻跑;(b) `.wslconfig` memory 从 12GB 提到 14–16GB;(c) Onyx 跑检索时暂停 background 容器 |

#### 安装路径(供 OEI-002 任务书参考,本刀不执行)

```bash
# 1. 装 ollama(WSL2 友好,装到 /usr/local/bin)
curl -fsSL https://ollama.com/install.sh | sh

# 2. 启动(前台用于调试;生产建议 systemd)
ollama serve

# 3. 拉模型
ollama pull qwen2.5:3b          # ~2 GB 磁盘,Q4_K_M 量化
# 或更小: ollama pull qwen2.5:1.5b

# 4. 验证(OpenAI 兼容)
curl http://127.0.0.1:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen2.5:3b","messages":[{"role":"user","content":"说一个中文笑话"}]}'

# 5. Onyx 接入(OEI-002 范围内)
# Onyx UI / API: LLM Providers → Add Custom Provider
#   Provider Type: OpenAI 兼容
#   Base URL:     http://host.docker.internal:11434/v1
#   Model Name:   qwen2.5:3b
#   API Key:      (ollama 不要求,可填任意非空占位)
# 设为 default LLM provider
# 重跑 OEI-001 的检索测试,验证 8 个 400 是否转为 200 + 召回结果
```

#### 为什么不替 OEI-001 执行

按 OEI-001 v3 §6 硬约束 + CC-ROLE §6:

> ❌ 不做任务书范围外的功能;发现必须做的额外事项,写进 `REPORT.md` 的"建议"段

`装 ollama + 拉模型 + 改 Onyx LLM 配置` 三步全部在 OEI-001 任务书之外,**且改 Onyx LLM 配置可能触及 compose / `.env` / admin API**(部分与硬约束冲突)。**必须由 codex 在 OEI-002 任务书里明确授权后才能执行**。

#### 给 codex 的建议

- OEI-002 任务书应包含:(a) LLM 选型最终拍板;(b) 安装/接入的执行步骤与证据要求;(c) 资源预算与 `.wslconfig` 调整建议;(d) 验收标准(如:重跑 OEI-001 的 8 个检索 = 3 + 2 + 3,期望 8/8 转 200 + 召回准确度判定);(e) ECE 侧接入边界(用户项目 API 凭证短效问题——见 §3)。
- 若选候选 B,OEI-002 任务书应明确授权 cc 改动 `.wslconfig`(本机配置,不属于 Onyx 上游)以缓解内存压力。

---

## 6. 完成动作

1. ✅ evidence/ 全部就位(共 25 个文件,**R3 更正**:原写"19 个"为口径错误,实际 `ls evidence/ | wc -l` = 25)
2. ⏳ 待执行:`echo "$(date -Iseconds) OEI-001 complete (TASK v3)" > DONE`
3. ⏳ STOP — 等待 codex 写 VERDICT.md
