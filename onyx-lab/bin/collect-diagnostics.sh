#!/usr/bin/env bash
# 采集固定范围的资源与容器诊断（无参数、无副作用、不读密钥）。
# 用法: collect-diagnostics.sh [输出文件]
set -euo pipefail

OUT="${1:-/dev/stdout}"

{
  echo "# collected_at: $(date -Iseconds)"
  echo
  echo "## uname"
  uname -a
  echo
  echo "## memory"
  free -h
  echo
  echo "## disk"
  df -h / /mnt/d 2>/dev/null || df -h /
  echo
  echo "## containers"
  docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'
  echo
  echo "## container stats (no-stream)"
  docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}'
  echo
  echo "## api health"
  curl -s -o /dev/null -w 'http_status=%{http_code}\n' http://127.0.0.1:8080/api/health || echo "health check failed"
  echo
  echo "## gpu (best effort)"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader
  elif [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
    /usr/lib/wsl/lib/nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader
  else
    docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi \
      --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null \
      || echo "gpu info unavailable"
  fi
} > "$OUT"

if [[ "$OUT" != "/dev/stdout" ]]; then
  echo "wrote $OUT"
fi
