-- Rollback of 0119 then 0118 (applied 2026-11-01 by scrooner-87 on the founder's typed go-ahead).
-- Run only on the founder's words. Drops the FSN store schema and every row in it.
begin;
set local lock_timeout = '5s';
drop trigger if exists trg_company_value_owner_guard on analytics.canonical_fact;
drop function if exists analytics.company_value_owner_guard();
drop table if exists analytics.owned_write_skipped;
drop table if exists analytics.company_value_owner;
alter table analytics.canonical_fact drop column if exists source_value_ids;
drop schema if exists fsn cascade;
commit;
