# CMCSA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001628280-26-004994 (CIK 0001166691, filed 2026-02-03): COVER R1.htm, IS R3.htm, CI R4.htm, CF R6.htm, BS R7.htm, BSP R8.htm
- 10-K 0001193125-16-452423 (CIK 0001166691, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R8.htm
- 10-K 0001166691-24-000011 (CIK 0001166691, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R6.htm, BS R7.htm, BSP R8.htm
- 10-K 0001166691-21-000008 (CIK 0001166691, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- companyfacts CIK0001166691.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenue | 123707000000 | 123707000000 | 123731000000 | 123731000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (881 tags across all 94 R pages, face and notes) of 0001628280-26-004994; no face row matched |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (881 tags across all 94 R pages, face and notes) of 0001628280-26-004994; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R3.htm | Total costs and expenses | 103035000000 | 103035000000 | 100434000000 | 100434000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (881 tags across all 94 R pages, face and notes) of 0001628280-26-004994; no face row matched |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (881 tags across all 94 R pages, face and notes) of 0001628280-26-004994; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 20672000000 | 20672000000 | 23297000000 | 23297000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest expense | -4409000000 | 4409000000 | -4134000000 | 4134000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 25766000000 | 25766000000 | 18673000000 | 18673000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income tax expense | -6106000000 | 6106000000 | -2796000000 | 2796000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R3.htm | Net income attributable to Comcast Corporation | 19998000000 | 19998000000 | 16192000000 | 16192000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic earnings per common share attributable to Comcast Corporation shareholders (in dollars per share) | 5.41 | 5.41 | 4.17 | 4.17 | Y | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted earnings per common share attributable to Comcast Corporation shareholders (in dollars per share) | 5.39 | 5.39 | 4.14 | 4.14 | Y | FILING-CHECKED | accn 0001628280-26-004994 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R82.htm | Equity - Weighted Average Common Shares Outstanding (Details) |  | 3699000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R82.htm 'Equity - Weighted Average Common Shares Outstanding (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R82.htm | Equity - Weighted Average Common Shares Outstanding (Details) |  | 3709000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R82.htm 'Equity - Weighted Average Common Shares Outstanding (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R7.htm | Cash and cash equivalents | 9481000000 | 9481000000 | 7322000000 | 7322000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R7.htm | Receivables, net | 13869000000 | 13869000000 | 13661000000 | 13661000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| inventory | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (881 tags across all 94 R pages, face and notes) of 0001628280-26-004994; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R7.htm | Total current assets | 29567000000 | 29567000000 | 26801000000 | 26801000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R7.htm | Property and equipment, net | 65680000000 | 65680000000 | 62548000000 | 62548000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R7.htm | Goodwill | 61502000000 | 61502000000 | 58209000000 | 58209000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R7.htm | Total assets | 272631000000 | 272631000000 | 266211000000 | 266211000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R7.htm | Accounts payable and accrued expenses related to trade creditors | 11058000000 | 11058000000 | 11321000000 | 11321000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R7.htm | Total current liabilities | 33524000000 | 33524000000 | 39581000000 | 39581000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R72.htm | Investments and Variable Interest Entities - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R72.htm 'Investments and Variable Interest Entities - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R7.htm | Total Comcast Corporation shareholders’ equity | 96903000000 | 96903000000 | 85560000000 | 85560000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R7.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash provided by operating activities | 33643000000 | 33643000000 | 27673000000 | 27673000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash provided by (used in) investing activities | -16157000000 | -16157000000 | -15670000000 | -15670000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash provided by (used in) financing activities | -14346000000 | -14346000000 | -10883000000 | -10883000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R6.htm | Capital expenditures | -11750000000 | 11750000000 | -12181000000 | 12181000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 16210000000 | 16210000000 | 14802000000 | 14802000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Share-based compensation | 1288000000 | 1288000000 | 1288000000 | 1288000000 | Y | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R6.htm | Dividends paid | -4894000000 | 4894000000 | -4814000000 | 4814000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Repurchases of common stock under repurchase program and employee plans | -7155000000 | 7155000000 | -9103000000 | 9103000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001628280-26-004994 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R88.htm | Supplemental Financial Information - Cash Payments for Interest and Income Taxes (Details) |  | 3871000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R88.htm 'Supplemental Financial Information - Cash Payments for Interest and Income Taxes' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R62.htm | Income Taxes - Schedule of Income Taxes Paid (Details) |  | 755000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R62.htm 'Income Taxes - Schedule of Income Taxes Paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R7.htm | Current portion of debt + Noncurrent portion of debt | 98937000000 | 98937000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R7.htm | Common stock, shares outstanding (in shares) | 3604212627 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Revenue' on us-gaap:Revenues = 74510000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Total costs and expenses' on us-gaap:CostsAndExpenses = 58512000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 15998000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -2702000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 13372000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -4959000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Net income attributable to Parent' on us-gaap:NetIncomeLoss = 8163000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Basic earnings per common share attributable to Comcast Corporation shareholders' on us-gaap:EarningsPerShareBasic = 3.28 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-452423 R4.htm prints 'Diluted earnings per common share attributable to Comcast Corporation shareholde' on us-gaap:EarningsPerShareDiluted = 3.24 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-452423 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-452423 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2295000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Receivables, net' on us-gaap:AccountsReceivableNetCurrent = 6896000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 12303000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 33665000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 32945000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Total assets' on us-gaap:Assets = 166574000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Accounts payable and accrued expenses related to trade creditors' on us-gaap:AccountsPayableCurrent = 6215000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 18178000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-452423 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001193125-16-452423 R2.htm prints 'Total Comcast Corporation shareholders' equity' on us-gaap:StockholdersEquity = 52269000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 18778000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -11964000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Net cash provided by (used in) financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -8429000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Capital expenditures' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -8499000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 8680000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 567000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -2437000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-452423 R8.htm prints 'Repurchases and retirements of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -6750000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-452423 R8.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-452423 R8.htm read; no row matched (auto)
- revenue: era 10-K 0001166691-24-000011 R3.htm prints 'Revenue' on us-gaap:Revenues = 121572000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001166691-24-000011 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = -4087000000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001166691-21-000008 R5.htm prints 'Depreciation, amortization and other operating gains' on cmcsa:DepreciationAndAmortizationAndGainLossOnDispositionOfAssets = 13100000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: mapped us-gaap:CostsAndExpenses (R3.htm): 2026-11-12 R3.htm: corrected: CMCSA prints no cost of revenue; 'Total costs and expenses' = 123,707 - 20,672 OI = 103,035 is the opex total (EOG/UPS precedent)
- sga_expense: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R82.htm): 2026-11-12 R82.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R82.htm): 2026-11-12 R82.htm: agree: carrying sentence read: the note value is the full data point
- inventory: not_presented  (R7.htm): 2026-11-12 R7.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R7.htm): 2026-11-12 R7.htm: corrected: the R72 Liabilities fact is the consolidated VIEs' liabilities, not CMCSA's total; the BS prints no total-liabilities line
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R88.htm): 2026-11-12 R88.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R62.htm): 2026-11-12 R62.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R7.htm): 2026-11-12 R7.htm: agree: R7 lines on LongTermDebtAndCapitalLeaseObligations; no finance-lease facts in the filing
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R7.htm): 2026-11-12 R7.htm: agree: Class A + Class B at the BS date (R7)
- operating_income: mapped us-gaap:OperatingIncomeLoss (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: IS R3.htm 'Operating income' is the operating_income line, printed 20672000000 = filing XBRL 20672000000; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: BS R7.htm 'Cash and cash equivalents' is the cash_and_equivalents line, printed 9481000000 = filing XBRL 9481000000; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: BS R7.htm 'Receivables, net' is the accounts_receivable line, printed 13869000000 = filing XBRL 13869000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R7.htm): 2026-11-12 R7.htm: 20% mapped sample: BS R7.htm 'Property and equipment, net' is the ppe_net line, printed 65680000000 = filing XBRL 65680000000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R6.htm): 2026-11-12 R6.htm: 20% mapped sample: CF R6.htm 'Share-based compensation' is the sbc line, printed 1288000000 = filing XBRL 1288000000; agrees
