---
id: migration-history-must-be-reconciled-with-manually-applied-p
title: Migration history must be reconciled with manually applied production DDL
kind: gotcha
tags: migrations, production, supabase, audit
paths: pipeline/db/migrations/, doc/planning/53_Multi_Session_Collaboration_Plan_2026-10-13.md
evidence: CODE-CHECKED
status: active
source: Independent live audit 2026-11-21
created: 2026-11-21
verified: 2026-11-21
---
Live Supabase had analytics.cell_proof, company_certification and company_tag_map, but supabase_migrations.schema_migrations ended at 20261003114421 while repository evidence says later numbered migrations were manually applied. Schema presence and migration history are divergent; future deploys need a reconciled ledger and drift gate.
