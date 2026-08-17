# Normalizer Day 7 — Q4 Derivation + End-to-End Definition of Done

## Problem: per-group round trips timed out on large companies

The first version of `derived.py` did several individual queries per candidate `(concept, unit, fiscal_year)` group — an existence check, a period lookup-or-insert, a fact insert. Fine in testing on small groups, but JPM alone has 3,704 candidate groups. Running it for real hit `OperationalError: SSL SYSCALL error: Operation timed out` partway through, twice — the same class of problem doc 08's `day-04-retry-and-resume.md` already flagged for the Collector (a long-lived connection making a huge number of round trips is fragile), just rediscovered one layer up because this was the first Normalizer stage that didn't follow the load-everything-up-front-then-batch-write pattern the other five already used.

### Fix

Rewrote `derive_q4_for_company` to match `identity.py`/`periods.py`/`facts.py`'s existing shape: load all existing periods and all reported (non-derived) fact keys into memory up front, compute every derivation in Python, then two batched `executemany` writes (new periods, then new facts) instead of one query per group. Same logical result, drastically fewer round trips — a full golden-8 run went from repeatedly timing out to completing in under a minute.

### Why it matters going forward

An inconsistency in a new module's own design (not following a pattern already proven necessary five times in the same codebase) is its own category of bug, separate from getting the domain logic wrong. Worth checking new Normalizer/Mapper code against the established "load lookups up front, batch the writes" shape specifically, not just against domain correctness.

## Verification: derived values, not just "it ran"

- AAPL FY2024 revenue by quarter: Q1 $119,575,000,000 (already reconciled Day 4), Q2 $90,753,000,000, Q3 $85,777,000,000, FY $391,035,000,000. Derived Q4 = FY − Q1 − Q2 − Q3 = **$94,930,000,000**, matching Apple's actual real-world reported Q4 FY2024 revenue.
- `is_derived` distribution: 169,825 reported (`false`) + 4,397 derived (`true`) = 174,222 total facts — clean split, no ambiguity.
- Investigated MSFT's 96 "already reported, skipped derivation" cases before trusting the number: these are `CommonStockDividendsPerShareDeclared` facts — MSFT's 10-K directly discloses the per-quarter dividend (including Q4) in its own dividend-history table, since a declared dividend isn't something that needs FY-minus-quarters math the way revenue does. Correctly left alone, not overwritten with a derived guess.
- Reran the whole job — identical stats (14,907 candidate groups, 4,397 derived, 174 already-reported, 10,336 incomplete), confirming idempotency. One rerun attempt hung for several minutes with no error (stopped manually, checked `pg_stat_activity` for blocking locks — found none, just a stalled client-side connection) — retried cleanly in ~47s. Isolated, not a recurrence of the round-trip design problem above (already fixed by that point).
- **Incremental-processing evidence** (doc 09's DoD explicitly requires this, not previously demonstrated): snapshotted every company's `core.fact` row count, reran fact extraction for a single CIK (RDDT) only, and confirmed every other company's count was byte-for-byte unchanged. The `ciks`-scoped design already supported this from Day 4 onward; this is the first time it was actually exercised and checked, not just assumed from reading the code.

## Definition of Done — full evidence, not re-assertion

See `doc/09b_Normalizer_Definition_of_Done_Evidence.md` for doc 09's complete Definition of Done mapped item-by-item to real evidence from Days 1–7, mirroring how `doc/08b` closed out the Collector.
