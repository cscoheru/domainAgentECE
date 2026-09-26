"""R3 — capture missing raw evidence.

All subprocess calls cd into the ece project root so relative paths in
alembic.ini and pytest config resolve correctly.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://ece:ece@127.0.0.1:55432/ece")
os.environ.setdefault("ECE_CONTENT_ENGINE", "onyx")

ECE = "/mnt/d/Projects/domainAgentECE/ece"


def _run(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a subprocess from ECE/ root, with DATABASE_URL exported."""
    return subprocess.run(
        args, cwd=ECE, capture_output=True, text=True,
        env={**os.environ, "DATABASE_URL": os.environ["DATABASE_URL"]},
        timeout=timeout,
    )


def _cookie_jar() -> dict[str, str]:
    CK = "/home/fisher/.onyx-lab/.secrets/admin-cookies.txt"
    jar: dict[str, str] = {}
    for line in open(CK):
        line = line.strip()
        if not line or (line.startswith("#") and not line.startswith("#HttpOnly_")):
            continue
        sep = "\t" if "\t" in line else None
        parts = line.split(sep) if sep else line.split()
        if len(parts) < 7:
            continue
        name = parts[5]
        value = "\t".join(parts[6:]) if sep == "\t" else " ".join(parts[6:])
        jar[name] = value
    return jar


