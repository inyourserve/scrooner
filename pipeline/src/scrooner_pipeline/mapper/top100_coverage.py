"""Top-100 coverage report: the work queue for every session (read-only on the database).

One row per (company, template data point, fiscal year FY2015..latest FY) for ranks 1-100 of
doc/data-moat/team/top1000/shards.csv. Each cell is exactly one class:

  PROVEN     served value and the latest analytics.cell_proof verdict (basis='latest') is PROVEN for that value
  REASON     no served value and an evidenced reason is stored (cell_proof NOT_PRESENTED, cell_blank_reason
             not_presented / not_in_template / evidenced_zero / undefined_by_math / history_horizon,
             or an analytics.company_tag_map not_presented / not_in_template decision covering the period)
  HELD       no served value, withheld on purpose: a defect row that is a held_/hold_ code or whose defect_class is
             guard_hidden / finding_open / filer_error (guard-held wrong value, scale error, open finding). Not a reason
             (nothing proves the line is absent), not BLANK (the work queue knows why it is empty); it is not counted in
             pct_proven_plus_reason
  DISAGREE   latest cell_proof verdict is DISAGREE
  UNCHECKED  a value is served but no PROVEN verdict covers it (no proof row, verdict UNCHECKED, or the proof was for
             another value)
  BLANK      nothing served and no evidenced reason (reason_code carries the stored defect code or the docmap status
             that is not loaded yet, for the work queue)

Template: the per-company data-point list is the FILING-CHECKED docmap (data-team/companies/reads/<T>-docmap-*.csv, latest
file); rows with status OUT are not cells. analytics.company_data_point_template (0120) is empty live and the sector
templates file is an unsigned proposal, so it cannot define cells yet. A company with no docmap has no template: it is
listed in the summary as TEMPLATE_UNAVAILABLE with zero cells, never guessed.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.proof.prove import DETECTOR_VERSION

CLASSES = ("PROVEN", "REASON", "HELD", "DISAGREE", "UNCHECKED", "BLANK")
REASON_STATES = {
    "not_presented",
    "not_in_template",
    "evidenced_zero",
    "undefined_by_math",
    "history_horizon",
}
HELD_RE = re.compile(r"^(held|hold)_")
# A defect of these classes means a value (or a candidate) exists and a guard or an open finding withholds it:
# the cell is held, not blank and not a verified reason.
HELD_DEFECT_CLASSES = {"guard_hidden", "finding_open", "filer_error"}
# Point-in-time (balance sheet / cover) data points: the FY cell is the instant at fiscal year end.
INSTANT_DPS = {
    "cash_and_equivalents",
    "accounts_receivable",
    "inventory",
    "current_assets",
    "ppe_net",
    "goodwill",
    "total_assets",
    "accounts_payable",
    "current_liabilities",
    "total_liabilities",
    "stockholders_equity",
    "shares_outstanding",
    "total_debt",
    "deposits",
    "loans_net",
}
FIRST_FY = 2015
UNMAPPED = "era_unmapped"
# docmap data point -> concept names looked up in order (resolved concept first: it is what is served).
SPECIAL_CANDIDATES = {"revenue": ["revenue_sanity_resolved", "revenue"]}

CSV_COLUMNS = [
    "rank",
    "ticker",
    "company_id",
    "data_point",
    "fiscal_year",
    "period_end",
    "class",
    "reason_code",
    "reason",
    "shown_value",
    "proof_verdict",
    "verdict",
    "accession",
    "r_page",
    "tag",
    "value_source",
    "docmap_status",
]


def candidates(dp: str) -> list[str]:
    return SPECIAL_CANDIDATES.get(dp, [f"{dp}_resolved", dp])


def classify(
    proof_verdict: str | None,
    proof_reason: str | None,
    proof_value: Decimal | None,
    served_value: Decimal | None,
    blank_state: str | None,
    blank_reason: str | None,
    tagmap_decision: str | None,
    docmap_status: str | None,
    blank_defect_class: str | None = None,
    tagmap_reason_class: str | None = None,
    in_template: bool | None = None,
) -> tuple[str, str | None]:
    """(class, reason_code). Pure. Precedence: proof verdict, served-but-unproven value, stored reason, blank."""
    if proof_verdict == "PROVEN":
        if served_value is None:
            return "BLANK", "proof_proven_but_no_served_value"
        if proof_value is None or served_value != proof_value:
            return "UNCHECKED", "proof_is_for_another_value"
        return "PROVEN", None
    if proof_verdict == "DISAGREE":
        return "DISAGREE", proof_reason
    if proof_verdict == "UNCHECKED":
        return "UNCHECKED", proof_reason or "proof_unchecked"
    if served_value is not None:
        return "UNCHECKED", "no_proof_row"
    if proof_verdict == "NOT_PRESENTED":
        return "REASON", proof_reason or "not_presented"
    # era_unmapped: the era guard found no filing-checked mapping for that year. A gap in the map, not a reason.
    if blank_reason == UNMAPPED or (
        tagmap_decision and tagmap_reason_class == UNMAPPED and not blank_state
    ):
        return "BLANK", UNMAPPED
    # not_in_template on a data point the company's current template includes is a contradiction, never a reason
    if in_template and (
        blank_state == "not_in_template" or tagmap_decision == "not_in_template"
    ):
        return "BLANK", "not_in_template_but_in_template"
    if blank_state in REASON_STATES:
        return "REASON", blank_reason or blank_state
    if blank_state == "defect" and (
        (blank_reason and HELD_RE.match(blank_reason))
        or blank_defect_class in HELD_DEFECT_CLASSES
    ):
        return "HELD", blank_reason or blank_defect_class
    if tagmap_decision in ("not_presented", "not_in_template"):
        return "REASON", f"company_tag_map:{tagmap_decision}"
    if blank_state == "defect":
        return "BLANK", blank_reason or "defect"
    if docmap_status and docmap_status != "mapped":
        return "BLANK", f"docmap_{docmap_status.replace(' ', '_')}_not_loaded"
    return "BLANK", "no_value_no_reason"


@dataclass(frozen=True)
class Company:
    rank: int
    ticker: str
    company_id: int
    excluded: str


def load_top(path: Path, n: int = 100) -> list[Company]:
    out = []
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["rank"].isdigit() and int(r["rank"]) <= n:
                out.append(
                    Company(
                        int(r["rank"]),
                        r["ticker"],
                        int(r["company_id"]),
                        (r.get("excluded") or "").strip(),
                    )
                )
    return sorted(out, key=lambda c: c.rank)


def load_docmap(reads_dir: Path, ticker: str) -> dict[str, dict[str, str]]:
    files = sorted(reads_dir.glob(f"{ticker}-docmap-*.csv"))
    if not files:
        return {}
    with files[-1].open(newline="") as fh:
        return {r["data_point"]: r for r in csv.DictReader(fh)}


def _fy_periods(
    conn: Any, ids: list[int], today: date
) -> dict[tuple[int, int, str], tuple[date, date]]:
    """(company, fiscal_year, 'duration'|'instant') -> (start, end) of the FY period ending last (duration >= 300 days)."""
    cur = conn.execute(
        """select company_id, fiscal_year, period_type, start_date, end_date from core.period
           where company_id = any(%s) and fiscal_period = 'FY' and fiscal_year >= %s and end_date <= %s""",
        (ids, FIRST_FY, today),
    )
    best: dict[tuple[int, int, str], tuple[date, date]] = {}
    for cid, fy, ptype, s, e in cur.fetchall():
        if ptype == "duration" and (e - s).days < 300:
            continue
        key = (cid, fy, ptype)
        if key not in best or e > best[key][1]:
            best[key] = (s, e)
    return best


def load_current_proofs(
    conn: Any, ids: list[int], names: list[str]
) -> dict[tuple[int, str, date, date], tuple]:
    """The verdict of each cell key: its newest analytics.cell_proof row written by the CURRENT detector version.
    A row of an older detector is history, never the verdict (a held cell is not re-proved, so a pre-R13
    restated_copies_disagree row outlived its rule for 48 MSFT cells)."""
    proofs: dict[tuple[int, str, date, date], tuple] = {}
    for row in conn.execute(
        """select distinct on (company_id, data_point_name, period_start, period_end)
                  company_id, data_point_name, period_start, period_end, verdict, reason_code, reason_text,
                  shown_value, shown_tag, shown_accession, position_source, face_report
           from analytics.cell_proof
           where company_id = any(%s) and data_point_name = any(%s) and basis = 'latest'
             and detector_version = %s
             and period_grain in ('FY', 'I') and period_end >= %s
           order by company_id, data_point_name, period_start, period_end, proved_at desc, id desc""",
        (ids, names, DETECTOR_VERSION, date(FIRST_FY - 1, 1, 1)),
    ).fetchall():
        proofs[(row[0], row[1], row[2], row[3])] = row[4:]
    return proofs


def _statement_pages(
    conn: Any, ids: list[int]
) -> dict[tuple[int, date, str], tuple[str, str]]:
    """(company, fiscal year end, statement code) -> (accession, 'R<n>.htm') of that year's own 10-K: the report that
    carries most of the statement's lines (fsn.line.stmt) in the filing whose period is the year end."""
    best: dict[tuple[int, date, str], tuple[int, str, str]] = {}
    for cid, period, acc, stmt, report, n in conn.execute(
        """select f.company_id, f.period, f.accession, l.stmt, l.report, count(*)
           from fsn.filing f join fsn.line l on l.filing_id = f.id
           where f.company_id = any(%s) and f.form in ('10-K', '10-K/A', '10-KT') and f.period is not null
             and l.stmt in ('IS', 'BS', 'CF', 'CI', 'EQ')
           group by f.company_id, f.period, f.accession, l.stmt, l.report""",
        (ids,),
    ).fetchall():
        k = (cid, period, stmt)
        if k not in best or (n, acc) > (best[k][0], best[k][1]):
            best[k] = (n, acc, f"R{report}.htm")
    return {k: (v[1], v[2]) for k, v in best.items()}


