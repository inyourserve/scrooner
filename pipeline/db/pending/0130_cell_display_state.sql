-- 0130: per-cell display state (founder approval 2026-11-17, doc 02: "the per-cell display-state migration for hidden
-- rows and years"). Supersedes the dropped 0127 shown_from (listed in SKIPPED.txt).
-- One row per (company, data point, period end, grain): whether the stock page SHOWS the cell, hides its row or its
-- year, or the cell is OUT of the company's template / still OPEN work. Written by the top-100 coverage export
-- (`top100_coverage.py --write-display-state`), scoped delete-then-insert per company, never by hand.
-- hide_class value set = HIDE_ELIGIBLE in pipeline/src/scrooner_pipeline/mapper/top100_coverage.py; it is required
-- exactly when display is HIDDEN_ROW or HIDDEN_YEAR (a pipeline-state reason is never a hide: it stays OPEN).
-- ROLLBACK: drop table analytics.cell_display_state;  (nothing references it)
create table if not exists analytics.cell_display_state (
    company_id       bigint      not null references core.company (id),
    data_point       text        not null check (btrim(data_point) <> ''),
    period_end       date        not null,
    grain            text        not null check (grain in ('FY', 'I')),
    display          text        not null
        check (display in ('SHOWN_VALUE', 'HIDDEN_ROW', 'HIDDEN_YEAR', 'OUT', 'OPEN')),
    hide_class       text
        check (hide_class in ('structural_not_presented', 'line_presented_combined', 'pre_filing', 'verified_absent')),
    evidence_accession text,
    evidence         text,
    r_page           text,
    resolver_version text,
    run_id           text,
    updated_at       timestamptz not null default now(),
    primary key (company_id, data_point, period_end, grain),
    constraint cell_display_state_hide_class_iff_hidden
        check ((display in ('HIDDEN_ROW', 'HIDDEN_YEAR')) = (hide_class is not null))
);

create index if not exists cell_display_state_company_idx
    on analytics.cell_display_state (company_id);

comment on table analytics.cell_display_state is
    'Per-cell display state written by the top-100 coverage export: SHOWN_VALUE / HIDDEN_ROW / HIDDEN_YEAR / OUT / OPEN, with the hide class and evidence for hidden cells. The stock page reads it to hide rows and years.';
