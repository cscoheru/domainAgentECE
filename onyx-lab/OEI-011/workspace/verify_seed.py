#!/usr/bin/env python3
"""OEI-011 步骤 2 — coverage targets, the new-object list, and the A2 scan.

Reads the REAL seed file (not a draft) and writes:
  evidence/03-new-objects-list.json       id / type / industry / 目标理由
  evidence/04-coverage-targets.json       before/after for every A4 target
  workspace/02a-a2-violation-scan.txt     the A2 scan, printed as raw text

A2 requires: every object's client_industry is non-empty and lands in
ALLOWED_INDUSTRIES ∪ {cross_industry}; and `case` / `industry_note` never carry
`cross_industry`. The scan is written to be re-runnable, not to be believed.

Usage:  uv run python verify_seed.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"
EVID = Path(__file__).resolve().parent.parent / "evidence"
WS = Path(__file__).resolve().parent
BASE_REV = "a463658"
CROSS = "cross_industry"

sys.path.insert(0, str(ECE / "src"))
from ece.consulting import metadata as md  # noqa: E402

# Why each new object exists. Kept next to the data so the reason travels with it.
RATIONALE = {
    "industry-note-cn-manufacturing-2026-003": "industry_note 2→3；manufacturing 1→2",
    "industry-note-cn-logistics-2026-004": "industry_note 3→4；logistics 1→2",
    "industry-note-cn-healthcare-2026-005": "industry_note 4→5；healthcare 1→2",
    "industry-note-cn-energy-2026-006": "industry_note 5→6；energy 1→2",
    "case-technology-data-platform-011": "technology 1→2（case 必须落在具体行业，不得 cross_industry）",
    "case-public-sector-service-window-012": "public_sector 1→2（同上）",
    "case-insurance-underwriting-013": "insurance 1→2（同上）",
    "risk-check-timeline-slippage-005": "risk_check 4→5（通用，故 cross_industry）",
    "risk-check-benefit-realization-006": "risk_check 5→6（通用，故 cross_industry）",
}


def counts(objects: list[dict]) -> dict:
    return {
        "total": len(objects),
        "type_counts": dict(sorted(Counter(o["type"] for o in objects).items())),
        "industry_counts": dict(sorted(Counter(v for o in objects for v in o["client_industry"]).items())),
    }


def main() -> int:
    base = json.loads(subprocess.run(
        ["git", "-C", str(ECE), "show", f"{BASE_REV}:src/ece/consulting/seed/consulting_objects.json"],
        check=True, capture_output=True).stdout.decode("utf-8"))
    cur = json.loads(SEED.read_text(encoding="utf-8"))
    base_ids = {o["id"] for o in base}
    new = [o for o in cur if o["id"] not in base_ids]

    # --- 03: the new-object list ------------------------------------------
    (EVID / "03-new-objects-list.json").write_text(json.dumps({
        "step": "OEI-011 step 2",
        "baseline_rev": BASE_REV,
        "new_object_count": len(new),
        "threshold_note": "TASK §3.2 suggests 8-12; A4 requires >= 8 (total >= 44).",
        "objects": [
            {"id": o["id"], "type": o["type"], "client_industry": o["client_industry"],
             "engagement_phase": o["engagement_phase"], "source_origin": o["source_origin"],
             "rationale": RATIONALE.get(o["id"], "?")}
            for o in new
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- 04: before / after for every A4 target ---------------------------
    b, a = counts(base), counts(cur)
    concrete = sorted(md.ALLOWED_INDUSTRIES - {CROSS})
    industry_ok = {i: a["industry_counts"].get(i, 0) for i in concrete}
    (EVID / "04-coverage-targets.json").write_text(json.dumps({
        "step": "OEI-011 step 2",
        "before": b, "after": a,
        "before_industries_with_exactly_1": sorted(
            i for i, n in b["industry_counts"].items() if n == 1),
        "after_per_concrete_industry": industry_ok,
        "a4": {
            "total >= 44": (a["total"], a["total"] >= 44),
            "every concrete industry >= 2": (min(industry_ok.values()), min(industry_ok.values()) >= 2),
            "industry_note >= 6": (a["type_counts"]["industry_note"], a["type_counts"]["industry_note"] >= 6),
            "risk_check >= 6": (a["type_counts"]["risk_check"], a["type_counts"]["risk_check"] >= 6),
            "cross_industry >= 10": (a["industry_counts"].get(CROSS, 0),
                                     a["industry_counts"].get(CROSS, 0) >= 10),
        },
        "all_targets_met": all([
            a["total"] >= 44, min(industry_ok.values()) >= 2,
            a["type_counts"]["industry_note"] >= 6, a["type_counts"]["risk_check"] >= 6,
            a["industry_counts"].get(CROSS, 0) >= 10]),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- A2 scan ----------------------------------------------------------
    allowed = md.ALLOWED_INDUSTRIES | {CROSS}
    lines = [
        "== OEI-011 A2 — client_industry coverage + vocabulary scan (REAL seed file) ==",
        f"seed: {SEED}",
        f"vocabulary: ALLOWED_INDUSTRIES ({len(md.ALLOWED_INDUSTRIES)}) = {sorted(md.ALLOWED_INDUSTRIES)}",
        f"            plus the only added value: {CROSS!r}",
        f"objects scanned: {len(cur)}   (baseline {BASE_REV}: {len(base)})",
        "",
        "--- check 1: every object's client_industry is non-empty ---",
    ]
    empty = [o["id"] for o in cur if not o["client_industry"]]
    lines.append(f"  objects with an EMPTY client_industry: {len(empty)}" +
                 (f"  {empty}" if empty else "   (expected 0)"))
    lines += ["", "--- check 2: every value lands in the vocabulary ---"]
    bad = [(o["id"], v) for o in cur for v in o["client_industry"] if v not in allowed]
    lines.append(f"  values outside the vocabulary: {len(bad)}" + (f"  {bad}" if bad else "   (expected 0)"))
    lines += ["", "--- check 3: case / industry_note never carry cross_industry (§3.1.3) ---"]
    banned = [o["id"] for o in cur
              if o["type"] in ("case", "industry_note") and CROSS in o["client_industry"]]
    lines.append(f"  violations: {len(banned)}" + (f"  {banned}" if banned else "   (expected 0)"))
    lines += ["", "--- check 4: the scan has teeth (it is shown detecting injected faults) ---"]
    probe = [{"id": "probe-empty", "type": "case", "client_industry": []},
             {"id": "probe-bad-value", "type": "case", "client_industry": ["not_a_real_industry"]},
             {"id": "probe-banned-cross", "type": "industry_note", "client_industry": [CROSS]}]
    caught = (
        sum(1 for o in probe if not o["client_industry"]),
        sum(1 for o in probe for v in o["client_industry"] if v not in allowed),
        sum(1 for o in probe if o["type"] in ("case", "industry_note") and CROSS in o["client_industry"]),
    )
    lines.append(f"  inject 3 faults -> checks report (empty, out-of-vocab, banned-cross) = {caught}")
    lines.append("  -> all three non-zero, so the three zeroes above are 'nothing found',"
                 " not 'nothing looked for'.")
    lines += ["", "--- per-type / per-industry tallies ---",
              f"  type_counts: {a['type_counts']}",
              f"  industry_counts: {a['industry_counts']}",
              "", "---- done ----"]
    (WS / "02a-a2-violation-scan.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"new={len(new)} total={a['total']} empty={len(empty)} bad={len(bad)} banned={len(banned)}",
          file=sys.stderr)
    return 0 if not (empty or bad or banned) else 1


if __name__ == "__main__":
    raise SystemExit(main())
