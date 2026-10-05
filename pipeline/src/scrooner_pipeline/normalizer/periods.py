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

import calendar
import json
from datetime import date, datetime

import psycopg
import structlog

from scrooner_pipeline.collector.storage import (
    SupabaseStorageClient,
    strip_bucket_prefix,
)
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


def _latest_companyfacts_object(
    conn: psycopg.Connection, cik: str
) -> tuple[int, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id, storage_path from raw.sec_companyfacts where cik = %s order by fetched_at desc limit 1",
            (cik,),
        )
        return cur.fetchone()


def _get_company(conn: psycopg.Connection, cik: str) -> tuple[int, str | None] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id, fiscal_year_end from core.company where cik = %s", (cik,)
        )
        return cur.fetchone()


# Sanity bounds on raw filer-submitted XBRL context dates (2026-10-05).
# These are NOT this project's own data -- extract_distinct_periods reads
# `end`/`start` directly off each company's raw SEC companyfacts payload,
# values a filer's own XBRL-generation software wrote into that filing's
# context element. Found live investigating an "operating_income not_
# resolved" gap for BK Technologies: core.period held a row spanning
# 2019-01-01 to 2020-12-31 (731 days) for a single stray
# DepreciationDepletionAndAmortization fact -- a real filer-side context
# error, not a Scrooner bug. Broadened the check population-wide and found
# it is NOT rare: 10,227 duration periods span >400 days, with absurd
# dates (year "205", year "202" -- clearly a truncated 4-digit year;
# Oracle's 1900-01-01..2199-12-31, almost certainly a "no specific period"
# sentinel some filer software emits; Tenax Therapeutics/Enpro/Mannatech
# spanning into 1967/1976/2108) -- 88,903 of the resulting facts are
# `is_authoritative=true` RIGHT NOW, meaning this isn't cold/dead data,
# it's live in `core.fact` today. FULL_YEAR_MAX_DAYS (380, this file's own
# already-documented empirical ceiling across AAPL's full 2007-2025
# history, "no fuzzy boundary cases observed") already told us the true
# ceiling for a real duration period; nothing here was ever supposed to
# exceed it by this much. Filtering here -- before ANY core.period row is
# created -- is the correct layer: Stage 2d (facts.py) already has a
# graceful, counted skip path for a fact whose period was never created
# (`skipped_period_not_found`), so a fact pointing at a now-filtered-out
# garbage period simply gets counted there instead of corrupting a real
# reporting slot. A plain year-bound check alone would catch most of
# these (year 205/202/1900/1967/1976/2108 are all absurd on their own),
# but the real bound that matters is the SPAN -- a company's own
# `fiscal_year_end`/`now` fields are irrelevant here; what makes a
# duration period real is only ever its length.
_MIN_PLAUSIBLE_YEAR = 1990  # EDGAR electronic filing predates nothing earlier
_MAX_SPAN_DAYS = 400  # FULL_YEAR_MAX_DAYS (380) + generous slack


def _is_plausible_period(end: str, start: str | None) -> bool:
    try:
        end_date = date.fromisoformat(end)
    except ValueError:
        return False
    if end_date.year < _MIN_PLAUSIBLE_YEAR:
        return False
    if start is None:
        return True
    try:
        start_date = date.fromisoformat(start)
    except ValueError:
        return False
    if start_date.year < _MIN_PLAUSIBLE_YEAR:
        return False
    if start_date > end_date:
        return False
    return (end_date - start_date).days <= _MAX_SPAN_DAYS


def extract_distinct_periods(payload: dict) -> set[tuple[str, str | None]]:
    """(end, start_or_None) for every distinct period referenced anywhere in
    a companyfacts payload, across every taxonomy/concept/unit -- the raw
    material this stage resolves, independent of which specific facts will
    eventually reference them (Stage 2d's job, not this one's). Silently
    drops any (start, end) pair failing `_is_plausible_period` -- a real
    filer-side XBRL date error, never a legitimate reporting period (see
    this module's own sanity-bounds comment above)."""
    periods: set[tuple[str, str | None]] = set()
    for _taxonomy, concepts in payload.get("facts", {}).items():
        for _concept, cdata in concepts.items():
            for _unit, entries in cdata.get("units", {}).items():
                for e in entries:
                    end = e.get("end")
                    if not end:
                        continue
                    start = e.get("start")
                    if not _is_plausible_period(end, start):
                        continue
                    periods.add((end, start))
    return periods


