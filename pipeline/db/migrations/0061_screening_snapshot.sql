-- Screener performance fix (doc/faster-loading/fast.md, 2026-09-10).
--
-- Root cause, measured live before building anything (not assumed from
-- fast.md's own guess of "recomputing from raw filing tables" -- that
-- guess was wrong, see doc/learnings/2026-09-10-screener-performance.md):
-- a real ROE screen took 13.9s end-to-end. EXPLAIN ANALYZE on the exact
-- query `screener/resolve.py` runs showed the actual cost is a Bitmap
-- Heap Scan against `analytics.metric_value` (11M rows across 82
-- metrics) touching ~16,000 COLD heap pages to pull out the ~205K raw
-- rows for just one metric, because rows for one metric_definition_id
-- are scattered across the whole table's physical storage, not because
-- the query itself is unindexed (idx_metric_value_metric_definition_id
-- already exists, added 2026-08-22) or because of raw-table joins.
--
-- Fix: precompute the "most recent value per company per metric"
-- resolution (screener/resolve.py's own row_number()-over-TTM-preferred
-- logic) ONCE, offline, into a small, densely-packed table -- so a
-- request-time screen never touches metric_value at all. This is the
-- same "serve from a small dedicated table" idea fast.md's item 1
-- describes, kept intentionally narrow (EAV: one row per company per
-- metric) rather than one-column-per-metric, since this project adds a
-- new metric_definition every few days (see pipeline/CLAUDE.md's own
-- changelog) and a wide table would need a schema migration each time --
-- narrow keeps the compiler in query.py (AND/OR/NOT tree -> EXISTS
-- subqueries per leaf) simple regardless of how many metrics exist.

-- Single-row version counter. Bumped by every full snapshot rebuild.
-- Doubles as fast.md's "dataset_version" for cache-key invalidation --
-- the Redis cache below never needs a TTL-based invalidation path,
-- since a query hash bakes in the version and a rebuild naturally mints
-- new keys.
create table if not exists analytics.screening_dataset_version (
    id         boolean primary key default true check (id),
    version    bigint not null default 0,
    updated_at timestamptz not null default now()
);

insert into analytics.screening_dataset_version (id, version)
values (true, 0)
on conflict (id) do nothing;

create table if not exists analytics.company_screening_snapshot (
    company_id           bigint  not null references core.company (id),
    metric_definition_id bigint  not null references analytics.metric_definition (id),
    value                numeric,
    period_label         text,
    period_end           date,
    formula_version      integer,
    dataset_version      bigint  not null,
    primary key (company_id, metric_definition_id)
);

-- The Screener's actual predicate shape is always "one metric, compared
-- against a value" -- this is the index every compiled EXISTS leaf hits.
create index if not exists idx_screening_snapshot_metric_value
    on analytics.company_screening_snapshot (metric_definition_id, value);

-- Reverse lookup: assembling the citation payload for a matched company's
-- full result row (every predicate + sort_by metric it has data for).
create index if not exists idx_screening_snapshot_company
    on analytics.company_screening_snapshot (company_id);
