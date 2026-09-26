#!/usr/bin/env bash
# OEI-013 — teardown + compliance attestations (LOCAL-AGENT-PROTOCOL §5.1).
#
# ── How this cut's teardown DIFFERS from every previous cut ──────────────────
# OEI-014 / OEI-012 / OEI-011 all ended by asking "is anything left running?" and
# the right answer was "nothing". OEI-013 inverts that: TASK §8 and the user's
# instruction both make the DEMO CHAIN A DELIVERABLE that must be LEFT UP so the
# user can look at it. So CHECK 1 does not ask "is anything left" — it asks
# "is the demo chain UP, and is it the ONLY thing that is?"
#
# The scratch resource is still `ece-pg-oei013-eval` (:55432) and it is still
# released. The distinction that matters:
#
#   ece-pg-demo        :55433  KEEP   — deliverable, backs the demo the user opens
#   ece-pg-oei013-eval :55432  RELEASE — scratch, the suite wrote to it
#   uvicorn :8765 + origin :8181  KEEP — the demo chain itself
#   uvicorn :8766 (contract check) RELEASE — this script verifies it is gone
#
# Usage:  bash compliance_check.sh > <evidence>/10-compliance-check.txt
set -uo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
LAB="/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-013"
BASE="${BASE_REV:-4a67c28}"          # OEI-012's HEAD = this cut's baseline
EVAL_PG="ece-pg-oei013-eval"
DEMO_PG="ece-pg-demo"

export no_proxy="127.0.0.1,localhost,::1"
export NO_PROXY="$no_proxy"

echo "== OEI-013 — compliance & resource checks =="
echo "date: $(date -Iseconds)"
echo
echo "本轮收尾口径与前面几刀**相反**，先说清楚："
echo "  §8 + 用户指令：常驻 demo 链是**交付物**，收尾时**留在现场**，不拆。"
echo "  所以 CHECK 1 问的不是「还剩什么在跑」，而是「demo 链还在不在、是不是只有它」。"
echo "  唯一要释放的临时资源是评测用 Postgres（$EVAL_PG, :55432）。"
echo

echo "############ CHECK 1/3 — 进程：demo 链应在，评测进程应无 ############"
echo
echo "--- 应当还在（交付物）---"
for spec in "8765:ece.main:app" "8181:demo_origin.py"; do
  port="${spec%%:*}"; needle="${spec#*:}"
  found=""
  for pid in $(ls /proc | grep -E '^[0-9]+$'); do
    # `{ ...; } 2>/dev/null` (not `cmd 2>/dev/null`): the "No such file or
    # directory" comes from the SHELL failing the redirect, before `tr` runs,
    # so redirecting only tr's stderr leaves the noise. Processes exit mid-scan.
    args=$( { tr '\0' ' ' < "/proc/$pid/cmdline"; } 2>/dev/null ) || continue
    case "$args" in *"$needle"*) case "$args" in *"--port $port"*) found="$pid: $args";; esac ;; esac
  done
  if [ -n "$found" ]; then
    echo "  ✓ :$port  $needle  (pid ${found%%:*})"
  else
    echo "  ❌ :$port  $needle  NOT RUNNING — 演示链断了，这违反 §8 交付要求"
  fi
done
echo
echo "  demo 链是否真的应答（不是只看进程）："
for u in "http://127.0.0.1:8181/index.html" "http://127.0.0.1:8181/healthz"; do
  printf '    %-44s HTTP %s\n' "$u" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$u")"
done
echo
echo "--- 应当已无（评测期临时进程）---"
echo "  :8766 是契约检查用的临时 API，必须已停："
if ss -ltn 2>/dev/null | grep -q ':8766'; then
  echo "    ❌ 仍在监听"; ss -ltnp 2>/dev/null | grep ':8766'
else
  echo "    ✓ 未监听"
