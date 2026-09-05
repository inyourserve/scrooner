-- Revenue by business segment (doc 37, built 2026-08-31 for the
-- golden-10 per direct user request). Sourced from each company's most
-- recent 10-Q/10-K's own auto-rendered "Details" report (R*.htm), not
-- the standard Company Facts API -- that API strips dimensional/segment
-- XBRL entirely (confirmed live, doc 22). Single most recent filing
-- only, per doc 38's case-1 reasoning: the report already contains
-- multiple comparison periods in one table (current + year-ago quarter,
-- current + year-ago YTD), so no backfill is needed.

create table if not exists core.segment_revenue (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    segment_name text not null,
    concept_ref text not null,
    period_type text not null,
    period_end text not null,
    value numeric not null,
    source_form text not null,
    source_accession text not null,
    source_report text not null,
    extracted_at timestamptz not null default now()
);

create index if not exists idx_segment_revenue_company
    on core.segment_revenue (company_id);
