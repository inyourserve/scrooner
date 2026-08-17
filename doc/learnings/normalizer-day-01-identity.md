# Normalizer Day 1 — Identity Normalization

## Problem: doc 09's original `core.filing` schema had two columns nothing could populate

The first draft of doc 09's `core.filing` table (written before any Normalizer code existed) included `fiscal_year`/`fiscal_period` columns, on the assumption SEC's submissions data would carry them per filing the same way it carries `filingDate`/`form`/`accessionNumber`.

### How it was found

Downloaded and inspected a real submissions payload (AAPL's base file and one continuation page) from Supabase Storage before writing the parser, rather than coding against the assumed shape. The `filings.recent` block (and every continuation page, same flat shape) only has: `accessionNumber`, `filingDate`, `reportDate`, `acceptanceDateTime`, `act`, `form`, `fileNumber`, `filmNumber`, `items`, `isXBRL`, `primaryDocument`. No fiscal year/period field anywhere. Made sense on reflection too: a single 10-K reports facts for the current year *and* comparatives from prior years — fiscal year/period is a property of a reported *fact* (or a period), not of the filing document itself.

### Fix

Dropped `fiscal_year`/`fiscal_period` from `core.filing` in both the migration (`0003_core_schema.sql`) and doc 09's schema table, before any row was written. `core.period` (Stage 2b, not yet built) is where fiscal year/period actually belongs, tied to each fact's period.

### Why it matters going forward

Checking the real payload shape before writing the schema (not just before writing the parser) caught a design mistake at zero cost. A migration applied against a wrong assumption would have shipped two columns permanently null, discovered only once Stage 2b tried and failed to backfill them from a source that was never going to have that data. Same lesson the Collector's own day-02/day-03 entries already recorded, just recurring at the Normalizer layer: verify the live payload shape before designing the table for it, not after.

## Problem: no source in `raw` carries historical ticker intervals

`core.listing` was designed with `effective_from`/`effective_to` columns, intended to capture things like Block's ticker change from `SQ` to `XYZ` (December 2021) — one of the golden-10 companies was chosen specifically to stress this case.

### How it was found

Pulled Block's (CIK `0001512673`) live submissions payload and checked its `tickers`/`exchanges` arrays directly: `['XYZ', 'BSQKZ']` / `['NYSE', 'OTC']`. No `SQ` anywhere. `raw.company_universe` (from `company_tickers.json`, upserted/current-state-only per doc 08) doesn't carry it either — confirmed by design, not just by omission, since that table is explicitly a mirror of SEC's *current* list. Neither Collector-fetched source has ever captured historical ticker state; there was nothing to normalize into `effective_from`/`effective_to` even in principle, not just an implementation gap.

### Fix

`core.listing.effective_from`/`effective_to` stay in the schema (real intervals may become available later, e.g. from a market-data vendor) but are populated as `null` for now — documented in doc 09 and in `identity.py`'s module docstring as "currently listed, start date unknown" rather than silently leaving the columns unexplained. Confirmed the golden-10 acceptance check for this company checks what's actually derivable (2 current tickers, both correct) rather than asserting ticker history the data can't support yet.

### Why it matters going forward

A golden-company test case chosen to "stress ticker changes" doesn't automatically mean the current pipeline stage can resolve that history — it depends on whether any upstream source actually captured it. Company Master (doc 06 Part 4) is where ticker-change history is scoped to eventually get resolved (via a source not yet built), not something to fabricate early just because the schema has a column for it. Worth re-checking this doc when Company Master's design starts, since `formerNames` (company-name-level history, with real `from`/`to` dates) *is* present in submissions data and wasn't used here — it's a `core.company` question, not `core.listing`, and out of Day 1's scope.
