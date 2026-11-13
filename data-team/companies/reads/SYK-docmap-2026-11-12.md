# SYK document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000310764-26-000010 (CIK 0000310764, filed 2026-02-11): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R8.htm
- 10-K 0000310764-16-000226 (CIK 0000310764, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0000310764-18-000031 (CIK 0000310764, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0000310764-25-000023 (CIK 0000310764, era filing): COVER R1.htm, IS R3.htm, CI R5.htm, BS R6.htm, BSP R7.htm, CF R9.htm
- companyfacts CIK0000310764.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Net sales | 25116000000 | 25116000000 | 22595000000 | 22595000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of sales | 9051000000 | 9051000000 | 8155000000 | 8155000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R3.htm | Gross profit | 16065000000 | 16065000000 | 14440000000 | 14440000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R3.htm | Total operating expenses | 11176000000 | 11176000000 | 10751000000 | 10751000000 | Y | FILING-CHECKED | printed total opex line excludes cost of revenue (= GP - OI) / accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 8651000000 | 8651000000 | 7685000000 | 7685000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R3.htm | Research, development and engineering expenses | 1623000000 | 1623000000 | 1466000000 | 1466000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 4889000000 | 4889000000 | 3689000000 | 3689000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -607000000 | 607000000 | -409000000 | 409000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before income taxes | 4514000000 | 4514000000 | 3492000000 | 3492000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income taxes | 1268000000 | 1268000000 | 499000000 | 499000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net earnings | 3246000000 | 3246000000 | 2993000000 | 2993000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic net earnings per share of common stock (in dollars per share) | 8.49 | 8.49 | 7.86 | 7.86 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted net earnings per share of common stock (in dollars per share) | 8.4 | 8.4 | 7.76 | 7.76 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R3.htm | Basic (in shares) | 382200000 | 382200000 | 381000000 | 381000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R3.htm | Diluted (in shares) | 386500000 | 386500000 | 385600000 | 385600000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R3.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 4011000000 | 4011000000 | 3652000000 | 3652000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Accounts receivable, less allowance of $216 ($213 in 2024) | 4039000000 | 4039000000 | 3987000000 | 3987000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R5.htm | Total inventories | 5310000000 | 5310000000 | 4774000000 | 4774000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 14755000000 | 14755000000 | 14847000000 | 14847000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant and equipment, net | 3876000000 | 3876000000 | 3448000000 | 3448000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 19291000000 | 19291000000 | 15855000000 | 15855000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 47844000000 | 47844000000 | 42971000000 | 42971000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableTradeCurrent | R5.htm | Accounts payable | 1799000000 | 1799000000 | 1679000000 | 1679000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 7794000000 | 7794000000 | 7616000000 | 7616000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R5.htm | Total liabilities | 25424000000 | 25424000000 | 22337000000 | 22337000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R5.htm | Total shareholders' equity | 22420000000 | 22420000000 | 20634000000 | 20634000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000310764-26-000010 R5.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 5044000000 | 5044000000 | 4242000000 | 4242000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -4866000000 | -4866000000 | -3000000000 | -3000000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 113000000 | 113000000 | -525000000 | -525000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchases of property, plant and equipment | -761000000 | 761000000 | -755000000 | 755000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | component sum | us-gaap:Depreciation | R8.htm | Depreciation | 461000000 | 461000000 | 427000000 | 427000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 243000000 | 243000000 | 229000000 | 229000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Payments of dividends | -1284000000 | 1284000000 | -1219000000 | 1219000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (960 tags across all 92 R pages, face and notes) of 0000310764-26-000010; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest on debt | 582000000 | 582000000 | 396000000 | 396000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes, net of refunds | 1002000000 | 1002000000 | 989000000 | 989000000 | Y | FILING-CHECKED | accn 0000310764-26-000010 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Current maturities of debt + Long-term debt, excluding current maturities | 15859000000 | 15859000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R7.htm | Consolidated Statements Of Shareholders' Equity |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R7.htm 'Consolidated Statements Of Shareholders' Equity' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| interest_income | mapped | us-gaap:InterestIncomeInterestEarningAsset | R50.htm | Interest income |  | 121000000 |  | 139000000 |  | DATA-INFERRED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / no interest income line on R3.htm / check: hand R50.htm corrected: MetaLinks presents InterestIncomeInterestEarningAsset 'Interest income' only on R50 (Fair Value Measurements narrative); companyfacts same accession 121 (2025) / 139 (2024); R50 not opened, printed value open |
| other_income_expense_net | mapped | us-gaap:NonoperatingIncomeExpense | R3.htm | Other income | 232000000 | 232000000 | 212000000 | 212000000 | Y | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / accn 0000310764-26-000010 period FY ending 2025-12-31 / check: hand R3.htm agree: row agrees with the printed face line (value matched companyfacts, same accession) |
| dividends_per_share | component sum | us-gaap:CommonStockDividendsPerShareDeclared | R86.htm | Dividends declared per share of common stock (quarters) | 3.4 |  | 3.24 |  |  | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / no dividends per share line on R3.htm+R7.htm+R6.htm+R8.htm / check: hand R86.htm corrected: R86 quarterly data: 2025 0.88 + 0.84 + 0.84 + 0.84 = 3.40; 2024 0.84 + 0.80 + 0.80 + 0.80 = 3.24 (no annual line) |
| comprehensive_income | mapped | us-gaap:ComprehensiveIncomeNetOfTax | R4.htm | Comprehensive income | 2852000000 | 2852000000 | 3116000000 | 3116000000 | Y | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / accn 0000310764-26-000010 period FY ending 2025-12-31 / check: hand R4.htm agree: row agrees with the printed face line (value matched companyfacts, same accession) |
| amortization_of_intangibles | mapped | us-gaap:AmortizationOfIntangibleAssets | R3.htm | Amortization of intangible assets | 732000000 | 732000000 | 623000000 | 623000000 | Y | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / accn 0000310764-26-000010 period FY ending 2025-12-31 / check: hand R3.htm agree: row agrees with the printed face line (value matched companyfacts, same accession) |
| cf_ar_change | mapped | us-gaap:IncreaseDecreaseInAccountsReceivable | R8.htm | Accounts receivable | 127000000 | -127000000 | -321000000 | 321000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / accn 0000310764-26-000010 period FY ending 2025-12-31 / check: hand R8.htm agree: row agrees with the printed face line (value matched companyfacts, same accession) |
| cf_inventory_change | mapped | us-gaap:IncreaseDecreaseInInventories | R8.htm | Inventories | -297000000 | 297000000 | -206000000 | 206000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / accn 0000310764-26-000010 period FY ending 2025-12-31 / check: hand R8.htm agree: row agrees with the printed face line (value matched companyfacts, same accession) |
| cf_ap_change | mapped | us-gaap:IncreaseDecreaseInAccountsPayableTrade | R8.htm | Accounts payable | 94000000 | 94000000 | 192000000 | 192000000 | Y | FILING-CHECKED | supplement: not emitted by the shared tool, read by pipeline/scripts/reads/docmap.py from the same accession / accn 0000310764-26-000010 period FY ending 2025-12-31 / check: hand R8.htm agree: row agrees with the printed face line (value matched companyfacts, same accession) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 9946000000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 3344000000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Gross profit' on us-gaap:GrossProfit = 6602000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 4741000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 3610000000 (FILING-CHECKED)
- research_and_development: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Research, development and engineering expenses' on us-gaap:ResearchAndDevelopmentExpense = 625000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1861000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000310764-16-000226 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Earnings before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1735000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Income taxes' on us-gaap:IncomeTaxExpenseBenefit = 296000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Net earnings' on us-gaap:NetIncomeLoss = 1439000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Basic net earnings per share of common stock (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.82 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Diluted net earnings per share of common stock (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.78 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Basic (in shares)' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 376600000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0000310764-16-000226 R2.htm prints 'Diluted (in shares)' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 380900000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 3379000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Accounts receivable, less allowance of $61 ($59 in 2014)' on us-gaap:AccountsReceivableNetCurrent = 1662000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Total inventories' on us-gaap:InventoryNet = 1639000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 7944000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Net property, plant and equipment' on us-gaap:PropertyPlantAndEquipmentNet = 1199000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 4136000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Total assets' on us-gaap:Assets = 16247000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableTradeCurrent = 410000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 3503000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000310764-16-000226 R4.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0000310764-16-000226 R4.htm prints 'Total shareholders' equity' on us-gaap:StockholdersEquity = 8511000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 899000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 1956000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -1141000000 (FILING-CHECKED)
- capex: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -270000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000310764-16-000226 R8.htm read; no row matched (auto)
- sbc: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 86000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -521000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Cash paid for interest on debt' on us-gaap:InterestPaid = 101000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000310764-16-000226 R8.htm prints 'Cash paid for income taxes, net of refunds' on us-gaap:IncomeTaxesPaidNet = 497000000 (FILING-CHECKED)
- revenue: era 10-K 0000310764-18-000031 R2.htm prints 'Net sales' on us-gaap:SalesRevenueNet = 12444000000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0000310764-18-000031 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsSold = 4271000000 (FILING-CHECKED)
- interest_expense: era 10-K 0000310764-25-000023 R3.htm read; no row matched (auto)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- depreciation_and_amortization: component sum us-gaap:Depreciation+us-gaap:AdjustmentForAmortization (R8.htm): 2026-11-12 R8.htm: R8 prints 'Depreciation' 461 and 'Amortization of intangible assets' 732 with no total: D&A = 1,193; the machine row carried depreciation only
- share_buybacks: not_presented  (R8.htm): 2026-11-12 R8.htm: R8 prints no repurchase line in FY2025; MetaLinks: PaymentsForRepurchaseOfCommonStock absent
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R5.htm): 2026-11-12 R5.htm: R5 prints current maturities 1,000 + long-term debt 14,859 = 15,859 = XBRL
- income_before_tax: mapped us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest (R3.htm): 2026-11-12 R3.htm: 10% mapped sample: IS R3.htm 'Earnings before income taxes' is the income_before_tax line, printed 4514000000 = filing XBRL 4514000000; agrees
- inventory: mapped us-gaap:InventoryNet (R5.htm): 2026-11-12 R5.htm: 10% mapped sample: BS R5.htm 'Total inventories' is the inventory line, printed 5310000000 = filing XBRL 5310000000; agrees
- total_liabilities: mapped us-gaap:Liabilities (R5.htm): 2026-11-12 R5.htm: 10% mapped sample: BS R5.htm 'Total liabilities' is the total_liabilities line, printed 25424000000 = filing XBRL 25424000000; agrees
- cash_flow_investing: mapped us-gaap:NetCashProvidedByUsedInInvestingActivities (R8.htm): 2026-11-12 R8.htm: 10% mapped sample: CF R8.htm 'Net cash used in investing activities' is the cash_flow_investing line, printed -4866000000 = filing XBRL -4866000000; agrees
