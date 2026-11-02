# FSN guide: SEC Financial Statement and Notes data sets

Owner: the FSN expert (Chief Financial Data Expert role). Written 2026-11-02. Read this before writing any code that reads `fsn.*` or an FSN zip.

Evidence labels:
- **SPEC**: SEC's technical specification, `https://www.sec.gov/files/aqfsn_1.pdf`, downloaded 2026-11-02 (HTTP 200, 269,165 bytes). It is linked from the data set page `https://www.sec.gov/data-research/sec-markets-data/financial-statement-notes-data-sets`.
- **MEASURED**: counted on our extracts, built this session. They hold all 76 published sets (2009q1 to 2026_09) filtered to 101 CIKs: the cohort top 100, plus TRV, PLD and Exxon Mobil's pre-2026 CIK 34088.
- **FILING-CHECKED**: the R page on sec.gov was opened and matches.

Where a measured fact contradicts the spec, **the data wins**. Each contradiction is marked **SPEC WRONG**.

## 0. What a set is
- **Cadence:** quarterly zips for 2009q1–2025q3, then **monthly** from 2025_10 (`2025_10_notes.zip` … `2026_09_notes.zip`). That is 76 sets on the page today (MEASURED).
- **Size:** a quarterly zip is about 0.4–0.8 GB (2025q3: 463,365,283 bytes).
- **Members:** `sub.tsv`, `tag.tsv`, `dim.tsv`, `ren.tsv`, `cal.tsv`, `pre.tsv`, `num.tsv`, `txt.tsv`, `readme.htm` and `notes-metadata.json`. All are tab-separated with a lower-case header. The spec says `.txt`; the files are `.tsv` (MEASURED, 2025q3).
- **Forms:** every XBRL form except 485BPOS, 497 and the SDR family (SPEC). That includes 8-K cover-page XBRL, DEF 14A pay-versus-performance and 11-K. In our 2025q3 extract, 300 of 412 submissions are 8-Ks (MEASURED). **Always filter `sub.form`** to 10-K, 10-Q, 10-K/A, 10-Q/A, 10-KT and 10-QT.
- **Which set holds a filing:** the one covering its acceptance date. A filing accepted after 17:30 ET on the quarter's last business day goes to the next set (SPEC).
- **Access:** one request per zip, a declared User-Agent, sec.gov only.
  - Download URL pattern: `https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/{2025q3|2025_10}_notes.zip`.
  - The extract for 101 CIKs over all 76 sets is 642 MB gzip (MEASURED). It took about 25 s per set.

## 1. Keys and joins
```
sub(adsh) 1─* num(adsh, tag, version, ddate, qtrs, uom, dimh, iprx)
sub(adsh) 1─* pre(adsh, report, line)     pre.(adsh,report) ─ ren(adsh,report)
sub(adsh) 1─* cal(adsh, grp, arc)          cal.ptag/ctag ─ tag(tag, version)
num.(tag,version) ─ tag(tag, version)      num.dimh ─ dim.dimhash
txt(adsh, tag, version, ddate, qtrs, dimh, iprx)
```
- **Line → value:** join `pre (adsh, tag, version)` to `num (adsh, tag, version)`. pre has no period, so a line carries every column (ddate, qtrs) of that tag in that filing. **The column set of a statement is not in FSN.**
  - Derive it as the (ddate, qtrs) columns for which that statement's anchor total has a value in the same filing. The store design does this (FSN-STORE-DESIGN §3).
- **One tag on two statements:** e.g. NetIncomeLoss on the IS, CI and CF. pre then has a row on each report, and num has one value per column (SPEC §5.7). **You cannot tell from num which statement a value was printed on.**
- **Custom tags:** `version` = the adsh of the filing that defined the tag, usually the filing itself (SPEC; MEASURED: 22,316 of 176,913 num rows in 2025q3 have version = an adsh).
  - A custom tag of the same name in two filings is two different `(tag, version)` keys. Join across filings by **tag name**, not by `(tag, version)`, or every custom line breaks its history at each filing.

