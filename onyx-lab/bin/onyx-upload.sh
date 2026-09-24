#!/usr/bin/env bash
# 受限上传包装：只允许上传 onyx-lab/ 工作区内的文件，且只打本机 API。
# 用法:
#   onyx-upload.sh <file> <project_id> [endpoint_path]
# 默认端点：POST /api/user/projects/file/upload
#   （codex 于 2026-09-23 在本机只读反查确认；不是 /api/management/... 那条）
#   · 文件字段名必须是 files（本机 API 契约，不是 file）
#   · project_id 为整数（用户项目 id）
# 本部署 /openapi.json 与 /docs 均返回 404（ENABLE_PUBLIC_DOCS 关闭），
# 需要核对路由时用只读命令：
#   docker exec onyx-api_server-1 python -c \
#     "from onyx.main import app; s=app().openapi(); [print(p) for p in sorted(s['paths'])]"
#
# 变更记录
#   v2 2026-09-23 codex: 默认端点由 /api/management/admin/connector/file/upload
#     改为 /api/user/projects/file/upload；表单字段 file -> files；新增 project_id 整数校验。
set -euo pipefail

BASE="http://127.0.0.1:8080"
LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Cookie 必须在 WSL 原生文件系统（/mnt/d 是 Windows 盘，chmod 不生效）
COOKIE_FILE="${ONYX_COOKIE_FILE:-$HOME/.onyx-lab/.secrets/admin-cookies.txt}"

DEFAULT_ENDPOINT="/api/user/projects/file/upload"

usage() {
  echo "usage: $(basename "$0") <file> <project_id> [endpoint_path]" >&2
  exit 2
}

[[ $# -ge 2 ]] || usage

FILE="$1"
PROJECT_ID="$2"
ENDPOINT="${3:-$DEFAULT_ENDPOINT}"

case "$PROJECT_ID" in
  ''|*[!0-9]*) echo "refusing: project_id must be an integer (got '$PROJECT_ID')" >&2; exit 2 ;;
esac

case "$ENDPOINT" in
  /api/*) ;;
  *) echo "refusing: endpoint must start with /api/" >&2; exit 2 ;;
esac

[[ -f "$FILE" ]] || { echo "not a file: $FILE" >&2; exit 2; }

# 解析真实路径，确保落在 onyx-lab 工作区内
REAL_FILE="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
case "$REAL_FILE" in
  "$LAB_ROOT"/*) ;;
  *) echo "refusing: only files under $LAB_ROOT may be uploaded (got $REAL_FILE)" >&2; exit 2 ;;
esac

[[ -r "$COOKIE_FILE" ]] || { echo "cookie file not readable: $COOKIE_FILE" >&2; exit 3; }

curl --silent --show-error --fail-with-body \
  --cookie "$COOKIE_FILE" \
  --form "files=@${REAL_FILE}" \
  --form "project_id=${PROJECT_ID}" \
  "${BASE}${ENDPOINT}"
