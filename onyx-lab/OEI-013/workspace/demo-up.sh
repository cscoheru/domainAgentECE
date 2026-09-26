#!/usr/bin/env bash
# OEI-013 — bring up the resident consulting demo in one command.
#
#   bash onyx-lab/OEI-013/workspace/demo-up.sh
#
# Chain:  PG → alembic migrate → seed → backfill 3 demo docs → uvicorn:8765
#         → same-origin server :8181  → warm-up recall → print browser URL
#
# ── Idempotent by design ────────────────────────────────────────────────────
# Re-running this script must NOT start a second copy of anything. Every step
# is guarded:
#   * PG      : reused if the container exists (started if merely stopped)
#   * migrate : `alembic upgrade head` is a no-op once at head
#   * seed    : `ece.seed` is idempotent (reports created=0)
#   * backfill: `backfill_demo_docs.py` asserts idempotency itself
#   * uvicorn : skipped if something already answers on 8765
#   * origin  : skipped if something already answers on 8181
# Guards are liveness probes (a TCP connect), not just pidfile checks — a stale
# pidfile must not be able to make this script lie about the chain being up.
#
# ── The removal decision (user, 2026-09-26) ─────────────────────────────────
# This chain deliberately does NOT run OEI-009's `step26_demo_falsifiable.py`,
# which is the script that *creates* the controlled comparison document
# `ece-df16d19c9e7b-oei009-comparison-restricted.md` in Onyx project 1.
#
# Two consequences, both intended:
#   1. Starting this chain never (re)creates that document. (TASK A2's
#      "起链不复建" — satisfied.)
#   2. That document has no row in this chain's `engine_documents` registry, so
#      the OEI-009 per-result filter hides it FAIL-CLOSED (`no_registry`) and it
#      never reaches the browser. The demo's engine group is therefore clean at
#      the product layer even though the document still exists in Onyx.
#      The user chose "先不删，只做只读取证", so nothing is deleted from Onyx.
#
# ── Stop / clean ────────────────────────────────────────────────────────────
#   bash onyx-lab/OEI-013/workspace/demo-down.sh          # stop api+origin
#   bash onyx-lab/OEI-013/workspace/demo-down.sh --all    # + drop the demo PG
#
# Set DEMO_REBUILD_PG=1 to force a fresh PG (true rebuild).
set -euo pipefail

# ---- config -----------------------------------------------------------------
ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OEY_DIR="$(cd "$WS_DIR/../.." && pwd)"          # onyx-lab/
RUN_DIR="${RUN_DIR:-/tmp/oei013-demo}"

PG_NAME="${PG_NAME:-ece-pg-demo}"
PG_PORT="${PG_PORT:-55433}"
PG_IMAGE="${PG_IMAGE:-pgvector/pgvector:pg16}"

API_PORT="${API_PORT:-8765}"
ORIGIN_PORT="${ORIGIN_PORT:-8181}"

COOKIE_FILE="${ECE_ONYX_COOKIE_FILE:-/home/fisher/.onyx-lab/.secrets/admin-cookies.txt}"
ONYX_BASE="${ECE_ONYX_BASE:-http://127.0.0.1:8080}"

# OEI-006 lesson: without no_proxy, the WSL HTTP proxy intercepts 127.0.0.1 and
# turns every same-origin call into a 502. Set it for this shell and everything
# it spawns, before any network step runs.
export no_proxy="127.0.0.1,localhost,::1"
export NO_PROXY="$no_proxy"

export DATABASE_URL="postgresql+psycopg://ece:ece@127.0.0.1:${PG_PORT}/ece"
export ECE_CONTENT_ENGINE="${ECE_CONTENT_ENGINE:-onyx}"
export ECE_ONYX_BASE="$ONYX_BASE"
export ECE_ONYX_COOKIE_FILE="$COOKIE_FILE"

# Which recall mode the Library API runs in (docs/API.md §10).
#
# OEI-013 measured BOTH modes at the product layer (evidence/03*.json) and the
# answer was not the one the task expected, so it is worth stating plainly:
#
#                     hit@3 (rewrite path)   engine group empty   raw reproducibility
#   default (expansion on)      80.0%              1/5                 0.917
#   deterministic (expansion off) 0.0%              5/5                 1.000
#
# The deterministic path IS more reproducible, and it IS ~3x faster. But it
# returns a narrower candidate set, and on this corpus the single hit it returns
# for these queries is the controlled comparison document — which the permission
# filter then hides. The user gets an EMPTY engine group where the default mode
# showed a real document. Trading 80% -> 0% recall for reproducibility is not a
# trade a demo should make, so the default here is OFF.
#
# Override with ECE_LIBRARY_SKIP_QUERY_EXPANSION=1|0 to force either mode.
export ECE_LIBRARY_SKIP_QUERY_EXPANSION="${ECE_LIBRARY_SKIP_QUERY_EXPANSION:-0}"

