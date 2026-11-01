---
id: sec-fsds-num-txt-has-no-note-facts-coexistence-counts-from-f
title: SEC FSDS num.txt has no note facts: coexistence counts from FSDS are face-only lower bounds
kind: gotcha
tags: fsds, tags, coverage
paths: data-team/tags/sources.md
evidence: FILING-CHECKED
status: active
source: Verifier R7 DLH 0000785557-25-000159 R55; Apple 0000320193-25-000079 (92 tags in num = 92 in pre)
created: 2026-10-21
verified: 2026-11-01
---
FSDS num.txt carries only facts on the presented statements. Any 'both tags filed', 'only in notes' or 'filed elsewhere' count from FSDS is a lower bound; use FSN (includes notes) or companyfacts for coexistence.

[2026-11-01] Curator 2026-11-01: the 'wrong' feedback was mistaken; the claim is RIGHT for FSDS (num.txt = face facts of presented statements only; Apple 92 num tags = 92 pre tags). SCOPE: this applies to FSDS only. The FSN (Financial Statement and Notes) num.tsv DOES include note facts: it carries dimh/durp/datp/dcml columns and dimensional note facts (see entry fsn-financial-statement-and-notes-num-ha... and fsn-num-tsv-equals-fsds-face-values-only-after-filtering-dim: FSN equals FSDS face values only after filtering dimn=0, iprx=0, empty coreg). For coexistence/note counts use FSN, not FSDS.
