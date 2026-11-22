# JNJ display certification, 2026-11-22 (request 2026-11-22, re-certification under token recert/JNJ-2026-11-22.md): FAIL

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Coverage sha256 0e27b457afcbfbb58fdf27b5eb6cb8d31bc07c4d6a98adb53dcc2ced45ddcf95. Run: https://github.com/inyourserve/scrooner/actions/runs/45050193567 (read-only, fsn.*).

**Approver note.** Every value checked is right:
- 199 of 199 drawn cells match; draw_check@2 settled 194.
- The 5 cf_ap_change cells left for a read are the values I checked one by one for the token.
- total_debt matches 11 of 11 years and the derived census 6 of 6.

**FAIL: all 12 cf_ap_change cells (FY2015-FY2025) carry badge `as_printed`.** The token accepted them only as `combined:Increase in accounts payable and accrued liabilities`.
- JNJ prints accounts payable only combined with accrued liabilities (us-gaap IncreaseDecreaseInAccountsPayableAndAccruedLiabilities), and the founder decision of 2026-11-22 (doc 02) requires a combined line to be shown with the `combined:<what it includes>` badge.
- Shown as `as_printed`, the screener would present JNJ's payables-plus-accruals change as a pure accounts-payable change.
- The automated checker agrees: the element is outside its cf_ap_change family.
- Fix: badge the 12 cells `combined:Increase in accounts payable and accrued liabilities` and re-request. No value changes.

**Token correction.** The token's FY2015 value (-3,000,000) came from the FY2015 10-K. The FY2016 and FY2017 10-Ks re-present FY2015 as 287,000,000, so the export's 287,000,000 (FY2017 10-K, R8) is the correct latest print.

---

# JNJ display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `data-team/strategy/certification/JNJ-coverage-2026-11-22.csv` (sha256 `0e27b457afcbfbb58fdf27b5eb6cb8d31bc07c4d6a98adb53dcc2ced45ddcf95`). Cells by display class: HIDDEN_ROW=22, SHOWN_VALUE=484. Seed `JNJ-0e27b457afcb`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 4 strata of 473 shown) | 199 match, 0 wrong, 0 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 194 auto-matched, 0 auto-mismatched, 5 need a read; 0 read, 5 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (6 undrawn) | 6 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 2 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for JNJ alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 473)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 51/121, balance_sheet|derived 5/11, cash_flow|as_printed 60/143, income_statement|as_printed 83/198

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** cf_ap_change FY2016 (family): no fact of the checker's cf_ap_change family at 2017-01-01 in 0000200406-17-000006 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** cf_ap_change FY2017 (family): no fact of the checker's cf_ap_change family at 2017-12-31 in 0000200406-18-000005 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** cf_ap_change FY2018 (family): no fact of the checker's cf_ap_change family at 2018-12-30 in 0000200406-19-000009 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** cf_ap_change FY2019 (family): no fact of the checker's cf_ap_change family at 2019-12-29 in 0000200406-20-000010 (custom, dimensioned or note-only line): read the filing -- pending read
- **NEEDS_READ** cf_ap_change FY2024 (family): no fact of the checker's cf_ap_change family at 2024-12-29 in 0000200406-25-000038 (custom, dimensioned or note-only line): read the filing -- pending read

## Hidden rows evidenced

- operating_expenses: no presented, undimensioned, annual ['CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses'] fact at a display-year end in any periodic filing
- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
