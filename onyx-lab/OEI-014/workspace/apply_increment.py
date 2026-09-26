#!/usr/bin/env python3
"""OEI-014 步骤 3 — 把 20 条新对象**只追加**到真实种子文件，并产出 A1 证明。

本刀是**纯新增**刀（§8：既有 45 条的所有字段逐字节不变、不删、不重排），所以
写盘前的守卫比 OEI-011 更严：

  ① 序列化器往返：`json.dumps(cur, ensure_ascii=False, indent=2)` 必须**逐字节**
     复原当前文件（否则重写会顺手重排未改动的对象）；
  ② 当前文件必须与 `git show c30e50e:<seed>` **完全一致**（开工前没有别的漂移）；
  ③ 写盘后逐条对 A1：既有 45 条**全部字段**的规范化 sha256 与 c30e50e 逐条相等
     （不是"除某字段外"，是本刀一个字都不该动）。

产出：
  evidence/02-new-objects-list.json      20 条（id/type/industry/理由）
  evidence/03-anchor-basis.json          每条新增对象的锚点依据（锚点词 + 所在字段 + 原句）
  evidence/04-coverage-before-after.json 前后对照（总数/每行业/类型/note 覆盖）
  evidence/01b-existing-45-unchanged-hashes.txt  A1 的逐条哈希对照
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"
BASE_REV = "c30e50e"          # OEI-011 的 HEAD = 本刀的前置基线
WS = Path(__file__).resolve().parent
EVID = WS.parent / "evidence"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


anchor = _load(WS / "anchor_scan.py", "anchor_scan")


def canon(obj: dict) -> str:
    """Canonical JSON of the WHOLE object (all fields, sorted keys)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def baseline() -> list[dict]:
    blob = subprocess.run(
        ["git", "-C", str(ECE), "show",
         f"{BASE_REV}:src/ece/consulting/seed/consulting_objects.json"],
        check=True, capture_output=True).stdout.decode("utf-8")
    return json.loads(blob)


_SENT_SPLIT = re.compile(r"(?<=[。;；])")


