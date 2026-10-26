---
id: verifier-kit-e7fa26c-filingsummary-regex-picks-r-n-1-parenth
title: Verifier kit e7fa26c: FilingSummary regex picks R(n+1) (Parenthetical); combined-filing registrant blocks give wrong derived liabilities
kind: gotcha
tags: verifier-kit, FilingSummary, R page, balance_sheet
paths: data-team/strategy/team/VERIFY-KIT-LIVE-TEST-2026-10-26.md
evidence: FILING-CHECKED
source: DUK 0001326160-16-000296 R4; JPM 0000019617-15-000318; BSX 0000885725-22-000006
created: 2026-10-26
verified: 2026-10-26
---
find_report_files pairs ShortName with the next report's HtmlFileName (HtmlFileName precedes ShortName): parse per <Report> block. Old R pages append element names to numbers ('2,341,284us-gaap_Liabilities') and use separate [1] footnote cells. L&E labels vary (', redeemable NCI, and', 'capitalization and liabilities', '..., Total', bare 'Total'). DUK combined filing: first L&E minus last equity = wrong 108,622 vs 81,768.
