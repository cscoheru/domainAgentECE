# OEI-001 任务书 — Onyx CE 咨询知识库首验（cc 执行 / codex 审验）

> 签发：codex（架构 + 审验） ｜ 执行：Claude Code（i9 / WSL / `fisher`）
> 签发日期：2026-09-23 ｜ 版本：v2（工作区改到项目文件夹内，凭据改为本地生成）
> 状态机：本文件 → cc 执行 → `DONE` → codex 审验 → `VERDICT.md` → 按裁定行动

---

## 0. 一句话目标

证明 Onyx CE 能作为 ECE 的"内容与检索引擎"承载咨询行业知识：建项目、传 3 类文档、确认索引、验证检索质量，并记录 CE/EE 能力边界。

**架构定位（不可偏离）**：ECE 拥有身份/权限/来源/审计/领域对象/工作流；Onyx CE 只是可替换的内容与检索引擎。本刀只做引擎侧验证，不写任何 ECE 代码。

## 1. 环境事实（已验证，直接信任，不要重新部署）

- Onyx CE v4.7.8，community tier，`gpu_enabled=true`，`ee_features_enabled=false`
- 服务入口（WSL 本机）：`http://127.0.0.1:8080`；局域网：`http://192.168.5.237:8080`
- 9 个容器在跑（api_server / background / web_server / relational_db / opensearch / cache / inference_model_server / indexing_model_server / nginx），`/api/health` 返回 200
- 管理员账号已创建且权限完整；**账号凭据由你自行输入或从用户处获取，不要写进任何文件**
- Compose 目录：`/home/codex/onyx-lab/src/deployment/docker_compose`（只读！）
- API 端点不确定时，以 `GET http://127.0.0.1:8080/openapi.json` 为唯一事实来源

## 2. 凭据处理（本刀的重要修正）

会话 Cookie 需要你自己换取，**只存在 WSL 原生路径**（放 `/mnt/d` 无效：该挂载是 Windows 盘，`chmod` 不生效，权限形同虚设）：

```bash
mkdir -p /home/fisher/.onyx-lab/.secrets
chmod 700 /home/fisher/.onyx-lab/.secrets
# 取得 cookie 后：
chmod 600 /home/fisher/.onyx-lab/.secrets/admin-cookies.txt
```

- `bin/onyx-api.sh` 与 `bin/onyx-upload.sh` 默认从该路径读取 Cookie，也可用 `ONYX_COOKIE_FILE` 环境变量覆盖。
- 旧文件 `/srv/onyx-lab/.secrets/admin-cookies.txt` 若可读且未过期，可 `cp` 过来后 `chmod 600`；否则重新登录生成。
- **任何 evidence / report / 日志里不得出现 Cookie 或 token 原文**，一律写 `<REDACTED>`。

## 3. 工作区（所有产出物写到这里）

```
/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-001/
├── TASK.md            ← 本文件（只读，不要改）
├── workspace/         ← 你生成的 3 份 Markdown 源文件
├── evidence/          ← 所有请求/响应 JSON、检索结果、资源诊断
├── REPORT.md          ← 收口报告
└── DONE               ← 全部完成后创建（内容写完成时间）
```

## 4. 任务步骤

1. **建项目**：创建 project `OEI-001 Consulting Lab`，创建响应存 `evidence/project-create.json`
2. **造文档**：在 `workspace/` 生成 3 份有实质内容的 Markdown（每份 ≥ 400 字，中文，明确标注为 Demo Case）：
   - `case-management-consulting.md` — 管理咨询案例（背景/问题/方法/交付/结果）
   - `methodology-framework.md` — 咨询方法论（问题树 / 假设驱动 / MECE 的应用说明）
   - `play-sales-delivery.md` — 销售→交付衔接 play（阶段、动作、产出物、责任人）
3. **上传 + 索引**：3 份文件上传到该项目，每份上传响应存盘；轮询直到 3 份全部 indexed，保存最终状态
4. **检索验证**：调 Search API 跑 ≥ 3 个查询（例：「问题树怎么用」「销售转交付的关键动作」「咨询项目的交付物清单」），保存请求 + 完整响应；每个查询判断：命中文档是否正确、引用是否可追溯
5. **资源诊断**：索引前、索引后各跑一次 `bin/collect-diagnostics.sh`，输出都存 `evidence/`
6. **写报告** `REPORT.md`，必须含：
   - 每一步实测结果（PASS/FAIL + 证据文件指针）
   - 检索质量评估（命中准确度 / 引用可追溯性）
   - 资源结论（这台 i9 + WSL 能否长期承载标准档；索引前后内存变化）
   - CE/EE 边界清单：本次用到哪些 CE 能力；哪些能力（外部源权限同步 / 用户组 / SSO / SCIM / 高级审计）确认在 EE
   - 对 OEI-002（ECE 侧接口接入）的具体建议（只写建议，不实现）

## 5. 完成后的动作（严格按序）

1. 确认 §3 目录结构与 `evidence/` 齐全、无密钥泄漏
2. `echo "$(date -Iseconds) OEI-001 complete" > DONE`
3. **STOP**：不要开始任何下一刀工作
4. 等 codex 在本目录写 `VERDICT.md`：
   - `PASS` → 本刀关闭，等 codex 签发 OEI-002
   - `FAIL` → 按 `VERDICT.md` 的 R{n} 项返工；删旧 `DONE`、重做、重建 `DONE`

## 6. 硬约束（违反即 FAIL）

- ❌ 不 commit、不 push
- ❌ 不修改 Onyx 上游源码（`/home/codex/onyx-lab/src` 只读）
- ❌ 不 restart / stop / down / rm 任何容器；不改 compose 与 `.env`
- ❌ 不触碰 `/mnt/c`
- ❌ 不在产出物中出现密码 / Cookie / token 原文
- ❌ 不修改 ECE 主仓任何代码（本刀纯 Onyx 侧验证）
- ✅ 除 `workspace/` 的 3 份文档外，其余全部是调用与观察，不是开发

## 7. 心跳约定

cc 侧心跳检查 `VERDICT.md` 是否出现：出现则读取并按 §5.4 行动；未出现则静默等待，不打扰用户。
