---
id: claude-code-token-time-usage-logs-only-go-back-30-days-how-t
title: Claude Code token/time usage: logs only go back ~30 days; how to measure
kind: howto
tags: usage, tokens, claude-code, cost
paths: 
evidence: CODE-CHECKED
status: active
created: 2026-11-17
verified: 2026-11-17
---
Session transcripts (*.jsonl, incl. subagents/) in ~/.claude/projects/-Users-vikash-scrooner hold message.usage per API response. Dedupe by (message.id, requestId), then sum input/output/cache_creation/cache_read tokens. Claude Code deletes logs after ~30 days by default (cleanupPeriodDays), so on 2026-11-17 the oldest log was 2026-10-17 while git starts 2026-08-14; anything older is unrecoverable. Measured for 17 Oct to 16 Nov: ~10.1B tokens, 97% cache reads, 21.4M output, ~99 wall-clock active hours (gaps under 15 min) and ~385 hours summed across parallel sessions. For the full project history, use git counts (git rev-list --count origin/main).
