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
# BROAD debt-candidate net (Verifier 30-set rejection, D1): the old narrow
# regex missed whole face lines - KO NotesAndLoansPayable[Current] ("Loans and
# notes payable"), ORCL LongTermNotesAndLoans, AMD LinesOfCredit (plural).
# This is a wide CANDIDATE detector; membership is then decided by the face
# coverage check: every candidate is a member or carries a recorded exclusion,
# and anything unclassified fails the record (coverage_clean=false).
DEBT_RX = re.compile(
    r"Debt|Borrow|Loan|NotesPayable|NotesAndLoans|CommercialPaper|"
    r"Lines?OfCredit|Lease|Convertible|FinanceObligation|DueToRelatedParties"
)
# Members come ONLY from the balance-sheet statement role (Verifier V2 R1/R3:
# note-role arcs put MSFT/GOOG securities-lending and GE/AVGO/TSLA note lines
# into members). Aggregates stay role-wide: they are evidence, not members.
BS_ROLE_RX = re.compile(r"balance ?-?sheets?|financial ?position|financial ?condition", re.I)
# Verifier V3 defect 2: note roles can CONTAIN 'BalanceSheet' (AVGO
# CondensedConsolidatingFinancialInformationBalanceSheetDetails, GE Guarantor
# ...StatementOfFinancialPositionDetails, TSLA DisclosureVIE...Detail) - the
# statement role is the one WITHOUT these markers.
NOTE_ROLE_RX = re.compile(r"Detail|Disclosure|Consolidating|Guarantor|Parenthetical", re.I)
# Candidate lines that are NOT debt members, with the recorded reason.
EXCLUDE_CLASSES = [
    (re.compile(r"AccountsPayable|AccruedLiabilit", re.I), "excluded_combined_nondebt"),
    # a combined AP+accrued(+debt) line is never a debt member (AMAT 2015:
    # amat_AccountsPayableandAccruedLiabilitiesCurrentandDebtCurrent is the
    # face "Accounts payable and accrued expenses" row)
    (
        re.compile(
            r"Receivable|LeasedAsset|PropertySubjectTo|CapitalLeasedAssets|"
            r"CapitalLeases.*(BalanceSheet|Deprecation)|PropertyPlantandEquipment|"
            r"SolarEnergy|RightofUseAsset",
            re.I,
        ),
        "excluded_asset_side",
        # lenders' finance receivables (CAT/CSCO/GE), leased ASSETS
        # (TSLA solar/vehicles, WMT property under capital leases) - the
        # label net catches them; they are never liabilities
    ),
    (re.compile(r"ReserveFor", re.I), "excluded_equity_reserve"),
    # PG ReserveForEsopDebtRetirement is an equity-section contra, not debt
    (
        re.compile(r"DepositsReceivedForSecuritiesLoaned", re.I),
        "excluded_securities_lending_payable",
        # Dhairya ruling under delegation (Std Lead to confirm): collateral
        # payable, not a borrowing; was +430M MSFT 2014, +62% GOOG 2015
    ),
    (
        re.compile(r"^(ShortTerm|LongTerm)DebtAssumed$"),
        "excluded_intercompany_elimination",
        # GE's 'assumed by GE / GE Capital' lines are 0 in the consolidated
        # column (0000040545-19-000014 R4); only the consolidated context counts
    ),
    (
        re.compile(r"^(LongTerm)?LeaseLiabilit(y|ies)(Current|Noncurrent)?$"),
        "excluded_mixed_lease",
        # a GENERIC 'lease liability' line (AMZN custom LeaseLiabilityNoncurrent)
        # mixes operating and finance leases; needs the lease note to split -
        # excluded (hold) rather than guessed (Verifier V2 R2)
    ),
]
# Never part of any debt perimeter even though the name matches ("Lease"):
# straight-line rent and similar accruals would be false positives; keep the
# regex result but classify, and let the replay variants decide.
FINANCE_LEASE_RX = re.compile(r"FinanceLease|CapitalLease")
OPERATING_LEASE_RX = re.compile(r"OperatingLease")
BORROWING_RX = re.compile(r"Debt|Borrow|CommercialPaper|NotesPayable|LineOfCredit|Convertible")
ERA_RX = re.compile(r"us-gaap[/-](\d{4})")


# Combined by NAME: the tag itself joins borrowings and leases.
COMBINED_TAGS = {
    "DebtAndCapitalLeaseObligations",
    "DebtLongtermAndShorttermCombinedAmount",
}
# Combined only WITH EVIDENCE (Verifier re-check 2026-10-24): DebtCurrent /
# DebtNoncurrent MAY hold a lease part (MU, GOOG 2015-16) or may be pure
# borrowings (MRK, INTC, CSCO, UNH - no lease fact exists at those dates).
# Evidence = the filer's own calc children of the line, or a same-date
# finance/capital-lease fact with no separate same-side lease line on the face.
DEFINITIONAL_MAYBE = {"DebtCurrent", "DebtNoncurrent"}


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


