# ICE document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001571949-26-000004 (CIK 0001571949, filed 2026-02-05): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001571949-16-000020 (CIK 0001571949, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm, CI R7.htm
- 10-K 0001571949-24-000007 (CIK 0001571949, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001571949-21-000003 (CIK 0001571949, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- companyfacts CIK0001571949.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 12640000000 | 12640000000 | 11761000000 | 11761000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (1120 tags across all 122 R pages, face and notes) of 0001571949-26-000004; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1120 tags across all 122 R pages, face and notes) of 0001571949-26-000004; no face row matched |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 5002000000 | 5002000000 | 4970000000 | 4970000000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 293000000 | 293000000 | 307000000 | 307000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1120 tags across all 122 R pages, face and notes) of 0001571949-26-000004; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 4929000000 | 4929000000 | 4309000000 | 4309000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -803000000 | 803000000 | -910000000 | 910000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income tax expense | 4346000000 | 4346000000 | 3628000000 | 3628000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 976000000 | 976000000 | 826000000 | 826000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Intercontinental Exchange, Inc. | 3315000000 | 3315000000 | 2754000000 | 2754000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 5.79 | 5.79 | 4.8 | 4.8 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 5.77 | 5.77 | 4.78 | 4.78 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 572000000 | 572000000 | 573000000 | 573000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 575000000 | 575000000 | 576000000 | 576000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 837000000 | 837000000 | 844000000 | 844000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Customer accounts receivable, net of allowance for doubtful accounts of $21 at both December 31, 2025 and 2024 | 1552000000 | 1552000000 | 1490000000 | 1490000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1120 tags across all 122 R pages, face and notes) of 0001571949-26-000004; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 85778000000 | 85778000000 | 89095000000 | 89095000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| ppe_net | mapped | ice:PropertyPlantAndEquipmentAndOperatingLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 2691000000 |  | 2153000000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 30646000000 | 30646000000 | 30595000000 | 30595000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 136887000000 | 136887000000 | 139428000000 | 139428000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued liabilities | 1078000000 | 1078000000 | 1051000000 | 1051000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 84116000000 | 84116000000 | 89553000000 | 89553000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 107896000000 | 107896000000 | 111708000000 | 111708000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Intercontinental Exchange, Inc. stockholders’ equity | 28915000000 | 28915000000 | 27647000000 | 27647000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 4662000000 | 4662000000 | 4609000000 | 4609000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -4249000000 | -4249000000 | -921000000 | -921000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by/(used in) financing activities | -6334000000 | -6334000000 | 79000000 | 79000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures | -373000000 | 373000000 | -406000000 | 406000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization | 1560000000 | 1560000000 | 1537000000 | 1537000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 238000000 | 238000000 | 231000000 | 231000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R8.htm | Dividends paid to stockholders | -1105000000 | 1105000000 | -1039000000 | 1039000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -1294000000 | 1294000000 | 0 | 0 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 764000000 | 764000000 | 870000000 | 870000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Cash paid for income taxes | 1068000000 | 1068000000 | 957000000 | 957000000 | Y | FILING-CHECKED | accn 0001571949-26-000004 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R3.htm | Short-term debt + Long-term debt | 19644000000 | 19644000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding (in shares) | 567000000 | 567000000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Total revenues' on us-gaap:Revenues = 4682000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Total operating expenses' on us-gaap:OperatingExpenses = 1588000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 116000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 1750000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -97000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Income before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 1653000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 358000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Net income attributable to IntercontinentalExchange Group, Inc.' on us-gaap:NetIncomeLoss = 1274000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Basic' on us-gaap:EarningsPerShareBasic = 11.45 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Diluted' on us-gaap:EarningsPerShareDiluted = 11.39 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 111000000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001571949-16-000020 R4.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 112000000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 627000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Customer accounts receivable, net of allowance for doubtful accounts of $1 at De' on us-gaap:AccountsReceivableNetCurrent = 700000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 53313000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 1037000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 12079000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Total assets' on us-gaap:Assets = 77987000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Accounts payable and accrued liabilities' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 398000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 54743000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 63112000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001571949-16-000020 R2.htm prints 'Total IntercontinentalExchange Group, Inc. shareholders’ equity' on us-gaap:StockholdersEquity = 14808000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1311000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -3298000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1976000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -190000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 374000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 111000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Dividends to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -331000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -660000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 123000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001571949-16-000020 R6.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 542000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001571949-24-000007 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -808000000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001571949-21-000003 R4.htm prints 'Income before income tax expense' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 2766000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- ppe_net: API missing (ice:PropertyPlantAndEquipmentAndOperatingLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization)

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent (R3.htm): 2026-11-12 R3.htm: agree: R3 short-term + long-term debt
- revenue: mapped us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Total revenues' is the revenue line, printed 12640000000 = filing XBRL 12640000000; agrees
- operating_expenses: mapped us-gaap:OperatingExpenses (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Total operating expenses' is the operating_expenses line, printed 5002000000 = filing XBRL 5002000000; agrees
- basic_eps: mapped us-gaap:EarningsPerShareBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in dollars per share)' is the basic_eps line, printed 5.79 = filing XBRL 5.79; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in shares)' is the weighted_basic_shares line, printed 572000000 = filing XBRL 572000000; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Customer accounts receivable, net of allowance for' is the accounts_receivable line, printed 1552000000 = filing XBRL 1552000000; agrees
- ppe_net: combined ice:PropertyPlantAndEquipmentAndOperatingLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: ice:PropertyPlantAndEquipmentAndOperatingLeaseRightOfUseAsset... includes operating-lease ROU assets: combined
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: BSP R4.htm 'Common stock, outstanding (in shares)' is the shares_outstanding line, printed 567000000 = filing XBRL 567000000; agrees
