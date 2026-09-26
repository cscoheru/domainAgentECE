# OEI-009 任务书 — 权限与审计接线（引擎召回的结果级授权 / 来源登记 / 时间盒授权生效）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1.3** ｜ 签发日期：2026-09-25
> **v1 → v1.1**：补"开工指令"节（用户要求：cc 刚重启，需要明确必读清单）。
> **v1.1 → v1.2（2026-09-25 15:1x）**：**新增步骤 0.0「凭据前置（blocking）」**。原因：两个 cookie 文件（`/home/fisher/.onyx-lab/.secrets/` 与 `/srv/onyx-lab/.secrets/`）**均已失效**，codex 实测同一个 jar 打 `/api/me`、`/api/settings`、`/api/user/projects` **全部 403**（而 `/api/health` 仍 200）——本刀步骤 0.3 / 1 / 2 / 6.2 都必须在真实引擎上取证，凭据修不好**整刀无法验收**。同时新增 `onyx-lab/bin/onyx-login.sh` 作为可复用的凭据刷新工装。
> **v1.2 → v1.3（2026-09-25 15:5x，由 cc 在步骤 1.1 合法停手触发）**：§1.2 那条"搜索响应里有 `document_id`"的前提**是错的**（我做的一次粗糙 grep，把上传/文件列表响应里的 `document_id` 当成了搜索响应的字段）。**映射键改判为「引擎侧文件名（`/api/search` 的 `title`）」**，§1.2 / 步骤 1 / 步骤 2 与验收 A1′ 相应重写；详见 `OEI-009/VERDICT.md`（含我的独立复跑与排除法）。**已完成并被审验的部分：步骤 0.1（webhook flake）、0.2（api-docs 解析器）、1.1（前提复核）——cc 从步骤 1.2 续做即可。**
> **v1.3 → v1.4（2026-09-25 16:2x）**：**§7 授权路径补上 `src/ece/identity/**`**。原因：本文档**步骤 4.1 自己就要求**"在权限模型层留出组织维度 …… `Identity` / `PermissionScope` 侧的组织标识"，而 `Identity` 定义在 `src/ece/identity/parser.py` —— **漏写进白名单是我的笔误**（与 OEI-008 §7 `tests/**` 那处自相矛盾同源）。本修订是**放宽性澄清，不新增任何工作项**：cc 已在该文件做的改动（`Identity.org_id` + 构造 helper）**不算越界**。约束不变：`Identity` 的既有字段语义与既有调用方式不得改变（只允许新增 org 维度与构造 helper），且**不得留下"调用方可自选主体"的入口**（TASK §1.3 事实 B）。
> 返工约定：本刀若需返工，一律标 **`OEI-009 R1` / `R2`**（不插新刀、不顺延既有编号）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## ✦ 开工指令（cc 必读：按序读完再动手）

> 你（Claude Code / `fisher`）刚重启过，会话记忆不可信任——**先按下面的清单读文件，再按本文档执行**。
> **`onyx-lab/` 顶层的一批文档已由用户并入 `onyx-lab/重启必读/`**（不是丢文件；`CODEX-ROLE.md` / `README.md` / `ASSET-INDEX.md` / `DECISION-ONYX.md` 仍在顶层）。

**① 按序必读（绝对路径，一份都别跳）**

```
1. /mnt/d/Projects/domainAgentECE/AGENTS.md                              ← 项目总规则（角色、红线、Case First）
2. /mnt/d/Projects/domainAgentECE/onyx-lab/README.md                      ← 入口索引 + 目录变更提示
3. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/CC-ROLE.md             ← 你的角色任务书（已升到 v2.1：§4 已改为指向本刀）
4. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/LOCAL-AGENT-PROTOCOL.md ← 共享规则 + **§5.1 资源纪律**（必读，本刀会用到真引擎取证）
5. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/OEI-ROADMAP.md         ← 路线图：看"已签发"一节里 OEI-009 的签发说明
6. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-008/VERDICT.md             ← 上一刀裁定（§7/§8.4 有转出给本刀的事项，步骤 0 就是从这来的）
7. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/DEPLOYMENT-STATUS.md   ← 环境事实：端口、密钥位置、内存约束、已知问题
8. /mnt/d/Projects/domainAgentECE/onyx-lab/重启必读/DEMO-DATA-CLEANUP-2026-09-25.md ← 演示项目现状 + 两步删除语义（本刀步骤 0.3 与 2.6 要用）
9. /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/TASK.md                 ← **本文件 = 唯一任务来源**
```

> 说明：`CC-ROLE.md` 里 §2/§4/§10 原来写的是首刀 OEI-001（已关闭），**v2.1 已更正**；若你读到的是旧版本，一律以本文件的清单为准。

**② 开工前先核对状态（只读，别凭记忆判断进度）**

