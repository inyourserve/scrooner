"""Strict face signatures computed from the rows of the filer's own balance sheet and income statement (R-file rows: tag + label).
Used in the reader phase (queue, filers missing from FSDS, extras). Each feature returns the trigger label (for the hand read) or ''."""
import re

def loc(tag):  # local tag name
    return tag.split("_", 1)[1] if "_" in tag else tag

def first(rows, tag_rx=None, label_rx=None, exclude_rx=None):
    for tag, label, val in rows:
        l = label.lower()
        if exclude_rx and re.search(exclude_rx, l):
            continue
        if (tag_rx and re.search(tag_rx, loc(tag))) or (label_rx and re.search(label_rx, l)):
            return label[:60]
    return ""

def features(rows):
    bs, is_ = rows.get("BS", []), rows.get("IS", [])
    f = {}
    f["deposits"] = first(bs, r"^(Deposits|InterestBearingDepositLiabilities|NoninterestBearingDepositLiabilities|DepositsDomestic|TimeDeposits|DepositsSavingsDeposits|DepositsDemand)", r"^(total )?(interest[- ]bearing |non-?interest[- ]bearing )?deposits$|^deposits\b(?!.*(with|on|paid|in escrow|and other assets))", r"customer|security deposit|escrow|vendor|tenant|deposits with|deposits on|deposits paid|deposit to|deposits and other")
    f["loans"] = first(bs, r"^(LoansAndLeasesReceivable|FinancingReceivableExcludingAccruedInterest|LoansReceivable|FinancingReceivableAfterAllowance)", r"^(total )?loans\b|^net loans|loans and leases")
    f["nii"] = first(is_, r"^(InterestIncomeExpenseNet|InterestIncomeExpenseAfterProvisionForLoanLoss|InterestRevenueExpenseNet)$", r"net interest (income|revenue)|net interest and dividend income")
    f["nonint_exp"] = first(is_, r"^NoninterestExpense$", r"^(total )?non-?interest expenses?")
    f["nonint_inc"] = first(is_, r"^NoninterestIncome$", r"^(total )?non-?interest (income|revenue)")
    f["provision"] = first(is_, r"^(ProvisionFor(Loan|Credit)|FinancingReceivableExcludingAccruedInterestCreditLossExpense|CreditLossExpense|ProvisionForLoanLeaseAndOtherLosses)", r"provision for (credit|loan)|provision for (possible )?(credit|loan)|credit loss expense")
    f["premiums"] = first(is_, r"^(PremiumsEarned|Premiums|InsurancePremiums|DirectPremiums|PremiumsWritten|HealthCarePremium)", r"premiums?\b")
    f["claims"] = first(is_, r"^(PolicyholderBenefitsAndClaimsIncurred|IncurredClaims|BenefitsLossesAndExpenses|LiabilityForClaims|LossesAndLossAdjustment|PolicyholderBenefits|ClaimsAndLoss|BenefitsAndExpenses|HealthCareCosts)", r"losses and loss adjustment|policyholder benefits|claims|benefits, losses|medical costs|medical care costs|health care costs|benefits and losses|insurance benefits|benefits and other deductions|policy benefits")
    f["reserves"] = first(bs, r"^(LiabilityForClaimsAndClaimsAdjustmentExpense|LiabilityForFuturePolicyBenefits|UnearnedPremiums|PolicyholderContractDeposits|PolicyholderFunds|LiabilityForUnpaidClaims|FuturePolicyBenefits|MedicalClaims)", r"policy ?holder|unpaid (loss|claims)|future policy benefits|unearned premiums|reserves? for|medical claims|claims payable|reserve for")
    f["current_assets"] = first(bs, r"^AssetsCurrent$", r"^total current assets")
    f["realestate"] = first(bs, r"^(RealEstateInvestmentProperty|RealEstateInvestments|RealEstate|RealEstateHeldforsale|RealEstateAccumulated|InvestmentBuildingAndBuildingImprovements|LandAndLandImprovements)", r"real estate|investments? in (real estate|propert)|rental propert|land and buildings")
    f["rental"] = first(is_, r"^(OperatingLeaseLeaseIncome|OperatingLeasesIncomeStatementLeaseRevenue|RealEstateRevenueNet|LeaseAndRentalRevenue|Rental|OperatingLeasesIncomeStatementLeaseRevenue)", r"rental|rent revenue|lease (income|revenue)|tenant|^rent\b|property revenue")
    f["regulatory"] = first(bs, r"^(RegulatoryAssets|RegulatoryLiabilit|PublicUtilities|RegulatoryAsset)", r"regulatory (assets|liabilit)|utility plant|utility property")
    f["reg_assets"] = first(bs, r"^RegulatoryAssets", r"regulatory assets")
    f["reg_liab"] = first(bs, r"^RegulatoryLiabilit", r"regulatory liabilit")
    f["fuel_is"] = first(is_, r"^(FuelCosts|CostOfPurchasedPower|FuelPurchasedPower|CostOfNaturalGas)", r"^fuel|purchased power|purchased gas|cost of gas|fuel and purchased|fuel, purchased|power purchased|energy purchases|fuel and energy")
    f["util_plant"] = first(bs, r"^PublicUtilities", r"utility plant|electric plant|gas plant|plant in service|public utility property")
    f["util_rev"] = first(is_, r"^(ElectricUtility|RegulatedAndUnregulated|PublicUtilities|GasUtility|RegulatedOperatingRevenue)", r"electric|natural gas|gas (revenue|sales|distribution)|utility|regulated")
    f["inv_income"] = first(is_, None, r"total investment income")
    f["net_assets"] = first(bs, r"^AssetsNet$", r"^total net assets|^net assets\b|net asset value")
    f["inv_fv"] = first(bs, r"^(InvestmentOwnedAtFairValue|InvestmentsFairValue|InvestmentOwnedAtCost)", r"investments?,? at fair value|investments? \(.*cost")
    f["brokerage_bs"] = first(bs, None, r"securities borrowed|receivables? from (broker|dealer|clearing)|payables? to (broker|customers|clients)|securities owned|securities sold, not yet purchased|segregated")
    f["brokerage_is"] = first(is_, None, r"commissions|principal transactions|trading (revenue|gains|income)|investment banking|brokerage")
    f["am_fees"] = first(is_, None, r"(investment )?(advisory|management|performance|incentive|base) fees?|asset management|performance (allocations|revenues?)|carried interest")
    f["digital"] = first(bs, None, r"digital assets?|bitcoin|crypto")
    f["oilgas"] = first(bs, r"^(OilAndGasProperty|CapitalizedCostsOilAndGas)", r"oil and (natural )?gas propert|oil & gas propert|proved propert")
    f["partners"] = first(bs, r"^(PartnersCapital|PartnersCapitalAccount)", r"partners['’] (capital|equity)|unitholders|limited partners")
    f["repo_mbs"] = first(bs, r"^(AssetsSoldUnderAgreementsToRepurchase|SecuritiesSoldUnderAgreementsToRepurchase|MortgageBackedSecurities)", r"repurchase agreements|mortgage[- ]backed|agency (rmbs|securities|mortgage)|residential mortgage")
    f["fin_recv"] = first(bs, r"^(FinancingReceivable|NotesReceivable|NetInvestmentInDirectFinancingAndSalesTypeLeases)", r"finance receivables|financing receivables|financial services receivables|receivables from financial|retail notes|net investment in (sales-type|direct financing)|finance and other receivables|loans and leases|receivables\W+\W*finance|financial receivables|credit finance receivables|customer financing")
    f["fin_is"] = first(is_, None, r"financial services|finance (and interest )?income|financing revenue|interest and other income from|revenues? of financial products|gm financial|credit revenue|financial products|ford credit|finance segment|finance group|finance revenue")
    f["rev"] = first(is_, r"^(Revenues|RevenueFromContract|SalesRevenue|RegulatedAndUnregulatedOperatingRevenue|OperatingLease|RealEstateRevenueNet|ElectricUtility|RevenuesNetOfInterestExpense)", r"^(total )?(net )?(revenues?|sales)\b|total revenues?|net sales|revenues?, net|total net revenues?|operating revenues?")
    f["rd"] = first(is_, r"^ResearchAndDevelopment", r"research and development|research & development")
    f["cogs"] = first(is_, r"^(CostOfRevenue|CostOfGoodsAndServicesSold|CostOfGoodsSold|CostOfServices)", r"cost of (revenues?|sales|goods|products|services)")
    f["interest_inc"] = first(is_, r"^(InterestAndDividendIncomeOperating|InterestIncomeOperating|InterestAndFeeIncome)", r"^(total )?interest (and dividend )?income|total interest")
    f["unclassified_bs"] = "" if f["current_assets"] else "no total current assets"
    return {k: v for k, v in f.items() if v}

