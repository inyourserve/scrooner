# Sector templates for the top-1000 cohort: PROPOSAL (Sector Analyst, 2026-11-01)

Founder ruling 2026-11-01: no displayed cell may be blank; a field a sector does not report is not in that sector's template; coverage = valued / template cells; target 100% for the top-1000 (top 100 first). **Proposal only: no code, no DB writes.** Every rule below needs an accountant/Standardization Lead sign-off before use. Labels: MEASURED (query run this session on our tables; it is DATA-INFERRED about filings, no filing was opened), DATA-INFERRED, ASSUMED. Only a rendered-statement check (FILING-CHECKED) can finally call a line structural. Reuses: data-team/30 (2026-10-19), strategy/50 (rows catalog, incl. its v1 corrections), strategy/FSN-STORE-DESIGN-2026-11-01.md, mind `face-statement-evidence-20-of-consumed-concept-cells-are-not`.

## 0. How measured (commands actually run)
One read connection, `statement_timeout=50s`, no heavy joins. Cohort = the 1,000 ids in `data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv` (rank order = file order; "top 100" = first 100). Tables: `core.company.sic_code`, `analytics.company_data_point_coverage` (163 data points x 1,000 = 163,000 cells, latest `checked_at` 2026-10-31 19:47Z), `analytics.company_filing_line_evidence` (9 lines x 1,000 companies, migration 0093), `analytics.company_sec_tag` + `core.concept` (tag presence). `analytics.cell_blank_reason` was NOT used for the numbers (its run is per-period, a different grain; it has no `not_in_template` rows today). Scratch scripts: `/private/tmp/claude-501/-Users-vikash-scrooner/65fdba90-5f59-4bea-890d-a333f876958e/scratchpad/{an.py,imp.py,ov.py,*.sql}`. Grain caveat: coverage is one cell per company x data point (latest period). The per-period statement grid will be larger; the FSN store's proof grid is the final denominator.

## 1. Sector taxonomy for the cohort
Rule: **SIC proposes, the company's own statements decide.** SIC is only the first guess (data-team/30 hazard 6, role spec: never classify by label or by one missing line). Final test per company (to run on the FSN store, section 4): the face statements carry the sector's defining lines. Bank: interest income, interest expense, provision line, deposits, unclassified balance sheet, no revenue/COR face lines. Insurer: premiums earned plus benefits/claims on the face, unclassified balance sheet. Equity REIT: rental revenue plus real estate at cost/accumulated depreciation, unclassified balance sheet. Mortgage REIT: interest income/expense as revenue plus repurchase agreements. Utility: classified balance sheet plus utility plant (corporate rows apply, so it is a light template). Tag presence alone is NOT a test: `Deposits` + `InterestIncomeExpenseNet` also fire at FCX, ZBRA, CPAY, WEX, CBC (customer deposits / net financing interest), so a tag-only classifier misassigns them (MEASURED, DATA-INFERRED about meaning).

| Sector (template) | SIC rule | Cohort | Top 100 | Notes |
|---|---|---|---|---|
| General operating company | everything else (incl. managed care 6324 (7), insurance brokers 6411 (9), RE services/royalty 6500-6795 (11), crypto/AI miners 6199 (7: MSTR, COIN, CRCL, IREN, HUT, WULF, BMNR)) | 712 | 76 | managed care and brokers keep corporate statements; SIC 6324/6411 would misplace 16 |
| General, pharma/biotech sub-shape | 2834-2836, 8071 | 60 | 10 | corporate template; "pre-revenue" is an overlay decided per company (no revenue line), not SIC |
| Bank | 6021, 6022 (6035, 6036 none) | 41 | 5 | GBCI has no bank tags in our table (tag gap, still a bank by SIC) |
| Lender (bank-like income statement) | 6141, 6162, 6199 minus crypto: AXP, SYF, SOFI, RKT, AFRM, OMF, CACC | 7 | 1 | too small to template alone: assigned by sub-shape (bank-like or general) |
| Broker / asset manager / exchange | 6200, 6211, 6282 | 37 | 4 | mixed (GS/MS bank-like; KKR/APO/AMP have insurance arms; CME/ICE/NDAQ are corporate). Template = intersection of what all print |
| Insurer (P&C + life; 6311, 6321, 6331, 6351, 6361, 6399) | by SIC | 39 | 2 | life vs P&C premium tags differ; keep one template with COND rows |
| Equity REIT | 6798 minus mortgage | 51 | 1 | |
| Mortgage REIT | NLY, AGNC (by name, ASSUMED; no other mortgage REIT found in the 53 by tag test) | 2 | 0 | n=2 cannot support a measured template; follows the lender/bank-like rows |
| Utility | 4911, 4922-4924, 4931, 4932, 4941 | 51 | 1 | corporate template with 2 lines OUT |
| BDC / closed-end fund | none found (the `bdc_total_investment_income` concept fires at 15 insurers, a known false positive) | 0 | 0 | ASSUMED absent from this cohort; ARCC-type names are outside the top 1,000 |
| Energy / midstream | 1311-1389, 2911, 4610 (inside General) | 35 | not measured | **does not truly differ**: corporate rows apply (data-team/30 s2.5, still true); keep in General with an optional MLP row set |
Sum check: 712 + 60 + 41 + 7 + 37 + 39 + 51 + 2 + 51 = 1,000 (MEASURED). Not templated, hybrids that need a company-level overlay: BRK-A (insurer + industrial), CVS, F, DE, UHAL (finance/insurance arms), HOOD, EQH (MEASURED by tag presence, DATA-INFERRED).

