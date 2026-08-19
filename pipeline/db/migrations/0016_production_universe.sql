-- Day 6 production-universe identities and point-in-time decisions.
--
-- Backward compatible: core.company.cik and core.listing.company_id remain
-- because existing pipeline stages use them. New universe code uses the
-- explicit filer/security identities introduced here.

create table if not exists core.filer (
    id          bigint generated always as identity primary key,
    company_id  bigint not null references core.company (id),
    cik         text not null unique,
    source      text not null default 'sec_submissions',
    created_at  timestamptz not null default now()
);

insert into core.filer (company_id, cik)
select id, cik from core.company
on conflict (cik) do update set company_id = excluded.company_id;

create table if not exists core.security (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null references core.company (id),
    source_key            text not null unique,
    security_type         text,
    classification_source text,
    created_at             timestamptz not null default now()
);

insert into core.security
    (company_id, source_key, security_type, classification_source)
select
    company_id,
    'listing:' || id::text,
    security_type,
    coalesce(security_type_source, 'unclassified')
from core.listing
on conflict (source_key) do update
set security_type = excluded.security_type,
    classification_source = excluded.classification_source;

alter table core.listing add column if not exists security_id bigint references core.security (id);

update core.listing l
set security_id = s.id
from core.security s
where s.source_key = 'listing:' || l.id::text
  and l.security_id is distinct from s.id;

create index if not exists idx_filer_company on core.filer (company_id);
create index if not exists idx_security_company on core.security (company_id);
create index if not exists idx_listing_security on core.listing (security_id);

create table if not exists core.universe_snapshot (
    id             bigint generated always as identity primary key,
    as_of          date not null,
    policy_version text not null,
    created_at     timestamptz not null default now(),
    unique (as_of, policy_version)
);

create table if not exists core.universe_member (
    id                 bigint generated always as identity primary key,
    snapshot_id        bigint not null references core.universe_snapshot (id) on delete cascade,
    company_id         bigint not null references core.company (id),
    filer_id           bigint not null references core.filer (id),
    security_id        bigint not null references core.security (id),
    listing_id         bigint not null references core.listing (id),
    eligibility_status text not null check (eligibility_status in ('eligible', 'excluded', 'uncertain')),
    reason_codes       jsonb not null,
    is_primary         boolean not null default false,
    decision_order     integer not null,
    unique (snapshot_id, listing_id)
);

create index if not exists idx_universe_member_snapshot_status
    on core.universe_member (snapshot_id, eligibility_status, decision_order);
create unique index if not exists idx_universe_one_primary_per_company
    on core.universe_member (snapshot_id, company_id)
    where is_primary;
