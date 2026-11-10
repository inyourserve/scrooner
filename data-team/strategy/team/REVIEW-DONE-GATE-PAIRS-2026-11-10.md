# Review: per-pair done gate on main (Ritwik (cloud), release approver, 2026-11-10)

Scope: `work/fsn/done-gate-pairs`, already merged into main (14d3b237, 9e80070e, cdb8825c, 50da4594; merges d78f74dc, 6db6f74d). Read at origin/main 84055f75.
- Tests: I re-ran `tests/unit/test_fsn_done_gate_pairs.py` and `test_fsn_pilot.py`: 17 passed, 2 skipped. The 2 skips are DB tests; this session has no `SCROONER_TEST_DATABASE_URL`.
- No DB queries and no SEC requests.
- Process note: the branch reached main before an approver review. No select_write has used it (NOW.md: only MDT is written, by run 42649721096 on 1beb755), so nothing needs undoing.

## Verdict: PASS against the ruling, with 4 conditions before the next select_write

| Condition | Built as | Verdict |
|---|---|---|
| C1 atomic pair | Every in-template listed pair of a company passing criteria 1/2/5 is written whole; gap keys are written as blanks (`gap_blank`) | PASS |
| C1(c) empty pair | `no_expected_keys`; `shares_outstanding` refused and out of the default | PASS |
| C2 (as report, plus Mac Ritwik's 2026-11-10 valued→no-row hold) | `hold_guard` by true duration class; `valued_to_blank.json`, `valued_to_no_row.tsv`; the command refuses when a written pair has a valued→no-row key | PASS |
| C4 proof scope | `written_companies.txt` | PASS |
| C5 | `company_value_owner` untouched | PASS |
| C6/C8 | DPS, debt and TL refused by the gate and out of the default | PASS |
| N1 | `select.REASONS` / `GAP_CAUSE_CLASS`: `filing_not_in_store` = ingestion / data_engineer_l1; cause-mapped class and owner; cause in reason_text; accession in input_refs | PASS. The doc says "data_engineer_l2" in one place; the code says l1, which is correct. |
| N2 | `blank_disagreements` and `proof-blank` built; **no workflow stage** | OPEN (G1) |
| N3, N5 | as ruled | PASS |
| Criterion 5 scoped to the switched data points | | ACCEPTED |
| An out-of-template point is not a company failure | | ACCEPTED |

Also accepted: `no_public_filing_for_period` as `history_horizon` (non-defect) inside an excluded wrong-entity window. It agrees with the approved 0121 windows.

## Conditions before the next select_write
- **G1. N2 must be runnable before the next write.**
  - Add the `proof_blank` workflow stage: it downloads `out/write/` from the write run and runs `proof-blank`, read-only. Loading its output is a production write and needs the founder's words.
  - Run cell_proof on MDT's 779 cells now, run `proof-blank` on them, and give me the summary before the next dispatch.
  - MDT's DPS cells were written before C6. They need a Verifier check against the filings, or a re-write as held blanks (`hybrid_rule_held`). Restoring old values is not an option.
- **G2. Old values that survive must be counted, and the no-fallback rule closes the two open cases.** Under the founder's "No fallback", a listed pair that is not written must not keep old-mapper values silently.
  - (a) An `out_of_template` pair with old valued rows: write `not_in_template` reason rows at the before-image keys. State `not_in_template` is a valid non-defect state in 0100. That replaces the pair, so no old value survives and the absence is visible. This is my answer to the builder's open question: blanks at the before-image keys, not a bare delete.
  - (b) An in-template `no_expected_keys` pair with old valued rows: write `hybrid_gap_unresolved` defect blanks at the before-image keys, with cause `no_calendar_key` (unclassified / triage). The 2026-11-10 C2 rule already says before-image keys are expected keys.
  - (c) A pair held by `C2_valued_to_no_row` keeps its old rows by design, so values are not deleted without a reason. That is a temporary exception to "no fallback". The C7 report must count it per data point, and NOW.md must say so for the founder.
- **G3. Separate the YTD holds in the C7 table.** `no_cell_grain_H1`, `no_cell_grain_9M` and `no_cell_grain_MULTI` hold a pair permanently, because no v1 cell grain or `cell_blank_reason.period_grain` can hold them. If old 6- and 9-month YTD rows are common (cash-flow 10-Q YTD), most CF pairs will never be written. At C7, report them apart from `no_new_cell`. Then the two approvers decide one question together in NOW.md: are old YTD rows read anywhere (screener, API, metrics)? If not, they may be removed with the pair, kept in the before-image as the archive. If yes, they stay held until a YTD grain exists. I am not overruling the Mac ruling; I am asking for the measurement.
- **G4.** Fix the doc's l2/l1 inconsistency when convenient. This is not blocking.

## C7 clearance (unchanged)
No data_points clearance until the C7 cohort dry run (main + PR #4 + PR #6, with this gate and the 2026m10 set) reports:
- the N4 table (the valued→blank share per data point, and any top-100 company losing all of its values for a data point);
- the G2 surviving-old-value counts;
- the G3 YTD split.
