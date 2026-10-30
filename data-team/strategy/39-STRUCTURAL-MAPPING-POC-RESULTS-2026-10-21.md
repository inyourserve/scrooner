# 39. Structural mapping proof of concept: results (Ritwik, 2026-10-21)

Data: SEC FSDS 2025q4, 353 10-K filings with an income statement. DATA-INFERRED only (no filing opened, no database: pooler at 21 connections on 2026-10-21). Scripts: `data-team/strategy/tools/structural_revenue_poc.py`, `structural_concepts_poc.py` (read-only, reproducible). Compares a name vocabulary (a list like our mapper's) with a position+label rule, FY value only.

> **CORRECTION 2026-10-21 (Ritwik, after Verifier R7):** the "values differ" counts in Result 2 came from a bug in my script: it read `pre.txt` rows in file order, not statement line order. After sorting by (report, line), re-run on the same data: D&A differences 61 -> 20, capex 29 -> 5, interest 7 -> 2, operating income 6 -> 3. Conclusion 2 (composition/perimeter is the main non-uniformity) is therefore NOT supported; R7 classified the original 90 D&A/capex differences as 78% my-rule-wrong, 12% name-path-wrong, 9% real perimeter, 0 confirmed filer errors (12 of 90 filing-checked). The NI IS-vs-CF "324/324" is also weak evidence (R6: vacuous when both use the same element). What survives: structure finds real vocabulary misses (NJR, Nikola, Photronics, DLH, all FILING-CHECKED by R7) and the name path has a likely rank bug for D&A (R7 finding 4). See the synthesis doc for the revised plan.

## Result 1: revenue (tested with a refined rule)
agree 275; name-only 9; structure-only 4; disagree 3; neither 62 (mostly banks, trusts, shells, which legitimately have no revenue line).
- Structure-only 4: NJR, Spire, TVA (utilities using RegulatedAndUnregulatedOperatingRevenue) and Nikola (custom tag): real vocabulary misses.
- The 3 disagreements: structure was wrong (picked "Other revenues", "Sales income"); name path was right. The rule needs the calculation tree before it can be trusted.
- Cross-statement identity: income-statement net income equals cash-flow net income in 324 of 324 filings (within 0.5%) once ProfitLoss vs NetIncomeLoss is allowed for. This is a strong, free, population-wide check we do not run.
Reading: for revenue the name path is already about 97% of filers that have a revenue line. The gap is small and sector-shaped (utilities, custom tags), not the main coverage problem.

## Result 2: other concepts (crude regex rules; counts are screening signals only)
| Concept | both | name only | structure only | values differ | neither |
|---|---|---|---|---|---|
| capex | 191 | 27 | 11 | 29 | 95 |
| D&A | 211 | 1 | 31 | 61 | 49 |
| interest expense | 175 | 29 | 20 | 7 | 122 |
| operating income | 241 | 38 | 3 | 6 | 65 |
| CFO | 331 | 9 | 0 | 9 | 4 |
Structure-only rows mix real vocabulary misses (Photronics InterestExpenseNet, Janel PaymentsToAcquirePropertyPlantAndEquipmentNetOfDisposals, CHS custom DD&A, Outdoor Specialty custom capex) with false positives (NJR "accrued capex", Gladstone "unrealized depreciation"). "Values differ" is high for D&A (61) and capex (29) because filers compose these lines differently (D&A with or without amortization of intangibles, capex gross vs net of disposals). That is the true non-uniformity: not the tag name, the PERIMETER of the line.

## Conclusions
1. Structure is a good candidate generator and an independent wrong-value detector, not a replacement for the name path. Label matching alone is noisy; the filer's calculation tree (FSN `cal.txt`) and the identities must gate it.
2. The costly non-uniformity is composition (D&A, capex, total debt, interest, operating income), where one canonical number needs a per-company recipe. Fix with a composition layer: for each such concept, store which components a company's value includes, taken from its `cal` tree, and expose the perimeter ("capex net of disposals") instead of forcing equality. This needs the Standardization Lead's definitions and an accountant for perimeter changes.
3. Run the free net-income IS vs CF identity now across the whole population; extend to Assets = L+E, GrossProfit = Revenue - Cost, CFO+CFI+CFF = change in cash. Any failure is a quarantined finding, not a guess.
4. Expected gain is modest per concept (about 1-9% of filers that have the line), but it is repeatable across all concepts and fixes wrong picks, which is where trust is lost.

## Recommended build order (needs founder go; owners per data-team roles)
1. Identity suite on stored data (Data Engineer, inside `scrooner-certify` I-series): NI cross-statement, balance, gross profit, cash change.
2. FSN `cal.txt` loader for the top 1,000, one monthly zip streamed and deleted (disk 98%): list each company's perimeter for the 6 composite concepts.
3. Composition layer proposal (Standardization Lead) then Verifier sample on 10 companies x 3 concepts.
4. Structure-only candidates for the vocabulary-miss cases (utilities revenue, custom tags) via Tag Mapper coexistence check.
Stop rule: if after step 2 fewer than half of the "values differ" cases are explained by `cal` perimeter, stop and report.

## Not verified
Quarters other than 2025q4; 10-Q and Q4 derivation; era effects before 2018; the top-1000 subset (script ran on all 353 10-Ks in the quarter); whether our stored values show the same disagreements (needs DB when the pooler is free).
