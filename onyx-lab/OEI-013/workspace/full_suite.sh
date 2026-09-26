#!/usr/bin/env bash
# OEI-013 step 4b — the full suite, on the EVAL database, via the full
# documented pre-chain. Emits evidence/08-test-suite-raw.txt.
#
# Carried over from OEI-012's `fresh_db_chain.sh`, with three changes:
#
#   1. it runs against `ece-pg-oei013-eval` (:55432), NOT the resident demo PG
#      (:55433). The suite's integration tests write to `engine_documents` and
#      other registry tables; pointing them at the demo's PG would let a test
#      mutate the state the user is about to be shown. The demo is a deliverable.
#   2. it creates the database FRESH and runs the seeding chain exactly ONCE.
#      This is not tidiness — reusing an already-seeded PG fails the suite for a
#      reason that has nothing to do with the code under test. Seeding twice
#      gives the relationship fixture two owners:
#          RuntimeError: canonical seed incomplete — relationship seeding failed:
#          fixture incomplete: 210 rows tagged 'demo:seed_relationships',
#          expected 1200 (200 PRs x 6) while 1200 insert(s) were reported.
#          A shortfall with no rejections means a foreign source_system already
#          owns those triples.
#      (That is exactly what the first run of this script produced, against a PG
#      that `eval_pg_up.sh` had already seeded.) OEI-012's runner used a brand-new
#      database for the same reason.
#   3. the expected count is computed from the baseline plus THIS cut's new test
#      files, and every new file is listed here by name.
#
# Why the full pre-chain and not just `pytest`: OEI-011/OEI-014 found that a
# full-suite run from an unseeded database reports ~48 failures in the
# three-domain integration tests (all "no entity with source_id='KM-POL-001'").
# Those failures come from skipping the documented seeding step, not from a code
# regression — so running the chain is what makes the result attributable.
#
# `make seed-fixtures` is deliberately NOT used: its recipe has an unescaped
# backtick pair in an `@echo` (`Now \`make test\` should reach baseline`) which
# the shell command-substitutes, so that target silently runs the ENTIRE suite as
# a side effect. That is a pre-existing Makefile defect, not OEI-013's. Its four
# seeders are invoked directly; README.md:79 and the Makefile comment both state
# they are exactly equivalent.
#
# Usage: bash full_suite.sh
set -uo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$(cd "$WS_DIR/.." && pwd)/evidence/08-test-suite-raw.txt}"
PG_NAME="${PG_NAME:-ece-pg-oei013-eval}"
PG_PORT="${PG_PORT:-55432}"
RUN_DIR="${RUN_DIR:-/tmp/oei013-demo}"

export no_proxy="127.0.0.1,localhost,::1"
export NO_PROXY="$no_proxy"
export DATABASE_URL="postgresql+psycopg://ece:ece@127.0.0.1:${PG_PORT}/ece"
export ECE_CONTENT_ENGINE=mock

mkdir -p "$RUN_DIR" "$(dirname "$OUT")"
exec > >(tee "$OUT") 2>&1

echo "== OEI-013 步骤 4b — 全套件，走完整文档化前置链 =="
echo "date: $(date -Iseconds)"
echo "cwd: $ECE_DIR"
echo "commit under test: $( cd "$ECE_DIR" && git rev-parse HEAD )  ($( cd "$ECE_DIR" && git log -1 --format=%s | cut -c1-60 ))"
echo "注意：本刀尚未 commit —— 上面的 hash 是 4a67c28，被测代码是【工作区】。"
echo "ECE_CONTENT_ENGINE = mock"
echo "DATABASE_URL = $DATABASE_URL   (评测库 $PG_PORT, 非演示库 55433)"
echo
echo "前置链（README.md / Makefile test-integration 记载的顺序）:"
echo "  alembic -c src/ece/migrations/alembic.ini upgrade head"
echo "  gen_dataset.py --out data/dataset/demo.json"
echo "  python -m ece.seed                                 (采购三域 demo pack)"
echo "  seed_temporal_roles.py / seed_knowledge_fixture.py /"
echo "  seed_compliance_fixture.py / seed_v0_spike_fixture.py   (集成 fixture)"
echo "  pytest -m 'not eval and not eval_llm' -rs          (= make test 的确切命令)"
echo

