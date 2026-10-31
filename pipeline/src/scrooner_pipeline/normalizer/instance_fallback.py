"""B9: a periodic filing the companyfacts API never carried (rule ingest.instance_fallback@1, flag OFF).

THE DEFECT (sized 2026-10-31): 130 cohort 10-K/10-Q filings since 2015 at 80
companies have a core.filing row and ZERO core.fact rows although a
companyfacts payload fetched after the filing exists: SEC's companyfacts API
simply lacks the accession (Visa 0001403161-26-000104, period 2026-06-30, is
still absent live). 119 of them were filed on or before 2026-09-30, inside the
FSN periods held in the fsn-notes bucket; 11 October-2026 filings wait for the
2026m10 set or need the filing's own instance.

THE RULE
  source  (a) the FSN set of the filing's month/quarter (proof/fsn.py: num rows
          with dimn = 0, iprx = 0, no co-registrant, standard taxonomies) --
          zero SEC requests; (b) the filing's own inline-XBRL instance (not in
          this version: scripts/slot_records/instance_reader.py is the reader,
          4 req/s, to be wired once (a) is proven).
  columns only the filing's CURRENT columns (FSN ddate = the period of report):
          the instant at the period end; the year-to-date duration from the
          fiscal-year start; the 3-month duration from the prior quarter end
          for income-statement lines of a 10-Q (a 10-K prints annual columns
          only; a 10-Q cash-flow statement prints year-to-date only, so a
          3-month cash-flow value is a note and is skipped). Prior-year
          comparatives already exist from earlier filings.
  periods created when missing (the periods stage never saw this filing):
          fiscal_year/fiscal_period from the FSN sub row for the quarter and
          the instant, none for the year-to-date span (the existing convention).
  lineage one raw.sec_companyfacts row per filing (accepted by the chief of staff
          2026-10-31: the FSN slice lives in the companyfacts raw table because
          the source is explicit in source_url and core.fact's lineage FK points
          there; nothing else in raw is a companyfacts payload) with source_url
          fsn://fsn-notes/<period>/<period>_num.tsv.zst#<accession> and the
          sha256 of the payload built from it; every fact's raw_object_id
          points at it, so facts from this path are always identifiable.
  write   through normalizer/facts.py::normalize_payload, the one write path
          (same concept/unit/period lookups, same upsert).
  rollback delete the facts whose raw_object_id is this run's lineage row and
          the periods this run created (when no other fact uses them); the raw
          row stays. Before-image: the created ids, per filing.
Modes: off/dry_run -> plan and report; on -> apply.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.rule_flags import ON, RULE_INSTANCE_FALLBACK, rule_mode
from scrooner_pipeline.common.history_floor import HISTORY_FLOOR
from scrooner_pipeline.normalizer.facts import normalize_payload
from scrooner_pipeline.proof.fsn import (
    FilingStructure,
    fsn_ddate,
    load_quarter,
    quarter_of,
)

logger = structlog.get_logger()

RULE_ID = RULE_INSTANCE_FALLBACK
PERIODIC = ("10-K", "10-K/A", "10-Q", "10-Q/A")
MIN_AGE_DAYS = 14
PER_SHARE_RE = re.compile(r"Per(Basic|Diluted|BasicAndDiluted)?Share|PerUnit")
BUCKET = "fsn-notes"


@dataclass(frozen=True)
class MissingFiling:
    company_id: int
    cik: str
    accession: str
    form: str
    filing_date: date
    period_of_report: date
    fy_start: date | None
    prev_quarter_end: date | None


@dataclass
class FilingPlan:
    filing: MissingFiling
    fsn_set: str
    structure_found: bool
    entries: list[dict[str, Any]] = field(default_factory=list)
    periods_to_create: list[tuple[date, date, str, int | None, str | None]] = field(
        default_factory=list
    )
    skipped: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def by_statement(self) -> dict[str, int]:
        c: dict[str, int] = defaultdict(int)
        for e in self.entries:
            c[e["stmt"]] += 1
        return dict(c)


def find_missing(
    conn: psycopg.Connection,
    company_ids: list[int],
    *,
    min_age_days: int = MIN_AGE_DAYS,
) -> list[MissingFiling]:
    """Periodic filings with no facts, older than min_age_days, whose company has
    a companyfacts payload fetched after the filing (so the API had its chance)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.company_id, co.cik, f.accession_number, f.form, f.filing_date, f.period_of_report
            from core.filing f
            join core.company co on co.id = f.company_id
            where f.company_id = any(%s) and f.form = any(%s) and f.period_of_report is not null
              and f.filing_date <= current_date - %s and f.filing_date >= %s
              and not exists (select 1 from core.fact x where x.filing_id = f.id)
              and (select max(r.fetched_at)::date from raw.sec_companyfacts r where r.cik = co.cik) > f.filing_date
            order by f.company_id, f.filing_date
            """,
            (company_ids, list(PERIODIC), min_age_days, HISTORY_FLOOR),
        )
        rows = cur.fetchall()
        out = []
        for company_id, cik, acc, form, fdate, por in rows:
            cur.execute(
                "select max(period_of_report) from core.filing where company_id = %s and form in ('10-K', '10-K/A') and period_of_report < %s",
                (company_id, por),
            )
            prev_fy_end = cur.fetchone()[0]
            cur.execute(
                "select max(period_of_report) from core.filing where company_id = %s and form = any(%s) and period_of_report < %s",
                (company_id, list(PERIODIC), por),
            )
            prev_q_end = cur.fetchone()[0]
            fy_start = (
                prev_fy_end + timedelta(days=1)
                if prev_fy_end and form.startswith("10-Q")
                else (prev_fy_end + timedelta(days=1) if prev_fy_end else None)
            )
            out.append(
                MissingFiling(
                    company_id, cik, acc, form, fdate, por, fy_start, prev_q_end
                )
            )
    return out


def payload_from_structure(filing: MissingFiling, st: FilingStructure) -> FilingPlan:
    """Companyfacts-shaped payload of the filing's CURRENT columns from its FSN rows."""
    plan = FilingPlan(filing, quarter_of(filing.filing_date), True)
    por = filing.period_of_report
    cur_dd = fsn_ddate(por)
    stmt_of: dict[str, str] = {}
    for line in st.pre:
        stmt_of.setdefault(line.tag, line.stmt)
    facts: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    is_10k = filing.form.startswith("10-K")
    for (tag, dd, qtrs), vals in st.num.items():
        if dd != cur_dd:
            plan.skipped["comparative_column"] += len(vals)
            continue
        for nv in vals:
            if not nv.version.startswith(("us-gaap/", "dei/", "srt/")):
                plan.skipped["custom_taxonomy"] += 1
                continue
            stmt = stmt_of.get(tag)
            if qtrs == 0:
                start, end, ptype, fp = por, por, "instant", None
            elif is_10k:
                if qtrs != 4 or filing.fy_start is None:
                    plan.skipped["10k_non_annual_duration"] += 1
                    continue
                start, end, ptype, fp = filing.fy_start, por, "duration", "FY"
            else:
                if qtrs == 1:
                    if stmt == "CF":
                        plan.skipped["cf_three_month_note"] += 1
                        continue
                    if filing.prev_quarter_end is None:
                        plan.skipped["no_prior_quarter_end"] += 1
                        continue
                    start, end, ptype, fp = (
                        filing.prev_quarter_end + timedelta(days=1),
                        por,
                        "duration",
                        "Q",
                    )
                else:
                    if filing.fy_start is None:
                        plan.skipped["no_fiscal_year_start"] += 1
                        continue
                    if abs((por - filing.fy_start).days - qtrs * 91) > 25:
                        plan.skipped["ytd_length_mismatch"] += 1
                        continue
                    start, end, ptype, fp = filing.fy_start, por, "duration", None
            taxonomy = nv.version.split("/", 1)[0]
            uom = nv.uom
            if PER_SHARE_RE.search(tag) and uom.upper() == "USD":
                uom = "USD/shares"
            entry = {
                "start": None if ptype == "instant" else start.isoformat(),
                "end": end.isoformat(),
                "val": nv.value,
                "accn": filing.accession,
                "fy": st.fy or (st.period.year if st.period else por.year),
                "fp": (st.fp if (ptype == "instant" or fp == "Q") else fp) or "FY",
                "form": filing.form,
                "filed": filing.filing_date.isoformat(),
            }
            facts[taxonomy][tag][uom].append(entry)
            plan.entries.append(
                {
                    "taxonomy": taxonomy,
                    "tag": tag,
                    "uom": uom,
                    "stmt": stmt or "note",
                    "start": start,
                    "end": end,
                    "ptype": ptype,
                    "value": nv.value,
                }
            )
            sub_fy = st.fy or (st.period.year if st.period else por.year)
            sub_fp = st.fp or ("FY" if is_10k else None)
            if ptype == "instant" or fp == "Q":
                label = (sub_fy, sub_fp)
            elif fp == "FY":
                label = (sub_fy, "FY")
            else:
                label = (
                    sub_fy,
                    None,
                )  # year-to-date span: no fiscal_period (existing convention)
            plan.periods_to_create.append((start, end, ptype, label[0], label[1]))
    plan.periods_to_create = sorted(set(plan.periods_to_create))
    plan.payload = {
        "cik": filing.cik,
        "facts": {
            t: {g: {"units": dict(u)} for g, u in tags.items()}
            for t, tags in facts.items()
        },
    }
    return plan


