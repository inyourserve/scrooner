"""Replicate structural_concepts_poc.py logic exactly, but dump per-filer detail for differing / struct_only cases."""
import collections, csv, os, re, sys, json
sys.path=[p for p in sys.path if p]
D=sys.argv[1]
C = {
 "capex": ("CF", r"purchase.*(property|equipment|plant)|capital expenditure|additions to (property|plant)|acquisition of (property|equipment)|payments for (property|capital)|purchases of premises", r"", {"PaymentsToAcquirePropertyPlantAndEquipment","PaymentsToAcquireProductiveAssets","PaymentsForCapitalImprovements","PaymentsToAcquireOtherPropertyPlantAndEquipment"}),
 "d_and_a": ("CF", r"depreciation|amortization", r"deferred|debt|discount|premium|intangible.*lease|right", {"DepreciationDepletionAndAmortization","DepreciationAndAmortization","DepreciationAmortizationAndAccretionNet","Depreciation","DepreciationAndAmortizationExcludingDebtIssuanceCosts"}),
 "interest_expense": ("IS", r"interest expense|interest and debt expense|interest cost|finance cost", r"net|income", {"InterestExpense","InterestExpenseNonoperating","InterestExpenseDebt","InterestAndDebtExpense","InterestExpenseOperating"}),
}
rd = lambda n: csv.DictReader(open(os.path.join(D, n), newline="", encoding="utf-8", errors="replace"), delimiter="\t")
sub = {r["adsh"]: r for r in rd("sub.txt") if r["form"] == "10-K"}
pre = collections.defaultdict(list)
for r in rd("pre.txt"):
    if r["adsh"] in sub and r["stmt"] in ("IS", "CF"): pre[r["adsh"]].append(r)
val = collections.defaultdict(dict)
for r in rd("num.txt"):
    if r["adsh"] in sub and r["uom"] == "USD" and not r["segments"] and not r["coreg"] and r["qtrs"] == "4" and r["ddate"] == sub[r["adsh"]]["period"] and r["value"]:
        val[r["adsh"]][(r["tag"], r["version"])] = float(r["value"])
out=[]
for adsh, s in sub.items():
    v = val[adsh]
    for k, (stmt, pos, neg, vocab) in C.items():
        nvk = next(((t,ver) for (t, ver) in v if t in vocab), None)
        nv = v[nvk] if nvk else None
        allvocab = {t:y for (t,ver),y in v.items() if t in vocab}
        st=None
        for r in pre.get(adsh, []):
            if r["stmt"] != stmt: continue
            if re.search(pos, r["plabel"], re.I) and not (neg and re.search(neg, r["plabel"], re.I)):
                y = v.get((r["tag"], r["version"]))
                if y is not None: st = (r["tag"], r["version"], r["plabel"], y, r["report"], r["line"]); break
        key = "both" if nv is not None and st else "name_only" if nv is not None else "struct_only" if st else "neither"
        if key == "both" and abs(abs(nv) - abs(st[3])) > max(1, 0.005 * abs(nv)): key = "differ"
        if key in ("differ","struct_only"):
            # is name tag presented on the stmt?
            prs=[(r["report"],r["line"],r["stmt"],r["plabel"]) for r in pre.get(adsh,[]) if nvk and r["tag"]==nvk[0]]
            out.append(dict(k=k,key=key,adsh=adsh,name=s["name"],cik=s["cik"],sic=s["sic"],afs=s["afs"],period=s["period"],nametag=nvk[0] if nvk else None,nv=nv,allvocab=allvocab,name_presented=prs,st=st))
json.dump(out,open(sys.argv[2],"w"),indent=0)
c=collections.Counter((o["k"],o["key"]) for o in out); print(c)
