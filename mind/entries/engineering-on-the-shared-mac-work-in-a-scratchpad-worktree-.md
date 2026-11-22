---
id: engineering-on-the-shared-mac-work-in-a-scratchpad-worktree-
title: Engineering on the shared Mac: work in a scratchpad worktree of origin/main with the main checkout's venv; pre-push hook enforces ruff format
kind: gotcha
tags: workflow, git, worktree, ruff
paths: scripts/top100_flow.sh
evidence: CODE-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
The shared checkout is 1,000+ commits behind and dirty. Pattern that worked 2026-11-21: git worktree add --detach <scratchpad>/wt origin/main; run tests from <wt>/pipeline with PYTHONPATH=src /Users/vikash/scrooner/pipeline/.venv/bin/python -m pytest (no venv in the worktree); format with uvx ruff format before committing because the pre-push hook runs ruff format --check pipeline/src and blocks; main moves every few minutes from flow publish jobs, so loop fetch/rebase/push. rg is not installed (use grep); zsh needs --include quoted. Remove the worktree when the lane ends (Dhairya rule).
