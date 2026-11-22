---
id: push-to-main-can-fail-right-after-a-green-branch-ci-retry-as
title: Push to main can fail right after a green branch CI; retry as a fast-forward
kind: gotcha
tags: git, ci, landing
paths: scripts/ci
evidence: DATA-INFERRED
status: active
created: 2026-11-14
verified: 2026-11-14
---
On 2026-11-14 three automated 'wait for branch CI then git push origin <sha>:main' steps failed with 'failed to push some refs' although origin/main was an ancestor of the sha; a manual retry seconds later fast-forwarded cleanly (55e1e3b4, 56e76dc6). A landing script must check the push exit code and retry (after git fetch and an ancestry check) before running anything that assumes the code is on main; one run reran MSFT on old code because the script continued after the failed push.
