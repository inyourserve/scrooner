"""Operating-income blank reasons from the filing's own face (stdlib, run with -I;
no database). Founder-side ruling relayed by the manager 2026-10-31: no
derivation of operating income; where the face prints no operating line the
cell is blank with reason line_not_presented_in_filing (JCI from FY2016 Q3,
BALL from 2024 Q2).

A cell (start, end) gets the reason when:
  * the ORIGINAL filing of that column (is_replay cells of another family give
    the filing's face columns and their accession) has gate
    no_printed_operating_line, AND
  * its face carries no line that could be an operating subtotal under any tag
    (stricter than the detector: a custom or standard line labelled
    operating income/profit/earnings, income from operations, EBIT or
    'before interest and (income) taxes' disqualifies the filing), AND
  * no filing prints an operating line for that column (the operating-income
    dry run has no slot cell for it).
Production's current state is carried: prod blank -> reason only (closes a
reasonless blank); prod has a value -> the value is a derivation the face does
not support -> would_hide stratum (own Verifier draw).
Rows are in the analytics.cell_blank_reason shape (migration 0100).
usage: is_oi_not_presented.py <is_fsn_dir> <is_filing_slots.jsonl> <oi_cells.jsonl> <out_dir> <cells.jsonl>...
  the trailing cells files (net income, revenue dry runs) supply face columns
"""
import glob
import gzip
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RULE = "slot.is_operating_income_not_presented@1"
OPERATING_LIKE = re.compile(
    r"operating (income|profit|loss|earnings)|income \(loss\) from operations|(income|earnings|profit|loss) from operations|"
    r"before interest|\bebit\b|operating (\(loss\) )?income", re.I)


def grain(start, end):
    from datetime import date
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
    return "FY" if days >= 350 else ("Q" if days <= 100 else "TP")


def main(fsn_dir, slots_path, oi_cells_path, out_dir, *col_files):
    nolines = {}
    for line in open(slots_path):
        s = json.loads(line)
        if s["family"] == "operating_income" and s["gate"] == "no_printed_operating_line":
            nolines[s["adsh"]] = s
    # stricter face check: any operating-like line on the primary face disqualifies
    disq = set()
    for p in sorted(glob.glob(f"{fsn_dir}/*_is_pre.jsonl.gz")):
        rows = defaultdict(list)
        for line in gzip.open(p, "rt"):
            if '"adsh": "' in line:
                r = json.loads(line)
                if r["adsh"] in nolines:
                    rows[r["adsh"]].append(r)
        for adsh, rs in rows.items():
            rep = nolines[adsh]["report"]
            if any(r["report"] == rep and (OPERATING_LIKE.search(r["label"]) and not re.search(r"expense|cost|activities|lease", r["label"], re.I))
                   for r in rs):
                disq.add(adsh)
    oi = {}
    for line in open(oi_cells_path):
        c = json.loads(line)
        oi[(c["cik"], c["start"], c["end"])] = c
    cols = {}
    for f in col_files:
        for line in open(f):
            c = json.loads(line)
            if c.get("accession") and c.get("original"):
                cols.setdefault((c["cik"], c["start"], c["end"]), c["accession"])
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, stats = [], Counter()
    for (cik, s0, e0), acc in sorted(cols.items()):
        if acc not in nolines:
            continue
        if acc in disq:
            stats["skipped_operating_like_line_on_face"] += 1
            continue
        c = oi.get((cik, s0, e0))
        if c and c["state"] == "slot_value":
            stats["skipped_another_filing_prints_the_line"] += 1
            continue
        if c and c["state"].startswith("hide"):
            stats["skipped_hide_stratum"] += 1
            continue
        prod = c.get("prod_value") if c else None
        stratum = "prod_blank_reason_only" if prod is None else "prod_has_value_would_hide"
        stats[stratum] += 1
        s = nolines[acc]
        rows.append({
            "cik": cik, "data_point_name": "operating_income", "period_grain": grain(s0, e0),
            "period_start": s0, "period_end": e0, "basis": "latest", "state": "not_presented",
            "rule_id": RULE, "reason_code": "line_not_presented_in_filing",
            "reason_text": "the filing's income statement prints no operating income line; not derived",
            "input_refs": {"accession": acc, "form": s["form"], "face_report": s["report"], "shape": s["shape"]},
            "stratum": stratum, "prod_value": prod, "prod_cf_id": c.get("prod_cf_id") if c else None,
        })
    # Q4 (manager 2026-10-31): production's 3-month Q4 = FY - 9M; when the FY column
    # is not presented, that Q4 has no filed basis either -> would-hide, same reason,
    # the FY filing's accession as evidence
    fy_np = {(r["cik"], r["period_end"]): r for r in rows if r["period_grain"] == "FY"}
    for (cik, s0, e0), c in sorted(oi.items()):
        # the replay labels these either prod_only_q4_not_a_face_column or, when the end
        # date is the held 10-K's own period, prod_only_filing_held:<gate>
        if c["state"] not in ("prod_only_q4_not_a_face_column", "prod_only_filing_held:no_printed_operating_line") \
                or c.get("prod_value") is None or grain(s0, e0) != "Q":
            continue
        if any((cik, s0, e0) == (r["cik"], r["period_start"], r["period_end"]) for r in rows if r["cik"] == cik):
            continue
        fy = fy_np.get((cik, e0))
        if fy is None:
            continue
        stats["q4_prod_has_value_would_hide"] += 1
        rows.append({
            "cik": cik, "data_point_name": "operating_income", "period_grain": "Q",
            "period_start": s0, "period_end": e0, "basis": "latest", "state": "not_presented",
            "rule_id": RULE, "reason_code": "line_not_presented_in_filing",
            "reason_text": "fourth quarter derived from a full year whose income statement prints no operating income line; not derived",
            "input_refs": {**fy["input_refs"], "q4_from_fy": [fy["period_start"], fy["period_end"]]},
            "stratum": "q4_prod_has_value_would_hide", "prod_value": c["prod_value"], "prod_cf_id": c.get("prod_cf_id"),
        })
    for st in ("prod_blank_reason_only", "prod_has_value_would_hide", "q4_prod_has_value_would_hide"):
        p = out / f"is_oi_not_presented_{st}.jsonl"
        with open(p, "w") as f:
            for r in rows:
                if r["stratum"] == st:
                    f.write(json.dumps(r, sort_keys=True) + "\n")
        stats[st + "_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    by_co = Counter(r["cik"] for r in rows)
    summary = {"rule_id": RULE, "cells": len(rows), "companies": len(by_co),
               "companies_reason_only": len({r["cik"] for r in rows if r["stratum"] == "prod_blank_reason_only"}),
               "companies_would_hide": len({r["cik"] for r in rows if r["stratum"] == "prod_has_value_would_hide"}),
               "companies_q4_would_hide": len({r["cik"] for r in rows if r["stratum"] == "q4_prod_has_value_would_hide"}),
               "by_grain": dict(Counter(r["period_grain"] for r in rows)),
               "by_shape": dict(Counter(r["input_refs"]["shape"] for r in rows)),
               "filings_disqualified_operating_like_line": len(disq), **stats}
    json.dump(summary, open(out / "NOT_PRESENTED_SUMMARY.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
