# 41. Template-driven coverage: how "100% coverage, 100% moat" is defined, measured and reached (Ritwik, 2026-10-21)

Founder direction (2026-10-21): "I want data coverage 100% and data moat 100%. Group companies by metric, use different templates for groups (sectors, industries, whatever). Why report blanks?"
This document makes that the backbone of the program. It reorganizes doc 40 (which stays as the evidence base and defect-closing plan); where they conflict, this one wins. Evidence: R4 (sector applicability), R2/R3 (tag and composition patterns), R8 (Chief). Labels: FILING-CHECKED / DATA-INFERRED / ASSUMED. Nothing here is built or approved; accounting definitions are proposals.

## 1. The model in one paragraph
Every company belongs to one **group** (bank, insurer, equity REIT, corporate, ...). Every group has one **template**: the exact list of metrics and statement lines that make sense for that kind of business, with each group's own definitions where the standard ones do not fit (a bank's revenue is not an industrial's revenue). The company page and the screener show **only** the cells in the company's template. There is no grid of metrics with holes in it. **Coverage = certified template cells / template cells.** 100% means every cell the template promises carries a value that traces to a filing and passed the checks. Moat 100% means every shown number has a source link, a formula version and a certification state (data-team/34).

## 2. Why we still keep an internal defect list (and no user-facing blank report)
Users never see a blank grid. But a number nobody counts never gets fixed. So engineering keeps one internal list, the **defect register**: template cells that do not yet hold a certified value, each with a class and an owner (vocabulary, perimeter, period, ingestion, resolver, evidence). The goal is that list reaching zero. It replaces today's "81.4% filled, 44.6% of blanks unexplained" reporting, which counts cells that are not supposed to exist.

## 3. Where a template can legitimately end in something other than a number
Honest limit, stated up front: a filer sometimes does not disclose a line a metric needs. Four ways a template cell resolves, in order:
1. **Reported value**: a mapped tag, or a candidate verified by the structural check, with the filing locator.
2. **Derived value** from identities or components the filing does report (gross profit = revenue - cost; Q4 = FY - 9M only under the additive allowlist).
3. **Evidenced zero**: the filing shows no such activity (no borrowings, no dividends paid, no buybacks in the period), recorded as 0 or "None", with locator. This is a value.
4. **"Not disclosed by this company"**: the Verifier opened the filing and the line is not presented or filed anywhere. This is the one visible non-number, shown with the filing link. It counts as covered only with that evidence and should be rare (target well under 0.5% of template cells, ASSUMED); a template metric that is not disclosed by most members of a group is a bad template and gets redefined, not tolerated.
Anything else is a defect and blocks "certified" for that company.
This is consistent with the Chief's rule: a denominator never shrinks without filing evidence. Group membership is the evidence; state 4 requires a Verifier check; nothing is hidden by assumption.

## 4. How groups are decided (the part that must be right)
- **By the filer's own statement shape, not SIC alone** (SIC 6211/6282 hold fund vehicles; SIC 6000-6199 hold crypto miners and fintech). Signature = which lines the face statements present: deposits and net interest income (bank); premiums earned and loss reserves (insurer); total investment income and net assets (BDC/fund); rental revenue and real estate at cost (REIT); no revenue line plus R&D or exploration (pre-revenue overlay).
- **Effective-dated per fiscal year**: a company moves groups in the first year its statements change (pre-revenue to commercial, thrift to bank holding company). History uses the template in force that year.
- **Audit gate**: 30 companies per group opened against their statements, zero wrong memberships, before the group's template cells are used in the denominator (R4 control, Chief K4).
- **Population (FSDS, 4,936 filers, DATA-INFERRED):** corporate 2,786 (base template; utilities 134 and energy 129 use it with vocabulary tweaks), banks 331, SPACs 279 (not screener companies), equity REITs 235, pre-revenue 218, BDC/fund 194, insurers 120, non-bank lenders 108, asset managers 87, mortgage REITs 35, brokers 33, MLPs 32, trusts 31, exploration 31. Minimal set of new templates covering 95% of family-structural cells: bank, insurer, REIT, BDC/fund, pre-revenue (R4, 16,647 of 17,520). Asset managers and brokers wait for a 30-company shape review.

