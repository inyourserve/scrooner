"""One-time FASB US-GAAP taxonomy fetch -> slim element attribute CSV (stdlib).

Approved by Dhairya 2026-10-25 under conditions: generic UA
'Scrooner-research/1.0 (no contact)', <= 1 request/second, ONE fetch, the zip
is deleted after extraction. Output columns: name, balance (debit/credit/''),
period_type (instant/duration), abstract (0/1), type. This is the structural
balance-attribute guard behind the lexical ones in bs_totals_detect.py and
face_admission.py: an element with balance=credit on the liabilities side is a
liability or equity; a debit-balance element printed in the liabilities zone
(NFG UnamortizedLossReacquiredDebtNoncurrent) is never a liability member.
usage: fasb_elements.py <year> <out.csv>
"""
import csv
import io
import shutil
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

year = sys.argv[1]
out = Path(sys.argv[2])
UA = "Scrooner-research/1.0 (no contact)"
url = f"https://xbrl.fasb.org/us-gaap/{year}/us-gaap-{year}.zip"
tmp = out.parent / f"_us-gaap-{year}.zip"
if shutil.disk_usage("/private/tmp").free < 4 * 1024**3:
    sys.exit("free disk < 4 GB; not fetching")
t0 = time.monotonic()
req = urllib.request.Request(url, headers={"User-Agent": UA})
with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
    shutil.copyfileobj(r, f)
print(f"fetched {url} {tmp.stat().st_size/1e6:.1f} MB in {time.monotonic()-t0:.0f}s (1 request)")

XS = "{http://www.w3.org/2001/XMLSchema}"
XBRLI = "{http://www.xbrl.org/2003/instance}"
rows = []
with zipfile.ZipFile(tmp) as z:
    names = [n for n in z.namelist() if n.endswith(".xsd") and "/elts/" in n and f"us-gaap-{year}" in n.rsplit("/", 1)[-1]]
    names = names or [n for n in z.namelist() if n.endswith(f"us-gaap-{year}.xsd")]
    if not names:
        sys.exit("element schema not found in zip: " + ", ".join(z.namelist()[:10]))
    for n in names:
        root = ET.parse(io.BytesIO(z.read(n))).getroot()
        for el in root.iter(XS + "element"):
            name = el.get("name")
            if not name:
                continue
            rows.append({
                "name": name,
                "balance": el.get(XBRLI + "balance") or "",
                "period_type": el.get(XBRLI + "periodType") or "",
                "abstract": "1" if (el.get("abstract") or "false").lower() == "true" else "0",
                "type": (el.get("type") or "").split(":")[-1],
            })
tmp.unlink()  # the zip is deleted after extraction
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name", "balance", "period_type", "abstract", "type"])
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r["name"]))
print(f"elements {len(rows)} -> {out} ({out.stat().st_size/1e6:.2f} MB); credit {sum(r['balance']=='credit' for r in rows)} debit {sum(r['balance']=='debit' for r in rows)} abstract {sum(r['abstract']=='1' for r in rows)}")
