"""Income-statement face rows and calc arcs from one FSN period (stdlib, run with -I).

Reads <period>_sub/pre/cal.tsv.zst from the FSN data set (bucket fsn-notes,
or a local copy) and writes, for the selected CIKs' periodic filings:
  <out_dir>/<period>_is_pre.jsonl.gz  face rows of the IS and CI statements
      (inpth = 0, i.e. never the parenthetical), one row per presented line,
      with the filer's label and negating flag; report/line kept so the
      caller can sort into statement order (pre.txt is not in order).
  <out_dir>/<period>_cal.jsonl.gz     every calc arc of those filings (the
      statement of a group is decided later by the elements it totals).
No values. A tag is custom when its version is the filing's own adsh (or not
a standard taxonomy).
usage: fsn_is_pre.py <fsn_root> <period> <cik-list-or-@file> <out_dir>
"""
import csv
import gzip
import io
import json
import subprocess
import sys
from pathlib import Path

csv.field_size_limit(1 << 24)
FORMS = {"10-K", "10-K/A", "10-KT", "10-Q", "10-Q/A", "10-QT"}
STMTS = {"IS", "CI"}
STD = ("us-gaap", "srt", "dei", "ifrs", "invest")


def tsv(path):
    p = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    fh = io.TextIOWrapper(p.stdout, encoding="utf-8", errors="replace", newline="")
    yield from csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
    p.wait()


def main(root, period, ciks, out_dir):
    if ciks.startswith("@"):
        ciks = {line.strip().zfill(10) for line in open(ciks[1:]) if line.strip()}
    else:
        ciks = {c.strip().zfill(10) for c in ciks.split(",")}
    d = Path(root) / period
    subs = {}
    for r in tsv(d / f"{period}_sub.tsv.zst"):
        if r["cik"].zfill(10) in ciks and r["form"] in FORMS:
            subs[r["adsh"]] = {"cik": r["cik"].zfill(10), "form": r["form"], "period": r["period"],
                               "filed": r["filed"], "fy": r.get("fy", ""), "fp": r.get("fp", "")}
    out = Path(out_dir)
    n_pre = n_cal = 0
    with gzip.open(out / f"{period}_is_pre.jsonl.gz", "wt") as o:
        for r in tsv(d / f"{period}_pre.tsv.zst"):
            s = subs.get(r["adsh"])
            if s is None or r["stmt"] not in STMTS or r["inpth"] != "0":
                continue
            custom = r["version"] == r["adsh"] or not r["version"].startswith(STD)
            o.write(json.dumps({**s, "adsh": r["adsh"], "stmt": r["stmt"], "report": int(r["report"]),
                                "line": int(r["line"]), "tag": r["tag"], "custom": custom,
                                "label": r["plabel"], "negating": r["negating"] == "1"}) + "\n")
            n_pre += 1
    with gzip.open(out / f"{period}_cal.jsonl.gz", "wt") as o:
        for r in tsv(d / f"{period}_cal.tsv.zst"):
            if r["adsh"] not in subs:
                continue
            o.write(json.dumps({"adsh": r["adsh"], "grp": r["grp"], "arc": r["arc"],
                                "w": r.get("negative") or "1", "p": r["ptag"], "c": r["ctag"],
                                "c_custom": r["cversion"] == r["adsh"] or not r["cversion"].startswith(STD),
                                "p_custom": r["pversion"] == r["adsh"] or not r["pversion"].startswith(STD)}) + "\n")
            n_cal += 1
    print(f"{period}: filings {len(subs)} is_rows {n_pre} cal_arcs {n_cal}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
