"""Stage 2b -- Period normalization (doc 09). Resolves every distinct
(start, end) span referenced anywhere in a company's companyfacts payload
into core.period rows: objective calendar dates plus a best-effort
fiscal_year/fiscal_period label. Read-only against `raw`, writes only
`core` -- no new SEC network calls.

Period IDENTITY is (company_id, start_date, end_date, period_type) -- the
objective calendar span -- never a fact's own reported fy/fp. Verified live
2026-08-15 against AAPL's raw companyfacts: the same real period is tagged
with DIFFERENT fy/fp depending on which filing mentions it (an original
disclosure vs. a later comparative), so fy/fp describes the REPORTING
FILING, not the period. See doc/learnings/normalizer-day-02-periods.md.

fiscal_year/fiscal_period are instead DERIVED here from each company's own
observed full-year period end dates (its real historical fiscal-year-ends,
found empirically in its own data -- no guessing from the nominal MMDD in
submissions' fiscalYearEnd, which wobbles by up to ~a week against actual
FYE dates) plus calendar-distance math for quarter numbering. They are
best-effort DISPLAY labels only -- nullable, and deliberately excluded from
the table's identity. Every downstream stage must key off
start_date/end_date/period_type, never these two.
"""

import json
from datetime import date, datetime

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix
from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()

# Verified live 2026-08-15 against AAPL's full companyfacts history (2007-2025):
# duration lengths cluster cleanly into four bands with empty gaps between
# them (quarter 75-100d, half-year 170-200d, three-quarter 260-290d,
# full-year 350-380d) -- no fuzzy boundary cases observed. Half-year/
# three-quarter (YTD cumulative, common on cash-flow-statement lines) are
# deliberately left unclassified below, not force-labeled into a quarter.
FULL_YEAR_MIN_DAYS, FULL_YEAR_MAX_DAYS = 350, 380
QUARTER_MIN_DAYS, QUARTER_MAX_DAYS = 75, 100
NOMINAL_QUARTER_DAYS = 91.25


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_fiscal_year_end(fiscal_year_end: str | None) -> tuple[int, int] | None:
    if not fiscal_year_end or len(fiscal_year_end) != 4:
        return None
    return int(fiscal_year_end[:2]), int(fiscal_year_end[2:])


def _load_json(storage: SupabaseStorageClient, storage_path: str) -> dict:
    raw_bytes = storage.download(strip_bucket_prefix(storage_path))
    return json.loads(raw_bytes)


def _latest_companyfacts_object(conn: psycopg.Connection, cik: str) -> tuple[int, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id, storage_path from raw.sec_companyfacts where cik = %s order by fetched_at desc limit 1",
            (cik,),
        )
        return cur.fetchone()


def _get_company(conn: psycopg.Connection, cik: str) -> tuple[int, str | None] | None:
    with conn.cursor() as cur:
        cur.execute("select id, fiscal_year_end from core.company where cik = %s", (cik,))
        return cur.fetchone()


def extract_distinct_periods(payload: dict) -> set[tuple[str, str | None]]:
    """(end, start_or_None) for every distinct period referenced anywhere in
    a companyfacts payload, across every taxonomy/concept/unit -- the raw
    material this stage resolves, independent of which specific facts will
    eventually reference them (Stage 2d's job, not this one's)."""
    periods: set[tuple[str, str | None]] = set()
    for _taxonomy, concepts in payload.get("facts", {}).items():
        for _concept, cdata in concepts.items():
            for _unit, entries in cdata.get("units", {}).items():
                for e in entries:
                    end = e.get("end")
                    if not end:
                        continue
                    periods.add((end, e.get("start")))
    return periods


def build_fye_anchors(periods: set[tuple[str, str | None]]) -> list[date]:
    """Every distinct end_date belonging to a full-year-length duration --
    empirically this company's OWN real fiscal-year-end dates. No MMDD
    guessing: verified live that AAPL's actual FYE wobbles day-to-day
    against its nominal '0926' (2016-09-24, 2017-09-30, 2018-09-29, ...),
    so only observed data is trustworthy here. Sorted ascending."""
    anchors = set()
    for end, start in periods:
        if start is None:
            continue
        if FULL_YEAR_MIN_DAYS <= (_parse_date(end) - _parse_date(start)).days <= FULL_YEAR_MAX_DAYS:
            anchors.add(_parse_date(end))
    return sorted(anchors)


