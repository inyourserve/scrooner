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

## Correction, 2026-10-02: the checker itself had the exact bug class it was built to catch

`CHECK_CONCEPTS` checked 5 of 6 concepts (`net_income`, `diluted_eps`, `cfo`, `total_assets`, `stockholders_equity`) against the **raw** canonical concept instead of its `*_resolved` display companion — the one the company page and screener actually read. Only `revenue` was checked correctly from the start (`revenue_sanity_resolved`).

Found by cross-checking the first run's own findings against the database directly: `net_income_resolved` already had Airbnb's FY2025 net income ($2,511,277,000, the corrected latest-filing value) and JPMorgan's full FY series, filled on 2026-09-29 by `conflict_resolution.py`'s restatement fill (commit `8e5599e`, landed before this checker's first run). The checker was reporting both as missing.

Fixed by pointing `CHECK_CONCEPTS` at the five `*_resolved` concepts. Cleared ~63,000 stale `period_gap` rows and ~19,000 stale findings recorded against the raw concept ids (deleted, not marked `fixed` — nothing was actually fixed; the checker was wrong). Reran full population:

| | First run (buggy) | Corrected |
|---|---|---|
| Periods present | 91.1% | 93.5% |
| Missing cells | 74,888 | 54,573 |
| Open findings | 21,864 | 15,774 |
| `conflict_rounding` (last 15mo) | 466 | 0 |
| `conflict_material` (last 15mo) | 505 | 50 |
| `conflict_split` (last 15mo) | 117 | 103 |

The conflict categories collapsed because they were exactly what the restatement fill already closed at the resolved layer — the raw layer is still deliberately blank per Stage 2e's design (dedupe.py's documented "flag, don't resolve" policy for disagreeing filings), that was never the bug.

**One category rose, and it's a real, newly-visible finding, not an artifact: `q4_not_derived` went from 515 to 792 recent periods** (net_income_resolved 372, diluted_eps_resolved 151, revenue_sanity_resolved 140, cfo_resolved 129, in the last 15 months). Root cause, traced on AZZ's FY2026 net income: the restatement fill writes a corrected FY value directly into `net_income_resolved` from `core.fact`, bypassing the raw `net_income` canonical concept entirely (AZZ has zero FY/Q4 rows under the raw concept for that period — the original conflict blocked it there and nothing ever unblocked it). `derive_q4` only derives from the raw canonical concept's own FY/Q1-Q3 facts, so a Q4 that could now be computed from the resolved layer's FY never gets derived. The two mechanisms (conflict-fill at the resolved layer, Q4 derivation at the raw layer) don't see each other's output. Flagged here as the next concrete lead, not fixed this pass — it needs a decision on which stage should close the gap (derive_q4 reading the resolved concept, or conflict-fill deriving Q4 itself for a period it just filled), the same "needs its own careful pass" discipline this project applies to any cross-stage change.

**Lesson, worth restating for the next checker built against this data truth layer: always verify a reported gap against the concept the product actually displays, not just the concept that seems most natural to query** — the same `*_resolved`-companion pattern already documented a dozen times in `pipeline/CLAUDE.md` for other modules. A checker is not exempt from the discipline it's meant to enforce on everything else.
