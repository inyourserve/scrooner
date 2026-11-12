-- 0123: the tag-map writer may write owned companies, and tag-map companies can be owned by it.
-- ROLLBACK: alter table analytics.company_tag_map drop column scale; restore the 0119 function body (writer 'fsn_cells' only) and the owner check ('fsn_cells' only);
--   delete the company_value_owner rows with owner 'company_tag_map' first.
-- 0119: once a company is owned, every analytics.canonical_fact write that is not made by the fsn cell writer
-- (session setting scrooner.writer = 'fsn_cells') is skipped and logged. The tag-map write path
-- (mapper/company_tag_map_plan.py, rule company_tag_map.select@1) sets scrooner.writer = 'company_tag_map' inside its
-- own transaction and is allowed through; every other stage (conflict fill, derived Q4, fallbacks, dedup, split
-- rebase) stays blocked for a company owned by 'company_tag_map'. NOT applied: needs the founder's typed words.
alter table analytics.company_value_owner drop constraint if exists company_value_owner_owner_check;
alter table analytics.company_value_owner
    add constraint company_value_owner_owner_check check (owner in ('fsn_cells', 'company_tag_map'));

create or replace function analytics.company_value_owner_guard() returns trigger
language plpgsql as $$
declare
    k_company bigint;
begin
    if coalesce(current_setting('scrooner.writer', true), '') in ('fsn_cells', 'company_tag_map') then
        if tg_op = 'DELETE' then
            return old;
        end if;
        return new;
    end if;
    k_company := case when tg_op = 'DELETE' then old.company_id else new.company_id end;
    if exists (select 1 from analytics.company_value_owner o where o.company_id = k_company) then
        insert into analytics.owned_write_skipped
            (company_id, canonical_concept_id, period_id, operation, attempted_value, application_name)
        values (k_company,
                case when tg_op = 'DELETE' then old.canonical_concept_id else new.canonical_concept_id end,
                case when tg_op = 'DELETE' then old.period_id else new.period_id end,
                tg_op,
                case when tg_op = 'DELETE' then null else new.value end,
                current_setting('application_name', true));
        return null;   -- skip the write
    end if;
    if tg_op = 'DELETE' then
        return old;
    end if;
    return new;
end;
$$;

-- company_tag_map.scale: served value = sign x scale x STORED companyfacts value. Valid ONLY on a row from a
-- filing-checked company override (decided_by 'company_override...'); the seeder refuses any other source and the
-- mapper ignores a scale on any other row. The scale-sanity check (filer_scale_error) runs everywhere else.
alter table analytics.company_tag_map add column if not exists scale numeric not null default 1 check (scale > 0);
