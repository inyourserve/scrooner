---
id: a-work-branch-cut-before-a-migration-landed-on-main-fails-ci
title: A work branch cut before a migration landed on main fails CI's contiguity check when it adds a later number
kind: gotcha
tags: ci, migrations, git, branches
paths: scripts/check_migrations.py
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
Seen 2026-10-30 on work/dhairya/bs-release1-regen: the branch added 0101_company_slot_record.sql but its base (75 commits behind origin/main) predated 0098-0100, so 'Check migration sequence' failed with 'migration sequence is not contiguous: found=[...97, 101], expected=[...97, 98, 99, 100, 101]'. The check reads the branch's own tree, not main's. Fix is a rebase or merge of origin/main, no code change. Diagnose with: gh run view <run> --json jobs --jq '.jobs[]|select(.conclusion=="failure")|.name,(.steps[]|select(.conclusion=="failure")|.name)' then gh run view --job <id> --log-failed.
