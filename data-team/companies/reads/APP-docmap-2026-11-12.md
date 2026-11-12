# APP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001751008-26-000010 (CIK 0001751008, filed 2026-02-19): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001751008-23-000006 (CIK 0001751008, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001751008-22-000005 (CIK 0001751008, era filing): COVER R1.htm, IS R5.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001751008.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenue | 5480717000 | 5480717000 | 3224058000 | 3224058000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 665140000 | 665140000 | 520613000 | 520613000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (898 tags across all 91 R pages, face and notes) of 0001751008-26-000010; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and expenses | 1328803000 | 1328803000 | 1313102000 | 1313102000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 233502000 | 233502000 | 164916000 | 164916000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 226510000 | 226510000 | 374710000 | 374710000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 4151914000 | 4151914000 | 1910956000 | 1910956000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestAndDebtExpense | R5.htm | Interest expense and loss on settlement of debt | -207016000 | 207016000 | -317209000 | 317209000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 3952910000 | 3952910000 | 1611943000 | 1611943000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 519715000 | 519715000 | 22419000 | 22419000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 3333751000 | 3333751000 | 1579776000 | 1579776000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic net income per share (in dollars per share) | 9.84 | 9.84 | 4.68 | 4.68 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted net income per share (in dollars per share) | 9.75 | 9.75 | 4.53 | 4.53 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 338781000 | 338781000 | 336922000 | 336922000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 341970000 | 341970000 | 347808000 | 347808000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 2487096000 | 2487096000 | 697030000 | 697030000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net | 1819366000 | 1819366000 | 1283335000 | 1283335000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (898 tags across all 91 R pages, face and notes) of 0001751008-26-000010; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 4430792000 | 4430792000 | 2312190000 | 2312190000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net | 122445000 | 122445000 | 159970000 | 159970000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 1539986000 | 1539986000 | 1457685000 | 1457685000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 7259610000 | 7259610000 | 5869259000 | 5869259000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 746977000 | 746977000 | 504302000 | 504302000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 1333788000 | 1333788000 | 1057472000 | 1057472000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 5124939000 | 5124939000 | 4779441000 | 4779441000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 2134671000 | 2134671000 | 1089818000 | 1089818000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 3971094000 | 3971094000 | 2099011000 | 2099011000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash provided by (used in) investing activities | 358428000 | 358428000 | -106754000 | -106754000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash used in financing activities | -2593069000 | -2593069000 | -1749844000 | -1749844000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| capex | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements in MetaLinks.json (898 tags across all 91 R pages, face and notes) of 0001751008-26-000010; no face row matched |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Amortization, depreciation and write-offs | 194778000 | 194778000 | 448680000 | 448680000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation, excluding cash-settled awards | 210421000 | 210421000 | 369367000 | 369367000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (898 tags across all 91 R pages, face and notes) of 0001751008-26-000010; no face row matched |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchases of common stock | -2191944000 | 2191944000 | -981297000 | 981297000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Cash paid for interest | 198788000 | 198788000 | 270615000 | 270615000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Cash paid for income taxes, net of refunds | 194843000 | 194843000 | 67332000 | 67332000 | Y | FILING-CHECKED | accn 0001751008-26-000010 R8.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R3.htm | Long-term debt | 3512987000 | 3512987000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 676626000 |  |  |  |  | FILING-CHECKED | balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- FY2015 10-K: none in companyfacts (fy=2015, form 10-K): the FY2015 era cannot be read
- cash_and_equivalents: era 10-K 0001751008-23-000006 R3.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 1080484000 (FILING-CHECKED)
- cash_paid_for_income_taxes: era 10-K 0001751008-22-000005 R9.htm prints 'Cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 90616000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingAndMarketingExpense+us-gaap:ResearchAndDevelopmentExpense+us-gaap:GeneralAndAdministrativeExpense (R5.htm): 2026-11-12 R5.htm: corrected: 203,651 + 226,510 + 233,502 = 663,663 = 5,480,717 - 665,140 - 4,151,914 (thousands)
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- capex: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: CF R8 prints no PP&E purchase line (only intangibles)
- dividends_paid: not_presented  (R8.htm): 2026-11-12 R8.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent (R3.htm): 2026-11-12 R3.htm: corrected per finance-lease ruling (founder 2026-11-04 item 5): R59 places finance leases in current liabilities (17,481) and other non-current liabilities (105,172), outside the debt line: 3,512,987 +
- shares_outstanding: component sum us-gaap:CommonStockSharesOutstanding (R4.htm): 2026-11-12 R4.htm: agree: class rows at the BS date (R4)
- research_and_development: mapped us-gaap:ResearchAndDevelopmentExpense (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Research and development' is the research_and_development line, printed 226510000 = filing XBRL 226510000; agrees
- weighted_basic_shares: mapped us-gaap:WeightedAverageNumberOfSharesOutstandingBasic (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Basic (in shares)' is the weighted_basic_shares line, printed 338781000 = filing XBRL 338781000; agrees
- weighted_diluted_shares: mapped us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Diluted (in shares)' is the weighted_diluted_shares line, printed 341970000 = filing XBRL 341970000; agrees
- cash_and_equivalents: mapped us-gaap:CashAndCashEquivalentsAtCarryingValue (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Cash and cash equivalents' is the cash_and_equivalents line, printed 2487096000 = filing XBRL 2487096000; agrees
- accounts_payable: mapped us-gaap:AccountsPayableCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Accounts payable' is the accounts_payable line, printed 746977000 = filing XBRL 746977000; agrees
- current_liabilities: mapped us-gaap:LiabilitiesCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current liabilities' is the current_liabilities line, printed 1333788000 = filing XBRL 1333788000; agrees
- interest_expense: combined check: hand 2026-11-12 R5.htm: 'Interest expense and loss on settlement of debt' includes the debt-settlement loss: combined
