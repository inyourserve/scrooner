# Card family: Debt and borrowings (written 2026-10-19 by the Tag Expert)

Tags: `us-gaap:LongTermDebt`, `LongTermDebtNoncurrent`, `LongTermDebtCurrent`, `DebtCurrent`, `NotesPayable`, `NotesPayableCurrent`, `LongTermNotesPayable`, `SeniorNotes`, `SubordinatedDebt`, `LongTermLineOfCredit`, `ConvertibleNotesPayable`, `FinanceLeaseLiability` (+ Current/Noncurrent), `AdvancesFromFederalHomeLoanBanks`; related: `ShortTermBorrowings`, `CommercialPaper`, `DebtAndCapitalLeaseObligations`, `LongTermDebtAndCapitalLeaseObligations`, `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities`, `DebtLongtermAndShorttermCombinedAmount`, `DebtInstrumentCarryingAmount`, `SecuredDebt`, `UnsecuredDebt`, `ConvertibleDebt`, `OperatingLeaseLiability`.
Method and limits: as in `revenue.md`. All balances are instants: Frames periods CY2013Q4I and CY2023Q4I (calendar year-end filers only, so fiscal-year filers drop out; counts are lower bounds of reporters). "bank-like" = also files `NoninterestExpense` in CY2023 (443 filers). File 31 gives library counts as read earlier today (companies per tag, DATA-INFERRED, whole population): NotesPayable 996, NotesPayableCurrent 1,202, LongTermNotesPayable 756, LongTermLineOfCredit 421, SeniorNotes 328, SubordinatedDebt 254, AdvancesFromFederalHomeLoanBanks 240, DebtInstrumentCarryingAmount 2,021.

## 1. Official meaning (taxonomy 2025, read 2026-10-19; all instant / credit)
| Tag | Definition (shortened) |
|---|---|
| LongTermDebt | Amount, after unamortized premium/discount and issuance cost, of long-term debt. **Excludes lease obligation.** (Taxonomy total of current + noncurrent.) |
| LongTermDebtNoncurrent | Same, classified as noncurrent. Excludes lease obligation |
| LongTermDebtCurrent | Same, classified as current |
| DebtCurrent | "Amount of debt **and lease obligation**, classified as current." |
| NotesPayable | "**Including the current and noncurrent portions**, aggregate carrying amount of all types of notes payable ... with initial maturities beyond one year" |
| NotesPayableCurrent | Portions of long-term notes payable due within one year |
| LongTermNotesPayable | Notes payable with maturity after one year, "excluding current portion" |
| SeniorNotes | Including current and noncurrent portions, carrying value of notes with the highest claim |
| SubordinatedDebt | Including current and noncurrent portions, carrying value of subordinated debt |
| LongTermLineOfCredit | **Noncurrent** portion of obligations drawn from a line of credit (long, refinancing-conditions text) |
| LineOfCredit | Current and noncurrent portions drawn on a line of credit |
| ConvertibleNotesPayable | Current and noncurrent portions of convertible notes |
| ConvertibleNotesPayableCurrent | Current portion |
| FinanceLeaseLiability (+Current/Noncurrent) | Present value of lessee's obligation for lease payments from finance leases |
| OperatingLeaseLiability | Same for operating leases (not borrowings) |
| AdvancesFromFederalHomeLoanBanks | Borrowings from an FHLB |
| ShortTermBorrowings | Debt with initial terms under one year / operating cycle |
| DebtAndCapitalLeaseObligations | Short-term and long-term debt and lease obligation (total) |
| LongTermDebtAndCapitalLeaseObligations | Long-term debt and lease obligation, noncurrent |
| LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities | Long-term debt and lease obligation including current portion |
| DebtLongtermAndShorttermCombinedAmount | Long-term debt incl. current maturities plus short-term debt |
| DebtInstrumentCarryingAmount | Amount **before** unamortized discount/premium and issuance cost (gross), all types of debt |
| SecuredDebt / UnsecuredDebt | Current + noncurrent collateralised / uncollateralised obligations |
| CommercialPaper | Unsecured short-term money-market borrowings (up to ~270 days) |
Key reading: `LongTermDebt` is net of issuance cost and excludes leases; `DebtInstrumentCarryingAmount` is gross; `NotesPayable`, `SeniorNotes`, `SubordinatedDebt`, `ConvertibleNotesPayable` include the current portion in their definition; `LongTermNotesPayable` and `LongTermLineOfCredit` are noncurrent only; `DebtCurrent` includes leases.

