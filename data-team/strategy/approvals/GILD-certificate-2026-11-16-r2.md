# GILD display certification, 2026-11-16 (second request): PASS

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/GILD-request-2026-11-16.md`. This supersedes the GILD verdict of the 2026-11-15 request.
Coverage: `data-team/strategy/certification/GILD-coverage-2026-11-16.csv`, sha256 `e4ed0b0f7eb9e927845211c4a4d13fc805723768d2472112192e4889568905f9` (checked against the request). Cells: HIDDEN_ROW=11, SHOWN_VALUE=495.
Method: CERTIFICATION-METHOD-2026-11-16.md and doc 02 (founder decision 2026-11-16, display rules 2bc5a106, founder approvals 2026-11-17 93c8d6ba), run by `certify_display.py --request ... --live` in https://github.com/inyourserve/scrooner/actions/runs/43935238837 (read-only, fsn.*, no re-downloads).

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession, R page on every shown cell and part; signed parts sum; per-share plausibility census | pass |
| 32 random shown cells (seed `GILD-e4ed0b0f7eb9`) | 32 match, 0 wrong |
| total_debt census | 11 of 11 years match |
| Hide classes, hidden rows and years | evidenced |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for GILD alone. Pooled over the latest PASS of each company in registry.csv (GILD, JNJ): 0 wrong in 64, upper bound 4.57%.

## Hides evidenced

- interest_income: no presented, undimensioned, annual interest-income fact at a display-year end in any periodic filing.

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days), duration and dimensions; presented on the cited R page; summed cells part by part; derived cells by their identity.

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_payable | 2016 | 1206000000 | 0000882095-17-000006 | R2 | AccountsPayableCurrent |
| 2 | accounts_receivable | 2015 | 5854000000 | 0000882095-16-000039 | R2 | AccountsReceivableNetCurrent |
| 3 | capex | 2017 | 590000000 | 0000882095-18-000008 | R8 | PaymentsToAcquireProductiveAssets |
| 4 | cash_and_equivalents | 2023 | 6085000000 | 0000882095-24-000007 | R3 | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents |
| 5 | cash_flow_financing | 2022 | -6469000000 | 0000882095-23-000007 | R10 | NetCashProvidedByUsedInFinancingActivities |
| 6 | cash_paid_for_income_taxes | 2018 | 3198000000 | 0000882095-19-000006 | R9 | IncomeTaxesPaid |
| 7 | cf_ar_change | 2025 | 367000000 | 0000882095-26-000006 | R9 | IncreaseDecreaseInAccountsReceivable |
| 8 | cfo | 2015 | 21250000000 | 0000882095-18-000008 | R8 | NetCashProvidedByUsedInOperatingActivities |
| 9 | comprehensive_income | 2018 | 5663000000 | 0000882095-19-000006 | R5 | ComprehensiveIncomeNetOfTax |
| 10 | comprehensive_income | 2019 | 5391000000 | 0000882095-20-000006 | R5 | ComprehensiveIncomeNetOfTax |
| 11 | diluted_eps | 2017 | 3.5100 | 0000882095-18-000008 | R4 | EarningsPerShareDiluted |
| 12 | dividends_paid | 2022 | 3709000000 | 0000882095-23-000007 | R10 | PaymentsOfDividends |
| 13 | dividends_per_share | 2015 | 1.2900 | 0000882095-16-000039 | R4 | CommonStockDividendsPerShareDeclared |
| 14 | dividends_per_share | 2022 | 2.9200 | 0000882095-23-000007 | R9 | CommonStockDividendsPerShareDeclared |
| 15 | gross_profit | 2016 | 26129000000 | 0000882095-19-000006 | R4 | derived |
| 16 | gross_profit | 2025 | 23209000000 | 0000882095-26-000006 | R5 | derived |
| 17 | income_before_tax | 2016 | 17097000000 | 0000882095-17-000006 | R4 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments |
| 18 | net_income | 2018 | 5455000000.0000 | 0000882095-19-000006 | R4 | NetIncomeLoss |
| 19 | ppe_net | 2022 | 5475000000 | 0000882095-23-000007 | R3 | PropertyPlantAndEquipmentNet |
| 20 | research_and_development | 2017 | 3734000000 | 0000882095-18-000008 | R4 | ResearchAndDevelopmentExpense |
| 21 | sbc | 2020 | 643000000 | 0000882095-21-000008 | R8 | ShareBasedCompensation |
| 22 | share_buybacks | 2025 | 1922000000 | 0000882095-26-000006 | R9 | PaymentsForRepurchaseOfCommonStock |
| 23 | shares_outstanding | 2019 | 1266000000 | 0000882095-20-000006 | R3 | CommonStockSharesOutstanding |
| 24 | stockholders_equity | 2015 | 18534000000 | 0000882095-16-000039 | R2 | StockholdersEquity |
| 25 | stockholders_equity | 2019 | 22525000000 | 0000882095-20-000006 | R2 | StockholdersEquity |
| 26 | stockholders_equity | 2020 | 18202000000 | 0000882095-21-000008 | R2 | StockholdersEquity |
| 27 | total_assets | 2016 | 56977000000 | 0000882095-17-000006 | R2 | Assets |
| 28 | total_assets | 2022 | 63171000000 | 0000882095-23-000007 | R3 | Assets |
| 29 | total_liabilities | 2021 | 46888000000 | 0000882095-22-000007 | R3 | derived |
| 30 | weighted_basic_shares | 2015 | 1464000000 | 0000882095-16-000039 | R4 | WeightedAverageNumberOfSharesOutstandingBasic |
| 31 | weighted_basic_shares | 2016 | 1339000000 | 0000882095-17-000006 | R4 | WeightedAverageNumberOfSharesOutstandingBasic |
| 32 | weighted_basic_shares | 2024 | 1247000000 | 0000882095-25-000006 | R5 | WeightedAverageNumberOfSharesOutstandingBasic |

## Limits

- Evidence for the coverage file above, not approval for a production write (founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
