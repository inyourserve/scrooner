"""Authenticated operational view over persisted daily coverage snapshots."""

from decimal import Decimal

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


_BAND_ORDER = ["top_100", "top_500", "top_1000", "top_1500", "top_2000", "top_3000", "all"]


def _score_delta(current, previous):
    return str(current - previous) if current is not None and previous is not None else None


@router.get("/data-coverage/groups")
def get_group_coverage(
    band: str = Query(default="top_1000", pattern="^(top_(100|500|1000|1500|2000|3000)|all)$"),
    days: int = Query(default=30, ge=2, le=365),
    _: str = Depends(get_current_user_id),
) -> dict:
    """Core-V1 coverage by company rank band (market cap) and by sector,
    from analytics.coverage_group_snapshot, with change vs the previous
    snapshot and a per-band history (mapper/coverage_groups.py)."""
    with get_pooled_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select snapshot_date, group_type, group_key, metric_name, companies, covered,
                       coverage_pct, pct_ge90, pct_lt60
                from analytics.coverage_group_snapshot
                where snapshot_date in (
                    select distinct snapshot_date from analytics.coverage_group_snapshot
                    order by snapshot_date desc limit 2)
                """
            )
            recent = cur.fetchall()
            cur.execute(
                """
                select snapshot_date, group_key, coverage_pct
                from analytics.coverage_group_snapshot
                where group_type = 'rank_band' and metric_name = '__summary__'
                  and snapshot_date in (
                    select distinct snapshot_date from analytics.coverage_group_snapshot
                    order by snapshot_date desc limit %s)
                order by snapshot_date desc
                """,
                (days,),
            )
            history_rows = cur.fetchall()
    dates = sorted({r[0] for r in recent}, reverse=True)
    if not dates:
        return {"as_of": None, "previous_as_of": None, "rank_bands": [], "sectors": [], "band_metrics": [], "history": []}
    latest = dates[0]
    prior = dates[1] if len(dates) > 1 else None
    cur_map = {(r[1], r[2], r[3]): r for r in recent if r[0] == latest}
    prev_map = {(r[1], r[2], r[3]): r for r in recent if r[0] == prior}

    def summary(group_type, key):
        c = cur_map.get((group_type, key, "__summary__"))
        if c is None:
            return None
        p = prev_map.get((group_type, key, "__summary__"))
        return {
            "key": key,
            "companies": c[4],
            "score": str(c[6]),
            "delta": _score_delta(c[6], p[6] if p else None),
            "pct_ge90": str(c[7]),
            "pct_lt60": str(c[8]),
        }

    rank_bands = [x for x in (summary("rank_band", k) for k in _BAND_ORDER) if x]
    sector_keys = sorted({k[1] for k in cur_map if k[0] == "sector_top1000"})
    sectors = []
    for key in sector_keys:
        t1 = summary("sector_top1000", key)
        t2 = cur_map.get(("sector_top2000", key, "__summary__"))
        al = cur_map.get(("sector_all", key, "__summary__"))
        sectors.append(
            {
                **t1,
                "score_top2000": str(t2[6]) if t2 else None,
                "companies_top2000": t2[4] if t2 else 0,
                "score_all": str(al[6]) if al else None,
                "companies_all": al[4] if al else 0,
            }
        )
    sectors.sort(key=lambda s: Decimal(s["score"]))
    band_metrics = []
    for (gt, key, metric), c in cur_map.items():
        if gt == "rank_band" and key == band and metric != "__summary__":
            p = prev_map.get((gt, key, metric))
            band_metrics.append(
                {
                    "metric_name": metric,
                    "companies": c[4],
                    "covered": c[5],
                    "missing": c[4] - c[5],
                    "coverage_pct": str(c[6]),
                    "delta": _score_delta(c[6], p[6] if p else None),
                }
            )
    band_metrics.sort(key=lambda m: (-m["missing"], m["metric_name"]))
    by_date: dict = {}
    for d, key, pct in history_rows:
        by_date.setdefault(str(d), {})[key] = str(pct)
    history = [{"date": d, "bands": v} for d, v in sorted(by_date.items(), reverse=True)]
    return {
        "as_of": str(latest),
        "previous_as_of": str(prior) if prior else None,
        "rank_bands": rank_bands,
        "sectors": sectors,
        "band": band,
        "band_metrics": band_metrics,
        "history": history,
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
