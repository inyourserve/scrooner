"""All undimensioned USD INSTANT facts (face and notes) of every 10-K/10-Q of the given CIKs, from
the local FSN extracts, plus their balance-sheet face rows; one JSON object per filing (gzip).
Zero SEC requests. For slot replays whose members can sit in notes (finance-lease liabilities,
current maturities inside other current liabilities).
usage: fsn_company_instants.py <fsn_dir> <cik,cik,...> <out.jsonl.gz>
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
fsn, ciks, out = Path(sys.argv[1]), {int(x) for x in sys.argv[2].split(",")}, sys.argv[3]
FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT"}


def rows(path):
    proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
    yield from csv.DictReader(io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace"), delimiter="\t")


def table(per, name):
    flat = fsn / f"{per}_{name}.tsv.zst"
    return flat if flat.exists() else fsn / per / f"{per}_{name}.tsv.zst"


n = 0
with gzip.open(out, "wt") as fo:
    for sub in sorted(glob.glob(str(fsn / "*_sub.tsv.zst")) + glob.glob(str(fsn / "*" / "*_sub.tsv.zst"))):
        per = Path(sub).name.split("_")[0]
        fil = {r["adsh"]: {"adsh": r["adsh"], "cik": int(r["cik"]), "form": r["form"], "period": r["period"], "filed": r["filed"],
                           "bs": [], "values": defaultdict(dict)}
               for r in rows(sub) if r["form"] in FORMS and int(r["cik"]) in ciks}
        if not fil:
            continue
        for r in rows(table(per, "pre")):
            if r["adsh"] in fil and r["stmt"] == "BS":
                fil[r["adsh"]]["bs"].append({"report": int(r["report"]), "line": int(r["line"]), "tag": r["tag"], "plabel": r["plabel"]})
        for r in rows(table(per, "num")):
            f = fil.get(r["adsh"])
            if f is None or r["qtrs"] != "0" or r["uom"] != "USD" or r["dimh"] != "0x00000000" or r["value"] in ("", None):
                continue
            if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", ""):
                continue
            f["values"][r["ddate"]][r["tag"]] = r["value"]
        for f in fil.values():
            f["bs"].sort(key=lambda x: (x["report"], x["line"]))
            fo.write(json.dumps(f) + "\n")
            n += 1
        print(per, len(fil), flush=True)
print("filings", n)
