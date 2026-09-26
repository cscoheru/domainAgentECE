"""OEI-009 step 2.5 — engine_status branches + static-side sha256 (R2 rework).

A7 acceptance:
  - static side payload byte-identical across engine states (sha256).
  - engine_status three branches (ok / unavailable / no-hit) behave the same.

R2 (codex VERDICT #2 §4.2): the v1 "no-hit" branch was **not a no-hit**.
  It used the query `oei009_definitelydoesnotmatchanywherezzq` and got
  `engine_items_count = 3`; the script's pass criterion only checked
  `engine_status == "ok"` and **never asserted the list was empty**. So the
  zero-result state was never demonstrated.

Why the v1 assumption failed (measured this session, see step26 docstring):
  `POST /api/search` runs `SearchTool.run()` — the agentic multi-stage
  pipeline used by chat mode, including LLM query expansion and LLM auto
  filter detection. The number of results is a *relevance* outcome, not a
  fixed k: the same corpus returned 1/2/3/4 docs for different queries, so a
  meaningless query is NOT guaranteed to return nothing.

R2 construction (genuine, explainable, verified stable 3/3):
  query ISO_QUERY = "员工报销政策与发票审核流程" recalls **only** the
  restricted comparison doc (that topic exists nowhere else in the corpus).
  For an anonymous caller that single result is filtered by the per-result
  permission filter → `engine_items == []` while `engine_status == "ok"`.
  This is the reachable zero-authorized-result state; it is asserted here.

Branches measured:
  branch_static_baseline : q="问题树", real engine — sha256 must equal the
                           historical value recorded in the accepted A7
                           evidence (regression guard on the static side).
  branch_ok              : q=DEMO_QUERY, real engine  → status ok
  branch_unavailable     : q=DEMO_QUERY, engine down  → status unavailable
                           (same query as branch_ok, so the static-sha
                           comparison is apples-to-apples)
  branch_no_hit          : q=ISO_QUERY, anonymous, real engine → status ok
                           AND len(engine_items) == 0   ← the R2 assertion

Run strategy: one *fresh subprocess* per branch, so a patch in one branch
cannot leak into another.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Single source of truth for the two fixed queries + the demo doc name.
from step26_demo_falsifiable import (  # noqa: E402
    CONTROLLED_FILENAME,
    DEMO_QUERY,
    ISO_QUERY,
)

DATABASE_URL = "postgresql+psycopg://ece:ece@127.0.0.1:55432/ece"
ECE_PY = "/mnt/d/Projects/domainAgentECE/ece"

# Historical static-side sha256 from the accepted A7 evidence
# (`05`/`07` in the a884d41 delivery, query "问题树"). If this changes, the
# static catalogue's response changed — which would be a real regression.
HISTORICAL_STATIC_SHA = "677538eaf60813fe1476c112e7aff9b3a9e44331b7d3e736cb84c028d3ac7b4d"


def _sha_of_static(body: dict) -> str:
    static = {k: v for k, v in body.items() if k not in ("engine_items", "engine_status")}
    raw = json.dumps(static, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# Subprocess scripts that produce JSON to stdout --------------------------------
# `{query}` is substituted with the branch's fixed query (json-escaped).

_PREAMBLE = """
import json, os, sys
os.environ['ECE_CONTENT_ENGINE'] = 'onyx'
os.environ['DATABASE_URL'] = 'postgresql+psycopg://ece:ece@127.0.0.1:55432/ece'
for m in list(sys.modules):
    if m.startswith('ece.'): del sys.modules[m]
QUERY = {query!r}
HEADERS = {headers!r}
"""

_TAIL = """
from fastapi.testclient import TestClient
from ece.main import app
client = TestClient(app)
r = client.get('/api/v1/consulting/library', params={{'q': QUERY}}, headers=HEADERS)
print(json.dumps({{'status': r.status_code, 'body': r.json()}}, ensure_ascii=False))
"""

_REAL = _PREAMBLE + _TAIL

_DOWN = _PREAMBLE + """
from ece.connectors.onyx.port import EngineError
from ece.consulting import engine_merge as _em
class _Down:
    engine_name = 'onyx'
    async def search(self, *a, **kw): raise EngineError('down')
    async def engine_status(self, *a, **kw): raise EngineError('down')
    async def list_projects(self, *a, **kw): return []
