# Same-vintage Q4 hold: top-1000 count, 2026-10-31

Rule period.same_vintage_derivation@1 (RF-04) in dry_run mode, `scripts/q4_vintage_hold_count.py`:
derive_q4 run per company in a rolled-back transaction, nothing written. Per-cell list:
`42-same-vintage-hold/cohort-held-cells.csv.gz`; summary `cohort-count-summary.json`.
Evidence: DATA-INFERRED (FSN/filings not opened in this count; the 10-cell check in the branch
history was filing-checked).

| | |
|---|---|
| Companies evaluated | 986 (969 with at least one hold) |
| Q4 cells derive_q4 produces today | 682,008 |
| Cells the hold catches | 37,654 (5.5%) |
| ...quarters_do_not_sum_to_ytd (filer's own 9M vs Q1+Q2+Q3 differ beyond rounding) | 30,447 |
| ...q4_inputs_mixed_vintage (real recast: FY and 9M from different bases) | 5,760 |
| ...q4_input_sign_conflict | 1,447 |
| On mapped statement concepts | 5,382: mixed vintage 4,537, quarters-vs-YTD 763, sign 82 |
| Statement concepts most held | net income 881, operating income 826, revenue 538, income tax 522, CFO 448, income before tax 367, gross profit 354 |
| Companies most held | FRHC 158, GMED 155, JEF 150, CDE 148, GS 131, FLS 120, SWK 116, DOV 107, ITT 103 |

First-10 candidates (holds on all tags): AAPL 33, MSFT 41, NVDA 30, GOOGL 31, AMZN 38, META 35,
JNJ 50, PG 56, KO 58, HD 37; of these, real recasts (mixed vintage) are 1-12 per company, the rest
are quarters-vs-YTD gaps of a few units at the filer's own rounding and sign conflicts.
