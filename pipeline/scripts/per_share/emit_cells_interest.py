"""Emit the `interest` family file (CELL-FORMAT-v1) for the 1,000 cohort companies, every FY / Q cell since 2014-01-01:
interest_expense and interest_income, base and *_resolved twins. Read-only (one connection, chunked).

Per (company, period of 3 or 12 months):
  1. the concept's existing concept_mapping tags (not rejected), best priority first: authoritative, non-derived facts
     of 10-K/10-Q-family filings. Copies of the chosen tag that agree (0.5% or one printed unit) -> state value,
     witness = the earliest-filed copy; copies that disagree -> defect restated_copies_disagree (founder rule: hidden);
  2. interest_expense only, when step 1 found nothing: the era rule interest_expense.era_tag_fill@1 (approved by
     Ritwik, verified 12/12 + 14/14): its fill cells -> value; its holds -> blank with the hold code;
  3. otherwise no row (no evidence of the line: the template / not-presented families decide those keys).
No derived quarters (no FY - 9M): a Q4 that is only implied stays without a row.
usage: emit_cells_interest.py <scratch> <ie_plan_cells_labeled.csv> <out_dir> <git_commit>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ro import conn  # noqa: E402

FAMILY = "interest"
FORMS = ["10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A"]
RULE_MAPPED = "interest.filed_mapped@1"
RULE_ERA = "interest_expense.era_tag_fill@1"
HOLD_TEXT = {
    "hold_net_label": "Filed only on a net interest line (interest expense net of income); not shown.",
    "hold_no_overlap": "The 2024 taxonomy tag has no period shared with the earlier tag and no plain face line to prove it is the same total; not shown.",
    "hold_nonbank_ieo": "Only operating interest expense is tagged (a component, not the total); not shown.",
    "hold_not_on_face": "The tagged amount is not on the income statement face; not shown.",
    "hold_label_unread": "The filing's statement layout is not in our data set yet; not shown until it is read.",
    "hold_perimeter": "The 2024 taxonomy tag differs from the earlier total in a shared period; not shown.",
    "hold_sign": "The tagged amount has the wrong sign for an expense; not shown.",
}  # fmt: skip
HOLD_CLASS = {"hold_net_label": "composition", "hold_no_overlap": "evidence_pending", "hold_nonbank_ieo": "composition",
              "hold_not_on_face": "composition", "hold_label_unread": "ingestion", "hold_perimeter": "composition",
              "hold_sign": "filer_error"}  # fmt: skip


def _unit(v: Decimal) -> Decimal:
    n, u = abs(v), Decimal(1)
    while n and u < Decimal(10) ** 6 and n % (u * 10) == 0:
        u *= 10
    return u


def same(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= max(
        Decimal("0.005") * max(abs(a), abs(b)), max(_unit(a), _unit(b))
    )


def main(scratch: str, plan_csv: str, out_dir: str, commit: str) -> None:
    txt = subprocess.run(["git", "-C", "/Users/vikash/scrooner", "show",
                          "origin/main:data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv"],
                         capture_output=True, text=True, check=True).stdout  # fmt: skip
    ids = sorted(int(r["company_id"]) for r in csv.DictReader(txt.splitlines()))
    era = {
        (int(r["company_id"]), int(r["period_id"])): r
        for r in csv.DictReader(open(plan_csv))
    }
    c = conn()
    c.execute("set statement_timeout = '300s'")
    mapped: dict[str, dict[int, int]] = {}
    for name in ("interest_expense", "interest_income"):
        mapped[name] = dict(c.execute(
            """select cm.concept_id, cm.priority from analytics.concept_mapping cm
               join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
               where cc.name = %s and cm.confidence <> 'rejected'""", (name,)).fetchall())  # fmt: skip
    tag_of = dict(c.execute("select id, tag from core.concept where id = any(%s)",
                            (sorted({k for m in mapped.values() for k in m}),)).fetchall())  # fmt: skip
    ciks = dict(
        c.execute(
            "select id, cik from core.company where id = any(%s)", (ids,)
        ).fetchall()
    )
    rows, stats = [], Counter()
    for i in range(0, len(ids), 50):
        part = ids[i : i + 50]
        facts: dict[tuple[str, int, int], dict[int, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        meta: dict[tuple[int, int], tuple] = {}
        for name, cmap in mapped.items():
            for (
                fid,
                cid,
                kid,
                pid,
                s,
                e,
                fy,
                fp,
                months,
                value,
                dec,
                acc,
                filed,
            ) in c.execute(
                """select f.id, f.company_id, f.concept_id, f.period_id, p.start_date, p.end_date, p.fiscal_year,
                          p.fiscal_period, round((p.end_date - p.start_date) / 30.4)::int, f.value, null::int as decimals,
                          fl.accession_number, fl.filing_date
                   from core.fact f join core.period p on p.id = f.period_id join core.filing fl on fl.id = f.filing_id
                   where f.company_id = any(%s) and f.concept_id = any(%s) and p.period_type = 'duration'
                     and p.end_date >= '2014-01-01' and f.is_authoritative and not f.is_derived and fl.form = any(%s)""",
                (part, list(cmap), FORMS),
            ):
                if months not in (3, 12):
                    continue
                facts[(name, cid, pid)][kid].append(
                    (Decimal(value), dec, acc, filed, fid)
                )
                meta[(cid, pid)] = (s, e, fy, fp, months)
        for (cid, pid), r in era.items():
            if cid in part and (cid, pid) not in meta:
                meta[(cid, pid)] = (
                    date.fromisoformat(r["start"]),
                    date.fromisoformat(r["end"]),
                    None,
                    None,
                    int(r["months"]),
                )
        for (cid, pid), (s, e, fy, fp, months) in meta.items():
            for name in ("interest_expense", "interest_income"):
                by_tag = facts.get((name, cid, pid))
                row = None
                if by_tag:
                    best = min(by_tag, key=lambda k: mapped[name][k])
                    copies = sorted(by_tag[best], key=lambda x: (x[3], x[4]))
                    v0 = copies[0][0]
                    common = _base(cid, ciks[cid], name, s, e, fy, fp, months)
                    if all(same(v0, x[0]) for x in copies):
                        _, dec, acc, _filed, fid = copies[0]
                        row = {**common, "state": "value", "value": str(v0), "unit": "USD", "decimals": dec,
                               "source_fact_ids": [fid], "accession": acc, "tag": tag_of[best], "rule_id": RULE_MAPPED,
                               "evidence_level": "DATA-INFERRED",
                               "input_refs": {"copies": len(copies), "priority": mapped[name][best]}}  # fmt: skip
                    else:
                        row = {**common, "state": "defect", "rule_id": RULE_MAPPED, "evidence_level": "DATA-INFERRED",
                               "reason_code": "restated_copies_disagree",
                               "reason_text": "Filed copies of this figure disagree (restated); not shown until resolved.",
                               "defect_class": "guard_hidden", "owner": "period_engineer", "root_cause_class": "period",
                               "input_refs": {"tag": tag_of[best], "values": sorted({str(x[0]) for x in copies}),
                                              "accessions": sorted({x[2] for x in copies})}}  # fmt: skip
                elif name == "interest_expense" and (cid, pid) in era:
                    r = era[(cid, pid)]
                    common = _base(cid, ciks[cid], name, s, e, fy, fp, months)
                    if r["outcome"] == "fill":
                        row = {**common, "state": "value", "value": r["value"], "unit": "USD",
                               "source_fact_ids": [int(r["fact_id"])], "accession": r["accession"], "tag": r["tag"],
                               "rule_id": RULE_ERA, "evidence_level": "FILING-CHECKED" if r.get("released_from") else "DATA-INFERRED",
                               "input_refs": {"label": r["label"], "released_from": r.get("released_from") or None}}  # fmt: skip
                    else:
                        row = {**common, "state": "defect", "rule_id": RULE_ERA, "evidence_level": "DATA-INFERRED",
                               "reason_code": r["outcome"], "reason_text": HOLD_TEXT[r["outcome"]],
                               "defect_class": "guard_hidden", "owner": "tag_mapper",
                               "root_cause_class": HOLD_CLASS[r["outcome"]],
                               "input_refs": {"tag": r["tag"], "accession": r["accession"], "fact_id": r["fact_id"],
                                              "label": r["label"], "value": r["value"]}}  # fmt: skip
                if row is None:
                    continue
                for dp in (name, f"{name}_resolved"):
                    rows.append({**row, "data_point_name": dp})
                    stats[
                        f"{dp}|{row['state']}|{row.get('reason_code') or row['rule_id']}"
                    ] += 1
        print(f"{min(i + 50, len(ids))}/{len(ids)} rows {len(rows)}", flush=True)
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
    dup = [k for k, n in Counter(keys).items() if n > 1]
    assert not dup, f"duplicate keys: {dup[:5]}"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "cells.jsonl.gz"
    with gzip.open(path, "wt") as fh:
        for x in rows:
            fh.write(json.dumps(x, default=str) + "\n")
    manifest = {"family": FAMILY, "rule_id": RULE_MAPPED, "rule_ids": [RULE_MAPPED, RULE_ERA], "git_commit": commit,
                "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rows": len(rows),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "companies": len({x["company_id"] for x in rows}),
                "data_points": sorted({x["data_point_name"] for x in rows}), "period_floor": "2014-01-01",
                "new_reason_codes": {k: v for k, v in HOLD_TEXT.items()}, "counts": dict(sorted(stats.items()))}  # fmt: skip
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(
        json.dumps(
            {k: manifest[k] for k in ("rows", "companies", "sha256", "data_points")},
            indent=1,
        )
    )


def _base(cid, cik, name, s, e, fy, fp, months):
    return {"company_id": cid, "cik": cik, "data_point_name": name, "period_grain": "FY" if months == 12 else "Q",
            "period_start": str(s), "period_end": str(e), "fiscal_year": fy, "fiscal_period": fp,
            "period_type": "duration", "fsn_end": None, "basis": "latest", "value": None, "unit": None, "decimals": None,
            "source_fact_ids": [], "accession": None, "tag": None, "members": None, "fsn_set": None, "fsn_stmt": None,
            "fsn_line": None, "derivation": None, "rule_run_id": None, "reason_code": None, "reason_text": None,
            "defect_class": None, "owner": None, "root_cause_class": None, "input_refs": {}}  # fmt: skip


if __name__ == "__main__":
    main(*sys.argv[1:5])
