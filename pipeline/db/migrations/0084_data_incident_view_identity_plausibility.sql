-- Wire the 2 newest checker systems into the Unified Data Incident view
-- (2026-10-03, by direct user request: "wire everything in the internal
-- dashboard"). Migration 0055 (2026-09-08) unioned the 5 checkers that
-- existed then (data_sanity/yfinance_financials/sec_frames/timeseries/
-- freshness) -- accounting-identity self-consistency (doc 48, built
-- 2026-09-30) and metric-plausibility gates (doc 47, built 2026-09-27)
-- were both built AFTER this view and never added, so incidents/
-- dashboard.py's "one place to look" property silently stopped being
-- true for the 2 newest, most-recently-active checkers -- confirmed live
-- before writing this: the view's own UNION ALL still only listed 5
-- sources.
--
-- Severity mapping, each explicit, not guessed:
--   identity_check_failure:    every stored row IS a failure (a passing
--                               check is only ever counted in identity_
--                               check_summary, never given its own
--                               failure row) -- mapped to 'major'
--                               uniformly, same treatment sec_frames'
--                               own "mismatch" severity already gets.
--   metric_plausibility_check: 'critical' unchanged; 'watch' -> 'minor'
--                               (a "worth a look" signal, same shape
--                               timeseries' own 'outlier' already gets);
--                               'ok' unchanged.
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
    'accounting_identity'::text as source_system,
    idf.company_id,
    c.company_name,
    (idf.identity_name || ' (' || idf.layer || ')') as metric_or_concept,
    idf.period_end,
    idf.actual as our_value,
    idf.expected as reference_value,
    (idf.rel_gap * 100) as pct_diff,
    'major'::text as severity,
    'self-consistency failure (not vs. an external source)'::text as note,
    idf.checked_at
from analytics.identity_check_failure idf
join core.company c on c.id = idf.company_id

union all

select
    'metric_plausibility'::text as source_system,
    mpc.company_id,
    c.company_name,
    md.metric_name as metric_or_concept,
    mpc.period_end,
    mpc.value as our_value,
    null::numeric as reference_value,
    null::numeric as pct_diff,
    case mpc.severity when 'watch' then 'minor' else mpc.severity end as severity,
    mpc.note,
    mpc.checked_at
from analytics.metric_plausibility_check mpc
join core.company c on c.id = mpc.company_id
join analytics.metric_definition md on md.id = mpc.metric_definition_id;
