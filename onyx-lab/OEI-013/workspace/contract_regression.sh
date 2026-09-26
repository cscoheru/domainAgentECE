#!/usr/bin/env bash
# OEI-013 step 4a — emit evidence/07-contract-regression.txt
#
# Three independent things, because A8 is three claims:
#   1. key sets (structural + wire + catalog)  → contract_regression.py
#   2. the consulting/demo/onyx/SPA test subsets still pass
#   3. no new dependencies; the three-domain business assertions untouched
#
# Comparisons are against `4a67c28` **and the working tree** (`git diff 4a67c28`
# with no second ref). This cut is not committed yet, so `git diff 4a67c28 HEAD`
# would compare two identical commits and prove nothing.
#
# Runs against the EVAL PG (55432) and a private API port (8766). The resident
# demo (PG 55433 / API 8765 / origin 8181) is NOT touched — it is a deliverable.
set -euo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${OUT:-$(cd "$WS_DIR/.." && pwd)/evidence/07-contract-regression.txt}"
API_PORT="${API_PORT:-8766}"
RUN_DIR="${RUN_DIR:-/tmp/oei013-demo}"

export no_proxy="127.0.0.1,localhost,::1"
export NO_PROXY="$no_proxy"
export DATABASE_URL="postgresql+psycopg://ece:ece@127.0.0.1:55432/ece"

mkdir -p "$RUN_DIR" "$(dirname "$OUT")"
exec > >(tee "$OUT") 2>&1

echo "=== OEI-013 步骤 4a — 契约不回归（A8）==="
echo "date: $(date -Iseconds)"
echo "DATABASE_URL=$DATABASE_URL   (评测库 55432, 非演示库 55433)"
echo "注意：本刀尚未 commit，所以下面一律用 \`git diff 4a67c28\`（比工作区），"
echo "      不用 \`git diff 4a67c28 HEAD\`（两个相同的 commit，什么都证不了）。"
echo

