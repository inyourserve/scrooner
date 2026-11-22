---
id: nightly-refresh-red-2026-11-11-20-is-one-mapper-dead-letter-
title: Nightly refresh red 2026-11-11..20: reprocess step failed 11-11..16, then one mapper dead letter tripped --fail-on-alert 11-17..20
kind: gotcha
tags: nightly, refresh, dead-letter, ops, certification, migrations
paths: .github/workflows/pipeline-refresh.yml
evidence: DATA-INFERRED
status: superseded
created: 2026-11-21
verified: 2026-11-21
---
pipeline-refresh failed 10/10 nights (2026-11-11..20), for two causes in sequence. 11-11..16: step 'Reprocess Normalizer + Mapper for recently-filed companies' failed (and 'Rebuild company/metric/tag coverage matrix' 11-12..15). 11-17..20: reprocess green; the only failing step is 'scrooner-operations --fail-on-alert' in the job 'Tickers, prices, freshness gate and coverage'; its only alert is unresolved_dead_letters:mapper:1 = analytics.mapper_error id 134 (cik 0001487798, stage filing_line_evidence, transient SEC 503 on FilingSummary.xml, 2026-11-17). Nothing auto-resolves mapper_error rows and the gate is zero-tolerance. A green run proves only the OLD path: the FSN nightly stage is continue-on-error and FSN_NIGHTLY_STAGE defaults to off. Ingest, reprocess and prices are green. Check: gh run view <id> --log-failed | grep -A3 '"alerts"'. Also verified 2026-11-21: analytics.company_certification has 0 rows (repo says GILD/JNJ are certified); supabase_migrations.schema_migrations stops at 20261003 (15 rows) while the repo is at 0128, and no app migration ledger exists.

[2026-11-22 curator] RETIRED: dated incident snapshot; re-derive nightly state from a live Actions query
