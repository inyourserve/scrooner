-- 0121: predecessor registrants (scrooner-87, 2026-11-01). A company that reorganised into a new holding
-- company files its history under the predecessor's CIK (Exxon Mobil Corp 0000034088 -> ExxonMobil Holdings
-- Corp 0002115436, 2026). One row per predecessor CIK names the company that owns that history; the FSN store
-- shard/load read it, so the predecessor's filings load under the successor's company_id.
-- Founder's typed go-ahead for the XOM history link in scrooner-87, 2026-11-01.
create table if not exists core.company_predecessor (
    predecessor_cik   text primary key check (predecessor_cik ~ '^[0-9]{10}$'),
    company_id        bigint not null references core.company (id),
    predecessor_name  text not null,
    succeeded_on      date,
    reason            text not null check (btrim(reason) <> ''),
    created_at        timestamptz not null default now()
);

create index if not exists idx_company_predecessor_company on core.company_predecessor (company_id);

comment on table core.company_predecessor is
    'Predecessor registrant CIK -> the company that owns its filing history (holding-company reorganisations).';
