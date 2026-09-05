-- analytics.concept_parser_result (doc 42, Parser 3 architecture, 2026-09-05)
--
-- The registry the multi-parser architecture needs: for a (company,
-- canonical_concept) pair that plain XBRL tag resolution (resolve.py +
-- concept_mapping) could NOT resolve, this table records which
-- dedicated parser (revenue_parser.py, and future ones) found a value,
-- via what mechanism, and from exactly which filing/report -- so a
-- future rerun knows which parser already succeeded (skip re-fetching)
-- or already tried and found nothing (skip re-trying every parser
-- blindly), and so every value here is traceable back to its source
-- filing the same way analytics.canonical_fact's own lineage works for
-- XBRL-tag-resolved facts.
--
-- Deliberately NOT the same table as analytics.canonical_fact --
-- resolve.py's own frozen resolution logic (doc 11's boundary table:
-- "the Mapper resolves XBRL tags") stays the ONLY writer to
-- canonical_fact. A value found by reading a rendered report's own
-- display label (not a recognized tag) is a genuinely different kind
-- of evidence, so it gets its own table with its own provenance
-- columns rather than being disguised as a resolved XBRL fact.
-- Downstream readers (screener, company page) that want "the best
-- available value" read canonical_fact FIRST, this table as a
-- fallback -- the same "prefer resolved value A, else B" idiom already
-- used for total_debt_resolved/shares_outstanding_fallback.

create table if not exists analytics.concept_parser_result (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    parser_name text not null,
    value numeric not null,
    period_end date,
    source_form text,
    source_accession text,
    source_report text,
    created_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id)
);

create index if not exists idx_concept_parser_result_concept
    on analytics.concept_parser_result (canonical_concept_id);

-- Also tracks a parser's negative result (considered, found nothing
-- safe to store) -- without this, a rerun can't distinguish "never
-- tried this company" from "tried, correctly found no revenue row" and
-- would re-fetch the same company's filing every single run forever.
create table if not exists analytics.concept_parser_attempt (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    parser_name text not null,
    outcome text not null check (outcome in ('matched', 'no_report', 'no_row_matched', 'errored')),
    attempted_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id, parser_name)
);
