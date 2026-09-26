#!/usr/bin/env bash
# OEI-010 step 2 (A2) — the org branch in `_subject_matches`.
#
# A2 asks for three things, and this captures all three as raw output:
#   1. the source diff — "only one match rule was added, nothing reordered"
#   2. the four-state unit tests, run for real
#   3. proof that the EXISTING subject kinds and the classification matrix are
#      untouched (the regression half of the same test file)
#
# Usage:  bash step2_subject_matches.sh > <evidence>/02-subject-matches.txt
set -euo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
cd "$ECE_DIR"

echo "== OEI-010 step 2 (A2) — org branch in _subject_matches =="
echo "date: $(date -Iseconds)"
echo "cwd : $(pwd)"
echo

echo "---- 1. source diff of the engine (working tree vs HEAD) ----"
echo "\$ git diff -- src/ece/permissions/engine.py"
git diff -- src/ece/permissions/engine.py
echo

echo "---- 1b. the added lines only (git diff -U0 | grep '^+') ----"
git diff -U0 -- src/ece/permissions/engine.py | grep '^+' | grep -v '^+++' || true
echo

echo "---- 1c. `_subject_matches` as it now stands ----"
sed -n '/^def _subject_matches/,/^def /p' src/ece/permissions/engine.py | head -40
echo

echo "---- 2. four-state unit tests (DB-free), raw output ----"
uv run pytest tests/unit/test_check_permission_org.py -v -p no:cacheprovider
echo

echo "---- 3. existing-subject regression, same file (raw output) ----"
uv run pytest tests/unit/test_check_permission_org.py -v -p no:cacheprovider \
  -k "still or matrix or deny"
echo

echo "---- done ----"
