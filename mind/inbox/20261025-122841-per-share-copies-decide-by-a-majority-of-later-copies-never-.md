---
id: per-share-copies-decide-by-a-majority-of-later-copies-never-
title: Per-share copies: decide by a majority of LATER copies; never by tag-agnostic label shift for dividends
kind: lesson
tags: split, dps, per-share, restatement
paths: pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py
evidence: FILING-CHECKED
source: Verifier VERIFY-SPLIT-OTHER-CHANGED-2026-10-25.md; branch work/period-engineer/split-rebase
created: 2026-10-25
verified: 2026-10-25
---
Constant dividend rates make a correct later copy equal another quarter's value in its own filing, so a label-shift rule drops the right copies (OC 0.24, TEX 0, DCI 0.175, AMGN 2.52 lost to a lone original). Rule that passed: >= 2 agreeing later copies, strictly more than any other later group, else hold (MSFT ASC 606, XYL). Also: a context dated after its own filing is a declared future amount (PPL); rounding slack across share bases only for YTD/annual totals (TSCO 0.22 vs 0.206); recurring 5% stock dividends (CBSH, VLY) re-present EPS by 21/20 every year and need their own event handling.
