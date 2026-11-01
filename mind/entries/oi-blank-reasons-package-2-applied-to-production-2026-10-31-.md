---
id: oi-blank-reasons-package-2-applied-to-production-2026-10-31-
title: OI blank reasons package 2 applied to production 2026-10-31 16:06 UTC (run 4d7b48ee): 13,942 reasons, 3,313 derived operating-income values hidden, 253 companies
kind: decision
tags: release, production, operating-income, blank-reason, slot-protected
evidence: CODE-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31
---
slot.is_operating_income_not_presented@1 on main ec6277c, writer mapper/slot_is_not_presented.py, package digest fd4d733058280d4a. Verifier YES 10/10 + 10/10 (verify/oi-not-presented-2026-11-01). Post-check: 13,942 cell_blank_reason rows, 3,313 canonical_fact_retired rows (97 companies), 13,942 slot_protected_cell rows with value null (protected blanks, needs 0115), 0 retired keys still shown, guard skip log 0. Rollback: slot_is_not_presented restore --run-id 4d7b48ee --confirm RELEASE-IS-OI-NOT-PRESENTED-2. Post-write owed: certify rerun on the 253 touched CIKs. Gotcha: the writer records git_commit from cwd; run it from a non-repo dir when the local checkout is not at the code commit, and cite the code commit in the report.
