-- yfinance About Text / Website columns, extending the same fetch as
-- migration 0044 (y_sector/y_industry) -- yf.Ticker().get_info() already
-- returns longBusinessSummary/website in the SAME payload, so this reuses
-- that one fetch rather than doubling requests against Yahoo's own
-- tightly-rate-limited unofficial endpoint. Explicit user direction
-- 2026-09-06: use yfinance for About Text and Company Website.
--
-- Kept SEPARATE from core.company.about_text/website (the existing,
-- SEC-10-K-prose-sourced fields, company_master/business_text.py) --
-- same "two independent, traceable sources, never merged silently"
-- discipline as y_sector/y_industry vs. sector/sector_reason. Reuses
-- y_industry_status/y_industry_updated_at for resumability (one fetch,
-- one status -- these two new fields succeed/fail together with
-- sector/industry since they all come from the same get_info() call).

alter table core.company add column if not exists y_about_text text;
alter table core.company add column if not exists y_website text;

comment on column core.company.y_about_text is 'Yahoo Finance longBusinessSummary via yfinance (unofficial, ToS personal-use data) -- kept separate from the SEC-10-K-sourced about_text column. See company_master/yfinance_industry.py.';
comment on column core.company.y_website is 'Yahoo Finance website via yfinance -- kept separate from the SEC-sourced website column (which has much lower coverage, ~9% vs. yfinance''s typical near-complete coverage for real tickers).';
