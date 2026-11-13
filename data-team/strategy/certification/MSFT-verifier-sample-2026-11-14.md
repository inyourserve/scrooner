# MSFT certification re-sample, Verifier, 2026-11-14 (run 2026-11-13)

Company: MSFT (company_id 4, CIK 0000789019). Population: 552 FY template cells FY2015-FY2026, 516 PROVEN and 36 REASON (all 36 `line_presented_combined`). Cell list rebuilt read-only from a clean worktree of origin/main 0ee2790f (contains d16a6910, DETECTOR_VERSION v6) with `scrooner_pipeline.mapper.top100_coverage.main` on a one-row shards file (MSFT only), one connection, statement_timeout 10min set by the module. Output reported "552 cells {PROVEN 516, REASON 36}". Per-cell results: `MSFT-verifier-sample-2026-11-14.csv`.

## Sampling (seed 20261114, 32 cells)

Code: `MSFT-verifier-sample-2026-11-14-sampler.py` (`python3 sampler.py top100-coverage.csv`).
- Risk stratum, forced (not random): revenue, operating_expenses and gross_profit FY2016-FY2017 (6 PROVEN).
- Random PROVEN (20): rows sorted, shuffled with `random.Random(20261114)`; greedy take of IS 6 / BS 7 / CF 7, at most 2 per fiscal year (forced cells count), at most 1 per data point.
- Random REASON (6): same generator; 2 per reason data point (D&A, interest_income, other_income_expense_net), distinct years.
- Result: 26 PROVEN + 6 REASON, all 12 fiscal years.

## Method

For each PROVEN cell I opened the sec.gov R page of the latest 10-K that prints the column (BS +1 year, IS/CF +2 years), and usually the cell's own-year 10-K as well. Where a note figure was involved I also read the XBRL instance. Pages fetched with the declared User-Agent, 0.3 s apart. Pages fetched on 2026-11-13 by the previous sample were reused from the local cache (same sec.gov bytes). Served values come from `analytics.canonical_fact` through the coverage module.

## Result

| | Sampled | Wrong | CP 95% upper bound, two-sided / one-sided |
|---|---|---|---|
| All 32 | 32 | 1 | 16.2% / 14.0% |
| Random part only (20 PROVEN + 6 REASON) | 26 | 1 | 19.6% / 17.0% |
| PROVEN (26) | 26 | 1 | 19.6% / 17.0% |
| REASON (6) | 6 | 0 | 45.9% / 39.3% |

The 6 risk-stratum cells were chosen on purpose, not drawn. A population bound strictly applies only to the random 26.

**The error: #12, total_debt FY2025.** Served 43,151, which is current long-term debt 2,999 plus long-term debt 40,152. The locked definition (doc 02 line 116, founder 2026-11-04 item 5) includes finance leases disclosed in the notes. The card `fsn-balance-sheet-liabilities-equity.md` line 67 includes FinanceLeaseLiability too.
- MSFT discloses finance lease liabilities of 46,172 at 2025-06-30: 3,172 in other current liabilities and 43,000 in other long-term liabilities.
- Sources: 0001193125-26-323660 R92, and the instance fact `FinanceLeaseLiability` 46,172,000,000 (also 0000950170-25-100235 R90).
- Correct value: 89,323. FILING-CHECKED. The MSFT docmap (`MSFT-docmap-2026-11-12.md` line 60) marks the 2-tag sum FILING-CHECKED, and cell_proof checks the same tags. Neither can catch a perimeter gap.

The other 31 cells match, with sign and scale right. That includes the three restated ASC 606 columns (FY2016-17 revenue, GP and opex).

### The whole total_debt data point is wrong (FILING-CHECKED, out of sample)

Every year leaves out a debt component the filings print:

