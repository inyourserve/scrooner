---
id: financial-report-xlsx-is-no-longer-generated-in-edgar-filing
title: Financial_Report.xlsx is no longer generated in EDGAR filing folders
kind: gotcha
tags: edgar, filing-package
evidence: FILING-CHECKED
source: 404: MU 0000723125-26-000023, MU 0000723125-25-000028, AAPL 0000320193-25-000079; 200: AAPL 0000320193-19-000119 (2026-10-24)
created: 2026-10-24
verified: 2026-10-24
---
Use R*.htm, FilingSummary.xml (report list, MenuCategory, role) and MetaLinks.json (per tag: presentation roles, labels, definition; per report first anchor with decimals) instead. MetaLinks.json + FilingSummary.xml + _cal.xml (about 1.5 MB, 3 requests) is the cheapest per-filing structure fingerprint.
