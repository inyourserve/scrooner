-- Screen runs store matched company IDs, not a copy of every company's
-- metric values (2026-09-26, founder-approved design change).
--
-- Measured live before changing anything: saving a 2,060-match screen run
-- took 1.7-2.8s, but EXPLAIN ANALYZE of the same insert server-side was
-- 104ms. The rest was uploading 2.26 MB of per-company JSONB
-- (app.screen_result_item.result, ~1.1 KB/row) plus 83-293 KB of
-- exclusions JSON from the backend to Supabase -- values that already
-- live in analytics.company_screening_snapshot. Uploading just the ID
-- array costs one round trip (~300ms).
--
-- Determinism is kept by versioning the snapshot: a run records its
-- dataset_version and reads that version's rows, so an old run shows the
-- exact values it matched on, never today's. build_snapshot() keeps the
-- latest few versions plus any version a saved screen still points at
-- (screener/snapshot.py), instead of wiping the table every rebuild.

-- 1. Versioned snapshot: one row per (dataset_version, company_id).
alter table analytics.company_screening_snapshot drop constraint if exists company_screening_snapshot_pkey;
alter table analytics.company_screening_snapshot add primary key (dataset_version, company_id);

drop index if exists analytics.idx_screening_snapshot_status;
create index if not exists idx_screening_snapshot_version_status
    on analytics.company_screening_snapshot (dataset_version, status);
-- Supports the core.company FK (the PK no longer leads with company_id).
create index if not exists idx_screening_snapshot_company_id
    on analytics.company_screening_snapshot (company_id);

-- 2. Compact run storage on app.screen_result.
--    company_ids: matched companies, in result order.
--    excluded_missing_ciks / excluded_missing_metrics: parallel arrays,
--    metrics comma-joined per company (metric names never contain commas).
--    excluded_inactive is not stored: it is fully determined by the
--    snapshot version's own status column.
alter table app.screen_result add column if not exists company_ids bigint[];
alter table app.screen_result add column if not exists excluded_missing_ciks text[];
alter table app.screen_result add column if not exists excluded_missing_metrics text[];

update app.screen_result r
set company_ids = coalesce(
        (select array_agg(i.company_id order by i.position)
         from app.screen_result_item i where i.screen_result_id = r.id),
        '{}'),
    excluded_missing_ciks = coalesce(
        (select array_agg(e ->> 'cik' order by ord)
         from jsonb_array_elements(r.exclusions -> 'excluded_missing_data') with ordinality as t(e, ord)),
        '{}'),
    excluded_missing_metrics = coalesce(
        (select array_agg(
                    (select string_agg(m, ',' order by mord)
                     from jsonb_array_elements_text(e -> 'missing_metrics') with ordinality as mm(m, mord))
                    order by ord)
         from jsonb_array_elements(r.exclusions -> 'excluded_missing_data') with ordinality as t(e, ord)),
        '{}')
where r.company_ids is null;

alter table app.screen_result alter column company_ids set not null;
alter table app.screen_result alter column excluded_missing_ciks set not null;
alter table app.screen_result alter column excluded_missing_metrics set not null;

-- 3. The per-company copies and the JSON exclusions are no longer read.
drop table if exists app.screen_result_item;
alter table app.screen_result drop column if exists exclusions;
