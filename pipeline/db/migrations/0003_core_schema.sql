-- Core schema for the Normalizer. See scrooner/doc/09_Scrooner_Normalizer_Execution_Plan.md
-- for the design rationale. The Normalizer reads `raw` (never writes it) and
-- writes only to `core`.
--
-- Full logical schema created up front (company/listing/filing/period/unit/
-- concept/fact), same precedent as 0001_raw_schema.sql -- populated
-- incrementally, stage by stage (2a company/listing/filing now; 2b-2d bring
-- period/unit/concept/fact online later), not all at once.

create schema if not exists core;

-- One row per CIK. Anchors identity -- never touched by a ticker change.
create table if not exists core.company (
    id              bigint generated always as identity primary key,
    cik             text not null unique,
    company_name    text not null,
    fiscal_year_end text,  -- MMDD, from submissions' own fiscalYearEnd field (e.g. '0926' = Sept 26). Added Day 2 (Stage 2b) -- Stage 2a's identity.py backfills it, harmless re-run since upserts are idempotent. Used only as a fallback anchor for period.fiscal_year/fiscal_period derivation; the primary signal is each company's own observed full-year period end dates (see core.period below) -- verified live 2026-08-15 that the nominal MMDD wobbles by up to ~a week around each company's actual fiscal-year-end date (e.g. AAPL: 2016-09-24, 2017-09-30, 2018-09-29 against a nominal '0926'), so trusting the nominal date alone would misclassify periods near the boundary.
    created_at      timestamptz not null default now()
);
alter table core.company add column if not exists fiscal_year_end text;

-- Ticker/exchange associations. Sourced from raw.sec_submissions' own
-- tickers/exchanges arrays (richer and more current than
-- raw.company_universe -- includes OTC-only symbols like Block's BSQKZ that
-- company_tickers.json omits). effective_from/effective_to are nullable and,
-- as of Stage 2a, always null: neither company_tickers.json nor the
-- submissions API exposes *historical* ticker intervals (verified live
-- 2026-08-14/15 -- Block/XYZ's submissions payload lists only its two
-- CURRENT tickers, XYZ and BSQKZ, not the former SQ). Populating real
-- effective_from/effective_to needs a source the Collector doesn't fetch;
-- that's Company Master's job (doc 06 Part 4, doc 03's gate before
-- Screener), not this phase's to fabricate. A null effective_to means
-- "currently listed as of the most recent submissions fetch."
create table if not exists core.listing (
    id             bigint generated always as identity primary key,
    company_id     bigint not null references core.company (id),
    ticker         text not null,
    exchange       text,
    effective_from date,
    effective_to   date,
    unique (company_id, ticker)
);

-- One row per filing, restricted to the form types doc 03's MVP actually
-- needs (10-K/10-Q for US domestic filers, plus the 20-F/40-F forms two
-- golden companies use -- recorded per doc 02's still-open foreign-filer
-- scope question, not treated as first-class). Everything else in a
-- company's submissions history (Form 4, 8-K, 144, UPLOAD correspondence,
-- etc.) is deliberately left unparsed here -- doc 09's own gotcha list warns
-- against scope creep past what doc 03 needs, and every one of those stays
-- fully inspectable in raw.sec_submissions regardless.
--
-- No fiscal_year/fiscal_period columns here -- an earlier draft of doc 09's
-- schema had them, but verified live 2026-08-15: SEC's submissions API
-- carries no such field per filing (only accessionNumber/form/filingDate/
-- reportDate). A single 10-K reports facts for several fiscal years at
-- once (current + comparatives) -- fiscal year/period is a per-FACT
-- attribute (core.period, Stage 2b), not a per-filing one. Fixed here
-- before any row shipped, rather than carrying a column nothing can
-- populate correctly.
create table if not exists core.filing (
    id                bigint generated always as identity primary key,
    company_id        bigint not null references core.company (id),
    accession_number  text not null unique,
    form              text not null,
    filing_date       date,
    period_of_report  date,
    is_amendment      boolean not null default false,
    amends_filing_id  bigint references core.filing (id),
    raw_submission_id bigint references raw.sec_submissions (id),
    created_at        timestamptz not null default now()
);

