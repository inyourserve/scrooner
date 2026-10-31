"""Emit the `pershare_derived` family file (CELL-FORMAT-v1, data-team/46-canonical-fact-v2) from Family C's reviewed plan.

Keys: every EPS cell of the cohort that today rests on a derived (subtracted) quarter, base and *_resolved twins.
EPS is never derived (founder rule): no `derived` rows. Per Family C outcome:
  remove not filed separately (FY on/after 2021-08-09, or the Item 302(a) relief 10-K printing no quarterly table)
                         -> state not_presented, reason per_share_not_filed_separately
  remove not captured    -> state defect (ingestion; the 10-K printed it, we have not read it), per_share_not_captured
  remove copies disagree -> state defect (guard_hidden, period), restated_copies_disagree
  replace with FSN value -> state value, DATA-INFERRED, accession / tag / fsn_set from the FSN scan (no core.fact row)
  review                 -> state defect (finding_open), held_pending_verifier
  replace with filed fact (204) -> NOT emitted: a filed fact is scrooner-28's pershare_filed key.
Inputs (read-only): Family C cells CSV (dry run v4), the FSN outcomes, the relief evidence, core.period for dates.
usage: emit_cells_pershare_derived.py <cells.csv> <fsn_outcomes.json> <relief_candidates.json> <relief_evidence.json>
                                      <out_dir> <git_commit>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ro import conn  # noqa: E402

RULE = "pershare.derived_eps_retired@1"
FAMILY = "pershare_derived"
NEW_CODES = {
    "per_share_not_filed_separately": "the fiscal year's 10-K does not print a separate Q4 per-share figure "
    "(fiscal years ending on/after 2021-08-09, or an earlier 10-K using the Item 302(a) relief); EPS is never derived",
    "per_share_not_captured": "the 10-K's quarterly table prints the Q4 figure but it is not in our XBRL data; "
    "never derived; recovery pending (HTML table reader)",
}


def main(
    cells_csv: str,
    fsn_path: str,
    relief_cands: str,
    relief_ev: str,
    out_dir: str,
    commit: str,
) -> None:
    cells = list(csv.DictReader(open(cells_csv)))
    fsn = {int(x["canonical_fact_id"]): x for x in json.load(open(fsn_path))}
    ev = json.load(open(relief_ev))
    relief = {int(x["canonical_fact_id"]): (x["accession"], ev[x["accession"]])
              for x in json.load(open(relief_cands))
              if ev.get(x["accession"], {}).get("outcome") == "no_quarterly_table"}  # fmt: skip
    c = conn()
    pids = sorted({int(r["period_id"]) for r in cells})
    period = {}
    for i in range(0, len(pids), 5000):
        for pid, s, e, fy, fp in c.execute(
            "select id, start_date, end_date, fiscal_year, fiscal_period from core.period where id = any(%s)",
            (pids[i : i + 5000],),
        ):
            period[pid] = (s, e, fy, fp)
    ciks = dict(c.execute("select id, cik from core.company where id = any(%s)",
                          (sorted({int(r["company_id"]) for r in cells}),)).fetchall())  # fmt: skip
    rows, stats = [], Counter()
    for r in cells:
        cf_id, cid, pid = (
            int(r["canonical_fact_id"]),
            int(r["company_id"]),
            int(r["period_id"]),
        )
        if r["action"] == "replace_with_filed_fact":
            stats["skipped_filed_fact_owned_by_pershare_filed"] += 1
            continue
        s, e, fy, fp = period[pid]
        if e < date(2014, 1, 1):
            stats["skipped_before_floor"] += 1
            continue
        grain = "FY" if fp == "FY" else "Q"
        base = {"company_id": cid, "cik": ciks[cid], "data_point_name": r["concept"], "period_grain": grain,
                "period_start": str(s), "period_end": str(e), "fiscal_year": fy, "fiscal_period": fp,
                "period_type": "duration", "fsn_end": None, "basis": "latest", "value": None, "unit": None,
                "decimals": None, "source_fact_ids": [], "accession": None, "tag": None, "members": None,
                "fsn_set": None, "fsn_stmt": None, "fsn_line": None, "derivation": None, "rule_id": RULE,
                "rule_run_id": None, "reason_code": None, "reason_text": None, "defect_class": None, "owner": None,
                "root_cause_class": None,
                "input_refs": {"retired_derived_fact_ids": [int(x) for x in r["retired_source_ids"].strip("()").replace(" ", "").split(",") if x],
                               "stored_derived_value": r["stored_value"], "family_c_digest": "de049d47"}}  # fmt: skip
        reason = r["reason_code"]
        if r["action"] == "replace_with_fsn_value":
            f = fsn[cf_id]
            row = {**base, "state": "value", "value": f["value"], "unit": "USD/shares", "accession": f["accession"],
                   "tag": f["tag"], "fsn_set": _fsn_set(f["filed"]), "fsn_stmt": None,
                   "evidence_level": "FILING-CHECKED" if f.get("face_check") else "DATA-INFERRED"}  # fmt: skip
            row["input_refs"] = {**base["input_refs"], "fsn_axis": f.get("axis") or None, "fsn_copies": f.get("copies"),
                                 "face_check": f.get("face_check")}  # fmt: skip
        elif r["action"] == "remove_with_reason" and (
            reason == "per_share_not_filed_separately" or cf_id in relief
        ):
            row = {**base, "state": "not_presented", "evidence_level": "DATA-INFERRED",
                   "reason_code": "per_share_not_filed_separately"}  # fmt: skip
            if cf_id in relief:
                acc, rec = relief[cf_id]
                row["reason_text"] = (f"10-K {acc} (filed after the Item 302(a) relief became available) prints no "
                                      "quarterly table, so no separate Q4 per-share figure exists; EPS is never derived.")  # fmt: skip
                row["accession"] = acc
                row["input_refs"] = {
                    **base["input_refs"],
                    "relief_documents": rec["documents"],
                }
                stats["relief_reclassified"] += 1
            else:
                row["reason_text"] = (
                    "The 10-K does not print a separate Q4 per-share figure; EPS is never derived."
                )
        elif r["action"] == "remove_with_reason" and reason == "per_share_not_captured":
            row = {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": reason,
                   "reason_text": "The 10-K's quarterly table prints this Q4 figure but it is not in our XBRL data yet; "
                                  "it is never derived.", "defect_class": "ingestion", "owner": "data_engineer_l2",
                   "root_cause_class": "ingestion"}  # fmt: skip
        elif (
            r["action"] == "remove_with_reason"
            and reason == "per_share_filed_copies_disagree"
        ):
            row = {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "restated_copies_disagree",
                   "reason_text": "Filed copies of this per-share value disagree (restated); not shown until resolved.",
                   "defect_class": "guard_hidden", "owner": "period_engineer", "root_cause_class": "period"}  # fmt: skip
        elif r["action"] == "review_not_retired":
            row = {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "held_pending_verifier",
                   "reason_text": f"Held for review ({r['note']}); not shown until checked against the filing.",
                   "defect_class": "finding_open", "owner": "verifier"}  # fmt: skip
        else:
            raise SystemExit(f"unexpected Family C row {cf_id}: {r['action']} {reason}")
        stats[f"{row['state']}:{row['reason_code'] or 'value'}"] += 1
        rows.append(row)
    keys = [
        (
            x["company_id"],
            x["data_point_name"],
            x["period_grain"],
            x["period_start"],
            x["period_end"],
            x["basis"],
        )
        for x in rows
    ]
    assert len(keys) == len(set(keys)), "duplicate key"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "cells.jsonl.gz"
    with gzip.open(path, "wt") as fh:
        for x in rows:
            fh.write(json.dumps(x, default=str) + "\n")
    manifest = {"family": FAMILY, "rule_id": RULE, "git_commit": commit,
                "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rows": len(rows),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "companies": len({x["company_id"] for x in rows}),
                "data_points": sorted({x["data_point_name"] for x in rows}), "period_floor": "2014-01-01",
                "new_reason_codes": NEW_CODES, "counts": dict(stats),
                "not_emitted": "204 cells with a filed 10-K/10-Q fact (pershare_filed, scrooner-28)"}  # fmt: skip
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))


def _fsn_set(filed: str) -> str:
    d = date(int(filed[:4]), int(filed[4:6]), int(filed[6:8]))
    return (
        f"{d.year}q{(d.month - 1) // 3 + 1}"
        if d < date(2025, 10, 1)
        else f"{d.year}m{d.month:02d}"
    )


if __name__ == "__main__":
    main(*sys.argv[1:7])
