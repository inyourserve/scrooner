# Pattern P07: one printed line serving two data points

Found 2026-11-22 by the verifier. Registry: `patterns.csv` P07. Hits: `pattern_hits.csv` P07.

**What.** The same printed line (filing, period, element, members, R page:line) is the value or a summed part of two served data points that are neither the same figure by definition nor a total and its part. The printed number is then counted twice. Examples: COST FY2022 `SellingGeneralAndAdministrativeExpense` is served alone as both sga_expense and operating_expenses; DE interest expense sits inside an operating-expense sum.

**How to detect.** `pattern_detectors.p07_line_double_count`, over `mapped` and `component_sum` resolver rows. Derived rows and differences (a node with a leading `-`) are excluded, because a computation may reuse its inputs. A shared line is allowed only for:
- `SAME_FIGURE` pairs: interest_income and total_interest_income; noninterest_expense and operating_expenses at banks.
- basic and diluted EPS or shares on a `BasicAndDiluted` line.
- a `CONTAINS` total and its part, such as operating_expenses and sga_expense, when the total is a sum.

**Rule (open, resolver .90).** One printed line serves one data point outside those pairs. Where the face prints only one operating line (WMT "Operating, selling, general and administrative expenses"), the line is a combined value with a badge (X113) for one data point, and the other data point is combined.

**Examples.** WMT, ADP and COST operating_expenses + sga_expense; DE interest_expense + operating_expenses.
