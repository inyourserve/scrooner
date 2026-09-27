-- 2026-09-21: companion to 0070 -- the 5 flagged unindexed foreign keys
-- that live on the two largest, actively-written tables in the database
-- (core.fact, 27 GB and growing daily via the Collector/Normalizer cron;
-- analytics.canonical_fact, 3.6 GB). A plain CREATE INDEX takes a SHARE
-- lock for the full build duration, which would block every write to
-- core.fact for however long a multi-GB index build takes -- a real risk
-- of colliding with a live pipeline run, unlike 0070's small tables.
--
-- CREATE INDEX CONCURRENTLY avoids that (no blocking of reads/writes,
-- just a brief final lock) but CANNOT run inside a transaction block --
-- so these must be applied one statement at a time, outside any
-- transaction wrapper, never bundled into a single multi-statement
-- migration the way 0070 is. Recorded here for history/documentation;
-- applied live via individual statements, not this file as a unit.
create index concurrently if not exists idx_fact_period_id
  on core.fact (period_id);
create index concurrently if not exists idx_fact_raw_object_id
  on core.fact (raw_object_id);
create index concurrently if not exists idx_fact_supersedes_fact_id
  on core.fact (supersedes_fact_id);
create index concurrently if not exists idx_fact_unit_id
  on core.fact (unit_id);
create index concurrently if not exists idx_canonical_fact_period_id
  on analytics.canonical_fact (period_id);
