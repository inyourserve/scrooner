-- DRAFT, not numbered, not applied. Do not claim a migration number from this
-- file; the owner claims one in doc/planning/53 when it is scheduled.
--
-- SYSTEMS.md #17 (2026-11-28): every company the screener cannot match carries
-- a reason on its snapshot row. screener/snapshot.py already computes it
-- (`exclusion_reason`) and writes it as soon as this column exists (it checks
-- information_schema before each build, so main works before and after).
--
-- Values: NULL (screenable), 'inactive_company', 'no_metric_values'.
-- Nullable, no default: metadata-only, no table rewrite. Rows of older
-- dataset versions keep NULL (not backfilled; they are pruned in 3 builds).

alter table analytics.company_screening_snapshot
    add column if not exists exclusion_reason text;

comment on column analytics.company_screening_snapshot.exclusion_reason is
    'Why this company can match no screen: inactive_company or no_metric_values; NULL when screenable. Per-metric reasons are resolved at query time (screener/missing_reasons.py).';
