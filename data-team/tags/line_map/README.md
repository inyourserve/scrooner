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
