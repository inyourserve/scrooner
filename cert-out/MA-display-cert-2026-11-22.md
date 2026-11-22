# MA display certification (Ritwik (cloud), approver, 2026-11-22): FAIL

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/MA-coverage-2026-11-21.csv` (sha256 `1e3a8bfaca0fd83a709dbe43abf46b708ab64d2388980c5e346b88ee77c4c0d4`). Cells by display class: HIDDEN_ROW=77, SHOWN_VALUE=429. Seed `MA-1e3a8bfaca0f`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 20 failing |
| 32 random shown cells | 32 match, 0 wrong, 0 locator only |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (24 undrawn) | 21 match, 0 wrong, 3 for review |
| Hidden rows and years | 0 failing, 0 for review, 7 evidenced |

**Bound:** 0 error(s) in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for MA alone (per-company screen; the 0.10% target is pooled across certified companies in registry.csv).

## Findings

- **FAIL** badge net_income 2024: shown cell has no badge
- **FAIL** badge net_income 2025: shown cell has no badge
- **FAIL** badge other_income_expense_net 2019: shown cell has no badge
- **FAIL** badge other_income_expense_net 2020: shown cell has no badge
- **FAIL** badge other_income_expense_net 2021: shown cell has no badge
- **FAIL** badge other_income_expense_net 2022: shown cell has no badge
- **FAIL** badge other_income_expense_net 2023: shown cell has no badge
- **FAIL** badge other_income_expense_net 2024: shown cell has no badge
- **FAIL** badge other_income_expense_net 2025: shown cell has no badge
- **FAIL** badge shares_outstanding 2015: shown cell has no badge
- **FAIL** badge shares_outstanding 2016: shown cell has no badge
- **FAIL** badge shares_outstanding 2017: shown cell has no badge
- **FAIL** badge shares_outstanding 2018: shown cell has no badge
- **FAIL** badge shares_outstanding 2019: shown cell has no badge
- **FAIL** badge shares_outstanding 2020: shown cell has no badge
- **FAIL** badge shares_outstanding 2021: shown cell has no badge
- **FAIL** badge shares_outstanding 2022: shown cell has no badge
- **FAIL** badge shares_outstanding 2023: shown cell has no badge
- **FAIL** badge shares_outstanding 2024: shown cell has no badge
- **FAIL** badge shares_outstanding 2025: shown cell has no badge
- **NOT_FOUND** cash_paid_for_interest FY2025: served 680000000, filing None. derived cell with no tag, parts or known identity: approver checks by hand
- **NOT_FOUND** dividends_per_share FY2020: served 1.64, filing None. derived cell with no tag, parts or known identity: approver checks by hand
- **NOT_FOUND** dividends_per_share FY2021: served 1.81, filing None. derived cell with no tag, parts or known identity: approver checks by hand

## Hidden rows evidenced

- cf_inventory_change: no presented, undimensioned, annual ['IncreaseDecreaseInInventories'] fact at a display-year end in any periodic filing
- comprehensive_income: no presented, undimensioned, annual ['ComprehensiveIncomeNetOfTax'] fact at a display-year end in any periodic filing
- cost_of_revenue: no presented, undimensioned, annual ['CostOfGoodsAndServicesSold', 'CostOfRevenue'] fact at a display-year end in any periodic filing
- gross_profit: no presented, undimensioned, annual ['GrossProfit'] fact at a display-year end in any periodic filing
- interest_income: no presented, undimensioned, annual ['InterestAndOtherIncome', 'InterestIncomeNonoperating', 'InterestIncomeOperating', 'InterestIncomeOther', 'InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend'] fact at a display-year end in any periodic filing
- inventory: no presented, undimensioned, annual ['InventoryNet'] fact at a display-year end in any periodic filing
- research_and_development: no presented, undimensioned, annual ['ResearchAndDevelopmentExpense'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
