# Rules: bs (GENERATED from rules/bs.csv and exam/results/ledger.csv — do not edit by hand)

168 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## (structural)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.LiabilitiesAndStockholdersEquity | tag | all | `{"stmt":"BS","tag":"LiabilitiesAndStockholdersEquity","order":2}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"identity_check_line"}` | explicit | 0 | 0 |  |
| lib.bs.OtherAssetsNoncurrent | tag | all | `{"stmt":"BS","tag":"OtherAssetsNoncurrent","order":23}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OtherLiabilitiesNoncurrent | tag | all | `{"stmt":"BS","tag":"OtherLiabilitiesNoncurrent","order":26}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.CommitmentsAndContingencies | tag | all | `{"stmt":"BS","tag":"CommitmentsAndContingencies","order":34}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"caption"}` | explicit | 0 | 0 |  |
| lib.bs.IntangibleAssetsNetExcludingGoodwill | tag | all | `{"stmt":"BS","tag":"IntangibleAssetsNetExcludingGoodwill","order":41}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.MinorityInterest | tag | all | `{"stmt":"BS","tag":"MinorityInterest","order":45}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"nci_component"}` | balance-sheet-equity-inventory-other.md §1 | 0 | 0 |  |
| lib.bs.OtherAssetsCurrent | tag | all | `{"stmt":"BS","tag":"OtherAssetsCurrent","order":76}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.PrepaidExpenseAndOtherAssetsCurrent | tag | all | `{"stmt":"BS","tag":"PrepaidExpenseAndOtherAssetsCurrent","order":78}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OtherLiabilitiesCurrent | tag | all | `{"stmt":"BS","tag":"OtherLiabilitiesCurrent","order":79}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.EmployeeRelatedLiabilitiesCurrent | tag | all | `{"stmt":"BS","tag":"EmployeeRelatedLiabilitiesCurrent","order":88}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.AccruedLiabilitiesCurrent | tag | all | `{"stmt":"BS","tag":"AccruedLiabilitiesCurrent","order":91}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.DeferredIncomeTaxLiabilitiesNet | tag | all | `{"stmt":"BS","tag":"DeferredIncomeTaxLiabilitiesNet","order":97}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.DeferredIncomeTaxAssetsNet | tag | all | `{"stmt":"BS","tag":"DeferredIncomeTaxAssetsNet","order":110}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.ShortTermInvestments | tag | all | `{"stmt":"BS","tag":"ShortTermInvestments","order":115}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.AccruedIncomeTaxesCurrent | tag | all | `{"stmt":"BS","tag":"AccruedIncomeTaxesCurrent","order":116}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OperatingLeaseRightOfUseAsset | tag | all | `{"stmt":"BS","tag":"OperatingLeaseRightOfUseAsset","order":127}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | debt.md | 0 | 0 |  |
| lib.bs.ContractWithCustomerLiabilityCurrent | tag | all | `{"stmt":"BS","tag":"ContractWithCustomerLiabilityCurrent","order":132}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OperatingLeaseLiabilityNoncurrent | tag | all | `{"stmt":"BS","tag":"OperatingLeaseLiabilityNoncurrent","order":135}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | debt.md | 0 | 0 |  |
| lib.bs.LongTermInvestments | tag | all | `{"stmt":"BS","tag":"LongTermInvestments","order":145}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.DeferredRevenueCurrent | tag | all | `{"stmt":"BS","tag":"DeferredRevenueCurrent","order":146}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.DeferredTaxLiabilitiesNoncurrent | tag | all | `{"stmt":"BS","tag":"DeferredTaxLiabilitiesNoncurrent","order":151}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.AccruedIncomeTaxesNoncurrent | tag | all | `{"stmt":"BS","tag":"AccruedIncomeTaxesNoncurrent","order":155}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OtherAssets | tag | all | `{"stmt":"BS","tag":"OtherAssets","order":159}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.MarketableSecuritiesCurrent | tag | all | `{"stmt":"BS","tag":"MarketableSecuritiesCurrent","order":168}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent | tag | all | `{"stmt":"BS","tag":"PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent","order":171}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.AccountsPayableAndAccruedLiabilitiesCurrent | tag | all | `{"stmt":"BS","tag":"AccountsPayableAndAccruedLiabilitiesCurrent","order":186}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"combined_perimeter"}` | explicit | 8 | 0 | 100.0% |
| lib.bs.ReceivablesNetCurrent | tag | all | `{"stmt":"BS","tag":"ReceivablesNetCurrent","order":190}` | `{"decision":"combined","concept":"","parent_concept":"","reason_class":"line_presented_combined_with` | fsn-balance-sheet-assets.md | 15 | 5 | 66.7% |
| lib.bs.RedeemableNoncontrollingInterestEquityCarryingAmount | tag | all | `{"stmt":"BS","tag":"RedeemableNoncontrollingInterestEquityCarryingAmount","order":206}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"nci_component"}` | balance-sheet-equity-inventory-other.md §1 | 0 | 0 |  |
| lib.bs.LiabilitiesNoncurrent | tag | all | `{"stmt":"BS","tag":"LiabilitiesNoncurrent","order":213}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"subtotal_not_in_catalog"}` | explicit | 0 | 0 |  |
| lib.bs.DividendsPayableCurrent | tag | all | `{"stmt":"BS","tag":"DividendsPayableCurrent","order":214}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.EquityMethodInvestments | tag | all | `{"stmt":"BS","tag":"EquityMethodInvestments","order":216}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OperatingLeaseLiabilityCurrent | tag | all | `{"stmt":"BS","tag":"OperatingLeaseLiabilityCurrent","order":217}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | debt.md | 0 | 0 |  |
| lib.bs.Deposits | tag | all | `{"stmt":"BS","tag":"Deposits","order":218}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | interest.md §7 | 0 | 0 |  |
| lib.bs.FiniteLivedIntangibleAssetsNet | tag | all | `{"stmt":"BS","tag":"FiniteLivedIntangibleAssetsNet","order":220}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.OtherLiabilities | tag | all | `{"stmt":"BS","tag":"OtherLiabilities","order":224}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.DeferredTaxAssetsNetNoncurrent | tag | all | `{"stmt":"BS","tag":"DeferredTaxAssetsNetNoncurrent","order":236}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.DeferredRevenueNoncurrent | tag | all | `{"stmt":"BS","tag":"DeferredRevenueNoncurrent","order":237}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.ContractWithCustomerLiabilityNoncurrent | tag | all | `{"stmt":"BS","tag":"ContractWithCustomerLiabilityNoncurrent","order":248}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.InvestmentsInAffiliatesSubsidiariesAssociatesAndJointVentures | tag | all | `{"stmt":"BS","tag":"InvestmentsInAffiliatesSubsidiariesAssociatesAndJointVentures","order":267}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.AvailableForSaleSecuritiesDebtSecuritiesCurrent | tag | all | `{"stmt":"BS","tag":"AvailableForSaleSecuritiesDebtSecuritiesCurrent","order":269}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.DeferredTaxAssetsNetCurrent | tag | all | `{"stmt":"BS","tag":"DeferredTaxAssetsNetCurrent","order":272}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.TaxesPayableCurrent | tag | all | `{"stmt":"BS","tag":"TaxesPayableCurrent","order":280}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.NotesAndLoansReceivableNetNoncurrent | tag | all | `{"stmt":"BS","tag":"NotesAndLoansReceivableNetNoncurrent","order":287}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | bank-loans-and-allowance.md | 0 | 0 |  |
| lib.bs.AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | tag | all | `{"stmt":"BS","tag":"AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent","order":289}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"combined_perimeter"}` | explicit | 9 | 5 | 44.4% |
| lib.bs.Investments | tag | all | `{"stmt":"BS","tag":"Investments","order":293}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OtherAccruedLiabilitiesCurrent | tag | all | `{"stmt":"BS","tag":"OtherAccruedLiabilitiesCurrent","order":302}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.AvailableForSaleSecuritiesCurrent | tag | all | `{"stmt":"BS","tag":"AvailableForSaleSecuritiesCurrent","order":305}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.MarketableSecuritiesNoncurrent | tag | all | `{"stmt":"BS","tag":"MarketableSecuritiesNoncurrent","order":306}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OtherReceivablesNetCurrent | tag | all | `{"stmt":"BS","tag":"OtherReceivablesNetCurrent","order":309}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | Dhairya document-first reads ranks 85-100, 2026-11-12, FILING-CHECKED | 0 | 0 |  |
| lib.bs.PrepaidExpenseCurrent | tag | all | `{"stmt":"BS","tag":"PrepaidExpenseCurrent","order":317}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | tag | all | `{"stmt":"BS","tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents","order":322}` | `{"decision":"combined","concept":"","parent_concept":"","reason_class":"line_presented_combined_with` | fsn-balance-sheet-assets.md; cash.md | 5 | 3 | 40.0% |
| lib.bs.DefinedBenefitPensionPlanLiabilitiesNoncurrent | tag | all | `{"stmt":"BS","tag":"DefinedBenefitPensionPlanLiabilitiesNoncurrent","order":323}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.NotesAndLoansReceivableNetCurrent | tag | all | `{"stmt":"BS","tag":"NotesAndLoansReceivableNetCurrent","order":324}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | bank-loans-and-allowance.md | 0 | 0 |  |
| lib.bs.LoansAndLeasesReceivableNetReportedAmount | tag | all | `{"stmt":"BS","tag":"LoansAndLeasesReceivableNetReportedAmount","order":330}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | bank-loans-and-allowance.md | 0 | 0 |  |
| lib.bs.AssetsOfDisposalGroupIncludingDiscontinuedOperationCurrent | tag | all | `{"stmt":"BS","tag":"AssetsOfDisposalGroupIncludingDiscontinuedOperationCurrent","order":333}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.OtherReceivables | tag | all | `{"stmt":"BS","tag":"OtherReceivables","order":336}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | MS 0000895421-26-000086 BS (FSN store; Dhairya full-10-K read 2026-11-11) | 0 | 0 |  |
| lib.bs.AssetsNoncurrent | tag | all | `{"stmt":"BS","tag":"AssetsNoncurrent","order":344}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"subtotal_not_in_catalog"}` | explicit | 0 | 0 |  |
| lib.bs.OtherPostretirementDefinedBenefitPlanLiabilitiesNoncurrent | tag | all | `{"stmt":"BS","tag":"OtherPostretirementDefinedBenefitPlanLiabilitiesNoncurrent","order":353}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.LiabilitiesOfDisposalGroupIncludingDiscontinuedOperationCurrent | tag | all | `{"stmt":"BS","tag":"LiabilitiesOfDisposalGroupIncludingDiscontinuedOperationCurrent","order":355}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.ContractWithCustomerAssetNetCurrent | tag | all | `{"stmt":"BS","tag":"ContractWithCustomerAssetNetCurrent","order":357}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.SalesAndExciseTaxPayableCurrent | tag | all | `{"stmt":"BS","tag":"SalesAndExciseTaxPayableCurrent","order":362}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.AvailableForSaleSecuritiesDebtSecurities | tag | all | `{"stmt":"BS","tag":"AvailableForSaleSecuritiesDebtSecurities","order":365}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.CashCashEquivalentsAndShortTermInvestments | tag | all | `{"stmt":"BS","tag":"CashCashEquivalentsAndShortTermInvestments","order":368}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"combined_perimeter"}` | cash.md | 0 | 0 |  |
| lib.bs.CommonStockSharesIssued | tag | all | `{"stmt":"BS","tag":"CommonStockSharesIssued","order":373}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"per_share_detail"}` | shares_outstanding playbook | 0 | 0 |  |
| lib.bs.FederalFundsSoldAndSecuritiesPurchasedUnderAgreementsToResell | tag | all | `{"stmt":"BS","tag":"FederalFundsSoldAndSecuritiesPurchasedUnderAgreementsToResell","order":374}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.TradingLiabilities | tag | all | `{"stmt":"BS","tag":"TradingLiabilities","order":375}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent | tag | all | `{"stmt":"BS","tag":"DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent","order":376}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.OtherLongTermInvestments | tag | all | `{"stmt":"BS","tag":"OtherLongTermInvestments","order":378}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.NotesReceivableNet | tag | all | `{"stmt":"BS","tag":"NotesReceivableNet","order":381}` | `{"decision":"component","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | bank-loans-and-allowance.md | 0 | 0 |  |
| lib.bs.AccruedLiabilitiesAndOtherLiabilities | tag | all | `{"stmt":"BS","tag":"AccruedLiabilitiesAndOtherLiabilities","order":387}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.TradingSecurities | tag | all | `{"stmt":"BS","tag":"TradingSecurities","order":388}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | pattern | 0 | 0 |  |
| lib.bs.IndefiniteLivedLicenseAgreements | tag | all | `{"stmt":"BS","tag":"IndefiniteLivedLicenseAgreements","order":391}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"component_no_concept"}` | explicit | 0 | 0 |  |
| lib.bs.IntangibleAssetsNetIncludingGoodwill | tag | all | `{"stmt":"BS","tag":"IntangibleAssetsNetIncludingGoodwill","order":446}` | `{"decision":"combined","concept":"","parent_concept":"","reason_class":"line_presented_combined_with` | fsn-balance-sheet-assets.md | 7 | 4 | 42.9% |
| lib.bs.Payables | tag | all | `{"stmt":"BS","tag":"Payables","order":451}` | `{"decision":"combined","concept":"","parent_concept":"","reason_class":"line_presented_combined_with` | MS 0000895421-26-000086 BS (FSN store; Dhairya full-10-K read 2026-11-11) | 0 | 0 |  |
| lib.bs.AccountsAndOtherReceivablesNetCurrent | tag | all | `{"stmt":"BS","tag":"AccountsAndOtherReceivablesNetCurrent","order":460}` | `{"decision":"combined","concept":"","parent_concept":"","reason_class":"line_presented_combined_with` | Dhairya document-first reads ranks 85-100, 2026-11-12, FILING-CHECKED | 2 | 1 | 50.0% |
| lib.bs.CommonStockParOrStatedValuePerShare | tag | all | `{"stmt":"BS","tag":"CommonStockParOrStatedValuePerShare","order":464}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"share_terms_parenthetical"}` | Dhairya / Engineering expander request 2026-11-12 | 0 | 0 |  |
| lib.bs.PreferredStockSharesAuthorized | tag | all | `{"stmt":"BS","tag":"PreferredStockSharesAuthorized","order":465}` | `{"decision":"excluded","concept":"","parent_concept":"","reason_class":"share_terms_parenthetical"}` | Dhairya / Engineering expander request 2026-11-12 | 0 | 0 |  |
| bs.detect_classified | sector_detect | all | `{"any_of":["AssetsCurrent"]}` | `{"group":"classified_bs"}` | balance-sheet card (unclassified BS) | 0 | 0 |  |
| bs.current.unclassified | unclassified_np | all | `{}` | `{"data_points":["current_assets","current_liabilities"],"status":"not_presented"}` | doc 02 2026-11-01 item 4 (no derived instants) | 24 | 4 | 83.3% |

## accounts_payable

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.AccountsPayableCurrent | tag | all | `{"stmt":"BS","tag":"AccountsPayableCurrent","order":33}` | `{"decision":"map","concept":"accounts_payable","parent_concept":"","reason_class":""}` | Data Verifier docmaps ranks 51-67, 2026-11-12, FILING-CHECKED | 67 | 0 | 100.0% |
| lib.bs.AccountsPayableTradeCurrent | tag | all | `{"stmt":"BS","tag":"AccountsPayableTradeCurrent","order":448}` | `{"decision":"map","concept":"accounts_payable","parent_concept":"","reason_class":""}` | Dhairya full 10-K reads 2026-11-11 (24 top-50 cos, FILING-CHECKED); balance-sheet §8 | 6 | 0 | 100.0% |
| lib.bs.AccountsPayableCurrentAndNoncurrent | tag | all | `{"stmt":"BS","tag":"AccountsPayableCurrentAndNoncurrent","order":468}` | `{"decision":"map","concept":"accounts_payable","parent_concept":"","reason_class":""}` | blind/dev reads 2026-11-12 (keyed mapped by readers) | 3 | 0 | 100.0% |
| nd.AccountsPayableAndOtherAccruedLiabilitiesCurrent | combined_concept | all | `{"tag":"AccountsPayableAndOtherAccruedLiabilitiesCurrent","order":31}` | `{"data_point":"accounts_payable","members":"accounts_payable:+1 (the AccountsPayableCurrent child or` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 2 | 0 | 100.0% |
| nd.AccountsPayableAndAccruedLiabilitiesCurrent | combined_concept | all | `{"tag":"AccountsPayableAndAccruedLiabilitiesCurrent","order":56}` | `{"data_point":"accounts_payable","members":"accounts_payable:+1 (the AccountsPayableCurrent child or` | needs-detail-answers-r1r2.csv (ranks_1_50.csv:library) | 8 | 0 | 100.0% |
| nd.AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent | combined_concept | all | `{"tag":"AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent","order":67}` | `{"data_point":"accounts_payable","members":"accounts_payable:+1 (the AccountsPayableCurrent child or` | needs-detail-answers-r1r2.csv (ranks_1_50.csv:library) | 9 | 5 | 44.4% |
| template.accounts_payable | data_point | all | `{"order":0}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bs.accounts_payable.label_demote | label_demote | all | `{"label_regex":"(?i)accrued\|and other"}` | `{"decision":"combined"}` | doc 02 2026-11-01 item 2: a label may demote, never promote | 0 | 0 |  |

## accounts_receivable

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.AccountsReceivableNetCurrent | tag | all | `{"stmt":"BS","tag":"AccountsReceivableNetCurrent","order":37}` | `{"decision":"map","concept":"accounts_receivable","parent_concept":"","reason_class":""}` | explicit | 56 | 1 | 98.2% |
| lib.bs.AccountsNotesAndLoansReceivableNetCurrent | tag | all | `{"stmt":"BS","tag":"AccountsNotesAndLoansReceivableNetCurrent","order":383}` | `{"decision":"map","concept":"accounts_receivable","parent_concept":"","reason_class":""}` | explicit | 5 | 4 | 20.0% |
| lib.bs.AccountsReceivableNet | tag | all | `{"stmt":"BS","tag":"AccountsReceivableNet","order":467}` | `{"decision":"map","concept":"accounts_receivable","parent_concept":"","reason_class":""}` | blind/dev reads 2026-11-12 (keyed mapped by readers) | 6 | 2 | 66.7% |
| nd.ReceivablesNetCurrent | combined_concept | all | `{"tag":"ReceivablesNetCurrent","order":1}` | `{"data_point":"accounts_receivable","members":"accounts_receivable:+1 (the AccountsReceivableNetCurr` | needs-detail-answers-r1r2.csv (tag-card) | 15 | 5 | 66.7% |
| nd.AccountsAndOtherReceivablesNetCurrent | combined_concept | all | `{"tag":"AccountsAndOtherReceivablesNetCurrent","order":12}` | `{"data_point":"accounts_receivable","members":"accounts_receivable:+1 (the AccountsReceivableNetCurr` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 2 | 1 | 50.0% |
| nd.AccountsNotesAndLoansReceivableNetCurrent | combined_concept | all | `{"tag":"AccountsNotesAndLoansReceivableNetCurrent","order":33}` | `{"data_point":"accounts_receivable","members":"accounts_receivable:+1 (the AccountsReceivableNetCurr` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.AccountsReceivableNetCurrent | combined_concept | all | `{"tag":"AccountsReceivableNetCurrent","order":69}` | `{"data_point":"accounts_receivable","members":"accounts_receivable:+1 (the AccountsReceivableNetCurr` | needs-detail-answers-r1r2.csv (ranks_1_50.csv:library) | 0 | 0 |  |
| template.accounts_receivable | data_point | all | `{"order":1}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bs.accounts_receivable.label_demote | label_demote | all | `{"label_regex":"(?i)and other\|notes\|other receivable"}` | `{"decision":"combined"}` | doc 02 2026-11-01 item 2 (label demotes only) | 6 | 6 | 0.0% |
| bs.accounts_receivable.single_line | procedure | all | `{"receivable_label":"(?i)receivable","exclude_label":"(?i)allowance\|noncurrent\|non-current\|long-term","wider_label":"(?i)\\band\\b\|other` | `{"procedure":"bs.accounts_receivable.single_line"}` | Dhairya AR override rule 2026-11-12; doc 02 item 2 | 23 | 12 | 47.8% |

## cash_and_equivalents

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.CashAndCashEquivalentsAtCarryingValue | tag | all | `{"stmt":"BS","tag":"CashAndCashEquivalentsAtCarryingValue","order":12}` | `{"decision":"map","concept":"cash_and_equivalents_resolved","parent_concept":"","reason_class":""}` | cash.md | 87 | 1 | 98.9% |
| lib.bs.CashAndDueFromBanks | tag | all | `{"stmt":"BS","tag":"CashAndDueFromBanks","order":279}` | `{"decision":"component","concept":"","parent_concept":"cash_and_equivalents_resolved","reason_class"` | cash.md; Dhairya full 10-K reads (12 cos) 2026-11-12, FILING-CHECKED | 0 | 0 |  |
| lib.bs.InterestBearingDepositsInBanks | tag | all | `{"stmt":"BS","tag":"InterestBearingDepositsInBanks","order":295}` | `{"decision":"component","concept":"","parent_concept":"cash_and_equivalents_resolved","reason_class"` | cash.md | 0 | 0 |  |
| lib.bs.Cash | tag | all | `{"stmt":"BS","tag":"Cash","order":459}` | `{"decision":"map","concept":"cash_and_equivalents_resolved","parent_concept":"","reason_class":""}` | Dhairya document-first reads ranks 85-100, 2026-11-12, FILING-CHECKED | 3 | 0 | 100.0% |
| nd.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | combined_concept | all | `{"tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents","order":51}` | `{"data_point":"cash_and_equivalents","members":"cash_and_equivalents_resolved:+1 (CashAndCashEquival` | needs-detail-answers-r1r2.csv (companies-101-200-exceptions-2026-11-11.csv) | 5 | 3 | 40.0% |
| nd.CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | combined_concept | all | `{"tag":"CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations","order":71}` | `{"data_point":"cash_and_equivalents","members":"cash_and_equivalents_resolved:+1 (CashAndCashEquival` | needs-detail-answers-r1r2.csv (companies-101-200-exceptions-2026-11-11.csv) | 0 | 0 |  |
| nd.CashCashEquivalentsAndRestrictedCashAtCarryingValue | combined_concept | all | `{"tag":"CashCashEquivalentsAndRestrictedCashAtCarryingValue","order":104}` | `{"data_point":"cash_and_equivalents","members":"cash_and_equivalents_resolved:+1 (CashAndCashEquival` | needs-detail-answers-r1r2.csv (companies-201-300-exceptions-2026-11-11.csv) | 0 | 0 |  |
| nd.CashAndCashEquivalentsAtCarryingValueAndRestrictedCashAndCashEquivalentsCurrent | combined_concept | all | `{"tag":"CashAndCashEquivalentsAtCarryingValueAndRestrictedCashAndCashEquivalentsCurrent","order":105}` | `{"data_point":"cash_and_equivalents","members":"cash_and_equivalents_resolved:+1 (CashAndCashEquival` | needs-detail-answers-r1r2.csv (companies-201-300-exceptions-2026-11-11.csv) | 0 | 0 |  |
| nd.RestrictedCashAndCashEquivalents | combined_concept | all | `{"tag":"RestrictedCashAndCashEquivalents","order":133}` | `{"data_point":"cash_and_equivalents","members":"cash_and_equivalents_resolved:+1 (CashAndCashEquival` | needs-detail-answers-r1r2.csv (companies-201-300-exceptions-2026-11-11.csv) | 1 | 1 | 0.0% |
| template.cash_and_equivalents | data_point | all | `{"order":5}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bs.cash_and_equivalents.label_demote | label_demote | all | `{"label_regex":"(?i)restricted"}` | `{"decision":"combined"}` | cash.md; Dhairya CB ruling | 1 | 1 | 0.0% |

## current_assets

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.AssetsCurrent | tag | all | `{"stmt":"BS","tag":"AssetsCurrent","order":19}` | `{"decision":"map","concept":"current_assets_resolved","parent_concept":"","reason_class":""}` | balance-sheet-equity-inventory-other.md §2 | 84 | 0 | 100.0% |
| template.current_assets | data_point | all | `{"order":16}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## current_liabilities

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.LiabilitiesCurrent | tag | all | `{"stmt":"BS","tag":"LiabilitiesCurrent","order":18}` | `{"decision":"map","concept":"current_liabilities_resolved","parent_concept":"","reason_class":""}` | explicit | 83 | 0 | 100.0% |
| template.current_liabilities | data_point | all | `{"order":17}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## goodwill

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.Goodwill | tag | all | `{"stmt":"BS","tag":"Goodwill","order":16}` | `{"decision":"map","concept":"goodwill","parent_concept":"","reason_class":""}` | fsn-line-to-concept.md §A | 85 | 1 | 98.8% |
| nd.IntangibleAssetsNetIncludingGoodwill | combined_concept | all | `{"tag":"IntangibleAssetsNetIncludingGoodwill","order":3}` | `{"data_point":"goodwill","members":"goodwill:+1 (the Goodwill fact of the same filing) ; intangibles` | needs-detail-answers-r1r2.csv (tag-card) | 7 | 4 | 42.9% |
| template.goodwill | data_point | all | `{"order":23}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bs.goodwill.label_demote | label_demote | all | `{"label_regex":"(?i)intangible"}` | `{"decision":"combined"}` | doc 02 2026-11-01 item 2: a label may demote, never promote | 1 | 1 | 0.0% |

## inventory

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.InventoryNet | tag | all | `{"stmt":"BS","tag":"InventoryNet","order":35}` | `{"decision":"map","concept":"inventory","parent_concept":"","reason_class":""}` | balance-sheet-equity-inventory-other.md §2 | 60 | 0 | 100.0% |
| lib.bs.InventoryFinishedGoodsNetOfReserves | tag | all | `{"stmt":"BS","tag":"InventoryFinishedGoodsNetOfReserves","order":326}` | `{"decision":"component","concept":"","parent_concept":"inventory","reason_class":"component_no_conce` | balance-sheet-equity-inventory-other.md §2 | 0 | 0 |  |
| lib.bs.InventoryWorkInProcessNetOfReserves | tag | all | `{"stmt":"BS","tag":"InventoryWorkInProcessNetOfReserves","order":363}` | `{"decision":"component","concept":"","parent_concept":"inventory","reason_class":"component_no_conce` | balance-sheet-equity-inventory-other.md §2 | 0 | 0 |  |
| template.inventory | data_point | all | `{"order":29}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## ppe_net

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.PropertyPlantAndEquipmentNet | tag | all | `{"stmt":"BS","tag":"PropertyPlantAndEquipmentNet","order":17}` | `{"decision":"map","concept":"ppe_net_resolved","parent_concept":"","reason_class":""}` | explicit | 73 | 0 | 100.0% |
| lib.bs.AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment | tag | all | `{"stmt":"BS","tag":"AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment","order":141}` | `{"decision":"component","concept":"","parent_concept":"ppe_net_resolved","reason_class":"component_n` | explicit | 0 | 0 |  |
| lib.bs.PropertyPlantAndEquipmentGross | tag | all | `{"stmt":"BS","tag":"PropertyPlantAndEquipmentGross","order":150}` | `{"decision":"component","concept":"","parent_concept":"ppe_net_resolved","reason_class":"component_n` | explicit | 0 | 0 |  |
| lib.bs.PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization | tag | all | `{"stmt":"BS","tag":"PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization","order":238}` | `{"decision":"map","concept":"ppe_net_resolved","parent_concept":"","reason_class":""}` | fsn-line-to-concept.md §A | 23 | 9 | 60.9% |
| lib.bs.PublicUtilitiesPropertyPlantAndEquipmentNet | tag | all | `{"stmt":"BS","tag":"PublicUtilitiesPropertyPlantAndEquipmentNet","order":447}` | `{"decision":"map","concept":"ppe_net_resolved","parent_concept":"","reason_class":""}` | fsn-balance-sheet-assets.md | 1 | 1 | 0.0% |
| template.ppe_net | data_point | all | `{"order":38}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## stockholders_equity

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.AccumulatedOtherComprehensiveIncomeLossNetOfTax | tag | all | `{"stmt":"BS","tag":"AccumulatedOtherComprehensiveIncomeLossNetOfTax","order":4}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.RetainedEarningsAccumulatedDeficit | tag | all | `{"stmt":"BS","tag":"RetainedEarningsAccumulatedDeficit","order":5}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.StockholdersEquity | tag | all | `{"stmt":"BS","tag":"StockholdersEquity","order":10}` | `{"decision":"map","concept":"stockholders_equity_resolved","parent_concept":"","reason_class":""}` | balance-sheet-equity-inventory-other.md §1 | 98 | 0 | 100.0% |
| lib.bs.CommonStockValue | tag | all | `{"stmt":"BS","tag":"CommonStockValue","order":25}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | tag | all | `{"stmt":"BS","tag":"StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest","order":43}` | `{"decision":"map","concept":"stockholders_equity_resolved","parent_concept":"","reason_class":""}` | fsn-balance-sheet-liabilities-equity.md | 9 | 5 | 44.4% |
| lib.bs.TreasuryStockValue | tag | all | `{"stmt":"BS","tag":"TreasuryStockValue","order":58}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.AdditionalPaidInCapitalCommonStock | tag | all | `{"stmt":"BS","tag":"AdditionalPaidInCapitalCommonStock","order":68}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.PreferredStockValue | tag | all | `{"stmt":"BS","tag":"PreferredStockValue","order":70}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.AdditionalPaidInCapital | tag | all | `{"stmt":"BS","tag":"AdditionalPaidInCapital","order":92}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.CommonStocksIncludingAdditionalPaidInCapital | tag | all | `{"stmt":"BS","tag":"CommonStocksIncludingAdditionalPaidInCapital","order":144}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.TreasuryStockCommonValue | tag | all | `{"stmt":"BS","tag":"TreasuryStockCommonValue","order":184}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| lib.bs.CommonStockValueOutstanding | tag | all | `{"stmt":"BS","tag":"CommonStockValueOutstanding","order":334}` | `{"decision":"component","concept":"","parent_concept":"stockholders_equity_resolved","reason_class":` | explicit | 0 | 0 |  |
| nd.StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | combined_concept | all | `{"tag":"StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest","order":76}` | `{"data_point":"stockholders_equity","members":""}` | needs-detail-answers-r1r2.csv (companies-51-100-exceptions-2026-11-11.csv) | 0 | 0 |  |
| nd.PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest | combined_concept | all | `{"tag":"PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest","order":145}` | `{"data_point":"stockholders_equity","members":""}` | needs-detail-answers-r1r2.csv (companies-201-300-exceptions-2026-11-11.csv) | 0 | 0 |  |
| template.stockholders_equity | data_point | all | `{"order":46}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bs.stockholders_equity.prefer.StockholdersEquity | prefer_tag | all | `{"among":"mapped candidates"}` | `{"tag":"StockholdersEquity"}` | net-income/equity cards | 98 | 0 | 100.0% |

## total_assets

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.Assets | tag | all | `{"stmt":"BS","tag":"Assets","order":1}` | `{"decision":"map","concept":"total_assets_resolved","parent_concept":"","reason_class":""}` | explicit | 104 | 0 | 100.0% |
| template.total_assets | data_point | all | `{"order":47}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

## total_debt

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.LongTermDebtNoncurrent | tag | all | `{"stmt":"BS","tag":"LongTermDebtNoncurrent","order":60}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 52 | 10 | 80.8% |
| lib.bs.DebtCurrent | tag | all | `{"stmt":"BS","tag":"DebtCurrent","order":105}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 22 | 1 | 95.5% |
| lib.bs.LongTermDebtAndCapitalLeaseObligations | tag | all | `{"stmt":"BS","tag":"LongTermDebtAndCapitalLeaseObligations","order":109}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 26 | 2 | 92.3% |
| lib.bs.ShortTermBorrowings | tag | all | `{"stmt":"BS","tag":"ShortTermBorrowings","order":123}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 20 | 5 | 75.0% |
| lib.bs.LongTermDebtCurrent | tag | all | `{"stmt":"BS","tag":"LongTermDebtCurrent","order":131}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 34 | 4 | 88.2% |
| lib.bs.LongTermDebtAndCapitalLeaseObligationsCurrent | tag | all | `{"stmt":"BS","tag":"LongTermDebtAndCapitalLeaseObligationsCurrent","order":194}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 14 | 1 | 92.9% |
| lib.bs.LongTermDebt | tag | all | `{"stmt":"BS","tag":"LongTermDebt","order":231}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 15 | 3 | 80.0% |
| lib.bs.CommercialPaper | tag | all | `{"stmt":"BS","tag":"CommercialPaper","order":382}` | `{"decision":"component","concept":"","parent_concept":"total_debt_resolved","reason_class":"componen` | debt.md §5-§9 | 4 | 1 | 75.0% |
| nd.FinanceLeaseLiabilityCurrent | combined_concept | all | `{"tag":"FinanceLeaseLiabilityCurrent","order":7}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 1 | 1 | 0.0% |
| nd.LineOfCredit | combined_concept | all | `{"tag":"LineOfCredit","order":10}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.LinesOfCreditCurrent | combined_concept | all | `{"tag":"LinesOfCreditCurrent","order":11}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 2 | 2 | 0.0% |
| nd.ConvertibleDebtNoncurrent | combined_concept | all | `{"tag":"ConvertibleDebtNoncurrent","order":13}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 1 | 1 | 0.0% |
| nd.LongTermLineOfCredit | combined_concept | all | `{"tag":"LongTermLineOfCredit","order":18}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 1 | 1 | 0.0% |
| nd.ConvertibleLongTermNotesPayable | combined_concept | all | `{"tag":"ConvertibleLongTermNotesPayable","order":24}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 3 | 3 | 0.0% |
| nd.CommercialPaper | combined_concept | all | `{"tag":"CommercialPaper","order":25}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.SecuredDebt | combined_concept | all | `{"tag":"SecuredDebt","order":27}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 1 | 1 | 0.0% |
| nd.ConvertibleDebtCurrent | combined_concept | all | `{"tag":"ConvertibleDebtCurrent","order":28}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.UnsecuredDebt | combined_concept | all | `{"tag":"UnsecuredDebt","order":36}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 3 | 3 | 0.0% |
| nd.OtherShortTermBorrowings | combined_concept | all | `{"tag":"OtherShortTermBorrowings","order":37}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 0 | 0 |  |
| nd.OtherBorrowings | combined_concept | all | `{"tag":"OtherBorrowings","order":44}` | `{"data_point":"total_debt","members":""}` | needs-detail-answers-r1r2.csv (std-tags-rank-360-744-2026-11-11.csv) | 1 | 1 | 0.0% |
| template.total_debt | data_point | all | `{"order":48}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |
| bs.total_debt.duration_sum | sum_allowed | all | `{}` | `{"sum":true}` | Dhairya ruling (a) 2026-11-12 (durations); total_debt founder doc 02 2026-11-04 item 5 | 0 | 0 |  |

## total_liabilities

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| lib.bs.Liabilities | tag | all | `{"stmt":"BS","tag":"Liabilities","order":29}` | `{"decision":"map","concept":"total_liabilities_resolved","parent_concept":"","reason_class":""}` | fsn-balance-sheet-liabilities-equity.md | 77 | 0 | 100.0% |
| template.total_liabilities | data_point | all | `{"order":50}` | `{"home_stmt":"BS"}` | docmap data-point vocabulary (data-team/companies/reads/*-docmap-*.csv) | 0 | 0 |  |

