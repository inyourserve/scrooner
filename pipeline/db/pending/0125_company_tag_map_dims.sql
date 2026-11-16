-- 0125: analytics.company_tag_map rows may name a dimension (Dhairya ruling 2026-11-13: printed member-only lines,
-- e.g. cost of sales by ProductOrService, amortization by StatementOfIncomeLocationBalance, are a component sum of
-- the printed members, value source fsn_xbrl).
-- ROLLBACK: delete from analytics.company_tag_map where dims <> ''; alter table analytics.company_tag_map drop column dims;
--   then re-run the 0122 body of analytics.company_tag_map_no_overlap() (unchanged except the dims equality).
-- dims is the FSN store's own segment string (fsn.dim.segments), e.g. 'ProductOrService=Product;' or, for a line
-- sliced on two axes, 'BusinessSegments=Gaming;ProductOrService=Gaming;'. '' = no dimension (every row so far).
-- The fsn_xbrl value path reads fsn.value through fsn.dim.segments = dims, consolidated (coreg ''), iprx 0.
-- A dimensioned row only feeds a component sum (or is excluded). One exception (Tag Expert ruling AE.3, Dhairya
-- 2026-11-13): a face line printed only under a single class-of-stock member (STZ diluted shares, Class A) IS the
-- data point, so a 'concept' row may carry dims of exactly one ClassOfStock member (the FSN axis name of
-- us-gaap:StatementClassOfStockAxis). Segment and other slices stay component or excluded.
-- NOT applied: needs the founder's typed words. Number: renumber on landing to the next contiguous file on main.
alter table analytics.company_tag_map
    add column if not exists dims text not null default ''
        check (dims = '' or dims ~ '^([A-Za-z0-9_]+=[A-Za-z0-9_:.-]+;)+$');

alter table analytics.company_tag_map drop constraint if exists company_tag_map_dims_decision_check;
alter table analytics.company_tag_map
    add constraint company_tag_map_dims_decision_check
        check (dims = '' or decision in ('component', 'excluded')
               or (decision = 'concept' and dims ~ '^ClassOfStock=[A-Za-z0-9_:.-]+;$'));

create or replace function analytics.company_tag_map_no_overlap() returns trigger
language plpgsql as $$
begin
    if exists (
        select 1 from analytics.company_tag_map m
        where m.company_id = new.company_id and m.stmt = new.stmt
          and m.id is distinct from new.id
          and not (m.decision = 'excluded' and new.decision = 'excluded')  -- excluded rows never feed anything
          and (case when new.tag is null
                   then m.tag is null and m.canonical_concept_id = new.canonical_concept_id
                   else m.taxonomy = new.taxonomy and m.tag = new.tag and m.dims = new.dims
                        and coalesce(m.canonical_concept_id, m.parent_concept_id)
                                is not distinct from coalesce(new.canonical_concept_id, new.parent_concept_id) end
               -- two 'concept' rows of one concept never cover the same period, even under different tags
               or (new.decision = 'concept' and m.decision = 'concept'
                   and m.canonical_concept_id = new.canonical_concept_id))
          and m.era_from <= coalesce(new.era_to, 'infinity'::date)
          and new.era_from <= coalesce(m.era_to, 'infinity'::date)
    ) then
        raise exception 'overlapping era for company % tag %:%[%] stmt % concept % (% to %)',
            new.company_id, new.taxonomy, new.tag, new.dims, new.stmt, new.canonical_concept_id, new.era_from, new.era_to;
    end if;
    return new;
end;
$$;

create index if not exists idx_fsn_dim_segments on fsn.dim (segments);
