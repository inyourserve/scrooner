-- 2026-09-15: two missing indexes found investigating "why is the stock
-- page still slow, even cached" -- EXPLAIN ANALYZE on a real but
-- previously-uncached ticker (not a popular one already warm in
-- shared_buffers) showed two full sequential scans on the SAME query,
-- every single page load:
--
-- 1. core.listing has no index usable for a ticker lookup -- only a
--    UNIQUE(company_id, ticker) constraint, useless when the ticker is
--    the known value and company_id isn't. Every `lower(l.ticker) =
--    lower($1)` query in apps/app/lib/company/db.ts (the company page
--    itself, plus ticker search/directory autocomplete) was doing a full
--    Seq Scan of the whole table just to find one row (confirmed live:
--    "Seq Scan on listing l ... Rows Removed by Filter: 6993").
-- 2. core.company has no index on y_industry, the peer-comparison join
--    key (same file's peer_companies CTE, doc 22/28's yfinance-industry
--    peer matching) -- a full Seq Scan of every active company on every
--    single stock page load, just to find others sharing the same
--    industry ("Seq Scan on company ... Filter: status = 'active' ...
--    Rows Removed by Filter: 66").
--
-- Both tables are small today (~7K/~5K rows, low single-digit ms each in
-- isolation) so this was invisible under repeat testing against a handful
-- of popular tickers already sitting in Postgres's shared_buffers -- but
-- both are on the single hottest read path in the whole app (every page
-- load, every search keystroke) and both costs grow linearly with a
-- universe this project intends to keep growing. Fixed now, while cheap,
-- rather than after it becomes a real, harder-to-diagnose slowdown.
create index if not exists idx_listing_lower_ticker on core.listing (lower(ticker));
create index if not exists idx_company_y_industry_active on core.company (y_industry) where status = 'active';

-- A third, more serious flaw, found by rechecking a LARGE company (AAPL)
-- rather than only small ones -- the fixes above made small/obscure
-- tickers fast (VITL: 861ms -> 82ms) but AAPL got WORSE (207ms warm ->
-- 8,767ms on a cold buffer cache), which looked like a regression until
-- EXPLAIN pinned it to a single, unrelated, pre-existing node:
--   Index Scan using idx_institutional_ownership_company_source ...
--   (actual time=3.274..8205.465 rows=18962 loops=1)
-- The "Institutional holders" disclosure list (apps/app/lib/company/db.ts)
-- dedupes core.institutional_ownership per filer_name (a filer can file
-- multiple INFOTABLE rows for one security, doc 19), which needs every
-- row for the company sorted by (filer_name, is_amendment desc,
-- filing_date desc) before the top-15-by-shares limit can apply. The
-- existing idx_institutional_ownership_company_source index covers
-- (company_id, source_zip) but not filer_name/is_amendment/filing_date,
-- so Postgres had to heap-fetch every one of AAPL's 18,962 rows
-- individually (~0.43ms/row -- consistent with random I/O against a
-- 1.8GB table on network-attached storage, not a planner mistake) just
-- to sort them. A large, heavily-held company (AAPL) has orders of
-- magnitude more institutional_ownership rows than a small one (VITL),
-- so this was invisible in every earlier test that only used small/
-- popular-but-cache-warm tickers.
--
-- A covering index matching the dedup subquery's own ORDER BY, with the
-- selected non-key columns as INCLUDE, turns this into a single
-- sequential Index Only Scan (no heap access, no separate Sort step) --
-- verified live: 8,767ms -> 187ms (47x) on the very next run, the
-- Institutional-ownership node itself 8,205ms -> 18ms (450x).
create index if not exists idx_institutional_ownership_dedup
  on core.institutional_ownership (company_id, filer_name, is_amendment desc, filing_date desc nulls last)
  include (shares, value_usd);