def is_custom(href: str) -> bool:
    """A non-us-gaap/ifrs prefix marks a filer extension tag; its values never
    reach the companyfacts API, so a replay must route it to the instance
    reader instead of silently treating it as absent (Verifier V3)."""
    prefix = href.split("#")[-1].split("_", 1)[0].lower()
    return prefix not in ("us-gaap", "ifrs-full", "srt", "dei")


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
            child_custom = child_q.split("_", 1)[0].lower() not in ("us-gaap", "ifrs-full", "srt", "dei")
            arcs.setdefault((role, parent), []).append(
                (child, str(float(rel.get("weight") or 1)), child_custom)
            )
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
        loc = {
            l.get(XL + "label"): (tag_of(l.get(XL + "href")), is_custom(l.get(XL + "href")))
            for l in link.iter(NS + "loc")
        }
        for a in link.iter(NS + "calculationArc"):
            parent = loc.get(a.get(XL + "from"))
            child = loc.get(a.get(XL + "to"))
            if parent is None or child is None:
                continue
            w = a.get("weight") or "1"
            arcs.setdefault((role, parent[0]), []).append((child[0], str(float(w)), child[1]))
    return {"era": era, "arcs": arcs}


def debt_observation(adsh: str, form: str, period: str, cal: dict) -> dict:
    members: dict[str, dict] = {}
    for (role, parent), children in cal["arcs"].items():
        if parent not in PARENTS or not BS_ROLE_RX.search(role) or NOTE_ROLE_RX.search(role):
            continue
        for child, weight, child_custom in children:
            if not DEBT_RX.search(child) or EXCLUDE_RX.search(child):
                continue
            side = "current" if parent == "LiabilitiesCurrent" else "noncurrent"
            key = f"{side}:{child}"
            excl = next((reason for rx, reason in EXCLUDE_CLASSES if rx.search(child)), None)
            members.setdefault(
                key,
                {
                    "tag": child,
                    "side": side,
                    "class": excl or classify(child),
                    "custom": child_custom,
                    "weight": weight,
                    "calc_parent": parent,
                    "roles": [],
                },
            )["roles"].append(role)
    aggregates = {}
    for (role, parent), children in cal["arcs"].items():
        if AGG_PARENT_RX.match(parent):
            aggregates.setdefault(parent, {})[role] = [
                {"tag": c, "weight": w, "class": classify(c)} for c, w, _ in children
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


def collapse(observations: list[dict], company: str, lease_facts: dict) -> list[dict]:
    """Consecutive identical fingerprints -> one PROPOSED slot record."""
    records = []
    run: list[dict] = []
    for obs in observations:
        if run and obs["debt_fingerprint"] != run[-1]["debt_fingerprint"]:
            records.append(_record(run, company, lease_facts))
            run = []
        run.append(obs)
    if run:
        records.append(_record(run, company, lease_facts))
    return records


def _apply_lease_evidence(record: dict, run: list[dict], company: str, lease_facts: dict) -> None:
    """DebtCurrent/DebtNoncurrent become 'combined' only with evidence; the
    rule is era-level: any period in the era with a same-side lease fact (and
    no separate same-side lease line on the face) marks the line combined."""
    face_lease_sides = {
        m["side"] for m in record["members"] if m["class"] in ("finance_lease", "operating_lease")
    }
    periods = {o["period_of_report"] for o in run}
    for m in record["members"]:
        if m["tag"] not in DEFINITIONAL_MAYBE:
            continue
        side_key = "cur" if m["side"] == "current" else "noncur"
        calc_children = [
            c["tag"]
            for o in run
            for role_children in (o.get("aggregates", {}).get(m["tag"], {}) or {}).values()
            for c in role_children
        ]
        lease_dates = lease_facts.get((company, side_key), set())
        # FSDS dates are month-rounded, so match on year-month; "ALL" means a
        # lease fact exists at every instant for this company/side.
        period_months = {p[:7] for p in periods if p}
        lease_months = {d[:7] for d in lease_dates if d != "ALL"}
        has_lease_fact = "ALL" in lease_dates or bool(period_months & lease_months)
        if any(FINANCE_LEASE_RX.search(c) or OPERATING_LEASE_RX.search(c) for c in calc_children):
            m["class"], m["class_evidence"] = "combined", "calc_children"
        elif m["side"] not in face_lease_sides and has_lease_fact:
            m["class"], m["class_evidence"] = "combined", "same_date_lease_fact"
        else:
            m["class"], m["class_evidence"] = "borrowing", "no_lease_part_found"


def _record(run: list[dict], company: str, lease_facts: dict) -> dict:
    first, last = run[0], run[-1]
    record = {
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
        "members": [dict(m) for m in first["members"]],
    }
    _apply_lease_evidence(record, run, company, lease_facts)
    return record


def load_lease_facts(path: Path | None) -> dict:
    """CSV ticker,end_date,side -> {(ticker, side): {end_date, ...}}"""
    facts: dict[tuple[str, str], set] = {}
    if path is None or not path.exists():
        return facts
    for line in path.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        ticker, end_date, side = line.strip().split(",")
        facts.setdefault((ticker, side), set()).add(end_date)
    return facts


def main() -> None:
    cal_dir, acc_file, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    company = sys.argv[4] if len(sys.argv) > 4 else "MU"
    lease_facts = load_lease_facts(Path(sys.argv[5]) if len(sys.argv) > 5 else None)
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
    records = collapse(observations, company, lease_facts)
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