```bash
cd /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009
ls -la                                     # DONE / VERDICT.md 是否存在（都不在 = 正常开工）
docker ps --format '{{.Names}}\t{{.Status}}'
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/api/health   # 期望 200
# ★ 凭据前置（本刀起必做）：health 200 ≠ 凭据可用
CK=/home/fisher/.onyx-lab/.secrets/admin-cookies.txt
for p in /api/me /api/user/projects; do printf '%s -> ' "$p"; curl -s -m 8 -b "$CK" -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8080$p"; done
# 两个都 200 才能开工；出现 403 → 走 §4 步骤 0.0（凭据由用户刷新，绝不用 mock 顶替）
cd /mnt/d/Projects/domainAgentECE/ece && git log --oneline -3 && git status -sb | head -5
```

**③ 本刀一句话（细节见 §4 步骤与 §5 验收）**

把 ECE 已有的权限引擎接到 OEI 这条线上：**引擎文档在 ECE 侧登记 → 引擎召回做结果级授权（fail-closed、无侧信道、主体只来自凭据）→ ACL 时间窗 `valid_from`/`valid_to` 真正生效**；外加 org scope 最小落位、三份只写不实现的设计文档、以及步骤 0 三项收尾（webhook flake / `check_api_docs.py` 解析器 / 测试上传改 scratch project）。

**④ 硬约束速查（违反即 FAIL，全文见 §7）**

- ✅ 本刀授权改：`src/ece/{consulting,api,permissions,connectors/onyx,migrations/versions}/**`、`scripts/check_api_docs.py`、`docs/{API,DATA_MODEL}.md`、`TASKS.md`、`tests/**`（可新增文件、可改装配部分，**断言不得改、测试不得删**）；可起临时 PG；可 `git commit`（**不 push**）
- ❌ 不引入新依赖（`pyproject.toml` / `uv.lock` 零 diff）；不改 Onyx 上游 / compose / `.env`；**不 restart / stop / down / rm 任何容器**；不做记忆 / 审批流 / 多租户 / ERP；不碰 `/mnt/c`；密钥只写 `<REDACTED>`
- ❌ **不要把测试产物传进演示项目 `id=1`**（唯一例外 = 步骤 2.6 那一份对照文档）；**验收不得要求用户截图**
- 📌 资源纪律：日常用 `ECE_CONTENT_ENGINE=mock`，**只在取证时**开真引擎，验完即释放（临时 PG / uvicorn / 反代一个都不留），收尾三查

**⑤ 收工与心跳**

```bash
echo "$(date -Iseconds) OEI-009 complete" > /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/DONE
```

然后 **STOP**（不启动下一刀）。心跳对象 = `onyx-lab/OEI-009/VERDICT.md`；出现 PASS 即停，出现 FAIL 按 `R1..Rn` 返工（删旧 `DONE` → 修 → 重建 `DONE`）。

## 0. 一句话目标

把 ECE **已经存在**的权限引擎接到 OEI 这条线上：让"引擎召回的文档"也受 ECE 授权约束（**结果级、fail-closed、无侧信道**），让 **ECE 成为这些文档的来源与权限的记录方**，并让 `acl_entries` 里**已经存在却从未参与判定**的时间窗（`valid_from` / `valid_to`）真正生效。

**为什么是这一刀**（codex 实测，见 §1）：

1. 今天 `GET /api/v1/consulting/library` 的**引擎召回对任何调用者返回同一组文档**（含匿名）——`engine_merge.py` 的注释自己写着 "any caller sees the same recall set"。这是 `CODEX-ROLE.md` R1（ECE 拥有身份/权限/来源/审计）在 OEI 线上**唯一的破口**，且它现在就在客户页面上。
2. ECE 侧对"送进引擎的文档"**没有任何登记**：不知道谁上传、属哪个部门、什么分类 → 既无法授权，也无法追溯。
3. `acl_entries.valid_from/valid_to` 被读出来、被传进 `check_permission`，**但六条判定规则没有一条看日期** → "临时授权"永远不过期（时间盒授权的模型已在、判定未接线，属可精确修复的小缺陷）。

> 本刀是"**接线**"而不是"重造"：`permissions/engine.py` 的判定顺序与 SQL 下推过滤已经在，别动它的秩序；本刀只把 OEI 的召回路径接上去，并把两处未接的判定补上。

---

## 1. 现状（codex 实测，可直接信任）

### 1.1 引擎召回这条路现在不受权限约束

- `src/ece/consulting/engine_merge.py`：`merge_engine()` 只按 `engine_name` / `EngineError` 决定"要不要给结果"，**不看身份**；文件头 docstring 原文：「the merge policy itself remains identity-agnostic (**any caller sees the same recall set**, gated only by whether the live engine is wired up)」。
- `src/ece/consulting/router.py`：`GET /library` 用 `caller_from_request_headers()` 构造 caller，注释写明 "read-only anonymous surface — no 401"；该 caller **只用于审计**，不参与筛选。
- `src/ece/connectors/onyx/port.py` 文件头：CE 无外部源权限同步能力（那在 EE）→ **只读调用不能下推权限**，per-result 过滤只能在 ECE 侧做。本刀就是把这句"设计契约"落成代码。

### 1.2 ECE 侧对"引擎里的文档"没有登记行