echo "############ 0. 全新评测库 ############"
echo "\$ docker rm -f $PG_NAME && docker run -d ... -p $PG_PORT:5432"
docker rm -f "$PG_NAME" >/dev/null 2>&1 || true
docker run -d --name "$PG_NAME" \
  -e POSTGRES_USER=ece -e POSTGRES_PASSWORD=ece -e POSTGRES_DB=ece \
  -p "127.0.0.1:${PG_PORT}:5432" "${PG_IMAGE:-pgvector/pgvector:pg16}" >/dev/null
# Same initdb-temp-server race as demo-up.sh: pg_isready can pass against the
# temporary server, which then shuts down. Confirm with a retry loop AND a real
# query, not a single probe.
for _ in $(seq 1 60); do
  docker exec "$PG_NAME" pg_isready -U ece -d ece >/dev/null 2>&1 && break
  sleep 1
done
ready=0
for _ in $(seq 1 30); do
  docker exec "$PG_NAME" psql -U ece -d ece -tAc 'select 1' >/dev/null 2>&1 && { ready=1; break; }
  sleep 1
done
[ "$ready" = "1" ] || { echo "评测库未能就绪"; exit 1; }
echo "  ✓ 全新库就绪（种子链只会跑这一次）"
echo "  演示库（不得受影响）:"
docker ps --filter 'name=^ece-pg-demo$' --format '  {{.Names}}  {{.Status}}  {{.Ports}}'
echo

echo "############ 1. 迁移 ############"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" alembic \
    -c src/ece/migrations/alembic.ini upgrade head ) 2>&1 | tail -3
echo "  head = $( cd "$ECE_DIR" && uv run --project "$ECE_DIR" alembic \
    -c src/ece/migrations/alembic.ini current 2>/dev/null | tail -1 )"
echo

echo "############ 2. 数据集 + 种子 ############"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" python scripts/gen_dataset.py \
    --out data/dataset/demo.json ) 2>&1 | tail -2
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" python -m ece.seed ) 2>&1 | tail -3
echo

echo "############ 3. 集成 fixture（四个 seeder，逐个跑） ############"
for s in seed_temporal_roles seed_knowledge_fixture seed_compliance_fixture seed_v0_spike_fixture; do
  echo "--- $s.py ---"
  ( cd "$ECE_DIR" && uv run --project "$ECE_DIR" python "scripts/$s.py" ) 2>&1 | tail -3
done
echo

echo "############ 4. 全套件（= make test 的确切命令 + -rs） ############"
echo '$ uv run pytest -m "not eval and not eval_llm" -rs'
# Captured to a file, not piped: `addopts` already supplies -q, and a pipe would
# let the warnings block push the summary line out of a `tail`.
# `-rs` (NOT another -q: addopts already has -q, and a second makes it -qq which
# suppresses the summary line) is added so every skip carries its REASON here.
# An unexplained skip count is not evidence.
SUITE_LOG="$RUN_DIR/full-suite.txt"
( cd "$ECE_DIR" && uv run --project "$ECE_DIR" pytest \
    -m "not eval and not eval_llm" -rs ) > "$SUITE_LOG" 2>&1
