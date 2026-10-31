-- 0113 (PROVISIONAL number, claim in doc 53 before landing): resolver guard for
-- slot-record releases. NOT applied; production applies need the founder's
-- own words.
--
-- Problem: about 40 write sites in 15 mapper/sanity/parser modules rewrite
-- analytics.canonical_fact, most of them delete-then-insert a whole concept
-- per company. A value written by a slot-record release (filing-checked by
-- the Verifier) is therefore overwritten by the next nightly resolver run.
-- Patching each site would miss the next new resolver; the guard lives on
-- the table instead.
--
-- Contract:
--   * analytics.slot_protected_cell lists the cells a release wrote. It is
--     written ONLY by the slot release write path, in the same transaction
--     as the cell itself, and emptied for a run by that run's rollback.
--   * While a cell is protected, any INSERT, UPDATE or DELETE of its
--     canonical_fact row is skipped (the trigger returns NULL) and logged in
--     analytics.slot_protected_write_skipped, unless the session has set
--     scrooner.slot_writer = 'on' (the release write path and its rollback).
--   * Delete-then-insert resolvers keep working: the delete of the protected
--     row and the insert of the replacement are both skipped, so the slot
--     value stays and no unique-key conflict is raised.
--   * Inert while the table is empty (one primary-key probe per row).
--   * TRUNCATE is not covered (no writer truncates canonical_fact).

create table if not exists analytics.slot_protected_cell (
    company_id            bigint not null references core.company (id),
    canonical_concept_id  bigint not null references analytics.canonical_concept (id),
    period_id             bigint not null references core.period (id),
    rule_id               text not null,
    value                 numeric not null,
    run_id                text not null,
    package_sha256        text not null,
    protected_at          timestamptz not null default now(),
    primary key (company_id, canonical_concept_id, period_id)
);

create index if not exists idx_slot_protected_cell_run
    on analytics.slot_protected_cell (run_id);

create table if not exists analytics.slot_protected_write_skipped (
    id                    bigint generated always as identity primary key,
    company_id            bigint not null,
    canonical_concept_id  bigint not null,
    period_id             bigint not null,
    operation             text not null,
    attempted_value       numeric,
    application_name      text,
    skipped_at            timestamptz not null default now()
);

create index if not exists idx_slot_protected_write_skipped_key
    on analytics.slot_protected_write_skipped (company_id, canonical_concept_id, period_id);

create or replace function analytics.slot_protected_cell_guard() returns trigger
language plpgsql as $$
declare
    k_company bigint;
    k_concept bigint;
    k_period  bigint;
    hit       boolean := false;
begin
    if coalesce(current_setting('scrooner.slot_writer', true), '') = 'on' then
        if tg_op = 'DELETE' then
            return old;
        end if;
        return new;
    end if;
    if tg_op in ('UPDATE', 'DELETE') then
        hit := exists (select 1 from analytics.slot_protected_cell p
                       where p.company_id = old.company_id
                         and p.canonical_concept_id = old.canonical_concept_id
                         and p.period_id = old.period_id);
        k_company := old.company_id; k_concept := old.canonical_concept_id; k_period := old.period_id;
    end if;
    if not hit and tg_op in ('INSERT', 'UPDATE') then
        hit := exists (select 1 from analytics.slot_protected_cell p
                       where p.company_id = new.company_id
                         and p.canonical_concept_id = new.canonical_concept_id
                         and p.period_id = new.period_id);
        if hit then
            k_company := new.company_id; k_concept := new.canonical_concept_id; k_period := new.period_id;
        end if;
    end if;
    if hit then
        insert into analytics.slot_protected_write_skipped
            (company_id, canonical_concept_id, period_id, operation, attempted_value, application_name)
        values (k_company, k_concept, k_period, tg_op,
                case when tg_op = 'DELETE' then null else new.value end,
                current_setting('application_name', true));
        return null;
    end if;
    if tg_op = 'DELETE' then
        return old;
    end if;
    return new;
end;
$$;

drop trigger if exists trg_slot_protected_cell_guard on analytics.canonical_fact;

create trigger trg_slot_protected_cell_guard
    before insert or update or delete on analytics.canonical_fact
    for each row execute function analytics.slot_protected_cell_guard();
