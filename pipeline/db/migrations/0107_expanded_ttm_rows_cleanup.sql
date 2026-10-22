-- One-time cleanup of superseded expanded_metrics TTM rows (Data Engineer lane 2,
-- claimed in doc 53 as 0107). NOT applied by this file alone.
--
-- Why: expanded_metrics.py stamps every TTM row period_start = period_end = the
-- compute date and (until the 2026-10-22 fix) only upserted, so each daily run
-- left one more TTM row per company per metric. Only the newest row is read.
--
-- What this migration creates (structure only; it changes NO existing row):
--   analytics.metric_value_ttm_archive  copy of metric_value's columns + archived_at,
--                                       archive_reason; the rows removed below live here.
--   analytics.archive_superseded_expanded_ttm(from_company, to_company, metric_ids)
--                                       moves, for companies in [from, to), every
--                                       period_label = 'TTM' row of the given metric ids
--                                       whose period_end is older than that company's
--                                       newest TTM period_end for the same metric, into
--                                       the archive, in ONE statement/transaction, and
--                                       returns the number of rows moved. The newest row
--                                       per (company, metric) is never touched.
--
-- Procedure (reviewed dry-run first): scripts/expanded_ttm_rows_cleanup_dryrun.py
-- counts the rows per metric and period_end (read-only); scripts/
-- expanded_ttm_rows_cleanup_run.py calls the function in company-id chunks and
-- refuses to apply unless the dry-run total is passed back. Restore of a chunk:
-- insert the archive rows back (the archive keeps the original id and values).
create table if not exists analytics.metric_value_ttm_archive (
    like analytics.metric_value,
    archived_at timestamptz not null default now(),
    archive_reason text not null default 'superseded_expanded_ttm_row'
);

create index if not exists idx_metric_value_ttm_archive_company
    on analytics.metric_value_ttm_archive (company_id, metric_definition_id, period_end);

create or replace function analytics.archive_superseded_expanded_ttm(
    p_company_from bigint,
    p_company_to bigint,
    p_metric_ids bigint[]
) returns bigint
language plpgsql
as $$
declare
    moved bigint;
begin
    with newest as (
        select company_id, metric_definition_id, max(period_end) as newest_end
        from analytics.metric_value
        where company_id >= p_company_from and company_id < p_company_to
          and period_label = 'TTM'
          and metric_definition_id = any (p_metric_ids)
        group by company_id, metric_definition_id
    ),
    gone as (
        delete from analytics.metric_value mv
        using newest n
        where mv.company_id = n.company_id
          and mv.metric_definition_id = n.metric_definition_id
          and mv.period_label = 'TTM'
          and mv.period_end < n.newest_end
          and mv.company_id >= p_company_from and mv.company_id < p_company_to
        returning mv.*
    )
    insert into analytics.metric_value_ttm_archive
        (id, company_id, metric_definition_id, period_start, period_end, period_label,
         value, data_as_of, is_null_reason, source_fact_ids, created_at)
    select id, company_id, metric_definition_id, period_start, period_end, period_label,
           value, data_as_of, is_null_reason, source_fact_ids, created_at
    from gone;
    get diagnostics moved = row_count;
    return moved;
end;
$$;