| FY | Served | Printed debt components left out | Locator |
|---|---|---|---|
| 2015 | 30,307 | Short-term debt (commercial paper) 4,985 | 0001193125-16-662209 R5 |
| 2016 | 40,557 | Short-term debt 12,904 | 0001564590-17-014900 R5 |
| 2017 | 77,122 | Short-term debt 9,072; finance leases 2,538 | 0001564590-18-019062 R4 + R103 |
| 2018 | 76,240 | Finance leases 4,301 | 0001564590-19-027952 R101 (also -18-019062 R103) |
| 2019 | 72,178 | Finance leases 6,574 | 0001564590-20-034944 R95 |
| 2020 | 63,327 | Finance leases 9,496 | 0001564590-21-039151 R93 |
| 2021 | 58,146 | Finance leases 12,541 | 0001564590-22-026876 R94 |
| 2022 | 49,781 | Finance leases 14,902 | 0000950170-23-035122 R94 |
| 2023 | 47,237 | Finance leases 17,067 | 0000950170-24-087843 R100 |
| 2024 | 44,937 | Finance leases 27,145 | 0000950170-25-100235 R90 |
| 2025 | 43,151 | Finance leases 46,172 | 0001193125-26-323660 R92 |
| 2026 | 40,294 | Finance leases 66,594 | 0001193125-26-323660 R92 |

- Short-term debt is a face line on the balance sheet. Leaving it out is wrong under any definition.
- For FY2015-16, I did not check whether capital leases were disclosed (pre-ASC 842).
- Route to the debt lane: the composition must include ShortTermBorrowings/CommercialPaper (the face "Short-term debt") and FinanceLeaseLiability(+Current/Noncurrent). Replay MSFT total_debt, then every top-100 company whose total_debt is a LongTermDebtCurrent+Noncurrent sum, and re-prove.
- The coverage rows for FY2025/26 still carry a stale "read: held_debt_lane" reason beside a PROVEN value.

## Previous-error re-checks

| Cell (2026-11-13 finding) | Now served | Latest eligible filing | Verdict |
|---|---|---|---|
| revenue FY2016 | 91,154 | 91,154, 0001564590-18-019062 R2 | FIXED |
| revenue FY2017 | 96,571 | 96,571, 0001564590-19-027952 R2 (and -18-019062 R2) | FIXED |
| operating_expenses FY2016 | 32,296 | 11,988 + 14,635 + 4,563 + 1,110, -18-019062 R2 | FIXED |
| operating_expenses FY2017 | 33,285 | 13,037 + 15,461 + 4,481 + 306, -19-027952 R2 | FIXED |
| D&A FY2022 (reason) | REASON line_presented_combined, cites 0001564590-22-026876 R6 | R6 prints "Depreciation, amortization, and other" 14,460 on msft:DepreciationAmortizationAndOther; FY2024 10-K R6 also prints 14,460 | FIXED. Cosmetic issue: the reason text quotes an empty label (combined line '') for FY2015-FY2024 |

FY2016 and FY2017 now tie: revenue minus cost equals GP, and GP minus opex equals the printed operating income (26,078 and 29,025).

## FY2017 balance sheet, served value vs FY2017 10-K and FY2018 10-K (coordinator request)

FY2017 10-K = 0001564590-17-014900 R5. FY2018 10-K = 0001564590-18-019062 R4: the ASC 606 and ASC 842 full-retrospective recast, and the latest filing that prints 2017-06-30. All values FILING-CHECKED, $M.

