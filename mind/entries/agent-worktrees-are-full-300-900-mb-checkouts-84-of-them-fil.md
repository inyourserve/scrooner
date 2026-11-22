---
id: agent-worktrees-are-full-300-900-mb-checkouts-84-of-them-fil
title: Agent worktrees are full 300-900 MB checkouts; 84 of them filled 32 GB by 2026-11-20. Give a worktree only to a committing agent and remove it when it reports
kind: gotcha
tags: disk, worktree, agents, repo-size
paths: data-team/tags/line_map, data-team/strategy/top100-coverage.csv
evidence: DATA-INFERRED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Measured 2026-11-20 on the shared Mac: .claude/worktrees held 84 agent worktrees, 32 GB, with 3.7 GiB free on disk. Each worktree is a full checkout and the repo tracks ~400 MB of generated data (pipeline/scripts 152 MB of CSVs, data-team/tags 142 MB incl. resolver-all110 30 MB, data-team/strategy 50 MB incl. the hourly 11 MB per-cell coverage export), so a fresh worktree is ~300 MB before caches. Cleanup that is safe: remove only worktrees with git status clean AND rev-list --count HEAD --not --remotes=origin = 0 (57 removed, 20 GB freed); keep dirty/unpushed ones until their owner confirms. Policy (Dhairya, founder-prompted): read-only or single-file agents run in the shared tree; only committing agents get a worktree, removed when they report; no generated file over 5 MB committed; the hourly export writes the summary only.
