# Why concept coverage is ~86%: an independent applicability probe (2026-10-13)

**Question:** the concept coverage score is 85.6% (mean over 78 concepts, each divided by all 4,815
real operating companies). How much of the missing 14.4 points is a line that does not exist for that
kind of company, and how much is a line we failed to extract?

**Why the existing data could not answer it:** 87% of absent cells in the 22 lowest concepts carry no
`gap_reason` (the classifier covers the revenue family only). Defining "applies to you" as "you have a
value" is circular (it would read 100%), so the evidence has to come from the filing itself.

## Method

`pipeline/scripts/applicability_probe.py` samples real operating companies uniformly within each of 12
sectors (22 per sector, seed 11), reads each company's latest 10-K/10-Q rendered balance sheet and
income statement (FilingSummary.xml -> R*.htm, the source the revenue parsers use) and checks whether a
row for the concept exists on the face of the statement. It also records whether our data has a value,
which gives a 2x2 per concept. Estimates are weighted by sector size to represent all 4,815 companies.
252 of 265 sampled companies were read (13 fetch errors). Nothing is stored; no yfinance.

Calibrated first on Apple, JPMorgan and Microsoft, which caught three matching bugs before the sample
(hidden "- Definition" popup rows read as lines, "Income Statements" titles not located, a section
heading read as a total).

## Result (share of companies with evidence)

| concept | ours has | lack, line IS in filing (extraction gap) | lack, no face line | noise* |
|---|---|---|---|---|
| inventory | 49.9% | 0.4% | 49.8% | 14% |
| goodwill | 65.3% | 0.0% | 34.7% | 16% |
| gross_profit | 51.3% | 0.0% | 48.7% | 22% |
| research_and_development | 44.0% | 0.0% | 56.0% | 24% |
| cost_of_revenue | 58.9% | 4.4% | 36.8% | 18% |
| accounts_receivable | 68.7% | 7.2% | 24.2% | 18% |
| operating_expenses | 59.5% | 9.7% | 30.8% | 20% |
| accounts_payable | 68.4% | 19.1% | 12.5% | 0% |
| interest_income | 42.0% | 26.5% | 31.5% | 34% |

\*noise = how often we HAVE a value although its line is absent from the face statement (disclosed only
in the notes, or a label miss). Absence from the face statement is therefore evidence, not proof, that a
line does not apply.

## What it says

1. **Most of the shortfall for inventory, goodwill, gross profit, R&D and cost of revenue is a line the
   company does not present** (extraction gap 0-4%). It is not a data failure, and it is concentrated in
   Financials, Real Estate and "Other" (e.g. 92% of Financials lack inventory; JPMorgan's own statements
   have no inventory, cost-of-revenue, gross-profit or R&D line).
2. **The real extraction gaps are interest income, accounts payable, operating expenses, accounts
   receivable, cost of revenue** (in that order), but the headline figures overstate them:
   - `accounts_payable`: ~35 of the 56 hits are COMBINED lines ("Accounts payable and accrued
     expenses/liabilities"). Mapping those as `accounts_payable` is the known "different concept sharing
     vocabulary" trap. Plain AP misses are ~8 of 56 (about 3% of companies).
   - `interest_income`: about half are plain "Interest income" (worth mapping); the rest are bank/insurer
     variants ("Interest and dividend income", "Investment income").
3. **A sector-keyed "does not apply" rule is statistically thin** at this sample size (about 10-20
   companies per sector-concept cell), and a company-level SIC rule was already shown wrong for
   universally-reported concepts (doc 50 Phase 3: the real pattern there is period-conditional). The
   sturdier design is per-company evidence: store, for every active company, whether each concept's line
   appears in its latest filing (with the label and accession, so it is traceable). Then
   "lack + no line" is a documented structural absence and "lack + line present" is a precise worklist.
   Cost: one pass of ~4 SEC requests per company (about 50 minutes at the shared rate limit), then an
   incremental update for companies with new filings.

## Caveats

Sample error is roughly +/-3-4 points overall and wider per sector. Label patterns are per-concept
regexes; the `accounts_receivable` and `interest_income` patterns are the loosest. Only the face of the
balance sheet and income statement is read, so cash-flow and note-only concepts are not covered.

Reproduce: `uv run python pipeline/scripts/applicability_probe.py --per-sector 22 --seed 11 --out /tmp/p.json`
