-- 0132: certification single source of truth (review-response plan P1.3, 2026-11-21).
-- Why: analytics.company_certification (0097) has 0 rows and is written only by the retired I1-I11 suite, which never sets
-- 'certified'. The real certificates (GILD, JNJ) are markdown under data-team/strategy/approvals/ and no code reads them;
-- invalidation on a new filing was prose. This table is the one place a certification lives: one row per certified cell,
-- loaded from a signed certificate by `scrooner_pipeline.certification.display_cert_load` (dry-run default).
-- Grain = the 32 individually filing-checked drawn cells of a certificate (data point x period end x grain), tied to the
-- coverage file's sha256 (the sample hash) and the proof_version (= resolver_version string) the draw was made under.
-- Depends on 0130 (analytics.cell_display_state), applied live 2026-11-17.
--
-- INVALIDATION: by JOIN, not trigger (decision, justified):
--  * analytics.display_cell_certificate_status is evaluated at read time against live data, so it can never lag; a
--    trigger on core.filing would add work to the nightly ingest hot path, fire per row, and miss a proof-version bump
--    (which is a change of a text column in cell_display_state, not an event on certificate rows);
--  * the status is exact and re-derivable; analytics.invalidate_display_cell_certificates() then materialises the
--    non-valid rows into invalidated_at + reason once (audit history), run by the loader and the nightly refresh.
--  status order: invalidated, unverifiable_accession, stale_display (cell no longer SHOWN_VALUE), stale_proof (display
--  resolver_version differs from the certificate's proof_version), stale_filing (a later annual filing prints the period
--  within 3 fiscal years: a possible restatement), else valid.
--
-- company_certification (0097) is DEPRECATED, not dropped: the retired suite code still writes it. A derived company view
-- replaces it for every reader: analytics.company_certification_derived.
-- ROLLBACK: drop view analytics.company_certification_derived; drop function analytics.invalidate_display_cell_certificates(bigint);
--           drop view analytics.display_cell_certificate_status; drop table analytics.display_cell_certificate;
create table if not exists analytics.display_cell_certificate (
    id               bigint generated always as identity primary key,
    company_id       bigint      not null references core.company (id),
    data_point       text        not null check (btrim(data_point) <> ''),
    period_end       date        not null,
    grain            text        not null check (grain in ('FY', 'I')),
    fiscal_year      integer,
    shown_value      numeric     not null,
    proof_version    text        not null check (btrim(proof_version) <> ''),
    accession        text        not null check (accession ~ '^[0-9]{10}-[0-9]{2}-[0-9]{6}$'),
    r_page           text,
    tag              text,
    sample_hash      text        not null check (sample_hash ~ '^[0-9a-f]{64}$'),
    draw_seed        text,
    certificate_path text        not null check (btrim(certificate_path) <> ''),
    approver         text        not null check (btrim(approver) <> ''),
    certified_at     timestamptz not null,
    invalidated_at   timestamptz,
    invalidated_reason text,
    loaded_at        timestamptz not null default now(),
    constraint display_cell_certificate_invalidation_pair
        check ((invalidated_at is null) = (invalidated_reason is null)),
    unique (company_id, data_point, period_end, grain, sample_hash)
);

create index if not exists display_cell_certificate_company_idx
    on analytics.display_cell_certificate (company_id);

comment on table analytics.display_cell_certificate is
    'Single source of truth for display certification: one row per individually filing-checked cell of a signed certificate (sample_hash = coverage file sha256, proof_version = resolver_version). Loaded from the certificate; invalidated by analytics.invalidate_display_cell_certificates().';

create or replace view analytics.display_cell_certificate_status as
select
    c.*,
    case
        when c.invalidated_at is not null then 'invalidated'::text
        when f.id is null then 'unverifiable_accession'::text
        when ds.display is distinct from 'SHOWN_VALUE' then 'stale_display'::text
        when ds.resolver_version is distinct from c.proof_version then 'stale_proof'::text
        when exists (
            select 1 from core.filing n
            where n.company_id = c.company_id
              and n.form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A')
              and n.filing_date > f.filing_date
              and n.period_of_report >= c.period_end
              and n.period_of_report <= (c.period_end + interval '3 years')::date
        ) then 'stale_filing'::text
        else 'valid'::text
    end as status
from analytics.display_cell_certificate c
left join core.filing f on f.accession_number = c.accession
left join analytics.cell_display_state ds
       on ds.company_id = c.company_id and ds.data_point = c.data_point
      and ds.period_end = c.period_end and ds.grain = c.grain;

-- Materialise invalidations once (idempotent). p_company_id null = all companies. Returns rows newly invalidated.
create or replace function analytics.invalidate_display_cell_certificates(p_company_id bigint default null)
returns bigint
language plpgsql
set search_path = pg_catalog, analytics, core
as $$
declare
    n bigint;
begin
    with stale as (
        select id, status from analytics.display_cell_certificate_status
        where invalidated_at is null and status <> 'valid'
          and (p_company_id is null or company_id = p_company_id)
    ), u as (
        update analytics.display_cell_certificate c
           set invalidated_at = now(), invalidated_reason = stale.status
          from stale where c.id = stale.id
        returning 1
    )
    select count(*) into n from u;
    return n;
end;
$$;

-- Company level, derived: a company is display_certified when its newest certificate (latest sample_hash by
-- certified_at) has every cell valid; stale when some are not; never uncertified rows (absent = no row).
create or replace view analytics.company_certification_derived as
with latest as (
    select distinct on (company_id) company_id, sample_hash, certified_at
    from analytics.display_cell_certificate_status
    order by company_id, certified_at desc, sample_hash
)
select
    l.company_id,
    l.sample_hash,
    l.certified_at,
    count(*)                                   as cells,
    count(*) filter (where s.status = 'valid') as valid_cells,
    case when count(*) filter (where s.status <> 'valid') = 0
         then 'display_certified'::text else 'stale'::text end as state
from latest l
join analytics.display_cell_certificate_status s
  on s.company_id = l.company_id and s.sample_hash = l.sample_hash
group by l.company_id, l.sample_hash, l.certified_at;

comment on table analytics.company_certification is
    'DEPRECATED 2026-11-21 (0132): written only by the retired I1-I11 suite, 0 rows, never sets certified. Read analytics.company_certification_derived (from analytics.display_cell_certificate) instead.';
