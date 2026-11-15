-- Display coverage (founder decision 2026-11-16, doc 02): a row the company never reports is hidden for that company,
-- and years before the company's first periodic filing that presents them are hidden. Both ride on the per-company
-- sector template (0120), which the product page does not read yet:
--   row hide   = a current-template row with in_template = false, source = 'company_override', reason = the evidence
--                (accessions checked, how); no schema change needed.
--   year hide  = this nullable column: the first period_end shown for that company x data point. The page shows only
--                cells whose period end is on or after shown_from; null = no year hidden.
-- Written 2026-11-16 (Data Engineer). NOT applied; applying it needs the founder's typed words. Lives in
-- pipeline/db/pending/ because 0124-0126 are not on main and the contiguity check (scripts/check_migrations.py) would fail;
-- move it into migrations/ once they land.
alter table analytics.company_data_point_template
    add column if not exists shown_from date,
    add column if not exists shown_from_basis text;

comment on column analytics.company_data_point_template.shown_from is
    'First period_end shown for this company x data point (display rule 2026-11-16: years before the first periodic filing that presents them are hidden). Null = none hidden.';
comment on column analytics.company_data_point_template.shown_from_basis is
    'Evidence for shown_from: the earliest periodic filing (accession) that presents the first shown year. Required when shown_from is set.';

alter table analytics.company_data_point_template
    drop constraint if exists company_data_point_template_shown_from_basis_required;
alter table analytics.company_data_point_template
    add constraint company_data_point_template_shown_from_basis_required check (
        shown_from is null or coalesce(btrim(shown_from_basis), '') <> ''
    );
