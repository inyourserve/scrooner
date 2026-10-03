-- Fix a real bug in migration 0082's uniqueness trigger, found 2026-10-03
-- chasing a plain `uv run scrooner-map seed-concepts` failure ("first_match
-- concept 1 already has a mapping at priority 1") on the exact first row of
-- CONCEPT_MAPPINGS -- an exact no-op reseed of an already-identical row.
--
-- Root cause, isolated with a direct psql repro before trusting the theory:
-- a plain `update ... where id = 1` succeeds; the EXACT same logical change
-- via `insert ... on conflict (canonical_concept_id, concept_id) do update`
-- fails. Postgres fires BEFORE INSERT row triggers on the speculative
-- insert attempt BEFORE it discovers the conflict and switches to the
-- UPDATE path -- so inside the trigger, `new.id` is the not-yet-assigned
-- sequence value for the INSERT that never happens, not the existing row's
-- real id. The original trigger's `cm.id <> new.id` guard therefore never
-- excludes the row's own pre-existing self during an upsert, so it always
-- sees itself as "another row already at this priority" and raises.
--
-- This broke `seed_concept_mappings()`'s core idempotent write pattern
-- (`on conflict (canonical_concept_id, concept_id) do update`) for EVERY
-- first_match canonical concept, not just the row being added when this was
-- found -- confirmed live nobody had rerun a full `seed-concepts` since
-- migration 0082 landed, which is why this sat undetected.
--
-- Fix: compare the business key (canonical_concept_id, concept_id) instead
-- of the surrogate id. A row sharing that exact pair IS the row being
-- written (whether this statement is a plain UPDATE or the UPDATE branch
-- of an upsert), so this correctly excludes self in both paths while still
-- catching a genuine different concept_id claiming the same priority.
create or replace function analytics.check_first_match_priority_unique()
returns trigger language plpgsql as $$
begin
    if new.confidence <> 'rejected' and exists (
        select 1
        from analytics.concept_mapping cm
        join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
        where cc.combination_mode = 'first_match'
          and cm.canonical_concept_id = new.canonical_concept_id
          and cm.priority = new.priority
          and cm.concept_id <> new.concept_id
          and cm.confidence <> 'rejected'
    ) then
        raise exception 'first_match concept % already has a mapping at priority % (conflicting concept_id)',
            new.canonical_concept_id, new.priority;
    end if;
    return new;
end $$;
