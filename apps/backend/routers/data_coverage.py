"""Authenticated operational view over persisted daily coverage snapshots."""

from fastapi import APIRouter, Depends, HTTPException, Query
from scrooner_pipeline.mapper.company_coverage_dashboard import summarize_company

from auth import get_current_user_id
from db_pool import get_pooled_connection

router = APIRouter(prefix="/v1", tags=["data_coverage"])


@router.get("/data-coverage")
def get_data_coverage(
    days: int = Query(default=30, ge=7, le=365),
    _: str = Depends(get_current_user_id),
) -> dict:
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select snapshot_date,
                       max(coverage_pct) filter (where item_name = 'avg_metric_coverage_score') as metric_score,
                       max(coverage_pct) filter (where item_name = 'avg_core_v1_metric_coverage_score') as core_score,
                       max(coverage_pct) filter (where item_name = 'avg_concept_coverage_score') as concept_score,
                       max(total_active_companies) as total_active_companies
                from analytics.coverage_snapshot
                where item_type = 'score'
                group by snapshot_date
                order by snapshot_date desc
                limit %s
                """,
                (days,),
            )
            history_rows = cur.fetchall()

            cur.execute(
                """
                with dates as (
                    select distinct snapshot_date
                    from analytics.coverage_snapshot
                    order by snapshot_date desc
                    limit 2
                ), ranked_dates as (
                    select snapshot_date, row_number() over (order by snapshot_date desc) as position
                    from dates
                )
                select current.item_name,
                       current.companies_covered,
                       current.total_active_companies,
                       current.coverage_pct,
                       previous.coverage_pct
                from analytics.coverage_snapshot current
                join ranked_dates current_date on current_date.snapshot_date = current.snapshot_date and current_date.position = 1
                left join ranked_dates previous_date on previous_date.position = 2
                left join analytics.coverage_snapshot previous
                  on previous.snapshot_date = previous_date.snapshot_date
                 and previous.item_type = current.item_type
                 and previous.item_name = current.item_name
                where current.item_type = 'metric'
                order by current.coverage_pct asc, current.item_name
                limit 20
                """
            )
            metric_rows = cur.fetchall()

    history = [
        {
            "date": str(row[0]),
            "metric_score": str(row[1]) if row[1] is not None else None,
            "core_score": str(row[2]) if row[2] is not None else None,
            "concept_score": str(row[3]) if row[3] is not None else None,
            "total_active_companies": row[4],
        }
        for row in history_rows
    ]
    metrics = [
        {
            "metric_name": row[0],
            "companies_covered": row[1],
            "total_active_companies": row[2],
            "coverage_pct": str(row[3]),
            "previous_coverage_pct": str(row[4]) if row[4] is not None else None,
            "delta": str(row[3] - row[4]) if row[4] is not None else None,
        }
        for row in metric_rows
    ]
    return {
        "as_of": history[0]["date"] if history else None,
        "history": history,
        "weakest_metrics": metrics,
    }


@router.get("/data-coverage/company/{ticker}")
def get_company_coverage(
    ticker: str,
    _: str = Depends(get_current_user_id),
) -> dict:
    """2026-10-03: the company-wise view (pipeline/mapper/company_coverage_dashboard.py)
    -- "for this one company, what's missing and why" -- exposed over HTTP
    for the first time. Ticker resolution mirrors company_page.py's own
    lower(ticker) lookup against core.listing."""
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select company_id from core.listing where lower(ticker) = lower(%s) limit 1",
                (ticker,),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Ticker not found")
            summary = summarize_company(conn, row[0])
    return summary
