-- Real security-type classification for core.listing (doc 25 follow-up,
-- 2026-08-17). Replaces the golden_companies.json curated-ticker
-- stopgap market_price_alpaca.py originally used to resolve "the"
-- primary ticker -- SEC's own submissions.json carries no security-type
-- field at all (checked live: `tickers`/`exchanges` are the only
-- per-ticker arrays, nothing else), so this is sourced from OpenFIGI
-- instead (free, unauthenticated, already used for Ownership Stage 4's
-- CUSIP crosswalk) -- explicitly NOT Alpaca, by direction, to keep the
-- price vendor's role scoped to price only.
--
-- security_type stores OpenFIGI's own raw `securityType` string
-- verbatim ("Common Stock", "ADR", "ETP", "CDI", etc.) -- never
-- reinterpreted, same "store what the source says" discipline as
-- everywhere else in this project. NULL means unclassified (no
-- OpenFIGI match), not "confirmed not primary" -- many OTC/preferred
-- tickers have no OpenFIGI coverage at all under a plain US exchCode
-- query; absence of a match is inconclusive, never treated as a
-- negative signal.
alter table core.listing add column if not exists security_type text;
alter table core.listing add column if not exists security_type_source text;
