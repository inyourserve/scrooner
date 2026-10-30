-- WO-22 / WO-2 item 6 split basis, ticket SB-1 (2026-10-22, Period Engineer).
-- SCHEMA ONLY: creates two EMPTY tables. Backfills nothing, changes no
-- existing table, row or value, and nothing on main reads or writes them yet.
-- Writer and readers come later (tickets SB-2..SB-8, data-team/strategy/team/
-- WO2-split-basis-tickets.md; design WO-REVIEW-period-engineer.md section 2).
-- Not applied by its author.
--
-- down: drop table if exists analytics.filing_share_basis;
--       drop table if exists analytics.split_event;
--
-- 1. analytics.split_event: one row per ECONOMIC split event (identity =
--    ratio + basis boundary, never a day window: GOOG 20:1 is in
--    company_stock_split twice, 0001652044-23-000016 R10/R5). company_stock_split
--    stays as the raw disclosure log. ratio = new shares per old share
--    (4 for AAPL 4:1, 0.025 for a 1-for-40 reverse). basis_date = first date
--    from which filings report on the new basis. evidence holds the fact ids,
--    accessions and locators per evidence kind. 'confirmed' needs at least two
--    evidence kinds (the CHECK counts array entries; the writer must not repeat
--    a kind); 'review' events never re-base a value.
--
-- 2. analytics.filing_share_basis: one row per (company, periodic filing).
--    factor_to_current = product of the ratios of confirmed events with
--    basis_date > filing_date. Unique on (company_id, filing_id), not on
--    filing_id alone (SB-1 draft said filing_id unique): a combined filing is
--    shared by several registrants (Entergy 0000065984-26-000174), and each
--    registrant has its own share basis. event_ids has no FK (arrays cannot);
--    the writer keeps it consistent with split_event.
create table if not exists analytics.split_event (
    id                bigint generated always as identity primary key,
    company_id        bigint not null references core.company (id),
    ratio             numeric not null check (ratio > 0 and ratio <> 1),
    basis_date        date not null,
    evidence          jsonb not null,
    evidence_kinds    text[] not null check (
        cardinality(evidence_kinds) >= 1
        and evidence_kinds <@ array['ratio_fact', 'filed_pair', 'share_step']::text[]
    ),
    status            text not null check (status in ('confirmed', 'review')),
    detector_version  text not null,
    created_at        timestamptz not null default now(),
    unique (company_id, ratio, basis_date),
    check (status <> 'confirmed' or cardinality(evidence_kinds) >= 2)
);

create table if not exists analytics.filing_share_basis (
    id                 bigint generated always as identity primary key,
    company_id         bigint not null references core.company (id),
    filing_id          bigint not null references core.filing (id),
    filing_date        date not null,
    factor_to_current  numeric not null check (factor_to_current > 0),
    event_ids          bigint[] not null default '{}',
    observed_factor    numeric check (observed_factor is null or observed_factor > 0),
    status             text not null check (status in ('consistent', 'date_only', 'conflict', 'review')),
    basis_version      text not null,
    computed_at        timestamptz not null default now(),
    unique (company_id, filing_id)
);

create index if not exists idx_filing_share_basis_filing
    on analytics.filing_share_basis (filing_id);