mkdir -p "$RUN_DIR"

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()  { printf '   \033[32m✓\033[0m %s\n' "$*"; }
sk()  { printf '   \033[33m•\033[0m %s\n' "$*"; }

# Liveness probe: is anything accepting TCP on this port? Uses a real connect,
# so a leftover pidfile can never make us skip a genuinely-dead service.
listening() {  # listening <port>
  python3 - "$1" <<'PY'
import socket, sys
s = socket.socket()
s.settimeout(0.5)
try:
    s.connect(("127.0.0.1", int(sys.argv[1])))
    print("yes")
except OSError:
    print("no")
finally:
    s.close()
PY
}

say "OEI-013 demo-up — $RUN_DIR"
echo "   PG=${PG_NAME}:${PG_PORT}  API=:${API_PORT}  ORIGIN=:${ORIGIN_PORT}"
echo "   no_proxy=$no_proxy"

# ---- 1. Postgres ------------------------------------------------------------
say "1/7 Postgres ($PG_NAME :$PG_PORT)"
if [ "${DEMO_REBUILD_PG:-0}" = "1" ] && docker inspect "$PG_NAME" >/dev/null 2>&1; then
  sk "DEMO_REBUILD_PG=1 → removing existing $PG_NAME"
  docker rm -f "$PG_NAME" >/dev/null
fi

if docker inspect "$PG_NAME" >/dev/null 2>&1; then
  running="$(docker inspect -f '{{.State.Running}}' "$PG_NAME")"
  if [ "$running" = "true" ]; then
    sk "container $PG_NAME already running — reusing"
  else
    sk "container $PG_NAME exists but stopped — starting"
    docker start "$PG_NAME" >/dev/null
  fi
else
  sk "creating $PG_NAME from $PG_IMAGE"
  docker run -d --name "$PG_NAME" \
    -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece \
    -p "127.0.0.1:${PG_PORT}:5432" \
    "$PG_IMAGE" >/dev/null
fi

printf '   waiting for Postgres'
for _ in $(seq 1 60); do
  if docker exec "$PG_NAME" pg_isready -U ece -d ece >/dev/null 2>&1; then
    printf ' — ready\n'; break
  fi
  printf '.'; sleep 1
done

# The official Postgres image runs a TEMPORARY server during initdb, then shuts
# it down and execs the real one. `pg_isready` can therefore succeed against the
# temp server and fail microseconds later against the real one — a first run on
# a fresh volume hit exactly that race. So: confirm readiness with a short
# retry loop, not a single probe. A genuinely dead Postgres still fails, just
# after ~30 s instead of instantly.
ready=0
for _ in $(seq 1 30); do
  if docker exec "$PG_NAME" pg_isready -U ece -d ece >/dev/null 2>&1; then ready=1; break; fi
  sleep 1
done
[ "$ready" = "1" ] || { echo "Postgres never became ready"; exit 1; }

# Distinguish "accepting connections" from "accepting connections AND has our
# database" — pg_isready alone does not prove the `ece` DB exists yet.
for _ in $(seq 1 30); do
  if docker exec "$PG_NAME" psql -U ece -d ece -tAc 'select 1' >/dev/null 2>&1; then break; fi
  sleep 1
done
docker exec "$PG_NAME" psql -U ece -d ece -tAc 'select 1' >/dev/null
ok "Postgres reachable on 127.0.0.1:$PG_PORT (db 'ece' accepts queries)"

# ---- 2. Migrate -------------------------------------------------------------
say "2/7 alembic upgrade head"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" alembic \
    -c src/ece/migrations/alembic.ini upgrade head ) | tail -3
ok "schema at head"

# ---- 3. Seed ----------------------------------------------------------------
say "3/7 seed (idempotent)"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" python -m ece.seed ) | tail -3
ok "seed done"

# ---- 4. Backfill the 3 demo docs -------------------------------------------
say "4/7 backfill registry (3 whitelisted demo docs, no comparison doc)"
( cd "$OEY_DIR/OEI-009/workspace" && uv run --project "$ECE_DIR" python backfill_demo_docs.py ) \
  | grep -E 'onyx reports|will register|skipped|engine_documents now|second run|PASS|FAIL'
ok "registry backfilled (idempotency self-check passed above)"

