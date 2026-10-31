# Verify: split run 7.4 (origin/work/cashflow/split-run7 8dbcb04), 2026-11-03

Seed 20261103. File: split_rebase_dryrun_cohort1000_run7_4.csv.gz. Evidence class: FILING-CHECKED (statement and equity / dividend R pages). Verifier 2 (scrooner-bc).
Sampling note: the package has no per-cell "released" marker. Released basis-pending holds = dividend cells with class new_value and status shown (483); released restated holds = non-dividend cells with class new_value and status shown (2,380).

## Result
**YES.** The named cells and 8 of 8 released cells are right. The 2 impossible-EPS hides are avoidable: both pairs are printed by the filer.
- AMT FY2022 5.86 and FY2023 6.45: right (VERIFY-SPLIT-RUN6 values).
- LOGI Oct-Dec 2021: hidden as quarter_equals_ytd_context_error (the 3-month context carries the 9M 0.95); right to hide.
- Released dividend-basis, 5 of 5 equal the face:
  - SNA Q3 2026 2.44 (declared and cash 2.44);
  - FSS Q3 2026 0.15;
  - UHS 6M 2022 0.40 (dividends declared and paid per share);
  - T Q3 2026 0.2775;
  - ECL 9M 2026 2.19.
- Released restated, 3 of 3 equal the face: AZO FY2026 diluted 152.55; JNJ Q3 2026 basic 0.09; ZWS Q3 2026 basic 0.46.
- Impossible-EPS hides (2 of 36):
  - NTNX 6M FY2024 prints basic 0.07, diluted 0.09 (Class A, two-class presentation);
  - ZWS FY2018 prints net income per share basic 0.51, diluted 0.62 (preferred dividends added back in diluted; continuing ops 1.76/1.69).
  These are the filer's own numbers. Show them as printed (optionally with a note) rather than hide them.

SEC requests: 30. One DB read for CIKs.
