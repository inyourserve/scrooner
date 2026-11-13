# Era predictions (top 110, FY2015 to FY-2)

These are predictor runs over the earlier 10-Ks of the top-110 cohort companies (ranks 1-110 in data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv). They are candidates for Engineering's tag-switch gaps. A row is served only if proof marks it PROVEN.

- **Files:** `<TICKER>-<accession>-prediction.csv`, one per 10-K. 938 filings, 105 companies; 5 of the 110 have no 10-K in the window.
- **Columns:**
  - The same columns as the FY0 predictions.
  - `fy0_value` is that filing's own fiscal-year value.
  - `period` is the filing's balance-sheet date.
  - `rules_commit` is the commit of data-team/tags/rules and exam/tools/predict.py used for the run.
- **Window:** every 10-K with period on or after 2015-01-01, except each company's latest two (FY0 and FY-1).
- **Inputs:** all from FSN in the database, read-only. No SEC requests were made for this run.
  - Face lines: `tools/render_sql.py tools/LINES.sql --eras <CIKS>` (or `--accession <ACC,...>`).
  - Note facts: NOTES.sql, the same way.
  - Location slices: LOCATION.sql, the same way.
- **Engine:** `tools/predict.py LINES.jsonl TICKER RANK ../../rules NOTES.jsonl --accession <ACC>`. The `--accession` filter keeps only that filing's lines and note facts. FY0 output is unchanged with or without it.
- **Instance-fed inputs** (regenerated 2026-11-13): exam/tools/fetch_era_instances.py read each era filing's XBRL instance from sec.gov at no more than 3 requests per second, plus the calculation linkbase where capital leases appear. exam/tools/build_era_notes.py turns the reads into the notes fields. 937 of 938 instances read; one had no index.
  - `fl_loc` (where the finance leases sit on the balance sheet). For ASC 842 filings it comes from FinanceLeaseLiability*StatementOfFinancialPositionExtensibleList. Before ASC 842 (FY2015-FY2018) it comes from the calculation-linkbase parent of CapitalLeaseObligations*: a debt total means in; other liabilities, accrued liabilities or accounts payable means out. Counts: in 113, out 39, none 785.
  - `debt_series`: per-series interest. It appears in 7 filings, and in each a face interest total exists, so the rule stands down.
  - Capital-lease facts were added to the note facts for 112 filings. The total_debt lease guards apply to capital lease obligations exactly as to finance leases (bs.total_debt.finance_leases v2).
- **Limit:** the prior-era label (`prior`) is the tag of the same printed label in the 10-K about four years before each filing.