_em.get_content_engine = lambda: _Down()
""" + _TAIL


def _run_subprocess(template: str, query: str, headers: dict | None = None) -> dict:
    script = template.format(query=query, headers=headers or {})
    proc = subprocess.run(
        ["uv", "run", "--project", ECE_PY, "python", "-c", script],
        capture_output=True,
        text=True,
        env={**os.environ, "DATABASE_URL": DATABASE_URL},
        timeout=300,
    )
    if proc.returncode != 0:
        raise SystemExit(f"subprocess failed:\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout.splitlines()[-1])


def _branch(template: str, query: str, headers: dict | None = None) -> dict:
    r = _run_subprocess(template, query, headers)
    items = r["body"].get("engine_items") or []
    return {
        "query": query,
        "status": r["status"],
        "engine_status": r["body"].get("engine_status"),
        "engine_items_count": len(items),
        "engine_items_titles": sorted(i.get("title", "?") for i in items),
        "static_sha256": _sha_of_static(r["body"]),
    }


def main() -> int:
    out: dict = {"controlled_filename": CONTROLLED_FILENAME}

    # 1. Static-side regression guard against the historical accepted value.
    out["branch_static_baseline"] = _branch(_REAL, "问题树")

    # 2. ok branch — real engine, fixed demo query, anonymous caller.
    out["branch_ok"] = _branch(_REAL, DEMO_QUERY)

    # 3. unavailable branch — same query, engine down.
    out["branch_unavailable"] = _branch(_DOWN, DEMO_QUERY)

    # 4. no-hit branch — R2: anonymous + a query that recalls ONLY the
    #    restricted doc ⇒ zero *authorized* results, engine still "ok".
    out["branch_no_hit"] = _branch(_REAL, ISO_QUERY)

    out["static_determinism"] = {
        "sha_ok": out["branch_ok"]["static_sha256"],
        "sha_unavailable": out["branch_unavailable"]["static_sha256"],
        "equal": out["branch_ok"]["static_sha256"] == out["branch_unavailable"]["static_sha256"],
        "historical_sha": HISTORICAL_STATIC_SHA,
        "baseline_matches_historical": (
            out["branch_static_baseline"]["static_sha256"] == HISTORICAL_STATIC_SHA
        ),
    }

    print(json.dumps(out, indent=2, ensure_ascii=False))

    # ---- Assertions -------------------------------------------------------
    fail = False
    ok = out["branch_ok"]
    un = out["branch_unavailable"]
    nh = out["branch_no_hit"]
    sd = out["static_determinism"]

    if ok["engine_status"] != "ok":
        print(f"FAIL: ok branch returned {ok['engine_status']!r}")
        fail = True
    if un["engine_status"] != "unavailable":
        print(f"FAIL: unavailable branch returned {un['engine_status']!r}")
        fail = True
    # R2 — the whole point: a real, asserted zero-result state.
    if nh["engine_status"] != "ok":
        print(f"FAIL: no-hit branch returned {nh['engine_status']!r} (expected 'ok')")
        fail = True
    if nh["engine_items_count"] != 0:
        print(
            f"FAIL: no-hit branch returned {nh['engine_items_count']} items "
            f"(expected 0) — raw recall did not isolate the restricted doc"
        )
        fail = True
    if not sd["equal"]:
        print("FAIL: static sha256 differs across engine states (should be engine-orthogonal)")
        fail = True
    if not sd["baseline_matches_historical"]:
        print(
            "FAIL: static sha256 for the baseline query no longer matches the "
            f"historical value {HISTORICAL_STATIC_SHA[:12]}…"
        )
        fail = True
    if fail:
        return 1

    print()
    print(
        "PASS — A7: static side byte-stable (baseline matches historical sha, "
        "ok==unavailable); engine_status ok/unavailable/no-hit all as specified; "
        "no-hit is a REAL zero-result state (engine_items == [], engine_status == ok)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
