# Slot records: balance-sheet totals V2 (2026-10-25, scrooner-25)

Answers the Verifier's BS V1 verdict (`VERIFY-BS-TOTALS-V1-2026-10-24.md`: gate failed on AWK; 292 holds, 129 avoidable; BRKR custom equity member). Branch `work/scrooner-25/slot-records`. Evidence level: DATA-INFERRED for the replay counts, FILING-CHECKED only where the Verifier's anchors say so. Nothing here touches the database.

## What changed
1. **AWK (item 1).** Root cause: the filer's custom subtotal `LongTermDebtIncludesRedeemablePreferredStockAtRedemptionValue` ("Total long-term debt") was classed mezzanine because its name contains `RedeemablePreferred`. Rule: a tag that reads as debt (`Debt|Borrow|NotesPayable|Loan`) is a liability line even when it also matches the mezzanine pattern. The redeemable preferred inside it then sits between two liability lines and is a liability by position (existing rule). Result: the subtotal is the calc-graph root, it is custom, so every AWK instant is now `needs_instance_reader` (46 of 46) instead of a value that omits 8-11M. No partial sum is published; the anchor path no longer leaks one (it printed 7,599M for AWK before this fix).
2. **No-cal holds (item 2).** Two changes. (a) The 163 boundary filings without a cal file were fetched (`fetch_boundary_cal.py`: folder index then `*_cal.xml`, else `MetaLinks.json`; 326 requests; 340 of 340 boundaries now have a cal). (b) If a boundary still has no cal, the assembler borrows the filer's own statement-role calc graph from its other boundary filings (`dedup: cal_roots_borrowed`, `cal_source: borrowed:<accessions>`), and **a face-sum value is published only when the accounting identity ties** on the same accession: L&E total (else assets) = liabilities + mezzanine + equity incl. NCI, within the filer's rounding unit. Borrowed graphs are a fallback only: 2 of 338 records use one now.
3. **BRKR custom equity (item 3).** Lexical balance-type guard widened (`ShareholdersEquity|Shareholders|EquityAttributable|CapitalSurplus|CapitalStock|PaidInCapital|OtherEquity|EquityOther`) until the FASB balance attribute CSV lands. `OthersShareholdersEquity` is now an equity component, not a liability member.
4. **Identity gate hardening** (found while applying item 2): equity incl. NCI is read two ways (the including-NCI total; parent equity + NCI under the filer's own nci tag) and a tie against either is accepted, because FE 2018-03-31 carries a stray 86M including-NCI fact beside a correct 7,375M equity line, and ET 2026-06-30 holds 15.2B of NCI under a tag other than `MinorityInterest`. The right-hand side is the filer's `LiabilitiesAndStockholdersEquity` when present (BRKR 2019-03-31 prints assets 2,242.5M against a liabilities side of 2,242.3M).
5. BRO anchor instant corrected to 2018-12-31 (FY2018 10-K 0000079282-19-000006); BX/KKR anchors carry a 0.1M tolerance (face quoted in millions to one decimal; Verifier: values right).

## Replay (19 companies, 338 era records, periodic 10-K/10-Q facts, same-accession inputs)
| | V1 (68ed251) | V2 |
|---|---|---|
| holds (`hold_no_cal_for_dedup`) | 292 | 0 |
| identity ties | 429 | 699 |
| identity gaps | 364 | 12 (all GE, printed total) |
| face-sum values withheld on a gap | n/a (values were produced) | 0 |
| needs_instance_reader cells | 55 | 143 (AWK 46, TRGP 46, DVN 30, MCK 12, ET 1, BRKR 1, ...) |
| anchors | 14/16 | 14/16 PASS; TRGP and AWK = correct holds |

The 12 GE gaps are against GE's own printed `Liabilities` total (the cross-check does not read something on GE's face, probably redeemable NCI or preferred); the printed total is still used, the gap is a finding for the Verifier, not a withheld value.

The instance reader (approved) is now the single biggest unblock for this family: 143 cells wait on custom-tag values the API never carries.

## What was withheld before the cal fetch landed, and why (kept as the record of the gate working)
With borrowed graphs only, 22 instants were withheld, every one a real double count or omission: FE 14 (long-term debt a sibling in these eras, a child in the borrowed era), BRKR 2 (`DeferredIncomeCurrent` beside `LiabilitiesCurrent`), NI 3 (`DerivativeLiabilitiesCurrent`, `AssetRetirementObligationCurrent`), ET 2 (`AccountsPayableRelatedParties` 7M; NCI tag). The gap equalled the offending line exactly in every case. None would have been published.

