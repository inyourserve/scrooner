---
id: a-green-branch-ci-does-not-mean-the-branch-can-land-on-main-
title: A green branch CI does not mean the branch can land on main: the pre-push hook blocks on mypy, which CI only runs as advisory
kind: gotcha
tags: ci, mypy, pre-push, release
paths: .githooks/pre-push, .github/workflows/ci.yml
evidence: CODE-CHECKED
status: active
created: 2026-11-01
verified: 2026-11-01
---
CI's 'Advisory formatting, typing, and dependency audits' job is continue-on-error, so a branch with mypy errors shows CI green (e.g. work/engineering/fsn-store, CI 41298631883, had 15 mypy errors). .githooks/pre-push runs the same ruff format + mypy on the pushed commit and BLOCKS a push to main; --no-verify is founder-only. Before landing a branch, run: uvx mypy --ignore-missing-imports --follow-imports=skip --explicit-package-bases pipeline/src apps/backend. Repo idiom for a comment-only fix is '# type: ignore[code]' (no typing.cast in pipeline/src). 2026-11-01, landed as c4c2931.
