"""Test harness: raw-SEC-column company dirs (FORMATS-v1 names) from the cohort
is_fsn extract, so the company-mode reader sees identical inputs."""
import csv, glob, gzip, json, sys
from collections import defaultdict
from pathlib import Path
src, coreg_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
coreg = set(open(coreg_path).read().split())
SUB = ["fsn_set", "adsh", "cik", "form", "period", "filed", "fy", "fp", "aciks"]
PRE = ["adsh", "report", "line", "stmt", "inpth", "tag", "version", "prole", "plabel", "negating"]
CAL = ["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"]
subs, pre, cal, cik_of, dup = defaultdict(dict), defaultdict(list), defaultdict(list), {}, 0
for p in sorted(glob.glob(f"{src}/*_is_pre.jsonl.gz")):
    per = Path(p).name.split("_")[0]
    seen_here = set()
    for line in gzip.open(p, "rt"):
        r = json.loads(line); a = r["adsh"]
        if a in cik_of and a not in seen_here and per not in subs[r["cik"]].get(a, {}).get("fsn_set", ""):
            dup += 1
        seen_here.add(a); cik_of[a] = r["cik"]
        subs[r["cik"]].setdefault(a, {"fsn_set": per, "adsh": a, "cik": r["cik"], "form": r["form"], "period": r["period"],
                                      "filed": r["filed"], "fy": r.get("fy") or "", "fp": r.get("fp") or "",
                                      "aciks": "0000000001" if a in coreg else ""})
        pre[r["cik"]].append({"adsh": a, "report": r["report"], "line": r["line"], "stmt": r["stmt"], "inpth": "0",
                              "tag": r["tag"], "version": a if r["custom"] else "us-gaap/2020", "prole": "terseLabel",
                              "plabel": r["label"], "negating": "1" if r["negating"] else "0"})
    for line in gzip.open(f"{src}/{per}_cal.jsonl.gz", "rt"):
        c = json.loads(line); a = c["adsh"]
        if a in seen_here:
            cal[cik_of[a]].append({"adsh": a, "grp": c["grp"], "arc": c["arc"], "negative": c["w"], "ptag": c["p"],
                                   "pversion": a if c["p_custom"] else "us-gaap/2020", "ctag": c["c"],
                                   "cversion": a if c["c_custom"] else "us-gaap/2020"})
def w(path, cols, rows):
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, cols, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="\\", lineterminator="\n")
        wr.writeheader(); wr.writerows(rows)
for cik in subs:
    d = out / cik; d.mkdir(parents=True, exist_ok=True)
    w(d / "sub.tsv", SUB, subs[cik].values()); w(d / "pre.tsv", PRE, pre[cik]); w(d / "cal.tsv", CAL, cal[cik])
print("companies", len(subs), "filings", len(cik_of), "adsh seen in 2+ period files", dup)
