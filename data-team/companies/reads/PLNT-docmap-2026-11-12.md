# PLNT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001637207-26-000011 (CIK 0001637207, filed 2026-02-25): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- 10-K 0001564590-16-014027 (CIK 0001637207, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001564590-18-004109 (CIK 0001637207, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R6.htm
- 10-K 0001637207-24-000020 (CIK 0001637207, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R7.htm
- companyfacts CIK0001637207.json (one call); submissions CIK0001637207.json (SIC 7997).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenue | 1324144000 | 1324144000 | 1181654000 | 1181654000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenue | 230308000 | 230308000 | 197122000 | 197122000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1020 tags across all 108 R pages, face and notes) of 0001637207-26-000011; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total operating costs and expenses | 929467000 | 929467000 | 857456000 | 857456000 | Y | FILING-CHECKED | check: machine-full-filing / CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R5.htm | Selling, general and administrative | 137634000 | 137634000 | 129146000 | 129146000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1020 tags across all 108 R pages, face and notes) of 0001637207-26-000011; label search over every tag in the filing (custom included) found no candidate |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 394677000 | 394677000 | 324198000 | 324198000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -108244000 | 108244000 | -100037000 | 100037000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before income taxes | 308978000 | 308978000 | 246728000 | 246728000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Provision for income taxes | 85874000 | 85874000 | 68443000 | 68443000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to Planet Fitness, Inc. | 219104000 | 219104000 | 172042000 | 172042000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in usd per share) | 2.62 |  | 2.01 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in usd per share) | 2.62 |  | 2 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 83518664 |  | 85621282 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 83725825 |  | 85827437 |  | API missing | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 345652000 | 345652000 | 293150000 | 293150000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowances for uncollectible amounts of $428 and $30 as of December 31, 2025 and 2024, respe | 70431000 | 70431000 | 77145000 | 77145000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R3.htm | Inventory | 7581000 | 7581000 | 6146000 | 6146000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 658386000 | 658386000 | 588019000 | 588019000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | R3.htm | Property and equipment, net of accumulated depreciation of $453,852 and $370,118, as of December 31, 2025 and 2024, resp | 466747000 | 466747000 | 423991000 | 423991000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 712450000 | 712450000 | 720633000 | 720633000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 3103395000 | 3103395000 | 3069708000 | 3069708000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 39683000 | 39683000 | 32887000 | 32887000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 312490000 | 312490000 | 282495000 | 282495000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (1020 tags across all 108 R pages, face and notes) of 0001637207-26-000011; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ deficit attributable to Planet Fitness, Inc. | -482777000 | -482777000 | -215380000 | -215380000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 418421000 | 418421000 | 343873000 | 343873000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -160164000 | -160164000 | -208711000 | -208711000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash used in financing activities | -198095000 | -198095000 | -104995000 | -104995000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Additions to property and equipment | -163670000 | 163670000 | -155061000 | 155061000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R7.htm | Depreciation and amortization | 155785000 | 155785000 | 160346000 | 160346000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Equity-based compensation | 12333000 | 12333000 | 8913000 | 8913000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1020 tags across all 108 R pages, face and notes) of 0001637207-26-000011; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:MinorityInterestDecreaseFromDistributionsToNoncontrollingInterestHolders 'Non-cash adjustments to VIEs / Noncontrolling Interest, Decr' R8 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase and retirement of Class A common stock | -500373000 | 500373000 | -300205000 | 300205000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for interest | 100247000 | 100247000 | 90853000 | 90853000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001637207-26-000011 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R95.htm | Net cash paid for income taxes | 21450000 | 21450000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R95.htm 'Income taxes - Additional information (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtCurrent | R3.htm | Current maturities of long-term debt | 23875000 | 23875000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | component sum | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 80762000 |  |  |  |  | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; classes summed (printed rows) |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 330537000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Cost of revenue' on us-gaap:CostOfRevenue = 113492000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Total operating costs and expenses' on us-gaap:CostsAndExpenses = 258435000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Selling, general and administrative' on us-gaap:SellingGeneralAndAdministrativeExpense = 55573000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 72102000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -24549000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 47278000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Provision for income taxes' on us-gaap:IncomeTaxExpenseBenefit = 9148000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Net income attributable to Planet Fitness, Inc.' on us-gaap:NetIncomeLoss = 18518000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Basic & diluted' on us-gaap:EarningsPerShareBasicAndDiluted = 0.11 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001564590-16-014027 R4.htm prints 'Basic & diluted' on us-gaap:EarningsPerShareBasicAndDiluted = 0.11 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001564590-16-014027 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001564590-16-014027 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 31430000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Accounts receivable, net of allowance for bad debts of $629 and $399 at December' on us-gaap:AccountsReceivableNetCurrent = 19079000 (FILING-CHECKED)
- inventory: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Inventory' on us-gaap:InventoryNet = 4557000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 72945000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Property and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 56139000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 176981000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Total assets' on us-gaap:Assets = 699177000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Accounts payable' on us-gaap:AccountsPayableCurrent = 23950000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001564590-16-014027 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 66252000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001564590-16-014027 R2.htm read; no row matched (auto)
- cfo: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 81663000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -19161000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -74240000 (FILING-CHECKED)
- capex: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Additions to property and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -19488000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 32158000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Equity-based compensation' on us-gaap:ShareBasedCompensation = 4877000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001564590-16-014027 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 23220000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-16-014027 R6.htm prints 'Net cash paid for income taxes' on us-gaap:IncomeTaxesPaid = 2834000 (FILING-CHECKED)
- revenue: era 10-K 0001564590-18-004109 R4.htm prints 'Total revenue' on us-gaap:SalesRevenueNet = 429942000 (FILING-CHECKED)
- interest_expense: era 10-K 0001564590-18-004109 R4.htm prints 'Interest expense, net' on us-gaap:InterestIncomeExpenseNonoperatingNet = -35283000 (FILING-CHECKED)
- cfo: era 10-K 0001564590-18-004109 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations = 131021000 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001564590-18-004109 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations = -37042000 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001564590-18-004109 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations = -21703000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001564590-18-004109 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 31418000 (FILING-CHECKED)
- interest_expense: era 10-K 0001637207-24-000020 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -86576000 (FILING-CHECKED)

## Mismatches (printed vs API)
- basic_eps: API missing (us-gaap:EarningsPerShareBasic)
- diluted_eps: API missing (us-gaap:EarningsPerShareDiluted)
- weighted_basic_shares: API missing (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: API missing (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)
