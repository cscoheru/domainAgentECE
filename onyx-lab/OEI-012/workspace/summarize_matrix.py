#!/usr/bin/env python3
"""OEI-012 — derive evidence 05 from the raw matrix (04-retrieval-matrix.json).

Every number in `05-hit-repro-summary.txt` is computed here, from the raw rows.
Nothing is transcribed by hand: re-running this script regenerates 05 byte for
byte from 04, which is what makes the summary independently checkable.

Usage:
  python3 summarize_matrix.py \
      --matrix  evidence/04-retrieval-matrix.json \
      --out     evidence/05-hit-repro-summary.txt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SHORT = {
    "case-management-consulting.md": "CASE",
    "methodology-framework.md": "METH",
    "play-sales-delivery.md": "PLAY",
    "ece-df16d19c9e7b-oei009-comparison-restricted.md": "RESTR",
}
MODES = ("expansion_on", "expansion_off")


def short(title: str) -> str:
    return SHORT.get(title, title)


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    d = json.loads(Path(args.matrix).read_text(encoding="utf-8"))
    rows, s = d["rows"], d["summary"]
    out: list[str] = []
    w = out.append

    w("=== OEI-012 步骤 3 — 命中率 / 复现性 / 延迟 汇总（由 04 原始数据机算）===")
    w(f"source      : {args.matrix}")
    w(f"eval_set    : {d['eval_set']}")
    w(f"engine      : {d['engine']} via {d['engine_adapter']}")
    w(f"started_at  : {d['started_at']}")
    w(f"finished_at : {d['finished_at']}")
    w(f"wall_seconds: {d['wall_seconds']}")
    w(f"partial_run : {d['partial_run']}  (false = 全量矩阵, 12 query × 2 档 × 3 次)")
    w(f"client_timeout_seconds: {s['client_timeout_seconds']} (测量用；产品默认仍为 60)")
    w("")
    w("图例: CASE=case-management-consulting.md  METH=methodology-framework.md")
    w("      PLAY=play-sales-delivery.md  RESTR=ece-...-oei009-comparison-restricted.md")
    w("")

    # ---- A3 hit rate -------------------------------------------------------
    w("--- A3 命中率（hit = expected_title 出现在去重后前 k 个 title 里）---")
    for m in MODES:
        w(f"  {m:14} hit@1 = {s['hit_at_1_pct'][m]}%   hit@3 = {s['hit_at_3_pct'][m]}%"
          f"   (hit 行数 {s['hit_rows_total'][m]} = {s['hit_queries_total']} query × 3 次)")
    w(f"  误召回（miss query 里 expected_title 仍出现）: "
      + "  ".join(f"{m}={s['miss_false_recall_count'][m]}/{s['miss_rows_total'][m]}"
                  for m in MODES))
    w("")

    # ---- A2 reproducibility ------------------------------------------------
    w("--- A2 复现性（逐 query、每档：3 次去重 title 集是否完全一致）---")
    for m in MODES:
        r = s["reproducibility"][m]
        w(f"  {m:14} 完全一致 {r['queries_fully_reproducible']}/{r['queries_with_complete_runs']}"
          f" = {r['fully_reproducible_ratio']}   "
          f"两两 Jaccard 均值 = {r['mean_pairwise_jaccard']}   "
          f"(运行不完整 query 数 {r['queries_with_incomplete_runs']})")
    w("")

    # ---- A2: per-pair Jaccard, per query, per mode -------------------------
    w("--- A2 复现性明细：逐 query 的**逐次两两 Jaccard**（N=3 → 3 对）---")
    qids_all = list(dict.fromkeys(r["id"] for r in rows))
    for m in MODES:
        w(f"  [{m}]")
        for qid in qids_all:
            sets = [r["dedup_titles"] for r in rows
                    if r["mode"] == m and r["id"] == qid and r["ok"]]
            if len(sets) != s["n_runs_per_query_per_mode"]:
                w(f"    {qid}: 运行不完整（{len(sets)}/{s['n_runs_per_query_per_mode']}），跳过")
                continue
            pairs = [
                (f"r{i+1}~r{j+1}", round(jaccard(sets[i], sets[j]), 3))
                for i in range(len(sets)) for j in range(i + 1, len(sets))
            ]
            allone = all(v == 1.0 for _, v in pairs)
            w(f"    {qid}: " + "  ".join(f"{k}={v}" for k, v in pairs)
              + ("   [全部 1.0]" if allone else "   *** 有 <1.0 ***"))
    w("")

    # ---- latency ----------------------------------------------------------
    w("--- 延迟（秒；仅统计成功行）---")
    for m in MODES:
        L = s["latency_seconds"][m]
        w(f"  {m:14} n={L['n']}  min={L['min']}  median={L['median']}  "
          f"mean={L['mean']}  max={L['max']}")
    on, off = s["latency_seconds"]["expansion_on"], s["latency_seconds"]["expansion_off"]
    if off["median"]:
        w(f"  → expansion_off / expansion_on 中位数加速比 = "
          f"{round(on['median'] / off['median'], 2)}x")
    if off["mean"]:
        w(f"  → expansion_off / expansion_on 均值加速比   = "
          f"{round(on['mean'] / off['mean'], 2)}x")
    w("")
    w(f"--- 调用失败数 ---  "
      + "  ".join(f"{m}={s['errors_by_mode'][m]}" for m in MODES))
    w("")

    # ---- per-query grid ---------------------------------------------------
    w("--- 逐 query × 档：3 次运行的去重 title 序列（顺序即引擎返回顺序）---")
    qids = list(dict.fromkeys(r["id"] for r in rows))
    for qid in qids:
        qr = [r for r in rows if r["id"] == qid]
        kind, exp, query = qr[0]["kind"], short(qr[0]["expected_title"]), qr[0]["query"]
        w(f"  {qid} [{kind}] expect={exp}  q={query}")
        for m in MODES:
            runs = [r for r in qr if r["mode"] == m]
            seq = " | ".join(
                ("+".join(short(t) for t in r["dedup_titles"]) or "(空)") for r in runs
            )
            same = "一致" if len({tuple(r["dedup_titles"]) for r in runs}) == 1 else "不一致"
            hits = [r["hit_at_3"] for r in runs]
            w(f"      {m:14} {seq:44} [{same}] hit@3={hits}")
    w("")

    # ---- retrievability control -------------------------------------------
    w("--- 对照：三份目标文档是否**确实可被召回**（否则 0% 可能是索引坏了）---")
    seen_rows: dict[str, list[str]] = {t: [] for t in SHORT}
    for r in rows:
        for t in r["dedup_titles"]:
            if t in seen_rows:
                seen_rows[t].append(f"{r['id']}/{r['mode']}")
    for t, where in seen_rows.items():
        w(f"  {short(t):6} 在矩阵中被召回 {len(where):3} 次"
          + (f"  例: {', '.join(where[:6])}" if where else "   ** 从未出现 **"))
    w("")
    w("结论口径提醒: hit@k 衡量的是**排名**（目标文档是否进入前 k），")
    w("而本节衡量的是**可召回性**。两者都报，才能区分『索引里没有』与『排不上来』。")

    Path(args.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
