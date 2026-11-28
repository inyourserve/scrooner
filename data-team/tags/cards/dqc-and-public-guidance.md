# DQC rules, FASB implementation guides and SEC staff guidance (Tag Expert, read 2026-11-12)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Precedence (Dhairya 2026-11-12): where a DQC rule conflicts with a card, the DQC rule wins unless a filing proves the company follows another treatment. Sources were read in full from the public XBRL US repository (raw files under https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/), xbrl.fasb.org/impguidance/ and sec.gov/structureddata. Runnable checks derived from them: validations/dqc-checks.csv.

## 1. Rules that change or confirm our mapping

| Rule | Status, release | What it says (from the rule text) | Consequence for our cards / predictor |
|---|---|---|---|
| DQC_0065 Interest Paid Net (Operating) Not on Cash Flow | Final, 2017-10-04 | Indirect-method filers must report interest paid net of capitalized interest; InterestPaidNet is that element; InterestPaid includes capitalized interest | cash_paid_for_interest = InterestPaidNet; InterestPaid only when the net element is absent (interest.md §10) |
| DQC_0181 Interest Expense Operating and Nonoperating | Final, 2024-06-27 | 2024 taxonomy adds InterestExpenseNonoperating / InterestExpenseOperating; InterestExpense = both; neither InterestExpense nor InterestExpenseOperating under NonoperatingIncomeExpense; neither InterestExpense nor InterestExpenseNonoperating under InterestIncomeExpenseNet or OperatingExpenses | 2024+ tag switches are era changes; InterestExpenseOperating = bank / opex-block interest (interest.md §10) |
| DQC_0051 Before Tax Items | Final, 2017-10-04 | IncomeLossIncludingPortionAttributableToNoncontrollingInterest, IncomeLossAttributableToParent and IncomeLossFromContinuingOperationsBeforeIncomeTaxes…NoncontrollingInterest are BEFORE-tax items and must not have an income-tax descendant | confirms the "…before Tax" pretax rule (operating-income.md §10); an after-tax use of these tags is a filer error |
| DQC_0004 Element Values Are Equal | Final, 2015-11-19 | accounting identities: Assets = L&E; Assets = current + noncurrent; Liabilities = current + noncurrent; equity incl. NCI = parent + MinorityInterest; L&E = equity incl. NCI + Liabilities + temporary equity; cash-flow continuing + discontinued; comprehensive income identities | validation checks only (a failed identity = held cell); never used to DERIVE an instant (doc 02) |
| DQC_0009 Element A <= Element B | Final, 2015-11-19 | e.g. CommonStockSharesOutstanding <= CommonStockSharesIssued <= CommonStockSharesAuthorized | shares sanity check |
| DQC_0015 Negative Values (list v1) | Final, 2015-11-19 | most elements are positive; the list names elements that must not be negative (incl. DepreciationDepletionAndAmortization, Depreciation, IncomeTaxesPaid, InterestPaid, PaymentsToAcquirePropertyPlantAndEquipment, AccountsReceivableNetCurrent, ReceivablesNetCurrent, CommonStockDividendsPerShareDeclared); InterestExpense, CostOfRevenue, CostOfGoodsAndServicesSold were REMOVED from the list | a negative value on an active element is a filer sign error: take the absolute value and flag; InterestExpense/COGS need our own sign sanity check |
| DQC_0013 / DQC_0014 Negative values (with dependence / no dimensions) | Final, 2016-09-29 | "it is an error to change the value … to a negative solely because the value is shown in parenthesis (e.g. interest expense)" | sign comes from the element definition, never from the label or brackets |
| DQC_0067 Mutually Exclusive Elements | Final, 2018-10-10 | new-standard revenue elements (RevenueFromContractWithCustomer…) must not be used together with prior-standard ones (SalesRevenueNet etc.) | a filing mixing them = check, era detection |
| DQC_0071 Revenue/Cost Single Member | Final, 2018-10-10 | revenue/COGS used on ProductOrServiceAxis with a single member and no total = error | supports the member rule: face-line members with no total are summed only when each is its own face line (fsn-line-to-concept §W) |
| DQC_0119 Income Before Tax Equity Method | Final, 2021-09-29 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments must not include equity-method income | pretax-before-equity-method line is not total pretax when equity income is printed below it |
| DQC_0057 Cash Flow Opening and Closing Balances | Final, 2017-10-04 | after ASU 2016-18 the CF opening/closing balance is CashCashEquivalentsRestrictedCash… (or …IncludingDisposalGroup…); before, CashAndCashEquivalentsAtCarryingValue(IncludingDiscontinuedOperations) | the CF printed ending cash used for bank/split cash (cash.md) is the restricted-inclusive element after adoption |
| DQC_0043 Incorrect Calculation Weights in Operating Cash Flows | Final, 2017-10-04 | effective calc weight of CFO descendants must match their balance type | our stored-sign rule for CF movement tags (stored positive = increase) is consistent |
| DQC_0180 Dividend Financial Statement Disclosures | Final, 2024-06-27 | DividendsPayableAmountPerShare is an instant, not the period DPS: use CommonStockDividendsPerShareDeclared; DPS declared is required when dividends are paid and differs from CashPaid when amounts differ | dividends_per_share never from DividendsPayableAmountPerShare; Declared first (shareholder-returns.md) |
| DQC_0178 Dividend Disclosures in the Statement of Changes in Equity | Final, 2024-06-27 | dividend elements on the equity statement with the retained-earnings member are reported positive | EQ dividend sign check |
| DQC_0187 Property Plant and Equipment Calculation | Final, 2024-06-27 | PropertyPlantAndEquipmentGross = PropertyPlantAndEquipmentNet + AccumulatedDepreciation…; the finance-lease-ROU gross = after + accumulated | ppe_net identity check; the ROU-inclusive tag has its own identity (balance-sheet §8) |
| DQC_0212 Missing Shares Issued or Authorized | Final, 2025-10-15 | shares outstanding facts require shares issued/authorized facts | completeness check for shares |
| DQC_0213 Missing Calculation Children for Key BS Items | Final, 2025-10-15 | Assets, AssetsCurrent, Liabilities, LiabilitiesCurrent, StockholdersEquity must have calc children on the balance sheet | a total without children = no structural check possible: flag |
| DQC.US.0227 Calculated Ratio Consistency Checks | Approved, 2026-03-18 (effective 2026-06-01) | per-share ratios must equal numerator / denominator within 0.01; EPS basic skipped for short periods and two-class filers | EPS × weighted shares ≈ NI to common check (catches ×1000 share scaling: RPAY, TBLA, MCD) |
| DQC_0206 Invalid Member on the DISE caption axis | Final, 2025-06-18 | each typed member QName on DisaggregationOfIncomeStatementExpenseCaptionIdentifierAxis must be an expense concept used on the income statement | DISE facts are caption-scoped: never read a DISE-axis Depreciation fact as the company total |
| DQC.US.0228 / 0230 / 0231 "Other" concepts | Approved, 2026-03-18 | an "other" fact must not exceed its aggregate; each calculated concept has only one "other" child; aggregate and its "other" concept must not be siblings | AccountsAndOtherReceivablesNetCurrent and InterestExpenseOther are wider/partial concepts: never AR alone / never total interest |

