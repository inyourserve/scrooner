# Mapper Day 4 — Point-in-Time Metric Calculation

Three real bugs this day, escalating in seriousness — the third is the most important finding of the whole Mapper phase so far, because it silently produced a *wrong number* rather than a safe null.

## Bug 1: NOT NULL violation on a real non-standard period

First run crashed outright: `period_label` NOT NULL violation on a 2010-01-01..2010-06-30 span. This is one of Normalizer Stage 2b's deliberately-unclassified non-standard durations (a 6-month YTD span) — `core.period.fiscal_period` is nullable there by design, but `metric_value.period_label` isn't. Fixed by skipping periods with no `fiscal_period` entirely — they don't fit the FY/Q1-4/TTM model this table represents, and Normalizer already made the correct call not to force a label onto them.

## Bug 2: duration and instant concepts for "the same period" are different `period_id`s

AAPL's FY2024 `net_income` (duration, `period_id=601`, 2023-10-01..2024-09-28) and FY2024 `stockholders_equity` (instant, `period_id=797`, 2024-09-28..2024-09-28) are genuinely different rows in `core.period`, even though both represent "AAPL FY2024." The first version of the resolver matched every input by strict `period_id` equality, so ROE and ROIC — both mixing a duration numerator with an instant denominator — came back `null` even when every underlying value actually existed. Fixed by anchoring on the duration period when one exists and matching instant inputs by **end date** against that anchor instead. `canonical_concept.statement` already losslessly encodes which behavior applies (`balance_sheet` → always instant, `income_statement`/`cash_flow` → always duration) — no new column needed, verified true for all 17 concepts before relying on it.

## Bug 3 (the important one): a partial summand list computed a wrong number instead of nulling

After fixing Bug 2, AAPL's ROIC computed as **346%** — accepted as suspicious rather than "not null, so probably fine," and investigated the same way Day 3's implausible 127.8% was. Found the cause: `total_debt` was genuinely unresolved for AAPL FY2024 (a real Stage 2e conflict, already known from Day 3), but `stockholders_equity` — also mapped to ROIC's `invested_capital_add` role — *was* resolved. The formula code checked only "does this role have at least one value," not "did every concept mapped to this role resolve," so it silently computed Invested Capital from equity alone, understating the denominator and inflating ROIC to an implausible number that was not flagged null at all.

This is categorically worse than Bugs 1-2: those produced a missing value (safe, traceable, matches doc 04's "null is a real outcome" principle) — this one would have produced a **wrong value that looked like a valid answer**, with no signal anything was off. Fixed by tracking which concepts actually resolved per role and requiring an exact match against which concepts are expected for that role (from `metric_definition_input`) — any role short even one expected concept nulls the entire metric for that period, with `is_null_reason='incomplete:<role>'`.

## Verification after all three fixes

- AAPL FY2024: `gross_margin` 46.21%, `operating_margin` 31.51%, `net_margin` 23.97%, `fcf` $108.807B, `fcf_margin` 27.83% — all hand-verified against known figures, exact matches.
- AAPL FY2024 `roe` = 164.59% (`93,736 / 56,950`, exact) — genuinely this high in real life due to Apple's aggressive buyback-driven equity reduction, not a bug; sanity-checked as plausible before accepting it.
- AAPL FY2024 `roic` now correctly `null` (`incomplete:invested_capital_add`) rather than a wrong 346%.
- AAPL's real ROIC values, for periods where every input genuinely resolves: FY2021 64.3%, FY2014 30.6%, FY2013 28.7% — a sane, plausible range once the bug was fixed.
- MSFT's `current_ratio` (a pure-instant metric, unaffected by Bugs 2-3): 1.2-1.4 across recent quarters — matches real-world expectation.
- Reran the whole job twice more after each fix — final state idempotent (2,271 computed / 1,187 null, unchanged on rerun).
- `analytics.metric_value`: 3,458 rows, 56 MB total DB (unchanged from Day 3, well within the free-tier budget).

## Why it matters going forward

Bug 3 is the clearest example yet in this entire build of why "not null" is not the same as "correct." Every prior day's discipline was "check a plausible-looking number a second way before trusting it" — this day's finding sharpens that into something more specific for any future formula work (Stage 3e's TTM windows, Company Master's price-dependent metrics): a formula with a summed, multi-concept role needs an explicit completeness check per role, not just a truthiness check on the accumulated list, or a missing summand will silently corrupt the result instead of correctly nulling it.
