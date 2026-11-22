# MA display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/MA-coverage-2026-11-22.csv` (sha256 `d982df758b460799fa2e59b9179b0f5f2d81847b78ff4623429cf9c78da0f0d6`). Cells by display class: HIDDEN_ROW=77, SHOWN_VALUE=429. Seed `MA-d982df758b46`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 6 strata of 418 shown) | 197 match, 0 wrong, 0 locator only |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (19 undrawn) | 19 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 7 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for MA alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 418)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 52/110, balance_sheet|derived 6/11, cash_flow|as_printed 57/121, cash_flow|derived 6/11, income_statement|as_printed 69/147, income_statement|derived 9/18

## Findings

- **NOT_FOUND** dividends_per_share FY2020: served 1.64, filing None. no fsn fact CommonStockDividendsPerShareDeclared[StatementEquityComponents=CommonStock] qtrs=4 near 2020-12-31 in 0001141391-23-000020
- **NOT_FOUND** dividends_per_share FY2021: served 1.81, filing None. no fsn fact CommonStockDividendsPerShareDeclared[StatementEquityComponents=CommonStock] qtrs=4 near 2021-12-31 in 0001141391-24-000022

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
