-- Persists resolve_primary_tickers()'s output onto core.company directly,
-- instead of every consumer (sanity/yfinance_check.py, yfinance_financials/
-- fetch.py, company_master/yfinance_industry.py) recomputing it from
-- core.listing on every single run. Added 2026-09-20, direct user request:
-- "map all companies with ticker" + "mark boolean or something" for active
-- companies.
--
-- primary_ticker_status follows the SAME 3-value convention as y_industry_
-- status (ok/not_found/no_data): 'resolved' when a real primary ticker was
-- found, 'no_ticker' when resolve_primary_tickers() genuinely returned
-- nothing for this company (SEC has no classifiable common-stock/ADR/REIT/
-- MLP/tracking-stock/LP-unit listing for it -- almost always a pre-merger
-- SPAC shell or a wholly-owned subsidiary with only debt/preferred
-- securities registered, not a mapping bug -- see company_master/
-- security_type.py's own module docstring). primary_ticker IS NOT NULL is
-- the boolean the user asked for -- no separate column needed, since a
-- status text column already carries strictly more information (WHY a
-- company has none) than a bare boolean would.
alter table core.company
    add column if not exists primary_ticker text,
    add column if not exists primary_ticker_status text,
    add column if not exists primary_ticker_updated_at timestamptz;

create index if not exists idx_company_primary_ticker on core.company (primary_ticker) where primary_ticker is not null;
