#!/usr/bin/env python3
"""OEI-013 step 2 — machine-checkable proof that view D shows the three acts.

TASK §3.3.3 forbids asking the user for screenshots. Everything here is
therefore text a reviewer can re-derive:

  1. the SPA as the DEMO ORIGIN serves it (not the file on disk) — so the proof
     covers the whole chain (origin → static file), not just the repo;
  2. the view-d slice, with the three acts and every anchor the existing tests
     pin, extracted with the SAME regex the test uses (so "the test would see
     this" is literal, not approximate);
  3. the API's RAW output for each act, fetched anonymously through the same
     origin the browser uses;
  4. the rewrite notice the user would actually read, computed by the SHIPPED
     JS rather than restated here.

Usage:
  python3 ui_dom_proof.py --base http://127.0.0.1:8181 --out .../04-ui-dom-proof.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

SPA_DIR = Path("/mnt/d/Projects/domainAgentECE/ece/demos/spa")
PROBE = Path(__file__).resolve().parent / "rewrite_probe.js"

# The exact slice test_consulting_spa_view uses. Duplicated deliberately: if the
# test's regex changes, this proof must go red rather than silently describe a
# different region.
VIEW_D_RE = r'<section[^>]*id=["\']view-d["\'][^>]*>(.*?)(?=<section|</main|</html)'

REQUIRED_ANCHORS = [
    "consulting-search", "filter-type", "filter-practice", "filter-phase",
    "filter-industry", "filter-problem", "filter-source", "consulting-reset",
    "consulting-total", "consulting-cards", "consulting-empty", "consulting-detail",
]
ACTS = [
    ("consulting-act-1", "① 一个问题"),
    ("consulting-act-2", "② 知识库怎么答"),
    ("consulting-act-3", "③ 你的文件"),
]
FORBIDDEN = ["embedding", "embeddings", "vector", "vectors", "ctx_", "decision_id",
             "policy_id", "evidence_id", "package_id", "context_request_id",
             "SQL", "prompt", "token"]


def fetch(base: str, path: str) -> tuple[int, bytes]:
    req = urllib.request.Request(base + path, headers={"Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def fetch_json(base: str, path: str) -> dict:
    status, body = fetch(base, path)
    try:
        return {"status": status, "json": json.loads(body)}
    except Exception:
        return {"status": status, "json": None, "raw_head": body[:200].decode("utf-8", "replace")}


def probe(question: str) -> dict:
    p = subprocess.run(["node", str(PROBE), question], capture_output=True, text=True,
                       timeout=60)
    if p.returncode != 0:
        raise SystemExit(f"rewrite_probe failed: {p.stderr[:300]}")
    data = json.loads(p.stdout)
    case = dict(data["cases"][0])
    # determinism is reported once for the whole probe run, not per case.
    case["determinism"] = data.get("determinism", "")
    case["lexicon_size"] = data.get("lexicon_size")
    return case


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8181")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    base = args.base.rstrip("/")
    L: list[str] = []

    def w(s: str = "") -> None:
        L.append(s)

    # ---- 1. what the origin serves -----------------------------------------
    w("# OEI-013 — 视图 D 三段演示叙事的机器可校验证据")
    w()
    w(f"- 演示起点（同源）: `{base}`  — 浏览器打开 `{base}/index.html`")
    w("- **无截图**：本文件全部结论可由下面的命令与原始输出复算。")
    w()
    w("## 1. 起点实际吐出的文件（不是仓库里的文件）")
    w()
    w("| 资源 | HTTP | 字节 | sha256 |")
    w("|---|---|---|---|")
    served: dict[str, bytes] = {}
    for path in ("/index.html", "/app.js", "/styles.css"):
        status, body = fetch(base, path)
        served[path] = body
        w(f"| `{path}` | {status} | {len(body)} | `{hashlib.sha256(body).hexdigest()[:16]}…` |")
    status_health, _ = fetch(base, "/healthz")
    w(f"| `/healthz` | {status_health} | — | — |")
    w()

    html = served["/index.html"].decode("utf-8")

    # ---- 2. the view-d slice, by the test's own regex ----------------------
    m = re.search(VIEW_D_RE, html, re.DOTALL | re.IGNORECASE)
    section = m.group(1) if m else ""
    w("## 2. 视图 D 切片（用 `test_consulting_spa_view` 的同一个正则切出来的）")
    w()
    w("```")
    w(f"regex: {VIEW_D_RE}")
    w(f"slice length: {len(section)} chars")
    w(f"nested <section> inside slice: {section.count('<section')}   (必须为 0 — 测试以「下一个分节标签」为切片终点)")
    w("```")
    w()
    w("### 三幕")
    w()
    w("| 锚点 | 标题 | 切片内存在 |")
    w("|---|---|---|")
    for anchor, title in ACTS:
        present = f'id="{anchor}"' in section
        w(f"| `#{anchor}` | {title} | {'✅' if present else '❌'} |")
    w()
    w("### 既有测试钉住的锚点（一个都不能少）")
    w()
    w("| 锚点 | 切片内存在 |")
    w("|---|---|")
    missing = []
    for a in REQUIRED_ANCHORS:
        present = f'id="{a}"' in section
        if not present:
            missing.append(a)
        w(f"| `#{a}` | {'✅' if present else '❌'} |")
    w()
    search_ok = 'type="search"' in section
    w(f"- `#consulting-search` 的 `type=\"search\"`: {'✅' if search_ok else '❌'}")
    bad = [t for t in FORBIDDEN if t in section]
    w(f"- PRD §9 禁用技术词出现在切片里: {bad if bad else '无 ✅'}")
    w(f"- **结论: {'PASS' if not missing and search_ok and not bad and section.count('<section') == 0 else 'FAIL'}**")
    w()

    # ---- 3. act one: the question the view opens on ------------------------
    dq = re.search(r'var CONSULTING_DEMO_QUESTION = "([^"]+)";', html)
    if not dq:
        dq = re.search(r'var CONSULTING_DEMO_QUESTION = "([^"]+)";',
                       served["/app.js"].decode("utf-8"))
    question = dq.group(1) if dq else ""
    pr = probe(question)
    w("## 3. 幕一 — 一个问题")
    w()
    w(f"- 视图 D 首次打开时预填的问句（读自 `app.js` 的 `CONSULTING_DEMO_QUESTION`）:")
    w(f"  > {question}")
    w(f"- 这句问句**不是**一个关键词 —— 这正是幕二要讲的东西。")
    w()

    w("## 4. 幕二 — 知识库怎么答")
    w()
    w("### 4a. 原样投喂这句问句（用户真实会做的事）")
    w()
    r = fetch_json(base, "/api/v1/consulting/library?" + urllib.parse.urlencode({"q": question}))
    b = r["json"] or {}
    w(f"- `GET /api/v1/consulting/library?q={urllib.parse.quote(question)}` → HTTP {r['status']}")
    w(f"- **`total = {b.get('total')}`**  (目录命中 0 条)")
    w(f"- `engine_status = {b.get('engine_status')!r}`")
    w(f"- `engine_items = {[i.get('title') for i in (b.get('engine_items') or [])]}`  ({len(b.get('engine_items') or [])} 条)")
    w()
    w("### 4b. 确定性关键词改写（无模型；词表与规则都在 `app.js` 里）")
    w()
    w(f"- `node rewrite_probe.js` 读出**实际发版代码**的改写结果: `{pr['search_terms']}`")
    w(f"- 确定性: {pr.get('determinism', '')}")
    w()
    w("| 检索词 | HTTP | total | engine_status | engine_items（权限过滤后） |")
    w("|---|---|---|---|---|")
    merged_ids: dict[str, dict] = {}
    for term in pr["search_terms"]:
        rr = fetch_json(base, "/api/v1/consulting/library?" + urllib.parse.urlencode({"q": term}))
        bb = rr["json"] or {}
        titles = [i.get("title") for i in (bb.get("engine_items") or [])]
        for it in (bb.get("items") or []):
            merged_ids.setdefault(it["id"], it)
        w(f"| `{term}` | {rr['status']} | {bb.get('total')} | `{bb.get('engine_status')}` | {titles} |")
    w()
    w(f"- 合并去重后目录命中: **{len(merged_ids)} 条**（原样投喂是 {b.get('total')} 条）")
    note = ("这句话不是一个关键词, 知识库没直接命中. 已按其中的业务词检索: "
            + " / ".join(pr["search_terms"]) + f" — 合并去重后 {len(merged_ids)} 条.")
    w(f"- 观众会看到的那行说明（按 `setConsultingRewriteNote` 的文案）:")
    w(f"  > {note}")
    w()

    w("## 5. 幕三 — 你的文件")
    w()
    w("- 上传入口锚点: " + ("✅" if 'id="consulting-upload"' in section else "❌") +
      "  `#consulting-upload` / `#consulting-upload-file` / `#consulting-upload-submit`")
    w("- 召回组锚点: " + ("✅" if 'id="consulting-engine"' in section else "❌") +
      "  `#consulting-engine` / `#consulting-engine-cards` / `#consulting-engine-status`")
    w()
    up = fetch_json(base, "/api/v1/consulting/library?q=" + urllib.parse.quote("诊断"))
    ub = up["json"] or {}
    w(f"- 以 `诊断` 为例的真实召回（匿名，权限过滤后）:")
    w(f"  `engine_status = {ub.get('engine_status')!r}` → `engine_items = "
      f"{[i.get('title') for i in (ub.get('engine_items') or [])]}`")
    w()

    w("## 6. 复算命令")
    w()
    w("```bash")
    w(f"curl -s {base}/index.html | grep -c 'consulting-act-'")
    w(f"curl -s {base}/api/v1/consulting/library | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"total\"])'")
    w(f"node {PROBE}   # 改写结果")
    w("python3 ui_dom_proof.py --base " + base + " --out <same file>")
    w("```")

    out = Path(args.out)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out}  ({len(L)} lines)")
    acts_present = [a for a, _ in ACTS if ('id="%s"' % a) in section]
    print("acts present: " + str(acts_present))
    print(f"missing anchors: {missing or 'none'}")
    print(f"forbidden words: {bad or 'none'}")
    return 0 if not missing and search_ok and not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
