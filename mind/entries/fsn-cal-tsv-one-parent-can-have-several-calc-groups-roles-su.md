---
id: fsn-cal-tsv-one-parent-can-have-several-calc-groups-roles-su
title: FSN cal.tsv: one parent can have several calc groups (roles); summing children across groups double-counts (income before tax = face group AND tax-note domestic+foreign group)
kind: gotcha
tags: fsn, xbrl, calc, proof
paths: 
evidence: FILING-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/src/scrooner_pipeline/proof/fsn.py; pipeline/src/scrooner_pipeline/proof/prove.py
---
MSFT FY2026 10-K in FSN 2026m08: IncomeLossFromContinuingOperationsBeforeIncomeTaxes... has children OperatingIncomeLoss + NonoperatingIncomeExpense in the statement role (grp 4) and IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic + ...Foreign in the tax-note role; merged, the children sum to exactly twice the printed 165,934M. cal.tsv rows carry grp/arc, so keep children per grp and test a components-sum per group (pass if any complete group ties). Also: the same arc repeats once per role, so dedupe arcs before counting. Found 2026-10-31 building the cell proof; 198 of 295 DISAGREE cells in the first-10 run were this.
