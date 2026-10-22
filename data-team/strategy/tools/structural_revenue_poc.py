"""Read-only PoC: structural revenue/net-income resolution from FSDS vs name vocabulary.
Usage: python3 -I structural_revenue_poc.py DIR [--form 10-K]
DIR has sub.txt pre.txt num.txt. No DB, no writes."""
import argparse, collections, csv, os, re

VOCAB = {"RevenueFromContractWithCustomerExcludingAssessedTax","RevenueFromContractWithCustomerIncludingAssessedTax","Revenues","SalesRevenueNet"}
REV = re.compile(r"revenue|net sales|^sales|total sales|turnover", re.I)
BAD = re.compile(r"cost|expense|deferred|tax|per share|%|percent|unearned|related part|marketing|selling|general", re.I)
NI = {"NetIncomeLoss","ProfitLoss","NetIncomeLossAvailableToCommonStockholdersBasic"}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--form", default="10-K"); a = ap.parse_args()
    rd = lambda n: csv.DictReader(open(os.path.join(a.dir, n), newline=""), delimiter="\t")
    sub = {r["adsh"]: r for r in rd("sub.txt") if r["form"] == a.form}
    pre = collections.defaultdict(list)
    for r in rd("pre.txt"):
        if r["adsh"] in sub and r["stmt"] in ("IS", "CF", "BS"): pre[r["adsh"]].append(r)
    val = collections.defaultdict(dict)  # adsh -> (tag, version, qtrs, ddate) -> value
    for r in rd("num.txt"):
        if r["adsh"] in sub and r["uom"] == "USD" and not r["segments"] and not r["coreg"] and r["value"]:
            val[r["adsh"]][(r["tag"], r["version"], r["qtrs"], r["ddate"])] = float(r["value"])
    out = collections.Counter(); ex = collections.defaultdict(list)
    for adsh, s in sub.items():
        rows = pre.get(adsh)
        if not rows: continue
        v = val[adsh]
        end = s["period"]
        def fy(tag, ver_any=True):
            for (t, ver, q, d), x in v.items():
                if t == tag and q == "4" and d == end: return x
        isr = [r for r in rows if r["stmt"] == "IS"]
        if not isr: continue
        rep = min(int(r["report"]) for r in isr)
        lines = sorted((r for r in isr if int(r["report"]) == rep), key=lambda r: int(r["line"]))
        # name path
        name_rev = next((fy(t) for t in VOCAB if fy(t) is not None), None)
        # structural path: first line before any cost/expense line whose label looks like revenue, with FY value
        st = None; st_tag = None
        for r in lines:
            if BAD.search(r["plabel"]) and not REV.search(r["plabel"]): break
            if not REV.search(r["plabel"]) or BAD.search(r["plabel"]): continue
            for (t, ver, q, d), y in v.items():
                if t == r["tag"] and ver == r["version"] and q == "4" and d == end:
                    if st is None or y > st: st, st_tag = y, (r["tag"], r["version"][:9], r["plabel"][:30])
                    break
        key = "name+struct" if name_rev is not None and st is not None else "name_only" if name_rev is not None else "struct_only" if st is not None else "neither"
        if key == "name+struct":
            key = "agree" if abs(name_rev - st) <= max(1, 0.005 * abs(name_rev)) else "DISAGREE"
        out[key] += 1
        if len(ex[key]) < 6: ex[key].append((s["name"][:26], s["sic"], name_rev, st, st_tag))
        # NI cross-statement identity: IS net income vs CF net income
        nis = [x for x in (fy("NetIncomeLoss"), fy("ProfitLoss")) if x is not None]
        ni_is = nis[0] if nis else None
        cf = [r for r in rows if r["stmt"] == "CF"]
        if cf and ni_is is not None:
            c0 = sorted(cf, key=lambda r: (int(r["report"]), int(r["line"])))[0]
            cx = fy(c0["tag"]) if c0["tag"] in NI else None
            out["ni_cf_checked"] += cx is not None
            out["ni_cf_ok"] += cx is not None and any(abs(cx - n) <= max(1, 0.005 * abs(n)) for n in nis)
    print(dict(out))
    for k, l in ex.items():
        if k in ("name_only", "DISAGREE"):
            print("--", k)
            for e in l: print("  ", e)

main()
