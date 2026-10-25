---
id: sec-insider-transactions-data-sets-all-forms-3-4-5-per-quart
title: SEC Insider Transactions Data Sets: all Forms 3/4/5 per quarter in one ~9 MB zip incl. AFF10B5ONE and footnotes
kind: lesson
tags: insider, form4, bulk, data-consumption
paths: pipeline/src/scrooner_pipeline/ownership/insider.py
evidence: FILING-CHECKED
source: https://www.sec.gov/files/datastandardsinnovation/data/insider-transactions-data-sets/2026q3_form345.zip (8,660,776 bytes; 38,153 submissions, 59,886 NONDERIV_TRANS rows; downloaded and deleted 2026-10-24)
created: 2026-10-24
verified: 2026-10-24
---
Tables: SUBMISSION (ISSUERCIK, DOCUMENT_TYPE, AFF10B5ONE), REPORTINGOWNER, NONDERIV_TRANS/HOLDING, DERIV_TRANS/HOLDING, FOOTNOTES, OWNER_SIGNATURE. Replaces per-filing Form 4 XML fetches (insider.py) and adds Forms 3/5 and full history at near-zero request cost. URL path moved from files/structureddata to files/datastandardsinnovation in 2026q2.
