# OEI-002 任务书 — 本地 LLM 部署与检索侧解封（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 版本：**v1** ｜ 签发日期：2026-09-23
> 本刀替代原《OEI-002 — ECE ↔ Onyx 连接器》：ECE 侧接入整体后移为 **OEI-003**（见 `OEI-ROADMAP.md`）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

## 本刀怎么来的

1. **用户决策（2026-09-23 22:2x）**：OEI-001 遗留的"大模型阻断"不在 OEI-001 内返工，**移入本刀执行**；同时采纳 cc 在 `OEI-001/REPORT.md` §5.5 提出的本地 LLM 部署建议。
2. **为什么顺序调换**：OEI-001 已证"写入侧"（建项目 / 上传 / 索引）可用，未证"查询侧"（`/api/search` 8 次全 400）。**引擎能否被检索是本刀之后所有刀的前提**——在它没被证实之前设计 ECE 适配器，等于在未验证的能力上做接口。
3. **cc 建议已并入**：候选 B（本地 ollama + Qwen2.5）定为主线；候选 A（云端 GLM-4-Plus）降为**需用户显式授权的降级路径**，不允许静默切换。

---

## 0. 一句话目标

在本机部署一个**常驻、离线、OpenAI 兼容**的本地 LLM，接成 Onyx 的 default LLM，把 OEI-001 那 8 次 `No default LLM model found` 的 400 **全部转成 200**，并在 Onyx 界面上看到"提问 → 引用那 3 份咨询文档 → 给出答案"的可见结果。

**架构定位（不可偏离）**：ECE 拥有身份/权限/来源/审计/领域对象/工作流；Onyx CE 是可替换的内容与检索引擎。本刀只动引擎侧，**不写任何 ECE 代码**。

## 1. 环境事实（codex 于 2026-09-23 22:2x 实测，可直接信任）

- Onyx CE v4.7.8，community tier，`gpu_enabled=true`，`ee_features_enabled=false`，9 容器在跑，`/api/health` = 200
- **LLM 现状**：`GET /api/admin/llm/provider` → `{"providers":[],"default_text":null,...}`（**零 provider**，这就是 400 的根因）
- **本机前提（本次新验，全部成立）**：
  - `systemctl is-system-running` → `running`（可做 systemd 常驻服务）
  - `ollama` **尚未安装**（`command -v ollama` 为空）
  - `https://ollama.com/install.sh` → 307（可达）；`https://registry.ollama.ai/...` → **200**（模型能拉）
  - WSL 侧 GPU：`/usr/lib/wsl/lib/nvidia-smi` → RTX 4070 Laptop，driver 528.76，8188 MiB 显存，已用 1760 MiB
  - **容器内可解析宿主机**：`docker exec onyx-api_server-1 python -c "socket.gethostbyname('host.docker.internal')"` → **172.17.0.1**（本地 LLM 能被 Onyx 访问的关键前提，已验）
- **资源现状（紧）**：Mem 11GiB / used 9.1GiB / **available 2.1GiB**；Swap 8GiB / **used 2.4GiB**（索引时涨上来的）
- **上刀遗留产物（保留，不要删）**：user project `id=1`（`OEI-001 Consulting Lab`）、3 份 COMPLETED 文档（user_file.id：`7bb48d46…` case / `1457df88…` methodology / `3b14b918…` play；chunk_count 3/4/4）
- **400 基线**：`OEI-001/evidence/05-*`(3) + `06-*`(2) + `07-*`(3) = **8 次**全部 400 `{"message":"No default LLM model found"}`。注意：`OEI-001/REPORT.md` §5.5 把它写成"9 个 400"，**实际是 8 个**，本刀顺手更正。

### 1.1 已验证的 LLM 配置 API（codex 只读反查）

