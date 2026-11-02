# FSN expert: engineering proposals (running list)

Advice only. Engineering builds, the approver signs. Each proposal names the companies and accessions that prove it. Status: OPEN until engineering answers.

## P-1. Add the two missing FX tags to the cash-change identity (OPEN, high)
- **Where:** `pipeline/src/scrooner_pipeline/fsn_store/checks.py` `CF_FX` (origin/main b785ec5).
- **Problem:** it holds only `EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` and `EffectOfExchangeRateOnCashAndCashEquivalents`.
- **Add:**
  - `…RestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations`;
  - `…RestrictedCashEquivalentsDisposalGroupIncludingDiscontinuedOperations`.
- **Proof:**
  - MSFT FY2026 10-K 0001193125-26-323660, FY2025 column: CFO 136,162 + CFI + CFF = 11,864; FX 63; net change 11,927. It ties only with the FX line, which uses the first missing tag.
  - Pilot run 41490670432 blanks MSFT cfo / dividends_paid / share_buybacks FY2020–FY2026 (22 cells each, `latest_copy_fails_identity`).
- **Scope:** 19 top-100 EDGAR names print the first tag on the CF face 2018–2026: ABT, AMZN, DELL, GE, GEV, GS, MSFT, NEM, ORCL, PM, PLD, QCOM, RTX, TSLA, TMO, DIS. CSCO and RTX print the second (DI, FSN pre).
- **Test:** the AMZN fixture `tests/fixtures/fsn_company_bs/0001018724` already contains a 2024 filing with the first tag (pre.tsv line 251). A test on that column must fail before the fix.

## P-2. A revenue (or COR) candidate that is a calc child of another candidate is a component (OPEN, high)
- **Problem:** the std_tag rule accepts `SalesRevenueGoodsNet` / `CostOfGoodsSold` as totals beside `SalesRevenueNet` / `CostOfRevenue`.
- **Proof:** MSFT FY2016 10-K 0001193125-16-662209 … Q3 FY2018 0001564590-18-009307: "Product" `SalesRevenueGoodsNet` + custom "Service and other" = "Total revenue" `SalesRevenueNet` (cal weight +1 each). The pilot raises `conflicting_values_in_filing` on 10 revenue and 10 COR cells (FY2014–FY2017), e.g. 72,948 vs 86,833.
- **Rule:** per filing × statement, if candidate A is a calc descendant of candidate B, drop A. Generalises to any concept with a goods/services split (39 top-100 names print `SalesRevenueGoodsNet`, mostly labelled "Product").

## P-3. Custom calc-position mapping must not fill a slot with two lines; mark "… and other" lines `combined` (OPEN, high)
- **Problem:** both MSFT custom CF adjustments land in the D&A slot: `DepreciationAmortizationAndOther` and `GainLossOnInvestmentsAndDerivativeInstruments`. The pilot gives 50 D&A cells `conflicting_values_in_filing`, e.g. FY2025 (29,433, −5,329).
- **Rule:**
  - (a) a custom line maps by calc position only when exactly one custom line occupies that position and its label contains the concept's core words;
  - (b) a label with "and other" / "and others" sets status `combined` (blank `line_presented_combined_with_others`).
- **Proof:** "Depreciation, amortization, and other" in all 54 MSFT filings. Its composition changed in FY2026 (FY2025 34,153 → 29,433; 10-Q 0001193125-26-027207 R6, FILING-CHECKED), so even a "D&A including other" concept would be wrong across that break.

## P-4. Missing concept rules: capex, cash and equivalents, total debt (OPEN, high)
The pilot leaves every MSFT cell unmapped where production already holds the right values (capex, cash) or the face clearly prints the lines (debt).

