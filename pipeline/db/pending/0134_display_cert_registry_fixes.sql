-- 0134: display-cell certificate registry fixes (found live 2026-11-21/22 after 0132 was applied).
-- (Numbered 0134: 0133 is claimed by cell_display_state_after_tax_class in doc 53.)
-- 1. hide_class '' vs NULL: the loader stored '' for SHOWN_VALUE cells, so `ds.hide_class is distinct from c.hide_class`
--    (cell_display_state holds NULL) read every shown JNJ cell (462 live, company 1164) as stale_display. Data fix first,
--    then a CHECK so an optional text column is NULL or non-blank. The loader normalises '' to NULL (display_cert_load.py).
--    The view's hide_class rule is unchanged (a hide-class change stays a live, non-permanent status, ruling 8).
-- 2. Performance: the restatement EXISTS reached fsn.value (about 39M rows) through a filing range on accepted alone
--    (fsn.filing was not restricted to the company): planner cost 984,902 for all companies and 327,722 for one company;
--    the GILD load hit its 120 s statement_timeout in invalidate_display_cell_certificates. Now: an undimensioned branch with
--    a literal dim_id = 0 (partial idx_fsn_value_series), a dimensioned branch driven by the company's later filings
--    (idx_fsn_filing_company_accepted) probing fsn.value by its unique key, and lf.company_id = c.company_id in both.
--    No new index on fsn.value. The view's column list is unchanged.
-- ROLLBACK: re-apply the 0132 definitions of the view and function; alter table analytics.display_cell_certificate
--           drop constraint display_cell_certificate_optional_text_nonblank;

update analytics.display_cell_certificate set hide_class = null where btrim(hide_class) = '';
update analytics.display_cell_certificate set reason_code = null where btrim(reason_code) = '';
update analytics.display_cell_certificate set r_page = null where btrim(r_page) = '';
update analytics.display_cell_certificate set tag = null where btrim(tag) = '';
update analytics.display_cell_certificate set detector_version = null where btrim(detector_version) = '';
update analytics.display_cell_certificate set resolver = null where btrim(resolver) = '';
update analytics.display_cell_certificate set code_sha = null where btrim(code_sha) = '';
update analytics.display_cell_certificate set draw_seed = null where btrim(draw_seed) = '';

alter table analytics.display_cell_certificate
    add constraint display_cell_certificate_optional_text_nonblank
    check ((hide_class is null or btrim(hide_class) <> '')
       and (reason_code is null or btrim(reason_code) <> '')
       and (r_page is null or btrim(r_page) <> '')
       and (tag is null or btrim(tag) <> '')
       and (detector_version is null or btrim(detector_version) <> '')
       and (resolver is null or btrim(resolver) <> '')
       and (code_sha is null or btrim(code_sha) <> '')
       and (draw_seed is null or btrim(draw_seed) <> ''));

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
        when c.display = 'SHOWN_VALUE' and (
            -- undimensioned keys: literal dim_id = 0 so the partial idx_fsn_value_series (company_id, tag_id, ddate, qtrs) is usable
            exists (
                select 1
                from jsonb_to_recordset(c.restate_keys) as k(tag text, dims text)
                join fsn.tag bt on bt.tag = k.tag
                join fsn.filing bf on bf.accession = c.accession
                join fsn.value base on base.filing_id = bf.id and base.tag_id = bt.id and base.ddate = c.period_end
                                   and base.qtrs = case c.grain when 'I' then 0 else 4 end and base.dim_id = 0
                join fsn.tag lt on lt.tag = bt.tag
                join fsn.value later on later.company_id = c.company_id and later.tag_id = lt.id and later.ddate = base.ddate
                                    and later.qtrs = base.qtrs and later.dim_id = 0 and later.uom = base.uom
                                    and later.iprx = base.iprx and later.coreg = base.coreg and later.filing_id <> base.filing_id
                join fsn.filing lf on lf.id = later.filing_id and lf.company_id = c.company_id and lf.accepted > bf.accepted
                                  and lf.form ~ '^(10-K|10-Q|20-F|40-F)'
                where coalesce(k.dims, '') = ''
                  and later.value is distinct from base.value
            )
            -- dimensioned keys: walk the company's later periodic filings (idx_fsn_filing_company_accepted) and probe fsn.value by its unique key
            or exists (
                select 1
                from jsonb_to_recordset(c.restate_keys) as k(tag text, dims text)
                join fsn.tag bt on bt.tag = k.tag
                join fsn.dim d on d.segments = k.dims and d.id <> 0
                join fsn.filing bf on bf.accession = c.accession
                join fsn.value base on base.filing_id = bf.id and base.tag_id = bt.id and base.ddate = c.period_end
                                   and base.qtrs = case c.grain when 'I' then 0 else 4 end and base.dim_id = d.id
                join fsn.tag lt on lt.tag = bt.tag
                join fsn.filing lf on lf.company_id = c.company_id and lf.accepted > bf.accepted and lf.id <> bf.id
                                  and lf.form ~ '^(10-K|10-Q|20-F|40-F)'
                join fsn.value later on later.filing_id = lf.id and later.tag_id = lt.id and later.ddate = base.ddate
                                    and later.qtrs = base.qtrs and later.uom = base.uom and later.dim_id = base.dim_id
                                    and later.iprx = base.iprx and later.coreg = base.coreg
                where later.value is distinct from base.value
            )
        ) then 'stale_restated'::text
        else 'valid'::text
    end as status
from analytics.display_cell_certificate c
join latest l on l.company_id = c.company_id
left join core.filing f on f.accession_number = c.accession
left join analytics.cell_display_state ds
       on ds.company_id = c.company_id and ds.data_point = c.data_point
      and ds.period_end = c.period_end and ds.grain = c.grain
;

-- Same contract as 0132. The status is computed once per candidate row (a materialised CTE restricted to open cells and
-- the company first), so the restatement subplans run once, not again in the filter.
create or replace function analytics.invalidate_display_cell_certificates(p_company_id bigint default null)
returns bigint
language plpgsql
set search_path = pg_catalog, analytics, core, fsn
as $$
declare
    n bigint;
begin
    with cand as materialized (
        select id, status from analytics.display_cell_certificate_status
        where invalidated_at is null
          and (p_company_id is null or company_id = p_company_id)
    ), stale as (
        select id, status from cand where status in ('stale_restated', 'superseded')
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
