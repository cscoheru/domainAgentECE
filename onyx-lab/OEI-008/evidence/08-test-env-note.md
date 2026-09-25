# 08 — environment note (read this before trusting the raw file)

`08-test-before-raw.txt` is the **verbatim** pre-commit suite run:

```
757 passed, 5 skipped, 3 deselected, 5 warnings in 203.91s
```

## What the DB had to look like for that to be true

The suite is an *integration* suite: ~48 of its tests read seeded fixture
entities out of Postgres. A fresh temp DB that has been migrated but **not
seeded** fails them all with

```
422 {"error":"invalid_scenario_spec",
     "detail":"no entity with source_id='COMP-CTL-001' source_system='comp:v0-compliance-fixture'"}
```

That is what the first attempt at this evidence produced: **48 failed,
709 passed**. It is an environment gap, not a regression — the same 48 tests
fail identically on `HEAD` (`caa69e8`, OEI-007) against the same unseeded DB.

## Preparation actually performed

```
docker run -d --name ece-pg-tmp -p 127.0.0.1:55432:5432 postgres:16-pgvector
DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece' \
  .venv/bin/python -c "alembic -c src/ece/migrations/alembic.ini upgrade head"

export DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece'
for s in seed_temporal_roles seed_knowledge_fixture \
         seed_compliance_fixture seed_v0_spike_fixture; do
  .venv/bin/python scripts/$s.py
done
```

All four seeders self-checked green:

```
seed_temporal_roles      Total temporal relationships in DB: 3
seed_knowledge_fixture   SELF-CHECK PASSED — all 8 fixture entities present …
seed_compliance_fixture  SELF-CHECK PASSED — all 6 fixture entities present …
seed_v0_spike_fixture    SELF-CHECK PASSED — all 7 fixture entities present …
```

The fourth seeder is the one OEI-007 step 0.1 added to the `seed-fixtures`
target — this evidence run is the first full-suite run that exercises it, and
it is the reason the spike-domain tests (`SPIKE-PR-001`) pass rather than 422.

Run command (identical for 08 and 09, so the two are comparable):

```
DATABASE_URL='postgresql+psycopg://ece:ece@127.0.0.1:55432/ece' \
ECE_SERVER_TODAY_ANCHOR=2026-09-22 \
no_proxy=127.0.0.1,localhost NO_PROXY=127.0.0.1,localhost \
.venv/bin/python -m pytest -m "not eval and not eval_llm" -p no:randomly
```

`-p no:randomly` disables test-order randomisation so 08 and 09 are directly
comparable rather than being two samples from a distribution.

## The one run that was not green

An earlier pre-commit run of the identical command produced

```
1 failed, 756 passed, 5 skipped, 3 deselected
FAILED tests/integration/test_s20_audit_webhook.py::test_webhook_receives_event
  assert 0 >= 1   where 0 = len([])
```

`08b-flake-analysis.txt` is the experiment that decides whether that was an
OEI-008 regression. Short answer: no — the same test fails at the same rate
(1/12) against **HEAD source with no OEI-008 code loaded at all**, and its body
is a fixed `time.sleep(0.5)` after a background-thread POST. Pre-existing
load-sensitive flake; see that file for the method and the raw run lines.
