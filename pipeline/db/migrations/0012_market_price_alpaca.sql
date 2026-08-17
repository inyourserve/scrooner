-- Real market-price ingestion (doc 25) -- Alpaca Markets, resolved doc 02
-- 2026-08-17. Deliberately a SEPARATE table from core.market_price
-- (0006, mock data only, doc 13 Part 4b) rather than reusing it with a
-- flag -- explicit user direction, and a stronger isolation guarantee
-- than a boolean: mock and real data can never land in the same table
-- at all, let alone the same row.
--
-- feed = 'delayed_sip' (not the free-tier default 'iex'), by explicit
-- choice -- confirmed live 2026-08-17: delayed_sip is the FULL
-- consolidated tape (trade counts 10-70x higher than iex in a live
-- side-by-side check), ~15-16 minutes delayed (confirmed by comparing
-- the returned bar's own timestamp to request time), available on the
-- free/Basic tier with no separate subscription. For a fundamental
-- screener (not a trading terminal), accurate-but-delayed full-market
-- data is a better fit than real-time-but-single-exchange IEX data.
--
-- One row per (company, price_date) -- the "latest bars" endpoint only
-- ever gives the most recent bar, so a natural daily history accumulates
-- for free as the once-daily refresh job runs, same shape precedent as
-- core.market_price's own (company_id, price_date) uniqueness.
create table if not exists core.market_price_alpaca (
    id            bigint generated always as identity primary key,
    company_id    bigint not null references core.company (id),
    symbol        text not null,
    price_date    date not null,
    price         numeric not null,
    -- The bar's own timestamp from Alpaca, NOT fetched_at -- this is
    -- what actually proves data recency/the real ~15min delay, the same
    -- "every number shows its own data date" discipline as everywhere
    -- else in this project.
    bar_timestamp timestamptz not null,
    feed          text not null default 'delayed_sip',
    currency      text not null default 'USD',
    fetched_at    timestamptz not null default now(),
    unique (company_id, price_date)
);
create index if not exists idx_market_price_alpaca_company_date on core.market_price_alpaca (company_id, price_date desc);
