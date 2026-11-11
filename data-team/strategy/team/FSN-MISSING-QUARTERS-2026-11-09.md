# "Older filings missing from the FSN store": causes, and the fix for one of them (2026-11-09)

For Dhairya. Branch `work/fsn/month-end-match`.

Evidence comes from two sources:
- read-only queries on production `fsn.*`;
- AT&T and PG&E reproduced on a local scratch database from the SEC FSN sets.

No production write. No new SEC requests.

## Finding: the filings are in the store

The queue item suspected that shard or load dropped filings (period floor, form filter, amendments). For the examples I checked, they did not:

- AT&T (CIK 732717): production `fsn.filing` holds every 10-Q and 10-K from 2016 to 2018, including the FY2017 10-K `0000732717-18-000009`.
- PG&E (CIK 1004980): the same, including the FY2016 10-K `0001004980-17-000006`.
- Kroger (CIK 56873): its Q2 FY2015 10-Q `0001104659-15-066444` is stored. It prints the 12-week Q2 revenue of 25,539M.

The gaps come from two other causes.

## (a) Q4 for every data point at once: the latest copy of the FY column fails a check

Reproduced on AT&T and PG&E with main's code.

**AT&T FY2017.**
- Revenue Q1–Q3 2017 are valued. FY2017 is a `latest_copy_fails_identity` blank.
- The latest filing that prints the FY2017 income statement is the FY2019 10-K `0001562762-20-000064`. In its 2017 column, the calc check `NonoperatingIncomeExpense` fails: the sum of the children is −4,831M, the printed total is −4,575M.
- select never falls back to an older copy, so the whole FY2017 income-statement column is blank. Q4 = FY − 9M cannot be derived for any income-statement data point: revenue, net income, EPS and the rest at once.

**PG&E FY2016.** The latest copy is the FY2018 10-K `0001004980-19-000004`. Its 2016 column fails `NetIncomeLossAvailableToCommonStockholdersBasic` (1,393M against 1,407M), so FY2016 and Q4 2016 are blank.

**What this means.** One failing subtotal blanks every line of that statement column, even lines the failing check does not touch. Revenue is not part of either failing calc.

**A fix needs a ruling.** One option is to blank only the concepts on the failing calc and their ancestors. That changes done criterion 3 / select's "latest copy fails identity" rule, so I have not changed it. I can build it once the approver rules.

**Still to do.** Count how many of the 115 companies / 214 company-quarters are cause (a). That needs the gap list from the run you measured. Send the artifact or run id. The test per key is simple: is the Q4 gap's FY cell a `latest_copy_fails_identity` blank?

## (b) Q1–Q3 on 52/53-week and 12/16-week calendars: FSN rounds dates to month ends (fixed)

In the SEC FSN sets, `num.ddate` is the period end **rounded to the nearest month end**.

- Kroger's Q2 FY2015 (12 weeks to 2015-08-15) is stored at ddate 2015-07-31.
- The expected-period calendar has the true end, 2015-08-15.
- The pilot matched a key only within ±10 days. 15 days apart, the key read as a gap, though the value is stored.

The cell loader binds FSN rows by fiscal label with the end within 10 days. The same row would therefore have been rejected as `period_unresolvable` on write. It would not have produced a wrong value, but it would have been missing.

**Fix.** `common/fsn_dates.fsn_end_matches(fsn_end, true_end)` accepts an FSN end within 10 days, or one equal to the SEC rounding of the true end (the nearest month end; both on a tie). It is used:
- in `pilot._match`, which the gap accounting and the C2 hold guard use;
- in `cell_loader.bind_periods`, still gated by the same fiscal year, fiscal period and period type.

An FSN date for a neighbouring month (for example Kroger Q2 against 2015-08-31) still does not match.

**Reach in the cohort gaps.** The cohort `gaps.csv` has 1,782 gap keys whose true end is more than 10 days from a month end. They sit at 10 companies:

| Company | Gap keys |
|---|---|
| PepsiCo | 330 |
| Costco | 330 |
| Domino's | 308 |
| AutoZone | 308 |
| Kroger | 264 |
| Yum | 66 |
| Albertsons | 66 |
| CAVA | 66 |
| Royalty Pharma | 22 |
| Allegro | 22 |

Of these, 1,458 are `quarter_not_printed_or_derivable` or `no_face_print_for_period`, the kinds this fix can free. The rest are mapping causes. The next cohort dry run measures the actual freed count.

**Not explained yet.** Kroger also misses its Q4 (late January) for FY2014–FY2021, but not from FY2022 on. Q4 is 1 day from its FSN date, so rounding is not the cause. The store holds both the FY and the 40-week year-to-date values. This needs Kroger rebuilt locally from the SEC sets, about 50 zip requests. I have not done that yet.

## Not covered

- Broadcom's quarters end near a month end, so its gaps have another cause. It is not in the cohort `gaps.csv` set I have.
- The 91 companies missing exactly one quarter need the gap list.
- The CAD filers IMO and CP wait for the founder's currency ruling.

## Tests

`pipeline/tests/unit/test_fsn_month_end_match.py`:

- nearest month ends: Kroger Q2/Q3/Q4, a PepsiCo-style Q2, a tie, and a February case;
- the match accepts the rounding and rejects a neighbouring month;
- `pilot._match` finds the rounded quarter;
- the loader binds Kroger's Q2 FSN row (2015-07-31) to the true `core.period` (2015-05-24 to 2015-08-15). This test is DB-backed.

Mutation-checked: the pilot match without the rounding fails, and the loader binding without it fails.

Full suite the way CI runs it: 2,382 passed, 1 skipped.
