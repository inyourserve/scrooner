-- Accounting identity checks + cost_of_revenue priority fix (2026-09-30) -- sanity/accounting_identity.py.
-- Coverage (does a value exist?) was the only data-quality score so far.
-- These tables measure CORRECTNESS: do a company's own numbers agree with
-- each other through identities that must hold (Assets = Liabilities +
-- Equity, Gross Profit = Revenue - Cost of Revenue, ...). Same idea as the
-- XBRL US Data Quality Committee rules and the internal-consistency gates
-- commercial fundamentals vendors run before publishing.
--
-- Stored as a per-(company, identity, layer) summary plus one row per
-- failing period only; passing periods are counted, not stored.

create table if not exists analytics.identity_check_summary (
    company_id bigint not null references core.company(id),
    identity_name text not null,
    layer text not null check (layer in ('display', 'raw')),
    checked integer not null,
    passed integer not null,
    worst_rel_gap numeric,
    checked_at timestamptz not null default now(),
    primary key (company_id, identity_name, layer)
);

create table if not exists analytics.identity_check_failure (
    company_id bigint not null references core.company(id),
    identity_name text not null,
    layer text not null check (layer in ('display', 'raw')),
    period_id bigint not null references core.period(id),
    period_end date not null,
    expected numeric,
    actual numeric,
    rel_gap numeric,
    operands jsonb not null,
    checked_at timestamptz not null default now(),
    primary key (company_id, identity_name, layer, period_id)
);

create index if not exists idx_identity_check_failure_identity
    on analytics.identity_check_failure (identity_name, layer);

-- One number per identity and layer: share of checkable company-periods
-- whose numbers agree. The population "data correctness %".
create or replace view analytics.identity_check_score as
select
    identity_name,
    layer,
    count(*) as companies,
    sum(checked) as checked,
    sum(passed) as passed,
    round(100.0 * sum(passed) / nullif(sum(checked), 0), 2) as pass_pct
from analytics.identity_check_summary
group by identity_name, layer;

-- ---------------------------------------------------------------------

-- cost_of_revenue: CostOfRevenue outranks CostOfGoodsSold (2026-09-29).
--
-- Both tags sat at priority 2, so resolve.py's first_match broke the tie
-- by concept_id (effectively arbitrary). CostOfGoodsSold is goods-only
-- for companies that also sell services: Microsoft FY2015 reports
-- CostOfGoodsSold 21.41B (product) and CostOfRevenue 33.04B (total), and
-- we picked the former, so gross_margin showed 77.1% instead of 64.7%.
--
-- Adjudicated with the gross-profit identity (sanity/accounting_identity.py)
-- over every company-period reporting both tags with different values:
-- CostOfRevenue satisfies Revenue - Cost = GrossProfit in 2,560 periods,
-- CostOfGoodsSold in 146 (94.6% vs 5.4%), across 172 companies.
-- The only tied first_match priority group in concept_mapping.
update analytics.concept_mapping cm
set priority = 3
from analytics.canonical_concept cc, core.concept con
where cc.id = cm.canonical_concept_id
  and con.id = cm.concept_id
  and cc.name = 'cost_of_revenue'
  and con.taxonomy = 'us-gaap'
  and con.tag = 'CostOfGoodsSold';

-- Guard against a future tie: first_match priorities must be unique per
-- concept so resolution never depends on concept_id order. A trigger, not
-- a unique index: sum-mode concepts (total_debt, total_debt_split)
-- legitimately share priorities, and a partial index cannot see
-- canonical_concept.combination_mode.
create or replace function analytics.check_first_match_priority_unique()
returns trigger language plpgsql as $$
begin
    if new.confidence <> 'rejected' and exists (
        select 1
        from analytics.concept_mapping cm
        join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
        where cc.combination_mode = 'first_match'
          and cm.canonical_concept_id = new.canonical_concept_id
          and cm.priority = new.priority
          and cm.id <> new.id
          and cm.confidence <> 'rejected'
    ) then
        raise exception 'first_match concept % already has a mapping at priority %',
            new.canonical_concept_id, new.priority;
    end if;
    return new;
end $$;

drop trigger if exists trg_first_match_priority_unique on analytics.concept_mapping;
create trigger trg_first_match_priority_unique
    before insert or update of priority, confidence, canonical_concept_id
    on analytics.concept_mapping
    for each row execute function analytics.check_first_match_priority_unique();
