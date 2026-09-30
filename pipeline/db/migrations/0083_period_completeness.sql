-- Period completeness (2026-09-30). The tag library says whether a company
-- has a concept at all; nothing said WHICH quarters are missing and why.
-- Airbnb's Q4 2025 net income was blank because its FY2025 value was filed
-- twice with a rounding difference ($2,511,000,000 vs $2,511,277,000), both
-- marked non-authoritative, so Q4 could not be derived and P/E went blank.
-- Found by hand, like the 348 never-normalized filings and Cardinal Health's
-- 10-Q missing from SEC's own feed.
--
-- Expected periods come from the company's own 10-Q/10-K filings
-- (period_of_report), not a calendar. Built by
-- sanity/period_completeness.py. Each gap cause also lands in
-- analytics.company_data_finding (evidence->>'source' = 'period_completeness'),
-- where a cause that stops occurring is marked fixed, so the history of what
-- was wrong and when it was fixed is kept.

-- One row per missing (company, concept, expected period).
create table if not exists analytics.period_gap (
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    period_kind text not null check (period_kind in ('Q', 'Q4', 'FY', 'I')),
    period_end date not null,
    filing_id bigint not null references core.filing(id),
    gap_cause text not null check (gap_cause in (
        'filing_not_processed',  -- the filing has no core.fact rows, nothing newer processed either
        'not_in_sec_feed',       -- the filing has no core.fact rows, but later filings do
        'conflict_rounding',     -- filed values disagree by <= 0.1%, all marked non-authoritative
        'conflict_split',        -- filed values differ by a stock-split ratio (restated per-share values)
        'conflict_material',     -- filed values disagree by more
        'not_resolved',          -- an authoritative fact exists but no canonical value
        'q4_not_derived',        -- 10-K filed, FY present, Q4 not derived
        'quarter_not_derived',   -- only a year-to-date value filed, discrete quarter not derived
        'no_mapped_tag'          -- the filing has facts, none under a tag mapped to the concept
    )),
    detail jsonb,
    checked_at timestamptz not null default now(),
    primary key (company_id, canonical_concept_id, period_kind, period_end)
);
create index if not exists idx_period_gap_cause on analytics.period_gap (canonical_concept_id, gap_cause);
create index if not exists idx_period_gap_filing on analytics.period_gap (filing_id);

-- One row per checked (company, concept): expected vs present.
create table if not exists analytics.period_completeness (
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    expected integer not null,
    present integer not null,
    missing integer not null,
    first_expected date,
    last_expected date,
    checked_at timestamptz not null default now(),
    primary key (company_id, canonical_concept_id)
);

-- Gap causes ranked for fixing: which cause, which concept, how many
-- companies, and how much market cap they carry.
create or replace view analytics.period_gap_summary as
with latest_mcap as (
    select distinct on (mv.company_id) mv.company_id, mv.value as market_cap
    from analytics.metric_value mv
    where mv.metric_definition_id = (select id from analytics.metric_definition where metric_name = 'market_cap')
      and mv.value is not null
    order by mv.company_id, mv.period_end desc
),
per_company as (
    select canonical_concept_id, gap_cause, company_id,
           count(*) as missing_periods,
           count(*) filter (where period_end >= current_date - 450) as missing_recent
    from analytics.period_gap
    group by 1, 2, 3
)
select cc.name as concept,
       p.gap_cause,
       sum(p.missing_periods) as missing_periods,
       count(*) as companies,
       sum(p.missing_recent) as missing_last_15_months,
       sum(m.market_cap) as market_cap_affected
from per_company p
join analytics.canonical_concept cc on cc.id = p.canonical_concept_id
left join latest_mcap m on m.company_id = p.company_id
group by cc.name, p.gap_cause;
