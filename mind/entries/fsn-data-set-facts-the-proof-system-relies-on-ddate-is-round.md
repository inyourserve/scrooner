---
id: fsn-data-set-facts-the-proof-system-relies-on-ddate-is-round
title: FSN data set facts the proof system relies on: ddate is rounded to the month end, cal 'negative' is the weight sign (1/-1), per-share uom is plain USD, dcml is the filer's precision
kind: gotcha
tags: fsn, fsds, xbrl, proof, cell-proof
paths: 
evidence: FILING-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/src/scrooner_pipeline/proof/fsn.py; pipeline/src/scrooner_pipeline/proof/prove.py
---
Checked on the 2023q1/2025m10 sets, 2026-10-31. (1) num.ddate is the period end ROUNDED TO THE MONTH END: AAPL FY ending 2025-09-27 is stored as 20250930; match core.period ends with fsn_ddate() (day <= 15 -> previous month end, else this month end). (2) cal.tsv 'negative' holds 1 or -1 (the arc weight sign), not a 0/1 flag: INTC GrossProfit <- CostOfGoodsAndServicesSold negative=-1, <- Revenue negative=1. Reading it as 0/1 inverts every components sum. (3) num.uom is 'USD' for per-share facts too (INTC EPS: uom USD, dcml 2); do not require 'USD/shares'. (4) num.dcml is the XBRL decimals attribute (-6 millions, 2 cents): 1.5 units of 10^-dcml is the right slack for 'same number'. (5) Subtotals are calc children of the next subtotal up (gross profit under operating income, Liabilities under LiabilitiesAndStockholdersEquity), so 'component' must mean a parent outside the concept's standard chain. (6) The bucket fsn-notes holds quarterly 2014q1-2025q3 then MONTHLY 2025m10 onward (59 periods, also copied locally in another session's scratchpad); a month the SEC has not published yet returns HTTP 400 from storage, treat as missing.
