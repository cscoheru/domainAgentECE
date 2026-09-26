#!/usr/bin/env python3
"""OEI-013 — same-origin server for the resident consulting demo.

Serves the SPA from `demos/spa/` and reverse-proxies `/api/*` to the FastAPI
upstream, so a browser opens ONE origin (no CORS, no separate API host).

Why this file exists instead of reusing `scripts/cut_045_local_origin.py`:

  1. `scripts/` is **outside** OEI-013's authorized change set (§8 lists
     `demos/spa/**`, `src/ece/{consulting,api,connectors/onyx}/**`, `Makefile`,
     `docs/API.md`, `TASKS.md`, `data/eval/retrieval/**`, `tests/**` and
     `onyx-lab/OEI-013/workspace/` — not `scripts/`). The workspace copy keeps
     the frozen smoke script byte-identical for its own tests.
  2. That script hardcodes a **10 s** upstream timeout
     (`urllib.request.urlopen(..., timeout=10)`). OEI-012 measured real
     `/api/search` latency at **1.5 s – 56 s**; a 10 s cap turns a slow-but-
     working recall into a 502, which the SPA renders as a failed search. A
     demo that 502s on its own search is a broken demo. Here the timeout is a
     flag (`--upstream-timeout`, default 120 s) so the number is explicit and
     reviewable rather than hidden.

Everything else (static root, proxy prefixes, no-store, path-traversal guard)
mirrors the cut-045 pattern deliberately — this is the same deployment shape,
not a new one.

Usage:
    python3 demo_origin.py --port 8181 --upstream http://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import os
import signal
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SPA_DIR = Path("/mnt/d/Projects/domainAgentECE/ece/demos/spa")

DEFAULT_ORIGIN_PORT = 8181
DEFAULT_API_UPSTREAM = "http://127.0.0.1:8765"
# See module docstring point 2. Generous on purpose: the engine is the slow
# dependency, and a 502 mid-demo is worse than a slow but correct answer.
DEFAULT_UPSTREAM_TIMEOUT = 120.0

PROXY_PREFIXES = ("/api/", "/healthz", "/openapi.json")
_PROXY_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")


class _OriginHandler(BaseHTTPRequestHandler):
    server_version = "oei013-demo-origin/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        path = self.path.split("?", 1)[0]
        kind = "proxy" if self._should_proxy(path) else "static"
        sys.stdout.write(f"[demo-origin] {self.command} {self.path} → {kind}\n")
        sys.stdout.flush()

    @staticmethod
    def _should_proxy(path: str) -> bool:
        return any(path.startswith(p) for p in PROXY_PREFIXES)

    def _dispatch(self) -> None:
        path = self.path.split("?", 1)[0]
        if self._should_proxy(path):
            self._proxy(self.command, path)
        elif self.command in ("GET", "HEAD"):
            self._serve_static(path)
        else:
            self.send_error(405, f"{self.command} only valid for /api/")

    do_GET = _dispatch
    do_HEAD = _dispatch
    do_POST = _dispatch
    do_PUT = _dispatch
    do_PATCH = _dispatch
    do_DELETE = _dispatch

    def do_OPTIONS(self) -> None:
        # Same-origin: the browser never fires a CORS preflight. Answer anyway
        # so scripts/curl against this origin don't get a hard failure.
        path = self.path.split("?", 1)[0]
        if self._should_proxy(path):
            self._proxy("OPTIONS", path)
            return
        self.send_response(204)
        self.end_headers()

    # -- static ------------------------------------------------------------

    def _serve_static(self, path: str) -> None:
        rel = path.lstrip("/") or "index.html"
        target = (SPA_DIR / rel).resolve()
        try:
            target.relative_to(SPA_DIR.resolve())
        except ValueError:
            self.send_error(404, f"path outside SPA root: {rel}")
            return
        if not target.is_file():
            fallback = SPA_DIR / "index.html"
            if fallback.is_file():
                target = fallback
            else:
                self.send_error(404, f"no SPA asset at {rel}")
                return
        try:
            data = target.read_bytes()
        except OSError as exc:
            self.send_error(500, f"failed to read {rel}: {exc}")
            return
        self.send_response(200)
        self.send_header("Content-Type", self._guess_content_type(rel))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    @staticmethod
    def _guess_content_type(rel: str) -> str:
        if rel.endswith(".html"):
            return "text/html; charset=utf-8"
        if rel.endswith(".js"):
            return "application/javascript; charset=utf-8"
        if rel.endswith(".css"):
            return "text/css; charset=utf-8"
        if rel.endswith(".json"):
            return "application/json; charset=utf-8"
        return "application/octet-stream"

    # -- proxy -------------------------------------------------------------

    def _proxy(self, method: str, path: str) -> None:
        qs = self.path.split("?", 1)[1] if "?" in self.path else ""
        upstream_url = f"{API_UPSTREAM}{path}{('?' + qs) if qs else ''}"
        headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in ("host", "content-length", "connection")
        }
        body: bytes | None = None
        if method in ("POST", "PUT", "PATCH"):
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length:
                body = self.rfile.read(length)
        try:
            req = urllib.request.Request(upstream_url, data=body, method=method,
                                         headers=headers)
            with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT) as resp:
                payload = resp.read()
                self.send_response(resp.status)
                for h in ("Content-Type", "Content-Length"):
                    v = resp.headers.get(h)
                    if v is not None:
                        self.send_header(h, v)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            try:
                payload = exc.read()
            except Exception:  # pragma: no cover - defensive
                payload = str(exc).encode()
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except urllib.error.URLError as exc:
            self.send_error(502, f"upstream unreachable: {exc}")
        except TimeoutError:
            self.send_error(504, f"upstream exceeded {UPSTREAM_TIMEOUT}s")


def main() -> int:
    ap = argparse.ArgumentParser(description="OEI-013 demo same-origin server")
    ap.add_argument("--port", type=int,
                    default=int(os.environ.get("DEMO_ORIGIN_PORT", DEFAULT_ORIGIN_PORT)))
    ap.add_argument("--upstream",
                    default=os.environ.get("DEMO_API_UPSTREAM", DEFAULT_API_UPSTREAM))
    ap.add_argument("--upstream-timeout", type=float,
                    default=float(os.environ.get("DEMO_UPSTREAM_TIMEOUT",
                                                 DEFAULT_UPSTREAM_TIMEOUT)))
    args = ap.parse_args()

    global API_UPSTREAM, UPSTREAM_TIMEOUT
    API_UPSTREAM = args.upstream
    UPSTREAM_TIMEOUT = args.upstream_timeout

    server = ThreadingHTTPServer(("127.0.0.1", args.port), _OriginHandler)
    print(f"[demo-origin] listening      127.0.0.1:{args.port}")
    print(f"[demo-origin] SPA static  →  {SPA_DIR}")
    print(f"[demo-origin] API upstream → {API_UPSTREAM}")
    print(f"[demo-origin] upstream timeout = {UPSTREAM_TIMEOUT}s")
    print(f"[demo-origin] browser URL  → http://127.0.0.1:{args.port}/index.html")
    sys.stdout.flush()

    def _shutdown(_signum: int, _frame: object) -> None:
        print("\n[demo-origin] shutting down ...")
        sys.stdout.flush()
        server.shutdown()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)
    try:
        server.serve_forever()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
