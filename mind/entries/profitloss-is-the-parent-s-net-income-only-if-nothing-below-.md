---
id: profitloss-is-the-parent-s-net-income-only-if-nothing-below-
title: ProfitLoss is the parent's net income only if nothing below it takes a share (NCI or subsidiary preferred)
kind: gotcha
tags: net_income, nci, slot_records, utilities
paths: 
evidence: DATA-INFERRED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/scripts/slot_records/is_detect.py
---
A face with ProfitLoss and no NetIncomeLoss is not automatically the parent's income. ELS (OP-unit NoncontrollingInterestInNetIncomeLossOperatingPartnershipsRedeemable), PG&E (PreferredStockDividendsAndOtherAdjustments labelled 'Preferred stock dividend requirement of subsidiary') and ETR (NoncontrollingInterestInNetIncomeLossPreferredUnitHoldersRedeemable) deduct below ProfitLoss; 14 cells of IS NI release 1 published consolidated income this way (re-cut 2026-10-31). The parent's OWN preferred dividends come after parent net income and do not count. Combined utility filings (ETR, ES 2024+) tag the attributable line NetIncomeLossAvailableToCommonStockholdersBasic while their NetIncomeLoss is only the subsidiaries' dimensioned columns (no undimensioned fact).
