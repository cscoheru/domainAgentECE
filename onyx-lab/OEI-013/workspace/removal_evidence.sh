#!/usr/bin/env bash
# OEI-013 step 0 — the removal that did not happen.
#
# User decision (2026-09-26): **先不删，只做只读取证** — do not delete; gather
# read-only evidence. TASK §3.1 had recorded removal as approved; the user
# overrode it when asked to confirm the irreversible step.
#
# This script is deliberately INCAPABLE of deleting anything: the two-step
# delete is printed from here as text, never executed. Running this file can
# only read. That is a safety property, not a stylistic choice — a script named
# "removal" that contains a live DELETE is one careless `bash` away from
# destroying the very corpus the demo depends on.
#
# What it does produce:
#   1. the decision, verbatim, with its provenance;
#   2. a READ-ONLY confirmation that the document is still present;
#   3. the exact commands a future removal would run, with the identifiers
#      filled in, so approving it later is copy-paste rather than archaeology.
#
# Usage: bash removal_evidence.sh > ../evidence/01-removal-two-step.txt
set -euo pipefail

CK="${ECE_ONYX_COOKIE_FILE:-/home/fisher/.onyx-lab/.secrets/admin-cookies.txt}"
BASE="${ECE_ONYX_BASE:-http://127.0.0.1:8080}"
PROJECT=1
UFID=6138305b-0f40-468f-a1c8-bdea6f68d424
DOC=ece-df16d19c9e7b-oei009-comparison-restricted.md

echo "=============================================================================="
echo " OEI-013 / step 0 — controlled comparison document: REMOVAL NOT PERFORMED"
echo " observed_at: $(date -Iseconds)"
echo "=============================================================================="
echo
echo "DECISION"
echo "  decided_by          : user"
echo "  decided_on          : 2026-09-26"
echo "  instruction_verbatim: 先不删，只做只读取证"
echo "  task_reference      : TASK.md §3.1 / §5 step 0 / A1 / A2"
echo "  effect              : no DELETE was issued against Onyx in this cut."
echo "                        Project ${PROJECT} still holds 4 files (3 real + 1 comparison)."
echo
echo "WHY THE DELETION WAS PROPOSED AT ALL"
echo "  OEI-012 measured this document dominating engine recall on project ${PROJECT}:"
echo "    61/72 runs in top-3, and 54/72 runs it was the ONLY result"
echo "    (onyx-lab/OEI-012/evidence/04-retrieval-matrix.json)"
echo "  It is unrelated to the consulting domain, so any 'engine recall' demo that"
echo "  shows it is showing the wrong thing."
echo
echo "------------------------------------------------------------------------------"
echo "READ-ONLY VERIFICATION (GET only — nothing below writes)"
echo "------------------------------------------------------------------------------"
code_cookie=$(curl -s -m 8 -b "$CK" -o /dev/null -w '%{http_code}' "$BASE/api/me" || echo "ERR")
echo "  GET /api/me                              -> $code_cookie"
code_files=$(curl -s -m 15 -b "$CK" -o /tmp/oei013-01-files.json -w '%{http_code}' "$BASE/api/user/projects/files/${PROJECT}" || echo "ERR")
echo "  GET /api/user/projects/files/${PROJECT}          -> $code_files"
python3 - "$DOC" <<'PY'
import json, sys
doc = sys.argv[1]
rows = json.load(open("/tmp/oei013-01-files.json"))
print(f"  files in project 1                       -> {len(rows)}")
for r in sorted(rows, key=lambda x: x.get("name") or ""):
    mark = "  <-- WOULD-BE-DELETED" if r.get("name") == doc else ""
    print(f"    - {r.get('name')}  id={r.get('id')}  status={r.get('status')}{mark}")
present = any(r.get("name") == doc for r in rows)
print()
print(f"  comparison document still present        -> {present}")
print(f"  two-step delete issued in this cut       -> False")
PY
echo
echo "------------------------------------------------------------------------------"
echo "NOT RUN — the two-step delete a future cut would execute"
echo "------------------------------------------------------------------------------"
echo "  Semantics (onyx-lab/重启必读/DEMO-DATA-CLEANUP-2026-09-25.md §2): deleting a"
echo "  file that still has a project association returns HTTP 200 with"
echo "  {\"has_associations\": true, ...} and does NOT delete it. Unlink first."
echo
echo "  # 1) unlink from project        (expect 204)"
echo "  curl -s -b \"\$CK\" -X DELETE \"${BASE}/api/user/projects/${PROJECT}/files/${UFID}\" -w 'unlink=%{http_code}\\n'"
echo
echo "  # 2) delete the user file       (expect 200, triggers async vector cleanup)"
echo "  curl -s -b \"\$CK\" -X DELETE \"${BASE}/api/user/projects/file/${UFID}\" -w 'delete=%{http_code}\\n'"
echo
echo "  # 3) verify                      (expect 3)"
echo "  curl -s -b \"\$CK\" \"${BASE}/api/user/projects/files/${PROJECT}\" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'"
echo
echo "  These lines are echoed, never executed, by this script."
echo
echo "HOW IT COULD BE RESTORED IF EVER REMOVED"
echo "  onyx-lab/OEI-009/workspace/step26_demo_falsifiable.py recreates it (with its"
echo "  ACL row). Note that script is OEI-009's historical evidence tool and is NOT in"
echo "  OEI-013's authorised change set, so it can still recreate the document today."
echo "  OEI-013's own demo chain deliberately does not call it (see demo-up.sh), so"
echo "  starting the demo never brings the document back."
echo "=============================================================================="
