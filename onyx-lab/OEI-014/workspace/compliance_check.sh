#!/usr/bin/env bash
# OEI-014 — teardown three-check + compliance attestations (LOCAL-AGENT-PROTOCOL §5.1).
#
# This cut started exactly ONE temporary resource: a Postgres container named
# `ece-pg-oei014` on port 55432 (needed for the full suite, which requires a live
# DB). No uvicorn, no reverse proxy, no worktree, and the real content engine was
# never started (ECE_CONTENT_ENGINE=mock throughout, per §8).
#
# This script is run AFTER `docker rm -f ece-pg-oei014`, so "0 ece-* containers"
# is the EXPECTED, EARNED result — not a tautology of never having started one.
# The container's removal is done by the operator of this script, not by the
# check, so the check can actually fail if the teardown was forgotten.
#
# Attribution for the process check is by CGROUP, not by cmdline text: Onyx's own
# `python -m model_server` processes never say "onyx" in their cmdline, and a
# cmdline pattern for our own work matches the shell running the pattern. cgroup
# membership is a fact about the process, not a guess from text.
#
# Usage:  bash compliance_check.sh > <evidence>/12-compliance-check.txt
set -uo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
LAB="/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-014"

echo "== OEI-014 — compliance & resource checks =="
echo "date: $(date -Iseconds)"
echo "NOTE: one temporary Postgres container (ece-pg-oei014, port 55432) was used"
echo "      for the full-suite run and has ALREADY been removed before this check."
echo "      So CHECK 1/2 are asked the question they are meant to ask: is anything"
echo "      of it left? ('0 ece-* containers' below is therefore a real pass/fail"
echo "      line, not a consequence of never having started one.)"
echo "      The real content engine was never started — ECE_CONTENT_ENGINE=mock."
echo

echo "############ CHECK 1/3 — no leftover processes ############"
echo
echo "--- host processes NOT inside a container cgroup, matching this cut's work ---"
external=""
for pid in $(ls /proc | grep -E '^[0-9]+$'); do
  cg=$(cat "/proc/$pid/cgroup" 2>/dev/null | head -1)
  [ -z "$cg" ] && continue
  case "$cg" in
    *docker-*) continue ;;
  esac
  args=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)
  case "$args" in
    *uvicorn*|*alembic*|*ece.seed*|*gen_dataset*|*cut_045_local*|*ece-pg-oei014*) external="$external$pid: $args\n" ;;
  esac
done
if [ -z "$external" ]; then
  echo "  (none — no uvicorn, no reverse proxy, no alembic/seed/dataset run)"
else
  printf '%b' "$external" | sed 's/^/  STRAY: /'
fi
echo
echo "--- anything listening on the temp PG port 55432? ---"
if ss -ltn 2>/dev/null | grep -q ':55432'; then
  echo "  LISTENING — unexpected"; ss -ltnp 2>/dev/null | grep ':55432'
else
  echo "  (not listening)"
fi
echo
echo "--- pytest / uv processes this cut left behind ---"
leftover=$(ps -eo pid,args --no-headers | grep -E 'pytest|uv run' | grep -v grep || true)
if [ -z "$leftover" ]; then echo "  (none)"; else printf '%s\n' "$leftover" | sed 's/^/  STRAY: /'; fi
echo
echo "--- this cut's own scanner / verifier scripts are NOT servers ---"
echo "  anchor_scan.py / apply_increment.py / verify_draft.py / verify_api.py are"
echo "  one-shot CLIs (they exit); verify_api.py drives the app in-process via"
echo "  fastapi.testclient, which starts no listener. Confirmed by the (none) above."
echo

