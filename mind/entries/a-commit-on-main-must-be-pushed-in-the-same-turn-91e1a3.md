---
id: a-commit-on-main-must-be-pushed-in-the-same-turn-91e1a3
title: A commit on `main` must be pushed in the same turn it's made — never left local-only "for later."
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
Standing rule since 2026-09-12 (three real recurrences of a "fixed" workflow sitting unpushed while the scheduled cron kept running the old, broken version). Don't try to auto-push via a git hook (blocked by the permission classifier for good reason — see root "Executing actions with care"). Before trusting a previously-reported fix is live, check `git log origin/main..HEAD`.
