---
id: supabase-pooler-drops-pgoptions-set-read-only-and-timeouts-i
title: Supabase pooler drops PGOPTIONS: set read-only and timeouts inside the session
kind: gotcha
tags: ci, db, pooler
paths: scripts/ci/run_extract_sql.py
evidence: CODE-CHECKED
status: active
created: 2026-11-16
verified: 2026-11-16
---
PGOPTIONS (-c default_transaction_read_only=on -c statement_timeout=...) is ignored through the Supabase pooler, so a session that asserts read-only refuses to start (standard extract run 43764375238). Set it after connecting: 'set session characteristics as transaction read only' and 'set default_transaction_read_only = on' (fixed a3274dac, verified live: a write raises ReadOnlySqlTransaction).
