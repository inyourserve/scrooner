# R4. Sector applicability: how much of the coverage gap is "does not apply", and the template layer that classifies every blank (Sector Analyst, 2026-10-21)

Role: Sector Analyst (12). Read-only. Everything below is PROPOSAL-ONLY (no accounting approval). Files written: this file only (plus one line in `data-team/tags/feedback-inbox.md`, required by the standing tag-learning rule).

Evidence labels: **FILING-CHECKED** = filing opened, locator cited. **DATA-INFERRED** = SEC Financial Statement Data Sets (FSDS) or our files, no filing opened for that item. **ASSUMED** = stated as such.

## 0. What was run, what was not
- Read: BRIEF, data-team 20/12/22/30/31/33/34, `mapper/definitions.py` + `expanded_definitions.py`, `mapper/coverage_matrix.py` (populations), `common/sector_applicability.py`, `doc/data-moat/team/top1000/{README,shards.csv,results/S*.md}`.
- Downloaded (2 files, 213 MB total, User-Agent from `pipeline/.env`, 2 requests): FSDS `2026q1.zip` and `2025q3.zip`; only `sub.txt` + `pre.txt` extracted; zips deleted. Used with the already-extracted 2025q4. Result: the latest 10-K per CIK across 2025q3/q4/2026q1 = **4,960 filers** (4,936 with face statements; 24 have none, ABS-type). Missing: filers whose latest 10-K was filed Apr-Jun 2025 (March-June fiscal year ends) and the successor-CIK cases.
- Filings opened (FILING-CHECKED, 3 requests, R5 income statement): Popular 0001193125-26-085756 (CIK 763901); Skyward Specialty 0001519449-26-000015; Empire State Realty Trust 0001541401-26-000008.
- **DB: NOT_RUN.** `pg_stat_activity` = 23, 21, 21, 20, 18 across five tries (rule: <= 14). So no fresh blank counts. Blank counts used are (a) `shards.csv` (2026-10-18 baseline, 163 data points) and (b) the worker-classified `not_applicable` column in the shard result tables (129 of the 1,000 companies, parsed from `results/S*.md`), and (c) data-team/30's 2026-10-19 pivot. All DATA-INFERRED.
- Scripts (read-only; scratchpad, not in repo; copy to `data-team/strategy/tools/` if wanted): `/private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/r4/scripts/{feat,analyze,stats,cells,tables}.py`, outputs `cls.json` (cik -> family + 33-concept face flags), `v1presence.csv`, `concept_table.csv`.
- Method limits: family and "line on the face" are tag-set plus label-regex rules over `pre.txt` (income statement, balance sheet, cash flow lines). Rule precision was not measured against opened statements beyond the 3 filings. "Not on the face" is not "not in the XBRL" (a line can sit in a note).

## 1. Headline (read this)
1. Of 212,014 (filer x {29 consumed concepts that are not activity-based (dividends, buybacks excluded) + 17 V1 metric rows}) cells in the FSDS population, **20.5% are not on the filer's own face statements**. About **40% of those (7-9% of all cells) are family-structural** (the line is presented by <= 10-30% of that family): a template removes them. About **60% (11.6-13.5% of all cells) are filer-variable** (family presents it at 10-95%): only a per-filing check removes them. A template layer alone cannot get to "every blank classified"; per-filing evidence is the larger lever.
2. Top-1000 (measured by the campaign's own workers, 129 companies, 3,828 blank cells): **31% of blank cells were classified `not_applicable`**; by family: banks 85%, non-bank deposit takers 73%, insurers 64%, REITs 44% (n=2 companies, weak), asset managers 42%, industrials 23%, energy 7%, utilities 5%. About 23 points of the 31 are NOT sector: dividend rows for non-payers, `bdc_total_investment_income` and `net_lease_revenue` rows counted against every company, negative-growth PEG. The sector-template part is about **11-12% of top-1000 blanks** (3,491 of 29,931 by my arithmetic, section 4).
3. Five templates (bank, insurer, pre-revenue overlay, REIT, BDC/fund) hold **95% of the family-structural cells** (16,647 of 17,520 at the 20% threshold). Utilities, energy, MLPs, real-estate operators, insurance agents, non-bank lenders are not template families: their blanks are vocabulary or per-filing.
4. Present-but-inapplicable values are a second defect, not only blanks (data-team/30 s6, `sector_applicability.py`): the code covers banks only, at serve time. No other family has any suppression. Insurers and REITs still show gross margin, current ratio, FCF yield from industrial formulas.

## 2. Families and counts
Family = evidence rule on the filer's own statements (precedence order: SPAC/trust assets; commodity-crypto pool; BDC/fund; bank = deposits liability + loans/NII/noninterest expense with SIC 6020-6036; deposit taker with other SIC; insurer = premiums + claims; REIT = SIC 6798 or real-estate assets + rental revenue, mortgage if mortgage assets and no rental revenue; SIC 62xx split by fees vs brokerage; non-bank lender 6000-6199; utility 49xx; MLP = partners' capital; energy; exploration miner; pre-revenue = no revenue line + R&D; else corporate).