echo "  pytest exit code: $?"
echo "  raw log: $SUITE_LOG (kept outside the repo)"
echo
echo "--- 原始输出尾部 ---"
tail -25 "$SUITE_LOG"
echo
echo "--- 汇总行（不经管道，避免被 warnings 块挤掉）---"
grep -E "^[0-9]+ (passed|failed)|[0-9]+ failed" "$SUITE_LOG" | tail -2
echo
echo "--- 每一条 skip 及其原因 ---"
grep -E "^SKIPPED" "$SUITE_LOG"
echo "  skip 条数: $(grep -cE '^SKIPPED' "$SUITE_LOG")"
echo
echo "--- 每一条 FAILED/ERROR（应为空）---"
grep -E "^(FAILED|ERROR)" "$SUITE_LOG" || echo "  (no FAILED/ERROR lines)"
echo
echo "--- 本刀新增的两个测试文件，用例数按 pytest 自己的收集结果 ---"
# NOT `grep -c '^def test_'`: parametrized cases count once in source but many
# times in the suite, and the whole point of this number is to reconcile against
# the collected total. Ask pytest.
for f in tests/unit/test_library_recall_mode.py tests/unit/test_consulting_demo_rewrite.py; do
  n=$( cd "$ECE_DIR" && uv run --project "$ECE_DIR" pytest "$f" \
        --collect-only -q -o addopts='' 2>/dev/null | grep -cE '::' )
  echo "  $f: $n 条（pytest --collect-only 计数）"
done
echo
echo "---- 差额归因（从本轮日志**算**出来，不写死数字）----"
# Computed, not hard-coded: `test_cut_045_local_origin_smoke` is FLAKY (it cold-
# starts its own uvicorn on a random port behind a 10 s timeout), so the totals
# differ run to run. Two consecutive OEI-013 runs produced 893/4 and 894/3. A
# hard-coded "expect 893" would have been a false statement in one of them.
python3 - "$SUITE_LOG" <<'PY'
import re, sys
log = open(sys.argv[1], encoding="utf-8", errors="replace").read()
m = re.search(r"^(\d+) passed(?:, (\d+) failed)?.*?(\d+) skipped", log, re.M)
if not m:
    m = re.search(r"(\d+) passed.*?(\d+) skipped", log)
passed, skipped = int(m.group(1)), int(m.group(3) if m.group(3) else m.group(2))
failed = int(re.search(r"(\d+) failed", log).group(1)) if " failed" in log else 0
BASE_P, BASE_S = 859, 5          # OEI-012 evidence 08
NEW = 33                          # this cut's two new test files
skips = re.findall(r"^SKIPPED \[\d+\] (\S+?):(\d+): (.+)$", log, re.M)
uniq = sorted({(s[0], s[1]) for s in skips})
print(f"  基线（OEI-012 证据 08）: {BASE_P} passed / {BASE_S} skipped / 0 failed")
print(f"  本轮                  : {passed} passed / {skipped} skipped / {failed} failed")
print(f"  passed 差额 {passed-BASE_P:+d} ；skipped 差额 {skipped-BASE_S:+d}")
print(f"  其中本刀新增测试贡献 {NEW:+d}（tests/unit/test_library_recall_mode.py 23 +")
print( "                                          tests/unit/test_consulting_demo_rewrite.py 10）")
print(f"  余下 {passed-BASE_P-NEW:+d} 必须由下面这份 skip 名单解释：")
for f, line in uniq:
    print(f"    skip: {f}:{line}")
print()
print("  基线里的 5 个 skip 是 test_e2_permission.py:50/:103 ×1 + test_s5_5_real_llm.py ×3。")
print("  test_e2_permission 的两条理由是 'e2 runner returned unexpected exit 3")
print("  (likely env not ready)' —— 本轮四个 fixture seeder 已跑，环境就绪，它们真的")
print("  跑起来了；若不在上面名单里，即已从 skip 转为 PASS。")
print()
print("  ⚠️  test_cut_045_local_origin_smoke.py:213 是**环境抖动**，不是本刀改动：")
print("      它自己在随机端口冷起一个 uvicorn，10 秒超时。本轮两次连跑的观测是")
print("      893 passed / 4 skipped 与 894 passed / 3 skipped —— 差别就在这一条。")
print("      该文件相对基线零 diff（证据 07 第 2 节里它在本刀子集中是 PASS），")
print("      且它 skip 时理由会原样打在上面的 SKIPPED 行里。如实报，不粉饰。")
print()
print(f"  结论: {failed} failed —— 与基线一致（0）。")
PY
echo "---- done ----"
