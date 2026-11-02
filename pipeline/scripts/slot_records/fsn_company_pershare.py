"""Per-share lane reader for one company directory of the FSN store (run with -I; needs the pipeline venv for
share_basis). Format: data-team/47-fsn-store/FORMATS-v1.md section 1.

Cells (concept, end, months) from FILED copies only, with the EPS lane's own selection
(per_share/pershare_fsn_rules.py, moved verbatim from eps_fsn_scan.py):
  basic_eps_resolved / diluted_eps_resolved  NEVER derived. A quarter with no filed 3-month copy has no cell
                                             here (the calendar emitter blanks it: not filed separately).
  dividends_per_share_resolved               filed copies; Q4 = filed FY - filed 9M only when both are on
                                             ONE share basis (founder ruling 2026-11-04; share_basis's split
                                             signal rule: no signal in (filed 9M, filed FY]) and no 3-month
                                             Q4 copy is filed. The cell is state derived, both accessions kept.
  shares_outstanding_resolved                instants, filed copies only (instants are never derived).
Copies agree within 0.005 -> value of the earliest filed copy; else hidden `fsn_copies_disagree`.
FSN num filters as the scan: qtrs 1-4 (durations) or 0 (instants), dimn 0 or the 10-K quarterly-data axis,
iprx 0, no co-registrant, a value. Tag order per concept: the mapper's approved order (CONCEPT_MAPPINGS + NEW_CONCEPT_MAPPINGS), the
combined EarningsPerShareBasicAndDiluted as the EPS fallback (the lane's rule).
usage: fsn_company_pershare.py <companies/<cik10>|parent|@list> <out.jsonl>
"""
import json
import sys
from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "per_share"))
sys.path.insert(0, str(HERE.parents[1] / "src"))
from fsn_company import company_cik, company_dir_list, table  # noqa: E402
from pershare_fsn_rules import FORMS, select, swapped_copies  # noqa: E402
from scrooner_pipeline.corporate_actions import share_basis as sb  # noqa: E402
from scrooner_pipeline.mapper import concepts as mc  # noqa: E402
from scrooner_pipeline.mapper import expanded_concepts as mx  # noqa: E402

COMBINED = "EarningsPerShareBasicAndDiluted"
BASE = {"basic_eps_resolved": "basic_eps", "diluted_eps_resolved": "diluted_eps",
        "dividends_per_share_resolved": "dividends_per_share", "shares_outstanding_resolved": "shares_outstanding"}
assert set(BASE) == set(sb.TARGETS), "share_basis.TARGETS changed: re-check the per-share concepts"
EPS = ("basic_eps_resolved", "diluted_eps_resolved")
DPS = "dividends_per_share_resolved"
SHARES = "shares_outstanding_resolved"
LANE_TAGS = set(sb.EVIDENCE_PER_SHARE_TAGS) | set(sb.EVIDENCE_SHARE_TAGS) | set(sb.SERIES_TAGS)


def tag_order(concept):
    """the mapper's approved tags for the concept, priority order, that the per-share lane reads."""
    rows = sorted((r[3], r[2]) for r in [*mc.CONCEPT_MAPPINGS, *mx.NEW_CONCEPT_MAPPINGS]
                  if r[0] == BASE[concept] and r[4] == "approved")
    tags = [t for _p, t in rows if t in LANE_TAGS]
    if concept in EPS and COMBINED not in tags:
        tags.append(COMBINED)  # own tag first, the combined tag only when the own tag has no copy
    return tags


TAGS = {c: tag_order(c) for c in BASE}


def ymd(s):
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def months_back(dd, n):
    """the month end n months before the month end dd (yyyymmdd)."""
    y, m = divmod(int(dd[:4]) * 12 + int(dd[4:6]) - 1 - n, 12)
    return f"{y:04d}{m + 1:02d}{monthrange(y, m + 1)[1]:02d}"


