# Cohort certification request: top100-9f9397e4059e, 2026-11-29

Stage 5 Certify, M3. Founder 2026-11-28 ("everything is approve"): one cohort-sampled certificate over the launch set replaces per-company certification. The preparer filed this request read-only; only the approver records the verdict, the registry row and the certificate (PIPELINE.md section 3). Nothing below is a verdict.

- cohort id: `top100-9f9397e4059e`
- companies: `96`
- coverage csv: `GitHub Actions run 46167654745 (top100-coverage-hourly, 2026-11-28T16:54Z), artifact top100-coverage-46167654745/top100-coverage.csv`
- sha256: `5899d7d9625ed9a153dfed8f7d18da25b88169bec0809ff980784fc85a91e7a6`
- judge: `cohort_cert@1+draw_check@3`
- key: `top100-9f9397e4059e|5899d7d9625ed9a153dfed8f7d18da25b88169bec0809ff980784fc85a91e7a6|cohort_cert@1+draw_check@3`
- seed: `top100-9f9397e4059e-5899d7d9625e`
- draw size rule: `n = ceil(ln(0.05) / ln(1 - 0.005)) = 598`
- n drawn: `598`
- code: `fa396611d422d3da80ef1e7f4a4e790961db80af`
- preparer: `cohort-cert preparer (agent)`
- drawn cells: `data-team/strategy/certification/cohort/top100-cohort-draw-2026-11-29.csv`
- read queue: `data-team/strategy/certification/cohort/top100-cohort-reads-2026-11-29.csv`
- exceptions: `data-team/strategy/certification/cohort/top100-cohort-exceptions-2026-11-29.csv`
- machine status: `FAIL`

## Draw

Pool: 42191 shown cells (total_debt excluded: census) over 96 companies, 30 strata (statement family x sector x rank band). Drawn 598 of target 598; every non-empty stratum gets one cell first, the rest proportional.

| stratum | pool | drawn | errors | needs read | upper 95% |
|---|---:|---:|---:|---:|---:|
| balance_sheet|bank|r0001-0050 | 219 | 4 | 0 | 0 | 52.7129% |
| balance_sheet|bank|r0051-0100 | 92 | 2 | 0 | 1 | 77.6393% |
| balance_sheet|broker_am|r0001-0050 | 144 | 3 | 0 | 0 | 63.1597% |
| balance_sheet|broker_am|r0051-0100 | 153 | 3 | 0 | 0 | 63.1597% |
| balance_sheet|equity_reit|r0051-0100 | 87 | 2 | 0 | 0 | 77.6393% |
| balance_sheet|general|r0001-0050 | 5123 | 70 | 0 | 0 | 4.1893% |
| balance_sheet|general|r0051-0100 | 5078 | 69 | 0 | 0 | 4.2487% |
| balance_sheet|insurer|r0051-0100 | 173 | 3 | 0 | 0 | 63.1597% |
| balance_sheet|lender|r0051-0100 | 101 | 2 | 0 | 1 | 77.6393% |
| balance_sheet|utility|r0051-0100 | 131 | 3 | 0 | 0 | 63.1597% |
| cash_flow|bank|r0001-0050 | 292 | 5 | 0 | 0 | 45.0720% |
| cash_flow|bank|r0051-0100 | 99 | 2 | 0 | 0 | 77.6393% |
| cash_flow|broker_am|r0001-0050 | 229 | 4 | 0 | 1 | 52.7129% |
| cash_flow|broker_am|r0051-0100 | 217 | 4 | 0 | 0 | 52.7129% |
| cash_flow|equity_reit|r0051-0100 | 104 | 2 | 0 | 0 | 77.6393% |
| cash_flow|general|r0001-0050 | 5500 | 75 | 0 | 0 | 3.9156% |
| cash_flow|general|r0051-0100 | 5544 | 76 | 0 | 3 | 3.8651% |
| cash_flow|insurer|r0051-0100 | 203 | 4 | 0 | 0 | 52.7129% |
| cash_flow|lender|r0051-0100 | 118 | 3 | 0 | 0 | 63.1597% |
| cash_flow|utility|r0051-0100 | 120 | 3 | 0 | 2 | 63.1597% |
| income_statement|bank|r0001-0050 | 484 | 8 | 0 | 0 | 31.2344% |
| income_statement|bank|r0051-0100 | 208 | 4 | 0 | 0 | 52.7129% |
| income_statement|broker_am|r0001-0050 | 329 | 5 | 0 | 0 | 45.0720% |
| income_statement|broker_am|r0051-0100 | 308 | 5 | 0 | 0 | 45.0720% |
| income_statement|equity_reit|r0051-0100 | 180 | 3 | 0 | 0 | 63.1597% |
| income_statement|general|r0001-0050 | 8149 | 111 | 0 | 4 | 2.6628% |
| income_statement|general|r0051-0100 | 8139 | 111 | 0 | 7 | 2.6628% |
| income_statement|insurer|r0051-0100 | 300 | 5 | 0 | 1 | 45.0720% |
| income_statement|lender|r0051-0100 | 209 | 4 | 0 | 0 | 52.7129% |
| income_statement|utility|r0051-0100 | 158 | 3 | 0 | 0 | 63.1597% |

