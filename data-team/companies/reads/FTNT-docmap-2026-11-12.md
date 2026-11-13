# FTNT document-first map, 2026-11-12 (read-only, built bottom-up from the 10-K)

Latest 10-K: accession 0001262039-26-000007, period end 2025-12-31. Evidence: R pages of FilingSummary (face statements + notes opened: R1.htm, R3.htm, R4.htm, R5.htm, R6.htm, R7.htm, R8.htm, R54.htm, R60.htm, R61.htm, R62.htm, R63.htm, R65.htm, R66.htm, R68.htm, R75.htm, R76.htm, R89.htm, R91.htm, R92.htm, R93.htm, R96.htm, R99.htm, R100.htm, R101.htm, R102.htm, R103.htm), values compared with data.sec.gov companyfacts (undimensioned, same accession). Values below are scaled to full units (USD, shares, USD/share). match = printed vs API; Y(abs) = same magnitude, sign differs (expense/outflow printed negative, tag positive).  Custom (company-prefix) tags are not in companyfacts: match NA.

Face statements: R3 balance sheet, R4/R6 comprehensive income, R5 income, R8 cash flows. FY0 = FY2025.

| data_point | status | tags | page | label | fy0 printed | fy0 api | fy1 printed | fy1 api | match | note |
|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 6799600000 | 6799600000 | 5955800000 | 5955800000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cost_of_revenue | mapped | CostOfGoodsAndServicesSold | R5.htm | Total cost of revenue | 1328900000 | 1328900000 | 1157600000 | 1157600000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| gross_profit | mapped | GrossProfit | R5.htm | Total gross profit | 5470700000 | 5470700000 | 4798200000 | 4798200000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| operating_expenses | mapped | OperatingExpenses | R5.htm | Total operating expenses | 3386000000 | 3386000000 | 2994800000 | 2994800000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| sga_expense | component sum | SellingAndMarketingExpense;GeneralAndAdministrativeExpense | R5.htm | Sales and marketing + General and administrative | 2580900000 | 2580900000 | 2282600000 | 2282600000 | Y/Y | no SG&A caption; duration sum of printed 'Sales and marketing' + 'General and administrative' (R&D and the IP-matters gain excluded); definition call for Standardization / fy0=2025-12-31 fy1=2024-12-31 |
| research_and_development | mapped | ResearchAndDevelopmentExpense | R5.htm | Research and development | 815500000 | 815500000 | 716800000 | 716800000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| operating_income | mapped | OperatingIncomeLoss | R5.htm | OPERATING INCOME | 2084700000 | 2084700000 | 1803400000 | 1803400000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| interest_expense | mapped | InterestExpense | R5.htm | INTEREST EXPENSE | -20100000 | 20100000 | -20000000 | 20000000 | Y(abs)/Y(abs) | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| interest_income | mapped | InvestmentIncomeNet | R5.htm | INTEREST INCOME | 162300000 | 162300000 | 155200000 | 155200000 | Y/Y | IS 'INTEREST INCOME' 162.3 carries tag InvestmentIncomeNet (not InvestmentIncomeInterest); MAPPER RISK / fy0=2025-12-31 fy1=2024-12-31 |
| other_income_expense_net | mapped | OtherNonoperatingIncomeExpense | R5.htm | OTHER INCOME (EXPENSE)—NET | 55300000 | 55300000 | 119900000 | 119900000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | INCOME BEFORE INCOME TAXES AND GAIN (LOSS) FROM EQUITY METHO | 2282200000 | 2282200000 | 2058500000 | 2058500000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | R5.htm | PROVISION FOR INCOME TAXES | 439100000 | 439100000 | 283900000 | 283900000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| net_income | mapped | NetIncomeLoss | R5.htm | NET INCOME | 1853400000 | 1853400000 | 1745200000 | 1745200000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| basic_eps | mapped | EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 2.45 | 2.45 | 2.28 | 2.28 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| diluted_eps | mapped | EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 2.42 | 2.42 | 2.26 | 2.26 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 758000000 | 758000000 | 764400000 | 764400000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 764600000 | 764600000 | 771900000 | 771900000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_per_share | not_presented |  |  |  |  |  |  |  |  | no dividends declared or paid (DPS tags absent per MetaLinks; agrees with Ritwik dividends_paid not_presented) |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | R6.htm | Comprehensive income | 1854100000 | 1854100000 | 1738000000 | 1738000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2495300000 | 2495300000 | 2875900000 | 2875900000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| accounts_receivable | mapped | AccountsReceivableNetCurrent | R3.htm | Accounts receivable—Net of allowance for credit losses of $7 | 1691200000 | 1691200000 | 1463400000 | 1463400000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| inventory | mapped | InventoryNet | R3.htm | Inventory | 399500000 | 399500000 | 315500000 | 315500000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| current_assets | mapped | AssetsCurrent | R3.htm | Total current assets | 5900200000 | 5900200000 | 5971500000 | 5971500000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| ppe_net | mapped | PropertyPlantAndEquipmentNet | R3.htm | PROPERTY AND EQUIPMENT—NET | 1619000000 | 1619000000 | 1349500000 | 1349500000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| goodwill | mapped | Goodwill | R3.htm | GOODWILL | 257400000 | 257400000 | 235400000 | 235400000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| total_assets | mapped | Assets | R3.htm | TOTAL ASSETS | 10389200000 | 10389200000 | 9763100000 | 9763100000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| accounts_payable | mapped | AccountsPayableCurrent | R3.htm | Accounts payable | 230800000 | 230800000 | 190900000 | 190900000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| current_liabilities | mapped | LiabilitiesCurrent | R3.htm | Total current liabilities | 5034000000 | 5034000000 | 4060700000 | 4060700000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| total_liabilities | mapped | Liabilities | R3.htm | Total liabilities | 9151700000 | 9151700000 | 8269300000 | 8269300000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| total_debt | component sum | LongTermDebtCurrent;LongTermDebtNoncurrent | R3.htm | Current portion of long-term debt + LONG-TERM DEBT | 996300000 | 996300000 | 994300000 | 994300000 | Y/Y | instant sum: 'Current portion of long-term debt' + 'LONG-TERM DEBT' (senior notes); no finance leases / fy0=2025-12-31 fy1=2024-12-31 |
| stockholders_equity | mapped | StockholdersEquity | R3.htm | Total stockholders’ equity | 1237500000 | 1237500000 | 1493800000 | 1493800000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| shares_outstanding | mapped | CommonStockSharesOutstanding | BSP R4.htm | Common Stock, shares outstanding | 743000000 | 743000000 | 767000000 | 767000000 | Y | FILING-CHECKED | BS-date count | FIX 2026-11-12
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 2590600000 | 2590600000 | 2258100000 | 2258100000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -599100000 | -599100000 | -727400000 | -727400000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -2371500000 | -2371500000 | -50100000 | -50100000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| capex | mapped | PaymentsToAcquireProductiveAssets | R8.htm | Purchases of property and equipment | -364800000 | 364800000 | -378900000 | 378900000 | Y(abs)/Y(abs) | 'Purchases of property and equipment' (tag PaymentsToAcquireProductiveAssets) / fy0=2025-12-31 fy1=2024-12-31 |
| depreciation_and_amortization | mapped | DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 152000000 | 152000000 | 122800000 | 122800000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| amortization_of_intangibles | mapped | AmortizationOfIntangibleAssets | R66.htm | Amortization expense | 50700000 | 50700000 | 23100000 | 23100000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| sbc | mapped | ShareBasedCompensation | R8.htm | Stock-based compensation | 279500000 | 279500000 | 257900000 | 257900000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| dividends_paid | not_presented |  |  |  |  |  |  |  |  | no dividends on the CF (agrees with Ritwik) |
| share_buybacks | mapped | PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase and retirement of common stock | -2289800000 | 2289800000 | -600000 | 600000 | Y(abs)/Y(abs) | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cf_ar_change | mapped | IncreaseDecreaseInAccountsReceivable | R8.htm | Accounts receivable—net | -215900000 | 215900000 | -45400000 | 45400000 | Y(abs)/Y(abs) | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cf_inventory_change | mapped | IncreaseDecreaseInInventories | R8.htm | Inventory | -90600000 | 90600000 | 131200000 | -131200000 | Y(abs)/Y(abs) | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cf_ap_change | mapped | IncreaseDecreaseInAccountsPayable | R8.htm | Accounts payable | 27900000 | 27900000 | -10200000 | -10200000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_interest | mapped | InterestPaidNet | R75.htm | Cash paid for interest | 16000000 | 16000000 | 16000000 | 16000000 | Y/Y | check: machine-full-filing 2026-11-12 (see the CSV) / fy0=2025-12-31 fy1=2024-12-31 |
| cash_paid_for_income_taxes | mapped | IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes—net | 451500000 | 451500000 | 578900000 | 578900000 | Y/Y | CF supplemental 'Cash paid for income taxes-net' (also tax note) / fy0=2025-12-31 fy1=2024-12-31 |

