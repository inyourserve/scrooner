-- Wide, one-row-per-company screening snapshot (2026-09-20), replacing
-- migration 0061's EAV shape (company_id, metric_definition_id, value).
--
-- Measured live before changing anything: a realistic 3-predicate boolean
-- screen ((roe > 15% AND debt/equity < 1) OR pe < 20) cost 70ms server-side
-- via EXPLAIN ANALYZE against the EAV table -- three separate Bitmap Heap
-- Scans (one per predicate, ~1,100-2,300 heap pages each) against a
-- 384,640-row table, for a universe of only 5,282 companies.
--
-- A first attempt at this migration used a single `metrics jsonb` column
-- (one row per company, all 82 metrics packed into one blob) -- REJECTED
-- after measuring it live: a single-predicate filter against that blob
-- cost 107ms with 13,513 buffer touches (~2.6 per row) just to decompress
-- and parse a ~2.4KB TOASTed JSONB value on every row of a full scan, and
-- the full 3-predicate query cost 214-225ms -- WORSE than the EAV table
-- it was meant to replace. Packing every metric into one blob means every
-- query pays to decompress/parse all 82 of them even when it only needs 1-3.
--
-- Fixed by giving each metric_definition its own native columns instead:
-- "<metric_name>" numeric (the value), "<metric_name>__period_label" text,
-- "<metric_name>__period_end" date, "<metric_name>__formula_version" int.
-- Verified live before committing to this shape: the identical single-
-- predicate filter dropped to 6.1ms with 582 buffer touches -- an 17-37x
-- improvement over both the JSONB attempt and the original EAV table.
--
-- This still resolves 0061's own original reason for choosing EAV in the
-- first place ("a wide table needs a schema migration every time a new
-- metric_definition lands, and this project adds one every few days"):
-- `screener/snapshot.py`'s `_ensure_metric_columns()` runs `ALTER TABLE
-- ... ADD COLUMN IF NOT EXISTS` for every active metric on every rebuild,
-- automatically, before inserting -- adding a nullable column with no
-- default is a fast, metadata-only operation in Postgres (no table
-- rewrite), so a new metric_definition needs zero manual migration, just
-- like the JSONB design would have, but without the parse-cost tax.
--
-- Only the identity columns are declared here; the per-metric columns
-- are added dynamically at runtime by build_snapshot() and are NOT
-- tracked by any versioned migration -- this is intentional, not schema
-- drift. `\d analytics.company_screening_snapshot` will show more columns
-- than this file declares once a snapshot has been built at least once.

drop table if exists analytics.company_screening_snapshot;

create table analytics.company_screening_snapshot (
    company_id       bigint  primary key references core.company (id),
    cik              text    not null,
    company_name     text    not null,
    sic_code         text,
    sic_description  text,
    sector           text,
    -- Nullable, matching core.company.status itself (checked live: at
    -- least one real company has status=NULL) -- treated identically to
    -- any other non-'active' value everywhere this is read (Python's
    -- `!= "active"` and SQL's `= 'active'` both correctly exclude NULL).
    status           text,
    ticker           text,
    dataset_version  bigint  not null
);

-- The Screener's own status filter (`and status = 'active'` unless a
-- query opts into `include_inactive`) applies to almost every request.
create index idx_screening_snapshot_status on analytics.company_screening_snapshot (status);
