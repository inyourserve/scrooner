# BMY display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/BMY-coverage-2026-11-22.csv` (sha256 `2a1319707e957eaf6f25cb2726c46282b18267f2d2b70fafe32c0286ad369528`). Cells by display class: HIDDEN_ROW=11, SHOWN_VALUE=495. Seed `BMY-2a1319707e95`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 5 strata of 484 shown) | 194 match, 0 wrong, 4 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 194 auto-matched, 0 auto-mismatched, 5 need a read; 0 read, 5 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (25 undrawn) | 24 match, 0 wrong, 1 for review |
| Hidden rows and years | 0 failing, 0 for review, 1 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for BMY alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 484)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 50/121, balance_sheet|derived 5/11, cash_flow|as_printed 58/143, income_statement|as_printed 72/176, income_statement|derived 14/33

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** accounts_receivable FY2019 (text): text-stated value (no tagged fact): read the quote at R4.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-20-000082, read FY2019 10-K of 0000014272-20-000082 -- pending read
- **NEEDS_READ** accounts_receivable FY2021 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + R87.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-22-000051, read FY2021 10-K of 0000014272-22-000051 -- pending read
- **NEEDS_READ** accounts_receivable FY2023 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + R92.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-24-000044, read FY2023 10-K of 0000014272-24-000044 -- pending read
- **NEEDS_READ** accounts_receivable FY2025 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + R98.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-26-000004, read FY2025 10-K of 0000014272-26-000004 -- pending read
- **NEEDS_READ** operating_expenses FY2017 (identity): derived derived:sum(printed operating lines) with no parts: the formula is not an identity the facts rebuild -- pending read

## Findings

- **LOCATOR** accounts_receivable FY2025: served 9592000000, filing None. text-stated value located by its quote (R5.htm (face) + R98.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-26-000004, read FY2025 10-K of 0000014272-26-000004), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2023: served 8882000000, filing None. text-stated value located by its quote (R5.htm (face) + R92.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-24-000044, read FY2023 10-K of 0000014272-24-000044), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2021: served 7979000000, filing None. text-stated value located by its quote (R5.htm (face) + R87.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-22-000051, read FY2021 10-K of 0000014272-22-000051), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2019: served 6476000000, filing None. text-stated value located by its quote (R4.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-20-000082, read FY2019 10-K of 0000014272-20-000082), no tag: approver reads the quote
- **NOT_FOUND** operating_expenses FY2017: served 11316000000, filing None. derived cell with no tag, parts or known identity: approver checks by hand
- **NOT_FOUND** operating_expenses FY2018: served 10980000000, filing None. derived cell with no tag, parts or known identity: approver checks by hand

## Hidden rows evidenced

- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
