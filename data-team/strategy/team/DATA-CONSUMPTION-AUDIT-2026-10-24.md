# Data consumption audit, 2026-10-24 (read-only)

Labels: M = measured today (one read-only connection, 20s statement timeout, chunked by company_id, nothing run on core.fact without a company filter). A = ASSUMED. Backends at start: platform only, no app sessions.

## 1. What we consume
- DB 47 GB (M): core 35 GB, analytics 12 GB, raw 0.09 GB. Compute 2 GB / max_connections 90 / shared_buffers 512 MB (M); plan tier cost not visible, A (Pro).
- core.fact 76.7M rows = 32 GB: table 11 GB + indexes 20 GB = about 417 B/row. canonical_fact 17.0M = 4.7 GB. metric_value 13.5M = 4.6 GB. Ownership tables 2.7 GB, yfinance_statement_line 0.9 GB, timeseries_outlier_check 0.75 GB.
- TTM: 784,191 rows, 705,336 flagged to archive (peer file ttm_cleanup, not re-run); at about 341 B/row that is about 0.24 GB (A). Trivial. No `canonical_fact_retired` table exists.
- **Storage bucket `raw` is 94 GB (M): 79 GB companyfacts (44,630 objects, 1.86 MB avg) + 15 GB submissions (89,157).** Growth is 7-10 GB per week (M, weekly sums). Distinct bytes: companyfacts has only 8,829 distinct (cik, sha256) of 44,626 rows = 16 GB; latest-only = 11 GB. Submissions: 6.2 GB distinct, 0.6 GB latest.
- Nightly SEC fetches (M, raw tables, last 9 days): about 550-630 companyfacts + about 1,200 submissions per night, about 1.8 GB uploaded. **92% of the last 9 days' companyfacts fetches were byte-identical to an earlier fetch of the same CIK (6,409 of 6,994).** The same about 580 CIKs are refetched nightly. Filing-document fetches are not timestamped, so not measured. At 10 req/s, 1,800 requests is about 3 min: SEC rate is not the bottleneck.
- Nightly wall time (M, gh run view): run 39993949615 took about 5 h. Reprocess 125 min, with dedupe, derive-interim-quarters and derive-q4 each killed at the 1800 s cap, so the mapper stages were skipped. Facts stage 677 s. Coverage job: tag-library rebuild 90 min (failed), snapshot 9 min. Valuations and screener snapshot 50 min. The later run 40065297098 had reprocess 74 min (green). Reprocess covers 327 companies, the "filed in last 10 days" window. Likely only about 33 are new each night (A).

## 2. Share out of scope for top-1000 from 2015 (M, 77.0M rows over 5,226 companies; cohort_v1_1, 1,000 ids, 2 of them have no facts: 1008, 1525)
| slice | rows | share |
|---|---|---|
| cohort, all years | 24.0M | 31.2% |
| cohort, 2015+ (period end), all tags | 17.4M | 22.5% |
| cohort 2015+, tags in concept_mapping (90 mapping rows) | 4.5M | 5.9% |
| non-cohort | 53.0M | 68.8% |
| pre-2015, all companies | 16.8M | 21.8% |
| **outside "cohort + 2015+"** | **59.7M** | **77.5%** |
| rows on tags with no concept_mapping | 55.5M | 72% (library says 64% on its own counts) |
| is_authoritative=false | 34.0M | 44% |
| is_derived | 6.3M | 8% |

Sample (3 companies, DATA-INFERRED): 56k rows are 31k distinct keys; 58% of rows are same-value repeats of a key across filings, and 7% of keys have no authoritative copy (conflicts). So most non-authoritative rows look like repeated copies, but conflict-fill uses some, so do not delete blindly.

## 3. Levers (size / risk)
1. Skip upload and refetch when sha256 is unchanged; fetch companyfacts only on a new accession. Cuts 63-68 GB of Storage (79 to about 16) and about 90% of companyfacts fetches. Risk low (identical bytes keep immutability). Deleting old duplicate objects needs explicit authorization.
2. Reprocess by watermark ("new accession since last normalize") instead of the 10-day window, plus a weekly sweep. Cuts the set from about 327 to about 33 companies (A). Risk low-medium.
3. Archive pre-2015 (or pre-2014 to keep a growth margin; not measured) to a cold table: 16.8M rows, about 7 GB. Risk medium (TTM and growth comparatives).
4. Hot table = cohort 2015+ all tags + others' 2015+ mapped tags: 29.6M rows (38%), saving 47M rows, about 19.8 GB (A, 417 B/row). Risk high: coverage growth comes from today's unmapped tags. The payload stays in Storage, so it can be rematerialized.
5. Drop unneeded non-authoritative repeat copies: up to about 14 GB (A), but provenance and conflict-fill need them. Needs a dry-run first.
6. Unused indexes (M, idx_scan=0, stats never reset): idx_fact_raw_object_id 1.4 GB and idx_fact_supersedes_fact_id 0.8 GB. All 119 never-scanned non-unique indexes total 3.1 GB. Risk: FK delete cost, so drop after archiving.
7. core.fact has never been autovacuumed (10.6M dead tuples = 12%). Set a per-table scale factor. This reuses space but does not shrink the file.
8. FSDS is useful for backfill and validation (one file per quarter, 60-128 MB). It does not reduce what we store. Not needed nightly.

## 4. Cannot lower
The product universe of 5.2k companies (canonical_fact and metric_value, 9.3 GB). The 3 indexes serving hot reads (fact_pkey 7 GB with 13M scans, unique key 3.4 GB, company_concept_period 3.3 GB). The latest raw payload per CIK. Raw immutability for changed filings. The nightly index and submissions diff. A reduced cohort cannot replace the full-population screener without a founder scope change.

## 5. Ranked plan
1. Lever 1. Biggest saving, smallest effort. Storage goes from 94 GB to under 20 GB and stops growing 9 GB/week. Nightly runtime falls a few minutes. $: Storage is about 94 GB against a 100 GB included allowance (A), so it removes imminent overage, a small amount of money.
2. Lever 2. Largest runtime effect: reprocess about 70-125 min to about 10-20 min (A, linear). It also removes the stage timeouts.
3. Levers 6 and 7 with the first archive.
4. Lever 3, then Lever 4 only after the founder confirms scope.
5. Lever 5 last, after a dry-run.
Supabase cost impact is small either way (disk about $0.125/GB-month, A). The real gain is runtime and reliability.
