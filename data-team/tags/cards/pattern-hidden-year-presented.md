# Patterns P05 and P06: a hidden year that a filing presents
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Found 2026-11-22 by the verifier (WMT). Registry: `patterns.csv` P05, P06. Hits: `pattern_hits.csv` (FSN, `--live`).

**What.** A cell is hidden (HIDDEN_YEAR or HIDDEN_ROW) at a period that a filing presents.
- **P06:** the year's own 10-K presents the row's element for that year. Example: WMT other income FY2015.
- **P05:** no own 10-K presents it, but a later 10-K or 10-Q prints the period as a comparative column. Example: WMT shares_outstanding at 2024-01-31, printed in a 10-Q balance sheet.

Doc 02 says a year a filing prints is never hidden: a printed value or dash must be shown.

**How to detect.** `pattern_detectors.p05_p06_hidden_presented`. For every hidden export cell, FSN undimensioned facts of the row's own elements are read from every periodic filing (10-K and 10-Q) at the cell's period, within 7 days and at the right qtrs. The row's own elements are single-element role alternatives the resolver has served alone for that data point somewhere. A part of a sum, or a combined line, is not the row presented.

**Rule.** The verifier's `check_hidden_years` and `check_hidden_rows` fail these cells, and the flow self-check now opens them before gate_ready. For the resolver, `comparative_fill` already covers later 10-Ks. Open for .90: (a) a 10-Q balance-sheet comparative fills an instant year-end; (b) a hide class on a year the own 10-K presents needs a filing read that names the combined line.

**Examples.** WMT shares_outstanding FY2024 (P05), ORCL cost_of_revenue FY2015-16 (P06, CostOfServices), MSFT interest_income FY2018 (P06, InvestmentIncomeNet: check whether the line is combined).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 2 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `CostOfServices`
- **Meaning:** Cost of Services (Deprecated 2018-01-31) (us-gaap, duration, debit). Total costs related to services rendered by an entity during the reporting period.
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#6
- **Rules:** I02; I03; I04
- **Evidence:** 8 companies, 30 served, 19 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 4 open hit(s) at 1 companies, e.g. ORCL cost_of_revenue 2015-05-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (4)
- **Deprecation:** replaced by CostOfGoodsAndServicesSold@2018; [ServiceMember@2018; srt:ProductOrServiceAxis]@2018

### `InvestmentIncomeNet`
- **Meaning:** Investment Income, Net (us-gaap, duration, credit). Amount after accretion (amortization) of discount (premium), and investment expense, of interest income and dividend income on nonoperating securities.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).
- **Data point:** interest_income; polarity interest_income:signed; role interest_income:primary#6
- **Rules:** X93; I27; I26; resolver functions apply_label_beyond
- **Evidence:** 9 companies, 26 served, 119 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 6 open hit(s) at 3 companies, e.g. AMAT interest_income 2021-10-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 58 open hit(s) at 8 companies, e.g. AMAT interest_income 2023-10-29 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (58); P05 (6)
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToInvestmentIncomeNet@2013; CashFlowHedgeGainReclassifiedToInvestmentIncome@2013; CashFlowHedgeLossReclassifiedToInvestmentIncome@2013
<!-- END GENERATED: tag library rows -->
