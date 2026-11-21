---
id: to-check-an-untracked-local-file-is-on-main-byte-compare-wit
title: To check an untracked local file is on main, byte-compare with git show | cmp, not git diff
kind: gotcha
tags: git, shared-tree, commit-check
paths: data-team/strategy/open-shown-fixes/
evidence: CODE-CHECKED
created: 2026-11-22
verified: 2026-11-22
---
In the shared dirty tree, committed files are often still untracked locally because the commit went through a temp worktree. 'git diff --quiet origin/main -- <file>' reports a DIFF for every such file even when the content is identical, because it sees the path as deleted. Use: git show origin/main:<path> | cmp -s - <path>. Verified 2026-11-22: all 16 of the 11-21 open-shown fix CSVs showed DIFF under git diff and were identical under cmp.
