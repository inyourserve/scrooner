"""Dividend Growth Streak (doc 26, built 2026-08-22). Consecutive most-
recent FY years with dividends_per_share strictly increasing, counted
backward from the latest year until a flat/decreasing/missing year
breaks the streak -- same "as of latest FY, single value" shape as
quality_flags.py's profitable_streak_years, same walk-backward
algorithm (a gap year in the fiscal-year sequence breaks the streak the
same way a missing fact does, since both fail the `fy in facts` check).

Null (not 0) for a company with no dividend history at all -- a company
that has never paid a dividend has no streak to report, which is a
different fact than "streak broken at 0 years," the same "absence isn't
evidence of a 0 value" discipline as zero_debt.

Important, honest caveat, found live checking AAPL's own real history
before trusting this: a stock split changes dividends_per_share's raw
reported value without the per-share economics actually declining --
AAPL's own dividends_per_share drops from $2.40 (FY2017) to $0.795
(FY2020) purely because of the Aug 2020 4-for-1 split, not a real
dividend cut. This project has no split-adjustment logic anywhere
(matching its existing "don't silently correct source data" discipline
for total_debt's conflicting values, dedupe.py Stage 2e, etc.) -- the
streak is computed on dividends_per_share exactly as reported, so a
split can visibly break a real, ongoing dividend-growth streak. This is
disclosed here rather than worked around with a heuristic.
"""

from datetime import date

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()


def _load_concept_id(conn: psycopg.Connection) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = 'dividends_per_share'"
        )
        row = cur.fetchone()
        return row[0] if row else None


def _load_fy_history(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> dict[int, float]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, cf.value
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s and p.fiscal_period = 'FY'
            """,
            (company_id, concept_id),
        )
        return {
            fy: value
            for fy, value in cur.fetchall()
            if fy is not None and value is not None
        }


def _fy_period_dates(
    conn: psycopg.Connection, company_id: int, concept_id: int, fiscal_year: int
):
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.start_date, p.end_date from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s and p.fiscal_period = 'FY' and p.fiscal_year = %s
            limit 1
            """,
            (company_id, concept_id, fiscal_year),
        )
        return cur.fetchone()


def calculate_streak_for_company(
    conn: psycopg.Connection, company_id: int, metric_id: int, concept_id: int
) -> dict:
    history = _load_fy_history(conn, company_id, concept_id)
    rows: list[dict] = []

    if not history:
        rows.append(
            {
                "company_id": company_id,
                "metric_definition_id": metric_id,
                "period_start": date.today(),
                "period_end": date.today(),
                "period_label": "FY",
                "value": None,
                "is_null_reason": "no_dividend_history",
                "source_fact_ids": None,
            }
        )
    else:
        latest_fy = max(history.keys())
        streak = 0
        fy = latest_fy
        while (fy - 1) in history and history[fy] > history[fy - 1]:
            streak += 1
            fy -= 1
        period = _fy_period_dates(conn, company_id, concept_id, latest_fy)
        start, end = period if period else (date.today(), date.today())
        rows.append(
            {
                "company_id": company_id,
                "metric_definition_id": metric_id,
                "period_start": start,
                "period_end": end,
                "period_label": "FY",
                "value": streak,
                "is_null_reason": None,
                "source_fact_ids": None,
            }
        )

    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = %s and period_label = 'FY'",
            (company_id, metric_id),
        )
        cur.executemany(
            """
            insert into analytics.metric_value
                (company_id, metric_definition_id, period_start, period_end, period_label,
                 value, is_null_reason, source_fact_ids)
            values
                (%(company_id)s, %(metric_definition_id)s, %(period_start)s, %(period_end)s,
                 %(period_label)s, %(value)s, %(is_null_reason)s, %(source_fact_ids)s)
            """,
            rows,
        )
        conn.commit()

    computed = sum(1 for r in rows if r["value"] is not None)
    null = sum(1 for r in rows if r["value"] is None)
    logger.info(
        "dividend_streak.company_done",
        company_id=company_id,
        computed=computed,
        null=null,
    )
    return {"computed": computed, "null": null}


def calculate_dividend_streak(conn: psycopg.Connection, ciks: set[str]) -> dict:
    concept_id = _load_concept_id(conn)
    if concept_id is None:
        raise RuntimeError(
            "dividend_streak: dividends_per_share canonical concept not found"
        )

    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.metric_definition where metric_name = 'dividend_growth_streak_years'"
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError(
            "dividend_streak: dividend_growth_streak_years metric_definition row not seeded yet"
        )
    metric_id = row[0]

    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "computed": 0,
        "null": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = calculate_streak_for_company(
                conn, company_id, metric_id, concept_id
            )
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "dividend_streak", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
    logger.info("dividend_streak.done", **totals)
    return totals
