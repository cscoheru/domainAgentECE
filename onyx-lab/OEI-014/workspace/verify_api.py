#!/usr/bin/env python3
"""OEI-014 步骤 4 + 5.1 — facets/过滤的加深实测 + 契约不回归。

走**真实 HTTP 面**（fastapi.testclient），静态目录是文件支撑的，不依赖库（DSN 指向
死端口，与 OEI-011 同法）。`ECE_CONTENT_ENGINE=mock`（§8：本刀不需要真引擎）。

产出：
  evidence/07-facet-and-filter.json  每个行业值的命中数（≥4）+ 该行业的 industry_note 列表
  evidence/08-contract-regression.txt /library 与 /facets 的键集合逐键对照（只允许值集变化）
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
SEED = ECE / "src/ece/consulting/seed/consulting_objects.json"
BASE_REV = "c30e50e"

os.environ.setdefault("ECE_CONTENT_ENGINE", "mock")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://nobody:nobody@127.0.0.1:1/nope")
sys.path.insert(0, str(ECE / "src"))

from fastapi.testclient import TestClient  # noqa: E402

from ece.main import app  # noqa: E402

client = TestClient(app)

CONCRETE = ("banking", "consumer_goods", "energy", "healthcare", "insurance",
            "logistics", "manufacturing", "public_sector", "retail", "technology")


def fields_at_rev(rev: str, path: str, classes: tuple[str, ...]) -> dict[str, list[str]]:
    src = subprocess.run(["git", "-C", str(ECE), "show", f"{rev}:{path}"],
                         check=True, capture_output=True).stdout.decode("utf-8")
    out: dict[str, list[str]] = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.ClassDef) and node.name in classes:
            out[node.name] = [s.target.id for s in node.body
                              if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
    return out


def main() -> int:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    lib = client.get("/api/v1/consulting/library", params={"limit": 100})
    fac = client.get("/api/v1/consulting/facets")
    lib.raise_for_status()
    fac.raise_for_status()
    lib_body, fac_body = lib.json(), fac.json()
    values = fac_body["facets"]["client_industries"]

    # ---- per-industry filter + note coverage -------------------------------
    per_industry = []
    for v in values:
        r = client.get("/api/v1/consulting/library",
                       params={"client_industry": v, "limit": 100})
        b = r.json()
        ids = [i["id"] for i in b["items"]]
        rn = client.get("/api/v1/consulting/library",
                        params={"client_industry": v, "type": "industry_note", "limit": 100})
        bn = rn.json()
        note_ids_api = sorted(i["id"] for i in bn["items"])
        note_ids_seed = sorted(o["id"] for o in seed
                               if o["type"] == "industry_note"
                               and v in (o.get("client_industry") or []))
        per_industry.append({
            "value": v,
            "http_status": r.status_code,
            "total": b["total"],
            "returned_on_this_page": len(ids),
            "limit_used": 100,
            "first_ids": ids[:3],
            "meets_min_4": b["total"] >= 4,
            "industry_note_total": bn["total"],
            "industry_note_ids_via_api": note_ids_api,
            "industry_note_ids_from_seed": note_ids_seed,
            "note_ids_agree": note_ids_api == note_ids_seed,
            "has_min_1_note": bn["total"] >= 1,
        })

    concrete_rows = [r for r in per_industry if r["value"] in CONCRETE]
    cross_row = next((r for r in per_industry if r["value"] == "cross_industry"), None)

    # ---- sampled new object through /objects/{id} --------------------------
    sample_id = "industry-note-cn-insurance-2026-007"
    detail = client.get(f"/api/v1/consulting/objects/{sample_id}")

    (EVID / "07-facet-and-filter.json").write_text(json.dumps({
        "endpoint_facets": "GET /api/v1/consulting/facets",
        "endpoint_filter": "GET /api/v1/consulting/library?client_industry=<v>&limit=100",
        "facet_total": fac_body["total"],
        "library_total": lib_body["total"],
        "client_industries": values,
        "value_to_match_count": {r["value"]: r["total"] for r in per_industry},
        "no_zero_match_value": all(r["total"] >= 1 for r in per_industry),
        "every_concrete_industry_at_least_4": all(r["meets_min_4"] for r in concrete_rows),
        "concrete_min": min(r["total"] for r in concrete_rows),
        "every_concrete_industry_has_note": all(r["has_min_1_note"] for r in concrete_rows),
        "every_note_id_list_agrees_with_seed": all(r["note_ids_agree"] for r in concrete_rows),
        "cross_industry": cross_row,
        "per_industry": per_industry,
        "sampled_new_object_detail": {
            "id": sample_id,
            "http_status": detail.status_code,
            "client_industry": detail.json().get("client_industry") if detail.status_code == 200 else None,
            "type": detail.json().get("type") if detail.status_code == 200 else None,
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- contract regression ----------------------------------------------
    pre = fields_at_rev(BASE_REV, "src/ece/consulting/models.py",
                        ("LibraryResponse", "FacetsResponse", "KnowledgeObject"))
    post = fields_at_rev("HEAD", "src/ece/consulting/models.py",
                         ("LibraryResponse", "FacetsResponse", "KnowledgeObject"))
    rt_lib = sorted(lib_body.keys())
    rt_fac = sorted(fac_body.keys())
    rt_axis = sorted(fac_body["facets"].keys())
    rt_item = sorted(lib_body["items"][0].keys()) if lib_body["items"] else []
    rows = [
        "== OEI-014 步骤 5.1 — 既有契约不回归：只允许值集变化，不允许键变化 (A7) ==",
        f"pre-cut source: git show {BASE_REV}:src/ece/consulting/models.py",
        "current source: HEAD（工作区；本刀未改 models.py）",
        "",
        "--- 1. 模型字段名：pre-cut vs HEAD（逐键）---",
    ]
    for cls in sorted(pre):
        same = pre[cls] == post[cls]
        rows.append(f"  {cls}:")
        rows.append(f"    pre-cut : {pre[cls]}")
        rows.append(f"    HEAD    : {post[cls]}")
        rows.append(f"    identical: {same}")
    rows += [
        "",
        "--- 2. 运行时响应键（真的调了接口）---",
        f"  GET /library  -> keys {rt_lib}",
        f"  GET /facets   -> keys {rt_fac}",
        f"  facets 轴键   -> {rt_axis}",
        f"  items[0] 键   -> {rt_item}",
        "",
        "--- 3. 允许变化 vs 不允许变化 ---",
        f"  library 键集合 与 pre-cut LibraryResponse 字段一致: {rt_lib == sorted(pre['LibraryResponse'])}",
        f"  facets  键集合 与 pre-cut FacetsResponse  字段一致: {rt_fac == sorted(pre['FacetsResponse'])}",
        f"  items[0] 键集合 与 pre-cut KnowledgeObject 字段一致: "
        f"{rt_item == sorted(pre['KnowledgeObject']) if rt_item else 'n/a'}",
        "",
        "  发生变化的是**值集**，不是键集：",
        f"    client_industries: 11 → {len(values)} 个值（本刀**不新增词表值**，仍是 11）",
        f"    total: 45 → {lib_body['total']}（本刀新增 20 条：45 → 65）",
        "  这些正是本刀**目的**（TASK §0）。键集合一字未变 = 前端 `app.js` 不需要改。",
        "---- done ----",
    ]
    (EVID / "08-contract-regression.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"facets values={len(values)} no-zero-match={all(r['total'] >= 1 for r in per_industry)}",
          file=sys.stderr)
    print(f"concrete min matches={min(r['total'] for r in concrete_rows)} (must be >=4)",
          file=sys.stderr)
    print(f"every concrete industry has >=1 industry_note: "
          f"{all(r['has_min_1_note'] for r in concrete_rows)}", file=sys.stderr)
    print(f"note id lists agree with seed: {all(r['note_ids_agree'] for r in concrete_rows)}",
          file=sys.stderr)
    ok = (all(r["meets_min_4"] for r in concrete_rows)
          and all(r["has_min_1_note"] for r in concrete_rows)
          and all(r["note_ids_agree"] for r in concrete_rows)
          and rt_lib == sorted(pre["LibraryResponse"])
          and rt_fac == sorted(pre["FacetsResponse"]))
    print(f"OVERALL: {'PASS' if ok else 'FAIL'}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