def build_rows(
    conn: Any, companies: list[Company], reads_dir: Path, today: date
) -> tuple[list[dict[str, Any]], dict[int, str]]:
    templates = {c.company_id: load_docmap(reads_dir, c.ticker) for c in companies}
    live = [c for c in companies if templates[c.company_id]]
    ids = [c.company_id for c in live]
    periods = _fy_periods(conn, ids, today)
    names = sorted(
        {n for c in live for dp in templates[c.company_id] for n in candidates(dp)}
    )
    concept_id = {
        n: i
        for i, n in conn.execute(
            "select id, name from analytics.canonical_concept where name = any(%s)",
            (names,),
        ).fetchall()
    }
    served: dict[tuple[int, str, date, date], Decimal] = {}
    for cid, name, s, e, v in conn.execute(
        """select f.company_id, c.name, p.start_date, p.end_date, f.value
           from analytics.canonical_fact f join core.period p on p.id = f.period_id
           join analytics.canonical_concept c on c.id = f.canonical_concept_id
           where f.company_id = any(%s) and c.name = any(%s) and p.fiscal_period = 'FY' and p.fiscal_year >= %s""",
        (ids, names, FIRST_FY),
    ).fetchall():
        served[(cid, name, s, e)] = v
    proofs = load_current_proofs(conn, ids, names)
    blanks: dict[tuple[int, str, date, date], tuple] = {}
    for row in conn.execute(
        """select distinct on (company_id, data_point_name, period_start, period_end)
                  company_id, data_point_name, period_start, period_end, state, reason_code, reason_text,
                  defect_class
           from analytics.cell_blank_reason
           where company_id = any(%s) and data_point_name = any(%s) and basis = 'latest'
             and period_grain in ('FY', 'I') and period_end >= %s
           order by company_id, data_point_name, period_start, period_end, created_at desc, id desc""",
        (ids, names, date(FIRST_FY - 1, 1, 1)),
    ).fetchall():
        blanks[(row[0], row[1], row[2], row[3])] = row[4:]
    tagmap: dict[tuple[int, str], list[tuple]] = defaultdict(list)
    for cid, name, dec, ef, et, reason, rclass in conn.execute(
        """select m.company_id, c.name, m.decision, m.era_from, m.era_to, m.reason, m.reason_class
           from analytics.company_tag_map m join analytics.canonical_concept c on c.id = m.canonical_concept_id
           where m.company_id = any(%s) and m.decision in ('not_presented', 'not_in_template')""",
        (ids,),
    ).fetchall():
        tagmap[(cid, name)].append((dec, ef, et, reason, rclass))

    # the company's CURRENT sector template (latest effective_from <= today): data point -> in_template
    in_tpl: dict[tuple[int, str], bool] = {}
    for cid, dp, inn in conn.execute(
        """select t.company_id, t.data_point, t.in_template from analytics.company_data_point_template t
           where t.company_id = any(%s) and t.effective_from = (
             select max(effective_from) from analytics.company_data_point_template x
             where x.company_id = t.company_id and x.effective_from <= %s)""",
        (ids, today),
    ).fetchall():
        in_tpl[(cid, dp)] = bool(inn)

    stmt_pages = _statement_pages(conn, ids)

    rows: list[dict[str, Any]] = []
    for c in live:
        years = sorted({fy for (cid, fy, _t) in periods if cid == c.company_id})
        if not years:
            continue
        for dp, dm in sorted(templates[c.company_id].items()):
            if dm["status"] == "OUT":
                continue
            ptype = "instant" if dp in INSTANT_DPS else "duration"
            for fy in years:
                per = periods.get((c.company_id, fy, ptype))
                if per is None:
                    continue
                s, e = per
                cand = candidates(dp)
                svalue = sname = None
                for n in cand:
                    if (c.company_id, n, s, e) in served:
                        svalue, sname = served[(c.company_id, n, s, e)], n
                        break
                prow = brow = pname = None
                for n in ([sname] if sname else []) + cand:
                    if prow is None and (c.company_id, n, s, e) in proofs:
                        prow, pname = proofs[(c.company_id, n, s, e)], n
                    if brow is None and (c.company_id, n, s, e) in blanks:
                        brow = blanks[(c.company_id, n, s, e)]
                tm = None
                for n in cand:
                    for dec, ef, et, why, rcl in tagmap.get((c.company_id, n), []):
                        if (ef is None or ef <= e) and (et is None or et >= e):
                            tm = (dec, why, rcl)
                verdict, preason, ptext, pval, ptag, pacc, psrc, pface = (
                    prow if prow else (None,) * 8
                )
                cls, code = classify(
                    verdict,
                    preason,
                    pval,
                    svalue,
                    brow[0] if brow else None,
                    brow[1] if brow else None,
                    tm[0] if tm else None,
                    dm["status"],
                    brow[3] if brow else None,
                    tm[2] if tm else None,
                    in_tpl.get((c.company_id, dp)),
                )
                # The docmap's r_page is the page in the read (latest) 10-K only: wrong for every earlier year.
                # The page comes from the proof (face_report) or from the fsn report of THAT year's own 10-K.
                fsn_acc, fsn_page = stmt_pages.get(
                    (c.company_id, e, dm.get("stmt", "")), ("", "")
                )
                reason_text = (
                    ptext or (brow[2] if brow else None) or (tm[1] if tm else None)
                )
                shown = (
                    svalue
                    if svalue is not None
                    else (pval if cls == "DISAGREE" else None)
                )
                rows.append(
                    {
                        "rank": c.rank,
                        "ticker": c.ticker,
                        "company_id": c.company_id,
                        "data_point": dp,
                        "fiscal_year": fy,
                        "period_end": e.isoformat(),
                        "class": cls,
                        "reason_code": code or "",
                        "reason": reason_text or "",
                        "shown_value": "" if shown is None else format(shown, "f"),
                        "proof_verdict": verdict or "",
                        "verdict": verdict or "",
                        "accession": pacc or fsn_acc,
                        "r_page": pface or fsn_page,
                        "tag": ptag or "",
                        "value_source": psrc
                        or ("canonical_fact" if svalue is not None else ""),
                        "docmap_status": dm["status"],
                    }
                )
    note = {
        c.company_id: (
            "TEMPLATE_UNAVAILABLE"
            + (f" (excluded: {c.excluded})" if c.excluded else " (no docmap)")
        )
        for c in companies
        if not templates[c.company_id]
    }
    return rows, note


