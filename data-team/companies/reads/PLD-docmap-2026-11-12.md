# PLD document-first map 2026-11-12 (read-only, bottom-up; Ritwik cloud)

Evidence label: FILING-CHECKED unless a row says otherwise. The R pages of the filing were opened on sec.gov; the tags come from each R row's element reference. API = SEC companyfacts, undimensioned, same accession, same period. A machine pass picked the lines; the disagreements below were decided by reading the printed rows.

## Filings opened
- Latest 10-K 0001193125-26-051453 (CIK 0001045609, filed 2026-02-13, FY ended 2025-12-31). Statement pages: BS R2.htm, BSP R3.htm, CF R8.htm, CI R5.htm, COVER R1.htm, EQ R6.htm, EQP R7.htm, IS R4.htm.
- Era 10-K for interest_expense (InterestExpense, FY2023): 0000950170-24-014539: IS R4.htm 'Interest expense' printed -641332000 API 641332000 match Y (sign differs: printed in parentheses/negated label).
- Era 10-K for interest_expense (InterestCostsIncurred, FY2023): 0000950170-24-014539: tag not on the statement pages (note or dimensioned).
- companyfacts and submissions JSON (one call each).

## Data points
| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | evidence | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | mapped | Revenues | IS R4.htm | Total revenues | 8790127000 | 8790127000 | 8201610000 | 8201610000 | Y | FILING-CHECKED |  |
| cost_of_revenue | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED | no cost-of-revenue line |
| gross_profit | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_expenses | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sga_expense | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| research_and_development | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| operating_income | mapped | OperatingIncomeLoss | IS R4.htm | Operating income | 4357864000 | 4357864000 | 4415920000 | 4415920000 | Y | FILING-CHECKED |  |
| interest_expense | mapped | InterestExpenseNonoperating | IS R4.htm | Interest expense | -1002344000 | 1002344000 | -863932000 | 863932000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| interest_income | not_presented |  | IS R4.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| other_income_expense_net | combined | NonoperatingIncomeExpense | IS R4.htm | Total other income (expense) | -588548000 | -588548000 | -301042000 | -301042000 | Y | FILING-CHECKED |  |
| income_before_tax | mapped | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest | IS R4.htm | Earnings before income taxes | 3769316000 | 3769316000 | 4114878000 | 4114878000 | Y | FILING-CHECKED |  |
| income_tax_expense | mapped | IncomeTaxExpenseBenefit | IS R4.htm | Income tax expense | -204017000 | 204017000 | -166943000 | 166943000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED |  |
| net_income | mapped | NetIncomeLoss | IS R4.htm | Net earnings attributable to controlling interests | 3328231000 | 3328231000 | 3731635000 | 3731635000 | Y | FILING-CHECKED |  |
| basic_eps | mapped | EarningsPerShareBasic | IS R4.htm | Net earnings per share/unit attributable to common stockhold | 3.58 | 3.58 | 4.02 | 4.02 | Y | FILING-CHECKED |  |
| diluted_eps | mapped | EarningsPerShareDiluted | IS R4.htm | Net earnings per share/unit attributable to common stockhold | 3.56 | 3.56 | 4.01 | 4.01 | Y | FILING-CHECKED |  |
| weighted_basic_shares | mapped | WeightedAverageNumberOfSharesOutstandingBasic | IS R4.htm | Weighted average common shares/units outstanding - Basic | 928473000 | 928473000 | 926172000 | 926172000 | Y | FILING-CHECKED |  |
| weighted_diluted_shares | mapped | WeightedAverageNumberOfDilutedSharesOutstanding | IS R4.htm | Weighted average common shares/units outstanding - Diluted | 956832000 | 956832000 | 953590000 | 953590000 | Y | FILING-CHECKED |  |
| dividends_per_share | mapped | CommonStockDividendsPerShareCashPaid | EQP R7.htm | Dividends per common share | 4.04 | 4.04 | 3.84 | 3.84 | Y | FILING-CHECKED |  |
| comprehensive_income | mapped | ComprehensiveIncomeNetOfTax | CI R5.htm | Comprehensive income attributable to common unitholders | 2772170000 | 2772170000 | 4125621000 | 4125621000 | Y | FILING-CHECKED |  |
| cash_and_equivalents | mapped | CashAndCashEquivalentsAtCarryingValue | BS R2.htm | Cash and cash equivalents | 1145647000 | 1145647000 | 1318591000 | 1318591000 | Y | FILING-CHECKED |  |
| accounts_receivable | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| inventory | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| current_assets | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| ppe_net | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| goodwill | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| total_assets | mapped | Assets | BS R2.htm | Total assets | 98724256000 | 98724256000 | 95328909000 | 95328909000 | Y | FILING-CHECKED |  |
| accounts_payable | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| current_liabilities | not_presented |  | BS R2.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| total_liabilities | mapped | Liabilities | BS R2.htm | Total liabilities | 40970248000 | 40970248000 | 36712139000 | 36712139000 | Y | FILING-CHECKED |  |
| total_debt | component sum | LongTermDebt+LongTermDebt | BS R2.htm | Debt + Debt | 70074146000 | 70074146000 | 61758526000 | 61758526000 | Y | FILING-CHECKED (debt lines); perimeter DATA-INFERRED | BS debt lines (the one instant sum allowed); check for double counts |
| stockholders_equity | mapped | StockholdersEquity | BS R2.htm | Total Prologis, Inc. stockholders’ equity | 53193178000 | 53193178000 | 53951138000 | 53951138000 | Y | FILING-CHECKED |  |
| shares_outstanding | mapped | dei:EntityCommonStockSharesOutstanding | COVER R1.htm | Entity Common Stock, Shares Outstanding | 929559000 | 929559000 |  |  | Y | FILING-CHECKED |  |
| cfo | mapped | NetCashProvidedByUsedInOperatingActivities | CF R8.htm | Net cash provided by (used in) operating activities | 5008434000 | 5008434000 | 4912209000 | 4912209000 | Y | FILING-CHECKED |  |
| cash_flow_investing | mapped | NetCashProvidedByUsedInInvestingActivities | CF R8.htm | Net cash provided by (used in) investing activities | -3630447000 | -3630447000 | -3099057000 | -3099057000 | Y | FILING-CHECKED |  |
| cash_flow_financing | mapped | NetCashProvidedByUsedInFinancingActivities | CF R8.htm | Net cash provided by (used in) financing activities | -1563619000 | -1563619000 | -999957000 | -999957000 | Y | FILING-CHECKED |  |
| capex | component sum | pld:PaymentForPropertyImprovements+PaymentsForLeasingCostsCommissionsAndTenantImprovements+PaymentsToDevelopRealEstateAssets | CF R8.htm | Property improvements + Tenant improvements and lease commis | -327355 |  |  |  | no API fact (dimensioned or not in companyfacts for this accession) | FILING-CHECKED | REIT capex (rule 24, doc 02 line 114): property improvements 327,355 + tenant improvements and lease commissions 562,197 + real estate development 2,781,260 (R8); acquisitions excluded |
| depreciation_and_amortization | mapped | DepreciationAndAmortization | CF R8.htm | Depreciation and amortization | 2626028000 | 2626028000 | 2580519000 | 2580519000 | Y | FILING-CHECKED |  |
| amortization_of_intangibles | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| sbc | mapped | ShareBasedCompensation | CF R8.htm | Equity-based compensation awards | 185466000 | 185466000 | 231747000 | 231747000 | Y | FILING-CHECKED |  |
| dividends_paid | combined | PaymentsOfDividends | CF R8.htm | Dividends/distributions paid on common and preferred stock/u | -3764745000 | 3764745000 | -3570480000 | 3570480000 | Y (sign differs: printed in parentheses/negated label) | FILING-CHECKED | label mixes common with preferred/NCI/units |
| share_buybacks | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_ar_change | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_inventory_change | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cf_ap_change | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED |  |
| cash_paid_for_interest | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |
| cash_paid_for_income_taxes | not_presented |  | CF R8.htm |  |  |  |  |  |  | FILING-CHECKED | not on the statement pages read |

## Era checks (tag changes in the last ~5 years)
- interest_expense: chosen tag FY[2024, 2025]; ERA-CHECK others: {'InterestExpense': [2021, 2022, 2023], 'InterestCostsIncurred': [2021, 2022, 2023]}

## Disagreements with my file (companies-101-200-exceptions-2026-11-11.csv)
- PLD capex: file says (file)  (-); read says component sum pld:PaymentForPropertyImprovements+us-gaap:PaymentsForLeasingCostsCommissionsAndTenantImprovements+us-gaap:PaymentsToDevelopRealEstateAssets 'Property improvements + Tenant improvements and lease commis'. DECISION: FILE STANDS: R8 prints the three lines; the machine pass took only development

## Mismatches (printed vs API)
- none beyond sign differences