- OEI-007 的写路径（`POST /api/v1/consulting/documents` → `ContentEnginePort.upload_document`）把文件送进引擎并拿到 `document_id`（`onyx_adapter.py:_upload_status_record`），**ECE 数据库不留任何记录**（`grep -rn 'consulting_document|engine_doc|registry' src/ece` 除 adapter 内部外无命中）。
- 后果：无法回答"这条召回来自谁、属谁的权限范围、什么分类"；演示项目 `id=1` 里的文档与 ECE 侧任何对象都没有关联行。
- **映射键：v1.2 的前提被推翻，v1.3 改判（实测见 `VERDICT.md` §3）**。cc 在步骤 1.1 复核后停手（历史证据 0/11 命中），codex 本机独立复跑确认：
  - `/api/search` 的结果字段**只有** `{citation_id, title, content, link, source_type, updated_at}` —— **没有 `document_id`**；`link` 实测为 **null**；`citation_id` 是**每次响应从 1 重新编号的序号**（同一份 `methodology-framework.md` 在两次查询里分别拿到 `citation_id=1` 与 `3`）→ 它不是文档标识。
  - `/api/user/projects/files/1` 的写侧标识是 **UUID**（如 `1457df88-02cc-473a-aacc-16dbaba0e332`），与搜索结果的任何字段**都无法对应**：**写侧有 id、读侧没有 id**。
  - **唯一可用且 ECE 完全可控的键 = `title`，即上传时 ECE 传给引擎的文件名**（实测 3 份演示文档每次召回都返回其上传时的文件名）。
- **因此本刀的映射契约（硬约束，写进代码注释与文档）**：

  ```
  写侧：ECE 生成"引擎文件名" ece-<docref>-<slug>.<ext>（确定性、人可读、唯一）→ 登记 engine_filename（唯一约束）+ original_filename（展示用原名）
  读侧：搜索结果 → 按 (engine_name, title) 精确查登记行（并要求 source_type == "user_file"）
        查到 → 用该登记行的 classification + ACL 走 check_permission
        查不到 → fail-closed 拒绝（并计数）
  多 chunk：同一 title 的多条结果 = 同一条登记行 = 同一判定；engine_items 按登记行去重
  ```

  - `engine_document_id`（写侧 user_file UUID）**只作写侧溯源，不是读侧键**——注释里写明，防止后人再推导出错误契约。
  - 排除记录（别再重开）：`citation_id` ❌（每次响应重排）、`document_id` ❌（不存在）、`link` ❌（null）、`content_sha256` ❌（chunk 级 + reindex 不稳定）、"召回后 N+1 反查文件列表" ❌（延迟 ×N 且最后仍要按名字对上）。

### 1.3 权限引擎：成熟，但两处没接线

- `src/ece/permissions/engine.py`：判定顺序 = deny > user > role > department > classification 默认 > default deny；Store 读走 **SQL 子查询过滤（非后置）**；`POST /permissions/check` 是验证面；`DEFAULT_CLASSIFICATION_MATRIX` 的 `restricted → deny` 有真实越权修复记录（e2-025）。
- **事实 A（本刀核心）**：`acl_entries` 从 0001 起就有 `valid_from` / `valid_to` 两列（`0001_initial.py:153` 附近）；`api/identity.py:118` 把它们 `SELECT` 出来并塞进 `acl_entries` 传给 `check_permission`；而 `check_permission` 规则 1–4 **只用 `effect` / `subject_type` / `subject_ref`，从不看日期**。全仓 `grep valid_from|valid_to` 的判定使用只出现在 `relationships` / 域策略那条线，**ACL 的这两列是惰性的**。
- **事实 B（范围外，但本刀必须遵守）**：`/permissions/check` 允许调用方在 body 里自选被检查主体（`req.user_ref`，`api/identity.py:69-88` 有 codex 的 SECURITY FINDING 注释，是已登记的 V0→Production 必过门槛）。**本刀新增的判定路径不得复用这个语义**（主体只能来自已认证凭据/请求头，不接受调用方自选）。

### 1.4 既有审计面与已知遗留

- `context_requests` / `context_items`（迁移 0005）是"一次 context 组装"的审计面，粒度是 **request 级**；`GET /audit/context/{request_id}` 可查（owner + delegation/org 规则）。
- OEI-008 的引擎调用审计是**进程内** `audit_log`（`onyx_adapter.py:_audit`），不持久、不跨 worker —— `OEI-008/VERDICT.md` §3 D3 已裁定：**持久化设计**是本刀交付项（含代价评估），本刀**只写设计、不实现**。
- 步骤 0 的三项收尾来自既有 VERDICT 转出：
  - `tests/integration/test_s20_audit_webhook.py::test_webhook_receives_event`：固定 `sleep(0.5)` 的投递竞态（≈1/12 flake，`OEI-008/VERDICT.md` §7.1）。
  - `scripts/check_api_docs.py`：解析器只认 `^### (GET|POST…)`，对 §11/§12 带编号标题的 4 条 consulting 路由误报（`OEI-008/VERDICT.md` §3 D6）。
  - 测试上传共用演示项目 `id=1` → 演示项目被探针污染（`DEMO-DATA-CLEANUP-2026-09-25.md` §4，转出要求写进本刀）。

