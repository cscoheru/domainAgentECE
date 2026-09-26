#!/usr/bin/env bash
# OEI-010 step 3 (A3) — migration 0010: upgrade, constraint probes, round trip.
#
# A3 wants four things: the upgrade output, a REAL unique-violation with the
# constraint name quoted from the database, a schema re-check, and one
# downgrade -> upgrade round trip. The round trip is not ceremony: CI
# (.github/workflows/ci.yml) runs `downgrade base` then `upgrade head`, so a
# `downgrade()` that does not actually drop the table turns CI red.
#
# Usage:  bash step3_memory_migration.sh > <evidence>/03-memory-migration.txt
set -euo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALEMBIC="uv run alembic -c src/ece/migrations/alembic.ini"
cd "$ECE_DIR"

echo "== OEI-010 step 3 (A3) — memories migration 0010 =="
echo "date: $(date -Iseconds)"
echo "DATABASE_URL: ${DATABASE_URL:-<unset>}"
echo

echo "---- 1. current revision BEFORE ----"
$ALEMBIC current 2>&1 | grep -v '^INFO' || true
echo

echo "---- 2. upgrade head (idempotent when already at 0010) ----"
$ALEMBIC upgrade head 2>&1
echo

echo "---- 3. live schema + constraint probes ----"
uv run python "$WS_DIR/step3_schema_probe.py"
echo

echo "---- 4. downgrade -1 (must DROP the table) ----"
$ALEMBIC downgrade -1 2>&1
echo "-- table present after downgrade? (expect 0) --"
docker exec ece-pg-oei010 psql -U ece -d ece -tAc \
  "SELECT count(*) FROM information_schema.tables WHERE table_name='memories'"
echo

echo "---- 5. upgrade head again (round trip) ----"
$ALEMBIC upgrade head 2>&1
echo "-- table present after re-upgrade? (expect 1) --"
docker exec ece-pg-oei010 psql -U ece -d ece -tAc \
  "SELECT count(*) FROM information_schema.tables WHERE table_name='memories'"
echo "-- constraints intact after the round trip --"
docker exec ece-pg-oei010 psql -U ece -d ece -tAc \
  "SELECT conname FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid WHERE t.relname='memories' ORDER BY conname"
echo "-- index count after the round trip --"
docker exec ece-pg-oei010 psql -U ece -d ece -tAc \
  "SELECT count(*) FROM pg_indexes WHERE tablename='memories'"
echo

echo "---- 6. current revision AFTER ----"
$ALEMBIC current 2>&1 | grep -v '^INFO' || true
echo
echo "---- done ----"
