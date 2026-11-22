# Pattern P07: one printed line serving two data points
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Found 2026-11-22 by the verifier. Registry: `patterns.csv` P07. Hits: `pattern_hits.csv` P07.

**What.** The same printed line (filing, period, element, members, R page:line) is the value or a summed part of two served data points that are neither the same figure by definition nor a total and its part. The printed number is then counted twice. Examples: COST FY2022 `SellingGeneralAndAdministrativeExpense` is served alone as both sga_expense and operating_expenses; DE interest expense sits inside an operating-expense sum.

**How to detect.** `pattern_detectors.p07_line_double_count`, over `mapped` and `component_sum` resolver rows. Derived rows and differences (a node with a leading `-`) are excluded, because a computation may reuse its inputs. A shared line is allowed only for:
- `SAME_FIGURE` pairs: interest_income and total_interest_income; noninterest_expense and operating_expenses at banks.
- basic and diluted EPS or shares on a `BasicAndDiluted` line.
- a `CONTAINS` total and its part, such as operating_expenses and sga_expense, when the total is a sum.

**Rule (X130, resolver .91).** One printed line serves one data point outside those pairs. Where the face prints only one operating line (WMT "Operating, selling, general and administrative expenses"), the line is a combined value with a badge (X113) for one data point, and the other data point is combined.

**Examples.** WMT, ADP and COST operating_expenses + sga_expense; DE interest_expense + operating_expenses.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 1 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `SellingGeneralAndAdministrativeExpense`
- **Meaning:** Selling, General and Administrative Expense (us-gaap, duration, debit). The aggregate total costs related to selling a firm's product and services, as well as all other general and administrative expenses. Direct selling expenses (for example, credit, warranty, and advertising) are expenses that can be directly...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; sga_expense: Selling, general and administrative expense for the period.
- **Data point:** sga_expense; operating_expenses; polarity sga_expense:positive; role sga_expense:primary#1
- **Rules:** I15; I16; I17; I18; family resolve_all.NARROW[sga_expense]
- **Evidence:** 66 companies, 1140 served, 3623 proven, 85 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RelatedPartyTransactionSellingGeneralAndAdministrativeExpensesFromTransactionsWithRelatedParty@2023
<!-- END GENERATED: tag library rows -->
