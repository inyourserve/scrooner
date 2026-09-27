-- 2026-09-21: live Supabase performance-advisor sweep (prompted directly:
-- "solve everything to make [the db] top class") found 26 foreign keys
-- across analytics/core/raw with no covering index -- each one is a real
-- risk of the exact failure this project has already hit twice for the
-- SAME underlying reason (a FK join/delete/cascade forced into a full
-- table scan): core.fact's own filing_id FK caused a live production
-- incident this way on 2026-08-22 (see pipeline/CLAUDE.md, "A repeated
-- connection-drop failure..."), and core.institutional_ownership's
-- dedup query hit an unrelated-but-same-shaped 8.2s-per-company cost on
-- 2026-09-15 (0066_company_page_hot_path_indexes.sql). Cheap, additive,
-- zero risk on tables this size -- applied directly rather than waiting
-- for a third incident to justify it.
--
-- This file covers every flagged FK EXCEPT the 5 on core.fact (27 GB,
-- written continuously by the daily Collector/Normalizer cron) and
-- analytics.canonical_fact.period_id (3.6 GB) -- those are applied
-- separately via CREATE INDEX CONCURRENTLY, outside any transaction, so a
-- long-running index build never blocks a live write on an active table
-- (see 0071_large_table_fk_indexes_concurrent.sql). Every table here is
-- small/moderate (under a few hundred MB), matching this project's own
-- established precedent (0066 added a plain index directly on a 1.8 GB
-- table with no CONCURRENTLY) of not needing that extra care.
create index if not exists idx_canonical_fact_sanity_override_concept_id
  on analytics.canonical_fact_sanity_override (canonical_concept_id);
create index if not exists idx_canonical_fact_sanity_override_period_id
  on analytics.canonical_fact_sanity_override (period_id);
create index if not exists idx_company_stock_split_source_fact_id
  on analytics.company_stock_split (source_fact_id);
create index if not exists idx_concept_mapping_concept_id
  on analytics.concept_mapping (concept_id);
create index if not exists idx_concept_parser_attempt_concept_id
  on analytics.concept_parser_attempt (canonical_concept_id);
create index if not exists idx_data_sanity_investigation_check_id
  on analytics.data_sanity_investigation (data_sanity_check_id);
create index if not exists idx_data_sanity_investigation_period_id
  on analytics.data_sanity_investigation (period_id);
create index if not exists idx_metric_definition_input_concept_id
  on analytics.metric_definition_input (canonical_concept_id);
create index if not exists idx_statement_comparison_finding_concept_id
  on analytics.statement_comparison_finding (canonical_concept_id);
create index if not exists idx_statement_comparison_finding_period_id
  on analytics.statement_comparison_finding (period_id);
create index if not exists idx_statement_line_concept_id
  on analytics.statement_line (canonical_concept_id);
create index if not exists idx_timeseries_outlier_check_concept_id
  on analytics.timeseries_outlier_check (canonical_concept_id);
create index if not exists idx_timeseries_outlier_check_period_id
  on analytics.timeseries_outlier_check (period_id);
create index if not exists idx_yfinance_line_item_mapping_concept_id
  on analytics.yfinance_line_item_mapping (canonical_concept_id);
create index if not exists idx_filing_amends_filing_id
  on core.filing (amends_filing_id);
create index if not exists idx_filing_raw_submission_id
  on core.filing (raw_submission_id);
create index if not exists idx_universe_member_company_id
  on core.universe_member (company_id);
create index if not exists idx_universe_member_filer_id
  on core.universe_member (filer_id);
create index if not exists idx_universe_member_listing_id
  on core.universe_member (listing_id);
create index if not exists idx_universe_member_security_id
  on core.universe_member (security_id);
create index if not exists idx_collector_errors_run_id
  on raw.collector_errors (run_id);

-- Same sweep found one orphaned table: core.period_snapshot_20260905, a
-- before/after snapshot taken ahead of the 2026-09-05/06 fiscal-year-end
-- period fixes (see pipeline/CLAUDE.md's "trailing twelve months" and
-- leap-year-FYE entries) and never cleaned up. No primary key (flagged
-- by the linter), no index, 974,721 rows, 59 MB, and confirmed via a
-- full repo grep to have zero references anywhere in pipeline/apps code
-- before dropping -- pure debug residue, not live schema.
drop table if exists core.period_snapshot_20260905;