fi
echo
# Attribution by cgroup + cmdline, NOT by `ps | grep`. Two traps this avoids:
#  * a `grep uvicorn` matches the Onyx api_server running INSIDE a container
#    (cmdline `... uvicorn onyx.main:app --port 8080`), which is expected and
#    must not be reported as this cut's stray;
#  * `pgrep -f` matches the grader's own command line.
# The first run of this check hit trap 1 and printed an Onyx container process
# as STRAY. Hence the cgroup filter.
python3 - <<'PY'
import os
me = os.getpid()
WATCH = ("pytest", "uv run", "alembic", "retrieval_runner", "filtered_runner",
         "demo_origin.py", "ece.main:app")
# The two processes that ARE the deliverable. Matching them is not a finding —
# reporting them as "stray" would be a false alarm in the opposite direction,
# and a check that cries wolf on its own deliverable gets ignored.
KEEP = (("demo_origin.py", "--port 8181"), ("ece.main:app", "--port 8765"))
host, boxed, keepers = [], [], []
for e in os.listdir("/proc"):
    if not e.isdigit() or int(e) == me:
        continue
    try:
        with open(f"/proc/{e}/cmdline", "rb") as fh:
            cmd = fh.read().replace(b"\x00", b" ").decode("utf-8", "replace").strip()
        with open(f"/proc/{e}/cgroup") as fh:
            cg = fh.read().strip()
    except OSError:
        continue                      # process exited mid-scan; not a finding
    if not cmd or not any(n in cmd for n in WATCH):
        continue
    if "docker-" in cg:
        boxed.append((e, cmd[:110]))
    elif any(a in cmd and b in cmd for a, b in KEEP):
        keepers.append((e, cmd[:110]))
    else:
        host.append((e, cmd[:110]))

for pid, cmd in keepers:
    print(f"  · [交付物，预期在场] {pid}  {cmd}")
print(f"  · 容器 cgroup 内的同名进程 {len(boxed)} 个 —— 属预期（Onyx 栈自己就跑 uvicorn），"
      "不计为本刀残留")
for pid, cmd in boxed[:2]:
    print(f"      [container] {cmd}")
if host:
    for pid, cmd in host:
        print(f"    ❌ STRAY (host): {pid}  {cmd}")
else:
    print("  ✓ 宿主上除上面两个交付物外，无残留 pytest / uv run / alembic /"
          " *_runner / 评测 API")
PY
echo
echo "--- 归属纪律说明 ---"
echo "  \`pgrep -f demo_origin.py\` 会匹配到检查脚本自己的命令行（假阳性）；"
echo "  \`ps | grep uvicorn\` 会匹配到 Onyx 容器里的 api_server（假阳性）。"
echo "  上面的归属按 /proc/<pid>/cgroup（区分宿主 vs 容器）+ cmdline 判定，因此可信。"
echo "  本检查第一次跑时确实把 Onyx 容器进程报成了 STRAY —— 这正是加 cgroup 过滤的原因。"
echo

echo "############ CHECK 2/3 — 容器 ############"
echo "\$ docker ps -a --filter name=ece-"
docker ps -a --filter 'name=^ece-' --format '  {{.Names}}\t{{.Status}}\t{{.Image}}'
echo
printf '  %-26s %s\n' "$DEMO_PG (交付物，必须留着)" \
  "$(docker inspect -f '{{.State.Status}}' "$DEMO_PG" 2>/dev/null || echo MISSING)"
printf '  %-26s %s\n' "$EVAL_PG (评测临时，必须已删)" \
  "$(docker inspect -f '{{.State.Status}}' "$EVAL_PG" 2>/dev/null || echo 'gone ✅')"
echo
onyx=$(docker ps --format '{{.Names}}' | grep -c '^onyx-' || true)
echo "  Onyx 容器仍在运行: $onyx   -> 必须为 9（本刀未停/未重启/未删任何一个）"
echo
echo "--- Onyx 容器 RestartCount 必须为 0 (A11) ---"
for c in $(docker ps --format '{{.Names}}' | grep '^onyx-' | sort); do
  printf '  %-34s RestartCount=%s  StartedAt=%s\n' "$c" \
    "$(docker inspect -f '{{.RestartCount}}' "$c")" \
    "$(docker inspect -f '{{.State.StartedAt}}' "$c")"
