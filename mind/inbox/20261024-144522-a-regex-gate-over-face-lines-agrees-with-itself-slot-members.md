---
id: a-regex-gate-over-face-lines-agrees-with-itself-slot-members
title: A regex gate over face lines agrees with itself: slot membership needs a FACE COVERAGE CHECK, and slot-vs-prod agreement proves nothing when both miss the same line
kind: lesson
tags: slot-records, coverage-check, total_debt, verification, regex
paths: pipeline/scripts/slot_records/build_debt_slots.py, era_detect.py, assemble30.py (branch work/scrooner-25/slot-records); data-team/strategy/team/VERIFY-SLOT-RECORDS-30SET-2026-10-24.md
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Verifier rejection of the 30-company debt slot set (2026-10-24): the debt-family regex missed whole printed face lines - KO 'Loans and notes payable' (NotesAndLoansPayable[Current], 12,973M), ORCL 'Notes payable, non-current' (LongTermNotesAndLoans, 50,489M), AMD LinesOfCredit (plural beats LineOfCredit) - so 12 cells where slot AGREED with production were wrong in BOTH (same line missing from both vocabularies). Fixes that generalize: (1) candidate detection must use tag AND printed label, wide net; (2) membership is then closed by a face-coverage check: every candidate is a member or carries a recorded exclusion reason, anything unclassified fails the record (coverage_clean=false) - never ship a composition whose face lines are not fully accounted for; (3) a missing member in a value replay is a HARD STOP, never a silent zero (it hid KO's custom line for 4 years); (4) non-authoritative fallbacks must be restricted to periodic filings (an 8-K recast copy slipped in for GE, 35,114M vs the 10-K's 35,185M); (5) a combined AP+accrued+debt custom line is never a debt member (AMAT 2015). Meta-lesson, same as the 2026-10-17 vocabulary-circularity audit but at line level: agreement between two systems sharing a vocabulary is not verification; only the filing's own face closes the loop.
