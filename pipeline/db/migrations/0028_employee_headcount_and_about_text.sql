-- Employee headcount (unstructured 10-K text extraction) + About text
-- (doc/scoping/39_Scrooner_Employee_Headcount_Full_Coverage_Plan.md).
--
-- Deliberately NOT core.fact: values here come from regex extraction over
-- 10-K prose, not tagged XBRL, so they carry a fundamentally different
-- confidence class than core.fact.is_authoritative rows -- mixing them in
-- would silently degrade the trust every other concept in that table
-- relies on. Kept in a dedicated table with its own provenance columns
-- (source filing, extraction snippet) instead.
--
-- Scope note (per user direction 2026-08-30, narrower than doc 39's
-- original 4-stage plan): only the 2 most recent 10-Ks per company (this
-- disclosure is annual-only -- confirmed live 2026-08-30 that Apple's own
-- 10-Q does NOT repeat the Human Capital section at all), not a multi-
-- year backfill to the 2021 Item 101(c) floor. about_text is a single
-- latest-only column on core.company (1 fetch, no history), matching doc
-- 38's case-1 reasoning -- a fresh fetch just overwrites it.

create table if not exists core.employee_headcount_disclosure (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    filing_date date not null,
    report_date date,
    headcount integer not null,
    is_approximate boolean not null default false,
    source_form text not null,
    source_accession text not null,
    source_snippet text not null,
    extracted_at timestamptz not null default now(),
    unique (company_id, source_accession)
);

create index if not exists idx_employee_headcount_disclosure_company
    on core.employee_headcount_disclosure (company_id, filing_date desc);

alter table core.company add column if not exists about_text text;
alter table core.company add column if not exists about_text_source_accession text;
