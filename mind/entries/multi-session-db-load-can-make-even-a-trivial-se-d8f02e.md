---
id: multi-session-db-load-can-make-even-a-trivial-se-d8f02e
title: Multi-session DB load can make even a trivial `select 1` round-trip hang for over an hour
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
(3,656s measured live, 2026-10-13/14), not just long batch writes — the documented "pooler ~15-connection ceiling" and "connection drops under contention" entries above apply to reads too. If a plain health-check query is slow, that's real signal to stop issuing more queries and check `ListAgents`/message the busy peer, not a fluke to retry through.
