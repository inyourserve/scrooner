-- Rollback for 0117: valid only while no writer has populated the columns (post-check showed 0 non-null).
set lock_timeout = '5s';
drop index if exists analytics.idx_canonical_fact_family_company;
alter table analytics.canonical_fact drop column if exists family, drop column if exists rule_run_id;
