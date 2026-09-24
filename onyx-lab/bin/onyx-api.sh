#!/usr/bin/env bash
# 受限 Onyx API 包装：只允许打本机 127.0.0.1:8080 的 /api/* 路径。
# 用法:
#   onyx-api.sh GET  /api/settings
#   onyx-api.sh GET  /api/user/projects
#   onyx-api.sh POST /api/search --data '{"query":"问题树怎么用"}'
#   onyx-api.sh POST /api/user/projects/file/statuses --data '{"file_ids":["<uuid>"]}'
# Cookie 从 ~/.onyx-lab/.secrets/admin-cookies.txt 读取（可用 ONYX_COOKIE_FILE 覆盖），绝不打印其内容。
# 注意: 本部署 /openapi.json 与 /docs 均返回 404（ENABLE_PUBLIC_DOCS 关闭）；需要核对路由用：
#   docker exec onyx-api_server-1 python -c "from onyx.main import app; s=app().openapi(); [print(p) for p in sorted(s['paths'])]"
set -euo pipefail

BASE="http://127.0.0.1:8080"
# Cookie 必须在 WSL 原生文件系统（/mnt/d 是 Windows 盘，chmod 不生效）
COOKIE_FILE="${ONYX_COOKIE_FILE:-$HOME/.onyx-lab/.secrets/admin-cookies.txt}"

usage() {
  echo "usage: $(basename "$0") <GET|POST|PUT|PATCH|DELETE> </api/...path> [curl args...]" >&2
  exit 2
}

[[ $# -ge 2 ]] || usage

METHOD="${1^^}"
PATH_ARG="$2"
shift 2

case "$METHOD" in
  GET|POST|PUT|PATCH|DELETE) ;;
  *) echo "refusing: method '$METHOD' not allowed" >&2; exit 2 ;;
esac

case "$PATH_ARG" in
  /api/*) ;;
  *) echo "refusing: path must start with /api/ (got '$PATH_ARG')" >&2; exit 2 ;;
esac

case "$PATH_ARG" in
  *..*) echo "refusing: path traversal" >&2; exit 2 ;;
esac

[[ -r "$COOKIE_FILE" ]] || {
  echo "cookie file not readable: $COOKIE_FILE" >&2
  echo "按 OEI-001/TASK.md §2 生成会话 Cookie（chmod 600，勿放 /mnt/d），再重试。" >&2
  exit 3
}

curl --silent --show-error --fail-with-body \
  --cookie "$COOKIE_FILE" \
  --header 'Accept: application/json' \
  --request "$METHOD" \
  "$@" \
  "${BASE}${PATH_ARG}"
