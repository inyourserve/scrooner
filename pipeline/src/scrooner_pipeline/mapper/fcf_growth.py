"""FCF Growth 3Y/5Y CAGR (doc 18 Tier A, built 2026-08-22 -- one of the
two doc 18 Tier A metrics never actually built, alongside
fcf_gt_net_income which turned out to already exist under a different
name -- see DATA_COVERAGE.md).

FCF (`fcf` metric_definition) is itself a computed analytics.metric_value
row (sum_diff of cfo - capex), not a raw canonical_fact -- ttm.py's
GROWTH_METRICS engine reads canonical_fact by canonical_concept_id, so it
can't reach a metric's own output. This module re-derives the same
FY-vs-prior-FY comparison one level up, over metric_value instead of
canonical_fact, reusing ttm.py's own `_growth_value` pure function
unchanged (same CAGR/YoY math, no new formula).

metric_value has no period_id column (period_start/period_end/
period_label only, confirmed in quality_score.py's own docstring) -- FY
identity is recovered by joining metric_value's period_end back to
core.period on (company_id, end_date, fiscal_period='FY'), the same
"match by end date, not a foreign key that doesn't exist" pattern
calculate.py's own module docstring already established for duration-vs-
instant matching.
"""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error
from scrooner_pipeline.mapper.ttm import _growth_value

logger = structlog.get_logger()

LAG_YEARS = {"fcf_growth_yoy": 1, "fcf_growth_3y_cagr": 3, "fcf_growth_5y_cagr": 5}


def _load_fcf_fy_history(
    conn: psycopg.Connection, company_id: int, fcf_metric_id: int
) -> dict[int, Decimal]:
    """fiscal_year -> fcf value, FY rows only, recovered via core.period."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, mv.value
            from analytics.metric_value mv
            join core.period p
              on p.company_id = mv.company_id and p.end_date = mv.period_end and p.fiscal_period = 'FY'
            where mv.company_id = %s and mv.metric_definition_id = %s
              and mv.period_label = 'FY' and mv.value is not null
            """,
            (company_id, fcf_metric_id),
        )
        result: dict[int, Decimal] = {}
        for fiscal_year, value in cur.fetchall():
            if fiscal_year is not None:
                result[fiscal_year] = value
    return result


def _fy_period_dates(conn: psycopg.Connection, company_id: int, fiscal_year: int):
    with conn.cursor() as cur:
        cur.execute(
            "select start_date, end_date from core.period where company_id = %s and fiscal_period = 'FY' and fiscal_year = %s limit 1",
            (company_id, fiscal_year),
        )
        return cur.fetchone()


def calculate_fcf_growth_for_company(
    conn: psycopg.Connection, company_id: int, metric_ids: dict[str, int]
) -> dict:
    fcf_history = _load_fcf_fy_history(conn, company_id, metric_ids["fcf"])
    rows: list[dict] = []

    for metric_name, lag_years in LAG_YEARS.items():
        if metric_name not in metric_ids:
            continue
        for fy in sorted(fcf_history.keys()):
            prior_fy = fy - lag_years
            period = _fy_period_dates(conn, company_id, fy)
            start, end = period if period else (None, None)
            if start is None:
                continue

            if prior_fy not in fcf_history:
                rows.append(
                    {
                        "company_id": company_id,
                        "metric_definition_id": metric_ids[metric_name],
                        "period_start": start,
                        "period_end": end,
                        "period_label": "FY",
                        "value": None,
                        "is_null_reason": f"missing:fcf({prior_fy})",
                        "source_fact_ids": None,
                    }
                )
                continue

            value, reason = _growth_value(
                fcf_history[fy], fcf_history[prior_fy], lag_years
            )
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_ids[metric_name],
                    "period_start": start,
                    "period_end": end,
                    "period_label": "FY",
                    "value": value,
                    "is_null_reason": reason,
                    "source_fact_ids": None,
                }
            )

    with conn.cursor() as cur:
        target_ids = [metric_ids[m] for m in LAG_YEARS if m in metric_ids]
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s) and period_label = 'FY'",
            (company_id, target_ids),
        )
        if rows:
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
        "fcf_growth.company_done", company_id=company_id, computed=computed, null=null
    )
    return {"computed": computed, "null": null}


def calculate_fcf_growth(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_names = ["fcf", "fcf_growth_yoy", "fcf_growth_3y_cagr", "fcf_growth_5y_cagr"]
    with conn.cursor() as cur:
        cur.execute(
            "select metric_name, id from analytics.metric_definition where metric_name = any(%s)",
            (metric_names,),
        )
        metric_ids = dict(cur.fetchall())
    missing = [m for m in metric_names if m not in metric_ids]
    if missing:
        raise RuntimeError(
            f"fcf_growth: metric_definition rows not seeded yet: {missing}"
        )

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
            stats = calculate_fcf_growth_for_company(conn, company_id, metric_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "fcf_growth", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
    logger.info("fcf_growth.done", **totals)
    return totals