## 2. Template per sector: IN / OUT
Legend: IN required; **OUT** removed for the sector; REP replaced by a sector row; COND in only for companies that print it (company overlay). Always IN everywhere (valued 77-100% in every sector at the latest period; dividends and buybacks vary by payer status and use the payer population): net income attributable, EPS basic and diluted, CFO, cash, total assets, total liabilities, equity, shares outstanding, tax, pretax income, SBC, D&A (a bank prints it in cash flow for 58% only: IN, COND), market cap, P/E, P/B, ROE, ROA, net margin, dividends, buybacks, EPS growth.

| Data point | General | Bank / lender | Broker-AM | Insurer | Equity REIT | Mtg REIT | Utility |
|---|---|---|---|---|---|---|---|
| Revenue | IN | REP bank revenue (NII + noninterest income; accountant, B7) | IN COND (net revenues) | IN (Revenues on the face for ~98%, doc 50) | IN (rental revenue) | REP interest income | IN |
| Cost of revenue / gross profit / gross margin / margin trend / Piotroski | IN, COND per company | **OUT** (E1: 98% / 100%) | GP **OUT** (100%); COR IN COND (86%) | **OUT** (97% / 100%) | GP **OUT** (98%); COR IN COND (78% absent) | **OUT** | GP **OUT** (100%); COR IN COND (67%) |
| Operating income / operating margin | IN | OUT by definition (interest is operating cost; 2% valued; accountant) | IN COND | IN COND (29-50% valued) | IN | OUT by definition | IN |
| Operating expenses | IN COND | **OUT** (93%; REP noninterest expense) | IN COND | IN COND | IN COND | IN COND | IN COND |
| SG&A | IN COND | OUT (0% valued; candidate) | IN COND | IN COND | IN (G&A) | IN COND | IN COND |
| R&D / R&D intensity | IN COND (441 of 712 absent) | **OUT** (100%) | **OUT** (97%) | **OUT** (100%) | **OUT** (100%) | **OUT** | **OUT** (100%) |
| Inventory / days / CCC / inventory change | IN COND | **OUT** (100%) | **OUT** (97%) | **OUT** (97%) | **OUT** (92%) | **OUT** | IN (fuel; 67% print) |
| Receivables / debtor days | IN COND | **OUT** (95% absent or combined) | IN COND (16 combined) | IN COND (premiums receivable differs) | IN COND | IN COND | IN |
| Payables / payable days | IN COND (95 combined) | **OUT** (95%) | IN COND (16 combined) | IN COND | IN COND (37 combined) | IN COND | IN |
| Current assets, current liabilities, current/quick ratio, working capital | IN | OUT candidate (0% valued, never any period) | IN COND (27% valued) | OUT candidate (0%) | OUT candidate (16%) | OUT candidate | IN |
| Goodwill / % assets | IN COND | IN COND (37 of 41 print) | IN COND | IN COND | IN COND (34 absent) | IN COND | IN COND |
| Interest income | IN COND | IN (all 41 print) | IN COND | IN COND | IN COND | IN | IN COND |
| Interest expense, interest coverage | IN | interest expense IN; coverage OUT by definition | IN | IN; coverage OUT by definition | IN | IN | IN |
| Total debt, D/E, net cash | IN | D/E OUT by definition (deposits; 63% show a value today, perimeter unreviewed); borrowings IN | IN COND | IN (FHLB perimeter: accountant) | IN | REP recourse leverage | IN |
| EBITDA family, ROIC | IN | OUT by definition | IN COND | OUT by definition | IN (EBITDA), ROIC IN COND | OUT | IN |
| Capex, FCF, FCF margin/yield | IN | OUT by definition (65% show a value today: wrong-class risk) | IN | OUT by definition (float dominates CFO) | OUT by definition (acquisitions investing) | OUT | IN |

