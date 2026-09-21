#!/usr/bin/env python3
"""Build the FOUNDATION_REUSE_* handoff packs from the three source documents.

Why this exists
---------------
Codex cannot take file uploads and its input has a size limit, so this study has to
be pasted as text. The first attempt produced a single 183 KB bundle, which exceeded
that limit.

The fix is deliberately NOT to summarise: the source documents include an evidence
appendix whose whole value is verbatim `path:line` excerpts, and paraphrasing them
would downgrade evidence into hearsay. So the packs are SPLIT BY SECTION while
carrying every byte of the sources through unchanged.

Only PACK_0 is abridged, and it abridges by *dropping whole sections* — never by
rewriting one. Its header says so.

Usage:
    uv run python docs/research/_build_foundation_reuse_packs.py [--verify-only]

Output:
    FOUNDATION_REUSE_PACK_0_MINIMAL.md      (~20 KB, optional last resort)
    FOUNDATION_REUSE_PACK_1_CONCLUSIONS.md  (~74 KB, STUDY + MATRIX, send first)
    FOUNDATION_REUSE_PACK_2_EVIDENCE_A.md   (~69 KB, CODE_NOTES §0-§3)
    FOUNDATION_REUSE_PACK_3_EVIDENCE_B.md   (~39 KB, CODE_NOTES §4-§12)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAR = "=" * 78
DASH = "-" * 78
GENERATED = "2026-09-21"

STUDY = "FOUNDATION_REUSE_STUDY.md"
MATRIX = "FOUNDATION_REUSE_MATRIX.md"
NOTES = "FOUNDATION_REUSE_CODE_NOTES.md"


def sections(name: str) -> tuple[str, list[str]]:
    """Split a document at top-level `## ` headings.

    Returns (preamble_before_first_heading, [section_text, ...]) where each section
    text starts at its `## ` line and runs to the next one.
    """
    text = (HERE / name).read_text(encoding="utf-8")
    starts = [m.start() for m in re.finditer(r"^## ", text, re.M)]
    if not starts:
        return text, []
    head = text[: starts[0]]
    secs = [
        text[s : (starts[i + 1] if i + 1 < len(starts) else len(text))]
        for i, s in enumerate(starts)
    ]
    return head, secs


def build(out_name: str, title: str, parts: list[tuple[str, list[str], str]], note: str) -> int:
    out = [f"# {title}\n", note, "", BAR]
    for src, segs, desc in parts:
        out += [BAR, f"# 来源文件：`{src}`", f"> {desc}", BAR, ""]
        for seg in segs:
            out += [seg.rstrip("\n"), "", DASH, ""]
    blob = "\n".join(out)
    (HERE / out_name).write_text(blob, encoding="utf-8")
    return len(blob.encode("utf-8"))


def generate() -> dict[str, int]:
    study_h, study_s = sections(STUDY)
    matrix_h, matrix_s = sections(MATRIX)
    notes_h, notes_s = sections(NOTES)
    stamp = f"> 仓库 `domainAgentECE` ｜ 目录 `docs/research/` ｜ 生成 {GENERATED}"

    sizes = {}
    sizes["0_MINIMAL"] = build(
        "FOUNDATION_REUSE_PACK_0_MINIMAL.md",
        "Foundation Reuse Study — 最小裁定版（仅在整包超限时使用）",
        [
            (STUDY, [study_s[0], study_s[10], study_s[11]],
             "§1 Executive Summary · §11 最终判断（指令 §20 的 A–F）· §12 报告状态"),
            (MATRIX, [matrix_s[2]], "§3 主矩阵（Capability × Candidate × Reuse Level）"),
        ],
        "> ⚠️ **这是删节版，不是全文合并。** 只含裁定所需的最小集合：结论、A–F 终判、报告状态、主矩阵。\n"
        "> 删节方式是**整节丢弃，绝不改写任何一节**。被删部分见合并包 1–3 与三份源文件。\n"
        f"> **仅在整包超出 Codex 输入上限时使用这一份。**\n>\n{stamp}",
    )
    sizes["1_CONCLUSIONS"] = build(
        "FOUNDATION_REUSE_PACK_1_CONCLUSIONS.md",
        "Foundation Reuse Study — 合并包 1/4：结论与矩阵",
        [
            (STUDY, [study_h] + study_s, "全文（§1 Executive Summary … §13 Codex 裁定与归档修正）"),
            (MATRIX, [matrix_h] + matrix_s, "全文（复用等级定义 · 能力归属 · 主矩阵 · 逐候选网格）"),
        ],
        "> **这是 4 份合并包中的第 1 份（结论层），先发这一份。**\n"
        "> 第 2、3 份是逐候选的代码级证据附录（`path:line` + 原文片段），按需查阅。\n"
        "> 正文与仓库内源文件**逐字节一致**，未做任何转述或删减。\n>\n"
        f"{stamp}",
    )
    sizes["2_EVIDENCE_A"] = build(
        "FOUNDATION_REUSE_PACK_2_EVIDENCE_A.md",
        "Foundation Reuse Study — 合并包 2/4：代码级证据 A（方法与 Tier-1）",
        [(NOTES, [notes_h] + notes_s[0:4],
          "§0 方法与可复现性（含候选坐标核实）· §1 HugAgentOS · §2 Semantica · §3 TrustGraph")],
        "> **这是 4 份合并包中的第 2 份（证据层 A）**：方法与三个 Tier-1 候选的源码级考察。\n"
        "> 正文与仓库内源文件**逐字节一致**。\n>\n"
        f"{stamp}",
    )
    sizes["3_EVIDENCE_B"] = build(
        "FOUNDATION_REUSE_PACK_3_EVIDENCE_B.md",
        "Foundation Reuse Study — 合并包 3/4：代码级证据 B（Tier-2 与横切结论）",
        [(NOTES, notes_s[4:],
          "§4 OpenEAAP · §5 GSearchAI · §6 qKnow · §7 KnowledgeOps · §8 mcp-agent · "
          "§9 DataLogicEngine · §10 Tier-2 交叉结论 · §11 Evidence 字段级横切分析 · §12 九候选裁决汇总")],
        "> **这是 4 份合并包中的第 3 份（证据层 B）**：六个 Tier-2 候选与两个横切结论节。\n"
        "> 正文与仓库内源文件**逐字节一致**。\n>\n"
        f"{stamp}",
    )
    return sizes


def verify() -> bool:
    """Every section of every source must appear verbatim in PACK 1-3; and PACK 1-3
    must contain no body line that does not exist in the sources."""
    pack_names = [
        "FOUNDATION_REUSE_PACK_1_CONCLUSIONS.md",
        "FOUNDATION_REUSE_PACK_2_EVIDENCE_A.md",
        "FOUNDATION_REUSE_PACK_3_EVIDENCE_B.md",
    ]
    blob = "\n".join((HERE / n).read_text(encoding="utf-8") for n in pack_names)
    assert blob.strip(), "comparison baseline is EMPTY — that is a bug, not a pass"

    ok = True
    print("== 覆盖性：每份源文件的每一节是否逐字出现在 PACK 1–3 ==")
    for name in (STUDY, MATRIX, NOTES):
        head, secs = sections(name)
        segs = [head] + secs
        missed = [i for i, s in enumerate(segs) if s.rstrip("\n") not in blob]
        ok &= not missed
        print(f"  {name:38s} 段数={len(segs):3d}  {'OK' if not missed else f'缺段 {missed}'}")

    src_lines = "\n".join((HERE / n).read_text(encoding="utf-8") for n in (STUDY, MATRIX, NOTES))
    extra = [
        ln for ln in blob.split("\n")
        if ln.strip() and not ln.startswith(("#", "> "))
        and ln.strip() not in (BAR, DASH)
        and ln not in src_lines
    ]
    ok &= not extra
    print(f"== 反向：PACK 1–3 中源文件里不存在的正文行 = {len(extra)} ==")
    for ln in extra[:10]:
        print("   +", ln[:100])

    mt = (HERE / "FOUNDATION_REUSE_PACK_0_MINIMAL.md").read_text(encoding="utf-8")
    sh, ss = sections(STUDY)
    mh, ms = sections(MATRIX)
    print("== 最小裁定版：所选四节是否逐字一致 ==")
    for label, seg in (("STUDY §1", ss[0]), ("STUDY §11", ss[10]), ("STUDY §12", ss[11]), ("MATRIX §3", ms[2])):
        same = seg.rstrip("\n") in mt
        ok &= same
        print(f"  {label:12s} {'OK' if same else 'FAIL'}")
    print()
    print("校验结论：" + ("全部通过 ✅" if ok else "存在失败 ❌"))
    return ok


if __name__ == "__main__":
    if "--verify-only" not in sys.argv:
        for k, v in generate().items():
            print(f"  PACK_{k:14s} {v:8,} bytes  ({v / 1024:.1f} KB)")
        print()
    sys.exit(0 if verify() else 1)
