# W10 share-date census and the `pershare.share_count_date@1` evaluation (Period Engineer, 2026-10-22)

Status: **EVIDENCE + RECOMMENDATION, read-only.** No DB writes, no code edits, no migration. Requested by PLAN.md "Rulings on lane 2 hand-back" item 6. Branch under review: `work/data-engineer/lane2-w10-anchor` 29cf9f5 (RF-10 `pershare.balance_sheet_date_anchor@1`). Machine-readable rows: `data-team/strategy/data/w10_share_date_census_2026-10-22.csv` (98 rows: 39 census + 59 control/tail).

Evidence labels: **FC** = FILING-CHECKED (I opened the filing's own XBRL instance and/or main document from EDGAR; accession cited). **DI** = DATA-INFERRED (our tables or the EDGAR filing index only). **AS** = ASSUMED.

## 0. Population and the "27 of 194" count

- Tool: `python -m scrooner_pipeline.mapper.bs_anchor_dryrun --sample 300 --seed 1 --chunk 100 --statement-timeout-ms 20000 --max-clients 14` run from the branch source (exported with `git archive`, the shared worktree was not checked out). DB watermark 2026-10-22 11:59 UTC. Output is byte-identical to lane 2's own `w10_s300.csv` (same sample).
- The dry-run tool does not emit share dates, so I added a read-only probe (one connection, 20 s timeout, chunks of 100, client count checked; 10 client backends at start): per company, latest balance-sheet date D = newest instant of canonical `stockholders_equity` since 2025-01-01; is there a canonical `shares_outstanding` at D; is there one at a later date (the cover date).
- Result on the same 300: **232** companies have a cover-dated count after D; **193** also have a D-dated count; **39** have only the cover count. The dry-run's own field agrees: 38 companies have `book_value_per_share` moving to D and blank with `incomplete:denominator` (all 38 are in my 39; the 39th is AIV, see 1.6).
- **I could not reproduce lane 2's 27 of 194 (167 both).** Same tool, same sample, same day. Lane 2's probe query is not in the branch. Census below covers all 39 (a superset under any definition I could construct). Next action for lane 2: state the probe query so the two numbers can be reconciled.
- All 39 cover facts are in the same accession as the D balance sheet, the cover date is 13 to 45 days after D (median 30), and every cover date is on or before the filing date (FC, instance contexts). All 39 are 10-Qs.

## 1. Census of the 39 cover-only companies (FC unless marked)

Method per company: downloaded the filing's XBRL instance (`*_htm.xml`) and read every fact with a `shares` unit at instant D or the cover date, with its dimensions; listed every EDGAR filing dated after D up to the filing date (8-K items, 424B, S-1/S-3, Form D); for the cases with no D-dated count, searched the main 10-Q text. Columns: accession, D, cover date, filing date, what the filing holds at D.

**Headline: 30 of 39 are capture gaps (the filing has a D-dated count we do not read), 5 have no D-dated outstanding count anywhere I looked, 4 are out of scope for a fallback.** The ASSUMED expectation in the brief ("many are capture gaps") is confirmed.

### 1.1 Issued and treasury both filed undimensioned at D (issued - treasury), 18
companyfacts strips dimensions and `CommonStockSharesOutstanding` is not filed undimensioned, so canonical has nothing at D.

| Ticker | Accession | D | Cover date / count | Filed | Issued - treasury at D | vs cover | Dimensioned "outstanding" at D |
|---|---|---|---|---|---|---|---|
| ALOT | 0001193125-26-261335 | 2026-04-30 | 06-04 / 7,747,772 | 06-08 | 11,156,635 - 3,433,213 = 7,723,422 | +0.32% | SharesOutstanding[CommonStockMember] 11,156,635 = **issued** (trap) |
| AROC | 0001389050-26-000028 | 06-30 | 07-29 / 175,338,185 | 08-05 | 184,982,818 - 9,765,857 = 175,216,961 | +0.07% | none |
| ARW | 0001104659-26-091983 | 07-04 | 07-30 / 50,905,423 | 08-06 | 56,094,000 - 5,119,000 = 50,975,000 | -0.14% | [CommonStockMember] 50,975,000 (agrees) |
| CBSH | 0000022356-26-000190 | 06-30 | 08-03 / 143,432,178 | 08-05 | 148,521,165 - 4,369,979 = 144,151,186 | -0.50% | none |
| CSW | 0001624794-26-000046 | 06-30 | 07-24 / 16,293,487 | 07-30 | 17,946,000 - 1,645,000 = 16,301,000 | -0.05% | [CommonStockMember] 17,946,378 = **issued** (trap) |
| DK | 0001628280-26-053106 | 06-30 | 07-30 / 61,232,174 | 08-05 | 78,774,745 - 17,575,527 = 61,199,218 | +0.05% | [CommonStockMember] 78,774,745 = **issued** (trap) |
| JBI | 0001839839-26-000018 | 07-04 | 08-07 / 136,435,790 | 08-11 | 149,709,078 - 13,243,691 = 136,465,387 | -0.02% | 136,465,387 (agrees) |
| KD | 0001104659-26-091129 | 06-30 | 07-29 / 217,818,263 | 08-05 | 247.2M - 27.8M = 219.4M (filed rounded to 0.1M) | -0.72% | [CommonStockIncludingAPIC] 219.4M (agrees) |
| KO | 0001628280-26-028802 | 04-03 | 04-28 / 4,302,482,418 | 04-30 | 7,040M - 2,737M = 4,303M (rounded to 1M) | -0.01% | 4,303M (agrees) |
| KR | 0001104659-26-108926 | 08-15 | 09-15 / 590,588,700 | 09-18 | 1,918M - 1,322M = 596M (rounded to 1M) | -0.91% | none |
| MHH | 0001193125-26-337054 | 06-30 | 07-31 / 12,012,581 | 08-06 | 14,052,048 - 2,022,864 = 12,029,184 | -0.14% | none |
| NPKI | 0000071829-26-000042 | 06-30 | 07-28 / 84,909,894 | 07-30 | 89,969,464 - 5,059,570 = 84,909,894 | 0.00% | none |
| NPO | 0001628280-26-052211 | 06-30 | 07-23 / 21,167,681 | 08-04 | 21,337,102 - 173,597 = 21,163,505 | +0.02% | 21.1M (rounded, agrees) |
| RRC | 0001193125-26-310446 | 06-30 | 07-17 / 233,679,515 | 07-21 | 269,589,292 - 35,915,000 = 233,674,292 | 0.00% | equity-component treasury filed as negative issued |
| SHC | 0001822479-26-000047 | 06-30 | 07-30 / 285,374,795 | 08-06 | 286,037,000 - 675,000 = 285,362,000 | 0.00% | 285,362,000 (agrees) |
| SNA | 0000091440-26-000144 | 07-04 | 07-17 / 51,727,124 | 07-23 | 67,466,117 - 15,745,419 = 51,720,698 | +0.01% | none |
| TOL | 0000794170-26-000102 | 07-31 | 08-26 / 92,147,000 | 08-28 | 102,937,000 - 10,569,000 = 92,368,000 | -0.24% | none |
| USPH | 0001140361-26-031825 | 06-30 | 08-07 / 14,922,698 | 08-07 | 17,526,791 - 2,603,117 = 14,923,674 | -0.01% | SharesOutstanding[CommonStockMember] 17,526,000 = **issued** (trap) |

Events D to filing date: only 8-K 2.02/5.02/7.01/8.01/1.01, S-8, DEF 14A, 10-K/A (ALOT), SD. No 3.02, 2.01, 3.03, 424B or split in any of the 18 (DI, EDGAR index; items read, documents not opened).

### 1.2 One common class filed only class-dimensioned, other classes zero or absent, 7
| Ticker | Accession | D | Cover | Filed | D-dated count | Note |
|---|---|---|---|---|---|---|
| RGR | 0001174947-26-000724 | 06-27 | 07-15 / 15,978,256 | 07-29 | [CommonStockOneMember] 15,978,256 | equals cover |
| WCC | 0000929008-26-000024 | 06-30 | 07-29 / 48,732,854 | 07-30 | Common 48,732,756; Class B 0 | +98 shares |
| VTSI | 0001437749-26-027657 | 06-30 | 08-04 / 11,319,624 | 08-13 | Undesignated 11,319,624; Class A 0; Class B 0 | equals cover |
| WTW | 0001193125-26-325374 | 06-30 | 07-27 / 92,871,937 | 07-30 | [OrdinaryShareOneMember] 93,003,869 | Irish plc, ordinary shares listed directly |
| RENT | 0001468327-26-000088 | 07-31 | 09-04 / 33,774,121 | 09-11 | Class A 33,757,416; Class B 0 | 8-K 1.01/3.02 on 09-04 and 09-11 (gap only +0.05% at the cover date) |
| SNFI | 0001493152-26-038484 | 06-30 | 08-14 / 16,289,293 | 08-14 | Class A 16,096,296 | 8-K 2.01/5.03 on 2026-07-21 (acquisition close between D and cover, +1.2%) |
| HOVR | 0001213900-26-108211 | 08-31 | 10-09 / 67,123,941 | 10-09 | Class A 67,123,941 plus member "Class A ordinary shares to be issued" 8,204 | perimeter question (to-be-issued) |

### 1.3 Issued only, no treasury share fact at D, 3
MDU 0000067716-26-000072 (issued 210,349,456 = cover), TROW 0001628280-26-051335 (issued 213,312,000, equity column equal; cover 213,315,850), SRTA 0001628280-26-052256 (issued 88,466,806 = cover). Issued is FC; "outstanding = issued" is **DI** (no treasury share fact in the instance; I did not check for a treasury dollar line, which is what separates these from HOG/NSP/PKOH below).

### 1.4 Two classes, both needed, 2
- PRLD 0001193125-26-343475: voting 65,028,996 + non-voting 14,728,135 = 79,757,131 at D; cover (one undimensioned dei fact) 79,803,485 is the total. A class sum recovers it.
- **SEV** 0001493152-26-037373: Class A 11,983,010 + Class B 25,439,653 at D (balance sheet: "11,983,010 ... shares issued and outstanding", "25,439,653 ..."). The cover reads "As of August 6, 2026, there were 28,560,115 Class B Common Stock": **the cover counts only the listed class**, while the undimensioned dei fact looks like a total. A cover fallback here would drop Class A entirely (classes incomplete). Also 8-K 1.01/3.02 2026-07-13 and S-1 2026-08-07 between D and filing.

### 1.5 No D-dated outstanding count in the filing, 5 (the only real fallback candidates)
| Ticker | Accession | D | Cover / count | Filed | What the filing has at D | Events D to filing |
|---|---|---|---|---|---|---|
| HUBB | 0001628280-26-029110 | 03-31 | 04-27 / 52,841,777 | 05-01 | No share-unit fact at D; repurchased shares are "constructively retired"; text search found only the cover and EPS weighted averages | 8-K 2.02, SD |
| LEG | 0000058492-26-000430 | 06-30 | 07-30 / 136,588,995 | 08-06 | No share-unit fact at D; balance sheet shows common stock and treasury stock in dollars only | DEFM14A 07-09 and 425 (Somnigroup all-stock acquisition of LEG, pending), 8-K 2.02 |
| HOG | 0000793952-26-000061 | 06-30 | 07-31 / 104,072,507 | 08-05 | Equity statement: issued shares 173,535,458 only; treasury stock in dollars (2,275,356K) with no share count | 8-K 2.02, 8-K/A 7.01 |
| NSP | 0001000753-26-000087 | 06-30 | 07-22 / 38,195,270 | 07-30 | Equity statement: issued 55 (millions); treasury in dollars only | S-8, 8-K 2.02 |
| PKOH | 0000076282-26-000028 | 06-30 | 07-31 / 14,490,010 | 08-06 | Equity statement "Common Stock Shares" 18,575,430 tagged `CommonStockSharesOutstanding` [CommonStockMember], but it is the **issued** count (treasury in dollars only; cover 14,490,010, -22%) | 8-K 2.02 |

FC for the instance (no D-dated outstanding fact) and for the text passages quoted; the text search used fixed patterns ("shares issued/outstanding", "par value", "treasury", "common stock ... authorized/issued/outstanding"), so an untagged sentence in a note could still be missed. That residue is stated as not found, not as absent.

### 1.6 Out of scope for a share-date fallback, 4
- **AIV** 0001193125-26-216904: the 10-Q presents a "Statement of Net Assets (Liquidation Basis)" at 2026-03-31 and a going-concern balance sheet only to 2026-01-31 (FC). A D-dated count exists (141,200,000 at 03-31, already canonical); the blank is the numerator, and book value per share is not applicable under liquidation basis. Needs a not-applicable reason, not a share rule.
- **Athene Holding** (CIK 0001527469) 0001527469-26-000056: "203,805 shares of our common stock were outstanding, all of which are held by Apollo Global Management" (FC); listed securities are preferreds. Per-common-share metrics are not applicable.
- **DBVT** 0001628280-26-048453: ADS issuer (excluded per brief; WO-21 NA-15). D-dated `SharesOutstanding` 296,061,497 is undimensioned and filed (a capture gap too), and includes 146,321 treasury shares (WO-21 AC-25).
- **NNDM** 0001193125-26-338523: D-dated class-dimensioned 210,589,406 exists; listing form (ADS vs ordinary) **AS**, so excluded pending the WO-21 ADS list. Its quarterly basic WASO in core.fact is about 1000x the cover count (DI), a separate scale defect to route.

## 2. Control set: cover vs balance-sheet count where both are filed

- Population: the 192 companies of the 193 with both dates whose cover fact sits in the D-dated filing (ACM's cover fact is in a filing with a different period of report). Gap = |cover - canonical D count| / D count (DI, core.fact).
- Distribution, all 192: median 0.043%, p75 0.46%, p90 7.5%, p95 67.7%; 80 above 0.1%, 45 above 0.5%, **35 above 1%**, 28 above 2%, **23 above 5%**, 10 above 50%. Excluding 5 SPACs (187): median 0.033%, 30 above 1%, 18 above 5%. 52 have a gap of exactly 0.
- Control sample (not chosen by me): stratified by gap bucket (0 / <=0.1% / <=1% / >1%) with proportional allocation, `random.Random(20261022)` over company ids sorted ascending; 29 companies (8/9/7/5): FELE, HAE, Electro-Sensors, LCII, CLSK, CRVL, PRSU, BZH, WINT, EBMT, BJRI, LIDR, TACT, MEHA, Ellington Credit, SOAR, VISM, MPTI, RDAC, MWYN, IMCR, LMNR, MWA, GDOT, ZSTK, MOJO, PCB, ARR, SGOL (SGOL instance fetch failed: a grantor trust with no `index.json` parse; NOT_RUN). I filing-checked the control set plus the whole >1% tail (35), 59 companies in all.

### 2.1 What moves the tail (35 companies above 1%)
FC = instance read plus EDGAR index; "text" = I also read the 10-Q note quoted.
- **SPAC perimeter, 5** (GUAC 0001829126-26-008903, ATII 0001437749-26-027710, LEGO 0001829126-26-007408, FWAC 0001829126-26-008763, RDAC 0001213900-26-086726): the D-dated `CommonStockSharesOutstanding` counts only non-redeemable (founder) shares; the redeemable public shares are `TemporaryEquitySharesOutstanding` (e.g. GUAC 7,877,500 vs 31,510,000 temporary; cover 39,387,500 = the sum). Not a share change: a perimeter difference. This also affects the **current A path**, not only the fallback (section 4).
- **Business combinations, 2**: ZSTK 0001062993-26-003961 (2,430,000 -> 17,489,828; 8-K 2.01 on 07-23, Form D), ESQ 0001104659-26-093295 (8,649,400 -> 12,104,583; 8-K 2.01 on 08-03).
- **Offerings, ATM, PIPE, conversions, or unexplained increases, 24** (cause DI from the event index unless marked text): VBIO (8-K 3.02, S-1), NGNE (424B5 07-02), BBLG (3.02, S-3, 424B3), CALC (S-3/EFFECT), AGPU, AVTX, ONCO, CIRC, TGL (five 8-K 3.02s), MGNC (3.02), DAIC (3.02/3.03), REVB, VERI, CREX, GPOX, **IVR** (text: "Between July 1, 2026 and August 5, 2026, we issued 5,380,335 shares ... under our equity distribution agreement"; gap 5,254,311 shares; no 8-K), ARR (ATM, referenced in its notes; DI), **BDPT** (36,595,174 -> 196,926,762 by debt conversions; text: Q2 equity statement "Common stock issued for conversion of debt 19,586,449"; subsequent-events note: "**No significant event to report**"; no 8-K, 424B or registration filed in the window), BSFC (convertible notes, text), LABT, DTII, PTOS, BEEM, CDLX (unexplained by events; CDLX also files undimensioned outstanding 5,451,000 below issued 5,808,000 with no treasury fact).
- **Buybacks, 3**: ABR 0001253986-26-000048 (text: "repurchase 2,140,300 shares of our common stock" with July convertible-note proceeds; 188,981,757 -> 186,558,043), LITS (-6.2%), BZH (-2.4%).
- **Split between the dates, 1**: VISM 0001654954-26-008927 (text: "On September 11, 2026, the Board approved a 1-for-1,500 reverse split"; cover 1,269,509,667 at 10-13 is pre-split; also +120M shares issued). REVB's 1-for-4 split (2026-01-28) is before D and already reflected in both counts.

### 2.2 Can a filing signal stand in for the missing D-dated count? (tested on the 59)
- **EDGAR event index** (8-K 3.02/2.01/3.03/5.03, 424B, S-1/S-3/EFFECT, Form D): flags 26 of the 35 >1% cases; **misses 9** (DTII, BDPT, PTOS, CDLX, LABT, BSFC, BEEM, ARR, IVR: ATM sales and note conversions need no 8-K); flags 3 of 24 <=1% cases (DI).
- **Subsequent-events note**: silent on a 5.4x change at BDPT (FC).
- **Quarterly basic weighted-average shares from the same filing** (DI, core.fact, 174 non-SPAC companies): at a 1% tolerance it catches 25 of 27 real >1% gaps but misses BZH (2.4% buyback, WASO gap 0.6%) and TGL (WASO stored with a sign/scale defect), and raises 58 false alarms out of 147; at 5% it misses TGL and CDLX.
- No signal tested separates "cover equals the D-dated count within tolerance" from "it does not" without error. The tolerance in rule B can only be **checked** when the D-dated count exists, which is exactly when B is not needed.

## 3. Evaluation of `pershare.share_count_date@1`

| Clause | Finding | Evidence |
|---|---|---|
| A: balance-sheet-date count | Correct anchor, but today it reads only undimensioned `CommonStockSharesOutstanding`. 30 of 39 "cover-only" companies have a D-dated count in the same filing in another form | 1.1-1.4 (FC) |
| B: same accession | Holds for all 39 | FC |
| B: cover after D and <= filing date | Holds for all 39; AVLN 0001193125-26-345820 (both group) files the cover count at 2026-08-31 in a 10-Q filed 2026-08-12, so the check is needed and works | FC (AVLN instance context) |
| B: no split or share-series step between | Detectable from 8-K 3.03/5.03 plus the filing text (VISM) | FC |
| B: no issuance/buyback above tolerance | **Not testable** for the companies B is meant for (no D-dated count). Every proxy tested misses real cases (2.2). Control: 16% of non-SPAC companies move more than 1% and 9.6% more than 5% between D and the cover date | 2, 2.2 |
| B: classes complete | Needed and not detectable from companyfacts: SEV's undimensioned cover fact is one class only | 1.4 SEV (FC) |
| C: otherwise incomplete:denominator | Correct and visible | - |

### Recommendation (Period Engineer; needs a Standardization Lead decision card and Verifier re-read before any build)
1. **Do not adopt clause B as an automatic rule.** Under the no-error standard it would publish an unverifiable value for exactly the residue it targets; the control evidence shows unflagged moves up to 5.4x (BDPT) and silent ATM moves of 5% (IVR). A labelled "shares as of <cover date>" does not make a ratio whose numerator is dated D correct. If the founder still wants the 5 residual companies covered, the only defensible form is a per-filing Verifier read, and BDPT shows even a clean note is not proof, so I recommend C for them.
2. **Widen A instead (capture, not fallback): `pershare.share_count_date@2` proposal**, all from the same accession and the same instant D, consolidated (no legal-entity axis), common classes only:
   - A1 undimensioned `CommonStockSharesOutstanding` (today's rule).
   - A2 the sum over `StatementClassOfStockAxis` members of `CommonStockSharesOutstanding`, only if every common class in the filing is present (zero-valued members count) and none is redeemable/temporary equity. Recovers RGR, WCC, VTSI, WTW, RENT, SNFI, PRLD, and SEV correctly (37,422,663, not the cover's 28,560,115). HOVR needs a ruling on the "to be issued" member.
   - A3 undimensioned `CommonStockSharesIssued` minus undimensioned `TreasuryStockCommonShares` (treasury >= 0). Recovers the 18 in 1.1. This is a same-instant balance identity (WO-21 3.1 already defines outstanding = issued - treasury), not period subtraction; it still needs its own decision card. Preserve precision: KO, KR and KD file both in rounded millions or 0.1M, so the derived count carries the coarser `decimals`.
   - A4 (needs one more check before proposing) undimensioned issued where the filing has neither a treasury share fact nor a treasury-stock value line: MDU, TROW, SRTA. HOG, NSP and PKOH show why the treasury value line matters.
   - **Never** take the equity-statement column fact (`StatementEquityComponentsAxis=CommonStockMember`, tagged `CommonStockSharesOutstanding` or `SharesOutstanding`) as outstanding unless it equals A3: at ALOT, CSW, DK, USPH and PKOH it is the issued count (FC). The NVDA note in the shares tag card (equity-component column = period-end count) is true for NVDA but not a general rule.
   - Cover count use: a cross-check only. Flag for review when |A-path count - cover| exceeds 5%, never as a value source. In the 18 A3 cases the gap is at most 0.91% (KR).
3. **C** with a specific reason for the rest: `incomplete:denominator:no_balance_sheet_date_share_count` (HUBB, LEG, HOG, NSP, PKOH in this sample), plus not-applicable reasons for liquidation-basis filers (AIV) and companies with no publicly held common (Athene). ADS issuers stay in WO-21.
4. Expected effect on this sample (DI, not a population figure): of the 35 in-scope cover-only companies, A2 + A3 recover 26 (A4 would add 3 more once checked; HOVR waits on the "to be issued" ruling), and 5 stay C with a reason. No value comes from a cover-dated count.

## 4. Defects found outside the fallback question (route; not fixed here)
- **SPAC book value per share on the current A path** (W10 as built): the D-dated count excludes redeemable shares (5 SPACs in the 192). Whether BVPS for a SPAC is equity / non-redeemable shares or something else is a definition call: Standardization Lead.
- **PKOH** tags issued shares as `CommonStockSharesOutstanding` (equity column 18,575,430 vs 14,490,010 outstanding at the cover date): any rule reading the dimensioned column gives a value 28% too high.
- **AIV** liquidation basis: book value per share and net cash per share are not applicable from 2026-02-01; current rows show `incomplete:numerator`, which is the wrong reason class.
- **NNDM** quarterly basic WASO about 1000x the cover count; **TGL** WASO sign or scale defect (both DI, core.fact; for the market-cap and EPS guards in lane 3).
- **CDLX** undimensioned outstanding 5,451,000 below issued 5,808,000 with no treasury fact (FC that both facts are filed; cause unexplained).

## 5. Commands actually run (all read-only)
- `git archive work/data-engineer/lane2-w10-anchor pipeline/src` to the scratchpad (shared worktree left on its branch).
- The dry-run command in section 0; one `pg_stat_activity` check before each DB step (10, 10 and 8 client backends).
- Probe (`scratchpad/w10c/probe.py`), AIV canonical read, WASO read: one connection each, `statement_timeout` 20 s, read-only transactions, at most 100 company ids per statement.
- SEC: `scratchpad/w10c/secchk.py`, `mainhtm.py`, `rpar.py` through the shared cross-process limiter (`common/rate_limiter.py`, 5 req/s, declared User-Agent); about 300 requests, cached.
- Scratch files: `/private/tmp/claude-501/-Users-vikash-scrooner/b256f7de-d50a-4757-b526-8e0954fad6db/scratchpad/w10c/` (`s300.csv`, `probe.json`, `targets.json`, `control.json`, `chk.jsonl`, `chk_by_cid.json`, `waso.json`, `only_table.txt`).

## 6. Not tested
Population beyond the seed-1 300 sample; 10-K filers (all 39 were 10-Qs); the rendered R-file view of dimensioned facts (instance read only); the treasury-value condition for A4; PRLD and HOVR cover text; SGOL (instance not parsed); event 8-K documents (items read from the index, not opened) except where marked text; whether net cash per share has blanks beyond the 41 `incomplete:denominator` rows in the sample (145 are `incomplete:subtract`, a debt-input problem, not share-date).
