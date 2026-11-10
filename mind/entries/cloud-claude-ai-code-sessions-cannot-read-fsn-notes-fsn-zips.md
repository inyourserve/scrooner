---
id: cloud-claude-ai-code-sessions-cannot-read-fsn-notes-fsn-zips
title: Cloud (claude.ai/code) sessions cannot read fsn-notes; FSN zips are reachable on sec.gov
kind: gotcha
tags: fsn, cloud, regression-gate, bucket
paths: pipeline/scripts/slot_records/results/fsn_quarter_links.txt
evidence: CODE-CHECKED
status: active
created: 2026-11-01
verified: 2026-11-01
---
A cloud session has no pipeline/.env and no SUPABASE_URL/SERVICE_ROLE_KEY, so the fsn-notes bucket and lane cell files (run 7 CF cells etc.) are unreadable; regression gates that need them must run on the dev Mac or in Actions with secrets. sec.gov is reachable: FSN zips are at https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/<YYYYqN>_notes.zip (note: 'financial-statement-notes-data-sets', not '...-and-notes-...', which 404s), ~430 MB per quarter (2024q4). zstd CLI is not installed in the cloud image. Checked 2026-11-01.
