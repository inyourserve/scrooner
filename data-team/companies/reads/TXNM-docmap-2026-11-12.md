# TXNM document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001108426-26-000006 (CIK 0001108426, filed 2026-02-27): COVER R1.htm, IS R3.htm, CI R4.htm, CF R6.htm, BS R7.htm, BSP R8.htm
- 10-K 0001108426-16-000165 (CIK 0001108426, filed FY2015 era): COVER R1.htm, IS R2.htm, CI R3.htm, CF R5.htm, BS R6.htm, BSP R7.htm
- 10-K 0001108426-24-000008 (CIK 0001108426, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R6.htm, BS R7.htm, BSP R8.htm
- 10-K 0001108426-25-000014 (CIK 0001108426, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, CF R6.htm, BS R7.htm, BSP R8.htm
- companyfacts CIK0001108426.json (one call); submissions CIK0001108426.json (SIC 4911).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R3.htm | Electric Operating Revenues | 2165606000 | 2165606000 | 1971199000 | 1971199000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| cost_of_revenue | component sum | us-gaap:CostOfGoodsAndServicesSold[member: Cost of energy]+us-gaap:CostOfGoodsAndServicesSold[member: Cost of energy] | R3.htm | Cost of energy + Cost of energy | 814376000 |  | 677732000 |  | API missing | FILING-CHECKED | check: machine-full-filing / all printed member rows of one tag summed (value_source fsn_xbrl); no printed total on the face / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1688 tags across all 169 R pages, face and notes) of 0001108426-26-000006; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | mapped | us-gaap:UtilitiesOperatingExpense | R3.htm | Total operating expenses | 1724427000 | 1724427000 | 1517713000 | 1517713000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line; no cost-of-revenue line above it / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R3.htm | Administrative and general | 274453000 | 274453000 | 247116000 | 247116000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1688 tags across all 169 R pages, face and notes) of 0001108426-26-000006; HAND REVIEW: 3 label candidate(s) incl. custom tags: us-gaap:DeferredTaxAssetsTaxCreditCarryforwards 'Federal tax credit carryforwards / Deferred Tax Assets, Tax ' R155; us-gaap:EffectiveIncomeTaxRateReconciliationTaxCreditsResearch 'Research credits / Effective Income Tax Rate Reconciliation,' R153; us-gaap:IncomeTaxReconciliationTaxCreditsResearch 'Research credits / Effective Income Tax Rate Reconciliation,' R153 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 441179000 | 441179000 | 453486000 | 453486000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R3.htm | Interest Charges | 271522000 | 271522000 | 228066000 | 228066000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Earnings before Income Taxes | 180013000 | 180013000 | 280240000 | 280240000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Income Taxes (Benefits) | 10187000 | 10187000 | 21518000 | 21518000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic | R3.htm | Net Earnings Available for PNM Common Stock | 151362000 | 151362000 | 242154000 | 242154000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerBasicShare | R3.htm | Basic (in dollars per share) | 1.49 | 1.49 | 2.67 | 2.67 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare | R3.htm | Diluted (in dollars per share) | 1.48 | 1.48 | 2.67 | 2.67 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0001108426-26-000006 R3.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R77.htm | Average shares – basic (in shares) | 101507000 | 101507000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R77.htm 'Earnings and Dividends Per Share (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R77.htm | Average shares – diluted (in shares) | 102392000 | 102392000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R77.htm 'Earnings and Dividends Per Share (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R7.htm | Cash and cash equivalents | 18256000 | 18256000 | 4498000 | 4498000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R7.htm | Accounts receivable, net of allowance for credit losses of $1,394 and $1,398 | 151804000 | 151804000 | 130351000 | 130351000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R7.htm | Materials, supplies, and fuel stock | 181316000 | 181316000 | 166861000 | 166861000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R7.htm | Total current assets | 564662000 | 564662000 | 498836000 | 498836000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PublicUtilitiesPropertyPlantAndEquipmentNet | R7.htm | Net utility plant | 9311435000 | 9311435000 | 8437008000 | 8437008000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R7.htm | Goodwill | 278297000 | 278297000 | 278297000 | 278297000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R7.htm | Total assets | 12059285000 | 12059285000 | 11211733000 | 11211733000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R7.htm | Accounts payable | 243062000 | 243062000 | 204468000 | 204468000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R7.htm | Total current liabilities | 1017537000 | 1017537000 | 1775098000 | 1775098000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R7.htm | Total liabilities | 8599750000 | 8599750000 | 8616919000 | 8616919000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R7.htm | Total TXNM common stockholders’ equity | 3404018000 | 3404018000 | 2536385000 | 2536385000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R7.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R6.htm | Net cash flows from operating activities | 584489000 | 584489000 | 508160000 | 508160000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R6.htm | Net cash flows used in investing activities | -1217146000 | -1217146000 | -1174372000 | -1174372000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R6.htm | Net cash flows from financing activities | 642525000 | 642525000 | 684354000 | 684354000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R6.htm | Additions to utility and non-utility plant | -1195922000 | 1195922000 | -1247041000 | 1247041000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R6.htm | Depreciation and amortization | 483378000 | 483378000 | 423010000 | 423010000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R6.htm | Stock based compensation expense | 8719000 | 8719000 | 9480000 | 9480000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R6.htm | Dividends paid | -163373000 | 163373000 | -140339000 | 140339000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R6.htm | Awards of common stock | -11972000 | 11972000 | -8460000 | 8460000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R6.htm | Interest paid, net of amounts capitalized | 234160000 | 234160000 | 207972000 | 207972000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R6.htm | Income taxes paid (refunded), net | 2350000 | 2350000 | -998000 | -998000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001108426-26-000006 R6.htm period ..2025-12-31 |
| total_debt | component sum | us-gaap:ShortTermBorrowings+us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent+us-gaap:FinanceLeaseLiability(note) | R7.htm | Short-term debt + Current installments of long-term debt (includes $7,303 and $6,907 related to ETBC I) + Long-term Debt | 5637493000 | 5637493000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / printed BS debt lines; finance lease liabilities 37529000 from the lease note (no face line carries them); operating leases never included |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R8.htm | Common stock, shares outstanding (in shares) | 108921356 | 108921356 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001108426-16-000165 R2.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001108426-16-000165 R2.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Total operating expenses' on us-gaap:UtilitiesOperatingExpense = 1314732000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Administrative and general' on us-gaap:GeneralAndAdministrativeExpense = 179100000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Operating income' on us-gaap:OperatingIncomeLoss = 124350000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Interest Charges' on us-gaap:InterestExpense = 114860000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Earnings before Income Taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 46153000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Income Taxes' on us-gaap:IncomeTaxExpenseBenefit = 15075000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Net Earnings Attributable to Company' on us-gaap:NetIncomeLoss = 15640000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Basic (dollars per share)' on us-gaap:EarningsPerShareBasic = 0.2 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001108426-16-000165 R2.htm prints 'Diluted (dollars per share)' on us-gaap:EarningsPerShareDiluted = 0.2 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001108426-16-000165 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001108426-16-000165 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 46051000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Accounts receivable, net of allowance for uncollectible accounts' on us-gaap:AccountsReceivableNetCurrent = 98699000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Materials, supplies, and fuel stock' on us-gaap:InventoryNet = 67386000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 385570000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Net utility plant' on us-gaap:PublicUtilitiesPropertyPlantAndEquipmentNet = 4535372000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Goodwill' on us-gaap:Goodwill = 278297000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Total assets' on us-gaap:Assets = 6009328000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 100419000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 641120000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Total liabilities' on us-gaap:Liabilities = 4271579000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001108426-16-000165 R6.htm prints 'Total PNMR common stockholders’ equity' on us-gaap:StockholdersEquity = 1654813000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Net cash flows from operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 386874000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Net cash flows from investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -544528000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Net cash flows from financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 175431000 (FILING-CHECKED)
- capex: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Additions to utility and non-utility plant' on us-gaap:PaymentsToAcquireProductiveAssets = -558589000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Depreciation and amortization' on us-gaap:DepreciationDepletionAndAmortization = 222861000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Stock based compensation expense' on us-gaap:ShareBasedCompensation = 4863000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Dividends paid' on us-gaap:PaymentsOfOrdinaryDividends = -64251000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Purchase of common stock' on us-gaap:PaymentsForRepurchaseOfCommonStock = -17720000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Interest paid, net of amounts capitalized' on us-gaap:InterestPaidNet = 103382000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001108426-16-000165 R5.htm prints 'Income taxes paid (refunded), net' on us-gaap:IncomeTaxesPaidNet = -1890000 (FILING-CHECKED)
- interest_expense: era 10-K 0001108426-24-000008 R3.htm prints 'Interest Charges' on us-gaap:InterestExpense = 190355000 (FILING-CHECKED)
- basic_eps: era 10-K 0001108426-25-000014 R3.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 2.67 (FILING-CHECKED)
- diluted_eps: era 10-K 0001108426-25-000014 R3.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 2.67 (FILING-CHECKED)

## Mismatches (printed vs API)
- cost_of_revenue: API missing (us-gaap:CostOfGoodsAndServicesSold[member: Cost of energy]+us-gaap:CostOfGoodsAndServicesSold[member: Cost of energy])
