#!/usr/bin/env python3
"""OEI-012 步骤 3 — 真引擎召回评测矩阵 runner（N=3 × 两档 expansion）。

走真实 Onyx（ECE_CONTENT_ENGINE=onyx），通过 OnyxContentEngineAdapter.search()
的 `skip_query_expansion` 形参切换两档 —— 这一步同时证明插桩端到端生效
（expansion_off 与 expansion_on 若真被引擎分别处理，结果/延迟会有可观测差异）。

口径（写死，对应 TASK §3.2）：
  - 两档：expansion_on  = skip_query_expansion=False（现状默认）
          expansion_off = skip_query_expansion=True
  - N=3：每条 query 每档各跑 3 次；记录每次**去重后 title 集合 + 顺序 + 延迟**。
  - hit@k：expected_title 是否出现在前 k 个去重 title 里（k=1 与 k=3 各报一个数）。
  - 复现性：逐 query、每档，N 次去重 title 集是否完全一致 + 两两 Jaccard。
  - 误召回：miss query 中 expected_title 出现次数。

用法（在 ece/ 根目录跑，真引擎 + cookie）：
  cd /mnt/d/Projects/domainAgentECE/ece
  ECE_CONTENT_ENGINE=onyx \
  uv run python /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/retrieval_runner.py \
      --eval data/eval/retrieval/consulting-demo.json \
      --out /mnt/d/Projects/domainAgentECE/onyx-lab/OEI-012/workspace/retrieval-matrix.json

资源纪律：评测全程只读检索，不上传/不删除任何文档。开始/结束时间与内存快照由
本脚本打印到 stderr（调用方负责落盘到 compliance 证据）。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
sys.path.insert(0, str(ECE / "src"))

from ece.connectors.onyx.onyx_adapter import OnyxContentEngineAdapter  # noqa: E402

N_RUNS = 3
MODES = (
    ("expansion_on", False),
    ("expansion_off", True),
)

# Measurement-harness client timeout (NOT a product change).
# The shipped adapter caps at _TIMEOUT_SECONDS = 60s. OEI-009 measured single
# /api/search calls at 20-56s, and a cold first call in this very run blew past
# 60s — so a 60s cap would silently convert "slow engine response" into "no data
# point", biasing the matrix. We widen it for the *measurement* only and record
# the value in the output JSON so the latency metric stays interpretable.
# `ece/src/ece/connectors/onyx/onyx_adapter.py` is untouched by this.
MEASURE_CLIENT_TIMEOUT_SECONDS = 180.0
import ece.connectors.onyx.onyx_adapter as _oa  # noqa: E402

_oa._TIMEOUT_SECONDS = MEASURE_CLIENT_TIMEOUT_SECONDS


def _free_mem_snapshot() -> dict[str, str]:
    """Read /proc/meminfo essentials (no external tool dependency)."""
    want = ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree")
    out: dict[str, str] = {}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            for key in want:
                if line.startswith(key + ":"):
                    out[key] = line.split(":", 1)[1].strip()
    except OSError:
        pass
    return out


def _dedup_titles(docs: list) -> tuple[list[str], list[str]]:
    """Return (ordered unique titles, ordered raw titles incl. dup chunks)."""
    seen: list[str] = []
    raw: list[str] = []
    for d in docs:
        t = d.title or ""
        raw.append(t)
        if t and t not in seen:
            seen.append(t)
    return seen, raw


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


async def run_matrix(adapter: OnyxContentEngineAdapter, evalset: dict) -> dict:
    queries = evalset["queries"]
    rows: list[dict] = []
    for q in queries:
        for mode, skip in MODES:
            for run in range(1, N_RUNS + 1):
                t0 = time.perf_counter()
                error = None
                try:
                    docs = await adapter.search(q["query"], skip_query_expansion=skip)
                except Exception as e:  # EngineError / transport / timeout
                    # Record-and-continue: an aborted matrix would lose every
                    # already-measured row. A failed call is DATA about the mode
                    # (it is a real engine outcome), so it is kept as an explicit
                    # row rather than silently dropped from the denominator.
                    docs = []
                    error = f"{type(e).__name__}: {e}"
                latency = round(time.perf_counter() - t0, 3)
                titles, raw = _dedup_titles(docs)
                hit = error is None
                rows.append({
                    "id": q["id"],
                    "query": q["query"],
                    "kind": q["kind"],
                    "expected_title": q["expected_title"],
                    "mode": mode,
                    "run": run,
                    "latency_seconds": latency,
                    "dedup_titles": titles,
                    "raw_title_count": len(raw),
                    "error": error,
                    "ok": hit,
                    "hit_at_1": (q["expected_title"] in titles[:1]) if hit else None,
                    "hit_at_3": (q["expected_title"] in titles[:3]) if hit else None,
                    "expected_present": (q["expected_title"] in titles) if hit else None,
                })
                print(f"[{q['id']} {mode} run{run}] latency={latency:.1f}s "
                      f"raw={len(raw)} dedup={titles}"
                      + (f" ERROR={error}" if error else ""),
                      file=sys.stderr, flush=True)
    return {"rows": rows}


def summarize(rows: list[dict], evalset: dict) -> dict:
    """Aggregate the matrix. Failed calls are excluded from every denominator
    and reported explicitly in `errors_by_mode`, so no metric silently absorbs
    a missing data point."""
    ok_rows = [r for r in rows if r["ok"]]
    hit_rows = [r for r in ok_rows if r["kind"] == "hit"]
    miss_rows = [r for r in ok_rows if r["kind"] == "miss"]

    def _per_mode(subset: list[dict], field: str) -> dict[str, float | None]:
        out: dict[str, float | None] = {}
        for mode, _ in MODES:
            m = [r for r in subset if r["mode"] == mode]
            out[mode] = round(sum(bool(r[field]) for r in m) / len(m) * 100, 1) if m else None
        return out

    def _count_per_mode(subset: list[dict]) -> dict[str, int]:
        return {mode: sum(1 for r in subset if r["mode"] == mode) for mode, _ in MODES}

    # reproducibility: group by (id, mode); only groups with all N runs OK count
    repro: dict[str, dict] = {}
    for mode, _ in MODES:
        by_query: dict[str, list[list[str]]] = {}
        for r in ok_rows:
            if r["mode"] != mode:
                continue
            by_query.setdefault(r["id"], []).append(r["dedup_titles"])
        complete = {qid: sets for qid, sets in by_query.items() if len(sets) == N_RUNS}
        exact_same = sum(1 for sets in complete.values() if all(s == sets[0] for s in sets))
        jaccards: list[float] = []
        for sets in complete.values():
            for i in range(len(sets)):
                for j in range(i + 1, len(sets)):
                    jaccards.append(_jaccard(sets[i], sets[j]))
        repro[mode] = {
            "queries_fully_reproducible": exact_same,
            "queries_with_complete_runs": len(complete),
            "queries_with_incomplete_runs": len(by_query) - len(complete),
            "fully_reproducible_ratio": (round(exact_same / len(complete), 3)
                                         if complete else None),
            "mean_pairwise_jaccard": (round(sum(jaccards) / len(jaccards), 3)
                                      if jaccards else None),
        }

    # latency per mode over OK rows only
    latency: dict[str, dict] = {}
    for mode, _ in MODES:
        vals = sorted(r["latency_seconds"] for r in ok_rows if r["mode"] == mode)
        latency[mode] = {
            "n": len(vals),
            "min": vals[0] if vals else None,
            "max": vals[-1] if vals else None,
            "mean": round(sum(vals) / len(vals), 2) if vals else None,
            "median": vals[len(vals) // 2] if vals else None,
        }

    return {
        "n_runs_per_query_per_mode": N_RUNS,
        "client_timeout_seconds": MEASURE_CLIENT_TIMEOUT_SECONDS,
        "modes": {m: {"skip_query_expansion": s} for m, s in MODES},
        "errors_by_mode": {mode: sum(1 for r in rows if not r["ok"] and r["mode"] == mode)
                           for mode, _ in MODES},
        "hit_at_1_pct": _per_mode(hit_rows, "hit_at_1"),
        "hit_at_3_pct": _per_mode(hit_rows, "hit_at_3"),
        "hit_rows_total": _count_per_mode(hit_rows),
        "hit_queries_total": len({r["id"] for r in hit_rows}),
        "reproducibility": repro,
        "latency_seconds": latency,
        "miss_false_recall_count": {
            mode: sum(1 for r in miss_rows if r["mode"] == mode and r["expected_present"])
            for mode, _ in MODES
        },
        "miss_rows_total": _count_per_mode(miss_rows),
        "miss_queries_total": len({r["id"] for r in miss_rows}),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-out", default=None)
    ap.add_argument("--limit", type=int, default=None,
                    help="only run the first N queries (smoke runs; NOT for the "
                         "recorded matrix — the committed matrix is always full)")
    args = ap.parse_args()

    evalset = json.loads(Path(args.eval).read_text(encoding="utf-8"))
    if args.limit:
        evalset = {**evalset, "queries": evalset["queries"][: args.limit]}
    print(f"== OEI-012 retrieval matrix start {time.strftime('%Y-%m-%dT%H:%M:%S%z')} ==",
          file=sys.stderr)
    print("mem before: " + json.dumps(_free_mem_snapshot(), ensure_ascii=False), file=sys.stderr)
    print(f"queries={len(evalset['queries'])} modes={len(MODES)} N={N_RUNS} "
          f"→ total engine calls={len(evalset['queries'])*len(MODES)*N_RUNS} "
          f"client_timeout={MEASURE_CLIENT_TIMEOUT_SECONDS}s",
          file=sys.stderr, flush=True)

    adapter = OnyxContentEngineAdapter()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    t0 = time.perf_counter()
    data = asyncio.run(run_matrix(adapter, evalset))
    wall = round(time.perf_counter() - t0, 1)
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    summary = summarize(data["rows"], evalset)
    payload = {
        "eval_set": args.eval,
        "engine": "onyx",
        "engine_adapter": "OnyxContentEngineAdapter",
        "wall_seconds": wall,
        "partial_run": bool(args.limit),
        "started_at": started_at,
        "finished_at": finished_at,
        "summary": summary,
        "rows": data["rows"],
    }
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")

    print(f"wall={wall}s  hit@1={summary['hit_at_1_pct']}  hit@3={summary['hit_at_3_pct']}",
          file=sys.stderr)
    print("repro=" + json.dumps(summary["reproducibility"], ensure_ascii=False), file=sys.stderr)
    print("false_recall=" + json.dumps(summary["miss_false_recall_count"], ensure_ascii=False),
          file=sys.stderr)
    print("mem after: " + json.dumps(_free_mem_snapshot(), ensure_ascii=False), file=sys.stderr)
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