## 2. SUB (one row per submission)
| Column | Meaning | Pitfall (evidence) |
|---|---|---|
| adsh | accession, `nnnnnnnnnn-nn-nnnnnn` | the PK; join key everywhere |
| cik | registrant CIK, no leading zeros | XOM's cohort CIK is 2115436 (ExxonMobil Holdings Corp), which has filed **only 8-Ks** (first 0002115436-26-000003, set 2026_07). Every 10-K/10-Q through 2026_09 is under Exxon Mobil Corp, CIK 34088 (latest 0000034088-26-000093). A cohort CIK that is a new holding company finds **zero** periodic filings unless the predecessor CIK is read (MEASURED; the pilot does read 34088) |
| name, former, changed | EDGAR name as of filing | "WAL MART STORES INC" → "Walmart Inc."; never key on name |
| sic | SIC at filing date | proposes a sector, never decides it (SECTOR-TEMPLATES §1) |
| countryba … mas2, countryinc, stprinc, ein | addresses, incorporation | not used for values |
| afs | filer status (1-LAF … 5-SML) | XBRL-sourced |
| wksi | WKSI flag | |
| fye | fiscal year end `mmdd` | 52/53-week filers show the nominal month end (HD `0131`; its FY2024 ended 2025-02-02) |
| form | submission type | filter it (§0) |
| period | balance sheet date `yyyymmdd` | **month-end rounded like ddate**, not the real date: HD 10-Q 0000354950-25-000217 has period 20250731 for a balance sheet dated 2025-08-03 (datp −3, §5); PepsiCo's Q2 ending 2025-06-14 has period 20250531 (MEASURED) |
| fy | fiscal year **focus** (DEI) | the company's own naming, not arithmetic. January-FYE filers (HD, WMT, NVDA, CRM, TJX) label the year that **ends** in January 2026 as fy 2025: HD 10-Q 0000354950-25-000217, period 20250731, fy 2025 (MEASURED: 266 of 5,944 periodic rows differ from "calendar year of the FY end") |
| fp | FY, Q1–Q4, H1, H2, M9, T1–T3, M8, CY | 10-Q Q2 can be H1 (SPEC); MSFT and HD always Q1/Q2/Q3/FY (MEASURED) |
| filed | filing date | |
| accepted | acceptance timestamp `yyyy-mm-dd hh:mm:ss.0` | **the vintage order**; two filings on one day are ordered by it |
| prevrpt | 1 = this submission was amended before the set's cutoff | 0 for all 412 rows in our 2025q3 extract; an amendment filed in a later set does **not** flip it (SPEC wording "prior to the end cutoff date of the data set") |
| detail | detail-tagged notes | |
| instance | instance file name | URL = `https://www.sec.gov/Archives/edgar/data/{cik}/{adsh without dashes}/` |
| nciks, aciks | co-registrant count and the other CIKs | NEE 10-Q 0000753308-25-000040: nciks 2, aciks 37634 (FPL); PLD: aciks 1045610 (Prologis LP). `PARTIAL` suffix when the list is truncated (SPEC) |
| pubfloatusd, floatdate, floataxis, floatmems | public float | 10-K only |

