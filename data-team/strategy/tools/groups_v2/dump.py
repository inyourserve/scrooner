"""Compact human-read dump of read filings. usage: dump.py <reason-prefix-or-ALL> [ticker,ticker...] [--rows N]"""
import json, glob, sys, csv
sys.path.insert(0, ".")
import strict, strict_decide as sd
SC = "/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w"
pref = sys.argv[1]; only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
nrows = int(sys.argv[sys.argv.index("--rows") + 1]) if "--rows" in sys.argv else 10
for p in sorted(glob.glob(SC + "/reads/*.json")):
    r = json.load(open(p))
    if "rows" not in r:
        if pref in ("ALL", "ERR"): print("ERR", r.get("cik"), r.get("err"), r.get("name"), r.get("sic"))
        continue
    f = strict.features(r["rows"]); s = strict.signatures(f)
    grp, ov, basis, why = sd.decide_strict(r["sic"] or "", f, s)
    tk = (r["tickers"] or ["?"])[0]
    if only and tk not in only: continue
    if pref != "ALL" and not why.startswith(pref): continue
    print(f"## {tk} {r['cik']} sic={r['sic']} {str(r['sicDescription'])[:28]} | {r['form']} {r['acc']} pe={r['period']} | BS:{r['bs'][1] if r['bs'] else None} IS:{r['is'][1] if r['is'] else None} | {basis}:{grp} {why}")
    print("   F:", "; ".join(f"{k}={v[:26]}" for k, v in f.items() if k not in ("rev",)), "| rev=" + f.get("rev", "-")[:20])
    if nrows:
        print("   IS:", " | ".join(x[1][:26] for x in r["rows"].get("IS", [])[:nrows]))
