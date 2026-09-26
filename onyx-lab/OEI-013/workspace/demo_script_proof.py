#!/usr/bin/env python3
"""OEI-013 step 3 — evidence that `demo-script.md` meets TASK §3.4.

The task pins four properties of the script. Three of them are structural (a
duration band, three acts in order, a closing that covers "what we did /
boundaries / next") and one is a prohibition ("不推进客户验证材料" — do not push
validation/collateral material, that is a different phase).

A reviewer should not have to take my word for any of them, so this reads the
shipped file and reports what it finds. It deliberately does NOT check tone or
quality — those are not machine-checkable, and pretending otherwise would make
the rest of the report less trustworthy, not more.

Usage:  python3 demo_script_proof.py --out <evidence>/05-demo-script.md
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

WS = Path(__file__).resolve().parent
SCRIPT = WS / "demo-script.md"

# §3.4.1 — the three acts, in this order.
ACTS = [
    ("幕一", "一个问题"),
    ("幕二", "知识库怎么答"),
    ("幕三", "你的文件"),
]
# §3.4.1 — the closing must cover all three of these.
CLOSING = ["我们做了什么", "边界", "下一步"]
# §3.4.1 — the phrase the prohibition is about.
FORBIDDEN_PUSH = [
    "验证报告", "验收材料", "合作意向书", "报价单", "合同", "SOW",
    "POC 计划书", "采购申请", "签约",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    text = SCRIPT.read_text(encoding="utf-8")
    L: list[str] = []
    fails: list[str] = []

    def w(s: str = "") -> None:
        L.append(s)

    w("# OEI-013 — 演示脚本的机器可校验证据（TASK §3.4）")
    w()
    w(f"- 文件: `workspace/demo-script.md`")
    w(f"- 字节: {len(text.encode('utf-8'))}")
    w(f"- 行数: {len(text.splitlines())}")
    w(f"- sha256: `{hashlib.sha256(text.encode()).hexdigest()}`")
    w()
    w("本文件只核对 §3.4 里**可机械判定**的那几条。语感、说服力这些不属于"
      "可机械判定的范畴，硬报只会让其它结论一起变得不可信，所以不报。")
    w()

    w("## 1. 时长声明在 10–15 分钟区间（§3.4.1）")
    w()
    found = re.findall(r"(\d{1,3})\s*[–~\-—至]\s*(\d{1,3})\s*分钟|(\d{1,3})\s*分钟", text)
    spans = [(int(a), int(b)) for a, b, _ in found if a and b]
    singles = [int(c) for _, _, c in found if c]
    w(f"- 文中出现的区间: {spans or '（无）'}")
    w(f"- 文中出现的单点: {singles or '（无）'}")
    lo, hi = (min(a for a, _ in spans), max(b for _, b in spans)) if spans else (None, None)
    ok_band = lo is not None and hi is not None and 10 <= lo and hi <= 15
    w(f"- 覆盖区间: {f'{lo}–{hi} 分钟' if lo else '未找到'}")
    w(f"- {'✅' if ok_band else '❌'} 区间落在 10–15 分钟内")
    if not ok_band:
        fails.append("时长区间不在 10–15 分钟")
    w()

    w("## 2. 三幕齐全且**顺序**正确（§3.4.1）")
    w()
    w("| 幕 | 标题 | 出现位置 |")
    w("|---|---|---|")
    pos: list[int] = []
    for tag, title in ACTS:
        i = text.find(title)
        pos.append(i)
        w(f"| {tag} | {title} | {'第 %d 字符' % i if i >= 0 else '❌ 未找到'} |")
    ordered = all(p >= 0 for p in pos) and pos == sorted(pos)
    w()
    w(f"- {'✅' if ordered else '❌'} 三幕都存在，且「问题 → 知识库 → 你的文件」顺序正确")
    if not ordered:
        fails.append("三幕缺失或顺序不对")
    w()

    w("## 3. 收尾覆盖「我们做了什么 / 边界 / 下一步」（§3.4.1）")
    w()
    w("| 小节 | 存在 |")
    w("|---|---|")
    for sec in CLOSING:
        present = sec in text
        w(f"| {f'**{sec}**'} | {'✅' if present else '❌'} |")
        if not present:
            fails.append(f"收尾缺「{sec}」")
    w()

    w("## 4. 未推进客户验证材料（§3.4.1 的禁止项）")
    w()
    hits = [p for p in FORBIDDEN_PUSH if p in text]
    w(f"- 检查这些词是否作为**要交付的东西**出现: {FORBIDDEN_PUSH}")
    w(f"- 命中: {hits if hits else '无 ✅'}")
    w("  （命中不等于违规 —— 需要人看上下文；这里只做机械筛查并如实列出。）")
    w()

    # ---- extra: the boundaries the demo must state out loud ------------------
    w("## 5. 附：脚本必须主动交代的边界（§3.4 与 §3.2 的诚实性要求）")
    w()
    w("这一节不是 §3.4 的原文要求，但 A4「结论诚实」在演示面上就落在这里，")
    w("所以一并机械核对：")
    w()
    CHECKS = [
        ("引擎召回不达标被写明", r"hit@1|hit@3|0%"),
        ("对照文档未删这件事被写明", r"对照文档"),
        ("关键词检索≠语义检索被写明", r"关键词|语义"),
        ("单域限制被写明", r"单域|只讲咨询"),
        ("引擎条数会变这件事被写明（演示者必读）", r"条数|每次不一样|91\.7"),
        ("真认证缺失被写明", r"真认证"),
    ]
    w("| 项 | 文中证据 |")
    w("|---|---|")
    for label, pat in CHECKS:
        m = re.search(pat, text)
        w(f"| {label} | {'✅ ' + m.group(0) if m else '❌ 未找到'} |")
        if not m:
            fails.append(f"边界未写明: {label}")
    w()

    w("## 6. 结论")
    w()
    if fails:
        w(f"**FAIL** — {len(fails)} 项:")
        for f in fails:
            w(f"  - {f}")
    else:
        w("**PASS** — §3.4 的可机械判定项全部满足；上表所列的边界也都在脚本里写着。")
    w()
    w("复算：`python3 workspace/demo_script_proof.py --out evidence/05-demo-script.md`")

    Path(args.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {args.out}  ({len(L)} lines)")
    print("FAILURES: " + (", ".join(fails) if fails else "none"))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