| Family | FSDS filers (4,960) | Top-1000 companies | Top-1000 blank cells (of 29,931) | DB active (data-team/30, SIC bin, 10-19) |
|---|---|---|---|---|
| Corporate (all other) | 2,786 | 644 | 15,025 (50.2%) | about 2,732 |
| Insurers (underwriters) | 120 | 54 | 2,768 (9.2%) | 127 (incl. 26 agents) |
| REIT, equity | 235 | 52 | 2,524 (8.4%) | 196 (6798, both kinds) |
| Banks and thrifts | 331 | 42 | 2,297 (7.7%) | 326 |
| Utilities and waste | 134 | 49 | 1,273 (4.3%) | 127 |
| Energy | 129 | 31 | 960 (3.2%) | 150 |
| Deposit takers with non-bank SIC (AXP/SCHW-type) | 37 | 10 | 528 | in A2/B |
| Asset managers / advisers (incl. fund vehicles under 6282) | 87 | 16 | 525 | 107 with brokers |
| Non-bank lenders, fintech | 108 | 9 | 484 | 148 |
| Brokers, exchanges | 33 | 9 | 378 | in B |
| Insurance agents | 17 | 6 | 240 | in C |
| REIT, mortgage | 35 | 3 | 201 | in D1 |
| BDC / investment company (SIC blank for 129) | 194 | 2 | 191 | 118 in `bdc_company` |
| Pre-revenue (R&D, no revenue line) | 218 | 2 | 121 | about 131 (pharma SIC guess) |
| MLP | 32 | 4 | 139 | in F |
| Real-estate operator | 46 | 3 | 102 | 71 |
| SPAC | 279 | 2 | 75 | 326 (6770 etc.), already out of `real_operating_company` |
| Commodity / crypto pool trusts | 31 | 0 | 0 | 6221 mostly excluded |
| Other trusts | 17 | 6 | 221 | |
| Exploration-stage miners / no revenue line other | 31 + 36 | 0 + 2 | 49 | |
| ABS-type, no statements | 24 | 1 | 24 | |
| Not matched in FSDS (June-Sept FYE or successor CIK, e.g. XOM holdco) | n/a | 53 | 1,806 | |
Real-operating shape (FSDS minus SPAC, pools, other trusts, ABS) = 4,609 filers vs DB `real_operating_company` 4,808. Hazards, FILING-CHECKED where noted: SIC 6199 contains crypto ETFs and miners; SIC 6221 is pools, not brokers; SIC 6798 mixes equity and mortgage; deposits appear at non-banks; Popular tags a partial fee line as revenue (below).

## 3. Per family: which of the 33 consumed concepts and 18 metrics apply, are replaced, or must be re-defined
The 33 consumed concepts (from `definitions.py` + `expanded_definitions.py` inputs; matches the "88 inputs over 33" in PLAN.md): accounts_payable, accounts_receivable, basic_eps, capex, cash_and_equivalents, cash_flow_financing, cash_flow_investing, cfo, cost_of_revenue, current_assets, current_liabilities, depreciation_and_amortization_resolved, diluted_eps, dividends_paid, dividends_per_share, goodwill, income_before_tax, income_tax_expense, interest_expense, interest_income, inventory, net_income, operating_income, operating_income_resolved, research_and_development, revenue, sbc, sga_expense, share_buybacks, shares_outstanding, stockholders_equity, total_assets, total_debt_resolved. (`operating_income_resolved` follows `operating_income`.)