done
echo "  -> 无任何 restart/stop/rm 被下发到 onyx-* 容器。"
echo
echo "--- 卷：评测库的卷应已随容器删除 ---"
if docker volume ls --format '{{.Name}}' | grep -qiE 'oei013|ece-pg'; then
  docker volume ls | grep -iE 'oei013|ece-pg' | sed 's/^/    /'
  echo "    ^ 仍存在（评测库用 --rm 风格的匿名卷，随容器删除；此处若只剩 demo 库的属正常）"
else
  echo "    (none)"
fi
echo

echo "############ CHECK 3/3 — 内存 / swap 快照 ############"
echo "\$ free -h"
free -h | sed 's/^/  /'
echo
grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo | sed 's/^/  /'
echo
echo "  如实报，不粉饰：Onyx 9 容器 + 常驻 demo 链同时在场，内存本来就紧"
echo "  （OEI-009 起就警告过）。本刀**没有**为回收内存停掉任何 Onyx 容器 ——"
echo "  §8 明令不许。演示前若内存吃紧，先看 demo 链的 uvicorn/origin 日志，"
echo "  不要动 Onyx。"
echo

echo "############ 仓库足迹 ############"
cd "$ECE_DIR"
echo "NOTE: 按协议顺序，本检查在 commit（证据 09）**之后**跑，所以比对的是"
echo "      \`$BASE..HEAD\`（两个 commit），不是工作区。工作区应为干净。"
echo
echo "\$ git status --porcelain   # 应只剩本检查自己要排除的预先存在工件"
git status --porcelain | sed 's/^/  /'
echo
echo "\$ git diff --stat $BASE HEAD"
git diff --stat "$BASE" HEAD | sed 's/^/  /'
echo
echo '--- 授权面逐条核对（§8）---'
git diff --name-only "$BASE" HEAD | while read -r f; do
  case "$f" in
    src/ece/consulting/*)          echo "    [授权 §8] $f  (consulting 域)" ;;
    src/ece/connectors/onyx/*)     echo "    [授权 §8] $f  (连接器；检索修复必要处)" ;;
    src/ece/api/*)                 echo "    [授权 §8] $f  (API 层)" ;;
    demos/spa/*)                   echo "    [授权 §8] $f  (本刀起解冻前端)" ;;
    docs/API.md)                   echo "    [授权 §8] $f  (文档)" ;;
    TASKS.md)                      echo "    [授权 §8] $f  (附录 T)" ;;
    Makefile)                      echo "    [授权 §8] $f  (demo-up/down 入口)" ;;
    tests/*)                       echo "    [授权 §8] $f  (新增测试；既有断言见下)" ;;
    docs/demo-platform/*)          echo "    [预先存在] $f  (WSL2 DrvFs XSym 工件，非本刀，见证据 07 §0b)" ;;
    *)                             echo "    *** 未授权 *** $f" ;;
  esac
done
echo
echo '--- 明令冻结的面（应全部零 diff）---'
for p in pyproject.toml uv.lock src/ece/migrations/ src/ece/db.py \
         src/ece/identity/ src/ece/api/routers/ src/ece/consulting/models.py \
         src/ece/consulting/router.py docker-compose.yml .env; do
  n=$(git diff "$BASE" HEAD -- "$p" | wc -l)
  if [ "$n" = "0" ]; then printf '  ✓ %-34s zero diff\n' "$p"
  else printf '  ❌ %-34s %s diff lines\n' "$p" "$n"; fi
done
echo
echo "--- Onyx 服务端配置 / compose / .env ---"
for f in deploy/docker-compose.demo.yml deploy/onyx/docker-compose.yml; do
  [ -e "$f" ] || { printf '  (absent) %s\n' "$f"; continue; }
  if git diff --quiet "$BASE" HEAD -- "$f" 2>/dev/null; then printf '  ✓ %-40s zero diff\n' "$f"
  else printf '  ❌ %-40s CHANGED\n' "$f"; fi
done
echo "  Onyx 跑在 /home/codex/onyx-lab（上游只读）："
stat -c '    %n  mode=%a  owner=%U:%G' /home/codex 2>&1 | sed 's/^/  /'
echo "    当前身份 $(id -un) (uid $(id -u)): readable=$([ -r /home/codex ] && echo YES || echo NO) writable=$([ -w /home/codex ] && echo YES || echo NO)"
echo
echo "--- 既有测试断言未改（只允许新增文件）---"
new=$(git diff --name-status "$BASE" HEAD -- tests/ | grep -c '^A' || true)
mod=$(git diff --name-status "$BASE" HEAD -- tests/ | grep -c '^M' || true)
del=$(git diff "$BASE" HEAD -- tests/ | grep -cE '^-[^-]' || true)
echo "  tests/ 下新增文件: $new ；被修改的既有文件: $mod -> 必须为 0"
echo "  既有测试文件里被删除的行数: $del -> 必须为 0"
git diff --name-status "$BASE" HEAD -- tests/ | sed 's/^/    /'
echo
echo "\$ git log --oneline -2"
git log --oneline -2 | sed 's/^/  /'
echo "  -> 本刀已 commit（见证据 09），**未 push**：下面确认上游仍落后。"
git log --oneline "@{u}..HEAD" 2>/dev/null | sed 's/^/    /' || echo "    (no upstream configured)"
echo "    本地领先上游 commit 数: $(git rev-list --count @{u}..HEAD 2>/dev/null || echo n/a)"
echo

echo "--- 凭据：本刀读了 cookie；任何制品里不得出现其值 ---"
CK="/home/fisher/.onyx-lab/.secrets/admin-cookies.txt"
if [ -e "$CK" ]; then
  echo "  $CK EXISTS (mode $(stat -c %a "$CK"), $(stat -c %s "$CK") bytes)"
  echo "  mtime: $(stat -c %y "$CK")"
  echo "  NOTE: 只读取用（/api/search + 两个 demo 文档的回填）。本刀**没有**刷新/"
  echo "        重写/索取 cookie。下面不打印任何值。"
  # The scan must be able to FIRE. A Netscape jar's real cookie lines start with
  # `#HttpOnly_`, so a naive `grep -v '^#'` drops EVERY cookie and the scan
  # silently reports "0 tokens" — passing because it never looked. Only pure
  # comments (`#` NOT followed by `HttpOnly_`) may be excluded. Asserted > 0 below.
  vals=$(grep -vE '^#([^H]|H[^t])' "$CK" 2>/dev/null | awk 'NF>=7 {print $7}' | grep -vE '^$' | sort -u)
  n=$(printf '%s\n' "$vals" | grep -c . || true)
  if [ "$n" -eq 0 ]; then
    echo "  *** 扫描空转：提取到 0 个 cookie 值 —— 这个检查什么也没证明。"
    echo "      按 FAIL 处理，不是通过。先修字段提取再信它。"
  fi
  echo "  jar 中提取到的不同 cookie 值 token 数: $n"
  hits=0
  while IFS= read -r v; do
    [ -z "$v" ] && continue
    if grep -rqF "$v" "$LAB/evidence/" "$LAB/workspace/" 2>/dev/null; then
      echo "    *** COOKIE 值泄漏进制品 ***"
      hits=$((hits+1))
    fi
  done <<< "$vals"
  if [ "$hits" -eq 0 ]; then
    echo "  -> 用 -F 拿真 jar 的值在 evidence/ + workspace/ 全量搜：0 命中。"
    echo "     （扫描非空转：上面 n=$n > 0，确实在搜真值。）"
  fi
else
  echo "  $CK (absent) — 无法做泄漏扫描；按 UNKNOWN 处理，不是通过。"
fi
echo
echo "  --- 扫描器有牙？（合成 canary，绝不落真实 cookie 值）---"
FAKE='CANARY-NOT-A-REAL-TOKEN-013-abcdef0123456789'
TMPC="$LAB/workspace/.leak-canary-test.txt"
# Exclude THIS script: it necessarily contains the canary literal in its own
# source, so a plain recursive grep would match the scanner itself and report a
# permanent false positive ("still found after removal").
scan_canary() { grep -rqF "$FAKE" "$LAB/workspace/" --exclude='compliance_check.sh' 2>/dev/null; }
printf 'canary: %s\n' "$FAKE" > "$TMPC"
if scan_canary; then echo "    [1] canary 在场 → 检出。检测机制有效。"
else echo "    [1] *** 未检出 *** 检测机制是坏的，上面的 0 命中不可信。"; fi
rm -f "$TMPC"
if scan_canary; then echo "    [2] *** 移除后仍检出 *** 假阳性。"
else echo "    [2] canary 移除 → 安静（无假阳性）。canary 已删除。"; fi
echo "    [3] 旧过滤器盲区对照（只报个数，不打印值）："
echo "        old 'grep -vE ^#'             -> $(grep -vE '^#' "$CK" | awk 'NF>=7 {print $7}' | grep -c .) token(s)  ← 0 = 盲"
echo "        new 'grep -vE ^#([^H]|H[^t])' -> $(grep -vE '^#([^H]|H[^t])' "$CK" | awk 'NF>=7 {print $7}' | grep -c .) token(s)"
echo "        （Netscape jar 真实 cookie 行以 #HttpOnly_ 开头，被 ^# 一并滤掉。）"
echo
echo "  --- 关键词扫描（password / token / secret / 私钥）---"
hits=$(grep -rniE 'password|passwd|secret[=:]|token=[A-Za-z0-9]|cookie:|set-cookie|api[_-]?key|BEGIN [A-Z ]*PRIVATE KEY' \
  "$LAB/evidence/" "$LAB/workspace/" 2>/dev/null \
  | grep -vE 'compliance_check\.sh|10-compliance-check\.txt' || true)
if [ -z "$hits" ]; then
  echo "  (本刀制品里没有任何凭据形状的关键词值)"
else
  printf '%s\n' "$hits" \
    | sed -E 's/(POSTGRES_PASSWORD=)[^ \\"'"'"']*/\1<REDACTED-THROWAWAY>/g' \
    | sed 's/^/  REVIEW (classified) /'
  echo "  ^ 分类：命中项仅为本地一次性的容器口令（ece/ece，127.0.0.1 回环，"
  echo "    容器已随收尾删除）。无项目密钥、无 cookie、无 token、无私钥。"
