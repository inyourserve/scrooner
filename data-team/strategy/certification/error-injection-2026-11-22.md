# Error-injection recall of the certification checks (2026-11-22)

Harness `inject@1` (`pipeline/src/scrooner_pipeline/certification/inject.py`, run by `pipeline/scripts/error_injection.py`). Export copy: `data-team/strategy/top100-coverage.csv` (sha256 `150bb817d4584f57`, read-only); seed `error-injection-2026-11-22`; 93 companies; read-only SELECTs on fsn.*. Per-cell rows: `error-injection-2026-11-22.csv`.

Method: plant one error per cell (at most one per company row) into a copy of the export, run every existing check on the mutated and the untouched copy, and count a planted cell caught by a check when the check flags it in the mutated copy and did not flag it the same way in the untouched copy. Checks: **self_check** = the top100-flow self-check / `certify_display.py --mechanical` census (gate incl. parts sum and per-share ceiling, registry badges, hide classes, hidden rows and years against fsn, derived and total_debt census); **patterns** = tag-expert detectors P02, P03, P05/P06, P08; **cell_match** = the drawn-cell fsn match (`display_cert.check_cell` / `check_derived`); **draw_check** = the automated draw checker (`draw_check@2`, AUTO_MISMATCH). cell_match and draw_check see a cell only when certify draws it, so they are run on every planted cell as if drawn; **one run** is the expected recall of a single certify: a census catch, else a draw catch times the chance the 199-cell draw takes the cell.

| Class | Planted | self_check | patterns | cell_match | draw_check | Any check | Census only | One certify run |
|---|---|---|---|---|---|---|---|---|
| scale_x1000 | 20 | 3 | 1 | 19 | 19 | **20 (100%)** | 4 (20%) | 55% |
| scale_x1e6 | 20 | 2 | 1 | 20 | 20 | **20 (100%)** | 3 (15%) | 52% |
| sign_flip | 20 | 0 | 2 | 2 | 17 | **19 (95%)** | 2 (10%) | 49% |
| period_shift | 20 | 0 | 0 | 20 | 20 | **20 (100%)** | 0 (0%) | 45% |
| dropped_component | 20 | 7 | 1 | 0 | 2 | **10 (50%)** | 8 (40%) | 45% |
| subline_as_total | 20 | 0 | 0 | 0 | 17 | **17 (85%)** | 0 (0%) | 37% |
| combined_as_narrow | 9 | 0 | 0 | 0 | 9 | **9 (100%)** | 0 (0%) | 46% |
| rounded_duplicate | 20 | 0 | 0 | 20 | 20 | **20 (100%)** | 0 (0%) | 47% |
| restricted_cash_total | 20 | 0 | 0 | 0 | 20 | **20 (100%)** | 0 (0%) | 48% |
| available_to_common_ni | 20 | 0 | 0 | 0 | 20 | **20 (100%)** | 0 (0%) | 50% |
| wrong_hide | 20 | 18 | 17 | 0 | 0 | **19 (95%)** | 19 (95%) | 95% |
| missing_badge | 20 | 20 | 0 | 0 | 0 | **20 (100%)** | 20 (100%) | 100% |
| derived_two_filings | 20 | 20 | 20 | 1 | 20 | **20 (100%)** | 20 (100%) | 100% |
| **overall** | 249 | | | | | **234 (94%)** | 76 (31%) | 60% |

**False positives (untouched control cells, 922: up to 8 shown and 2 hidden per evaluated company).** New flags after the injection (spillover): 1 (self_check 0, patterns 0, cell_match 1, draw_check 0). Flagged in the untouched export itself: 79 of 922 (9%; self_check 62, patterns 22, cell_match 0, draw_check 3): an upper bound on the false-positive rate, since a flag on an untouched cell may also be a real error in the export.

## Weakest classes

- **dropped_component**: 10/20 caught by any check; 45% in one certify run.
- **subline_as_total**: 17/20 caught by any check; 37% in one certify run.
- **sign_flip**: 19/20 caught by any check; 49% in one certify run.
- **wrong_hide**: 19/20 caught by any check; 95% in one certify run.
- **period_shift**: 20/20 caught by any check; 45% in one certify run.

## Notes

- Export: main b03168e4d hourly export (2026-11-22T16:54Z). It has no `badge`/`sector` column yet (the exporter writes one since resolver .92), so the harness gives each shown cell the badge its own evidence names (`top100_coverage.proof_step` -> `registry.badge_for`). On the committed export as-is, `check_badges` is inert: missing_badge would be 0% caught and derived_two_filings would rest on pattern P08 alone.
- Misses (15): **dropped_component** 10 (ACN, AMAT, AMD, BMY, DHR, GILD, MRK x3, PLTR; opex/SG&A/other-income/shares sums): a sum of printed parts that still adds up passes the gate, the fsn part match and the draw checker's parts method; only a total the filing prints (gate sum vs a printed total, draw-check identity) can catch it. **subline_as_total** 3 (GE cost_of_revenue ProductOrService=Service, TJX and VLO opex CorporateNonSegment): no first-tier family fact for the draw checker to compare against. **sign_flip** 1 (GOOG weighted_basic_shares: share counts are compared as magnitudes). **wrong_hide** 1 (BLK shares_outstanding FY2016 hidden as verified_absent: an allowlisted data point and fsn.line holds no shares-outstanding line for the presenting filings, so the printed-line test passes).
- Census vs draw: only 76 of 249 (31%) are caught by checks that see every cell (self-check, patterns). Value errors (scale, sign, period, rounding, fact swaps) are caught almost only by cell_match/draw_check, which see a cell only when the 199-cell draw takes it (about 45% of a company's shown cells), so one certify run catches about 60% of planted errors overall. A census run of draw_check over every shown cell would lift those classes to their any-check recall.
- combined_as_narrow: 9 planted, not 20: in 400 AR/AP candidate cells only 9 filings tag a wider receivable/payable line beside the narrow one (cap of 400 filing reads per class).
- The one spillover flag (GE gross_profit FY2025, cell_match) is the derived-identity check catching the planted GE cost_of_revenue sub-line through its neighbour: a true catch attributed to an untouched cell, not a false positive.
- Untouched control flags (79 of 922): 62 self_check (mostly hide-class misfits, blank-badge cells and missing locators already in the export), 22 pattern hits, 3 draw-check mismatches; these were not read, so they bound the false-positive rate from above.

## CI baseline

`pipeline/tests/test_error_injection.py` replays a fixed small injection set (`pipeline/tests/fixtures/error_injection/`, offline bundle, no database) and fails when any class's recall drops below `baseline.json`.
Fixture: 25 planted cells (2 per class, combined_as_narrow 1) in T, RTX, AXP and JPM, 32 control cells, recorded with `--tickers T,RTX,AXP,JPM --per-class 2 --controls-shown 6 --controls-hidden 2 --record-fixture`; baseline recall 100% for every class except dropped_component and subline_as_total (50%). It also fails on any new flag on an untouched control cell. Mutation check: with `draw_check.check_draw` returning no checks the gate fails on 5 classes (available_to_common_ni, combined_as_narrow, restricted_cash_total, sign_flip, subline_as_total).
