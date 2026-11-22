---
id: proof-guard-holds-must-expire-when-their-cause-clears
title: Proof guard holds must expire when their cause clears
kind: lesson
tags: proof, guard, cell_proof
paths: pipeline/src/scrooner_pipeline/mapper/company_tag_map.py
evidence: CODE-CHECKED
status: active
created: 2026-11-14
verified: 2026-11-14
---
A held cell is never served, so never re-proved: any DISAGREE reason whose cause can be fixed outside the cell (filer_arithmetic_fails from a since-fixed fsn.filing_check, a detector change) must be re-validated when loading holds, or the cell stays blank for ever. 56e76dc6 releases filer_arithmetic_fails holds once the cited check passes; proof-logic changes bump DETECTOR_VERSION (pin test) so older-detector holds release once.