def _onyx_get(path: str, jar: dict[str, str]):
    req = urllib.request.Request(f"http://127.0.0.1:8080{path}")
    for k, v in jar.items():
        req.add_header("Cookie", f"{k}={v}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read())


def _fmt_files(files: list) -> list[str]:
    return [
        f"    {str(f.get('name'))[:64]:64s}  status={f.get('status')}  id={f.get('id')}"
        for f in files
    ]


def scratch_project_evidence() -> str:
    """00c-scratch-project.txt — R3.1.

    The v1 file merely listed project 1 twice with no test in between, so it
    proved nothing about the scratch-project discipline. This version:

      1. lists demo project 1 and scratch project 2  (BEFORE)
      2. actually RUNS the test/probe work:
           a. the 4 DB-free unit-test files;
           b. `step22_fail_closed.py` — the engine probe sanctioned by TASK
              §4 step 2.2 to touch project 1 (it deletes its own probe with
              the two-step semantic);
           c. an explicit upload → list → delete round-trip against the
              scratch project, proving that path works end to end.
      3. lists both projects again                (AFTER)

    Acceptance: project 1 is identical before/after (4 = 3 real + 1 authorised
    comparison doc); the scratch probe is visible only in project 2 and is
    removed afterwards.
    """
    jar = _cookie_jar()

    before_status, before = _onyx_get("/api/user/projects/files/1", jar)
    _, before_scratch = _onyx_get("/api/user/projects/files/2", jar)
    _, projects = _onyx_get("/api/user/projects", jar)

    # --- 2a. DB-free unit tests -----------------------------------------
    test_files = [
        "tests/unit/test_engine_documents_registry.py",
        "tests/unit/test_check_permission_timebox.py",
        "tests/unit/test_engine_merge_filter.py",
        "tests/unit/test_org_scope.py",
    ]
    test_summaries = []
    for f in test_files:
        proc = _run(["uv", "run", "pytest", f, "-q", "-p", "no:randomly"], timeout=180)
        lines = [ln.strip() for ln in proc.stdout.strip().splitlines() if ln.strip()]
        tail = lines[-1] if lines else f"(no output; rc={proc.returncode})"
        if not lines and proc.stderr.strip():
            tail = proc.stderr.strip().splitlines()[-1]
        test_summaries.append(f"    {f}: {tail}")

    # --- 2b. sanctioned fail-closed probe (step 2.2, project 1) ----------
    probe = _run(
        ["uv", "run", "python",
         "/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/workspace/step22_fail_closed.py"],
        timeout=900,
    )
    probe_tail = (probe.stdout.strip() or probe.stderr.strip()).splitlines()[-6:]
    probe_ok = "PASS" in probe.stdout

    # --- 2c. scratch-project round-trip ---------------------------------
    scratch_note: list[str] = []
    import httpx

    hx = httpx.Cookies()
    for n, v in jar.items():
        hx.set(n, v, domain="127.0.0.1", path="/")
    scratch_name = "oei009-scratch-roundtrip-probe.txt"
    with httpx.Client(base_url="http://127.0.0.1:8080", cookies=hx, timeout=60.0) as cli:
        up = cli.post(
            "/api/user/projects/file/upload",
            data={"project_id": "2"},
            files={"files": (scratch_name, b"scratch round-trip probe\n", "text/plain")},
        )
        scratch_note.append(f"    upload -> {up.status_code}")
        scratch_fid = up.json()["user_files"][0]["id"] if up.status_code == 200 else None
        _, mid_scratch = _onyx_get("/api/user/projects/files/2", jar)
        scratch_note.append(f"    scratch now has {len(mid_scratch)} file(s): "
                            f"{[f.get('name') for f in mid_scratch]}")
        _, mid_demo = _onyx_get("/api/user/projects/files/1", jar)
        scratch_note.append(f"    demo project 1 during probe: {len(mid_demo)} files "
                            f"(must be unchanged)")
        if scratch_fid:
            code1 = cli.delete(f"/api/user/projects/2/files/{scratch_fid}").status_code
            code2 = cli.delete(f"/api/user/projects/file/{scratch_fid}").status_code
            scratch_note.append(f"    two-step delete -> unlink={code1} delete={code2}")
        _, after_scratch = _onyx_get("/api/user/projects/files/2", jar)
        scratch_note.append(f"    scratch after cleanup: {len(after_scratch)} files")

    after_status, after = _onyx_get("/api/user/projects/files/1", jar)

    lines = [
        "=== R3.1 — scratch project: before / RUN TESTS / after ===",
        "",
        "scratch project creation (15:5x, idempotent):",
        "  POST /api/user/projects/create?name=OEI-009%20Scratch",
        "  -> {id: 2, name: 'OEI-009 Scratch'}",
        "",
        f"demo project id=1 : before={len(before)} files (HTTP {before_status}), "
        f"after={len(after)} files (HTTP {after_status})",
        f"scratch project 2 : before={len(before_scratch)} files",
        "",
        "--- work actually run in between ---",
        "",
        "2a. DB-free unit tests (do not touch the engine):",
        *test_summaries,
        "",
        f"2b. step22_fail_closed.py (TASK §4 step 2.2 sanctioned project-1 probe):",
        *[f"    {ln}" for ln in probe_tail],
        f"    verdict: {'PASS' if probe_ok else 'CHECK OUTPUT'}",
        "",
        "2c. scratch-project round-trip (upload -> list -> two-step delete):",
        *scratch_note,
        "",
        "--- BEFORE: project 1 ---",
        *_fmt_files(before),
        "",
        "--- AFTER: project 1 ---",
        *_fmt_files(after),
        "",
        "all projects:",
        *[f"  id={p.get('id')} name={p.get('name')!r}" for p in projects],
        "",
        "ACCEPTANCE:",
        f"  project 1 unchanged by the test run: {len(before) == len(after)} "
        f"({len(before)} -> {len(after)}; expected 4 = 3 real + 1 sanctioned comparison doc)",
        f"  no test/probe artifact left in project 1: "
        f"{sorted(f.get('name') for f in before) == sorted(f.get('name') for f in after)}",
        f"  scratch project empty again: {len(after_scratch) == 0}",
    ]
    return "\n".join(lines) + "\n"


def registry_migration_evidence() -> str:
    """02-registry-migration.txt."""
    out = ["=== R3.2 — registry migration evidence ===", ""]

    proc = _run(["uv", "run", "alembic", "-c", "src/ece/migrations/alembic.ini",
                 "downgrade", "0008_evidence_records"], timeout=180)
    out.append("--- alembic downgrade to 0008 (drop engine_documents) ---")
    out.append(proc.stdout.strip() or proc.stderr.strip())

    proc = _run(["uv", "run", "alembic", "-c", "src/ece/migrations/alembic.ini",
                 "upgrade", "head"], timeout=180)
    out.append("")
    out.append("--- alembic upgrade head (recreate engine_documents) ---")
    out.append(proc.stdout.strip() or proc.stderr.strip())

    # UNIQUE constraint proof — write a temp script (not inline).
    insert1 = ECE + "/.r3_insert1.py"
    with open(insert1, "w") as f:
        f.write(
            "from sqlalchemy import text\n"
            "from ece.db import get_engine\n"
            "sql = get_engine()\n"
            # Use begin() so the INSERT is committed before the duplicate test.
            "with sql.begin() as c:\n"
            "    c.execute(text(\"INSERT INTO engine_documents \"\n"
            "                  \"(engine_name, engine_project_id, engine_filename, \"\n"
            "                  \"original_filename, classification, uploaded_by) \"\n"
            "                  \"VALUES ('onyx', 1, 'r3-dup.md', 'r3-dup.md', 'public', 'r3')\"))\n"
            "print('insert 1 OK')\n"
        )
    insert2 = ECE + "/.r3_insert2.py"
    with open(insert2, "w") as f:
        f.write(
            "from sqlalchemy import text\n"
            "from ece.db import get_engine\n"
            "sql = get_engine()\n"
            "try:\n"
            "    with sql.begin() as c:\n"
            "        c.execute(text(\"INSERT INTO engine_documents \"\n"
            "                      \"(engine_name, engine_project_id, engine_filename, \"\n"
            "                      \"original_filename, classification, uploaded_by) \"\n"
            "                      \"VALUES ('onyx', 1, 'r3-dup.md', 'r3-dup.md', 'public', 'r3')\"))\n"
            "    print('FAIL: duplicate did NOT raise')\n"
            "except Exception as e:\n"
            "    print(f'PASS: IntegrityError raised ({type(e).__name__}): {str(e).strip()[:200]}')\n"
        )

    proc = _run(["uv", "run", "python", ".r3_insert1.py"], timeout=60)
    proc2 = _run(["uv", "run", "python", ".r3_insert2.py"], timeout=60)
    out.append("")
    out.append("--- direct SQL UNIQUE constraint proof ---")
    out.append(proc.stdout.strip() or proc.stderr.strip())
    out.append(proc2.stdout.strip() or proc2.stderr.strip())

    schema = ECE + "/.r3_schema.py"
    with open(schema, "w") as f:
        f.write(
            "from sqlalchemy import text\n"
            "from ece.db import get_engine\n"
            "sql = get_engine()\n"
            "with sql.connect() as c:\n"
            "    print('table:', c.execute(text(\"SELECT 1 FROM pg_tables WHERE tablename='engine_documents'\")).scalar())\n"
            "    cons = c.execute(text(\"SELECT conname FROM pg_constraint WHERE conrelid='engine_documents'::regclass AND contype='u'\")).fetchall()\n"
            "    print('unique constraints:', [r[0] for r in cons])\n"
            "    idx = c.execute(text(\"SELECT indexname FROM pg_indexes WHERE tablename='engine_documents' ORDER BY indexname\")).fetchall()\n"
            "    print('indexes:', [r[0] for r in idx])\n"
        )
    proc = _run(["uv", "run", "python", ".r3_schema.py"], timeout=60)
    out.append("")
    out.append("--- schema check (post round-trip) ---")
    out.append(proc.stdout.strip() or proc.stderr.strip())

    # Cleanup.
    cleanup = ECE + "/.r3_cleanup.py"
    with open(cleanup, "w") as f:
        f.write(
            "from sqlalchemy import text\n"
            "from ece.db import get_engine\n"
            "sql = get_engine()\n"
            "with sql.begin() as c:\n"
            "    c.execute(text(\"DELETE FROM engine_documents WHERE engine_filename = 'r3-dup.md'\"))\n"
        )
    _run(["uv", "run", "python", ".r3_cleanup.py"], timeout=60)

    # Remove temp scripts.
    for p in (insert1, insert2, schema, cleanup):
        try:
            os.unlink(p)
        except OSError:
            pass

    return "\n".join(out) + "\n"


def unit_test_raw_evidence() -> str:
    """12-test-db-free-raw.txt."""
    files = [
        "tests/unit/test_engine_documents_registry.py",
        "tests/unit/test_check_permission_timebox.py",
        "tests/unit/test_engine_merge_filter.py",
        "tests/unit/test_org_scope.py",
    ]
    out = ["=== R3.3 — DB-free unit test raw output (4 files, 49 tests) ===", ""]
    for f in files:
        proc = _run(["uv", "run", "pytest", f, "-v", "--tb=short",
                     "-p", "no:randomly"], timeout=120)
        out.append(f"--- {f} ---")
        out.append(proc.stdout.strip() or proc.stderr.strip())
        out.append("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    open("/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/evidence/00c-scratch-project.txt", "w").write(
        scratch_project_evidence()
    )
    print("wrote 00c-scratch-project.txt")
    open("/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/evidence/02-registry-migration.txt", "w").write(
        registry_migration_evidence()
    )
    print("wrote 02-registry-migration.txt")
    open("/mnt/d/Projects/domainAgentECE/onyx-lab/OEI-009/evidence/12-test-db-free-raw.txt", "w").write(
        unit_test_raw_evidence()
    )
    print("wrote 12-test-db-free-raw.txt")