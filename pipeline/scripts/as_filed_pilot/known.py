"""Known-cell check: face lines (FSDS) vs API-stored value (core.fact, same accession/tag/period). usage: known.py <workdir> <TICKER> <adsh> <tagregex> <stmt>"""
import glob, gzip, json, re, sys
from decimal import Decimal
W, T, A, RX, ST = sys.argv[1:6]
rx = re.compile(RX)
def ym(s):
    y, m, d = int(s[:4]), int(s[5:7]), int(s[8:10])
    if d <= 15:
        m -= 1
        if m == 0: y, m = y - 1, 12
    return f"{y:04d}-{m:02d}"
stored = {}
for l in gzip.open(f"{W}/stored/stored_{T}.jsonl.gz", "rt"):
    q = json.loads(l)
    if q[0] == A: stored.setdefault((q[3], ym(q[6])), []).append((q[7], q[8], q[2], q[5]))
seen = set()
for fn in sorted(glob.glob(f"{W}/out/*.jsonl.gz")):
    for l in gzip.open(fn, "rt"):
        if A not in l: continue
        r = json.loads(l)
        if r["adsh"] != A or r["stmt"] != ST or r["dims"] or r["value"] is None or not rx.search(r["tag"] + " " + r["label"]): continue
        k = (r["report"], r["line"], r["tag"], r["end"], r["qtrs"])
        if k in seen: continue
        seen.add(k)
        st = [s for kk, v in stored.items() if kk[0] == r["tag"] and kk[1] == r["end"][:7] or False for s in v] 
        print(f'{"T" if r["is_total"] else " "}{"C" if r["custom"] else " "} L{r["line"]:>3} {r["tag"][:45]:45} | {r["label"][:42]:42} | {r["end"]} q{r["qtrs"]} {Decimal(r["value"]):>18,.0f} | API: ' + (", ".join(f"{Decimal(x[0]):,.0f}{'' if x[1] else '(non-auth)'}" for x in st) or "ABSENT"))