## 2. Who reports it (Frames year-end instants, DATA-INFERRED; CY2023Q4I, bank-like in brackets; CY2013Q4I after the slash)
| Tag | CY2023Q4I | CY2013Q4I |
|---|---|---|
| LongTermDebt | 2,290 (146) | 2,443 (206) |
| LongTermDebtNoncurrent | 1,873 (15) | 2,137 (13) |
| LongTermDebtCurrent | 1,547 (5) | 1,786 (5) |
| DebtCurrent | 406 (3) | 515 (3) |
| NotesPayable | 439 (15) | 685 (33) |
| NotesPayableCurrent | 587 (2) | 851 (3) |
| LongTermNotesPayable | 326 (0) | 488 (4) |
| SeniorNotes | 114 (21) | 186 (20) |
| SubordinatedDebt | 167 (151) | 176 (131) |
| LongTermLineOfCredit | 175 (1) | 230 (0) |
| ConvertibleNotesPayable | 198 (5) | 328 (3) |
| FinanceLeaseLiability | 1,389 (78) | none (tag introduced with ASC 842) |
| AdvancesFromFederalHomeLoanBanks | 192 (178) | 260 (247) |
| ShortTermBorrowings | 786 (134) | 807 (183) |
| DebtAndCapitalLeaseObligations | 228 (22) | 553 (62) |
Reading the counts:
- `LongTermDebt` and `LongTermDebtNoncurrent` together cover 2,915 CY2023 filers; only 1,248 filers carry both. **410 more filers carry only NotesPayable/LongTermNotesPayable/SeniorNotes and neither** (union check, CY2023Q4I).
- `LongTermLineOfCredit`, `LongTermNotesPayable` and `NotesPayableCurrent` have ~0 bank-like users; they are small-company tags.
- `SubordinatedDebt` (151 of 167) and `AdvancesFromFederalHomeLoanBanks` (178 of 192) are almost entirely bank tags; only 46 and 57 of their filers also file `LongTermDebt`.
- `NotesPayable` and `NotesPayableCurrent` populations fell about a third from 2013 to 2023 (685 -> 439, 851 -> 587); `FinanceLeaseLiability` is an ASC 842 (2019+) tag (1,389 filers CY2023; no 2013 frame).
- Calendar-year-end only: fiscal-year filers (AAPL Sep, DHI Sep, BBW Jan) are NOT in these frames.

