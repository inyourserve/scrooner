# AHR document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-082692 (CIK 0001632970, filed 2026-02-27): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001632970-16-000070 (CIK 0001632970, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, CF R5.htm
- 10-K 0001632970-21-000028 (CIK 0001632970, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- 10-K 0001632970-17-000022 (CIK 0001632970, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R7.htm
- companyfacts CIK0001632970.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R4.htm | Resident fees and services | 2094506000 | 2094506000 | 1883798000 | 1883798000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R4.htm | Property operating expenses | 1793531000 | 1793531000 | 1653893000 | 1653893000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1509 tags across all 98 R pages, face and notes) of 0001193125-26-082692; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R4.htm | Total expenses | 2096360000 | 2096360000 | 1941024000 | 1941024000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R4.htm | General and administrative | 58735000 | 58735000 | 47559000 | 47559000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R4.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1509 tags across all 98 R pages, face and notes) of 0001193125-26-082692; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R90.htm | Segment Reporting - Summary Information for Reportable Segments (Details) |  | 415160000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Segment Reporting - Summary Information for Reportable Segments (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| interest_expense | mapped | us-gaap:InterestExpense | R4.htm | Interest expense, net | -85775000 | 85775000 | -127730000 | 127730000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R4.htm | Income (loss) before income taxes | 48647000 | 48647000 | -33887000 | -33887000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R4.htm | Income tax benefit (expense) | 22171000 | -22171000 | -1713000 | 1713000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R4.htm | Net income (loss) attributable to controlling interest | 69806000 | 69806000 | -37812000 | -37812000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R4.htm | Net income (loss) per share of Common Stock, Class T common stock and Class I common stock attributable to controlling i | 0.42 | 0.42 | -0.29 | -0.29 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R4.htm | Net income (loss) per share of Common Stock, Class T common stock and Class I common stock attributable to controlling i | 0.42 | 0.42 | -0.29 | -0.29 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R4.htm | Weighted average number of shares of Common Stock, Class T common stock and Class I common stock outstanding — basic (in | 166055466 | 166055466 | 130637539 | 130637539 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R4.htm | Weighted average number of shares of Common Stock, Class T common stock and Class I common stock outstanding — diluted ( | 166849603 | 166849603 | 130637539 | 130637539 | Y | FILING-CHECKED | accn 0001193125-26-082692 R4.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R2.htm | Cash and cash equivalents | 114836000 | 114836000 | 76702000 | 76702000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNet | R2.htm | Accounts and other receivables, net | 204313000 | 204313000 | 211104000 | 211104000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| inventory | mapped | us-gaap:InventoryNet | R61.htm | Other Assets - Other Assets, Net (Details) |  | 18838000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R61.htm 'Other Assets - Other Assets, Net (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| current_assets | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (1509 tags across all 98 R pages, face and notes) of 0001193125-26-082692; no face row matched |
| ppe_net | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PropertyPlantAndEquipmentNet, PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization, PublicUtilitiesPropertyPlantAndEquipmentNet in MetaLinks.json (1509 tags across all 98 R pages, face and notes) of 0001193125-26-082692; no face row matched |
| goodwill | mapped | us-gaap:Goodwill | R2.htm | Goodwill | 234942000 | 234942000 | 234942000 | 234942000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R2.htm | Total assets | 5426226000 | 5426226000 | 4488057000 | 4488057000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R2.htm | Accounts payable and accrued liabilities | 317742000 | 317742000 | 258324000 | 258324000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| current_liabilities | not_presented |  | R2.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (1509 tags across all 98 R pages, face and notes) of 0001193125-26-082692; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R2.htm | Total liabilities | 2065611000 | 2065611000 | 2183895000 | 2183895000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R2.htm | Total stockholders’ equity | 3320638000 | 3320638000 | 2261231000 | 2261231000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R2.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 294441000 | 294441000 | 176087000 | 176087000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash (used in) provided by investing activities | -1083292000 | -1083292000 | -8734000 | -8734000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash provided by (used in) financing activities | 817241000 | 817241000 | -134743000 | -134743000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| capex | mapped | ahr:PaymentsToDevelopRealEstateAssetsAndPaymentsForCapitalExpenditures | R7.htm | Developments and capital expenditures | -128562000 |  | -91940000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R7.htm | Depreciation and amortization | 187559000 | 187559000 | 179192000 | 179192000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R7.htm | Stock based compensation | 14621000 | 14621000 | 9870000 | 9870000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Distributions paid | -163522000 | 163522000 | -120895000 | 120895000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R7.htm | Repurchase of common stock | 0 | 0 | -14000 | 14000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Cash paid for: Interest | 80111000 | 80111000 | 116285000 | 116285000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R7.htm | Cash paid for: Income taxes | 1799000 | 1799000 | 1320000 | 1320000 | Y | FILING-CHECKED | accn 0001193125-26-082692 R7.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R66.htm | Lines of Credit and Term Loan (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R66.htm 'Lines of Credit and Term Loan (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R3.htm | Common stock, shares outstanding | 185911442 |  |  |  | API missing | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: 10-K 0001632970-16-000070 statement not identified (auto)
- cost_of_revenue: 10-K 0001632970-16-000070 statement not identified (auto)
- operating_expenses: 10-K 0001632970-16-000070 statement not identified (auto)
- sga_expense: 10-K 0001632970-16-000070 statement not identified (auto)
- operating_income: 10-K 0001632970-16-000070 statement not identified (auto)
- interest_expense: 10-K 0001632970-16-000070 statement not identified (auto)
- income_before_tax: 10-K 0001632970-16-000070 statement not identified (auto)
- income_tax_expense: 10-K 0001632970-16-000070 statement not identified (auto)
- net_income: 10-K 0001632970-16-000070 statement not identified (auto)
- basic_eps: 10-K 0001632970-16-000070 statement not identified (auto)
- diluted_eps: 10-K 0001632970-16-000070 statement not identified (auto)
- weighted_basic_shares: 10-K 0001632970-16-000070 statement not identified (auto)
- weighted_diluted_shares: 10-K 0001632970-16-000070 statement not identified (auto)
- cash_and_equivalents: FY2015 10-K 0001632970-16-000070 R2.htm prints 'Cash' on us-gaap:Cash = 202000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001632970-16-000070 R2.htm read; no row matched (auto)
- inventory: FY2015 10-K 0001632970-16-000070 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001632970-16-000070 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001632970-16-000070 R2.htm prints 'Total assets' on us-gaap:Assets = 202000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001632970-16-000070 R2.htm read; no row matched (auto)
- total_liabilities: FY2015 10-K 0001632970-16-000070 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001632970-16-000070 R2.htm prints 'Total stockholder's equity' on us-gaap:StockholdersEquity = 200000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- cash_flow_investing: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- cash_flow_financing: FY2015 10-K 0001632970-16-000070 R5.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities =  (FILING-CHECKED)
- capex: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001632970-16-000070 R5.htm read; no row matched (auto)
- basic_eps: era 10-K 0001632970-21-000028 R4.htm prints 'Net loss per Class T and Class I common share attributable to controlling intere' on us-gaap:EarningsPerShareBasicAndDiluted = -0.22 (FILING-CHECKED)
- diluted_eps: era 10-K 0001632970-21-000028 R4.htm prints 'Net loss per Class T and Class I common share attributable to controlling intere' on us-gaap:EarningsPerShareBasicAndDiluted = -0.22 (FILING-CHECKED)
- cash_and_equivalents: era 10-K 0001632970-17-000022 R2.htm prints 'Cash and cash equivalents' on us-gaap:Cash = 2237000 (FILING-CHECKED)

## Mismatches (printed vs API)
- capex: API missing (ahr:PaymentsToDevelopRealEstateAssetsAndPaymentsForCapitalExpenditures)
- shares_outstanding: API missing (us-gaap:CommonStockSharesOutstanding)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| gross_profit | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_expenses | combined | agree | page value 2096360000 vs printed 2096360000 |
| sga_expense | mapped-sample | agree | page value 58735000 vs printed 58735000 |
| research_and_development | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | NOTE | agree | page value 415160000 vs API 415160000 |
| interest_expense | combined | agree | page value -85775000 vs printed -85775000 |
| inventory | NOTE | agree | page value 18838000 vs API 18838000 |
| current_assets | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | not_presented | agree | none of the candidate elements in MetaLinks.json |
| current_liabilities | not_presented | agree | none of the candidate elements in MetaLinks.json |
| stockholders_equity | mapped-sample | agree | page value 3320638000 vs printed 3320638000 |
| cash_flow_financing | mapped-sample | agree | page value 817241000 vs printed 817241000 |
| total_debt | NOTE | agree | page value 583663000 vs printed 583663000 |
