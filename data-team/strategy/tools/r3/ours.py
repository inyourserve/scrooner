"""Read-only: compare our current single-tag recipes against face-line composition (FSDS face extract). DATA-INFERRED."""
import json, sys, re, collections
F = json.load(open(sys.argv[1]))
def pick(stmt, form, v):
    if not v: return None
    if stmt == "BS": return v.get("0")
    if form == "10-K": return v.get("4")
    if stmt == "IS": return v.get("1") or v.get("4")
    for q in ("3","2","1","4"):
        if q in v: return v[q]
fin = lambda s: s[:2] in ("60","61","62","63","64","67") or s == "6798"
CFO = {"NetCashProvidedByUsedInOperatingActivities","NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"}
CFI = {"NetCashProvidedByUsedInInvestingActivities","NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"}
OURS_DA = {"DepreciationAndAmortization","DepreciationDepletionAndAmortization"}
OTHER_DA = {"Depreciation","OtherDepreciationAndAmortization","AmortizationOfIntangibleAssets","DepreciationAmortizationAndAccretionNet","DepreciationNonproduction","DepreciationAndDepletion","Depletion","CapitalizedComputerSoftwareAmortization1","FinanceLeaseRightOfUseAssetAmortization"}
OURS_CAPEX = {"PaymentsToAcquirePropertyPlantAndEquipment","PaymentsToAcquireSoftware"}
OTHER_CAPEX = {"PaymentsToAcquireProductiveAssets","PaymentsToDevelopSoftware","PaymentsForSoftware","PaymentsToAcquireIntangibleAssets","PaymentsToAcquireOtherPropertyPlantAndEquipment","PaymentsForCapitalImprovements","PaymentsToAcquireOilAndGasPropertyAndEquipment","PaymentsToExploreAndDevelopOilAndGasProperties","PaymentsToAcquireMachineryAndEquipment","PaymentsForProceedsFromProductiveAssets","PaymentsToAcquireAndDevelopRealEstate","PaymentsToDevelopRealEstateAssets","PaymentsToAcquireRealEstate","PaymentsForConstructionInProcess"}
OURS_INT = ["InterestExpense","InterestExpenseDebt"]
OTHER_GROSS = {"InterestExpenseNonoperating","InterestExpenseOperating","InterestAndDebtExpense","FinanceLeaseInterestExpense","InterestExpenseOther","InterestExpenseRelatedParty"}
NET = {"InterestIncomeExpenseNet","InterestIncomeExpenseNonoperatingNet","InterestRevenueExpenseNet"}
c = collections.defaultdict(collections.Counter); ex = collections.defaultdict(list)
def add(k, key, a, f, x=""):
    c[k][key] += 1
    if len(ex[(k,key)]) < 5: ex[(k,key)].append(f"{f['name'][:26]}|{a}{x}")
for a, f in F.items():
    if fin(f["sic"] or ""): continue
    L = f["lines"]; form = f["form"]
    cf = [l for l in L if l[0]=="CF"]; is_ = [l for l in L if l[0]=="IS"]
    i = next((k for k,l in enumerate(cf) if l[3] in CFO), None); j = next((k for k,l in enumerate(cf) if l[3] in CFI), None)
    if i is not None:
        op = [l for l in cf[:i] if pick("CF",form,l[7]) is not None]
        o = {l[3] for l in op if l[3] in OURS_DA}
        other = {l[3] for l in op if l[3] in OTHER_DA}
        cust = [l for l in op if not l[4].startswith("us-gaap") and re.search(r"depreciation|amortization|depletion", l[5], re.I) and not re.search(r"debt|financ|discount|premium|lease|right.of.use|deferred", l[5], re.I)]
        if o and not other and not cust: k = "ours_only_line"
        elif o: k = "ours_plus_more_lines(understated?)"
        elif other or cust: k = "ours_absent_components_present(blank)"
        else: k = "no_da_line"
        add("DA_vs_ours", k, a, f, "|"+",".join(sorted(other))[:80] + ("|custom" if cust else ""))
    if i is not None and j is not None:
        inv = [l for l in cf[i+1:j] if pick("CF",form,l[7]) is not None]
        o = {l[3] for l in inv if l[3] in OURS_CAPEX}
        other = {l[3] for l in inv if l[3] in OTHER_CAPEX}
        cust = [l for l in inv if not l[4].startswith("us-gaap") and re.search(r"capital expend|purchases? of (property|equipment|plant|fixed)|additions to (property|plant|fixed)|software", l[5], re.I)]
        if o and not other and not cust: k = "ours_only_line"
        elif o: k = "ours_plus_more_lines"
        elif other or cust: k = "ours_absent_components_present"
        else: k = "no_capex_line"
        add("CAPEX_vs_ours", k, a, f, "|"+",".join(sorted(other))[:80] + ("|custom" if cust else ""))
    if is_:
        tags = {l[3] for l in is_ if pick("IS",form,l[7]) is not None}
        ours = next((t for t in OURS_INT if t in tags), None)
        og = tags & OTHER_GROSS; n = tags & NET
        if ours and not og: k = "ours_found"
        elif ours and og: k = "ours_found_plus_other_gross(" + ",".join(sorted(og)) + ")"
        elif og: k = "ours_absent_other_gross_present"
        elif n: k = "net_only"
        else: k = "no_interest_line"
        add("INT_vs_ours", k, a, f)
for k in c: print("==", k, dict(c[k].most_common(12)))
for k,v in ex.items():
    if k[0] in ("DA_vs_ours","CAPEX_vs_ours") and "only" not in k[1]: print(k); [print("   ",e) for e in v]
