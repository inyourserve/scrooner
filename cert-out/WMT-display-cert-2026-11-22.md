# WMT display certification (Ritwik (cloud), approver, 2026-11-22): FAIL

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/WMT-coverage-2026-11-21.csv` (sha256 `f3e8af7878d1b43175165c223f6e14bf9d6d5689eee9841c9da7e6c219afe35e`). Cells by display class: HIDDEN_ROW=26, HIDDEN_YEAR=11, SHOWN_VALUE=515. Seed `WMT-f3e8af7878d1`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 17 failing |
| 32 random shown cells | 32 match, 0 wrong, 0 locator only |
| total_debt census (12 years) | 12 match, 0 wrong, 0 for review |
| Derived cells census (21 undrawn) | 21 match, 0 wrong, 0 for review |
| Hidden rows and years | 2 failing, 0 for review, 12 evidenced |

**Bound:** 0 error(s) in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for WMT alone (per-company screen; the 0.10% target is pooled across certified companies in registry.csv).

## Findings

- **FAIL** badge interest_expense 2015: shown cell has no badge
- **FAIL** badge interest_expense 2016: shown cell has no badge
- **FAIL** badge interest_expense 2017: shown cell has no badge
- **FAIL** badge interest_expense 2018: shown cell has no badge
- **FAIL** badge interest_expense 2019: shown cell has no badge
- **FAIL** badge interest_expense 2020: shown cell has no badge
- **FAIL** badge interest_expense 2021: shown cell has no badge
- **FAIL** badge interest_expense 2022: shown cell has no badge
- **FAIL** badge interest_expense 2023: shown cell has no badge
- **FAIL** badge interest_expense 2024: shown cell has no badge
- **FAIL** badge interest_expense 2025: shown cell has no badge
- **FAIL** badge interest_expense 2026: shown cell has no badge
- **FAIL** badge other_income_expense_net 2019: shown cell has no badge
- **FAIL** badge other_income_expense_net 2020: shown cell has no badge
- **FAIL** badge other_income_expense_net 2022: shown cell has no badge
- **FAIL** badge other_income_expense_net 2023: shown cell has no badge
- **FAIL** badge other_income_expense_net 2024: shown cell has no badge
- **FAIL** hidden_year other_income_expense_net 2015: periodic filing 0000104169-15-000011 presents 2015-01-31 (own or comparative column): not a pre-filing year, and other_income_expense_net is neither on the hide allowlist nor hidden as reported only combined
- **FAIL** hidden_year shares_outstanding 2024: 0000104169-24-000105 presents 2024-01-31 and prints the line (CommonStockSharesOutstanding); a printed value or dash must be shown

## Hidden rows evidenced

- amortization_of_intangibles: no presented, undimensioned, annual ['AmortizationOfIntangibleAssets'] fact at a display-year end in any periodic filing
- research_and_development: no presented, undimensioned, annual ['ResearchAndDevelopmentExpense'] fact at a display-year end in any periodic filing
- shares_outstanding: no presented, undimensioned, annual ['CommonStockSharesOutstanding'] fact at a display-year end in any periodic filing

## Hidden years evidenced (allowlist)

- shares_outstanding FY2015: allowlisted: 6 periodic filing(s) present 2015-01-31, none prints a shares_outstanding line
- shares_outstanding FY2016: allowlisted: 6 periodic filing(s) present 2016-01-31, none prints a shares_outstanding line
- shares_outstanding FY2017: allowlisted: 6 periodic filing(s) present 2017-01-31, none prints a shares_outstanding line
- shares_outstanding FY2018: allowlisted: 6 periodic filing(s) present 2018-01-31, none prints a shares_outstanding line
- shares_outstanding FY2019: allowlisted: 6 periodic filing(s) present 2019-01-31, none prints a shares_outstanding line
- shares_outstanding FY2020: allowlisted: 6 periodic filing(s) present 2020-01-31, none prints a shares_outstanding line
- shares_outstanding FY2021: allowlisted: 6 periodic filing(s) present 2021-01-31, none prints a shares_outstanding line
- shares_outstanding FY2022: allowlisted: 6 periodic filing(s) present 2022-01-31, none prints a shares_outstanding line
- shares_outstanding FY2023: allowlisted: 6 periodic filing(s) present 2023-01-31, none prints a shares_outstanding line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
