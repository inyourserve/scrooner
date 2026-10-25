---
id: bs-face-sum-v1-awk-redeemable-preferred-inside-debt-total-ho
title: BS face-sum v1: AWK redeemable preferred inside debt total; holds without calc files are mostly false holds
kind: lesson
tags: total_liabilities, face_sum, false_hold, balance_sheet
paths: data-team/strategy/team/VERIFY-BS-TOTALS-V1-2026-10-24.md
evidence: FILING-CHECKED
source: AWK 0001410636-18-000076 R2; BRO 0000079282-19-000006 R3; TRGP 0001564590-21-054348 R2; WMT 0000104169-21-000042; NI 0001111711-16-000084; EMR 0000032604-20-000033
created: 2026-10-25
verified: 2026-10-25
---
AWK's redeemable preferred (PreferredStockRedemptionAmount) is a row inside 'Total long-term debt' (custom subtotal), so summing Long-term debt misses it on every instant. TRGP's missing 151.2M is a custom noncurrent risk-management liability line (trgp_DerivativeLiability...Noncurrent). Brown & Brown's 2019-01-01 is the ASC 842 adoption column of the Q1 2019 10-Q; the FY2018 balance sheet is 2018-12-31. Holding every cell without a calc file (hold_no_cal_for_dedup) withheld right values at WMT, NI, MCK, EMR (129 v0 ties held).
