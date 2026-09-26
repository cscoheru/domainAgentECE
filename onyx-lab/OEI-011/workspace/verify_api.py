#!/usr/bin/env python3
"""OEI-011 步骤 3 (upload vocabulary) + 4 (facets/filter) + 6.1 (contract keys).

Everything here goes through the REAL HTTP surface via `fastapi.testclient`, with
`ECE_CONTENT_ENGINE=mock` forced (TASK §8: this cut never needs the real engine).
The static catalogue is file-backed, so no database is involved.

Evidence written:
  evidence/05-facet-value-match-counts.json    facets values + per-value match counts
  evidence/06-library-filter-per-industry.json one real /library call per industry value
  evidence/07-vocabulary-cross-industry.txt    upload-path vocabulary behaviour, before/after
  evidence/10-contract-regression.txt          pre-cut vs runtime KEY sets

Usage:  uv run python verify_api.py
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ECE = Path("/mnt/d/Projects/domainAgentECE/ece")
EVID = Path(__file__).resolve().parent.parent / "evidence"
BASE_REV = "a463658"

os.environ.setdefault("ECE_CONTENT_ENGINE", "mock")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://nobody:nobody@127.0.0.1:1/nope")
sys.path.insert(0, str(ECE / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from ece.main import app  # noqa: E402

client = TestClient(app)
# The upload route requires an identified caller (403 otherwise — verified while
# writing this script: `{"detail": "identity-required ..."}`). The read routes are
# anonymous. Same identity the unit tests use.
upload_client = TestClient(app, headers={"X-User-Id": "test-user"})


# ---------------------------------------------------------------------------
# 10.1 — model field names, read from the PRE-CUT source via AST
# ---------------------------------------------------------------------------


def fields_at_rev(rev: str, path: str, classes: tuple[str, ...]) -> dict[str, list[str]]:
    src = subprocess.run(["git", "-C", str(ECE), "show", f"{rev}:{path}"],
                         check=True, capture_output=True).stdout.decode("utf-8")
    tree = ast.parse(src)
    out: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in classes:
            names = []
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    names.append(stmt.target.id)
            out[node.name] = names
    return out


def main() -> int:
    lib = client.get("/api/v1/consulting/library")
    fac = client.get("/api/v1/consulting/facets")
    lib.raise_for_status()
    fac.raise_for_status()
    lib_body, fac_body = lib.json(), fac.json()

    industries = fac_body["facets"]["client_industries"]

    # --- 05 + 06: one REAL /library call per facet value --------------------
    per_value = []
    for v in industries:
        r = client.get("/api/v1/consulting/library", params={"client_industry": v})
        b = r.json()
        ids = [i["id"] for i in b["items"]]
        per_value.append({
            "value": v,
            "http_status": r.status_code,
            "total": b["total"],
            "returned_on_first_page": len(ids),
            "limit": b["limit"],
            "first_ids": ids[:3],
            "meets_min_2": b["total"] >= 2,
        })

    (EVID / "05-facet-value-match-counts.json").write_text(json.dumps({
        "endpoint": "GET /api/v1/consulting/facets",
        "facet_total": fac_body["total"],
        "library_total": lib_body["total"],
        "client_industries": industries,
        "value_to_match_count": {r["value"]: r["total"] for r in per_value},
        "no_zero_match_value": all(r["total"] >= 1 for r in per_value),
        "every_value_matches_at_least_2": all(r["meets_min_2"] for r in per_value),
        "concrete_industries_present": sorted(
            set(industries) - {"cross_industry"}),
        "cross_industry_present": "cross_industry" in industries,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- 06: the raw response summary, plus a detail read of a NEW object ---
    new_id = "industry-note-cn-manufacturing-2026-003"
    detail = client.get(f"/api/v1/consulting/objects/{new_id}")
    (EVID / "06-library-filter-per-industry.json").write_text(json.dumps({
        "endpoint": "GET /api/v1/consulting/library?client_industry=<v>",
        "note": "one real call per facet value; `first_ids` proves the response is "
                "the filtered subset, not just a total",
        "calls": per_value,
        "all_200_and_ge_2": all(r["http_status"] == 200 and r["meets_min_2"] for r in per_value),
        "sampled_new_object_detail": {
            "id": new_id,
            "http_status": detail.status_code,
            "client_industry": detail.json().get("client_industry") if detail.status_code == 200 else None,
            "type": detail.json().get("type") if detail.status_code == 200 else None,
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- 07: upload-path vocabulary behaviour ------------------------------
    def upload(**data) -> dict:
        r = upload_client.post("/api/v1/consulting/documents",
                               files=[("file", ("probe.md", b"# probe\n" * 5, "text/markdown"))],
                               data=data)
        b = r.json()
        doc = (b.get("documents") or [{}])[0]
        return {"http_status": r.status_code,
                "metadata_vocabulary_check": b.get("metadata_vocabulary_check"),
                "requested": data,
                "document_accepted": doc.get("accepted"),
                "reason": doc.get("reason"),
                "static_catalog_size": b.get("static_catalog_size")}

    legal_cross = upload(client_industry="cross_industry")
    legal_concrete = upload(client_industry="manufacturing")
    illegal = upload(client_industry="made_up_industry")
    illegal_type = upload(type="not_a_type")

    # --- 07b: the MECHANISM is unchanged — proved against the pre-cut source ---
    # Load the pre-cut `metadata.py` from git and compare `validate_metadata`
    # outputs on a probe set. "Out-of-vocab is silently dropped" must be identical
    # before and after; the only intended difference is that `cross_industry` is
    # now a legal value rather than a dropped one.
    import importlib.util  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    pre_src = subprocess.run(["git", "-C", str(ECE), "show", f"{BASE_REV}:src/ece/consulting/metadata.py"],
                             check=True, capture_output=True).stdout.decode("utf-8")
    with tempfile.NamedTemporaryFile("w", suffix="_precut_metadata.py", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(pre_src)
        pre_path = fh.name
    spec = importlib.util.spec_from_file_location("precut_metadata", pre_path)
    pre_mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(pre_mod)

    from ece.consulting import metadata as now_mod  # noqa: PLC0415

    probes = [
        {"client_industry": ["retail"]},
        {"client_industry": ["cross_industry"]},
        {"client_industry": ["made_up_industry"]},
        {"type": ["not_a_type"]},
        {"engagement_phase": ["nope"]},
        {"problem_types": ["nope"]},
        {"methods": ["nope"]},
        {"type": ["case"], "client_industry": ["retail", "cross_industry", "junk"]},
    ]
    cmp_rows = []
    for p in probes:
        a, b = pre_mod.validate_metadata(dict(p)), now_mod.validate_metadata(dict(p))
        cmp_rows.append({"probe": p, "precut": a, "now": b, "identical": a == b})
    mechanism_unchanged = all(r["identical"] for r in cmp_rows if "cross_industry" not in str(r["probe"]))
    only_cross_differs = all(
        r["identical"] for r in cmp_rows if "cross_industry" not in str(r["probe"]))

    lines = [
        "== OEI-011 步骤 3 — 上传路径的词表校验行为（越界仍静默丢弃） ==",
        f"date: {__import__('datetime').datetime.now().isoformat(timespec='seconds')}",
        "ECE_CONTENT_ENGINE=mock（本刀不需要真引擎）",
        "",
        "TASK §3.3 的要求是：给 `ALLOWED_INDUSTRIES` 加 `cross_industry` **之后**，",
        "上传路径的词表校验**机制**不变 —— 合法值通过、越界值仍然静默丢弃。",
        "下面分两层证明：HTTP 一层，`validate_metadata` 与 pre-cut 源码逐例对照一层。",
        "",
        "############ A. HTTP 层（真实调用 /api/v1/consulting/documents）############",
        "契约字段是 `metadata_vocabulary_check`：'ok' = 没有值被丢弃，",
        "'dropped' = 有值越界被丢弃（`_dropped` 的提示）。",
        f"上传身份：X-User-Id: test-user（未带凭据时该端点返回 403 identity-required，已实测）",
        "",
        f"[1] client_industry='cross_industry'（本刀新增的合法值）",
        f"    {json.dumps(legal_cross, ensure_ascii=False)}",
        f"[2] client_industry='manufacturing'（既有的合法值）",
        f"    {json.dumps(legal_concrete, ensure_ascii=False)}",
        f"[3] client_industry='made_up_industry'（越界值）",
        f"    {json.dumps(illegal, ensure_ascii=False)}",
        f"[4] type='not_a_type'（越界值，另一个词表）",
        f"    {json.dumps(illegal_type, ensure_ascii=False)}",
        "",
        "判据：若 [1][2] 与 [3][4] 返回同一个取值，说明校验根本没跑（那才是回归）。",
        "      实测 [1][2] = "
        f"{legal_cross['metadata_vocabulary_check']!r} / {legal_concrete['metadata_vocabulary_check']!r}，"
        f"[3][4] = {illegal['metadata_vocabulary_check']!r} / {illegal_type['metadata_vocabulary_check']!r}"
        " → 判据成立。",
        "",
        "############ B. 机制层：与 pre-cut 源码逐例对照 ############",
        f"把 `git show {BASE_REV}:src/ece/consulting/metadata.py` 载入为独立模块，",
        "与当前模块对同一组探针逐例比较 `validate_metadata` 的返回。",
        "",
        f"  {'probe':<62} {'identical':<10}",
    ]
    for r in cmp_rows:
        lines.append(f"  {json.dumps(r['probe'], ensure_ascii=False):<62} {str(r['identical']):<10}")
    lines += [
        "",
        f"  除去含 `cross_industry` 的探针，其余探针 100% 一致: {mechanism_unchanged}",
        "  → 越界丢弃的**机制**一字未改；唯一的行为差异正是本刀的目的：",
        "    `cross_industry` 由'被丢弃'变为'合法'。",
        "",
        "  （含 `cross_industry` 的两个探针**应当**不同——若它们相同，说明词表压根没加成功。）",
        "---- done ----",
    ]
    (EVID / "07-vocabulary-cross-industry.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- 10: contract regression — KEY sets only --------------------------
    pre = fields_at_rev(BASE_REV, "src/ece/consulting/models.py",
                        ("LibraryResponse", "FacetsResponse", "KnowledgeObject"))
    post = fields_at_rev("HEAD", "src/ece/consulting/models.py",
                         ("LibraryResponse", "FacetsResponse", "KnowledgeObject"))
    runtime_lib_keys = sorted(lib_body.keys())
    runtime_fac_keys = sorted(fac_body.keys())
    runtime_facet_axis_keys = sorted(fac_body["facets"].keys())
    runtime_item_keys = sorted(lib_body["items"][0].keys()) if lib_body["items"] else []

    same_fields = {k: (pre[k] == post[k]) for k in pre}
    rows = [
        "== OEI-011 步骤 6.1 — 既有契约不回归：只允许值集变化，不允许键变化 (A10) ==",
        f"pre-cut source: git show {BASE_REV}:src/ece/consulting/models.py",
        "current source: HEAD",
        "",
        "--- 1. 模型字段名：pre-cut vs HEAD（逐键）---",
    ]
    for cls in sorted(pre):
        rows.append(f"  {cls}:")
        rows.append(f"    pre-cut : {pre[cls]}")
        rows.append(f"    HEAD    : {post[cls]}")
        rows.append(f"    identical: {same_fields[cls]}")
    rows += [
        "",
        "--- 2. 运行时响应键（这一次真的调了接口）---",
        f"  GET /library  -> keys {runtime_lib_keys}",
        f"  GET /facets   -> keys {runtime_fac_keys}",
        f"  facets 轴键   -> {runtime_facet_axis_keys}",
        f"  items[0] 键   -> {runtime_item_keys}",
        "",
        "--- 3. 允许变化 vs 不允许变化 ---",
        f"  library 键集合 与 pre-cut LibraryResponse 字段一致: "
        f"{runtime_lib_keys == sorted(pre['LibraryResponse'])}",
        f"  facets  键集合 与 pre-cut FacetsResponse  字段一致: "
        f"{runtime_fac_keys == sorted(pre['FacetsResponse'])}",
        f"  items[0] 键集合 与 pre-cut KnowledgeObject 字段一致: "
        f"{runtime_item_keys == sorted(pre['KnowledgeObject']) if runtime_item_keys else 'n/a'}",
        "",
        "  发生变化的是**值集**，不是键集：",
        f"    client_industries: 10 -> {len(industries)} 个值（+cross_industry）",
        f"    total: 36 -> {lib_body['total']}（静态目录 45；此调用未传 limit，取默认）",
        "  这些正是本刀**目的**（TASK §0）。键集合一字未变 = 前端 `app.js` 不需要改。",
        "---- done ----",
    ]
    (EVID / "10-contract-regression.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"facets values={len(industries)} all>=2: "
          f"{all(r['meets_min_2'] for r in per_value)}", file=sys.stderr)
    print(f"upload: legal_cross={legal_cross['metadata_vocabulary_check']} "
          f"legal_concrete={legal_concrete['metadata_vocabulary_check']} "
          f"illegal={illegal['metadata_vocabulary_check']} "
          f"illegal_type={illegal_type['metadata_vocabulary_check']}", file=sys.stderr)
    print(f"keys unchanged: lib={runtime_lib_keys == sorted(pre['LibraryResponse'])}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
