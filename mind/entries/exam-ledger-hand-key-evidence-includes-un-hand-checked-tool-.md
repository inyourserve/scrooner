---
id: exam-ledger-hand-key-evidence-includes-un-hand-checked-tool-
title: Exam ledger 'hand' key_evidence includes un-hand-checked tool rows; hand-vs-machine accuracy gap is mostly not key quality
kind: lesson
tags: tag-expert, exam, answer-key, verifier
paths: data-team/tags/exam/tools/grade.py, data-team/tags/exam/results/key-adjudication-2026-11-13.csv
evidence: FILING-CHECKED
status: active
source: key-adjudication-2026-11-13.csv (seed 20261113, v6 blind rows)
created: 2026-11-13
verified: 2026-11-13
---
grade.py sets key_evidence=machine only if the docmap note contains 'machine-full-filing'; every other row is 'hand'. In v6 blind rows, 367 of 770 'hand' rows carry no hand-check marker (tool note-map rows; 90.7% agreement) vs 403 marked rows (73.0%). Filing check of 30 hand_wrong rows: key right 11, prediction right 9, both wrong 2, ruling gap 8 (OUT vs not_presented on financials). 30 machine_correct rows: 28 right, 0 both wrong, 2 ruling gaps (lone G&A as SG&A; bank capex ', net'). Recurring key errors: note-map picks dimensioned or segment facts (BWXT investee GP, SEIC corporate overhead); hand keys ignore opex rule 3 component sums (UTHR, PNW); capex perimeter misses (GKOS, PBF).
