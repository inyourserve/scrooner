---
id: q4-missing-for-every-data-point-at-once-the-latest-copy-of-t
title: Q4 missing for every data point at once = the latest copy of the FY column fails one unrelated subtotal check (AT&T FY2017, PG&E FY2016), not a missing filing
kind: lesson
tags: fsn, select, q4, latest_copy_fails_identity, checks
paths: data-team/strategy/team/FSN-MISSING-QUARTERS-2026-11-09.md
evidence: DATA-INFERRED
source: local reproduction 2026-11-09 on the SEC FSN sets; production fsn.filing read
created: 2026-11-09
verified: 2026-11-09
---
AT&T: the FY2019 10-K (0001562762-20-000064) prints FY2017, and its calc NonoperatingIncomeExpense fails (-4,831M vs -4,575M); select blanks the WHOLE IS column (latest_copy_fails_identity, never an older copy), so FY2017 and Q4 2017 (FY - 9M) are blank for every IS data point. PG&E FY2016: FY2018 10-K fails NetIncomeLossAvailableToCommonStockholdersBasic (1,393M vs 1,407M). The filings ARE in the store. Scoping the blank to the failing calc's concepts needs an approver ruling (criterion 3).