## 3. TAG (one row per tag × version)
Columns:
- `tag`, `version`;
- `custom` (1 = defined by a filing);
- `abstract` (1 = no numeric fact);
- `datatype` (monetary, perShare, shares, …);
- `iord` (I = instant, D = duration; **empty for abstract tags**: 7,971 of 17,891 rows in 2025q3 are empty, MEASURED);
- `crdr` (C/D natural balance, monetary only);
- `tlabel` (the taxonomy label, or the filer's label for a custom tag);
- `doc` (the definition, truncated to 2,048 characters).

Pitfalls:
- The full TAG file lists every standard tag of every taxonomy, used or not (SPEC). Our extract keeps only the tags used by our filings (17,891 rows in 2025q3, of which 13,873 are custom).
- **crdr is the tag's balance, not the printed sign.** MSFT's custom `GainLossOnInvestmentsAndDerivativeInstruments` is stored −2,136M for the quarter ended 2024-12-31 while the R6 page prints **2,136** on the line "Net recognized losses (gains) on investments and derivatives".
  - The label role negates it (FILING-CHECKED: MSFT 10-Q 0001193125-26-027207 R6).
  - Read the sign from num, never from the rendered page.

## 4. DIM (one row per axis/member combination)
| Column | Meaning | Pitfall |
|---|---|---|
| **dimhash** | MD5 of `segments` | **SPEC WRONG**: the column is named `dimhash`, not `dimh` (header of `dim.tsv`, every set we read). num and txt call it `dimh` |
| segments | `Axis=Member;` pairs in lexical axis order, with the "Statement", "Axis", "Member" and "Domain" affixes trimmed | `LegalEntity=FloridaPowerLightCompany;` (NEE 0000753308-25-000040) |
| segt | segments truncated at 1,024 characters | |

The no-dimension key is **`0x00000000`**. **SPEC WRONG**: the spec says "0" (MEASURED: first row of `dim.tsv`, and `num.dimh` of every undimensioned fact).

## 5. NUM (one row per distinct fact)
| Column | Meaning | Pitfall (evidence) |
|---|---|---|
| adsh, tag, version | fact identity | |
| ddate | period end **rounded to the nearest month end** | HD balance sheet 2025-08-03 → `20250731`; HD 2025-02-02 → `20250131` (0000354950-25-000217). **PepsiCo Q2 ending 2025-06-14 → `20250531`**: the rounded date can fall in the month **before** the quarter's own month (MEASURED, 2025q3). Two real dates in one month collide: 52/53-week filers and merger predecessors (mind `before-any-write-keyed-on-fsn-columns-...`) |
| qtrs | duration in quarters, rounded; 0 = instant | a 13-week quarter = 1, YTD 26 weeks = 2; durp keeps the remainder |
| uom | unit | **EPS is `USD`, not `USD/shares`** (MSFT 0000950170-25-100235 EarningsPerShareDiluted 20230630 qtrs 4 uom USD value 9.6800; 1,507 of 1,507 EPS rows in 2025q3 are USD, MEASURED). Shares are `shares` |
| dimh | dimension hash, `0x00000000` = none | |
| iprx | tie-breaker between otherwise identical facts | **SPEC WRONG**: the spec calls it "a positive integer"; it **starts at 0** (161,366 of 176,913 rows are 0 in 2025q3). iprx 0 is the highest-precision copy, see below |
| value | as filed, unscaled, 4 decimals | **empty when the fact is nil**; such rows carry dcml −32768 (381 of 381 in 2025q3, e.g. AMD 0000002488-25-000108 CommitmentsAndContingencies). 0.00001 par values truncate to 0.0000 |
| footnote, footlen | superscript footnote text | |
| dimn | number of axes | |
| coreg | co-registrant or entity | see the coreg finding below |
| durp | duration minus `qtrs`, as a fraction of a quarter | 0.0137 = one extra day on a 4-quarter year; it is a fraction, as the spec says |
| datp | **ddate − actual end date, in days** | **SPEC WRONG on both unit and sign**: the spec says "fraction of 1" and gives −2/31 for 29 Dec → 31 Dec. Real rows give **+3.0** for AMD's 2024-12-28 → 20241231 and **−3.0** for HD's 2025-08-03 → 20250731. Actual date = ddate − datp days (MEASURED) |
| dcml | XBRL `decimals` | −6 = millions, 2 = cents, **32767 = INF (exact)**, **−32768 = nil value** (MEASURED). The spec only mentions 32767 |

### The face filter: `dimn = 0 AND iprx = 0` (coreg empty follows)
- **iprx > 0 rows are duplicates at lower precision**, mostly the same number repeated in a note.
  - 7,533 dimn=0 key groups have more than one iprx in 2025q3; **195 of them differ in value**, 152 on statement tags.
  - In every one we read, iprx 0 has the finer `dcml`: CAT `TreasuryStockSharesAcquired` 4,578,023 (dcml INF) vs 4,600,000 (dcml −5); ADI `CommercialPaper` 547,738,000 (−3) vs 547,700,000 (−5) (MEASURED).
  - **Keep iprx 0.**
- **coreg is set only when the fact's single dimension is the LegalEntity axis.**
  - Every coreg row in 2025q3 has dimn = 1 and segments `LegalEntity=…` (1,016 of 1,016). NEE example: `Assets` 20250630 101,805M, dimn 1, coreg `FloridaPowerLightCompany`.
  - A fact with LegalEntity **plus** another axis has an **empty** coreg: NEE `AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax`, dimn 2, segments `FinancialInstrument=…;LegalEntity=FloridaPowerLightCompany;`, coreg empty.
  - So "LegalEntity members live in coreg" is **only half true**. `dimn = 0` already excludes every coreg row; "empty coreg" is redundant once dimn = 0.
  - coreg also names employee benefit plans (`EBPJapan`, 11-K-style data) and trusts (AmEx `AmericanExpressLendingTrust`).
- **dimn = 0 is necessary but not sufficient for "the face"**:
  - (a) Statement lines can be **dimensional**. MSFT's income statement prints Product / Service-and-other revenue and cost as `ProductOrServiceAxis` members (MSFT 0001193125-26-323660 R2: Product revenue 64,696M, Service and other 267,143M; FILING-CHECKED).
  - The equity statement is entirely on `StatementEquityComponentsAxis`.
  - (b) A dimn=0 fact need not be on any statement: num holds **note facts** too (MSFT `InterestExpense` FY2024 2,935M is in the Other income note only). A value is "on the face" only if its tag is a pre line of a statement report **and** its (ddate, qtrs) is a column of that statement.

## 6. PRE (one row per presented line)
| Column | Meaning | Pitfall |
|---|---|---|
| adsh, report, line | PK; `report` = R-file number | |
| stmt | BS, IS, CF, EQ, CI, CP, UN; **empty for note/detail reports** | FSN pre covers **notes too** (76,947 of 95,991 rows in 2025q3 have an empty stmt, MEASURED). FSDS pre is statements only. **Values outside the spec: `SI`** (ABT equity statement, 2025q3). **Mislabels: PLD's partnership "Statements of Capital" are `UN`; MPC's "Equity and Redeemable Noncontrolling Interest" is `UN`** |
| inpth | 1 = parenthetical | Parenthetical *reports* (e.g. "BALANCE SHEETS (Parenthetical)") also carry stmt BS; detect them by `ren.shortname` |
| tag, version | | |
| prole | label role (terseLabel, totalLabel, negatedLabel …) | |
| plabel | the label printed on the line | the same tag changes label across filings (MSFT `NonoperatingIncomeExpense`: "Other income (expense)", "Other income", "Other income, net", "Other income (expense), net") |
| negating | 1 = rendered negated | the sign rule of the page, not of the value |

- **pre is not in statement order.** Sort by `line` within `(adsh, report)`.
  - Lines of MSFT FY2025 10-K R2 in file order: 6, 1, 8, 18, 19, 20, 12, 9, 15, 16, 17, 14, 13, 4, 10, 7, 11, 5, 23, 21, 22, 2, 3 (MEASURED). **Confirmed.**
- **Which reports are statements:** `ren.menucat = 'S'`.
  - MSFT's Q1 FY2014 10-Q (0001193125-13-409855) has **no** report with menucat S in FSN, so any menucat-only rule loses that filing (MEASURED).
  - Use pre.stmt as a second signal; never use either alone for PLD or ABT.
- **Abstract, axis and member rows are pre lines with no value** (`StatementTable`, `ProductOrServiceAxis`, `ProductMember`). Drop them by `tag.abstract = 1` or by the absence of a value.

## 7. CAL (one row per calculation arc)
Columns: adsh, grp, arc, `negative`, ptag, pversion, ctag, cversion.
- **`negative` holds the weight itself, 1 or −1.**
  - **SPEC WRONG**: the spec calls it a BOOLEAN, "TRUE if the arc is negative".
  - MSFT FY2025 10-K 0000950170-25-100235: `GrossProfit ← RevenueFromContractWithCustomerExcludingAssessedTax negative=1`, `GrossProfit ← CostOfGoodsAndServicesSold negative=-1`.
  - 2025q3 counts: 1 → 11,955, −1 → 3,281, no 0 (MEASURED). **Team belief confirmed.**
- **grp = one calculation group (role).** The same parent can have different children in different groups; key the check on (grp, ptag).
- **Calc arcs cross statements.** NetIncomeLoss is a child of `ComprehensiveIncomeNetOfTax` (CI) and of `NetCashProvidedByUsedInOperatingActivities` (CF) in one filing. Restrict a statement's calc tree to arcs whose parent **and** child are lines of that statement.
- **Incomplete trees are normal.** MSFT `WeightedAverageNumberOfDilutedSharesOutstanding ← WeightedAverageNumberOfSharesOutstandingBasic` (the dilutive-effect child is a note fact). `PropertyPlantAndEquipmentNet ← accumulated depreciation` (gross is parenthetical).
  - Check a parent only when **all** its children have values.
- **Coverage (MEASURED on our 101 CIKs):**
  - **No cal rows at all before 2013q3.** 2009q2 to 2013q2: 0 to 2 of 80-odd periodic filings per set have cal. From 2013q4: 0–5 periodic filings per set lack cal, for example:
    - MSFT FY2024 10-K 0000950170-24-087843 and Q1 FY2025 10-Q 0000950170-24-118967 (both Donnelley, 0000950170);
    - PLD, BLK, ORCL, DE and SCCO in 2024;
    - TSLA and MO in several years.
  - That is 1–4% of top-100 periodic filings per set, **not the ~11% the mind entry `sec-financial-statement-and-notes-data-set-fsn-cal-tsv-repro` reports for 2024q4** (that count was over 988 cohort filings; our 2024q4 is 4 of 101). MSFT's FY2025 10-K is back to full cal.
  - A missing cal is a filer-agent issue, not a company trait.

## 8. REN (one row per R page)
Columns: adsh, report, rfile (H/X), `menucat` (C cover, S statement, N note, P policy, T table, D detail, O other, U uncategorised), shortname, longname, roleuri, parentroleuri, parentreport, ultparentrpt.
- **Rendering version:** the report numbers are those of the EDGAR renderer current at **publication**, which can differ from the R numbers of the filing as originally rendered (SPEC §5.6). For recent filings they matched: MSFT 0001193125-26-323660 R2/R4/R6 = IS/BS/CF on sec.gov (FILING-CHECKED).
- **Statement reports per periodic filing:** 4 to 11 (MEASURED, 2025q3). Parentheticals count.

## 9. TXT (one row per non-numeric fact)
- Holds every text block (policies, notes) as plain text.
  - **This is where restatement reasons live**: MSFT `NewAccountingPronouncementsPolicyPolicyTextBlock` in 0001193125-16-550254 gives "As reported / As adjusted" for the ASU 2016-09 early adoption.
  - `PriorPeriodReclassificationAdjustmentDescription` and `BasisOfAccountingPolicyPolicyTextBlock` ("We have recast certain prior period amounts on our consolidated cash flows statements", 0001193125-26-027207) are the first places to look.
- **SPEC oddity:** txt `dcml` holds a **language** rank (32767 = en-US), not decimals.
- `value` is truncated at 2,048 characters (SPEC), but long text blocks in our extracts run beyond that. Treat txt as evidence text, not a complete note.

## 10. Team beliefs: verdicts
| Belief | Verdict | Evidence |
|---|---|---|
| pre is not in statement order (use `line`) | **TRUE** | §6, MSFT 0000950170-25-100235 R2 file order |
| cal `negative` is the arc weight | **TRUE** (spec wrong) | §7, 1/−1 only |
| num needs dimn=0, iprx=0 and empty coreg to equal the face | **PARTLY TRUE**: necessary, not sufficient. Empty coreg is implied by dimn=0. The face also has dimensional lines (MSFT Product/Service), and dimn=0 includes note facts | §5 |
| LegalEntity members live in coreg | **PARTLY TRUE**: only when LegalEntity is the only axis. With a second axis, coreg is empty | §5, NEE |
| dates match by nearest month-end | **TRUE, with a trap**: ddate can fall in the previous month (PepsiCo 2025-06-14 → 20250531). `datp` (days) recovers the real date. Never compare a period's *label month* with ddate | §5 |
| a huge decimals value (INF) means exact | **TRUE for 32767.** **−32768 is not "exact": it marks a nil (empty) value.** Code that treats \|dcml\| > 20 as exact (fsn_store/checks.py `DCML_EXACT`) is safe only because nil rows have no value | §5 |
| EPS uom is USD in FSN | **TRUE** | §5 |

## 11. Recipe: one company's face statements (what the store must do)
1. **Filings:** `sub` where cik ∈ the company's CIKs (successor and predecessor) and form ∈ periodic, ordered by `accepted`.
2. **Statement reports:** `ren.menucat = 'S'`, with `pre.stmt` as the second signal. Exclude parentheticals by shortname.
3. **Lines:** pre rows of those reports, sorted by `line`. Drop abstracts and axis/member rows.
4. **Values:** num where (adsh, tag, version) = the line's, `iprx = 0`, value not empty. Use dimn=0 for the line total; keep dimensional rows when the line is a member row under an axis on the face.
5. **Columns:** the (ddate, qtrs) for which the statement's anchor total has a value (Assets for BS; NetIncomeLoss or ProfitLoss for IS; the CFO total for CF).
6. **Checks:** the calc tree restricted to that statement, parents with all children valued only; weight = `negative`.
7. **History:** join filings by tag **name**. A period printed by several filings is a vintage series. A changed value is a restatement or recast, and its reason is in that filing's txt.
