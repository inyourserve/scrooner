# Day 7 — Definition of Done

## Problem

Day 7 wasn't a new-feature day — it was a consolidation/proof day (doc 08: "End-to-end proof against doc 06's Definition of Done ... all demonstrated, not asserted"). The risk wasn't a missing feature, it was writing up a Definition-of-Done report that quietly re-asserted things from memory of earlier days' work instead of re-checking them live, which would defeat the entire point of the day.

## How it was found

Went through doc 06's 8-item checklist one at a time and asked, for each: is there an actual `run_id`, row count, or query output backing this, right now, in the live DB — not a recollection of a `doc/learnings/` entry? For 7 of the 8 items, real evidence already existed in `raw.collector_runs`/`raw.sec_*`/`raw.collector_errors` from Days 2-6 and just needed to be queried and cited precisely (exact run IDs, exact stats). One item did not: "(4) respect SEC fair-access limits" had only ever been a code-level design claim (`_RateLimiter` capped at `sec_max_requests_per_second=8.0`) — nobody had actually timed real requests through it and computed an achieved req/s.

## Fix / decision

Ran two fresh, real measurements against the production `SECClient`/`_RateLimiter` classes (not reimplementations, not mocks):

1. 40 sequential real HTTP GETs to `data.sec.gov/submissions/...` for 40 distinct real CIKs pulled from `raw.company_universe`, through the actual client used in production. Result: **2.864 req/s average**, max 4 req/s in any 1-second sliding window, all 40 returned HTTP 200 — real Collector traffic runs well under the 8 req/s configured buffer (and SEC's 10 req/s ceiling, doc 07 §3) because real network latency (~300ms/request) already exceeds the limiter's 125ms minimum spacing.
2. Because (1) only proves *normal* traffic stays under the ceiling, not that the limiter would actually cap throughput under near-zero latency, drove the real `_RateLimiter` class directly with 80 back-to-back `.wait()` calls and no I/O in between — the actual worst case for exceeding the ceiling. Result: **7.863 req/s average, max 8 in any 1-second window** — confirms the mechanism itself holds the line at ≤8/s even when nothing else would slow it down.

Also ran a fresh (not just cited-from-Day-6) exhaustive integrity reconciliation (`uv run scrooner-report reconcile`) live today: 364/364 stored objects (186 companyfacts + 178 submissions) still exist and still hash to their recorded SHA-256, zero unexplained deltas, exit code 0. Numbers are unchanged from Day 6's own pass because no new bootstrap/incremental run has added objects since — the point of rerunning wasn't to find something new, it was to not simply cite an old number as if it were still verified.

All 8 of doc 06's Definition-of-Done items, plus a fresh live re-check of doc 08's condensed 5-clause Day 7 text via the `verify-collector-day` skill, came back PASS with real, citable evidence — compiled into `doc/08b_Collector_Definition_of_Done_Evidence.md`.

## Why it matters going forward

"Demonstrated, not asserted" has to apply to the *proof-writing* step itself, not just the code. A consolidation day that only reads back through `doc/learnings/` and repeats what it finds there is still an assertion — it's re-asserting Day 4's evidence instead of re-verifying it. The discipline that made this genuinely a proof rather than a summary was querying the live DB fresh for every cited number in this session (not from memory of what a prior day's entry said), and specifically noticing which one of the 8 items had never actually been measured at all (fair-access) rather than assuming "the code looks right" was equivalent to "demonstrated." This is the same lesson as every prior day's entry, just applied one level up: to writing the final report, not just to writing the code.

## Collector build status

All 7 days of doc 08's plan are now complete with live evidence: Day 1 (scaffold/client), Day 2 (company universe), Day 3 (companyfacts/submissions), Day 4 (retry/checkpoint/resume), Day 5 (incremental updates), Day 6 (logs/integrity), Day 7 (end-to-end Definition-of-Done proof, this entry). Per doc 06: "Then — and only then — the team moves to the Normalizer." `doc/PROGRESS.md`'s Data Collector row is updated to ✅ accordingly. No Normalizer work was started as part of this day.
