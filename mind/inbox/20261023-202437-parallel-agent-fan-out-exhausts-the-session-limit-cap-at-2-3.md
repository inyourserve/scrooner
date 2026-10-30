---
id: parallel-agent-fan-out-exhausts-the-session-limit-cap-at-2-3
title: Parallel agent fan-out exhausts the session limit; cap at 2-3 and resume with SendMessage
kind: gotcha
tags: process, agents, rate-limit
paths: doc/data-moat/team/PLAN.md
evidence: DATA-INFERRED
created: 2026-10-23
verified: 2026-10-23
---
2026-10-22: about ten concurrent subagents (several on Opus), each re-reading PLAN.md, doc 49 and SEC filings, hit the session rate limit (HTTP 429, reset 7:30pm IST) and three died mid-task. Their partial work is saved; continue them with SendMessage instead of respawning. Cap concurrency at 2-3, use smaller models for read-heavy work, keep PLAN.md appends short, and point agents at paths instead of pasting context. Also: the auto-mode classifier denies pushes to origin/main and --force-with-lease by Release Manager worktrees even after a relayed go-ahead; only the founder's own message or a permission rule clears it, so use new -v2 branch names instead of overwriting.
