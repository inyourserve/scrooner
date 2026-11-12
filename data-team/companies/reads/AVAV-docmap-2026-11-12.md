# AVAV document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12); a not_presented row whose note starts AUTO is the tool finding no matching face line, not a by-hand verdict.

## Filings opened
- 10-K 0001104659-26-078906 (CIK 0001368622, filed 2026-06-29): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001558370-25-008838 (CIK 0001368622, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R8.htm
- 10-K 0001558370-23-011469 (CIK 0001368622, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R6.htm, CF R9.htm
- companyfacts CIK0001368622.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Revenue | 1976845000 | 1976845000 | 820627000 | 820627000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of sales | 1476203000 | 1476203000 | 501991000 | 501991000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| gross_profit | mapped | us-gaap:GrossProfit | R4.htm | Total gross margin | 500642000 | 500642000 | 318636000 | 318636000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| operating_expenses | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R4.htm read; no face row matched the operating_expenses tag/label rules; not hand-verified |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R4.htm | Selling, general and administrative | 443251000 | 443251000 | 158753000 | 158753000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R4.htm | Research and development | 127678000 | 127678000 | 100729000 | 100729000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R4.htm | (Loss) income from operations | -310995000 | -310995000 | 40795000 | 40795000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| interest_expense | mapped | us-gaap:InterestIncomeExpenseNonoperatingNet | R4.htm | Interest expense, net | -5613000 | -5613000 | -2188000 | -2188000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R4.htm | (Loss) income before income taxes | -305622000 | -305622000 | 39664000 | 39664000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | (Benefit from) provision for income taxes | -23059000 | -23059000 | 882000 | 882000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| net_income | mapped | us-gaap:ProfitLoss | R4.htm | Net (loss) income | -265122000 | -265122000 | 43619000 | 43619000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Basic (in dollars per share) | -5.4 | -5.4 | 1.56 | 1.56 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Diluted (in dollars per share) | -5.4 | -5.4 | 1.55 | 1.55 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Basic (in shares) | 49087346 | 49087346 | 28018656 | 28018656 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Diluted (in shares) | 49087346 | 49087346 | 28173488 | 28173488 | Y | FILING-CHECKED | accn 0001104659-26-078906 R4.htm period ..2026-04-30 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 377325000 | 377325000 | 40862000 | 40862000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R2.htm | Accounts receivable, net of allowance for credit losses of $1,961 at April 30, 2026 and $203 at April 30, 2025 | 316167000 | 316167000 | 101967000 | 101967000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| inventory | mapped | us-gaap:InventoryNet | R2.htm | Inventories, net | 312856000 | 312856000 | 144090000 | 144090000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| current_assets | mapped | us-gaap:AssetsCurrent | R2.htm | Total current assets | 1890423000 | 1890423000 | 606516000 | 606516000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R2.htm | Property and equipment, net | 166719000 | 166719000 | 50704000 | 50704000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 2493678000 | 2493678000 | 256781000 | 256781000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 5716742000 | 5716742000 | 1120567000 | 1120567000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R2.htm | Accounts payable | 160507000 | 160507000 | 72462000 | 72462000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R2.htm | Total current liabilities | 439237000 | 439237000 | 172161000 | 172161000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| total_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R2.htm read; no face row matched the total_liabilities tag/label rules; not hand-verified |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R2.htm | Total stockholders' equity | 4400400000 | 4400400000 | 886507000 | 886507000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001104659-26-078906 R2.htm period ..2026-04-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash (used in) provided by operating activities | -78404000 | -78404000 | -1318000 | -1318000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -1232671000 | -1232671000 | -28490000 | -28490000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 1647178000 | 1647178000 | -2856000 | -2856000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Acquisition of property and equipment | -62544000 | 62544000 | -19547000 | 19547000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 265037000 | 265037000 | 40998000 | 40998000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Stock-based compensation | 38334000 | 38334000 | 21461000 | 21461000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the dividends_paid tag/label rules; not hand-verified |
| share_buybacks | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | AUTO: R8.htm read; no face row matched the share_buybacks tag/label rules; not hand-verified |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | Interest | 12847000 | 12847000 | 1757000 | 1757000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R8.htm | Income taxes | 3606000 | 3606000 | 24631000 | 24631000 | Y | FILING-CHECKED | accn 0001104659-26-078906 R8.htm period ..2026-04-30 |
| total_debt | component sum | us-gaap:LongTermDebtNoncurrent | R2.htm | Long-term debt | 728967000 | 728967000 |  |  | Y | FILING-CHECKED | sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, outstanding shares | 50610514 | 50610514 |  |  | Y | FILING-CHECKED | balance-sheet date 2026-04-30; single row |

## Era checks (tag changes in the last ~5 years)
- revenue: era 10-K 0001558370-25-008838 R4.htm prints 'Revenue' on us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax = 820627000 (FILING-CHECKED)
- stockholders_equity: era 10-K 0001558370-23-011469 R2.htm prints 'Total AeroVironment, Inc. stockholders' equity' on us-gaap:StockholdersEquity = 550970000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
