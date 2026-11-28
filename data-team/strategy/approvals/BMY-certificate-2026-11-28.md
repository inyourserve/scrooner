# BMY display certification (scrooner-data-verifier (agent), approver read; run by the Stage 5 certify session, 2026-11-28): PASS

Coverage `data-team/strategy/certification/BMY-coverage-2026-11-22.csv` (sha256 `1eafcef0c57f4c46c462ee828b1d818c135d5fc9336f74f8b278ee59d6f3acbf`). Cells by display class: HIDDEN_ROW=11, SHOWN_VALUE=495. Seed `BMY-1eafcef0c57f`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 0 failing |
| 199 random shown cells (stratified, 5 strata of 484 shown) | 196 match, 0 wrong, 3 locator only |
| Automated draw checker (draw_check@3, the filing's own facts) | 196 auto-matched, 0 auto-mismatched, 3 need a read; 3 read, 0 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (25 undrawn) | 25 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 1 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for BMY alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 484)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 50/121, balance_sheet|derived 5/11, cash_flow|as_printed 58/143, income_statement|as_printed 72/176, income_statement|derived 14/33

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** accounts_receivable FY2020 (text): text-stated value (no tagged fact): read the quote at R4.htm (face) + R81.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-21-000066, read FY2020 10-K of 0000014272-21-000066 -- read by scrooner-data-verifier (agent, approver read 2026-11-28): MATCH (0000014272-21-000066 FY2020 10-K, R81.htm RECEIVABLES (Details) $ in Millions, Dec. 31, 2020: "Net trade receivables" 7,219 (us-gaap:AccountsReceivableNetCurrent) = trade receivables 7,882 - charge-backs/cash discounts 645 - allowances 18; plus "Alliance, Royalties, VAT and other" 1,282 = "Receivables" 8,501, which ties to face R4.htm CONSOLIDATED BALANCE SHEETS "Receivables" 8,501. Shown 7,219,000,000 = 7,219 x 1e6.)
- **NEEDS_READ** accounts_receivable FY2022 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-23-000046, read FY2022 10-K of 0000014272-23-000046 -- read by scrooner-data-verifier (agent, approver read 2026-11-28): MATCH (0000014272-23-000046 FY2022 10-K, R90.htm RECEIVABLES - Schedule of Accounts... (Details) $ in Millions, Dec. 31, 2022: "Net trade receivables" 8,151 (us-gaap:AccountsReceivableNetCurrent) = 8,848 - 675 - 22; plus "Alliance, royalties, VAT and other" 1,735 = "Receivables" 9,886, which ties to face R5.htm "Receivables" 9,886. Shown 8,151,000,000 = 8,151 x 1e6.)
- **NEEDS_READ** accounts_receivable FY2025 (text): text-stated value (no tagged fact): read the quote at R5.htm (face) + R98.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-26-000004, read FY2025 10-K of 0000014272-26-000004 -- read by scrooner-data-verifier (agent, approver read 2026-11-28): MATCH (0000014272-26-000004 FY2025 10-K, R98.htm RECEIVABLES - Schedule of Accounts... (Details) $ in Millions, Dec. 31, 2025: "Net trade receivables" 9,592 (us-gaap:AccountsReceivableNetCurrent) = 11,370 - 1,720 - 58; plus "Alliance, royalties, VAT and other" 1,821 = "Receivables" 11,414, which ties to face R5.htm "Receivables" 11,414. Shown 9,592,000,000 = 9,592 x 1e6.)

## Findings

- **LOCATOR** accounts_receivable FY2025: served 9592000000, filing None. text-stated value located by its quote (R5.htm (face) + R98.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-26-000004, read FY2025 10-K of 0000014272-26-000004), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2022: served 8151000000, filing None. text-stated value located by its quote (R5.htm (face) + Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: trade receivables, net)) of 0000014272-23-000046, read FY2022 10-K of 0000014272-23-000046), no tag: approver reads the quote
- **LOCATOR** accounts_receivable FY2020: served 7219000000, filing None. text-stated value located by its quote (R4.htm (face) + R81.htm Receivables note (us-gaap:AccountsReceivableNetCurrent (Receivables note: net trade receivables)) of 0000014272-21-000066, read FY2020 10-K of 0000014272-21-000066), no tag: approver reads the quote

## Hidden rows evidenced

- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.

## Approver notes (2026-11-28)

- Preparer: the top100-flow workflow (request d030f3d65). Approver reads: scrooner-data-verifier agent, every cell opened on sec.gov (reads/BMY-1eafcef0c57f.csv: 3 NEEDS_READ accounts_receivable cells, all MATCH; reads/BMY-1eafcef0c57f-audit.csv: 10 of 196 AUTO_MATCH cells, 10/10 agree).
- The 3 "locator only" rows are the same text-stated accounts_receivable cells; a matching read settles them (display_cert Run.settled_by_read, this commit). The coverage file is identical to BMY's rows in the 2026-11-28 17:02Z hourly export (506/506 rows, 0 differences).
