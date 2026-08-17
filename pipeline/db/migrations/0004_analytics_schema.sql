-- Analytics schema for the Mapper & Metrics Engine. See
-- scrooner/doc/11_Scrooner_Mapper_Metrics_Execution_Plan.md for the design
-- rationale. The Mapper reads `core` (never writes it) and writes only to
-- `analytics` -- same one-writer-per-schema discipline as raw (Collector)
-- and core (Normalizer).
--
-- Full logical schema created up front, same precedent as 0001/0003 --
-- populated incrementally, stage by stage (3a canonical_concept +
-- concept_mapping now; 3c-3d bring metric_definition/metric_value online
-- later), not all at once.

create schema if not exists analytics;

-- Scrooner's own concept vocabulary -- 17 entries per doc 11's resolved
-- list, bounded by the same guardrail as the 18-metric list itself. Never
-- an issuer tag (that's core.concept).
--
-- combination_mode resolves a real ambiguity found while designing this
-- (doc 11 problem #3): a canonical concept's mapped tags are either
-- ALTERNATIVES (revenue -- a company reports under exactly one of several
-- possible tags depending on taxonomy era/industry; try priority order,
-- first match with data wins) or SUMMANDS (total_debt -- a company can
-- report several simultaneously, e.g. NKE's LongTermDebtCurrent +
-- LongTermDebtNoncurrent + ShortTermBorrowings all at once; sum every
-- mapped tag this company has data for). A resolver needs to know which
-- behavior applies per concept, not guess from the mapping list alone.
create table if not exists analytics.canonical_concept (
    id               bigint generated always as identity primary key,
    name             text not null unique,
    statement        text not null check (statement in ('income_statement', 'balance_sheet', 'cash_flow')),
    combination_mode text not null check (combination_mode in ('first_match', 'sum')),
    description      text
);

-- Ordered, human-curated list of which core.concept (issuer tag) rows
-- count as a given canonical concept. priority matters only for
-- first_match concepts (lowest tried first); ignored (all summed) for sum
-- concepts. confidence follows doc 05's data-quality methodology --
-- 'provisional' entries still participate in resolution (so real coverage
-- happens immediately) but are flagged for review; 'rejected' entries are
-- explicitly excluded and never re-suggested by future coverage-gap
-- discovery (doc 11's scaling section).
create table if not exists analytics.concept_mapping (
    id                  bigint generated always as identity primary key,
    canonical_concept_id bigint not null references analytics.canonical_concept (id),
    concept_id          bigint not null references core.concept (id),
    priority            int not null default 100,
    confidence          text not null default 'provisional'
                        check (confidence in ('approved', 'provisional', 'rejected')),
    notes                text,
    created_at           timestamptz not null default now(),
    unique (canonical_concept_id, concept_id)
);

-- One row per metric per formula version -- never mutated once it has
-- metric_value rows depending on it (doc 04: "version metric definitions
-- ... so historical outputs are reproducible"). A formula change creates a
-- new formula_version; old metric_value rows keep citing the version that
-- produced them.
create table if not exists analytics.metric_definition (
    id                 bigint generated always as identity primary key,
    metric_name        text not null,
    formula_version    int not null default 1,
    formula_description text not null,
    requires_price     boolean not null default false,
    status             text not null default 'active' check (status in ('active', 'deprecated')),
    created_at         timestamptz not null default now(),
    unique (metric_name, formula_version)
);

-- Structured formula inputs -- not a jsonb blob, so "what does this metric
-- depend on" is a real, queryable join (doc 05: "one definition, formula,
-- inputs... per metric"). `role` stays free text rather than a rigid enum
-- deliberately -- most metrics are simple numerator/denominator ratios,
-- but ROIC's exact formula is still Stage 3c's to pin down with evidence
-- (doc 02), and a fixed enum would force that decision prematurely at
-- migration time instead of when Stage 3c actually has it.
create table if not exists analytics.metric_definition_input (
    id                    bigint generated always as identity primary key,
    metric_definition_id  bigint not null references analytics.metric_definition (id),
    canonical_concept_id  bigint not null references analytics.canonical_concept (id),
    role                  text not null
);

-- Stage 3b's actual persisted output -- one resolved value per company/
-- canonical_concept/period, applying concept_mapping's priority-ordered
-- fallback (combination_mode='first_match') or summation
-- (combination_mode='sum') over core.fact. Unlike metric_value below,
-- THIS table can legitimately FK to core.period -- Stage 3b resolves
-- values for periods the Normalizer already materialized, it doesn't
-- invent new ones (TTM windows are Stage 3e's job, downstream of this).
-- Only successfully-resolved (concept, period) pairs get a row; an
-- unresolved one is absence, not a null-value row -- coverage gaps stay
-- visible via a query over core.fact/concept_mapping directly (Stage 3a's
-- coverage_report), not a second null-tracking mechanism duplicating it.
create table if not exists analytics.canonical_fact (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null references core.company (id),
    canonical_concept_id  bigint not null references analytics.canonical_concept (id),
    period_id             bigint not null references core.period (id),
    value                 numeric not null,
    source_fact_ids       bigint[] not null,
    resolved_at           timestamptz not null default now(),
    unique (company_id, canonical_concept_id, period_id)
);

-- One computed value per company/period/metric/formula-version. NOT a FK
-- to core.period -- a metric's period (a fiscal quarter, a TTM window) is
-- an analytics-layer concept the Mapper computes, not something the
-- Normalizer already materialized. Self-contained so a TTM window never
-- needs core.period relaxed or written to from here (Mapper writes only
-- `analytics`, never `core`).
create table if not exists analytics.metric_value (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null references core.company (id),
    metric_definition_id  bigint not null references analytics.metric_definition (id),
    period_start          date not null,
    period_end            date not null,
    period_label          text not null check (period_label in ('FY', 'Q1', 'Q2', 'Q3', 'Q4', 'TTM')),
    value                 numeric,
    data_as_of            timestamptz not null default now(),
    is_null_reason        text,
    source_fact_ids       bigint[],
    created_at            timestamptz not null default now(),
    unique (company_id, metric_definition_id, period_start, period_end, period_label)
);
create index if not exists idx_metric_value_company_metric on analytics.metric_value (company_id, metric_definition_id);
