---
id: drop-trigger-if-exists-in-a-migration-takes-access-exclusive
title: DROP TRIGGER IF EXISTS in a migration takes ACCESS EXCLUSIVE and is blocked by peers' idle-in-transaction read connections; CREATE TRIGGER alone is not
kind: gotcha
tags: migration, locks, canonical_fact, 0113, statement_timeout
paths: 
evidence: CODE-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/db/migrations/0113_slot_protected_cell.sql
---
Applying 0113 (2026-10-31, scrooner-31) failed on lock_timeout although only AccessShareLock holders existed on analytics.canonical_fact: several peer sessions leave psycopg read connections 'idle in transaction' for minutes, and DROP TRIGGER IF EXISTS needs ACCESS EXCLUSIVE even when the trigger is absent; waiting also queues every new reader behind the lock request. CREATE TRIGGER needs only SHARE ROW EXCLUSIVE, compatible with readers. Fix used: confirm the trigger is absent (pg_trigger), run the migration with the DROP line omitted, set lock_timeout (90s) so a failure cancels instead of stalling peers, post-check pg_trigger. Write new migrations without a no-op DROP on a hot table, or run them when no peer holds a read transaction.
