# JNJ display certification, 2026-11-16 (second request): PASS

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/JNJ-request-2026-11-16.md`. This supersedes the JNJ verdict of the 2026-11-15 request.
Coverage: `data-team/strategy/certification/JNJ-coverage-2026-11-16.csv`, sha256 `674389ae0acd749aea09ffaa48e37fe3ab1ca07f7044f9cf7385f42a497229bb` (checked against the request). Cells: HIDDEN_ROW=44, SHOWN_VALUE=462.
Method: CERTIFICATION-METHOD-2026-11-16.md and doc 02 (founder decision 2026-11-16, display rules 2bc5a106, founder approvals 2026-11-17 93c8d6ba), run by `certify_display.py --request ... --live` in https://github.com/inyourserve/scrooner/actions/runs/43935238837 (read-only, fsn.*, no re-downloads).

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession, R page on every shown cell and part; signed parts sum; per-share plausibility census | pass |
| 32 random shown cells (seed `JNJ-674389ae0acd`) | 32 match, 0 wrong |
| total_debt census | 11 of 11 years match |
| Hide classes, hidden rows and years | evidenced |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for JNJ alone. Pooled over the latest PASS of each company in registry.csv (GILD, JNJ): 0 wrong in 64, upper bound 4.57%.

## Hides evidenced

- cf_ap_change, operating_expenses, operating_income, shares_outstanding: no presented, undimensioned, annual fact of the row's tag family at a display-year end in any periodic filing.

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days), duration and dimensions; presented on the cited R page; summed cells part by part; derived cells by their identity.

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_payable | 2019 | 8544000000 | 0000200406-20-000010 | R2 | AccountsPayableCurrent |
| 2 | accounts_receivable | 2015 | 10734000000 | 0000200406-16-000071 | R2 | AccountsReceivableNetCurrent |
| 3 | accounts_receivable | 2017 | 13490000000 | 0000200406-18-000005 | R2 | AccountsReceivableNetCurrent |
| 4 | amortization_of_intangibles | 2023 | 4500000000 | 0000200406-24-000013 | R64 | AmortizationOfIntangibleAssets |
| 5 | cash_and_equivalents | 2015 | 13732000000 | 0000200406-16-000071 | R2 | CashAndCashEquivalentsAtCarryingValue |
| 6 | cash_and_equivalents | 2019 | 17305000000 | 0000200406-20-000010 | R2 | CashAndCashEquivalentsAtCarryingValue |
| 7 | cash_and_equivalents | 2020 | 13985000000 | 0000200406-21-000008 | R2 | CashAndCashEquivalentsAtCarryingValue |
| 8 | cash_flow_financing | 2015 | -11136000000 | 0000200406-18-000005 | R8 | NetCashProvidedByUsedInFinancingActivities |
| 9 | cash_flow_financing | 2016 | -8551000000 | 0000200406-17-000006 | R8 | NetCashProvidedByUsedInFinancingActivities |
| 10 | cash_flow_investing | 2018 | -3167000000 | 0000200406-19-000009 | R9 | NetCashProvidedByUsedInInvestingActivities |
| 11 | cash_flow_investing | 2025 | -23588000000 | 0000200406-26-000016 | R10 | NetCashProvidedByUsedInInvestingActivities |
| 12 | cash_paid_for_interest | 2023 | 1766000000 | 0000200406-24-000013 | R10 | InterestPaidNet |
| 13 | cfo | 2023 | 22791000000 | 0000200406-24-000013 | R10 | NetCashProvidedByUsedInOperatingActivities |
| 14 | comprehensive_income | 2019 | 14450000000 | 0000200406-20-000010 | R5 | ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest |
| 15 | cost_of_revenue | 2023 | 26553000000 | 0000200406-24-000013 | R5 | CostOfGoodsAndServicesSold |
| 16 | current_assets | 2025 | 55624000000 | 0000200406-26-000016 | R3 | AssetsCurrent |
| 17 | depreciation_and_amortization | 2016 | 3754000000 | 0000200406-17-000006 | R8 | DepreciationDepletionAndAmortization |
| 18 | diluted_eps | 2019 | 5.6300 | 0000200406-20-000010 | R4 | EarningsPerShareDiluted |
| 19 | diluted_eps | 2025 | 11.03 | 0000200406-26-000016 | R5 | EarningsPerShareDiluted |
| 20 | gross_profit | 2016 | 50101000000 | 0000200406-19-000009 | R4 | GrossProfit |
| 21 | gross_profit | 2017 | 51011000000 | 0000200406-20-000010 | R4 | GrossProfit |
| 22 | interest_income | 2016 | 368000000 | 0000200406-17-000006 | R4 | InvestmentIncomeInterest |
| 23 | interest_income | 2019 | 357000000 | 0000200406-20-000010 | R4 | InvestmentIncomeInterest |
| 24 | interest_income | 2025 | 1056000000 | 0000200406-26-000016 | R5 | InvestmentIncomeInterest |
| 25 | other_income_expense_net | 2024 | -4694000000 | 0000200406-25-000038 | R5 | OtherNonoperatingIncomeExpense |
| 26 | ppe_net | 2016 | 15912000000 | 0000200406-17-000006 | R2 | PropertyPlantAndEquipmentNet |
| 27 | revenue | 2018 | 81581000000.0000 | 0000200406-19-000009 | R4 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 28 | revenue | 2019 | 82059000000.0000 | 0000200406-20-000010 | R4 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 29 | revenue | 2020 | 82584000000 | 0000200406-21-000008 | R4 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 30 | revenue | 2024 | 88821000000 | 0000200406-25-000038 | R5 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 31 | stockholders_equity | 2022 | 76804000000 | 0000200406-23-000016 | R3 | StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest |
| 32 | stockholders_equity | 2025 | 81544000000 | 0000200406-26-000016 | R3 | StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest |

## Limits

- Evidence for the coverage file above, not approval for a production write (founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
