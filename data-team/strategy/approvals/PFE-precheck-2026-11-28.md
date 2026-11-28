# PFE certification precheck, 2026-11-28 (preparer: Scrooner data verifier): FAIL (census gate), draw clean

NOT a registry verdict and NOT a certificate. No certification request from top100-flow exists for this coverage; the coverage
file is this company's rows of the hourly export artifact top100-coverage-46167654745 (as_of 2026-11-28T16:55Z), so a
flow request will carry a different sha256 and a new seeded draw. Approver countersign is needed only for a FAIL record if wanted.

- Rank check: rank 75, company 1030, CIK 78003; in ranks 1-100 of doc/data-moat/team/top1000/shards.csv and not excluded.
- Hourly summary: 1 OPEN shown cell.
- Coverage: `data-team/strategy/certification/PFE-coverage-2026-11-28.csv`, sha256 `d50118dc25cff38ec573a750a102eca4afd2ad84b23879684bb903f1feba33ee`.
- Run: pipeline/scripts/certify_display.py at origin/main f0f7ffbd9, --live (read-only, one connection), --no-registry, --reads approvals/reads/PFE-d50118dc25cf.csv where present.
- Blocker: OPEN revenue FY2021 (DISAGREE shown_is_not_the_authoritative_copy) plus 4 census badge FAILs: gross_profit FY2017, FY2021, FY2022, FY2023 carry badge as_printed but their locator is a formula (Revenues - CostOfGoodsAndServicesSold). Cause (revenue): the resolver keeps RevenueFromContractWithCustomerExcludingAssessedTax, which in the FY2023 10-K 0000078003-24-000039 R3 becomes the 'Product revenues' component (73,636) under the new 'Total revenues | 58,496 | 100,330 | 81,288' (us-gaap:Revenues; FILING-CHECKED this session). Fix: resolver rule: when the element used becomes a calc child of a new printed total in the later filing, take the total line (Revenues, 81,288,000,000). Badge fix: gross_profit FY2017/2021-2023 badge derived:revenue-cost_of_revenue (values 50,467 for 2021 = 81,288 - 30,821 are right; FY2020/2024/2025 are already badged derived).
- Draw: 199 stratified shown cells, 0 wrong, Clopper-Pearson 95% upper bound 1.49% (target 1.5%). Every NEEDS_READ cell was read in the filing (FILING-CHECKED); reads file above.
- Next: land the fix above, then one top100-flow run for this company (queue empty), then display-certify on the new request.
- Untested: the 5% AUTO_MATCH audit sample (--audit-out) was not run; it belongs to the request-sha draw.

## Generated output: PFE display certification (Ritwik (cloud), approver, 2026-11-28): FAIL

Coverage `data-team/strategy/certification/PFE-coverage-2026-11-28.csv` (sha256 `d50118dc25cff38ec573a750a102eca4afd2ad84b23879684bb903f1feba33ee`). Cells by display class: HIDDEN_ROW=22, HIDDEN_YEAR=1, OPEN=1, SHOWN_VALUE=482. Seed `PFE-d50118dc25cf`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 5 failing |
| 199 random shown cells (stratified, 5 strata of 471 shown) | 197 match, 0 wrong, 2 locator only |
| Automated draw checker (draw_check@3, the filing's own facts) | 199 auto-matched, 0 auto-mismatched, 0 need a read; 0 read, 0 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (16 undrawn) | 16 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 3 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for PFE alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 471)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 51/121, balance_sheet|derived 5/11, cash_flow|as_printed 60/142, income_statement|as_printed 75/179, income_statement|derived 8/18

## Findings

- **FAIL** gate revenue 2021: OPEN cell
- **FAIL** badge gross_profit 2017: badge 'as_printed' on a computation: the locator is a formula (R2.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-20-000014, read FY2017 10-K); a value the filing does not print carries its derived: badge
- **FAIL** badge gross_profit 2021: badge 'as_printed' on a computation: the locator is a formula (R3.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-24-000039, read FY2021 10-K); a value the filing does not print carries its derived: badge
- **FAIL** badge gross_profit 2022: badge 'as_printed' on a computation: the locator is a formula (R3.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-25-000054, read FY2022 10-K); a value the filing does not print carries its derived: badge
- **FAIL** badge gross_profit 2023: badge 'as_printed' on a computation: the locator is a formula (R3.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-26-000026, read FY2023 10-K); a value the filing does not print carries its derived: badge
- **LOCATOR** gross_profit FY2017: served 41318000000, filing None. text-stated value located by its quote (R2.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-20-000014, read FY2017 10-K of 0000078003-20-000014), no tag: approver reads the quote
- **LOCATOR** gross_profit FY2022: served 66831000000, filing None. text-stated value located by its quote (R3.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-25-000054, read FY2022 10-K of 0000078003-25-000054), no tag: approver reads the quote

## Hidden rows evidenced

- operating_expenses: no presented, undimensioned, annual ['CostsAndExpenses', 'OperatingCostsAndExpenses', 'OperatingExpenses'] fact at a display-year end in any periodic filing
- operating_income: no presented, undimensioned, annual ['OperatingIncomeLoss'] fact at a display-year end in any periodic filing

## Hidden years evidenced (allowlist)

- share_buybacks FY2025: allowlisted: 1 periodic filing(s) present 2025-12-31, none prints a share_buybacks line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