## Machine check

- draw checker: AUTO_MATCH 582, AUTO_MISMATCH 1, NEEDS_READ 15
- cell outcome: PASS 578, FAIL 0, NEEDS_READ 20
- pooled: 0/598 wrong; exact Clopper-Pearson 95% upper bound 0.4997% (target 0.50%). With 20 cells unread this bound holds only if every queued read is a MATCH; each queued read that is a MISMATCH adds one error.

## Read queue (by class)

- needs_read:text: 6
- needs_read:family: 5
- claim_locator: 3
- needs_read:label: 3
- auto_mismatch:family: 1
- claim_not_found: 1
- needs_read:identity: 1

## Census (every company of the cohort; counts by family)

- FAIL census:gate:OPEN cell: 1513
- FAIL census:gate:shown cell has no accession or R page: 335
- REVIEW census:debt:review: 136
- FAIL census:gate:part <tag> has no accession or R page: 90
- FAIL census:hidden_year:periodic filing ### presents ### (own or comparative column): not a pre-filing y: 41
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm (derived: u: 32
- REVIEW census:hidden_row:no tag family on file for this data point: approver checks the filings by hand: 30
- FAIL census:hidden_year:### presents ### and prints the line (<tag>); a printed value or dash must be sh: 28
- FAIL census:hide_reason:verified_absent, but inventory is not on the VERIFIED_ABSENT_HIDE allowlist and : 22
- REVIEW census:derived:shares_outstanding:not_found: 21
- FAIL census:hidden_year:### presents ### and prints the line (Revenues); a printed value or dash must be: 10
- FAIL census:hidden_year:not-disclosed search evidence does not cover every presenting filing: CIK #: 10
- REVIEW census:derived:depreciation_and_amortization:locator: 10
- REVIEW census:derived:dividends_paid:locator: 10
- FAIL census:hidden_year:not-disclosed search evidence does not cover every presenting filing: #-Q (an in: 8
- FAIL census:debt:mismatch: 7
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm (derived C#: 6
- FAIL census:hidden_year:### presents ### and prints the line (<tag>, <tag>); a printed value or dash mus: 6
- REVIEW census:derived:interest_income:locator: 6
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm (sum of ope: 4
- REVIEW census:derived:gross_profit:not_found: 4
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm; MD&A (head: 3
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm + Other inc: 2
- FAIL census:derived:other_income_expense_net:mismatch: 2
- FAIL census:derived:total_liabilities:mismatch: 2
- FAIL census:hidden_year:### presents ### and prints the line (<tag>, Revenues); a printed value or dash : 2
- FAIL census:hidden_year:### presents ### and prints the line (Depreciation); a printed value or dash mus: 2
- FAIL census:hidden_year:not-disclosed search evidence does not cover every presenting filing: CIK # #-Q : 2
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm (component : 1
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm+R#htm+notes: 1
- FAIL census:badge:badge 'as_printed' on a computation: the locator is a formula (R#htm; R#htm; R#h: 1
- REVIEW census:derived:capex:not_found: 1
- REVIEW census:derived:other_income_expense_net:not_found: 1
- REVIEW census:derived:sga_expense:not_found: 1
- REVIEW census:derived:stockholders_equity:not_found: 1
