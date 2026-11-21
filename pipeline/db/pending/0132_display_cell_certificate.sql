-- 0132: certification single source of truth (review-response plan P1.3, 2026-11-21).
-- Why: analytics.company_certification (0097) has 0 rows and is written only by the retired I1-I11 suite, which never sets
-- 'certified'. The real certificates (GILD, JNJ) were markdown and no code read them. This table is the one place a
-- certification lives: one row per cell of a PASS certificate, loaded from its JSON (schema display-certificate/1,
-- written by pipeline/scripts/certify_display.py) by `scrooner_pipeline.certification.display_cert_load` (dry-run default).
-- Rulings: data-team/strategy/approvals/CERT-REGISTRY-rulings-2026-11-21.md.
--  * Scope: EVERY cell of the certified coverage file, shown and hidden. `evidence` says how it was checked:
--    drawn = individually matched to the filing (the only cells the error bound counts); census = every total_debt year,
--    the per-share census and every hidden cell's hide-class proof; sampled = covered by the bound, NEVER individually
--    verified (CHECK below: a sampled cell's result is 'SAMPLED').
--  * Identity and versions: sample_hash (= the coverage file's sha256), detector_version, resolver path and code_sha come
--    from the certificate. There is NO single proof_version string, so a version-only bump makes nothing stale.
--  * Staleness (analytics.display_cell_certificate_status, read-time join, never lags): a cell is stale only when its
--    display class (display, and hide_class when the certificate states one: the GILD certificate carries none for its hidden rows) or its evidence accession differs from the certified row, or when a later periodic
--    filing RESTATES it. cell_display_state holds no served value, so the value is guarded by accession (a different filing
--    means a different printed value) and by the restatement check.
--  * Restatement (ruling 3): a later periodic filing (10-K/10-Q/20-F/40-F, fsn.filing.accepted later than the certified
--    filing) printing a DIFFERENT value than the certified filing printed for the same tag, period (ddate, qtrs) and
--    dimensions (fsn.value). A comparative column with the same value voids nothing; a new fiscal year voids nothing.
--    Needs fsn.* (0118). A cell whose certified filing has no fsn.value row for its key cannot be compared and is not flagged.
--  * Company level: analytics.company_certification_derived is 'display_certified' only while EVERY cell of the company's
--    LATEST certificate is valid (all cells, not the 32 drawn); any stale or invalidated cell makes it 'stale'. The latest
--    certificate per company wins (greatest certified_at, then newest load); older ones show status 'superseded'.
--  * Invalidation is materialised by analytics.invalidate_display_cell_certificates() (idempotent; the loader calls it for
--    the company inside its own transaction). It records only what is a permanent fact: 'restated' (the filing record
--    changed; a restated cell stays void until a new certificate is drawn) and 'superseded'. Display/accession drift is NOT
--    made permanent: a pipeline rerun that rewrites cell_display_state must not void a certificate for good, so those stay
--    live statuses that recover when the state returns to the certified one.
-- Depends on 0118 (fsn.*) and 0130 (analytics.cell_display_state, applied live 2026-11-17).
--
-- company_certification (0097) is DEPRECATED, not dropped: the retired suite code still writes it. Drop it in its own
-- migration once that writer is removed (ruling 6).
-- ROLLBACK: drop view analytics.company_certification_derived; drop function analytics.invalidate_display_cell_certificates(bigint);
--           drop view analytics.display_cell_certificate_status; drop table analytics.display_cell_certificate;
create table if not exists analytics.display_cell_certificate (
    id               bigint generated always as identity primary key,
    company_id       bigint      not null references core.company (id),
    data_point       text        not null check (btrim(data_point) <> ''),
    period_end       date        not null,
    grain            text        not null check (grain in ('FY', 'I')),
    fiscal_year      integer,
    display          text        not null check (display in ('SHOWN_VALUE', 'HIDDEN_ROW', 'HIDDEN_YEAR', 'OUT', 'OPEN')),
    hide_class       text,
    reason_code      text,
    shown_value      numeric,
    accession        text        check (accession ~ '^[0-9]{10}-[0-9]{2}-[0-9]{6}$'),
    r_page           text,
    tag              text,
    restate_keys     jsonb       not null default '[]'::jsonb,   -- [{"tag": ..., "dims": ""}]: the filing keys the restatement check compares
    evidence         text        not null check (evidence in ('drawn', 'census', 'sampled')),
    result           text        not null check (result in ('MATCH', 'MISMATCH', 'NOT_FOUND', 'LOCATOR', 'REVIEW', 'SAMPLED')),
    sample_hash      text        not null check (sample_hash ~ '^[0-9a-f]{64}$'),
    detector_version text,
    resolver         text,
    code_sha         text,
    draw_seed        text,
    certificate_path text        not null check (btrim(certificate_path) <> ''),
    approver         text        not null check (btrim(approver) <> ''),
    certified_at     timestamptz not null,
    invalidated_at   timestamptz,
    invalidated_reason text,
    loaded_at        timestamptz not null default now(),
    constraint display_cell_certificate_invalidation_pair
        check ((invalidated_at is null) = (invalidated_reason is null)),
    -- a shown cell carries its value and accession; a hidden cell carries no value
    constraint display_cell_certificate_shown_has_value
        check ((display = 'SHOWN_VALUE') = (shown_value is not null)),
    constraint display_cell_certificate_shown_has_accession
        check (display <> 'SHOWN_VALUE' or accession is not null),
    -- never present a sampled cell as individually verified; a drawn cell of a PASS certificate matched the filing
    constraint display_cell_certificate_sampled_not_verified
        check ((evidence = 'sampled') = (result = 'SAMPLED')),
    constraint display_cell_certificate_drawn_matched
        check (evidence <> 'drawn' or result = 'MATCH'),
    unique (company_id, data_point, period_end, grain, sample_hash)
);

create index if not exists display_cell_certificate_company_idx
    on analytics.display_cell_certificate (company_id);

alter table analytics.display_cell_certificate enable row level security;

comment on table analytics.display_cell_certificate is
    'Single source of truth for display certification: one row per cell (shown and hidden) of a PASS certificate; evidence drawn/census/sampled (only drawn counts toward the bound, sampled is never individually verified); sample_hash = coverage file sha256. Stale only on a display-class or accession change or a restatement. Loaded from the certificate JSON.';

create or replace view analytics.display_cell_certificate_status as
with latest as (
    select distinct on (company_id) company_id, sample_hash
    from analytics.display_cell_certificate
    order by company_id, certified_at desc, id desc
)
select
    c.*,
    case
        when c.invalidated_at is not null then 'invalidated'::text
        when c.sample_hash <> l.sample_hash then 'superseded'::text
        when c.display = 'SHOWN_VALUE' and f.id is null then 'unverifiable_accession'::text
        when ds.display is distinct from c.display
          or (c.hide_class is not null and ds.hide_class is distinct from c.hide_class) then 'stale_display'::text
        when c.display = 'SHOWN_VALUE' and ds.evidence_accession is distinct from c.accession then 'stale_accession'::text
        when c.display = 'SHOWN_VALUE' and exists (
            select 1
            from jsonb_to_recordset(c.restate_keys) as k(tag text, dims text)
            join fsn.tag bt on bt.tag = k.tag
            join fsn.dim d on d.segments = coalesce(k.dims, '')
            join fsn.filing bf on bf.accession = c.accession
            join fsn.value base on base.filing_id = bf.id and base.tag_id = bt.id and base.ddate = c.period_end
                               and base.qtrs = case c.grain when 'I' then 0 else 4 end and base.dim_id = d.id
            join fsn.tag lt on lt.tag = bt.tag
            join fsn.value later on later.company_id = c.company_id and later.tag_id = lt.id and later.ddate = base.ddate
                                and later.qtrs = base.qtrs and later.dim_id = base.dim_id and later.uom = base.uom
                                and later.iprx = base.iprx and later.coreg = base.coreg and later.filing_id <> base.filing_id
            join fsn.filing lf on lf.id = later.filing_id and lf.accepted > bf.accepted
                              and lf.form ~ '^(10-K|10-Q|20-F|40-F)'
            where later.value is distinct from base.value
        ) then 'stale_restated'::text
        else 'valid'::text
    end as status
from analytics.display_cell_certificate c
join latest l on l.company_id = c.company_id
left join core.filing f on f.accession_number = c.accession
left join analytics.cell_display_state ds
       on ds.company_id = c.company_id and ds.data_point = c.data_point
      and ds.period_end = c.period_end and ds.grain = c.grain;

-- Materialise the permanent invalidations once (idempotent). p_company_id null = all companies. Returns rows newly invalidated.
create or replace function analytics.invalidate_display_cell_certificates(p_company_id bigint default null)
returns bigint
language plpgsql
set search_path = pg_catalog, analytics, core, fsn
as $$
declare
    n bigint;
begin
    with stale as (
        select id, status from analytics.display_cell_certificate_status
        where invalidated_at is null and status in ('stale_restated', 'superseded')
          and (p_company_id is null or company_id = p_company_id)
    ), u as (
        update analytics.display_cell_certificate c
           set invalidated_at = now(), invalidated_reason = replace(stale.status, 'stale_', '')
          from stale where c.id = stale.id
        returning 1
    )
    select count(*) into n from u;
    return n;
end;
$$;

-- Company level, derived: display_certified only while EVERY cell of the latest certificate is valid. Counts per
-- evidence class are reported; only drawn cells are individually verified (and the only ones the bound counts).
create or replace view analytics.company_certification_derived as
with latest as (
    select distinct on (company_id) company_id, sample_hash, certified_at
    from analytics.display_cell_certificate
    order by company_id, certified_at desc, id desc
)
select
    l.company_id,
    l.sample_hash,
    l.certified_at,
    count(*)                                        as cells,
    count(*) filter (where s.status = 'valid')      as valid_cells,
    count(*) filter (where s.evidence = 'drawn')    as drawn_cells,
    count(*) filter (where s.evidence = 'census')   as census_cells,
    count(*) filter (where s.evidence = 'sampled')  as sampled_cells,
    case when count(*) filter (where s.status <> 'valid') = 0
         then 'display_certified'::text else 'stale'::text end as state
from latest l
join analytics.display_cell_certificate_status s
  on s.company_id = l.company_id and s.sample_hash = l.sample_hash
group by l.company_id, l.sample_hash, l.certified_at;

comment on table analytics.company_certification is
    'DEPRECATED 2026-11-21 (0132): written only by the retired I1-I11 suite, 0 rows, never sets certified. Read analytics.company_certification_derived (from analytics.display_cell_certificate) instead.';

-- Defence in depth: the API roles have no USAGE on analytics today; make the certificate objects unreachable even if that changes.
do $$
begin
    if exists (select 1 from pg_roles where rolname = 'anon') then
        execute 'revoke all on analytics.display_cell_certificate, analytics.display_cell_certificate_status, analytics.company_certification_derived from anon';
        execute 'revoke all on function analytics.invalidate_display_cell_certificates(bigint) from anon';
    end if;
    if exists (select 1 from pg_roles where rolname = 'authenticated') then
        execute 'revoke all on analytics.display_cell_certificate, analytics.display_cell_certificate_status, analytics.company_certification_derived from authenticated';
        execute 'revoke all on function analytics.invalidate_display_cell_certificates(bigint) from authenticated';
    end if;
end
$$;
revoke all on function analytics.invalidate_display_cell_certificates(bigint) from public;
