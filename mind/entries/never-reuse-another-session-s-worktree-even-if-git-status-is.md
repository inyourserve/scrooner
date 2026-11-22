---
id: never-reuse-another-session-s-worktree-even-if-git-status-is
title: Never reuse another session's worktree, even if git status is clean
kind: gotcha
tags: worktree, sessions
paths: 
evidence: DATA-INFERRED
status: active
created: 2026-11-22
verified: 2026-11-22
---
2026-11-22: /private/tmp/claude-501/wt-hide showed a clean tree, but another session started editing it minutes later. A checkout there moved its HEAD. Create your own worktree under your session scratchpad (git worktree add --detach <scratch>/wt-x origin/main) and never check out inside a worktree you did not create.
