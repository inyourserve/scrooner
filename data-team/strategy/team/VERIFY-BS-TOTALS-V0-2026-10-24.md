# Verify: balance-sheet totals family v0 (scrooner-25, origin/work/scrooner-25/slot-records 4279f9e), 2026-10-24

Verifier 2. Method: re-ran the branch's `bs_replay.py` unchanged in logic (read-only copy that also dumps each instant's value and the accession of every member fact; one connection, 20s; it reproduced 459 ties / 191 gaps exactly), then opened the balance-sheet R page of the filing for each checked cell and wrote the face value first (printed Total liabilities, else LSE - total equity - printed mezzanine lines, cross-checked against the face-line sum). One regex reader. FILING-CHECKED unless marked.

## Result: GATE FAILS. Of the slot values I checked, 14 liabilities values are wrong (anchors and samples), from 6 defect classes; T and OXY miss the noncurrent long-term-debt line on every instant.

## 1. OXY and T (all 46 instants gap): the skeleton drops the noncurrent long-term-debt line
`bs_totals_detect.py`: after "Total current liabilities" a new run starts; the next line, Long-term debt (a standalone line with no section header), joins that run, and the later section subtotal "Total deferred credits and other (noncurrent) liabilities" then does `skeleton[run_start:] = [t]`, replacing the debt line with the section subtotal. The subtotal does not contain the debt.
| Cell | Accession, locator | Slot | Face | Missing line |
|---|---|---|---|---|
| T 2026-06-30 | 0000732717-26-000297 R5 | 165,289M | 53,382 + 134,631 + 111,907 = 299,920 | Long-Term Debt 134,631 (= the gap) |
| T 2016-09-30 | 0000732717-16-000233 R5 | 161,133M | 402,975 - 124,603 = 278,372 | Long-Term Debt 117,239 (= the gap) |
| OXY 2018-12-31 | 0000797468-19-000004 R2 | 12,323M | 7,412 + 10,201 + 4,911 = 22,524 | LONG-TERM DEBT, NET 10,201 |
| OXY 2015-09-30 | 0000797468-15-000014 R2 | 13,325M | 50,089 - 29,882 = 20,207 | long-term debt 6,882 (= the gap) |
| OXY 2025-09-30 | 0001628280-25-051071 R2 | 25,860M | 83,472 - 36,766 = 46,706 | long-term debt 20,846 (= the gap) |
Fix: take a subtotal's members from the filer's calc children (or the presentation abstract the subtotal closes), never "everything since the last Total". Also the OXY 2023-03-31 era record lists `LongTermDebtAndCapitalLeaseObligationsCurrent` next to `LiabilitiesCurrent` (a component plus its own subtotal): not filing-checked, check before use. OXY's equity_parent and nci slots are None in 4 eras although the face prints "Total stockholders' equity".

