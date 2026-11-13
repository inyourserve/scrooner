# Rules: dqc (GENERATED from rules/dqc.csv and exam/results/ledger.csv — do not edit by hand)

40 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## (any using AccountsAndOtherReceivablesNetCurrent)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-accountsandotherreceivablesnetcurrent | validation | all | `{"check_type":"non_negative","condition":"undimensioned AccountsAndOtherReceivablesNetCurrent >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using AccountsReceivableNetCurrent)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-accountsreceivablenetcurrent | validation | all | `{"check_type":"non_negative","condition":"undimensioned AccountsReceivableNetCurrent >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using Assets)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-assets | validation | all | `{"check_type":"non_negative","condition":"undimensioned Assets >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using CommonStockDividendsPerShareDeclared)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-commonstockdividendspersharedeclared | validation | all | `{"check_type":"non_negative","condition":"undimensioned CommonStockDividendsPerShareDeclared >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using Depreciation)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-depreciation | validation | all | `{"check_type":"non_negative","condition":"undimensioned Depreciation >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using DepreciationDepletionAndAmortization)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-depreciationdepletionandamortization | validation | all | `{"check_type":"non_negative","condition":"undimensioned DepreciationDepletionAndAmortization >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using Goodwill)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-goodwill | validation | all | `{"check_type":"non_negative","condition":"undimensioned Goodwill >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using IncomeTaxesPaid)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-incometaxespaid | validation | all | `{"check_type":"non_negative","condition":"undimensioned IncomeTaxesPaid >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using InterestPaid)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-interestpaid | validation | all | `{"check_type":"non_negative","condition":"undimensioned InterestPaid >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using InventoryNet)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-inventorynet | validation | all | `{"check_type":"non_negative","condition":"undimensioned InventoryNet >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using Liabilities)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-liabilities | validation | all | `{"check_type":"non_negative","condition":"undimensioned Liabilities >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using LongTermDebt)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-longtermdebt | validation | all | `{"check_type":"non_negative","condition":"undimensioned LongTermDebt >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using LongTermDebtNoncurrent)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-longtermdebtnoncurrent | validation | all | `{"check_type":"non_negative","condition":"undimensioned LongTermDebtNoncurrent >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using PaymentsToAcquirePropertyPlantAndEquipment)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-paymentstoacquirepropertyplantandequipment | validation | all | `{"check_type":"non_negative","condition":"undimensioned PaymentsToAcquirePropertyPlantAndEquipment >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using PropertyPlantAndEquipmentNet)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-propertyplantandequipmentnet | validation | all | `{"check_type":"non_negative","condition":"undimensioned PropertyPlantAndEquipmentNet >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## (any using ReceivablesNetCurrent)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc15-receivablesnetcurrent | validation | all | `{"check_type":"non_negative","condition":"undimensioned ReceivablesNetCurrent >= 0"}` | `{"on_fail":"sign error: serve abs(value), flag filer_sign_error"}` | DQC_0015 (list v1) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015. | 0 | 0 |  |

## accounts_receivable;interest_expense

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc230-01 | validation | all | `{"check_type":"structure","condition":"AccountsAndOtherReceivablesNetCurrent / InterestExpenseOther are \"other\"/wider concepts; an aggrega` | `{"on_fail":"never map the \"other\" concept as the data point alone; never add aggregate + other"}` | DQC.US.0230/0231/0228 (approved 2026-03-18) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/d | 0 | 0 |  |

## basic_eps;diluted_eps;weighted_basic_shares

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc227-01 | validation | all | `{"check_type":"ratio","condition":"EarningsPerShareBasic \u2248 NetIncomeLossAvailableToCommonStockholdersBasic / WeightedAverageNumberOfSha` | `{"on_fail":"flag; a \u00d71000 mismatch = share scaling error (scale override)"}` | DQC.US.0227 (approved, effective 2026-06-01) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/ | 0 | 0 |  |

## cash_and_equivalents

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc57-01 | validation | all | `{"check_type":"structure","condition":"CF opening/closing balance element: CashCashEquivalentsRestrictedCash\u2026 after ASU 2016-18, CashAn` | `{"on_fail":"the CF ending-cash source for bank/split cash follows the adoption era"}` | DQC_0057 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0057/DQC_0057.md | 0 | 0 |  |

## cash_paid_for_income_taxes

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.it-01 | validation | all | `{"check_type":"preference","condition":"use the undimensioned IncomeTaxesPaidNet fact from any location (face or note); never add IncomeTaxP` | `{"on_fail":"choose the total; flag a jurisdiction-only filing as component_sum candidate"}` | FASB Income Taxes TIG v1.0 2025-02 https://xbrl.fasb.org/impguidance/IT_TIG/incometaxes.pdf | 0 | 0 |  |

## cash_paid_for_interest

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc65-01 | validation | all | `{"check_type":"preference","condition":"if InterestPaidNet reported use it; InterestPaid only when InterestPaidNet absent; never sum"}` | `{"on_fail":"choose InterestPaidNet; flag filings with InterestPaid only (value includes capitalized ` | DQC_0065 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0065/DQC_0065.md | 0 | 0 |  |

## cfo;cash_flow_investing;cash_flow_financing

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-06 | validation | all | `{"check_type":"equality","condition":"NetCashProvidedByUsedIn{Operating,Investing,Financing}Activities = \u2026ContinuingOperations + CashPr` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

## comprehensive_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-07 | validation | all | `{"check_type":"equality","condition":"ComprehensiveIncome incl. NCI = ProfitLoss + OtherComprehensiveIncomeLossNetOfTax; = attributable to N` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

