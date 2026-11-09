Branch verify/msft-hd-2026-11-01. Plain-language summary of VERIFY-MSFT-HD-2026-11-01.md (same branch), which has the full cell list.
Seed 20261101. 80 cells drawn (40 MSFT, 40 HD) from analytics.canonical_fact and analytics.cell_blank_reason. 156 SEC requests.

# MSFT and HD check: what I found (for Dhairya)

## In one paragraph

Every number we show for MSFT and HD that I checked is correct: **62 of 62 match the filing, none are wrong.** The problem is the blanks. **11 of the 18 blank cells I checked should not be blank,** because the filing clearly prints the number. My advice on the 17,981 cells held for the verifier: **do not release them yet.** They carry no stored numbers to check, and the reason they were held is wrong for at least one company.

## How I checked

For every cell I opened the original SEC filing (the 10-K or 10-Q page for that statement) on sec.gov and read the printed number for that period. I did not trust our database or the builder's code; the filing alone decides. For quarters we calculate ourselves (full year minus nine months), I opened both filings and redid the subtraction.

## 1. The numbers we show: all correct

| Family | Checked | Right | Wrong |
|---|---|---|---|
| Income statement (revenue, cost of revenue, gross profit, operating income, net income) | 37 | 37 | 0 |
| Capex and cash | 25 | 25 | 0 |
| **Total** | **62** | **62** | **0** |

That covers yearly values, quarterly values, calculated fourth quarters and cash balances, for both companies from 2014 to 2026.

**Not tested:** we show no D&A or debt values for MSFT or HD, so I could not check those.

## 2. Blanks that should have a number (11, plus 5 extra)

A blank is fine only when the filing really has no number. These ones do have a number.

**a) HD depreciation and amortization (5 cells).** These are held because "D&A is made of several lines". That is not true for HD before 2025: its cash-flow statement prints **one** D&A line. Examples ($ millions): Q1 2016 = 486, full year 2020 = 2,519, Q1 2024 = 837. All 63 HD D&A cells carry this same wrong reason. HD really does print two lines only from FY2025.

**b) MSFT restated years (3 cells).** In 2018 Microsoft restated 2016 and 2017 for a new revenue accounting rule. Our system saw two different numbers for the same period and left the cell blank. Our own rule (decision register, 2026-11-01, rule 3) says to **use the latest printed number** instead. Values ($ millions):
- FY2016 net income: **20,539** (FY2018 10-K; originally 16,798)
- Q4 FY2017 operating income: **7,682** (FY2018 10-K; originally 5,330)
- Q4 FY2014 gross profit: **15,749** (FY2015 10-K; originally 15,787)

**c) MSFT quarter ending 2026-09-30 (3 cells).** The reason says "no filing prints this period", but Microsoft filed this 10-Q on 2026-10-28, before our load. Values: net income 36,629, cost of revenue 29,720, cash 20,281. Our filing data set probably did not include it yet, so the reason text should say that.

**d) Extra check, outside the random sample (5 cells).** For the MSFT quarter ending 2016-09-30, revenue, cost of revenue, gross profit, operating income and net income are all blank with "no filing prints this period". The 10-Q for that quarter prints all five. This needs a look.

**Blanks that are correct (7):** all 6 MSFT D&A blanks are right, because Microsoft only prints a combined line "Depreciation, amortization, and other". The HD FY2025 D&A blank's reason is also accurate (two lines).

## 3. The 17,981 cells held for the verifier: my recommendation

What they are: about 10,300 D&A cells and 7,700 capex cells across 518 companies.

**Recommendation: do not release them as one batch.**
1. **There is nothing to check yet.** None of these cells stores a candidate number, so releasing them would publish numbers nobody has seen.
2. **The hold reason is partly wrong.** For HD it was set per company, not per filing, and caught many simple single-line cases. I only measured this for HD, so I don't know the share across all 518 companies.
3. **Suggested order:**
   1. The builder re-checks each held cell against its own filing (one line or several) and stores the candidate number with its source filing.
   2. A verifier checks about 15 cells per group. A group is released only if none are wrong.
   3. Start with the 158 D&A cells that tie to the income statement (the safest group).
   4. Leave multi-line capex last. What counts as capex there is a definition question for the Standardization Lead, not the verifier.
4. My sample gives no evidence for releasing any held **capex** cell, because I did not draw one.

## 4. One more thing

The capex family's load run (rule_run 9f1a0908) has no finish time recorded, yet its cells are live. Please confirm that load completed.

## What to fix and re-check

| Fix | Then re-check |
|---|---|
| HD D&A: decide the hold per filing, not per company | the 5 HD cells above plus one FY2025 cell |
| MSFT restatements: use the latest printed number; read the 10-K "Quarterly Information" page for quarters | the 3 MSFT cells above, then all MSFT FY2016-FY2017 cells |
| "No filing prints this period" reason: fix it when the filing exists | MSFT 2016-09-30 and 2026-09-30 cells |
| Held cells: store candidate numbers, then run a verifier sample per group | before any release |