## 2. Anchors (values from my identity reports; correct instants, not the dates in `bs_anchors.json`)
| Anchor | Accession, locator | Expected | Slot | Verdict |
|---|---|---|---|---|
| WMT 2026-07-31 | 0000104169-26-000154 R4 | 189,115M | 189,115 | right |
| T 2026-06-30 | 0000732717-26-000297 R5 | 299,920M | 165,289 | WRONG (class 1) |
| VLO 2020-12-31 | 0001035002-21-000051 R2 | 32,132M | 32,132 | right |
| EMR 2024-12-31 | 0000032604-25-000012 R5 | 16,231M | 16,231 | right (the anchors file has 2016-09-30, which is a different instant) |
| DIS 2020-03-28 | 0001744489-20-000102 R5 | 102,321M | 102,321 | right |
| AWK 2017-12-31 | 0001410636-18-000076 R2 | 14,097M | 14,089 | WRONG: misses Redeemable preferred stock at redemption value 8 (`PreferredStockRedemptionAmount`, inside "Total long-term debt"); MEZZ_RX `RedeemablePreferred` classes the AWK line as mezzanine although it is debt |
| BX 2019-06-30 parent | 0001193125-19-216805 R2 | 6,308.355M | 6,308.355 (PartnersCapital); liabilities 16,907.127 printed | right; NCI slot None (NCI 7,655.4 on PartnersCapitalAttributableToNoncontrollingInterest not read) |
| KKR 2015-06-30 parent | 0001404912-15-000005 R2 | 5,947.415M | 5,947.415; liabilities 19,577.562 | right; NCI slot None (46,050.7) |
| BRKR 2019-03-31 | 0001104659-19-027788 R2 | 1,298.7M | needs_instance_reader (held) | hold right |
| FE 2018-03-31 | 0001031296-18-000031 R5 | 31,420M | 31,420 | right |
| DVN 2017-03-31 | 0001564590-17-008268 R4 | 15,212M | 15,212 | right (the cross-check took Assets 28,635 from 0001564590-18-010177: vintage mix) |
| MCK 2015-06-30 | 0000927653-15-000006 R4 | 45,556M | 45,552 | WRONG: skeleton includes the EQUITY line "Other (4)" (`OtherAdditionalCapital`); EQUITY_START_RX does not match it |
| NI 2023-12-31 | 0001111711-24-000011 R6 | 20,940.9M | 21,013.4 (held as needs_instance_reader) | WRONG if released: "Asset Retirement Obligation, Current 72.5" is rendered after the total but is inside Total Current Liabilities (5,192.6 of listed lines + 72.5 = 5,265.1), so it is counted twice |
| TRGP 2021-09-30 | 0001564590-21-054348 R2 | 9,823.1M | needs_instance_reader (held) | hold right; note `DerivativeLiabilityBeforeEffectsOfMasterNettingArrangementsNoncurrent` is flagged custom |
| "AJG 2019-01-01 equity 3,000,568K" | 0000079282-19-000016 R3 | n/a | n/a | not applicable: that cell is Brown & Brown (CIK 0000079282), mislabeled AJG in my V2 report (corrected there); fixture AJG is CIK 0000354190 |

