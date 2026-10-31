---
id: common-fsn-cal-arcs-caches-every-period-s-whole-cal-tsv-clea
title: common.fsn_cal_arcs caches every period's whole cal.tsv: clear _FSN_CAL_CACHE per period or a cohort run thrashes swap
kind: gotcha
tags: slot-records, fsn, memory
paths: pipeline/scripts/slot_records/common.py, pipeline/scripts/slot_records/cf_cal_rows.py
evidence: CODE-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
Calling fsn_cal_arcs for filings across all 59 FSN periods keeps each period's full cal table in _FSN_CAL_CACHE; with 3.6M num values loaded too, the 2026-10-30 cohort CFO replay hit 412 GB virtual / 31 MB resident (state U) on the dev Mac. Fix: extract cash-flow arcs once per period (cf_cal_rows.py clears the cache after each period, 89 MB peak) and replay in company batches of 100. Branch work/cashflow/cfo-buybacks.