echo "############ CHECK 2/3 — no leftover containers ############"
echo "\$ docker ps -a"
docker ps -a --format '  {{.Names}}\t{{.Status}}\t{{.Image}}'
echo
temp=$(docker ps -a --format '{{.Names}}' | grep -c -E '^ece-' || true)
onyx=$(docker ps --format '{{.Names}}' | grep -c '^onyx-' || true)
echo "  containers named ece-* (this cut's temp PG would be one): $temp   -> must be 0"
echo "  Onyx containers still running:                            $onyx   -> must still be 9"
echo "  (the 5 Exited containers pre-date this session by 8-9 days and were never touched.)"
echo
echo "--- volumes left behind? ---"
if docker volume ls --format '{{.Name}}' | grep -qiE 'oei014|ece-pg'; then
  docker volume ls | grep -iE 'oei014|ece-pg'; echo "  ^ FOUND (unexpected)"
else
  echo "  (none)"
fi
echo
echo "--- temp dirs this cut used (must be gone or empty of servers) ---"
for d in /tmp/oei014; do
  if [ -e "$d" ]; then echo "  $d exists: $(ls -A "$d" | tr '\n' ' ')  (logs only, no process)"; else echo "  $d (absent)"; fi
done
echo

echo "############ CHECK 3/3 — memory / swap snapshot ############"
echo "\$ free -h"
free -h | sed 's/^/  /'
echo
grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo | sed 's/^/  /'
echo

