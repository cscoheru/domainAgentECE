#!/usr/bin/env bash
# OEI-011 步骤 6.2 — the full suite on a FRESHLY created database.
#
# Why a fresh DB: the first full-suite run of this cut reported 48 failures, all
# in the three-domain integration tests, all complaining about missing fixture
# entities ("no entity with source_id='KM-POL-001'"). Cause: the documented setup
# chain has a fixture-seeding step (`make seed-fixtures`) that I had not run — the
# Makefile itself warns this costs 27 tests. To show the failures were a setup
# omission rather than a regression, the suite is re-run from a brand-new
# database through the FULL documented chain.
#
# `make seed-fixtures` is deliberately NOT used: its recipe contains an unescaped
# backtick pair in an `@echo` (`Now \`make test\` should reach baseline`), which the
# shell command-substitutes — so that target silently runs the entire suite as a
# side effect. Its four seeders are invoked directly instead; README.md:79 and the
# Makefile comment both state they are exactly equivalent to the target.
#
# Usage: bash fresh_db_chain.sh > <evidence>/12-test-suite-raw.txt 2>&1
set -uo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
PG_NAME="ece-pg-oei011"
PG_IMAGE="postgres:16-pgvector"
DSN="postgresql+psycopg://ece:ece@127.0.0.1:55432/ece"
cd "$ECE_DIR"
export DATABASE_URL="$DSN"
export ECE_CONTENT_ENGINE=mock

echo "== OEI-011 步骤 6.2 — 全套件，在【全新库】上，走完整文档化前置链 =="
echo "date: $(date -Iseconds)"
echo "cwd: $ECE_DIR"
echo "commit under test: $(git rev-parse HEAD)  ($(git log -1 --format=%s | cut -c1-60))"
echo "ECE_CONTENT_ENGINE = mock"
echo
echo "前置链（README.md / Makefile test-integration 记载的顺序）:"
echo "  docker run $PG_IMAGE                       (全新空库)"
echo "  alembic -c src/ece/migrations/alembic.ini upgrade head"
echo "  gen_dataset.py --out data/dataset/demo.json"
echo "  make seed                                   (采购三域 demo pack)"
echo "  seed_temporal_roles.py / seed_knowledge_fixture.py /"
echo "  seed_compliance_fixture.py / seed_v0_spike_fixture.py   (集成 fixture)"
echo "  pytest -m 'not eval and not eval_llm'       (= make test 的确切命令)"
echo
echo "NOTE: 'make seed-fixtures' 未使用 —— 它的 recipe 里 @echo 的反引号未转义，"
echo "      shell 会做命令替换，导致该 target **顺带把整套测试跑一遍**（预先存在的"
echo "      Makefile 缺陷，非本刀引入）。这里直接调它的四个 seeder，Makefile 注释与"
echo "      README.md:79 都写明两者等价。"
echo

echo "############ 0. 全新库 ############"
docker rm -f "$PG_NAME" >/dev/null 2>&1
docker run -d --name "$PG_NAME" -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece \
  -e POSTGRES_DB=ece -p 55432:5432 "$PG_IMAGE" >/dev/null
for i in $(seq 1 60); do
  docker exec "$PG_NAME" pg_isready -U ece >/dev/null 2>&1 && { echo "  ready after ${i}s"; break; }
  sleep 1
done
echo "  extensions available: $(docker exec "$PG_NAME" psql -U ece -tAc \
  "select string_agg(name,',') from pg_available_extensions where name in ('vector','pg_trgm')")"
echo

echo "############ 1. 迁移 ############"
uv run alembic -c src/ece/migrations/alembic.ini upgrade head 2>&1 | tail -4
echo "  head = $(uv run alembic -c src/ece/migrations/alembic.ini current 2>/dev/null | tail -1)"
echo

echo "############ 2. 数据集 + 种子 ############"
uv run python scripts/gen_dataset.py --out data/dataset/demo.json 2>&1 | tail -2
make seed 2>&1 | tail -4
echo

echo "############ 3. 集成 fixture（四个 seeder，逐个跑） ############"
for s in seed_temporal_roles seed_knowledge_fixture seed_compliance_fixture seed_v0_spike_fixture; do
  echo "--- $s.py ---"
  uv run python "scripts/$s.py" 2>&1 | tail -3
done
echo

echo "############ 4. 全套件（= make test 的确切命令 + -rs） ############"
echo "\$ uv run pytest -m \"not eval and not eval_llm\" -rs"
# Capture to a file first: `addopts` already supplies -q, and a pipe would let the
# warnings block push the summary line out of a `tail`.
# `-rs` (NOT another -q: addopts already has -q, a second one makes it -qq and
# suppresses the summary line) is added so every skip carries its REASON in this
# evidence file. An unexplained skip count is not evidence.
SUITE_LOG="/tmp/oei011/fresh-suite.txt"
uv run pytest -m "not eval and not eval_llm" -rs > "$SUITE_LOG" 2>&1
echo "  pytest exit code: $?"
echo "  raw log: $SUITE_LOG (kept outside the repo)"
echo
echo "--- 原始输出尾部 ---"
tail -30 "$SUITE_LOG"
echo
echo "--- 汇总行（不经管道，避免被 warnings 块挤掉）---"
grep -E "^[0-9]+ (passed|failed)|failed," "$SUITE_LOG" | tail -2
echo
echo "--- 每一条 skip 及其原因 ---"
grep -E "^SKIPPED" "$SUITE_LOG"
echo "  skip 条数: $(grep -cE '^SKIPPED' "$SUITE_LOG")"
echo
echo "--- 每一条 deselected/failed（应为空）---"
grep -E "^(FAILED|ERROR)" "$SUITE_LOG" || echo "  (no FAILED/ERROR lines)"
echo
echo "§1.7 基线为 847 passed / 5 skipped / 0 failed."
echo "本轮若 skip 数不是 5，差额必须能由上一条打印出的 skip 名单解释 —— 名单就在上面，勿凭记忆。"
echo "---- done ----"