Sector REP rows (candidate, face lines or arithmetic on them only; from strategy/50, v1 corrections applied, so tags are leads, unverified): Bank: net interest income (`InterestIncomeExpenseNet`), total interest income, interest expense (`InterestExpenseOperating`), noninterest income/expense, provision (`ProvisionForCreditLosses`, `ProvisionForLoanLeaseAndOtherLosses`, era split at CECL), deposits, loans net (post-CECL tag withdrawn), efficiency ratio, loans/deposits, equity/assets, TBV per share. Insurer: premiums earned, net investment income (two meanings, doc 50 F2/v1), claims incurred, policy acquisition costs, reserves, loss ratio (COND P&C/health). Equity REIT: rental revenue, property opex (COND), NOI (COND), real estate at cost, accumulated depreciation, debt/total assets. Mortgage REIT: interest income/expense, net interest spread, recourse leverage. Utility: utility plant net (COND). **Replacement rows add cells that are 0% valued today** (ASSUMED ~13 per bank, 9 per insurer, 8 per equity REIT, 6 per mortgage REIT, 3 per utility = about 1,000 new cells cohort-wide, almost all `definition_pending`/`evidence_pending` defects until built). They enlarge the denominator before they raise coverage.

## 3. Evidence per OUT decision
Rule used (stated before measuring): OUT iff (absent + combined) / n >= 90% AND separately presented <= 10% of the sector's cohort members, per `company_filing_line_evidence` (latest 10-K/10-Q, E1 evidence, not proof: data-team/30 notes 14-34% of held values show no face line). Cells = companies absent / combined / presented separately (MEASURED).

| Line | Bank 41 | Lender 7 | Broker-AM 37 | Insurer 39 | Eq REIT 51 | Mtg REIT 2 | Utility 51 | Pharma 60 | General 712 |
|---|---|---|---|---|---|---|---|---|---|
| Gross profit | 41/0/0 OUT | 7/0/0 OUT | 37/0/0 OUT | 39/0/0 OUT | 50/0/1 OUT | 2/0/0 | 51/0/0 OUT | 51/0/9 no (85%) | 352/0/360 no |
| Cost of revenue | 40/0/1 OUT | 6/0/1 | 32/0/5 no (86%) | 38/0/1 OUT | 40/0/11 no (78%) | 2/0/0 | 34/0/17 no | 11/0/49 | 140/0/572 |
| Inventory | 41/0/0 OUT | 7/0/0 OUT | 36/0/1 OUT | 38/0/1 OUT | 47/0/4 OUT | 2/0/0 | 17/0/34 no | 11/0/49 | 223/0/489 |
| R&D | 41/0/0 OUT | 6/0/1 | 36/0/1 OUT | 39/0/0 OUT | 51/0/0 OUT | 2/0/0 | 51/0/0 OUT | 3/0/57 | 441/0/271 |
| Operating expenses | 38/0/3 OUT | 4/0/3 | 12/0/25 no | 21/0/18 no | 9/0/42 no | 1/0/1 | 15/0/36 no | 14/0/46 | 348/0/364 |
| Accounts receivable | 36/3/1 OUT | 6/0/1 | 6/4/27 no | 23/1/15 no | 26/5/20 no | 0/0/2 | 0/3/48 no | 9/0/51 | 33/25/654 |
| Accounts payable | 39/1/1 OUT | 2/3/2 | 4/16/17 no | 19/7/13 no | 7/37/7 no | 0/0/2 | 0/2/49 no | 0/10/50 | 13/95/604 |
| Goodwill | 4/0/37 no | 2/0/5 | 5/0/32 | 12/0/27 | 34/0/17 no | 1/0/1 | 18/0/33 | 20/0/40 | 89/0/623 |
| Interest income | 0/1/40 IN | 1/0/6 | 11/1/25 | 1/1/37 | 16/12/23 | 0/0/2 | 37/0/14 | 25/7/28 | 399/46/267 |