def read_copies(d):
    cik = company_cik(d)
    subs = {}
    for r in table(d, "sub"):
        if r["cik"].zfill(10) == cik and r["form"] in FORMS and r["adsh"] not in subs:
            subs[r["adsh"]] = (cik, r["form"], r["filed"])
    seg = {r["dimhash"]: r["segments"] for r in table(d, "dim")}
    want = {t for ts in TAGS.values() for t in ts}
    signal_tags = {"EntityCommonStockSharesOutstanding", *sb.WEIGHTED_SHARE_TAGS}
    copies, signal_rows = defaultdict(list), []
    for r in table(d, "num"):
        s = subs.get(r["adsh"])
        if s is None or not r["value"] or r.get("iprx", "0") != "0" or r.get("coreg"):
            continue
        if r["tag"] in signal_tags and r.get("dimn", "0") == "0" and Decimal(r["value"]) > 0:
            signal_rows.append((r["tag"], r["qtrs"], r["ddate"], Decimal(r["value"]), ymd(s[2])))
        if r["tag"] not in want or r.get("dimn", "0") not in ("0", "1"):
            continue
        instant = r["tag"] in TAGS[SHARES]
        if (r["qtrs"] == "0") != instant or r["qtrs"] not in ("0", "1", "2", "3", "4"):
            continue
        segment = "" if r.get("dimn") == "0" else seg.get(r["dimh"], "?")
        copies[(s[0], r["tag"], r["ddate"], r["qtrs"])].append((r["value"], r["adsh"], s[1], s[2], segment))
    signal_rows.sort(key=lambda x: x[4])
    return cik, copies, sb.split_signal_dates_from_rows(signal_rows)


def company_cells(d):
    cik, copies, signals = read_copies(d)
    swapped = swapped_copies(copies)
    out = []
    keys = defaultdict(set)
    for (_c, tag, dd, q) in copies:
        for concept, tags in TAGS.items():
            if tag in tags:
                keys[concept].add((dd, q))
    chosen = {}
    for concept in BASE:
        for dd, q in sorted(keys[concept]):
            res = select(copies, swapped, cik, TAGS[concept], dd, q)
            verdict = {"replace_with_fsn_value": "filed", "fsn_copies_disagree": "hidden_fsn_copies_disagree",
                       "not_in_fsn": "hidden_only_rejected_axes"}[res["outcome"]]  # copies exist, none on an allowed axis
            cell = {"cik": cik, "concept": concept, "ddate": dd, "qtrs": int(q), "verdict": verdict,
                    "value": res.get("value"), "accession": res.get("accession"), "tag": res.get("tag"),
                    "copies": res.get("copies"), "axis": res.get("axis"), "values": res.get("values")}
            chosen[(concept, dd, q)] = cell
            out.append(cell)
    # Q4 DPS = FY - 9M on one share basis (founder 2026-11-04). Never for EPS, never for instants.
    # Both inputs come from ONE tag series (tags tried in priority order): CFG's 10-K tags the Q4 declared
    # 0.18 as CommonStockDividendsPerShareDeclared on a 12-month context beside CashPaid FY 0.64; mixing the
    # Declared FY with the CashPaid 9M (0.46) gave -0.28 (found by this port's gate, 2026-11-01).
    for (concept, dd, q), fy0 in sorted(chosen.items()):
        if concept != DPS or q != "4" or fy0["verdict"] != "filed" or (DPS, dd, "1") in chosen:
            continue
        d9 = months_back(dd, 3)
        for tag in TAGS[DPS]:
            fy, nine = select(copies, swapped, cik, [tag], dd, "4"), select(copies, swapped, cik, [tag], d9, "3")
            if fy["outcome"] == nine["outcome"] == "replace_with_fsn_value":
                break
        else:
            continue  # no tag carries both a filed FY and a filed 9M: no derivation
        lo, hi = sorted((ymd(fy["filed"]), ymd(nine["filed"])))
        zero = Decimal(fy["value"]) == 0 and Decimal(nine["value"]) == 0  # a zero is the same on every basis
        straddle = [s.isoformat() for s in signals if lo < s <= hi]
        q4 = Decimal(fy["value"]) - Decimal(nine["value"])
        cell = {"cik": cik, "concept": DPS, "ddate": dd, "qtrs": 1, "accession": fy["accession"],
                "inputs": [fy["accession"], nine["accession"]], "tag": tag, "policy": "same_vintage_one_basis"}
        if straddle and not zero:
            cell |= {"verdict": "hidden_dps_inputs_not_on_one_basis", "value": None, "split_signals": straddle}
        elif q4 < 0:
            cell |= {"verdict": "hidden_dps_q4_negative", "value": None, "candidate": str(q4)}  # residual guard
        else:
            cell |= {"verdict": "derived", "value": str(q4)}
        out.append(cell)
    return out


def main(arg, out_path):
    with open(out_path, "w") as fo:
        for d in company_dir_list(arg):
            for c in company_cells(d):
                fo.write(json.dumps(c) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
