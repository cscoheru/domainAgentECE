#!/usr/bin/env bash
# OEI-013 — the EVAL Postgres: a throwaway PG for the test suite runs.
#
# Why a second PG instead of the demo one: the suite's integration tests write to
# `engine_documents` and other registry tables. Pointing them at the resident
# demo's PG would let a test mutate the state the user is about to be shown.
# The demo chain is a deliverable (TASK §8); the test PG is scratch (A11: release
# it at the end). Keeping them apart is what makes both statements true at once.
#
# Port 55432 is deliberately different from the demo's 55433.
set -euo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
PG_NAME="${PG_NAME:-ece-pg-oei013-eval}"
PG_PORT="${PG_PORT:-55432}"
PG_IMAGE="${PG_IMAGE:-pgvector/pgvector:pg16}"

export no_proxy="127.0.0.1,localhost,::1"
export NO_PROXY="$no_proxy"

echo "== OEI-013 eval PG: $PG_NAME on :$PG_PORT (fresh)"

docker rm -f "$PG_NAME" >/dev/null 2>&1 || true
docker run -d --name "$PG_NAME" \
  -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece \
  -p "127.0.0.1:${PG_PORT}:5432" "$PG_IMAGE" >/dev/null

# Same initdb-temp-server race as demo-up.sh — confirm with retries and with a
# real query, not a single pg_isready.
for _ in $(seq 1 60); do
  docker exec "$PG_NAME" pg_isready -U ece -d ece >/dev/null 2>&1 && break
  sleep 1
done
ready=0
for _ in $(seq 1 30); do
  docker exec "$PG_NAME" psql -U ece -d ece -tAc 'select 1' >/dev/null 2>&1 && { ready=1; break; }
  sleep 1
done
[ "$ready" = "1" ] || { echo "eval PG never became ready"; exit 1; }
echo "   ✓ Postgres up"

export DATABASE_URL="postgresql+psycopg://ece:ece@127.0.0.1:${PG_PORT}/ece"

echo "== alembic upgrade head"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" alembic \
    -c src/ece/migrations/alembic.ini upgrade head ) 2>&1 | tail -2

echo "== gen-dataset"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" python scripts/gen_dataset.py \
    --out data/dataset/demo.json ) 2>&1 | tail -2

echo "== seed"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" python -m ece.seed ) 2>&1 | tail -2

echo "== seed-fixtures (temporal / knowledge / compliance / spike)"
( cd "$ECE_DIR" && for s in seed_temporal_roles seed_knowledge_fixture \
      seed_compliance_fixture seed_v0_spike_fixture; do
    echo "   - $s"; uv run --project "$ECE_DIR" python "scripts/$s.py" 2>&1 | tail -2
  done )

echo
echo "== eval PG ready: DATABASE_URL=$DATABASE_URL"
echo "   release with: docker rm -f $PG_NAME"