### 1.5 演示数据现状（本刀会碰它，先知道现状）

- 演示项目 `id=1` 现有**已清理为 3 份真文档**：`case-management-consulting.md` / `methodology-framework.md` / `play-sales-delivery.md`（全部 `status=COMPLETED`）。
- 删除有项目关联的文件是**两步语义**（先 `unlink` 204，再 `delete` 200；直接 delete 会返回 200 + `has_associations: true` 却不删）——`DEMO-DATA-CLEANUP-2026-09-25.md` §2 已记录。

---

## 2. 范围锁

**做**：

1. 引擎文档的 **ECE 侧登记**（来源 + 分类 + 上传者 + 引擎 id）；
2. `/library` 引擎召回的**结果级授权**（fail-closed + 侧信道规则 + 主体只来自凭据）；
3. **ACL 时间窗生效**（`valid_from`/`valid_to` 参与判定 + 边界用例）；
4. **org scope 最小落位**（为 OEI-010 记忆预留，只到模型与单测，不实现记忆）；
5. **三份设计文档**（引擎审计持久化 / org scope 与记忆挂接点 / context assembly 第 6 步接法）；
6. 步骤 0 的三项收尾。

**不做**（做了即越界）：

- 不做持久上下文记忆（OEI-010）；不做审批流 / 授权签发流程（模型定稿，实现后置）；
- 不做多租户 SaaS、计费、K8s；不做 ERP 或任何"写企业系统"的能力；
- 不调检索质量 / 不改 top_k 策略 / 不换模型（OEI-012）；
- 不补种子内容与行业标签（OEI-011）；
- 不改 Onyx 任何东西（源码 / compose / `.env` / 容器）；不引入新依赖。

---

## 3. 工作区与证据命名

```
onyx-lab/OEI-009/
├── TASK.md      ← 本文件（只读）
├── workspace/   ← 源文件/素材（如 ACL 种子脚本、登记回填脚本）
├── evidence/    ← 逐项证据
├── REPORT.md    ← 收口报告
└── DONE         ← 完成信号
```

建议证据文件（命名沿用既往刀）：

`00-credentials.txt`（凭据前置：**只记状态码与文件 mtime，绝不记 cookie 值**）、`00a-webhook-flake-fix.txt`、`00b-api-docs-parser.txt`、`00c-scratch-project.txt`、`01-engine-doc-key-mapping.json`、`02-registry-migration.txt`、`03-registry-write-path.json`、`04-backfill-demo-docs.json`、`05-per-result-filter-matrix.json`、`06-fail-closed.json`、`07-side-channel.txt`、`08-timebox-acl.txt`、`09-design-engine-audit.md`、`10-design-org-scope.md`、`11-design-assembly-step6.md`、`12-test-db-free-raw.txt`、`13-test-suite-raw.txt`、`14-docs-backfill.txt`、`15-git-commit.txt`、`16-compliance-check.txt`

> **背景文档的位置（本刀签发时的事实，用户正在整理中）**：状态类文档已归入 **`onyx-lab/重启必读/`** —— 目前含 `CC-ROLE.md`、`LOCAL-AGENT-PROTOCOL.md`、`OEI-ROADMAP.md`、`DEPLOYMENT-STATUS.md`、`DEMO-DATA-CLEANUP-2026-09-25.md`、`PATH-NOTES-2026-09-25.md`、`REVIEW-sonnet-assessment.md`；而 `CODEX-ROLE.md`、`README.md`、`ASSET-INDEX.md`、`DECISION-ONYX.md` **仍在 `onyx-lab/` 顶层**。本文件正文里出现的无路径文件名，按上面这一分布解析（找不到就问 codex，不要猜）。`OEI-00N/` 与 `templates/`、`bin/` 位置不变。

---

## 4. 任务步骤

### 步骤 0.0 — 凭据前置（**blocking**：凭据不修好，本刀无法验收）

**现状（codex 2026-09-25 实测，可直接信任）**

- Onyx 栈健康、`/api/health` = **200**，但两个 cookie 文件**都已失效**：同一个 jar 打 `/api/me`、`/api/settings`、`/api/user/projects` **全部 403**。
- 两个文件都是 **2026-09-23** 生成（237 字节，cookie 名 `fastapiusersauth`，jar 自带 expiry ≈ 2026-09-30）→ 失效原因**不是 jar 自身到期，而是服务端会话失效**（容器重启 / 会话丢失）：`exp` 看着还有效也会 403。别被 jar 里的日期骗了。
- 本机 Onyx **只认这个 jar**：`onyx_adapter._parse_netscape_cookies()` 与 `bin/onyx-api.sh` 都从文件读 cookie，**没有**环境变量或 Bearer 兜底。
- 影响面：本刀**步骤 0.3 / 1 / 2 / 6.2** 全部要在真引擎上取证 → 凭据不修，核心交付**无法验收**。
- **更新（2026-09-25 15:20，用户已刷新；codex 实测 200/200）**：两份 jar 均已用 `bin/onyx-login.sh` 重写（mtime `2026-09-25 15:20:16`，chmod 600），`/api/me`、`/api/settings`、`/api/user/projects` 均 **200**，认证身份 `codex@onyx-lab.example.com`。→ **cc 仍须自己复验并落盘**（A0b 要的是你自己的证据，不是转述我的结论）。注意新 jar 的 session 仍是 **7 天**量级（约 2026-10-02 失效），本刀取证要在窗口内做完。

