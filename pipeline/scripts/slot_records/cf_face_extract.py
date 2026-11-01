"""Cohort cash-flow and income-statement FACE rows with their duration values,
from the LOCAL FSN extracts (bucket fsn-notes; zero SEC requests).

For every 10-K/10-Q (and amendments) of a cohort CIK: the CF and IS rows of
pre.tsv (report, line, tag, plabel, negating, custom) and, from num.tsv, every
duration value (qtrs > 0, USD, undimensioned, primary registrant: iprx 0, no
coreg) for a tag printed on those faces, same accession by construction.
cal.tsv arcs between two printed face tags are kept (grp, parent, child,
weight) so a printed child is never summed beside its printed parent.
One JSON object per filing, gzip.
usage: cf_face_extract.py <fsn_dir> <cohort.csv> <out.jsonl.gz> [STMTS] [instant]
  STMTS: comma list of statements (default CF,IS); 'instant' keeps qtrs = 0 values (balance sheet)
  instead of durations. fsn_dir may hold <period>_<table>.tsv.zst flat or in <period>/ subfolders.
"""
import csv
import glob
import gzip
import io
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)
fsn, cohort_csv, out_path = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
STMTS = set((sys.argv[4] if len(sys.argv) > 4 else "CF,IS").split(","))
INSTANT = len(sys.argv) > 5 and sys.argv[5] == "instant"


def table(per, name):
    flat = fsn / f"{per}_{name}.tsv.zst"
    return flat if flat.exists() else fsn / per / f"{per}_{name}.tsv.zst"
cohort = {int(r["cik"]): r["ticker"] for r in csv.DictReader(open(cohort_csv))}
FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT"}
NO_DIM = "0x00000000"
STD = ("us-gaap", "srt", "dei", "ifrs")


def rows(path):
    proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    yield from csv.DictReader(io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace"), delimiter="\t")


n_fil = 0
with gzip.open(out_path, "wt") as fo:
    for sub_path in sorted(glob.glob(str(fsn / "*_sub.tsv.zst")) + glob.glob(str(fsn / "*" / "*_sub.tsv.zst"))):
        per = Path(sub_path).name.split("_")[0]
        filings = {}
        for r in rows(sub_path):
            if r["form"] in FORMS and int(r["cik"]) in cohort:
                filings[r["adsh"]] = {"adsh": r["adsh"], "cik": int(r["cik"]), "ticker": cohort[int(r["cik"])],
                                      "form": r["form"], "period": r["period"], "fy": r["fy"], "fp": r["fp"],
                                      "filed": r["filed"], "fsn_period": per, "face": [], "values": defaultdict(dict)}
        wanted = defaultdict(set)
        for r in rows(table(per, "pre")):
            f = filings.get(r["adsh"])
            if f is None or r["stmt"] not in STMTS:
                continue
            f["face"].append({"stmt": r["stmt"], "report": int(r["report"]), "line": int(r["line"]), "tag": r["tag"],
                              "plabel": r["plabel"], "negating": r["negating"] == "1",
                              "custom": not r["version"].startswith(STD), "inpth": r["inpth"] == "1"})
            wanted[r["adsh"]].add(r["tag"])
        for r in rows(table(per, "num")):
            w = wanted.get(r["adsh"])
            if not w or r["tag"] not in w or r["uom"] != "USD" or r["dimh"] != NO_DIM:
                continue
            if (r["qtrs"] != "0") if INSTANT else (r["qtrs"] in ("0", "")):
                continue
            if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", "") or r["value"] in ("", None):
                continue
            filings[r["adsh"]]["values"][f"{r['ddate']}|{r['qtrs']}"][r["tag"]] = r["value"]
        for r in rows(table(per, "cal")):
            w = wanted.get(r["adsh"])
            if w and r["ptag"] in w and r["ctag"] in w:
                filings[r["adsh"]].setdefault("cal", []).append(
                    [r["grp"], r["ptag"], r["ctag"], int(float(r.get("negative") or 1))])
        k = 0
        for f in filings.values():
            if not f["face"]:
                continue
            f["face"].sort(key=lambda x: (x["stmt"], x["report"], x["line"]))
            fo.write(json.dumps(f) + "\n")
            k += 1
        n_fil += k
        print(f"{per}: {k} filings with CF/IS face", flush=True)
print(f"total filings {n_fil} -> {out_path}")
