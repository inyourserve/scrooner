---
id: fsn-write-2026-11-09-every-listed-data-point-is-written-from
title: FSN write 2026-11-09: every listed data point is written from the hybrid per (company, data point); a hybrid gap is a defect-state blank, never an old value
kind: decision
tags: fsn, write, done-gate, blank-reason, approver
paths: pipeline/src/scrooner_pipeline/fsn_store/pilot.py, .github/workflows/pipeline-fsn-write.yml
evidence: CODE-CHECKED
source: branch review/ruling-done-gate-c4-2026-11-09, data-team/strategy/team/RULING-DONE-GATE-C4-2026-11-09.md
created: 2026-11-09
verified: 2026-11-09
---
Approver ruling C1-C8 plus addendum N1-N5. The founder's 'Yes approved' and 'No fallback. Everything is the hybrid' were typed in Dhairya's session and relayed. Criterion 4 is now per (company, data point), and a data point is written in full (atomic). filing_not_in_store and hybrid_gap_unresolved are written as cell_blank_reason state=defect with a class and an owner, never not_presented. A cell_proof DISAGREE is to become a defect blank (cell_proof_disagree); the before-image restore is emergency rollback only. Debt, total liabilities and DPS stay unlisted until fixed or until the founder chooses held blanks. company_value_owner stays empty. Check the ruling file for the current text before relying on this.
