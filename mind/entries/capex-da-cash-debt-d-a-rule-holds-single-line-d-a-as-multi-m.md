---
id: capex-da-cash-debt-d-a-rule-holds-single-line-d-a-as-multi-m
title: capex_da_cash_debt D&A rule holds single-line D&A as multi_member (false holds)
kind: lesson
tags: d_and_a, held_pending_verifier, capex_da_cash_debt, verifier
paths: data-team/22-FILING-LESSONS-LEDGER.md
source: commit dd53219ef (verify note, file not on main)
evidence: FILING-CHECKED
status: active
created: 2026-11-01
verified: 2026-11-01
---
Rule capex_da_cash_debt.d_and_a_face@21 (file sha256 6f53c9456bc1) sets da_class=multi_member and holds cells whose members list has ONE member (the CF DepreciationDepletionAndAmortization line). HD: 22 such holds, face-checked FY2013 1,757 (0000354950-14-000008 R8) and Q1 FY24 837 equal the held member value. File-wide 1,366 single-member D&A holds at 155 companies. Count members before trusting a multi_member hold. Same load: 3,585/46,823 cells end before 2015-01-01 (outside window). Branch verify/msft-hd-capex-cash-2026-11-01 dd53219.
