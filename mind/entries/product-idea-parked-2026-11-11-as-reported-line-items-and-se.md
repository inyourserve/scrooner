---
id: product-idea-parked-2026-11-11-as-reported-line-items-and-se
title: Product idea parked 2026-11-11: as-reported line items and segments from FSN
kind: decision
evidence: DOC-CITED
status: active
created: 2026-11-11
verified: 2026-11-11
---
Founder 2026-11-11 (Dhairya session): show every printed line item in a dynamic financials table (revenue/expenses as the company's own lines) and derive segments from the same data; parked behind the top-1000 goal. Basis: fsn.line holds every presented line (label, order, calc parent, tag); values come from SEC companyfacts via the tag; analytics.company_tag_map links each line to a standard concept or marks it combined/excluded; segments come from dimensional facts (ProductOrServiceAxis, StatementBusinessSegmentsAxis). Screening stays on standardized concepts; cross-year comparison follows the tag map, not labels (labels shift; see data-team/tags/cards/fsn-*.md).