echo "############ 0. 改动面（工作区 vs 4a67c28）############"
echo '$ git diff 4a67c28 --stat -- src/ demos/ docs/ Makefile TASKS.md tests/'
( cd "$ECE_DIR" && git diff 4a67c28 --stat -- src/ demos/ docs/ Makefile TASKS.md tests/ )
echo
echo '### 0a. 本刀对该面造成的改动 = 除 docs/demo-platform/ 之外的那些'
echo '$ git status --porcelain -- src/ demos/ docs/ Makefile TASKS.md tests/'
( cd "$ECE_DIR" && git status --porcelain -- src/ demos/ docs/ Makefile TASKS.md tests/ )
echo
echo "### 0b. 预先存在的环境工件（**不是本刀造成的**，如实披露）"
echo '$ git status --porcelain -- docs/demo-platform/'
( cd "$ECE_DIR" && git status --porcelain -- docs/demo-platform/ )
echo
echo '这两个文件在 /mnt/d (WSL2 DrvFs) 上被存成 "XSym" 重解析点，git 因此看到的是'
echo "1067 字节常规文件，而 tree 里是 51 字节符号链接 → typechange。"
echo "文件 mtime 是 2026-09-22 13:47；该目录最后一次提交是 03662da (cut-042R)，"
echo "都远早于 OEI-013。本刀**没有**碰 docs/demo-platform/，也不改它（§8 未授权）。"
echo '$ head -c 40 docs/demo-platform/DEMO_PLATFORM_PRD.md | od -c | head -3'
( cd "$ECE_DIR" && head -c 40 docs/demo-platform/DEMO_PLATFORM_PRD.md | od -c | head -3 )
echo '$ stat -c "%y  %n" docs/demo-platform/*.md'
( cd "$ECE_DIR" && stat -c '%y  %n' docs/demo-platform/*.md )
echo
echo '断言：`src/ece/consulting/models.py` 不在改动列表里（响应模型零 diff）。'
echo '$ git diff 4a67c28 --stat -- src/ece/consulting/models.py'
md="$( cd "$ECE_DIR" && git diff 4a67c28 --stat -- src/ece/consulting/models.py )"
if [ -z "$md" ]; then echo "(空 — 零 diff ✅)"; else echo "$md"; fi
echo
echo '断言：`tests/` 只有新增文件 — 既有断言不得改（删掉的行数必须为 0）。'
del="$( cd "$ECE_DIR" && git diff 4a67c28 -- tests/ | grep -c '^-[^-]' || true )"
echo "\$ git diff 4a67c28 -- tests/ | grep -c '^-[^-]'   # 被删的既有测试行数"
echo "$del"
[ "$del" = "0" ] && echo "   ✓ 既有断言零删除" || echo "   ❌ 有既有断言被删"
echo '$ git diff 4a67c28 --stat -- tests/'
( cd "$ECE_DIR" && git diff 4a67c28 --stat -- tests/ ) || true
echo

echo '断言：无新依赖 — pyproject.toml / uv.lock 零 diff。'
echo '$ git diff 4a67c28 --stat -- pyproject.toml uv.lock'
nodep="$( cd "$ECE_DIR" && git diff 4a67c28 --stat -- pyproject.toml uv.lock )"
if [ -z "$nodep" ]; then echo "(空 — 零 diff ✅)"; else echo "$nodep"; fi
echo

echo "############ 1. 键集合：结构性 + 线上 + 目录 ############"
echo '$ ECE_CONTENT_ENGINE=mock python -m uvicorn ece.main:app --port 8766   (评测库实例)'
( cd "$ECE_DIR" && ECE_CONTENT_ENGINE=mock nohup .venv/bin/python -m uvicorn ece.main:app \
    --host 127.0.0.1 --port "$API_PORT" >"$RUN_DIR/uvicorn-eval.log" 2>&1 &
  echo $! >"$RUN_DIR/uvicorn-eval.pid" )
for _ in $(seq 1 60); do
  curl -sf -o /dev/null "http://127.0.0.1:${API_PORT}/healthz" && break
  sleep 0.5
done
curl -sf -o /dev/null "http://127.0.0.1:${API_PORT}/healthz" \
  || { echo "评测 API 未起来；见 $RUN_DIR/uvicorn-eval.log"; exit 1; }
echo "   ✓ 评测 API 就绪于 :$API_PORT (pid $(cat "$RUN_DIR/uvicorn-eval.pid"))"
echo
python3 "$WS_DIR/contract_regression.py" --base "http://127.0.0.1:${API_PORT}" \
  --out "$OUT.part1" || true
cat "$OUT.part1"; rm -f "$OUT.part1"
echo
echo "停止评测 API (pid $(cat "$RUN_DIR/uvicorn-eval.pid" 2>/dev/null || echo '?'))"
kill "$(cat "$RUN_DIR/uvicorn-eval.pid" 2>/dev/null)" 2>/dev/null || true
for _ in $(seq 1 20); do kill -0 "$(cat "$RUN_DIR/uvicorn-eval.pid" 2>/dev/null)" 2>/dev/null || break; sleep 0.25; done
kill -9 "$(cat "$RUN_DIR/uvicorn-eval.pid" 2>/dev/null)" 2>/dev/null || true
rm -f "$RUN_DIR/uvicorn-eval.pid"

# SWEEP for survivors, by /proc/<pid>/cmdline + port — not by pidfile alone.
# A pidfile can name the wrong pid, and the FIRST run of this script left a
# uvicorn holding :8766 that the compliance check then (correctly) flagged as a
# stray. Attribution is cmdline + `--port 8766`, so an unrelated process that
# merely mentions the string cannot be killed by accident.
python3 - 8766 <<'PY'
import os, signal, sys, time
port, me = sys.argv[1], os.getpid()
victims = []
for e in os.listdir("/proc"):
    if not e.isdigit() or int(e) == me:
        continue
    try:
        with open(f"/proc/{e}/cmdline", "rb") as fh:
            cmd = fh.read().replace(b"\x00", b" ").decode("utf-8", "replace")
        with open(f"/proc/{e}/cgroup") as fh:
            if "docker-" in fh.read():
                continue                      # a container's own uvicorn
    except OSError:
        continue
    if "uvicorn" in cmd and f"--port {port}" in cmd:
        victims.append((int(e), cmd.strip()[:100]))
for pid, cmd in victims:
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
        print(f"   ✓ SIGKILLed survivor pid={pid}  ({cmd})")
    except OSError:
        print(f"   ✓ stopped survivor pid={pid}")
if not victims:
    print("   ✓ 无幸存进程（pidfile 与实际一致）")
PY
if ss -ltn 2>/dev/null | grep -q ':8766'; then
  echo "   ❌ :8766 仍在监听 —— 收尾失败"; ss -ltnp 2>/dev/null | grep ':8766'
else
  echo "   ✓ :8766 已释放（演示实例 :8765 未受影响）"
fi
echo

echo "############ 2. 既有契约测试全绿（不是本刀新写的测试）############"
echo "\$ ECE_CONTENT_ENGINE=mock pytest <consulting/demo/onyx/SPA 既有子集> -v --tb=short -o addopts=''"
( cd "$ECE_DIR" && ECE_CONTENT_ENGINE=mock uv run --project "$ECE_DIR" pytest \
    tests/unit/test_consulting_documents.py \
    tests/unit/test_consulting_service.py \
    tests/unit/test_consulting_seed_schema.py \
    tests/unit/test_consulting_seed_count.py \
    tests/unit/test_consulting_seed_discipline.py \
    tests/unit/test_consulting_engine_merge.py \
    tests/unit/test_consulting_spa_view.py \
    tests/unit/test_engine_merge_filter.py \
    tests/unit/test_engine_documents_registry.py \
    tests/unit/test_content_engine_identity.py \
    tests/unit/test_skip_query_expansion.py \
    tests/unit/test_demo_smoke_script.py \
    tests/unit/test_no_procurement_literal_in_engine.py \
    tests/integration/test_consulting_api_contract.py \
    tests/integration/test_consulting_filters_search.py \
    tests/integration/test_demo_api_contract.py \
    tests/integration/test_spa_smoke.py \
    -v --tb=short -o addopts='' )
echo

echo "############ 3. 三域业务断言与 65 个种子对象未被本刀触碰 ############"
for f in tests/integration/test_three_domain_acceptance.py \
         tests/integration/test_canonical_seed_completeness.py \
         src/ece/consulting/seed/consulting_objects.json \
         data/eval/retrieval/consulting-demo.json; do
  d="$( cd "$ECE_DIR" && git diff 4a67c28 --stat -- "$f" )"
  if [ -z "$d" ]; then echo "  ✓ $f  零 diff"; else echo "  ❌ $f"; echo "$d"; fi
done
echo
echo "=== END 07 ==="