n=7 (lender) and n=2 (mortgage REIT) are below any statistical use: their OUT marks are inherited from the bank-like family and carried as "unconfirmed". **Not OUT, whatever intuition says**: every line for General and Pharma (no line reaches 90%: general companies present R&D at 271 of 712, gross profit at 360), so those two templates stay full and rely on company overrides (section 4). Measured exceptions inside OUT cells (company-level overrides, 19 total): Bank 10: JPM AR (comb) x2, BAC AR (comb), BNY AR (comb) and AR, BOKF AR, MTB COR, BPOP/C/STT opex; Equity REIT 5: RYN, LINE, SUI, WY inventory, WY gross profit; Insurer 2: BRK-A inventory and COR; Broker-AM 2: SNEX inventory, HOOD R&D.

**Not yet evidenced (do not mark OUT; no probe exists):** current assets/liabilities and their ratios, D&A, capex, CFO, dividends, buybacks, SG&A, interest expense, tax, operating income, goodwill-like lines beyond the 9. `company_filing_line_evidence` covers 9 lines only. For banks and insurers current assets are 0% valued and have never had a value in any period (MEASURED), which makes them OUT candidates but only DATA-INFERRED; vendor or tag absence cannot decide it. Next action 1: extend `parsers/filing_line_evidence.py` to current assets, current liabilities, SG&A, operating income, D&A, capex for the 175 non-General sector companies first (cheap, bounded), then the cohort. "OUT by definition" cells (EBITDA, FCF, ROIC, interest coverage, D/E for banks and insurers, operating income/margin for banks) are accountant decisions, not evidence decisions (role spec: avoid industrial EBITDA/FCF for banks); they must be labeled as such on the page.

