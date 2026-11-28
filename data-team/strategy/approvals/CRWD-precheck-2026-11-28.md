# CRWD certification precheck, 2026-11-28 (preparer: Scrooner data verifier): FAIL (census gate), draw clean

NOT a registry verdict and NOT a certificate. No certification request from top100-flow exists for this coverage; the coverage
file is this company's rows of the hourly export artifact top100-coverage-46167654745 (as_of 2026-11-28T16:55Z), so a
flow request will carry a different sha256 and a new seeded draw. Approver countersign is needed only for a FAIL record if wanted.

- Rank check: rank 51, company 2726, CIK 1535527; in ranks 1-100 of doc/data-moat/team/top1000/shards.csv and not excluded.
- Hourly summary: 1 OPEN shown cell.
- Coverage: `data-team/strategy/certification/CRWD-coverage-2026-11-28.csv`, sha256 `4f3ea5752152f3d30b5e244f1578a1a8bedf33874352dba51f4302c4ad72f2a8`.
- Run: pipeline/scripts/certify_display.py at origin/main f0f7ffbd9, --live (read-only, one connection), --no-registry, --reads approvals/reads/CRWD-4f3ea5752152.csv where present.
- Blocker: OPEN interest_income FY2020 (BLANK not_presented_but_row_shown), plus census FAILs on hidden years interest_income FY2018 and FY2019 (hidden as pre-filing although the FY2020 10-K presents them). Cause: CRWD prints only a residual 'Other income (expense), net' line before FY2021 (first annual interest-income line: FY2023 10-K 0001535527-23-000008 R5); no approved reason class covers 'not separately stated' for a row that is shown in later years. Fix: approve and implement the year-level reason interest_income_not_separately_stated (proposal in open-shown-fixes/CRWD-2026-11-24.csv, confidence medium) for FY2018-FY2020 with the quoted evidence, replacing the before_first_10k hide; this is a rule decision, then a flow run.
- Draw: 199 stratified shown cells, 0 wrong, Clopper-Pearson 95% upper bound 1.49% (target 1.5%). Every NEEDS_READ cell was read in the filing (FILING-CHECKED); reads file above.
- Next: land the fix above, then one top100-flow run for this company (queue empty), then display-certify on the new request.
- Untested: the 5% AUTO_MATCH audit sample (--audit-out) was not run; it belongs to the request-sha draw.

## Generated output: CRWD display certification (Ritwik (cloud), approver, 2026-11-28): FAIL

Coverage `data-team/strategy/certification/CRWD-coverage-2026-11-28.csv` (sha256 `4f3ea5752152f3d30b5e244f1578a1a8bedf33874352dba51f4302c4ad72f2a8`). Cells by display class: HIDDEN_ROW=26, HIDDEN_YEAR=21, OPEN=1, SHOWN_VALUE=366. Seed `CRWD-4f3ea5752152`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 1 failing |
| 199 random shown cells (stratified, 6 strata of 359 shown) | 196 match, 0 wrong, 3 locator only |
| Automated draw checker (draw_check@3, the filing's own facts) | 196 auto-matched, 0 auto-mismatched, 3 need a read; 3 read, 0 pending |
| total_debt census (7 years) | 7 match, 0 wrong, 0 for review |
| Derived cells census (13 undrawn) | 13 match, 0 wrong, 0 for review |
| Hidden rows and years | 2 failing, 0 for review, 9 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for CRWD alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 359)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 45/82, balance_sheet|derived 4/6, cash_flow|as_printed 42/76, cash_flow|derived 10/18, income_statement|as_printed 92/168, income_statement|derived 6/9

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** dividends_per_share FY2018 (text): text-stated value (no tagged fact): read the quote at Rcrwd-20200131.htm Item 5 (stated_zero (text: never declared or paid)) of 0001535527-20-000006, read FY2018 10-K of 0001535527-20-000006 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2020 10-K 0001535527-20-000006 crwd-20200131.htm Item 5 Dividend Policy: "We have never declared or paid any cash dividends on our capital stock." No dividends-paid line anywhere in the document. Served 0.)
- **NEEDS_READ** dividends_per_share FY2023 (text): text-stated value (no tagged fact): read the quote at Rcrwd-20230131.htm Item 5. Market for Registrant’s Common Equity, Dividend Policy of 0001535527-23-000008 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2023 10-K 0001535527-23-000008 crwd-20230131.htm Item 5 Dividend Policy: "We have never declared or paid any cash dividends on our capital stock." Served 0.)
- **NEEDS_READ** dividends_per_share FY2024 (text): text-stated value (no tagged fact): read the quote at Rcrwd-20240131.htm Item 5. Market for Registrant’s Common Equity, Dividend Policy of 0001535527-24-000007 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2024 10-K 0001535527-24-000007 crwd-20240131.htm Item 5 Dividend Policy: "We have never declared or paid any cash dividends on our capital stock." Served 0.)

## Findings

- **FAIL** gate interest_income 2020: OPEN cell
- **FAIL** hidden_year interest_income 2018: periodic filing 0001535527-20-000006 presents 2018-01-31 (own or comparative column): not a pre-filing year, and interest_income is neither on the hide allowlist nor hidden as reported only combined nor a verified absence evidenced by a full-text search
- **FAIL** hidden_year interest_income 2019: periodic filing 0001535527-20-000006 presents 2019-01-31 (own or comparative column): not a pre-filing year, and interest_income is neither on the hide allowlist nor hidden as reported only combined nor a verified absence evidenced by a full-text search
- **LOCATOR** dividends_per_share FY2018: served 0, filing None. text-stated value located by its quote (Rcrwd-20200131.htm Item 5 (stated_zero (text: never declared or paid)) of 0001535527-20-000006, read FY2018 10-K of 0001535527-20-000006), no tag: approver reads the quote
- **LOCATOR** dividends_per_share FY2023: served 0, filing None. text-stated value located by its quote (Rcrwd-20230131.htm Item 5. Market for Registrant’s Common Equity, Dividend Policy of 0001535527-23-000008), no tag: approver reads the quote
- **LOCATOR** dividends_per_share FY2024: served 0, filing None. text-stated value located by its quote (Rcrwd-20240131.htm Item 5. Market for Registrant’s Common Equity, Dividend Policy of 0001535527-24-000007), no tag: approver reads the quote

## Hidden rows evidenced

- cf_inventory_change: no presented, undimensioned, annual ['IncreaseDecreaseInInventories'] fact at a display-year end in any periodic filing
- dividends_paid: no presented, undimensioned, annual ['PaymentsOfDividends', 'PaymentsOfDividendsCommonStock'] fact at a display-year end in any periodic filing
- inventory: no presented, undimensioned, annual ['InventoryNet'] fact at a display-year end in any periodic filing

## Hidden years evidenced (allowlist)

- share_buybacks FY2022: allowlisted: 3 periodic filing(s) present 2022-01-31, none prints a share_buybacks line
- share_buybacks FY2023: allowlisted: 3 periodic filing(s) present 2023-01-31, none prints a share_buybacks line
- share_buybacks FY2024: allowlisted: 3 periodic filing(s) present 2024-01-31, none prints a share_buybacks line
- share_buybacks FY2025: allowlisted: 2 periodic filing(s) present 2025-01-31, none prints a share_buybacks line
- share_buybacks FY2026: allowlisted: 1 periodic filing(s) present 2026-01-31, none prints a share_buybacks line
- total_debt FY2019: allowlisted: 4 periodic filing(s) present 2019-01-31, none prints a total_debt line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
