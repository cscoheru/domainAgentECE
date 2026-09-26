#!/usr/bin/env bash
# OEI-013 — stop the resident consulting demo.
#
#   bash demo-down.sh          # stop api + origin (leaves the demo PG running)
#   bash demo-down.sh --all    # also drop the demo PG container
#
# Why PG is not dropped by default: the demo is meant to stay resident between
# showings, and the seeded state is cheap to keep but slower to rebuild. Use
# `--all` for a clean slate, or `demo-up.sh` with `DEMO_REBUILD_PG=1`.
#
# Note: this never touches the Onyx stack (9 containers) or the host's Onyx
# data — only this cut's own PG container, API process and origin process.
set -euo pipefail

RUN_DIR="${RUN_DIR:-/tmp/oei013-demo}"
PG_NAME="${PG_NAME:-ece-pg-demo}"
API_PORT="${API_PORT:-8765}"
ORIGIN_PORT="${ORIGIN_PORT:-8181}"

say() { printf '\n== %s\n' "$*"; }

# Stop by pidfile, then SWEEP for survivors by inspecting /proc/<pid>/cmdline.
#
# The sweep exists because a pidfile can name the wrong process: `uv run` forks
# a child, so killing the recorded pid leaves the server holding the port. That
# happened during OEI-013 and silently kept the old process (and the old
# retrieval mode) serving after a "restart".
#
# Matching is done on cmdline contents + port, not on `pgrep <text>` — the same
# attribution discipline OEI-012 used, so an unrelated process that merely
# mentions the string cannot be killed by accident.
sweep() {  # sweep <label> <cmdline-needle> <port>
  local label="$1" needle="$2" port="$3"
  python3 - "$label" "$needle" "$port" <<'PY'
import os, signal, sys, time
label, needle, port = sys.argv[1], sys.argv[2], sys.argv[3]
me = os.getpid()
victims = []
for entry in os.listdir("/proc"):
    if not entry.isdigit():
        continue
    pid = int(entry)
    if pid == me:
        continue
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            cmdline = fh.read().replace(b"\x00", b" ").decode("utf-8", "replace")
    except OSError:
        continue
    if needle in cmdline and f"--port {port}" in cmdline:
        victims.append((pid, cmdline.strip()[:110]))
if not victims:
    print(f"   • no surviving {label} process for port {port}")
    raise SystemExit(0)
for pid, cmdline in victims:
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        continue
    for _ in range(20):
        try:
            os.kill(pid, 0)
        except OSError:
            break
        time.sleep(0.25)
    try:
        os.kill(pid, signal.SIGKILL)
        print(f"   ✓ SIGKILLed {label} pid={pid}  ({cmdline})")
    except OSError:
        print(f"   ✓ stopped {label} pid={pid}  ({cmdline})")
PY
}

stop_pidfile() {  # stop_pidfile <name>
  local f="$RUN_DIR/$1.pid"
  if [ ! -f "$f" ]; then
    echo "   • no pidfile for $1"
    return
  fi
  local pid; pid="$(cat "$f")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 20); do kill -0 "$pid" 2>/dev/null || break; sleep 0.25; done
    if kill -0 "$pid" 2>/dev/null; then
      echo "   $1 (pid $pid) did not exit — SIGKILL"; kill -9 "$pid" 2>/dev/null || true
    else
      echo "   ✓ stopped $1 (pid $pid)"
    fi
  else
    echo "   • $1 (pid $pid) already gone"
  fi
  rm -f "$f"
}

say "stopping demo processes from $RUN_DIR"
stop_pidfile origin
stop_pidfile uvicorn
sweep origin demo_origin.py "$ORIGIN_PORT"
sweep uvicorn "uvicorn ece.main:app" "$API_PORT"

if [ "${1:-}" = "--all" ]; then
  say "dropping demo PG ($PG_NAME)"
  if docker inspect "$PG_NAME" >/dev/null 2>&1; then
    docker rm -f "$PG_NAME" >/dev/null && echo "   ✓ removed $PG_NAME"
  else
    echo "   • no container named $PG_NAME"
  fi
  echo
  echo "   demo PG gone. Onyx stack untouched:"
  docker ps --filter 'name=onyx-' --format '     {{.Names}}  {{.Status}}'
else
  echo
  echo "   demo PG ($PG_NAME) left running — use --all to drop it."
fi
