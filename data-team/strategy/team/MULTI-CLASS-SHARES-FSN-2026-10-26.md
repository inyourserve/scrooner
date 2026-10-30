# Multi-class share counts: what the Financial Statement and Notes data carries (2026-10-26)

Written for: Dhairya, to assign the mapper build. Evidence level: **MEASURED from the SEC Notes data sets** (bucket `fsn-notes`: `num` rows tag `EntityCommonStockSharesOutstanding`, `dimh` joined to `dim.segments`; local `sub` gives the filing). Not yet filing-checked against the cover pages; the per-class counts are the SEC's own parsed XBRL cover values.

**Finding.** Yes: for all six companies the FSN `num` table carries the cover-page `EntityCommonStockSharesOutstanding` once per class, with `dimh` naming the class (`ClassOfStock=<member>`, uom shares, no coreg). companyfacts drops these dimensional values, which is why the six have no current share fact. Every 10-K/10-Q from 2024 on has 2 to 3 class rows. Latest 10-Q (period 2026-06-30, cover date 2026-07-31, file 2026m08):

| Company (company_id) | Class member | Shares at cover date |
|---|---|---|
| UHAL (107) | CommonClassA | 19,224,580 |
| | NonvotingCommonStock | 175,168,915 |
| SUN (2870) | CommonUnits | 136,896,651 |
| | ClassCUnits | 16,410,780 |
| | ClassDUnits | 51,517,198 |
| FWONA (2946) | LibertyFormulaOneGroupCommonClass (A) | 23,991,058 |
| | ...Class B | 2,381,188 |
| | ...Class C | 224,336,239 |
| BRK-A (3034) | CommonClassA | 488,450 |
| | CommonClassB | 1,408,035,161 |
| BAM (3697) | CommonClassA | 1,597,230,353 |
| | CommonClassB | 21,280 |
| PLNT (3937) | CommonClassA | 75,216,965 |
| | CommonClassB | 316,128 |

Class members are the extension names the filer used; UHAL's 2025 filings used `CommonStock` and `NonvotingCommonStock` (19,607,788 and 176,470,092 at 2025-07-31), so the member label can change between filings and a rule must key on the filing, not on a fixed member name.

**Rule the mapper needs (proposal).** Total shares for a market-cap input = sum of all class rows of one filing at that filing's cover date (same date basis), after a per-company class-equivalence table. Do NOT add blindly:
- BRK-A/B: classes are not equivalent shares (one Class A converts into 1,500 Class B). Equivalent-share conversion ratio must come from the 10-K's equity note; flagged, not guessed.
- PLNT and BAM Class B (316,128 and 21,280): the filings must be read to see whether the class carries economic rights; summing them may overstate. Flagged.
- SUN: units, with Class C and Class D units alongside common units; economic equivalence not checked. Flagged.
- UHAL: the nonvoting class is the large one (175M of 194M); economic equivalence to Class A is believed but unchecked.
Until the equivalence is checked per company, publish market cap only where the sum rule is evidenced, otherwise keep the reasoned blank (`stale:shares_outstanding`, class ingestion, reason map v2.3).
