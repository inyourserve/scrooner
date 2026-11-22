# MO display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/MO-coverage-2026-11-22.csv` (sha256 `4d3975880260bfcf156e48a53a015145b6d18bb1e738555e47b2a17b90681d5d`). Cells by display class: HIDDEN_ROW=11, HIDDEN_YEAR=10, SHOWN_VALUE=459. Seed `MO-4d3975880260`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 5 strata of 450 shown) | 198 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 197 auto-matched, 0 auto-mismatched, 2 need a read; 2 read, 0 pending |
| total_debt census (9 years) | 9 match, 0 wrong, 0 for review |
| Derived cells census (8 undrawn) | 8 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 11 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for MO alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 450)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 48/108, cash_flow|as_printed 59/134, cash_flow|combined 4/9, income_statement|as_printed 81/184, income_statement|derived 7/15

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** other_income_expense_net FY2015 (identity): the band at 2015-12-31 in 0000764180-16-000128 does not settle it (IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest=8078000000.0000 (dcml -6, 2015-12-31, qtrs 4) - OperatingIncomeLoss=8361000000.0000 (dcml -6, 2015-12-31, qtrs 4) unsplit 'Interest and other debt expense, net' InterestIncomeExpenseNet=-817000000.0000 (dcml -6, 2015-12-31, qtrs 4) - interest income inside the band InterestIncomeOther=4000000.0000 (dcml -6, 2015-12-31, qtrs 4)): read the printed nonoperating lines -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (FY2015 10-K 0000764180-16-000128 R4 IS prints 'Other income, net' OtherNonoperatingIncomeExpense FY2015 = 5,000,000 (dcml -6, undimensioned): the shown value is the printed line)
- **NEEDS_READ** sbc FY2016 (family): no fact of the checker's sbc family at 2016-12-31 in 0000764180-19-000023 (custom, dimensioned or note-only line): read the filing -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (AllocatedShareBasedCompensationExpense [AwardType=RestrictedAndDeferredStock] at 2016-12-31 = 44,000,000 in the FY2016, FY2017 and FY2018 10-Ks (0000764180-17-000028, -18-000028, -19-000023); no PerformanceShares fact before 2017-12-31 in any MO 10-K (PSU expense starts 2017: 6M), so 44M is total SBC for 2016. Export locator gap: the part omits the AwardType dimension that 2017+ parts carry)

## Findings

- **NOT_FOUND** sbc FY2016: served 44000000, filing None. no fsn fact AllocatedShareBasedCompensationExpense[] qtrs=4 near 2016-12-31 in 0000764180-19-000023

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