| 动作 | 方法 | 路径 | 要点 |
|---|---|---|---|
| 写入 provider | PUT | `/api/admin/llm/provider` | body：`provider`(必填) / `name` / `api_key` / `api_base` / `model_configurations[{name,is_visible}]` |
| 查看 | GET | `/api/admin/llm/provider` | 返回 `{providers, default_text, …}` |
| 设默认 | POST | `/api/admin/llm/default` | 契约未验证，先反查 schema |
| 连通测试 | POST | `/api/admin/llm/test` | 同上 |
| 列模型 | POST | `/api/admin/llm/openai-compatible/available-models` | 同上 |

- provider 取值实测自源码常量，含 **`openai_compatible`**、`openai`、`ollama_chat` 等。
- **该账号（`codex@onyx-lab.example.com`，STANDARD）实测可直接调用 `/api/admin/llm/*`**（空体 PUT 返回 422 校验错误而非 403），本刀不需要管理员账号。
- 需要核对任意路由时（`/openapi.json`、`/docs` 均为 404）：

```bash
docker exec onyx-api_server-1 python -c \
  "from onyx.main import app; s=app().openapi(); [print(p) for p in sorted(s['paths'])]"
```

### 1.2 候选 A 的凭据事实（**默认不用**）

`/mnt/d/Projects/video-factory/.env.local` 存在（1112 字节），含键名 `GLM_API_KEY` / `GLM_BASE_URL` / `GLM_MODEL`（**cc 不读值、不复制、不打印**）。该文件属于**另一个项目**，跨项目复用云端密钥需要用户明确同意；未获授权前不得使用。

## 2. 工作区

```
onyx-lab/OEI-002/
├── TASK.md            ← 本文件（只读）
├── evidence/          ← 全部证据，按 01.. 序号命名
├── REPORT.md          ← 收口报告
└── DONE               ← 完成信号
```

**证据命名**：`00-oei001-hygiene.txt`、`01-llm-baseline.json`、`01-diagnostics-pre-llm.json`、`02-ollama-install.txt`、`03-ollama-service.txt`、`04-ollama-model.txt`、`05-ollama-local-probe.json`、`06-container-reach.json`、`07-onyx-llm-config.json`、`08-llm-ready.json`、`09-search-q1..3.json`、`10-search-boundary.json`、`11-repeat-1..3.json`、`12-ui-proof.md`、`13-diagnostics-post-llm.json`、`14-compliance-check.txt`、`15-container-snapshots.txt`

## 3. 任务步骤

**步骤 0 — 收尾 OEI-001 的三项遗留（R2/R3/R4）**

1. `OEI-001/REPORT.md` 的 CE/EE 边界清单：11 项逐项补**可追溯来源**（官方文档 URL + 引文）；凡落不到来源的一律改标 `UNKNOWN`；把"本刀实测"与"文献依据"分开标注。
2. 事实性更正：§5.5 的"9 个 400" → **8 个**；§6 的"共 19 个文件" → 按 `evidence/` 实际计数；`03-upload-*` 表格名与磁盘实名一致。
3. 合规证据补一条**真实命令的原始输出**（value-level 模式），落 `OEI-002/evidence/00-oei001-hygiene.txt`。

**步骤 1 — 基线快照**：`bin/collect-diagnostics.sh OEI-002/evidence/01-diagnostics-pre-llm.json`；同时保存 `01-llm-baseline.json`（`GET /api/admin/llm/provider`）。

**步骤 2 — 安装 ollama 并配成常驻服务**

```bash
curl -fsSL https://ollama.com/install.sh | sh        # 官方脚本；systemd 已在运行
```

- **必须**让它监听所有网卡，否则容器连不上（默认只听 127.0.0.1，这是本刀最容易踩的坑）：
  在 `/etc/systemd/system/ollama.service.d/override.conf` 写入 `[Service]` 段 + `Environment="OLLAMA_HOST=0.0.0.0:11434"`，再 `systemctl daemon-reload && systemctl restart ollama`。
