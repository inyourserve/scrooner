# JNJ display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/JNJ-coverage-2026-11-22.csv` (sha256 `ffa773adb1c32e97b7d5f6ff608e8a271110ad44fbb91f59c1faa7c5d7887181`). Cells by display class: HIDDEN_ROW=33, SHOWN_VALUE=473. Seed `JNJ-ffa773adb1c3`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 4 strata of 462 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@1, the filing's own facts) | 190 auto-matched, 0 auto-mismatched, 9 need a read; 0 read, 9 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (6 undrawn) | 6 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 3 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for JNJ alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 462)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 52/121, balance_sheet|derived 5/11, cash_flow|as_printed 57/132, income_statement|as_printed 85/198

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** dividends_paid FY2020 (family): no fact of the checker's dividends_paid family at 2021-01-03 in 0000200406-21-000008 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** dividends_paid FY2021 (family): no fact of the checker's dividends_paid family at 2022-01-02 in 0000200406-22-000022 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** dividends_paid FY2022 (family): no fact of the checker's dividends_paid family at 2023-01-01 in 0000200406-23-000016 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** dividends_paid FY2023 (family): no fact of the checker's dividends_paid family at 2023-12-31 in 0000200406-24-000013 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** revenue FY2015 (family): no fact of the checker's revenue family at 2016-01-03 in 0000200406-16-000071 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** stockholders_equity FY2015 (family): no fact of the checker's stockholders_equity family at 2016-01-03 in 0000200406-16-000071 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** stockholders_equity FY2017 (family): no fact of the checker's stockholders_equity family at 2017-12-31 in 0000200406-18-000005 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** stockholders_equity FY2018 (family): no fact of the checker's stockholders_equity family at 2018-12-30 in 0000200406-19-000009 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** stockholders_equity FY2020 (family): no fact of the checker's stockholders_equity family at 2021-01-03 in 0000200406-21-000008 (custom, dimensioned or note-only line): read the filing -- pending read

## Hidden rows evidenced

- cf_ap_change: no presented, undimensioned, annual ['IncreaseDecreaseInAccountsPayable', 'IncreaseDecreaseInAccountsPayableTrade'] fact at a display-year end in any periodic filing
- operating_expenses: no presented, undimensioned, annual ['CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses'] fact at a display-year end in any periodic filing
- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
