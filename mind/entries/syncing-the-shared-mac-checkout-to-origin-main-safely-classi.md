---
id: syncing-the-shared-mac-checkout-to-origin-main-safely-classi
title: Syncing the shared Mac checkout to origin/main safely: classify local edits, back up, stash -u, ff-only, restore unique files
kind: howto
tags: git, sync, shared-tree, stash, fast-forward
paths: .
evidence: CODE-CHECKED
status: active
created: 2026-11-10
verified: 2026-11-10
---
2026-11-10: the shared Mac checkout was 458 commits behind with 320 dirty entries. Never reset --hard a shared tree. Recipe: (1) for each modified file, check git diff --quiet origin/main -- f; 132 of 133 were byte-identical to origin. (2) Untracked files that origin now tracks are usually OLDER drafts; diff them, don't keep them. (3) Untracked files unique to the tree (comm -23 against git ls-tree origin/main) are the only content at risk; here, 16 mind inbox notes. (4) tar a backup to the scratchpad, git stash push --include-untracked, git merge --ff-only origin/main, then git checkout 'stash@{0}^3' -- <unique files> and append any lines that exist only locally in append-only files (grep -vxF -f). The stash stays as a second backup.
