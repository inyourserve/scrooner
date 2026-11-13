---
id: reader-sec-files-some-primary-statements-under-menucategory-
title: Reader: SEC files some primary statements under MenuCategory 'Uncategorized'; old filings have no MetaLinks, so check the XBRL instance for note-only lines
kind: gotcha
evidence: FILING-CHECKED
created: 2026-11-13
verified: 2026-11-13
---
NEE 0000753308-22-000014 R3 and PEP 0000077476-22-000010 R3 (income statements) are MenuCategory Uncategorized; sec_fetch.py/docmap.py accept such pages when the title names a primary statement (07fdc435, work/reads/301-400). Pre-2019 10-Ks (e.g. TJX) have no MetaLinks.json: for not_presented or combined cells fetch the instance (extras=1 in fetch_request.csv) and look for an undimensioned fact of the narrower tag; found only in a note -> map with stmt NOTE (DIS AccountsPayableCurrent, gross InterestExpense). Caveat: an undimensioned OperatingIncomeLoss can be a segment-profit total (DIS, TJX), not operating income.
