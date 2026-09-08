-- Sanity-layer investigation + auto-fix (2026-09-08, explicit user
-- request: when the sanity layer finds a problem, trace the "fetcher
-- tree" for that specific company, find which tag is actually correct,
-- and store it).
--
-- Deliberately NOT a write into analytics.concept_mapping. A single
-- company's tag match is real evidence for THAT company, but is NOT
-- evidence a tag is safe to add globally -- resolve.py includes every
-- non-'rejected' confidence tier (checked directly: 'provisional' rows
-- are used in resolution exactly like 'approved' ones), so writing a new
-- concept_mapping row would immediately change resolve() output for
-- EVERY company reporting that tag, the exact single-company-generalized
-- risk doc 40's tag-coverage-library work already warned about
-- ("every candidate is a lead to investigate, never an approval").
--
-- Instead, two new tables:
--   analytics.data_sanity_investigation: an audit trail of what was
--     checked for a given (company, concept, period) sanity finding --
--     every candidate tag considered, its value, how it compared to the
--     external (yfinance) figure, and the outcome. Written whether or
--     not a fix was found, so "we looked and found nothing reconcilable"
--     is a distinct, visible, non-silent outcome from "never investigated."
--   analytics.canonical_fact_sanity_override: the actual fix, scoped to
--     exactly the (company_id, canonical_concept_id, period_id) the
--     investigation verified against an independent source -- never a
--     blast-radius-widening tag-priority change. Generalized (works for
--     any canonical_concept, not hardcoded to revenue) so a future
--     concept needing the same per-company correction reuses it directly,
--     the same "generalized, not hardcoded" idiom as concept_fallback.py's
--     ARITHMETIC_FALLBACKS/FALLBACK_PAIRS.
--
-- revenue_sanity_resolved: a THIRD concept (same "resolve() never
-- touches it, zero concept_mapping rows" idiom as total_debt_resolved/
-- gross_profit_resolved) that merges raw `revenue` with any override
-- found for that exact period -- override wins only where one exists,
-- since it was created specifically because the primary value was wrong.
-- Populated by sanity/tag_investigator.py's resolve_sanity_overrides(),
-- NOT resolve.py.

create table if not exists analytics.data_sanity_investigation (
    id bigint generated always as identity primary key,
    data_sanity_check_id bigint references analytics.data_sanity_check(id) on delete set null,
    company_id bigint not null references core.company(id),
    concept_name text not null,
    period_id bigint references core.period(id),
    candidate_taxonomy text,
    candidate_tag text,
    candidate_value numeric,
    external_value numeric,
    pct_diff_vs_external numeric,
    outcome text not null,  -- 'auto_fixed', 'needs_review', 'no_match_found'
    note text,
    investigated_at timestamptz not null default now(),
    unique (company_id, concept_name, period_id)
);

create table if not exists analytics.canonical_fact_sanity_override (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    period_id bigint not null references core.period(id),
    value numeric not null,
    source_fact_ids bigint[] not null,
    evidence text not null,
    investigated_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id, period_id)
);

insert into analytics.canonical_concept (name, statement, combination_mode, description)
values (
    'revenue_sanity_resolved', 'income_statement', 'first_match',
    'Prefers the raw revenue tag value, EXCEPT for a (company, period) the Data Sanity Layer investigated and found a specific, evidence-backed override for (analytics.canonical_fact_sanity_override) -- e.g. the resolve() authoritative-$0 bug (2026-09-07) where the priority-1 revenue tag has real near-consensus values marked non-authoritative only over a trivial cross-filing rounding difference, and a lower-priority tag''s spurious $0 won by default. Scoped to exactly the periods actually verified against an independent source (yfinance), never a blanket tag-priority change. Populated by sanity/tag_investigator.py, NOT resolve.py.'
)
on conflict (name) do nothing;
