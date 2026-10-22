-- WO-2 RU-1 (2026-10-22, Period Engineer): per-share values are never derived.
-- Additive only; backfills nothing. Not applied by its author (Release
-- Manager commits, Data Engineer applies after the reviewed dry-run).
--
-- 1. period_gap.gap_cause gains 'per_share_not_filed_separately'
--    (finding_type data_limit in sanity/period_completeness.py). A Q4 EPS/DPS
--    with the FY filed but no filed 3-month fact, or a Q2/Q3 per-share value
--    filed only as YTD, used to be labelled q4_not_derived / quarter_not_derived
--    (pipeline_bug). Derivation of per-share values is now refused by policy
--    (MSFT Q4 FY26 derived 4.80 vs filed 4.81, 8-K 0001193125-26-323632
--    Ex. 99.1; AAPL Q4 FY25 1.84 vs 1.85, 8-K 0000320193-25-000077 Ex. 99.1),
--    so the gap is that the filer reports no separate value. The code checks
--    this constraint at run time and keeps the old labels until it is applied.
--    The list below is the full allowed set (0083 + 0090 + the new value).
--
-- 2. analytics.canonical_fact_retired: archive for canonical_fact rows that a
--    reviewed run removes or replaces (first users: the RU-1 retirement of
--    derived-sourced *_resolved per-share Q2/Q3/Q4 rows, then the split-basis
--    writer, migration 0099). "Never delete" = archive-then-replace in the same
--    transaction (doc 49 section 7.3 item 7). Rollback of a run (restore_run)
--    deletes the keys it inserted, re-inserts the before-images of the rows it
--    replaced or removed, and stamps restored_at. No foreign key to
--    canonical_fact: the archived row is gone from it by design.
alter table analytics.period_gap drop constraint period_gap_gap_cause_check;
alter table analytics.period_gap add constraint period_gap_gap_cause_check check (gap_cause in (
    'filing_not_processed', 'not_in_sec_feed', 'conflict_rounding', 'conflict_split',
    'conflict_material', 'not_resolved', 'q4_not_derived', 'quarter_not_derived',
    'no_mapped_tag', 'unmapped_candidate_tag', 'no_line_item_filed',
    'per_share_not_filed_separately'
));

create table if not exists analytics.canonical_fact_retired (
    id                    bigint generated always as identity primary key,
    -- replaced / removed: the before-image of a row the run changed or removed;
    -- inserted: a key the run filled where no row existed (value columns null),
    -- so a rollback can delete it. Written only by mapper/canonical_archive.py.
    action                text not null check (action in ('replaced', 'removed', 'inserted')),
    canonical_fact_id     bigint not null,
    company_id            bigint not null references core.company (id),
    canonical_concept_id  bigint not null references analytics.canonical_concept (id),
    period_id             bigint not null references core.period (id),
    value                 numeric,
    source_fact_ids       bigint[],
    resolved_at           timestamptz,
    reason_code           text not null,
    run_id                text not null,
    basis_version         text,
    retired_at            timestamptz not null default now(),
    restored_at           timestamptz,
    check (action = 'inserted' or (value is not null and source_fact_ids is not null and resolved_at is not null))
);

create index if not exists idx_canonical_fact_retired_run
    on analytics.canonical_fact_retired (run_id);
create index if not exists idx_canonical_fact_retired_company
    on analytics.canonical_fact_retired (company_id, canonical_concept_id);