## 5. Draft template contents (v1 proposal, from R4 section 3; product choices are mine to recommend, definitions need the accountant)
Cell rule codes: REQ required; REP replaced by a group definition; COND applies only when an evidenced condition holds; not listed = not in template.
| Group | Required core | Replaced / group-specific | Conditional | Not in template |
|---|---|---|---|---|
| Corporate (base; utilities, energy as variants) | revenue, cost of revenue (where presented), operating income, net income, EPS, CFO, capex, total assets, equity, cash, total debt, margins, ROE/ROIC, P/E, P/B, P/S, FCF yield, market cap | none | dividend metrics (COND: pays dividends; else evidenced zero), inventory/receivables chain (COND: line presented), R&D, goodwill | n/a |
| Bank / thrift | net income, EPS, ROE, P/B, P/E, market cap, total assets, equity, CFO | revenue = net interest income + noninterest income (REP, accountant); NII, noninterest income, efficiency ratio, equity/assets, loans/deposits, ROA | dividend yield (COND) | gross margin, operating margin, ROIC, current ratio, inventory, FCF family, interest coverage, EBITDA family (meaningless by definition) |
| Insurer | net income, EPS, ROE, P/B, P/E, market cap, total assets, equity | premiums earned, net investment income, losses and LAE, reserves; loss ratio (COND: P&C/health where both inputs exist) | dividend yield (COND) | gross margin, operating margin, current ratio, inventory, FCF family |
| Equity REIT | revenue, net income, EPS, ROE, P/B, total assets, debt, interest expense | G&A replaces SG&A; property operating expenses; capex per a REIT definition (REP, accountant); FFO/AFFO only if the filing presents it | operating income (COND: presented), dividend yield (COND) | current ratio, inventory, R&D, gross margin |
| Mortgage REIT | net income, EPS, book value per share, equity | interest income as revenue (REP), net interest spread, economic leverage | dividend yield | gross/operating margin, ROIC, coverage, current ratio |
| BDC / fund | net assets (NAV), net investment income, total investment income, distributions, P/NAV | total investment income replaces revenue (REP) | dividend yield | gross margin, current ratio, ROIC, FCF family |
| Pre-revenue overlay | cash and short-term investments, operating loss, R&D, cash burn, runway (only if the disclosed formula exists), accumulated deficit, dilution | accumulated deficit, equity proceeds (new concepts) | exits overlay in the first year it presents revenue | every revenue-denominated ratio |
| Non-screener (SPAC, pool trust, ABS) | one stated reason + trust assets | none | none | all |
The 18 V1 metrics are the starting inventory; the product keeps its ~18-metric guardrail per group's visible set (doc 02), so expanding a group's set is a decision, not drift.

## 6. How this changes the plan in doc 40
1. **Templates become the organizing structure**: the coverage grid, the certification state (data-team/34) and the screener all read the company's group and template. Everything else is defect-closing inside it.
2. **The 57% "applicability" blanks disappear by construction** for companies whose group is audited, because those cells are no longer in the template. The remaining 43% (vocabulary, perimeter, period, ingestion, resolver, unknown) are the defect register.
3. **Doc 40's ranks 1-10 are unchanged in content**; they now each carry the template group(s) whose cells they close. Rank 7 (sector suppression) is promoted to week 1 and widened from "suppress" to "define the template".
4. **Group-specific definitions need the accountant earlier**: bank revenue, REIT capex, insurer revenue composition. They are the same decisions as before, now with a visible deadline: a group cannot go to 100% without its replaced definitions approved.

## 7. The scoreboard (one table the founder sees weekly)
Per group: companies, template cells, certified cells, evidenced-zero cells, "not disclosed" cells (with Verifier evidence), defects by class, companies fully certified. Headline = certified template cells / template cells for the top 986 first, then 5,216. Report alongside it, on the fixed all-cells denominator (160,718 for the top 986), value-filled and current-and-not-stale cells, so denominator work cannot masquerade as progress (Chief fail-mode 1).

## 8. Build order (compatible with the R8 30-day plan)
1. Step 0: measured baseline (migrations 0096/0097, the four gap queries, certify dry-run). Capacity is no longer the blocker (Postgres max_connections 60, 15 in use, database 46 GB of a 60 GB plan, checked live 2026-10-21).
2. Week 1-2: shape signatures for the top 986; assign groups; 30-company audit for bank, insurer, REIT, pre-revenue; freeze template v1 for corporate, bank, insurer, REIT.
3. Week 2-4: measure template-cell baseline per group; close the first defect classes (total-debt, Q4 EPS, revenue total, split, interest expense, per-share pairing) group by group.
4. Day 31-90: BDC/fund, mortgage REIT, asset manager/broker; structure evidence layer for vocabulary and perimeter defects; accountant-gated replaced definitions; extend from 986 to 5,216.
5. Data model (proposal for the Data Engineer; extend, do not duplicate): a `company_group` assignment (company, group, effective period, evidence accession) and a `metric_template` (group, cell, rule, definition version), reusing `company_filing_line_evidence` (0093) and `common/sector_applicability.py` (serve-time bank suppression becomes template-driven for all groups).

## 9. What I cannot promise (so nobody is surprised)
- 100% is a destination. Transition states exist, with the defect register as the honest measure. I will not report 100% until the invariant suite, the independent reconciliation and the Verifier headline check pass for the cohort (data-team/34).
- Some value cells need an accountant's ruling before a number can be shown (bank revenue, REIT capex, finance leases in debt). Until then those cells are defects, not blanks.
- A filer-reported error remains a filer error; certification records it as a company-scoped exception.
- Template membership errors would hide real gaps. The 30-company audit per group and a quarterly re-audit are the control.
- All counts above are DATA-INFERRED projections from the SEC data sets and repo files; the measured baseline (step 0) replaces them.

## 10. Decisions for the founder
1. Approve the model: users see template cells only; internal defect register; the single visible "Not disclosed by this company" state, evidence-backed and rare.
2. Name the accounting reviewer (still the one human gate on replaced definitions).
3. Confirm the product set per group (section 5 is my recommendation; changes to the visible metric set per group are your call).
