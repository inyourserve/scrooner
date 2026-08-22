-- Missing index found live 2026-08-22 while investigating why the
-- 100-company pilot's Normalizer restatement-linking stage was running
-- extremely slowly (10-23 SECOND individual queries, confirmed via
-- Supabase's own query logs) and correlated with repeated connection
-- drops. normalizer/restatements.py joins core.fact to itself, matching
-- an amending filing's facts against the filing it amends, filtered by
-- filing_id on each side -- but core.fact had no index with filing_id as
-- a usable leading column (only a 5-column composite key with filing_id
-- LAST, and a company/concept/period index that doesn't include it at
-- all). Also independently flagged by Supabase's own performance
-- advisor ("fact_filing_id_fkey... without a covering index").
--
-- Verified live before/after: EXPLAIN on the exact slow query dropped
-- from a Nested Loop plan (cost=0.86..51998.41) to a Hash Join using
-- this index (cost=330.51..656.61) -- roughly 80x cheaper, and the
-- planner switches from full-range index scanning to a direct lookup.

create index if not exists idx_fact_filing_id on core.fact (filing_id);
