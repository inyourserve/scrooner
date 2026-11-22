---
id: the-shared-users-vikash-scrooner-checkout-lags-origin-main-b
title: The shared /Users/vikash/scrooner checkout lags origin/main by 1,000+ commits; read files from origin/main
kind: gotcha
tags: git, shared-checkout
paths: data-team/strategy/open-shown
evidence: CODE-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
2026-11-21: the shared checkout was 1,228 commits behind origin/main. Files committed by CI flows (open-shown/MRK.csv, mapper/structural_direct.py) were missing locally and looked like skipped runs. Check with git show origin/main:<path> or a detached worktree of origin/main before concluding that a file or flow output is missing.
