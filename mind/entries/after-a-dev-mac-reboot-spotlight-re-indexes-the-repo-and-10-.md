---
id: after-a-dev-mac-reboot-spotlight-re-indexes-the-repo-and-10-
title: After a dev-Mac reboot, Spotlight re-indexes the repo and ~10 scrooner-* worktrees and pins the CPU (load avg 149)
kind: gotcha
tags: mac, spotlight, mds, worktrees, overload
paths: .
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
Measured 2026-11-01, 30 minutes after a reboot: load average 149, mds_stores at 72% CPU, 21 mdworker_shared processes, indexing /Users/vikash/scrooner plus 10 scrooner-* worktrees and backup copies (~3.5 GB) and 7.6 GB of Library/Caches. Mitigation applied: an empty .metadata_never_index in each scrooner* folder (hidden from git via .git/info/exclude); load fell to 86 within a minute. The reliable fix is System Settings, Spotlight, Search Privacy, adding those folders. Also remove finished-lane worktrees once they are checked as pushed. Related: dev-mac-has-8-gb-ram-5-6-claude-sessions-plus-loaders-swap-i.