| Data point | Served | FY2017 10-K | FY2018 10-K | Served from | Change if the whole column comes from the FY2018 10-K |
|---|---|---|---|---|---|
| accounts_receivable | 22,431 | 19,792 | 22,431 | FY2018 | none |
| current_assets | 162,696 | 159,851 | 162,696 | FY2018 | none |
| total_assets | 250,312 | 241,086 | 250,312 | FY2018 | none |
| current_liabilities | 55,745 | 64,527 | 55,745 | FY2018 | none |
| total_liabilities | 162,601 | 168,692 | 162,601 | FY2018 | none |
| stockholders_equity | 87,711 | 72,394 | 87,711 | FY2018 | none |
| accounts_payable | 7,390 | 7,390 | 7,390 | FY2017 (equal) | none (locator only) |
| cash_and_equivalents | 7,663 | 7,663 | 7,663 | FY2017 (equal) | none (locator only) |
| goodwill | 35,122 | 35,122 | 35,122 | FY2017 (equal) | none (locator only) |
| inventory | 2,181 | 2,181 | 2,181 | FY2017 (equal) | none (locator only) |
| ppe_net | 23,734 | 23,734 | 23,734 | FY2017 (equal) | none (locator only) |
| shares_outstanding | 7,708,000,000 | 7,708 (label) | 7,708,000,000 (R5 parenthetical) | FY2017 (equal) | none (locator only) |
| total_debt | 77,122 | 1,049 + 76,073 (+ short-term 9,072) | 1,049 + 76,073 (+ short-term 9,072; finance leases 2,538 in R103) | FY2017 (equal parts) | none from the rule. WRONG either way: 86,194 on the FY2017 10-K perimeter, 88,732 with the FY2018 10-K finance leases |

Answer: the statement-coherence rule changes no FY2017 balance-sheet values. The six restated lines already come from the FY2018 10-K, and the other seven are equal in both filings. The rule only changes accession/locator for those seven.

The served column is coherent: 162,601 + 87,711 = 250,312. Other restated lines in the FY2018 10-K column are not in the template: unearned revenue, deferred taxes, the operating-lease ROU asset and liability, and other current assets 5,103 vs 4,897.

## Defects that are not value errors (route to the coverage/evidence export owner)

1. **Locator mismatch (14 rows).** The accession is the latest filing, but the R page number comes from the cell's own-year filing layout. The rows:
   - Six FY2017 BS cells cite 0001564590-18-019062 R5, which is BALANCE SHEETS (Parenthetical); the BS is R4.
   - Seven FY2016-17 CF cells (CFO, CFI and CFF 2016/2017, cf_ar_change 2016) cite -18-019062 R7, which is the equity statement; the CF is R6.
   - cf_ar_change 2017 cites -19-027952 R7.

   I found these by matching each cited page to its FilingSummary title.
2. **Missing locators (72 rows).** No accession or R page for all 12 years of amortization_of_intangibles, cash_paid_for_income_taxes, cash_paid_for_interest, interest_expense and shares_outstanding, and for the 12 interest_income REASON cells. Sampled #15, #23, #29 and #30 are right on substance but cite nothing.
3. **Reason text on PROVEN cells.** 9 interest_expense rows carry "the predictor's candidate ... not backed by the cell proof (NOT_PRESENTED): the line is not mapped for this era". Other PROVEN rows carry old hold texts ("held by the tag-map mapper: proof_disagree"), and interest_expense FY2025/26 carries "row: combined". If any UI shows this text, it contradicts the value. DATA-INFERRED; I did not check what the UI shows.
4. **other_income_expense_net policy inconsistency.** MSFT's line is correctly a REASON, because the line holds interest income and interest expense while interest_expense is served from the note. Card `fsn-income-statement.md` (NonoperatingIncomeExpense) would fill the concept for a single-line filer like AAPL. The Standardization Lead should make one ruling for both.
5. **D&A FY2025 reclassified in the FY2026 10-K.** "Depreciation, amortization, and other" for FY2025 is 34,153 in the FY2025 10-K and 29,433 in the FY2026 10-K; FY2024 changed from 22,287 to 20,958. CF FY2024 inventories changed too (1,284 in the FY2026 10-K). The REASON is unaffected. Restated FY2024/25 CF columns are worth a targeted check: not sampled here.

## Untested

The other 520 cells, quarterly cells and the UI sign display. FY2015-16 capital leases. Interest_expense FY2025/26 against the "row: combined" read note. Restated FY2024-25 CF columns in the FY2026 10-K.
