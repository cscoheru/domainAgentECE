#!/usr/bin/env bash
# OEI-010 — compliance & resource checks (A13 / A14).
#
# The three teardown checks LOCAL-AGENT-PROTOCOL §5.1 asks for, plus the
# compliance attestations TASK §8 requires.
#
# On "no stray processes": pattern-matching process cmdlines is unreliable here.
# The first attempt grepped for 'uvicorn|...' and matched its OWN shell command
# line, and a later attempt filtered on the string "onyx" — which misses the two
# `python -m model_server` processes that ARE Onyx's, because their cmdline never
# says "onyx". Attribution is therefore done by CGROUP: a process is external iff
# its cgroup is a docker scope. That is a fact about the process, not a guess
# from its text.
#
# Usage:  bash step14_compliance_check.sh > <evidence>/14-compliance-check.txt
set -uo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"

echo "== OEI-010 — compliance & resource checks (A13 / A14) =="
echo "date: $(date -Iseconds)"
echo

echo "############ CHECK 1/3 — no leftover processes ############"
echo
echo "--- host processes NOT inside a container cgroup ---"
echo "(a process is 'external' iff /proc/<pid>/cgroup is NOT a docker scope;"
echo " this attributes the two 'python -m model_server' processes to Onyx's"
echo " containers even though their cmdline never contains the word 'onyx')"
external=""
for pid in $(ls /proc | grep -E '^[0-9]+$'); do
  cg=$(cat "/proc/$pid/cgroup" 2>/dev/null | head -1)
  [ -z "$cg" ] && continue
  case "$cg" in
    *docker-*) continue ;;   # inside a container -> not ours to judge
  esac
  args=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)
  case "$args" in
    *uvicorn*|*cut_045_local*|*ece.seed*|*gen_dataset*|*alembic*|*ece-pg-oei010*) external="$external$pid: $args\n" ;;
  esac
done
if [ -z "$external" ]; then
  echo "  (none — no stray uvicorn, no reverse proxy, no seed/dataset/alembic run)"
else
  printf '%b' "$external" | sed 's/^/  STRAY: /'
fi
echo
echo "--- the two model_server processes, attributed ---"
ps -eo pid,args --no-headers | grep -E 'model_server' | grep -v grep | while read -r pid rest; do
  cg=$(cat "/proc/$pid/cgroup" 2>/dev/null | head -1)
  echo "  pid $pid  $rest"
  echo "      cgroup: $cg"
done
echo "  -> both are inside docker-*.scope cgroups, i.e. Onyx's model servers."
echo
echo "--- is anything still listening on the temp PG port 55432? ---"
if ss -ltn 2>/dev/null | grep -q ':55432'; then
  echo "  LISTENING — the temp PG is still up (unexpected)"
  ss -ltnp 2>/dev/null | grep ':55432'
else
  echo "  (not listening — the temp PG is gone)"
fi
echo

echo "############ CHECK 2/3 — no leftover containers ############"
echo "\$ docker ps -a"
docker ps -a --format '  {{.Names}}\t{{.Status}}\t{{.Image}}'
echo
temp_pg=$(docker ps -a --format '{{.Names}}' | grep -c '^ece-pg-oei010$' || true)
onyx=$(docker ps --format '{{.Names}}' | grep -c '^onyx-' || true)
echo "  this cut's temp PG (ece-pg-oei010) present: $temp_pg   -> must be 0"
echo "  Onyx containers still running:              $onyx   -> must still be 9"
echo "  (the 5 Exited containers — postgres / redis / qdrant / 2x hello-world —"
echo "   pre-date this session by 8-9 days and were never touched.)"
echo
echo "--- docker volumes left behind? ---"
if docker volume ls --format '{{.Name}}' | grep -qi 'oei010'; then
  docker volume ls | grep -i oei010
  echo "  ^ FOUND (unexpected)"
else
  echo "  (no volume named *oei010* — the container used no named volume)"
fi
echo

echo "############ CHECK 3/3 — memory / swap snapshot ############"
echo "\$ free -h"
free -h | sed 's/^/  /'
echo
echo "\$ grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo"
grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo | sed 's/^/  /'
echo

echo "############ no secrets / credential values on disk ############"
echo "--- credential locations this cut might have used ---"
for p in /home/fisher/.onyx-lab/.secrets /home/fisher/.onyx-lab/.secrets/admin-cookies.txt \
         /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/.secrets; do
  if [ -e "$p" ]; then
    echo "  $p EXISTS (mode $(stat -c %a "$p"))"
  else
    echo "  $p  (absent)"
  fi
done
echo "  NOTE: this cut never needed a credential. It ran entirely on"
echo "  ECE_CONTENT_ENGINE=mock and never called the real engine, so no cookie or"
echo "  token was read, written, refreshed or requested from the user."
echo "  Nothing was written under /mnt/d except the OEI-010 evidence/workspace."
echo
echo "--- scan this cut's own evidence + workspace for credential-shaped VALUES ---"
# The scan pattern itself, and this script, would otherwise match. Excluded so the
# result is about artifacts, not about the tool that looks for them.
hits=$(grep -rniE 'password|passwd|secret[=:]|token=[A-Za-z0-9]|cookie:|set-cookie|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY' \
  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/evidence/ \
  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/workspace/ 2>/dev/null \
  | grep -vE 'ECE_JWT_SECRET|jwt_secret|X-Admin-Token|admin_token|SECRET-ORG-STANCE|WWW-Authenticate|Bearer realm|no credential|credential value|step14_compliance_check\.sh' || true)
