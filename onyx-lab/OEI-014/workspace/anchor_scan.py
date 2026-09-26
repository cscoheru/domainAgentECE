#!/usr/bin/env python3
"""OEI-014 步骤 0 — 词边界安全的行业锚点扫描器。

它回答一个问题：**这个对象真的"属于"这个行业吗？** 依据必须是一条锚点 ——
一个出现在该对象**自己的 `title` 或 `summary`** 里、且**够具体**的行业词。

为什么需要它（OEI-014 §3.3 / §1.3）：`metadata.py:298 _INDUSTRY_KEYWORDS` 是给
"上传时猜元数据"用的松表，它按**子串**匹配，而且扫描范围包含 `practice` /
`methods` / `problem_types`。用它来判断"有没有行业锚点"会产生假阳性 —— 已知 4 例：

  methodology-value-chain-003      `practice` 里的 `supply_chain` 被 `"ai"` 命中 → technology
  risk-check-data-availability-001 `problem_types` 里的 `data_availability` 同样被 `"ai"` 命中
  methodology-benchmarking-public-010 `methods` 里的 `public_benchmark` 被 `"public"` 命中
  methodology-lean-waste-walk-005  summary 里"用于**制造业**与服务运营场景"被 `"制造"` 命中

最后一条值得注意：它的假命中**就在 summary 里**，所以"只扫 title/summary"**不足以**
解决问题 —— 还必须要求锚点词**够具体**。`制造业`/`制造` 在这里是"讲给哪些行业听"的
场景范围，不是"这条内容发生在制造业里"。

因此本扫描器比 `_INDUSTRY_KEYWORDS` 严三档：
  ① 范围：只扫 `title` + `summary`（§3.3.1）；
  ② 词边界：ASCII 关键词一律 `\\b...\\b`（§3.3.2，`"ai"` 因此不再命中 `supply_ch-ai-n`）；
  ③ 词表：只收**具体**行业词。`ai` / `public` / `tech` / `制造(业)` / `供应链` / `运输`
     这些"可作普通词义或长度≤2"的词**一律不作为锚点判据**（§3.3.2 后半句）—— 要表达
     科技行业请用 `人工智能` / `软件` / `云平台`，要表达公共部门请用 `政务` / `事业单位`，
     要表达制造业请用 `工厂` / `产线` / `车间`。

`--loose` 用旧规则（`_INDUSTRY_KEYWORDS` + 子串 + 全字段）再扫一遍，作为**对照**：
同一批对象，松规则报出假阳性，严规则报"无锚点"。这正是"扫描器有牙"的证明 ——
一个永远报"无锚点"的扫描器和"什么都没扫"没有区别，所以本脚本还带自注入故障自检。

用法：
  uv run python anchor_scan.py                     # 严规则，扫当前 seed，打印报告
  uv run python anchor_scan.py --loose             # 对照：旧松规则
  uv run python anchor_scan.py --json out.json     # 同时落一份机器可读结果
  uv run python anchor_scan.py --require FILE      # FILE 里列出的 id 必须每条都有锚点，
                                                   #   否则退出码 1（A3 的机检入口）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"

# ---------------------------------------------------------------------------
# 1. 严规则锚点词表（每个具体行业一组**具体**词）
# ---------------------------------------------------------------------------
# ASCII 词用词边界匹配；中文词用子串（CJK 没有词边界，但下面这些词本身就是
# 多字具体词，不会被更长的词"意外包含"到别的行业含义里 —— 这一点用
# test_teeth() 的故障注入来守）。
ANCHOR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "banking": ("银行", "城商行", "农商行", "信贷", "个贷", "对公", "网点", "存贷", "手机银行"),
    "consumer_goods": ("消费品", "快消", "快消品", "经销商", "铺货", "动销", "品牌商"),
    "energy": ("能源", "电力", "电网", "油气", "光伏", "风电", "储能", "双碳", "发电"),
    "healthcare": ("医疗", "医院", "患者", "临床", "诊疗", "门诊", "住院", "药械", "药品"),
    "insurance": ("保险", "寿险", "财险", "核保", "理赔", "精算", "保费", "保单", "投保"),
    "logistics": ("物流", "仓储", "配送", "快递", "干线", "仓配", "运力", "末端配送"),
    "manufacturing": ("制造企业", "工厂", "产线", "车间", "良率", "生产线", "工单",
                      "工艺", "设备维护", "设备综合效率"),
    "public_sector": ("政府", "政务", "事业单位", "国企", "机关", "公共服务",
                      "一网通办", "政务大厅", "财政"),
    "retail": ("零售", "门店", "坪效", "连锁", "便利店", "商超", "导购", "货架"),
    "technology": ("科技企业", "软件", "互联网", "人工智能", "SaaS", "云平台",
                   "研发团队", "数据平台"),
}

CONCRETE_INDUSTRIES: tuple[str, ...] = tuple(ANCHOR_KEYWORDS)

# §3.3.2 明确点名、**不得单独作为锚点判据**的词。这张表的作用是**可审计**：
# 它把"为什么不把 ai 当锚点"写成数据，而不是藏在某段 if 里。`--loose` 会用到
# `_INDUSTRY_KEYWORDS`（含这些词），严规则则完全不看它们。
WEAK_TOKENS: dict[str, str] = {
    "ai": "长度≤2 的 ASCII；是 supply_chain / availability 的子串",
    "public": "可作普通词义（公开/公共）；是 public_benchmark 的一部分",
    "tech": "可作普通词义；且常作别的词的前缀",
    "制造 / 制造业": "可作'场景范围'讲（'用于制造业与服务运营场景'），不指内容所属行业",
    "供应链 / supply_chain": "通用概念（任何行业都有供应链），且含 `ai` 子串",
    "运输": "通用活动（任何行业都可能运输），单用不足以判定物流行业",
    "金融": "跨银行/保险/证券的宽词，且常作'金融科技'修饰语",
}

# 旧松规则（`metadata.py` 的 `_INDUSTRY_KEYWORDS`），仅为 `--loose` 对照而复制。
# 复制而不是 import：这样对照实验不依赖被测模块当前的实现（若有人改了
# metadata.py 的表，对照关系不该悄悄跟着变）。
LOOSE_INDUSTRY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("retail", ("零售", "retail", "门店", "坪效")),
    ("banking", ("银行", "bank", "城商行", "金融", "信贷")),
    ("manufacturing", ("制造", "manufactur", "工厂", "供应链")),
    ("technology", ("科技", "tech", "saas", "软件", "互联网", "ai")),
    ("healthcare", ("医疗", "health", "医院", "药")),
    ("logistics", ("物流", "logistic", "运输", "快递")),
    ("energy", ("能源", "energy", "电力", "油气")),
    ("insurance", ("保险", "insurance", "精算")),
    ("consumer_goods", ("消费品", "consumer", "快消", "fmcg")),
    ("public_sector", ("政府", "public", "事业单位", "国企", "机关")),
)
LOOSE_FIELDS = ("title", "summary", "practice", "problem_types", "methods",
                "deliverables", "outcomes")

# §3.3.3 的回归样例：这 4 条**必须**被严规则报为"无锚点"。
REGRESSION_SAMPLES: tuple[str, ...] = (
    "methodology-value-chain-003",
    "methodology-lean-waste-walk-005",
    "methodology-benchmarking-public-010",
    "risk-check-data-availability-001",
)

_ASCII_RE = re.compile(r"^[\x00-\x7f]+$")


def _is_ascii(s: str) -> bool:
    return bool(_ASCII_RE.match(s))


def anchor_hits(text: str, industry: str) -> list[dict[str, str]]:
    """Return every anchor hit of `industry` in `text` (strict rule)."""
    hits: list[dict[str, str]] = []
    for kw in ANCHOR_KEYWORDS[industry]:
        if _is_ascii(kw):
            # §3.3.2: ASCII keywords match on WORD BOUNDARIES only.
            if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
                hits.append({"keyword": kw, "mode": "ascii_word_boundary"})
        else:
            # CJK: substring. Multi-char specific terms only (see ANCHOR_KEYWORDS).
            if kw in text:
                hits.append({"keyword": kw, "mode": "cjk_substring"})
    return hits


def scan_object(obj: dict, strict: bool) -> list[dict]:
    """All anchor evidence for one object: one row per (industry, field)."""
    rows: list[dict] = []
    industries = [i for i in (obj.get("client_industry") or [])
                  if i in CONCRETE_INDUSTRIES]
    if strict:
        for ind in industries:
            for field in ("title", "summary"):
                for hit in anchor_hits(obj.get(field) or "", ind):
                    rows.append({"industry": ind, "field": field,
                                 "keyword": hit["keyword"], "mode": hit["mode"]})
    else:
        # ---- loose control: metadata.py's table, substring, ALL fields ----
        joined = "\n".join(
            " ".join(str(v) for v in ([obj.get(f)] if isinstance(obj.get(f), str)
                                      else (obj.get(f) or [])))
            for f in LOOSE_FIELDS
        ).lower()
        for vocab, kws in LOOSE_INDUSTRY_KEYWORDS:
            for kw in kws:
                if kw.lower() in joined:
                    rows.append({"industry": vocab, "field": "(all fields, loose)",
                                 "keyword": kw, "mode": "substring_loose"})
    return rows


def loose_only_false_positives(obj: dict, strict_rows: list[dict]) -> list[dict]:
    """Loose hits for industries the STRICT scan did NOT confirm. These are the
    false positives that make the loose rule unusable as an anchor test."""
    strict_inds = {r["industry"] for r in strict_rows}
    return [r for r in scan_object(obj, strict=False) if r["industry"] not in strict_inds]


# ---------------------------------------------------------------------------
# 2. Self-injected faults — a scanner must be shown to be able to say "yes"
# ---------------------------------------------------------------------------
def test_teeth(seed_objects: list[dict]) -> tuple[bool, list[str]]:
    """Inject known-good and known-bad objects; the scanner must classify both
    correctly. Without this, 'no anchor found' could just mean 'nothing ran'."""
    log: list[str] = []
    ok = True

    good = {
        "id": "__injected_positive__", "type": "case",
        "title": "某城商行网点产能评估",          # 城商行 + 网点 → banking
        "summary": "为某中型城商行评估网点产能与柜面流程。",
        "client_industry": ["banking"],
    }
    rows = scan_object(good, strict=True)
    got = {r["industry"] for r in rows}
    passed = got == {"banking"}
    ok &= passed
    log.append(f"  注入正例 __injected_positive__ (title 含 '城商行'+'网点') "
               f"-> 锚点行业 {sorted(got)}  {'PASS' if passed else '*** FAIL ***'}")

    bad = {
        "id": "__injected_negative__", "type": "methodology",
        "title": "价值链拆解方法",
        "summary": "公开价值链模型, 覆盖 supply_chain 与 data_availability 口径。",
        "client_industry": ["technology", "public_sector"],
    }
    rows_b = scan_object(bad, strict=True)
    loose_b = scan_object(bad, strict=False)
    loose_inds = {r["industry"] for r in loose_b}
    passed_b = (not rows_b) and bool(loose_inds)
    ok &= passed_b
    log.append(f"  注入反例 __injected_negative__ (只有 supply_ch**ai**n / "
               f"data_av**ai**lability) -> 严规则锚点 {sorted({r['industry'] for r in rows_b})} "
               f"(应为空)，松规则却报了 {sorted(loose_inds)}  {'PASS' if passed_b else '*** FAIL ***'}")

    # The 4 real regression samples must all be anchor-free under the strict rule.
    by = {o["id"]: o for o in seed_objects}
    for rid in REGRESSION_SAMPLES:
        if rid not in by:
            ok = False
            log.append(f"  *** 回归样例 {rid} 不在 seed 里 —— FAIL ***")
            continue
        rows_r = scan_object(by[rid], strict=True)
        passed_r = not rows_r
        ok &= passed_r
        log.append(f"  回归样例 {rid:<34} 严规则锚点 {sorted({r['industry'] for r in rows_r})}"
                   f" (应为空)  {'PASS' if passed_r else '*** FAIL ***'}")
    return ok, log


# ---------------------------------------------------------------------------
# 3. Report
# ---------------------------------------------------------------------------
def build_report(seed_objects: list[dict], require_ids: list[str] | None) -> tuple[str, dict, int]:
    strict_by_id = {o["id"]: scan_object(o, strict=True) for o in seed_objects}
    anchored_ids = {i for i, r in strict_by_id.items() if r}
    teeth_ok, teeth_log = test_teeth(seed_objects)

    L: list[str] = []
    L.append("== OEI-014 步骤 0 — 行业锚点扫描器（词边界安全）+ 4 条假阳性回归 ==")
    L.append("")
    L.append(f"扫描器源码: {Path(__file__).resolve()}")
    L.append(f"被扫文件  : {SEED}")
    L.append(f"对象总数  : {len(seed_objects)}")
    L.append("")
    L.append("---- 规则（§3.3）----")
    L.append("① 范围：锚点必须出现在对象**自己的 title 或 summary**里；")
    L.append("   `practice` / `methods` / `problem_types` / 关键词表推导**不算**。")
    L.append("② 词边界：ASCII 关键词用 \\b...\\b（大小写不敏感）。")
    L.append("③ 词表：只收具体行业词。以下词**不得单独作为锚点判据**（§3.3.2）：")
    for tok, why in WEAK_TOKENS.items():
        L.append(f"     - `{tok}`：{why}")
    L.append("")
    L.append(f"严规则锚点词表（{len(ANCHOR_KEYWORDS)} 个具体行业）：")
    for ind in CONCRETE_INDUSTRIES:
        L.append(f"  {ind:<16} {list(ANCHOR_KEYWORDS[ind])}")
    L.append("")

    L.append("---- 自注入故障自检（证明扫描器能说【是】，也能说【否】）----")
    L.extend(teeth_log)
    L.append(f"  自检总判定: {'PASS' if teeth_ok else '*** FAIL ***'}")
    L.append("")

    L.append("---- 对照：4 条已知假阳性，松规则 vs 严规则 ----")
    by = {o["id"]: o for o in seed_objects}
    L.append(f"  {'id':<36} {'松规则(旧)报出':<28} {'严规则(本扫描器)'}")
    for rid in REGRESSION_SAMPLES:
        o = by.get(rid)
        if not o:
            L.append(f"  {rid:<36} *** NOT IN SEED ***")
            continue
        loose = scan_object(o, strict=False)
        loose_s = ", ".join(sorted({f"{r['industry']}←{r['keyword']}" for r in loose})) or "(none)"
        strict = scan_object(o, strict=True)
        strict_s = ", ".join(sorted({r["industry"] for r in strict})) or "无锚点 ✓"
        L.append(f"  {rid:<36} {loose_s:<28} {strict_s}")
    L.append("")
    L.append("  上表读法：松规则在 `practice`/`methods`/`problem_types` 或子串上命中，")
    L.append("  严规则一律报【无锚点】 —— 这 4 条**本来就是通用方法/通用清单**，")
    L.append("  这正是它们保持 `cross_industry` 的理由。")
    L.append("")

    L.append("---- 全量：既有对象里严规则能认出锚点的（参考；既有 45 条不改）----")
    for o in seed_objects:
        rows = strict_by_id[o["id"]]
        inds = sorted({r["industry"] for r in rows})
        if inds:
            det = "; ".join(
                f"{r['industry']}@{r['field']}←{r['keyword']}"
                for r in sorted(rows, key=lambda r: (r["industry"], r["field"], r["keyword"]))
            )
            L.append(f"  {o['id']:<46} {det}")
    L.append(f"  -> 严规则可认出锚点的对象: {len(anchored_ids)}/{len(seed_objects)}")
    L.append("")
    no_ind = [o["id"] for o in seed_objects if not (o.get("client_industry") or [])]
    unanchored_concrete = sorted(
        o["id"] for o in seed_objects
        if [i for i in (o.get("client_industry") or []) if i in CONCRETE_INDUSTRIES]
        and o["id"] not in anchored_ids
    )
    L.append(f"  没有任何行业的对象: {len(no_ind)}  {no_ind}")
    L.append(f"  带了具体行业但严规则在 title/summary 找不到锚点的既有对象: "
             f"{len(unanchored_concrete)}")
    for i in unanchored_concrete:
        L.append(f"    - {i}")
    L.append("")
    L.append("  ⚠️ 读法（不许含糊）：上面这些既有对象**不是本刀的问题** —— OEI-011 的标注")
    L.append("  规则允许依据落在 `practice`/`methods`/`problem_types`（OEI-011 §3.1.6），")
    L.append("  严格度本来就低于本刀 §3.3 对**新增对象**的要求。本刀只新增、不改它们，")
    L.append("  所以这里如实录出、不做任何回溯改动。")
    L.append("")

    result = {
        "scanner": str(Path(__file__).resolve()),
        "seed": str(SEED),
        "object_count": len(seed_objects),
        "teeth_self_test_passed": teeth_ok,
        "regression_samples": {
            rid: {
                "strict_anchors": sorted({r["industry"] for r in strict_by_id.get(rid, [])}),
                "loose_hits": sorted({f"{r['industry']}<-{r['keyword']}"
                                      for r in scan_object(by[rid], strict=False)}) if rid in by else None,
                "strict_says_no_anchor": not strict_by_id.get(rid),
            } for rid in REGRESSION_SAMPLES
        },
        "objects_with_strict_anchor": sorted(anchored_ids),
        "concrete_but_no_strict_anchor": unanchored_concrete,
    }

    exit_code = 0 if teeth_ok else 1
    if require_ids:
        L.append("---- A3 机检：以下新增对象必须每条都有锚点 ----")
        missing = []
        for oid in require_ids:
            rows = strict_by_id.get(oid)
            if rows is None:
                missing.append(oid)
                L.append(f"  {oid:<46} *** 不在 seed 里 ***")
            elif not rows:
                missing.append(oid)
                L.append(f"  {oid:<46} *** 无锚点 ***")
            else:
                det = "; ".join(sorted({f"{r['industry']}@{r['field']}<-{r['keyword']}"
                                        for r in rows}))
                L.append(f"  {oid:<46} {det}")
        L.append(f"  -> {len(require_ids) - len(missing)}/{len(require_ids)} 有锚点"
                 f"{'' if not missing else '  *** 缺: ' + ', '.join(missing) + ' ***'}")
        result["required_ids_missing_anchor"] = missing
        if missing:
            exit_code = 1
    L.append("---- done ----")
    return "\n".join(L) + "\n", result, exit_code


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loose", action="store_true",
                    help="用旧松规则（子串 + 全字段）再扫一遍做对照")
    ap.add_argument("--json", metavar="PATH", default=None)
    ap.add_argument("--require", metavar="FILE", default=None,
                    help="每行一个 id；这些 id 必须都有锚点，否则退出码 1")
    args = ap.parse_args(argv)

    seed_objects = json.loads(SEED.read_text(encoding="utf-8"))
    require_ids = None
    if args.require:
        require_ids = [ln.strip() for ln in Path(args.require).read_text(
            encoding="utf-8").splitlines() if ln.strip()]

    text, result, code = build_report(seed_objects, require_ids)

    if args.loose:
        print("== 对照模式 --loose：只打印松规则命中（全字段 + 子串）==", file=sys.stderr)
        for o in seed_objects:
            rows = scan_object(o, strict=False)
            if rows:
                inds = sorted({f"{r['industry']}<-{r['keyword']}" for r in rows})
                print(f"  {o['id']:<46} {inds}", file=sys.stderr)

    print(text, end="")
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    if not result["teeth_self_test_passed"]:
        print("ANCHOR SCAN FAILED: self-test did not pass", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