## 2. FASB taxonomy implementation guides (xbrl.fasb.org/impguidance/)

- **DISE (Subtopic 220-40), proposed TIG v1.0, 2025-07-21** (DISE_TIG/…Disaggregation of Income Statement Expenses Subtopic 220-40.pdf; final not yet issued, dise.pdf 2025-11-14 "under development"): typed axis DisaggregationOfIncomeStatementExpenseCaptionIdentifierAxis whose member is the face caption QName; new elements …CaptionPurchaseOfInventory, …CaptionEmployeeCompensation…, SellingExpense, etc.; existing Depreciation, AmortizationOfIntangibleAssets, RestructuringCharges reused on the axis. Example 1 tags a "Total operating expenses" that INCLUDES cost of goods sold as `OperatingExpenses` → `OperatingExpenses` can include COGS: the opex value check (operating-income.md §11) applies to it as to CostsAndExpenses. Example 3 (bank): total interest expense = `InterestExpenseOperating` with children deposits + borrowings; NII = `InterestIncomeExpenseNet`.
- **Income Taxes (Topic 740) TIG v1.0, February 2025** (IT_TIG/incometaxes.pdf): "Income Taxes Paid, Net" (IncomeTaxesPaidNet) = tax paid net of refunds; jurisdiction elements IncomeTaxPaidFederal/StateAndLocal/ForeignAfterRefundReceived and IncomeTaxAuthorityAxis for ≥5% jurisdictions. → cash_paid_for_income_taxes = the undimensioned IncomeTaxesPaidNet fact wherever it is presented (face or note); never add the jurisdiction parts on top.
- **Financial Statement Location Dimensions, proposed preparer guide v1.0, 2026-07-20** (FSL_PG/finstatelocdimensions.pdf): from the 2026 taxonomy, IncomeStatementLocationAxis and related axes are typed with the caption QName as member; "location context only", the element meaning does not change. → an impairment/amortization fact on the location axis tells which caption contains it (use for combined-line detection), never a separate total.
- Not found in the guide directory: any TIG on interest (capitalized/net), cost of revenue, or the cash-flow supplemental section (fasb.org itself returned 403).

## 3. SEC staff guidance (sec.gov/structureddata)

- Staff Observations 2011-12-13 (osd_staffobs_12-13-11.html): values "should almost always be entered as positive numbers"; a negative InterestExpense "would actually be adding the value to revenue". → a negative InterestExpense fact is a sign error: absolute value + flag.
- Data Quality Reminder "Negative Values" 2017-07-20: debit/credit and negated labels are presentation; sign comes from the element.
- "Cash Flow Statement Data Element Presentation" 2024-03-08: Income Taxes Paid found under the financing abstract. → identify taxes/interest paid by element, never by CF section.
- "Changing Tags for the Same Reported Items over Multiple Periods" 2022-12-08: different elements for the same line across periods or forms. → resolve by position + label; a tag switch is not a new series (era map).
- "Scaling and Tagging Errors for Shares Outstanding" 2022-10-06: dei:EntityCommonStockSharesOutstanding and us-gaap:CommonStockSharesOutstanding "should not differ significantly"; scaling errors (555,555,000 entered as 555,555) and CommonStockSharesIssued used for outstanding. → cross-check (×1000 ratio flag); the cover count stays a check, never the value (Dhairya 2026-11-12).

## 4. Index of DQC rules that name a tag our library maps (86 of 184 US rules)

