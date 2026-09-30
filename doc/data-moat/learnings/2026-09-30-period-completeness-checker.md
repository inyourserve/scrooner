# 2026-09-30: Period completeness checker

## Why

Airbnb had no P/E. Tracing it by hand showed a quarter of net income was missing: its FY2025 net income was filed twice, as $2,511,000,000 and $2,511,277,000. Both values were marked non-authoritative (the Stage 2e conflict rule), so there was no full year, Q4 couldn't be derived, TTM broke, and P/E went blank. Earlier gaps were also found by hand: 348 never-normalized filings, and Cardinal Health's 10-Q missing from SEC's feed. The founder asked for a systematic check whose findings are stored, so each fix round can build on the last.

## Design decisions

- **A separate checker, no separate silo.** The tag library answers "which tag feeds this concept". Completeness answers "did every filed period arrive". The checker writes into the existing data truth layer (`company_data_finding`), plus one period-level table joined on the same keys.
- **Expected periods come from filings, not a calendar**, so a non-calendar or late filer isn't flagged for periods it never filed.
- **Cause over count.** One blank quarter can be our bug, SEC's gap, or a filer's error, and each needs a different fix.

## Findings on the first run

- **SEC's own Company Facts feed lacks some filings.** PayPal's 2026-07-28 10-Q (accession `0001633917-26-000082`) was absent two months after filing; the latest accession in its feed was the May 10-Q. 159 companies' recent periods are affected. "No facts attached" first looked like our miss, but a normalization run adds nothing from a payload that lacks the filing, and it doesn't update `raw_object_id` on existing rows. So only asking SEC distinguishes the two. The checker probes `dei:EntityCommonStockSharesOutstanding` (every cover page), falling back to `us-gaap:Assets`. Result: 263 filings confirmed absent and 31 present-but-unprocessed.
- **Rounding conflicts blank whole years at large companies.** JPMorgan's FY net income 2021–2025 and Airbnb's FY2021–2025 are missing for this reason. Most-recent-filing-wins for ≤0.1% conflicts is the fix candidate (the open question noted in the Frames checker learnings).
- **Stock-split restatements look like filer errors.** Apple's 2019–2020 EPS has pre- and post-split values for the same period. It's classified `conflict_split`, not `conflict_material`, so it's routed to split adjustment rather than blamed on the filer.
- **Performance.** The first trace joined `core.fact` by tag and scanned for 10+ minutes on six companies. Joining candidate periods first (company-first period index), then `(company_id, concept_id, period_id)` exact index hits, brought all active companies down to about 8 minutes.

## Next fixes, ranked by the stored findings

1. `conflict_rounding`: resolve ≤0.1% filing disagreements to the most recent filing (Airbnb, JPM).
2. `not_in_sec_feed`: a rendered-report or XBRL-instance reader for filings SEC's feed lacks.
3. `q4_not_derived` / `quarter_not_derived`: derivation gaps in `normalizer/derived.py`.
4. `no_mapped_tag`: feed `concept_gap_lead` / tag verdicts.
