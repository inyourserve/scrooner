# HLT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001585689-26-000007 (CIK 0001585689, filed 2026-02-11): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001585689-16-000161 (CIK 0001585689, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001585689-18-000033 (CIK 0001585689, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R8.htm
- 10-K 0001585689-25-000008 (CIK 0001585689, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- companyfacts CIK0001585689.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues | 12039000000 | 12039000000 | 11174000000 | 11174000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (928 tags across all 103 R pages, face and notes) of 0001585689-26-000007; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (928 tags across all 103 R pages, face and notes) of 0001585689-26-000007; no face row matched |
| operating_expenses | mapped | hlt:CostsAndExpensesExcludingCostOfReimbursableExpense | R5.htm | Total expenses excluding reimbursable expenses | 1796000000 |  | 1824000000 |  | API missing | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it; company extension tag, matched by printed label / accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 393000000 | 393000000 | 415000000 | 415000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (928 tags across all 103 R pages, face and notes) of 0001585689-26-000007; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Operating income | 2693000000 | 2693000000 | 2370000000 | 2370000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -620000000 | 620000000 | -569000000 | 569000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 2072000000 | 2072000000 | 1783000000 | 1783000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -611000000 | 611000000 | -244000000 | 244000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Hilton stockholders | 1457000000 | 1457000000 | 1535000000 | 1535000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic EPS | 6.18 | 6.18 | 6.2 | 6.2 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted EPS | 6.12 | 6.12 | 6.14 | 6.14 | Y | FILING-CHECKED | accn 0001585689-26-000007 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R96.htm | Earnings (Loss) Per Share (Details) |  | 236000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R96.htm 'Earnings (Loss) Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R96.htm | Earnings (Loss) Per Share (Details) |  | 238000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R96.htm 'Earnings (Loss) Per Share (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 918000000 | 918000000 | 1301000000 | 1301000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance for credit losses | 1690000000 | 1690000000 | 1583000000 | 1583000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (928 tags across all 103 R pages, face and notes) of 0001585689-26-000007; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 2996000000 | 2996000000 | 3272000000 | 3272000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 684000000 | 684000000 | 411000000 | 411000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5081000000 | 5081000000 | 5035000000 | 5035000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 16774000000 | 16774000000 | 16522000000 | 16522000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable, accrued expenses and other | 2336000000 | 2336000000 | 2124000000 | 2124000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 4508000000 | 4508000000 | 4700000000 | 4700000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 22120000000 | 22120000000 | 20211000000 | 20211000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total Hilton stockholders' deficit | -5388000000 | -5388000000 | -3727000000 | -3727000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 2129000000 | 2129000000 | 2013000000 | 2013000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -190000000 | -190000000 | -446000000 | -446000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -2348000000 | -2348000000 | -1045000000 | -1045000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Capital expenditures for property and equipment | -101000000 | 101000000 | -96000000 | 96000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R8.htm | Depreciation and amortization expenses | 177000000 | 177000000 | 146000000 | 146000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Share-based compensation expense | 170000000 | 170000000 | 176000000 | 176000000 | Y | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R8.htm | Dividends paid | -143000000 | 143000000 | -150000000 | 150000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock, including excise tax payments | -3182000000 | 3182000000 | -2893000000 | 2893000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001585689-26-000007 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R103.htm | Supplemental Disclosure of Cash Flow Information (Details) |  | 648000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R103.htm 'Supplemental Disclosure of Cash Flow Information (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R77.htm | Income Taxes - Schedule of Cash Flow, Supplemental Disclosures (Details) |  | 523000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R77.htm 'Income Taxes - Schedule of Cash Flow, Supplemental Disclosures (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | component sum | us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations | R3.htm | Current maturities of long-term debt + Long-term debt | 12363000000 | 12363000000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, outstanding shares (in shares) | 230433192 | 230433192 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Total revenues' on us-gaap:Revenues = 11272000000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Total expenses excluding cost of reimbursable expense' on hlt:CostsAndExpensesExcludingCostOfReimbursableExpense = 5377000000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001585689-16-000161 R4.htm prints 'General, administrative and other' on us-gaap:GeneralAndAdministrativeExpense = 611000000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 2071000000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -575000000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 1496000000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -80000000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Net income attributable to Hilton Stockholders' on us-gaap:NetIncomeLoss = 1404000000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Earnings per share, basic' on us-gaap:EarningsPerShareBasic = 1.42 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001585689-16-000161 R4.htm prints 'Earnings per share, diluted' on us-gaap:EarningsPerShareDiluted = 1.42 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001585689-16-000161 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001585689-16-000161 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 609000000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts' on us-gaap:AccountsReceivableNetCurrent = 876000000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 2585000000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 9119000000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 5887000000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Total assets' on us-gaap:Assets = 25716000000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Accounts payable, accrued expenses and other' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 2206000000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 2467000000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 19765000000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001585689-16-000161 R2.htm prints 'Total Hilton stockholders' equity' on us-gaap:StockholdersEquity = 5985000000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 1394000000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Net cash provided by (used in) investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 392000000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -1724000000 (FILING-CHECKED)
- capex: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Capital expenditures for property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -310000000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 692000000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = 124000000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001585689-16-000161 R7.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -138000000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001585689-16-000161 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001585689-16-000161 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001585689-16-000161 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001585689-18-000033 R4.htm prints 'Total revenues' on us-gaap:Revenues = 9140000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001585689-25-000008 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -569000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- operating_expenses: API missing (hlt:CostsAndExpensesExcludingCostOfReimbursableExpense)

## Hand checks 2026-11-12 (Ritwik cloud)
- cost_of_revenue: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R96.htm): 2026-11-12 R96.htm: agree: carrying sentence read: the note value is the full data point
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R96.htm): 2026-11-12 R96.htm: agree: carrying sentence read: the note value is the full data point
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- cash_paid_for_interest: mapped us-gaap:InterestPaidNet (R103.htm): 2026-11-12 R103.htm: agree: carrying sentence read: the note value is the full data point
- cash_paid_for_income_taxes: mapped us-gaap:IncomeTaxesPaidNet (R77.htm): 2026-11-12 R77.htm: agree: carrying sentence read: the note value is the full data point
- total_debt: component sum us-gaap:LongTermDebtAndCapitalLeaseObligationsCurrent+us-gaap:LongTermDebtAndCapitalLeaseObligations (R3.htm): 2026-11-12 R3.htm: agree: R3 lines on LongTermDebtAndCapitalLeaseObligations*; R68 places finance leases inside the debt lines (finance-lease ruling (founder 2026-11-04 item 5))
- operating_expenses: mapped hlt:CostsAndExpensesExcludingCostOfReimbursableExpense (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Total expenses excluding reimbursable expenses' is the operating_expenses line, printed 1796000000 = filing XBRL ; agrees
- net_income: mapped us-gaap:NetIncomeLoss (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Net income attributable to Hilton stockholders' is the net_income line, printed 1457000000 = filing XBRL 1457000000; agrees
- accounts_payable: combined us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: sample DISAGREES: 'Accounts payable, accrued expenses and other' bundles accrued expenses: combined
- total_liabilities: mapped us-gaap:Liabilities (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total liabilities' is the total_liabilities line, printed 22120000000 = filing XBRL 22120000000; agrees
- sbc: mapped us-gaap:ShareBasedCompensation (R8.htm): 2026-11-12 R8.htm: 20% mapped sample: CF R8.htm 'Share-based compensation expense' is the sbc line, printed 170000000 = filing XBRL 170000000; agrees
- shares_outstanding: mapped us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: 20% mapped sample: BSP R4.htm 'Common stock, outstanding shares (in shares)' is the shares_outstanding line, printed 230433192 = filing XBRL 230433192; agrees
