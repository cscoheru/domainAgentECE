# i9 本地部署实况（Onyx CE）

> 实测时间：2026-09-23 ｜ 采集方式：`bin/collect-diagnostics.sh` 同类命令，非推断
> 一句话：9 个容器全部 Up，API healthy，唯一的硬约束是内存余量（约 2.9Gi）。

---

## 1. 主机与 WSL 配置

| 项 | 值 |
|---|---|
| 主机 | Intel i9-13900H / 20 逻辑 CPU / 16GB 物理内存 / 1TB SSD |
| GPU | NVIDIA RTX 4070 Laptop 8GB（WSL GPU passthrough 已开通，`nvidia-container-toolkit` 已装） |
| 系统 | Windows + WSL2 + Ubuntu 22.04 |
| `.wslconfig` | `memory=**14GB**`（2026-09-24 起，原 12GB）、`processors=16`、`swap=8GB`、`networkingMode=mirrored`。改前备份：`onyx-lab/.wslconfig.bak-2026-09-24.txt`。⚠️ **改这行必须 `wsl --shutdown` 才生效**（见 §9） |
| 主机 LAN 地址 | `192.168.5.237` |
| WSL 用户 | `fisher`（本地 agent 运行账号）、`codex`（另一账号，本目录对两者可读写） |

## 2. 资源实测

```
Mem:  total 11Gi   used 8.4Gi   available 2.9Gi
Swap: total 8.0Gi  used 10Mi
Disk: /        1007G, used 41G, avail 916G
      /mnt/d    621G, used 27G, avail 595G
```

容器内存占用（`docker stats --no-stream`）：

| 容器 | 内存 | CPU | 上限 |
|---|---|---|---|
| onyx-background-1 | 2.353 GiB | 2.8% | 3 GiB |
| onyx-opensearch-1 | 1.977 GiB | 1.6% | 2.5 GiB |
| onyx-inference_model_server-1 | 1.178 GiB | 0.3% | 2 GiB |
| onyx-indexing_model_server-1 | 1.094 GiB | 0.3% | 2 GiB |
| onyx-api_server-1 | 616.9 MiB | 0.3% | 1.5 GiB |
| onyx-relational_db-1 | 141.3 MiB | 3.8% | 768 MiB |
| onyx-web_server-1 | 130.4 MiB | 0.0% | 512 MiB |
| onyx-nginx-1 | 17.8 MiB | 0.0% | 128 MiB |
| onyx-cache-1 | 15.1 MiB | 2.4% | 128 MiB |

合计约 **7.5 GiB**。结论：**空载可跑，余量偏紧**；重索引或并发演示前应先看 `collect-diagnostics.sh` 的输出。

## 3. Onyx 部署位置与形态

| 项 | 值 |
|---|---|
| 版本 | Onyx CE v4.7.8 |
| 源码/部署目录 | `/home/codex/onyx-lab/src`（**只读，禁止改动**） |
| Compose 目录 | `/home/codex/onyx-lab/src/deployment/docker_compose` |
| 实际使用的 compose 文件 | `docker-compose.yml` + `docker-compose.lab.yml`（由容器 label 确认） |
| 环境文件 | 同目录 `.env`（含密钥，**不要读出内容，也不要写进任何报告**） |
| tier | community（`ee_features_enabled=false`） |
| GPU | `gpu_enabled=true`（embedding 走 GPU） |

## 4. 访问入口与端口

| 入口 | 地址 | 说明 |
|---|---|---|
| WSL 本机 API/UI | `http://127.0.0.1:8080` | 容器内 nginx 统一入口（host 只发布 8080） |
| 局域网 | `http://192.168.5.237:8080` | 同一 Wi-Fi 下的 Mac 可直接打开 |
| 公网 | `https://corln.rana.asia` | **当前不可用**（Cloudflare 526，外部阻断，与本机部署无关） |

Postgres / OpenSearch / Redis **未对外发布端口**，只在 Docker 网络内互访——排障请在容器内执行，不要在 host 上找 5432/9200。

## 5. 健康检查（可直接复制）

```bash
# 容器状态
docker ps --format '{{.Names}}\t{{.Status}}'

# API 健康（期望 200）
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/api/health

# 当前档位与 GPU 开关
./bin/onyx-api.sh GET /api/settings | head -c 400
```

最近一次实测结果：9 个容器 Up（其中 api / web / inference / indexing / relational_db / nginx 报 healthy），`/api/health` 返回 **200**。

## 6. 凭据与会话

- 管理员账号已创建，拥有完整 `effective_permissions`（已验证 `/api/me`、`/api/settings`）。
- **密钥不能放在 `/mnt/d` 下**：实测 `/mnt/d` 是 9p/drvfs 挂载（Windows D 盘），`chmod` 返回 "Operation not permitted"，**POSIX 权限不生效**，任何 Windows 进程或用户在 D 盘上都能读到。放在那里等于没有保护。
- 约定位置（WSL 原生文件系统，权限可用）：

  ```
  /home/fisher/.onyx-lab/.secrets/admin-cookies.txt    # chmod 600
  ```

  包装脚本默认从这个路径读；也可用环境变量 `ONYX_COOKIE_FILE` 覆盖。
