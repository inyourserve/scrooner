-- Audit trail for normalizer/conflict_latest_filed.py: every core.fact it made
-- authoritative when a period's filings disagreed and none was authoritative
-- (Stage 2e leaves those groups with no authoritative row by design).
-- One row per flipped fact, so the change is queryable and undoable:
--   update core.fact set is_authoritative = false
--   where id in (select fact_id from core.fact_conflict_resolution where rule = '<rule>');
create table if not exists core.fact_conflict_resolution (
    fact_id     bigint primary key references core.fact (id) on delete cascade,
    rule        text not null,
    -- Number of facts competing in the group and the spread of their values,
    -- kept so a reviewer can tell a rounding wobble from a real restatement.
    group_size  integer not null,
    value_min   numeric not null,
    value_max   numeric not null,
    resolved_at timestamptz not null default now()
);

create index if not exists idx_fact_conflict_resolution_rule
    on core.fact_conflict_resolution (rule);

comment on table core.fact_conflict_resolution is
    'Facts made authoritative by a documented tie-break rule where Stage 2e found disagreeing filings. See normalizer/conflict_latest_filed.py.';
