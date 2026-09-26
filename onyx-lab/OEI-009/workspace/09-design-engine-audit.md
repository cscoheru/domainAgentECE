# OEI-009 — Engine Call Audit Persistence Design

> Status: **design only**, this cut (OEI-009) does not write code.
> Author: Claude Code (cc), based on TASK v1.3 §4 step 5.1.
> Persistence target: a future cut (post-OEI-010). The current state — an
> in-process `audit_log` list on `OnyxContentEngineAdapter` — is a
> temporary measure documented in `docs/API.md §13.4` and rejected by
> codex in `OEI-008/VERDICT.md §3 D3`.

---

## 1. The problem

`OnyxContentEngineAdapter._audit(...)` (introduced in OEI-008 §A6) appends
one row per call to `self.audit_log: list[dict]`. Properties:

- **Process-local.** Restarts wipe the log; multi-worker deployments lose
  visibility entirely.
- **Not durable.** Anything that crashes the adapter mid-call loses the
  row. The accounting "how many times did alice search engine X" can't be
  audited after the fact.
- **No atomicity with `0005_context_audit`.** A `context_request` row that
  triggered an engine recall is in the DB; the engine-side audit row for
  the same `request_id` is in memory only. Joining the two requires both
  sides to flush.

Acceptable for OEI-008 / OEI-009 (single-worker dev box, one demo at a
time). Unacceptable for any deployment that survives a worker restart,
runs more than one uvicorn, or needs post-hoc SIEM-style review.

## 2. Requirements (what the next cut must satisfy)

| # | Requirement | Source |
|---|---|---|
| R1 | Persist every engine call, success AND failure, by identity | OEI-008 VERDICT §3 D3; A6 |
| R2 | Survive worker restart; durable across deployments | This doc, §1 |
| R3 | Correlatable with `context_requests.request_id` when present | OEI-008 audit row already carries `request_id` |
| R4 | **Write path MUST NOT block the request** | OEI-008 §A6; cut-006 audit webhook precedent |
| R5 | Storage footprint under OEI-002-class load (≪ 100 ms, ~10 RPS) | DEPLOYMENT-STATUS.md §2 |
| R6 | Compatible with the existing `0005_context_audit` schema | Migrate-by-extension, not by-replacement |

## 3. Three candidate designs

### 3.A. Per-call INSERT into `context_audit.audit_events` (extend 0005)

**Idea**: every `_audit()` call writes one row to a new
`engine_audit_events` table inside the existing `context_audit` schema.

```
Table: context_audit.engine_audit_events
- id bigserial PK
- when timestamptz
- what text NOT NULL             -- 'search' / 'engine_status' / 'upload_document' / 'document_status' / 'list_projects'
- caller_user_ref text
- caller_source text              -- jwt / header / anonymous / test
- caller_dept text
- caller_org_id text
- result text NOT NULL            -- 'ok' / 'transport_failure' / 'auth_failure' / ...
- duration_ms int                 -- for ok rows; null on failure
- request_id text NULL            -- join key to context_requests
- engine_name text NOT NULL
- query text NULL                 -- for 'search': the user query (redacted of PII beyond user_ref)
- hits int NULL                   -- for 'search' / 'ok': result count
- document_id text NULL           -- for 'upload_document' / 'document_status'
- error_text text NULL            -- for failure rows
- created_at timestamptz DEFAULT now()
INDEX (when), INDEX (caller_user_ref, when), INDEX (engine_name, when), INDEX (request_id)
```

**Cost estimate** (per OEI-002-class load, ~10 RPS, 50% search / 50%
uploads + status):

- 10 INSERTs/sec → ~864k rows/day, ~30M rows/month
- avg row size ≈ 400 bytes → ~12 GB raw / month before TOAST / indexes
- write amplification: 1 row per call → matches R1, R6
- latency: 1 INSERT ≤ 5 ms on local PG (per OEI-002 §1.1 measurements)

**Verdict**: simple, correct, but **fails R4** if latency becomes > 50 ms
under load, and storage grows without bound. Needs a TTL/partition policy.

### 3.B. Sampling + batched bulk insert (rate-limit the audit)

**Idea**: keep `_audit()` in-memory but flush a batch every N rows or
every T seconds via COPY. Sampling rate p ∈ [0, 1] controls footprint.

```
Same table as 3.A.
- in-process buffer: list[(row,)] size ≤ N or age ≤ T
- background task flushes via COPY to PG (or to a local file in
  degraded mode)
- sampling: drop row with prob (1 - p); p=0.05 keeps 5% — enough for
  SIEM-style review, not for full forensics
```

