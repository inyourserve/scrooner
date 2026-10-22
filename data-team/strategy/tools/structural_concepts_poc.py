"""Read-only: for several concepts, how often does a name vocabulary vs a statement-position+label rule find a FY value?
Usage: python3 -I structural_concepts_poc.py DIR [--form 10-K]"""
import argparse, collections, csv, os, re
C = {
 "capex": ("CF", r"purchase.*(property|equipment|plant)|capital expenditure|additions to (property|plant)|acquisition of (property|equipment)|payments for (property|capital)|purchases of premises", r"", {"PaymentsToAcquirePropertyPlantAndEquipment","PaymentsToAcquireProductiveAssets","PaymentsForCapitalImprovements","PaymentsToAcquireOtherPropertyPlantAndEquipment"}),
 "d_and_a": ("CF", r"depreciation|amortization", r"deferred|debt|discount|premium|intangible.*lease|right", {"DepreciationDepletionAndAmortization","DepreciationAndAmortization","DepreciationAmortizationAndAccretionNet","Depreciation","DepreciationAndAmortizationExcludingDebtIssuanceCosts"}),
 "interest_expense": ("IS", r"interest expense|interest and debt expense|interest cost|finance cost", r"net|income", {"InterestExpense","InterestExpenseNonoperating","InterestExpenseDebt","InterestAndDebtExpense","InterestExpenseOperating"}),
 "operating_income": ("IS", r"operating income|income from operations|operating profit|loss from operations|operating loss", r"before|per share", {"OperatingIncomeLoss"}),
 "cfo": ("CF", r"net cash.*(provided|used).*operating|cash flows? from operating|operating activities", r"discontinued|continuing", {"NetCashProvidedByUsedInOperatingActivities","NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"}),
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--form", default="10-K"); a = ap.parse_args()
    rd = lambda n: csv.DictReader(open(os.path.join(a.dir, n), newline=""), delimiter="\t")
    sub = {r["adsh"]: r for r in rd("sub.txt") if r["form"] == a.form}
    pre = collections.defaultdict(list)
    for r in rd("pre.txt"):
        if r["adsh"] in sub and r["stmt"] in ("IS", "CF"): pre[r["adsh"]].append(r)
    val = collections.defaultdict(dict)
    for r in rd("num.txt"):
        if r["adsh"] in sub and r["uom"] == "USD" and not r["segments"] and not r["coreg"] and r["qtrs"] == "4" and r["ddate"] == sub[r["adsh"]]["period"] and r["value"]:
            val[r["adsh"]][(r["tag"], r["version"])] = float(r["value"])
    res = {k: collections.Counter() for k in C}; ex = {k: [] for k in C}
    for adsh, s in sub.items():
        v = val[adsh]
        for k, (stmt, pos, neg, vocab) in C.items():
            name = any((t, ver) in v for t in vocab for ver in [x[1] for x in v if x[0] == t])
            nv = next((y for (t, ver), y in v.items() if t in vocab), None)
            st = None
            for r in sorted(pre.get(adsh, []), key=lambda r: (int(r["report"]), int(r["line"]))):
                if r["stmt"] != stmt: continue
                if re.search(pos, r["plabel"], re.I) and not (neg and re.search(neg, r["plabel"], re.I)):
                    y = v.get((r["tag"], r["version"]))
                    if y is not None: st = (r["tag"], r["version"][:9], r["plabel"][:34], y); break
            key = "both" if nv is not None and st else "name_only" if nv is not None else "struct_only" if st else "neither"
            if key == "both" and abs(abs(nv) - abs(st[3])) > max(1, 0.005 * abs(nv)): key = "both_values_differ"
            res[k][key] += 1
            if key == "struct_only" and len(ex[k]) < 5: ex[k].append((s["name"][:24], s["sic"], st[:3]))
    for k in C:
        print(k, dict(res[k]))
        for e in ex[k]: print("    struct_only:", e)
main()
