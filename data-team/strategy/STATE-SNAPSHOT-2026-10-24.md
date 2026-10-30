# State snapshot (GENERATED, not hand-written) 2026-10-24 10:43:25 IST

## git
origin/main head: 2cafb1b 2026-10-24 Nightly reprocess: 4-day lookback for the 10-K/10-Q cohort (was 10), backlog branch unchang
local main vs origin (behind ahead): 113	8
changed or untracked paths in the shared tree:      110
migrations on origin/main (last 3): 0095_cash_flow_continuing_operations_fallback.sql 0096_coverage_has_value_any_period.sql 0097_certification_tables.sql 

## applied schema (live DB)
certification_finding=true, company_certification=true, has_value_any_period=true

## coverage table
built 2026-10-23 20:46:41.673786+00, rows 848578, valued 531830, valued any-period (metric rows only) 268356
last snapshot 2026-10-23
cohort v1 (986) cells in table / valued / reasonless blanks: 160718 / 123320 / 13349
cohort v1.1 (1,000) cells in table / valued / reasonless blanks: 161533 / 124029 / 13354

## workflows (last 2 runs each)
pipeline-refresh.yml: 2026-10-24T05:11:44Z in_progress  40065297098;2026-10-23T17:18:17Z completed failure 39993949615;
pipeline-sanity.yml: 2026-10-23T19:18:51Z completed failure 40010416711;2026-10-22T19:14:40Z completed failure 39838371297;
pipeline-frames-check.yml: 2026-10-19T21:25:53Z completed failure 39327427688;2026-10-12T23:35:02Z completed success 38322894090;
workflow-health-check.yml: 2026-10-19T13:49:26Z completed failure 39263442979;2026-10-12T15:56:01Z completed failure 38273802739;

## DB load
Supabase Storage API idle ClientRead x8
(none) idle ClientRead x2
PostgREST 14.5 idle ClientRead x2
postgres_exporter idle ClientRead x1
Supavisor idle ClientRead x1
Supavisor (auth_query) idle ClientRead x1
core.fact live 77194020, dead 7765779, last_autovacuum -
shared_buffers 655368kB
