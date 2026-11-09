---
id: rebuilding-fsn-rows-from-a-filing-s-own-edgar-xbrl-the-calib
title: Rebuilding FSN rows from a filing's own EDGAR XBRL: the calibrated rules (ddate day<=15 back, durp=(q*91.25-days)/91.25, LegalEntity coreg only when alone, typed axes last, pre mirrors R pages)
kind: reference
tags: fsn, xbrl, edgar, nightly
paths: pipeline/src/scrooner_pipeline/fsn_store/xbrl_fsn.py, pipeline/scripts/results/fsn_xbrl_equivalence/summary.md
evidence: DATA-INFERRED
created: 2026-11-09
verified: 2026-11-09
---
Calibrated against the SEC set 2026m10 (20 top-100 filings, 22,774 num rows exact): ddate = previous month end if day<=15 else this month end (not nearest); qtrs=round(days/91.25), durp=(qtrs*91.25-days)/91.25; LegalEntityAxis stays in segments and is coreg only when it is the context's only axis; explicit axes sorted case-insensitively, then typed axes (keep 'Statement' prefix and raw QName value); iprx order = higher decimals first; text drops non-ASCII and is CSV-quoted when it holds a double quote; accepted is rounded to the minute; pre rows mirror the R page (rows the renderer hides are absent); stmt: first report of each type wins, parenthetical inherits the previous statement's type; SEC cal grp/arc numbering is not reproducible (arcs per group are). Full rules in the xbrl_fsn module docstring.
