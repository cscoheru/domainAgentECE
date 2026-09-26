#!/usr/bin/env bash
# OEI-012 — "扫描要有牙" 检查（A12 / OEI-011 立的规矩）。
#
# 证明 tests/unit/test_skip_query_expansion.py 不是"跑绿了但什么都测不出"：
# 把真正的接线（body["skip_query_expansion"] = True）从适配器里挖掉，
# 断言测试**必须变红**；随后无条件还原并断言还原成功。
#
# 用法: bash mutation_check.sh
# 退出码: 0 = 牙在（先红后绿）；非 0 = 扫描器没牙或还原失败。
set -uo pipefail

ECE=/mnt/d/Projects/domainAgentECE/ece
TARGET="$ECE/src/ece/connectors/onyx/onyx_adapter.py"
TESTFILE="tests/unit/test_skip_query_expansion.py"
BAK=$(mktemp /tmp/oei012-onyx_adapter.XXXXXX.bak)

cp "$TARGET" "$BAK"
restore() { cp "$BAK" "$TARGET"; rm -f "$BAK"; }
trap restore EXIT

cd "$ECE" || exit 1
export ECE_CONTENT_ENGINE=mock

echo "== OEI-012 mutation check =="
echo "target : $TARGET"
echo "test   : $TESTFILE"
echo

# --- 1. 基线：必须绿 -------------------------------------------------------
echo "--- [1/3] 未变异（基线）---"
uv run pytest "$TESTFILE" -q -o addopts='' 2>&1 | tail -2
base=${PIPESTATUS[0]}
echo "baseline exit=$base"
echo

# --- 2. 变异：挖掉接线，必须红 ---------------------------------------------
echo "--- [2/3] 变异：删除 body[\"skip_query_expansion\"] = True ---"
python3 - "$TARGET" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
needle = '        if skip_query_expansion:\n            body["skip_query_expansion"] = True\n'
if needle not in s:
    print("FATAL: 找不到要挖掉的接线（源码已变？）"); sys.exit(2)
p.write_text(s.replace(needle, ""), encoding="utf-8")
print("mutation applied")
PY
[ $? -ne 0 ] && { echo "FAIL: 变异未施加，本次检查无效"; exit 3; }

uv run pytest "$TESTFILE" -q -o addopts='' 2>&1 | tail -4
mut=${PIPESTATUS[0]}
echo "mutated exit=$mut"
echo

# --- 3. 还原 + 复验 --------------------------------------------------------
echo "--- [3/3] 还原并复验 ---"
restore
trap - EXIT
uv run pytest "$TESTFILE" -q -o addopts='' 2>&1 | tail -2
after=${PIPESTATUS[0]}
echo "restored exit=$after"
echo

if [ "$base" -eq 0 ] && [ "$mut" -ne 0 ] && [ "$after" -eq 0 ]; then
  echo "RESULT: PASS — 基线绿 / 变异红 / 还原绿 → 扫描器有牙，且接线确实被测到"
  exit 0
fi
echo "RESULT: FAIL — base=$base mutated=$mut restored=$after"
exit 1
