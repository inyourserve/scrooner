# Day 2 — Company Universe

## Problem

`raw.company_universe` was originally designed with `cik` as the sole primary key. That's wrong: CIK→ticker is one-to-many, not one-to-one.

## How it was found

Before writing `collector/universe.py`, fetched SEC's real `company_tickers.json` live (10,396 entries) and checked it programmatically rather than assuming its shape from memory or from doc 06's prose description. Found 1,448 of 7,995 distinct CIKs (18%) have more than one ticker — e.g. Alphabet, CIK `0001652044`, has four: `GOOGL`/`GOOG`/`GOOGM`/`GOOGN`.

Also found the file has no `exchange` or `status` field at all, contradicting what the original schema draft assumed it would provide.

## Fix

- Primary key changed from `cik` alone to the composite `(cik, ticker)`.
- `exchange`/`status` columns dropped entirely. `exchange` isn't in this source (it's in the Submissions API instead — see Day 3). There's no SEC-provided `status` field anywhere; keeping a `status` column would mean the Collector deciding what "active" means, which is interpretation, not collection.
- Applied directly to the live Supabase table (it was still empty — safe to drop/recreate) rather than left as a doc-only correction.

A separate, unrelated finding during the same check: one single live fetch of `company_tickers.json` returned 10,391 instead of 10,396. Re-fetched three more times a few seconds apart — all three came back 10,396, byte-identical. Concluded: transient CDN edge-cache inconsistency on SEC's side, not a bug — but only concluded that *after* repeating the check, not by assuming it away on the first anomalous read.

## Why it matters going forward

Don't design a schema — or trust a doc's description of an external API's shape — from memory or from another doc's prose. Fetch it live and inspect the real response before the schema goes into a migration, especially before that migration gets applied to production. This became the standing practice for the rest of the build (see Day 3's TSM/`ifrs-full` and JPM/pagination findings, which were caught the same way).
