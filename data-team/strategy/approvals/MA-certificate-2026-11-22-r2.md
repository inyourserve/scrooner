# MA display certification (Ritwik (cloud), approver, 2026-11-22): PASS

Coverage `data-team/strategy/certification/MA-coverage-2026-11-22.csv` (sha256 `ec326ca1b4a38b892d5da4b7d0f4e0512f7fe1db7c56d15c96255c2e3e128e97`). Cells by display class: HIDDEN_ROW=77, SHOWN_VALUE=429. Seed `MA-ec326ca1b4a3`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 6 strata of 418 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 197 auto-matched, 0 auto-mismatched, 2 need a read; 2 read, 0 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (19 undrawn) | 19 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 7 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for MA alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 418)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 52/110, balance_sheet|derived 6/11, cash_flow|as_printed 57/121, cash_flow|derived 6/11, income_statement|as_printed 69/147, income_statement|derived 9/18

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** cash_paid_for_interest FY2025 (family): no fact of the checker's cash_paid_for_interest family at 2025-12-31 in 0001141391-26-000013 (custom, dimensioned or note-only line): read the filing -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (FY2025 10-K 0001141391-26-000013 tags the interest-paid series as InterestExpenseDebt (undimensioned): 477M (2023) and 571M (2024) equal the FY2024 10-K's InterestPaidNet for the same years (0001141391-25-000011) and differ from IS interest expense InterestExpenseNonoperating (575M, 646M), so 680M is FY2025 interest paid; IS interest expense FY2025 is 722M)
- **NEEDS_READ** other_income_expense_net FY2015 (identity): the band at 2015-12-31 in 0001141391-16-000085 does not settle it (IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments=4958000000.0000 (dcml -6, 2015-12-31, qtrs 4) - OperatingIncomeLoss=5078000000.0000 (dcml -6, 2015-12-31, qtrs 4) unsplit 'Investment income' InvestmentIncomeNet=25000000.0000 (dcml -6, 2015-12-31, qtrs 4) + 'Interest expense' InterestExpense=61000000.0000 (dcml -6, 2015-12-31, qtrs 4)): read the printed nonoperating lines -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (FY2015 10-K 0001141391-16-000085 R4 income statement line 12 'Other income (expense), net' OtherNonoperatingIncomeExpense = -84M (undimensioned, FY2015); a separate printed line from Investment income (25M) and Interest expense (61M); 25 - 61 - 84 = -120 = printed 'Total other income (expense)')

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
