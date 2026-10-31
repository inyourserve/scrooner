# VERIFY: cell proof, first-10 run v2 (2026-11-04)
Branch work/engineering/cell-proof 2d233e8, data-team/43-cell-proof/first10-cells.jsonl.gz (12,143 cells). Seed 20261104: 20 PROVEN, 10 DISAGREE, plus the 4 shown-differs cells at MSFT/HD. Verifier 2 (scrooner-bc). 87 SEC requests.

## Result
- **PROVEN: 0 of 20 wrong values. 4 of 20 wrong location ("printed line on the face").** All 20 shown values match a number in the cited filing. In 4 of them the statement has no column for that period, and the number is printed elsewhere:
  - HD net income Q4 FY2016 (1,744) and HD net sales Q2 FY2017 (28,108) are in the Quarterly Financial Data note of 10-Ks 0000354950-17-000005 and -19-000010.
  - GOOGL capex Q2 2015 (2,515) is in the segment capex note of 10-Q 0001652044-16-000032, whose cash flow statement shows six months only.
  - NVDA dividends Q2 FY2019 (91) is in the MD&A text of 10-Q 0001045810-18-000114, whose cash flow statement shows six months only.
- **DISAGREE: 0 of 10 real.** In every cell, shown equals the printed statement line, and the statement's own arithmetic ties:
  - PG Q3 2022 operating income: 20,612 - 10,846 - 4,827 = 4,939.
  - AMZN FY2017 CFO: the 11 printed items sum to 18,365.
  - META pre-tax income FY2017/FY2019/FY2022 and META Q2 2026 operating income tie, as do GOOGL Q2 2019 net income and FY2021 pre-tax ("Total" 90,734).
  - AMZN net income FY2017 (3,806 - 769 - 4) and Q2 2026 (80,857 - 18,199 - 11) tie.
  - The `components_sum` check (8 of the 10) and `only_a_component_line_presented` (2) both raised false alarms here.
- **Shown-differs, 4 of 4 real.** Each shown value is the ORIGINAL filing's figure, credited to a later accession whose face prints the restated one (basis `latest`):

| Cell | Shown (original 10-K) | Face of credited accession |
|---|---|---|
| MSFT total assets 2016-06-30 | 193,694 (0001193125-16-662209) | 193,468 (0001564590-17-014900) |
| MSFT total liabilities 2016-06-30 | 121,697 (same) | 121,471 (same) |
| MSFT current liabilities 2015-06-30 | 49,858 (0001193125-15-272806) | 49,647 (0001193125-16-662209) |
| HD current liabilities 2016-01-31 | 12,526 (0000354950-16-000060) | 12,524 (0000354950-17-000005) |

## Findings for the builder
1. Proof: a FSN `pre` statement line plus any `num` value for that tag and date is not "printed on the face". Require the period (qtrs) to be a column of that statement. Otherwise label the cell NOTE-PROVEN, not PROVEN. Re-verify by drawing 20 PROVEN Q cells taken from 10-K and from 10-Q cash flow statements.
2. `components_sum`: false on 8 of 8 drawn. Likely causes: META's SBC rows parented under the totals, the sign of tax and equity-method lines, and unrelated children. Recheck the custom-parent rule against these 8 accessions before trusting any DISAGREE from it.
3. Production, latest basis: these balance-sheet cells keep the original value but cite the restating filing. Either show the restated face value or cite the original accession. Re-verify all 16 shown-differs cells (KO restricted cash 6, AAPL 2, FB 2, AMZN 1, NVDA 1 are not checked here).

## Untested scope
UNCHECKED (2,847) and NOT_PRESENTED (805) were not drawn. 12 of the 16 shown-differs cells were not checked.
