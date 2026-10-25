"""Assemble the 30-company-set debt slot records (stdlib, run with -I).
"""
import re  # noqa: E402,F401

_DOC = """

Joins FSDS-detected eras (era_detect.py) with the boundary filings' own calc
linkbases: each era's members come from its first filing's _cal.xml; adjacent
eras whose CAL debt fingerprints are identical are re-collapsed (a face
label/order change with no calc change is not a format change). Lease
classification follows the Verifier's evidence rule via build_debt_slots.
usage: assemble30.py <eras.json> <boundary_cal_dir> <lease_facts.csv> <out.jsonl> [face_rows.jsonl(.gz)]
  face_rows: FSDS pre rows (stmt=BS) of the boundary filings, for the
  face-admission guards; without it no face line is admitted.
"""  # noqa: E501
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_debt_slots as b  # noqa: E402
import face_admission as fa  # noqa: E402

TICKER = {
    "0000002488": "AMD", "0000006951": "AMAT", "0000018230": "CAT", "0000021344": "KO",
    "0000040545": "GE", "0000050863": "INTC", "0000059478": "LLY", "0000080424": "PG",
    "0000093410": "CVX", "0000104169": "WMT", "0000200406": "JNJ", "0000310158": "MRK",
    "0000320193": "AAPL", "0000354950": "HD", "0000707549": "LRCX", "0000723125": "MU",
    "0000731766": "UNH", "0000789019": "MSFT", "0000858877": "CSCO", "0000909832": "COST",
    "0001018724": "AMZN", "0001045810": "NVDA", "0001065280": "NFLX", "0001141391": "MA",
    "0001181412": "SPCX", "0001318605": "TSLA", "0001326801": "META", "0001341439": "ORCL",
    "0001413329": "PM", "0001551152": "ABBV", "0001652044": "GOOG", "0001720592": "RPAY",
    "0001730168": "AVGO",
}

eras = json.load(open(sys.argv[1]))
cal_dir = Path(sys.argv[2])
lease_facts = b.load_lease_facts(Path(sys.argv[3]))
out = open(sys.argv[4], "w")

