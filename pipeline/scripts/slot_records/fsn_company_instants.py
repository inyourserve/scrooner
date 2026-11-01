"""All undimensioned USD INSTANT facts (face and notes) of every 10-K/10-Q of the given CIKs, from
the local FSN extracts, plus their balance-sheet face rows; one JSON object per filing (gzip).
Zero SEC requests. For slot replays whose members can sit in notes (finance-lease liabilities,
current maturities inside other current liabilities).
usage: fsn_company_instants.py <fsn_dir> <cik,cik,...|@cohort.csv> <out.jsonl.gz> [debt]
  'debt' keeps only facts whose tag is on that filing's balance-sheet face or is debt/lease/borrowing
  vocabulary (notes included), to keep a cohort-wide extract small
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
fsn, out = Path(sys.argv[1]), sys.argv[3]
if sys.argv[2].startswith("@"):
    ciks = {int(r["cik"]) for r in csv.DictReader(open(sys.argv[2][1:]))}
else:
    ciks = {int(x) for x in sys.argv[2].split(",")}
DEBT_ONLY = len(sys.argv) > 4 and sys.argv[4] == "debt"
import re  # noqa: E402
DEBT_VOCAB = re.compile(r"Debt|Borrow|Loan|Notes|CommercialPaper|Lease|LineOfCredit|Convertible|FinanceObligation|"
                        r"^Liabilities|^Assets$|LiabilitiesAndStockholdersEquity|LiabilitiesAndPartnersCapital")
STD = ("us-gaap", "srt", "dei", "ifrs")
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
                fil[r["adsh"]]["bs"].append({"report": int(r["report"]), "line": int(r["line"]), "tag": r["tag"], "plabel": r["plabel"],
                                             "custom": not r["version"].startswith(STD)})
        for r in rows(table(per, "num")):
            f = fil.get(r["adsh"])
            if f is None or r["qtrs"] != "0" or r["uom"] != "USD" or r["dimh"] != "0x00000000" or r["value"] in ("", None):
                continue
            if (r.get("coreg") or "").strip() or (r.get("iprx") or "0") not in ("0", ""):
                continue
            if DEBT_ONLY and not DEBT_VOCAB.search(r["tag"]) and r["tag"] not in f.setdefault("_face", {x["tag"] for x in f["bs"]}):
                continue
            f["values"][r["ddate"]][r["tag"]] = r["value"]
        for f in fil.values():
            f.pop("_face", None)
            f["fsn_period"] = per
            f["bs"].sort(key=lambda x: (x["report"], x["line"]))
            fo.write(json.dumps(f) + "\n")
            n += 1
        print(per, len(fil), flush=True)
print("filings", n)
