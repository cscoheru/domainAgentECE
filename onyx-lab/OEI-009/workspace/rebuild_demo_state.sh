#!/usr/bin/env bash
# OEI-009 — rebuild the demo state from nothing, in one command.
#
# Why this exists (codex VERDICT #2 §8.4): the "alice sees 4 / anonymous sees 3"
# demo state lives in the THROWAWAY Postgres, and LOCAL-AGENT-PROTOCOL §5.1
# forbids leaving temp PG containers around. So the state is deliberately
# ephemeral — which only works if it can be rebuilt deterministically. This is
# that command.
#
# What it does:
#   1. (re)creates a FRESH temp Postgres (pgvector/pgvector:pg16) — any previous
#      container of the same name is removed first, so this is a true rebuild.
#   2. waits for readiness.
#   3. alembic upgrade head           → engine_documents + all prior migrations.
#   4. backfill_demo_docs.py          → register the 3 historical demo docs
#                                       (whitelist: exactly those three).
#   5. step26_demo_falsifiable.py     → the sanctioned restricted comparison doc
#                                       + its ACL row, then the A4 matrix probe.
#   6. step33_timebox_e2e.py          → expire / restore the ACL window.
#
# Usage:
#   bash rebuild_demo_state.sh                 # rebuild, print output
#   bash rebuild_demo_state.sh <evidence_dir>  # rebuild, also tee into evidence
#
# Leak/teardown: this script does NOT stop the PG. Release it yourself when the
# demo is over (LOCAL-AGENT-PROTOCOL §5.1):
#   docker stop ece-pg-oei009r1 && docker rm ece-pg-oei009r1
set -euo pipefail

PG_NAME="${PG_NAME:-ece-pg-oei009r1}"
PG_PORT="${PG_PORT:-55432}"
PG_IMAGE="${PG_IMAGE:-pgvector/pgvector:pg16}"
ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE="${1:-}"

echo "== OEI-009 rebuild_demo_state: PG=$PG_NAME port=$PG_PORT evidence=${EVIDENCE:-<none>}"

# 1. fresh Postgres ------------------------------------------------------------
docker rm -f "$PG_NAME" >/dev/null 2>&1 || true
docker run -d --name "$PG_NAME" \
  -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece \
  -p "127.0.0.1:${PG_PORT}:5432" \
  "$PG_IMAGE" >/dev/null

# 2. readiness ----------------------------------------------------------------
echo -n "   waiting for Postgres"
for _ in $(seq 1 60); do
  if docker exec "$PG_NAME" pg_isready -U ece -d ece >/dev/null 2>&1; then
    echo " — ready"; break
  fi
  echo -n "."
  sleep 1
done
docker exec "$PG_NAME" pg_isready -U ece -d ece >/dev/null

export DATABASE_URL="postgresql+psycopg://ece:ece@127.0.0.1:${PG_PORT}/ece"
export ECE_CONTENT_ENGINE="${ECE_CONTENT_ENGINE:-onyx}"

# Helper: run a command in a given cwd, optionally teeing into an evidence file.
step() {  # step <cwd> <evidence-filename|-> <command...>
  local cwd="$1"; shift
  local out="$1"; shift
  echo
  echo "==> (cwd=$cwd) $*"
  if [ -n "$EVIDENCE" ] && [ "$out" != "-" ]; then
    ( cd "$cwd" && "$@" ) 2>&1 | tee "$EVIDENCE/$out"
  else
    ( cd "$cwd" && "$@" )
  fi
}

# 3. migrations ---------------------------------------------------------------
# NOTE: alembic.ini uses a RELATIVE script_location (src/ece/migrations), so this
# must run with cwd = the ECE repo root.
step "$ECE_DIR" - uv run --project "$ECE_DIR" alembic -c src/ece/migrations/alembic.ini upgrade head

# 4. backfill the 3 historical demo docs --------------------------------------
step "$WS_DIR" 04-backfill-demo-docs.json uv run --project "$ECE_DIR" python backfill_demo_docs.py

# 5. restricted comparison doc + ACL + A4 matrix ------------------------------
step "$WS_DIR" 05-per-result-filter-matrix.json uv run --project "$ECE_DIR" python step26_demo_falsifiable.py

# 6. timebox e2e --------------------------------------------------------------
step "$WS_DIR" 08-timebox-acl.json uv run --project "$ECE_DIR" python step33_timebox_e2e.py

echo
echo "== demo state rebuilt. Release the temp PG when done:"
echo "   docker stop $PG_NAME && docker rm $PG_NAME"
