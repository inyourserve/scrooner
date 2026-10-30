import json, re, collections, sys
F = json.load(open(sys.argv[1]))
def T(f, st): return {t for t, c, l, r, ln in f["ls"].get(st, [])}
def L(f, st): return [l.lower() for t, c, l, r, ln in f["ls"].get(st, [])]
def anyre(labels, rx): return any(re.search(rx, l) for l in labels)
def hastag(tags, prefixes=(), exact=()):
    return any(t in exact or any(t.startswith(p) for p in prefixes) for t in tags)

def concept_flags(f):
    bs, is_, cf = T(f,"BS"), T(f,"IS"), T(f,"CF")
    bl, il, cl = L(f,"BS"), L(f,"IS"), L(f,"CF")
    o = {}
    o["revenue"] = hastag(is_, exact={"RevenueFromContractWithCustomerExcludingAssessedTax","RevenueFromContractWithCustomerIncludingAssessedTax","Revenues","SalesRevenueNet","SalesRevenueGoodsNet","SalesRevenueServicesNet","RegulatedAndUnregulatedOperatingRevenue","OperatingLeaseLeaseIncome","RealEstateRevenueNet","ElectricUtilityRevenue","RevenuesNetOfInterestExpense"}) or anyre(il, r"^(total )?(net )?(revenues?|sales)\b|total revenues?|net sales|revenues?, net")
    o["cost_of_revenue"] = hastag(is_, exact={"CostOfRevenue","CostOfGoodsAndServicesSold","CostOfGoodsSold","CostOfServices","CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization","CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"}) or anyre(il, r"cost of (revenues?|sales|goods|products|services)|cost of (net )?revenues?")
    o["gross_profit_line"] = "GrossProfit" in is_ or anyre(il, r"gross (profit|margin)")
    o["operating_income"] = "OperatingIncomeLoss" in is_ or anyre(il, r"(operating (income|profit|loss)|income \(loss\) from operations|(loss|income) from operations)")
    o["income_before_tax"] = hastag(is_, prefixes=("IncomeLossFromContinuingOperationsBeforeIncomeTaxes",)) or anyre(il, r"before (provision for |benefit from )?(income )?tax")
    o["income_tax_expense"] = "IncomeTaxExpenseBenefit" in is_ or anyre(il, r"income tax")
    o["net_income"] = bool({"NetIncomeLoss","ProfitLoss"} & is_) or anyre(il, r"^net (income|loss|earnings)")
    o["diluted_eps"] = bool({"EarningsPerShareDiluted","EarningsPerShareBasicAndDiluted"} & is_) or anyre(il, r"diluted")
    o["basic_eps"] = bool({"EarningsPerShareBasic","EarningsPerShareBasicAndDiluted"} & is_)
    o["interest_expense"] = hastag(is_, prefixes=("InterestExpense","InterestAndDebtExpense")) or anyre(il, r"interest expense|interest and debt expense")
    o["interest_income"] = hastag(is_, prefixes=("InvestmentIncomeInterest","InterestIncome","InterestAndDividendIncome","InterestAndFeeIncome")) or anyre(il, r"interest (and dividend )?income|interest income|investment income")
    o["sga_expense"] = "SellingGeneralAndAdministrativeExpense" in is_ or anyre(il, r"selling,? general")
    o["g_and_a_only"] = "GeneralAndAdministrativeExpense" in is_ or anyre(il, r"general and administrative")
    o["research_and_development"] = hastag(is_, prefixes=("ResearchAndDevelopment",)) or anyre(il, r"research and development|research & development")
    o["sbc"] = hastag(cf, prefixes=("ShareBasedCompensation","AllocatedShareBasedCompensation","StockIssuedDuringPeriodValueShareBasedCompensation")) or anyre(cl, r"(stock|share|equity)[- ]based compensation|stock compensation")
    o["depreciation_and_amortization_resolved"] = hastag(cf, prefixes=("DepreciationDepletionAndAmortization","DepreciationAndAmortization","DepreciationAmortizationAndAccretion","Depreciation","AmortizationOf","DepletionOfOilAndGasProperties")) or anyre(cl, r"deprec|amortiz|depletion")
    o["cfo"] = hastag(cf, prefixes=("NetCashProvidedByUsedInOperatingActivities",)) or anyre(cl, r"net cash.*operating")
    o["cash_flow_investing"] = hastag(cf, prefixes=("NetCashProvidedByUsedInInvestingActivities",)) or anyre(cl, r"net cash.*investing")
    o["cash_flow_financing"] = hastag(cf, prefixes=("NetCashProvidedByUsedInFinancingActivities",)) or anyre(cl, r"net cash.*financing")
    o["capex"] = hastag(cf, prefixes=("PaymentsToAcquirePropertyPlantAndEquipment","PaymentsToAcquireProductiveAssets","PaymentsToAcquireOtherPropertyPlantAndEquipment","PaymentsToAcquireOilAndGasPropertyAndEquipment","PaymentsForCapitalImprovements","PaymentsToDevelopRealEstateAssets","PaymentsToAcquireRealEstate","PaymentsForSoftware","PaymentsToAcquireOtherProductiveAssets")) or anyre(cl, r"capital expenditure|purchases? of (property|premises|fixed|equipment)|additions to (property|plant|premises)|acquisitions? of (property|premises)|purchase of (property|premises|equipment)")
    o["dividends_paid"] = hastag(cf, prefixes=("PaymentsOfDividends","PaymentsOfOrdinaryDividends","PaymentsOfCapitalDistribution")) or anyre(cl, r"dividends? paid|payments? of dividends|dividends to|cash dividends|distributions? (paid|to)")
    o["share_buybacks"] = hastag(cf, prefixes=("PaymentsForRepurchaseOf",)) or anyre(cl, r"repurchase|purchases? of treasury|treasury stock")
    o["total_assets"] = "Assets" in bs
    o["current_assets"] = "AssetsCurrent" in bs
    o["current_liabilities"] = "LiabilitiesCurrent" in bs
    o["stockholders_equity"] = hastag(bs, prefixes=("StockholdersEquity","PartnersCapital","MembersEquity","LiabilitiesAndStockholdersEquity_x")) or anyre(bl, r"total (stockholders|shareholders|members|partners)['’]? ?(equity|capital|deficit)")
    o["cash_and_equivalents"] = hastag(bs, prefixes=("CashAndCashEquivalents","CashCashEquivalents","Cash","CashAndDueFromBanks","CashAndCashEquivalentsAtCarryingValue")) or anyre(bl, r"^cash")
    o["inventory"] = hastag(bs, prefixes=("InventoryNet","Inventory","InventoryFinishedGoods")) or anyre(bl, r"^inventor")
    o["accounts_receivable"] = hastag(bs, prefixes=("AccountsReceivable","ReceivablesNetCurrent","AccountsAndOtherReceivables")) or anyre(bl, r"accounts receivable|trade receivable|^receivables?(,| net|$)|receivables?, net|accounts and (notes|other) receivable")
    o["accounts_payable"] = hastag(bs, prefixes=("AccountsPayable",)) or anyre(bl, r"accounts payable|trade payables")
    o["goodwill"] = "Goodwill" in bs or anyre(bl, r"^goodwill")
    o["total_debt_resolved"] = hastag(bs, prefixes=("DebtCurrent","LongTermDebt","NotesPayable","ConvertibleNotesPayable","SeniorNotes","LineOfCredit","ShortTermBorrowings","LongTermNotesPayable","SecuredDebt","UnsecuredDebt","ConvertibleDebt","OtherLongTermDebt","DebtInstrument","LongTermLineOfCredit","FinanceLeaseLiability","CommercialPaper","OtherBorrowings","FederalHomeLoanBankAdvances","NotesIssued")) or anyre(bl, r"\bdebt\b|notes? payable|borrowings|senior notes|term loan|credit facility|convertible notes|debentures")
    o["dividends_per_share"] = any(("DividendsDeclaredPerShare" in t or "CommonStockDividendsPerShare" in t or "DistributionMadeToLimitedPartnerDistributionsPaidPerUnit" in t) for t in is_|T(f,"EQ")|T(f,"CI")) or anyre(il, r"dividends? (declared )?per")
    o["shares_outstanding"] = True  # cover page dei, not a face line; assumed applicable to all
    return o

