# MA display certification, 2026-11-22 (request 2026-11-22, 199-cell draw): PASS

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `requests/MA-request-2026-11-22.md` (resolver-all110-.90, code 0d6af170). Run: https://github.com/inyourserve/scrooner/actions/runs/45003062114 (read-only, fsn.*). JSON: `certificates/MA-d982df758b46.json`. Supersedes the MA FAIL notes of 2026-11-21 and 2026-11-22 (32-cell draws, on earlier exports).

**Approver note.**
- 199 of 199 stratified drawn cells match the filing. The automated checker (draw_check@1) settled 196; I read the other 3 against the filing, and all 3 MATCH (`reads/MA-d982df758b46.csv`). One of them, cash_paid_for_interest FY2025 (680M), is tagged `InterestExpenseDebt` by the filer, but the same series equals the prior 10-K's `InterestPaidNet` for 2023 and 2024, and income-statement interest expense is 722M. So it is interest paid.
- total_debt matches 11 of 11 years and the derived census 19 of 19; the 7 hidden rows are evidenced.
- Bound: 0 wrong in 199 gives 1.49% for MA. Pooled over the latest PASS of each company (GILD, JNJ, MA): 0 wrong in 430, 95% upper bound 0.69%.

---

# MA display certification (Ritwik (cloud), approver, 2026-11-22): PASS

Coverage `data-team/strategy/certification/MA-coverage-2026-11-22.csv` (sha256 `d982df758b460799fa2e59b9179b0f5f2d81847b78ff4623429cf9c78da0f0d6`). Cells by display class: HIDDEN_ROW=77, SHOWN_VALUE=429. Seed `MA-d982df758b46`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 6 strata of 418 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@1, the filing's own facts) | 196 auto-matched, 0 auto-mismatched, 3 need a read; 3 read, 0 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (19 undrawn) | 19 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 7 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for MA alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 418)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 52/110, balance_sheet|derived 6/11, cash_flow|as_printed 57/121, cash_flow|derived 6/11, income_statement|as_printed 69/147, income_statement|derived 9/18

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** cash_paid_for_interest FY2025 (family): no fact of the checker's cash_paid_for_interest family at 2025-12-31 in 0001141391-26-000013 (custom, dimensioned or note-only line): read the filing -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (FY2025 10-K 0001141391-26-000013 tags the interest-paid series as InterestExpenseDebt (undimensioned, not on an R page): 477M (2023) and 571M (2024) equal the FY2024 10-K's InterestPaidNet for the same years (0001141391-25-000011: 477M, 571M) and differ from IS interest expense (575M, 646M), so 680M is FY2025 interest paid; IS interest expense FY2025 is 722M)
- **NEEDS_READ** dividends_per_share FY2020 (family): no fact of the checker's dividends_per_share family at 2020-12-31 in 0001141391-23-000020 (custom, dimensioned or note-only line): read the filing -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (FY2022 10-K 0001141391-23-000020: CommonStockDividendsPerShareDeclared [EquityComponents=CommonStock] at 2020-12-31 = 1.64 (equity statement common stock column, full precision); 0.40 x 3 + 0.44)
- **NEEDS_READ** dividends_per_share FY2021 (family): no fact of the checker's dividends_per_share family at 2021-12-31 in 0001141391-24-000022 (custom, dimensioned or note-only line): read the filing -- read by Ritwik (cloud) approver session_01GLmSDz8UUfjBrVex2j8ugb: MATCH (FY2023 10-K 0001141391-24-000022: CommonStockDividendsPerShareDeclared [EquityComponents=CommonStock] at 2021-12-31 = 1.81 (equity statement common stock column); 0.44 x 3 + 0.49)

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
