# BPOP document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001193125-26-085756 (CIK 0000763901, filed 2026-03-02): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R11.htm
- 10-K 0001193125-16-485443 (CIK 0000763901, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001193125-18-066922 (CIK 0000763901, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- companyfacts CIK0000763901.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Net fees | 155868000 |  | 151343000 |  | API missing | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| cost_of_revenue | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of CostOfRevenue, CostOfGoodsAndServicesSold, CostOfGoodsSold, CostOfServices in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| operating_expenses | mapped | us-gaap:NoninterestExpense | R5.htm | Total operating expenses | 1932266000 | 1932266000 | 1887637000 | 1887637000 | Y | FILING-CHECKED | printed total opex line; no cost-of-revenue line above it / accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| sga_expense | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of SellingGeneralAndAdministrativeExpense, GeneralAndAdministrativeExpense in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of OperatingIncomeLoss in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| interest_expense | mapped | us-gaap:InterestExpense | R5.htm | Total interest expense | 1241806000 | 1241806000 | 1390975000 | 1390975000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | R5.htm | Income before income tax | 1006793000 | 1006793000 | 796618000 | 796618000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax (benefit) expense | 173634000 | 173634000 | 182406000 | 182406000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net Income | 833159000 | 833159000 | 614212000 | 614212000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Net Income per Common Share - Basic | 12.31 | 12.31 | 8.56 | 8.56 | Y | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Net Income per Common Share - Diluted | 12.3 | 12.3 | 8.56 | 8.56 | Y | FILING-CHECKED | accn 0001193125-26-085756 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R195.htm | Net income per common share - Computation of net income (loss) per common share (Details) |  | 67586130 |  |  |  | FILING-CHECKED | not on the face statement; shown in R195.htm 'Net income per common share - Computation of net income (loss) per common share ' (MetaLinks.json presentation); value from companyfacts same accession |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R195.htm | Net income per common share - Computation of net income (loss) per common share (Details) |  | 67612847 |  |  |  | FILING-CHECKED | not on the face statement; shown in R195.htm 'Net income per common share - Computation of net income (loss) per common share ' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_and_equivalents | mapped | us-gaap:CashAndDueFromBanks | R3.htm | Cash and due from banks | 402755000 | 402755000 | 419638000 | 419638000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:InterestReceivable | R3.htm | Accrued income receivable | 300824000 | 300824000 | 263389000 | 263389000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| current_assets | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AssetsCurrent in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Premises and equipment, net | 685820000 | 685820000 | 601787000 | 601787000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 789954000 | 789954000 | 802954000 | 802954000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 75348267000 | 75348267000 | 73045383000 | 73045383000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| accounts_payable | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of AccountsPayableCurrent, AccountsPayableTradeCurrent, AccountsPayableAndAccruedLiabilitiesCurrent in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| current_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LiabilitiesCurrent in MetaLinks.json (2668 tags across all 226 R pages, face and notes) of 0001193125-26-085756; no face row matched |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 69099188000 | 69099188000 | 67432317000 | 67432317000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders' equity | 6249079000 | 6249079000 | 5613066000 | 5613066000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R11.htm | Net cash provided by operating activities | 878447000 | 878447000 | 674722000 | 674722000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R11.htm | Net cash used in investing activities | -1759445000 | -1759445000 | -1632474000 | -1632474000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R11.htm | Net cash provided by (used in) financing activities | 864581000 | 864581000 | 959583000 | 959583000 | Y | FILING-CHECKED | accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R11.htm | Acquisition of premises and equipment | -197460000 | 197460000 | -213412000 | 213412000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| depreciation_and_amortization | mapped | bpop:DepreciationNonproductionContinuedAndDiscontinuedOperations | R11.htm | Depreciation and amortization of premises and equipment | 53230000 |  | 57078000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| sbc | mapped | bpop:StockBasedCompensation | R11.htm | Share-based compensation | 26937000 |  | 19676000 |  | API missing | FILING-CHECKED | company extension tag, matched by printed label / accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R11.htm | Dividends paid | -197568000 | 197568000 | -180461000 | 180461000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| share_buybacks | mapped | us-gaap:IncreaseDecreaseInFederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchaseNet | R11.htm | Assets sold under agreements to repurchase | -15832000 | -15832000 | -36551000 | -36551000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001193125-26-085756 R11.htm period ..2025-12-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R214.htm | Supplemental disclosure on the consolidated statments of cash flows -  Non-cash activities (Details) |  | 1236290000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R214.htm 'Supplemental disclosure on the consolidated statments of cash flows -  Non-cash ' (MetaLinks.json presentation); value from companyfacts same accession |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R206.htm | Income taxes - Income taxes paid (net of refunds) (Details) |  | 204174000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R206.htm 'Income taxes - Income taxes paid (net of refunds) (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| total_debt | mapped | us-gaap:LongTermDebt | R138.htm | Borrowings - Notes payable (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R138.htm 'Borrowings - Notes payable (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common Stock Shares Outstanding | 65719385 | 65719385 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001193125-16-485443 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001193125-16-485443 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001193125-16-485443 R4.htm prints 'Total interest expense' on us-gaap:InterestExpense = 194031000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001193125-16-485443 R4.htm prints 'Income (loss) from continuing operations before income tax' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 398825000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001193125-16-485443 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -495172000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001193125-16-485443 R4.htm prints 'Net (Loss) Income' on us-gaap:NetIncomeLoss = 895344000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001193125-16-485443 R4.htm prints 'Net (Loss) Income per Common Share - Basic' on us-gaap:EarningsPerShareBasic = 8.66 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001193125-16-485443 R4.htm prints 'Net (Loss) Income per Common Share - Diluted' on us-gaap:EarningsPerShareDiluted = 8.65 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001193125-16-485443 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001193125-16-485443 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Cash And Due From Banks' on us-gaap:CashAndDueFromBanks = 363674000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Accrued income receivable' on us-gaap:InterestReceivable = 124234000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Premises and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 502611000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 626388000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Total assets' on us-gaap:Assets = 35769534000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 30664210000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001193125-16-485443 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 5105324000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 670135000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Net cash provided by investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = 238339000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -925895000 (FILING-CHECKED)
- capex: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Acquisition of premises and equipment' on us-gaap:PaymentsToAcquirePropertyPlantAndEquipment = -62656000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Depreciation and amortization of premises and equipment' on us-gaap:DepreciationNonproduction = 47474000 (FILING-CHECKED)
- sbc: FY2015 10-K 0001193125-16-485443 R9.htm read; no row matched (auto)
- dividends_paid: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Dividends paid' on us-gaap:PaymentsOfDividends = -19257000 (FILING-CHECKED)
- share_buybacks: FY2015 10-K 0001193125-16-485443 R9.htm prints 'Federal funds purchased and assets sold under agreements to repurchase' on us-gaap:IncreaseDecreaseInFederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchaseNet = -509512000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0001193125-16-485443 R9.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001193125-16-485443 R9.htm read; no row matched (auto)
- cash_paid_for_interest: era 10-K 0001193125-18-066922 R9.htm read; no row matched (auto)

## Mismatches (printed vs API)
- revenue: API missing (us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax)
- depreciation_and_amortization: API missing (bpop:DepreciationNonproductionContinuedAndDiscontinuedOperations)
- sbc: API missing (bpop:StockBasedCompensation)

## Check pass
Every row: check: machine-full-filing (shared docmap.py @558f2f15). Re-checked by a second script that re-opens the cited R page (or MetaLinks.json for not_presented): every not_presented, combined, component and NOTE row, plus a seeded random 10% of mapped rows (3). This is a scripted re-check, not a human hand check.

| data point | class | verdict | detail |
|---|---|---|---|
| sga_expense | not_presented | agree | none of the candidate elements in MetaLinks.json |
| operating_income | not_presented | agree | none of the candidate elements in MetaLinks.json |
| income_before_tax | mapped-sample | agree | page value 1006793000 vs printed 1006793000 |
| weighted_basic_shares | NOTE | agree | page value 67586130 vs API 67586130 |
| weighted_diluted_shares | NOTE | agree | page value 67612847 vs API 67612847 |
| accounts_receivable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| ppe_net | mapped-sample | agree | page value 685820000 vs printed 685820000 |
| accounts_payable | not_presented | agree | none of the candidate elements in MetaLinks.json |
| cash_paid_for_interest | NOTE | agree | page value 1236290000 vs API 1236290000 |
| cash_paid_for_income_taxes | NOTE | agree | page value 204174000 vs API 204174000 |
| total_debt | NOTE | agree | moved: the cited page had no 2025-12-31 value; LongTermDebt read off R225.htm (500706000) |
| shares_outstanding | mapped-sample | agree | page value 65719385 vs printed 65719385 |