| Concept | Tags | Pilot | Prod |
|---|---|---|---|
| capex | `PaymentsToAcquirePropertyPlantAndEquipment` | `no_mapped_line`, 59 | values agree with FSN |
| cash_and_equivalents | `CashAndCashEquivalentsAtCarryingValue` | `no_concept_rule`, 47 | agree |
| total_debt | `ShortTermBorrowings` \| `CommercialPaper`, plus `LongTermDebtCurrent`, `LongTermDebtNoncurrent` | `no_mapped_line`, 47 | **wrong for FY2016 (12,904 vs 53,461) and FY2024 (44,937 vs 51,630)** |

- Seed the rules from the Verifier-passed lane code (FSN-STORE-DESIGN §3, "do not retype rules").
- The debt rule must include `CommercialPaper` when it is a face line (cards/CommercialPaper.md).

## P-5. Interest expense: the reason class and the 2024 tag (OPEN, medium)
- **Proof:** MSFT never prints interest expense on the face; it sits inside "Other income (expense), net". The pilot says `no_mapped_line` for 59 cells.
- **(a) Reason:** use `line_not_presented` (evidence: the R2 line list), not a gap.
- **(b) Note values, if the concept allows them:**
  - `InterestExpense` to FY2024, then `InterestExpenseNonoperating` from Q1 FY2025 0000950170-24-118967.
  - Production stops at 2024-06-30 for this reason. Task-board B6, confirmed at MSFT.
  - 42 top-100 names print `InterestExpenseNonoperating` on the IS face 2024+.

## P-6. Instants printed only on the equity statement, after a retrospective restatement (OPEN, decision)
- **Proof:** MSFT equity at 2016-06-30:
  - every BS that printed it says 71,997 (FY2016 10-K … FY2017 10-K);
  - the FY2018 10-K equity statement prints the ASC 606-restated **83,090**.
- The pilot serves 71,997, while its FY2016 NI is the restated 20,539, so ROE mixes bases.
- **Decision needed (Standardization Lead):** does an EQ-statement balance count as a print of the BS instant for "latest vintage"? Recommendation: yes, but only for the equity total and only when the same filing restates the IS for that year. Otherwise keep the BS print and flag `mixed_vintage_inputs` on ratio cells.

## P-7. Use printed Q4 from the 10-K quarterly note (route a) before deriving, including per-share (OPEN, medium)
- **Proof:** MSFT 10-Ks FY2011–FY2020 print qtrs=1 values at the FY-end date: NI, revenue, GP and diluted EPS. FY2019 Q4 diluted EPS 1.71 (0001564590-19-027952).
- The pilot derives Q4 NI by YTD (equal values) and marks Q4 EPS FY2014–FY2020 `not_filed_separately` (7 cells each, basic and diluted).
- **Rule:** a qtrs=1 print in the 10-K at the FY end is a printed value (note-sourced stratum), and it wins over derivation. EPS from it is allowed: it is printed, not derived.
- Reg S-K Item 302(a) quarterly data stopped being required in 2021. MSFT drops it from the FY2021 10-K (0001564590-21-039151), so route (a) is mostly a pre-2021 source.

## P-8. Read predecessor CIKs and successor holding companies (OPEN, info)
- **Proof:** XOM's cohort CIK 2115436 (ExxonMobil Holdings Corp) has only 8-Ks in FSN (first 0002115436-26-000003, set 2026_07). All 10-K/10-Qs are under CIK 34088 through 0000034088-26-000093.
- The pilot already reads 34088. Make this a cohort-wide check: any cohort CIK with zero periodic filings in FSN must have a predecessor mapping, or be blanked with a reason.

## P-9. FSN spec deviations to encode as tests (OPEN, low)
From FSN-GUIDE §10, each verified on real rows:
- `dim.tsv` key column is `dimhash` and the no-dimension key is `0x00000000`;
- iprx starts at 0;
- datp is in days, sign = ddate − actual;
- dcml −32768 marks a nil value;
- cal `negative` is ±1;
- pre.stmt can be `SI` or a mislabelled `UN` (ABT, PLD, MPC);
- ren menucat S can be missing (MSFT 0001193125-13-409855).

A loader test per item stops a regression when someone "fixes" code to the spec.
