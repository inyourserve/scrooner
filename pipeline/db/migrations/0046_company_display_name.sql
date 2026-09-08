-- Clean display name for companies whose core.company.company_name carries a
-- raw SEC EDGAR artifact suffix -- e.g. "COSTCO WHOLESALE CORP /NEW",
-- "TUCOWS INC /PA/" (EDGAR appends a state-of-incorporation or "/NEW" tag to
-- disambiguate a re-registered entity from an older CIK of the same name).
-- Found live 2026-09-07: 140 active companies carry this pattern. Kept
-- strictly separate from core.company.company_name (the SEC source of
-- truth, never overwritten) -- same "new column, never overwrite the
-- authoritative field" discipline as y_sector/y_industry and y_about_text/
-- y_website. See company_master/display_name.py.

alter table core.company add column if not exists display_name text;
alter table core.company add column if not exists display_name_source text;
alter table core.company add column if not exists display_name_updated_at timestamptz;

comment on column core.company.display_name is 'Clean company name for UI display -- prefers yfinance longName/shortName, then OpenFIGI name, then a deterministic EDGAR-suffix strip of company_name. Never the sole source of truth: company_name remains authoritative.';
comment on column core.company.display_name_source is 'yfinance | openfigi | suffix_stripped -- which source produced display_name, for traceability.';
