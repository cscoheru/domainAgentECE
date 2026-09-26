#!/usr/bin/env python3
"""OEI-013 step 1b — PRODUCT-layer recall measurement (after permission filtering).

Why a second measurement (OEI-012 VERDICT §5): OEI-012 measured the **raw engine
layer** (`/api/search` titles) and got hit@1 = hit@3 = 0%. That is an engine
fact, but it is not what a user sees. `/api/v1/consulting/library` runs every
engine hit through `filter_engine_items`, which is FAIL-CLOSED: an engine
document with no `engine_documents` registry row is hidden (`no_registry`), and
an anonymous caller only ever sees `classification == "public"` rows. The
dominant engine hit (`ece-…-oei009-comparison-restricted.md`) is `restricted`, so
it is invisible here.

This script therefore measures what the browser would actually get:

  1. RAW      — GET /library?q=<the eval query>, anonymously, N=3.
                Records the post-filter `engine_items` title list.
  2. REWRITE  — the demo path: the same call for each keyword the shipped SPA
                rewrite would extract, unioned. The terms are NOT re-derived
                here; they are read out of `demos/spa/app.js` by
                `rewrite_probe.js` so this measures the code that ships.

Nothing here writes to Onyx. Read-only GETs against the demo chain.

Usage:
  python3 filtered_runner.py --base http://127.0.0.1:8181 \
      --eval /mnt/d/Projects/domainAgentECE/ece/data/eval/retrieval/consulting-demo.json \
      --out  /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-013/evidence/03-retrieval-filtered.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

N_RUNS = 3
RESTRICTED_TITLE = "ece-df16d19c9e7b-oei009-comparison-restricted.md"
PROBE = Path(__file__).resolve().parent / "rewrite_probe.js"
TIMEOUT = 240.0


def library(base: str, q: str) -> dict:
    """One anonymous /library call. No cookie, no X-User-Id → anonymous."""
    url = f"{base}/api/v1/consulting/library?" + urllib.parse.urlencode({"q": q})
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def call_library(base: str, q: str) -> dict:
    t0 = time.perf_counter()
    error = None
    try:
        body = library(base, q)
    except Exception as exc:  # HTTP error / timeout / transport
        body, error = {}, f"{type(exc).__name__}: {exc}"
    return {"body": body, "latency_seconds": round(time.perf_counter() - t0, 3),
            "error": error}


def engine_titles(body: dict) -> list[str]:
    """Post-filter engine titles, in returned order, de-duplicated."""
    out: list[str] = []
    for item in (body.get("engine_items") or []):
        t = item.get("title") or ""
        if t and t not in out:
            out.append(t)
    return out


def rewrite_terms(question: str) -> dict:
    """Ask the SHIPPED SPA code what it would search for.

    Shelling out to node (rather than porting the rule to Python) is the whole
    point: a Python re-implementation could disagree with app.js and this
    evidence would then describe a program nobody runs.
    """
    proc = subprocess.run(["node", str(PROBE), question],
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"rewrite_probe failed: {proc.stderr.strip()[:400]}")
    data = json.loads(proc.stdout)
    case = data["cases"][0]
    return {"rewritten": case["rewritten"], "terms": case["search_terms"],
            "determinism": data["determinism"]}


def hit_flags(titles: list[str], expected: str) -> dict:
    return {
        "hit_at_1": expected in titles[:1],
        "hit_at_3": expected in titles[:3],
        "expected_present": expected in titles,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="demo origin, e.g. http://127.0.0.1:8181")
    ap.add_argument("--eval", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    evalset = json.loads(Path(args.eval).read_text(encoding="utf-8"))
    queries = evalset["queries"][: args.limit] if args.limit else evalset["queries"]

    print(f"== OEI-013 product-layer matrix start {time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
          flush=True)
    print(f"   base={args.base} queries={len(queries)} N={N_RUNS} "
          f"→ library calls={len(queries) * N_RUNS}", flush=True)

    rows: list[dict] = []
    for q in queries:
        rw = rewrite_terms(q["query"])
        # --- 1. RAW: the eval query verbatim, as a user would type it.
        raw_runs = []
        for run in range(1, N_RUNS + 1):
            res = call_library(args.base, q["query"])
            titles = engine_titles(res["body"])
            row = {
                "id": q["id"], "kind": q["kind"], "expected_title": q["expected_title"],
                "query": q["query"], "path": "raw", "run": run,
                "static_total": res["body"].get("total"),
                "engine_status": res["body"].get("engine_status"),
                "engine_titles": titles,
                "engine_item_count": len(res["body"].get("engine_items") or []),
                "restricted_doc_visible": RESTRICTED_TITLE in titles,
                "error": res["error"],
                "latency_seconds": res["latency_seconds"],
                **hit_flags(titles, q["expected_title"]),
            }
            raw_runs.append(row)
            rows.append(row)
            print(f"[{q['id']} raw run{run}] static={row['static_total']} "
                  f"status={row['engine_status']} engine={titles}"
                  + (f" ERROR={res['error']}" if res["error"] else ""), flush=True)

        # --- 2. REWRITE: the demo path (only when the SPA would rewrite).
        if rw["rewritten"] and rw["terms"]:
            merged: list[str] = []
            statuses: list[str] = []
            static_total = 0
            lat = 0.0
            err = None
            for term in rw["terms"]:
                res = call_library(args.base, term)
                lat += res["latency_seconds"]
                err = err or res["error"]
                statuses.append(res["body"].get("engine_status") or "disabled")
                static_total += res["body"].get("total") or 0
                for t in engine_titles(res["body"]):
                    if t not in merged:
                        merged.append(t)
            status = ("ok" if "ok" in statuses
                      else "unavailable" if "unavailable" in statuses
                      else "skipped" if "skipped" in statuses else "disabled")
            row = {
                "id": q["id"], "kind": q["kind"], "expected_title": q["expected_title"],
                "query": q["query"], "path": "rewrite", "run": 0,
                "terms": rw["terms"],
                "static_total_sum": static_total,
                "engine_status": status,
                "engine_titles": merged,
                "engine_item_count": len(merged),
                "restricted_doc_visible": RESTRICTED_TITLE in merged,
                "error": err,
                "latency_seconds": round(lat, 3),
                **hit_flags(merged, q["expected_title"]),
            }
            rows.append(row)
            print(f"[{q['id']} rewrite] terms={rw['terms']} static~{static_total} "
                  f"status={status} engine={merged}", flush=True)

    # ---- summary -----------------------------------------------------------
    def _pct(subset: list[dict], field: str) -> float | None:
        vals = [bool(r[field]) for r in subset if r["error"] is None]
        return round(sum(vals) / len(vals) * 100, 1) if vals else None

    hit_rows = [r for r in rows if r["kind"] == "hit"]
    raw_hit = [r for r in hit_rows if r["path"] == "raw"]
    rw_hit = [r for r in hit_rows if r["path"] == "rewrite"]

    def _repro(subset: list[dict]) -> dict:
        by_q: dict[str, list[list[str]]] = {}
        for r in subset:
            if r["path"] != "raw" or r["error"] is not None:
                continue
            by_q.setdefault(r["id"], []).append(r["engine_titles"])
        complete = {k: v for k, v in by_q.items() if len(v) == N_RUNS}
        same = sum(1 for v in complete.values() if all(x == v[0] for x in v))
        return {"queries_with_complete_runs": len(complete),
                "fully_reproducible": same,
                "ratio": round(same / len(complete), 3) if complete else None}

    empty_raw = sum(1 for r in raw_hit if r["path"] == "raw" and not r["engine_titles"])
    summary = {
        "n_runs_per_query": N_RUNS,
        "raw_path": {
            "hit_at_1_pct": _pct(raw_hit, "hit_at_1"),
            "hit_at_3_pct": _pct(raw_hit, "hit_at_3"),
            "hit_rows": len(raw_hit),
            "engine_group_empty_runs": empty_raw,
            "restricted_doc_visible_runs": sum(
                1 for r in rows if r["path"] == "raw" and r["restricted_doc_visible"]),
            "reproducibility": _repro(rows),
        },
        "rewrite_path": {
            "hit_at_1_pct": _pct(rw_hit, "hit_at_1"),
            "hit_at_3_pct": _pct(rw_hit, "hit_at_3"),
            "hit_rows": len(rw_hit),
            "engine_group_empty_runs": sum(1 for r in rw_hit if not r["engine_titles"]),
            "restricted_doc_visible_runs": sum(
                1 for r in rows if r["path"] == "rewrite" and r["restricted_doc_visible"]),
        },
        "restricted_title": RESTRICTED_TITLE,
        "errors": sum(1 for r in rows if r["error"] is not None),
    }

    payload = {
        "eval_set": args.eval, "base": args.base, "engine": "onyx",
        "path_note": ("raw = the eval query verbatim (what a user types). "
                      "rewrite = the shipped-SPA keyword path (terms read from "
                      "demos/spa/app.js via rewrite_probe.js)."),
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "summary": summary, "rows": rows,
    }
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    print("\nsummary=" + json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
