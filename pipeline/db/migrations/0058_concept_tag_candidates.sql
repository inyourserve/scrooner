-- Retires pipeline/reference/xbrl_tag_coverage_library.json (doc 40,
-- built 2026-09-02) into the database -- 2026-09-08, direct user
-- instruction ("retire json, make everything into db as source of
-- truth"). The JSON file was a manually-triggered, point-in-time
-- research artifact (last built 2026-09-02, already stale relative to
-- today's other_income_expense_net addition and the CostsAndExpenses
-- rejection) sitting alongside, but never merged with, the DB-native
-- coverage matrix (analytics.data_point_registry/
-- company_data_point_coverage, doc 41) built 2026-09-06 and now
-- continuously rebuilt daily. This table is the one new piece the JSON
-- had that the coverage matrix didn't: candidate UNMAPPED tags per
-- concept, ranked by real company count, for widening decisions.
create table analytics.concept_tag_candidate (
    id bigint generated always as identity primary key,
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    taxonomy text not null,
    tag text not null,
    company_count integer not null,
    checked_at timestamptz not null default now(),
    unique (canonical_concept_id, taxonomy, tag)
);

create index idx_concept_tag_candidate_concept on analytics.concept_tag_candidate(canonical_concept_id);