-- Small, mostly-static lookup -- referenced by core.fact via unit_id rather
-- than repeating unit text on tens of millions of fact rows (doc 09's
-- Supabase free-tier capacity section explains why this matters).
create table if not exists core.unit (
    id        bigint generated always as identity primary key,
    unit_name text not null unique
);

-- Lookup of (taxonomy, tag) pairs -- cardinality is a few thousand across
-- every filer, versus tens of millions of fact rows that would otherwise
-- repeat tag text. Still the issuer's ORIGINAL tag, never a canonical
-- Scrooner concept -- renaming to canonical concepts is Mapper work
-- (Phase 3), not this schema's job.
create table if not exists core.concept (
    id       bigint generated always as identity primary key,
    taxonomy text not null,
    tag      text not null,
    unique (taxonomy, tag)
);

-- Canonical fiscal periods (Stage 2b). Identity is the OBJECTIVE calendar
-- span -- (company_id, start_date, end_date, period_type) -- not
-- (fiscal_year, fiscal_period). Corrected 2026-08-15, before any row
-- shipped (core.period was empty): verified live against AAPL's raw
-- companyfacts that a single real period gets reported under DIFFERENT
-- fy/fp labels depending on which filing mentions it -- e.g. AAPL's
-- 2017-07-02..2017-09-30 quarter appears tagged fy=2017/fp=FY (in the
-- FY2017 10-K's own supplementary quarterly footnote), fy=2018/fp=FY (as a
-- prior-year comparative in the FY2018 10-K) and fy=2018/fp=Q1 (as context
-- in a later 10-Q) -- fy/fp describes the REPORTING FILING, not the
-- period's own identity. Trusting it as the period's key would have
-- created spurious duplicate period rows for the same real period. See
-- doc/learnings/normalizer-day-02-periods.md.
--
-- fiscal_year/fiscal_period here are instead DERIVED, best-effort display
-- labels (Stage 2b's own job, from each company's own observed full-year
-- period end dates, not from any entry's fy/fp field) -- nullable, and
-- deliberately NOT part of the table's identity. Every downstream stage
-- must key off start_date/end_date/period_type, never these two.
--
-- start_date is NOT NULL even for instants (set equal to end_date) so the
-- unique constraint below works correctly -- Postgres treats every NULL as
-- distinct in a unique constraint, which would have let duplicate instant
-- periods slip through silently.
create table if not exists core.period (
    id            bigint generated always as identity primary key,
    company_id    bigint not null references core.company (id),
    start_date    date not null,
    end_date      date not null,
    period_type   text not null check (period_type in ('instant', 'duration')),
    fiscal_year   int,
    fiscal_period text check (fiscal_period in ('FY', 'Q1', 'Q2', 'Q3', 'Q4')),
    unique (company_id, start_date, end_date, period_type)
);

-- Every individual reported value (Stage 2d onward). Still keyed to the
-- issuer's original tag via concept_id -- never renamed to a canonical
-- concept here (that's the Mapper's job, deliberately, with a version
-- number attached).
--
-- unique(company_id, concept_id, unit_id, period_id, filing_id): verified
-- live 2026-08-15 across the golden-8's ~178K raw datapoints that a single
-- filing never reports the same (concept, unit, period) combination twice
-- with conflicting values (0 conflicts found) -- so this is a safe,
-- correctness-preserving idempotency key, not a lossy dedup guess. Multiple
-- DIFFERENT filings reporting the same period (comparatives, restatements)
-- still get separate rows, since filing_id differs -- resolving which is
-- authoritative is Stage 2e/2f's job, not this constraint's.
create table if not exists core.fact (
    id                  bigint generated always as identity primary key,
    company_id          bigint not null references core.company (id),
    concept_id          bigint not null references core.concept (id),
    unit_id             bigint not null references core.unit (id),
    period_id           bigint not null references core.period (id),
    filing_id           bigint not null references core.filing (id),
    value               numeric not null,
    is_derived          boolean not null default false,
    is_authoritative    boolean not null default true,
    supersedes_fact_id  bigint references core.fact (id),
    raw_object_id       bigint not null references raw.sec_companyfacts (id),
    created_at          timestamptz not null default now(),
    unique (company_id, concept_id, unit_id, period_id, filing_id)
);
create index if not exists idx_fact_company_concept_period on core.fact (company_id, concept_id, period_id);