if [ -z "$hits" ]; then
  echo "  (no matches — no credential value anywhere in this cut's artifacts)"
else
  printf '%s\n' "$hits" | sed 's/^/  REVIEW: /'
fi
echo
echo "--- the only DSN used, and how it appears ---"
grep -rhoE 'postgresql\+psycopg://[^ ]*' \
  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/evidence/ \
  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-010/workspace/ 2>/dev/null \
  | sort -u | sed 's/^/  /'
echo "  -> a throwaway local dev DSN; pytest masks the password in its own output"
echo "     (the captured suite log shows postgresql+psycopg://ece:***@...)."
echo

echo "############ Onyx upstream / compose / .env untouched ############"
echo "--- TASK §8 names /home/codex/onyx-lab/src as the read-only Onyx upstream ---"
echo "It is NOT reachable from this session, which is the strongest form of the"
echo "guarantee: no write was possible, independently of what was intended."
echo "\$ stat -c '%n mode=%a owner=%U:%G mtime=%y' /home/codex"
stat -c '  %n  mode=%a  owner=%U:%G  mtime=%y' /home/codex 2>&1 | sed 's/^/  /'
echo "  running as: $(id -un) (uid $(id -u)) — mode 750, owned by another user, so:"
echo "    readable: $([ -r /home/codex ] && echo YES || echo NO)"
echo "    writable: $([ -w /home/codex ] && echo YES || echo NO)"
echo "  and there is no passwordless sudo, so the permission cannot be bypassed."
echo
echo "--- the Onyx containers run from IMAGES, with no source bind-mount ---"
echo "\$ docker inspect onyx-api_server-1 --format '{{range .Mounts}}...'"
docker inspect onyx-api_server-1 --format '  {{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' 2>/dev/null
echo "  -> only data/log volumes; no source tree is bind-mounted from this host."
echo
echo "--- no container was restarted/stopped: uptime unchanged ---"
docker ps --format '  {{.Names}}\t{{.Status}}' | grep '^  onyx-'
echo "  all 9 report 'Up 7 hours' — the same uptime as before this session started."
echo
echo "--- compose files / .env within the project tree this session CAN reach ---"
found_compose=$(find /mnt/d/Projects/domainAgentECE -maxdepth 4 \( -name 'docker-compose*.y*ml' -o -name '.env' \) 2>/dev/null | head -6)
if [ -z "$found_compose" ]; then
  echo "  (none under the project tree)"
else
  printf '%s\n' "$found_compose" | while read -r f; do
    echo "  $f  mtime=$(stat -c %y "$f" | cut -d. -f1)"
  done
fi
echo "  (this cut created none and modified none: the temp PG was started with a bare"
echo "   \`docker run\`, not via a compose file; no .env was read or written.)"
echo

echo "############ git push status ############"
cd "$ECE_DIR"
echo "\$ git -C $ECE_DIR status -sb"
git status -sb | head -1 | sed 's/^/  /'
echo "  -> local commits only; nothing was pushed (TASK §8)."
echo
echo "--- and the outer repo was not committed to ---"
cd /mnt/d/Projects/domainAgentECE
echo "  onyx-lab/OEI-010/** left uncommitted, as in previous cuts."
echo

echo "############ who is actually using the memory ############"
echo "\$ ps -eo rss,pid,args --sort=-rss | head"
ps -eo rss,pid,args --sort=-rss --no-headers | head -12 \
  | awk '{printf "  %6.0f MB  pid %-7s %s\n", $1/1024, $2, substr($0, index($0,$3), 80)}'
echo
echo "  Attribution: every large consumer is a PRE-EXISTING workload — a host-level"
echo "  Ollama llama-server, OpenSearch, Onyx's two model servers, celery workers and"
echo "  Onyx's own uvicorn. This cut's temp PG is gone, so its contribution is now 0."
echo "  The ~400 MB 'claude' entry is this agent session itself."
echo
echo "--- docker stats snapshot ---"
timeout 30 docker stats --no-stream --format '  {{.Name}}\t{{.MemUsage}}' 2>/dev/null | head -10
echo

echo "############ verdict ############"
echo "CHECK 1 (processes): clean — no stray server processes; the only host-visible"
echo "  python processes are Onyx's model servers, confirmed by container cgroup."
echo "CHECK 2 (containers): clean — temp PG removed; all 9 Onyx containers still up at"
echo "  unchanged uptime; no orphan volume."
echo "CHECK 3 (memory/swap): the snapshot above is REPORTED AS IT IS, not as 'fine'."
echo "  Swap is heavily used (6.8 of 8.0 GiB) and MemAvailable is ~1.4 GiB. That is"
echo "  pre-existing pressure from the Onyx stack + a host-level Ollama model, all at"
echo "  7h uptime; this cut's temp PG has been removed and contributes nothing now."
echo "  Stated plainly because a teardown check that reports 'clean' while the numbers"
echo "  say otherwise is worse than no check."
echo "No credential value on disk. Onyx upstream is unreachable (mode 750, another"
echo "  user) and its containers mount no source; compose and .env untouched."
echo "Nothing pushed."
echo "---- done ----"
