"""Filer-printed capex totals BELOW the investing total (supplemental block of the cash-flow face),
for every cell of a capex release (Verifier V13 / Dhairya 2026-11-01, ACI: the face prints
"Total payments for capital investments, excluding lease buyouts" 1,467.4M under the investing
section while the investing line includes buyouts, 1,475.1M; the filer's own total is the anchor).

A supplemental capex figure = a cash-flow row after the investing total, same filing and column,
carrying a capex element (PaymentsToAcquire...PropertyPlantAndEquipment / ProductiveAssets ...)
or labelled as a capital expenditures / capital investments total. Where one exists and differs
from the release value, the cell leaves the release: to the keep-list when production equals the
filer's figure, else to a hold. Removal only. Zero SEC requests (FSN face extract).
usage: capex_supplemental_totals.py <release1_cells.jsonl> <cf_face.jsonl.gz> <out.json>
"""
import gzip
import json
import re
import sys
from decimal import Decimal

rel_path, face_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
INV_TOTAL = ("NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations")
OP_TOTAL = ("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations")
CAPEX_EL = re.compile(r"^(PaymentsToAcquirePropertyPlantAndEquipment|PaymentsToAcquireProductiveAssets|"
                      r"PaymentsToAcquireOtherPropertyPlantAndEquipment|PaymentsForCapitalImprovements)$")
TOTAL_LABEL = re.compile(r"total .*capital (expenditure|investment)|capital (expenditures|investments),? total|^total capex", re.I)

rel = [json.loads(x) for x in open(rel_path)]
by_acc = {}
for r in rel:
    by_acc.setdefault(r["accession"], []).append(r)
found = []
for line in gzip.open(face_path, "rt"):
    acc = line[10:30]
    if acc not in by_acc:
        continue
    f = json.loads(line)
    rows_cf = [x for x in f["face"] if x["stmt"] == "CF"]
    reps = {x["report"] for x in rows_cf if x["tag"] in OP_TOTAL + INV_TOTAL}
    for r in by_acc[acc]:
        col = f"{r['end'].replace('-', '')}|{r['qtrs']}"
        vals = f["values"].get(col, {})
        for rep in reps:
            rows = [x for x in rows_cf if x["report"] == rep]
            inv_i = max((i for i, x in enumerate(rows) if x["tag"] in INV_TOTAL), default=None)
            if inv_i is None:
                continue
            for x in rows[inv_i + 1:]:
                if x["tag"] not in vals or not (CAPEX_EL.match(x["tag"]) or TOTAL_LABEL.search(x["plabel"])):
                    continue
                if re.search(r"proceeds|sale|accrued|accrual|payable|non.?cash|incurred|financed|leases? obligation", x["plabel"], re.I):
                    continue  # supplemental non-cash / accrual disclosures are not the cash capex total
                v = abs(Decimal(vals[x["tag"]]))
                if v == 0:
                    continue  # a zero supplemental line is not a capex total (KDP "Payments for Capital Improvements" 0)
                rv = Decimal(r["value"])
                if v != rv:
                    p = Decimal(r["prod_value"]) if r["prod_value"] else None
                    found.append({"cik": r["cik"], "ticker": r["ticker"], "end": r["end"], "qtrs": r["qtrs"], "accession": acc,
                                  "release_value": str(rv), "filer_supplemental_total": str(v), "label": x["plabel"], "tag": x["tag"],
                                  "prod_value": r["prod_value"],
                                  "to": "keep_list" if p is not None and p == v else "hold_filer_total_differs"})
seen, out = set(), []
for x in found:
    k = (x["cik"], x["end"], x["qtrs"])
    if k not in seen:
        seen.add(k)
        out.append(x)
json.dump(out, open(out_path, "w"), indent=1)
from collections import Counter
print(len(out), "cells leave release 1:", dict(Counter(x["to"] for x in out)), Counter(x["ticker"] for x in out).most_common(15))
