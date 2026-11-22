---
id: mutation-checks-restore-and-read-git-diff-before-committing
title: Mutation checks: restore and read git diff before committing
kind: rule
evidence: CODE-CHECKED
status: active
created: 2026-11-16
verified: 2026-11-16
---
After any mutation check, restore the code, run git diff and read it before committing. 12b975f8 shipped reason_code == 'zz' (a mutation-check edit) at mapper/top100_coverage.py:1399; it broke test_proof_pre_filing_period_is_a_hidden_year on main and was fixed in PR #15 (77b91030). A mutant left in production passes the local tests run before the mutation and only fails in CI.
