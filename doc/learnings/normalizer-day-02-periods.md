# Normalizer Day 2 — Period Normalization

## Problem: a period's own reported `fy`/`fp` describes the filing, not the period

The plan was to key `core.period` on `(company_id, fiscal_year, fiscal_period, start_date, end_date, period_type)`, trusting each XBRL fact's own `fy`/`fp` fields (visible right there in every companyfacts entry) as the period's fiscal-year/quarter label.

### How it was found

Before writing `periods.py`, searched AAPL's real companyfacts payload for every entry sharing the exact same `(start, end)` = `(2017-07-02, 2017-09-30)`. Found the same real calendar quarter reported three different ways:
- `fy=2017, fp='FY'` — in the FY2017 10-K's own supplementary quarterly footnote
- `fy=2018, fp='FY'` — as a prior-year comparative in the FY2018 10-K
- `fy=2018, fp='Q1'` — as context in a later 10-Q

Same period, three different `(fy, fp)` labels, depending only on which filing happened to mention it. `fy`/`fp` is metadata about the *reporting filing*, not an intrinsic property of the period.

### Fix

Redesigned `core.period`'s identity to `(company_id, start_date, end_date, period_type)` — the objective calendar span — before any row shipped (table was empty; dropped and recreated per the same precedent the Collector used for pre-data schema fixes). `fiscal_year`/`fiscal_period` are now DERIVED columns, nullable, explicitly outside the table's uniqueness key. Derivation doesn't trust any entry's `fy`/`fp` field at all — instead:
1. Build each company's own set of real historical fiscal-year-end dates empirically, from its own full-year-length (350–380 day) duration periods — no guessing from the nominal `fiscalYearEnd` (MMDD) in submissions, which wobbles by up to ~a week against real FYE dates (verified: AAPL's nominal `0926` vs actual 2016-09-24, 2017-09-30, 2018-09-29, ...).
2. For any period, bracket it between the nearest observed (or extrapolated) fiscal-year-end anchors, then assign `fiscal_year` from the bracketing anchor and `fiscal_period` (`Q1`–`Q4`) from how many ~91.25-day chunks separate it from the prior anchor.
3. Any duration that isn't ~90 days (quarter) or ~365 days (full year) — commonly ~180 day (half-year YTD) or ~270 day (three-quarter YTD) cash-flow-statement spans, or odd stub/since-inception periods — is left `fiscal_period = null` rather than force-labeled into the nearest quarter.

### Verification (not just "it ran")

- Structural: 0 `bad_instants`/`bad_durations` across 1,832 period rows (an instant row must have `start_date = end_date`, a duration row must not — checked directly, not assumed).
- AAPL's 19 derived `FY` end dates matched the public record exactly (2007-09-29 through 2025-09-27).
- AAPL FY2024 quarter ends derived as 2023-12-30 / 2024-03-30 / 2024-06-29 / 2024-09-28 — match Apple's actual reported quarter-end dates exactly.
- MSFT (June FYE) and NKE (May FYE) — same spot-check, both correct against their known real fiscal calendars.
- JPM (calendar FYE) correctly degenerates to plain Jan–Mar/Apr–Jun/Jul–Sep/Oct–Dec.
- The "unclassified" bucket's duration-day distribution clustered exactly at ~180d and ~272d (YTD spans) plus a long tail of genuine oddball stub/since-inception periods — no stray ~90-day values that should have been classified as quarters but weren't.
- Reran the whole job: identical row count (1,832), confirming idempotency.

### Why it matters going forward

A field that's *present and looks like exactly what you need* (per-fact `fy`/`fp`, sitting right next to `start`/`end` in the same JSON object) isn't automatically trustworthy for the purpose you have in mind — it can be authoritative for one thing (which filing/context reported this value) while being systematically wrong for another (what period this value covers). The fix was cheap only because the real payload was checked *before* the schema was built around the assumption, not after. Same generalizable lesson as Day 1's `fiscal_year`/`fiscal_period`-on-`filing` mistake, recurring one layer deeper: verify the live data's actual semantics, not just its field names, before designing identity/uniqueness around it.
