-- Found live 2026-09-02 building the XBRL tag-coverage research script
-- (doc 40): core.fact has no index with concept_id as a leading column
-- -- only a 5-column composite unique key with concept_id second, the
-- exact same indexing-gap shape already found and fixed once for
-- filing_id (migration 0019) and again for institutional/fund ownership
-- (migration 0029). A `count(distinct company_id) from core.fact where
-- concept_id = %s` (needed for any per-concept coverage check, not just
-- this research script) never completed inside a 2-minute window without
-- this index, against a ~67M-row table.

-- CONCURRENTLY: core.fact is ~67M rows and potentially still written to
-- by other pipeline jobs -- a plain CREATE INDEX would hold a lock
-- blocking writes for the build's full duration. Cannot run inside an
-- explicit transaction block (apply this statement standalone, not via
-- `psql -f` wrapped in BEGIN/COMMIT).
create index concurrently if not exists idx_fact_concept_id
    on core.fact (concept_id) where is_authoritative = true;

-- Same gap, found immediately after fixing the one above (2026-09-02):
-- analytics.canonical_fact has only a composite unique key with
-- canonical_concept_id second, not a leading index -- a per-concept
-- `count(distinct company_id) where canonical_concept_id = X` (the most
-- basic "how many companies have this concept" query, run by hand
-- throughout this session and now by the tag-coverage-library script)
-- took 9+ seconds per call without this.
create index concurrently if not exists idx_canonical_fact_concept_id
    on analytics.canonical_fact (canonical_concept_id);
