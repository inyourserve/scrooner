-- 0122: analytics.company_tag_map, the per-company tag -> concept map (founder order 2026-11-11:
-- "FSN for learning (which tag is what), SEC for mapping").
-- ROLLBACK: drop trigger trg_company_tag_map_no_overlap on analytics.company_tag_map; drop function
--   analytics.company_tag_map_no_overlap(); drop table analytics.company_tag_map;  (nothing else references it)
-- The FSN store (schema fsn, 0118) teaches, per company, which XBRL tag is which statement line (statement,
-- position, label, calc tree, era). This table records that decision per (company, taxonomy, tag, stmt, era).
-- Values still come from the SEC company-API facts in core.fact. For a company with rows here the mapper
-- (mapper/company_tag_map.py, rule company_tag_map.select@1, off by default) selects facts ONLY through this
-- table: no analytics.concept_mapping rule, no company_tag_preference override, no fallback applies.
--   decision 'concept'   : the tag IS canonical_concept_id on this stmt in this era.
--   decision 'component' : the tag is a summand of parent_concept_id; combine_sign +1/-1.
--   decision 'combined'  : the tag is the company's own total for canonical_concept_id; components lists its
--                          member tags (evidence of the combination, the members have own 'component' rows).
--   decision 'excluded'  : the tag is never used (reason_class / reason say why).
-- stmt is the FSN statement code (BS/IS/CF/EQ/CI/UN): the same tag on two statements is two rows
-- (NetIncomeLoss on CF is the cash-flow start line, not net income). era_to NULL = open-ended.
-- Eras of one (company, taxonomy, tag, stmt) must not overlap (trigger; btree_gist is not assumed).
-- NOT applied: needs the founder's typed words.
create table if not exists analytics.company_tag_map (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null references core.company (id),
    cik                   text,
    taxonomy              text not null,
    tag                   text not null check (btrim(tag) <> '' and position(':' in tag) = 0),
    stmt                  text not null check (stmt in ('BS', 'IS', 'CF', 'EQ', 'CI', 'UN')),
    decision              text not null check (decision in ('concept', 'component', 'combined', 'excluded')),
    canonical_concept_id  bigint references analytics.canonical_concept (id),
    parent_concept_id     bigint references analytics.canonical_concept (id),
    combine_sign          smallint check (combine_sign in (-1, 1)),
    components            text[],
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
    rule_id               text not null check (btrim(rule_id) <> ''),
    created_at            timestamptz not null default now(),
    check (era_to is null or era_from <= era_to),
    check (decision <> 'concept' or canonical_concept_id is not null),
    check (decision <> 'component' or (parent_concept_id is not null and combine_sign is not null)),
    check (decision <> 'combined' or (canonical_concept_id is not null and components is not null
                                       and cardinality(components) > 0)),
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
        where m.company_id = new.company_id and m.taxonomy = new.taxonomy
          and m.tag = new.tag and m.stmt = new.stmt
          and m.id is distinct from new.id
          and m.era_from <= coalesce(new.era_to, 'infinity'::date)
          and new.era_from <= coalesce(m.era_to, 'infinity'::date)
    ) then
        raise exception 'overlapping era for company % tag %:% stmt % (% to %)',
            new.company_id, new.taxonomy, new.tag, new.stmt, new.era_from, new.era_to;
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
