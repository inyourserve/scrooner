# EQIX document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001101239-26-000032 (CIK 0001101239, filed 2026-02-11): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R9.htm
- 10-K 0001628280-16-011802 (CIK 0001101239, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001628280-21-002563 (CIK 0001101239, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R9.htm
- 10-K 0001628280-24-005350 (CIK 0001101239, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R10.htm
- companyfacts CIK0001101239.json (one call).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Revenues | 9217000000 | 9217000000 | 8748000000 | 8748000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| cost_of_revenue | mapped | us-gaap:CostOfRevenue | R5.htm | Cost of revenues | 4508000000 | 4508000000 | 4467000000 | 4467000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| gross_profit | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of GrossProfit in MetaLinks.json (1265 tags across all 133 R pages, face and notes) of 0001101239-26-000032; no face row matched |
| operating_expenses | combined | us-gaap:CostsAndExpenses | R5.htm | Total costs and operating expenses | 7369000000 | 7369000000 | 7420000000 | 7420000000 | Y | FILING-CHECKED | CostsAndExpenses (total costs and expenses) includes cost of revenue: combined, never opex / accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| sga_expense | mapped | us-gaap:GeneralAndAdministrativeExpense | R5.htm | General and administrative | 1840000000 | 1840000000 | 1766000000 | 1766000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| research_and_development | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of ResearchAndDevelopmentExpense, ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost in MetaLinks.json (1265 tags across all 133 R pages, face and notes) of 0001101239-26-000032; no face row matched |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 1848000000 | 1848000000 | 1328000000 | 1328000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -527000000 | 527000000 | -457000000 | 457000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 1508000000 | 1508000000 | 975000000 | 975000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | -160000000 | 160000000 | -161000000 | 161000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income attributable to common stockholders | 1350000000 | 1350000000 | 815000000 | 815000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic EPS (in dollars per share) | 13.79 | 13.79 | 8.54 | 8.54 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted EPS (in dollars per share) | 13.76 | 13.76 | 8.5 | 8.5 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Weighted-average shares used to calculate basic EPS (in shares) | 97883000 | 97883000 | 95457000 | 95457000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Weighted-average shares used to calculate diluted EPS (in shares) | 98123000 | 98123000 | 95827000 | 95827000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R5.htm period ..2025-12-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 1727000000 | 1727000000 | 3081000000 | 3081000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Accounts receivable, net of allowance of $16 and $19 | 1001000000 | 1001000000 | 949000000 | 949000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (1265 tags across all 133 R pages, face and notes) of 0001101239-26-000032; no face row matched |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 5125000000 | 5125000000 | 5447000000 | 5447000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property, plant and equipment, net | 23584000000 | 23584000000 | 19249000000 | 19249000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 5984000000 | 5984000000 | 5504000000 | 5504000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 40141000000 | 40141000000 | 35085000000 | 35085000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent | R3.htm | Accounts payable and accrued expenses | 1350000000 | 1350000000 | 1193000000 | 1193000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 3893000000 | 3893000000 | 3349000000 | 3349000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 25963000000 | 25963000000 | 21533000000 | 21533000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total common stockholders' equity | 14156000000 | 14156000000 | 13528000000 | 13528000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R9.htm | Net cash provided by operating activities | 3911000000 | 3911000000 | 3249000000 | 3249000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R9.htm | Net cash used in investing activities | -6484000000 | -6484000000 | -3937000000 | -3937000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R9.htm | Net cash provided by financing activities | 1272000000 | 1272000000 | 1723000000 | 1723000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R128.htm | Segment Information - Schedule of Segment Disclosures (Details) |  | 4311000000 |  |  |  | FILING-CHECKED | not on the face statement; shown in R128.htm 'Segment Information - Schedule of Segment Disclosures (Details)' (MetaLinks.json presentation); value from companyfacts same accession |
| depreciation_and_amortization | mapped | us-gaap:DepreciationAmortizationAndAccretionNet | R9.htm | Depreciation, amortization and accretion | 2066000000 | 2066000000 | 2011000000 | 2011000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R9.htm | Stock-based compensation | 498000000 | 498000000 | 462000000 | 462000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| dividends_paid | mapped | us-gaap:PaymentsOfDividends | R9.htm | Payment of dividends | -1856000000 | 1856000000 | -1643000000 | 1643000000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R9.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsForRepurchaseOfCommonStock in MetaLinks.json (1265 tags across all 133 R pages, face and notes) of 0001101239-26-000032; no face row matched |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidCapitalized | R9.htm | Cash paid for interest, net of amounts capitalized | 448000000 | 448000000 | 486000000 | 486000000 | Y | FILING-CHECKED | matched by printed label (tag outside the usual set) / accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaid | R9.htm | Cash paid for taxes, net | 207000000 | 207000000 | 185000000 | 185000000 | Y | FILING-CHECKED | accn 0001101239-26-000032 R9.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R90.htm | Debt Facilities - Narrative (Details) |  |  |  |  |  | FILING-CHECKED | not on the face statement; shown in R90.htm 'Debt Facilities - Narrative (Details)' (MetaLinks.json presentation); value from companyfacts same accession (no undimensioned companyfacts fact: read the R page) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 98226000 | 98226000 |  |  | Y | FILING-CHECKED | balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Revenues' on us-gaap:Revenues = 2725867000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Cost of revenues' on us-gaap:CostOfRevenue = 1291506000 (FILING-CHECKED)
- operating_expenses: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Total costs and operating expenses' on us-gaap:CostsAndExpenses = 2158525000 (FILING-CHECKED)
- sga_expense: FY2015 10-K 0001628280-16-011802 R4.htm prints 'General and administrative' on us-gaap:GeneralAndAdministrativeExpense = 493284000 (FILING-CHECKED)
- operating_income: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Income from operations' on us-gaap:OperatingIncomeLoss = 567342000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Interest expense' on us-gaap:InterestExpense = -299055000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Income from operations before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest = 210998000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Income tax expense' on us-gaap:IncomeTaxExpenseBenefit = -23224000 (FILING-CHECKED)
- net_income: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Net income (loss) attributable to Equinix' on us-gaap:NetIncomeLoss = 187774000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Basic EPS (in dollars per share)' on us-gaap:EarningsPerShareBasic = 3.25 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Diluted EPS (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 3.21 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Weighted-average shares' on us-gaap:WeightedAverageNumberOfSharesOutstandingBasic = 57790000 (FILING-CHECKED)
- weighted_diluted_shares: FY2015 10-K 0001628280-16-011802 R4.htm prints 'Weighted-average shares' on us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding = 58483000 (FILING-CHECKED)
- cash_and_equivalents: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Cash and cash equivalents' on us-gaap:CashAndCashEquivalentsAtCarryingValue = 2228838000 (FILING-CHECKED)
- accounts_receivable: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Accounts receivable, net of allowance for doubtful accounts of $10,352 and $9,46' on us-gaap:AccountsReceivableNetCurrent = 291964000 (FILING-CHECKED)
- current_assets: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Total current assets' on us-gaap:AssetsCurrent = 3259280000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Property, plant and equipment, net' on us-gaap:PropertyPlantAndEquipmentNet = 5606436000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 1063200000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Total assets' on us-gaap:Assets = 10356695000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent = 400948000 (FILING-CHECKED)
- current_liabilities: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Total current liabilities' on us-gaap:LiabilitiesCurrent = 1656354000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 7611309000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0001628280-16-011802 R2.htm prints 'Total stockholders' equity' on us-gaap:StockholdersEquity = 2745386000 (FILING-CHECKED)
- cfo: FY2015 10-K 0001628280-16-011802 R7.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 894793000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0001628280-16-011802 R7.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -1134927000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0001628280-16-011802 R7.htm prints 'Net cash provided by financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = 1873182000 (FILING-CHECKED)
- capex: FY2015 10-K 0001628280-16-011802 R7.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001628280-16-011802 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001628280-16-011802 R7.htm prints 'Stock-based compensation' on us-gaap:ShareBasedCompensation = 132443000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0001628280-16-011802 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001628280-16-011802 R7.htm prints 'Cash paid for interest' on us-gaap:InterestPaid = 237410000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-16-011802 R7.htm prints 'Cash paid for taxes' on us-gaap:IncomeTaxesPaid = 132302000 (FILING-CHECKED)
- revenue: era 10-K 0001628280-21-002563 R4.htm prints 'Revenues' on us-gaap:Revenues = 5998545000 (FILING-CHECKED)
- interest_expense: era 10-K 0001628280-24-005350 R5.htm prints 'Interest expense' on us-gaap:InterestExpense = -402022000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences

## Hand checks 2026-11-12 (Ritwik cloud)
- gross_profit: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- operating_expenses: component sum us-gaap:SellingAndMarketingExpense+us-gaap:GeneralAndAdministrativeExpense+us-gaap:RestructuringCharges+us-gaap:BusinessCombinationAcquisitionRelatedCosts+us-gaap:AssetImpairmentCharges+us-gaap:GainLossOnDispositionOfAssets1 (R5.htm): 2026-11-12 R5.htm: corrected: 903 + 1,840 + 33 + 18 + 68 - 1 = 2,861 = 9,217 - 4,508 - 1,848 (FY2024 2,953 ties)
- research_and_development: not_presented  (R5.htm): 2026-11-12 R5.htm: agree: whole-filing check agrees; nothing printed
- inventory: not_presented  (R3.htm): 2026-11-12 R3.htm: agree: whole-filing check agrees; nothing printed
- capex: mapped us-gaap:PaymentsToAcquireOtherPropertyPlantAndEquipment (R9.htm): 2026-11-12 R9.htm: corrected: the capex line is printed on the CF face (R9), not only in the segment note
- share_buybacks: not_presented  (R9.htm): 2026-11-12 R9.htm: agree: whole-filing check agrees; nothing printed
- total_debt: component sum us-gaap:FinanceLeaseLiabilityCurrent+us-gaap:LoansPayableCurrent+us-gaap:SeniorNotesCurrent+us-gaap:FinanceLeaseLiabilityNoncurrent+us-gaap:LongTermLoansPayable+us-gaap:SeniorLongTermNotes (R3.htm): 2026-11-12 R3.htm: corrected: every printed BS debt line incl. finance leases (operating leases excluded): 168 + 17 + 1,299 + 2,187 + 686 + 16,910; the tool's NOTE row had no value
- interest_expense: mapped us-gaap:InterestExpenseNonoperating (R5.htm): 2026-11-12 R5.htm: 20% mapped sample: IS R5.htm 'Interest expense' is the interest_expense line, printed -527000000 = filing XBRL 527000000; agrees
- current_assets: mapped us-gaap:AssetsCurrent (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total current assets' is the current_assets line, printed 5125000000 = filing XBRL 5125000000; agrees
- ppe_net: mapped us-gaap:PropertyPlantAndEquipmentNet (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Property, plant and equipment, net' is the ppe_net line, printed 23584000000 = filing XBRL 23584000000; agrees
- goodwill: mapped us-gaap:Goodwill (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Goodwill' is the goodwill line, printed 5984000000 = filing XBRL 5984000000; agrees
- stockholders_equity: mapped us-gaap:StockholdersEquity (R3.htm): 2026-11-12 R3.htm: 20% mapped sample: BS R3.htm 'Total common stockholders' equity' is the stockholders_equity line, printed 14156000000 = filing XBRL 14156000000; agrees
- dividends_paid: mapped us-gaap:PaymentsOfDividends (R9.htm): 2026-11-12 R9.htm: 20% mapped sample: CF R9.htm 'Payment of dividends' is the dividends_paid line, printed -1856000000 = filing XBRL 1856000000; agrees