## 3. Random tie and gap cells (seed random.Random(20261027); frame = replay instants since 2015 with a computed value: 459 ties, 191 gaps; list sorted by (ticker, end), shuffled, max 2 per company)
Ties, 20: right 18 = WMT 2021-04-30 151,989; KKR 2019-03-31 25,796,178K; BX 2023-03-31 22,372,614K; FE 2024-06-30 37,293; AJG 2015-06-30 7,004.6; AJG 2020-09-30 15,996.7; FE 2023-06-30 36,094; VLO 2023-03-31 33,110; NI 2016-09-30 14,255.6; BRKR 2024-06-30 4,078.1; EMR 2018-09-30 11,400; MCK 2024-06-30 73,051; NI 2017-12-31 15,641.6; WMT 2026-01-31 178,488; EMR 2024-03-31 19,659; DIS 2024-09-28 90,697; KKR 2020-06-30 32,715,720K; BRKR 2015-12-31 997.1 (equals the restated FY2016 10-K column 0001047469-17-001114; the FY2015 10-K prints 998.0; members come from both filings). **Wrong 1**: DVN 2018-03-31 slot 15,577 vs face 29,316 - 13,725 = 15,591 (0001564590-18-010177 R4): `AssetRetirementObligationsNoncurrent` 1,127 was taken from the Q1 2019 10-Q (0001564590-19-014637); identity gap 14M is inside the 0.05% tolerance (14.7M). **Not adjudicated 1**: GE 2015-03-31 (old-format R page with several entity blocks; my reader's columns are not reliable there).
Gaps, 15: real composition misses 6 (T x2, OXY x2: long-term debt, class 1; AWK 2016-12-31 13,254 vs 13,264 and AWK 2016-09-30 12,722 vs 12,733: redeemable preferred inside long-term debt). Wrong values from other classes 2: NI 2025-09-30 23,318.5 vs face 23,161.1 (0001111711-25-000055 R5; `PrepaidExpenseCurrent` 157.4, an ASSET row rendered in the bottom section, summed as a liability); DVN 2017-09-30 15,611 vs face 27,559 - 11,934 = 15,625 (ARO taken from the 2018 10-Q). Liabilities right, gap caused by the cross-check's other inputs 7: GE 2021-09-30 (printed 198,172; the replay subtracted a 171M redeemable fact the face does not show), FE 2017-06-30 (37,007 right; equity input 163M is the bad NCI-inclusive fact), FE 2015-09-30 (40,035 right; Assets from 0001031296-16-000121, 51,930 vs face 52,663), GE 2022-06-30 (149,597 right; equity fact 31,728 vs face 35,942), KKR 2016-06-30, KKR 2016-09-30, BX 2018-03-31 (printed liabilities right; gap = partnership NCI not read). None of the 15 gaps is filer rounding.

## 4. Era boundaries (5 + 1)
| Era first filing | Layout | Slot | Face | Verdict |
|---|---|---|---|---|
| NI 0001111711-15-000022 R5 (2015-03-31) | capitalization first | 17,429.2 | 24,898.9 - 7,469.7 = 17,429.2 | right |
| FE 0001031296-17-000023 R5 (2017-03-31) | capitalization in the middle | 37,073 | 43,212 - 6,139 = 37,073 | right |
| AWK 0001564590-16-022379 R2 (2016-06-30) | capitalization first | 12,542 | 17,706 - 5,153 = 12,553 | WRONG (redeemable preferred 11) |
| ET (ETP) 0001276187-15-000033 R2 (2015-03-31) | predecessor, two mezzanine lines | 44,165 | 67,004 - 22,791 - 33 - 15 = 44,165 | right; mezzanine 33 + 15 on the face |
| NI 0001111711-25-000020 R5 (2025-03-31) | new class: bottom "Joint Ventures" block | 22,297.3 | 33,105.1 - 10,946.0 = 22,159.1 | WRONG (`PrepaidExpenseCurrent` 138.2 after the total) |
| ET 0001276187-25-000086 R2 (2025-06-30) | new class | 79,407 | 11,849 + 60,749 + 754 + 4,204 + 1,609 = 79,165 | WRONG (`CashAndCashEquivalentsAtCarryingValue` 242 in the skeleton) |

Record scan (DATA-INFERRED, all 194 records): asset or equity tags inside `total_liabilities_members` in MCK (OtherAdditionalCapital / OtherCapital, 13 eras, 9 computed instants, 8 of them "ties"), NI 2024-03 to 2026-06 (DepositsToRenewableGenerationAssetDeveloper, PrepaidExpenseCurrent, OtherAssets, AccruedInsuranceNoncurrent), ET 2025-06/09 (CashAndCashEquivalentsAtCarryingValue). Classify by the element's balance/statement side (asset elements never in a liability sum) and stop the zone at the L&E total.

## 5. Is the identity only a cross-check? Yes, and it is a weak one
Cases where face-sum and identity BOTH "tie" and the value is wrong: MCK 2015-06-30 (slot 45,552 incl. an equity line; gap 4M inside tolerance), AWK 2017-12-31 (14,089, gap 8M < 9.7M tolerance), DVN 2018-03-31 (15,577, gap 14M < 14.7M). An exact tie can also be wrong for the filing: BRKR 2015-12-31 ties at 997.1 because Assets and members both came from the later restated copy, while the filing for that period prints 998.0. And the replay's own inputs mix vintages (`distinct on (tag, end_date) ... order by is_authoritative desc, id desc` picks the latest copy across filings: OXY 2018 Assets from the FY2020 10-K, FE 2015 Assets from a 2016 10-Q), so its gaps are partly its own. Proposal: tolerance = rounding of the filer's unit (one unit of the R page scale per summed line), and all terms from one accession.

## Defects to send to scrooner-25
1. Subtotal swallowing a preceding standalone line (T, OXY; class 1).
2. Asset/equity rows in the liability skeleton (MCK equity "Other"; NI prepaid/other assets in the bottom block; ET cash).
3. Rows rendered after the L&E total that are components of an earlier subtotal (NI ARO current 72.5).
4. `RedeemablePreferred` treated as mezzanine when the face puts it inside debt (AWK, every era).
5. Member facts and cross-check inputs taken across filings (DVN 2017-09-30, 2018-03-31; BRKR 2015; OXY, FE assets).
6. Partnership NCI slot not read (BX, KKR) and OXY equity slots None.
Not tested: GE multi-entity layout, the other 12 fixture companies' boundaries, any cell with mezzanine dim tags, second reader.