def extract_fy_tagged_spans(payload: dict) -> set[tuple[str, str]]:
    """(start, end) pairs where SEC's own per-fact `fp` field says this
    span IS the company's fiscal year ('FY') -- a peer signal to `end`/
    `start` themselves (SEC-computed from the filer's own
    dei:DocumentFiscalPeriodFocus, not a guessed/wobbly company-level
    default), used to confirm a genuine annual span rather than one that
    merely happens to be ~365 days long. See build_fye_anchors' own
    docstring for why this distinction matters."""
    fy_spans: set[tuple[str, str]] = set()
    for _taxonomy, concepts in payload.get("facts", {}).items():
        for _concept, cdata in concepts.items():
            for _unit, entries in cdata.get("units", {}).items():
                for e in entries:
                    end, start = e.get("end"), e.get("start")
                    if end and start and e.get("fp") == "FY":
                        fy_spans.add((start, end))
    return fy_spans


def build_fye_anchors(
    periods: set[tuple[str, str | None]],
    fy_tagged_spans: set[tuple[str, str]] | None = None,
) -> list[date]:
    """Every distinct end_date belonging to a full-year-length duration --
    empirically this company's OWN real fiscal-year-end dates. No MMDD
    guessing: verified live that AAPL's actual FYE wobbles day-to-day
    against its nominal '0926' (2016-09-24, 2017-09-30, 2018-09-29, ...),
    so only observed data is trustworthy here. Sorted ascending.

    Found live 2026-09-05 (Amazon): duration length alone is NOT a
    sufficient signal. Amazon's 2008-2013-era 10-Qs additionally disclose
    a real, legitimate "trailing twelve months ended <quarter-end>" cash-
    flow-statement comparative -- a genuine GAAP figure, but not the
    company's fiscal year -- that also spans 350-380 days. Its end dates
    land on ordinary quarter-ends (2008-06-30, 2008-09-30, ...), so the
    old duration-only heuristic treated EVERY quarter as a phantom
    fiscal-year-end, collapsing the anchor spacing from ~365 days to
    ~91 days and making every subsequent classify_period() call compute
    idx~0-1 regardless of the real quarter -- every period in the company's
    history was mislabeled 'Q1'. Confirmed the TTM entries are explicitly
    tagged fp='Q2'/form='10-Q' by SEC itself, while real annual entries for
    the same company are consistently fp='FY'/form='10-K' -- a reliable,
    already-present per-fact signal, not a new guess. When fy_tagged_spans
    is available and non-empty for this company, only those (start, end)
    pairs count as anchors; falls back to the original duration-only
    heuristic when a company has no fp='FY' evidence at all (better than
    zero anchors, and preserves prior behavior for that rare case)."""
    duration_anchors, fy_anchors = set(), set()
    for end, start in periods:
        if start is None:
            continue
        if (
            FULL_YEAR_MIN_DAYS
            <= (_parse_date(end) - _parse_date(start)).days
            <= FULL_YEAR_MAX_DAYS
        ):
            duration_anchors.add(_parse_date(end))
            if fy_tagged_spans and (start, end) in fy_tagged_spans:
                fy_anchors.add(_parse_date(end))
    if fy_anchors:
        return sorted(fy_anchors)
    return sorted(duration_anchors)


