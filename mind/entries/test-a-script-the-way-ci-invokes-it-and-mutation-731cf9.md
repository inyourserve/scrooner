---
id: test-a-script-the-way-ci-invokes-it-and-mutation-731cf9
title: Test a script the way CI invokes it, and mutation-check the test
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
The sharded nightly reprocess passed tests that sourced its helper by absolute path, then crashed in CI (`pipeline/scripts/...` relative path after a `cd`). Also: `scripts/check_migrations.py` requires every migration to END with a semicolon (a trailing SQL comment fails it), and CI skips every later step of a job after its first failure, so a green-looking tail proves nothing.
