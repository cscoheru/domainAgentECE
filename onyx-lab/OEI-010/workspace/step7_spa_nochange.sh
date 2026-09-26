#!/usr/bin/env bash
# OEI-010 step 7 (A8, second half) — `ece/demos/spa/**` must be UNTOUCHED.
#
# PATHS: `ece/` is an independent git repo of its own (see /ece/ in the outer
# .gitignore — "never nest it here"). TASK writes the path as `ece/demos/spa/**`,
# i.e. relative to the PROJECT root; inside the ECE repo it is `demos/spa`. The
# two are the same files. `git diff` only means anything inside the ECE repo —
# run from the outer repo the whole tree is ignored and every check passes
# vacuously.
#
# EVIDENCE: an empty `git diff` is necessary but weak — it says "no diff right
# now", not "these bytes are what is committed". So the script compares worktree
# against the committed blob PER FILE by content hash, which is a content claim
# rather than a claim about git's view of the index.
#
# This script FAILS LOUDLY (exit 1) if the tree is missing or untracked. An
# earlier revision referenced a non-existent path, matched nothing, and printed
# "IDENTICAL: every SPA file matches its committed blob" — a false PASS. The
# guards below exist so that cannot recur.
#
# Usage:  bash step7_spa_nochange.sh > <evidence>/07-audit-provenance.txt
set -uo pipefail

ECE_DIR="${ECE_DIR:-/mnt/d/Projects/domainAgentECE/ece}"
SPA_REL="demos/spa"          # from the ECE repo root; == ece/demos/spa from the project root
cd "$ECE_DIR"

echo "== OEI-010 step 7 (A8) — SPA zero-change proof =="
echo "date: $(date -Iseconds)"
echo "ECE repo: $(git rev-parse --show-toplevel)"
echo "HEAD: $(git rev-parse HEAD)  ($(git log --oneline -1 --format=%s))"
echo "SPA path checked: $SPA_REL  (== ece/$SPA_REL from the project root)"
echo

# ---- guard: the tree must exist AND be tracked, or nothing below is evidence
if [ ! -d "$SPA_REL" ]; then
  echo "FATAL: $SPA_REL does not exist — cannot prove anything about it" >&2
  exit 1
fi
tracked=$(git ls-files "$SPA_REL" | wc -l)
if [ "$tracked" -eq 0 ]; then
  echo "FATAL: $SPA_REL has no tracked files — git diff would be vacuous" >&2
  exit 1
fi
echo "tracked files under $SPA_REL: $tracked"
echo

echo "---- 1. git status for the SPA tree (expect no output) ----"
git status --porcelain -- "$SPA_REL"
echo "[end of status output]"
echo

echo "---- 2. git diff --stat vs HEAD (expect no output) ----"
git diff --stat HEAD -- "$SPA_REL"
echo "[end of diff output]"
echo

echo "---- 3. per-file content hash: worktree vs committed blob ----"
tmp_wt=$(mktemp); tmp_hd=$(mktemp)
find "$SPA_REL" -type f -print0 | sort -z | xargs -0 sha256sum > "$tmp_wt"
while IFS= read -r path; do
  git show "HEAD:$path" | sha256sum | sed "s|-|$path|"
done < <(git ls-tree -r --name-only HEAD -- "$SPA_REL" | sort) > "$tmp_hd"

printf 'worktree files: %s\n' "$(wc -l < "$tmp_wt")"
printf 'committed files: %s\n' "$(wc -l < "$tmp_hd")"
echo "-- per-file hashes --"
sort "$tmp_wt"
echo "-- differences (expect none) --"
if diff <(sort "$tmp_wt") <(sort "$tmp_hd"); then
  echo "IDENTICAL: every SPA file matches its committed blob byte-for-byte"
else
  echo "MISMATCH: the SPA tree differs from HEAD" >&2
  rm -f "$tmp_wt" "$tmp_hd"
  exit 1
fi
echo

echo "---- 4. memory-related strings ANYWHERE in the SPA ----"
echo "grep -rniE 'memory|memories|记忆' $SPA_REL :"
matches=$(grep -rniE 'memory|memories|记忆' -r "$SPA_REL" || true)
if [ -z "$matches" ]; then
  echo "  (no matches at all)"
else
  printf '%s\n' "$matches"
fi
echo "  NOTE: matches are not automatically a violation — the word 'memory' may"
echo "  appear in unrelated pre-existing code. Section 3 proves these files are"
echo "  byte-identical to HEAD, so none of the above was added by this cut."
echo

echo "---- 5. what the SPA actually renders (a memory display would appear here) ----"
for f in "$SPA_REL/app.js" "$SPA_REL/index.html"; do
  [ -f "$f" ] || continue
  echo "-- $f: references to package fields --"
  grep -nE 'documents|business_data|\.memory|package\.|relationships' "$f" | head -20 || echo "  (none)"
done
echo

echo "---- 6. the migration/tests/docs this cut DID touch, for contrast ----"
git status --porcelain | sed 's/^/  /'
echo "  (note: nothing under $SPA_REL appears above)"
echo

rm -f "$tmp_wt" "$tmp_hd"
echo "---- verdict ----"
echo "SPA tree is byte-identical to HEAD ($(git rev-parse --short HEAD)); this cut added no"
echo "memory display to the SPA, and no SPA file was modified."
echo "---- done ----"