def signatures(f):
    """Strict signatures (>= 2 independent face lines of the family on the filer's own BS/IS)."""
    s = {}
    b = [k for k in ("deposits", "loans", "nii", "nonint_exp", "provision", "nonint_inc") if k in f]
    if "deposits" in f and len(b) >= 3:
        s["bank"] = b
    ins = [k for k in ("premiums", "claims", "reserves") if k in f]
    if "premiums" in f and "claims" in f and len(ins) >= 2:
        s["insurer" if "current_assets" not in f else "insurer_or_managed_care_classified_bs"] = ins
    if "inv_income" in f and ("net_assets" in f or "inv_fv" in f):
        s["bdc"] = [k for k in ("inv_income", "net_assets", "inv_fv") if k in f]
    if "realestate" in f and "rental" in f:
        s["reit_equity"] = ["realestate", "rental"]
    u = [k for k in ("reg_assets", "reg_liab", "fuel_is", "util_plant", "util_rev") if k in f]
    if "reg_assets" in f and len(u) >= 2:
        s["utility"] = u
    if "partners" in f:
        s["partnership"] = ["partners"]
    if "digital" in f:
        s["digital_assets"] = ["digital"]
    if "oilgas" in f:
        s["oilgas"] = ["oilgas"]
    if "brokerage_bs" in f and "brokerage_is" in f:
        s["brokerage"] = ["brokerage_bs", "brokerage_is"]
    if "am_fees" in f and "brokerage_bs" not in f:
        s["asset_mgmt_fees"] = ["am_fees"]
    if "fin_recv" in f and "fin_is" in f:
        s["finance_arm"] = ["fin_recv", "fin_is"]
    return s
