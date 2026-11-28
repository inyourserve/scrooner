# BA certification precheck, 2026-11-28 (preparer: Scrooner data verifier): FAIL (census gate), draw clean

NOT a registry verdict and NOT a certificate. No certification request from top100-flow exists for this coverage; the coverage
file is this company's rows of the hourly export artifact top100-coverage-46167654745 (as_of 2026-11-28T16:55Z), so a
flow request will carry a different sha256 and a new seeded draw. Approver countersign is needed only for a FAIL record if wanted.

- Rank check: rank 84, company 207, CIK 12927; in ranks 1-100 of doc/data-moat/team/top1000/shards.csv and not excluded.
- Hourly summary: 0 OPEN in the hourly summary, but 2 pageless shown cells (gate_ready no).
- Coverage: `data-team/strategy/certification/BA-coverage-2026-11-28.csv`, sha256 `73ef96e1cff98ed524309f7b8ec477aec86b225ed04b37a26b5c6fa37fbf9395`.
- Run: pipeline/scripts/certify_display.py at origin/main f0f7ffbd9, --live (read-only, one connection), --no-registry, --reads approvals/reads/BA-73ef96e1cff9.csv where present.
- Blocker: dividends_per_share FY2020 and FY2021 (value 0, PROVEN, locator_source note_fact_report_not_stored: accession, no R page). Cause: the proof matched an FSN fact whose report is not stored, and no stated_zero/text_stated locator row exists for these two years (FY2022-FY2025 have one). Fix (resolver/text-stated locator, not a value change): attach FY2020 10-K 0000012927-21-000011 ba-20201231.htm Item 6 'Dividends declared per share (1) | — | 8.22 ...' and FY2021 10-K 0000012927-22-000010 ba-20211231.htm Item 7 'During the year ended December 31, 2021, we paid no dividends' as text_stated locators (open-shown-fixes/BA-2026-11-24.csv already decided this 11-17/22/23/24).
- Draw: 199 stratified shown cells, 0 wrong, Clopper-Pearson 95% upper bound 1.49% (target 1.5%). Every NEEDS_READ cell was read in the filing (FILING-CHECKED); reads file above.
- Next: land the fix above, then one top100-flow run for this company (queue empty), then display-certify on the new request.
- Untested: the 5% AUTO_MATCH audit sample (--audit-out) was not run; it belongs to the request-sha draw.

## Generated output: BA display certification (Ritwik (cloud), approver, 2026-11-28): FAIL

Coverage `data-team/strategy/certification/BA-coverage-2026-11-28.csv` (sha256 `73ef96e1cff98ed524309f7b8ec477aec86b225ed04b37a26b5c6fa37fbf9395`). Cells by display class: HIDDEN_ROW=11, HIDDEN_YEAR=3, SHOWN_VALUE=492. Seed `BA-73ef96e1cff9`.
Method: CERTIFICATION-METHOD-2026-11-16.md. Each shown value is matched to SEC's Financial Statement and Notes data set for the cited filing (fsn.*): same tag, period end, duration and dimensions, presented on the cited R page.

