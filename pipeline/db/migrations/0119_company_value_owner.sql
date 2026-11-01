-- Company value ownership and the 0113 guard extension (design §6, migration 0119).
-- Once a company is served from the FSN store, every analytics.canonical_fact write for it that is not made by the
-- fsn cell writer (session setting scrooner.writer = 'fsn_cells') is skipped and logged: the nightly's
-- mapper/conflict-fill/derivation stages can no longer overwrite owned cells. The slot_writer path of 0113 is kept.
-- Written 2026-11-01 by scrooner-8a; NOT applied; apply needs the founder's words.
create table if not exists analytics.company_value_owner (
    company_id  bigint primary key references core.company (id),
    owner       text not null check (owner in ('fsn_cells')),
    since       timestamptz not null default now(),
    note        text
);

create table if not exists analytics.owned_write_skipped (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null,
    canonical_concept_id  bigint,
    period_id             bigint,
    operation             text not null,
    attempted_value       numeric,
    application_name      text,
    skipped_at            timestamptz not null default now()
);
create index if not exists idx_owned_write_skipped_company on analytics.owned_write_skipped (company_id, skipped_at);

create or replace function analytics.company_value_owner_guard() returns trigger
language plpgsql as $$
declare
    k_company bigint;
begin
    if coalesce(current_setting('scrooner.writer', true), '') = 'fsn_cells' then
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

drop trigger if exists trg_company_value_owner_guard on analytics.canonical_fact;
create trigger trg_company_value_owner_guard
    before insert or update or delete on analytics.canonical_fact
    for each row execute function analytics.company_value_owner_guard();