## Disagreements with cloud Ritwik (companies-51-100-exceptions-2026-11-11.csv)
No disagreement. interest_expense: FY2025 R5 prints 'INTEREST EXPENSE' (20.1, InterestExpense), so FTNT has an interest expense line from the 2021 notes on; Ritwik's not_presented (1312-2103, 30 filings) agrees with the pre-2021 era. dividends_paid not_presented: agrees.

## Era checks (older 10-K opened: tag on the same printed line?)
Older 10-K opened: 0001262039-21-000008 (period 2020-12-31); face pages ['R2.htm', 'R3.htm', 'R4.htm', 'R5.htm', 'R6.htm', 'R7.htm', 'R8.htm']. Result: 44 mapped rows checked.
- interest_expense: tag us-gaap:InterestExpense ABSENT from the old filing 0001262039-21-000008 (2020-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read)
- total_debt: tag us-gaap:LongTermDebtCurrent ABSENT from the old filing 0001262039-21-000008 (2020-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read) ; tag us-gaap:LongTermDebtNoncurrent ABSENT from the old filing 0001262039-21-000008 (2020-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read)
- cash_paid_for_interest: tag us-gaap:InterestPaidNet ABSENT from the old filing 0001262039-21-000008 (2020-12-31) per MetaLinks and no candidate tag on its statements: line/tag new or differently tagged (needs a manual read)
- (41 rows: same tag and same label on the older 10-K, no change)

## Mismatches / unresolved
- none

## Method and untested scope
- FILING-CHECKED = value read from the 10-K R page (MetaLinks used to locate tags/pages) and compared with companyfacts for the same accession; not_presented/OUT rows are FILING-CHECKED for the statements opened (all face statements plus the note pages that carry the candidate tags per MetaLinks); a note not opened could still hold an unprinted detail.
- Era check: one older 10-K per company (statement pages only, via MetaLinks); same-tag / label comparison on the same statement type. Note-page values of the older filing were not opened.
- Not covered: 10-Q-era tag history, quarterly values, segment-level data points, FSN store comparison (document-first read only).
## Fixes 2026-11-12 (Ritwik cloud re-read of the same 10-K)
- shares_outstanding: mapped dei:EntityCommonStockSharesOutstanding -> mapped us-gaap:CommonStockSharesOutstanding | shares_outstanding = BS-date count, never dei (Dhairya ruling 2026-11-12)
- 38 AUTO rows machine-checked against the same 10-K (R-page row = the filing's XBRL fact, or blank confirmed by the whole-filing MetaLinks check); hand checks are listed separately
