---
id: cell-proof-rules-that-survived-the-verifier-2026-10-31-to-11
title: Cell proof rules that survived the Verifier (2026-10-31 to 11-04): every periodic copy must agree; a value must sit in a statement column, not a note; a calc-parent line is a total; subtotals are children of higher subtotals
kind: rule
tags: proof, cell-proof, verifier, fsn, restatement
paths: 
evidence: FILING-CHECKED
status: active
created: 2026-10-31
verified: 2026-10-31

unmerged_paths: pipeline/src/scrooner_pipeline/proof/prove.py; pipeline/src/scrooner_pipeline/proof/shown.py
---
Rules the Verifier draws confirmed or corrected on the first-10 proof runs (verify/cell-proof-first10-2026-11-04, -v4): (1) PROVEN requires every PERIODIC copy of the cell in core.fact to agree within the filer's precision; if copies disagree the verdict is DISAGREE restated_copies_disagree whichever copy production shows (founder: restated copies that disagree are hidden; 'show the latest recast' is his decision, not the engine's). Comparing only against the filing that carries the shown value makes any as-filed value look proven: rejected. (2) PROVEN requires the value's column to exist on the statement face: a 10-K prints annual columns only, a 10-Q income statement the 3-month and year-to-date columns, a 10-Q cash-flow statement the year-to-date only, a balance sheet the dates where total assets is printed; FSN num holds note and MD&A facts too (HD quarterly-data note, 3-month cash-flow figures), so a matching number from a note is NOT_PRESENTED value_in_note_not_on_statement_face. (3) A line that is itself a calc parent is a printed total whatever custom line rolls it up (AMZN CFO under a custom cash roll-up, PG operating income); a line is a component only when its parent is a filer extension. (4) Subtotals are calc children of the next subtotal up (gross profit under operating income, Liabilities under LiabilitiesAndStockholdersEquity): never a component. (5) Components sum per calc GROUP (face vs tax-note groups double-count when merged); a single-arc group is not a decomposition; a sum of n rounded children may miss by n/2 units. Results: v1 7,828 PROVEN / 797 DISAGREE of 12,143 cells -> v4 10,548 PROVEN / 124 DISAGREE; derived quarters 2,158 of 2,228 PROVEN through YTD_n - YTD_n-1. Real defect found: AAPL quarterly dividends paid FY2015-FY2017 show 3-month note facts (declared amounts) instead of the cash-flow face quarters.
