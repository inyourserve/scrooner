-- Time-series self-consistency check (2026-09-08, doc "what more can we do"
-- follow-on, explicit user direction: "time-series self-consistency
-- detector"). Genuinely different from every other check built today --
-- zero external API calls, zero external source at all. Compares a
-- company's own value for a period against its OWN value for the SAME
-- fiscal_period one year earlier (fiscal-calendar-aware, not calendar-
-- date-aware -- correctly handles a non-calendar fiscal year the same
-- way ttm.py/calculate.py's own YoY growth metrics already do).
--
-- Catches a class of bug NOTHING else built today can: a value that's
-- internally wrong (e.g. a unit-scaling error) but happens to look
-- plausible in isolation would sail past both yfinance (which only sees
-- the LATEST period) and even the SEC Frames checker (which only proves
-- "we copied the chosen tag's value correctly" -- if the wrong VALUE was
-- itself what SEC served, Frames agrees with us and is silent). A wild,
-- multi-year-implausible swing in a company's own history is a real,
-- free signal neither of those can produce.
--
-- Two distinct signals: a YoY ratio implausible relative to the
-- company's own history (`outlier`), and an absolute sign violation for
-- concepts that structurally can never be negative regardless of
-- history (`sign_violation` -- e.g. total_assets, cash, revenue).

create table if not exists analytics.timeseries_outlier_check (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    period_id bigint not null references core.period(id),
    period_end date not null,
    fiscal_year integer not null,
    fiscal_period text not null,
    current_value numeric not null,
    prior_value numeric,
    prior_period_end date,
    yoy_ratio numeric,
    severity text not null check (severity in ('ok', 'outlier', 'sign_violation')),
    checked_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id, period_id)
);

create index if not exists idx_timeseries_outlier_check_severity on analytics.timeseries_outlier_check (severity) where severity <> 'ok';