**谁来做（分工硬约束）**

- **刷新凭据 = 用户（`fisher`）手工做，不是 cc 的活。** 密码是用户资产：cc **不得**索取、不得接触、不得写进任何文件或证据。工装已就位：

  ```bash
  bash /mnt/d/Projects/domainAgentECE/onyx-lab/bin/onyx-login.sh \
    --also /srv/onyx-lab/.secrets/admin-cookies.txt
  # 交互输入邮箱（默认 codex@onyx-lab.example.com）与密码（不回显）；
  # 成功后自动 chmod 600，并只读验证 /api/me 与 /api/user/projects
  ```

  脚本设计：**先写临时 jar，`/api/me` 验证通过后才替换目标文件** → 登录失败不会破坏旧凭据；只打印状态码，不打印 cookie 值。

**cc 要做的**

1. **开工第一件事就是验证凭据**：用上面的 jar 打 `/api/me` 与 `/api/user/projects` **必须都 200**；把**状态码 + 两个 jar 的 mtime** 写进 `evidence/00-credentials.txt`（**绝不记录 cookie 值**）。
2. 若仍是 403 → **立即停手**：在 `REPORT.md` 顶部写 `BLOCKED — 引擎凭据未刷新`，把不依赖引擎的部分（步骤 0.1 / 0.2、只写不实现的设计文档）做完或明确标注未做，**然后停机等用户**。**绝不允许**用 `ECE_CONTENT_ENGINE=mock` 顶替真引擎取证（OEI-007 R1 的教训），也绝不允许把 mock 结果写成"已取证"。
3. 凭据在手后，**每一步真引擎取证都要留状态码**；中途再出现 401/403，一律按"凭据又失效"处理（停手 + 请用户刷新），**不要在代码里加重试去绕过**。

**允许 / 不允许**

- ✅ 允许：刷新 cookie 文件（用户执行）、只读验证、必要时重建两个 jar。
- ❌ 不允许：改 Onyx 的 compose / `.env`、改 `USER_AUTH_SECRET`、重启/重建容器、把密码或 cookie 值写进任何证据或文档、用 mock 冒充真引擎。
- 📌 **若反复失效**：把"引擎凭据耐久化"写进 REPORT 的建议段——本部署 API 支持 `Authorization: Bearer <PAT>`（security 为 `APIKeyCookie` 或 `OAuth2PasswordBearer`），且有 `/api/user/pats` 创建接口，但 **ECE adapter 目前只支持 cookie 文件**；是否改造由 codex 决定，**本刀不实现**。

### 步骤 0 — 三项收尾（先做，做完再进主线）

1. **修 flake**：`tests/integration/test_s20_audit_webhook.py::test_webhook_receives_event` 的固定 `time.sleep(0.5)` 改为**轮询等待事件（带明确超时）**。完成标准：同条件连跑 **12 次 0 failed**（把原始汇总落盘；不改断言语义，只改等待方式）。
2. **修 `scripts/check_api_docs.py` 解析器**：让 §11/§12 那 4 条带编号标题的 consulting 路由被正确解析。**不得靠改文档标题来迁就解析器**（若你判断必须改文档格式，先在 REPORT 说明理由）。给出"修前 4 条误报 / 修后 0 条"的对照输出。
3. **测试上传改用独立 scratch project**：跑测试/探针时不再往演示项目 `id=1` 上传。`POST /api/v1/consulting/documents` 已支持 `project_id`，用一个专用 scratch project（如 `OEI-009 Scratch`）。完成标准：跑完测试后 `GET /api/user/projects/files/1` **仍是 3 份**（给出前后对照）。

### 步骤 1 — 引擎文档的 ECE 侧登记（来源与权限的记录方）

1. ~~复核映射键~~ **✅ 已完成并审验（见 `VERDICT.md` §1/§3）**：结论 = 映射键是 `title`（引擎侧文件名），不是 `document_id`/`citation_id`/`link`。**不要再重新论证，直接按 §1.2 的契约实现。**
2. **新增登记表**（推荐**新表**，如 `engine_documents`，迁移 `0009_*`）：至少含 `engine_name` / `engine_project_id` / **`engine_filename`（= 引擎侧 `title`，读侧唯一键）** / `original_filename`（展示用）/ `engine_document_id`（写侧 user_file UUID，**仅写侧溯源**）/ `content_sha256` / `classification` / `uploaded_by`(user_ref) / `department` / `org_id`(可空) / `created_at`，并对 **`(engine_name, engine_filename)`** 建唯一约束。
   - 为什么推荐新表而不是扩展 `documents`：`documents` 是 ECE **原生 ingest** 表（带 `doc_chunks` / FTS / vector，被 `context/assembly.py` 读），把引擎指针塞进去等于把可替换引擎耦进原生管线。若你选择改 `documents`，必须在 REPORT 写明理由与兼容性论证。