def _bracket_fye(
    target: date, anchors: list[date], nominal_month_day: tuple[int, int] | None
) -> tuple[date | None, date | None]:
    """(next_fye_on_or_after_target, prior_fye_before_target). Extrapolates
    past the observed anchor range (year-by-year, using the nearest known
    anchor or the nominal month/day as a fallback) when target falls
    outside what's actually been observed -- e.g. the most recent quarter
    of a company's history, filed before its next fiscal year-end exists to
    observe."""
    next_fye = next((a for a in anchors if a >= target), None)
    prior_fye = next((a for a in reversed(anchors) if a < target), None)

    if next_fye is None:
        base = anchors[-1] if anchors else (date(target.year - 1, *nominal_month_day) if nominal_month_day else None)
        if base is not None:
            candidate = base
            while candidate < target:
                candidate = date(candidate.year + 1, candidate.month, candidate.day)
            next_fye = candidate
    if prior_fye is None:
        base = anchors[0] if anchors else next_fye
        if base is not None:
            candidate = base
            while candidate >= target:
                candidate = date(candidate.year - 1, candidate.month, candidate.day)
            prior_fye = candidate
    return next_fye, prior_fye


def classify_period(
    end: str, start: str | None, anchors: list[date], nominal_month_day: tuple[int, int] | None
) -> dict:
    end_date = _parse_date(end)
    if start is None:
        period_type = "instant"
        start_date = end_date  # schema: start=end for instants (keeps the unique constraint NULL-safe)
        duration_days = 0
    else:
        period_type = "duration"
        start_date = _parse_date(start)
        duration_days = (end_date - start_date).days

    next_fye, prior_fye = _bracket_fye(end_date, anchors, nominal_month_day)
    fiscal_year = next_fye.year if next_fye else None
    fiscal_period = None

    if period_type == "duration":
        if FULL_YEAR_MIN_DAYS <= duration_days <= FULL_YEAR_MAX_DAYS:
            fiscal_period = "FY"
        elif QUARTER_MIN_DAYS <= duration_days <= QUARTER_MAX_DAYS and prior_fye is not None:
            idx = round((end_date - prior_fye).days / NOMINAL_QUARTER_DAYS)
            fiscal_period = f"Q{min(max(idx, 1), 4)}"
        # else: non-standard duration (half-year/three-quarter YTD spans,
        # irregular stub periods) -- left unclassified rather than mislabeled.
    elif prior_fye is not None:
        idx = round((end_date - prior_fye).days / NOMINAL_QUARTER_DAYS)
        if idx >= 4:
            fiscal_period = "FY" if end_date == next_fye else "Q4"
        elif idx >= 1:
            fiscal_period = f"Q{idx}"

    return {
        "start_date": start_date,
        "end_date": end_date,
        "period_type": period_type,
        "fiscal_year": fiscal_year,
        "fiscal_period": fiscal_period,
    }


def upsert_periods(conn: psycopg.Connection, company_id: int, rows: list[dict]) -> int:
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
            values (%(company_id)s, %(start_date)s, %(end_date)s, %(period_type)s, %(fiscal_year)s, %(fiscal_period)s)
            on conflict (company_id, start_date, end_date, period_type) do update
                set fiscal_year    = excluded.fiscal_year,
                    fiscal_period  = excluded.fiscal_period
            """,
            [{"company_id": company_id, **row} for row in rows],
        )
    conn.commit()
    return len(rows)


def normalize_periods_for_cik(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> dict:
    company = _get_company(conn, cik)
    if company is None:
        logger.warning("periods.no_company_for_cik", cik=cik)
        return {"cik": cik, "status": "no_company"}
    company_id, fiscal_year_end = company

    cf_row = _latest_companyfacts_object(conn, cik)
    if cf_row is None:
        logger.warning("periods.no_companyfacts_for_cik", cik=cik)
        return {"cik": cik, "status": "no_companyfacts"}
    _raw_id, storage_path = cf_row
    payload = _load_json(storage, storage_path)

    distinct_periods = extract_distinct_periods(payload)
    anchors = build_fye_anchors(distinct_periods)
    nominal_month_day = _parse_fiscal_year_end(fiscal_year_end)

    rows = [classify_period(end, start, anchors, nominal_month_day) for end, start in distinct_periods]
    count = upsert_periods(conn, company_id, rows)

    logger.info(
        "periods.normalized",
        cik=cik,
        company_id=company_id,
        periods=count,
        fye_anchors=len(anchors),
        unclassified=sum(1 for r in rows if r["fiscal_period"] is None),
    )
    return {"cik": cik, "status": "ok", "company_id": company_id, "periods": count}


def normalize_periods(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "no_company": 0, "no_companyfacts": 0, "errored": 0}
    with SupabaseStorageClient() as storage:
        for cik in sorted(ciks):
            stats["considered"] += 1
            try:
                result = normalize_periods_for_cik(storage, conn, cik)
                stats[result["status"]] += 1
            except Exception as exc:
                stats["errored"] += 1
                log_error(conn, "core.normalizer_error", cik, "periods", exc)
    logger.info("periods.normalize.done", **stats)
    return stats
