"""Inputs for the cohort total-debt slot build from a cohort FSN instants extract
(fsn_company_instants.py ... debt): balance-sheet face rows for era_detect.py and the face-admission
guards, the accession -> FSN period map for assemble_fsn.py, and the lease-evidence CSV
(ticker,end_date,side wherever a finance/capital lease fact exists; build_debt_slots.load_lease_facts).
usage: debt_fsn_inputs.py <instants.jsonl.gz> <cohort.csv> <out_dir>
"""
import csv
import gzip
import json
import sys
from pathlib import Path

inst, cohort, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
tick = {int(r["cik"]): r["ticker"] for r in csv.DictReader(open(cohort))}
LEASE = {"cur": ("FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"),
         "noncur": ("FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent")}
adsh_period, lease = {}, set()
n = 0
with open(out / "bs_pre_rows.jsonl", "w") as fo:
    for line in gzip.open(inst, "rt"):
        f = json.loads(line)
        cik = f"{f['cik']:010d}"
        adsh_period[f["adsh"]] = f["fsn_period"]
        for r in f["bs"]:
            fo.write(json.dumps({"adsh": f["adsh"], "cik": cik, "form": f["form"], "period": f["period"], "filed": f["filed"],
                                 "stmt": "BS", "report": r["report"], "line": r["line"], "tag": r["tag"],
                                 "custom": r.get("custom", False), "label": r["plabel"]}) + "\n")
            n += 1
        for d, vals in f["values"].items():
            for side, tags in LEASE.items():
                if any(t in vals and vals[t] not in ("0", "0.0000") for t in tags):
                    lease.add((tick.get(f["cik"], cik), f"{d[:4]}-{d[4:6]}-{d[6:]}", side))
json.dump(adsh_period, open(out / "adsh_period.json", "w"))
with open(out / "lease_facts.csv", "w") as fo:
    fo.write("ticker,end_date,side\n")
    for t, d, s in sorted(lease):
        fo.write(f"{t},{d},{s}\n")
print("bs rows", n, "filings", len(adsh_period), "lease facts", len(lease))
