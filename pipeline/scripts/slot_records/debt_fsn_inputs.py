"""Inputs for the cohort total-debt slot build from a cohort FSN instants extract
(fsn_company_instants.py ... debt): balance-sheet face rows for era_detect.py and the face-admission
guards, the accession -> FSN period map for assemble_fsn.py, and the lease-evidence CSV
(ticker,end_date,side wherever a finance/capital lease fact exists; build_debt_slots.load_lease_facts).
usage: debt_fsn_inputs.py <instants.jsonl.gz> <cohort.csv> <out_dir>
The per-filing transforms (face_rows, lease_evidence) are shared with the FSN store
company reader (fsn_company_bs.py), so company mode builds the same rows.
"""
import csv
import gzip
import json
import sys
from pathlib import Path

LEASE = {"cur": ("FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"),
         "noncur": ("FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent")}


def face_rows(f):
    """bs_pre_rows.jsonl rows of one instants filing object."""
    cik = f"{f['cik']:010d}"
    for r in f["bs"]:
        yield {"adsh": f["adsh"], "cik": cik, "form": f["form"], "period": f["period"], "filed": f["filed"],
               "stmt": "BS", "report": r["report"], "line": r["line"], "tag": r["tag"],
               "custom": r.get("custom", False), "label": r["plabel"]}


def lease_evidence(f, tick):
    """(ticker, end_date, side) wherever the filing carries a non-zero finance/capital lease fact."""
    cik = f"{f['cik']:010d}"
    out = set()
    for d, vals in f["values"].items():
        for side, tags in LEASE.items():
            if any(t in vals and vals[t] not in ("0", "0.0000") for t in tags):
                out.add((tick.get(f["cik"], cik), f"{d[:4]}-{d[4:6]}-{d[6:]}", side))
    return out


def lease_facts_dict(lease):
    """the in-memory shape of build_debt_slots.load_lease_facts for a lease_evidence set."""
    facts: dict[tuple[str, str], set] = {}
    for t, d, s in sorted(lease):
        facts.setdefault((t, s), set()).add(d)
    return facts


def ticker_map(cohort):
    return {int(r["cik"]): r["ticker"] for r in csv.DictReader(open(cohort))}


def main(argv):
    inst, cohort, out = argv[1], argv[2], Path(argv[3])
    out.mkdir(parents=True, exist_ok=True)
    tick = ticker_map(cohort)
    adsh_period, lease = {}, set()
    n = 0
    with open(out / "bs_pre_rows.jsonl", "w") as fo:
        for line in gzip.open(inst, "rt"):
            f = json.loads(line)
            adsh_period[f["adsh"]] = f["fsn_period"]
            for row in face_rows(f):
                fo.write(json.dumps(row) + "\n")
                n += 1
            lease |= lease_evidence(f, tick)
    json.dump(adsh_period, open(out / "adsh_period.json", "w"))
    with open(out / "lease_facts.csv", "w") as fo:
        fo.write("ticker,end_date,side\n")
        for t, d, s in sorted(lease):
            fo.write(f"{t},{d},{s}\n")
    print("bs rows", n, "filings", len(adsh_period), "lease facts", len(lease))


if __name__ == "__main__":
    main(sys.argv)