- 证据：`02-ollama-install.txt`（版本输出）、`03-ollama-service.txt`（`systemctl status ollama` + 生效后的 `OLLAMA_HOST`）。
- 关注点：**重启后自恢复**（systemd `enabled`），不是只有当前会话能跑。

**步骤 3 — 拉模型**：`ollama pull qwen2.5:3b`（Q4_K_M，约 2GB 磁盘，8GB 显存够）。证据 `04-ollama-model.txt`（`ollama list` + 磁盘占用）。

- **降级顺序（写死，不要自由发挥）**：`qwen2.5:3b` → 拉取或加载失败（含 OOM/显存不足）→ `qwen2.5:1.5b` → 仍不行 → **停下报告**，附原始错误与资源快照，等用户决定是否授权候选 A。**不得静默切云端。**

**步骤 4 — 本机验证**：`curl http://127.0.0.1:11434/v1/chat/completions`（OpenAI 兼容）跑一次中文请求 → `05-ollama-local-probe.json`（记录响应时间与 `model` 字段回显）。

**步骤 5 — 容器内可达性闸门（不过就停）**

```bash
docker exec onyx-api_server-1 python -c "
import urllib.request
print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags', timeout=10).status)"
```

- 期望 200。**不通即 FAIL 并停**：原始报错存 `06-container-reach.json`，写清排查线索（OLLAMA_HOST 是否 0.0.0.0、WSL 防火墙、`host.docker.internal` 解析值），**不要改 compose / 不要重启容器**。

**步骤 6 — 接入 Onyx**

1. 先用 §1.1 的反查命令确认 `PUT /api/admin/llm/provider`、`POST /api/admin/llm/default`、`POST /api/admin/llm/test` 的 body schema；
2. 写入 provider：`provider=openai_compatible`、`name` 自定、`api_base=http://host.docker.internal:11434/v1`、`api_key` 填任意非空占位（ollama 不校验）、`model_configurations=[{"name":"qwen2.5:3b","is_visible":true}]`；
3. 设为 default 文本模型（UI 更顺手就用 UI，配置页截图路径计入证据）；
4. 连通测试；5. `GET /api/admin/llm/provider` 确认 `default_text` 非空。

- 证据：`07-onyx-llm-config.json`（请求 + 响应，**api_key 一律 `<REDACTED>`**）、`08-llm-ready.json`。
- `api_key` 不要出现在命令行参数里（会留在 shell 历史与 `ps`）；用 `--data @文件` 或环境变量。

**步骤 7 — 重跑 OEI-001 的检索验证（原样标准，本刀核心验收）**

原样重跑 v3 的 8 次调用：

- `09-search-q1..3.json`：`问题树怎么用` / `销售转交付的关键动作` / `咨询项目的交付物清单`
- `10-search-boundary.json`：负例 `zzz-nonexistent-topic-9371` + 一个精确命中词
- `11-repeat-1..3.json`：同一查询连跑 3 次

每个查询判定：命中是否正确、引用能否追溯到 `workspace/` 源文件（文件名 + 片段或行号）；并记录响应里**生成答案与召回文档的字段名**（以实测为准）。**与 8 次 400 基线逐一对照。**

**步骤 8 — UI 可见产物（"马上能看到"铁律）**：在 Onyx 界面用同一条查询，得到引用那 3 份咨询文档的答案。截图文件放 `OEI-002/evidence/`，路径 + 答案原文摘要写入 `12-ui-proof.md`。这一步是给人看的，不是给机器看的。

**步骤 9 — 资源复采**：`13-diagnostics-post-llm.json`，与 `OEI-001/diagnostics-pre.json`、`OEI-001/08-diagnostics-post.json` 三者对比；额外记录 ollama 进程 RSS 与显存占用；给出更新后的**长期承载结论**（YES/NO/CONDITIONAL + 依据）。

