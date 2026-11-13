# MCY document-first map 2026-11-12 (read-only, bottom-up)

Evidence label: FILING-CHECKED unless a row says otherwise (R pages of the filing; tags from the R-page element references; API = SEC companyfacts, same accession, same period). Built with data-team/companies/reads/tools/docmap.py: status vocabulary mapped / combined / component sum / component_in_note / not_presented / OUT (Dhairya 2026-11-12). Every face miss is resolved against the whole filing (MetaLinks.json: every tag in the filing with the R pages, face and notes, that present it): stmt NOTE = found only outside the face statements; not_presented cites that whole-filing check.

## Filings opened
- 10-K 0000064996-26-000005 (CIK 0000064996, filed 2026-02-17): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0000064996-16-000036 (CIK 0000064996, filed FY2015 era): COVER R1.htm, BS R2.htm, BSP R3.htm, IS R4.htm, CF R6.htm
- 10-K 0000064996-24-000002 (CIK 0000064996, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- 10-K 0000064996-23-000004 (CIK 0000064996, era filing): COVER R1.htm, BS R3.htm, BSP R4.htm, IS R5.htm, CF R7.htm
- companyfacts CIK0000064996.json (one call); submissions CIK0000064996.json (SIC 6331).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | us-gaap:Revenues | R5.htm | Total revenues | 5992468000 | 5992468000 | 5475633000 | 5475633000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| cost_of_revenue | OUT | us-gaap:CostOfGoodsAndServicesSold | R51.htm | Cost of goods and services sold | 15200000 | 15200000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: mapped us-gaap:CostOfGoodsAndServicesSold 15200000 |
| gross_profit | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_expenses | mapped | us-gaap:BenefitsLossesAndExpenses | R5.htm | Total expenses | 5328819000 | 5328819000 | 4900753000 | 4900753000 | Y | FILING-CHECKED | check: machine-full-filing / printed total opex line; no cost-of-revenue line above it / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| sga_expense | combined | us-gaap:OtherCostAndExpenseOperating | R5.htm | Other operating expenses | 394226000 |  |  |  |  | FILING-CHECKED | check: hand / The insurer reports no SG&A line; general and administrative costs sit inside 'Other operating expenses' ($394,226K), beside policy acquisition costs, and R112's parent-only figures are excluded. / pages opened: R5, R108, R112, R17, R19, R27 |
| research_and_development | OUT |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| operating_income | not_presented |  | R5.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / Insurance-format income statement goes from total revenues and total expenses straight to income before income taxes; no operating income subtotal. / pages opened: R5, R26, R50, R74, R108, R109 |
| interest_expense | mapped | us-gaap:InterestExpenseOperating | R5.htm | Interest | 28623000 | 28623000 | 30824000 | 30824000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| income_before_tax | mapped | us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | R5.htm | Income before income taxes | 663649000 | 663649000 | 574880000 | 574880000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| income_tax_expense | mapped | us-gaap:IncomeTaxExpenseBenefit | R5.htm | Income tax expense | 122555000 | 122555000 | 106927000 | 106927000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| net_income | mapped | us-gaap:NetIncomeLoss | R5.htm | Net income | 541094000 | 541094000 | 467953000 | 467953000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| basic_eps | mapped | us-gaap:EarningsPerShareBasic | R5.htm | Basic (in dollars per share) | 9.77 | 9.77 | 8.45 | 8.45 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| diluted_eps | mapped | us-gaap:EarningsPerShareDiluted | R5.htm | Diluted (in dollars per share) | 9.77 | 9.77 | 8.45 | 8.45 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R5.htm period ..2025-12-31 |
| weighted_basic_shares | mapped | us-gaap:WeightedAverageNumberOfSharesOutstandingBasic | R105.htm | Weighted shares, basic (in shares) | 55389000 | 55389000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R105.htm 'Earnings (Loss) Per Share - Reconciliation (Details)' (MetaLinks.json presentation) |
| weighted_diluted_shares | mapped | us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding | R105.htm | Weighted shares, diluted (in shares) | 55389000 | 55389000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R105.htm 'Earnings (Loss) Per Share - Reconciliation (Details)' (MetaLinks.json presentation) |
| cash_and_equivalents | mapped | us-gaap:Cash | R3.htm | Cash | 1315574000 | 1315574000 | 720257000 | 720257000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| accounts_receivable | mapped | us-gaap:PremiumsReceivableAtCarryingValue | R3.htm | Premiums receivable, net of allowance for credit losses | 745554000 |  |  |  |  | FILING-CHECKED | check: hand / The insurer's customer receivable is premiums receivable, net ($745,554K at 2025-12-31); total receivables ($905,066K) also hold accrued investment income and other items, and R111's $432K is parent-only. / pages opened: R3, R7, R33, R51, R54, R55 |
| inventory | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| current_assets | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| ppe_net | mapped | us-gaap:PropertyPlantAndEquipmentNet | R3.htm | Fixed assets, net | 146880000 | 146880000 | 138177000 | 138177000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| goodwill | mapped | us-gaap:Goodwill | R3.htm | Goodwill | 42796000 | 42796000 | 42796000 | 42796000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| total_assets | mapped | us-gaap:Assets | R3.htm | Total assets | 9560669000 | 9560669000 | 8310632000 | 8310632000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| accounts_payable | mapped | us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | R3.htm | Accounts payable and accrued expenses | 448703000 | 448703000 | 417765000 | 417765000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| current_liabilities | OUT |  | R3.htm |  |  |  |  |  |  | FILING-CHECKED | check: machine-full-filing / OUT: outside the insurer template (SIC 6331; Dhairya OUT ruling main @020ebb29); was: not_presented |
| total_liabilities | mapped | us-gaap:Liabilities | R3.htm | Total liabilities | 7143394000 | 7143394000 | 6364108000 | 6364108000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| stockholders_equity | mapped | us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | R3.htm | Total shareholders’ equity | 2417275000 | 2417275000 | 1946524000 | 1946524000 | Y | FILING-CHECKED | check: machine-full-filing / matched by printed label (tag outside the usual set) / accn 0000064996-26-000005 R3.htm period ..2025-12-31 |
| cfo | mapped | us-gaap:NetCashProvidedByUsedInOperatingActivities | R7.htm | Net cash provided by operating activities | 1087188000 | 1087188000 | 1037117000 | 1037117000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| cash_flow_investing | mapped | us-gaap:NetCashProvidedByUsedInInvestingActivities | R7.htm | Net cash used in investing activities | -420156000 | -420156000 | -796656000 | -796656000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| cash_flow_financing | mapped | us-gaap:NetCashProvidedByUsedInFinancingActivities | R7.htm | Net cash (used in) provided by financing activities | -71715000 | -71715000 | -71107000 | -71107000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| capex | mapped | us-gaap:PaymentsToAcquireProductiveAssets | R7.htm | Purchases of fixed assets | -58431000 | 58431000 | -46138000 | 46138000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| depreciation_and_amortization | combined | us-gaap:DepreciationAmortizationAndAccretionNet | R7.htm | Depreciation and amortization | 74989000 | 74989000 | 73433000 | 73433000 | Y | FILING-CHECKED | check: machine-full-filing / D&A line includes accretion: combined (Dhairya 2026-11-12) / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| sbc | mapped | us-gaap:AllocatedShareBasedCompensationExpense | R99.htm | Compensation cost, all share-based awards | 14633000 | 14633000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R99.htm 'Share-Based Compensation - Narrative (Details)' (MetaLinks.json presentation) |
| dividends_paid | mapped | us-gaap:PaymentsOfDividendsCommonStock | R7.htm | Dividends paid to shareholders | -70343000 | 70343000 | -70326000 | 70326000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| share_buybacks | not_presented |  | R7.htm |  |  |  |  |  |  | FILING-CHECKED | check: hand / No repurchases in the equity or cash flow statements; shares issued and outstanding are unchanged at 55,389K. / pages opened: R3, R4, R6, R7, R56, R64, R111 |
| cash_paid_for_interest | mapped | us-gaap:InterestPaidNet | R7.htm | Interest paid | 28161000 | 28161000 | 30077000 | 30077000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| cash_paid_for_income_taxes | mapped | us-gaap:IncomeTaxesPaidNet | R7.htm | Total income taxes paid, net | 97320000 | 97320000 | 94935000 | 94935000 | Y | FILING-CHECKED | check: machine-full-filing / accn 0000064996-26-000005 R7.htm period ..2025-12-31 |
| total_debt | mapped | us-gaap:LongTermDebt | R76.htm | Total | 575000000 | 575000000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / not on the face statement; shown in R76.htm 'Notes Payable - Schedule of Maturities of Debt (Details)' (MetaLinks.json presentation) |
| shares_outstanding | mapped | us-gaap:CommonStockSharesOutstanding | R4.htm | Common stock, shares outstanding (in shares) | 55389000 | 55389000 |  |  | Y | FILING-CHECKED | check: machine-full-filing / balance-sheet date 2025-12-31; single row |

## Era coverage FY2015 to latest (runs from companyfacts; FY2015 10-K opened)
- revenue: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Total revenues' on us-gaap:Revenues = 3009300000 (FILING-CHECKED)
- cost_of_revenue: FY2015 10-K 0000064996-16-000036 R4.htm read; no row matched (auto)
- operating_expenses: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Total expenses' on us-gaap:BenefitsLossesAndExpenses = 2938733000 (FILING-CHECKED)
- interest_expense: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Interest' on us-gaap:InterestExpense = 3168000 (FILING-CHECKED)
- income_before_tax: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = 70567000 (FILING-CHECKED)
- income_tax_expense: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Income tax (benefit) expense' on us-gaap:IncomeTaxExpenseBenefit = -3912000 (FILING-CHECKED)
- net_income: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Net income' on us-gaap:NetIncomeLoss = 74479000 (FILING-CHECKED)
- basic_eps: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Basic (in dollars per share)' on us-gaap:EarningsPerShareBasic = 1.35 (FILING-CHECKED)
- diluted_eps: FY2015 10-K 0000064996-16-000036 R4.htm prints 'Diluted (in dollars per share)' on us-gaap:EarningsPerShareDiluted = 1.35 (FILING-CHECKED)
- weighted_basic_shares: FY2015 10-K 0000064996-16-000036 R4.htm read; no row matched (auto)
- weighted_diluted_shares: FY2015 10-K 0000064996-16-000036 R4.htm read; no row matched (auto)
- cash_and_equivalents: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Cash' on us-gaap:Cash = 264221000 (FILING-CHECKED)
- ppe_net: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Fixed assets, net' on us-gaap:PropertyPlantAndEquipmentNet = 157131000 (FILING-CHECKED)
- goodwill: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Goodwill' on us-gaap:Goodwill = 42796000 (FILING-CHECKED)
- total_assets: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Total assets' on us-gaap:Assets = 4628645000 (FILING-CHECKED)
- accounts_payable: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Accounts payable and accrued expenses' on us-gaap:AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent = 122571000 (FILING-CHECKED)
- total_liabilities: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Total liabilities' on us-gaap:Liabilities = 2807760000 (FILING-CHECKED)
- stockholders_equity: FY2015 10-K 0000064996-16-000036 R2.htm prints 'Total shareholders’ equity' on us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = 1820885000 (FILING-CHECKED)
- cfo: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Net cash provided by operating activities' on us-gaap:NetCashProvidedByUsedInOperatingActivities = 190244000 (FILING-CHECKED)
- cash_flow_investing: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Net cash used in investing activities' on us-gaap:NetCashProvidedByUsedInInvestingActivities = -81682000 (FILING-CHECKED)
- cash_flow_financing: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Net cash used in financing activities' on us-gaap:NetCashProvidedByUsedInFinancingActivities = -134248000 (FILING-CHECKED)
- capex: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Purchase of fixed assets' on us-gaap:PaymentsToAcquireProductiveAssets = -20112000 (FILING-CHECKED)
- depreciation_and_amortization: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Depreciation and amortization' on us-gaap:DepreciationAmortizationAndAccretionNet = 26478000 (FILING-CHECKED)
- sbc: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Share-based compensation' on us-gaap:ShareBasedCompensation = -5208000 (FILING-CHECKED)
- dividends_paid: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Dividends paid to shareholders' on us-gaap:PaymentsOfDividendsCommonStock = -136386000 (FILING-CHECKED)
- cash_paid_for_interest: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Interest paid' on us-gaap:InterestPaid = 2989000 (FILING-CHECKED)
- cash_paid_for_income_taxes: FY2015 10-K 0000064996-16-000036 R6.htm prints 'Income taxes paid' on us-gaap:IncomeTaxesPaid = 31390000 (FILING-CHECKED)
- interest_expense: era 10-K 0000064996-24-000002 R5.htm prints 'Interest' on us-gaap:InterestExpense = 24169000 (FILING-CHECKED)
- income_before_tax: era 10-K 0000064996-23-000004 R5.htm prints '(Loss) income before income taxes' on us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments = -670715000 (FILING-CHECKED)

## Mismatches (printed vs API)
none beyond sign differences