def _step_year(d: date, delta: int) -> date:
    """date(year+delta, month, day), except Feb 29 rolls to Feb 28 in a
    non-leap target year instead of raising ValueError -- found live
    2026-09-03 (MannKind, CIK 0000899460): a company with an observed Feb
    29 fiscal-year-end anchor crashed _bracket_fye's plain
    date(candidate.year +/- 1, ...) the moment it stepped into a non-leap
    year, which is most years. Rolling to Feb 28 is the same convention
    already implicit in FULL_YEAR_MIN_DAYS/MAX_DAYS treating adjacent
    Feb-28/Feb-29 fiscal years as the same ~365-day cadence."""
    year = d.year + delta
    month, day = d.month, d.day
    if month == 2 and day == 29 and not calendar.isleap(year):
        day = 28
    return date(year, month, day)


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
        base = (
            anchors[-1]
            if anchors
            else (
                date(target.year - 1, *nominal_month_day) if nominal_month_day else None
            )
        )
        if base is not None:
            candidate = base
            while candidate < target:
                candidate = _step_year(candidate, 1)
            next_fye = candidate
    if prior_fye is None:
        base = anchors[0] if anchors else next_fye
        if base is not None:
            candidate = base
            while candidate >= target:
                candidate = _step_year(candidate, -1)
            prior_fye = candidate
    return next_fye, prior_fye


def _fiscal_year_label(fye: date | None) -> int | None:
    """Fiscal-year label for a fiscal-year-end date.

    Normally the calendar year of the year-end. A 52/53-week calendar ends on
    the Saturday/Sunday nearest Dec 31, so a year can end Jan 1-3 of the NEXT
    calendar year (BlueLinx FY ending 2022-01-01, HNI 2011-01-01, Illumina
    2012-01-01). SEC files those under the prior fiscal year, and labelling
    them by calendar year gave two different fiscal years the same label
    (2022-01-01 and 2022-12-31 both "2022"). derived.py groups by
    (concept, unit, fiscal_year), so the collision overwrote Q1/FY slots and
    blocked Q4 derivation (found 2026-10-03, 95 of 98 such companies).
    A year-end in Jan 1-10 therefore belongs to the prior year; retailers
    ending late January/early February are unaffected."""
    if fye is None:
        return None
    if fye.month == 1 and fye.day <= 10:
        return fye.year - 1
    return fye.year


def classify_period(
    end: str,
    start: str | None,
    anchors: list[date],
    nominal_month_day: tuple[int, int] | None,
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
    fiscal_year = _fiscal_year_label(next_fye)
    fiscal_period = None

    if period_type == "duration":
        # Found live 2026-09-05 (Amazon): duration length alone is NOT
        # sufficient for "FY" -- a real, legitimate "trailing twelve
        # months ended <quarter-end>" cash-flow-statement comparative
        # (Amazon's 2008-2013-era 10-Qs) also spans 350-380 days but ends
        # on an ordinary quarter-end, not the company's real fiscal-year-
        # end. The instant branch below already requires end_date ==
        # next_fye for its own FY case; this now matches that same
        # anchor-confirmed check, rather than trusting length alone.
        if (
            FULL_YEAR_MIN_DAYS <= duration_days <= FULL_YEAR_MAX_DAYS
            and end_date == next_fye
        ):
            fiscal_period = "FY"
        elif (
            QUARTER_MIN_DAYS <= duration_days <= QUARTER_MAX_DAYS
            and prior_fye is not None
        ):
            idx = round((end_date - prior_fye).days / NOMINAL_QUARTER_DAYS)
            fiscal_period = f"Q{min(max(idx, 1), 4)}"
        # else: non-standard duration (half-year/three-quarter YTD spans,
        # irregular stub periods, or a full-year-length span whose end
        # date isn't a confirmed anchor -- e.g. a TTM comparative) --
        # left unclassified rather than mislabeled.
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


def normalize_periods_for_cik(
    storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str
) -> dict:
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
    fy_tagged_spans = extract_fy_tagged_spans(payload)
    anchors = build_fye_anchors(distinct_periods, fy_tagged_spans)
    nominal_month_day = _parse_fiscal_year_end(fiscal_year_end)

    rows = [
        classify_period(end, start, anchors, nominal_month_day)
        for end, start in distinct_periods
    ]
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
    stats = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "no_companyfacts": 0,
        "errored": 0,
    }
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
