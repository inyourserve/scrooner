---
id: net-income-nci-bridge-use-only-the-lines-printed-between-pro
title: Net income NCI bridge: use only the lines printed between ProfitLoss and NetIncomeLoss
kind: gotcha
tags: net_income, nci, slot_records, income_statement
paths: pipeline/scripts/slot_records/is_detect.py
evidence: DATA-INFERRED
created: 2026-10-31
verified: 2026-10-31
---
GE 10-Q 0000040545-16-000152 (FSN pre, IS report 2) prints the total NCI line (NetIncomeLossAttributableToNoncontrollingInterest, line 28) between ProfitLoss and NetIncomeLoss, and ALSO its continuing/discontinued split (IncomeLossFromContinuingOperationsAttributableToNoncontrollingEntity line 34, IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToNoncontrollingInterest line 39) further down. Summing every NCI tag on the face double-counts and fails PL - NCI = NI on 55 GE cells. Also a regex on 'MinorityInterest' catches the pretax tag IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments. Rule: take the bridge terms only from face lines strictly between the ProfitLoss and NetIncomeLoss lines.
