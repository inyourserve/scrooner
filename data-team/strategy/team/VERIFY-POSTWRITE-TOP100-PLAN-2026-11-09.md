Prepared for: top-100 FSN production write, run 42649721096 (15 data points). Answer key built BEFORE the write; canonical_fact was not read.
Seed 20261109. SEC requests: 1,415 (sec.gov only, <= 3.4/s, the repo's declared User-Agent). Verifier session scrooner-c3. DB: read-only lookups on core.filing only.

# Post-write Verifier check, top 100: plan and answer key (2026-11-09)

## What is ready

`results/verify-postwrite-top100-2026-11-09/answer_key.csv` holds **200 cells across 100 companies** (the top 100 of `data/cohort_v1_1_proposal_2026-10-24.csv`), all 15 data points:

| data point | cells | | grain | cells |
|---|---|---|---|---|
| gross_profit | 17 | | FY | 102 |
| dividends_paid | 17 | | Q (printed 3-month, or CF quarter) | 78 |
| net_income, operating_income, cost_of_revenue | 14 each | | QD (derived Q4 = FY − 9M) | 20 |
| revenue, income_tax, cfo, eps_diluted, dps, shares_outstanding | 13 each | | | |
| pretax_income, interest_expense | 12 each | | | |
| eps_basic, share_buybacks | 11 each | | | |

| expected state | cells |
|---|---|
| value | 141 |
| value, definition to confirm (shares outstanding) | 12 |
| blank with an expected reason | 46 |
| drop (draw artefact) | 1 |

## How the draw was made

1. Each company gets 2 data points by rotation, `(rank × 2 + k) mod 15`, so all 15 points are covered about evenly.
2. Eight blank candidates were steered on purpose: gross profit at JPM, BAC, WFC and GS; dividends at AMZN, TSLA, NFLX and CRWD.
3. The grain comes from md5('20261109:'+cik+':'+k): EPS, DPS and shares are 90% FY / 10% Q; the rest are 44% FY, 37% Q and 19% QD.
4. The period is a seeded pick among the company's 10-K / 10-Q in `core.filing` (2015–2025).
5. **XOM:** its pre-2026 history is not in `core.filing`, so its 2 cells (EPS basic Q2 2020, EPS diluted Q1 2024) were added by hand from 10-Qs filed under CIK 0000034088. That gap in core.filing is itself worth fixing.

## How each expected value was read

The expected value follows decision 02 rule 3 (latest print wins). For each cell I read the period's own filing and its later copies (the next two 10-Ks for FY, the next-year same-quarter 10-Q for Q) from the filing's own R pages (Statements). Rows are matched by XBRL tag; columns by end date (±7 days) and duration.

- **`expected`:** the value in the latest copy that prints the column. `original` is the period's own filing, and `copies` lists every copy read.
- **Derived Q4 (QD):** FY − 9M, each taken from its latest copy (`expected_from` shows both inputs).
- **Cash-flow quarters:** 3M where printed (Q1); otherwise YTD minus the prior YTD.
- **Scale:** money values are scaled by the page header. EPS and DPS are per share. Shares use the "shares in …" header.

**Tag lists per data point** are in `tools/akey.py` (TAGS). Revenue, for example: Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet, RevenuesNetOfInterestExpense, ….

**Hand corrections made while building:**
- P&G pretax uses the plain `IncomeLossFromContinuingOperationsBeforeIncomeTaxes`; that tag was added.
- Progressive presents on a "Comprehensive Income" statement; a fallback was added.
- Caterpillar FY2020 DPS of 4.12 is taken from the equity statement (row layout, read by hand).
- T-Mobile cost of revenue: the face prints "Cost of services" + "Cost of equipment sales" with no total, so the expected state is blank. The reader's 11,497M was a component.
- Chevron buybacks: only "Net sales (purchases) of treasury shares" (a net line), so the expected state is blank.

## Expected blanks (46) and their reasons

| reason | cells |
|---|---|
| gross profit not printed (MA, ORCL, RTX, ABT, TMUS, T, ACN, SPGI, MDT, GE) | 10 |
| no dividend paid (AMZN, META, TSLA, PLTR, NFLX ×2, CRWD, AMD) | 8 |
| interest expense not on the face (MSFT, PM, ANET, SCCO, ETN, INTC Q4, NEM Q4): note-sourced value or template OUT | 7 |
| bank, no gross profit / cost of revenue (JPM, BAC, WFC, GS, SCHW) | 5 |
| no dividend declared (DELL, SNDK, NOW, VRTX) | 4 |
| operating income not printed (LLY, AXP, PH) | 3 |
| no buyback line (AMD 2015, SHOP 2025, NEE Q3 2025) | 3 |
| DPS not on the statements (AVGO, TJX): note-sourced | 2 |
| cost-of-revenue total not printed (ORCL, TMUS) | 2 |
| net line only (CVX) | 1 |
| unclassified, hand-check (CAT shares Q3 2022) | 1 |

A blank cell in the store is right only if its reason agrees. A **value** where the key expects a blank is checked by hand: it may be note-sourced, which is acceptable if the line is the concept.

## Grading procedure, once Dhairya says the write finished

1. Read `analytics.canonical_fact` and `analytics.cell_blank_reason` for the 200 keys (one connection, statement_timeout; period matched within ±10 days).
2. **Value cells:** the store value must equal `expected` within half the printed rounding unit. For a mismatch, re-open the filing and decide: store wrong, key wrong (fix the key and say so), or a basis difference (e.g. the original vs the latest copy, recorded in `original` / `copies`).
3. **Blank cells:** the state and reason must agree with `blank_reason_expected`. A store value there gets a hand check (note-sourced or wrong).
4. **Shares outstanding (12 + CAT):** grade against the definition the store uses. The key records both the period-end balance-sheet parenthetical (`expected`) and the own filing's cover-page dei count with its date (`note`). Visa is multi-class.
5. **cell_proof first:** compare its verdicts with this key. Cells where cell_proof says "proved" and the key disagrees are reported first.
6. **Report:** N of N right, the wrong cells with accession and page, avoidable holds, and false holds. Gate: zero wrong shown values.

## Known limits of the key

- The reader matches by tag, not by label. A company that tags its total with an unlisted tag may show as a blank in the key; every key blank is re-checked at grading if the store has a value.
- The equity-statement DPS layout (row-wise periods) is not parsed automatically. Only CAT was found and fixed by hand.
- GE QD 2015-02-27 is a draw artefact (core.filing gives that period_of_report for a 10-K). It is marked `drop`.
