"""Stage 5b -- Most-recent-value resolution (doc 14 Sec 1). analytics.
metric_value has multiple rows per company per metric (one per reported
period, not just the latest) -- checked live before writing doc 14: roic/
roe have FY and TTM rows (TTM updates every quarter, never more than ~3
months stale); every other of the 12 EDGAR-only metrics has FY and
Q1-Q4 rows, no TTM at all.

Rule, evidenced against real data: prefer the most recent TTM row if one
exists for that metric/company; otherwise take the row with the latest
period_end regardless of label. This naturally favors a fresher quarter
over a stale prior-year FY for the 12 metrics that have no TTM, and
favors TTM's quarterly-updating figure over FY for roic/roe.

Read-only against `analytics`/`core` -- the Screener never writes.
"""

import psycopg
import structlog

logger = structlog.get_logger()


def load_screenable_metric_catalog(conn: psycopg.Connection) -> dict[str, int]:
    """metric_name -> metric_definition_id, for the EDGAR-only (non-price)
    metrics -- doc 14 Sec 5 scopes the screenable catalog to these until
    the price-dependent metrics have real computed values."""
    with conn.cursor() as cur:
        cur.execute("select metric_name, id from analytics.metric_definition where requires_price = false")
        return dict(cur.fetchall())


def resolve_most_recent_values(conn: psycopg.Connection, metric_definition_ids: list[int]) -> dict[tuple[int, int], dict]:
    """(company_id, metric_definition_id) -> {value, period_label, period_end,
    formula_version, is_null_reason} for the single most-recent row per
    company/metric, per the TTM-preferred/latest-period_end rule above.
    Batch-loaded in one query, not per-company -- doc 04's correctness
    controls (load lookups up front, never a query per candidate row)."""
    if not metric_definition_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            with ranked as (
                select mv.company_id, mv.metric_definition_id, mv.value, mv.period_label,
                       mv.period_end, mv.is_null_reason, md.formula_version,
                       row_number() over (
                           partition by mv.company_id, mv.metric_definition_id
                           order by (mv.period_label = 'TTM') desc, mv.period_end desc
                       ) as rn
                from analytics.metric_value mv
                join analytics.metric_definition md on md.id = mv.metric_definition_id
                where mv.metric_definition_id = any(%s)
            )
            select company_id, metric_definition_id, value, period_label, period_end,
                   is_null_reason, formula_version
            from ranked
            where rn = 1
            """,
            (metric_definition_ids,),
        )
        rows = cur.fetchall()

    result = {}
    for company_id, metric_definition_id, value, period_label, period_end, is_null_reason, formula_version in rows:
        result[(company_id, metric_definition_id)] = {
            "value": value,
            "period_label": period_label,
            "period_end": period_end,
            "is_null_reason": is_null_reason,
            "formula_version": formula_version,
        }
    logger.info("screener.resolve.done", metric_count=len(metric_definition_ids), resolved_pairs=len(result))
    return result