## 4. Company-level overrides
Rule: **the company's template = the lines its own statements present; the sector template is only the default and the tie-breaker.** Three steps, all computable from the FSN store (`fsn.line`, `fsn.line_map`, `fsn.report`): (1) sector default from section 1/2; (2) for each template line, the company's latest 10-K and last two 10-Qs either print a face line mapped to that concept (IN), print only a combined line (IN under the company's own label, section 5), or print nothing (OUT for that company, evidence = accession + R-page + line search); (3) any face line the company prints that the sector template lacks and that maps to a concept in our catalog is added (COND) (JPM AR, BRK-A inventory above). Effective-dated: the template is per filing period (a company that starts printing a line, or exits pre-revenue, changes template from that filing; the cell history keeps the old template). Hybrids (BRK-A, CVS, F, DE, UHAL, AMP/APO/KKR, HOOD, EQH): template by dominant face shape, second shape's lines added as overlay rows, as doc 50 s4 q1 proposes. Counts today: 19 company-line overrides inside the OUT templates (s3); inside the always-full General and Pharma templates the company-level OUT population is **1,528 + 53 blank cells already evidenced `line_not_presented_in_filing`** and a further ~4,420 cohort blank cells (360 top-100) sit on a line the company's own evidence says is absent but carry another reason (upstream/no reason/other): those would be re-labeled OUT for that company once step (2) is run (DATA-INFERRED; evidence is not proof). 1,732 valued cells (191 top-100) also sit on lines the evidence says are not on the face (mostly derived GP, CCC): they need Verifier review, not deletion.

## 5. Combined lines
A company that prints a combined line shows that line under its own label as the cell for the concept it spans; no concept is silently filled with the combined amount (FSN design s3 rule 3: status `combined`, blank `line_presented_combined_with_others`). MEASURED where combined lines occur most (probe, cohort): accounts payable (general 95, REIT 37, broker 16, insurer 7, utility 2 of its sector), accounts receivable (general 25, broker 4, REIT 5), interest income (general 46, REIT 12, pharma 7), goodwill 0. Not probed: D&A (typically inside cost of revenue/opex or the cash-flow line), accrued liabilities, short-term investments.
How metrics behave (proposal; accountant to confirm): (a) a metric whose numerator or denominator is a combined line is **NOT-APPLICABLE for that company** unless the combined line IS the metric's definition input by approval (e.g. "accounts payable and accrued liabilities" never feeds plain `payables_days`, per the root CLAUDE.md bullet on migration 0093); the cell shows "not computed: payables printed combined with accrued liabilities", it is not blank and not a guess. (b) D&A printed only inside another line: EBITDA, EBITDA margin, EV/EBITDA, Net debt/EBITDA, Debt/EBITDA are N/A for that company if the cash-flow D&A line is also absent; if the cash-flow statement prints D&A (almost all do, 85-91% valued in General), EBITDA computes from it. (c) Net income attributable vs incl. NCI printed combined: ROE/net margin follow the attributable rule in the net income bridge entry; if not printed, the cell is a defect, never combined. (d) Cost of revenue combined with opex (no gross profit): gross margin OUT for that company (company override), operating margin still computes from operating income if printed.

## 6. Impact estimate (coverage snapshot 2026-10-31; MEASURED counts, assignment of cells to categories is DATA-INFERRED)
Cells = 163 data points x 1,000 (top 100: 16,300). Valued today: **123,995 (76.1%)** cohort, **13,104 (80.4%)** top 100. Blank: 39,005 cohort, 3,196 top 100.
OUT categories (cells leave the template; counts are blank / of which currently valued):
| Category | Basis | Cohort blank (valued) | Top 100 blank (valued) |
|---|---|---|---|
| A: OUT by section-3 evidence (+ dependent metrics, e.g. gross margin, Piotroski, CCC, days) | MEASURED E1 | 2,832 (209) | 216 (9) |
| D: company-level, gap_reason already `line_not_presented_in_filing`, outside A/B/C | MEASURED label | 1,872* | 151* |
| B: OUT candidates pending probe (current assets/liabilities and ratios, bank/insurer/REIT) | DATA-INFERRED | 854 (63) | 56 (0) |
| C: OUT by definition, accountant decision (EBITDA, FCF, ROIC, coverage, SG&A, net cash for banks/insurers/lenders) | ASSUMED | 1,183 (546) | 117 (37) |
*D per sector in the table: General 1,528, pharma 53, REIT 58, utility 111, insurer 56, broker 50, lender 16 (cohort); top 100: 138+1+1+3+2+5+1. Note C removes 546 cohort cells (37 top-100) that HAVE a value today; those values are displayed for banks/insurers now and the accountant decides if they stay.
Template coverage after OUT (valued / remaining cells): now 76.1% → A 77.4% → A+D 78.3% → A+B+D 78.7% → A+B+C+D **79.2%** cohort; top 100: 80.4% → 81.5% → 82.2% → 82.5% → **83.1%**. **Sector templates alone move coverage by about 3 points; they do not reach 100%.** After A+B+C+D, 83% of today's blank cells stay IN-and-blank: **cohort 32,264** (of 39,005; 6,741 leave) and **top 100 2,656** (of 3,196; 540 leave), real defects or reasonless cells, before replacement rows add more denominator.
Remaining IN-and-blank by reason (gap_reason class; cohort / top 100):
| Class | Cohort | Top 100 | Owner |
|---|---|---|---|
| No reason recorded (`gap_reason` null; the "reasonless blanks") | 12,715 | 1,019 | Data Chief / reason rules (B3) |
| Upstream input missing (`incomplete:*`, `missing:<concept>`) | 12,115 | 1,051 | resolver/period/mapper families |
| Math / history / non-payer (reasoned: negative CAGR base, <3 years, no dividend history, pre-revenue) | 5,746 | 463 | already reasoned; show as "undefined by math", not blank |
| `line_presented_combined_with_others` (IN under company label) | 187 | 18 | combined label (s5) |
| Sector revenue perimeter (`*_not_revenue`: bank, REIT, BDC, financial institution) | 520 | 44 | replaced by sector revenue row (needs definition B7) |
| `line_in_filing_not_extracted` (the filing HAS the line) | 750 | 61 | extraction defect, Data Engineer |
| Implausible value (institutional shares exceed outstanding) | 215 | 0 | defect |
| Other (stale shares) | 16 | 0 | defect |
(Table = IN-and-blank after A, B, C and D are removed; classes sum to 32,264 and 2,656. Without the B/C scenarios, add back 854+1,183 cohort / 56+117 top-100 blank cells.)
Top-100 reality: 2,656 IN-blank cells, of which 1,019 reasonless and 1,051 upstream. 100% of top 100 requires fixing those, not shrinking the template.

## 7. Risks and decisions needed
1. **Evidence is the 9-line probe only.** OUT today is justified for 9 lines. Everything else in the template matrix marked "candidate" or "by definition" is not evidenced; do not publish those OUTs until probe extension or accountant sign-off.
2. **n is small:** lender 7, mortgage REIT 2, BDC 0; insurer 39 mixes P&C and life; broker-AM 37 mixes four business models. Per-sub-shape confirmation needs the FSN statement shape per company.
3. **OUT hides valued cells** (209 A, 546 C cohort). Removing a displayed, correct value to follow a template is a product call for the founder/accountant; the safe default is: a template-OUT line with a value we hold stays displayed until the Verifier rules it wrong.
4. **Coverage denominators:** replacement rows enlarge it first; report coverage on a frozen template version (`catalog_version`) and show OUT counts openly (role spec: never improve coverage by silently shrinking the denominator). Decision needed: is "OUT by definition" counted as OUT in the founder's coverage, or as "not applicable" shown separately?
5. Hybrids and sub-shapes must be re-derived from FSN once loaded; the SIC counts here will shift (SIC 6199/6211/6282 hide four models).
6. Accountant items still open (doc 50 v1): bank revenue B7, capex definition R8, debt perimeter R7, BDC NII definition, collision of registry `net_interest_income` (InvestmentIncomeInterest) with the bank NII row.

## 8. Approval (Ritwik, release approver; not the preparer), 2026-11-01
Status: **APPROVED WITH CORRECTIONS**, under the all-agent approver policy (approver ≠ preparer). Dhairya's rulings (scrooner-df, 2026-11-01) are adopted. This page is analysis, not seeder input: `scrooner-map seed-sector-templates` needs the four-table file (`mapper/sector_templates.py` header). The preparer writes that file from this section; the approver checks the file against it before 0120 is applied.
1. **Taxonomy and the OUT evidence rule (§1, §3): approved.** SIC proposes and the company's own statements decide. The section-3 OUTs (category A, 9 probed lines) are approved as sector defaults.
2. **OUT by definition (category C): approved as OUT.** EBITDA family, capex/FCF family, ROIC and interest coverage for banks, lenders and insurers; D/E and operating income/margin for banks; plus the matrix's other "by definition" cells. They are not in the template and do not count in the denominator. The page labels them "not applicable by definition" and we publish OUT counts per `template_version`. A value we already hold on an OUT line stays shown **only** where that company's own statements present the line (company override, `in_template = true`, reason = evidence accession).
3. **Category B (current assets/liabilities and ratios for banks, insurers, REITs): not approved as sector OUT.** They stay IN by default. The FSN-store company step (§4 step 2) removes them per company, with the accession as evidence. A sector-level OUT needs the probe extension first.
4. **Correction, BDCs.** §1 says no BDC is in the cohort; that is wrong. Cohort v1.1 holds ARCC (CIK 0001287750, rank 588) and BXSL (CIK 0001736035, rank 999). Add a `bdc` template (ASC 946 investment company) and assign both by company assignment:
   - REP: total investment income replaces revenue.
   - IN: net investment income, NAV per share, total debt / D/E (asset coverage), NII per share.
   - OUT by definition: COR/GP, inventory, R&D, current ratio family, EBITDA family, capex/FCF family.
   - **Ruled by the founder 2026-11-01** (doc 02): revenue = total investment income as printed (interest, dividend and fee income); the earnings line = net investment income as printed. The seeder file marks both as ruled, not `definition_pending`.
5. **Correction, CBC.** CBC is Central Bancompany, Inc. (CIK 0002065601), a bank holding company with no SIC in our master. Assign it to `bank` by company assignment. Delete it from §1's list of tag false positives.
6. **Cohort:** v1.1, 1,000 companies (`data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv`), not shards.csv's 986. Redo §1's sum check with ARCC, BXSL and CBC moved.
7. **Lender (n=7) and mortgage REIT (n=2):** the inherited OUT marks are approved as defaults only. The FSN company step decides per company.
8. **The goal is unchanged:** templates move coverage by about 3 points. The 12,715 reasonless and 12,115 upstream blanks are the work.
