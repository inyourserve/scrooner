# Card family: Bank net loans and allowance for credit losses (written 2026-10-22 by the Tag Expert)

Tags: `us-gaap:FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss` (FRAfter), `FinancingReceivableExcludingAccruedInterestBeforeAllowanceForCreditLoss` (FRBefore), `LoansAndLeasesReceivableNetReportedAmount` (LLNet), `NotesReceivableNet`, `LoansAndLeasesReceivableNetOfDeferredIncome`, `FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest` (ACLExcl), `FinancingReceivableAllowanceForCreditLosses` (ACL), `LoansAndLeasesReceivableAllowance` (ALLL).
Asked by: Sector Analyst, SECTOR-ROWS-REVIEW rows B10 and B12 and section 8 item 1.
Method: FASB 2026 taxonomy; one read-only DB connection (`company_sec_tag` for eras; `core.fact` same company and period, authoritative, undimensioned, since 2015, chunked); bank population = active companies with SIC 6021, 6022, 6029, 6035, 6036 (**326**). 3 filings opened.

## 1. Official meaning (FASB 2026)
| Tag | Period / balance | Definition | Status |
|---|---|---|---|
| FRAfter | instant / debit | "Amortized cost excluding accrued interest, after allowance for credit loss, of financing receivable. Excludes net investment in lease." | current (CECL-era element) |
| FRBefore | instant / debit | same, before allowance | current |
| LLNet | instant / debit | "Amount after allowance and deduction of deferred interest and fees, unamortized costs and premiums and discounts from face amounts, of loans and leases held in portfolio ..." | current (pre-CECL wording; not deprecated in 2026) |
| NotesReceivableNet | instant / debit | standard label "Financing Receivable, after Allowance for Credit Loss": "Amortized cost, after allowance for credit loss, of financing receivable. Excludes ... loss sharing agreement and net investment in lease." | current |
| ACLExcl | instant / credit (contra) | "Amount excluding accrued interest, of allowance for credit loss on financing receivable. Excludes net investment in lease." | current |
| ACL | instant / credit (contra) | "Amount of allowance for credit loss on financing receivable ..." | current |
| ALLL | instant / credit | "Amount of allowance to cover probable credit losses on loans and leases ..." ("probable" = incurred-loss, pre-CECL wording) | current, not deprecated |
Not in the 2025 or 2026 schema: `LoansReceivableNet`. It is a REMOVED historical element, still in our data: 143 companies, 1,817 facts, 2007-09-30 to 2020-03-31 (`sec_tag_library`). Keep it for pre-2020 periods (doc 21 sec. 8 rule 8: keep every historical tag). The `AllowanceForLoanAndLeaseLosses*` elements that exist (WriteOffs 317 companies, RecoveriesOfBadDebts, ProvisionForLossGross/Net, AdjustmentsNet, PeriodIncreaseDecrease, RealEstate ...) are roll-forward COMPONENTS, not the allowance balance. The real pre-CECL allowance total is `LoansAndLeasesReceivableAllowance`.

## 2. Who reports it (banks, DATA-INFERRED, `company_sec_tag`, read 2026-10-22)
| Tag | Banks | First period (any / median) | Median last period | Banks current (last >= 2025-06-30) |
|---|---|---|---|---|
| FRAfter | 229 | 2019-12-31 / 2022-12-31 | 2026-06-30 | 224 |
| FRBefore | 218 | 2019-12-31 / 2022-12-31 | 2026-06-30 | 215 |
| LLNet | 282 | 2008-06-30 / 2010-12-31 | **2022-12-31** | 6 |
| LoansAndLeasesReceivableNetOfDeferredIncome | 186 | 2006 / 2010 | 2022-09-30 | 1 |
| NotesReceivableNet | 227 | 2010 / 2019-12-31 | 2023-12-31 | 86 |
| ACLExcl | 238 | 2018-09-30 / 2020-12-31 | 2026-06-30 | 233 |
| ACL | 264 | 2006 / 2012-12-31 | 2023-06-30 | 85 |
| ALLL | 284 | 2006 / 2010-12-31 | **2022-12-31** | 3 |
**Era break:** banks moved from LLNet / ALLL to FRAfter / ACLExcl between 2020 and 2023 (CECL adoption and the taxonomy elements that came with it). For the 2015-to-date window (invariant I11) most banks need BOTH tags of each pair, by period. The Sector Analyst's counts (FRAfter 33/44, LLNet 1/44) are right for the latest 10-K and say nothing about 2015-2022.

