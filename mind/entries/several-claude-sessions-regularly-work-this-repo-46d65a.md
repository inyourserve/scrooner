---
id: several-claude-sessions-regularly-work-this-repo-46d65a
title: Several Claude sessions regularly work this repo concurrently against the same shared dev Supabase instance
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
`ListAgents` before any heavy batch job (full/wide `--ciks` run, bulk `executemany`, full-population rerun); `SendMessage` a peer showing `busy` before starting one. The pooler has a real ~15-connection ceiling — concurrent heavy jobs have taken prod Postgres fully unreachable at least once (needed a founder-only dashboard restart). Light, single-connection, index-backed reads are fine even while a peer's heavy job runs.
