-- Institutional Ownership QoQ summary (doc scoping/insider_info.md's
-- Ownership page spec). Extends core, same identity-adjacent home as
-- institutional_ownership (0010) -- this is presentation-shaped derived
-- data over that table (holder counts, new/exited positions, top-10),
-- not a financial-statement metric, so it stays out of `analytics`.
--
-- One row per company holding the CURRENT "latest two report_periods"
-- comparison -- recomputed and overwritten each run (unique on
-- company_id, upserted), not an append-only history table. If a genuine
-- multi-quarter trend view is ever built, that's a new table, not this
-- one growing a period dimension -- doc 05's "no premature abstraction."
--
-- top_holders is JSONB (one array element per holder: filer_name,
-- filer_cik, shares, value_usd, ownership_pct, share_change,
-- pct_change, status, report_period) -- same "structured payload in a
-- JSONB column" precedent already used for app.saved_screen's
-- ScreenQuery, chosen here because a fixed-width top-10 list of
-- multi-field rows has no other natural relational shape without a
-- second child table for what's fundamentally one snapshot's display
-- data.
create table if not exists core.institutional_ownership_summary (
    id                             bigint generated always as identity primary key,
    company_id                     bigint not null references core.company (id) unique,
    report_period_latest           date not null,
    report_period_prior            date not null,
    total_institutional_pct        numeric,
    total_institutional_pct_prior  numeric,
    qoq_change_pct                 numeric,
    total_holders                  int not null,
    holders_increased              int not null,
    holders_decreased              int not null,
    new_positions                  int not null,
    exited_positions               int not null,
    top_holders                    jsonb not null,
    computed_at                    timestamptz not null default now()
);
