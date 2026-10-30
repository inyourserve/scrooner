---
id: bs-totals-v3-rules-from-verifier-112-112-check-mezzanine-by-
title: BS totals V3 rules from Verifier 112/112 check: mezzanine by face position only; a member blank in a column is zero only when the identity ties without it; no tag fallbacks inside the cross-check
kind: rule
evidence: FILING-CHECKED
created: 2026-10-25
verified: 2026-10-25
---
Verifier 2 filing-checked slot-record BS totals V2 (24684b4): 112 of 112 shown values right across 114 filings; four fixes required before switch-on, applied in V3 (work/scrooner-25/slot-records). (1) A slot's mezzanine lines are the ones the detector CLASSED mezzanine by position, never by tag name (AWK's custom LongTermDebtIncludesRedeemablePreferredStockAtRedemptionValue would otherwise be subtracted twice once the instance reader fills it). (2) Equity guard: OtherCapital is MCK's equity row 'Other (1)' (0000927653-18-000010 R4); ConvertiblePreferredUnits is an equity-section line at ET (0001276187-16-000165 R2); their earlier needs_instance_reader holds were really equity rows mis-held as custom liabilities. (3) A standard member missing in one column (DVN 2018-09-30 held-for-sale liabilities, 0001564590-18-027813 R4) is a printed blank = zero ONLY when the accounting identity ties without it on the same accession; otherwise the cell is not computable. Custom members never get this treatment. (4) The identity cross-check reads mezzanine only from the record's face lines; a tag fallback subtracted GE's 408M RedeemableNoncontrollingInterestEquityCarryingAmount (a note value) and flagged 12 right values. Result: 728 ties, 0 gaps, 0 holds on 19 companies; 123 cells wait on the instance reader.
