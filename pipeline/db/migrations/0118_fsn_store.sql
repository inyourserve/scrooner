-- Company-wise FSN statement store, schema fsn (data-team/strategy/FSN-STORE-DESIGN-2026-11-01.md §1).
-- Every 10-K/10-Q of a cohort company, as printed: filings, reports, presentation lines, every non-dimensional
-- value and every dimensional value on a statement line, calc arcs; plus the mapping (line -> canonical concept),
-- the per-column identity checks and the company load ledger. Nothing here is ever overwritten by a later filing:
-- "latest" and "as filed" are queries. Written 2026-11-01 by scrooner-8a; NOT applied; apply needs the founder's words.
create schema if not exists fsn;

create table if not exists fsn.filing (
    id          bigint generated always as identity primary key,
    accession   text not null unique,
    company_id  bigint references core.company (id),       -- the registrant (sub.cik); co-registrants in aciks
    cik         text not null,
    form        text not null,
    period      date,                                        -- sub.period (balance sheet date)
    fy          integer,
    fp          text,
    fye         text,
    filed       date,
    accepted    timestamptz,                                 -- the vintage order
    amendment   boolean not null default false,
    prevrpt     boolean not null default false,
    aciks       text[] not null default '{}',
    fsn_set     text not null,
    src_sha256  text
);
create index if not exists idx_fsn_filing_company_accepted on fsn.filing (company_id, accepted);
create index if not exists idx_fsn_filing_cik on fsn.filing (cik);

create table if not exists fsn.report (
    filing_id     bigint not null references fsn.filing (id) on delete cascade,
    report        integer not null,
    rfile         text,
    menucat       text,                                      -- 'S' = statement
    shortname     text,
    longname      text,
    roleuri       text,
    parentreport  integer,
    ultparentrpt  integer,
    primary key (filing_id, report)
);

create table if not exists fsn.tag (
    id        bigint generated always as identity primary key,
    tag       text not null,
    version   text not null,                                  -- taxonomy/year or the accession for custom tags
    custom    boolean not null default false,
    abstract  boolean not null default false,
    datatype  text,
    iord      text,
    crdr      text,
    tlabel    text,
    unique (tag, version)
);

create table if not exists fsn.dim (
    id        bigint generated always as identity primary key,
    dimh      text not null unique,                           -- '0x00000000' = no dimension
    segments  text,
    segt      boolean
);

create table if not exists fsn.line (
    id         bigint generated always as identity primary key,
    filing_id  bigint not null references fsn.filing (id) on delete cascade,
    report     integer not null,
    line       integer not null,
    stmt       text not null,
    inpth      boolean not null default false,
    tag_id     bigint not null references fsn.tag (id),
    prole      text,
    plabel     text,
    negating   boolean not null default false,
    unique (filing_id, report, line)
);
create index if not exists idx_fsn_line_filing_stmt on fsn.line (filing_id, stmt, report, line);
create index if not exists idx_fsn_line_tag on fsn.line (tag_id);

create table if not exists fsn.value (
    id          bigint generated always as identity primary key,
    filing_id   bigint not null references fsn.filing (id) on delete cascade,
    company_id  bigint references core.company (id),
    tag_id      bigint not null references fsn.tag (id),
    ddate       date not null,
    qtrs        smallint not null,
    uom         text not null,
    dim_id      bigint not null references fsn.dim (id),
    iprx        smallint not null default 0,
    coreg       text not null default '',
    value       numeric,
    footnote    text,
    durp        real,
    datp        real,
    dcml        smallint,
    unique (filing_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg)
);
create index if not exists idx_fsn_value_series on fsn.value (company_id, tag_id, ddate, qtrs)
    include (value, filing_id) where dim_id = 1;             -- the no-dimension row is inserted first (id 1) by the loader
create index if not exists idx_fsn_value_filing on fsn.value (filing_id);

create table if not exists fsn.calc_arc (
    filing_id      bigint not null references fsn.filing (id) on delete cascade,
    grp            integer not null,
    arc            integer not null,
    parent_tag_id  bigint not null references fsn.tag (id),
    child_tag_id   bigint not null references fsn.tag (id),
    weight         smallint not null check (weight in (1, -1)),
    primary key (filing_id, grp, arc)
);
create index if not exists idx_fsn_calc_arc_parent on fsn.calc_arc (filing_id, parent_tag_id);

create table if not exists fsn.company_load (
    company_id     bigint primary key references core.company (id),
    cik            text not null,
    input_sha256   text not null,                             -- manifest.json input_sha256 of the company directory
    loader_commit  text not null,
    row_counts     jsonb not null default '{}'::jsonb,
    run_id         uuid references analytics.rule_run (run_id),
    loaded_at      timestamptz not null default now()
);

create table if not exists fsn.concept_rule (
    id                    bigint generated always as identity primary key,
    canonical_concept_id  bigint not null references analytics.canonical_concept (id),
    stmt                  text not null check (stmt in ('BS', 'IS', 'CF')),
    match_kind            text not null check (match_kind in ('std_tag', 'calc_position', 'combined')),
    tag                   text,                               -- prefix:tag, version-agnostic; null for calc_position
    position              jsonb,
    components            text[],
    priority              integer not null,
    era_from              date,
    era_to                date,
    rule_id               text not null check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    source_commit         text,
    evidence              text,
    seeded_at             timestamptz not null default now(),
    check (match_kind <> 'calc_position' or position is not null),
    check (match_kind <> 'combined' or components is not null),
    check (match_kind = 'calc_position' or tag is not null)
);
create unique index if not exists uq_fsn_concept_rule
    on fsn.concept_rule (canonical_concept_id, stmt, match_kind, coalesce(tag, ''), priority);

create table if not exists fsn.line_map (
    filing_id             bigint not null references fsn.filing (id) on delete cascade,
    report                integer not null,
    line                  integer not null,
    canonical_concept_id  bigint references analytics.canonical_concept (id),
    status                text not null check (status in ('mapped', 'combined', 'unmapped', 'excluded')),
    rule_id               text,
    era                   text,
    evidence              jsonb not null default '{}'::jsonb,
    primary key (filing_id, report, line),
    foreign key (filing_id, report, line) references fsn.line (filing_id, report, line) on delete cascade
);
create index if not exists idx_fsn_line_map_concept on fsn.line_map (canonical_concept_id, filing_id);

create table if not exists fsn.filing_check (
    filing_id  bigint not null references fsn.filing (id) on delete cascade,
    stmt       text not null,
    ddate      date not null,
    qtrs       smallint not null,
    check_id   text not null,
    ok         boolean not null,
    lhs        numeric,
    rhs        numeric,
    tol        numeric,
    detail     jsonb not null default '{}'::jsonb,
    primary key (filing_id, stmt, ddate, qtrs, check_id)
);

alter table analytics.canonical_fact
    add column if not exists source_value_ids bigint[] not null default '{}';