def anchor_basis(obj: dict) -> list[dict]:
    """For each concrete industry the object carries: the anchor hit(s), the
    field they live in, and the SENTENCE they live in (so a human can check)."""
    out: list[dict] = []
    for ind in [i for i in (obj.get("client_industry") or [])
                if i in anchor.CONCRETE_INDUSTRIES]:
        hits = anchor.scan_object(obj, strict=True)
        hits = [h for h in hits if h["industry"] == ind]
        for h in hits:
            field = h["field"]
            text = obj[field]
            if field == "title":
                sentence = text
            else:
                segs = [s for s in _SENT_SPLIT.split(text) if h["keyword"] in s]
                sentence = segs[0].strip() if segs else text
            out.append({
                "industry": ind,
                "anchor_keyword": h["keyword"],
                "anchor_field": field,
                "match_mode": h["mode"],
                "anchor_sentence": sentence,
                "is_substring_of_that_field": h["keyword"] in obj[field],
                # 机器判据：锚点必须落在**自己**的 title/summary 里
                "in_own_title_or_summary": h["keyword"] in obj["title"] + obj["summary"],
            })
    return out


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    base = baseline()
    draft = json.loads((WS / "draft-new-objects.json").read_text(encoding="utf-8"))
    new_objects = draft["objects"]
    rationale = draft["rationale"]

    cur_raw = SEED.read_text(encoding="utf-8")
    cur = json.loads(cur_raw)

    # ---- guard ① serialiser round-trip ----
    assert json.dumps(cur, ensure_ascii=False, indent=2) == cur_raw, (
        "seed 文件不能被 ensure_ascii=False/indent=2 逐字节复原 —— 重写会重排未改动的对象")
    # ---- guard ② no drift since the baseline ----
    assert [o["id"] for o in cur] == [o["id"] for o in base] and \
           all(canon(a) == canon(b) for a, b in zip(cur, base, strict=True)), (
        f"当前文件与 {BASE_REV} 不一致 —— 先查清再动手")

    new_ids = {o["id"] for o in new_objects}
    assert not (new_ids & {o["id"] for o in base}), "新增 id 与既有 id 冲突"

    combined = base + new_objects
    if apply:
        SEED.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {SEED}: {len(combined)} objects", file=sys.stderr)
    else:
        print("--dry-run：未写盘", file=sys.stderr)

    # ---- A1: whole-object hashes, 45/45 ----
    # In a dry run the file on disk is still the OLD 45, so reading it back would
    # "prove" 45/45 trivially. Use the would-be file content instead, and say so.
    now = json.loads(SEED.read_text(encoding="utf-8")) if apply else combined
    now_raw = SEED.read_text(encoding="utf-8") if apply else json.dumps(
        combined, ensure_ascii=False, indent=2)
    lines, all_eq = [], True
    for i, (b, n) in enumerate(zip(base, now[:len(base)], strict=True), 1):
        assert b["id"] == n["id"], (b["id"], n["id"])
        hb, hn = sha(canon(b)), sha(canon(n))
        ok = hb == hn
        all_eq &= ok
        lines.append(
            f"[{i:2d}/{len(base)}] {b['id']}\n"
            f"        {BASE_REV}(baseline) whole-object sha256 = {hb}\n"
            f"        current            whole-object sha256 = {hn}   "
            f"{'EQUAL' if ok else '*** DIFFERENT ***'}")
    (EVID / "01b-existing-45-unchanged-hashes.txt").write_text("\n".join([
        "== OEI-014 A1 — 既有 45 条【全字段】逐字节不变（对照 c30e50e）==",
        f"MODE: {'真实写盘后的文件' if apply else '*** DRY RUN — 文件未写，本文件不该作为证据 ***'}",
        f"baseline: git show {BASE_REV}:src/ece/consulting/seed/consulting_objects.json",
        "hash: sha256 of the canonical JSON of the ENTIRE object (sorted keys, compact",
        "      separators). 本刀是纯新增刀，所以是**整对象**相等，不是'除某字段外'相等。",
        "      写盘前已验证：seed 文件能被子自身的序列化器逐字节复原（否则排版会变），",
        "      且写盘时既有 45 条是按原 dict 原样拼接的（不是重新构造）。",
        "      为防'新条目与旧条目的一刀切'被混淆，这里也比较了文件长度：",
        f"        baseline 文件对象数 = {len(base)}；current 文件对象数 = {len(now)}",
        "",
        *lines,
        "",
        (f"RESULT: 既有 {len(base)}/{len(base)} 条整对象 sha256 相等 —— 一个字都没动。"
         if all_eq else "RESULT: MISMATCH —— 见上方 *** DIFFERENT ***"),
        "",
        "文件级 diff 形态（证明只有新增）：",
        "  $ git diff --numstat -- src/ece/consulting/seed/consulting_objects.json",
        "    见 evidence/01c-seed-diff-stat.txt（由本脚本外的命令落盘）",
        "---- done ----",
    ]) + "\n", encoding="utf-8")

    # ---- 02 new-objects-list ----
    (EVID / "02-new-objects-list.json").write_text(json.dumps({
        "step": "OEI-014 step 2/3",
        "baseline_rev": BASE_REV,
        "baseline_total": len(base),
        "new_object_count": len(new_objects),
        "total_after": len(combined),
        "objects": [{
            "id": o["id"], "type": o["type"],
            "client_industry": o["client_industry"],
            "engagement_phase": o["engagement_phase"],
            "source_origin": o["source_origin"],
            "rationale": rationale.get(o["id"], ""),
        } for o in new_objects],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- 03 anchor-basis ----
    rows, unanchored = [], []
    for o in new_objects:
        basis = anchor_basis(o)
        if not basis:
            unanchored.append(o["id"])
        rows.append({"id": o["id"], "type": o["type"],
                     "client_industry": o["client_industry"],
                     "anchors": basis,
                     "every_industry_anchored": bool(basis)})
    (EVID / "03-anchor-basis.json").write_text(json.dumps({
        "step": "OEI-014 §3.3 锚点依据表",
        "rule": ("锚点必须出现在**该对象自己的** title 或 summary 里，且必须是具体行业词；"
                 "ai / public / tech / 制造(业) / 供应链 等弱词不作为判据（见 "
                 "workspace/anchor_scan.py 的 WEAK_TOKENS 与 ANCHOR_KEYWORDS）。"),
        "objects_without_anchor": unanchored,
        "all_new_objects_anchored": not unanchored,
        "rows": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- 04 coverage before/after ----
    per_b = Counter(i for o in base for i in o["client_industry"])
    per_a = Counter(i for o in combined for i in o["client_industry"])
    typ_b = Counter(o["type"] for o in base)
    typ_a = Counter(o["type"] for o in combined)
    note_b = Counter(i for o in base if o["type"] == "industry_note" for i in o["client_industry"])
    note_a = Counter(i for o in combined if o["type"] == "industry_note" for i in o["client_industry"])
    concrete = anchor.CONCRETE_INDUSTRIES
    a2 = {
        "total 65<=N<=70": [len(combined), 65 <= len(combined) <= 70],
        "every concrete industry >= 4": [min(per_a[i] for i in concrete),
                                         all(per_a[i] >= 4 for i in concrete)],
        "every concrete industry has >=1 industry_note": [
            min(note_a[i] for i in concrete), all(note_a[i] >= 1 for i in concrete)],
        "deliverable_template >= 6": [typ_a["deliverable_template"],
                                      typ_a["deliverable_template"] >= 6],
        "cross_industry >= 10": [per_a["cross_industry"], per_a["cross_industry"] >= 10],
    }
    (EVID / "04-coverage-before-after.json").write_text(json.dumps({
        "step": "OEI-014 step 3",
        "before": {"total": len(base), "type_counts": dict(sorted(typ_b.items())),
                   "industry_counts": dict(sorted(per_b.items())),
                   "industry_note_per_industry": dict(sorted(note_b.items()))},
        "after": {"total": len(combined), "type_counts": dict(sorted(typ_a.items())),
                  "industry_counts": dict(sorted(per_a.items())),
                  "industry_note_per_industry": dict(sorted(note_a.items()))},
        "concrete_industries_gaining_a_note": sorted(
            set(note_a) - set(note_b) | {i for i in note_a if note_a[i] > note_b.get(i, 0)}),
        "a2": a2,
        "all_targets_met": all(v[1] for v in a2.values()),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"A1 whole-object identical: {len(base)}/{len(base)} -> {all_eq}", file=sys.stderr)
    print(f"A3 新增对象有锚点: {len(new_objects) - len(unanchored)}/{len(new_objects)}"
          f"{'' if not unanchored else f'  缺: {unanchored}'}", file=sys.stderr)
    print(f"A2 全部达标: {all(v[1] for v in a2.values())}  {a2}", file=sys.stderr)
    print(f"total: {len(base)} -> {len(combined)}", file=sys.stderr)
    return 0 if all_eq and not unanchored and all(v[1] for v in a2.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
