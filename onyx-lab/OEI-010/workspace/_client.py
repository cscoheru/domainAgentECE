"""Shared test client for the OEI-010 evidence scripts.

Uses `fastapi.testclient.TestClient` rather than a live uvicorn: the cut's
endpoints are in-process, and LOCAL-AGENT-PROTOCOL §5.1 asks that background
uvicorn / reverse-proxy processes not be left running. A TestClient is created,
used, and discarded inside one script.

`ECE_CONTENT_ENGINE` is forced to `mock` (the cut's default per TASK §8 — memory
is entirely ECE-side; the engine is not involved).

IMPORTANT: the app must be imported AFTER `DATABASE_URL` / `ECE_CONTENT_ENGINE`
are set in the environment, because `ece.db.get_engine` is an `lru_cache`
singleton. `fresh_app()` also clears any already-imported `ece.*` modules so a
script that imports this helper first still gets the right engine.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_ECE_SRC = _REPO / "ece" / "src"

if str(_ECE_SRC) not in sys.path:
    sys.path.insert(0, str(_ECE_SRC))


def reset_modules() -> None:
    """Drop cached `ece.*` modules so the next import re-reads the environment."""
    for name in list(sys.modules):
        if name == "ece" or name.startswith("ece."):
            del sys.modules[name]


def fresh_app():
    """Return `(client, sql_engine)` with the engine bound to the current env."""
    os.environ.setdefault("ECE_CONTENT_ENGINE", "mock")
    reset_modules()

    from fastapi.testclient import TestClient  # noqa: PLC0415

    from ece.db import get_engine  # noqa: PLC0415
    from ece.main import app  # noqa: PLC0415

    return TestClient(app), get_engine()


def hdr(user_ref: str | None) -> dict[str, str]:
    """Headers for an identified caller (or anonymous when `user_ref` is None)."""
    return {} if user_ref is None else {"X-User-Id": user_ref}


# ── thin wrappers that record the raw HTTP result ──────────────────────────


def _record(resp: Any, body: Any = None) -> dict[str, Any]:
    try:
        parsed = resp.json()
    except Exception:  # noqa: BLE001 — non-JSON body is itself evidence
        parsed = {"_raw": resp.text[:400]}
    return {"status": resp.status_code, "body": parsed}


def create_memory(client, user_ref: str | None, **body: Any) -> dict[str, Any]:
    resp = client.post("/api/v1/memory", json=body, headers=hdr(user_ref))
    return _record(resp)


def list_memory(client, user_ref: str | None, include_inactive: bool = False) -> dict[str, Any]:
    params = {"include_inactive": "true"} if include_inactive else None
    resp = client.get("/api/v1/memory", params=params, headers=hdr(user_ref))
    return _record(resp)


def delete_memory(client, user_ref: str | None, memory_id: int) -> dict[str, Any]:
    resp = client.delete(f"/api/v1/memory/{memory_id}", headers=hdr(user_ref))
    return _record(resp)


def delete_memory_bulk(client, user_ref: str | None, scope: str) -> dict[str, Any]:
    resp = client.delete("/api/v1/memory", params={"scope": scope}, headers=hdr(user_ref))
    return _record(resp)


def assemble_context(
    client, user_ref: str | None, *, intent: str = "evaluate_purchase_request",
    entity_id: str = "PR001", entity_type: str = "purchase_request",
) -> dict[str, Any]:
    resp = client.post(
        "/api/v1/context",
        json={
            "intent": intent,
            "entities": [{"type": entity_type, "id": entity_id}],
        },
        headers=hdr(user_ref),
    )
    return _record(resp)


def sql_scalar(engine, sql: str, **params: Any) -> Any:
    from sqlalchemy import text  # noqa: PLC0415

    with engine.connect() as conn:
        return conn.execute(text(sql), params).scalar()


def sql_rows(engine, sql: str, **params: Any) -> list[tuple]:
    from sqlalchemy import text  # noqa: PLC0415

    with engine.connect() as conn:
        return list(conn.execute(text(sql), params).fetchall())


def sql_exec(engine, sql: str, **params: Any) -> int:
    from sqlalchemy import text  # noqa: PLC0415

    with engine.begin() as conn:
        return conn.execute(text(sql), params).rowcount


def sql_write_scalar(engine, sql: str, **params: Any) -> Any:
    """A COMMITTED write that returns one value (e.g. `INSERT ... RETURNING id`).

    `sql_scalar` uses `engine.connect()`, which does not commit: an INSERT there
    is rolled back when the connection closes, and the failure is silent — the
    row simply is not there afterwards. Use this for anything that must persist.
    """
    from sqlalchemy import text  # noqa: PLC0415

    with engine.begin() as conn:
        return conn.execute(text(sql), params).scalar()


def dump(out: dict[str, Any]) -> None:
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