## 3. How filers use it (filings opened)
| Family | Filing | Statement and row | Tag |
|---|---|---|---|
| Big tech, FY Sep | AAPL 0000320193-25-000079 R5 (me) | "Commercial paper" 7,979M; "Term debt" current 12,350M and noncurrent 78,328M | `CommercialPaper`; `LongTermDebtCurrent`; `LongTermDebtNoncurrent`. **No total-debt tag on the face**; a total needs a sum of three tags |
| E-commerce | AMZN 0001018724-26-000004 R7 (me) | "Long-term debt" 65,648M; "Long-term lease liabilities" 87,339M | `LongTermDebtNoncurrent`; custom `amzn_LeaseLiabilityNoncurrent` (leases NOT in the standard lease tags) |
| Utility | DUK 0001326160-26-000014 R6 (me) | "Notes payable and commercial paper" 2,624M; "Current maturities of long-term debt" 7,104M; "Long-Term Debt (includes amounts related to VIEs)" 80,108M | `ShortTermBorrowings`; `LongTermDebtCurrent`; `LongTermDebtNoncurrent`. The row called "Notes payable" is `ShortTermBorrowings`, not NotesPayable |
| Oil major | CVX 0000093410-26-000078 R5 (me) | "Short-term debt" 977M; "Long-term debt" 39,781M | `ShortTermBorrowings`; **`LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities`** (includes leases and current maturities) |
| REIT | PLD 0001193125-26-051453 R2 (me) | "Debt" 35,037,073K | `LongTermDebt` as the single total |
| BDC | ARCC 0001287750-26-000006 R3 (me) | "Debt" 15,991M | `LongTermDebt` total, no current/noncurrent split |
| Rental | HTZ 0001657853-26-000008 R3/R5 (me) | "Total debt" 17,054M (HGH) | `DebtAndCapitalLeaseObligations`, includes finance leases and vehicle debt |
| Insurer | PGR 0000080661-26-000086 R4 (me) | "Debt" 6,897M | `DebtLongtermAndShorttermCombinedAmount` |
| Large banks | JPM, BAC, WFC [32] | short-term borrowings + long-term debt as separate face lines | WFC: 18,323M short-term only was stored, face debt 193,035M; BAC stored 338,216M vs face 365,904M |
| Regional bank | EWBC 0001069157-26-000009 R3 [32] and my read of the cached R-file | "FHLB advances" 3,000,000K; "Long-term debt and finance lease liabilities" 35,645K | `AdvancesFromFederalHomeLoanBanks`; `LongTermDebtAndCapitalLeaseObligations` (stored total debt 35.6M instead of 3,035.6M) |
| Broker-bank | AX 0001299709-26-000060 R3 [32]/me | FHLB advances 154,000K; "Secured financings" 576,680K; "Borrowings, subordinated notes and debentures" 342,915K | `AdvancesFromFederalHomeLoanBanks`; `SecuredDebt`; `SubordinatedDebt` (stored total debt 342.9M instead of 1,073.6M) |
| Regional bank | ZION 0000109380-26-000046 [32]/me | "Federal funds and other short-term borrowings" 3,104M; "Long-term debt" 1,472M | `FederalFundsPurchasedAndSecuritiesSoldUnderAgreementsToRepurchase`; `LongTermDebtAndCapitalLeaseObligations` |
| Non-bank (notes) | CDNL 0001193125-26-120014 R60 [27] | "Summary of Notes payable" | `NotesPayable` gross total beside its own net parts |

