"""Assemble D&A / capex slot records (stdlib, run with -I).

Members come from the FSDS face lines already embedded in the family eras
(the cash-flow face answers the composition question for these families);
the boundary filing's calc linkbase supplies the taxonomy era key and
confirms each member's section parent (operating / investing), recorded as
`section_confirmed`. Adjacent eras with identical member sets after dropping
IS sub-lines are NOT re-collapsed: an IS sub-line change is still a face
change worth keeping visible for these families.
usage: assemble_family.py <family> <eras.json> <fam_cal_dir> <out.jsonl>
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402
import family_config as fc  # noqa: E402

TICKER = {
    "0000002488": "AMD", "0000006951": "AMAT", "0000018230": "CAT", "0000021344": "KO",
    "0000040545": "GE", "0000050863": "INTC", "0000059478": "LLY", "0000073309": "NUE",
    "0000080424": "PG", "0000093410": "CVX", "0000097476": "TXN", "0000104169": "WMT",
    "0000200406": "JNJ", "0000310158": "MRK", "0000320193": "AAPL", "0000354950": "HD",
    "0000707549": "LRCX", "0000723125": "MU", "0000731766": "UNH", "0000789019": "MSFT",
    "0000858877": "CSCO", "0000909832": "COST", "0001018724": "AMZN", "0001045810": "NVDA",
    "0001065280": "NFLX", "0001141391": "MA", "0001181412": "SPCX", "0001318605": "TSLA",
    "0001326801": "META", "0001341439": "ORCL", "0001413329": "PM", "0001551152": "ABBV",
    "0001652044": "GOOG", "0001720592": "RPAY", "0001730168": "AVGO", "0001772177": "KRUS",
}
SECTION_PARENT = {
    "d_and_a": re.compile(r"NetCashProvidedByUsedInOperatingActivities"),
    "capex": re.compile(r"NetCashProvidedByUsedInInvestingActivities"),
}
CF_ROLE_RX = re.compile(r"cash ?-?flows?", re.I)

family, eras_path, cal_dir, out_path = sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[4]
eras = json.load(open(eras_path))
out = open(out_path, "w")
summary = []
for cik, era_list in sorted(eras.items()):
    ticker = TICKER[cik]
    n_rec = 0
    for era in era_list:
        adsh = era["first"]
        cals = sorted((cal_dir / adsh).glob("*_cal.xml"))
        meta = cal_dir / adsh / "MetaLinks.json"
        tax_era, arcs = None, {}
        if cals:
            cal = b.parse_cal(cals[0])
            tax_era, arcs = cal["era"], cal["arcs"]
        elif meta.exists():
            cal = b.parse_metalinks(meta)
            tax_era, arcs = cal["era"], cal["arcs"]
        parent_rx = SECTION_PARENT[family]
        confirmed = set()
        # the filer's own cash-flow SECTION arithmetic from the statement role
        # (never a note role): the section total tag and its signed roots. The
        # replay publishes a member value only when the section ties on the
        # same accession (the analogue of the balance-sheet identity gate;
        # a verdict never depends on production's value).
        section = {}
        for (role, parent), children in arcs.items():
            if not parent_rx.search(parent):
                continue
            confirmed.update(c for c, *_ in children)
            if b.NOTE_ROLE_RX.search(role) or not CF_ROLE_RX.search(role):
                continue
            if len(children) > len(section.get("roots", [])):
                section = {"total": parent, "role": role,
                           "roots": [{"tag": c, "weight": w, "custom": cu} for c, w, cu in children]}
        members = []
        for m in era["members"]:
            mm = dict(m)
            mm["class"] = fc.classify(family, m["tag"], m["stmt"])  # classes come from family_config NOW, not from era-detect time
            mm["section_confirmed"] = m["tag"] in confirmed if m["stmt"] == "CF" else None
            if m["custom"]:
                mm["value_derivable_from_api"] = False  # custom tags never reach companyfacts
            members.append(mm)
        # MEMBER-LEVEL composition (gate design 2026-10-25): among the CF
        # members, which are calc parents of which, in the cash-flow STATEMENT
        # role (never a note role). G1: a single root member = the printed
        # line. G2: a parent whose printed children tie to it.
        cf_tags = {m["tag"] for m in members if m["stmt"] == "CF"}
        parent_of = {}
        for (role, parent), children in arcs.items():
            if b.NOTE_ROLE_RX.search(role) or not CF_ROLE_RX.search(role):
                continue
            if parent in cf_tags:
                for c, w, cu in children:
                    if c in cf_tags:
                        parent_of[c] = {"parent": parent, "weight": w}
        roots = sorted(t for t in cf_tags if t not in parent_of)
        composition = {
            "roots": roots,
            "children_of": {p: sorted(c for c, v in parent_of.items() if v["parent"] == p) for p in set(v["parent"] for v in parent_of.values())},
            "weights": {c: v["weight"] for c, v in parent_of.items()},
            "has_statement_cal": bool(section),
        }
        rec = {
            "kind": "slot_record", "company": ticker, "cik": cik,
            "canonical_concept": family, "rule_type": "slot_composition",
            "status": "proposed",
            "taxonomy_era_from": tax_era, "taxonomy_era_to": tax_era,
            "filing_from": era["first"], "filing_to": era["last"],
            "period_from": era["period_from"], "period_to": era["period_to"],
            "filings_observed": era["n"],
            "evidence_accession": era["first"], "evidence_level": "FILING-CHECKED",
            "source": f"assemble_family.py ({family}: FSDS face lines + boundary cal)",
            "members": members,
            "section": section or None,  # the section arithmetic, informational since the gate redesign
            "composition": composition,
        }
        out.write(json.dumps(rec) + "\n")
        n_rec += 1
    summary.append((ticker, n_rec))
print(f"family {family}: records {sum(n for _, n in summary)}")
for t, n in sorted(summary):
    print(f"  {t:6} {n}")