| Check | Result |
|---|---|
| Gate (no OPEN; value, accession and R page on every shown cell and part; parts sum) | 2 failing |
| 199 random shown cells (stratified, 5 strata of 481 shown) | 192 match, 0 wrong, 7 locator only |
| Automated draw checker (draw_check@3, the filing's own facts) | 192 auto-matched, 0 auto-mismatched, 7 need a read; 7 read, 0 pending |
| total_debt census (11 years) | 11 match, 0 wrong, 0 for review |
| Derived cells census (13 undrawn) | 13 match, 0 wrong, 0 for review |
| Hidden rows and years | 0 failing, 0 for review, 4 evidenced |

**Bound:** 0 error(s) in 199 random shown cells: Clopper-Pearson 95% upper bound **1.49%** for BA alone (target 1.5%; draw n = min(ceil(ln(0.05) / ln(1 - 0.015)), shown cells) = min(199, 481)). The 0.10% target is pooled across certified companies in registry.csv.

Draw by stratum (statement | badge class: drawn of shown): balance_sheet|as_printed 51/123, balance_sheet|derived 4/9, cash_flow|as_printed 58/140, income_statement|as_printed 80/195, income_statement|derived 6/14

## Drawn cells for a person or agent read (the machine did not settle them)

- **NEEDS_READ** dividends_paid FY2023 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 40 of 0000012927-24-000010 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2023 10-K 0000012927-24-000010 ba-20231231.htm Item 7 Liquidity: "In 2020, we announced the suspension of our dividend until further notice. As a result, we did not pay any dividends in 2023, 2022 and 2021." Served 0.)
- **NEEDS_READ** dividends_paid FY2024 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0000012927-25-000015 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2024 10-K 0000012927-25-000015 ba-20241231.htm Item 7: "we did not pay any dividends to common shareholders in 2024, 2023 and 2022." Served 0 (registry: dividends paid to common shareholders).)
- **NEEDS_READ** dividends_paid FY2025 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0001628280-26-004357 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2025 10-K 0001628280-26-004357 ba-20251231.htm Item 7 p.43: "Our dividend to common shareholders has been suspended since 2020." Cash flow prints only "Dividends paid on Mandatory convertible preferred stock (331)"; registry dividends_paid = common only, so common = 0. Served 0.)
- **NEEDS_READ** dividends_per_share FY2021 (text): text-stated value (no tagged fact): read the quote at ? of 0000012927-22-000010 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2021 10-K 0000012927-22-000010 ba-20211231.htm Item 7: "During the year ended December 31, 2021, we paid no dividends ... In March 2020, the Company announced that our dividend will be suspended until further notice."; equity statement has no dividends-declared row after 2019 ($8.22). Served 0.)
- **NEEDS_READ** dividends_per_share FY2022 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0000012927-25-000015 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2024 10-K 0000012927-25-000015 Item 7: "we did not pay any dividends to common shareholders in 2024, 2023 and 2022"; dividend suspended since March 2020. Served 0.)
- **NEEDS_READ** dividends_per_share FY2023 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 40 of 0000012927-24-000010 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2023 10-K 0000012927-24-000010 Item 7: "As a result, we did not pay any dividends in 2023, 2022 and 2021." Served 0.)
- **NEEDS_READ** dividends_per_share FY2025 (text): text-stated value (no tagged fact): read the quote at RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0001628280-26-004357 -- read by Scrooner data verifier (preparer, 2026-11-28; FILING-CHECKED, main document fetched from sec.gov): MATCH (FY2025 10-K 0001628280-26-004357 Item 7 p.43: "Our dividend to common shareholders has been suspended since 2020." Preferred dividends ($86 declared Dec 2025) are not common DPS. Served 0.)

## Findings

- **FAIL** gate dividends_per_share 2020: shown cell has no accession or R page
- **FAIL** gate dividends_per_share 2021: shown cell has no accession or R page
- **LOCATOR** dividends_paid FY2025: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0001628280-26-004357), no tag: approver reads the quote
- **LOCATOR** dividends_paid FY2023: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 40 of 0000012927-24-000010), no tag: approver reads the quote
- **LOCATOR** dividends_paid FY2024: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0000012927-25-000015), no tag: approver reads the quote
- **LOCATOR** dividends_per_share FY2025: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0001628280-26-004357), no tag: approver reads the quote
- **LOCATOR** dividends_per_share FY2023: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 40 of 0000012927-24-000010), no tag: approver reads the quote
- **LOCATOR** dividends_per_share FY2022: served 0, filing None. text-stated value located by its quote (RItem 7. Management’s Discussion and Analysis of Financial Condition and Results of Operati, p. 43 of 0000012927-25-000015), no tag: approver reads the quote
- **LOCATOR** dividends_per_share FY2021: served 0, filing None. text-stated value located by its quote (no locator of 0000012927-22-000010), no tag: approver reads the quote

## Hidden rows evidenced

- interest_income: no presented, undimensioned, annual ['InterestAndOtherIncome', 'InterestIncomeNonoperating', 'InterestIncomeOperating', 'InterestIncomeOther', 'InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend'] fact at a display-year end in any periodic filing

## Hidden years evidenced (allowlist)

- share_buybacks FY2023: allowlisted: 3 periodic filing(s) present 2023-12-31, none prints a share_buybacks line
- share_buybacks FY2024: allowlisted: 2 periodic filing(s) present 2024-12-31, none prints a share_buybacks line
- share_buybacks FY2025: allowlisted: 1 periodic filing(s) present 2025-12-31, none prints a share_buybacks line

## Limits

- This certifies the evidence for the cells listed; it does not authorize a production write (founder's typed words in the applying session).
- A change to any cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-sampled.