def plan_filings(filings: list[MissingFiling], fsn_root: Path) -> list[FilingPlan]:
    by_q: dict[str, set[str]] = defaultdict(set)
    for f in filings:
        by_q[quarter_of(f.filing_date)].add(f.accession)
    structures: dict[str, FilingStructure] = {}
    missing_sets: set[str] = set()
    for q, accs in sorted(by_q.items()):
        try:
            structures.update(load_quarter(fsn_root, q, accs))
        except FileNotFoundError:
            missing_sets.add(q)
    plans = []
    for f in filings:
        st = structures.get(f.accession)
        if st is None:
            p = FilingPlan(f, quarter_of(f.filing_date), False)
            p.skipped[
                "fsn_set_missing"
                if quarter_of(f.filing_date) in missing_sets
                else "accession_not_in_fsn_set"
            ] += 1
            plans.append(p)
            continue
        plans.append(payload_from_structure(f, st))
    return plans


def _merge_counts(dicts) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for d in dicts:
        for k, v in d.items():
            out[k] += v
    return dict(out)


def _json_default(o: Any) -> Any:
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


def apply_plan(
    conn: psycopg.Connection, plan: FilingPlan, backup_dir: Path
) -> dict[str, Any]:
    if rule_mode(RULE_ID) != ON:
        raise RuntimeError(f"{RULE_ID} is not ON; refusing to write")
    f = plan.filing
    payload_json = json.dumps(plan.payload, default=_json_default, sort_keys=True)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()
    created_periods: list[int] = []
    with conn.transaction():
        with conn.cursor() as cur:
            for start, end, ptype, fy, fp in plan.periods_to_create:
                cur.execute(
                    """
                    insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                    values (%s, %s, %s, %s, %s, %s)
                    on conflict (company_id, start_date, end_date, period_type) do nothing
                    returning id
                    """,
                    (f.company_id, start, end, ptype, fy, fp),
                )
                row = cur.fetchone()
                if row:
                    created_periods.append(row[0])
            cur.execute(
                """
                insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status, fetched_at)
                values (%s, %s, %s, %s, 200, now()) returning id
                """,
                (
                    f.cik,
                    f"fsn://{BUCKET}/{plan.fsn_set}/{plan.fsn_set}_num.tsv.zst#{f.accession}",
                    sha,
                    f"{BUCKET}/{plan.fsn_set}/{plan.fsn_set}_num.tsv.zst",
                ),
            )
            raw_id = cur.fetchone()[0]
        stats = normalize_payload(conn, f.company_id, f.cik, plan.payload, raw_id)
    backup_dir.mkdir(parents=True, exist_ok=True)
    image = {
        "accession": f.accession,
        "company_id": f.company_id,
        "raw_object_id": raw_id,
        "created_period_ids": created_periods,
        "facts_written": stats.get("written"),
        "sha256": sha,
        "taken_at": datetime.now().isoformat(timespec="seconds"),
    }
    (backup_dir / f"{f.accession}.json").write_text(json.dumps(image, indent=2))
    return {**stats, "raw_object_id": raw_id, "periods_created": len(created_periods)}


