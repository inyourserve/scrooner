# JNJ display certification (Ritwik (cloud), approver, 2026-11-22): PASS

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/JNJ-coverage-2026-11-22.csv` (sha256 `ffa773adb1c32e97b7d5f6ff608e8a271110ad44fbb91f59c1faa7c5d7887181`). Cells by display class: HIDDEN_ROW=33, SHOWN_VALUE=473. Seed `JNJ-ffa773adb1c3`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 4 strata of 462 shown) | 199 match, 0 wrong, 0 locator only |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (6 undrawn) | 6 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 3 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for JNJ alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 462)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 52/121, balance_sheet|derived 5/11, cash_flow|as_printed 57/132, income_statement|as_printed 85/198

## Hidden rows evidenced

- cf_ap_change: no presented, undimensioned, annual ['IncreaseDecreaseInAccountsPayable', 'IncreaseDecreaseInAccountsPayableTrade'] fact at a display-year end in any periodic filing
- operating_expenses: no presented, undimensioned, annual ['CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses'] fact at a display-year end in any periodic filing
- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
