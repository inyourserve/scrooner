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
- Inbox accepted: `NotesPayable` is current + noncurrent by definition; edgartools maps it to Long-Term Debt; never treat it as noncurrent-only (FASB doc label, official, FILING-CHECKED on the definition).

## 6. Mapping verdict
- `LongTermDebt`: **safe as total long-term debt (net, no leases) where present** (PLD, ARCC FILING-CHECKED). Do not add `LongTermDebtCurrent` on top.
- `LongTermDebtNoncurrent` + `LongTermDebtCurrent`: safe pair where both are present and no `LongTermDebt` exists (AAPL, DUK, AMZN noncurrent only). One-sided presence gives an incomplete total, to be flagged.
- `ShortTermBorrowings`, `CommercialPaper`: safe as short-term borrowings (DUK, CVX, AAPL).
- `NotesPayable`, `SeniorNotes`, `SubordinatedDebt`: **last-resort sole tags only if the coexistence checks pass** (file 27 proposal, still NOT_RUN in file 31); never alongside `LongTermDebt*`; include the current portion by definition. `SubordinatedDebt` and `AdvancesFromFederalHomeLoanBanks` are bank components, not totals (AX, EWBC).
- `LongTermLineOfCredit`, `LongTermNotesPayable`, `ConvertibleNotesPayable`: components; per company, only with a sum check against a face total.
- `FinanceLeaseLiability*`: lease, not debt, unless the policy decides to include finance leases (Standardization Lead); never `OperatingLeaseLiability`.
- `DebtAndCapitalLeaseObligations`, `LongTermDebtAndCapitalLeaseObligations*`, `DebtLongtermAndShorttermCombinedAmount`: totals that include leases (or current maturities); safe only when the policy label says so (HTZ, CVX, PGR FILING-CHECKED).
- Banks: **no single tag**; borrowings = short-term + FHLB advances + long-term + secured/sub debt from the face; total debt for banks needs a bank template (data-team/32 section 5).
- Evidence: FILING-CHECKED for the filings named; populations DATA-INFERRED. Verified by: Tag Expert (me), Verifier [32], Standardization Lead [27] (proposal only).
