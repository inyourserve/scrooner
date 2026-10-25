---
id: mu-48-filings-collapse-to-3-debt-slot-records-slot-sum-exact
title: MU 48 filings collapse to 3 debt slot records; slot sum exact at all 53 instants; prod total_debt perimeter switches across MU history
kind: lesson
tags: slot-records, total_debt, hybrid, format-gate, MU
paths: pipeline/scripts/slot_records/build_debt_slots.py (branch work/scrooner-25/slot-records), data-team/strategy/team/SLOT-RECORDS-MU-V0-2026-10-24.md
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Built the first slot-record run (V2 step 2 / as-filed pilot section 7): parsed the _cal.xml of all 48 MU 10-K/10-Q since 2015. (1) Format stability is real: 48 filings -> 3 era-keyed records, the single change is ASC 842 (2019), exactly the gate's known break class. (2) DebtCurrent + LongTermDebtAndCapitalLeaseObligations = the filer's own DebtAndCapitalLeaseObligations at ALL 53 stored instants 2012-2026, zero exceptions (stored-vs-stored vs the filer's own tagged aggregate; anchors 2021-09-02 6,776M and 2025-08-28 11,533M/14,577M filing-checked by Dhairya). (3) Production total_debt_resolved switches perimeter across MU's own history: lease-inclusive 2015/2019 (7,341M, 5,851M), borrowings-only 2021/2025/2026 (5,968M, 11,533M, 2,792M), and 2021-09-02 is wrong under either definition. Generalizable rule: a composite's perimeter must be an explicit slot/product decision, never an emergent property of tag priorities - tag-priority resolution produces silently inconsistent time series within one company. Era keying must use taxonomy version, not period dates.