| Rule | Title | Status | Release | Our tags named | Source |
|---|---|---|---|---|---|
| DQC.US.0226.10791 | US GAAP Elements Used in Employee Benefit Plan Filings | Approved | March 18, 2026 | Assets;InvestmentIncomeInterest;Liabilities | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0226/DQC_0226.md |
| DQC.US.0227.10920 | Calculated Ratio Consistency Checks | Approved | March 18, 2026 | EarningsPerShareBasic;NetIncomeLossAvailableToCommonStockholdersBasic;WeightedAverageNumberOfSharesOutstandingBasic | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0227/DQC_0227.md |
| DQC.US.0228.10801 | 'Other' Concept Should Not Exceed Aggregate | Approved | March 18, 2026 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0228/DQC_0228.md |
| DQC.US.0229.10802 | Multiple 'Other' Concepts in a Calculation Network | Removed |  | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0229/DQC_0229.md |
| DQC.US.0230.10803 | Disallowed 'Other' Concepts in Calculation Networks | Approved | March 18, 2026 | AccountsAndOtherReceivablesNetCurrent;Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0230/DQC_0230.md |
| DQC.US.0231.10804 | Aggregate and 'Other' Concepts Appearing as Siblings in Calculation Networks | Approved | March 18, 2026 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0231/DQC_0231.md |
| DQC.US.0236.10933 | Domestic Tax Jurisdiction Without Other Jurisdiction Breakdown | Final | June 29, 2026 | IncomeTaxExpenseBenefit | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0236/DQC_0236.md |
| DQC.US.0237.10934 | Location Balance Axis Member Not Present in Face Financial Statements | Final | June 29, 2026 | LongTermDebtNoncurrent | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0237/DQC_0237.md |
| DQC.US.0241.10942 | Incorrect Use of TransactionTypeAxis with Transaction Market Method Members | Final | June 29, 2026 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0241/DQC_0241.md |
| DQC.US.0243.10944 | Inappropriate Use of ConsolidationItemsAxis with Cash Flow and Equity Concepts | Final | June 29, 2026 | AdditionalPaidInCapital;Cash;CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents;NetCashProvidedByUsedInOperatingActivities;StockholdersEquity | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0243/DQC_0243.md |
| DQC_0001 | Axis with Inappropriate Members | Final | September 29, 2016 | PropertyPlantAndEquipmentGross;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0001/DQC_0001.md |
| DQC_0004 | Element Values Are Equal | Final | November 19, 2015 | Assets;AssetsCurrent;CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations;CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations;ComprehensiveIn… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0004/DQC_0004.md |
| DQC_0005 | Context Dates After Period End Date | Final | November 19, 2015 | Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0005/DQC_0005.md |
| DQC_0009 | Element A must be less than or equal to Element B | Final | November 19, 2015 | Assets;CommonStockSharesOutstanding | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0009/DQC_0009.md |
| DQC_0011 | Dimensional Equivalents | Final | October 4, 2017 | NetIncomeLoss;TreasuryStockCommonValue | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0011/DQC_0011.md |
| DQC_0014 | Negative Values With No Dimensions | Final | September 29, 2016 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0014/DQC_0014.md |
| DQC_0015 | Negative Values | Final | November 19, 2015 | AllocatedShareBasedCompensationExpense;Assets;Cash;Liabilities;NoninterestIncomeOtherOperatingIncome;RevenueFromContractWithCustomerExcludingAssessedTax;Revenue… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0015/DQC_0015.md |
| DQC_0041 | Axis with a Default Member that Differs from the Base Taxonomy | Final |  | Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0041/DQC_0041.md |
| DQC_0043 | Incorrect Calculation Weights in Operating Cash Flows | Final | October 4, 2017 | Cash;ComprehensiveIncomeNetOfTax;IncomeLossAttributableToParent;IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity;IncomeLossFromContinuingOpe… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0043/DQC_0043.md |
| DQC_0044 | Accrual Items used in Investing/Financing Cash flow Reconciliation | Final | October 4, 2017 | Cash;NetCashProvidedByUsedInFinancingActivities;NetCashProvidedByUsedInFinancingActivitiesContinuingOperations;NetCashProvidedByUsedInInvestingActivities;NetCas… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0044/DQC_0044.md |
| DQC_0045 | Movement of Concepts between Calculation Trees | Final | October 4, 2017 | Cash;NetCashProvidedByUsedInFinancingActivitiesContinuingOperations;NetCashProvidedByUsedInInvestingActivitiesContinuingOperations;NetCashProvidedByUsedInOperat… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0045/DQC_0045.md |
| DQC_0046 | Inappropriate Calculation Descendent | Final | October 4, 2017 | Cash;NetIncomeLoss;OtherComprehensiveIncomeLossNetOfTax;OtherComprehensiveIncomeLossNetOfTaxPortionAttributableToParent | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0046/DQC_0046.md |
| DQC_0047 | Calculation Descendants with No Balance Type | Final | October 4, 2017 | Cash;NetCashProvidedByUsedInOperatingActivities;NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0047/DQC_0047.md |
| DQC_0048 | Required Calculation Parent Element in the Cash Flow Statement | Final | October 4, 2017 | Cash;NetCashProvidedByUsedInFinancingActivities;NetCashProvidedByUsedInOperatingActivities | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0048/DQC_0048.md |
| DQC_0049 | Single Calculation Tree for Change in Cash Flows | Final | October 4, 2017 | Cash | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0049/DQC_0049.md |
| DQC_0051 | Before Tax Items | Final | October 4, 2017 | IncomeLossAttributableToParent;IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest;IncomeTaxExpenseBenefit;NetIncomeLoss | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0051/DQC_0051.md |
| DQC_0052 | Member Values | Final | October 4, 2017 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0052/DQC_0052.md |
| DQC_0053 | Excluded Members from an Axis | Final | October 4, 2017 | Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0053/DQC_0053.md |
| DQC_0057 | Cash Flow Opening and Closing Balances | Final | October 4, 2017 | Cash;CashAndCashEquivalentsAtCarryingValue;CashAndDueFromBanks;CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0057/DQC_0057.md |
| DQC_0060 | Element Dependence for Specific Elements | Final | October 4, 2017 | CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations;CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations;NetCashProvidedByUsedInFinancingActi… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0060/DQC_0060.md |
| DQC_0061 | Cash Flow Continuing Operations Elements not Used | Final | October 4, 2017 | Cash;CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations;CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations;NetCashProvidedByUsedInFinancin… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0061/DQC_0061.md |
| DQC_0062 | No Fact Value for Change in Cash | Final | October 4, 2017 | Cash | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0062/DQC_0062.md |
| DQC_0065 | Interest Paid Net (Operating) Not on Cash Flow | Final | October 4, 2017 | Cash;InterestPaid;InterestPaidNet | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0065/DQC_0065.md |
| DQC_0067 | Mutually Exclusive Elements | Final | October 10, 2018 | RevenueFromContractWithCustomerExcludingAssessedTax;SalesRevenueNet | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0067/DQC_0067.md |
| DQC_0071 | Revenue/Cost Single Member | Final | October 10, 2018 | CostOfGoodsAndServicesSold;RevenueFromContractWithCustomerExcludingAssessedTax;RevenueFromContractWithCustomerIncludingAssessedTax;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0071/DQC_0071.md |
| DQC_0076 | Performance Obligations With No Durations | Final | October 10, 2018 | RevenueFromContractWithCustomerIncludingAssessedTax | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0076/DQC_0076.md |
| DQC_0081 | Sibling and Child Relationships | Final | July 15, 2019 | Assets;Cash;CostOfRevenue;Liabilities;LiabilitiesCurrent;NetIncomeLoss;OperatingExpenses | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0081/DQC_0081.md |
| DQC_0082 | Disaggregation by Variable Interest Elements (VIE) | Final | October 1, 2019 | Assets;AssetsCurrent;Liabilities;LiabilitiesCurrent | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0082/DQC_0082.md |
| DQC_0083 | Consolidated Variable Interest Entities (VIE) | Final | October 1, 2019 | AccountsPayableCurrent | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0083/DQC_0083.md |
| DQC_0085 | Deferred Tax Assets & Liabilities | Final | February 12, 2020 | Assets;Liabilities | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0085/DQC_0085.md |
| DQC_0095 | Scale - Common Stock Outstanding | Final | July 15, 2020 | CommonStockSharesOutstanding | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0095/DQC_0095.md |
| DQC_0099 | FS with No Associated Calculation | Final | October 7, 2020 | AllocatedShareBasedCompensationExpense;Cash;ComprehensiveIncomeNetOfTax;NetIncomeLossAvailableToCommonStockholdersBasic;NoninterestIncomeOtherOperatingIncome | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0099/DQC_0099.md |
| DQC_0100 | Invalid Consolidation Axis | Final | October 7, 2020 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0100/DQC_0100.md |
| DQC_0107 | General Text Block | Final | June 29, 2021 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0107/DQC_0107.md |
| DQC_0113 | Gross Acquisition Less Than Net Acquisition | Final | June 29, 2021 | Cash | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0113/DQC_0113.md |
| DQC_0114 | Assets Acquired Net of Goodwill | Final | June 29, 2021 | Assets;Goodwill;Liabilities | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0114/DQC_0114.md |
| DQC_0117 | Financial Statement Tables Dimensional Cross Check | Final | September 29, 2021 | Cash;PreferredStockValue;RevenueFromContractWithCustomerExcludingAssessedTax;RevenueFromContractWithCustomerIncludingAssessedTax;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0117/DQC_0117.md |
| DQC_0118 | Financial Statement Tables Calculation Check of Required Context | Final | September 29, 2021 | Cash;CostOfRevenue;OperatingExpenses;OperatingIncomeLoss;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0118/DQC_0118.md |
| DQC_0119 | Income Before Tax Equity Method | Final | September 29, 2021 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest;IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestA… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0119/DQC_0119.md |
| DQC_0121 | Incorrect Transition Elements Used | Final | September 29, 2021 | Cash | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0121/DQC_0121.md |
| DQC_0122 | Components of Equity on the Balance Sheet | Final | September 29, 2021 | CommonStockValue;StockholdersEquity | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0122/DQC_0122.md |
| DQC_0123 | Missing Components of Equity Axis | Final | September 29, 2021 | StockholdersEquity;StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0123/DQC_0123.md |
| DQC_0124 | Breakdown of Lease Liabilities & Assets Across Financial Statement Lines Items | Final | September 29, 2021 | Assets;Liabilities | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0124/DQC_0124.md |
| DQC_0139 | Bank Ratios - Scale Issues | Final | September 21, 2022 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0139/DQC_0139.md |
| DQC_0145 | Inappropriate Cash Flow Presentation | Final | January 25, 2023 | Cash | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0145/DQC_0145.md |
| DQC_0148 | OCI Items In Income & Income in OCI | Final | July 6, 2023 | IncomeTaxExpenseBenefit;NetIncomeLoss;NetIncomeLossAvailableToCommonStockholdersBasic;OtherComprehensiveIncomeLossNetOfTax;OtherComprehensiveIncomeLossNetOfTaxP… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0148/DQC_0148.md |
| DQC_0149 | Use of Noncurrent Assets | Final | July 6, 2023 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0149/DQC_0149.md |
| DQC_0150 | Segment Reporting Inconsistencies | Final | July 6, 2023 | Assets;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0150/DQC_0150.md |
| DQC_0153 | Financial Statements Table Placement | Final | July 6, 2023 | ComprehensiveIncomeNetOfTax;IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest;IncomeTaxExpenseBenefit;NetIncomeLoss;Ot… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0153/DQC_0153.md |
| DQC_0154 | Tax Reconciliation Items | Final | July 6, 2023 | IncomeTaxExpenseBenefit | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0154/DQC_0154.md |
| DQC_0163 | Segment Expenditure Addition To Long Lived Assets | Final | October 5, 2023 | Assets;PaymentsToAcquireProductiveAssets;PaymentsToAcquirePropertyPlantAndEquipment | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0163/DQC_0163.md |
| DQC_0164 | Use of Location Axis | Final | October 5, 2023 | Assets;AssetsCurrent;CostOfRevenue;GrossProfit;IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest;IncomeLossFromContinu… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0164/DQC_0164.md |
| DQC_0167 | Inconsistent Calculation Roots | Final | January 16, 2024 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0167/DQC_0167.md |
| DQC_0168 | Tax Reconciliation Calculation | Final | January 16, 2024 | IncomeTaxExpenseBenefit | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0168/DQC_0168.md |
| DQC_0169 | Calculation in the Parenthetical Disclosure | Final | January 16, 2024 | Assets;AssetsCurrent | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0169/DQC_0169.md |
| DQC_0178 | Dividend Disclosures in the Statement of Changes in Shareholders Equity | Final | June 27, 2024 | Cash;CommonStockDividendsPerShareDeclared | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0178/DQC_0178.md |
| DQC_0179 | Dividend Event Disclosures | Final | June 27, 2024 | CommonStockDividendsPerShareDeclared | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0179/DQC_0179.md |
| DQC_0180 | Dividend Financial Statement Disclosures | Final | June 27, 2024 | CommonStockDividendsPerShareCashPaid;CommonStockDividendsPerShareDeclared;PaymentsOfDividendsCommonStock | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0180/DQC_0180.md |
| DQC_0181 | Interest Expense Operating and Nonoperating | Final | June 27, 2024 | InterestExpense;InterestExpenseNonoperating;InterestExpenseOperating;InterestIncomeExpenseNet;NonoperatingIncomeExpense;OperatingExpenses | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0181/DQC_0181.md |
| DQC_0182 | Dimensional Equivalents Using the Meta Taxonomy | Final | June 27, 2024 | RetainedEarningsAccumulatedDeficit;StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0182/DQC_0182.md |
| DQC_0183 | Face Financial Statement Location using the Accrual Axis | Final | June 27, 2024 | Assets;Depreciation | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0183/DQC_0183.md |
| DQC_0184 | OCI Reconciliation of Before Tax and Net of Tax OCI Items | Final | June 27, 2024 | OtherComprehensiveIncomeLossPensionAndOtherPostretirementBenefitPlansAdjustmentNetOfTax;OtherComprehensiveIncomeUnrealizedHoldingGainLossOnSecuritiesArisingDuri… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0184/DQC_0184.md |
| DQC_0187 | Property Plant and Equipment Calculation | Final | June 27, 2024 | AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment;Depreciation;PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDep… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0187/DQC_0187.md |
| DQC_0192 | Balance Sheet Numerical Scaling | Final | September 25, 2024 | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0192/DQC_0192.md |
| DQC_0194 | Negative Values for  Members on the Statement of Equity Components Axis | Final | February 28, 2025 | CommonStockSharesOutstanding | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0194/DQC_0194.md |
| DQC_0195 | Facts using an invalid member with the Equity Components Axis | Final | February 28, 2025 | SharesOutstanding;StockholdersEquity;StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0195/DQC_0195.md |
| DQC_0196 | Opening and Closing Balances on the Statement of Shareholders Equity | Final | February 28, 2025 | AccumulatedOtherComprehensiveIncomeLossNetOfTax;AdditionalPaidInCapital;RetainedEarningsAccumulatedDeficit;StockholdersEquity;TreasuryStockCommonValue | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0196/DQC_0196.md |
| DQC_0197 | Income Statement Items used on The Changes in Shareholders Equity | Final | February 28, 2025 | NetIncomeLoss;NetIncomeLossAttributableToNoncontrollingInterest;Revenues | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0197/DQC_0197.md |
| DQC_0198 | Tax Reconciliation Percentage and Monetary Disclosures | Final | February 28, 2025 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest;IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestA… | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0198/DQC_0198.md |
| DQC_0200 | Income Statement Location Axis with Instant Elements | Final | February 28, 2025 | Assets;OperatingExpenses | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0200/DQC_0200.md |
| DQC_0203 | Income Tax Authority Axis with Invalid Members | Removed |  | Assets | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0203/DQC_0203.md |
| DQC_0204 | Invalid Axis used for Tangible and Intangible Assets | Final | June 18, 2025 | Assets;PropertyPlantAndEquipmentGross | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0204/DQC_0204.md |
| DQC_0206 | Invalid Member used on Disaggregation Of Income Statement Expense Caption Axis | Final | June 18, 2025 | Depreciation | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0206/DQC_0206.md |
| DQC_0212 | Missing Shares Issued or Authorized Facts When Shares Outstanding Reported | Final | October 15, 2025 | CommonStockSharesOutstanding;SharesOutstanding | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0212/DQC_0212.md |
| DQC_0213 | Missing Calculation Children for Key Balance Sheet Items | Final | October 15, 2025 | Assets;AssetsCurrent;Liabilities;LiabilitiesCurrent;StockholdersEquity | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0213/DQC_0213.md |
| DQC_0214 | Missing Equity Concepts in Balance Sheet Calculation | Final | October 15, 2025 | TreasuryStockValue | https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/docs/DQC_US_0214/DQC_0214.md |

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.94). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.94. 71 elements named in this card have library knowledge; the 30 most served are below. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `LiabilitiesCurrent`
- **Meaning:** Liabilities, Current (us-gaap, instant, credit). Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
- **Data point definition:** current_liabilities: Total current liabilities as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]; total_liabilities: Total liabilities as printed.
- **Data point:** current_liabilities; total_liabilities
- **Rules:** X39; C03; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1439 served, 32338 proven, 137 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentLiabilities@2020; FreshStartAdjustmentIncreaseDecreaseCurrentLiabilities@2021; PostconfirmationCurrentLiabilities@2021; PreconfirmationCurrentLiabilities@2021 (+3 more)