def family(f):
    sic = f["sic"] or ""
    bs, is_, cf = T(f,"BS"), T(f,"IS"), T(f,"CF")
    bl, il = L(f,"BS"), L(f,"IS")
    allt = bs|is_|cf
    ev = {}
    ev["deposits"] = hastag(bs, exact={"Deposits","InterestBearingDepositLiabilities","NoninterestBearingDepositLiabilities","DepositsDomestic","DepositsSavingsDeposits","TimeDeposits","InterestBearingDepositLiabilitiesDomestic"}) or anyre(bl, r"^(total )?deposits|customer deposits|deposit liabilit")
    ev["loans_line"] = hastag(bs, prefixes=("LoansAndLeasesReceivable","FinancingReceivableExcludingAccruedInterest","LoansReceivable","NotesReceivable","FinancingReceivable")) or anyre(bl, r"^loans")
    ev["nonint_exp"] = "NoninterestExpense" in is_ or anyre(il, r"non-?interest expense|total other expense")
    ev["provision_credit"] = hastag(is_, prefixes=("ProvisionForLoan","ProvisionForCreditLoss","CreditLossExpense","ProvisionForLoanLeaseAndOtherLosses")) or anyre(il, r"provision for (credit|loan)|credit loss")
    ev["net_interest_inc"] = hastag(is_, exact={"InterestIncomeExpenseNet","InterestIncomeExpenseAfterProvisionForLoanLoss"}) or anyre(il, r"net interest income")
    ev["premiums"] = hastag(is_, prefixes=("PremiumsEarned","Premiums","InsurancePremiums","DirectPremiums","PremiumsWritten")) or anyre(il, r"premium")
    ev["claims_liab"] = hastag(bs, prefixes=("LiabilityForClaimsAndClaimsAdjustmentExpense","LiabilityForFuturePolicyBenefits","PolicyholderContractDeposits","FuturePolicyBenefits","UnearnedPremiums","LiabilityForUnpaidClaims","PolicyholderFunds")) or anyre(bl, r"policy ?holder|unpaid (loss|claims)|future policy benefits|unearned premiums|reserves? for (losses|claims)")
    ev["claims_exp"] = hastag(is_, prefixes=("PolicyholderBenefitsAndClaimsIncurred","IncurredClaims","LiabilityForClaimsAndClaims","BenefitsLossesAndExpenses","LossesAndLossAdjustmentExpense","ClaimsAndLoss")) or anyre(il, r"losses? and loss adjustment|policyholder benefits|claims incurred|benefits, losses")
    ev["real_estate_bs"] = hastag(bs, prefixes=("RealEstateInvestmentProperty","RealEstateInvestments","RealEstateHeldforsale","RealEstateAccumulatedDepreciation","RealEstate")) or anyre(bl, r"real estate|investments? in properties|rental propert")
    ev["rental_rev"] = hastag(is_, prefixes=("OperatingLeaseLeaseIncome","LeaseAndRentalRevenue","OperatingLeasesIncomeStatementLeaseRevenue","RealEstateRevenueNet","Rental")) or anyre(il, r"rental|rent revenue|lease (income|revenue)|tenant|property revenue")
    ev["mort_assets"] = hastag(bs, prefixes=("MortgageLoansOnRealEstate","AvailableForSaleSecuritiesDebtSecurities","MortgageBackedSecurities","SecuritiesSoldUnderAgreementsToRepurchase","AssetsSoldUnderAgreementsToRepurchase")) or anyre(bl, r"mortgage[- ](backed|loans?)|repurchase agreements|residential mortgage|agency (rmbs|securities)|commercial mortgage")
    ev["trust_assets"] = hastag(bs, prefixes=("AssetsHeldInTrust",)) or anyre(bl, r"held in trust account|trust account")
    ev["investments_fv"] = hastag(bs, prefixes=("InvestmentOwnedAtFairValue","InvestmentsAtFairValue","InvestmentOwnedAtCost")) or anyre(bl, r"investments?,? at fair value|investments? \(cost")
    ev["total_inv_income"] = anyre(il, r"total investment income|net investment income") and not ev["premiums"]
    ev["nav"] = anyre(bl, r"net assets") and anyre(bl, r"net asset value|total net assets")
    ev["partners_cap"] = hastag(bs, prefixes=("PartnersCapital","PartnersCapitalAccount"))
    ev["reg_assets"] = hastag(bs, prefixes=("RegulatoryAssets","RegulatoryLiabilit","PublicUtilities")) or anyre(bl, r"regulatory assets|regulatory liabilit|utility plant")
    ev["util_rev"] = hastag(is_, prefixes=("ElectricUtility","RegulatedAndUnregulated","PublicUtilities","GasUtility","RegulatedOperatingRevenue")) or anyre(il, r"electric|natural gas|utility|regulated")
    ev["og_props"] = hastag(bs, prefixes=("OilAndGasProperty","OilAndGasPropertyFullCostMethod","OilAndGasPropertySuccessfulEffortMethod","CapitalizedCostsOilAndGas")) or anyre(bl, r"oil and gas propert|oil and natural gas propert|oil & gas")
    ev["fees_mgmt"] = anyre(il, r"(investment )?(advisory|management|performance|incentive) fees?|asset management|assets under")
    ev["brokerage"] = anyre(il, r"commissions|principal transactions|trading (revenue|gains)|brokerage") or anyre(bl, r"receivables? from (broker|dealer|clearing)|securities owned|payables? to (broker|customers)|securities borrowed")
    ev["research_dev"] = hastag(is_, prefixes=("ResearchAndDevelopment",)) or anyre(il, r"research and development")
    ev["no_is"] = not f["ls"].get("IS")
    ev["no_stmts"] = not f["ls"]
    ev["rev_line"] = concept_flags(f)["revenue"]
    return ev, sic

