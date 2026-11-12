# SAIC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001571123-26-000029 (CIK 0001571123, filed 2026-03-16): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- 10-K 0001564590-15-002280 (CIK 0001571123, filed FY2015 era): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R7.htm, CI R17.htm
- 10-K 0001571123-18-000010 (CIK 0001571123, era filing): COVER R1.htm, IS R2.htm, BS R3.htm, BSP R4.htm, CF R7.htm
- 10-K 0001571123-23-000031 (CIK 0001571123, era filing): COVER R1.htm, IS R3.htm, CI R4.htm, BS R5.htm, BSP R6.htm, CF R9.htm
- companyfacts CIK0001571123.json (one call); submissions CIK0001571123.json (SIC 7373).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R3.htm | Revenues | 7262000000 | 7262000000 | 7479000000 | 7479000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R3.htm | Cost of revenues | 6390000000 | 6390000000 | 6587000000 | 6587000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| gross_profit | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (857 tags across all 95 R pages, face and notes) of 0001571123-26-000029; label search over every tag in the filing (custom included) found no candidate |
| operating_expenses | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingExpenses in MetaLinks.json (857 tags across all 95 R pages, face and notes) of 0001571123-26-000029; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:OperatingIncomeLoss 'Operating income / Operating Income (Loss) / The net result ' R3 |
| sga_expense | mapped | us-gaap:SellingGeneralAndAdministrativeExpense | R3.htm | Selling, general and administrative expenses | 350000000 | 350000000 | 339000000 | 339000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R47.htm | Internal research and development costs included in selling, general and administrative expenses | 13000000 | 13000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R47.htm 'Business Overview and Summary of Significant Accounting Policies - Narrative (De' (MetaLinks.json presentation) |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R3.htm | Operating income | 521000000 | 521000000 | 563000000 | 563000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| interest_expense | combined | us-gaap:InterestExpenseOperating | R3.htm | Interest expense, net | 128000000 | 128000000 | 126000000 | 126000000 | Y | FILING-CHECKED | check: machine-full-filing / net interest line: interest_expense is the gross charge only, a net line is combined (Dhairya 2026-11-12) / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R3.htm | Income before income taxes | 387000000 | 387000000 | 428000000 | 428000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R3.htm | Provision for income taxes | -29000000 | 29000000 | -66000000 | 66000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| net_income | mapped | us-gaap:ProfitLoss | R3.htm | Net income | 358000000 | 358000000 | 362000000 | 362000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R3.htm | Basic (in dollars per share) | 7.73 | 7.73 | 7.23 | 7.23 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R3.htm | Diluted (in dollars per share) | 7.7 | 7.7 | 7.17 | 7.17 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R3.htm period ..2026-01-30 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R49.htm | Basic weighted-average number of shares outstanding (in shares) | 46.3 | 46300000 |  |  | N (printed 46.3 vs API 46300000) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R49.htm 'Earnings Per Share, Share Repurchases and Dividends - Schedule of Weighted Avera' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R49.htm | Diluted weighted-average number of shares outstanding (in shares) | 46.5 | 46500000 |  |  | N (printed 46.5 vs API 46500000) | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R49.htm 'Earnings Per Share, Share Repurchases and Dividends - Schedule of Weighted Avera' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R5.htm | Cash and cash equivalents | 182000000 | 182000000 | 56000000 | 56000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R5.htm | Receivables, net | 853000000 | 853000000 | 1000000000 | 1000000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| inventory | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (857 tags across all 95 R pages, face and notes) of 0001571123-26-000029; HAND REVIEW: 1 label candidate(s) incl. custom tags: us-gaap:DisposalGroupIncludingDiscontinuedOperationInventory1 'Inventories, net / Disposal Group, Including Discontinued Op' R95 |
| current_assets | mapped | us-gaap:AssetsCurrent | R5.htm | Total current assets | 1179000000 | 1179000000 | 1154000000 | 1154000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R5.htm | Property, plant, and equipment, net | 110000000 | 110000000 | 104000000 | 104000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| goodwill | mapped | us-gaap:Goodwill | R5.htm | Goodwill | 2944000000 | 2944000000 | 2851000000 | 2851000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| total_assets | mapped | us-gaap:Assets | R5.htm | Total assets | 5354000000 | 5354000000 | 5246000000 | 5246000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R5.htm | Accounts payable | 500000000 | 500000000 | 631000000 | 631000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R5.htm | Total current liabilities | 982000000 | 982000000 | 1396000000 | 1396000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| total_liabilities | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (857 tags across all 95 R pages, face and notes) of 0001571123-26-000029; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R5.htm | Total stockholders' equity | 1500000000 | 1500000000 | 1577000000 | 1577000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R5.htm period ..2026-01-30 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 609000000 | 609000000 | 494000000 | 494000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash (used in) provided by investing activities | -248000000 | -248000000 | -35000000 | -35000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash used in financing activities | -235000000 | -235000000 | -498000000 | -498000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R9.htm | Expenditures for property, plant, and equipment | -32000000 | 32000000 | -36000000 | 36000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAndAmortization | R9.htm | Depreciation and amortization | 149000000 | 149000000 | 140000000 | 140000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation expense | 64000000 | 64000000 | 53000000 | 53000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R9.htm | Dividend payments to stockholders | -70000000 | 70000000 | -75000000 | 75000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R9.htm | Stock repurchased and retired or withheld for taxes on equity awards | -445000000 | 445000000 | -558000000 | 558000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R9.htm | Cash paid for interest | 101000000 | 101000000 | 121000000 | 121000000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001571123-26-000029 R9.htm period ..2026-01-30 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R73.htm | Income Taxes Paid, Net | 22000000 | 22000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R73.htm 'Income Taxes - Narrative (Details)' (MetaLinks.json presentation) |
| total_debt | component sum | us-gaap:LongTermDebtCurrent+us-gaap:LongTermDebtNoncurrent | R5.htm | Debt, current portion + Debt, net of current portion | 2487000000 | 2487000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / sum of printed BS debt lines (auto; leases and other borrowings need a by-hand check) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R6.htm | Common stock, shares outstanding (in shares) | 44000000 | 44000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-01-30; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- research_and_development: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- income_tax_expense: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- net_income: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- basic_eps: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- diluted_eps: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- weighted_basic_shares: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001564590-15-002280 R2.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- accounts_receivable: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- accounts_payable: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- current_liabilities: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001564590-15-002280 R3.htm read; no row matched (auto)
- cfo: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- cash_flow_investing: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- cash_flow_financing: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- capex: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001564590-15-002280 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001571123-18-000010 R2.htm prints 'Revenues' on us-gaap:Revenues = 4454000000 (FILING-CHECKED)
- net_income: era 10-K 0001571123-18-000010 R2.htm prints 'Net income' on us-gaap:NetIncomeLoss = 179000000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001571123-18-000010 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 41000000 (FILING-CHECKED)
- interest_expense: era 10-K 0001571123-23-000031 R3.htm prints 'Interest expense' on us-gaap:InterestExpense = 120000000 (FILING-CHECKED)

## Mismatches (printed vs API)
- weighted_basic_shares: N (printed 46.3 vs API 46300000) (us-gaap:WeightedAverageNumberOfSharesOutstandingBasic)
- weighted_diluted_shares: N (printed 46.5 vs API 46500000) (us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding)
