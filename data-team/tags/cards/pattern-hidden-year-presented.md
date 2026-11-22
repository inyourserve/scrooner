# Patterns P05 and P06: a hidden year that a filing presents

Found 2026-11-22 by the verifier (WMT). Registry: `patterns.csv` P05, P06. Hits: `pattern_hits.csv` (FSN, `--live`).

**What.** A cell is hidden (HIDDEN_YEAR or HIDDEN_ROW) at a period that a filing presents.
- **P06:** the year's own 10-K presents the row's element for that year. Example: WMT other income FY2015.
- **P05:** no own 10-K presents it, but a later 10-K or 10-Q prints the period as a comparative column. Example: WMT shares_outstanding at 2024-01-31, printed in a 10-Q balance sheet.

Doc 02 says a year a filing prints is never hidden: a printed value or dash must be shown.

**How to detect.** `pattern_detectors.p05_p06_hidden_presented`. For every hidden export cell, FSN undimensioned facts of the row's own elements are read from every periodic filing (10-K and 10-Q) at the cell's period, within 7 days and at the right qtrs. The row's own elements are single-element role alternatives the resolver has served alone for that data point somewhere. A part of a sum, or a combined line, is not the row presented.

**Rule.** The verifier's `check_hidden_years` and `check_hidden_rows` fail these cells, and the flow self-check now opens them before gate_ready. For the resolver, `comparative_fill` already covers later 10-Ks. Open for .90: (a) a 10-Q balance-sheet comparative fills an instant year-end; (b) a hide class on a year the own 10-K presents needs a filing read that names the combined line.

**Examples.** WMT shares_outstanding FY2024 (P05), ORCL cost_of_revenue FY2015-16 (P06, CostOfServices), MSFT interest_income FY2018 (P06, InvestmentIncomeNet: check whether the line is combined).
