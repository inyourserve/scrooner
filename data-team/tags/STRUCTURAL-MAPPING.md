# Structural mapping: a data point is a node in the filing's own trees (design, 2026-11-13)

**Status.** Design by the tag expert, at the founder's direction (relayed by Dhairya). Not approved. Perimeter changes still need the named accountant.

**Inputs (already loaded in FSN).**
- `fsn.line`: statement, report, line order, indent (`inpth`), preferred label role (`prole`), label (`plabel`), sign (`negating`).
- `fsn.calc_arc`: parent tag, child tag and weight, per group. It covers 45,223 of 45,747 filings.
- `fsn.value`: values by tag, `ddate`, `qtrs` and dimension.
- `fsn.filing_check` already evaluates the filer's calc tree. Pass rates (live, 2026-11-13):

| Check | Pass rate | Checks |
|---|---|---|
| `bs_assets_eq_liabilities_equity` | 99.95% | 72.0k |
| `calc:GrossProfit` | 99.94% | 43.3k |
| `calc:OperatingIncomeLoss` | 99.62% | 74.8k |
| `calc:` change in cash | 99.61% | 44.9k |
| `calc:LiabilitiesAndStockholdersEquity` | 98.43% | 38.8k |
| `calc:Assets` | 97.84% | 66.6k |

## 1. Data point = role in the tree; the tag only names the node
A resolver walks one filing's statement, in line order, with its calc arcs. It returns, for each data point, the node, its value at (`ddate`, `qtrs`), and a structural path as evidence (accession, R page, line, calc parent).

| Data point | Structural role (what the resolver finds) |
|---|---|
| total_assets | BS face total: the calc root of the asset side, the line whose value equals the L&SE root |
| total_liabilities | the calc child of L&SE that is the liabilities subtotal; absent → DERIVED (§3) only when the tree gives L&SE − every equity-side child |
| stockholders_equity | the parent-equity subtotal under L&SE (before NCI); the total-incl-NCI node is a separate role |
| mezzanine / NCI | every other calc child of the L&SE root, whatever its tag (temporary equity, redeemable NCI, nonredeemable NCI, convertible equity component) |
| revenue | IS first total line: the calc root of the top-line children (top-most revenue parent, never a child of another revenue line) |
| cost_of_revenue | the subtotal between revenue and gross profit, or the sum of the calc children there with weight −1 (excise is a sibling of COR, not part of it) |
| gross_profit | the IS node whose calc children are revenue (+1) and COR (−1); not printed → reason or DERIVED |
| operating_expenses | the lines between GP (or COR when there is no GP) and OI: OI's calc children other than GP/revenue/COR. A "total costs and expenses" node that contains COR is not opex |
| operating_income | the IS node that is the calc parent of GP/revenue and the opex children; a filer label like "income before taxes" does not make it OI |
| total_debt | BS liabilities children with debt role (borrowings, notes, commercial paper, current portion) plus the finance/capital lease nodes the filing places under liabilities; never a note-only aggregate that double-counts |
| cfo / cfi / cff | the three CF section totals: the calc children of the change-in-cash root, alongside fx and discontinued flows |

## 2. Identities are the filing's own calc arithmetic
- The cross-check is the company's declared tree, evaluated on its own values. That is `fsn.filing_check` `calc:<root>` plus the BS check. There are no operand lists.
- Mezzanine, NCI, excise, fx and discontinued flows enter because the filer put them in the tree.
- **Served values must sit on that tree.** Each served member must equal the node value in **one** filing, the filing it is served from. A served cell whose value is not the node in its own filing is a wrong-value finding. That catches the vintage mixes, e.g. JPM 2015-Q1 assets taken from a later 10-Q's summary table.
- A filing whose own check fails is quarantined. Nothing is served from it as PROVEN.

## 3. Not printed → DERIVED from the same tree, or a reason
- **DERIVED:** the value is computed only from nodes of the same filing and column. Evidence is the arithmetic path, e.g. GP = revenue − COR, or L = L&SE − equity side.
- **Reason:** when the tree has no such span, the cell takes one of not_presented, combined (the node's children mix it with other items), or not_in_template (bank, insurer or REIT trees have no COR/GP role).

## 4. What collapses
- **Identity operand lists go:** `TEMP_EQUITY_GROUPS`, `NCI_*`, `FX_TAGS`, `DISCONTINUED_CF_TAGS` and the HD exception in `proof/identities.py`. The tree carries every operand, and the 199 + 49 + 6 "missing operand" breaks in `red-cells/identity-breaks-2026-11-13.csv` disappear.
- **Existing rulings that become one tree rule each:**
  - opex = component_sum between GP/COR and OI (§AE), plus its tie tolerance;
  - SG&A = G&A + S&M (MSFT);
  - revenue = top-most line (S4);
  - CAT "total operating costs" is not opex;
  - components without a single calc parent (S9);
  - opex tie from COR (S12);
  - mixed-statement components (R06/S1);
  - total_debt with leases;
  - member-only COGS: the node is the dimension total.
- **What stays outside the tree:** facts that live only in notes (cash taxes, cash interest, weighted shares, amortization). For these the role is "undimensioned consolidated fact in the note whose table belongs to the data point" (§AG), still identified by position in its R page.
- **The predictor (`predict.py` v7)** keeps its CSV rules, but each rule becomes a **hint**: a tag prior used only to rank candidate nodes. Its order is:
  1. structural role from the tree;
  2. tag hint, among nodes that hold that role;
  3. label, which can demote a node but never promote one.

  A tag match outside the role is never served. Rules that only patched a missing role are retired once the backtest shows the structural resolver holding the same answers. The backtest gate, `exam/tools/backtest.py`, is unchanged.

## Rollout (tests first)
1. Resolver as a read-only function over `fsn.line` + `calc_arc` + `value`. Write `fsn.line_map` (its `status` values already exist: mapped, combined, excluded, unmapped).
2. Backtest against the hand exam and the reader fix files. Measure agreement and wrong rows per class; zero new wrong rows is the gate.
3. Then the proof reads `line_map` instead of tag lists.

Evidence labels: anything from data sets alone is DATA-INFERRED, until a filing sample is opened (xbrl-structure skill).
