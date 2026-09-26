#!/usr/bin/env python3
"""OEI-013 step 0 — read-only corpus snapshot + the deferred-removal record.

TASK §5 step 0 asked for a two-step DELETE of the controlled comparison
document, followed by a snapshot proving project 1 shrank to 3 real documents.
The user overrode that on 2026-09-26: **"先不删，只做只读取证"** — do not delete,
gather read-only evidence instead.

So this script does the read-only half, and does it in a way that still answers
the questions the deletion was meant to answer:

  * what exactly is in project 1, with the identifiers a later deletion would
    need (user_file_id / file_id / chunk_count) — so removing it later is a
    copy-paste, not an investigation;
  * whether anything changed between the two snapshots taken in this cut
    (it must not have: this cut writes nothing to Onyx);
  * whether the document that would be deleted is the one OEI-012 measured as
    dominating recall.

Nothing here writes, deletes or uploads anything on Onyx. GETs only.

Usage:
  python3 corpus_snapshot.py --before /tmp/oei013-p1-before.json \
      --out .../evidence/00-corpus-before-after.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ONYX_BASE = "http://127.0.0.1:8080"
COOKIE_FILE = "/home/fisher/.onyx-lab/.secrets/admin-cookies.txt"
PROJECT_ID = 1
COMPARISON_DOC = "ece-df16d19c9e7b-oei009-comparison-restricted.md"
REAL_DOCS = (
    "case-management-consulting.md",
    "methodology-framework.md",
    "play-sales-delivery.md",
)


def _cookie_jar():
    """Parse the Netscape cookie jar. Mirrors backfill_demo_docs.py — including
    its handling of the `#HttpOnly_` prefix, which naive parsers drop (that
    exact bug produced a vacuous '0 tokens' scan result in OEI-012)."""
    import http.cookiejar

    jar = http.cookiejar.CookieJar()
    text = Path(COOKIE_FILE).read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or (line.startswith("#") and not line.startswith("#HttpOnly_")):
            continue
        parts = line.split("\t") if "\t" in line else line.split()
        if len(parts) < 7:
            continue
        domain, _flag, path_, _secure, _expires, name = parts[:6]
        value = "\t".join(parts[6:]) if "\t" in line else " ".join(parts[6:])
        c = http.cookiejar.Cookie(
            version=0, name=name, value=value,
            port=None, port_specified=False,
            domain=domain.lstrip("#HttpOnly_"), domain_specified=True,
            domain_initial_dot=False, path=path_ or "/", path_specified=True,
            secure=False, expires=None, discard=False, comment=None,
            comment_url=None, rest={}, rfc2109=False,
        )
        jar.set_cookie(c)
    return jar


def _get(url: str):
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(_cookie_jar())
    )
    with opener.open(url, timeout=30) as resp:
        return resp.status, json.load(resp)


def fetch_project_files() -> list[dict]:
    status, rows = _get(f"{ONYX_BASE}/api/user/projects/files/{PROJECT_ID}")
    if status != 200 or not isinstance(rows, list):
        raise SystemExit(f"unexpected response: {status} {type(rows).__name__}")
    out = []
    for r in rows:
        out.append({
            "name": r.get("name"),
            "user_file_id": r.get("id"),
            "file_id": r.get("file_id"),
            "status": r.get("status"),
            "chunk_count": r.get("chunk_count"),
            "token_count": r.get("token_count"),
        })
    return sorted(out, key=lambda x: x["name"] or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default=None,
                    help="JSON snapshot taken at cut start (list of file rows)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    _, me = _get(f"{ONYX_BASE}/api/me")
    after = fetch_project_files()

    before = None
    if args.before and Path(args.before).is_file():
        raw = json.loads(Path(args.before).read_text(encoding="utf-8"))
        rows = raw if isinstance(raw, list) else raw.get("files")
        # Accept either this script's normalised shape or the raw Onyx payload
        # (which uses `id` for what the two-step delete calls user_file_id).
        before = sorted(
            [
                {
                    "name": r.get("name"),
                    "user_file_id": r.get("user_file_id") or r.get("id"),
                    "file_id": r.get("file_id"),
                    "status": r.get("status"),
                    "chunk_count": r.get("chunk_count"),
                    "token_count": r.get("token_count"),
                }
                for r in (rows or [])
            ],
            key=lambda x: x["name"] or "",
        )

    names_after = [f["name"] for f in after]
    comparison_rows = [f for f in after if f["name"] == COMPARISON_DOC]
    real_rows = [f for f in after if f["name"] in REAL_DOCS]

    payload = {
        "observed_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "onyx_base": ONYX_BASE,
        "project_id": PROJECT_ID,
        "identity": {"email": me.get("email"), "id": me.get("id")},
        "decision": {
            "removal_performed": False,
            "decided_by": "user",
            "decided_on": "2026-09-26",
            "instruction_verbatim": "先不删，只做只读取证",
            "task_reference": "TASK.md §3.1 / §5 step 0 / A1 / A2",
            "note": ("TASK §3.1 recorded the user as having approved removing "
                     "the comparison document. When cc requested explicit "
                     "confirmation for the irreversible deletion, the user "
                     "instead chose read-only evidence. No deletion was "
                     "attempted or performed in this cut."),
        },
        "before": before,
        "after": after,
        "before_after_identical": (
            before is not None
            and [f["name"] for f in before] == names_after
            and [f["user_file_id"] for f in before] == [f["user_file_id"] for f in after]
        ) if before is not None else None,
        "counts": {
            "total_files": len(after),
            "comparison_docs": len(comparison_rows),
            "expected_real_docs_present": len(real_rows),
            "task_expected_total_if_removed": 3,
        },
        "would_be_deleted": comparison_rows[0] if comparison_rows else None,
        "real_docs": real_rows,
        "note_on_identifiers": (
            "`user_file_id` is the Onyx `id` field and is what the two-step "
            "deletion (unlink then delete) takes; `file_id` is the underlying "
            "file object. Both are recorded so a future removal needs no "
            "rediscovery."
        ),
    }
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    print(f"project {PROJECT_ID}: {len(after)} files "
          f"(comparison={len(comparison_rows)}, real={len(real_rows)})")
    print(f"before/after identical: {payload['before_after_identical']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
