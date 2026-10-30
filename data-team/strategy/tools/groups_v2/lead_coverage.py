"""For each draft-50 / corrected tag lead, how many members of the group show it on their own BS/IS (R-file rows; Reader 1)."""
import csv, json, os, sys, glob
DATA = "/Users/vikash/wt-sector-groups/data-team/strategy/data/"
SC = os.environ.get("SA_SCRATCH", "/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w")
A = [a for a in csv.DictReader(open(DATA + "group_assignment_v2.csv")) if a["cohort_status"] == "cohort_file_v1" and not a["group"].startswith("excluded")]
TAGS = {  # (group, row) -> tags (local names) ; a company counts if ANY appears on its BS/IS
 ("bank", "sr.fin.net_interest_income"): ["InterestIncomeExpenseNet", "InterestRevenueExpenseNet"],
 ("bank", "sr.fin.interest_income_total"): ["InterestAndDividendIncomeOperating", "InterestIncomeOperating"],
 ("bank", "sr.fin.interest_expense_total"): ["InterestExpenseOperating", "InterestExpense"],
 ("bank", "draft B3 lead InterestExpense only"): ["InterestExpense"],
 ("bank", "sr.bank.noninterest_income"): ["NoninterestIncome"],
 ("bank", "sr.bank.noninterest_expense"): ["NoninterestExpense"],
 ("bank", "sr.fin.provision_credit_losses"): ["ProvisionForLoanLeaseAndOtherLosses", "ProvisionForLoanAndLeaseLosses", "ProvisionForLoanLossesExpensed", "FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal", "ProvisionForCreditLosses", "ProvisionForOtherCreditLosses", "ProvisionForLoanAndLeaseLossesExcludingUnfundedCommitments"],
 ("bank", "draft B6 lead ProvisionForLoanLeaseAndOtherLosses only"): ["ProvisionForLoanLeaseAndOtherLosses"],
 ("bank", "sr.bank.deposits_total"): ["Deposits"],
 ("bank", "sr.fin.loans_net post-CECL tag"): ["FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss"],
 ("bank", "draft B10 lead LoansAndLeasesReceivableNetReportedAmount (pre-CECL)"): ["LoansAndLeasesReceivableNetReportedAmount"],
 ("bank", "sr.fin.loans_net any of 3"): ["FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss", "LoansAndLeasesReceivableNetReportedAmount", "NotesReceivableNet", "LoansReceivableNet"],
 ("bank", "sr.fin.allowance post-CECL"): ["FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest", "FinancingReceivableAllowanceForCreditLosses", "LoansAndLeasesReceivableAllowance"],
 ("insurer", "sr.ins.premiums_earned"): ["PremiumsEarnedNet"],
 ("insurer", "sr.ins.net_investment_income"): ["NetInvestmentIncome", "InvestmentIncomeNet"],
 ("insurer", "sr.ins.benefits_claims_incurred"): ["PolicyholderBenefitsAndClaimsIncurredNet", "IncurredClaimsPropertyCasualtyAndLiability", "PolicyholderBenefitsAndClaimsIncurredGross"],
 ("insurer", "sr.ins.policy_acquisition_cost_amortization"): ["DeferredPolicyAcquisitionCostAmortizationExpense"],
 ("insurer", "sr.ins.reserves_unpaid_claims"): ["LiabilityForClaimsAndClaimsAdjustmentExpense"],
 ("insurer", "sr.ins.future_policy_benefits"): ["LiabilityForFuturePolicyBenefits", "LiabilityForFuturePolicyBenefitsAndUnpaidClaimsAndClaimsAdjustmentExpense", "PolicyholderContractDeposits"],
 ("insurer", "revenue total (Revenues)"): ["Revenues"],
 ("managed_care", "sr.ins.premiums_earned at managed care"): ["PremiumsEarnedNet"],
 ("managed_care", "sr.ins.benefits_claims_incurred at managed care"): ["PolicyholderBenefitsAndClaimsIncurredNet"],
 ("insurance_broker", "single revenue line"): ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
 ("insurance_broker", "fiduciary assets"): ["FiduciaryAssets", "FiduciaryAssetsCurrent", "FiduciaryCashCurrent"],
 ("reit_equity", "sr.reit.rental_revenue"): ["OperatingLeaseLeaseIncome", "OperatingLeasesIncomeStatementLeaseRevenue", "RealEstateRevenueNet", "LeaseAndRentalRevenue"],
 ("reit_equity", "sr.reit.real_estate_net"): ["RealEstateInvestmentPropertyNet"],
 ("reit_equity", "sr.reit.real_estate_at_cost (face)"): ["RealEstateInvestmentPropertyAtCost", "RealEstateInvestmentPropertyGross"],
 ("reit_equity", "sr.reit.accumulated_depreciation (face)"): ["RealEstateInvestmentPropertyAccumulatedDepreciation"],
 ("reit_equity", "sr.reit.general_and_administrative"): ["GeneralAndAdministrativeExpense"],
 ("reit_equity", "sr.reit.property_operating_expenses"): ["DirectCostsOfLeasedAndRentedPropertyOrEquipment", "OperatingExpenses", "CostDirectLaborAndPropertyOperatingExpense"],
 ("reit_mortgage", "sr.fin.net_interest_income"): ["InterestIncomeExpenseNet"],
 ("reit_mortgage", "sr.fin.interest_income_total"): ["InterestIncomeOperating", "InterestAndDividendIncomeOperating"],
 ("reit_mortgage", "repurchase agreements"): ["SecuritiesSoldUnderAgreementsToRepurchase", "AssetsSoldUnderAgreementsToRepurchase"],
 ("bdc", "sr.bdc.total_investment_income"): ["GrossInvestmentIncomeOperating"],
 ("bdc", "draft F2 NetInvestmentIncome (pre-tax at ARCC, BXSL)"): ["NetInvestmentIncome"],
 ("bdc", "NII after tax"): ["InvestmentIncomeOperatingAfterExpenseAndTax"],
 ("bdc", "draft F3 AssetsNet"): ["AssetsNet"],
 ("bdc", "net assets = StockholdersEquity"): ["StockholdersEquity"],
 ("bdc", "sr.bdc.nav_per_share"): ["NetAssetValuePerShare"],
 ("bdc", "sr.bdc.investments_fair_value"): ["InvestmentOwnedAtFairValue"],
 ("bdc", "net increase in net assets"): ["NetIncomeLoss"],
 ("asset_manager", "compensation (LaborAndRelatedExpense)"): ["LaborAndRelatedExpense"],
 ("asset_manager", "total revenue single tag"): ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
 ("asset_manager", "management fee tag candidates"): ["InvestmentAdvisoryManagementAndAdministrativeFees", "InvestmentAdvisoryFees", "AssetManagementFees1", "AssetManagementFees", "ManagementFeeRevenue"],
 ("broker_dealer", "net revenues"): ["RevenuesNetOfInterestExpense"],
 ("broker_dealer", "Revenues"): ["Revenues"],
 ("broker_dealer", "commissions"): ["BrokerageCommissionsRevenue"],
 ("broker_dealer", "receivables from brokers/dealers"): ["ReceivablesFromBrokersDealersAndClearingOrganizations"],
 ("crypto_digital", "digital assets BS"): ["CryptoAssetFairValue", "CryptoAssetFairValueNoncurrent", "CryptoAssetFairValueCurrent", "CryptoAssetNoncurrent", "CryptoAssetCost"],
 ("crypto_digital", "digital asset gains IS"): ["CryptoAssetRealizedGainLossOperating", "CryptoAssetRealizedAndUnrealizedGainLossOperating", "CryptoAssetUnrealizedGainLossOperating"],
 ("lender_nonbank", "provision"): ["ProvisionForLoanLossesExpensed", "ProvisionForLoanLeaseAndOtherLosses", "FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal"],
 ("lender_nonbank", "loans receivable net"): ["NotesReceivableNet", "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss", "LoansReceivableNet"],
 ("utility", "draft U1 PublicUtilitiesPropertyPlantAndEquipmentNet"): ["PublicUtilitiesPropertyPlantAndEquipmentNet"],
 ("utility", "draft U2 RegulatoryAssets (no suffix)"): ["RegulatoryAssets"],
 ("utility", "regulatory assets current/noncurrent"): ["RegulatoryAssetsCurrent", "RegulatoryAssetsNoncurrent", "RegulatoryAssets"],
 ("utility", "regulatory liabilities"): ["RegulatoryLiabilityCurrent", "RegulatoryLiabilityNoncurrent", "RegulatoryLiabilities"],
 ("midstream", "PartnersCapital"): ["PartnersCapital", "PartnersCapitalIncludingPortionAttributableToNoncontrollingInterest", "LimitedPartnersCapitalAccount"],
 ("midstream", "EPS per LP unit (basic/diluted)"): ["NetIncomeLossPerOutstandingLimitedPartnershipUnitBasicNetOfTax", "NetIncomeLossPerOutstandingLimitedPartnershipUnitDiluted", "NetIncomeLossPerOutstandingLimitedPartnershipUnit"],
 ("midstream", "EPS per share (basic/diluted)"): ["EarningsPerShareBasic", "EarningsPerShareDiluted"],
 ("exchange", "clearing/margin lines (us-gaap tags)"): ["MarginDepositsAndGuarantyFundsCurrent", "MarginDepositsAndGuarantyFundsLiabilitiesCurrent", "MarginDepositsAssets", "MarginDepositsLiabilities"],
}
rows = []
N = {}
for a in A: N[a["group"]] = N.get(a["group"], 0) + 1
tagsets = {}
for a in A:
    p = f"{SC}/reads/{a['cik']}.json"
    if not os.path.exists(p): continue
    r = json.load(open(p))
    if "rows" not in r: continue
    s = set()
    for st in ("BS", "IS"):
        for tag, label, val in r["rows"].get(st, []):
            if tag and (tag.startswith("us-gaap_") or tag.startswith("srt_")): s.add(tag.split("_", 1)[1])   # standard prefixes only: an extension tag with the same local name is NOT the standard tag
    tagsets[a["cik"]] = (a["group"], s)
out = []
for (g, row), tags in TAGS.items():
    n = sum(1 for cik, (gg, s) in tagsets.items() if gg == g and any(t in s for t in tags))
    out.append(dict(group=g, row_or_lead=row, tags="|".join(tags), companies_with_any=n, group_size=N.get(g, 0), share=round(n / max(N.get(g, 1), 1), 2)))
with open(DATA + "sector_lead_coverage_v2.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for o in out: print(f"{o['group'][:10]:10} {o['companies_with_any']:3d}/{o['group_size']:3d}  {o['row_or_lead'][:70]}")