3. **写路径接线（含受控文件名）**：`POST /api/v1/consulting/documents` 在调 `upload_document()` **之前**，把调用方给的文件名转成 ECE 受控引擎文件名 `ece-<docref>-<slug>.<ext>`（`docref` 用登记行主键的稳定短表示；转换必须是**确定性**的：同输入 N=5 次同名），把**原名**存 `original_filename`；上传成功后写登记行（分类取调用方给的值或确定性词典建议值）。写失败与上传失败的一致性策略要写清。**空/越界值按既有 `_dropped` 语义处理，不新增枚举。**
   - 也就是说：**引擎里看到的文件名从此带 `ece-` 前缀**——这是可读性换确定性，属于有意的设计取舍，要在 `docs/API.md` 写一句。
4. **回填现有 3 份演示文档**（**不改名、不重传**）：按它们**当前真实的 `title`** 建登记行——`case-management-consulting.md` / `methodology-framework.md` / `play-sales-delivery.md`（要先用只读接口 `/api/user/projects/files/1` 复核当前列表）。分类建议 **`public`**（理由：它们是已发布方法论的演示素材，且**保持今天"匿名也能看到"的行为不退化**——若你判断该改，必须先给出"演示面不倒退"的对照实测）。回填必须**可重复执行（幂等）**，给出前后行数与二次执行无新增的证据。

### 步骤 2 — 结果级授权（本刀核心，必须用真实引擎取证）

1. `/library` 的引擎召回结果**逐条**判定：`EngineDocument → (title, 且 source_type == "user_file") → 登记行 → check_permission(identity, object_type='engine_document', object_ref=<登记行键>, classification=<登记行.classification>)`；只保留 `allowed` 的条目；**同一登记行的多条 chunk 结果只出一张卡**（去重，理由写进代码注释）。
2. **fail-closed**：召回结果**映射不到登记行**（或登记行缺 `classification`）→ **不返回**并计数。实测要求（这条现在很容易造）：用 **`bin/onyx-upload.sh` 直接往演示项目 `id=1` 传一份不经过 ECE 的探针文件**（它没有登记行），证明它**不出现**在任何身份（含匿名、含管理身份）的 `engine_items` 里；测完按 `DEMO-DATA-CLEANUP` §2 的两步语义把它删掉，避免污染演示项目。
3. **无侧信道**：返回的 `engine_items` 必须就是"授权后集合"本身——**标题、片段、条数、顺序都不得泄露被过滤项的存在**（不得出现"共 3 条，隐藏 2 条"之类计数；`engine_status` 的枚举语义不得被借用成泄露通道）。给出规则说明 + 至少一组对照实测（授权前/后）。
4. **主体只来自凭据**：新增判定路径**不得**接受调用方自选主体（不得复用 `/permissions/check` 的 body 语义）。匿名调用者按既有 "read-only anonymous" 策略继续可用，但必须按**最小权限**判定（匿名只应看到 `public` 档；给出实测）。
5. **回归不破**：static 侧载荷逐字节不变（sha256 对照）；`engine_status` 的 `ok` / `unavailable` / 无命中三种状态行为不变（给出三种状态各一次实测）。
6. **演示可证伪**（本刀的门面）：准备一组**对照数据**，使"同一 query、两个身份 → 不同可见集合"可被机器证明。推荐最小做法：
   - 新增 1 份对照文档（走上传路径进演示项目 `id=1`），登记为 `restricted` 档；
   - 加 1 条 `acl_entries`：`subject_type=user`、`subject_ref=<演示用户>`、`object_type=engine_document`、`object_ref=<登记行键>`、`effect=allow`、`valid_from/valid_to` 给定未来窗口；
   - 断言：**该用户看到 4 条，其他用户/匿名看到 3 条**，且该文档的标题与片段对无权者**完全不出现**。
   - 这份对照数据属**有意保留的演示数据**（不是污染）：要在 REPORT 与 `DEMO-DATA` 记录里登记（含它的两步删除方法），并保证可重复创建（脚本或 make 目标）。

### 步骤 3 — 时间盒授权（ACL 时间窗生效）

1. 让 `check_permission` 的 ACL 规则（deny 与 allow 两侧）**考虑时间窗**：语义与 `DATA_MODEL.md` 一致——`valid_from IS NULL → -∞`、`valid_to IS NULL → +∞`，区间为 `[valid_from, valid_to)`。**判定时点要参数化**（默认"现在"），以便测试确定性覆盖边界。
2. 边界两侧各一例（含"未生效"与"已过期"两种失权方向）：`valid_to = 今天` → 无效；`valid_to = 明天` → 有效；`valid_from = 明天` → 无效（未生效）。
3. **端到端实测**：用步骤 2.6 那条 ACL，把 `valid_to` 改成过去 → 该用户立即看不到那第 4 条；改回未来 → 又能看到（给出两次原始响应）。
4. 既有权限数据集（`e2_*` / `test_s22_permissions.py` 等）**断言不得改**。若某条既有用例因此改变结论，**不要顺手改期望值**——写进 REPORT 偏差段并给根因分析（这属于"发现真缺陷"的信号）。