### `WeightedAverageNumberOfSharesOutstandingBasic`
- **Meaning:** Weighted Average Number of Shares Outstanding, Basic (us-gaap, duration). Number of [basic] shares or units, after adjustment for contingently issuable shares or units and other shares or units not deemed outstanding, determined by relating the portion of time within a reporting period that common shares or units...
- **Data point definition:** weighted_basic_shares: Weighted average basic common shares as printed.
- **Data point:** weighted_basic_shares; role weighted_basic_shares:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1316 served, 4583 proven, 139 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000063908-24-000072: MCD FY2023 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average basic shares 727.9;  the XBRL fact is 727.9 shares (scale ; filer XBRL error 0000063908-25-000012: MCD FY2024 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average basic shares 718.3;  the XBRL fact is 718.3 shares (scale  (+4 more)
- **Pattern hits:** P03 (5); P04 (3)
- **Deprecation:** replaces WeightedAverageNumberOfShareOutstandingBasicAndDiluted@2022

### `IncomeTaxExpenseBenefit`
- **Meaning:** Income Tax Expense (Benefit) (us-gaap, duration, debit). Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.
- **Data point definition:** income_tax_expense: Income tax expense (benefit) for the period, as printed;  a benefit is a real negative.
- **Data point:** income_tax_expense; polarity income_tax_expense:signed; role income_tax_expense:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1302 served, 44905 proven, 140 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncomeTaxExpenseBenefitContinuingOperations@2013; RestatementOfPriorYearIncomeTaxEffects@2020

### `EarningsPerShareBasic`
- **Meaning:** Earnings Per Share, Basic (us-gaap, duration). The amount of net income (loss) for the period per each share of common stock or unit outstanding during the reporting period.
- **Data point definition:** basic_eps: Basic EPS per common share as printed (latest print = split-adjusted history, X92).
- **Data point:** basic_eps; role basic_eps:primary#1
- **Rules:** none
- **Evidence:** 109 companies, 1236 served, 4644 proven, 139 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; EarningsPerShareBasicAndDiluted@2022 (+5 more)

### `NetIncomeLoss`
- **Meaning:** Net Income (Loss) Attributable to Parent (us-gaap, duration, credit). The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#1
- **Rules:** X77; X140; C29; resolver functions resolve
- **Evidence:** 105 companies, 1212 served, 28185 proven, 129 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InvestmentCompanyNetAssetsFromOperationsIncreaseDecrease@2023; RestatementOfPriorYearIncomeNetOfTax@2020

### `Goodwill`
- **Meaning:** Goodwill (us-gaap, instant, debit). Amount, after accumulated impairment loss, of asset representing future economic benefit arising from other asset acquired in business combination or from joint venture formation or both, that is not individually identified and separately r...
- **Data point definition:** goodwill: Goodwill at period end as printed.
- **Data point:** goodwill; role goodwill:primary#1
- **Rules:** X78; B20
- **Evidence:** 105 companies, 1206 served, 4387 proven, 137 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces BusinessCombinationGoodwillRecognizedSegmentAllocation@2013; FreshStartAdjustmentIncreaseDecreaseGoodwill@2021; FreshStartAdjustmentIncreaseDecreaseReorganizationValueInExcessOfAmountsAllocableToIdentifiableAssets@2021; PostconfirmationGoodwill@2021 (+2 more)

### `ComprehensiveIncomeNetOfTax`
- **Meaning:** Comprehensive Income (Loss), Net of Tax, Attributable to Parent (us-gaap, duration, credit). Amount after tax of increase (decrease) in equity from transactions and other events and circumstances from net income and other comprehensive income, attributable to parent entity. Excludes changes in equity resulting from investments by o...
- **Data point definition:** comprehensive_income: Comprehensive income attributable to the parent as printed.
- **Data point:** comprehensive_income; role comprehensive_income:primary#1
- **Rules:** X43; X67; X76; I38; I39; I40; I41; I42; resolver functions COMBINED_YIELDS_TO; comparative_fill; DERIVED_YIELDS_TO; fill_printed_zero_and_comparative; resolve_ci
- **Evidence:** 108 companies, 1206 served, 4365 proven, 99 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `StockholdersEquity`
- **Meaning:** Equity, Attributable to Parent (us-gaap, instant, credit). Amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable to noncontrolling interest.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.
- **Data point:** stockholders_equity
- **Rules:** X78; C06; resolver functions resolve
- **Evidence:** 104 companies, 1190 served, 22897 proven, 126 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CommonStockholdersEquity@2013; EquityMethodInvestmentSummarizedFinancialInformationEquityOrCapital@2020; FreshStartAdjustmentIncreaseDecreaseStockholdersEquity@2021; PostconfirmationStockholdersEquity@2021 (+1 more)

### `AmortizationOfIntangibleAssets`
- **Meaning:** Intangible Asset, Finite-Lived, Amortization Expense (us-gaap, duration, debit). Amount of amortization expense for finite-lived intangible asset. Excludes goodwill and capitalized cost for software to be sold, leased, or marketed.
- **Data point definition:** amortization_of_intangibles: Amortization of acquired finite-lived intangible assets for the period (face line, cash-flow line or note).; depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers). (+1 more)
- **Data point:** amortization_of_intangibles; depreciation_and_amortization; operating_expenses; polarity amortization_of_intangibles:positive; depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#1; depreciation_and_amortization:primary-part#2; depreciation_and_amortization:primary-part#3; depreciation_and_amortization:primary-part#8 (+1 more)
- **Rules:** I51; I52; I53; I54; I43; I44; I45; I46; I47; I48; I49; I50; family resolve_all.NARROW[amortization_of_intangibles]
- **Evidence:** 92 companies, 1180 served, 2150 proven, 103 certified cells; last verified 2026-11-15
- **Known problems:** FSN dropped fact 0001413329-23-000025 (fsn_dropped_facts.csv); FSN dropped fact 0001413329-24-000013 (fsn_dropped_facts.csv); pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. ISRG amortization_of_intangibles 2025-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)
- **Deprecation:** replaces AmortizationOfAcquiredIntangibleAssets@2013; AmortizationOfIntangiblesNonproductionMember@2013; FiniteLivedIntangibleAssetsAmortizationExpense@2012

