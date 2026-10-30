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
import os
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402
import common  # noqa: E402

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
FSN_QUARTER_OF = {}
if os.environ.get("FSN_ROOT"):  # adsh -> quarter, from the sub extracts
    import csv
    import subprocess
    import io
    csv.field_size_limit(10**9)
    for subf in sorted(Path(os.environ["FSN_ROOT"]).glob("20*/*_sub.tsv.zst")):
        fh = io.TextIOWrapper(subprocess.Popen(["zstd", "-dc", str(subf)], stdout=subprocess.PIPE).stdout, encoding="utf-8", errors="replace")
        for r in csv.DictReader(fh, delimiter="\t"):
            FSN_QUARTER_OF[r["adsh"]] = subf.parent.name
ARC_WEIGHT = {}  # (adsh, child) -> weight in the statement role (VMI: deferred taxes carry -1)


def load_cal(adsh):
    """The boundary filing's statement-role calc arcs (shared loader: _cal.xml -> .xsd -> MetaLinks)."""
    era, arcs = common.load_cal(cal_dir, adsh)
    if not arcs and os.environ.get("FSN_ROOT"):
        # no SEC-fetched cal on disk: the Notes data set's cal.tsv for the filing's quarter (zero SEC requests)
        q = FSN_QUARTER_OF.get(adsh)
        if q:
            arcs = common.fsn_cal_arcs(Path(os.environ["FSN_ROOT"]) / q / f"{q}_cal.tsv.zst", adsh)
            era = common.FSN_ERA.get(adsh) if arcs else None
    for (role, parent), kids in arcs.items():
        if b.BS_ROLE_RX.search(role) and not b.NOTE_ROLE_RX.search(role):
            for c, w, _cu in kids:
                ARC_WEIGHT.setdefault((adsh, c), w)
    return era, common.statement_children(arcs, b.BS_ROLE_RX) if arcs else {}


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
            # TAXONOMY-TOTAL coverage by face position (batch 2: TMUS 2015-18,
            # ALB 2015 - the filer's statement calc omits the arc from
            # LiabilitiesCurrent / LiabilitiesNoncurrent to their components,
            # so the total and its lines were both roots). A us-gaap total
            # element covers the liability lines PRINTED before it since the
            # previous total; the identity gate still decides publication.
            # This is an element rule (taxonomy totals), not a label rule.
            TOTALS = ("LiabilitiesCurrent", "LiabilitiesNoncurrent", "LiabilitiesOtherThanLongtermDebtNoncurrent")
            tax_covered = set()
            run = []
            for t in raw:
                if t in TOTALS:
                    tax_covered |= {x for x in run if x not in TOTALS}
                    run = []
                else:
                    run.append(t)
            # NOT dropped: capitalization-format filers (EMR, FE, NI, AWK) print
            # long-term debt BEFORE current liabilities, so 'covered' lines are
            # only an ALTERNATIVE reading; the replay publishes whichever
            # reading ties the identity (reading A: all cal roots; reading B:
            # roots minus taxonomy-total-covered lines).
            dedup_kind = ("cal_roots_borrowed" if borrowed else "cal_roots") if cal_children else "taxonomy_totals_only"
            if not cal_children and not (set(raw) & set(TOTALS)):
                # raw lines without ANY calc graph of this filer and no taxonomy
                # total on the face DOUBLE COUNT (FE +14.6B, DVN +2.5B when a
                # boundary cal is missing). No structure at all -> hold.
                liab_members = []
                rule = "hold_no_cal_for_dedup"
            else:
                liab_members = [
                    {"tag": t, "custom": by_tag.get(t, {}).get("custom", False),
                     "label": by_tag.get(t, {}).get("label", ""),
                     "cal_confirmed": t in cal_liab, "rule": "face_sum",
                     "weight": ARC_WEIGHT.get((adsh, t), "1.0"),
                     "dedup": dedup_kind, "tax_covered": t in tax_covered}
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
        # mezzanine = lines the detector CLASSED mezzanine by position, never
        # by name alone (Verifier BS-V2 fix 1: AWK's custom Total long-term
        # debt subtotal matched the pattern and would be subtracted twice)
        mezz_face = [z for z in zone if z["seg"] == "mezz"]
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
            "cal_source": ("own" if cal_children and not borrowed else
                           f"borrowed:{','.join(company_cal_sources[:3])}" if borrowed else
                           "none:taxonomy_totals" if rule == "face_sum" else None),
            "equity_parent_tag": equity_parent,
            "equity_component_tags": [z["tag"] for z in zone if z["seg"] == "equity_component" and not z["custom"]],
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
