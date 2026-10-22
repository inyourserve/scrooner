-- Header watermarks. READ ONLY. NOT RUN by the author. One statement each; the 0097 ones only if the table exists.
select max(checked_at) as coverage_checked_at from analytics.company_data_point_coverage;
select max(snapshot_date) as snapshot_date from analytics.coverage_snapshot;
select max(checked_at) as period_gap_checked_at from analytics.period_gap;
select to_regclass('analytics.company_certification') is not null as certification_table_exists;
select to_regclass('analytics.cell_state') is not null as cell_state_exists;
select exists (select 1 from information_schema.columns
               where table_schema='analytics' and table_name='company_data_point_coverage'
                 and column_name='has_value_any_period') as has_value_any_period_exists;
select count(*) as client_connections from pg_stat_activity;      -- the gate: must be <= 14
select max(checks_run_at) from analytics.company_certification;   -- only after 0097
