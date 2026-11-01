---
id: migrations-0114-0116-applied-to-production-2026-10-31-15-45-
title: Migrations 0114-0116 applied to production 2026-10-31 15:45 UTC by Ritwik (scrooner-31) on founder authorization
kind: decision
tags: migrations, release, production
evidence: CODE-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31
---
origin/main 1062649/50683b1/20e2926, sha f065f696161afd9e/2501eb60863c8f30/b8a944316a6671fe; CI 41215553055 clean replay 0001-0116 green. Applied in file order, each in its own transaction, lock_timeout 90s, first attempt each, no deviation from the files (all additive; drop-not-null on an empty table). Post-check: analytics.cell_proof and fact_authority_retired exist with indexes, slot_protected_cell.value nullable YES, guard trigger intact. supabase_migrations.schema_migrations stops at 0072 and is not the project's record (file + doc 53 ledger is). 0115 unblocks OI reasons pkg 2; 0116 is the before-image table for Family A/B/C retirements.
