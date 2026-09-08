-- Unified Data Incident view (2026-09-08, doc/data-moat/scope/
-- internal-auto-fixer.md, evaluated then built). Normalizes the 5
-- checker tables built today (Data Sanity, yfinance Financials, SEC
-- Frames, Time-Series Self-Consistency, Freshness) into ONE consistent
-- shape -- a live VIEW (no sync lag, no duplicate storage, always
-- reflects each checker's current state) rather than a materialized
-- copy.
--
-- Deliberately NOT six separate LLM agents (per the scope doc's own
-- admission: "you don't necessarily need six separate LLM processes").
-- This is the "Watcher" + "Finding/Incident" layer of that vision,
-- expressed as plain deterministic SQL, matching doc 05's "determinism
-- before AI magic" -- the Investigator (sanity/tag_investigator.py)
-- already exists; this view is what makes it (and a future dashboard/
-- verifier) able to reason across all 4 checkers uniformly instead of
-- querying 4 differently-shaped tables by hand every time.
--
-- Severity normalized to one shared vocabulary (ok/minor/major/
-- critical/missing) -- each source's own vocabulary mapped explicitly,
-- not guessed:
--   data_sanity_check:            ok/minor/major/critical unchanged; missing_ours/missing_external -> missing
--   statement_comparison_finding: ok/minor/major unchanged; missing_ours -> missing
--   frames_consistency_check:     ok unchanged; mismatch -> major (SEC's own re-served data disagreeing
--                                 is the highest-confidence signal of any checker); missing_ours -> missing
--   timeseries_outlier_check:     ok unchanged; outlier -> minor (a "worth a look" signal); sign_violation -> major
--                                 (a concept that structurally can never be negative, IS -- unambiguous)
--   data_freshness_check:         ok unchanged; stale -> minor; unknown -> missing

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
join core.company c on c.id = fc.company_id;
