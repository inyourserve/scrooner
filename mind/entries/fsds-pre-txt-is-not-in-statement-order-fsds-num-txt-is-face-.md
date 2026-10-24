---
id: fsds-pre-txt-is-not-in-statement-order-fsds-num-txt-is-face-
title: FSDS pre.txt is not in statement order; FSDS num.txt is face-statement facts only
kind: gotcha
tags: fsds, poc, structure, d_and_a
paths: data-team/strategy/team/R7-verifier-poc-filing-check.md, data-team/strategy/tools/structural_concepts_poc.py
evidence: FILING-CHECKED
status: active
source: R7 verifier 2026-10-21
created: 2026-10-21
verified: 2026-10-21
---
Sort pre.txt by (report,line) before any position rule: structural_concepts_poc.py D&A differ 61->20, capex 29->5 after sorting (ADI 0000006281-25-000153 R10, Costco 0000909832-25-000101 R8). num.txt lacks note-only facts (DLH 0000785557-25-000159 R55 InterestExpenseNonoperating absent), so FSDS name-path counts understate companyfacts.
