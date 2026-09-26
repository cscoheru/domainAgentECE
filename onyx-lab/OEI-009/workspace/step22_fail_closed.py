"""OEI-009 step 2.2 — fail-closed verification.

Upload a probe file DIRECTLY to Onyx (bypassing ECE), so NO engine_documents
row is created. Then query /library with multiple identities and prove the
probe does NOT appear in any result (fail-closed: un-registered = invisible).

Uses /api/user/projects/file/upload against project id=1 directly (via
bin/onyx-upload.sh equivalent in Python). Marker is unique per run.

Cleanup: probe is removed via the 2-step delete semantic
(unlink from project, then delete the user_file) per DEMO-DATA-CLEANUP-2026-09-25.md §2.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

import httpx

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "ece" / "src"))


ONYX_BASE = os.environ.get("ECE_ONYX_BASE", "http://127.0.0.1:8080")
COOKIE_FILE = os.environ.get(
    "ECE_ONYX_COOKIE_FILE", "/home/fisher/.onyx-lab/.secrets/admin-cookies.txt"
)
PROJECT_ID = 1
QUERY = "oei009failclosedprobeunique"  # unique phrase for recall


def _marker() -> str:
    nonce = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:10]
    return f"oei009step22_{nonce}"


def _load_cookies() -> httpx.Cookies:
    jar = httpx.Cookies()
    text = Path(COOKIE_FILE).read_text(encoding="utf-8", errors="replace")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or (line.startswith("#") and not line.startswith("#HttpOnly_")):
            continue
        sep = "\t" if "\t" in line else None
        parts = line.split(sep) if sep else line.split()
        if len(parts) < 7:
            continue
        domain, _flag, path_, _secure, _expires, name = parts[:6]
        value = "\t".join(parts[6:]) if sep == "\t" else " ".join(parts[6:])
        jar.set(name, value, domain=domain.lstrip("#HttpOnly_"), path=path_ or "/")
    return jar


def _cleanup(cli: httpx.Client, user_file_id: str) -> None:
    """Two-step delete per DEMO-DATA-CLEANUP-2026-09-25.md §2."""
    cli.delete(f"/api/user/projects/{PROJECT_ID}/files/{user_file_id}")
    cli.delete(f"/api/user/projects/file/{user_file_id}")


def main() -> int:
    marker = _marker()
    # The probe filename DOES NOT have the `ece-` prefix → even if it
    # somehow leaked into engine_documents later, it's clearly a probe.
    # We use a long unique-ish name for the probe.
    docref = hashlib.sha256(marker.encode()).hexdigest()[:12]
    probe_filename = f"oei009-step22-probe-{docref}.md"
    body = (
        f"# OEI-009 step 2.2 — fail-closed probe\n\n"
        f"marker: {marker}\n\n"
        f"This file is uploaded DIRECTLY to Onyx (no engine_documents row).\n"
        f"Unique phrase: `{QUERY}`.\n"
    ).encode("utf-8")

    jar = _load_cookies()
    out: dict = {"marker": marker, "probe_filename": probe_filename}

    with httpx.Client(base_url=ONYX_BASE, cookies=jar, timeout=30.0) as cli:
        # 1. Upload probe to project 1, bypassing ECE.
        up = cli.post(
            "/api/user/projects/file/upload",
            data={"project_id": str(PROJECT_ID)},
            files={"files": (probe_filename, io.BytesIO(body), "text/markdown")},
        )
        out["upload_status"] = up.status_code
        if up.status_code != 200:
            print(json.dumps(out, indent=2, default=str))
            return 1
        user_file_id = up.json()["user_files"][0]["id"]
        out["user_file_id"] = user_file_id

        # 2. Wait for indexing.
        deadline = time.monotonic() + 60
        indexed = False
        while time.monotonic() < deadline:
            poll = cli.post(
                "/api/user/projects/file/statuses",
                json={"file_ids": [user_file_id]},
            )
            if poll.status_code == 200 and poll.json():
                if poll.json()[0].get("status") == "COMPLETED":
                    indexed = True
                    break
            time.sleep(2)
        out["indexed"] = indexed
        if not indexed:
            print("indexing timed out")
            _cleanup(cli, user_file_id)
            return 1

        # 3. Probe library endpoint with three identities.
        os.environ["ECE_CONTENT_ENGINE"] = "onyx"
        for mod in list(sys.modules):
            if mod.startswith("ece."):
                del sys.modules[mod]

        from fastapi.testclient import TestClient  # noqa: PLC0415

        from ece.main import app  # noqa: PLC0415

        client = TestClient(app)

        for label, headers in (
            ("anonymous", {}),
            ("demo_user", {"X-User-Id": "alice"}),
            ("other_user", {"X-User-Id": "bob"}),
        ):
            r = client.get(
                "/api/v1/consulting/library",
                params={"q": QUERY},
                headers=headers,
            )
            titles = [it["title"] for it in r.json().get("engine_items", [])]
            out[f"library_{label}"] = {
                "status": r.status_code,
                "engine_status": r.json().get("engine_status"),
                "engine_items_titles": titles,
                "probe_visible": probe_filename in titles,
            }

        # 4. Cleanup.
        _cleanup(cli, user_file_id)

    print(json.dumps(out, indent=2, default=str))

    # Acceptance: probe NOT visible to ANY identity.
    fail = False
    for label in ("anonymous", "demo_user", "other_user"):
        if out[f"library_{label}"]["probe_visible"]:
            print(f"FAIL — probe visible to {label}")
            fail = True
    if fail:
        return 1
    print("PASS — fail-closed: probe (no engine_documents row) invisible to all identities.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())