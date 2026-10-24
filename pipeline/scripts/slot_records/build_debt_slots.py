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
# LiabilitiesAndStockholdersEquity is real: NVDA FY2015 and GOOG 2015 put
# noncurrent debt lines directly under it (no Liabilities calc node).
PARENTS = {
    "LiabilitiesCurrent",
    "LiabilitiesNoncurrent",
    "Liabilities",
    "LiabilitiesAndStockholdersEquity",
}
# Children that match DEBT_RX lexically but are never debt (equity instruments,
# investment securities, totals of the statement itself).
EXCLUDE_RX = re.compile(
    r"PreferredStock|CommonStock|Equity|TreasuryStock|RetainedEarnings|"
    r"AccumulatedOtherComprehensive|CommitmentsAndContingencies|"
    r"DebtSecurities|SecuritiesBorrowed|LiabilitiesCurrent$|LiabilitiesNoncurrent$|"
    r"OtherThanLongtermDebt|"  # 'liabilities other than LTD' is the non-debt remainder line
    r"TemporaryEquity|RedeemableNoncontrolling"  # mezzanine, never total debt (Verifier: MU 2014-15 redeemable convertible notes)
)
# Debt AGGREGATE parents (face or note roles): their children are the filer's
# own statement of what a debt total contains (e.g. GOOG's note-level
# LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities).
AGG_PARENT_RX = re.compile(
    r"^(DebtAndCapitalLeaseObligations|DebtLongtermAndShorttermCombinedAmount|"
    r"LongTermDebtAndCapitalLeaseObligations(IncludingCurrentMaturities)?|"
    r"LongTermDebt|DebtCurrent|DebtNoncurrent)$"
)
# A child is debt-family if it matches this (the pilot's regex, plus LineOfCredit).
DEBT_RX = re.compile(
    r"Debt|Borrow|Lease|CommercialPaper|NotesPayable|LineOfCredit|Convertible"
)
# Never part of any debt perimeter even though the name matches ("Lease"):
# straight-line rent and similar accruals would be false positives; keep the
# regex result but classify, and let the replay variants decide.
FINANCE_LEASE_RX = re.compile(r"FinanceLease|CapitalLease")
OPERATING_LEASE_RX = re.compile(r"OperatingLease")
BORROWING_RX = re.compile(r"Debt|Borrow|CommercialPaper|NotesPayable|LineOfCredit|Convertible")
ERA_RX = re.compile(r"us-gaap[/-](\d{4})")


# Combined by the FASB definition itself, whatever the printed label says:
# DebtCurrent/DebtNoncurrent are "borrowings plus finance (capital) lease"
# aggregates (Verifier 2026-10-24: MU's "Current debt" DebtCurrent at
# 2021-09-02 is exactly the current finance-lease amount; GOOG's 2015-16
# "Short-term debt" DebtCurrent contains current capital leases).
COMBINED_TAGS = {
    "DebtCurrent",
    "DebtNoncurrent",
    "DebtAndCapitalLeaseObligations",
    "DebtLongtermAndShorttermCombinedAmount",
}


def classify(tag: str) -> str:
    """A line naming both a borrowing and a lease (or an explicit And-joined
    aggregate) is 'combined' and must never be mapped as either side alone."""
    if tag in COMBINED_TAGS:
        return "combined"
    is_borrowing = bool(BORROWING_RX.search(tag))
    is_fin_lease = bool(FINANCE_LEASE_RX.search(tag))
    is_op_lease = bool(OPERATING_LEASE_RX.search(tag))
    if is_borrowing and (is_fin_lease or is_op_lease):
        return "combined"
    if is_op_lease:
        return "operating_lease"
    if is_fin_lease:
        return "finance_lease"
    return "borrowing"


def tag_of(href: str) -> str:
    return href.split("#")[-1].split("_", 1)[-1]


def parse_metalinks(path: Path) -> dict:
    """Modern filings (e.g. MSFT 2024+) ship no separate _cal.xml; the calc
    relationships live in MetaLinks.json (instance -> tag -> calculation:
    child tag -> {role: {parentTag, weight}})."""
    data = json.loads(path.read_text())
    inst = next(iter(data["instance"].values()))
    era = None
    for ns in inst.get("nsprefix", {}).values() if isinstance(inst.get("nsprefix"), dict) else []:
        m = ERA_RX.search(str(ns))
        if m:
            era = m.group(1)
    if era is None:
        m = ERA_RX.search(path.read_text()[:500000])
        era = m.group(1) if m else None
    arcs: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for child_q, meta in inst.get("tag", {}).items():
        child = child_q.split("_", 1)[-1]
        for role_uri, rel in (meta.get("calculation") or {}).items():
            parent_q = rel.get("parentTag")
            if not parent_q:
                continue
            parent = parent_q.split("_", 1)[-1]
            role = role_uri.rsplit("/", 1)[-1]
            arcs.setdefault((role, parent), []).append((child, str(float(rel.get("weight") or 1))))
    return {"era": era, "arcs": arcs}


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
            w = a.get("weight") or "1"
            arcs.setdefault((role, parent), []).append((child, str(float(w))))
    return {"era": era, "arcs": arcs}


def debt_observation(adsh: str, form: str, period: str, cal: dict) -> dict:
    members: dict[str, dict] = {}
    for (role, parent), children in cal["arcs"].items():
        if parent not in PARENTS:
            continue
        for child, weight in children:
            if not DEBT_RX.search(child) or EXCLUDE_RX.search(child):
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
    aggregates = {}
    for (role, parent), children in cal["arcs"].items():
        if AGG_PARENT_RX.match(parent):
            aggregates.setdefault(parent, {})[role] = [
                {"tag": c, "weight": w, "class": classify(c)} for c, w in children
            ]
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
        "aggregates": aggregates,
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
    company = sys.argv[4] if len(sys.argv) > 4 else "MU"
    observations = []
    missing = []
    for line in acc_file.read_text().splitlines():
        if not line.strip():
            continue
        adsh, form, period = line.split()
        cals = sorted((cal_dir / adsh).glob("*_cal.xml"))
        meta = cal_dir / adsh / "MetaLinks.json"
        if cals:
            cal = parse_cal(cals[0])
        elif meta.exists():
            cal = parse_metalinks(meta)
        else:
            missing.append(adsh)
            continue
        observations.append(debt_observation(adsh, form, period, cal))
    records = collapse(observations, company)
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
