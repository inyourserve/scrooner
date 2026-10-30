---
id: modern-filings-can-ship-no-separate-cal-xml-calc-linkbase-em
title: Modern filings can ship no separate _cal.xml: calc linkbase embedded in the .xsd (MSFT 2024+); MetaLinks lacks BS calc; fallback chain
kind: gotcha
tags: xbrl, cal-linkbase, metalinks, slot-records, filing-formats
paths: pipeline/scripts/slot_records/build_debt_slots.py (branch work/scrooner-25/slot-records)
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Found building the slot-record engine (2026-10-24): MSFT filings from 0000950170-24-008814 (FY2024 era, Donnelley agent) onward have NO *_cal.xml in the EDGAR archive folder, the -xbrl.zip contains NO XML files at all, and MetaLinks.json carries calculation relationships for note roles but NOT the balance sheet in 3 of 5 checked filings. The calculation linkbase is EMBEDDED IN THE SCHEMA (.xsd) as linkbase elements (grep calculationArc msft-20240630.xsd = true). Any per-filing calc reader needs the fallback chain: *_cal.xml -> embedded-in-xsd -> MetaLinks.json; FSN bulk cal.tsv is the systematic path. Two more extractor rules from real filings: debt lines can hang directly under LiabilitiesAndStockholdersEquity with no Liabilities calc node (NVDA FY2015 10-K 0001045810-15-000036, GOOG 2015 10-Q 0001652044-15-000005), and LiabilitiesOtherThanLongtermDebtNoncurrent is a NON-debt remainder line that lexically matches Debt (ABBV FY2017 10-K).
