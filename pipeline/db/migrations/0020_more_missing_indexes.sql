-- More missing indexes found live 2026-08-22, same investigation as
-- 0019 -- checked each against real query patterns in the codebase
-- before adding (grep for standalone WHERE usage), not blindly applied
-- from Supabase's advisor list. Several advisor-flagged FK columns
-- (core.fact.period_id/unit_id/raw_object_id/supersedes_fact_id,
-- analytics.canonical_fact.canonical_concept_id/period_id,
-- analytics.concept_mapping.concept_id, analytics.statement_line.
-- canonical_concept_id, core.filing.amends_filing_id/raw_submission_id,
-- core.universe_member.*, raw.collector_errors.run_id) were checked and
-- found to have NO standalone-filter usage anywhere in the codebase --
-- always used within a join/composite filter already covered by an
-- existing composite index -- so deliberately NOT added; a real
-- performance win here, not a checklist exercise.
--
-- core.fact.concept_id: resolve.py's per-concept mapping resolution
-- (`where company_id = %s and concept_id = any(%s)`) -- company_id is
-- already the leading column of the existing composite unique key, but
-- concept_id alone is worth having too for other access patterns.
--
-- core.filing.company_id: real, frequent, and had ZERO supporting index
-- at all -- every "get filings for this company" query (apps/site's
-- getRecentFilings, ownership modules, status.py's latest-filing-date
-- lookup, restatements.py) was a full sequential scan over the whole
-- table every time.
--
-- analytics.metric_value.metric_definition_id: screener/resolve.py's
-- own `resolve_most_recent_values` -- the Screener's core query, run on
-- every screen -- filters `where mv.metric_definition_id = any(%s)`
-- with NO company_id in the filter at all, so the existing
-- (company_id, metric_definition_id) composite index (company_id
-- leading) couldn't serve it. Verified via EXPLAIN: now uses a Bitmap
-- Index Scan on this new index directly.
--
-- analytics.metric_definition_input.metric_definition_id: calculate.py's
-- `_load_target_metrics()` queries this per metric on every single
-- calculate() run -- the table had ZERO non-PK indexes at all.

create index concurrently if not exists idx_fact_concept_id on core.fact (concept_id);
create index concurrently if not exists idx_filing_company_id on core.filing (company_id);
create index concurrently if not exists idx_metric_value_metric_definition_id on analytics.metric_value (metric_definition_id);
create index concurrently if not exists idx_metric_definition_input_metric_definition_id on analytics.metric_definition_input (metric_definition_id);