def summarize(
    rows: list[dict[str, Any]],
    companies: list[Company],
    notes: dict[int, str],
    as_of: str,
) -> list[dict[str, Any]]:
    by: dict[int, dict[str, int]] = defaultdict(lambda: dict.fromkeys(CLASSES, 0))
    for r in rows:
        by[r["company_id"]][r["class"]] += 1
    out = []
    for c in companies:
        t = by.get(c.company_id, dict.fromkeys(CLASSES, 0))
        total = sum(t.values())
        out.append(
            {
                "rank": c.rank,
                "ticker": c.ticker,
                "company_id": c.company_id,
                "cells": total,
                **t,
                "pct_proven_plus_reason": f"{100 * (t['PROVEN'] + t['REASON']) / total:.1f}"
                if total
                else "",
                "note": notes.get(c.company_id, ""),
                "as_of": as_of,
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def main(out_dir: Path, shards: Path, reads_dir: Path, n: int = 100) -> int:
    from scrooner_pipeline.db.connection import get_connection

    companies = load_top(shards, n)
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute("set transaction read only")
        conn.execute("set statement_timeout = '10min'")
        rows, notes = build_rows(conn, companies, reads_dir, now.date())
    as_of = now.strftime("%Y-%m-%dT%H:%MZ")
    summary = summarize(rows, companies, notes, as_of)
    write_csv(out_dir / "top100-coverage.csv", rows, CSV_COLUMNS)
    scols = [
        "rank",
        "ticker",
        "company_id",
        "cells",
        *CLASSES,
        "pct_proven_plus_reason",
        "note",
        "as_of",
    ]
    write_csv(out_dir / "top100-coverage-summary.csv", summary, scols)
    tot = {k: sum(r[k] for r in summary) for k in CLASSES}
    print(f"top100 coverage as of {as_of}: {len(rows)} cells {tot}")
    return 0