**步骤 10 — 合规与收口**：`14-compliance-check.txt`（value-level 凭据模式原始输出）、`15-container-snapshots.txt`（`docker ps` Up 时长，证明容器未被重启），写 `REPORT.md`。

## 4. 验收标准（codex 将逐条核对）

- [ ] **A0** 收尾项完成：`OEI-001/REPORT.md` 的 A9 有可追溯来源、计数与命名已更正、"9 个 400" 改成 8 个
- [ ] **A1** LLM 就绪：`08-llm-ready.json` 中 `providers` 非空且 **`default_text` 非 null**
- [ ] **A2** ollama 常驻：systemd 服务 `enabled` 且 `active`，且 **`OLLAMA_HOST=0.0.0.0:11434` 生效**（`03-ollama-service.txt`）
- [ ] **A3** 容器内可达：`06-container-reach.json` 显示容器访问 `host.docker.internal:11434` 成功
- [ ] **A4** 8 次检索**全部 200**（3 + 2 + 3），且逐次给出与 400 基线的对照
- [ ] **A5** 命中判定可核对：每个查询的判定引用 `workspace/` 源文件的文件名 + 片段或行号
- [ ] **A6** 边界两侧成立：负例给出"无相关命中"的判定与依据；精确命中确实命中对应文档
- [ ] **A7** 重复性：3 次响应的召回文档 id 集合给出"一致 / 不一致 + 差异明细"（基准是文档集合，不是生成文本逐字一致）
- [ ] **A8** UI 可见产物：`12-ui-proof.md` 含截图路径 + 答案原文摘要，且答案引用那 3 份文档
- [ ] **A9** 资源结论更新：三份诊断对比 + ollama RSS/显存 + 长期承载结论（YES/NO/CONDITIONAL + 依据）
- [ ] **A10** 合规：无凭据原值泄漏（含 ollama 配置与 api_key）；容器未重启/停止；未改上游源码 / compose / `.env` / ECE 主仓 / `onyx-lab/bin/`；未改 `.wslconfig`
- [ ] **A11** `REPORT.md` 对 A0..A10 每条都有结论 + 证据指针，无模糊表述
- [ ] **A12** 降级合规：若降到 1.5b 或候选 A，必须有原始错误证据 + 用户授权记录；**不得静默切换**

## 5. 完成后的动作（严格按序）

1. 自检目录、证据完整性、无密钥泄漏
2. `echo "$(date -Iseconds) OEI-002 complete" > DONE`
3. **STOP**，不启动下一刀
4. 等 `VERDICT.md`：PASS → 关闭本刀并签发 OEI-003（ECE 侧 Content Engine Port）；FAIL → 按 R{n} 返工

## 6. 硬约束（违反即 FAIL）

- ✅ **本刀显式授权的例外**（其余照旧）：安装 ollama 与拉取模型；写 ollama 的 systemd override；调用 `/api/admin/llm/*` 配置 provider 与 default。
- ❌ 不 restart / stop / down / rm **任何 Onyx 容器**；不改 compose 与 `.env`；不启动 code-interpreter
- ❌ **不改 `.wslconfig`**（改它必须 `wsl --shutdown`，会重启全部容器）。内存不够就写进报告建议，交用户决定
- ❌ 不用候选 A 的云端密钥（未经用户显式授权）；不读 `/mnt/d/Projects/video-factory/.env.local` 的值
- ❌ 不把 api_key / cookie 写进任何产出物；不在命令行参数里传密钥
- ❌ 不 commit / push；不碰 ECE 主仓；不改 `onyx-lab/bin/`、不改历史 `TASK.v*.md` / `VERDICT.md`
- ❌ 不做范围外功能；额外发现写进 REPORT 的"建议"段

## 7. 心跳约定

- cc 心跳对象：`onyx-lab/OEI-002/VERDICT.md`
- codex 心跳对象：`onyx-lab/OEI-002/DONE`
- 无新文件则静默，不重复执行、不打扰用户
