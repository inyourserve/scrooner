-- Mutual fund / ETF holdings via SEC Form N-PORT bulk data set (doc 21
-- Sec 1). Same conceptual home and CUSIP-matching mechanism as Stage 4's
-- Form 13F (0010_institutional_ownership_schema.sql) -- N-PORT is filed
-- by registered investment companies/ETFs specifically (a narrower,
-- purer "fund" universe than 13F's broad "institutional manager"
-- definition), matched the identical way: FUND_REPORTED_HOLDING.ISSUER_CUSIP
-- against a golden company's own CUSIP, already captured in
-- core.beneficial_ownership.cusip (doc 19 Stage 3/4) -- no new crosswalk
-- problem.

-- One row per N-PORT FUND_REPORTED_HOLDING line item whose ISSUER_CUSIP
-- matches a golden company's own. Deliberately NOT one row per company --
-- shares/value legitimately vary per fund, and each row traces to its own
-- accession_number (doc 04's "every number traces to source" requirement),
-- same granularity precedent as institutional_ownership.
--
-- Scoped to golden-company CUSIP matches only, from a single most-recent
-- bulk window (a snapshot, not a multi-quarter trend) -- same free-tier
-- capacity discipline as institutional_ownership; the full N-PORT
-- universe would blow the budget the same way an unscoped 13F load would.
create table if not exists core.fund_ownership (
    id                      bigint generated always as identity primary key,
    company_id              bigint not null references core.company (id),
    accession_number        text not null,
    holding_id              bigint not null,
    -- The specific named fund (N-PORT's FUND_REPORTED_INFO.SERIES_NAME),
    -- NOT the umbrella trust registrant -- found live 2026-08-28: a
    -- registrant filer (REGISTRANT.REGISTRANT_NAME, e.g. "MFS SERIES
    -- TRUST X") is the legal entity that files, but the actual fund an
    -- investor would recognize (e.g. "MFS International Growth Fund") is
    -- one of potentially several *series* under that trust, named only in
    -- FUND_REPORTED_INFO. Falls back to registrant_name on the rare
    -- filing with no series row rather than leaving it null.
    fund_name               text not null,
    fund_cik                text,
    series_id               text,
    shares                  numeric,
    -- Raw as-reported value in the fund's own reporting currency --
    -- CURRENCY_VALUE is USD for the large majority of matched rows but
    -- NOT always (found live: ~2% of real golden-10 matches report in
    -- CAD/TWD for foreign-domiciled holdings, e.g. TSMC's Taiwan-listed
    -- ordinary shares). Keep the raw figure so nothing is lost even when
    -- value_usd below is null.
    currency_code           text not null,
    currency_value          numeric,
    -- Populated ONLY when currency_code = 'USD' (a direct passthrough,
    -- never a computed conversion) -- same "leave null, never guess"
    -- discipline as everywhere else in this project (see
    -- pipeline/CLAUDE.md's Form 13F VALUE-field $242T incident). An
    -- EXCHANGE_RATE field exists on non-USD rows but its multiply-vs-
    -- divide convention was not confirmed against a second independent
    -- source before this was built, so no conversion is attempted here.
    value_usd               numeric,
    -- N-PORT reports this directly (FUND_REPORTED_HOLDING.PERCENTAGE,
    -- "percentage value compared to net assets of the Fund", per SEC's
    -- own nport_readme.htm field-layout table) -- Form 13F has no
    -- equivalent field, so this column doesn't exist on
    -- core.institutional_ownership.
    pct_of_fund_net_assets  numeric,
    report_period           date,
    filing_date             date,
    is_amendment            boolean not null default false,
    source_zip              text not null,
    created_at              timestamptz not null default now(),
    unique (accession_number, holding_id)
);
create index if not exists idx_fund_ownership_company on core.fund_ownership (company_id, shares desc);

-- Lightweight provenance for the bulk N-PORT zip itself, mirroring
-- raw.sec_13f_bulk_fetch's shape -- a genuinely new SEC discovery fetch
-- (N-PORT is filed *about* fund portfolios, never appears in a golden
-- company's own raw.sec_submissions), so it gets its own audit row.
create table if not exists raw.sec_nport_bulk_fetch (
    id                  bigint generated always as identity primary key,
    source_url          text not null,
    window_label        text not null,
    sha256              text not null,
    fetched_at          timestamptz not null default now(),
    holding_row_count   bigint,
    matched_row_count   bigint,
    unique (window_label)
);