## depreciation_and_amortization;operating_expenses

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc206-01 | validation | all | `{"check_type":"structure","condition":"facts on DisaggregationOfIncomeStatementExpenseCaptionIdentifierAxis / IncomeStatementLocationAxis ar` | `{"on_fail":"never read them as company totals; use them to detect combined captions"}` | DQC_0206; FASB DISE TIG https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0206/DQC_ | 0 | 0 |  |

## dividends_per_share

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc180-01 | validation | all | `{"check_type":"preference","condition":"never DividendsPayableAmountPerShare (an instant) as period DPS; Declared first, CashPaid only when ` | `{"on_fail":"route to Declared/CashPaid; flag"}` | DQC_0180 (10147) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0180/DQC_0180.md | 0 | 0 |  |

## income_before_tax

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc119-01 | validation | all | `{"check_type":"structure","condition":"IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInves` | `{"on_fail":"prefer the total pretax line when equity income is printed below it"}` | DQC_0119 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0119/DQC_0119.md | 0 | 0 |  |

## income_before_tax;net_income

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc51-01 | validation | all | `{"check_type":"structure","condition":"IncomeLossIncludingPortionAttributableToNoncontrollingInterest, IncomeLossAttributableToParent, Incom` | `{"on_fail":"if a tax line sits under them they are used as AFTER-tax (Chubb/ORCL-type misuse): do no` | DQC_0051 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0051/DQC_0051.md | 0 | 0 |  |

## interest_expense

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.sec-neg-ie | validation | all | `{"check_type":"non_negative","condition":"gross InterestExpense / InterestExpenseNonoperating / InterestExpenseOperating / InterestExpenseDe` | `{"on_fail":"sign error: abs + flag (NOT net interest income)"}` | SEC staff observations 2011-12-13; DQC_0013/0014 https://www.sec.gov/structureddata/osd_staffobs_12-13-11.html | 0 | 0 |  |

## interest_expense;other_income_expense_net;operating_expenses

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc181-01 | validation | all | `{"check_type":"structure","condition":"InterestExpense/InterestExpenseOperating must not be calc children of NonoperatingIncomeExpense; Inte` | `{"on_fail":"flag the filer calc; resolve by caption + position"}` | DQC_0181 (10180-10182) https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0181/DQC_0 | 0 | 0 |  |

## operating_expenses

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dise-01 | validation | all | `{"check_type":"value_check","condition":"OperatingExpenses (like CostsAndExpenses) may include cost of goods sold: map only when it ties to ` | `{"on_fail":"combined when it includes COGS (Dhairya opex ruling)"}` | FASB DISE TIG (proposed 2025-07-21), Example 1 https://xbrl.fasb.org/impguidance/DISE_TIG/ | 0 | 0 |  |

## ppe_net

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc187-01 | validation | all | `{"check_type":"equality","condition":"PropertyPlantAndEquipmentGross = PropertyPlantAndEquipmentNet + AccumulatedDepreciationDepletionAndAmo` | `{"on_fail":"flag; never derive ppe_net"}` | DQC_0187 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0187/DQC_0187.md | 0 | 0 |  |

## revenue

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc67-01 | validation | all | `{"check_type":"mutual_exclusion","condition":"RevenueFromContractWithCustomer* not together with SalesRevenueNet / SalesRevenueGoodsNet / Sa` | `{"on_fail":"flag; era-transition filing"}` | DQC_0067 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0067/DQC_0067.md | 0 | 0 |  |

## revenue;cost_of_revenue

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc71-01 | validation | all | `{"check_type":"structure","condition":"RFCWC*/CostOfGoodsAndServicesSold on ProductOrServiceAxis with a single member and no total"}` | `{"on_fail":"treat the single member as the total line only if it is the face line; flag"}` | DQC_0071 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0071/DQC_0071.md | 0 | 0 |  |

## shares_outstanding

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc9-01 | validation | all | `{"check_type":"less_or_equal","condition":"CommonStockSharesOutstanding <= CommonStockSharesIssued <= CommonStockSharesAuthorized (same date` | `{"on_fail":"flag; an outstanding value above issued suggests the wrong fact (issued count) or scale"` | DQC_0009 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0009/DQC_0009.md | 0 | 0 |  |
| dqc.sec-shr-01 | validation | all | `{"check_type":"scale","condition":"dei:EntityCommonStockSharesOutstanding vs us-gaap:CommonStockSharesOutstanding ratio within 0.5-2 (dates ` | `{"on_fail":"flag a ~1000x ratio as scaling error; the cover count is never the value"}` | SEC staff reminder 2022-10-06 https://www.sec.gov/structureddata/announcement/osd-announcement-2210-dqreminder-entitycom | 0 | 0 |  |

## stockholders_equity

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-04 | validation | all | `{"check_type":"equality","condition":"StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest = StockholdersEquity + Minority` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

## total_assets

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-01 | validation | all | `{"check_type":"equality","condition":"Assets = LiabilitiesAndStockholdersEquity; tolerance: dcml rounding"}` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

## total_assets;current_assets

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-02 | validation | all | `{"check_type":"equality","condition":"Assets = AssetsCurrent + AssetsNoncurrent (when both printed); tolerance: dcml rounding"}` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

## total_liabilities;current_liabilities

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-03 | validation | all | `{"check_type":"equality","condition":"Liabilities = LiabilitiesCurrent + LiabilitiesNoncurrent (when both printed); tolerance: dcml rounding` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

## total_liabilities;stockholders_equity

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| dqc.dqc4-05 | validation | all | `{"check_type":"equality","condition":"LiabilitiesAndStockholdersEquity = equity incl. NCI + Liabilities + TemporaryEquityCarryingAmountInclu` | `{"on_fail":"hold the cell (identity failure); NEVER derive a missing instant from it"}` | DQC_0004 https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md | 0 | 0 |  |

