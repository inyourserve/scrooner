---
id: debtcurrent-debtnoncurrent-are-combined-debt-lease-lines-onl
title: DebtCurrent/DebtNoncurrent are combined debt+lease lines only WITH evidence; never from the tag name alone (and never pure either)
kind: rule
tags: total_debt, DebtCurrent, leases, slot-records, classification
paths: pipeline/scripts/slot_records/build_debt_slots.py and results/expected_debt_classes.json (branch work/scrooner-25/slot-records)
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Verifier-confirmed rule (VERIFY-SLOT-RECORDS-2026-10-24 + RECHECK): a DebtCurrent/DebtNoncurrent line holds a finance/capital-lease part at some filers (MU - its own cal tree declares the lease inside DebtCurrent from 2019 on; at 2021-09-02 DebtCurrent 155M equals the current finance-lease fact exactly; GOOG 2015-16 short-term debt contains current capital leases 238/223/220M) and is a pure borrowing line at others (MRK, INTC, CSCO, UNH - filing-checked, and zero finance/capital-lease liability facts exist for them at any stored instant). So classification must be evidence-based per company: 'combined' iff the filer's calc children of the line include a lease tag, OR a same-date same-side lease fact exists with no separate lease line on the face; otherwise 'borrowing'. Neither a blanket 'DebtCurrent=borrowing' nor a blanket 'DebtCurrent=combined' (the FASB definition permits both) survives filing checks. Fixtures: expected_debt_classes.json, checked by check_expected_classes.py.