## For the Verifier (fresh draw requested)
Every AWK era (expect `needs_instance_reader`, no value), the 129 formerly held ties (WMT 34, NI 32, MCK 15, EMR 13, FE 12, ET 6, AWK 6, DVN 5, BRKR 5, VLO 1), all 47 BRO instants (46 tie, 1 not computable), GE's 12 printed-total gaps.

## V3 addendum (same day): the Verifier's four pre-switch-on fixes
Verifier 2 on V2 (`VERIFY-BS-TOTALS-V2-2026-10-25.md`): 112 of 112 shown values right across 114 filings; four fixes required before switch-on. All applied:
1. Mezzanine slot now holds only lines the detector CLASSED mezzanine by position (AWK's custom Total long-term debt subtotal no longer appears in `mezzanine_face`).
2. Equity guard extended: `OtherCapital` (MCK "Other (1)" equity row, 0000927653-18-000010 R4), `ConvertiblePreferredUnits` / `*PreferredUnits|CommonUnits|LimitedPartnersUnits` (ET 0001276187-16-000165 R2). Side effect: MCK's 12 `needs_instance_reader` cells and ET's custom member were that equity row; both companies now tie at every instant.
3. A standard member missing in a column is treated as a printed blank (zero) ONLY when the identity ties without it on the same filing (DVN 2018-06-30, 2018-09-30, 2018-12-31 held-for-sale liabilities; ET 2018-03-31). State `member_blank_in_column_identity_confirmed`. A missing custom member still holds for the instance reader.
4. The identity's mezzanine term is read only from the record's face lines; the tag fallback (GE's 408M `RedeemableNoncontrollingInterestEquityCarryingAmount`, a note value) is gone. GE: 12 gaps -> 0.

| | V2 | V3 |
|---|---|---|
| identity ties | 699 | 728 |
| identity gaps | 12 | 0 |
| member blank in column, identity-confirmed | n/a | 4 (DVN 3, ET 1) |
| needs_instance_reader | 143 | 123 (AWK 46, TRGP 46, DVN 30, BRKR 1) |
| not computable | 5 | 1 (BRO 2019-01-01 lease-adoption column) |
| anchors | 14/16 + 2 holds | 14/16 + 2 holds |
| records on a borrowed calc graph | 2 | 2 (`cal_source` starts with `borrowed:`) |

Draw requested: MCK, ET, DVN 2018, the two borrowed-graph records, plus a random tie sample.

## V3.2 addendum: instance reader, every held cell filled (same day)
`instance_reader.py` reads each held instant's ORIGINAL periodic filing (folder index + inline-XBRL instance, 2 requests), keeps facts in undimensioned filer-entity contexts, plus, for explicitly wanted mezzanine tags, facts dimensioned on one axis (TRGP's Series A preferred is tagged only per `StatementClassOfStockAxis`; in 10-Ks the same value also appears under a second axis, so members are grouped per axis and one axis is used). Downloads are deleted after extraction; evidence JSONL `results/instance_evidence_bs.jsonl` (412 rows, 340 KB).

| | V3 | V3.2 |
|---|---|---|
| identity ties | 728 | 851 |
| needs_instance_reader | 123 | 0 (AWK 46, TRGP 46, DVN 30, BRKR 1 filled; each ties) |
| gaps / withheld | 0 | 0 |
| anchors | 14/16 + 2 holds | 16/16 PASS (TRGP 9,823.1M; AWK 14,097M) |
| SEC requests | | 94 + 152 + 92 = 338; cumulative about 1,138 of the 1,300 cap |

Rules added: a dimension-only mezzanine tag counts only with its per-class instance value, never with an undimensioned API fact of the same name (GE's 408M note value); a member blank in a column is zero only when the identity ties without it; mezzanine lines are the ones classed by face position.

## Budget
SEC requests this step: 326 (plus 163 TLS handshake failures from a system Python without a cert bundle that never reached sec.gov). Cumulative about 776 of 1,100. Free disk 10 GB. Cal folder 62 MB (kept until the family closes).
