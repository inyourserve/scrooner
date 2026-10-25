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

## Budget
SEC requests this step: 326 (plus 163 TLS handshake failures from a system Python without a cert bundle that never reached sec.gov). Cumulative about 776 of 1,100. Free disk 10 GB. Cal folder 62 MB (kept until the family closes).
