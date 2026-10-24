"""Print one filing's extracted face lines (non-dimensioned) in presentation order. usage: show.py <workdir> <adsh> [STMT] [tagregex]"""
import glob, gzip, json, re, sys
W, A = sys.argv[1], sys.argv[2]
st = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
rx = re.compile(sys.argv[4]) if len(sys.argv) > 4 else None
rows = []
for fn in sorted(glob.glob(f"{W}/out/*.jsonl.gz")):
    for l in gzip.open(fn, "rt"):
        if A in l:
            r = json.loads(l)
            if r["adsh"] == A: rows.append(r)
if not rows: print("filing not found"); sys.exit(1)
print(rows[0]["form"], "period", rows[0]["period"], "fy/fp", rows[0]["fy"], rows[0]["fp"], "filed", rows[0]["filed"])
for r in rows:
    if st and r["stmt"] != st: continue
    if rx and not rx.search(r["tag"] + " " + r["label"]): continue
    if r.get("dims") or r["value"] is None: continue
    print(r["stmt"], r["report"], r["line"], "T" if r["is_total"] else " ", "C" if r["custom"] else " ", r["tag"][:60], "|", r["label"][:55], "|", r["end"], r["qtrs"], r["uom"], r["value"], "neg" if r["negating"] == "1" else "")
