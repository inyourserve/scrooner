# FRHC document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000924805-26-000012 (CIK 0000924805, filed 2026-06-01): COVER R1.htm, BS R3.htm, IS R4.htm, BSP R5.htm, CF R7.htm
- 10-K 0001038838-15-000084 (CIK 0000924805, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000924805-24-000041 (CIK 0000924805, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R8.htm
- 10-K 0001654954-17-006033 (CIK 0000924805, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- companyfacts CIK0000924805.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R4.htm | TOTAL REVENUE, NET | 2191291000 | 2191291000 | 2004155000 | 2004155000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Cost of sales | 79632000 | 79632000 | 31278000 | 31278000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | TOTAL EXPENSE | 1965326000 | 1965326000 | 1899572000 | 1899572000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative expense | 222339000 | 222339000 | 162474000 | 162474000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| operating_income | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R4.htm | Interest expense | 489036000 | 489036000 | 535895000 | 535895000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | INCOME BEFORE INCOME TAX | 225965000 | 225965000 | 104583000 | 104583000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax expense | -72637000 | 72637000 | -28425000 | 28425000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | NET INCOME ATTRIBUTABLE TO COMMON SHAREHOLDERS | 153328000 | 153328000 | 76287000 | 76287000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Earnings per common share - basic (in dollars per share) | 2.56 | 2.56 | 1.28 | 1.28 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Earnings per common share - diluted (in dollars per share) | 2.51 | 2.51 | 1.26 | 1.26 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average number of shares (basic) (in shares) | 59992357 | 59992357 | 59393629 | 59393629 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average number of shares (diluted) (in shares) | 61117931 | 61117931 | 60490564 | 60490564 | Y | FILING-CHECKED | accn 0000924805-26-000012 R4.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 966115000 | 966115000 | 837302000 | 837302000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:OtherReceivablesNetCurrent | R3.htm | Margin lending, brokerage and other receivables, net | 4690782000 | 4690782000 | 3319145000 | 3319145000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Fixed assets, net | 358396000 | 358396000 | 191103000 | 191103000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 51099000 | 51099000 | 49093000 | 49093000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | TOTAL ASSETS | 13155239000 | 13155239000 | 9915117000 | 9915117000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | TOTAL LIABILITIES | 11665960000 | 11665960000 | 8690553000 | 8690553000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | TOTAL FRHC SHAREHOLDERS' EQUITY | 1489279000 | 1489279000 | 1224447000 | 1224447000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R3.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash flows from/(used in) operating activities | 185221000 | 185221000 | 1681058000 | 1681058000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash flows used in investing activities | -1049155000 | -1049155000 | -905472000 | -905472000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash flows (used in)/from financing activities | 1191629000 | 1191629000 | -1578000 | -1578000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R7.htm | Purchase of fixed assets | -198766000 | 198766000 | -80902000 | 80902000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation and amortization | 34560000 | 34560000 | 17158000 | 17158000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock compensation expense | 68047000 | 68047000 | 59592000 | 59592000 | Y | FILING-CHECKED | accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| dividends_paid | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends in MetaLinks.json (1224 tags across all 166 R pages, face and notes) of 0000924805-26-000012; no face row matched |
| share_buybacks | mapped | frhc:NetRepaymentsProceedsFromSecuritiesRepurchaseAgreementObligations | R7.htm | Net (repayment)/proceeds from securities repurchase agreement obligations | -431540000 |  | -1061430000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0000924805-26-000012 R7.htm period ..2026-03-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R8.htm | CONSOLIDATED STATEMENTS OF CASH FLOWS (Parenthetical) |  | 452976000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R8.htm 'CONSOLIDATED STATEMENTS OF CASH FLOWS (Parenthetical)' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R108.htm | INCOME TAXES - Schedule of tax paid (Details) |  | 81300000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R108.htm 'INCOME TAXES - Schedule of tax paid (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | mapped | us-gaap:DebtInstrumentCarryingAmount | R134.htm | OTHER LIABILITIES - Schedule of loans received (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R134.htm 'OTHER LIABILITIES - Schedule of loans received (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R81.htm | RECAST - Condensed consolidated balance sheet (Details) |  | 61292581 |  |  |  | FILING-CHECKED | not on the face statement; shown in R81.htm 'RECAST - Condensed consolidated balance sheet (Details)' (MetaLinks.json presentation); value from companyfacts same accession |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001038838-15-000084 R4.htm prints 'REVENUES' on us-gaap:Revenues = 0 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001038838-15-000084 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001038838-15-000084 R4.htm prints 'Total costs and operating expenses' on us-gaap:CostsAndExpenses = 80410 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001038838-15-000084 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 80410 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001038838-15-000084 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001038838-15-000084 R4.htm prints 'LOSS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -73591 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001038838-15-000084 R4.htm prints 'INCOME TAX BENEFIT' on us-gaap:IncomeTaxExpenseBenefit = 54804 (FILING-CHECKED)
- net_income: FY2015 10-K 0001038838-15-000084 R4.htm prints 'NET LOSS' on us-gaap:NetIncomeLoss = -18787 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001038838-15-000084 R4.htm prints 'BASIC AND DILUTED NET LOSS PER COMMON SHARE' on us-gaap:IncomeLossFromContinuingOperationsPerBasicAndDilutedShare = 0 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001038838-15-000084 R4.htm prints 'BASIC AND DILUTED NET LOSS PER COMMON SHARE' on us-gaap:IncomeLossFromContinuingOperationsPerBasicAndDilutedShare = 0 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001038838-15-000084 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001038838-15-000084 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001038838-15-000084 R2.htm prints 'Cash and cash equivalents' on us-gaap:Cash = 8624986 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001038838-15-000084 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001038838-15-000084 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001038838-15-000084 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001038838-15-000084 R2.htm prints 'TOTAL ASSETS' on us-gaap:Assets = 8624986 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001038838-15-000084 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001038838-15-000084 R2.htm prints 'Total shareholders' deficit' on us-gaap:StockholdersEquity = -38084 (FILING-CHECKED)
- cfo: FY2015 10-K 0001038838-15-000084 R6.htm prints 'Net cash provided by (used in) operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 40201 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001038838-15-000084 R6.htm prints 'Net cash provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 0 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001038838-15-000084 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -2460 (FILING-CHECKED)
- capex: FY2015 10-K 0001038838-15-000084 R6.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001038838-15-000084 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAndAmortization = 0 (FILING-CHECKED)
- sbc: FY2015 10-K 0001038838-15-000084 R6.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001038838-15-000084 R6.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001038838-15-000084 R6.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001038838-15-000084 R6.htm read; no row matched (auto)
- interest_expense: era 10-K 0000924805-24-000041 R5.htm prints 'Interest expense (including $955, $1,578 and $217 from related parties)' on us-gaap:InterestExpense = 501111000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001654954-17-006033 R4.htm prints 'LOSS BEFORE INCOME TAXES' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = -578039 (FILING-CHECKED)
- cfo: era 10-K 0001654954-17-006033 R6.htm prints 'Net cash used in operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = -369141 (FILING-CHECKED)
- cash_flow_investing: era 10-K 0001654954-17-006033 R6.htm prints 'Net cash provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 0 (FILING-CHECKED)
- cash_flow_financing: era 10-K 0001654954-17-006033 R6.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 320000 (FILING-CHECKED)
- depreciation_and_amortization: era 10-K 0001654954-17-006033 R6.htm prints 'Depreciation expense' on us-gaap:DepreciationAndAmortization = 3330 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001654954-17-006033 R6.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 0 (FILING-CHECKED)

## Mismatches (printed vs API)
- share_buybacks: API missing (frhc:NetRepaymentsProceedsFromSecuritiesRepurchaseAgreementObligations)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 1965326000 vs printed 1965326000 |
| sga_expense | mapped-sample | agree | page value 222339000 vs printed 222339000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_tax_expense | mapped-sample | agree | page value -72637000 vs printed -72637000 |
| inventory | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_flow_financing | mapped-sample | agree | page value 1191629000 vs printed 1191629000 |
| depreciation_and_amortization | combined | agree | page value 34560000 vs printed 34560000 |
| dividends_paid | not_presented | agree | none of the candidate elements in MetaLinks.json |
| share_buybacks | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_income_taxes | NOTE | agree | page value 81300000 vs API 81300000 |
| total_debt | NOTE | agree | value 96771000 read off its own R page (no companyfacts fact to compare) |
| shares_outstanding | NOTE | agree | page value 61292581 vs API 61292581 |
