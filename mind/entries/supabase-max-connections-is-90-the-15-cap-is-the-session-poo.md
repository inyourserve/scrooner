---
id: supabase-max-connections-is-90-the-15-cap-is-the-session-poo
title: Supabase max_connections is 90; the ~15 cap is the session pooler, so heavy loads should connect directly or via the transaction pooler
kind: reference
tags: supabase, connections, pooler, sharding, loader
paths: pipeline
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
Measured 2026-11-01: current_setting('max_connections') = 90, about 18-22 backends in use at rest. The ~15-client ceiling agents kept hitting is the session-mode pooler, not Postgres. Founder direction 2026-11-01: use the maximum. Dhairya set a 40-connection budget for data loads (the rest is left for the app, backend, nightly and superuser). To get past 15, connect directly (db.<ref>.supabase.co:5432) or use transaction mode (port 6543), and shard by company_id. Back off if CPU goes above ~80% or queries wait on locks. Related: connection-cap-count-pooler-app-backends-not-total-client-ba.
