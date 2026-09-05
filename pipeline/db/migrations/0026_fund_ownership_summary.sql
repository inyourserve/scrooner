-- Mutual Fund Ownership QoQ summary (doc/scoping/insider_info.md's
-- Ownership page spec, Mutual Fund Ownership subsection). Same shape and
-- rationale as 0024_institutional_ownership_summary.sql's twin table for
-- Form 13F -- consumes core.fund_ownership's now-two-window data
-- (ownership/mutual_fund.py) and computes, per company, the comparison
-- between its two most recent report_periods: total mutual fund
-- ownership %, change, fund counts, increased/decreased/new/exited, and
-- a Top 10 holders table.
--
-- Lives in `core`, not `analytics` -- same reasoning as
-- institutional_ownership_summary: this is ownership-identity-adjacent
-- presentation data (a Top Holders table, fund counts), not one of doc
-- 02's locked financial-statement metrics.
--
-- One row per company for the CURRENT "latest two report_periods"
-- comparison -- recomputed and overwritten each run (unique on
-- company_id), not an append-only history table, same "no premature
-- abstraction" precedent as the institutional twin.
--
-- Never combined with total_institutional_pct anywhere -- doc's explicit
-- rule that institutional and mutual-fund ownership percentages must
-- never be summed (a mutual fund can appear via both its own N-PORT
-- filing and its manager's separate 13F filing).
--
-- top_holders is JSONB (one array element per fund: fund_name,
-- fund_cik, series_id, fund_family [always null -- see
-- mutual_fund_summary.py's own docstring on this real, uncaptured data
-- gap], shares, value_usd, ownership_pct, portfolio_weight_pct
-- [FUND_REPORTED_HOLDING.PERCENTAGE, "when available" per the product
-- spec -- null whenever N-PORT itself didn't report one], share_change,
-- pct_change, status, report_period) -- same "structured payload in a
-- JSONB column" precedent as the institutional twin's own top_holders.
create table if not exists core.fund_ownership_summary (
    id                          bigint generated always as identity primary key,
    company_id                  bigint not null references core.company (id) unique,
    report_period_latest        date not null,
    report_period_prior         date not null,
    total_fund_ownership_pct    numeric,
    total_fund_ownership_pct_prior numeric,
    change_in_pct               numeric,
    total_funds_holding         int not null,
    funds_increasing            int not null,
    funds_decreasing            int not null,
    new_positions               int not null,
    exited_positions            int not null,
    top_holders                 jsonb not null,
    computed_at                 timestamptz not null default now()
);
