-- Ownership / insider activity schema (doc 19). Extends `core` -- this is
-- identity-adjacent data (who transacts in / owns a company's stock),
-- the same conceptual home as core.company/core.listing, not analytics.

-- One row per disclosed transaction (Form 4, the core insider-activity
-- feed per doc 10 -- Form 3/5 deliberately out of this pass, see doc 19).
-- transaction_index handles one filing disclosing multiple transactions.
create table if not exists core.insider_transaction (
    id                       bigint generated always as identity primary key,
    company_id               bigint not null references core.company (id),
    accession_number         text not null,
    transaction_index        int not null,
    form                     text not null check (form in ('3', '4', '5', '3/A', '4/A', '5/A')),
    reporting_owner_name     text not null,
    reporting_owner_cik      text,
    is_director              boolean not null default false,
    is_officer               boolean not null default false,
    is_ten_percent_owner     boolean not null default false,
    officer_title            text,
    security_title           text,
    transaction_date         date,
    transaction_code         text,
    shares                   numeric,
    price_per_share          numeric,
    acquired_disposed_code   text check (acquired_disposed_code in ('A', 'D')),
    shares_owned_following   numeric,
    filing_date              date,
    created_at               timestamptz not null default now(),
    unique (accession_number, transaction_index)
);
create index if not exists idx_insider_transaction_company on core.insider_transaction (company_id, transaction_date desc);

-- One row per disclosed >5% beneficial-ownership stake (Schedule 13D/13G).
-- Only ever populated when the filing's own issuerCik is confirmed to
-- match the golden company (doc 19 Sec 1's issuer-vs-filer finding) --
-- never inferred from which company's submissions list the filing was
-- found under.
create table if not exists core.beneficial_ownership (
    id                bigint generated always as identity primary key,
    company_id        bigint not null references core.company (id),
    accession_number  text not null unique,
    schedule_type     text not null check (schedule_type in ('13D', '13G')),
    is_amendment      boolean not null default false,
    filer_name        text not null,
    filer_cik         text,
    percent_of_class  numeric,
    shares_owned      numeric,
    filing_date       date,
    created_at        timestamptz not null default now()
);
create index if not exists idx_beneficial_ownership_company on core.beneficial_ownership (company_id, filing_date desc);