## 4. Siblings and confusables
- Net vs gross: `LongTermDebt` (net of discount/issuance cost) vs `DebtInstrumentCarryingAmount` (gross).
- Current + noncurrent vs parts: `LongTermDebt` = `LongTermDebtCurrent` + `LongTermDebtNoncurrent`; `NotesPayable`/`SeniorNotes`/`SubordinatedDebt` are totals of both; `LongTermNotesPayable`/`LongTermLineOfCredit` are noncurrent only.
- With vs without leases: `LongTermDebt*` exclude leases; `DebtCurrent`, `DebtAndCapitalLeaseObligations`, `LongTermDebtAndCapitalLeaseObligations*` include them. The tag name `LongTermDebtAndCapitalLeaseObligations` (EWBC, ZION) is used for rows labelled "long-term debt" regardless.
- Labels do not identify tags: DUK's "Notes payable and commercial paper" is `ShortTermBorrowings`; a row labelled "Total debt" is `DebtAndCapitalLeaseObligations` at HTZ and `DebtLongtermAndShorttermCombinedAmount` at PGR.
- Finance vs operating lease liabilities: operating leases are NOT borrowings (yfinance's "Total Debt" includes them: CATO 150,448K, ATEX 4,419K with no borrowings [22]).
- A company may file the same row under totals and parts; summing every present tag double counts (CDNL).

## 5. Known misuses and company quirks
- CDNL: `NotesPayable` gross total filed beside its net parts -> summing double counts [27].
- Carried from [32]: total-debt perimeter errors at WFC (long-term debt missing), EWBC and AX and GABC (FHLB advances missing), BAC (short-term partly missing), BNY (other borrowed funds missing), CARV; all shown today.
- NEW (me): CVX tags "Long-term debt" with the including-current-maturities-and-leases total, so adding a separate current-maturities tag would double count; AAPL has no total at all; AMZN reports lease liabilities on custom tags (a "debt incl. leases" rule built from standard tags finds nothing there).
- NEW (me): DUK's "Notes payable" row is `ShortTermBorrowings`; a rule that treats `NotesPayable` as the notes row misses it.
- RELAYED (VERIFY-W1, FILING-CHECKED by them, not re-opened by me): `LongTermDebt` includes current maturities at CSCO (0000858877-26-000132 R96) and TMO (0000097745-26-000144 R37); adding `DebtCurrent` on top double counts. Consistent with the definition read above.
- RELAYED (Verifier file 35, FILING-CHECKED by them, not re-opened by me): `LongTermDebt` is FACE value, not carrying amount, at AMZN (68,836M vs carrying 65,648M + 2,748M; 0001018724-26-000004 R69) and GOOG (49,085M vs 46,547M + 1,996M; 0001652044-26-000018 R67), and a $0.1B-rounded narrative at AAPL's 10-Q (82,300M vs 82,347M; 0000320193-26-000020 R38). Build total debt from balance-sheet carrying lines.
- NEW (me, 2026-10-21, FILING-CHECKED rendering): CAT 0000018230-26-000008 R5 shows long-term debt only per segment (two member blocks: 35M + 10,678M and 7,085M + 20,018M; CAT's columns are Machinery-Energy-Transportation and Financial Products, member names not read from the instance) on `LongTermDebtAndCapitalLeaseObligations*`, with no consolidated undimensioned fact in FSDS; APD 0000002969-25-000055 R6 shows two "Long-term debt" rows (16,769.9M and 177.5M in a second block, member not identified) on the same tag, no undimensioned FY fact in FSDS. Consolidated debt = sum of members.
- NEW population (me, FY2025 10-K face, DATA-INFERRED): 297 filers put a debt-plus-lease tag on a row labelled debt only (283 with no separate finance-lease row); BS debt is spread over 1 row (663), 2 (1,266), 3-4 (1,493), 5+ (435) rows; 512 filers (13%) have a custom debt row. Detail: R2 report sec. 10.
- Inbox accepted: `NotesPayable` is current + noncurrent by definition; edgartools maps it to Long-Term Debt; never treat it as noncurrent-only (FASB doc label, official, FILING-CHECKED on the definition).

## 6. Mapping verdict
- `LongTermDebt`: **safe as total long-term debt (net, no leases) where present** (PLD, ARCC FILING-CHECKED). Do not add `LongTermDebtCurrent` on top. Not safe where it is face value (AMZN, GOOG) or a rounded note figure (AAPL 10-Q): prefer the balance-sheet carrying lines when both exist (RELAYED, Verifier file 35).
- `LongTermDebtNoncurrent` + `LongTermDebtCurrent`: safe pair where both are present and no `LongTermDebt` exists (AAPL, DUK, AMZN noncurrent only). One-sided presence gives an incomplete total, to be flagged.
- `ShortTermBorrowings`, `CommercialPaper`: safe as short-term borrowings (DUK, CVX, AAPL).
- `NotesPayable`, `SeniorNotes`, `SubordinatedDebt`: **last-resort sole tags only if the coexistence checks pass** (file 27 proposal, still NOT_RUN in file 31); never alongside `LongTermDebt*`; include the current portion by definition. `SubordinatedDebt` and `AdvancesFromFederalHomeLoanBanks` are bank components, not totals (AX, EWBC).
- `LongTermLineOfCredit`, `LongTermNotesPayable`, `ConvertibleNotesPayable`: components; per company, only with a sum check against a face total.
- `FinanceLeaseLiability*`: lease, not debt, unless the policy decides to include finance leases (Standardization Lead); never `OperatingLeaseLiability`.
- `DebtAndCapitalLeaseObligations`, `LongTermDebtAndCapitalLeaseObligations*`, `DebtLongtermAndShorttermCombinedAmount`: totals that include leases (or current maturities); safe only when the policy label says so (HTZ, CVX, PGR FILING-CHECKED).
- Banks: **no single tag**; borrowings = short-term + FHLB advances + long-term + secured/sub debt from the face; total debt for banks needs a bank template (data-team/32 section 5).
- Evidence: FILING-CHECKED for the filings named; populations DATA-INFERRED. Verified by: Tag Expert (me), Verifier [32], Standardization Lead [27] (proposal only).

## 7. SecuritiesLoaned (Tag Expert, 2026-11-09, asked by release prep for the MSFT FY2015-FY2017 debt hold)
- **Not debt.** By element (instant, credit): the liability for collateral received when securities are lent; a secured financing at broker-dealers, outside the total-debt perimeter.
- **At MSFT it is not even a liability (FILING-CHECKED)**: FY2016 10-K 0001193125-16-662209 R5 prints "Short-term investments (including securities loaned of $204 and $75)" (106,730M, current ASSETS); R6 (parenthetical) carries the 204 on `SecuritiesLoaned`. fsn.line: inpth=true in every MSFT filing 2013-12-31..2017-12-31 (75M FY2015, 204M FY2016, up to 4,774M 2017-09-30). A filer used a liability element for an asset-side parenthetical. **Rule: a parenthetical (inpth) line is never a balance line**; coverage and debt logic should skip it (the FSN mapper already excludes inpth).
- Face users in fsn.* (10 companies): GS 886982, MS 895421, RJF 720005, TRV 96223, NLY 1043219, HOOD 1783879, 913760, 1094831, 1822993 ("Securities lending payable"): a real liability, still not debt. Anomaly, not yet opened: Farmer Mac 924805 labels a `SecuritiesLoaned` line "Debt securities issued", so a blanket tag exclusion could drop real debt there; check the filing first.

## 8. Inbox relays processed 2026-11-09 (FILING-CHECKED by the named role unless marked; not re-opened by me)
The FSN-era total-debt rule is the release-prep lane (era_detect → assemble_fsn → replay_debt_fsn), summing face borrowing lines + CommercialPaper + note current maturities + note finance leases. Each relay below is a test case for it.
- **Same tag, different perimeters**:
  - `DebtCurrent` = current LTD + CP at CSCO (10,161 = 3,500 + 6,661); = ShortTermBorrowings only at JNJ (8,500, excluding 2,000 current LTD); = finance leases only at MU (560M); = the pre-refinancing subtotal at CVX FY2016 (19,840 vs face 10,840, R98); = "short-term borrowings and current maturities" at LLY; = face "Short-term debt" including CapitalLeaseObligationsCurrent at GOOG 2015-18 (238M at 2015-09-30). The face line itself at MRK, INTC, CSCO and UNH, often with no separate current-maturity tag (Tag Mapper DATA-INFERRED; Standardization Lead, Verifier). At TSLA 2017 it is the debt-note current total (incl. related-party notes, excl. capital leases), larger than the face line; never pair it with the lease-inclusive LTDACLO (R2/R60).
  - **Rule**: classify DebtCurrent by identity (equal to one short-term tag ⇒ short-term only; L − N equal to it ⇒ already inside), never by name.
- **FASB 2025 calc** (Standardization Lead): LTDACLO = LongTermDebtNoncurrent + FinanceLeaseLiabilityNoncurrent; DebtCurrent = ShortTermBorrowings + LongTermDebtCurrent + FinanceLeaseLiabilityCurrent. The old `compute_total_debt` used LTDACLO as an alternate of LongTermDebtNoncurrent, so the lease perimeter shifted silently.
- **`LongTermDebt` containment fails** (smaller than LongTermDebtNoncurrent, LongTermDebtCurrent or half of LTDACLO) at 72 top-1000 companies / 333 instants (MAR, TSCO, CSGP, WTRG, DPZ, ALGM); differs from Noncurrent + Current by >0.5% in 1,122 of 7,102 company-instants (158 of 428 companies) (Data Engineer, Tag Mapper, DATA-INFERRED). Never take it alone.
- **Short-term tags overlap or add**: ShortTermBorrowings = LongTermDebtCurrent at MRVL, DVN, DRI, MATX, VOYA (same debt); CP/bank loans nested in OtherShortTermBorrowings at KEY, BAC; additive at DAL (+1,100M), UGI, TDG. The filer's own calc linkbase lists these as children of LiabilitiesCurrent/Liabilities (AAPL 0000320193-20-000062, ABBV, CVX, MU), so slots can be read from the filing (Data Engineer). AAPL's "Commercial paper and repurchase agreements" is `OtherShortTermBorrowings` (11,166M, 2020-06-27).
- **Missed debt tags (Verifier slot records)**: KO "Loans and notes payable" on `NotesAndLoansPayable(Current)` from 2018-09 (custom before; ShortTermBorrowings in the FY2020-22 10-Ks); ORCL's whole noncurrent debt "Notes payable and other borrowings, non-current" on `LongTermNotesAndLoans` (50-85B) from FY2017; AMD "Short-term debt" on `LinesOfCreditCurrent` (plural escapes a "LineOfCredit" regex); TSLA related-party solar bonds and notes on `DueToRelatedPartiesCurrent/Noncurrent` (100,000K + 100K at 2017-12-31); BAX noncurrent debt only on LTDACLO (6,055M, 2020-06-30; production showed 319M); CDE noncurrent debt on custom `cde:LongTermDebtAndLeaseObligationNet` (323,537K; production showed only DebtCurrent 16,996K); converts or unsecured debt as the only debt tags at NET, PANW, SNOW, CME, CDNS; zero-valued role tags gave 77 wrong zero totals (NOW 2022, DDOG 2024, ILMN 2022, ADI 2016-20).
- **CVX refinancing**: face ShortTermBorrowings = DebtCurrent − ShortTermDebtRefinancedAmount (2022: 6,014 − 4,050 = 1,964); the reclassified amount sits inside the face long-term line; CVX `LongTermDebt` excludes it (22,700 vs face 29,960 at 2015-03-31); production was 2.8-17.1B low.
- **Not debt, though the name says so**: `DepositsReceivedForSecuritiesLoanedAtCarryingValue` = face "Securities lending payable" at MSFT (430M, 2014-12-31) and GOOG (3,266M, 2015-09-30): collateral liability (see §7, SecuritiesLoaned). `UnamortizedLossReacquiredDebtNoncurrent` = NFG's "Unamortized Debt Expense" ASSET (14,922K). `OtherLongTermDebtNoncurrent` = a component under a face "Total long-term debt" subtotal (CNP 19,902 of 20,566; D 19,790 of 23,245): never additive.
- **Principal vs carrying**: `DebtInstrumentCarryingAmount` is "Unpaid Principal Balance" at TSLA (8,104,869K vs carrying 7,515,847K) and principal at GOOG 2025 (49,085M vs 48,543M). The tag name does not guarantee carrying amount. `CapitalLeaseObligations` at AMZN 2016 = GROSS minimum payments 9,406 (PV 9,077).
- **Leases era break**: FinanceLeaseLiability on 0.1% / 20.9% / 22.4% of top-1000 BS instants (2015-17 / 2018-20 / 2021+); before FY2019 finance leases sit inside LTDACLO*, so lease-in vs lease-out totals are not comparable across that break (Tag Mapper, DATA-INFERRED). META FY2019 10-K prints the 2019 noncurrent finance lease 418 under the 2018-12-31 context (filer context error; 2018 debt = 0) (R47).
- **Capitalization-format utilities** (NI, FE, AWK): LTDACLO/LongTermDebtNoncurrent prints after common equity inside "Total capitalization"; it is still a liability; position guards must not reclass it (0001111711-17-000032 R5, 0001031296-18-000015 R5, 0001564590-15-003448 R2).
- **Finance-lease location guard**: `FinanceLeaseLiabilityCurrent/NoncurrentStatementOfFinancialPositionExtensibleList` names the BS element holding the finance lease (MU: DebtCurrent and LTDACLO; GOOG 2025: AccruedLiabilitiesCurrent and OtherLiabilitiesNoncurrent; AMZN: AccruedLiabilitiesCurrent and a custom). Read it before adding note finance leases to a total (Standardization Lead, instances).

## 9. Folded in from the FSN-expert per-tag cards (handover 2026-11-10, branch docs/fsn-expert 78ea731c)
- **`CommercialPaper` can be the only short-term debt line, labelled "Short-term debt"**: MSFT FY2024 10-K 0000950170-24-087843 R4 "Short-term debt 6,693" (**FILING-CHECKED again by me 2026-11-10**). MSFT used `ShortTermBorrowings` for the same label through FY2018 (2017-06-30 9,072; fsn.* 2026-11-10), so label and tag switch independently. Face use in the top-100 extract: 13 names (AMGN, ADI, AAPL, NEE, HD, JPM, MSFT, QCOM, TXN, WMT …), labels "Commercial paper" 141, "Short-term debt" 48 (FSN expert, DATA-INFERRED). The old production MSFT total_debt FY2024 (44,937M) omitted it; the face total is 51,630M. Rule: a face CP line is a debt component; never add it on top of a ShortTermBorrowings/DebtCurrent line that is its calc parent.
- **NEW trap (me, 2026-11-10, fsn.value)**: the same filing carries `CommercialPaper` twice at 2024-06-30, both non-dimensional: 6,693 (decimals −6, the face) and 6,700 (decimals −8, a note's "$6.7 billion"). `select` uses face prints only and tolerates rounding (`select._same`, `tol_of(dcml)`), so it is safe. But a note-sourced sum (the debt lane, any max()/any-value read) must take the value with the finest `dcml` (or the face print), never the max. **Confirmed by the FSN expert 2026-11-10**: in all five filings that print 2024-06-30 `CommercialPaper`, 6,693 is `iprx` 0 (dcml −6) and 6,700 is `iprx` 1 (dcml −8). FSN's `iprx` ranks copies by precision (0 = finest), so the rule is: **filter `iprx = 0`** for any note-sourced read (FSN-GUIDE §5 on docs/fsn-expert).
- **`FinanceLeaseLiability`**: a note total, on no top-100 face (FSN expert, 101 companies). MSFT: 2,538 (FY2017) … 66,594 (FY2026) $M; MSFT keeps finance leases inside property and equipment, other current liabilities and other long-term liabilities (LesseeLeasesPolicyTextBlock 0001564590-17-020171). "Total debt including finance leases" needs the note value as its own labelled component; never infer it from "Other liabilities". GOOG 2026-06-30: FinanceLeaseLiability 2,590 = Current 449 + Noncurrent 2,141; face debt is only LongTermDebtNoncurrent 98,165; note LongTermDebtCurrent 1,999 (fsn.* 0001652044-26-000071), so no lease is inside the debt tags.

## 10. Release-prep relay 2026-11-11 (FAMILY-RELEASE-CASE-2026-11-09 §2-§6 on work/release/family-release-case-2026-11-10 490bebc)
- Position is not meaning: the calc_position seeds mapped any custom child of LiabilitiesCurrent as total debt (7,335 lines, 5,441 filings, 236 companies; "Accounts payable and accrued liabilities" 97.9M, "Accounts payable, client accounts" 1,941M) — dropped. Total debt is a sum of classified members, never one mapped line.
- After skipping inpth lines, MSFT FY2015-FY2026 borrowings = the FSN-expert face series 12/12 (35,292 / 53,461 / 86,194 / 76,240 / 72,178 / 63,327 / 58,146 / 49,781 / 47,237 / 51,630 / 43,151 / 40,294; pilot 42665907782, work/fsn/debt-lane-port b22f896). MSFT finance leases are note-only (FY2018 4,301 = Verifier; FY2017 2,538 pre-ASC 842, FY2025 46,172, FY2026 66,594 not yet verified).
- GOOG 2026-06-30 = 102,754 = 98,165 + 1,999 + 2,590 (corrected; "100,164 noncurrent" was a mislabel). META 2022-12-31 = 9,923 + 687 = 10,610 (lease from the earlier copy when both copies' debt lines agree); META 2016-2018 total debt 0 with no member facts (debt-free; nothing to cite).
- Combined debt-and-lease members (PGR DebtLongtermAndShorttermCombinedAmount; TMO NI FE AWK APD LTDACLO and …Current) get no note lease on top; DebtCurrent is "combined" only with evidence. Note-vs-face LongTermDebt differences are flags (CSCO +6,661M, TMO +265M, AMZN −771M).
- Segment-only debt: CAT through 2020-06-30 = six custom segment face lines (Financial Products / ME&T, due within and after one year, short-term borrowings) = 38,622M, then held; APD through 2023-03-31 with `NotesPayableRelatedPartiesNoncurrent` as a member. Open: does CAT's segment sum equal its consolidated total (inter-segment elimination)? DUK: every key held (NotesPayable missing member). Banks held (`bank_debt_perimeter_pending`).
- AMZN face "Long-term lease liabilities" combines operating and finance leases; finance part from the note (Verifier).

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.
