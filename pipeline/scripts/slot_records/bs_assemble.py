"""Assemble balance-sheet-totals slot records (stdlib, run with -I).

Slots per era: total_liabilities (printed-total-first, else the face-sum
skeleton validated against the boundary cal's statement role), equity_parent
(printed StockholdersEquity / partners-capital line), nci (printed
MinorityInterest), mezzanine (temporary-equity zone lines; dimensioned
class-of-stock lines noted from the FSDS dims extract - their values never
reach the API). The accounting identity is the replay's cross-check, never a
source. Inherits: statement-role-only cal reads, note-role rejection, custom
flags, face-admission for standard tags.
usage: bs_assemble.py <bs_eras.json> <bs_cal_dir> <cohort_bs_dims.jsonl.gz> <out.jsonl>
"""
import gzip
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402

EQUITY_PARENT_TAGS = {
    "StockholdersEquity", "PartnersCapital", "MembersEquity",
    "PartnersCapitalAttributableToParent", "LimitedLiabilityCompanyLlcMembersEquity",
}
MEZZ_RX = re.compile(r"TemporaryEquity|RedeemableNoncontrolling|RedeemablePreferred")
NOISE_RX = re.compile(r"CommitmentsAndContingencies")
TICKER = json.loads('{"0000354190":"AJG","0001410636":"AWK","0001109354":"BRKR","0001393818":"BX","0001744489":"DIS","0001090012":"DVN","0000032604":"EMR","0001276187":"ET","0001031296":"FE","0000040545":"GE","0001404912":"KKR","0000927653":"MCK","0001111711":"NI","0000797468":"OXY","0000732717":"T","0001389170":"TRGP","0001035002":"VLO","0000104169":"WMT","0000079282":"BRO"}')

eras = json.load(open(sys.argv[1]))
cal_dir = Path(sys.argv[2])

# dimensioned mezzanine facts per (cik): dates where class-of-stock mezz lines exist
dim_mezz = defaultdict(set)
with gzip.open(sys.argv[3], "rt") as f:
    for line in f:
        r = json.loads(line)
        if MEZZ_RX.search(r["tag"]):
            dim_mezz[r["cik"]].add((r["tag"], r["ddate"]))

out = open(sys.argv[4], "w")
summary = []
def load_cal(adsh):
    """The boundary filing's statement-role calc arcs (cal.xml, else MetaLinks)."""
    cals = sorted((cal_dir / adsh).glob("*_cal.xml"))
    meta = cal_dir / adsh / "MetaLinks.json"
    if cals:
        cal = b.parse_cal(cals[0])
    elif meta.exists():
        cal = b.parse_metalinks(meta)
    else:
        return None, {}
    children = defaultdict(set)
    for (role, parent), kids in cal["arcs"].items():
        if not b.BS_ROLE_RX.search(role) or b.NOTE_ROLE_RX.search(role):
            continue
        children[parent].update(c for c, _, _ in kids)
    return cal["era"], children


