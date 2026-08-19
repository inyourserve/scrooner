-- Raw schema for the Collector. See scrooner/doc/execution-plans/08_Scrooner_Collector_Execution_Plan.md
-- for the design rationale. The Collector writes ONLY to this schema.

create schema if not exists raw;

-- Current-state mirror of SEC's own ticker/CIK list (company_tickers.json).
-- Verified live against the real endpoint 2026-08-14: CIK->ticker is ONE-TO-MANY
-- (e.g. Alphabet/CIK 1652044 has GOOGL/GOOG/GOOGM/GOOGN) — primary key is the
-- (cik, ticker) pair, NOT cik alone. Upserted on that pair — the one table here
-- that is NOT append-only.
--
-- No `exchange` or `status` column: company_tickers.json doesn't carry exchange
-- (that lives in the Submissions API/submissions.zip, populated during the Day 3
-- bulk submissions pass, not fetched per-company here) and there is no SEC-provided
-- "status" field at all — deriving one would be interpretation, which belongs to
-- the Normalizer/Company Master, not the Collector.
create table if not exists raw.company_universe (
    cik              text not null,
    ticker           text not null,
    company_name     text not null,
    collected_at     timestamptz not null default now(),
    primary key (cik, ticker)
);

-- Append-only: one row per fetch, never updated. History is reconstructable
-- from the row set alone.
create table if not exists raw.sec_companyfacts (
    id           bigint generated always as identity primary key,
    cik          text not null,
    fetched_at   timestamptz not null default now(),
    source_url   text not null,
    sha256       text not null,
    storage_path text not null,
    http_status  int not null
);
create index if not exists idx_sec_companyfacts_cik on raw.sec_companyfacts (cik, fetched_at desc);

create table if not exists raw.sec_submissions (
    id           bigint generated always as identity primary key,
    cik          text not null,
    fetched_at   timestamptz not null default now(),
    source_url   text not null,
    sha256       text not null,
    storage_path text not null,
    http_status  int not null
);
create index if not exists idx_sec_submissions_cik on raw.sec_submissions (cik, fetched_at desc);

-- Upserted on (cik, accession_number) — NOT append-only. A filing at a given
-- accession number is immutable once filed (amendments get a new accession
-- number), so this is one row per known filing whose download_status
-- transitions indexed -> downloaded/failed via UPDATE, same pattern as
-- company_universe. (Earlier draft called this append-only with only a
-- non-unique index, which would have let duplicate rows accumulate per
-- filing as volume grew — fixed before any real data was loaded.)
create table if not exists raw.sec_filing_documents (
    cik              text not null,
    accession_number text not null,
    form             text not null,
    filing_date      date,
    report_date      date,
    source_url       text not null,
    sha256           text,
    storage_path     text,
    download_status  text not null default 'indexed'
                     check (download_status in ('indexed', 'downloaded', 'failed')),
    collected_at     timestamptz not null default now(),
    primary key (cik, accession_number)
);

create table if not exists raw.collector_runs (
    id          bigint generated always as identity primary key,
    run_type    text not null check (run_type in ('bootstrap', 'incremental')),
    started_at  timestamptz not null default now(),
    finished_at timestamptz,
    status      text not null default 'running'
               check (status in ('running', 'succeeded', 'failed')),
    stats       jsonb not null default '{}'::jsonb
);

create table if not exists raw.collector_errors (
    id          bigint generated always as identity primary key,
    run_id      bigint references raw.collector_runs (id),
    cik         text,
    source      text,
    error_type  text not null,
    message     text not null,
    occurred_at timestamptz not null default now(),
    resolved    boolean not null default false
);