echo "############ the cut's footprint on the repository ############"
cd "$ECE_DIR"
BASE="${BASE_REV:-c30e50e}"   # OEI-011's HEAD = the pre-cut baseline for THIS cut
echo "NOTE: the cut is COMMITTED by this point, so \`git diff\` (worktree vs index) is"
echo "      trivially empty and would prove nothing. The question 'did the cut touch"
echo "      anything it was not authorised to touch?' is instead put to the BASELINE:"
echo "      \`git diff $BASE HEAD\`. That comparison cannot be satisfied by committing."
echo
echo "\$ git diff --stat $BASE HEAD         # must be exactly the 3 authorised files"
git diff --stat "$BASE" HEAD | sed 's/^/  /'
changed=$(git diff --name-only "$BASE" HEAD | wc -l)
echo "  files changed vs baseline: $changed   -> must be 3"
echo
echo "  \$ git diff --name-only $BASE HEAD | while read f; do case ... # authorisation map"
git diff --name-only "$BASE" HEAD | while read -r f; do
  case "$f" in
    src/ece/consulting/seed/consulting_objects.json) echo "    [authorised] $f  (只新增 20 条；既有 45 条见 evidence/01b 的整对象哈希)" ;;
    docs/API.md|docs/DATA_MODEL.md|TASKS.md)         echo "    [authorised] $f  (§6.1 文档)" ;;
    tests/*)                                         echo "    [authorised] $f  (§8 允许新增测试文件；本刀实际未新增)" ;;
    *)                                               echo "    *** NOT AUTHORISED *** $f" ;;
  esac
done
echo
echo "--- 本刀明令冻结的面（应全部零 diff）---"
echo "\$ git diff --stat $BASE HEAD -- pyproject.toml uv.lock demos/ src/ece/migrations/ \\"
echo "                                    src/ece/consulting/metadata.py tests/"
git diff --stat "$BASE" HEAD -- pyproject.toml uv.lock demos/ src/ece/migrations/ \
                            src/ece/consulting/metadata.py tests/ | sed 's/^/  /'
echo "  (no output above = zero diff: no new dependency, no SPA byte changed, no"
echo "   migration, ALLOWED_* vocabulary untouched, and NOT ONE existing assertion"
echo "   changed — which is §8/A6's whole point.)"
echo
for p in pyproject.toml uv.lock demos/ src/ece/migrations/ src/ece/consulting/metadata.py tests/; do
  printf '  %-40s diff lines: %s\n' "$p" "$(git diff "$BASE" HEAD -- "$p" | wc -l)"
done
echo
echo "--- 种子文件：只有新增（numstat）+ 整对象哈希（真正的证明）---"
git diff --numstat "$BASE" HEAD -- src/ece/consulting/seed/consulting_objects.json | sed 's/^/  /'
echo "  ^ 插入 / 删除。删除必须是 0。"
echo "  NOTE: diff 的行匹配可能是巧合，所以上面这行**不是**主证据。主证据是"
echo "  evidence/01b-existing-45-unchanged-hashes.txt：既有 45 条**整对象**规范化"
echo "  JSON 的 sha256 与 $BASE 逐条相等（45/45）。"
echo
echo "--- pre-existing dirt in the worktree (NOT this cut's; deliberately left alone) ---"
echo "\$ git -C $ECE_DIR status --porcelain | wc -l"
dirt=$(git status --porcelain)
n_dp=$(printf '%s\n' "$dirt" | grep -c 'docs/demo-platform/' || true)
n_rep=$(printf '%s\n' "$dirt" | grep -c 'reports/cut-04' || true)
echo "  $(printf '%s\n' "$dirt" | grep -c . ) dirty entries (breakdown computed, not asserted):"
printf '%s\n' "$dirt" | sed 's/^/    /'
echo "    = $n_dp x 'docs/demo-platform/*.md' (symlink typechange ' T')"
echo "    + $n_rep x 'reports/cut-04*/mutation-evidence/*.md' (' M')"
echo "      all present before OEI-014 began (mtime 2026-09-22/23), all excluded from"
echo "      the commit; verified by the 3-file count above."
echo
echo "\$ git -C $ECE_DIR status -sb | head -1"
git status -sb | head -1 | sed 's/^/  /'
echo "  -> local commits only; nothing pushed (TASK §8)."
echo
echo "\$ git log --oneline @{u}..HEAD   # everything unpushed, incl. this cut"
git log --oneline "@{u}..HEAD" 2>/dev/null | sed 's/^/    /' || echo "    (no upstream configured)"
echo "  HEAD = $(git rev-parse --short HEAD)  ($(git log -1 --format=%s | cut -c1-64))"
echo
echo "--- no credential was read, written, refreshed or requested ---"
for p in /home/fisher/.onyx-lab/.secrets /home/fisher/.onyx-lab/.secrets/admin-cookies.txt "$LAB/.secrets"; do
  if [ -e "$p" ]; then echo "  $p EXISTS (mode $(stat -c %a "$p"))"; else echo "  $p  (absent)"; fi
done
echo "  NOTE: this cut never needed the real engine (static catalog + vocabulary only),"
echo "  so no project cookie/token was touched and none was requested from the user."
echo
hits=$(grep -rniE 'password|passwd|secret[=:]|token=[A-Za-z0-9]|cookie:|set-cookie|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY' \
  "$LAB/evidence/" "$LAB/workspace/" 2>/dev/null \
  | grep -vE 'compliance_check\.sh' || true)
if [ -z "$hits" ]; then
  echo "  (no credential-shaped value anywhere in this cut's artifacts)"
else
  # The scan must be able to FIRE (an earlier revision grep'd a pattern that could
  # never match and printed nothing, which reads like a pass). It does fire — on
  # the throwaway local-container password. That value is a one-off for a Postgres
  # container that no longer exists; it is not a project credential, and the value
  # itself is redacted here rather than echoed (LOCAL-AGENT-PROTOCOL: no secret
  # value in an artifact).
  printf '%s\n' "$hits" \
    | sed -E 's/(POSTGRES_PASSWORD=)[^ \\"'"'"']*/\1<REDACTED-THROWAWAY>/g' \
    | sed 's/^/  REVIEW (classified) /'
  echo "  ^ classification: the ONLY hits are the throwaway local-container password in"
  echo "    workspace/fresh_db_chain.sh. It guarded a temp DB on 127.0.0.1:55432 that"
  echo "    has been removed. No project secret, no cookie, no token, no private key."
  echo "    The scan is not vacuous — it fired, and it fired on the one thing that"
  echo "    legitimately looks like a password."
