-- 2026-09-14/15: doc 21's "Stock splits: raw data exists, unmapped" item,
-- finally built. StockholdersEquityNoteStockSplitConversionRatio(1) sits
-- in core.fact as a captured-but-unmapped tag -- checked live before
-- trusting it: 97.3% of real candidate facts (2,945 of 3,028) parse as a
-- plausible raw ratio (2, 0.1, 1.5, 10, etc. -- exactly what real split/
-- reverse-split ratios look like), confirmed independently against KLA
-- Corp's real 10-for-1 split (already proven from conflicting EPS values
-- the same week). A small minority need a scale correction (some filers
-- report the ratio x1000/x10000) or get rejected outright (negative or
-- wildly implausible values -- likely a different real concept, a
-- convertible-security conversion ratio, sharing the same tag name).
--
-- This is a discrete corporate-action EVENT record (like
-- core.company_name_history/core.listing's ticker-change tracking), not a
-- financial metric -- deliberately NOT a canonical_concept/canonical_fact
-- row. `ratio` follows the SEC element's own definition: new shares issued
-- per old share (2 = 2-for-1 forward split, 0.1 = 1-for-10 reverse split).
-- source_fact_id keeps this traceable to the exact filing it came from,
-- per doc 01's trust principle -- this table only ever RECORDS a detected
-- event, it does not itself adjust or fabricate any historical value.
create table if not exists analytics.company_stock_split (
    id bigint generated always as identity primary key,
    company_id integer not null references core.company(id),
    effective_date date not null,
    ratio numeric not null,
    raw_value numeric not null,
    scale_correction integer not null default 1,
    source_fact_id bigint not null references core.fact(id),
    source_tag text not null,
    detected_at timestamptz not null default now(),
    unique (company_id, effective_date)
);
create index if not exists idx_company_stock_split_company on analytics.company_stock_split (company_id);
