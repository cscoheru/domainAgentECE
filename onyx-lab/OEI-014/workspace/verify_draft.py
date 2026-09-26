#!/usr/bin/env python3
"""OEI-014 步骤 2/3 之间的守门：把「既有 45 + 草稿 20」拼成内存目录，
用**真实的那两个闸门测试函数**先跑一遍，全绿才允许写真实种子文件。

为什么不直接写进文件再跑测试：OEI-011 的教训是"写错了再回滚"没有必要 ——
先在内存里过闸门，写盘只做一次。**但最终证据仍必须是在真实文件上跑出来的**，
所以本脚本的输出只是"允许写盘"的判据，不作为 A4 的收口证据（收口证据是
`05-seed-gates-raw.txt`，那是在真实文件上跑的）。

两个测试模块里读文件的用例（`test_seed_bundle_is_valid_json` /
`test_catalog_can_load_seed_without_error`）**不能**用于内存校验，这里明确列出、
不当成"跑过了"。

用法：uv run python verify_draft.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
SEED = ECE / "src" / "ece" / "consulting" / "seed" / "consulting_objects.json"
WS = Path(__file__).resolve().parent
sys.path.insert(0, str(ECE / "src"))


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


schema_t = _load(ECE / "tests/unit/test_consulting_seed_schema.py", "seed_schema_t")
disc_t = _load(ECE / "tests/unit/test_consulting_seed_discipline.py", "seed_disc_t")
anchor = _load(WS / "anchor_scan.py", "anchor_scan")

from ece.consulting import metadata as md  # noqa: E402
from ece.consulting.models import KnowledgeObject  # noqa: E402
from ece.consulting.service import ConsultingCatalog  # noqa: E402

# 读文件的用例：内存校验用不了，必须在真实文件上跑（步骤 3）。
FILE_BOUND_TESTS = ("test_seed_bundle_is_valid_json",
                    "test_catalog_can_load_seed_without_error")


def main() -> int:
    base = json.loads(SEED.read_text(encoding="utf-8"))
    draft = json.loads((WS / "draft-new-objects.json").read_text(encoding="utf-8"))
    new = draft["objects"]

    lines: list[str] = []
    failures: list[str] = []

    def check(name: str, fn) -> None:
        try:
            fn()
            lines.append(f"  PASS  {name}")
        except AssertionError as exc:
            failures.append(name)
            lines.append(f"  FAIL  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures.append(name)
            lines.append(f"  FAIL  {name}: {type(exc).__name__}: {exc}")

    lines.append(f"既有: {len(base)} 条 | 草稿: {len(new)} 条 | 合并: {len(base) + len(new)} 条")
    lines.append("")

    # ---- id 冲突 ----
    base_ids = {o["id"] for o in base}
    dup_with_base = sorted(base_ids & {o["id"] for o in new})
    check("id 与既有 45 条不冲突", lambda: (_ for _ in ()).throw(
        AssertionError(f"冲突: {dup_with_base}")) if dup_with_base else None)

    # ---- schema 闸门（真实测试函数）----
    combined_raw = base + new
    combined_objs = [KnowledgeObject(**o) for o in combined_raw]
    cat = ConsultingCatalog(combined_objs)
    check("schema::test_every_seed_record_passes_pydantic_schema",
          lambda: schema_t.test_every_seed_record_passes_pydantic_schema(combined_raw))
    check("schema::test_type_enum_is_exactly_one_of_six",
          lambda: schema_t.test_type_enum_is_exactly_one_of_six(combined_objs))
    check("schema::test_source_origin_enum_is_exactly_one_of_four",
          lambda: schema_t.test_source_origin_enum_is_exactly_one_of_four(combined_objs))
    check("schema::test_required_text_fields_are_nonempty",
          lambda: schema_t.test_required_text_fields_are_nonempty(combined_objs))

    # ---- 内容纪律闸门（真实测试函数）----
    for tname in ("test_summary_and_title_are_chinese",
                  "test_no_real_or_competitor_org_names",
                  "test_synthetic_confidence_requires_synthetic_variant",
                  "test_founder_case_records_are_marked_as_such",
                  "test_no_precision_numeric_outcome_claims"):
        check(f"discipline::{tname}", lambda t=tname: getattr(disc_t, t)(cat))

    # ---- 数量下限（真实测试函数）----
    count_t = _load(ECE / "tests/unit/test_consulting_seed_count.py", "seed_count_t")
    for tname in ("test_total_object_count_meets_minimum",
                  "test_type_distribution_matches_documented_targets",
                  "test_source_origin_covers_at_least_three_distinct_values",
                  "test_no_duplicate_object_ids"):
        check(f"count::{tname}", lambda t=tname: getattr(count_t, t)(cat))

    # ---- 词表：新增对象的 5 个受约束字段必须落在 ALLOWED_* 内 ----
    def vocab_check() -> None:
        for o in new:
            assert o["type"] in md.ALLOWED_TYPES, f"{o['id']} type={o['type']}"
            for ph in o["engagement_phase"]:
                assert ph in md.ALLOWED_PHASES, f"{o['id']} phase={ph}"
            for ind in o["client_industry"]:
                assert ind in md.ALLOWED_INDUSTRIES, f"{o['id']} industry={ind}"
            for pt in o["problem_types"]:
                assert pt in md.ALLOWED_PROBLEM_TYPES, f"{o['id']} problem_type={pt}"
            for m in o["methods"]:
                assert m in md.ALLOWED_METHODS, f"{o['id']} method={m}"
            assert o["source_origin"] in (
                "founder_case", "methodology_note", "synthetic_variant", "licensed_public")
            assert o["confidence"] in ("high", "medium", "synthetic")
            assert o["review_state"] in ("approved", "draft")
    check("vocab::新增对象 5 个词表字段全部合法", vocab_check)

    # ---- 锚点：每条新增对象必须有锚点；4 条回归样例必须仍无锚点 ----
    def anchor_check() -> None:
        for o in new:
            rows = anchor.scan_object(o, strict=True)
            assert rows, f"{o['id']} 在 title/summary 里没有具体行业锚点"
    check("anchor::20 条新增对象每条都有锚点", anchor_check)

    def regression_check() -> None:
        by = {o["id"]: o for o in combined_raw}
        for rid in anchor.REGRESSION_SAMPLES:
            assert not anchor.scan_object(by[rid], strict=True), \
                f"回归样例 {rid} 竟然有锚点了"
    check("anchor::4 条假阳性回归样例仍报无锚点", regression_check)

    def teeth_check() -> None:
        ok, _ = anchor.test_teeth(combined_raw)
        assert ok, "扫描器自检未通过"
    check("anchor::扫描器自检（正例能报、反例能拒）", teeth_check)

    # ---- 目标达成（§3.1 硬门槛，内存预演）----
    def targets() -> None:
        import collections
        t = collections.Counter(o["type"] for o in combined_raw)
        per = collections.Counter(i for o in combined_raw for i in o["client_industry"])
        notes = collections.Counter(
            i for o in combined_raw if o["type"] == "industry_note"
            for i in o["client_industry"])
        assert 65 <= len(combined_raw) <= 70, f"total={len(combined_raw)}"
        for ind in anchor.CONCRETE_INDUSTRIES:
            assert per[ind] >= 4, f"{ind}={per[ind]} < 4"
            assert notes[ind] >= 1, f"{ind} 无 industry_note"
        assert t["deliverable_template"] >= 6, t["deliverable_template"]
        assert per["cross_industry"] >= 10, per["cross_industry"]
        lines.append(f"  total={len(combined_raw)} types={dict(sorted(t.items()))}")
        lines.append(f"  per_industry={ {k: per[k] for k in sorted(per)} }")
        lines.append(f"  industry_note per industry={ {k: notes[k] for k in sorted(notes)} }")
    check("targets::§3.1 五项硬门槛（内存预演）", targets)

    lines.append("")
    lines.append("注意：以下两个读文件的用例**没有**在本次内存校验里跑（它们读的是当前"
                 "真实文件，即旧 45 条），必须在步骤 3 写入后用真实文件跑：")
    for t in FILE_BOUND_TESTS:
        lines.append(f"  (未跑) {t}")
    lines.append("")
    if failures:
        lines.append(f"结论: FAIL —— {len(failures)} 项未过: {failures}")
    else:
        lines.append("结论: PASS —— 允许写入真实种子文件（写盘后仍须在真实文件上重跑闸门）。")
    print("\n".join(lines))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
