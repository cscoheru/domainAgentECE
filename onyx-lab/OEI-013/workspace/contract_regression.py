#!/usr/bin/env python3
"""OEI-013 step 4a — contract non-regression (A8), machine-checkable.

A8 says the `/library` and `/facets` KEY SETS must not change. "Key set" has
three levels here, and a check that stops at one of them is not evidence:

  (1) STRUCTURAL — the response models at the OEI-012 commit (`4a67c28`) vs the
      working tree. Parsed with `ast` out of `git show`, so no import, no venv,
      and no chance of "it still matches because I changed both sides".
  (2) WIRE — the JSON keys the running API actually returns. Models can be right
      while a handler drops or adds a key.
  (3) CATALOG — `/facets` returns the six facet slugs as DICT KEYS, which is a
      key set the response model does not describe (the model types it as a
      plain `dict`). Those six names come from `service._FACET_KEYS`, so they are
      read from the source and compared to the wire.

Shapes this resolves (learned by looking, not assumed):
  LibraryResponse   : items, total, limit, offset, facets, engine_items, engine_status
  KnowledgeObject   : id, type, title, ...           (the `items[]` shape)
  EngineItem        : engine_doc_id, title, ...      (the `engine_items[]` shape)
  FacetsResponse    : facets, total                  (`facets` values are list[str])

Usage:  python3 contract_regression.py --base http://127.0.0.1:8766 --out <file>
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ECE_DIR = Path("/mnt/d/Projects/domainAgentECE/ece")
BASE_REF = "4a67c28"                 # OEI-012's commit — the last ruled-PASS contract
MODELS = "src/ece/consulting/models.py"
SERVICE = "src/ece/consulting/service.py"


def _fields_from(src: str, model: str) -> list[str] | None:
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ClassDef) and node.name == model:
            return [s.target.id for s in node.body
                    if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
    return None


def model_fields(ref: str | None, model: str) -> list[str] | None:
    """Field names of `model` as declared at `ref` ('HEAD' or None = working tree)."""
    if ref is None:
        src = (ECE_DIR / MODELS).read_text()
    else:
        src = subprocess.run(["git", "show", f"{ref}:{MODELS}"], cwd=ECE_DIR,
                             capture_output=True, text=True, check=True).stdout
    return _fields_from(src, model)


def facet_keys_at(ref: str | None) -> list[str]:
    """The six facet slugs, read out of `service._FACET_KEYS`."""
    if ref is None:
        src = (ECE_DIR / SERVICE).read_text()
    else:
        src = subprocess.run(["git", "show", f"{ref}:{SERVICE}"], cwd=ECE_DIR,
                             capture_output=True, text=True, check=True).stdout
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == "_FACET_KEYS":
            return list(ast.literal_eval(node.value))
    raise SystemExit("_FACET_KEYS not found")


def fetch_json(base: str, path: str) -> tuple[int, object]:
    req = urllib.request.Request(base + path, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read())
        except Exception:
            return exc.code, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8766")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    base = args.base.rstrip("/")
    L: list[str] = []
    failures: list[str] = []

    def w(s: str = "") -> None:
        L.append(s)

    def check(label: str, cond: bool, detail: str = "") -> None:
        w(f"- {'✅' if cond else '❌'} {label}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures.append(label)

    w("# OEI-013 step 4a — 契约不回归（A8）")
    w()

    # ---- 1. structural ------------------------------------------------------
    w(f"## 1. 结构性：`{MODELS}` 在 `{BASE_REF}` 与工作区之间")
    w()
    diff = subprocess.run(["git", "diff", BASE_REF, "--", MODELS],
                          cwd=ECE_DIR, capture_output=True, text=True).stdout
    w("```")
    w(f"$ git diff {BASE_REF} -- {MODELS}      # 工作区，不是 HEAD —— 本刀尚未 commit")
    w(diff.rstrip() if diff.strip() else "(空 — 文件逐字节未改)")
    w("```")
    w()
    check(f"`{MODELS}` 相对 {BASE_REF} 零 diff → 字段集合不可能变", not diff.strip())

    w("### 逐模型核对（AST，不 import、不建 venv）")
    w()
    w(f"| 模型 | {BASE_REF} | 工作区 | 集合相同 |")
    w("|---|---|---|---|")
    for model in ("LibraryResponse", "KnowledgeObject", "EngineItem", "FacetsResponse"):
        old, new = model_fields(BASE_REF, model), model_fields(None, model)
        same = old is not None and new is not None and set(old) == set(new)
        w(f"| `{model}` | {len(old) if old else 0} | {len(new) if new else 0} | "
          f"{'✅' if same else '❌'} |")
        if not same:
            failures.append(f"{model} 字段集合变了")
    w()

    fk_old, fk_new = facet_keys_at(BASE_REF), facet_keys_at(None)
    check(f"`_FACET_KEYS` 六个 slug 未变", tuple(fk_old) == tuple(fk_new),
          f"{fk_new}")
    w()

    # ---- 2. wire: /library -------------------------------------------------
    w("## 2. 线上：运行中的 API 实际吐出的键")
    w()
    w(f"- base: `{base}`   （评测库实例，非演示实例）")
    w()
    status, lib = fetch_json(base, "/api/v1/consulting/library?limit=2")
    check("`GET /api/v1/consulting/library` → 200", status == 200, f"HTTP {status}")
    if not isinstance(lib, dict):
        L.append("**无法继续：/library 未返回 JSON 对象**")
        Path(args.out).write_text("\n".join(L) + "\n", encoding="utf-8")
        print("FAILED (no library json)", file=sys.stderr)
        return 1

    want = set(model_fields(BASE_REF, "LibraryResponse") or [])
    got = set(lib.keys())
    w("```")
    w("GET /api/v1/consulting/library?limit=2")
    w(json.dumps({k: (f"<{len(v)} items>" if isinstance(v, list) else v)
                  for k, v in lib.items()}, ensure_ascii=False, indent=2))
    w("```")
    w()
    check("`/library` 顶层键集合与 baseline 模型一致", got == want,
          f"多 `{sorted(got - want)}` / 少 `{sorted(want - got)}`" if got != want
          else f"{sorted(got)}")

    items = lib.get("items") or []
    item_keys = set().union(*(set(i) for i in items)) if items else set()
    want_item = set(model_fields(BASE_REF, "KnowledgeObject") or [])
    check(f"`items[]` 键集合（{len(item_keys)} 键 × {len(items)} 行）与 baseline 一致",
          bool(items) and item_keys == want_item,
          f"多 `{sorted(item_keys - want_item)}` / 少 `{sorted(want_item - item_keys)}`"
          if item_keys != want_item else "")

    eng = lib.get("engine_items") or []
    eng_keys = set().union(*(set(i) for i in eng)) if eng else set()
    want_eng = set(model_fields(BASE_REF, "EngineItem") or [])
    check(f"`engine_items[]` 键集合与 baseline 一致（本次 engine_items {len(eng)} 行）",
          not eng or eng_keys == want_eng,
          f"{sorted(eng_keys)}" if eng else "（空 — mock 引擎，无行可核）")
    w()

    # ---- 3. /facets: dict keys ARE the contract ----------------------------
    status_f, fr = fetch_json(base, "/api/v1/consulting/facets")
    check("`GET /api/v1/consulting/facets` → 200", status_f == 200, f"HTTP {status_f}")
    if not isinstance(fr, dict):
        failures.append("/facets 非对象")
    else:
        want_fr = set(model_fields(BASE_REF, "FacetsResponse") or [])
        got_fr = set(fr.keys())
        check("`/facets` 顶层键集合与 baseline 模型一致", got_fr == want_fr,
              f"{sorted(got_fr)}")
        facets = fr.get("facets")
        if not isinstance(facets, dict):
            failures.append("/facets.facets 非对象")
        else:
            got_fk = set(facets.keys())
            w()
            w("```")
            w("GET /api/v1/consulting/facets")
            w(json.dumps({k: (f"<{len(v)} values>" if isinstance(v, list) else v)
                          for k, v in facets.items()}, ensure_ascii=False, indent=2))
            w("```")
            w()
            check(f"`/facets.facets` 键集合 == `_FACET_KEYS`（{len(fk_new)} 个 slug）",
                  got_fk == set(fk_new),
                  f"多 `{sorted(got_fk - set(fk_new))}` / 少 `{sorted(set(fk_new) - got_fk)}`"
                  if got_fk != set(fk_new) else f"{sorted(got_fk)}")
            empty = [k for k, v in facets.items() if isinstance(v, list) and not v]
            check("每个 facet 列表非空（既有断言 `test_facets_have_six_documented_keys` 不变）",
                  not empty, f"空的: {empty}")
            w(f"- `total = {fr.get('total')}`")
    w()

    # ---- 4. verdict --------------------------------------------------------
    w("## 3. 结论")
    w()
    if failures:
        w(f"**FAIL** — {len(failures)} 项不通过:")
        for f in failures:
            w(f"  - {f}")
    else:
        w(f"**PASS** — 响应模型相对 `{BASE_REF}` 零 diff；`/library` 与 `/facets` 的"
          "各级键集合（顶层 / 数组元素 / facets dict）均未变。")

    Path(args.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {args.out}  ({len(L)} lines)")
    print("FAILURES: " + (", ".join(failures) if failures else "none"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
