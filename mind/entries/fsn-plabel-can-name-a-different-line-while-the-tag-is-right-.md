---
id: fsn-plabel-can-name-a-different-line-while-the-tag-is-right-
title: FSN plabel can name a different line while the tag is right (label linkbase shift); resolve by tag+value+position
kind: lesson
tags: fsn, plabel, balance-sheet, tag-map
paths: data-team/tags/cards/fsn-balance-sheet-assets.md
evidence: FILING-CHECKED
status: active
source: STX 0001137789-26-000309 R2 + stx-20261002.htm; POWL 0000080420-23-000051 R3 + powl-20230930.htm
created: 2026-11-11
verified: 2026-11-22
---
7 of 8 label-tag conflicts checked (STX, POWL, EXLS, DY, HLI, TRU, JBHT 2026) were XBRL label shifts with correct tags; JBHT 2020 0001437749-20-021952 was a real wrong tag (PrepaidExpenseAndOtherAssetsCurrent on goodwill+intangibles). A label demotion must not fire on a label that names another line of the same statement.

[2026-11-22] Merged 2026-11-22 from the LH/MUR entry: LH 10-Qs 2016-2024 have every BS equity/liability label one row off (Liabilities 10,427.1M labelled Noncontrolling interest; source LH 0000920148-24-000118 R2); MUR FY2019 Liabilities 5,913,893K labelled as held-for-sale liabilities (0000717423-20-000008 R2). Values tie to the tag, so check value before demoting a line on its label. Real misuses: LW 2017-Q1, WFRD 2019, PCAR. See data-team/tags/cards/fsn-balance-sheet-liabilities-equity.md.