## 3. How filers use it
| Filing | Rows | Finding |
|---|---|---|
| EFSC 10-K 0001025835-26-000058 (efsc-20251231.htm) (me) | "Total loans, net" `FRAfter` 11,660,316K; "ACL on loans" `ACLExcl` 140,022K; ACLExcl also on the roll-forward rows by segment member | the current clean layout |
| OSBC 10-Q 0001558370-23-008865 (tmb-20230331x10q.htm) (me) | Face "Net loans" `LLNet` 3,949,962K (2023-03-31) / 3,820,129K (2022-12-31); "Allowance for credit losses on loans" `ACLExcl` 53,392K / 49,480K; **undimensioned `FRAfter` 55,179K / 50,478K = the "Total" row of the collateral-dependent loans table in a note** | **misuse: FRAfter undimensioned is a note SUBSET at OSBC, while the face net-loans line stays on LLNet after CECL** |
| Citigroup, JPM, BAC, FLG [interest.md, 32] | provision and interest lines | see interest.md |
Population checks (banks, since 2015, tolerance 0.5%):
| Pair | Banks with both tags | Banks sharing periods | Shared periods | Equal | Differ |
|---|---|---|---|---|---|
| LLNet vs FRAfter | 197 | 83 | 103 | 97 | 6 (OSBC 3,820M vs 50.5M; BANC 28,408M vs 7,029M; EFSC 2022; HBAN 2021 109,890M vs 109,237M; FINW) |
| NotesReceivableNet vs FRAfter | 148 | 124 | 191 | 188 | 3 (LKFN 2020 250K vs 4,588M; UBCP; PNFP 2024 35,071M vs 42,122M) |
| ALLL vs ACLExcl | 207 | 155 | 610 | 589 | 21 (BAC 2019-12-31 9,416M vs 12,358M: likely the CECL day-1 figure on a year-end context, not opened; CMTV sign; PFBX 55K vs 3,224K) |
| ACL vs ACLExcl | 182 | 173 | 915 | 887 | 28 (USB 2022 7,404M vs 6,936M; UNB files ACL = 0 against ACLExcl 8.4M every period) |
The tags rarely share a period (they replace each other). Where they do, they agree about 94-98% of the time, and every disagreement found is a subset or perimeter case, not rounding.

## 4. Siblings and confusables
- FRAfter vs FRBefore (before allowance = gross loans) vs LLNet (pre-CECL net loans, includes deferred fees) vs `LoansAndLeasesReceivableNetOfDeferredIncome` (gross of allowance, net of deferred income) vs NotesReceivableNet (general financing receivable; used by banks mostly 2019-2023 and by non-bank lenders).
- ACLExcl (excludes accrued interest) vs ACL (generic; also used on roll-forward and segment rows) vs ALLL (incurred-loss era). The allowance for unfunded commitments is a liability on other tags and is not in any of these.
- Loans held for sale (`LoansReceivableHeldForSaleAmount` and similar) are never net loans held for investment (PEBK quirk in company-quirks.md).

## 5. Known misuses and quirks
- OSBC: undimensioned FRAfter = collateral-dependent loans total (note), not net loans (FILING-CHECKED above).
- BANC 2022 (28,408M vs 7,029M), LKFN 2020, PNFP 2024, UNB (ACL = 0): same "one tag is a subset" signature; not opened (DATA-INFERRED leads).
- FCCO and others still used pre-CECL tags after CECL (data-team/32).

## 6. Mapping verdict
- Bank net loans (`sr.fin.loans_net`): **safe only as a period-scoped set with a face check**: FRAfter for CECL-era periods, LLNet for earlier periods (and for late adopters such as OSBC), NotesReceivableNet as a third alternate. Each value must be the face "net loans" line: presence on the balance-sheet presentation, or (proposal, threshold ASSUMED, Standardization Lead to set) a plausibility guard such as "net loans is a large share of total assets for a bank" that would have rejected OSBC's 50.5M against 3,820M. Never pick by tag priority alone (OSBC). The draft lead (LLNet alone) is wrong for current periods; the Sector Analyst's lead (FRAfter alone) is wrong for 2015-2022. FILING-CHECKED (EFSC, OSBC); counts DATA-INFERRED.
- Bank allowance (`sr.fin.allowance`): **period-scoped set** ACLExcl (CECL era) -> ACL -> ALLL (pre-CECL), each the face contra line; reject a zero when another allowance tag is non-zero (UNB). The draft name `AllowanceForLoanAndLeaseLosses...` is not a taxonomy element; the pre-CECL element is `LoansAndLeasesReceivableAllowance`. FILING-CHECKED (EFSC, OSBC); counts DATA-INFERRED.
- Keep `LoansReceivableNet` in the set for 2015-2020 periods only (removed element; 143 companies until 2020-03-31, DATA-INFERRED). CORRECTED before publishing: my first draft said to remove it because it is absent from the 2025/2026 schemas; the tag library shows it is historical. Never use an `AllowanceForLoanAndLeaseLosses*` roll-forward component as the allowance balance.
- Verified by: Tag Expert (me), 2026-10-22. Not an approval; route to the Tag Mapper (coexistence already run above) and the Standardization Lead (era rule and the face guard).