**Cost estimate** (p=0.05):

- ~43200 rows/day, ~1.3M rows/month
- ~0.5 GB raw / month
- write amplification: 1 bulk-COPY per N rows → reduces R4 risk
- latency: in-process append is sub-microsecond; bulk flush is ~50 ms but
  off the request path

**Verdict**: better footprint + lower per-request latency; but **fails R1
under audit** when p < 1 — sampling is acceptable for SIEM but not for
"every call recorded" (the OEI-008 contract).

### 3.C. Per-call + TTL partitioning (3.A + Postgres partitioning)

**Idea**: same as 3.A but partition `engine_audit_events` by month
(Postgres native partitioning). Drop old partitions instead of DELETE.

```
CREATE TABLE engine_audit_events (...) PARTITION BY RANGE (created_at);
CREATE TABLE engine_audit_events_2026_09 PARTITION OF engine_audit_events
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
... cron: CREATE next month's partition; DROP partitions older than 90d.
```

**Cost estimate**:

- same per-row cost as 3.A
- storage footprint = bounded by retention policy (e.g. 90 days = ~3.5 GB)
- DROP PARTITION is O(1) (catalog operation); no row-level DELETE cost
- write path is the same as 3.A

**Verdict**: this is **3.A with operational hygiene**. Recommended.

## 4. Recommendation

**Adopt 3.C with sampling disabled** (p = 1.0) for the first durable
implementation. Rationale:

- meets R1–R6 directly without sub-rosa sampling
- partitions make retention a one-statement cron job
- the existing 0005 migration's `audit_events`-style pattern is the
  template — minimal new surface
- write cost is bounded by retention; OEI-009 §6 sets a 90-day default
  (adjustable per customer)

**Migration plan**:

1. cut X.1: extend `0005_context_audit` with the partitioned
   `engine_audit_events` table + a `create_engine_audit_partition(year,
   month)` helper + cron entry. **No code changes** to the adapter — it
   still buffers in `self.audit_log`.
2. cut X.2: implement a background flusher in `OnyxContentEngineAdapter`
   (or a separate `EngineAuditSink` injected via DI). One COPY per batch.
3. cut X.3: integrate with `request_id` from `context_requests`. Add a
   `GET /audit/engine/by-request/{request_id}` endpoint that joins the
   two audit sources.

**Failure paths** (must be designed, not patched later):

- **PG down** at flush time → buffer to a local file (`/var/log/ece/engine-audit.jsonl`),
  replay on PG recovery. This file MUST be on WSL-native FS (NOT `/mnt/d`)
  per DEPLOYMENT-STATUS.md §6 — the cookie jar's permissiveness argument
  applies equally to PII logs.
- **Process death** between buffer and flush → accept loss of in-memory
  rows; document a "best-effort, at-least-once after restart" guarantee
  rather than promising strict durability from in-memory state.
- **Sampling failure** (DB write failure inside the buffer) → log +
  alert. Do NOT block the request.

## 5. Cost table (rolled forward)

| Choice | p | Rows/day | Rows/month | Storage/month | Per-call latency |
|---|---|---|---|---|---|
| 3.A un-partitioned | 1.0 | 864k | 26M | ~10 GB | +5 ms |
| 3.C partitioned, 90d retention | 1.0 | 864k | 26M | ≤ 3.5 GB | +5 ms |
| 3.B sampling p=0.05 | 0.05 | 43k | 1.3M | ~0.5 GB | +0 ms (per-call), +50 ms (bulk) |

## 6. Open questions for codex

1. Retention: 90 days? 30? Customer-configurable? (Default: 90; matches
   OEI-002-era SIEM retentions.)
2. Should `engine_audit_events` be in the `context_audit` schema, or
   its own `engine_audit` schema? (Pro `context_audit`: one migration
   family. Con: couples unrelated lifecycles.)
3. Is the `engine_audit_events.audit_text` field (a structured JSON of
   the request body) worth the storage? For Onyx, the bodies are tiny;
   for a future heavier engine, they may matter.
4. Where does the background flusher live — in `OnyxContentEngineAdapter`
   or in a new module `engine_audit/sink.py` injected via DI? (DI is
   cleaner; requires a constructor change to the adapter.)

## 7. Why this is "design only, not implement" (TASK §4 step 5.1)

The OEI-009 deliverable is the **design document** above + the cost
table. The implementation is **explicitly out of scope** per TASK v1.3
§2 "不做" — it must land in a separate cut that takes the time-budget
for migration + DI plumbing without blocking OEI-010's memory cut.