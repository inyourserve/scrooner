"""Build per-filer face-statement feature table from FSDS sub+pre (read-only). Writes feat.json
usage: python3 -I feat.py OUT dir1 dir2 ..."""
import csv, sys, json, re, collections
csv.field_size_limit(10**9)
out = sys.argv[1]; dirs = sys.argv[2:]
best = {}  # cik -> sub row (latest filed 10-K by period)
for d in dirs:
    for r in csv.DictReader(open(d + "/sub.txt", newline=""), delimiter="\t"):
        if r["form"] != "10-K": continue
        k = r["cik"]
        if k not in best or r["period"] > best[k]["period"] or (r["period"] == best[k]["period"] and r["filed"] > best[k]["filed"]):
            r["_dir"] = d; best[k] = r
adsh2cik = {r["adsh"]: k for k, r in best.items()}
feats = {k: {"name": r["name"], "sic": r["sic"], "period": r["period"], "fp": r["fp"], "adsh": r["adsh"], "cb": r["countryba"], "afs": r["afs"],
             "ls": collections.defaultdict(list)} for k, r in best.items()}
for d in dirs:
    for r in csv.DictReader(open(d + "/pre.txt", newline=""), delimiter="\t"):
        k = adsh2cik.get(r["adsh"])
        if k is None or best[k]["_dir"] != d: continue
        if r["stmt"] not in ("BS", "IS", "CF", "EQ", "CI"): continue
        feats[k]["ls"][r["stmt"]].append((r["tag"], r["version"] == r["adsh"], r["plabel"], int(r["report"]), int(r["line"])))
json.dump(feats, open(out, "w"))
print(len(feats), sum(1 for f in feats.values() if f["ls"]))