- 旧位置 `/srv/onyx-lab/.secrets/admin-cookies.txt` 仍然存在，但 `/srv/onyx-lab` 对 `codex` 用户不可读（需 root）。**请 `fisher` 自行确认一次**：若可读且未过期，用 `cp` 复制到上面新位置并 `chmod 600`；不可读或已过期就重新登录生成。
- 任何报告、evidence、日志里**不得出现 Cookie / token / 密码原文**，需要时用 `<REDACTED>`。
- `onyx-lab/.gitignore` 已排除 `.secrets/`，作为第二道保险。

## 7. 运维命令（给人看，不是给 agent 自动执行）

```bash
cd /home/codex/onyx-lab/src/deployment/docker_compose
docker compose -f docker-compose.yml -f docker-compose.lab.yml ps
docker compose -f docker-compose.yml -f docker-compose.lab.yml logs -f api_server
```

> agent 硬约束：**未经任务书明确授权，不得 restart / stop / down / rm 任何容器，也不得修改 compose 与 `.env`**。

## 8. 已知问题

| # | 问题 | 影响 | 处理 |
|---|---|---|---|
| 1 | 公网 `corln.rana.asia` 返回 Cloudflare 526 | 客户无法远程访问演示 | 外部阻断，另案处理；本刀验收用局域网/本机 smoke |
| 2 | 内存余量曾低至 1.3 GiB，**swap 一度 100% 占满**（2026-09-24 上午） | 大文件索引、并发检索有 OOM 风险 | 已加 `/swapfile-ece` 8GB 作缓冲（§9）；配额提到 14GB 待重启生效；索引前后采集诊断 |
| 3 | `nvidia-smi` 在部分用户 shell 不在 PATH | 无法直接看 GPU 状态 | 用 `/usr/lib/wsl/lib/nvidia-smi`，或 `docker run --rm --gpus all …` 验证 |
| 4 | ONYX 各服务未全部带 healthcheck（background/cache/opensearch 无 healthy 标记） | 不易一眼判断是否卡死 | 以 API 200 + 索引任务是否完成作为主判据 |

## 9. 资源事件与运维记录（2026-09-24）

### 9.1 发生了什么

OEI-002 引入本地 LLM（ollama + Qwen2.5:3b）后，整机footprint 变成"9 个 Onyx 容器（约 7.5 GiB）+ llama-server（约 2.5 GiB）"，而 WSL 上限只有 12GB（实际可见 11.7GiB）。到当日中午：

```
Mem:  total 11Gi, used 9.7Gi, available 1.5Gi
Swap: total 8.0Gi, used 8.0Gi, free 17Mi   ← 100% 占满
```

占用者全是自有栈，无外部进程：`llama-server` 2.46GB、OpenSearch JVM 2.10GB、两个 `model_server` 各 1.78GB。

### 9.2 两处处置

**① 已生效：新增 8GB swap 文件**（用户执行）

```bash
sudo fallocate -l 8G /swapfile-ece && sudo chmod 600 /swapfile-ece
sudo mkswap /swapfile-ece && sudo swapon /swapfile-ece
echo '/swapfile-ece none swap sw 0 0' | sudo tee -a /etc/fstab
```

结果：`Swap: total 15Gi, used 8.0Gi, free 8.0Gi`。注意**老分区里已换出的 8GB 不会自动搬回**，新文件是干净的缓冲——目的是把"swap 耗尽"这个悬崖填掉。swap 文件必须放 WSL 原生 ext4，**绝不可放 `/mnt/d`**（9p 挂载不支持可靠 swap）。

**② 待重启生效：`.wslconfig` 内存配额 12GB → 14GB**（codex 改，2026-09-24 16:0x）

- 备份：`onyx-lab/.wslconfig.bak-2026-09-24.txt`（md5 `5c15c1dc…`）
- 宿主机物理 16GB，故取 14GB 而非 16GB（要给 Windows 留 ~2GB）
- **必须 `wsl --shutdown` 才生效**；重启后可见 `MemTotal` 应约 13.7GiB

### 9.3 ⚠️ 不要做的事

**不要在当前状态下跑 `sudo swapoff -a && swapon -a`。** 该命令要求把已换出的 8GB 全部搬回物理内存，而当时可用内存仅 1.5GiB（即便丢掉 1.8GiB page cache 也只有约 3.3GiB）→ 结果是大规模换页抖动并触发 OOM killer，最可能被杀死的正是 llama-server / OpenSearch。要清 swap，**正确做法是重启 WSL**（`wsl --shutdown`，swap 会随 VM 一起重置），而不是 swapoff。

### 9.4 重启 WSL 后的预期（已核实）

- Docker 是 **WSL 内原生 systemd 服务**（`systemctl is-active docker` = active，socket `/var/run/docker.sock`），非 Docker Desktop 集成
- 9 个 Onyx 容器重启策略均为 **`unless-stopped`** → dockerd 起来后**容器自动恢复**，不需要手动 `docker compose up`
- `ollama` 也是 systemd 服务 → 自动恢复；模型首次查询会冷启动（30–60s）
- 重启命令（Windows 侧）：`wsl --shutdown`；之后打开任意 WSL 终端或运行 `wsl -d <distro>` 即会重新拉起
