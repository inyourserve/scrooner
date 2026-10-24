"""Read-only composition census on FSDS face lines. Usage: python3 -I compose.py faceq.json"""
import json, sys, re, collections
F = json.load(open(sys.argv[1]))
def pick(stmt, form, v):
    if not v: return None
    if stmt == "BS": return v.get("0")
    if form == "10-K": return v.get("4")
    if stmt == "IS": return v.get("1") or v.get("4")
    for q in ("3","2","1","4"):
        if q in v: return v[q]
def us(ver): return ver.startswith("us-gaap")
bank = lambda s: s.startswith("60") or s.startswith("61") or s.startswith("63") or s.startswith("64") or s.startswith("62") or s=="6798" or s.startswith("67")
CFO = {"NetCashProvidedByUsedInOperatingActivities","NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"}
CFI = {"NetCashProvidedByUsedInInvestingActivities","NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"}
DA = {
 "combined": {"DepreciationDepletionAndAmortization","DepreciationAndAmortization","DepreciationAmortizationAndAccretionNet","OtherDepreciationAndAmortization","DepreciationAmortizationAndOther","DepreciationAndAmortizationExcludingAmortizationOfIntangibleAssets"},
 "depreciation": {"Depreciation","DepreciationNonproduction","DepreciationDepletion","DepreciationAndDepletion"},
 "intangibles": {"AmortizationOfIntangibleAssets","AmortizationOfAcquiredIntangibleAssets","AmortizationOfIntangibleAssetsExcludingGoodwill"},
 "rou_lease": {"OperatingLeaseRightOfUseAssetAmortizationExpense","FinanceLeaseRightOfUseAssetAmortization","OperatingLeaseRightOfUseAssetPeriodicReduction","AmortizationOfLeasedAsset","NoncashOrPartNoncashLeaseExpense"},
 "debt_cost": {"AmortizationOfDebtIssuanceCosts","AmortizationOfFinancingCosts","AmortizationOfDebtDiscountPremium","AmortizationOfFinancingCostsAndDiscounts","AmortizationOfDebtIssuanceCostsAndDiscounts","AmortizationOfDeferredCharges"},
 "software": {"CapitalizedComputerSoftwareAmortization1","CapitalizedComputerSoftwareAmortization"},
 "contract_cost": {"CapitalizedContractCostAmortization"},
}
CAPEX = {
 "ppe": {"PaymentsToAcquirePropertyPlantAndEquipment","PaymentsToAcquireProductiveAssets","PaymentsToAcquireOtherPropertyPlantAndEquipment","PaymentsForCapitalImprovements","PaymentsToAcquireMachineryAndEquipment","PaymentsForConstructionInProcess","PaymentsToAcquireOilAndGasPropertyAndEquipment","PaymentsToAcquireOilAndGasProperty","PaymentsToAcquireRealEstate","PaymentsToDevelopRealEstateAssets","PaymentsToAcquireAndDevelopRealEstate","PaymentsForSoftware","PaymentsToAcquireLand","PaymentsToAcquireBuildings","PaymentsToExploreAndDevelopOilAndGasProperties","PaymentsToAcquireMiningAssets","PaymentsToAcquireEquipmentOnLease","PaymentsToAcquireFurnitureAndFixtures","PaymentsToAcquireRealEstateHeldForInvestment","PaymentsForProceedsFromProductiveAssets"},
 "software": {"PaymentsToAcquireSoftware","PaymentsToDevelopSoftware"},
 "intangible": {"PaymentsToAcquireIntangibleAssets","PaymentsToAcquireFiniteLivedIntangibleAssets"},
 "proceeds": {"ProceedsFromSaleOfPropertyPlantAndEquipment","ProceedsFromSaleOfProductiveAssets","ProceedsFromSaleOfOtherPropertyPlantAndEquipment","ProceedsFromSaleOfRealEstate","ProceedsFromSaleOfRealEstateHeldforinvestment"},
}
GROSS_INT = {"InterestExpense","InterestExpenseNonoperating","InterestExpenseDebt","InterestExpenseOperating","InterestAndDebtExpense","InterestExpenseRelatedParty","InterestExpenseOther","InterestExpenseBorrowings"}
NET_INT = {"InterestIncomeExpenseNet","InterestIncomeExpenseNonoperatingNet","InterestRevenueExpenseNet","InterestIncomeExpenseOperatingNet"}
INC_INT = {"InvestmentIncomeInterest","InterestIncomeOther","InvestmentIncomeInterestAndDividend","InterestAndOtherIncome","InterestIncomeOperating","InterestAndDividendIncomeOperating","InterestIncomeNonoperating"}
DEBT = {"LongTermDebt","LongTermDebtNoncurrent","LongTermDebtCurrent","DebtCurrent","ShortTermBorrowings","CommercialPaper","NotesPayable","NotesPayableCurrent","LongTermNotesPayable","SeniorNotes","SubordinatedDebt","LongTermLineOfCredit","LineOfCredit","ConvertibleNotesPayable","ConvertibleNotesPayableCurrent","ConvertibleLongTermNotesPayable","LongTermDebtAndCapitalLeaseObligations","LongTermDebtAndCapitalLeaseObligationsCurrent","LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities","DebtAndCapitalLeaseObligations","DebtLongtermAndShorttermCombinedAmount","SecuredDebt","UnsecuredDebt","OtherLongTermDebtNoncurrent","OtherLongTermDebtCurrent","AdvancesFromFederalHomeLoanBanks","LinesOfCreditCurrent","OtherBorrowings","LoansPayableCurrent","LoansPayable","LongTermLoansPayable","NotesPayableRelatedPartiesClassifiedCurrent","DebtInstrumentCarryingAmount","SecuredLongTermDebt","OtherShortTermBorrowings","BankOverdrafts","LongTermDebtAndFinanceLeasesNoncurrent"}
LEASE_IN_DEBT = {"LongTermDebtAndCapitalLeaseObligations","LongTermDebtAndCapitalLeaseObligationsCurrent","LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities","DebtAndCapitalLeaseObligations","DebtCurrent"}
FINLEASE = {"FinanceLeaseLiability","FinanceLeaseLiabilityCurrent","FinanceLeaseLiabilityNoncurrent"}
OPLEASE = {"OperatingLeaseLiability","OperatingLeaseLiabilityCurrent","OperatingLeaseLiabilityNoncurrent"}
OI_ITEMS = {"impairment": re.compile(r"Impairment", re.I), "restructuring": re.compile(r"Restructuring|Severance", re.I), "gain_sale": re.compile(r"GainLossOn(Sale|Disposition)|GainOnSale|LossOnSale|GainsLossesOnSalesOf", re.I), "other_opinc": re.compile(r"OtherOperatingIncome|OtherOperatingIncomeExpenseNet|OtherCostAndExpenseOperating", re.I), "equity_method": re.compile(r"IncomeLossFromEquityMethodInvestments", re.I), "da_line": re.compile(r"Depreciation|Amortization", re.I)}
def fam(tag, ver, table):
    for k, s in table.items():
        if tag in s: return k
    return None
c = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
def add(k, key, a, f, extra=""):
    c[k][key] += 1
    if len(ex[(k,key)]) < 6: ex[(k,key)].append(f"{f['name'][:28]}|{f['sic']}|{a}|{f['form']}{extra}")
for a, f in F.items():
    L = f["lines"]; form = f["form"]; sic = f["sic"] or ""
    fin = bank(sic)
    cf = [l for l in L if l[0]=="CF"]; is_ = [l for l in L if l[0]=="IS"]; bs = [l for l in L if l[0]=="BS"]
    # --- D&A in CF operating section
    if cf:
        idx = next((i for i,l in enumerate(cf) if l[3] in CFO), None)
        op = cf[:idx] if idx is not None else []
        fams = set(); custom = []
        for l in op:
            fm = fam(l[3], l[4], DA)
            if fm and pick("CF", form, l[7]) is not None: fams.add(fm)
            elif not us(l[4]) and re.search(r"depreciation|amortization|depletion", l[5], re.I): custom.append(l[5][:40])
        if idx is not None and not fin:
            key = "+".join(sorted(fams)) or "none"
            if custom: key += "+custom"
            add("cf_DA_shape", key, a, f)
            core = fams & {"combined","depreciation","intangibles"}
            add("cf_DA_core", "+".join(sorted(core)) + ("+custom" if custom else "") if core or custom else "none", a, f)
        # --- capex in investing section
        j = next((i for i,l in enumerate(cf) if l[3] in CFI), None)
        if idx is not None and j is not None and not fin:
            inv = cf[idx+1:j]
            fams = collections.Counter(); custom = []
            for l in inv:
                fm = fam(l[3], l[4], CAPEX)
                if fm and pick("CF", form, l[7]) is not None: fams[fm] += 1
                elif not us(l[4]) and re.search(r"capital expend|purchase.*(property|equipment)|additions to (property|plant)", l[5], re.I): custom.append(l[5][:40])
            key = "+".join(f"{k}{'x'+str(v) if v>1 else ''}" for k,v in sorted(fams.items()) if k!="proceeds") or "none"
            if custom: key += "+custom"
            add("cf_capex_shape", key, a, f)
            add("cf_capex_has_proceeds", "yes" if fams["proceeds"] else "no", a, f)
        # interest paid on CF
        ip = any(l[3] in ("InterestPaidNet","InterestPaid","InterestPaidCapitalized") for l in cf)
        c["cf_interest_paid_line"]["yes" if ip else "no"] += 1
    # --- interest on IS (non-financials)
    if is_ and not fin:
        g = {l[3] for l in is_ if l[3] in GROSS_INT and pick("IS",form,l[7]) is not None}
        n = {l[3] for l in is_ if l[3] in NET_INT and pick("IS",form,l[7]) is not None}
        i = {l[3] for l in is_ if l[3] in INC_INT and pick("IS",form,l[7]) is not None}
        cust = [l[5][:40] for l in is_ if not us(l[4]) and re.search(r"interest", l[5], re.I)]
        key = ("gross" if g else "") + ("+net" if n else "") + ("+income" if i else "") + ("+custom" if cust else "")
        add("is_interest_shape", key.strip("+") or "none", a, f)
        if len(g) > 1: add("is_interest_multi_gross", "+".join(sorted(g)), a, f)
        # --- operating income composition
        has_oi = [k for k,l in enumerate(is_) if l[3]=="OperatingIncomeLoss"]
        if has_oi:
            above = is_[:has_oi[0]]
            items = set()
            for l in above:
                for k, rx in OI_ITEMS.items():
                    if rx.search(l[3]) and pick("IS",form,l[7]) is not None: items.add(k)
            add("oi_present", "yes", a, f)
            for k in items: add("oi_contains", k, a, f)
            if not items: add("oi_contains", "none_of_listed", a, f)
        else:
            shape = "CostsAndExpenses" if any(l[3]=="CostsAndExpenses" for l in is_) else ("custom_oi_label" if any((not us(l[4])) and re.search(r"operating (income|loss)|income from operations|loss from operations", l[5], re.I) for l in is_) else "no_oi")
            add("oi_present", "no:"+shape, a, f)
        # --- net income attribution
        tags = {l[3] for l in is_}
        k = ("NetIncomeLoss" if "NetIncomeLoss" in tags else "") + ("+ProfitLoss" if "ProfitLoss" in tags else "") + ("+NCI" if "NetIncomeLossAttributableToNoncontrollingInterest" in tags else "") + ("+AvailToCommon" if "NetIncomeLossAvailableToCommonStockholdersBasic" in tags else "")
        add("is_ni_shape", k.strip("+") or "none", a, f)
        # --- revenue top lines
        rev = {l[3] for l in is_ if l[3] in ("Revenues","RevenueFromContractWithCustomerExcludingAssessedTax","RevenueFromContractWithCustomerIncludingAssessedTax","SalesRevenueNet","RegulatedAndUnregulatedOperatingRevenue") and pick("IS",form,l[7]) is not None}
        add("is_revenue_tags", "+".join(sorted(rev)) or "none", a, f)
        if "Revenues" in rev and "RevenueFromContractWithCustomerExcludingAssessedTax" in rev:
            vr = [float(pick("IS",form,l[7])) for l in is_ if l[3]=="Revenues"][0]
            vc = [float(pick("IS",form,l[7])) for l in is_ if l[3]=="RevenueFromContractWithCustomerExcludingAssessedTax"][0]
            add("rev_both_relation", "equal" if abs(vr-vc)<=max(1,abs(vr)*1e-4) else ("rcfc<rev" if vc<vr else "rcfc>rev"), a, f, f"|R={vr:.0f}|C={vc:.0f}")
        if any(l[3] in ("ExciseAndSalesTaxes","SalesAndExciseTaxPayable") or re.search(r"excise", l[5], re.I) for l in is_):
            add("is_excise_line", "yes", a, f)
        # D&A on IS (separate line) for non-fin
        isda = [l for l in is_ if fam(l[3], l[4], DA) in ("combined","depreciation","intangibles") and pick("IS",form,l[7]) is not None]
        if isda and cf and form=="10-K":
            cfda = [l for l in cf if fam(l[3], l[4], DA) in ("combined",) and pick("CF",form,l[7]) is not None]
            if cfda:
                vi = sum(float(pick("IS",form,l[7])) for l in isda); vc = float(pick("CF",form,cfda[0][7]))
                add("da_is_vs_cf_10K", "equal" if abs(vi-vc)<=max(1,abs(vc)*0.005) else "differ", a, f, f"|IS={vi:.0f}|CF={vc:.0f}")
    # --- debt on BS
    if bs and not fin:
        d = {l[3] for l in bs if l[3] in DEBT and pick("BS",form,l[7]) is not None}
        cust = [l[5][:40] for l in bs if not us(l[4]) and re.search(r"debt|borrowing|notes payable|loan|credit facilit|convertible", l[5], re.I) and pick("BS",form,l[7]) is not None]
        fl = {l[3] for l in bs if l[3] in FINLEASE and pick("BS",form,l[7]) is not None}
        n = len(d) + len(cust)
        add("bs_debt_line_count", str(min(n,4)) + ("+custom" if cust else ""), a, f)
        if d & LEASE_IN_DEBT: add("bs_debt_lease_combined_tag", "yes", a, f, "|"+",".join(sorted(d & LEASE_IN_DEBT)))
        if fl: add("bs_finance_lease_separate_line", "yes", a, f)
        if fl and (d & LEASE_IN_DEBT): add("bs_finlease_sep_AND_combined", "yes", a, f)
        if any(l[3] in OPLEASE for l in bs): c["bs_oplease_line"]["yes"] += 1
    c["population"]["fin" if fin else "nonfin"] += 1
    c["population"][form] += 1
for k in c:
    print("==", k, dict(c[k].most_common(14)))
import pickle; pickle.dump(dict(ex), open("examples.pkl","wb"))