### `NetCashProvidedByUsedInFinancingActivities`
- **Meaning:** Cash Provided by (Used in) Financing Activity, Including Discontinued Operation (us-gaap, duration, debit). Amount of cash inflow (outflow) from financing activity, including, but not limited to, discontinued operation. Financing activity includes, but is not limited to, obtaining resource from owner and providing return on, and return of, their ...
- **Data point definition:** cash_flow_financing: Net cash provided by (used in) financing activities as printed.
- **Data point:** cash_flow_financing; polarity cash_flow_financing:signed; role cash_flow_financing:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1161 served, 42499 proven, 136 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NetCashProvidedByUsedInInvestingActivities`
- **Meaning:** Cash Provided by (Used in) Investing Activity, Including Discontinued Operation (us-gaap, duration, debit). Amount of cash inflow (outflow) from investing activity, including, but not limited to, discontinued operation. Investing activity includes, but is not limited to, making and collecting loan, acquiring and disposing of debt and equity instr...
- **Data point definition:** cash_flow_investing: Net cash provided by (used in) investing activities as printed.
- **Data point:** cash_flow_investing; polarity cash_flow_investing:signed; role cash_flow_investing:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1161 served, 42135 proven, 136 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CashAndCashEquivalentsAtCarryingValue`
- **Meaning:** Cash and Cash Equivalent (us-gaap, instant, debit). Amount of cash and cash equivalent. Cash includes, but is not limited to, currency on hand, demand deposit with financial institution, and account with general characteristic of demand deposit. Cash equivalent includes, but is not limited t...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:primary#1
- **Rules:** B05; B06; B07; B08; family resolve_all.NARROW[cash_and_equivalents]
- **Evidence:** 103 companies, 1156 served, 22866 proven, 131 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 2 companies, e.g. DELL cash_and_equivalents 2015-01-30 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseCashAndCashEquivalents@2021; PostconfirmationCashAndCashEquivalents@2021; PreconfirmationCashAndCashEquivalents@2021

