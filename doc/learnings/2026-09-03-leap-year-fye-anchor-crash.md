# 2026-09-03 — A leap-year date-arithmetic bug silently zeroed out 29 companies' entire `core` footprint

## What happened

While investigating a "Parser 3" candidate for `revenue`/`operating_income` coverage gaps (doc 42), sampling real companies missing `revenue` (non-financial, non-SPAC, non-biotech) surfaced Artificial Intelligence Technology Solutions Inc. — a real company whose live SEC Company Facts payload has 42 real, correctly-tagged `RevenueFromContractWithCustomerExcludingAssessedTax` values under the exact tag this project's `concept_mapping` already recognizes. Yet `core.fact` had **zero rows for this company, for any tag** — not a Mapper/tag gap at all, a much earlier failure.

Broadened the check: **29 active companies** (out of 5,216) had real `core.filing` rows (Collector-level identity worked) but **zero `core.period` rows** — meaning Normalizer Stage 2b (`periods`) had never successfully processed them, and every later stage silently had nothing to build on.

## Root cause

`normalizer/periods.py`'s `_bracket_fye()` extrapolates a company's fiscal-year-end pattern forward/backward past its observed anchor dates by stepping one calendar year at a time:

```python
candidate = date(candidate.year + 1, candidate.month, candidate.day)  # and -1 the other direction
```

For a company with an **observed Feb 29 fiscal-year-end anchor** (a real, if unusual, calendar-based FYE), this crashes with `ValueError: day is out of range for month` the moment the extrapolation steps into a non-leap year — which is 3 years out of every 4. MannKind Corp (CIK 0000899460, a real, unambiguous domestic 10-K/10-Q filer, not a foreign issuer or an XBRL-less trust) hit this directly: `periods.normalize.done` reported `errored=1` for it with no further detail in the batch summary output, and the exception silently stopped that company's processing — Stage 2b's own docstring says "the batch itself keeps going past a single company's failure," which is correct batch behavior but meant this specific company was permanently stuck at zero `core.period` rows with no visible alarm.

## Scope, checked before fixing

Of the 29 companies with zero `core.period` rows: **24 have no `raw.sec_companyfacts` payload at all** (real royalty trusts and asset-backed/structured-product trusts — SEC's Company Facts API genuinely has nothing for these, a structural gap, not this bug). Of the remaining 5 with a real payload, the periods stage crashed on exactly this Feb-29 pattern for at least MannKind; the same fix cleared periods successfully for all 5 with `errored=0` afterward.

## Fix

Added `_step_year(d, delta)` — steps a `date` by whole years, rolling Feb 29 to Feb 28 in a non-leap target year instead of raising, the same convention already implicit in this file's own `FULL_YEAR_MIN_DAYS`/`MAX_DAYS` band (350–380 days) treating adjacent Feb-28/Feb-29 fiscal years as the same annual cadence. Replaced both `date(candidate.year ± 1, ...)` call sites in `_bracket_fye` with it. New regression test (`test_feb_29_fye_anchor_extrapolates_without_crashing`) reproduces the crash directly via `classify_period()` with a real Feb-29 anchor, both extrapolation directions. Full suite: 360/360 passing after the fix (was 359 before the new test was added).

## Recovery run

Re-ran the full Normalizer chain (periods → units → facts → dedupe → restatements → derive-interim-quarters → derive-q4) and the full Mapper chain (resolve-facts → resolve-concept-fallbacks → calculate → growth → ttm-returns → calculate-expanded-metrics → calculate-piotroski → calculate-quality-flags → calculate-reconciliation → calculate-tax-reconciliation → calculate-fcf-growth → calculate-dividend-streak) scoped to the 29 CIKs. Real, verified output for previously-100%-empty companies: **29,468 new `core.fact` rows** (`skipped_period_not_found` dropped from 48,580 to 0, confirming the fix — every one of those 48,580 skips before the fix was this exact bug's downstream symptom, not real missing data), 559 derived Q2s, 706 derived Q3s, 997 derived Q4s, 5,755 canonical facts resolved, ~2,000 metric values computed across all stages. Zero errors in any stage on the recovery run.

## Lesson

**A batch job that correctly "keeps going past a single company's failure" can still leave that company permanently, silently at zero — the resilience that protects the batch is exactly what hides the gap from ever being noticed.** This bug likely existed since Normalizer Stage 2b was first built (2026-08-15) and was never caught by the full-population run "completing successfully" on 2026-08-26, because success was measured in aggregate (row-count deltas), not by checking whether every company with real, fetched SEC data actually made it into `core`. The check that surfaced this wasn't "did the batch report errors" (it did, buried in a per-company debug line, not the summary) — it was "does every company with a real upstream payload have a downstream row," a completeness check the aggregate stats never make visible. Worth periodically re-running that completeness check (companies with `core.filing` rows but zero `core.fact`/`core.period` rows) rather than trusting a clean-looking aggregate summary alone — the same "always spot-verify, never trust the printed summary alone" discipline this project's `coverage_snapshot.py` write-anomaly finding already established for a different table.
