import csv, os, sys, collections
D=sys.argv[1]
rd=lambda n: csv.DictReader(open(os.path.join(D,n),newline="",encoding="utf-8",errors="replace"),delimiter="\t")
sub={r["adsh"]:r for r in rd("sub.txt") if r["form"] in ("10-K","10-Q")}
T={"DepreciationAndAmortization","DepreciationDepletionAndAmortization"}
v=collections.defaultdict(dict)
for r in rd("num.txt"):
    s=sub.get(r["adsh"])
    if s and r["tag"] in T and r["uom"]=="USD" and not r["segments"] and not r["coreg"] and r["ddate"]==s["period"] and r["value"] and r["version"].startswith("us-gaap"):
        v[(r["adsh"],r["qtrs"])][r["tag"]]=float(r["value"])
st=collections.defaultdict(set)
for r in rd("pre.txt"):
    if r["adsh"] in sub and r["tag"] in T: st[(r["adsh"],r["tag"])].add(r["stmt"])
c=collections.Counter(); ex=[]
for (a,q),d in v.items():
    if len(d)<2: continue
    da,dda=d["DepreciationAndAmortization"],d["DepreciationDepletionAndAmortization"]
    same=abs(da-dda)<=max(1,0.005*abs(dda))
    k=(sub[a]["form"],"same" if same else ("DA<DDA" if abs(da)<abs(dda) else "DA>DDA"))
    c[k]+=1
    if not same and sub[a]["form"]=="10-K": ex.append((sub[a]["name"][:22],q,da,dda,sorted(st[(a,"DepreciationAndAmortization")]),sorted(st[(a,"DepreciationDepletionAndAmortization")])))
print(c); print("filings with both:",sum(c.values()))
for e in ex[:40]: print(e)