### `NetCashProvidedByUsedInOperatingActivities`
- **Meaning:** Cash Provided by (Used in) Operating Activity, Including Discontinued Operation (us-gaap, duration). Amount of cash inflow (outflow) from operating activity, including, but not limited to, discontinued operation. Operating activity includes, but is not limited to, transaction, adjustment, and change in value not defined as investing or fin...
- **Data point definition:** cfo: Net cash provided by (used in) operating activities as printed.
- **Data point:** cfo; polarity cfo:signed; role cfo:primary#1
- **Rules:** X84
- **Evidence:** 110 companies, 1154 served, 40731 proven, 136 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `AssetsCurrent`
- **Meaning:** Assets, Current (us-gaap, instant, debit). Amount of asset recognized for present right to economic benefit, classified as current.
- **Data point definition:** current_assets: Total current assets as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]
- **Data point:** current_assets
- **Rules:** X39; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1118 served, 32318 proven, 137 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentAssets@2020; FreshStartAdjustmentIncreaseDecreaseCurrentAssets@2021; PostconfirmationCurrentAssets@2021; PreconfirmationCurrentAssets@2021 (+3 more)

### `PropertyPlantAndEquipmentNet`
- **Meaning:** Property, Plant, and Equipment, after Accumulated Depreciation, Depletion, and Amortization (us-gaap, instant, debit). Amount, after accumulated depreciation, depletion, and amortization, of property, plant, and equipment. Includes, but is not limited to, land and land improvement; building; machinery and equipment; furniture and fixture; and work of art, h...
- **Data point definition:** ppe_net: Property, plant and equipment net of accumulated depreciation at period end (incl. finance-lease ROU only where the filer prints them together).
- **Data point:** ppe_net; role ppe_net:primary#1
- **Rules:** B22
- **Evidence:** 106 companies, 1096 served, 32159 proven, 113 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FlightEquipmentOwnedNet@2016; FreshStartAdjustmentIncreaseDecreasePropertyAndEquipmentNet@2021; PostconfirmationPropertyAndEquipmentNet@2021; PreconfirmationPropertyAndEquipmentNet@2021