### 步骤 4 — org scope 最小落位（为 OEI-010 预留）

1. 在权限模型层留出**组织维度**并写清来源：`Identity` / `PermissionScope` 侧的组织标识 + 判定入口如何接受它（现有事实：`0007_user_orgs` 只给 `context_requests` 加了 `org_id`；`X-Org-Id` / `ECE_USER_ORGS` 只在 `/audit`、`/debug` 用）。
2. 定义**一条可判定的可见性规则**并落成单测（例如：org 级对象 → 同 org 用户可见；user 级对象 → 仅 owner 可见），证明"两种 scope 都能被表达"。
3. **不实现记忆**：不建记忆表、不加记忆接口、不碰 `context/assembly.py` 的组装顺序。
4. 文档写明 010 的挂接点：记忆写入/读取都必须经过权限引擎，且**读取步骤必须位于权限判定之后**，并说明理由（否则重蹈"后置过滤"侧信道）。组织级记忆的**写入权限**候选方案放步骤 5.2。

### 步骤 5 — 三份设计文档（只写，不实现）

1. `09-design-engine-audit.md`：引擎调用审计的**持久化设计**——字段、粒度（per-call vs per-request）、采样/批量写入 vs 接入 `0005_context_audit` 的**代价评估**（含写放大估算与失败路径），以及"进程内 `audit_log` 的已知局限"。给结论与建议归属的下一刀，**本刀不实现**。
2. `10-design-org-scope.md`：scope 模型定稿 + **组织级记忆的写入权限**（谁能改组织口径：管理员？领域负责人？）候选方案与建议——这是 `REVIEW-sonnet-assessment.md` §4.2 遗留的待澄清项。
3. `11-design-assembly-step6.md`：`src/ece/context/assembly.py` 第 6 步（"Retrieve authorized documents"，现为 stub）**改走 `ContentEnginePort`** 的接法与代价评估，含"如何复用步骤 2 的过滤"、"与原生 `documents` 检索的关系"。**只写评估，不改代码。**

### 步骤 6 — 测试与收尾

1. **DB 无关单测**（新文件，不依赖 PG）：登记映射与合并、fail-closed、侧信道规则（计数/顺序）、时间窗三个边界、org scope 两种 scope 的判定。
2. **集成实测**（真实 `ECE_CONTENT_ENGINE=onyx` + 临时 PG）：步骤 2.6 的"两个身份 → 不同集合"矩阵 + 步骤 3.3 的端到端。
3. **无回归**：按资源纪律（`LOCAL-AGENT-PROTOCOL.md` §5.1）**先跑相关子集**，收尾**跑一次**全套件并落盘原始汇总（基线 `757 passed / 0 failed`；步骤 0 修掉 flake 后应期望 `0 failed`）。
4. **收尾三查**（写进 REPORT）：无残留探测进程（`pgrep`）、无残留 `ece-*` / `ece-pg-*` 容器（`docker ps -a`）、内存/swap 快照。

### 步骤 7 — 文档与提交

- `docs/API.md`：登记与过滤语义、匿名最小权限、`engine_items` 的授权后语义、时间窗语义；
- `docs/DATA_MODEL.md`：新表（若你选了新表）；
- `TASKS.md`：本刀条目；
- `git add` + `git commit`（**不 push**），并在 REPORT 里给出 commit 短 hash 与文件清单。

---

## 5. 验收标准（codex 将逐条核对）

