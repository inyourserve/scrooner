-- Metric Plausibility Check (2026-09-27) -- the code-side implementation
-- of doc/reference/47_Scrooner_Metric_Plausibility_Gates.md's CRITICAL/
-- WATCH bounds table. Same shape as analytics.timeseries_outlier_check
-- (0054) -- zero external calls, checks our OWN already-computed
-- analytics.metric_value against a plausible-range table, not a second
-- source. Scoped to each company's MOST RECENT value per metric (what a
-- real user would actually see on the company page/screener today), not
-- every historical period -- keeps the table bounded and matches what
-- doc 47 itself was framed around ("the real number a user would see").

create table if not exists analytics.metric_plausibility_check (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    metric_definition_id bigint not null references analytics.metric_definition(id),
    period_label text,
    period_end date,
    value numeric not null,
    severity text not null check (severity in ('ok', 'watch', 'critical')),
    note text,
    checked_at timestamptz not null default now(),
    unique (company_id, metric_definition_id)
);

create index if not exists idx_metric_plausibility_check_severity on analytics.metric_plausibility_check (severity) where severity <> 'ok';

-- Extend the unified incident view (0055) with this 6th checker --
-- severity vocabulary: ok unchanged, watch -> minor, critical -> major
-- (deliberately not "critical" in the shared vocabulary too -- a
-- plausibility-bound violation is strong evidence of a bug, matching
-- frames_consistency_check's own "mismatch -> major" precedent, but SEC
-- Frames disagreeing with our own re-served data is a strictly stronger
-- signal than an internal range check, so this checker doesn't claim
-- the same top severity tier).
create or replace view analytics.data_incident as
select
    'data_sanity'::text as source_system,
    d.company_id,
    c.company_name,
    d.metric_name as metric_or_concept,
    null::date as period_end,
    d.our_value,
    d.external_value as reference_value,
    d.pct_diff,
    case d.severity
        when 'missing_ours' then 'missing'
        when 'missing_external' then 'missing'
        else d.severity
    end as severity,
    d.note,
    d.checked_at
from analytics.data_sanity_check d
join core.company c on c.id = d.company_id

union all

select
    'yfinance_financials'::text as source_system,
    f.company_id,
    c.company_name,
    cc.name as metric_or_concept,
    f.period_end,
    f.our_value,
    f.yfinance_value as reference_value,
    f.pct_diff,
    case f.severity when 'missing_ours' then 'missing' else f.severity end as severity,
    f.note,
    f.checked_at
from analytics.statement_comparison_finding f
join core.company c on c.id = f.company_id
join analytics.canonical_concept cc on cc.id = f.canonical_concept_id

union all

select
    'sec_frames'::text as source_system,
    fr.company_id,
    c.company_name,
    cc.name as metric_or_concept,
    fr.period_end,
    fr.our_value,
    fr.frames_value as reference_value,
    fr.pct_diff,
    case fr.severity
        when 'mismatch' then 'major'
        when 'missing_ours' then 'missing'
        else fr.severity
    end as severity,
    ('SEC accession ' || coalesce(fr.accession, 'unknown')) as note,
    fr.checked_at
from analytics.frames_consistency_check fr
join core.company c on c.id = fr.company_id
join analytics.canonical_concept cc on cc.id = fr.canonical_concept_id

union all

select
    'timeseries'::text as source_system,
    t.company_id,
    c.company_name,
    cc.name as metric_or_concept,
    t.period_end,
    t.current_value as our_value,
    t.prior_value as reference_value,
    (t.yoy_ratio * 100) as pct_diff,
    case t.severity
        when 'outlier' then 'minor'
        when 'sign_violation' then 'major'
        else t.severity
    end as severity,
    (t.fiscal_period || ' ' || t.fiscal_year::text || ' vs. prior year') as note,
    t.checked_at
from analytics.timeseries_outlier_check t
join core.company c on c.id = t.company_id
join analytics.canonical_concept cc on cc.id = t.canonical_concept_id

union all

select
    'freshness'::text as source_system,
    fc.company_id,
    c.company_name,
    'data_freshness'::text as metric_or_concept,
    fc.our_latest_period_end as period_end,
    null::numeric as our_value,
    null::numeric as reference_value,
    fc.days_stale::numeric as pct_diff,
    case fc.severity when 'stale' then 'minor' when 'unknown' then 'missing' else fc.severity end as severity,
    ('yfinance most recent quarter: ' || coalesce(fc.yfinance_most_recent_quarter::text, 'unknown')) as note,
    fc.checked_at
from analytics.data_freshness_check fc
join core.company c on c.id = fc.company_id

union all

select
    'plausibility'::text as source_system,
    p.company_id,
    c.company_name,
    md.metric_name as metric_or_concept,
    p.period_end,
    p.value as our_value,
    null::numeric as reference_value,
    null::numeric as pct_diff,
    case p.severity when 'watch' then 'minor' when 'critical' then 'major' else p.severity end as severity,
    p.note,
    p.checked_at
from analytics.metric_plausibility_check p
join core.company c on c.id = p.company_id
join analytics.metric_definition md on md.id = p.metric_definition_id;