# ---- 5. uvicorn -------------------------------------------------------------
say "5/7 uvicorn :$API_PORT"
if [ "$(listening "$API_PORT")" = "yes" ]; then
  sk "port $API_PORT already answers — not starting a second API"
else
  # Launch the venv's python DIRECTLY rather than through `uv run`.
  # `uv run` forks a child, so a pidfile holding `uv run`'s pid cannot stop the
  # server — killing it leaves the child holding the port. (That exact bug made
  # a mode-switch restart silently keep serving the OLD process.) With the venv
  # interpreter the pidfile pid IS the server.
  VENV_PY="$ECE_DIR/.venv/bin/python"
  if [ -x "$VENV_PY" ]; then
    LAUNCH=( "$VENV_PY" -m uvicorn )
  else
    sk "no $VENV_PY — falling back to 'uv run' (pidfile will hold the wrapper)"
    LAUNCH=( uv run --project "$ECE_DIR" uvicorn )
  fi
  ( cd "$ECE_DIR" && nohup "${LAUNCH[@]}" ece.main:app \
      --host 127.0.0.1 --port "$API_PORT" \
      >"$RUN_DIR/uvicorn.log" 2>&1 & echo $! >"$RUN_DIR/uvicorn.pid" )
  for _ in $(seq 1 60); do
    [ "$(listening "$API_PORT")" = "yes" ] && break
    sleep 0.5
  done
  [ "$(listening "$API_PORT")" = "yes" ] || { echo "API failed to start; see $RUN_DIR/uvicorn.log"; exit 1; }
  ok "started (pid $(cat "$RUN_DIR/uvicorn.pid")), log $RUN_DIR/uvicorn.log"
fi

# ---- 6. Same-origin server --------------------------------------------------
say "6/7 same-origin server :$ORIGIN_PORT"
if [ "$(listening "$ORIGIN_PORT")" = "yes" ]; then
  sk "port $ORIGIN_PORT already answers — not starting a second origin"
else
  nohup python3 "$WS_DIR/demo_origin.py" --port "$ORIGIN_PORT" \
      --upstream "http://127.0.0.1:${API_PORT}" \
      >"$RUN_DIR/origin.log" 2>&1 & echo $! >"$RUN_DIR/origin.pid"
  for _ in $(seq 1 40); do
    [ "$(listening "$ORIGIN_PORT")" = "yes" ] && break
    sleep 0.25
  done
  [ "$(listening "$ORIGIN_PORT")" = "yes" ] || { echo "origin failed to start; see $RUN_DIR/origin.log"; exit 1; }
  ok "started (pid $(cat "$RUN_DIR/origin.pid")), log $RUN_DIR/origin.log"
fi

# ---- 7. Warm-up + self-check ------------------------------------------------
# Pay the engine's cold-start cost here rather than on the presenter's first
# click. Also proves, from the demo's own origin, that the whole chain answers.
say "7/7 warm-up + self-check (via the same origin the browser will use)"
BASE="http://127.0.0.1:${ORIGIN_PORT}"

code_index="$(curl -s -o /dev/null -w '%{http_code}' "$BASE/index.html")"
code_health="$(curl -s -o /dev/null -w '%{http_code}' "$BASE/healthz")"
ok "GET /index.html  → $code_index"
ok "GET /healthz     → $code_health"

warm_q="%%E4%%B8%%9A%%E5%%8A%%A1%%E6%%88%%98%%E7%%95%%A5%%E8%%AF%%8A%%E6%%96%%AD"   # 业务战略诊断
t0=$(date +%s)
warm="$(curl -s --max-time 180 "$BASE/api/v1/consulting/library?q=${warm_q}" \
        | python3 -c 'import json,sys
try:
    b=json.load(sys.stdin)
except Exception:
    print("unparseable"); raise SystemExit
print("total=%s engine_status=%s engine_items=%s"
      % (b.get("total"), b.get("engine_status"),
         len(b.get("engine_items") or [])))' 2>&1 || echo "warm-up failed")"
t1=$(date +%s)
ok "warm-up recall (${t1}s - ${t0}s = $((t1-t0))s): $warm"

# The user-visible deliverable: a URL a human opens.
cat <<EOF

────────────────────────────────────────────────────────────────────────
 演示已就绪 / DEMO IS UP — 打开浏览器:

     http://127.0.0.1:${ORIGIN_PORT}/index.html     ← 咨询演示 (视图 D)

 本机 API :  http://127.0.0.1:${API_PORT}
 起点日志 :  ${RUN_DIR}/
 停止     :  bash ${WS_DIR}/demo-down.sh
 连带清库 :  bash ${WS_DIR}/demo-down.sh --all
────────────────────────────────────────────────────────────────────────
EOF
