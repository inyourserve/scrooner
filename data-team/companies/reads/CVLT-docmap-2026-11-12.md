# CVLT document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0001169561-26-000017 (CIK 0001169561, filed 2026-05-11): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CI R6.htm, CF R8.htm
- 10-K 0001628280-15-003946 (CIK 0001169561, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001169561-17-000014 (CIK 0001169561, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- 10-K 0001169561-18-000018 (CIK 0001169561, era filing): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CI R5.htm, CF R7.htm
- companyfacts CIK0001169561.json (one call); submissions CIK0001169561.json (SIC 7372).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax | R5.htm | Total revenues | 1183690000 | 1183690000 | 995619000 | 995619000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| cost_of_revenue | mapped | us-gaap:CostOfGoodsAndServicesSold | R5.htm | Total cost of revenues | 223120000 | 223120000 | 179035000 | 179035000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| gross_profit | mapped | us-gaap:GrossProfit | R5.htm | Gross margin | 960570000 | 960570000 | 816584000 | 816584000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| operating_expenses | mapped | us-gaap:OperatingExpenses | R5.htm | Total operating expenses | 886580000 | 886580000 | 742846000 | 742846000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line excludes cost of revenue (= GP - OI) / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| sga_expense | component sum | us-gaap:GeneralAndAdministrativeExpense+us-gaap:SellingAndMarketingExpense | R5.htm | General and administrative + Sales and marketing | 682410000 | 682410000 | 572492000 | 572492000 | Y | FILING-CHECKED | check: machine-full-filing / SG&A = G&A + printed selling/marketing line(s); never G&A alone (Dhairya 2026-11-12) / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| research_and_development | mapped | us-gaap:ResearchAndDevelopmentExpense | R5.htm | Research and development | 162213000 | 162213000 | 146286000 | 146286000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| operating_income | mapped | us-gaap:OperatingIncomeLoss | R5.htm | Income from operations | 73990000 | 73990000 | 73738000 | 73738000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| interest_expense | mapped | us-gaap:InterestExpenseNonoperating | R5.htm | Interest expense | -3795000 | 3795000 | -416000 | 416000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 92124000 | 92124000 | 81053000 | 81053000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense (benefit) | 21467000 | 21467000 | 4947000 | 4947000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 70657000 | 70657000 | 76106000 | 76106000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 1.61 | 1.61 | 1.74 | 1.74 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 1.58 | 1.58 | 1.68 | 1.68 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R5.htm | Basic (in shares) | 43976000 | 43976000 | 43850000 | 43850000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R5.htm | Diluted (in shares) | 44654000 | 44654000 | 45187000 | 45187000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R5.htm period ..2026-03-31 |
| cash_and_equivalents | mapped | us-gaap:CashAndCashEquivalentsAtCarryingValue | R3.htm | Cash and cash equivalents | 899987000 | 899987000 | 302103000 | 302103000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| accounts_receivable | mapped | us-gaap:AccountsReceivableNetCurrent | R3.htm | Trade accounts receivable, net | 330483000 | 330483000 | 251995000 | 251995000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| inventory | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of InventoryNet in MetaLinks.json (835 tags across all 91 R pages, face and notes) of 0001169561-26-000017; label search over every tag in the filing (custom included) found no candidate |
| current_assets | mapped | us-gaap:AssetsCurrent | R3.htm | Total current assets | 1286510000 | 1286510000 | 635057000 | 635057000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Property and equipment, net | 9750000 | 9750000 | 8294000 | 8294000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 209322000 | 209322000 | 185255000 | 185255000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 1886305000 | 1886305000 | 1118266000 | 1118266000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableCurrent | R3.htm | Accounts payable | 651000 | 651000 | 373000 | 373000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| current_liabilities | mapped | us-gaap:LiabilitiesCurrent | R3.htm | Total current liabilities | 658170000 | 658170000 | 555050000 | 555050000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| total_liabilities | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of Liabilities in MetaLinks.json (835 tags across all 91 R pages, face and notes) of 0001169561-26-000017; label search over every tag in the filing (custom included) found no candidate |
| stockholders_equity | mapped | us-gaap:StockholdersEquity | R3.htm | Total stockholders’ equity | 7494000 | 7494000 | 325122000 | 325122000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R3.htm period ..2026-03-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R8.htm | Net cash provided by operating activities | 244680000 | 244680000 | 207382000 | 207382000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R8.htm | Net cash used in investing activities | -5446000 | -5446000 | -70400000 | -70400000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R8.htm | Net cash provided by (used in) financing activities | 345301000 | 345301000 | -147818000 | -147818000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| capex | mapped | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment | R8.htm | Purchase of property and equipment | -7529000 | 7529000 | -3756000 | 3756000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| depreciation_and_amortization | mapped | us-gaap:DepreciationDepletionAndAmortization | R8.htm | Depreciation and amortization | 10348000 | 10348000 | 9072000 | 9072000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| sbc | mapped | us-gaap:ShareBasedCompensation | R8.htm | Noncash stock-based compensation | 123425000 | 123425000 | 113262000 | 113262000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| dividends_paid | not_presented |  | R8.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of PaymentsOfDividendsCommonStock, PaymentsOfDividends, PaymentsOfOrdinaryDividends, PaymentsOfCapitalDistribution in MetaLinks.json (835 tags across all 91 R pages, face and notes) of 0001169561-26-000017; label search over every tag in the filing (custom included) found no candidate |
| share_buybacks | mapped | us-gaap:PaymentsForRepurchaseOfCommonStock | R8.htm | Repurchase of common stock | -446106000 | 446106000 | -165015000 | 165015000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R89.htm | Interest paid | 665000 | 665000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R89.htm 'Debt - Additional Information (Details)' (MetaLinks.json presentation) |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R8.htm | Income taxes paid | 13612000 | 13612000 | 42185000 | 42185000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0001169561-26-000017 R8.htm period ..2026-03-31 |
| total_debt | not_presented |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | whole-filing check: none of LongTermDebt, DebtLongtermAndShorttermCombinedAmount, DebtInstrumentCarryingAmount, LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities, LongTermDebtNoncurrent, LongTermDebtCurrent, ShortTermBorrowings, CommercialPaper, SeniorNotes, NotesPayable, LinesOfCreditCurrent in MetaLinks.json (835 tags across all 91 R pages, face and notes) of 0001169561-26-000017; HAND REVIEW: 31 label candidate(s) incl. custom tags: us-gaap:AmortizationOfFinancingCosts 'Amortization of debt issuance costs / Amortization of debt i' R8,R89,R91; us-gaap:ConvertibleDebtFairValueDisclosures 'Fair value of the Notes / Convertible Debt, Fair Value Discl' R43; us-gaap:ConvertibleLongTermNotesPayable 'Convertible notes, net / Convertible Notes Payable, Noncurre' R3; us-gaap:DebtInstrumentBasisSpreadOnVariableRate1 'Basis spread on variable rate / Debt Instrument, Basis Sprea' R89; us-gaap:DebtInstrumentCarryingAmount 'Principal amount / Long-Term Debt, Gross / Amount, before un' R90; us-gaap:DebtInstrumentConvertibleConversionPrice1 'Conversion price (in dollars per share) / Debt Instrument, C' R89; us-gaap:DebtInstrumentConvertibleConversionRatio1 'Conversion ratio / Debt Instrument, Convertible, Conversion ' R89; us-gaap:DebtInstrumentConvertibleThresholdConsecutiveTradingDays1 'Threshold consecutive trading days / Debt Instrument, Conver' R89 |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 41255000 | 41255000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2026-03-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- cost_of_revenue: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- gross_profit: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- sga_expense: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- research_and_development: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- operating_income: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- interest_expense: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- income_before_tax: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- income_tax_expense: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- net_income: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- basic_eps: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- diluted_eps: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- weighted_basic_shares: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0001628280-15-003946 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- accounts_receivable: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- current_assets: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- ppe_net: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- goodwill: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- total_assets: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- accounts_payable: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- current_liabilities: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- stockholders_equity: FY2015 10-K 0001628280-15-003946 R2.htm read; no row matched (auto)
- cfo: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- cash_flow_investing: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- cash_flow_financing: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- capex: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- depreciation_and_amortization: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- sbc: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- share_buybacks: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- cash_paid_for_interest: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- cash_paid_for_income_taxes: FY2015 10-K 0001628280-15-003946 R7.htm read; no row matched (auto)
- revenue: era 10-K 0001169561-17-000014 R4.htm prints 'Total revenues' on us-gaap:Revenues = 650518000 (FILING-CHECKED)
- cost_of_revenue: era 10-K 0001169561-18-000018 R4.htm prints 'Total cost of revenues' on us-gaap:CostOfRevenue = 98152000 (FILING-CHECKED)
- income_before_tax: era 10-K 0001169561-18-000018 R4.htm prints 'Income (loss) before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -3500000 (FILING-CHECKED)
- cash_paid_for_interest: era 10-K 0001169561-18-000018 R7.htm prints 'Interest paid' on us-gaap:InterestPaid = 592000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