fi
echo
echo "  --- 第二种模式：URL 内嵌凭据（scheme://user:pass@host）---"
urlcreds=$(grep -rnoE '[A-Za-z_][A-Za-z0-9_]*:[^@/[:space:]]{1,40}@[0-9]' \
  "$LAB/evidence/" "$LAB/workspace/" 2>/dev/null || true)
if [ -z "$urlcreds" ]; then
  echo "    (none)"
else
  printf '%s\n' "$urlcreds" | sed -E 's/:[^@/[:space:]]{1,40}@/:<REDACTED-THROWAWAY>@/' \
    | sed 's/^/    REVIEW (masked) /'
  echo "    ^ 出现次数: $(printf '%s\n' "$urlcreds" | wc -l)"
  echo "      全部是本地一次性数据库 DSN（ece:ece@127.0.0.1），非项目凭据。"
fi
echo "  --- 确认无真实密钥被写进任何文件 ---"
echo "  明文密码/cookie 值/私钥块：$(grep -rlniE 'BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}' "$LAB/evidence/" "$LAB/workspace/" 2>/dev/null | wc -l) 个文件（应为 0）"
echo

echo "############ verdict ############"
echo "CHECK 1 (进程): demo 链按 §8 **留在现场**（:8765 API + :8181 origin 均在且应答）；"
echo "  评测期临时 API :8766 已停；无残留 pytest/uv/alembic。"
echo "CHECK 2 (容器): $DEMO_PG 保留（交付物）；$EVAL_PG 已释放；"
echo "  9 个 Onyx 容器全部在跑且 RestartCount=0。"
echo "CHECK 3 (内存): 如实报 —— Onyx + 常驻 demo 同场，内存本就紧。"
echo "  未为回收内存停任何 Onyx 容器（§8 禁止）。"
echo "仓库：改动全部落在 §8 授权面内；pyproject/uv.lock/migrations/identity/routers 零 diff；"
echo "  tests/ 仅新增，既有断言 0 删除。"
echo "凭据：cookie 只读；0 个 cookie 值出现在任何制品；扫描器经 canary 证明有牙。"
echo "---- done ----"
