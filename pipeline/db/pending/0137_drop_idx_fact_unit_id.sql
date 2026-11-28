-- 0137: drop core.idx_fact_unit_id (unit_id; 903 MB, 55.7K scans since stats reset).
-- Draft 2026-11-28 (Data Engineer, write-load cut; founder approved the work, NOT the apply).
--
-- Kept on purpose: idx_fact_company_concept_period (20.2M scans, hot lookups), so it is NOT dropped.
--
-- unit_id is never filtered on its own in pipeline/src. The one join on unit_id (conflict_latest_filed.py:889)
-- uses company_id, concept_id, unit_id, period_id, which the unique constraint
-- fact_company_id_concept_id_unit_id_period_id_filing_id_key serves on its leading columns. The only other use is the
-- FK check when a core.unit row is deleted or updated, which does not happen (static lookup).
--
-- Apply note: written for the ledger path (psql --single-transaction), where DROP INDEX CONCURRENTLY is not
-- allowed. A plain DROP INDEX needs ACCESS EXCLUSIVE on core.fact, so it is bounded by lock_timeout: if core.fact
-- is busy the migration fails cleanly with nothing dropped and can be retried. CONCURRENTLY alternative, run
-- outside a transaction (ledger row inserted separately):
--   drop index concurrently if exists core.idx_fact_unit_id;
-- Rollback (use CONCURRENTLY, slow on a 30 GB table):
--   create index concurrently idx_fact_unit_id on core.fact (unit_id);

set local lock_timeout = '5s';

drop index if exists core.idx_fact_unit_id;
