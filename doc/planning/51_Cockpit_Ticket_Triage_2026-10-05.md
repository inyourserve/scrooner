# Cockpit Ticket Triage — 2026-10-05

**Status: Investigation in progress, written for tonight's fix session.** Full day task: pick up every open `analytics.company_data_finding` ticket, group by root cause, find the highest-leverage ("whale") fixes, document findings — **investigation and write-up only, fixing happens tonight.**

## Starting state

60,188 open tickets (as of this morning, before today's cleanup work — see note below on staleness). Grouped by `summary`/`finding_type`:

| Summary | Count | Companies | Type |
|---|---|---|---|
| Periods missing: no mapped tag in the filing | 17,735 | 4,067 | data_limit |
| Periods missing: Q4 not derived | 16,968 | 4,129 | pipeline_bug |
| Periods missing: quarter filed only as year-to-date | 9,622 | 3,806 | pipeline_bug |
| Periods missing: filing absent from SEC Company Facts | 5,681 | 735 | data_limit |
| Periods missing: authoritative fact not resolved | 4,998 | 2,741 | pipeline_bug |
| Periods missing: filings disagree materially | 3,137 | 1,612 | filer_error |
| Periods missing: filings disagree by a stock-split ratio | 2,001 | 1,046 | pipeline_bug |

**⚠️ Known staleness**: `analytics.company_data_finding` (the cockpit table) is a snapshot that predates some of today's reprocessing. `analytics.period_gap` (the live table `period_completeness.py` writes) already reflects today's balance-sheet-identity fix and the period-corruption cleanup. Re-sync the cockpit from `period_gap` before tonight's session to get accurate current counts — the numbers below are cross-checked against `period_gap` directly, not the stale cockpit snapshot.

---

## Finding 1 (WHALE, already shipped): balance-sheet identity fallback

**Status: DONE, not a tonight task.** See `pipeline/CLAUDE.md`'s 2026-10-05 entry. `total_liabilities_resolved`/`stockholders_equity_resolved` now ~100% of the population. `avg_concept_coverage_score` 85.48%→85.62%.

## Finding 2 (WHALE, root-caused and code-fixed, cleanup in progress): corrupted filer-date periods

**Status: Code fix shipped, data cleanup running in background as of this writing.** 10,227 `core.period` rows span >400 days — real filer-side XBRL context-date corruption (truncated years like "205-01-01", Oracle's 1900-2199 sentinel span, companies spanning into 1967/1976/2108). 88,903 affected facts were `is_authoritative=true` — live corruption, not cold data. Confirmed real impact: MIND Technology had two competing `canonical_fact` rows for the same quarter's operating income.

- **Root cause fixed**: `normalizer/periods.py::extract_distinct_periods()` now rejects implausible periods before any `core.period` row is created (commit `bb9d63d`).
- **Existing bad data**: 88,903 facts marked `is_authoritative=false` (reversible, not deleted). 1,754 affected companies' full calculation chain is being rerun as of this writing — check `/tmp/bogus_remaining_stages.log` for completion before assuming this is done.
- **Nothing left to do here tonight** unless the rebuild didn't finish — verify first.

## Finding 3 (REJECTED, documented): dividends_per_share fallback

**Status: Closed, do not re-attempt without new evidence.** `dividends_paid ÷ shares_outstanding` looked like a candidate but verified unsafe two ways: (a) internal coexistence only 67% agreement, (b) real yfinance ground truth (Digital Realty Trust's actual $1.22/share/quarter vs. our implied $2.497 — `dividends_paid` bundles preferred-stock dividends with common). No safe derivation exists today.

## Finding 4 (WHALE CANDIDATE, sized, not yet fixed): `conflict_split` mislabeling bug

**Real, scoped, high-confidence fix for tonight.** `sanity/period_completeness.py::_is_split_ratio()` is a generic numeric check ("do two values differ by a whole-number ratio ≥2, within 2%") applied to **every** concept, with no awareness that only per-share/share-count concepts (`basic_eps`, `diluted_eps`, `dividends_per_share`, `shares_outstanding` — the same 4 already in `dedup_majority_resolver.py`'s `SPLIT_AWARE_CONCEPTS`) can legitimately be affected by a stock split.

**Confirmed via real samples**: `total_assets_resolved` tickets labeled "conflict_split" show ratios like 41.3x, 38.76x, 20.86x, and ~938x (Palomino Laboratories) — none are real split ratios (companies don't do 41-for-1 splits). These are almost certainly genuine material disagreements or **unit-scale filer errors** (the ~938x one especially looks like a dollars-vs-thousands mistake) currently hidden under an incorrect "harmless split" label.

**Scope**: ~1,810 tickets across 10 non-per-share concepts (`cash_and_equivalents_resolved` 366, `income_before_tax_resolved` 274+349, `income_tax_expense_resolved` 229+686, `cash_flow_investing_resolved` 223+320, `cash_flow_financing_resolved` 215+316, `cfo_resolved` 162+127, `stockholders_equity_resolved` 92+145, `revenue_sanity_resolved` 75+73, `net_income_resolved` 39+30, `total_assets_resolved` 37+9, plus smaller balance-sheet concepts) are currently mislabeled "conflict_split" when they're really `conflict_material`.

**Fix for tonight**: scope `classify()`'s call to `_is_split_ratio()` to only the 4 real per-share/share-count concepts. Everything else falls through to `conflict_material`, where it belongs — surfacing real disagreements (including possible unit-scale bugs) instead of hiding them.

**Bonus investigation thread this unlocks**: once un-hidden, the "conflict_material" dollar-value tickets with suspiciously round large ratios (~10x, ~100x, ~1000x) are worth a dedicated sweep for unit-scale filer errors — a different, real bug class from the split mislabeling itself, just newly visible once the mislabel is fixed.

## Finding 5 (WHALE CANDIDATE, sized, modest yield): extend majority-vote dedup to income-statement concepts

**Real but smaller than hoped — do, but don't oversell it.** `dedup_majority_resolver.py`'s `SAFE_CONCEPTS` list only covers 9 balance-sheet concepts, deliberately excluding income-statement concepts (revenue, net_income, cfo, operating_income, income_tax_expense, income_before_tax) because a prior sample showed only 68-75% overall agreement ("a blind majority vote would silently pick a wrong number ~25-30% of the time").

**Found a real instance**: American Express FY2016 `income_tax_expense` has 3 raw filed values (2688M, 2667M, 2688M — a clear 2-of-3 majority) but Stage 2e marked all 3 non-authoritative, and this exact concept family is excluded from the fix that would otherwise catch it.

**Sized the real opportunity** (sampled 800 of 27,765 "not_resolved"/"q4_not_derived" income-statement gaps): 333/800 (42%) had no FY row at all (a quarterly gap, not an FY-resolution issue — not helped by this fix). Of the remaining 467, only 16 (3.4%) had a clear real majority. **Extrapolated: roughly 400-600 real fixes population-wide, not thousands.** Worth doing — it's safe, proven, and matches an already-built mechanism — but temper expectations; this is not the whale Finding 4 is.

**Fix for tonight**: extend `dedup_majority_resolver.SAFE_CONCEPTS` to the 6 income-statement concepts (revenue, net_income, cfo, operating_income, income_tax_expense, income_before_tax), reusing the exact same majority-vote logic already proven safe for balance-sheet concepts. Verify the extrapolated ~400-600 number against the real run before trusting it.

## Finding 6 (classification, not a fix): `not_in_sec_feed` cluster is mostly already-known structural absence

**No action needed beyond classification (Phase 3 work).** Top companies: Southern California Edison, Entergy Arkansas, Southern California Gas Co — these are the exact "wholly-owned utility co-registrant subsidiary" pattern already documented (2026-09-12 entry: these file combined 10-Ks under a parent's primary XBRL context, a genuine SEC/EDGAR-side limit, not a Scrooner bug). SIC breakdown also shows pharma/biotech/REITs (same pre-revenue/pass-through pattern as every other structural-absence finding this project has made) plus a cluster of BDCs (Hercules Capital, Stellus Capital BDC, Crescent Capital BDC, RAND Capital Corp) not yet explained — worth a quick check (are these genuinely sparse small-cap filers, or a real Collector gap?) before assuming structural.

## Not yet investigated (continuing)

- "quarter filed only as year-to-date" (9,622 tickets) — the known, harder cumulative-YTD cash-flow reconstruction gap. Not touched today.
- "no mapped tag in the filing" (17,735) — partially explained (structural absence for pharma/biotech/SPACs/REITs in the 5 concepts checked 2026-10-04/05), but the full 17,735 hasn't been swept concept-by-concept yet.
- The BDC sub-cluster inside `not_in_sec_feed` (Finding 6).
- Continuing to investigate — this document will be appended to throughout the day.

## Priority order for tonight (my recommendation)

1. **Finding 4** (`conflict_split` mislabeling) — highest confidence, clear fix, ~1,810 tickets correctly reclassified, may surface new unit-scale-error leads.
2. **Verify Finding 2's cleanup rebuild actually finished** before assuming it's done.
3. **Finding 5** (income-statement majority-vote extension) — safe, proven pattern, modest real yield (~400-600).
4. Investigate the BDC sub-cluster from Finding 6.
5. Start on "quarter filed only as year-to-date" (9,622) — the biggest still-unexplained bucket.
