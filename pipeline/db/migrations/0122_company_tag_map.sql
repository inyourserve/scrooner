-- 0122: analytics.company_tag_map, the per-company tag -> concept map (founder order 2026-11-11:
-- "FSN for learning (which tag is what), SEC for mapping").
-- ROLLBACK: drop trigger trg_company_tag_map_no_overlap on analytics.company_tag_map; drop function
--   analytics.company_tag_map_no_overlap(); drop table analytics.company_tag_map;  (nothing else references it)
--   delete from analytics.canonical_concept where name in ('weighted_basic_shares',
--   'weighted_diluted_shares','cash_paid_for_interest','cash_paid_for_income_taxes','net_interest_income');  (only while unreferenced)
-- The FSN store (schema fsn, 0118) teaches, per company, which XBRL tag is which statement line (statement,
-- position, label, calc tree, era). This table records that decision per (company, taxonomy, tag, stmt, era).
-- Values still come from the SEC company-API facts in core.fact. For a company with rows here the mapper
-- (mapper/company_tag_map.py, rule company_tag_map.select@1, off by default) selects facts ONLY through this
-- table: no analytics.concept_mapping rule, no company_tag_preference override, no fallback applies.
--   sign                 : every value-bearing row ('concept', 'component') serves sign x fact value (multiplies the STORED core.fact value, never the printed sign; -1: gross
--                          interest reported under a net tag; a capitalized-interest component that subtracts).
--   serve_note           : label note that travels with the served value (e.g. 'face line including restricted cash').
--   decision 'concept'   : the tag IS canonical_concept_id on this stmt in this era.
--   decision 'component' : the tag is a summand of parent_concept_id, added with its sign.
--   decision 'combined' : ONE printed line that spans SEVERAL concepts ("Accounts payable and accrued liabilities");
--                          components holds the spanned CONCEPT names. It never feeds any concept: the mapper serves
--                          it as the company's own line in analytics.company_combined_line and marks each spanned
--                          concept not_in_template for those periods (founder ruling, doc 02 sector templates item 3).
--   decision 'excluded'  : the tag is never used (reason_class / reason say why).
--   decision 'not_presented' / 'not_in_template': a CONCEPT-level company decision, no tag ("KLAC's IS has no gross
--                          profit line"): company, stmt, canonical_concept_id, era, reason. taxonomy and tag are NULL.
--                          The mapper turns the cell into a reasoned blank (analytics.cell_blank_reason, state
--                          not_presented / not_in_template) unless a printed 'concept' value exists for that period.
--   'review' (undecided) is never stored.
-- stmt is the FSN statement code (BS/IS/CF/EQ/CI/UN/CP): the same tag on two statements is two rows
-- (NetIncomeLoss on CF is the cash-flow start line, not net income). era_to NULL = open-ended.
-- Eras of one (company, taxonomy, tag, stmt, concept) - or, for tagless rows, (company, stmt, canonical_concept) -
-- must not overlap; and two 'concept' rows of one (company, stmt, concept) never overlap, even under different
-- tags (the library cuts eras so a concept has one tag per period). One tag may feed two concepts (EarningsPerShareBasicAndDiluted: basic and diluted EPS) and
-- one concept may list several tags in consecutive eras (10-Q vs 10-K tags); an 'excluded' detail row (no
-- concept) may coexist with a component row of the same tag (two excluded rows still clash). The mapper takes the latest filing's value among a concept's tags. (trigger; btree_gist is not assumed).
-- NOT applied: needs the founder's typed words.
create table if not exists analytics.company_tag_map (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null references core.company (id),
    cik                   text,
    taxonomy              text,
    tag                   text check (tag is null or (btrim(tag) <> '' and position(':' in tag) = 0)),
    stmt                  text not null check (stmt in ('BS', 'IS', 'CF', 'EQ', 'CI', 'UN', 'CP')),
    decision              text not null check (decision in ('concept', 'component', 'combined', 'excluded',
                                                              'not_presented', 'not_in_template')),
    canonical_concept_id  bigint references analytics.canonical_concept (id),
    parent_concept_id     bigint references analytics.canonical_concept (id),
    sign                  smallint not null default 1 check (sign in (-1, 1)),
    components            text[],
    serve_note            text,
    reason_class          text,
    reason                text,
    era_from              date not null,
    era_to                date,
    evidence_adsh         text,
    evidence_report       int,
    evidence_line         int,
    evidence_plabel       text,
    evidence_cal_parent   text,
    decided_by            text not null check (btrim(decided_by) <> ''),
    rule_id               text not null check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    created_at            timestamptz not null default now(),
    check (era_to is null or era_from <= era_to),
    check (decision <> 'concept' or canonical_concept_id is not null),
    check (decision <> 'component' or parent_concept_id is not null),
    check (decision <> 'combined' or (components is not null and cardinality(components) > 1)),
    check ((decision in ('not_presented', 'not_in_template')) = (tag is null and taxonomy is null)),
    check (decision not in ('not_presented', 'not_in_template')
           or (canonical_concept_id is not null and nullif(btrim(coalesce(reason, '')), '') is not null)),
    check (decision <> 'excluded' or nullif(btrim(coalesce(reason_class, '')), '') is not null
                                  or nullif(btrim(coalesce(reason, '')), '') is not null)
);

create index if not exists idx_company_tag_map_company_concept
    on analytics.company_tag_map (company_id, canonical_concept_id);
create index if not exists idx_company_tag_map_company_parent
    on analytics.company_tag_map (company_id, parent_concept_id);
create index if not exists idx_company_tag_map_company_tag
    on analytics.company_tag_map (company_id, taxonomy, tag);

-- eras of one (company, taxonomy, tag, stmt) must not overlap
create or replace function analytics.company_tag_map_no_overlap() returns trigger
language plpgsql as $$
begin
    if exists (
        select 1 from analytics.company_tag_map m
        where m.company_id = new.company_id and m.stmt = new.stmt
          and m.id is distinct from new.id
          and (case when new.tag is null
                   then m.tag is null and m.canonical_concept_id = new.canonical_concept_id
                   else m.taxonomy = new.taxonomy and m.tag = new.tag
                        and coalesce(m.canonical_concept_id, m.parent_concept_id)
                                is not distinct from coalesce(new.canonical_concept_id, new.parent_concept_id) end
               -- two 'concept' rows of one concept never cover the same period, even under different tags
               or (new.decision = 'concept' and m.decision = 'concept'
                   and m.canonical_concept_id = new.canonical_concept_id))
          and m.era_from <= coalesce(new.era_to, 'infinity'::date)
          and new.era_from <= coalesce(m.era_to, 'infinity'::date)
    ) then
        raise exception 'overlapping era for company % tag %:% stmt % concept % (% to %)',
            new.company_id, new.taxonomy, new.tag, new.stmt, new.canonical_concept_id, new.era_from, new.era_to;
    end if;
    return new;
end;
$$;

drop trigger if exists trg_company_tag_map_no_overlap on analytics.company_tag_map;
create trigger trg_company_tag_map_no_overlap
    before insert or update on analytics.company_tag_map
    for each row execute function analytics.company_tag_map_no_overlap();

comment on table analytics.company_tag_map is
    'Per-company tag -> canonical concept decisions per era, learned from the FSN store; the only tag route for companies that have rows (no global concept_mapping, no company_tag_preference).';

-- Concepts the first tag library maps to that the catalog lacked (no concept_mapping rows: only company_tag_map
-- feeds them). Shares are a count (unit shares), not money; weighted-average counts are income-statement
-- durations, unlike the balance-sheet instant shares_outstanding.
insert into analytics.canonical_concept (name, statement, combination_mode, description) values
    ('weighted_basic_shares', 'income_statement', 'first_match',
     'Weighted-average basic common shares outstanding for the period (unit: shares, not USD)'),
    ('weighted_diluted_shares', 'income_statement', 'first_match',
     'Weighted-average diluted common shares outstanding for the period (unit: shares, not USD)'),
    ('net_interest_income', 'income_statement', 'first_match',
     'Net interest income as presented by banks (interest income less interest expense, USD)'),
    ('cash_paid_for_interest', 'cash_flow', 'first_match',
     'Cash paid for interest (supplemental cash-flow disclosure, USD)'),
    ('cash_paid_for_income_taxes', 'cash_flow', 'first_match',
     'Cash paid for income taxes, net of refunds (supplemental cash-flow disclosure, USD)')
on conflict (name) do nothing;

-- The company's own combined lines (a line printed spanning several concepts), served instead of a blank.
-- Written by mapper/company_tag_map.py (delete-then-insert per company); value = sign x stored companyfacts value.
create table if not exists analytics.company_combined_line (
    id               bigint generated always as identity primary key,
    company_id       bigint not null references core.company (id),
    period_id        bigint not null references core.period (id),
    stmt             text not null,
    taxonomy         text not null,
    tag              text not null,
    plabel           text not null check (btrim(plabel) <> ''),
    components       text[] not null,
    value            numeric not null,
    source_fact_ids  bigint[] not null,
    tag_map_id       bigint references analytics.company_tag_map (id) on delete set null,
    run_id           uuid references analytics.rule_run (run_id),
    created_at       timestamptz not null default now(),
    unique (company_id, period_id, stmt, tag)
);

comment on table analytics.company_combined_line is
    'A line the company prints combined with others, shown as its own combined line in its template (never a blank, never mapped to one concept).';
