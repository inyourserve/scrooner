"""Build PROPOSED total-debt slot records for one company from its filings' own
calculation linkbases (stdlib only; run with python3 -I).

Input:  a directory of per-accession subdirs each holding that filing's *_cal.xml,
        and the accessions list file (lines: "<adsh> <form> <period_of_report>").
Output: JSONL, two kinds of line:
        kind=observation  - one per filing: the debt-family calc arcs it declares
        kind=slot_record  - consecutive filings with an identical debt fingerprint
                            collapsed into one era-spanned PROPOSED record

Nothing here touches a database. Values are NOT read; this emits structure only.
usage: build_debt_slots.py <cal_dir> <accessions_file> <out.jsonl>
"""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://www.xbrl.org/2003/linkbase}"
XL = "{http://www.w3.org/1999/xlink}"

# Parents whose children define the debt perimeter on the face balance sheet.
PARENTS = {"LiabilitiesCurrent", "LiabilitiesNoncurrent", "Liabilities"}
# A child is debt-family if it matches this (the pilot's regex, plus LineOfCredit).
DEBT_RX = re.compile(
    r"Debt|Borrow|Lease|CommercialPaper|NotesPayable|LineOfCredit|ConvertibleNotes"
)
# Never part of any debt perimeter even though the name matches ("Lease"):
# straight-line rent and similar accruals would be false positives; keep the
# regex result but classify, and let the replay variants decide.
FINANCE_LEASE_RX = re.compile(r"FinanceLease|CapitalLease")
OPERATING_LEASE_RX = re.compile(r"OperatingLease")
ERA_RX = re.compile(r"us-gaap[/-](\d{4})")


def classify(tag: str) -> str:
    if OPERATING_LEASE_RX.search(tag):
        return "operating_lease"
    if FINANCE_LEASE_RX.search(tag):
        return "finance_lease"
    return "borrowing"


def tag_of(href: str) -> str:
    return href.split("#")[-1].split("_", 1)[-1]


def parse_cal(path: Path) -> dict:
    """All (role, parent) -> [(child, weight)] plus the taxonomy era."""
    root = ET.parse(path).getroot()
    era = None
    m = ERA_RX.search(path.read_text(errors="replace")[:200000])
    if m:
        era = m.group(1)
    arcs: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for link in root.iter(NS + "calculationLink"):
        role = (link.get(XL + "role") or "").rsplit("/", 1)[-1]
        loc = {l.get(XL + "label"): tag_of(l.get(XL + "href")) for l in link.iter(NS + "loc")}
        for a in link.iter(NS + "calculationArc"):
            parent = loc.get(a.get(XL + "from"))
            child = loc.get(a.get(XL + "to"))
            if parent is None or child is None:
                continue
            arcs.setdefault((role, parent), []).append((child, a.get("weight") or "1"))
    return {"era": era, "arcs": arcs}


def debt_observation(adsh: str, form: str, period: str, cal: dict) -> dict:
    members: dict[str, dict] = {}
    for (role, parent), children in cal["arcs"].items():
        if parent not in PARENTS:
            continue
        for child, weight in children:
            if not DEBT_RX.search(child):
                continue
            side = "current" if parent == "LiabilitiesCurrent" else "noncurrent"
            key = f"{side}:{child}"
            members.setdefault(
                key,
                {
                    "tag": child,
                    "side": side,
                    "class": classify(child),
                    "weight": weight,
                    "calc_parent": parent,
                    "roles": [],
                },
            )["roles"].append(role)
    ordered = sorted(members.values(), key=lambda x: (x["side"], x["tag"]))
    fp_src = "|".join(f"{m['side']}:{m['tag']}:{m['weight']}" for m in ordered)
    return {
        "kind": "observation",
        "accession": adsh,
        "form": form,
        "period_of_report": period,
        "taxonomy_era": cal["era"],
        "debt_fingerprint": hashlib.sha256(fp_src.encode()).hexdigest()[:16],
        "members": ordered,
    }


def collapse(observations: list[dict], company: str) -> list[dict]:
    """Consecutive identical fingerprints -> one PROPOSED slot record."""
    records = []
    run: list[dict] = []
    for obs in observations:
        if run and obs["debt_fingerprint"] != run[-1]["debt_fingerprint"]:
            records.append(_record(run, company))
            run = []
        run.append(obs)
    if run:
        records.append(_record(run, company))
    return records


def _record(run: list[dict], company: str) -> dict:
    first, last = run[0], run[-1]
    return {
        "kind": "slot_record",
        "company": company,
        "canonical_concept": "total_debt",
        "rule_type": "slot_composition",
        "status": "proposed",
        "taxonomy_era_from": first["taxonomy_era"],
        "taxonomy_era_to": last["taxonomy_era"],
        "filing_from": first["accession"],
        "filing_to": last["accession"],
        "period_from": first["period_of_report"],
        "period_to": last["period_of_report"],
        "filings_observed": len(run),
        "debt_fingerprint": first["debt_fingerprint"],
        "evidence_accession": first["accession"],
        "evidence_level": "FILING-CHECKED",
        "source": "build_debt_slots.py (filer's own _cal.xml)",
        "members": first["members"],
    }


def main() -> None:
    cal_dir, acc_file, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    observations = []
    missing = []
    for line in acc_file.read_text().splitlines():
        if not line.strip():
            continue
        adsh, form, period = line.split()
        cals = sorted((cal_dir / adsh).glob("*_cal.xml"))
        if not cals:
            missing.append(adsh)
            continue
        observations.append(debt_observation(adsh, form, period, parse_cal(cals[0])))
    records = collapse(observations, "MU")
    with open(out_path, "w") as f:
        for obs in observations:
            f.write(json.dumps(obs) + "\n")
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    print(f"observations {len(observations)}  slot_records {len(records)}  missing_cal {missing}")
    for rec in records:
        tags = ", ".join(f"{m['side'][0]}:{m['tag']}({m['class'][0]})" for m in rec["members"])
        print(
            f"  era {rec['taxonomy_era_from']}-{rec['taxonomy_era_to']}"
            f"  {rec['period_from']}..{rec['period_to']}  x{rec['filings_observed']}  [{tags}]"
        )


if __name__ == "__main__":
    main()