### `CommonStockSharesOutstanding`
- **Meaning:** Common Stock, Shares, Outstanding (us-gaap, instant). Number of shares of common stock outstanding. Common stock represent the ownership interest in a corporation.
- **Data point definition:** shares_outstanding: Common shares outstanding at period end (all economic classes).
- **Data point:** shares_outstanding; role shares_outstanding:primary#1
- **Rules:** X67; X111; B23; B24; B29; resolver functions DERIVED_YIELDS_TO; comparative_fill; fill_printed_zero_and_comparative; shares
- **Evidence:** 83 companies, 989 served, 2408 proven, 80 certified cells; last verified 2026-11-15
- **Known problems:** pattern P04 round_share_count: 3 open hit(s) at 3 companies, e.g. CVS shares_outstanding 2022-12-31 (resolver) (pattern_hits.csv); pattern P05 comparative_only_year_hidden: 1 open hit(s) at 1 companies, e.g. WFC shares_outstanding 2023-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P04 (3); P05 (1)

### `AccountsPayableCurrent`
- **Meaning:** Accounts Payable, Current (us-gaap, instant, credit). Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business. Used to reflect the curr...
- **Data point definition:** accounts_payable: Trade accounts payable at period end. [not applicable: bank]
- **Data point:** accounts_payable; role accounts_payable:primary#1
- **Rules:** B16; B17; B18; B19; family resolve_all.NARROW[accounts_payable]
- **Evidence:** 84 companies, 985 served, 3404 proven, 134 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsPayableRelatedPartiesCurrent@2023; FreshStartAdjustmentIncreaseDecreaseAccountsPayable@2021; PostconfirmationAccountsPayable@2021; PreconfirmationAccountsPayable@2021

### `CostOfGoodsAndServicesSold`
- **Meaning:** Cost of Product and Service Sold (us-gaap, duration, debit). The aggregate costs related to goods produced and sold and services rendered by an entity during the reporting period. This excludes costs incurred during the reporting period related to financial services rendered and other revenue generat...
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#2
- **Rules:** I02; I03; I04
- **Evidence:** 65 companies, 955 served, 16174 proven, 84 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AdvertisingRevenueCost@2018; AssetManagementCosts@2018; CasinoExpenses@2018; ConcessionsCosts@2018 (+62 more)