for cik, era_list in sorted(eras.items()):
    ticker = TICKER.get(cik, cik)
    n_rec, dirty = 0, 0
    # The FILER'S OWN calc graph across all its boundary filings. An era whose
    # boundary filing has no cal file borrows it for subtotal dedup (Verifier
    # BS-V1 item 2: 129 clean ties were held as hold_no_cal_for_dedup); the
    # value is then published only if the accounting identity ties (replay).
    company_children = defaultdict(set)
    company_cal_sources = []
    for e2 in era_list:
        _, ch = load_cal(e2["first"])
        if ch:
            company_cal_sources.append(e2["first"])
            for p, kids in ch.items():
                company_children[p].update(kids)
    for era in era_list:
        adsh = era["first"]
        tax_era, cal_children = load_cal(adsh)
        borrowed = False
        if not cal_children and company_children:
            cal_children, borrowed = company_children, True
        cal_liab = set(cal_children.get("Liabilities", set()) | cal_children.get("LiabilitiesCurrent", set())
                       | cal_children.get("LiabilitiesNoncurrent", set())
                       | cal_children.get("LiabilitiesAndStockholdersEquity", set()))

        def descendants(tag, seen=None):
            seen = seen or set()
            for ch in cal_children.get(tag, ()):  # statement role only
                if ch not in seen:
                    seen.add(ch)
                    descendants(ch, seen)
            return seen
        zone = era["zone_lines"]
        anchors = era["anchors"]
        by_tag = {z["tag"]: z for z in zone}
        # total_liabilities slot
        if anchors["liabilities_total"]:
            liab_members = [{"tag": "Liabilities", "custom": False, "rule": "printed_total"}]
            rule = "printed_total"
        else:
            raw = era.get("skeleton", [])
            raw_set = set(raw)
            # ROOTS of the liability line set under the filer's own statement-
            # role calc graph: a subtotal keeps itself and drops its printed
            # cal-descendants (T: 'Total deferred credits...' covers exactly
            # its own group, never the standalone Long-Term Debt line)
            covered = set()
            for t in raw:
                covered |= descendants(t) & raw_set
            roots = [t for t in raw if t not in covered]
            if not cal_children:
                # raw lines without ANY calc graph of this filer DOUBLE COUNT
                # (subtotals + their components both summed: FE +14.6B,
                # DVN +2.5B when a boundary cal is missing). No cal -> hold.
                liab_members = []
                rule = "hold_no_cal_for_dedup"
            else:
                liab_members = [
                    {"tag": t, "custom": by_tag.get(t, {}).get("custom", False),
                     "label": by_tag.get(t, {}).get("label", ""),
                     "cal_confirmed": t in cal_liab, "rule": "face_sum",
                     "dedup": "cal_roots_borrowed" if borrowed else "cal_roots"}
                    for t in roots
                ]
                rule = "face_sum" if liab_members else "hold_no_liability_lines"
        # equity / nci / mezzanine slots
        eq_tags = [z["tag"] for z in zone if z["seg"] in ("equity_total", "nci", "equity_component")]
        equity_parent = next((t for t in eq_tags if t in EQUITY_PARENT_TAGS), None)
        nci = next((t for t in eq_tags if t in (
            "MinorityInterest", "NonredeemableNoncontrollingInterest",
            "PartnersCapitalAttributableToNoncontrollingInterest",
            "MinorityInterestInLimitedPartnerships")), None)
        mezz_face = [z for z in zone if MEZZ_RX.search(z["tag"])]
        mezz_dims = sorted({t for (t, _) in dim_mezz.get(cik, set())})
        rec = {
            "kind": "slot_record", "company": ticker, "cik": cik,
            "canonical_concept": "bs_totals", "rule_type": "slot_composition",
            "status": "proposed", "taxonomy_era_from": tax_era, "taxonomy_era_to": tax_era,
            "filing_from": era["first"], "filing_to": era["last"],
            "period_from": era["period_from"], "period_to": era["period_to"],
            "filings_observed": era["n"], "evidence_accession": era["first"],
            "evidence_level": "FILING-CHECKED",
            "source": "bs_assemble.py (FSDS skeleton + boundary statement-role cal)",
            "total_liabilities_rule": rule,
            "total_liabilities_members": liab_members,
            # a face-sum value is PUBLISHED only when assets = L + mezz +
            # equity(incl. NCI) ties within the filer's rounding unit on the
            # same filing (Verifier BS-V1: never produce a value beside a gap)
            "requires_identity_tie": rule == "face_sum",
            "cal_source": "own" if (rule == "face_sum" and not borrowed) else (
                f"borrowed:{','.join(company_cal_sources[:3])}" if borrowed else None),
            "equity_parent_tag": equity_parent,
            "nci_tag": nci,
            "mezzanine_face": [
                {"tag": z["tag"], "custom": z["custom"], "label": z["label"]} for z in mezz_face
            ],
            "mezzanine_dim_tags": mezz_dims,
            "coverage_clean": rule != "hold_no_liability_lines",
        }
        out.write(json.dumps(rec) + "\n")
        n_rec += 1
        dirty += 0 if rec["coverage_clean"] else 1
    summary.append((ticker, n_rec, dirty))
print(f"{'ticker':6} {'records':>7} {'holds':>5}")
for t, n, d in sorted(summary):
    print(f"{t:6} {n:>7} {d:>5}")
print("total:", sum(n for _, n, _ in summary), "holds:", sum(d for *_, d in summary))
