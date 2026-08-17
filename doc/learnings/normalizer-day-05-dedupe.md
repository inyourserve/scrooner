# Normalizer Day 5 — Duplicate/Overlap Resolution

## Finding: real value conflicts are ~6.6% of duplicate groups, not a rare edge case

Before writing `dedupe.py`, queried `core.fact` directly (already populated by Day 4) for how many `(company, concept, unit, period)` groups have more than one row, and how many of those actually disagree on value rather than just repeating the same number across filings. 48,360 groups have duplicates; 3,178 of them (~6.6%) genuinely disagree.

### How it was found, and what it turned out to be

Pulled several real conflicting groups in full detail before designing the resolution rule. Pattern was consistent across all of them: small, non-material revisions companies make to prior-period comparatives in *later* filings, without ever filing a formal `10-K/A`. E.g. JPM's `DerivativeNotionalAmount` for 2013-12-31: the original 10-K and the next 10-Q both report $70.430T, then starting with the 10-Q filed 2014-08-04 it quietly becomes $70.413T (a ~0.024% change) and stays there through the next 10-K — no amendment on file anywhere. Same pattern on `AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent` (a ~$15M/$206.9B revision) and others.

This is real, expected EDGAR messiness (exactly what doc 09 anticipated with "flag it when they don't [agree]") — not a bug in Day 4's extraction, and not rare enough to treat as an edge case. It changed the design: a log line isn't sufficient "flagging" at this volume: it needs to be genuinely queryable.

### Design

No new table needed. `core.fact.is_authoritative` (already in the schema from Day 1) does the whole job:
- Singleton group: untouched (stays the Stage 2d default, `true`).
- Duplicate group, all rows agree: earliest-filed row → `true`, every later repeat → `false`. Earliest-filed is the most defensible "primary source" — where the value was first disclosed, independent of how many later filings repeat it as a comparative.
- Duplicate group, rows disagree: **every** row → `false`. Picking any single value here (even "most recent") would be exactly the silent guess doc 09 prohibits. A genuine unresolved conflict is then fully queryable directly against `core.fact` with no new schema: `group by (company,concept,unit,period) having count(*) > 1 and bool_or(is_authoritative) = false`.

Added a read-only `conflicts` CLI command over that same query, for manual review — not automated resolution. Formal restatements (`10-K/A`) stay Stage 2f's job; this stage only handles same-form-type disagreement between an original filing and a later comparative repeat, not amendment supersession.

### Verification

- Spot-checked both directions: AAPL's Q1 FY2024 revenue (agreed duplicate) → earliest row `true`, later comparative `false`. JPM's `DerivativeNotionalAmount` conflict (5 rows, 2 distinct values) → all 5 `false`.
- Global consistency check across all 48,360 duplicate groups: zero groups with the wrong authoritative-row count (agreed groups must have exactly 1 `true`; conflict groups must have 0).
- Zero singleton facts incorrectly touched.
- Reran the whole job — identical stats (48,360 / 45,182 / 3,178), confirming idempotency.
- Same `ON CONFLICT`-adjacent tuple-bloat pattern as Day 4 (this time from repeated `UPDATE`, not `INSERT ... ON CONFLICT`) — 126,748 dead tuples after two runs, reclaimed with `VACUUM FULL` back to 52 MB. Expected now, not a new finding; the lesson was already captured Day 4.

### Why it matters going forward

Don't estimate the volume of a "flag, don't resolve" case from the docs' framing alone ("flag it when they don't" reads like an occasional exception) — query the real data first. The actual rate here (6.6%, thousands of groups) changed the design from "a log line is enough" to "this needs to be queryable structure." Same generalizable lesson as every prior Normalizer day, now on its fifth confirmation: check live data before finalizing the design, not after.
