"""Grouped coverage snapshots: core-V1 coverage cut by company rank band
(market cap, revenue fallback) and by sector, persisted daily to
analytics.coverage_group_snapshot so changes over time are queryable.

Raw lens by design: every active company in a group counts in the
denominator, and a data point is covered only if it has a value in
analytics.company_data_point_coverage. No structural-gap exclusions --
this shows the real product-facing picture of what a user would see.
Reads company_data_point_coverage as last refreshed; it does not
rebuild it."""

from datetime import date, datetime, timezone

import psycopg
import structlog

from scrooner_pipeline.mapper.coverage_snapshot import CORE_V1_METRIC_NAMES

logger = structlog.get_logger()

RANK_BANDS = (100, 500, 1000, 1500, 2000, 3000)

_SNAPSHOT_SQL = """
with mc as (
    select distinct on (mv.company_id) mv.company_id, mv.value as v
    from analytics.metric_value mv
    join analytics.metric_definition d on d.id = mv.metric_definition_id
         and d.metric_name = 'market_cap' and d.status = 'active'
    where mv.value is not null
    order by mv.company_id, mv.period_end desc
), rv as (
    select distinct on (mv.company_id) mv.company_id, mv.value as v
    from analytics.metric_value mv
    join analytics.metric_definition d on d.id = mv.metric_definition_id
         and d.metric_name = 'revenue' and d.status = 'active'
    where mv.value is not null
    order by mv.company_id, mv.period_end desc
), ranked as (
    select c.id as company_id,
           coalesce(nullif(c.sector, ''), nullif(c.y_sector, ''), 'Unclassified') as sector,
           row_number() over (
               order by (mc.v is null), mc.v desc nulls last, rv.v desc nulls last, c.id
           ) as rnk
    from core.company c
    left join mc on mc.company_id = c.id
    left join rv on rv.company_id = c.id
    where c.status = 'active'
), cov as (
    select r.company_id, r.sector, r.rnk, cv.data_point_name, cv.has_value
    from ranked r
    join analytics.company_data_point_coverage cv on cv.company_id = r.company_id
    where cv.data_point_name = any(%(core)s)
), company_score as (
    select company_id, sector, rnk,
           100.0 * count(*) filter (where has_value) / %(n_core)s as pct
    from cov group by company_id, sector, rnk
), memberships as (
    select 'rank_band'::text as group_type,
           case when b = 0 then 'all' else 'top_' || b end as group_key,
           r.company_id, r.rnk
    from ranked r cross join unnest(%(bands)s::int[]) as b
    where b = 0 or r.rnk <= b
    union all
    select 'sector_all', sector, company_id, rnk from ranked
    union all
    select 'sector_top1000', sector, company_id, rnk from ranked where rnk <= 1000
    union all
    select 'sector_top2000', sector, company_id, rnk from ranked where rnk <= 2000
), per_metric as (
    select m.group_type, m.group_key, cv.data_point_name as metric_name,
           count(*) as companies,
           count(*) filter (where cv.has_value) as covered
    from memberships m
    join cov cv on cv.company_id = m.company_id
    group by 1, 2, 3
), summary as (
    select m.group_type, m.group_key, '__summary__' as metric_name,
           count(*) as companies,
           round(sum(s.pct) / 100.0 * %(n_core)s)::int as covered,
           round(avg(s.pct), 2) as coverage_pct,
           round(100.0 * count(*) filter (where s.pct >= 90) / count(*), 2) as pct_ge90,
           round(100.0 * count(*) filter (where s.pct < 60) / count(*), 2) as pct_lt60
    from memberships m
    join company_score s on s.company_id = m.company_id
    group by 1, 2
)
insert into analytics.coverage_group_snapshot
    (snapshot_date, group_type, group_key, metric_name, companies, covered, coverage_pct, pct_ge90, pct_lt60)
select %(as_of)s, group_type, group_key, metric_name, companies, covered,
       round(100.0 * covered / companies, 2), null, null
from per_metric
union all
select %(as_of)s, group_type, group_key, metric_name, companies, covered, coverage_pct, pct_ge90, pct_lt60
from summary
"""


def write_group_snapshot(conn: psycopg.Connection, as_of: date | None = None) -> dict:
    as_of = as_of or datetime.now(timezone.utc).date()
    core = sorted(CORE_V1_METRIC_NAMES)
    with conn.cursor() as cur:
        cur.execute("set local statement_timeout = 0")
        cur.execute(
            "delete from analytics.coverage_group_snapshot where snapshot_date = %s",
            (as_of,),
        )
        cur.execute(
            _SNAPSHOT_SQL,
            {
                "as_of": as_of,
                "core": core,
                "n_core": len(core),
                "bands": [*RANK_BANDS, 0],
            },
        )
        rows = cur.rowcount
    conn.commit()
    stats = {"snapshot_date": as_of.isoformat(), "rows_written": rows}
    logger.info("coverage_group_snapshot.written", **stats)
    return stats
