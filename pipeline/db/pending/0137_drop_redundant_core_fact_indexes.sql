-- 0137: drop two core.fact indexes that cost write load and space for little read value.
-- Draft 2026-11-28 (Data Engineer, egress/write-load cut; founder approved the work, NOT the apply).
--
--   idx_fact_company_concept_period (company_id, concept_id, period_id)  3466 MB, 20.2M scans since stats reset
--   idx_fact_unit_id                (unit_id)                              903 MB,  55.7K scans
--
-- Every insert into core.fact (142M statements) maintains both. Live reads were checked first:
--
-- * Queries filtering core.fact by company_id/concept_id/period_id (about 150 sites in pipeline/src) keep
--   a covering index: the unique constraint fact_company_id_concept_id_unit_id_period_id_filing_id_key
--   (company_id, concept_id, unit_id, period_id, filing_id) serves company_id, company_id + concept_id,
--   and (company_id, concept_id, unit_id, period_id) lookups on its leading columns, including the
--   conflict_latest_filed.py join (the one place that joins on unit_id, always with all four leading columns).
--   The one shape that loses its exact index is company_id + concept_id + period_id WITHOUT unit_id: it
--   becomes a range scan over the (company, concept) entries (company 3: median 24, p99 218, max 242 rows
--   per concept) with period_id as an index qual, instead of one entry.
-- * unit_id is never filtered on its own in code; the only other use is the FK check when a core.unit row is
--   deleted or updated, which does not happen (core.unit is a static lookup, canonicalize_unit).
--
-- Apply note: this file is written for the ledger path (psql --single-transaction), where DROP INDEX
-- CONCURRENTLY is not allowed (0071 had to be applied statement by statement for the same reason).
-- A plain DROP INDEX needs ACCESS EXCLUSIVE on core.fact, so it is bounded by lock_timeout: if core.fact is
-- busy the whole migration fails cleanly with nothing dropped and can simply be retried. If the founder
-- prefers CONCURRENTLY, run the two statements below one at a time outside a transaction instead
-- (and insert the ledger row separately):
--   drop index concurrently if exists core.idx_fact_company_concept_period;
--   drop index concurrently if exists core.idx_fact_unit_id;
-- Rollback (both are plain btrees, rebuild is slow on a 30 GB table, so use CONCURRENTLY):
--   create index concurrently idx_fact_company_concept_period on core.fact (company_id, concept_id, period_id);
--   create index concurrently idx_fact_unit_id on core.fact (unit_id);

set local lock_timeout = '5s';

drop index if exists core.idx_fact_company_concept_period;
drop index if exists core.idx_fact_unit_id;
