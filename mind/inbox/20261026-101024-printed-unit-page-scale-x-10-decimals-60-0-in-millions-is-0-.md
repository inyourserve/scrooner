---
id: printed-unit-page-scale-x-10-decimals-60-0-in-millions-is-0-
title: Printed unit = page scale x 10^-decimals; '60.0' in millions is 0.1M; 'shares in Millions' is not the money scale
kind: gotcha
tags: rounding, printed_unit, income_statement, verifier-kit
paths: data-team/strategy/team/VERIFY-RETIREMENT-B11-2026-10-26.md
evidence: FILING-CHECKED
source: 0001628280-25-049844; ABNB 0001559720-25-000010; Ambac 0000874501-25-000032
created: 2026-10-26
verified: 2026-10-26
---
B11 rounds by page scale only, so a 9M printed '$ 60.0' (millions, one decimal) forces a 1M unit: Q4 shown 18M vs 17.8M. ABNB's page prints dollars ('1,893,000,000') and the 1M scale came from 'shares in Millions' (kit multiplier has the same bug). Kit net_income_lines tags 'Including Portion Attributable to Noncontrolling Interest' as nci.
