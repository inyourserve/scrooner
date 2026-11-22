---
id: absence-hides-are-an-allowlist-a-data-point-may-hide-absent-
title: Absence hides are an allowlist: a data point may hide 'absent in own filing' only after a 20-cell filing check with 0 wrong
kind: rule
tags: display, hide, verification
evidence: FILING-CHECKED
status: active
created: 2026-11-16
verified: 2026-11-16
---
2026-11-16: two verifier samples of absent_in_own_filing hides found 6/20 then 8/20 wrong (note data points under custom tags or quarterly-only contexts; face lines mis-tagged e.g. T 'Inventories' as PrepaidExpenseCurrent; NFLX trade receivables inside 'Other current assets' note; CVX SBC as components; PH interest income only in MD&A). Rule: hides allowed only for allowlisted data points (operating_income, shares_outstanding, share_buybacks so far); others stay OPEN until a >=20-cell filing check passes with 0 wrong. Never ship a new hide class without a verifier sample. Face label beats element (label_overrides_element).
