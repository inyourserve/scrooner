---
id: connection-cap-count-pooler-app-backends-not-total-client-ba
title: Connection cap: count pooler/app backends, not total client backends; 10+ idle Supabase platform backends are not ours
kind: gotcha
tags: supabase, connections, pooler
paths: CLAUDE.md
evidence: DATA-INFERRED
created: 2026-10-23
verified: 2026-10-23
---
2026-10-23 pg_stat_activity breakdown (scrooner-4d): of 18-26 client backends, 10 were idle 'Supabase Storage API', 4 Supavisor pooler connections (running refresh job plus one MCP query), 1 pgbouncer, 1 postgres_exporter, 1 supabase_admin, 1 mgmt-api. The ~14 team cap applies to Supavisor/app backends; group by application_name and usename before concluding the team is over the cap. Status 2026-10-23: none of the four scheduled workflows (Refresh, Frames, Sanity, Health-check) green; dispatch one at a time through heavy-db-jobs in that order. VACUUM of core.fact done (4m48s, 1.52M dead rows removed; bloat smaller than the 14M counter suggested).
