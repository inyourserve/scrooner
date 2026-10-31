"""Rebuild the two FSDS-shaped cohort inputs from the FSN extracts (bucket fsn-notes, downloaded
per quarter as <root>/<q>/<q>_{sub,pre,num}.tsv.zst). Zero SEC requests.
  cohort_pre_rows.jsonl.gz : one row per FSN pre line: cik (10-digit), adsh, form, period, filed,
                             stmt, report, line, tag, custom, label   (same shape bs_totals_detect reads)
  cohort_bs_dims.jsonl.gz  : dimensioned mezzanine-tag instants: cik, tag, ddate (what bs_assemble reads)
usage: fsn_cohort_inputs.py <fsn_root> <out_dir>
"""
import csv
import gzip
import io
import json
import re
import subprocess
import sys
from pathlib import Path

csv.field_size_limit(10**9)
root, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
MEZZ_RX = re.compile(r"TemporaryEquity|RedeemableNoncontrolling|RedeemablePreferred")
NO_DIM = "0x00000000"


def rd(p):
    return csv.DictReader(io.TextIOWrapper(subprocess.Popen(["zstd", "-dc", str(p)], stdout=subprocess.PIPE).stdout,
                                           encoding="utf-8", errors="replace"), delimiter="\t")


def dim_segments(quarter, need):
    """dimhash -> segments from the private bucket (SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY; run with the venv python)."""
    import os
    import ssl
    import urllib.request
    import certifi
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    req = urllib.request.Request(os.environ["SUPABASE_URL"].rstrip("/") + f"/storage/v1/object/fsn-notes/{quarter}/{quarter}_dim.tsv.zst",
                                 headers={"Authorization": "Bearer " + key, "apikey": key})
    data = urllib.request.urlopen(req, context=ssl.create_default_context(cafile=certifi.where()), timeout=600).read()
    txt = subprocess.run(["zstd", "-dc"], input=data, capture_output=True).stdout.decode("utf-8", "replace")
    o = {}
    for line in txt.split("\n")[1:]:
        p_ = line.split("\t")
        if len(p_) >= 2 and p_[0] in need:
            o[p_[0]] = p_[1]
    return o


npre = ndim = 0
with gzip.open(out / "cohort_pre_rows.jsonl.gz", "wt") as fp, gzip.open(out / "cohort_bs_dims.jsonl.gz", "wt") as fd:
    for qd in sorted(root.glob("20*")):
        q = qd.name
        sub = {r["adsh"]: r for r in rd(qd / f"{q}_sub.tsv.zst")}
        for r in rd(qd / f"{q}_pre.tsv.zst"):
            s = sub.get(r["adsh"])
            if not s or r["stmt"] != "BS":
                continue
            fp.write(json.dumps({"cik": s["cik"].zfill(10), "adsh": r["adsh"], "form": s["form"], "period": s["period"],
                                 "filed": s["filed"], "stmt": "BS", "report": int(r["report"]), "line": int(r["line"]),
                                 "tag": r["tag"], "custom": not r["version"].startswith(("us-gaap", "srt", "dei", "ifrs")),
                                 "label": r["plabel"]}) + "\n")
            npre += 1
        seen = set()
        cand = [r for r in rd(qd / f"{q}_num.tsv.zst")
                if r["dimh"] != NO_DIM and r["qtrs"] == "0" and MEZZ_RX.search(r["tag"])]
        segs = dim_segments(q, {r["dimh"] for r in cand}) if cand else {}
        for r in cand:
            # class-of-stock members only (as the FSDS dims extract did): a mezzanine-named tag on a
            # fair-value-hierarchy or other axis (AWK MandatorilyRedeemablePreferredStockFairValueDisclosure)
            # is a disclosure, not a balance-sheet mezzanine line
            if "StatementClassOfStockAxis" in segs.get(r["dimh"], ""):
                s = sub.get(r["adsh"])
                k = (s["cik"] if s else None, r["tag"], r["ddate"])
                if s and k not in seen:
                    seen.add(k)
                    fd.write(json.dumps({"cik": s["cik"].zfill(10), "tag": r["tag"], "ddate": r["ddate"]}) + "\n")
                    ndim += 1
        print(q, npre, ndim, flush=True)