BANKSIC = lambda s: s.isdigit() and 6020 <= int(s) <= 6036
def classify(f):
    ev, sic = family(f)
    n = int(sic) if sic.isdigit() else -1
    if ev["no_stmts"]: return "nofin_statements (ABS/other)", ev
    if n == 6770 or ev["trust_assets"]: return "SPAC_blank_check", ev
    if (n == 6221 or (n in (6199, 6282, 6211) and re.search(r"\b(ETF|TRUST|FUND|FUTURES|L\.P\.)\b", f["name"].upper()) and not ev["rev_line"] and not ev["total_inv_income"])) and not ev["investments_fv"]: return "commodity_crypto_pool_trust", ev
    if sic == "" and ev["investments_fv"]: return "BDC_fund", ev
    if n in (6726, 6799) and ev["investments_fv"] and ev["total_inv_income"]: return "BDC_fund", ev
    if ev["investments_fv"] and ev["total_inv_income"] and (ev["nav"] or n in (6199,6726,6799,6282)): return "BDC_fund", ev
    if ev["deposits"] and (ev["loans_line"] or ev["nonint_exp"] or ev["net_interest_inc"]) and (BANKSIC(sic) or n in (6035,6036,6099,6111,6199,6211,6141,6153,6159,6162)): 
        return ("bank_thrift" if BANKSIC(sic) else "deposit_taker_nonbank_sic"), ev
    if ev["premiums"] and (ev["claims_liab"] or ev["claims_exp"]) : return "insurer_underwriter", ev
    if 6300 <= n <= 6499 and (ev["claims_liab"] or ev["claims_exp"]): return "insurer_underwriter", ev
    if n == 6411: return "insurance_agent_broker", ev
    if n == 6798 or (ev["real_estate_bs"] and ev["rental_rev"] and 6500<=n<=6799):
        if ev["mort_assets"] and not ev["rental_rev"]: return "REIT_mortgage", ev
        if n == 6798 and ev["mort_assets"] and not ev["real_estate_bs"]: return "REIT_mortgage", ev
        return "REIT_equity", ev
    if 6500 <= n <= 6599 or (ev["real_estate_bs"] and ev["rental_rev"] and ev["reg_assets"] is False and n in (6552,1531,1520,7011)): return "real_estate_operator", ev
    if 6200 <= n <= 6299:
        if ev["fees_mgmt"] and not ev["brokerage"]: return "asset_manager_adviser", ev
        if ev["brokerage"]: return "broker_dealer_exchange", ev
        return "asset_manager_adviser", ev
    if 6000 <= n <= 6199 or n in (6099,):
        if ev["deposits"] and BANKSIC(sic): return "bank_thrift", ev
        return "nonbank_lender_credit_fintech", ev
    if 6700 <= n <= 6799: return "trust_holding_other_investor", ev
    if 4900 <= n <= 4991: return "utility_waste", ev
    if ev["partners_cap"]: return "MLP_partnership", ev
    if n in (1311,1381,1382,1389,2911,2990,4610,4922,4923,4924,1321) or ev["og_props"]: return "energy", ev
    if 1000 <= n <= 1099 and not ev["rev_line"]: return "exploration_stage_miner", ev
    if ev["no_is"]: return "no_income_statement_other", ev
    if not ev["rev_line"] and ev["research_dev"]: return "pre_revenue_rd_overlay", ev
    if not ev["rev_line"]: return "no_revenue_line_other", ev
    return "corporate_other", ev

res = {}
for k, f in F.items():
    fam, ev = classify(f)
    res[k] = {"fam": fam, "sic": f["sic"], "name": f["name"], "cb": f["cb"], "flags": concept_flags(f) if f["ls"] else {}, "ev": ev, "adsh": f["adsh"], "period": f["period"]}
json.dump(res, open(sys.argv[2], "w"))
c = collections.Counter(r["fam"] for r in res.values())
for a, b in c.most_common(): print(f"{b:5d} {a}")
