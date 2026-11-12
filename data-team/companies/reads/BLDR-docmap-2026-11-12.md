# BLDR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-054643 (CIK 0001316835, filed 2026-02-17): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- 10-K 0001564590-16-014562 (CIK 0001316835, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R4.htm, BSP R5.htm, CF R6.htm
- 10-K 0001564590-18-004035 (CIK 0001316835, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- 10-K 0001564590-22-007980 (CIK 0001316835, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R5.htm
- companyfacts CIK0001316835.json (one call); submissions CIK0001316835.json (SIC 5211).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R2.htm | Net sales | 15190638000 | 15190638000 | 16400492000 | 16400492000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R2.htm | Cost of sales | 10574861000 | 10574861000 | 11017448000 | 11017448000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R2.htm | Gross margin | 4615777000 | 4615777000 | 5383044000 | 5383044000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| operating_expenses | component sum | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 3829501000 | 3829501000 | 3787795000 | 3787795000 | Y | FILING-CHECKED | check: machine-full-filing / every face line between gross profit and operating income; ties to GP - OI / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R2.htm | Selling, general and administrative expenses | 3829501000 | 3829501000 | 3787795000 | 3787795000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (891 tags across all 84 R pages, face and notes) of 0001193125-26-054643; HAND REVIEW: 2 label candidate(s) incl. custom tags: us-gaap:EffectiveIncomeTaxRateReconciliationTaxCreditsResearch 'Effective Income Tax Rate Reconciliation, Tax Credit, Resear' R78; us-gaap:IncomeTaxReconciliationTaxCreditsResearch 'Effective Income Tax Rate Reconciliation, Tax Credit, Resear' R78 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R2.htm | Income from operations | 786276000 | 786276000 | 1595249000 | 1595249000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| interest_expense | combined | us-gaap:InterestIncomeExpenseNonoperatingNet | R2.htm | Interest expense, net | 273894000 | -273894000 | 207724000 | -207724000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income taxes | 512382000 | 512382000 | 1387525000 | 1387525000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Income tax expense | 77183000 | 77183000 | 309627000 | 309627000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income | 435199000 | 435199000 | 1077898000 | 1077898000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic | 3.91 | 3.91 | 9.13 | 9.13 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted | 3.89 | 3.89 | 9.06 | 9.06 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic | 111421000 | 111421000 | 118038000 | 118038000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted | 111822000 | 111822000 | 118980000 | 118980000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 181753000 | 181753000 | 153624000 | 153624000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, less allowances of $42,511 and $41,233, respectively | 1061011000 | 1061011000 | 1163147000 | 1163147000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventories, net | 1094684000 | 1094684000 | 1212375000 | 1212375000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2927283000 | 2927283000 | 3141239000 | 3141239000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 2204184000 | 2204184000 | 1961731000 | 1961731000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 4137377000 | 4137377000 | 3678504000 | 3678504000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 11237530000 | 11237530000 | 10583086000 | 10583086000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 714710000 | 714710000 | 868054000 | 868054000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1574941000 | 1574941000 | 1777276000 | 1777276000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 6885279000 | 6885279000 | 6286616000 | 6286616000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 4352251000 | 4352251000 | 4296470000 | 4296470000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R5.htm | Net cash provided by operating activities | 1215886000 | 1215886000 | 1872692000 | 1872692000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R5.htm | Net cash used in investing activities | -1467174000 | -1467174000 | -710719000 | -710719000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R5.htm | Net cash provided by (used in) financing activities | 279417000 | 279417000 | -1074505000 | -1074505000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R5.htm | Purchases of property, plant and equipment | -362602000 | 362602000 | -380569000 | 380569000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R5.htm | Depreciation and amortization | 591432000 | 591432000 | 561929000 | 561929000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R5.htm | Stock-based compensation expense | 53512000 | 53512000 | 63111000 | 63111000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (891 tags across all 84 R pages, face and notes) of 0001193125-26-054643; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R5.htm | Repurchase of common stock | -413958000 | 413958000 | -1517131000 | 1517131000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R5.htm | Cash paid for interest | 260515000 | 260515000 | 188453000 | 188453000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001193125-26-054643 R5.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R79.htm | Total Taxes Paid | 67658000 | 67658000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R79.htm 'Income Taxes - Total Income Taxes Paid, Net of Refunds (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt + Long-term debt, net of current maturities, discounts and issuance costs | 4441367000 | 4441367000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding | 110585000 | 110585000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Sales' on us-gaap:SalesRevenueNet = 3564425000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Cost of sales' on us-gaap:CostOfGoodsAndServicesSold = 2662967000 (FILING-CHECKED)
- gross_profit: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Gross margin' on us-gaap:GrossProfit = 901458000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 810841000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Selling, general and administrative expenses' on us-gaap:SellingGeneralAndAdministrativeExpense = 810841000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 90617000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 109199000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Income (loss) from continuing operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -18582000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = 4387000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Net income (loss)' on us-gaap:NetIncomeLoss = -22831000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Net income (loss)' on us-gaap:EarningsPerShareBasic = -0.22 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Net income (loss)' on us-gaap:EarningsPerShareDiluted = -0.22 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 103190000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-014562 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 103190000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 65063000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Accounts receivable, less allowances of $8,049 and $3,153 for 2015 and 2014, res' on us-gaap:AccountsReceivableNetCurrent = 528544000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Inventories, net' on us-gaap:InventoryNet = 513045000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 1194329000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 734329000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Goodwill' on us-gaap:Goodwill = 739625000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Total assets' on us-gaap:Assets = 2882038000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 365347000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 735238000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Total liabilities' on us-gaap:Liabilities = 2732843000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-014562 R4.htm prints 'Total stockholders’ equity' on us-gaap:StockholdersEquity = 149195000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 177034000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1508047000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1378303000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Purchases of property, plant and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -43811000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Depreciation and amortization' on bldr:DepreciationAndAmortizationOfLongLivedAssets = 58280000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Stock compensation expense' on us-gaap:ShareBasedCompensation = 6848000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-014562 R6.htm prints 'Repurchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -986000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-014562 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-014562 R6.htm read; no row matched (auto)
- revenue: era 10-K 0001564590-18-004035 R2.htm prints 'Sales' on us-gaap:SalesRevenueNet = 7034209000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564590-18-004035 R2.htm prints 'Interest expense, net' on us-gaap:InterestExpense = 193174000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001564590-22-007980 R5.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 105570000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
