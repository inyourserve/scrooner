-- ROLLBACK for rule slot.is_revenue_tagged_total_sum@1: restore production revenue_sanity_resolved from the before-image.
-- Generated, NOT executed. Run inside one transaction by the Release Manager only.
begin;
set local scrooner.slot_writer = 'on';
update analytics.canonical_fact set value = 930400000, source_fact_ids = array[11815578]::bigint[], resolved_at = '2026-09-08 19:38:45.403793+00' where id = 98959418;
update analytics.canonical_fact set value = 949200000, source_fact_ids = array[11815603]::bigint[], resolved_at = '2026-09-08 19:38:45.403793+00' where id = 98959427;
update analytics.canonical_fact set value = 1879600000, source_fact_ids = array[11815600]::bigint[], resolved_at = '2026-09-08 19:38:45.403793+00' where id = 98959468;
do $$ begin if to_regclass('analytics.slot_protected_cell') is not null then delete from analytics.slot_protected_cell where rule_id = 'slot.is_revenue_tagged_total_sum@1'; end if; end $$;
commit;
