"""Cash-flow and income-statement face rows for the cohort from the FSN
data sets (stdlib, run with -I; zstd CLI). Zero SEC requests: the inputs are
the `fsn-notes` bucket extracts (<period>/<period>_{pre,sub}.tsv.zst).

One row per face line in the shape era_detect_family.py reads, plus the
filer's own face label (`label`, FSN plabel) and `negating`, which the D&A /
capex perimeter rules need (APPROVAL-DA-CAPEX-2026-10-26: the label or an
income-statement tie decides an `other_amort` line; the face subsection
decides continuing vs discontinued capex). Parenthetical rows (inpth=1) are
dropped; periodic forms only.
usage: cf_face_rows.py <fsn_root> <cohort.csv> <out.jsonl.gz> [stmts=CF,IS]
"""
import csv
import glob
import gzip
import io
import json
import subprocess
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)
FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT"}
STD = ("us-gaap", "srt", "dei", "ifrs")


def tsv(path):
    proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    return csv.DictReader(io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace"), delimiter="\t", quoting=csv.QUOTE_NONE)


root, cohort_csv, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
stmts = set((sys.argv[4] if len(sys.argv) > 4 else "CF,IS").split(","))
ciks = {int(r["cik"]) for r in csv.DictReader(open(cohort_csv))}
n_rows = n_filings = 0
seen = set()
with gzip.open(out, "wt") as fo:
    for sub_path in sorted(glob.glob(str(root / "*" / "*_sub.tsv.zst"))):
        period_dir = Path(sub_path).parent
        subs = {}
        for r in tsv(sub_path):
            if int(r["cik"]) in ciks and r["form"] in FORMS and r["adsh"] not in seen:
                subs[r["adsh"]] = r
        seen.update(subs)
        pre_path = period_dir / f"{period_dir.name}_pre.tsv.zst"
        k = 0
        for r in tsv(pre_path):
            s = subs.get(r["adsh"])
            if s is None or r["stmt"] not in stmts or r["inpth"] != "0":
                continue
            fo.write(json.dumps({
                "adsh": r["adsh"], "cik": f"{int(s['cik']):010d}", "form": s["form"],
                "period": s["period"], "filed": s["filed"], "fy": s["fy"], "fp": s["fp"],
                "stmt": r["stmt"], "report": int(r["report"]), "line": int(r["line"]),
                "tag": r["tag"], "custom": not r["version"].startswith(STD),
                "label": r["plabel"], "negating": r["negating"] == "1",
                "fsn": period_dir.name,  # where this filing's cal/num rows live
            }) + "\n")
            k += 1
        n_rows += k
        n_filings += len(subs)
        print(f"  {period_dir.name}: {len(subs)} filings, {k} rows", flush=True)
print(f"cohort face rows: {n_filings} filings, {n_rows} rows ({','.join(sorted(stmts))})")