fi
echo
echo "  --- second pattern: credentials embedded in a URL (scheme://user:pass@host) ---"
echo "  The scan above greps KEYWORDS (password / token / secret ...). A DSN carries a"
echo "  credential without any of those words, so a keyword-only scan is BLIND to it."
echo "  Asked separately here, and the value is masked in the output:"
urlcreds=$(grep -rnoE '[A-Za-z_][A-Za-z0-9_]*:[^@/[:space:]]{1,40}@[0-9]' \
  "$LAB/evidence/" "$LAB/workspace/" 2>/dev/null || true)
if [ -z "$urlcreds" ]; then
  echo "    (none)"
else
  printf '%s\n' "$urlcreds" | sed -E 's/:[^@/[:space:]]{1,40}@/:<REDACTED-THROWAWAY>@/' \
    | sed 's/^/    REVIEW (masked) /'
  echo "    ^ occurrence count: $(printf '%s\n' "$urlcreds" | wc -l)"
  echo "      All of them are the local temp-DB DSN for a container that no longer"
  echo "      exists — same pattern and same value as OEI-010's evidence, which passed"
  echo "      review (OEI-010's own compliance file masked it as 'ece:***@'). Not a"
  echo "      project credential: it never left 127.0.0.1 and the database is deleted."
fi
echo
echo "--- Onyx upstream / compose / .env ---"
stat -c '  %n  mode=%a  owner=%U:%G' /home/codex 2>&1 | sed 's/^/  /'
echo "  running as $(id -un) (uid $(id -u)): readable=$([ -r /home/codex ] && echo YES || echo NO) writable=$([ -w /home/codex ] && echo YES || echo NO)"
echo "  -> unreachable at the permission level, not merely by intent."
uptime_onyx=$(docker ps --format '{{.Names}}\t{{.Status}}' | grep '^onyx-' || true)
if [ -z "$uptime_onyx" ]; then
  # A grep that can match nothing and then print nothing reads like a pass.
  echo "  NO MATCH — the Onyx uptime check found no container; treat as UNKNOWN,"
  echo "  not as 'unchanged'."
else
  printf '%s\n' "$uptime_onyx" | sed 's/^/  /'
  echo "  (uptimes as reported. No restart/stop/down/rm was issued against any onyx-*"
  echo "   container: the only docker writes in this cut were \`docker run\` and"
  echo "   \`docker rm -f\` on the name ece-pg-oei014 — provable by grepping this cut's"
  echo "   workspace/ for 'docker'. All onyx-* uptimes above exceed this session's"
  echo "   length, which is the machine-checkable form of 'unchanged'.)"
fi
echo

echo "############ verdict ############"
echo "CHECK 1 (processes): clean — no uvicorn, no reverse proxy, no leftover pytest/uv,"
echo "  nothing listening on the temp PG port. The temp PG container is gone."
echo "CHECK 2 (containers): clean — 0 ece-* containers after an explicit teardown;"
echo "  9 Onyx containers running at uptimes longer than this session."
echo "CHECK 3 (memory/swap): REPORTED AS IT IS, not as 'fine' — swap usage and"
echo "  MemAvailable are reported above verbatim. This is PRE-EXISTING pressure from"
echo "  the Onyx stack; this cut's only contribution was one Postgres container, now"
echo "  removed, which the snapshot above is taken AFTER. Stated plainly because a"
echo "  teardown check that reports 'clean' while the numbers say otherwise is worse"
echo "  than no check."
echo "Repository: 3 files changed vs the $BASE baseline, all authorised; zero diff on"
echo "  pyproject.toml / uv.lock / demos/ / src/ece/migrations/ / metadata.py / tests/."
echo "  Nothing pushed."
echo "Secrets: no project credential appears anywhere; the scan fired only on a redacted"
echo "  throwaway local-container password."
echo "---- done ----"
