# Tag cards, ranks 96-359 of TAG-PRIORITY-2026-11-11 (Tag Expert, 2026-11-11)

Same columns as TOP-TAGS-001-095.md. Ranks 1-359 together = 80% of top-1,000 company-tag pairs. `source` = explicit (decided tag by tag from the family cards) or family (axis/member/abstract, IncreaseDecreaseIn*, Proceeds/Payments/Repayments*, per-share split, gains/losses). Family rows are defaults; a company whose use contradicts one is residue for the Ritwik sessions.

| Rank | Tag | Cos | Period | Balance | Concept / decision | Sign | Company variants | Do NOT map when | Source |
|---|---|---|---|---|---|---|---|---|---|
| 96 | ProductOrServiceAxis | 280 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 97 | GrossProfit | 280 | D | C | gross_profit_resolved | credit; negative = gross loss | only 36 of 100 print it; derive revenue − cost of revenue only for a full cost-of-sales perimeter | not when cost is "excluding D&A" (overstated) or when CostsAndExpenses is the only cost line | explicit |
| 98 | ProductsAndServicesDomain | 280 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 99 | AccruedLiabilitiesCurrent | 277 | I | C | excluded: component_no_concept | credit | GOOG keeps finance-lease current inside it (ExtensibleList) | never debt | explicit |
| 100 | GainsLossesOnExtinguishmentOfDebt | 274 | D | C | excluded: component_no_concept | credit-typed; gain positive | InterestAndDebtExpense can include it (FASB calc) | never interest expense | explicit |
| 101 | PreferredStockSharesOutstanding | 271 | I | — | excluded: per_share_detail | shares |  | never common shares | explicit |
| 102 | StockholdersEquityIncludingPortionAttributableToNoncontrollingInterestAbstract | 261 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 103 | WeightedAverageNumberOfSharesOutstandingAbstract | 261 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 104 | TreasuryStockValue | 260 | I | D | component of stockholders_equity (contra) | DEBIT-typed: positive = a deduction from equity | TreasuryStockCommonValue variant | never added to equity with a plus sign | explicit |
| 105 | IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets | 255 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 106 | PaymentsOfDebtIssuanceCosts | 253 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 107 | OtherLiabilitiesCurrent | 250 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 108 | ProceedsFromSaleOfPropertyPlantAndEquipment | 249 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 109 | CostsAndExpenses | 248 | D | D | excluded: subtotal_not_in_catalog | debit | four perimeters (includes COGS; CVX/AJG/HTZ include interest/taxes) | never cost_of_revenue or operating_expenses by name | explicit |
| 110 | AllowanceForDoubtfulAccountsReceivableCurrent | 243 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 111 | NonoperatingIncomeExpense | 239 | D | C | other_income_expense_net | credit; signed | can CONTAIN interest (DLH, ODFL calc) | never interest expense; "Interest and other" label = combined | explicit |
| 112 | OperatingLeaseLiabilityCurrent | 236 | I | C | excluded: component_no_concept | credit |  | never debt | explicit |
| 113 | TreasuryStockCommonValue | 235 | I | D | component of stockholders_equity (contra) | debit-typed: positive = deduction |  | as above | explicit |
| 114 | LongTermDebtCurrent | 235 | I | C | component of total_debt_resolved | credit | = ShortTermBorrowings at MRVL DVN DRI MATX VOYA (same debt) | never add on top of LongTermDebt (includes current at CSCO TMO) | explicit |
| 115 | ProceedsFromIssuanceOfCommonStock | 234 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 116 | IncomeLossFromEquityMethodInvestments | 229 | D | C | excluded: component_no_concept | credit; signed | sits below or above pretax by filer (the pretax pair differs by it) | never | explicit |
| 117 | GeneralAndAdministrativeExpense | 229 | D | D | component of sga_expense | debit |  | never SG&A alone when S&M is printed separately | explicit |
| 118 | IncreaseDecreaseInOtherOperatingAssets | 227 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 119 | IncreaseDecreaseInOtherOperatingCapitalNet | 226 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 120 | ResearchAndDevelopmentExpense | 225 | D | D | research_and_development | debit | JNJ: face is …ExcludingAcquiredInProcessCost; RDE = CF IPR&D add-back | not the CF add-back copy | explicit |
| 121 | OperatingExpensesAbstract | 220 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 122 | IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | 219 | D | D | excluded: combined_perimeter | debit-typed | 262 of 358 cf_ap_change residue filers | never cf_ap_change | explicit |
| 123 | ProceedsFromStockOptionsExercised | 218 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 124 | ContractWithCustomerLiabilityCurrent | 211 | I | C | excluded: component_no_concept (deferred revenue) | credit | DeferredRevenueCurrent older twin | never debt | explicit |
| 125 | EmployeeRelatedLiabilitiesCurrent | 206 | I | C | excluded: component_no_concept | credit |  | never | explicit |
| 126 | PaymentsOfDividends | 196 | D | C | dividends_paid_resolved | credit-typed payment | generic: may include preferred (BPOP) or equivalents (TDG) | not evidence of a COMMON dividend without a common DPS | explicit |
| 127 | CostsAndExpensesAbstract | 196 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 128 | StatementClassOfStockAxis | 188 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 129 | ClassOfStockDomain | 188 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 130 | CapitalExpendituresIncurredButNotYetPaid | 186 | D | C | excluded: supplemental (NONCASH) | credit-typed |  | never capex | explicit |
| 131 | OtherOperatingActivitiesCashFlowStatement | 185 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 132 | AssetImpairmentCharges | 184 | D | D | excluded: component_no_concept | debit |  | never D&A | explicit |
| 133 | OperatingExpenses | 182 | D | D | operating_expenses_resolved | debit | REITs: OHI incl. interest, DOC property-only | not "Total costs and expenses" including COGS | explicit |
| 134 | NetIncomeLossAvailableToCommonStockholdersBasic | 179 | D | C | component of net_income_resolved (nci/preferred) | credit | parent line at ~30 filers with no NetIncomeLoss (CAT, ES) | NI only with no NetIncomeLoss, no preferred line, and ProfitLoss − NCI = it | explicit |
| 135 | DepreciationAndAmortization | 175 | D | D | depreciation_and_amortization_resolved (CF); IS copy is often a sub-line | debit | Kura IS 448K vs CF 14,046K | not the IS sub-line when a CF total exists | explicit |
| 136 | AmortizationOfIntangibleAssets | 175 | D | D | amortization_of_intangibles; component of D&A | debit | HD FY2025+ separate line | never alone as D&A | explicit |
| 137 | IncreaseDecreaseInOtherOperatingLiabilities | 172 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 138 | EarningsPerShareBasicAbstract | 167 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 139 | AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment | 164 | I | C | component of ppe_net_resolved | credit (contra) |  | never | explicit |
| 140 | LiabilitiesAbstract | 163 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 141 | LongTermDebtAndCapitalLeaseObligations | 162 | I | C | component of total_debt_resolved (includes finance leases) | credit | "long-term debt" label at EWBC ZION; BAX only debt tag; capitalization-format utilities | never add note finance leases on top | explicit |
| 142 | PaymentsToAcquireAvailableForSaleSecuritiesDebt | 161 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 143 | CashFlowNoncashInvestingAndFinancingActivitiesDisclosureAbstract | 160 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 144 | IncreaseDecreaseInContractWithCustomerLiability | 160 | D | D | excluded: movement_line | debit-typed |  | never | explicit |
| 145 | DeferredIncomeTaxesAndTaxCredits | 158 | D | D | excluded: component_no_concept | debit-typed |  | never income_tax_expense | explicit |
| 146 | GainLossOnSaleOfBusiness | 155 | D | C | excluded: component_no_concept | credit-typed |  | never revenue | explicit |
| 147 | AccruedIncomeTaxesCurrent | 154 | I | C | excluded: component_no_concept | credit |  | never | explicit |
| 148 | IncreaseDecreaseInAccruedIncomeTaxesPayable | 154 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 149 | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | 152 | I | D | ppe_net_resolved (perimeter flag: incl. finance-lease ROU) | debit |  | never together with PropertyPlantAndEquipmentNet | explicit |
| 150 | ShortTermBorrowings | 149 | I | C | component of total_debt_resolved | credit | DUK "Notes payable and commercial paper"; can equal LongTermDebtCurrent | never add a note CommercialPaper that it already contains | explicit |
| 151 | IncomeLossFromContinuingOperationsPerDilutedShare | 148 | D | — | excluded: per_share_detail | per share | continuing/discontinued EPS split | never total EPS | family |
| 152 | InvestmentIncomeInterest | 148 | D | C | interest_income (NON-banks) | credit | securities line at banks (CCB SFNC CARV FLG); total at BANR FCCO; NII at PEBK | never bank interest income | explicit |
| 153 | IncomeTaxesPaid | 148 | D | C | excluded: supplemental | credit-typed |  | never income tax expense | explicit |
| 154 | IncomeLossFromContinuingOperationsPerBasicShare | 148 | D | — | excluded: per_share_detail | per share | continuing/discontinued EPS split | never total EPS | family |
| 155 | NonoperatingIncomeExpenseAbstract | 147 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 156 | EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | 147 | D | D | excluded: identity_check_line (FX sibling) | debit-typed | MSFT from FY2022, AMZN 2024; CSCO's near-twin DisposalGroupIncluding… | sum every FX-family calc child | explicit |
| 157 | Depreciation | 143 | D | D | component of depreciation_and_amortization_resolved | debit | ArcBest labels it "D&A" | never alone as D&A when amortization is printed | explicit |
| 158 | IncreaseDecreaseInAccruedLiabilities | 142 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 159 | ProceedsFromDivestitureOfBusinesses | 141 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 160 | GainLossOnSaleOfPropertyPlantEquipment | 141 | D | C | excluded: component_no_concept | credit-typed |  | never | explicit |
| 161 | PaymentsToAcquireInvestments | 140 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 162 | RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability | 140 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 163 | CostOfRevenue | 139 | D | D | cost_of_revenue_resolved | debit |  | not CostsAndExpenses | explicit |
| 164 | ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities | 137 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 165 | OtherAssets | 133 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 166 | ShortTermInvestments | 130 | I | D | excluded: component_no_concept | debit | MSFT parenthetical "including securities loaned" (SecuritiesLoaned is NOT debt) | never cash | explicit |
| 167 | AssetsOfDisposalGroupIncludingDiscontinuedOperationCurrent | 129 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 168 | ProceedsFromSaleOfAvailableForSaleSecuritiesDebt | 129 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 169 | RestructuringCharges | 127 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 170 | ComprehensiveIncomeNetOfTax | 125 | D | C | comprehensive_income | credit |  | not the NCI-inclusive total | explicit |
| 171 | LiabilitiesOfDisposalGroupIncludingDiscontinuedOperationCurrent | 125 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 172 | NoncashInvestingAndFinancingItemsAbstract | 125 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 173 | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | 125 | I | D | excluded: identity_check_line | debit |  | never cash_and_equivalents | explicit |
| 174 | EarningsPerShareDilutedAbstract | 125 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 175 | RepaymentsOfLinesOfCredit | 124 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 176 | DebtCurrent | 124 | I | C | component of total_debt_resolved | credit | perimeters: CP + current LTD (CSCO), short-term only (JNJ), leases only (MU), pre-refinancing (CVX FY2016), incl. capital leases (GOOG 2015-18) | classify by identity, never by name | explicit |
| 177 | ProceedsFromLinesOfCredit | 122 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 178 | PaymentForContingentConsiderationLiabilityFinancingActivities | 122 | D | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 179 | GainLossOnDispositionOfAssets1 | 122 | D | C | excluded: component_no_concept | credit-typed; gain positive |  | never revenue | family |
| 180 | PaymentsToAcquireProductiveAssets | 120 | D | C | capex_resolved | credit-typed | may include software and intangibles (Aptiv) | not the discontinued investing block (AMD FY2025) | explicit |
| 181 | InterestIncomeExpenseNet | 119 | D | C | excluded: combined_perimeter (bank NII; no catalog concept) | credit | non-banks: net financing line (ANDE AAON) | never interest_expense | explicit |
| 182 | TreasuryStockShares | 116 | I | — | excluded: per_share_detail | shares |  | never | explicit |
| 183 | InterestIncomeExpenseNonoperatingNet | 116 | D | C | excluded: combined_perimeter | credit | 98 net-only filers in the top 632 latest 10-Ks | never interest_expense | explicit |
| 184 | NetCashProvidedByUsedInOperatingActivitiesContinuingOperationsAbstract | 115 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 185 | ProceedsFromDivestitureOfBusinessesNetOfCashDivested | 114 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 186 | ProvisionForDoubtfulAccounts | 113 | D | D | excluded: component_no_concept | debit |  | never | explicit |
| 187 | GainLossOnInvestments | 113 | D | C | excluded: component_no_concept | credit-typed; gain positive |  | never revenue | family |
| 188 | PaymentsToMinorityShareholders | 112 | D | C | excluded: nci_component | credit-typed |  | never dividends_paid | explicit |
| 189 | FiniteLivedIntangibleAssetsNet | 111 | I | D | excluded: component_no_concept | debit |  | never goodwill | explicit |
| 190 | ProceedsFromIssuanceOfDebt | 110 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 191 | NetCashProvidedByUsedInFinancingActivitiesContinuingOperationsAbstract | 110 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 192 | ProductMember | 108 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 193 | LiabilitiesNoncurrentAbstract | 107 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 194 | NetCashProvidedByUsedInInvestingActivitiesContinuingOperationsAbstract | 106 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 195 | IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest | 106 | D | C | component (nci_component) | credit |  | never NI to parent | explicit |
| 196 | RepaymentsOfDebt | 105 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 197 | ReceivablesNetCurrent | 105 | I | D | accounts_receivable (wider perimeter flag) | debit |  | not when AccountsReceivableNetCurrent is also printed | explicit |
| 198 | LongTermDebtAndCapitalLeaseObligationsCurrent | 103 | I | C | component of total_debt_resolved (incl. leases) | credit |  | never add current finance lease on top | explicit |
| 199 | AmortizationOfFinancingCostsAndDiscounts | 103 | D | D | excluded: component_no_concept | debit | inside DDA by FASB calc at some filers | never D&A | explicit |
| 200 | SellingAndMarketingExpense | 102 | D | D | component of sga_expense | debit |  | never SG&A alone | explicit |
| 201 | FinanceLeasePrincipalPayments | 102 | D | C | excluded: component_no_concept | credit-typed |  | never capex or buybacks | explicit |
| 202 | IncreaseDecreaseInReceivables | 102 | D | C | cf_ar_change (wider perimeter flag) | credit-typed |  | not when …AccountsReceivable is printed | explicit |
| 203 | ProceedsFromSaleOfProductiveAssets | 101 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 204 | EquityMethodInvestments | 98 | I | D | excluded: component_no_concept | debit |  | never | explicit |
| 205 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments | 98 | D | C | income_before_tax_resolved (p20) | credit | MSFT switch Q2 FY2022 | if the other pretax tag is also printed, they differ by equity-method income | explicit |
| 206 | IncomeLossFromDiscontinuedOperationsNetOfTaxPerDilutedShare | 97 | D | — | excluded: per_share_detail | per share | continuing/discontinued EPS split | never total EPS | family |
| 207 | PaymentsOfDividendsMinorityInterest | 97 | D | C | excluded: nci_component | credit-typed |  | never dividends_paid | explicit |
| 208 | IncomeLossFromDiscontinuedOperationsNetOfTaxPerBasicShare | 97 | D | — | excluded: per_share_detail | per share | continuing/discontinued EPS split | never total EPS | family |
| 209 | ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions | 96 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 210 | ContractWithCustomerLiabilityNoncurrent | 95 | I | C | excluded: component_no_concept | credit |  | never debt | explicit |
| 211 | ProceedsFromRepaymentsOfShortTermDebt | 95 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 212 | LiabilitiesNoncurrent | 94 | I | C | excluded: subtotal_not_in_catalog | credit |  | never total liabilities | explicit |
| 213 | CommonStockDividendsPerShareDeclared | 94 | D | — | dividends_per_share_resolved | per share | quarterly rate on annual contexts (V LEA WTRG); MDT on EQ from FY2019 | FY = sum of quarters guard; one basis per company | explicit |
| 214 | OtherOperatingIncomeExpenseNet | 94 | D | C | excluded: component_no_concept | credit |  | never | explicit |
| 215 | PaymentsOfFinancingCosts | 93 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 216 | PaymentsToAcquireIntangibleAssets | 92 | D | C | excluded: component_no_concept | credit-typed | capitalised software at some filers | never capex unless the capex rule includes intangibles by calc | explicit |
| 217 | OperatingLeaseRightOfUseAssetAmortizationExpense | 92 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 218 | PaymentsToAcquireEquityMethodInvestments | 91 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 219 | IncreaseDecreaseInDeferredIncomeTaxes | 91 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 220 | AmortizationOfFinancingCosts | 91 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 221 | CommonClassAMember | 90 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 222 | PaymentsToAcquireMarketableSecurities | 90 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 223 | RedeemableNoncontrollingInterestEquityCarryingAmount | 90 | I | C | excluded: nci_component (mezzanine) | credit | …Common/FairValue/Other variants (MCK IPG ETP) | never permanent equity | explicit |
| 224 | ProceedsFromMinorityShareholders | 90 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 225 | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsAbstract | 89 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 226 | LaborAndRelatedExpense | 89 | D | D | excluded: component_no_concept | debit |  | never | explicit |
| 227 | IncreaseDecreaseInOtherCurrentAssets | 89 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 228 | IncomeLossFromContinuingOperations | 88 | D | C | excluded: subtotal_not_in_catalog | credit |  | never NI (excludes discontinued) | explicit |
| 229 | ProceedsFromSaleAndMaturityOfMarketableSecurities | 87 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 230 | ProceedsFromSaleMaturityAndCollectionsOfInvestments | 86 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 231 | AdjustmentsNoncashItemsToReconcileNetIncomeLossToCashProvidedByUsedInOperatingActivitiesAbstract | 86 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 232 | PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent | 86 | I | C | excluded: component_no_concept | credit |  | never debt | explicit |
| 233 | GoodwillImpairmentLoss | 86 | D | D | excluded: component_no_concept | debit |  | never | explicit |
| 234 | IncreaseDecreaseInOtherNoncurrentAssets | 85 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 235 | OtherLiabilities | 85 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 236 | CommonClassBMember | 85 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 237 | RestrictedCash | 85 | I | D | excluded: component_no_concept | debit |  | never cash_and_equivalents | explicit |
| 238 | AccountsPayableAndAccruedLiabilitiesCurrent | 84 | I | C | excluded: combined_perimeter | credit |  | never accounts_payable | explicit |
| 239 | ServiceMember | 84 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 240 | LongTermDebt | 83 | I | C | component of total_debt_resolved | credit | includes current maturities (CSCO TMO); face value at AMZN GOOG; containment fails at 72 companies | never add LongTermDebtCurrent on top; prefer the carrying face lines | explicit |
| 241 | IncreaseDecreaseInEmployeeRelatedLiabilities | 83 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 242 | ProceedsFromIssuanceOfSeniorLongTermDebt | 83 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 243 | IncomeLossFromDiscontinuedOperationsNetOfTax | 80 | D | C | excluded: component_no_concept | credit |  | never | explicit |
| 244 | CommonStockValueOutstanding | 80 | I | C | component of stockholders_equity | credit |  | never | explicit |
| 245 | PrepaidExpenseCurrent | 80 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 246 | AccretionAmortizationOfDiscountsAndPremiumsInvestments | 80 | D | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 247 | IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity | 80 | D | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 248 | OtherCostAndExpenseOperating | 79 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 249 | ForeignCurrencyTransactionGainLossBeforeTax | 78 | D | C | excluded: component_no_concept | credit |  | never | explicit |
| 250 | RestrictedCashAndCashEquivalents | 77 | I | D | excluded: component_no_concept | debit |  | never cash_and_equivalents | explicit |
| 251 | RestrictedCashAndCashEquivalentsAtCarryingValue | 76 | I | D | excluded: component_no_concept | debit |  | never cash_and_equivalents | explicit |
| 252 | PropertyPlantAndEquipmentGross | 76 | I | D | component of ppe_net_resolved | debit |  | never | explicit |
| 253 | EquityMethodInvestmentDividendsOrDistributions | 76 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 254 | IncreaseDecreaseInOperatingLeaseLiability | 75 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 255 | DepreciationAmortizationAndAccretionNet | 75 | D | D | depreciation_and_amortization_resolved (perimeter flag) | debit | KEY "…, net" nets below intangible amortization: held | not when "net" nets accretion against D&A | explicit |
| 256 | BusinessCombinationContingentConsiderationArrangementsChangeInAmountOfContingentConsiderationLiability1 | 74 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 257 | PaymentsToAcquireShortTermInvestments | 74 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 258 | RepaymentsOfSeniorDebt | 74 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 259 | RepaymentsOfShortTermDebt | 73 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 260 | IncreaseDecreaseInOtherNoncurrentLiabilities | 73 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 261 | PaymentsOfDebtExtinguishmentCosts | 73 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 262 | StockIssued1 | 72 | D | C | excluded: supplemental (noncash stock issued) | credit |  | never | explicit |
| 263 | WeightedAverageNumberOfSharesOutstandingDilutedDisclosureItemsAbstract | 72 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 264 | CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect | 71 | D | D | excluded: identity_check_line | debit |  | never | explicit |
| 265 | RestrictedCashCurrent | 71 | I | D | excluded: component_no_concept | debit |  | never cash_and_equivalents | explicit |
| 266 | ProceedsFromEquityMethodInvestmentDividendsOrDistributionsReturnOfCapital | 70 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 267 | ConsolidatedEntitiesDomain | 70 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 268 | ConsolidatedEntitiesAxis | 70 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 269 | PreferredStockDividendsIncomeStatementImpact | 70 | D | D | excluded: nci_component | debit | its presence blocks the NIACSB-as-NI rule | never | explicit |
| 270 | ProceedsFromLongTermLinesOfCredit | 69 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 271 | PaymentsToAcquireOtherInvestments | 69 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 272 | AssetsNoncurrentAbstract | 69 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 273 | ProceedsFromShortTermDebt | 69 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 274 | CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations | 69 | D | D | component of cfo_resolved (discontinued) | debit | AMD 1,216 | never alone as CFO | explicit |
| 275 | CostOfRevenueAbstract | 67 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 276 | NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | 66 | D | — | cfo_resolved (only without a total line) | — | the only CFO line at MSFT FY2014-18 and many others | never when the total is printed (AMD) | explicit |
| 277 | PaymentsOfDividendsPreferredStockAndPreferenceStock | 66 | D | C | excluded: nci_component (preferred) | credit-typed |  | never common dividends | explicit |
| 278 | InterestExpenseOperating | 65 | D | D | interest_expense_resolved | debit | banks 2024+ (pair with InterestExpense); HTZ/MTZ "…, net" at non-banks | "…, net" label at non-banks; under NonoperatingIncomeExpense = wrong element (DQC_0181) | explicit |
| 279 | IncreaseDecreaseInDeferredRevenue | 65 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 280 | IncomeTaxesReceivable | 65 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 281 | OtherAccruedLiabilitiesCurrent | 65 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 282 | ProceedsFromStockPlans | 64 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 283 | RevenueFromContractWithCustomerIncludingAssessedTax | 63 | D | C | revenue_sanity_resolved | credit | excise pair with …Excluding (14693 Sales 5,082 vs Net sales 3,928) | take "Net sales" (Excluding) in an excise pair | explicit |
| 284 | IncreaseDecreaseInAccountsPayableTrade | 62 | D | D | cf_ap_change | debit-typed |  | never the combined AP+accrued | explicit |
| 285 | RepaymentsOfLongTermLinesOfCredit | 62 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 286 | InvestmentsInAffiliatesSubsidiariesAssociatesAndJointVentures | 62 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 287 | LiabilitiesOfDisposalGroupIncludingDiscontinuedOperationNoncurrent | 61 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 288 | RelatedPartyDomain | 61 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 289 | RelatedPartyTransactionsByRelatedPartyAxis | 61 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 290 | MarketableSecuritiesCurrent | 60 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 291 | ProceedsFromRepaymentsOfCommercialPaper | 60 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 292 | TaxesPayableCurrent | 59 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 293 | DisposalGroupIncludingDiscontinuedOperationAssetsNoncurrent | 59 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 294 | RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability | 58 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 295 | LongTermInvestments | 57 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 296 | AccruedIncomeTaxesNoncurrent | 57 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 297 | IncreaseDecreaseInContractWithCustomerAsset | 57 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 298 | CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations | 57 | D | D | component of cash_flow_investing_resolved | debit |  | never | explicit |
| 299 | Investments | 57 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 300 | IncomeLossFromEquityMethodInvestmentsNetOfDividendsOrDistributions | 56 | D | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 301 | ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities | 56 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 302 | RelatedPartyMember | 56 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 303 | RestrictedCashNoncurrent | 55 | I | D | excluded: component_no_concept | debit |  | never cash_and_equivalents | explicit |
| 304 | NetCashProvidedByUsedInInvestingActivitiesContinuingOperations | 55 | D | D | cash_flow_investing_resolved (only without a total line) | debit |  | as CFO | explicit |
| 305 | DeferredRevenueCurrent | 55 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 306 | InterestPayableCurrent | 54 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 307 | ProceedsFromSaleOfEquityMethodInvestments | 54 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 308 | IncreaseDecreaseInOperatingCapital | 54 | D | C | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 309 | PaymentsToAcquireHeldToMaturitySecurities | 53 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 310 | ContractWithCustomerAssetNetCurrent | 52 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 311 | OccupancyNet | 52 | D | D | excluded: component_no_concept (bank) | debit |  | never | explicit |
| 312 | IncreaseDecreaseInAccruedLiabilitiesAndOtherOperatingLiabilities | 52 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 313 | AvailableForSaleSecuritiesDebtSecuritiesCurrent | 51 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 314 | RepaymentsOfOtherLongTermDebt | 51 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 315 | UnrealizedGainLossOnDerivatives | 51 | D | C | excluded: component_no_concept | credit-typed; gain positive |  | never revenue | family |
| 316 | VariableInterestEntityPrimaryBeneficiaryMember | 51 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 317 | CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization | 50 | D | D | component of cost_of_revenue_resolved (perimeter pending) | debit | 36 latest 10-Ks | do not serve as cost_of_revenue until the excl-D&A ruling | explicit |
| 318 | ProceedsFromSaleOfEquitySecuritiesFvNi | 50 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 319 | RepaymentsOfConvertibleDebt | 50 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 320 | AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | 50 | I | C | excluded: combined_perimeter | credit |  | never accounts_payable | explicit |
| 321 | DividendsPayableCurrent | 50 | I | C | excluded: component_no_concept | credit |  | never dividends_paid | explicit |
| 322 | IncreaseDecreaseInAccountsAndOtherReceivables | 50 | D | C | cf_ar_change (wider perimeter flag) | credit-typed |  | as IncreaseDecreaseInReceivables | explicit |
| 323 | ProceedsFromMaturitiesPrepaymentsAndCallsOfHeldToMaturitySecurities | 49 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 324 | EquityComponentDomain | 49 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 325 | StatementEquityComponentsAxis | 49 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 326 | BusinessCombinationAcquisitionRelatedCosts | 48 | D | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 327 | RepaymentsOfLongTermDebtAndCapitalSecurities | 48 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 328 | OtherIncome | 48 | D | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 329 | UnrealizedGainLossOnInvestments | 48 | D | C | excluded: component_no_concept | credit-typed; gain positive |  | never revenue | family |
| 330 | CommonStockMember | 48 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 331 | ProceedsFromIssuanceOfPreferredStockAndPreferenceStock | 48 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 332 | PaymentsToAcquireBusinessesGross | 48 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 333 | InterestAndDividendIncomeOperating | 48 | D | C | interest_income (bank total interest income) | credit | insurer investment income (PGR): not a bank detector | never with InvestmentIncomeInterest at banks | explicit |
| 334 | NoninterestExpense | 47 | D | D | excluded: component_no_concept (bank template) | debit |  | never operating_expenses without the bank template | explicit |
| 335 | FinanceLeaseLiabilityNoncurrent | 47 | I | C | component of total_debt_resolved (finance leases per founder ruling) | credit | META FY2019 context error (2019 value on 2018-12-31) | never when the debt tag already includes leases | explicit |
| 336 | LegalEntityAxis | 47 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 337 | EntityDomain | 47 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 338 | ProceedsFromRepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess | 47 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 339 | BusinessAcquisitionAxis | 46 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 340 | BusinessAcquisitionAcquireeDomain | 46 | — | — | dimension structure | — |  | dimension structure (axis/domain/member): never a line value by itself; a face fact on a member is a per-member breakdown, the non-dimensional (dim_id = 0) fact is the total | family |
| 341 | PaymentsForRepurchaseOfRedeemableNoncontrollingInterest | 46 | D | C | excluded: nci_component | credit-typed |  | never share_buybacks | explicit |
| 342 | DisposalGroupNotDiscontinuedOperationGainLossOnDisposal | 46 | D | C | excluded: component_no_concept | credit-typed; gain positive |  | never revenue | family |
| 343 | NoninterestExpenseAbstract | 45 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 344 | RepaymentsOfSecuredDebt | 45 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 345 | InventoryWriteDown | 45 | D | D | excluded: component_no_concept | debit |  | never | explicit |
| 346 | AdjustmentForAmortization | 45 | D | D | component of depreciation_and_amortization_resolved | debit | AMD 2,254 = intangible amortization (COGS 1,031 + opex 1,223); can include financing-cost/DAC/MSR amortization (FASB) | check what it amortizes | explicit |
| 347 | ProceedsFromInsuranceSettlementInvestingActivities | 45 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 348 | IncreaseDecreaseInOtherCurrentLiabilities | 45 | D | D | excluded: movement_line | debit/credit per element: credit-typed asset changes are positive when the asset DECREASES |  | no concept (except AR/AP/inventory rows) | family |
| 349 | ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest | 44 | D | C | component of comprehensive_income (nci) | credit |  | never comprehensive_income to parent | explicit |
| 350 | PropertyPlantAndEquipmentNetAbstract | 44 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 351 | PaymentsToAcquireEquitySecuritiesFvNi | 44 | D | C | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 352 | ProceedsFromSaleAndMaturityOfOtherInvestments | 44 | D | D | excluded: component_no_concept (cash-flow detail) | receipt = debit-typed, payment = credit-typed; stored positive |  | never capex, buybacks or dividends unless named in their cards | family |
| 353 | OtherNoninterestExpense | 44 | D | D | excluded: component_no_concept | debit |  | never | explicit |
| 354 | GainLossOnDispositionOfAssets | 43 | D | C | excluded: component_no_concept | credit-typed; gain positive |  | never revenue | family |
| 355 | PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAccumulatedDepreciationAndAmortization | 43 | I | C | excluded: component_no_concept |  |  | no catalog concept | family |
| 356 | AvailableForSaleSecuritiesDebtSecurities | 43 | I | D | excluded: component_no_concept |  |  | no catalog concept | family |
| 357 | OtherComprehensiveIncomeLossNetOfTaxPeriodIncreaseDecreaseAbstract | 43 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |
| 358 | Deposits | 43 | I | C | excluded: component_no_concept (bank deposits) | credit | customer deposits at FCX ZBRA CPAY WEX | never debt; not a bank test | explicit |
| 359 | EquityAbstract | 43 | — | — | abstract (structure) | — |  | abstract heading: no value; structural status "abstract" | family |

Explicit: 105; family: 159.