Percent of family filers whose own statements present the line (DATA-INFERRED, FSDS, label/tag rules). Codes: A apply, N not applicable (line absent), R replace, D re-define, V per-filing (10-95%).

| line | corp 2786 | util 134 | energy 129 | bank 331 | insurer 120 | REIT eq 235 | REIT mtg 35 | asset mgr 87 | broker 33 | lender 108 | BDC 194 | pre-rev 218 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| revenue | 100 | 95 | 98 | **49 D** | 99 | 96 | **54 D** | 47 V | 61 V | 89 | 2 R | 0 N |
| cost_of_revenue | 83 | 49 V | 57 V | 0 N | 10 N | 23 V | 9 N | 5 N | 15 N | 38 V | 0 N | 0 N |
| operating_income | 94 | 98 | 88 | 9 N | 19 N | 45 V | 11 N | 43 V | 61 V | 68 V | 6 N | 97 |
| income_before_tax / tax | 90 | 90 | 86 | 100 | 99 | 49-54 V | 60 V | 46 V | 55 V | 88 | 34-42 V | 39-41 V |
| net_income | 100 | 100 | 99 | 100 | 100 | 99 | 100 | 93 | 100 | 99 | 95 | 100 |
| diluted_eps / basic_eps | 99/95 | 78/73 V | 88/82 | 97/98 | 89/90 | 98/94 | 100/97 | 52/64 V | 55/52 V | 91/87 | 65/63 V | 99/97 |
| interest_expense | 73 | 93 | 83 | 100 | 82 | 92 | 100 | 39 V | 85 | 78 | 83 | 39 V |
| interest_income | 60 | 43 | 55 | 100 | 94 | 59 | 94 | 63 | 91 | 65 | 100 | 76 |
| sga_expense | 52 V | 18 | 30 | 2 N | 16 | 6 N (G&A 91) | 3 N | 5 N | 6 N | 20 | 1 N | 7 N |
| research_and_development | 50 V | 6 | 5 | 0 N | 1 N | 0 N | 0 N | 0 N | 3 N | 21 | 0 N | 100 |
| sbc | 91 | 55 | 71 | 82 | 68 | 74 | 69 | 43 | 55 | 83 | 2 N | 96 |
| depreciation_and_amortization | 97 | 99 | 95 | 100 (*) | 92 (*) | 97 | 91 (*) | 68 | 85 | 94 | 92 (*) | 89 |
| cfo / investing / financing | 100/97/99 | 100 | 100 | 100 | 100 | 99 | 100 | 74/49/66 | 97/55/97 | 99 | 98/1/98 | 100/87/100 |
| capex | 91 | 95 | 85 | 95 | 72 V | 86 | 37 V | 46 V | 52 V | 73 | 1 N | 68 V |
| dividends_paid / per share | 37/21 (activity) | 83/48 | 63/25 | 89/79 | 79/36 | 94/46 | 91/49 | 48/31 | 67/30 | 34/9 | 82/9 | 1/0 |
| share_buybacks | 55 | 38 | 57 | 88 | 78 | 69 | 94 | 51 | 82 | 50 | 50 | 9 |
| total_assets / equity | 100/100 | 100/95 | 100/100 | 100/100 | 100/100 | 100/100 | 100/100 | 94/54 V | 100/100 | 99/99 | 96/84 | 100/100 |
| cash_and_equivalents | 100 | 99 | 99 | 100 | 100 | 100 | 100 | 56 V | 94 | 98 | 92 | 100 |
| current_assets / liabilities | 98 | 100 | 99-100 | 0 N | 11 N | 7 N | 0 N | 16 N | 15 N | 62 V | 0 N | 97 |
| inventory | 64 V | 63 V | 49 V | 0 N | 3 N | 3 N | 6 N | 1 N | 3 N | 6 N | 0 N | 1 N |
| accounts_receivable | 88 | 97 | 91 | 17 N | 48 V | 55 V | 17 N | 38 V | 30 V | 60 V | 7 N | 8 N |
| accounts_payable | 99 | 100 | 99 | 13 N | 43 V | 86 | 54 V | 79 | 58 V | 83 | 47 V | 100 |
| goodwill | 62 V | 59 V | 27 V | 76 | 57 | 18 V | 9 N | 38 V | 45 V | 32 V | 0 N | 9 N |
| total_debt_resolved | 77 | 99 | 83 | 92 **D** | 90 D | 89 | 77 D | 37 V | 45 V | 79 | 80 | 40 V |
(*) "amortization" lines at financials are often premium/discount/DAC amortization, not D&A: D&A presence here is overstated (perimeter issue, see Ritwik's 39).

Metric rows (share of family filers with ALL inputs on the face), V1 18 metrics (20 DB rows):

| metric | corp | bank | insurer | REIT eq | REIT mtg | BDC | pre-rev | Disposition |
|---|---|---|---|---|---|---|---|---|
| gross_margin | 83 | 0 | 10 | 23 | 9 | 0 | 0 | N for bank, insurer, mortgage REIT, BDC, pre-rev. V for REIT eq, utility 48, energy 57 |
| operating_margin | 94 | 5 | 19 | 44 | 6 | 1 | 0 | N bank, insurer, mtg REIT, BDC, pre-rev. V REIT eq (needs OI fallback from components) |
| net_margin, revenue_growth, price_to_sales | 100 | 49 | 99 | 95 | 54 | 2 | 0 | D for bank (bank revenue) and mortgage REIT (interest income as revenue); N for BDC (replace with total investment income) and pre-rev |
| roe, price_to_book | 100 | 100 | 100 | 99 | 100 | 79-84 | 100 | A everywhere (BDC: net assets/NAV) |
| eps_growth, trailing_pe | 99 | 97 | 89 | 98 | 100 | 65 | 99 | A; N where the filer reports no EPS (LLC/LP/wholly-owned subsidiary registrants: utilities 78%, asset mgr 52%, BDC 65%) |
| market_cap | 100 | all | all | all | all | all | all | A (cover page shares, assumed) |
| roic | 66 | 9 | 17 | 22 | 6 | 0 | 19 | N bank, insurer, mtg REIT, BDC; V REIT eq (needs OI and debt) |
| fcf, fcf_margin, fcf_yield | 91 | 95 (**meaning N**) | 72 (**meaning N**) | 86 | 37 | 1 | 68 | bank and insurer: lines exist, metric meaningless (CFO is deposit/loan/float flow): N by definition rule (E-M, section 6), not by absence. REIT: D (capex definition) |
| debt_to_equity | 77 | 92 **D** | 90 D | 89 | 77 D | 72 | 40 | bank: deposits are not debt; replace with equity/assets or borrowings/equity |
| current_ratio | 98 | 0 | 11 | 7 | 0 | 0 | 95 | N for bank, insurer, REIT, mtg REIT, BDC |
| interest_coverage_ratio | 69 | 9 | 17 | 40 | 11 | 3 | 38 | N bank, insurer, mtg REIT, BDC; V REIT (OI) |
| dividend_yield | 21 (activity) | 79 | 36 | 46 | 49 | 9 | 0 | A for payers; reason "no dividend in latest FY" for others (E2) |
Registry rows that exist only for a sector (`bdc_total_investment_income`, `net_lease_revenue`) must be gated by the family, not counted against all companies.

### Replacement and re-definition per template (proposals; inputs from face tags in FSDS, rates DATA-INFERRED)
- **Bank / thrift.** Revenue must be re-defined. FILING-CHECKED at Popular 0001193125-26-085756 R5: the statement has Total interest income 3,783,009, Net interest income 2,541,203, Total non-interest income 658,019 (thousands) and no total revenue line; the XBRL tag `RevenueFromContractWithCustomerExcludingAssessedTax` is on the face only as a partial line "Net fees" (FSDS pre.txt). Across 331 banks (DATA-INFERRED): `Revenues` on the face 2%, `RevenueFromContract*` 44% (a partial fee line), `InterestIncomeExpenseNet` 97%, `NoninterestIncome` 98%, `NoninterestExpense` 98%, `Deposits` family present. Proposal for the Standardization Lead and a named accountant: bank revenue = NII + noninterest income, labelled; do not read `Revenues` (Citigroup is net, ledger 2026-10-19) or `RevenueFromContract*`. New concepts (data-team/30 s2.1): NII, interest income on loans, deposit interest, noninterest income and expense, provision (CECL tag switch needs period-scoped tags), deposits, loans, allowance, nonaccrual, Tier 1. N by absence: gross margin, operating margin, ROIC, current ratio, interest coverage, inventory, receivables, payables, SG&A, R&D. N by meaning: FCF family, debt-to-equity on borrowings. Matches `sector_applicability.py` except that it hides "Total Debt" and some rows for a "pending" reason, never replaces them.
- **Insurer (underwriter).** Revenue applies (`Revenues` 98%; FILING-CHECKED Skyward R5: "Total revenues" 1,416,541 = net earned premiums 1,304,505 + fee 6,855 + NII 83,619 + gains 22,149 + other (587)). No cost of revenue, no operating income (19%), no classified balance sheet (11%). Replace with premiums earned (`Premiums*` on face 92%), losses and LAE incurred, net investment income (83%), reserves; loss ratio only for P&C and health where both inputs exist; combined ratio stays "reported in MD&A, not on the face" (data-team/30). Keep separate: life, P&C, health; agents/brokers (17) are ordinary companies.
- **Equity REIT.** Mostly ordinary (revenue 96%, interest 92%, D&A 97). N: current ratio, inventory, R&D, goodwill mostly; SG&A replaced by G&A (91%). V: operating income (45%) and gross margin (23%): property operating expenses are a different line (ESRT R5, FILING-CHECKED: "Property operating expenses" 184,714, "Total operating income" 135,649, no cost of revenue). FFO/AFFO/NOI not computed from the face. Capex is a definition item (capital improvements vs acquisitions, S008 WELL).
- **Mortgage REIT.** Own set: interest income, interest expense, net interest spread, book value per share, economic leverage; revenue D; coverage replaced by spread.
- **BDC / investment company.** Own concept set: total investment income (`GrossInvestmentIncomeOperating` 78%), net investment income (90%), net assets, investments at fair value, distributions. 13 of 32 listed concepts and 11 of 17 metric rows do not apply.
- **Pre-revenue overlay (not an SIC class).** No revenue line on the latest 10-K statements plus R&D or exploration. N: every revenue-denominated row. Apply: operating income (97%), CFO, EPS. Add: R&D, cash burn, cash plus short-term investments (needs a concept), runway (disclosed formula), accumulated deficit, dilution. Effective-dated: a company leaves the overlay in the first fiscal year it presents revenue.
- **Broker-dealer, exchange, asset manager.** Heterogeneous (SIC 6211/6282 contain fund vehicles). Split by statement shape: fees plus operating income (Franklin Resources 0000038777-25-000238, FSDS IS report 3) = ordinary template minus gross margin; investment-company shape = BDC/fund template; brokerage shape = partial bank-like (no classified balance sheet). Do not build a family template before a 30-company statement review.
- **SPAC, commodity/crypto pool trust, other trust, ABS.** Not screener companies: show one stated reason plus trust assets. 351 FSDS filers. The existing classifier already removes SPACs and pass-through trusts.

## 4. Share of current blank cells that are not applicable
Measured (DATA-INFERRED, worker-classified, partly FILING-CHECKED in the shard files; 129 companies, 3,828 blanks; not a random sample, ranks 1-100 heavy):
| Family | companies in sample | blanks | `not_applicable` | rate |
|---|---|---|---|---|
| Bank | 6 | 351 | 299 | 85% |
| Non-bank deposit taker | 5 | 264 | 194 | 73% |
| Insurer | 5 | 201 | 128 | 64% |
| REIT, equity | 2 | 109 | 48 | 44% (too few) |
| Asset manager | 3 | 113 | 47 | 42% |
| Insurance agent | 1 | 28 | 11 | 39% |
| Corporate | 90 | 1,861 | 421 | 23% |
| Energy | 5 | 110 | 8 | 7% |
| Utility | 4 | 79 | 4 | 5% |
| All | | 3,828 | 1,177 | 31% |
Applied to the top-1000 blank mix (29,931 blanks): 9,166-9,615 not applicable (31-32%). Sector-template part = blanks x (family rate minus the 23% corporate baseline): bank 1,424 + deposit takers 264 + insurers 1,135 + REIT 530 + asset managers 100 + agents 38 = **3,491 (11.7%)**. The other ~20 points are population gating and math conditions (non-payer dividend rows, BDC/net-lease rows against every company, PEG on negative growth), fixed by gating, not by templates.
Population-wide (data-team/30, 10-19, 82-metric registry, 92,132 non-gated blank rows): bank 6,440 of 9,046 (71%), insurer 1,910 of 2,998 (64%), REIT/real-estate about 2,600 of 6,757, lender/broker about 800-1,000, pre-revenue 2,000-3,300 (ASSUMED) = **14-15k, about 15-17%** from templates. Not counted: J-family lines simply not presented (needs per-filing evidence).
**Not measured:** the exact share of today's blank cells that are face-absent. Run when the pooler is <= 14 connections: join `analytics.company_data_point_coverage` (has_value, gap_reason; remember `coverage_matrix.py:746` any-period overcount) to the cik -> family file in `cls.json` and the face flags for the 33 concepts; report by family. FSDS face evidence is available for 4,936 filers now.

## 5. Which families need their own concept set, and the minimal template set
Own concept set: bank, insurer, BDC/fund, mortgage REIT. Small add-on: equity REIT (rental revenue, real estate at cost, secured debt). Overlay using existing concepts plus three new (short-term investments, accumulated deficit, equity proceeds): pre-revenue. No new set: utilities, energy, MLP, real-estate operators, lenders, agents (vocabulary and per-filing issues; MLP needs `PartnersCapital` in the equity vocabulary, EPD/S017).
Ranking by cells a template classifies (structural cells at the 20% threshold across the 33 concepts + 17 metric rows; top-1000 blank mass):
| Rank | Template | Structural cells (population) | Top-1000 evidence |
|---|---|---|---|
| 1 | Bank (add evidence-based deposit takers) | 4,634 | 42 banks + 10 deposit takers, 2,825 blanks, 73-85% not applicable |
| 2 | Insurer | 1,440 | 54 companies, 2,768 blanks (9.2%), 64% not applicable |
| 3 | Pre-revenue / no-revenue / exploration overlay | 3,782 | 4 companies; large in the full population |
| 4 | REIT (equity + mortgage) | 2,135 | 55 companies, 2,725 blanks; sample only 2 companies |
| 5 | BDC / investment company | 4,656 | 2 companies; matters for the full population and the wrong-denominator issue |
Order for the top-1000 launch: bank, insurer, REIT, then population gating (the 20-point item, cheapest), then pre-revenue and BDC. Together 95% of family-structural cells; everything else needs the per-filing layer.

## 6. Method: evidence applicability per filing, not by SIC
Reason classes. **E1** face absence (filer's own statements, accession, statement, line). **E-M** definition rule: the line exists but the metric is meaningless for the family (bank FCF); needs a named accountant, never an automatic reason. **E2** math condition from verified values. **E3** history. **E4** filing text. A missing tag, SIC, or a vendor figure is never evidence (data-team/30 s3.0).
Per (filing, concept) state, computed from the filing's own presentation (FSDS `pre.txt` for the free bulk path, `R*.htm` for the golden checks):
1. **Face-presented, value held** = fine.
2. **Face-presented, value missing** = APPLICABLE-BUT-MISSING (mapping or derivation bug). Highest priority; the face tag is the lead (Popular-style partial lines need the calculation tree before they count).
3. **Face-presented as a combined line** (label joins two concepts, e.g. "accounts payable and accrued") = `combined`, never plain AP.
4. **Not on the face, filed in a note** (undimensioned fact exists in `num.txt` / our `core.fact`) = `not_presented_on_statements_disclosed_in_note`; value may be shown flagged, or derived.
5. **Not on the face, not filed anywhere** = NOT-REPORTED (E1 with accession). Only this state may be shown as "not applicable / not reported".
6. **Family rule decides meaning only for E-M**; the family comes from the shape signature (section 2), never SIC alone; a mixed company gets its family per fiscal year (effective-dated).
Controls: (a) identities gate the classification (net income IS vs CF 324/324 pass in Ritwik's PoC; Assets = L + E; revenue - cost = gross profit when both present); (b) a family is accepted only when >= 2 independent signals agree (e.g. deposits + loans + nonint expense); (c) E1 precision is audited by opening statements: data-team/30 reports 18% of `no_line_item_filed` cells showed the line, so E1 needs a stratified sample (30 filings per family) with zero false "absent" before it is displayed.
Storage: extend `analytics.company_filing_line_evidence` (lane B, `probe-filing-lines`) rather than a new table; add accession, fiscal year, statement, tag, custom flag, label, line order. Size (DATA-INFERRED): 578,803 face lines for 4,936 filers = about 117 lines per filing, about 50 MB per cross-section of latest 10-Ks; a 2015+ history of every 10-K is roughly 11 cross-sections, about 0.6 GB: a Data Engineer size pilot (doc 56 W2), streamed from the quarterly zips, not stored raw. This replaces the circular `has_inventory_company` / `has_accounts_receivable_company` / `has_accounts_payable_company` populations (membership = "has a fact", so a line we failed to map shrinks the denominator; role spec: never improve coverage by silently shrinking the denominator).
Coverage rule: report three denominators per concept and family: all companies in the family, face-presented, and APPLICABLE-BUT-MISSING. Coverage = held / face-presented; reasoned blank = state 5 plus E-M.

## 7. Risks and what I could not verify
- Detector precision unmeasured (3 filings opened); label regexes over-count (D&A at financials, receivable labels at lenders). FSDS covers 3 quarters only; Q2 fiscal-year filers are absent from the table.
- DB blank counts not refreshed (pooler 18-23); top-1000 NA rates rest on 129 companies, REITs on 2.
- "Not on the face" does not mean "not in XBRL" (notes). States 4 and 5 need `num.txt` or `core.fact` to separate.
- Bank revenue (NII + noninterest income), borrowings perimeter, FCF-not-meaningful and insurer ratios are proposals for the Standardization Lead and a named accountant, not decisions.
- The 20-point non-sector share depends on how the workers used `not_applicable`; formats differ across shards.

## 8. What would change my mind
- If DB intersection shows most face-absent cells are already filled from notes, the filer-variable bucket shrinks and templates become the main lever.
- If a 30-filing audit finds >0 false "absent" per family, E1 display waits on that family.

## 9. Exact next actions
1. Data Engineer: when pooler <= 14, run the family x concept blank intersection (section 4 last paragraph), and the FSDS `pre.txt` face-line size pilot.
2. Sector Analyst (next run): freeze cohorts (30 banks, 20 insurers, 20 REITs incl. 5 mortgage, 20 pre-revenue, 10 asset managers/brokers) from `cls.json`; open statements; produce the row diff; test E1 precision.
3. Standardization Lead + accountant: bank revenue, borrowings perimeter, FCF/D/E meaning rules, insurer loss ratio scope.
4. Lane B: gate `bdc_total_investment_income`, `net_lease_revenue` and dividend rows by evidence-based populations (the ~20-point item); extend `sector_applicability.py` to insurer and REIT only after the cohorts pass.

## Proposed ledger rows (not appended: task restricts writes)
| 2026-10-21 | Of 212,014 filer x (29 concepts + 17 metric rows) cells, 20.5% are not on the filer's own statements; 40% of those are family-structural, 60% filer-variable | A template layer cannot classify every blank; per-filing face evidence is the larger lever | FSDS 2025q3/q4/2026q1 pre.txt, 4,936 filers (DATA-INFERRED) |
| 2026-10-21 | Popular tags only a partial fee line ("Net fees") as RevenueFromContractWithCustomerExcludingAssessedTax; no total revenue line | A bank's revenue cannot be read from a revenue tag; use NII + noninterest income | Popular 0001193125-26-085756 R5 (FILING-CHECKED) |
| 2026-10-21 | has_inventory/AR/AP populations are defined by "has a fact" | Circular denominator; use face evidence | `coverage_matrix.py` POPULATION_QUERIES (code-read) |
