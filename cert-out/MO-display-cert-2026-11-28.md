# MO display certification (Ritwik (cloud), approver, 2026-11-28): PASS

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/MO-coverage-2026-11-22.csv` (sha256 `61b71f5091d2ee2514cf51351204d395f09ae9f5ddcda86f512a434d1306d362`). Cells by display class: HIDDEN_ROW=11, HIDDEN_YEAR=10, SHOWN_VALUE=459. Seed `MO-61b71f5091d2`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 5 strata of 450 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@4, the filing's own facts) | 199 auto-matched, 0 auto-mismatched, 0 need a read; 0 read, 0 pending |
| total_debt census (9 years) | 9 match, 0 wrong, 0 for review |
| Derived cells census (8 undrawn) | 8 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 11 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for MO alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 450)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 48/108, cash_flow|as_printed 59/134, cash_flow|combined 4/9, income_statement|as_printed 81/184, income_statement|derived 7/15

## Hidden rows evidenced

- sga_expense: no presented, undimensioned, annual ['GeneralAndAdministrativeExpense', 'SellingGeneralAndAdministrativeExpense'] fact at a display-year end in any periodic filing

## Hidden years evidenced (allowlist)

- other_income_expense_net FY2016: only combined: 3 periodic filing(s) present 2016-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2017: only combined: 3 periodic filing(s) present 2017-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2018: only combined: 3 periodic filing(s) present 2018-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2019: only combined: 3 periodic filing(s) present 2019-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2020: only combined: 3 periodic filing(s) present 2020-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2021: only combined: 3 periodic filing(s) present 2021-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2022: only combined: 3 periodic filing(s) present 2022-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2023: only combined: 3 periodic filing(s) present 2023-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2024: only combined: 2 periodic filing(s) present 2024-12-31, none prints a other_income_expense_net line
- other_income_expense_net FY2025: only combined: 1 periodic filing(s) present 2025-12-31, none prints a other_income_expense_net line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
