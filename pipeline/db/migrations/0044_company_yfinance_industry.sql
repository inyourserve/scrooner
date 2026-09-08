-- yfinance sector/industry columns, separate from core.company.sector/
-- sector_reason (the SIC-range-derived taxonomy, company_master/sector_bucket.py).
-- Explicit user direction 2026-09-06 to store yfinance's own classification as a
-- real, persisted, production-facing field per company -- a deliberate reversal
-- of doc/planning/y-finance.md's original "never store, dev-tool only" stance;
-- see doc 02's decision register for the superseding entry and
-- company_master/yfinance_industry.py for the fetch/backfill job.
--
-- y_industry_status distinguishes "fetched, no data" (Yahoo has no
-- classification for this ticker -- a real, valid outcome) from "not attempted
-- yet" / "attempt failed" (rate-limited, ticker not found, transient error) so a
-- resumable backfill job knows what to retry vs. what to leave alone.

alter table core.company add column if not exists y_sector text;
alter table core.company add column if not exists y_industry text;
alter table core.company add column if not exists y_industry_status text;
alter table core.company add column if not exists y_industry_updated_at timestamptz;

comment on column core.company.y_sector is 'Yahoo Finance sector via yfinance (unofficial, ToS personal-use data) -- reference/production field per explicit 2026-09-06 direction, kept separate from the SIC-derived sector column.';
comment on column core.company.y_industry is 'Yahoo Finance industry via yfinance -- finer-grained than y_sector, see company_master/yfinance_industry.py.';
comment on column core.company.y_industry_status is 'ok | no_data | not_found | error -- lets the backfill job resume without re-fetching successes.';
