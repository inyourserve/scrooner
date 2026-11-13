# line_map: the structural resolver, read-only (2026-11-13)

**Design.** `data-team/tags/STRUCTURAL-MAPPING.md`, approved as the direction (Dhairya 2026-11-13). Perimeters are unchanged.

**What it does.** For every top-110 10-K in FSN (1,243 filings, 109 companies; XOM's new CIK has no 10-K in FSN yet), it finds each data point's node:
- the face statement (FSN `line`, the report with the most valued lines);
- the filer's calc tree (`calc_arc`, the group that ties on the face);
- the own-column values (`value`: `ddate` = the period, `qtrs` 0 or 4, undimensioned, no co-registrant).

The tag only ranks nodes that already hold the role.

## Files
- `<TICKER>.csv`: one row per filing and data point. Columns: `status` (mapped, component_sum, derived, combined, no_role), `tags`, `value`, `lines` (R report:line), `path` (the structural evidence), `flag` (`hint_ranked`, `hint_only` or `DERIVED`) and `filing_checks` (the filer's own calc arithmetic on its own numbers).
- `tools/extract.sql`: the FSN query, read-only, five CIK batches.
- `tools/resolve.py`: the resolver.
- `tools/gate.py`: the backtest.
- `_gate-nonagree-2026-11-13.csv`: every comparison that is not an agreement.
- `_would-close-2026-11-13.csv`: non-PROVEN coverage cells where the resolver finds a node.

## Filer arithmetic
The filer's tree ties on its own numbers:
- **L&SE:** 1,234 of 1,240 balance sheets.
- **Change in cash:** 1,206 of 1,212 cash-flow statements.

The 12 failures are quarantine candidates.

## Gate (16 data points: BS totals, IS top-to-net lines, the three CF totals)
| Key | Agree | Disagree | Agreement where both resolved | Gap (no node) | Derived where the key says not_presented |
|---|---|---|---|---|---|
| Hand rows of the docmaps (`check: hand`) | 231 | 17 | 88.5% (93.1% without the 15 stale "combined" opex keys) | 12 | 13 |
| Other docmap FY0 rows | 1,276 | 4 | 98.6% | 47 | 14 |
| Reader fix files | 191 | 7 | 93.2% (99.5% without the 6 CAT "combined" opex keys) | 53 | 7 |
| Served PROVEN cells, own filing only | 10,426 | 40 | 99.62% | 573 | 0 |

**DERIVED values are not served.** They are candidates (total_liabilities when not printed), and serving them is a new perimeter, so it needs the founder's ruling.

## The disagreements
1. **Stale "combined" opex keys (21 rows, 16 companies).** The keys predate the S12/§AE ruling (opex = the tying face lines between COR/GP and OI). The resolver follows the ruling, as TMO's key does after the ruling.
   - Docmap rows: VLO, BLK, T, MCD, ORCL, SPGI, TMUS, VRTX, SBUX, UBER, SCCO, ACN, UNP, STX, CVS.
   - CAT fix rows: 2015–2019.
   - BLK, MCD, ORCL, SBUX and UNP have no cost-of-revenue line, so the printed total is the whole expense line; it should be checked whether that is opex.

   These need Dhairya's adjudication, not code.
2. **Served PROVEN cells that structure shows are wrong (19 cells it would fix):**
   - cost_of_revenue served as goods only while the filer's cost node also contains cost of services: RTX 2015–17, TMO 2017, VZ 2015–17, TMUS 2015–17. ORCL 2015–17 also differs, but ORCL prints no cost-of-revenue total, so it needs a reader.
   - CAT operating_expenses 2018–19 served at 46.4B/45.5B. That includes cost of goods sold; the founder's perimeter excludes it.
   - AVGO net_income FY2018 served as ProfitLoss 12,610M; the parent node is 12,259M.
3. **Perimeter question for the founder: oil-major revenue (15).** CVX keys use "total revenues and other income" (189,031M), but COP's docmap uses the sales line, and COP's served 2015–19 cells use the total. The resolver demotes the "and other income" total to the sales child (label demotes, never promotes). One rule is needed.
4. **Resolver defects still open (fix before Engineering wires it):**
   - AXP revenue 2018–22: it picks the custom "after provisions" node.
   - ORCL revenue 2024: wrong calc group.
   - COF revenue: the bank shape is not found.
   - VLO cost of revenue: it went one level too deep (the 2020 value is off by 19M).
   - RTX opex: sign of OtherOperatingIncomeExpenseNet (8,489M vs 8,902M).
   - MO cost of revenue: OtherCostOfOperatingRevenue is dropped as a tax.

   Until these are fixed the gate is not at zero.
5. **Keys that conflict with each other:** VZ stockholders_equity 2025 (the docmap says not_presented, the fix file maps the total including NCI).

## What it would close
971 non-PROVEN cells in the coverage of `ae92a1b5`:
- HELD 241;
- UNCHECKED 447;
- BLANK 219;
- DISAGREE 16;
- REASON 48 where the resolver finds a node: these are conflicts to check.

These are structure-only candidates. Per the xbrl-structure rules they are never auto-published: they need a Verifier filing sample with zero wrong rows.

## total_debt (2026-11-13): `total_debt-2026-11-13.csv`
**Rule (`tools/total_debt.py`).** total_debt = every debt-role node under the BS liabilities (between the asset total and the equity section), deduplicated through the filer's calc tree, plus the lease nodes the filing locates outside those lines.
- **Debt-role nodes:** the face lines with a debt-role element, or a custom line whose label (or section header) names debt or borrowings. A node whose calc parent is also a debt node is inside that parent and is dropped.
- **Leases already inside a debt line:** a face line whose tag or label names leases (e.g. LongTermDebtAndCapitalLeaseObligations) already contains them, so nothing is added.
- **Note finance lease:** added when the ExtensibleList says it sits outside the debt lines. It is not added when the ExtensibleList, a calc arc, or a debt-note total that ties says it is inside.
- **No ExtensibleList and no containing line:** the note finance lease is added as "location by absence: CHECK". This is the MSFT pattern: finance leases sit in other liabilities. It applies in 34 replace/fill rows.
- **Pre-842 capital lease:** added when its calc parent on the face is not a debt line.

**Which copy.** The latest-filed copy: the next 10-K's comparative column, else the year's own 10-K.

**Backtest.**
- MSFT hand fix rows: **12 of 12**. Two years come from the next 10-K's comparative column (FY2016 53,461; FY2017 88,732).
- Other hand keys: fix files 49 of 56, docmap FY0 57 of 59.
- The disagreements:
  - DIS FY2023–25 and TJX FY2017: the readers left out a lease that sits outside the debt lines, which is the perimeter_incomplete defect;
  - ORCL and MSFT docmap FY0: docmaps older than the fix rows;
  - AMZN 2015: capital-lease current/noncurrent split, ±35M;
  - DIS FY2018: comparative under the new CIK;
  - NEE 2017: a comparative column with no value;
  - MS: no face debt node.

**Rows** (62 companies, every year with a served cell):

| Action | Rows | Meaning |
|---|---|---|
| keep | 246 | the served value equals the structural sum |
| replace | 184 | served UNCHECKED 120, DISAGREE 37, PROVEN 27 |
| fill | 114 | served blank |
| review_missing_column_value | 29 | a debt node has no value in the chosen column |
| reason_not_presented | 29 | |
| no_structural_node | 4 | |

Each row carries the nodes (tag=value [R page, why]), the tags, the sum, the accession, the column, the R pages and the flags.

## Update 2026-11-13 (late): Dhairya's rulings applied, resolver defects fixed
**Rulings applied:**
- **1. Opex, BKNG test.** Cost of sales by nature means a CostOf* tag, a label starting "cost(s) of", or "food & paper".
  - Leading cost-of-sales lines: the block up to the last one is cost of sales, and opex is the lines after it.
  - Cost-of-sales lines scattered through the band (UNH): only those lines are excluded.
  - Cost of sales by label only (MCD food & paper): it shapes the opex band but gives no cost_of_revenue value.
  - No cost-of-sales line in the band (BLK, ORCL, SBUX, UNP): the printed total is opex.
- **3. Revenue.** The operating top line; an "and other income" total is demoted to its sales child (CVX, COP, PSX, MPC).
- **5. Parent equity.** When only the total including NCI is printed, parent equity is DERIVED as total − NCI from the same filing (VZ, T, UNH, PG, CAT).

**Defects fixed:**
- AXP: revenue after provisions descends to RevenuesNetOfInterestExpense.
- ORCL 2024: no calc arcs; the first printed total equal to the sum above it is used.
- COF: no revenue total, so net interest income + noninterest income.
- VLO: the printed cost-of-sales subtotal is used.
- BAC: pretax +1 child before the bank parts.
- MO vs PM: excise is a revenue deduction only when a net-revenue line follows it.

**Gate now** (agreement where both sides resolve):

| Key | Agreement |
|---|---|
| PROVEN own-filing | **99.68%** (10,428 / 10,461) |
| Docmap FY0 | **99.92%** (1,276 / 1,277) |
| Fix files | 95.14% (176 / 185) |
| Hand rows | 93.09% (229 / 246) |

**What remains:**
- 21 stale "combined" opex keys: ruling 1 says re-key.
- 33 PROVEN cells that are wrong under rulings 2 and 3: CVX 11, COP 5, goods-only COR 13 (ORCL 3 goes to a reader), CAT opex 2, AVGO NI 1, MO COR 2018 1.
- VZ equity 2025: ruling 5; both keys are wrong.
- **Open, needs a ruling:**
  - **PM 2015–16 vs MO.** Both print excise taxes between net revenues and gross profit. MO's docmap puts excise in cost_of_revenue; PM's fix rows leave it out.
  - **RTX opex.** RTX's key leaves OtherOperatingIncomeExpenseNet out of opex; MU's key includes it.