### `Liabilities`
- **Meaning:** Liabilities (us-gaap, instant, credit). Amount of liability recognized for present obligation requiring transfer or otherwise providing economic benefit to others.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** C03; F02; B25; resolver functions resolve; run; apply_tl_corroboration
- **Evidence:** 83 companies, 950 served, 29466 proven, 110 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000101829-20-000013: RTX (UTX) FY2019 10-K utx-20191231.htm consolidated balance sheet prints Total Liabilities 95,390 (2018: 93,492);  the XBRL tags only the 2018 value (R4.htm show
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationLiabilities@2020; FreshStartAdjustmentIncreaseDecreaseLiabilities@2021; PostconfirmationLiabilities@2021; PreconfirmationLiabilities@2021 (+4 more)

### `OperatingIncomeLoss`
- **Meaning:** Operating Income (Loss) (us-gaap, duration, credit). The net result for the period of deducting operating expenses from operating revenues.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; operating_income: Operating income: revenue minus all operating costs (COR, opex, restructuring and impairment), before interest, other non-operating items, equity-method income and tax. [not applicable: bank] (+1 more)
- **Data point:** operating_income; operating_expenses; other_income_expense_net
- **Rules:** C13; resolver functions resolve
- **Evidence:** 80 companies, 949 served, 34797 proven, 118 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpense`
- **Meaning:** Interest Expense, Operating and Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as operating and nonoperating. Includes, but is not limited to, cost of borrowing accounted for as interest expense.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** interest_expense; other_income_expense_net; operating_expenses; interest_income; polarity interest_expense:positive; role interest_expense:primary#1
- **Rules:** X115; I21; I20; I22; I23; I24; resolver functions resolve_band; family resolve_all.NARROW[interest_expense]
- **Evidence:** 88 companies, 938 served, 24594 proven, 65 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. META interest_expense 2021-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToInterestExpenseNet@2013; CashFlowHedgeGainReclassifiedToInterestExpense@2013; CashFlowHedgeLossReclassifiedToInterestExpense@2013; InterestExpenseRelatedParty@2023

### `PaymentsToAcquirePropertyPlantAndEquipment`
- **Meaning:** Payments to Acquire Property, Plant, and Equipment (us-gaap, duration, credit). The cash outflow associated with the acquisition of long-lived, physical assets that are used in the normal conduct of business to produce goods and services and not intended for resale; includes cash outflows to pay for construction of sel...
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: insurer,bdc]
- **Data point:** capex; polarity capex:positive; role capex:primary#1
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX; resolve_all.NARROW[capex]
- **Evidence:** 82 companies, 914 served, 17784 proven, 110 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestPaidNet`
- **Meaning:** Interest Paid, Excluding Capitalized Interest, Operating Activity (us-gaap, duration, credit). Amount of cash paid for interest, excluding capitalized interest, classified as operating activity. Includes, but is not limited to, payment to settle zero-coupon bond for accreted interest of debt discount and debt instrument with insignif...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#1
- **Rules:** K35
- **Evidence:** 98 companies, 883 served, 1627 proven, 90 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncomeTaxesPaidNet`
- **Meaning:** Income Tax Paid, after Refund Received (us-gaap, duration, credit). Amount, after refund, of cash paid to foreign, federal, state, and local jurisdictions as income tax.
- **Data point definition:** cash_paid_for_income_taxes: Cash paid for income taxes, net of refunds, as printed.
- **Data point:** cash_paid_for_income_taxes; polarity cash_paid_for_income_taxes:signed; role cash_paid_for_income_taxes:primary#1
- **Rules:** K32; K34; K33
- **Evidence:** 105 companies, 866 served, 1547 proven, 93 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000040545-17-000010: GE FY2016 10-K R7.htm statement of cash flows: Cash recovered (paid) during the year for income taxes (7,469): 7,469 paid;  IncomeTaxesPaidNet is positive for ta; filer XBRL error 0000040545-16-000145: GE FY2016 10-K R7.htm (0000040545-17-000010) prints the FY2015 column: Cash recovered (paid) during the year for income taxes (2,486): 2,486 paid;  the FY2015 10 (+2 more)
- **Pattern hits:** none

### `AccountsReceivableNetCurrent`
- **Meaning:** Accounts Receivable, after Allowance for Credit Loss, Current (us-gaap, instant, debit). Amount, after allowance for credit loss, of right to consideration from customer for product sold and service rendered in normal course of business, classified as current.
- **Data point definition:** accounts_receivable: Trade accounts receivable, net of allowance, at period end. [not applicable: bank]
- **Data point:** accounts_receivable; role accounts_receivable:primary#1
- **Rules:** B09; B10; B11; B12; B13; B30
- **Evidence:** 74 companies, 832 served, 3022 proven, 102 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsReceivableRelatedPartiesCurrent@2023

### `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`
- **Meaning:** Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest (us-gaap, duration, credit). Amount of income (loss) from continuing operations, including income (loss) from equity method investments, before deduction of income tax expense (benefit), and income (loss) attributable to noncontrolling interest.
- **Data point definition:** income_before_tax: Income from continuing operations before income taxes, as printed (incl. equity-method income where the filer places it above tax).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** income_before_tax; other_income_expense_net; role income_before_tax:primary#1
- **Rules:** I36; I37
- **Evidence:** 95 companies, 816 served, 32500 proven, 95 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; RetrospectiveEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAmountAfterApplication@2012 (+2 more)

### `CommonStockDividendsPerShareDeclared`
- **Meaning:** Common Stock, Dividends, Per Share, Declared (us-gaap, duration). Aggregate dividends declared during the period for each share of common stock outstanding.
- **Data point definition:** dividends_per_share: Dividends declared per common share for the fiscal year.
- **Data point:** dividends_per_share; polarity dividends_per_share:positive; role dividends_per_share:primary#1
- **Rules:** none
- **Evidence:** 81 companies, 765 served, 2489 proven, 119 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0001137789-24-000068: STX FY2024 10-K stx-20240628.htm consolidated statements of shareholders' equity: Dividends to shareholders ($ 2.80 per ordinary share);  the XBRL facts are 10^6; filer XBRL error 0001137789-24-000068: STX FY2024 10-K stx-20240628.htm R9 consolidated statements of shareholders' equity, FY2022 column: Dividends to shareholders ($ 2.77 per ordinary share);  the X (+1 more)
- **Pattern hits:** none
- **Deprecation:** replaces DividendDeclaredMember@2025

### `LongTermDebtNoncurrent`
- **Meaning:** Long-Term Debt, Excluding Current Maturities (us-gaap, instant, credit). Amount, after deduction of unamortized premium (discount) and debt issuance cost, of long-term debt classified as noncurrent. Excludes lease obligation.
- **Data point definition:** total_debt: Total debt: short- and long-term borrowings incl. current portion, commercial paper, finance and capital leases (face or notes), financing obligations and failed sale-leasebacks;  excludes operating leases and accrued interest. (+1 more)
- **Data point:** total_debt; total_liabilities
- **Rules:** D14; resolver functions run
- **Evidence:** 61 companies, 751 served, 203 proven, 3 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces NonRecourseDebt@2022

### `Revenues`
- **Meaning:** Revenues (us-gaap, duration, credit). Amount of revenue recognized from goods sold, services rendered, insurance premiums, or other activities that constitute an earning process. Includes, but is not limited to, investment and interest income before deduction of interest expens...
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** revenue; gross_profit
- **Rules:** X123
- **Evidence:** 69 companies, 708 served, 12391 proven, 44 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToRevenueNet@2013; CashFlowHedgeGainReclassifiedToRevenue@2013; CashFlowHedgeLossReclassifiedToRevenue@2013; DevelopmentStageEnterpriseCumulativeRevenue@2012 (+10 more)

### `DepreciationDepletionAndAmortization`
- **Meaning:** Depreciation, Depletion and Amortization (us-gaap, duration, debit). The aggregate expense recognized in the current period that allocates the cost of tangible assets, intangible assets, or depleting assets to periods that benefit from use of the assets.
- **Data point definition:** depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** depreciation_and_amortization; operating_expenses; polarity depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#1; depreciation_and_amortization:primary#4
- **Rules:** I43; I44; I45; I46; I47; I48; I49; I50; family resolve_all.NARROW[depreciation_and_amortization]
- **Evidence:** 62 companies, 660 served, 10498 proven, 60 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 12 open hit(s) at 1 companies, e.g. CSCO depreciation_and_amortization 2015-07-25 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (12)
<!-- END GENERATED: tag library rows -->
