-- Market-price schema (doc 13, Part 4b). Deliberately minimal -- EOD close
-- only, matching doc 02's "no real-time promise" default.
--
-- Built ahead of a real vendor decision (doc 02, still open) using MOCK
-- data to unblock the pipeline's shape -- NOT a resolution of that
-- decision. `is_mock` is a hard boolean, not just a string convention on
-- `source`, specifically so a future query can't accidentally treat mock
-- rows as real by a spelling mistake or a missed filter. Every mock row
-- must have is_mock=true and source='mock' -- never a fake vendor name
-- that could be confused with a real one later. This table must be
-- cleared (not just appended to) before any real vendor data lands in it.

create table if not exists core.market_price (
    id          bigint generated always as identity primary key,
    company_id  bigint not null references core.company (id),
    price_date  date not null,
    close_price numeric not null,
    currency    text not null default 'USD',
    source      text not null,
    is_mock     boolean not null,
    fetched_at  timestamptz not null default now(),
    unique (company_id, price_date)
);

create index if not exists idx_market_price_company_date on core.market_price (company_id, price_date);
