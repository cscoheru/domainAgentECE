# OEI-009 — Context Assembly Step 6 Re-wiring (design)

> Status: **evaluation only**, no code change in this cut.
> Target: a future cut (post-OEI-010) that re-wires
> `src/ece/context/assembly.py` step 6 to read from `ContentEnginePort`
> instead of the native `documents` table.

---

## 1. What step 6 does today

`src/ece/context/assembly.py` step 6 ("Retrieve authorized documents")
is currently a stub: it reads from the native `documents` table via the
Store layer, applies the SQL subquery permission filter (ADR-004), and
returns chunks for the assembler to consume.

Concretely: today, an `assemble_context(user_ref, intent, entities)`
call walks the user's department/roles → selects `documents` WHERE
classification matches and department matches (via SQL subquery) →
returns text chunks for the LLM to consume.

This path is *correct* but **does not benefit from the content engine**
(OEI-006 added engine recall as a UI-only Library group; the LLM never
sees it).

## 2. Why the next cut should re-wire it

The OEI-006/008/009 work proved the engine has two properties the native
table lacks:

1. **Recall over uploaded client data** (PDFs, DOCX, etc. via the upload
   path).
2. **Permission-aware retrieval** (per OEI-009, the consulting layer
   already does per-result filtering using the registry).

The customer pays for the engine. If the LLM in `assemble_context` is
still reading only from `documents`, the engine is wasted for the
**most important call path** (the one that produces the actual answer
to the user's question, not a Library card).

The re-wiring collapses "two retrieval surfaces" into one: the Library
engine group and the LLM's source documents both come from
`ContentEnginePort.search(...)`. Per-result permission filter
(OEI-009's `consulting/permissions_filter.py`) runs in both places
unchanged.

## 3. Proposed re-wiring

```
current step 6:
  Store.documents.search(scope=identity.scope, ...) → chunks

proposed step 6:
  engine = get_content_engine()
  docs = await engine.search(query=assembled_query, top_k=top_k, caller=identity.caller)
  rows = permissions_filter.filter_engine_items(docs, sql_engine, engine_name, identity)
  rows_to_chunks(rows) → chunks
```

Where:
- `assembled_query` is derived from `intent` + the named entities (today
  it's a simple `intent` text; future: LLM-built, but OEI-009/010 don't
  introduce that — same scope).
- `rows_to_chunks` is a thin adapter: each allowed `EngineItem` becomes
  one chunk with `text = snippet`, `document_id = engine_doc_id`,
  `source_type = engine`, `classification = row.classification`. The
  downstream LLM contract doesn't change.
- The filter is **the same** filter the Library uses. One implementation,
  one permission model, one audit surface.

## 4. What changes in the codebase

| File | Change |
|---|---|
| `src/ece/context/assembly.py` step 6 | replace Store.documents call with engine.search + filter_engine_items |
| `src/ece/context/assembly.py` | new helper: `engine_query_for(intent, entities)` (deterministic, no LLM) |
| `src/ece/consulting/permissions_filter.py` | already exposes `filter_engine_items`; no change here |
| `src/ece/connectors/onyx/port.py` | no change |
| `tests/integration/test_assembly_*` | add a "real-engine path" test case that asserts the LLM sees an engine chunk |

## 5. Cost estimate

- Latency: today OEI-008 §1.1 reports ~4 s steady-state for engine.search
  on Onyx, ~15 s cold start. assemble_context currently takes <100 ms on
  Store.documents. The re-wire trades 4 s for 100 ms. This is the
  single biggest visible regression.
- Mitigation: keep Store.documents as the **fallback** when
  `ECE_CONTENT_ENGINE` is `mock` (no live engine), so unit tests don't
  slow down. Production demo gets the engine path.
- Failure mode: when engine is unreachable, `merge_engine` returns
  `("unavailable", [])`. The assembly step MUST translate that to
  "no engine chunks, use Store.documents as graceful fallback" —
  otherwise an Onyx hiccup turns every `assemble_context` call into an
  empty answer.
- Audit: each step-6 call should append to `engine_audit_events` (the
  table OEI-009 §5.1 designs). One INSERT per `assemble_context` call
  rather than one per `engine.search` call (these are 1:1 here).

## 6. Side-channel risk (why this re-wiring is non-trivial)

The current Store.documents path uses SQL subquery filtering — the
filter is at the *storage* layer. The proposed re-wiring uses
per-result filtering at the *application* layer.

This is a known worse-than-SQL-subquery against adversarial callers:
the filter has to roundtrip `acl_entries` for every result, and a
slow / poisoned engine could leak through ordering signals.

Mitigations:

- **Same filter** as the Library path (already audited under OEI-009
  §6 / A6).
- **Top-k cap** is 8 (Library) → for assembly, raise to **10–20** to get
  enough chunks but keep latency bounded.
- **Sort stability**: when the filter narrows, the relative order of
  *surviving* chunks is preserved. No "filtered to N from M"
  telemetry to the caller.
- **Cold-start strategy**: in step 6, *not* the Library: the engine
  recall IS the answer. If it's cold, fall back to Store.documents
  with a banner row in the response ("engine cold-start, partial
  recall").

## 7. Why this is "evaluation only, not implement" (TASK §4 step 5.3)

The OEI-009 deliverable is the **design** above + the cost estimate +
the side-channel risk analysis. The implementation is a separate cut
because:

- It depends on the OEI-009 audit persistence design (§5.1) — we want to
  write the audit row from the *new* step 6, not retrofit it.
- It depends on the org-scope finalization (§5.2) — org-level memory
  should plug into the same step 6.
- It changes the perceived latency of every `assemble_context` call,
  which is the customer-visible demo metric. That deserves its own cut
  with explicit customer-facing acceptance criteria.

The cutoff for the next cut is: **after** OEI-010 ships. If OEI-010
turns out to need org-level memory read *inside* step 6, the two cuts
collapse; if not, the next cut is post-OEI-010.

## 8. Compatibility check

- The existing `Store.documents.search(scope, ...)` is the **only**
  read path that uses ADR-004's SQL subquery filter. Removing it as the
  primary read path doesn't break any other code that uses it — but it
  should be kept (under a flag or behind a feature toggle) for at least
  one release, because the re-wire is risky.
- The mock adapter (`MockContentEngineAdapter`) doesn't support
  `search()` the way the real Onyx adapter does — it has canned
  responses. The re-wire must include a small mock dataset for the 3
  demo docs so unit tests can run offline.

## 9. Acceptance (for the future cut)

- assemble_context(real-engine, intent) returns at least one chunk
  sourced from an engine doc with the right citation format.
- assemble_context(engine=down) returns at least one chunk from
  Store.documents fallback (no empty response).
- All existing assembly tests still pass (with the engine turned on).
- New test: assemble_context runs the same permission filter as the
  Library; an unauthorized engine doc doesn't leak into the LLM.