- [ ] **A0** 步骤 0 三项收尾完成：webhook flake 12 连跑 0 failed（原始输出）；api-docs 解析器误报 4 → 0（前后对照）；测试上传后演示项目仍是 3 份（前后对照）
- [ ] **A0b**（**blocking，先于一切**）凭据前置：`evidence/00-credentials.txt` 里 `/api/me` 与 `/api/user/projects` **均为 200**（只记状态码与 jar mtime，**无 cookie 值**）；若为 403，则 `REPORT.md` 顶部必须是 `BLOCKED`，且**全刀不得出现任何 mock 冒充实引擎的取证**
- [x] **A1**（2026-09-25 已裁）原前提不成立，**cc 的合法停手分支成立**，codex 已独立复跑并改判映射键 = `title`（见 `VERDICT.md` §3）——**本条不再重开**
- [ ] **A1′** 映射契约落实：写侧生成**确定性的受控引擎文件名** `ece-<docref>-<slug>.<ext>`（同输入 N=5 同名）、登记表 `(engine_name, engine_filename)` 唯一、读侧按 `(title, source_type="user_file")` 精确匹配、**`engine_document_id` 的注释写明"仅写侧溯源、非读侧键"**（给出代码片段 + 一次上传后引擎里确实带 `ece-` 前缀的召回证据）
- [ ] **A2** 登记表落位：迁移可升可降、**`(engine_name, engine_filename)`** 唯一约束在、写路径上传成功即登记（给出写入后的查表输出）
- [ ] **A3** 3 份演示文档回填**幂等**（二次执行零新增），且演示行为不退化（匿名仍能看到它们）
- [ ] **A4** **结果级授权**：同一 query 下，**两个不同身份得到不同 `engine_items`**（推荐对照：授权用户 4 条 / 其他身份与匿名 3 条），且被拒文档的**标题与片段完全不出现**（原始响应）
- [ ] **A5** **fail-closed**：引擎里存在但 ECE 未登记的文档，对**任何**身份都不返回（原始响应 + 说明）
- [ ] **A6** **无侧信道**：授权后集合的条数/顺序不泄露被过滤项（规则说明 + 至少一组对照实测）；匿名按最小权限（仅 `public`）且实测一致
- [ ] **A7** static 侧零变化（sha256 对照）+ `engine_status` 三分支行为不变（ok / unavailable / 无命中各一次）
- [ ] **A8** **时间窗生效**：边界两侧各一例（`valid_to=今天` 无效 / `=明天` 有效 / `valid_from=明天` 未生效）+ 端到端"过期即失权、恢复即复现"两次原始响应；既有权限用例断言未被改动
- [ ] **A9** **org scope 最小落位**：模型层有组织维度 + 一条可判定规则 + 对应单测；**未引入任何记忆表/接口**（给出 `grep` 证据）
- [ ] **A10** 三份设计文档存在（`09/10/11-*`），且引擎审计持久化那份含**代价评估**、org scope 那份含**组织级记忆写入权限**候选、assembly 那份含**接法与复用步骤 2 的说明**
- [ ] **A11** DB 无关单测通过（落盘原始输出）；集成矩阵与端到端落盘；全套件跑一次并落盘（failed ≤ 基线 0）
- [ ] **A12** 文档与提交：`docs/API.md` / `docs/DATA_MODEL.md` / `TASKS.md` 已更新；commit 落盘（**不 push**）
- [ ] **A13** **合规**：无凭据值落盘；未碰 Onyx 上游 / compose / `.env` / `.wslconfig` / swap；未改 36 个种子对象与三域业务断言；**未 push**；未把测试产物留在演示项目
- [ ] **A14** **不使用"用户截图"作为任何验收项**；可见性/行为证据一律机器可校验（HTML 转储 + DOM 锚点或经同源代理的原始 API 输出）

---

## 6. 完成后的动作（严格按序）

1. 自检目录结构与证据完整性、无密钥泄漏、临时资源已清理（收尾三查）
2. `echo "$(date -Iseconds) OEI-009 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭并签发 OEI-010；FAIL → 按 `R1/R2…` 返工后重建 `DONE`

---

## 7. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**：改 `src/ece/consulting/**`、`src/ece/api/**`、`src/ece/permissions/**`、`src/ece/identity/**`（**仅限 `Identity` 的 org 维度与构造 helper；既有字段语义与调用方式不得改变**，且不得新增"调用方可自选主体"的入口）、`src/ece/connectors/onyx/**`（只在必要处）、`src/ece/migrations/versions/**`（新增 0009）、`scripts/check_api_docs.py`、`docs/API.md`、`docs/DATA_MODEL.md`、`TASKS.md`、`tests/**`（**允许新增文件，且允许修改既有测试文件的装配部分（fixture / stub / 依赖注入 / import）——断言不得改动、测试不得删除**）；可起临时 PG 跑套件；可往演示项目 `id=1` 只加**步骤 2.6 那一份对照文档**（其余测试产物一律进 scratch project）；可 `git commit`（**不 push**）
- ✅ **凭据规则**：允许用 `onyx-lab/bin/onyx-login.sh`（由用户执行）刷新 cookie jar，允许只读验证 `/api/me`；**不得**索取/接触用户密码，**不得**把 cookie 或密码原文写进 `evidence/`、`REPORT.md` 或任何文档（只记状态码与 mtime）
- ❌ **凭据不可用时不得降级**：不得用 `ECE_CONTENT_ENGINE=mock` 顶替真引擎取证，不得把未取证项写成已通过（应按步骤 0.0 停手并标 `BLOCKED`）
- ❌ 不引入新依赖；不改 `pyproject.toml` / `uv.lock`
- ❌ 不改 Onyx 上游源码 / compose / `.env`；不 restart / stop / down / rm 任何 Onyx 容器
- ❌ 不改 `check_permission` 的**判定顺序**（deny > user > role > dept > classification > default deny）；只在规则内部补时间窗，不重排优先级
- ❌ 不做记忆 / 审批流 / 多租户 / ERP 写能力 / 检索调优 / 种子内容补全
- ❌ 不删演示项目里的 3 份真文档；不使用"删了再说"的破坏性操作
- ❌ 不得要求用户截图

---

## 8. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-009/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-009/DONE`
- 无新文件则静默，不重复执行、不打扰用户
