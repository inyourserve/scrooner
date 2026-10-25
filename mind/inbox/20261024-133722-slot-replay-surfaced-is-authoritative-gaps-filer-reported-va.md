---
id: slot-replay-surfaced-is-authoritative-gaps-filer-reported-va
title: Slot replay surfaced is_authoritative gaps: filer-reported values with no authoritative row (NVDA FY2015 LongTermDebt, GOOG 2023 LTD&CLO)
kind: gotcha
tags: is_authoritative, triage, total_debt, slot-records
paths: data-team/strategy/team/SLOT-RECORDS-STAGE2-2026-10-24.md
evidence: DATA-INFERRED
created: 2026-10-24
verified: 2026-10-24
---
Stage-2 slot replay (2026-10-24): NVDA FY2015 (instant 2015-01-25) LongTermDebt has NO is_authoritative=true row - the exact original 1,384,342K and all rounded later comparatives are all false. GOOG 2023-12-31 LongTermDebtAndCapitalLeaseObligations 13,253M exists only as non-authoritative copies (it IS composable from authoritative members: LongTermDebtNoncurrent 11,870M + noncurrent finance leases 1,383M). Consequence: the hard 'is_authoritative=false is a hard filter' rule can blank values the filer actually reported on the face; a slot-composed value from authoritative members is the safe fill. Needs triage before any slot-record ship.
