"""Plan the extra R pages the hand check needs: NOTE rows' pages, component_in_note pages, and the R page presenting
finance lease liabilities (founder 2026-11-04 item 5: total_debt includes finance leases). Companies whose MetaLinks
is not cached get MetaLinks.json requested first. usage: plan_pages.py reads_out tool_cache ranks.csv > request.csv"""

import csv
import json
import re
import sys
from pathlib import Path

out, cache = Path(sys.argv[1]), Path(sys.argv[2])
ranks = list(csv.DictReader(Path(sys.argv[3]).read_text().splitlines()))
key = lambda u: re.sub(r"\W", "_", u)[-150:]
LEASE = (
    "FinanceLeaseLiabilityCurrent",
    "FinanceLeaseLiabilityNoncurrent",
    "FinanceLeaseLiability",
    "FinanceLeaseLiabilityCurrentStatementOfFinancialPositionExtensibleList",
)
w = csv.writer(sys.stdout)
w.writerow(["cik", "ticker", "accession", "statements", "extras", "pages"])
stats = {"metalinks_needed": 0, "pages": 0, "lease_cos": 0}
for r in ranks:
    t = r["ticker"]
    md = (out / f"{t}-docmap-2026-11-12.md").read_text()
    m = re.search(r"10-K (\d{10}-\d\d-\d{6}) \(CIK (\d{10}), filed", md)
    if not m:
        continue
    accn, cik = m.groups()
    base = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/"
    )
    rows = list(csv.DictReader((out / f"{t}-docmap-2026-11-12.csv").open()))
    pages = {
        x["r_page"]
        for x in rows
        if x["stmt"] == "NOTE" or x["status"] == "component_in_note"
    }
    ml = cache / key(base + "MetaLinks.json")
    if not ml.exists():
        stats["metalinks_needed"] += 1
        pages.add("MetaLinks.json")
    else:
        inst = next(iter(json.loads(ml.read_text())["instance"].values()))
        role2r = {
            v.get("role"): (k, v.get("groupType", ""), v.get("menuCat", ""))
            for k, v in inst.get("report", {}).items()
        }
        for tg in LEASE:
            tt = inst.get("tag", {}).get(f"us-gaap_{tg}")
            if not tt:
                continue
            rs = sorted(
                (role2r[x] for x in tt.get("presentation", []) if x in role2r),
                key=lambda x: (x[2] != "Details", int(re.sub(r"\D", "", x[0]) or 0)),
            )
            if rs:
                pages.add(f"{rs[0][0]}.htm")
                stats["lease_cos"] += 1
                break
    pages = sorted(p for p in pages if p and not (cache / key(base + p)).exists())
    if pages:
        stats["pages"] += len(pages)
        w.writerow([cik, t, accn, "0", "0", ";".join(pages)])
print(json.dumps(stats), file=sys.stderr)
