# HCA document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-044769 (CIK 0000860730, filed 2026-02-10): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001193125-16-482165 (CIK 0000860730, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001193125-21-048994 (CIK 0000860730, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R8.htm
- 10-K 0001193125-18-056057 (CIK 0000860730, era filing): COVER R1.htm, IS R2.htm, CI R3.htm, BS R4.htm, BSP R5.htm, CF R7.htm
- companyfacts CIK0000860730.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R2.htm | Revenues | 75600000000 | 75600000000 | 70603000000 | 70603000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (921 tags across all 75 R pages, face and notes) of 0001193125-26-044769; no face row matched |
| gross_profit | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (921 tags across all 75 R pages, face and notes) of 0001193125-26-044769; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R2.htm | Total expenses including equity in earnings of affiliates | 65768000000 | 65768000000 | 62080000000 | 62080000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R40.htm | Accounting Policies - Additional Information (Detail) |  | 548000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R40.htm 'Accounting Policies - Additional Information (Detail)' (MetaLinks.json presentation); value from companyfacts same accession |
| research_and_development | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (921 tags across all 75 R pages, face and notes) of 0001193125-26-044769; no face row matched |
| operating_income | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (921 tags across all 75 R pages, face and notes) of 0001193125-26-044769; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R2.htm | Interest expense | 2248000000 | 2248000000 | 2061000000 | 2061000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R2.htm | Income before income taxes | 9832000000 | 9832000000 | 8523000000 | 8523000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R2.htm | Provision for income taxes | 2050000000 | 2050000000 | 1866000000 | 1866000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R2.htm | Net income attributable to HCA Healthcare, Inc. | 6784000000 | 6784000000 | 5760000000 | 5760000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R2.htm | Basic earnings per share | 28.7 | 28.7 | 22.27 | 22.27 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R2.htm | Diluted earnings per share | 28.33 | 28.33 | 22 | 22 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R2.htm | Basic | 236413000 | 236413000 | 258603000 | 258603000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R2.htm | Diluted | 239495000 | 239495000 | 261806000 | 261806000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R2.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R4.htm | Cash and cash equivalents | 1040000000 | 1040000000 | 1933000000 | 1933000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R4.htm | Accounts receivable | 10867000000 | 10867000000 | 10751000000 | 10751000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R4.htm | Inventories | 1652000000 | 1652000000 | 1738000000 | 1738000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R4.htm | Total current assets | 15783000000 | 15783000000 | 16414000000 | 16414000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R4.htm | Property and equipment, net | 31141000000 | 31141000000 | 29414000000 | 29414000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:IntangibleAssetsNetIncludingGoodwill | R4.htm | Goodwill and other intangible assets | 10293000000 | 10293000000 | 10093000000 | 10093000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R4.htm | Total assets | 60720000000 | 60720000000 | 59513000000 | 59513000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R4.htm | Accounts payable | 4659000000 | 4659000000 | 4276000000 | 4276000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R4.htm | Total current liabilities | 16350000000 | 16350000000 | 15177000000 | 15177000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (921 tags across all 75 R pages, face and notes) of 0001193125-26-044769; no face row matched |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R4.htm | Stockholders' deficit attributable to HCA Healthcare, Inc. | -6027000000 | -6027000000 | -2499000000 | -2499000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R4.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 12636000000 | 12636000000 | 10514000000 | 10514000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -4988000000 | -4988000000 | -4933000000 | -4933000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -8550000000 | -8550000000 | -4582000000 | -4582000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property and equipment | -4944000000 | 4944000000 | -4875000000 | 4875000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 3523000000 | 3523000000 | 3312000000 | 3312000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation | 401000000 | 401000000 | 360000000 | 360000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Payment of dividends | -679000000 | 679000000 | -690000000 | 690000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -10067000000 | 10067000000 | -6042000000 | 6042000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest payments | 2207000000 | 2207000000 | 1938000000 | 1938000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income tax payments, net | 1740000000 | 1740000000 | 1844000000 | 1844000000 | Y | FILING-CHECKED | accn 0001193125-26-044769 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent | R4.htm | Short-term borrowings and long-term debt due within one year + Long-term debt, less debt issuance costs and discounts of | 46492000000 | 46492000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R5.htm | Common stock, shares outstanding | 224605100 | 224605100 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Revenues' on us-gaap:HealthCareOrganizationPatientServiceRevenueLessProvisionForBadDebts =  (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Total expenses including equity in earnings of affiliates' on hca:ExpensesIncludingEquityInEarningsOfAffiliates =  (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001193125-16-482165 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Interest expense' on us-gaap:InterestExpense =  (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest =  (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit =  (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Net income attributable to HCA Holdings, Inc.' on us-gaap:NetIncomeLoss =  (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Basic earnings per share' on us-gaap:EarningsPerShareBasic =  (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Diluted earnings per share' on us-gaap:EarningsPerShareDiluted =  (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Basic' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic =  (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-482165 R2.htm prints 'Diluted' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding =  (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 741000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Accounts receivable, less allowance for doubtful accounts of $5,326 and $5,011' on us-gaap:AccountsReceivableNetCurrent = 5889000000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Inventories' on us-gaap:InventoryNet = 1439000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 9232000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 15014000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Goodwill and other intangible assets' on us-gaap:IntangibleAssetsNetIncludingGoodwill = 6731000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Total assets' on us-gaap:Assets = 32744000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 2170000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 5516000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-482165 R4.htm prints 'Stockholders' deficit attributable to HCA Holdings, Inc.' on us-gaap:StockholdersEquity = -7599000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 4734000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -2583000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -1976000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Purchase of property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -2375000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 1904000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 239000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001193125-16-482165 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Repurchases of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -2397000000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Interest payments' on us-gaap:InterestPaidNet = 1650000000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-482165 R7.htm prints 'Income tax payments, net' on us-gaap:IncomeTaxesPaidNet = 1186000000 (FILING-CHECKED)
- revenue: era 10-K 0001193125-21-048994 R2.htm prints 'Revenues' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 51533000000 (FILING-CHECKED)
- cfo: era 10-K 0001193125-18-056057 R7.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 5426000000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001193125-18-056057 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -4279000000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001193125-18-056057 R7.htm prints 'Net cash (used in) provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -1061000000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: combined us-gaap:CostsAndExpenses (R2.htm): 2026-11-12 R2.htm: agree: the total includes interest, equity earnings and gains/losses and no OI line is printed: combined
- sga_expense: review us-gaap:GeneralAndAdministrativeExpense (R40.htm): 2026-11-12 R40.htm: R40 G&A 548,000,000 sits in an accounting-policy narrative and HCA prints no SG&A line; R40 read owed to decide component_in_note vs map
- research_and_development: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- operating_income: not_presented  (R2.htm): 2026-11-12 R2.htm: agree: whole-filing check agrees; nothing printed
- total_liabilities: not_presented  (R4.htm): 2026-11-12 R4.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:DebtCurrent+us-gaap:LongTermDebtNoncurrent (R4.htm): 2026-11-12 R4.htm: agree: R4 4,889 + 41,603
- net_income: mapped us-gaap:NetIncomeLoss (R2.htm): 2026-11-12 R2.htm: 20% mapped sample: IS R2.htm 'Net income attributable to HCA Healthcare, Inc.' is the net_income line, printed 6784000000 = filing XBRL 6784000000; agrees
- diluted_eps: mapped us-gaap:EarningsPerShareDiluted (R2.htm): 2026-11-12 R2.htm: 20% mapped sample: IS R2.htm 'Diluted earnings per share' is the diluted_eps line, printed 28.33 = filing XBRL 28.33; agrees
- accounts_receivable: mapped us-gaap:AccountsReceivableNetCurrent (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: BS R4.htm 'Accounts receivable' is the accounts_receivable line, printed 10867000000 = filing XBRL 10867000000; agrees
- goodwill: combined us-gaap:IntangibleAssetsNetIncludingGoodwill (R4.htm): 2026-11-12 R4.htm: sample DISAGREES: 'Goodwill and other intangible assets' (IntangibleAssetsNetIncludingGoodwill) bundles intangibles: combined, not goodwill
- cash_flow_financing: mapped us-gaap:NetCashProvidedByUsedInFinancingActivities (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Net cash used in financing activities' is the cash_flow_financing line, printed -8550000000 = filing XBRL -8550000000; agrees
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Interest payments' is the cash_paid_for_interest line, printed 2207000000 = filing XBRL 2207000000; agrees
- sga_expense (review resolved, Dhairya relay 2026-11-12): mapped us-gaap:GeneralAndAdministrativeExpense (R40.htm): decided by the filing: R40 prints total G&A 548,000,000 (FY2024 421,000,000); HCA prints no selling line, so G&A is the whole SG&A; fact only in a note -> mapped NOTE
- sga_expense: corrected to not_presented (Dhairya 2026-11-12, card AD.7): R40 548M is corporate-office costs only, a slice
- total_debt: finance-lease ruling (founder 2026-11-04 item 5, Dhairya 2026-11-12): R65 places finance leases (133 + 625) inside 'Short-term borrowings and long-term debt due within one year' and 'Long-term debt', so no lease is added
