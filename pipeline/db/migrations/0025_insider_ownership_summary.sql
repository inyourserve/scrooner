-- Insider Ownership & Transactions aggregate summary (doc/scoping/insider_info.md).
-- Pure computation over the already-fully-populated core.insider_transaction
-- (Form 4, last 12 months, ~5,160 companies) -- no new SEC fetches. Lives in
-- `core`, same schema as core.insider_transaction itself (identity-adjacent,
-- not analytics) -- a precomputed table refreshed by a batch job
-- (ownership/insider_summary.py), not a view: a live company-page load
-- recomputing 3 rolling-window aggregates per request across a 500K+-row
-- table is real query cost every page view doesn't need to pay when the
-- underlying Form 4 data only changes as often as this job reruns.

-- One row per company: the current, non-windowed insider ownership %.
-- Numerator is the sum of shares_owned_following from each unique reporting
-- owner's OWN most recent transaction (not summed across all their
-- transactions -- shares_owned_following is already a running post-
-- transaction balance, so summing every row would double/triple count).
-- Denominator reuses mapper/price_metrics.py's exact shares_outstanding
-- resolution (instant fact + cover-page fallback) so this can never
-- silently disagree with how shares_outstanding is resolved elsewhere
-- (doc's own explicit requirement).
create table if not exists core.insider_ownership_summary (
    company_id                  bigint primary key references core.company (id),
    ownership_pct               numeric,
    shares_owned_by_insiders    numeric,
    shares_outstanding          numeric,
    distinct_insiders_count     int not null default 0,
    is_null_reason              text,
    computed_at                 timestamptz not null default now()
);

-- One row per (company, window). window_months in (3, 6, 12) per doc's
-- three required rolling summaries. shares_bought/sold, dollar volumes, and
-- insider counts are always non-null (0 is a real, meaningful answer when
-- a company has Form 4 data for the period but no matching transactions --
-- distinct from "we don't know", which never applies here since the
-- underlying data already covers the full 12-month window for every company
-- in this table). Largest purchase/sale fields are genuinely NULL when no
-- open-market transaction of that side exists in the window -- a real
-- absence, not a missing-data gap.
create table if not exists core.insider_window_summary (
    id                          bigint generated always as identity primary key,
    company_id                  bigint not null references core.company (id),
    window_months               smallint not null check (window_months in (3, 6, 12)),
    shares_bought                numeric not null default 0,
    shares_sold                  numeric not null default 0,
    buy_dollar_volume            numeric not null default 0,
    sell_dollar_volume           numeric not null default 0,
    insiders_buying_count        int not null default 0,
    insiders_selling_count       int not null default 0,
    largest_purchase_owner_name  text,
    largest_purchase_date        date,
    largest_purchase_shares      numeric,
    largest_purchase_price       numeric,
    largest_purchase_value       numeric,
    largest_sale_owner_name      text,
    largest_sale_date            date,
    largest_sale_shares          numeric,
    largest_sale_price           numeric,
    largest_sale_value           numeric,
    computed_at                  timestamptz not null default now(),
    unique (company_id, window_months)
);
create index if not exists idx_insider_window_summary_company on core.insider_window_summary (company_id);