# ordered BS face rows per boundary filing (for the face-admission guards)
face_rows: dict[str, list] = {}
if len(sys.argv) > 5:
    boundary = {e["first"] for el in eras.values() for e in el}
    tmp = defaultdict(list)
    opener = gzip.open if sys.argv[5].endswith(".gz") else open
    with opener(sys.argv[5], "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("stmt") == "BS" and r["adsh"] in boundary:
                tmp[r["adsh"]].append((r["report"], r["line"], {"tag": r["tag"], "custom": r["custom"], "label": r.get("label") or ""}))
    face_rows = {a: [d for _, _, d in sorted(v, key=lambda x: (x[0], x[1]))] for a, v in tmp.items()}

summary = []
for cik, era_list in sorted(eras.items()):
    ticker = TICKER[cik]
    obs_list = []
    missing = []
    for era in era_list:
        adsh = era["first"]
        cals = sorted((cal_dir / adsh).glob("*_cal.xml"))
        meta = cal_dir / adsh / "MetaLinks.json"
        if cals:
            cal = b.parse_cal(cals[0])
        elif meta.exists():
            cal = b.parse_metalinks(meta)
        else:
            missing.append(adsh)
            continue
        obs = b.debt_observation(adsh, era["form"], era["period_from"], cal)
        obs["era_span"] = era  # carry the FSDS span
        obs_list.append(obs)
    # re-collapse adjacent eras with identical CAL fingerprints
    records = []
    for obs in obs_list:
        if records and records[-1]["debt_fingerprint"] == obs["debt_fingerprint"]:
            prev = records[-1]
            prev["period_to"] = obs["era_span"]["period_to"]
            prev["filing_to"] = obs["era_span"]["last"]
            prev["filings_observed"] += obs["era_span"]["n"]
            prev["taxonomy_era_to"] = obs["taxonomy_era"]
            continue
        span = obs["era_span"]
        rec = {
            "kind": "slot_record", "company": ticker, "cik": cik,
            "canonical_concept": "total_debt", "rule_type": "slot_composition",
            "status": "proposed",
            "taxonomy_era_from": obs["taxonomy_era"], "taxonomy_era_to": obs["taxonomy_era"],
            "filing_from": span["first"], "filing_to": span["last"],
            "period_from": span["period_from"], "period_to": span["period_to"],
            "filings_observed": span["n"], "debt_fingerprint": obs["debt_fingerprint"],
            "evidence_accession": span["first"], "evidence_level": "FILING-CHECKED",
            "source": "assemble30.py (FSDS eras + boundary _cal.xml)",
            "members": [dict(m) for m in obs["members"]],
        }
        run = [{"period_of_report": span["period_from"], "aggregates": obs.get("aggregates", {})},
               {"period_of_report": span["period_to"], "aggregates": obs.get("aggregates", {})}]
        b._apply_lease_evidence(rec, run, ticker, lease_facts)
        # Verifier V5 (WSO 2024-12-31): a debt-and-lease total whose own calc
        # children (any role) include an OPERATING lease line (321,715K of
        # operating leases inside 'LongTermDebtAndCapitalLeaseObligations',
        # and in the current-portion tag beside it) must never feed a
        # borrowings slot: class it excluded_mixed_lease so the lease-evidence
        # path and the Verifier see it.
        any_role_children = fa.all_role_children(cal["arcs"])
        for m in rec["members"]:
            if not m["class"].startswith("excluded_") and any(
                "OperatingLease" in ch for ch in fa.descendants(any_role_children, m["tag"])
            ):
                m["class"] = "excluded_mixed_lease"
                m["mixed_lease_evidence"] = sorted(
                    ch for ch in fa.descendants(any_role_children, m["tag"]) if "OperatingLease" in ch
                )
        # cal-sourced exclusions (e.g. combined AP lines) are bookkept as
        # exclusions, never as members
        excluded_members = [m for m in rec["members"] if m["class"].startswith("excluded_")]
        rec["members"] = [m for m in rec["members"] if not m["class"].startswith("excluded_")]
        # FACE COVERAGE CHECK (Verifier D1): every face line that reads as debt
        # (by tag or printed label) is a member or carries a recorded exclusion;
        # anything else fails the record.
        member_tags = {m["tag"] for m in rec["members"]}
        excluded, uncovered = [], []
        for cand in span.get("candidates", []):
            tag = cand["tag"]
            if tag in member_tags:
                continue
            reason = next((rsn for rx, rsn in b.EXCLUDE_CLASSES if rx.search(tag)), None)
            if reason is None and b.EXCLUDE_RX.search(tag):
                reason = "excluded_structural"
            if reason is None and not b.DEBT_RX.search(tag):
                reason = "label_match_only_nondebt_tag"
            if reason:
                excluded.append({"tag": tag, "label": cand["label"], "reason": reason})
                continue
            side = (
                "current" if re.search(r"Current$|^ShortTerm", tag)
                else "noncurrent" if re.search(r"Noncurrent$|^LongTerm", tag)
                else None
            )
            if not cand["custom"] and side:
                # a STANDARD face line missing from the statement-role cal
                # (AVGO 2018: LiabilitiesCurrent children live only in the
                # consolidating-note role) may be admitted from the face itself,
                # behind the Verifier's four guards (face_admission.py): never
                # an Abstract row, only inside the liabilities zone, never a
                # calc descendant / total / component of a member, and a value
                # tie at replay. Custom uncovered lines stay dirty for the Verifier.
                face = face_rows.get(adsh, [])
                ok, why, tie = fa.admit(tag, face, cal["arcs"], member_tags, side) if face else (
                    False, "no_face_rows_for_boundary_filing", None)
                if ok:
                    rec["members"].append(
                        {"tag": tag, "side": side, "class": b.classify(tag), "custom": False,
                         "weight": "1.0", "calc_parent": None, "roles": [],
                         "source": "face_line_not_in_statement_cal", "tie": tie}
                    )
                    member_tags.add(tag)
                else:
                    excluded.append({"tag": tag, "label": cand["label"], "reason": f"face_admission_rejected:{why}"})
            else:
                uncovered.append({"tag": tag, "label": cand["label"], "custom": cand["custom"]})
        excluded.extend(
            {"tag": m["tag"], "label": "", "reason": m["class"]} for m in excluded_members
        )
        rec["excluded_candidates"] = excluded
        rec["uncovered_candidates"] = uncovered
        rec["coverage_clean"] = not uncovered
        records.append(rec)
    for rec in records:
        out.write(json.dumps(rec) + "\n")
    dirty = sum(1 for r in records if not r["coverage_clean"])
    summary.append((ticker, len(era_list), len(records), len(missing), dirty))

print(f"{'ticker':6} {'fsds_eras':>9} {'cal_records':>11} {'missing_cal':>11} {'NOT_COVERED':>11}")
for t, fe, cr, mi, dirty in sorted(summary):
    print(f"{t:6} {fe:>9} {cr:>11} {mi:>11} {dirty:>11}")
print(
    "total records:", sum(c for _, _, c, _, _ in summary),
    "missing:", sum(m for *_, m, _ in summary),
    "coverage_dirty:", sum(d for *_, d in summary),
)
