# BMY display certification (Ritwik (cloud), approver, 2026-11-22): REVIEW

Coverage `/home/runner/work/scrooner/scrooner/data-team/strategy/certification/BMY-coverage-2026-11-22.csv` (sha256 `87d0a7503087288104d0ee0eec9bde092eb40160174690a946aace767b446bb2`). Cells by display class: HIDDEN_ROW=11, SHOWN_VALUE=495. Seed `BMY-87d0a7503087`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 5 strata of 484 shown) | 189 match, 0 wrong, 10 locator only |
| Automated draw checker (draw_check@2, the filing's own facts) | 194 auto-matched, 0 auto-mismatched, 5 need a read; 0 read, 5 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (20 undrawn) | 20 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 1 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for BMY alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 484)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 50/121, balance_sheet|derived 5/11, cash_flow|as_printed 58/143, income_statement|as_printed 75/184, income_statement|derived 11/25

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** accounts_receivable FY2018 (text): text-stated value (no tagged fact): read the quote at R4.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-20-000082, read FY2018 10-K of 0000014272-20-000082 -- pending read
- **NEEDS_READ** accounts_receivable FY2019 (text): text-stated value (no tagged fact): read the quote at R4.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-20-000082, read FY2019 10-K of 0000014272-20-000082 -- pending read
- **NEEDS_READ** accounts_receivable FY2021 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + R87.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-22-000051, read FY2021 10-K of 0000014272-22-000051 -- pending read
- **NEEDS_READ** accounts_receivable FY2022 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-23-000046, read FY2022 10-K of 0000014272-23-000046 -- pending read
- **NEEDS_READ** accounts_receivable FY2025 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + R98.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-26-000004, read FY2025 10-K of 0000014272-26-000004 -- pending read

## Findings

- **LOCATOR** accounts_receivable FY2025: served 9592000000, filing None. text-stated value located by its quote (R5.htm (face) + R98.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-26-000004, read FY2025 10-K of 0000014272-26-000004), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2021: served 7979000000, filing None. text-stated value located by its quote (R5.htm (face) + R87.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-22-000051, read FY2021 10-K of 0000014272-22-000051), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2018: served 4636000000, filing None. text-stated value located by its quote (R4.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-20-000082, read FY2018 10-K of 0000014272-20-000082), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2022: served 8151000000, filing None. text-stated value located by its quote (R5.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-23-000046, read FY2022 10-K of 0000014272-23-000046), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2019: served 6476000000, filing None. text-stated value located by its quote (R4.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-20-000082, read FY2019 10-K of 0000014272-20-000082), no tag: approver reads the quote
- **LOCATOR** gross_profit FY2019: served 18067000000, filing None. text-stated value located by its quote (R3.htm (us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000014272-22-000051, read FY2019 10-K of 0000014272-22-000051), no tag: approver reads the quote
- **LOCATOR** gross_profit FY2018: served 16094000000, filing None. text-stated value located by its quote (R2.htm (us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000014272-21-000066, read FY2018 10-K of 0000014272-21-000066), no tag: approver reads the quote
- **LOCATOR** gross_profit FY2016: served 14458000000, filing None. text-stated value located by its quote (R2.htm (us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000014272-19-000047, read FY2016 10-K of 0000014272-19-000047), no tag: approver reads the quote
- **LOCATOR** gross_profit FY2020: served 30745000000, filing None. text-stated value located by its quote (R3.htm (us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000014272-23-000046, read FY2020 10-K of 0000014272-23-000046), no tag: approver reads the quote
- **LOCATOR** gross_profit FY2017: served 14762000000, filing None. text-stated value located by its quote (R2.htm (us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000014272-20-000082, read FY2017 10-K of 0000014272-20-000082), no tag: approver reads the quote

## Hidden rows evidenced

- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
