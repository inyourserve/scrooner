"""Calendar-driven cell files (CELL-FORMAT-v1.1) for scrooner-26's data points, one row per expected key of the shared
calendar (data-team/46-canonical-fact-v2/expected_periods_2026-10-31.csv.gz: cohort, 2014+, FY and Q1..Q4 durations).
Read-only: one connection, chunked by 50 companies.

Outputs (each cells.jsonl.gz + manifest.json):
  interest/            interest_expense_resolved, interest_income_resolved  (loaded by scrooner-8a's loader)
  effective_tax_rate/  effective_tax_rate_reported                          (loaded)
  eps_input_for_28/    basic_eps_resolved, diluted_eps_resolved Q blanks + FSN values (INPUT file for scrooner-28)
Per key and data point:
  value      the concept's concept_mapping tags (not rejected), best priority first: authoritative, non-derived facts of
             10-K/10-Q-family filings whose period ends within 7 days of the key and spans the same length (+-10 days);
             copies of the chosen tag that agree (0.5% or one printed unit), witness = the earliest-filed copy
  restated_copies_disagree  copies disagree (founder rule: hidden)
  interest_expense only: no mapped fact -> the approved era rule's fill (value) or hold (its hold code)
  effective_tax_rate_reported: a cell Family A retires (FY rate minus 9M rate) -> derived_value_retired
  EPS: no filed fact -> Family C's blank / FSN value for the key when it has one; else Q4 of a FY ending on/after
       2021-08-09 or an Item 302(a)-relief 10-K without a quarterly table -> not_filed_separately; else not_captured
  otherwise  no_mapped_tag_filed (interest, Q1-Q3 and FY rates) / q4_only_by_subtraction (interest Q4) /
             rate_not_printed_for_period (rate, Q4)
No derived values (no FY - 9M) are emitted.
usage: emit_cells_calendar.py <calendar.csv.gz> <ie_plan_labeled.csv> <family_a_cells.csv> <pershare_derived_cells.jsonl.gz>
                              <relief_candidates.json> <relief_evidence.json> <out_root> <git_commit>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ro import conn  # noqa: E402
from emit_cells_interest import HOLD_CLASS, HOLD_TEXT, _base, same  # noqa: E402

FORMS = ["10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A"]
CUTOFF = date(2021, 8, 9)
CONCEPTS = {"interest_expense": "interest", "interest_income": "interest",
            "effective_tax_rate_reported": "effective_tax_rate", "basic_eps": "eps_input_for_28", "diluted_eps": "eps_input_for_28"}  # fmt: skip
UNIT = {"interest_expense": "USD", "interest_income": "USD", "effective_tax_rate_reported": "pure",
        "basic_eps": "USD/shares", "diluted_eps": "USD/shares"}  # fmt: skip
RULE = {"interest": "interest.filed_mapped@1", "effective_tax_rate": "tax.rate_printed_only@1",
        "eps_input_for_28": "pershare.derived_eps_retired@1"}  # fmt: skip
NEW_CODES = {
    "no_mapped_tag_filed": "none of the tags mapped to this line is filed for this period (vocabulary or not presented; not proven)",
    "q4_only_by_subtraction": "the filings give this Q4 only as FY minus 9M; derived quarters are not emitted by this family",
    "rate_not_printed_for_period": "the filer prints no effective tax rate for this quarter; a rate is never derived",
    "derived_value_retired": "the stored value was derived by subtraction, which is invalid for this concept; retired",
    "per_share_not_filed_separately": "no separate Q4 per-share figure is printed (FY on/after 2021-08-09 or Item 302(a) relief)",
    "per_share_not_captured": "the filing prints the per-share figure but it is not in our XBRL data; never derived",
    **HOLD_TEXT,
}  # fmt: skip


def months_of(s: date, e: date) -> int:
    return round((e - s).days / 30.4)


def main(
    cal_path, plan_csv, fam_a_csv, psd_path, relief_cands, relief_ev, out_root, commit
) -> None:
    cal = [
        r
        for r in csv.DictReader(gzip.open(cal_path, "rt"))
        if r["period_type"] == "duration"
    ]
    by_company: dict[int, list[dict]] = defaultdict(list)
    for r in cal:
        by_company[int(r["company_id"])].append(r)
    era = defaultdict(list)
    for r in csv.DictReader(open(plan_csv)):
        era[int(r["company_id"])].append(r)
    psd = defaultdict(dict)  # Family C rows by company -> (concept, end) -> row
    for line in gzip.open(psd_path, "rt"):
        x = json.loads(line)
        if x["data_point_name"].endswith("_resolved"):
            psd[x["company_id"]][
                (x["data_point_name"].removesuffix("_resolved"), x["period_end"])
            ] = x
    ev = json.load(open(relief_ev))
    relief_no_table: dict[int, list[date]] = defaultdict(
        list
    )  # company -> Q4 ends whose 10-K prints no quarterly table
    for x in json.load(open(relief_cands)):
        if ev.get(x["accession"], {}).get("outcome") == "no_quarterly_table":
            relief_no_table[x["company_id"]].append(date.fromisoformat(x["end"]))
    c = conn()
    c.execute("set statement_timeout = '300s'")
    fam_a = defaultdict(set)
    pids = defaultdict(list)
    for r in csv.DictReader(open(fam_a_csv)):
        if r["action"] == "remove_with_reason":
            pids[int(r["company_id"])].append(int(r["period_id"]))
    allp = sorted({p for v in pids.values() for p in v})
    pend = {}
    for i in range(0, len(allp), 5000):
        pend.update({pid: (s, e) for pid, s, e in c.execute(
            "select id, start_date, end_date from core.period where id = any(%s)", (allp[i : i + 5000],))})  # fmt: skip
    for cid, ps in pids.items():
        fam_a[cid] = {pend[p] for p in ps if p in pend}
    mapped: dict[str, dict[int, int]] = {}
    for name in CONCEPTS:
        mapped[name] = dict(c.execute(
            """select cm.concept_id, cm.priority from analytics.concept_mapping cm join analytics.canonical_concept cc
               on cc.id = cm.canonical_concept_id where cc.name = %s and cm.confidence <> 'rejected'""", (name,)).fetchall())  # fmt: skip
    tag_of = dict(c.execute("select id, tag from core.concept where id = any(%s)",
                            (sorted({k for m in mapped.values() for k in m}),)).fetchall())  # fmt: skip
    concept_of = {k: n for n, m in mapped.items() for k in m}
    out: dict[str, list] = defaultdict(list)
    stats: dict[str, Counter] = defaultdict(Counter)
    ids = sorted(by_company)
    for i in range(0, len(ids), 50):
        part = ids[i : i + 50]
        facts = defaultdict(
            lambda: defaultdict(list)
        )  # (cid, concept) -> end -> [(start, end, kid, value, dec, acc, filed, fid)]
        for fid, cid, kid, s, e, value, dec, acc, filed in c.execute(
            """select f.id, f.company_id, f.concept_id, p.start_date, p.end_date, f.value, null::int as decimals, fl.accession_number,
                      fl.filing_date
               from core.fact f join core.period p on p.id = f.period_id join core.filing fl on fl.id = f.filing_id
               where f.company_id = any(%s) and f.concept_id = any(%s) and p.period_type = 'duration'
                 and p.end_date >= '2014-01-01' and f.is_authoritative and not f.is_derived and fl.form = any(%s)""",
            (part, sorted(concept_of), FORMS),
        ):
            facts[(cid, concept_of[kid])][e].append(
                (s, e, kid, Decimal(value), dec, acc, filed, fid)
            )
        for cid in part:
            era_by_end = {}
            for r in era.get(cid, []):
                era_by_end[(date.fromisoformat(r["end"]), int(r["months"]))] = r
            for key in by_company[cid]:
                s, e = (
                    date.fromisoformat(key["period_start"]),
                    date.fromisoformat(key["period_end"]),
                )
                fp, months = key["fiscal_period"], months_of(s, e)
                for name, fam in CONCEPTS.items():
                    if fam == "eps_input_for_28" and fp == "FY":
                        continue  # FY EPS is filed: scrooner-28's own key
                    cands = [x for d, xs in facts[(cid, name)].items() if abs((d - e).days) <= 7 for x in xs
                             if abs(((x[1] - x[0]).days) - (e - s).days) <= 10]  # fmt: skip
                    base = _base(cid, key["cik"], f"{name}_resolved" if fam != "effective_tax_rate" else name,
                                 s, e, int(key["fiscal_year"]), fp, 12 if fp == "FY" else 3)  # fmt: skip
                    base["rule_id"] = RULE[fam]
                    row = _filed_row(base, cands, mapped[name], tag_of, UNIT[name])
                    if row is not None and fam == "eps_input_for_28":
                        stats[fam]["filed_fact_left_to_28"] += 1
                        continue  # a filed EPS fact: scrooner-28 emits it
                    if row is None:
                        row = _blank(
                            base,
                            name,
                            fam,
                            cid,
                            s,
                            e,
                            fp,
                            months,
                            era_by_end,
                            fam_a,
                            psd,
                            relief_no_table,
                        )
                    if row is None:
                        continue
                    out[fam].append(row)
                    stats[fam][
                        f"{row['data_point_name']}|{row['state']}|{row.get('reason_code') or 'value'}"
                    ] += 1
        print(
            f"{min(i + 50, len(ids))}/{len(ids)} "
            + " ".join(f"{k}={len(v)}" for k, v in out.items()),
            flush=True,
        )
    for fam, rows in out.items():
        keys = [
            (
                x["company_id"],
                x["data_point_name"],
                x["period_grain"],
                x["period_start"],
                x["period_end"],
            )
            for x in rows
        ]
        dup = [k for k, n in Counter(keys).items() if n > 1]
        assert not dup, f"{fam} duplicate keys: {dup[:3]}"
        d = Path(out_root) / fam
        d.mkdir(parents=True, exist_ok=True)
        path = d / "cells.jsonl.gz"
        with gzip.open(path, "wt") as fh:
            for x in rows:
                fh.write(json.dumps(x, default=str) + "\n")
        used = {x.get("reason_code") for x in rows} - {None}
        manifest = {"family": {"interest": "interest", "effective_tax_rate": "pershare_derived",
                               "eps_input_for_28": "pershare_derived (input file for pershare_filed)"}[fam],
                    "rule_id": RULE[fam], "git_commit": commit,
                    "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rows": len(rows),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "companies": len({x["company_id"] for x in rows}),
                    "data_points": sorted({x["data_point_name"] for x in rows}), "period_floor": "2014-01-01",
                    "calendar": "expected_periods_2026-10-31.csv.gz",
                    "new_reason_codes": {k: v for k, v in NEW_CODES.items() if k in used}, "counts": dict(sorted(stats[fam].items()))}  # fmt: skip
        (d / "manifest.json").write_text(json.dumps(manifest, indent=1))
        print(
            fam, json.dumps({k: manifest[k] for k in ("rows", "companies", "sha256")})
        )


def _filed_row(base, cands, prio, tag_of, unit):
    if not cands:
        return None
    best = min({x[2] for x in cands}, key=lambda k: prio[k])
    copies = sorted((x for x in cands if x[2] == best), key=lambda x: (x[6], x[7]))
    v0 = copies[0][3]
    if all(same(v0, x[3]) for x in copies):
        _s, _e, kid, value, dec, acc, _filed, fid = copies[0]
        return {**base, "state": "value", "value": str(value), "unit": unit, "decimals": dec, "source_fact_ids": [fid],
                "accession": acc, "tag": tag_of[kid], "evidence_level": "DATA-INFERRED",
                "input_refs": {"copies": len(copies), "priority": prio[kid]}}  # fmt: skip
    return {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "restated_copies_disagree",
            "reason_text": "Filed copies of this figure disagree (restated); not shown until resolved.",
            "defect_class": "guard_hidden", "owner": "period_engineer", "root_cause_class": "period",
            "input_refs": {"tag": tag_of[best], "values": sorted({str(x[3]) for x in copies}),
                           "accessions": sorted({x[5] for x in copies})}}  # fmt: skip


def _blank(
    base, name, fam, cid, s, e, fp, months, era_by_end, fam_a, psd, relief_no_table
):
    if name == "interest_expense":
        r = next(
            (
                v
                for (d, m), v in era_by_end.items()
                if abs((d - e).days) <= 7 and m == months
            ),
            None,
        )
        if r is not None:
            if r["outcome"] == "fill":
                return {**base, "state": "value", "value": r["value"], "unit": "USD", "source_fact_ids": [int(r["fact_id"])],
                        "accession": r["accession"], "tag": r["tag"], "rule_id": "interest_expense.era_tag_fill@1",
                        "evidence_level": "FILING-CHECKED" if r.get("released_from") else "DATA-INFERRED",
                        "input_refs": {"label": r["label"], "released_from": r.get("released_from") or None}}  # fmt: skip
            return {**base, "state": "defect", "rule_id": "interest_expense.era_tag_fill@1", "evidence_level": "DATA-INFERRED",
                    "reason_code": r["outcome"], "reason_text": HOLD_TEXT[r["outcome"]], "defect_class": "guard_hidden",
                    "owner": "tag_mapper", "root_cause_class": HOLD_CLASS[r["outcome"]],
                    "input_refs": {"tag": r["tag"], "accession": r["accession"], "fact_id": r["fact_id"], "label": r["label"]}}  # fmt: skip
    if fam == "interest":
        if fp == "Q4":
            return {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "q4_only_by_subtraction",
                    "reason_text": "This quarter is not filed on its own; it is not derived from the year and nine months here.",
                    "defect_class": "period", "owner": "period_engineer", "root_cause_class": "period"}  # fmt: skip
        return {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "no_mapped_tag_filed",
                "reason_text": "None of the tags mapped to this line is filed for this period.",
                "defect_class": "vocabulary", "owner": "tag_mapper", "root_cause_class": "vocabulary"}  # fmt: skip
    if fam == "effective_tax_rate":
        if any(
            abs((pe - e).days) <= 7 and abs((pe - ps).days - (e - s).days) <= 10
            for ps, pe in fam_a.get(cid, ())
        ):
            return {**base, "state": "not_presented", "evidence_level": "DATA-INFERRED", "reason_code": "derived_value_retired",
                    "reason_text": "The stored rate was the year's rate minus the nine months' rate, which is not a valid rate; "
                                   "the filer prints no rate for this period."}  # fmt: skip
        if fp == "Q4":
            return {**base, "state": "not_presented", "evidence_level": "DATA-INFERRED", "reason_code": "rate_not_printed_for_period",
                    "reason_text": "The filer prints no effective tax rate for this quarter; a rate is never derived."}  # fmt: skip
        return {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "no_mapped_tag_filed",
                "reason_text": "No effective tax rate tag is filed for this period.", "defect_class": "vocabulary",
                "owner": "tag_mapper", "root_cause_class": "vocabulary"}  # fmt: skip
    # EPS (input for 28): Family C's row for the key first
    x = next(
        (
            v
            for (n, pe), v in psd.get(cid, {}).items()
            if n == name and abs((date.fromisoformat(pe) - e).days) <= 7
        ),
        None,
    )
    if x is not None:
        return {**x, "period_start": str(s), "period_end": str(e)}
    if fp == "Q4" and (
        e >= CUTOFF or any(abs((d - e).days) <= 7 for d in relief_no_table.get(cid, ()))
    ):
        return {**base, "state": "not_presented", "evidence_level": "DATA-INFERRED", "reason_code": "per_share_not_filed_separately",
                "reason_text": "The 10-K does not print a separate Q4 per-share figure; EPS is never derived."}  # fmt: skip
    return {**base, "state": "defect", "evidence_level": "DATA-INFERRED", "reason_code": "per_share_not_captured",
            "reason_text": "The filing prints this per-share figure but it is not in our XBRL data yet; it is never derived.",
            "defect_class": "ingestion", "owner": "data_engineer_l2", "root_cause_class": "ingestion"}  # fmt: skip


if __name__ == "__main__":
    main(*sys.argv[1:9])