def rollback_filing(conn: psycopg.Connection, image_path: Path) -> dict[str, int]:
    img = json.loads(image_path.read_text())
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(
                "delete from core.fact where raw_object_id = %s",
                (img["raw_object_id"],),
            )
            facts = cur.rowcount
            periods = 0
            for pid in img["created_period_ids"]:
                cur.execute(
                    "delete from core.period where id = %s and not exists (select 1 from core.fact where period_id = %s)",
                    (pid, pid),
                )
                periods += cur.rowcount
    return {"facts_deleted": facts, "periods_deleted": periods}


def run(
    conn: psycopg.Connection,
    ciks: set[str],
    *,
    fsn_root: Path,
    backup_dir: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, Any]:
    mode = rule_mode(RULE_ID)
    with conn.cursor() as cur:
        cur.execute("select id from core.company where cik = any(%s)", (sorted(ciks),))
        ids = [r[0] for r in cur.fetchall()]
    filings = find_missing(conn, ids)
    plans = plan_filings(filings, fsn_root)
    totals: dict[str, Any] = {
        "mode": mode,
        "companies": len(ids),
        "missing_filings": len(filings),
        "with_fsn_structure": sum(1 for p in plans if p.structure_found),
        "facts_planned": sum(len(p.entries) for p in plans),
        "periods_to_create": sum(len(p.periods_to_create) for p in plans),
        "skipped": _merge_counts(p.skipped for p in plans),
        "applied": 0,
        "facts_written": 0,
    }
    if mode == ON and backup_dir is None:
        raise ValueError("backup_dir is required when the rule is ON")
    report = report_path.open("a") if report_path else None
    try:
        for p in plans:
            rec = {
                "cik": p.filing.cik,
                "accession": p.filing.accession,
                "form": p.filing.form,
                "period_of_report": p.filing.period_of_report,
                "fsn_set": p.fsn_set,
                "structure_found": p.structure_found,
                "facts": len(p.entries),
                "by_statement": p.by_statement,
                "periods_to_create": p.periods_to_create,
                "skipped": dict(p.skipped),
            }
            if mode == ON and p.structure_found and p.entries:
                try:
                    out = apply_plan(conn, p, backup_dir)  # type: ignore[arg-type]
                    rec["applied"] = out
                    totals["applied"] += 1
                    totals["facts_written"] += out.get("written", 0)
                except Exception as exc:  # noqa: BLE001
                    rec["error"] = repr(exc)[:200]
                    conn.rollback()
            if report is not None:
                report.write(json.dumps(rec, default=_json_default) + "\n")
    finally:
        if report is not None:
            report.close()
    logger.info(
        "instance_fallback.done", **{k: v for k, v in totals.items() if k != "skipped"}
    )
    return totals


def rollback_run_dir(conn: psycopg.Connection, backup_dir: Path) -> dict[str, int]:
    out = {"filings": 0, "facts_deleted": 0, "periods_deleted": 0}
    for path in sorted(backup_dir.glob("*.json")):
        r = rollback_filing(conn, path)
        out["filings"] += 1
        out["facts_deleted"] += r["facts_deleted"]
        out["periods_deleted"] += r["periods_deleted"]
    return out
