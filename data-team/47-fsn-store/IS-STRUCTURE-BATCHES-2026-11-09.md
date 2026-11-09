# Income-statement mapping by structure, batches 1-3 (2026-11-09)

Owner: tag & mapping expert (cloud session, started by the manager session). Branches, stacked:
`work/tag-expert/is-net-income-detector` (batch 1) <- `work/tag-expert/is-pretax-structure` (batch 2) <-
`work/tag-expert/is-interest-structure` (batch 3, carries all three). Nothing written to production; no migration.

## What changed
| batch | rule_id | what | gap it closes (cohort dry run 41708119011, no_mapped_line) |
|---|---|---|---|
| 1 | `is.net_income_profit_loss_no_nci@1` | lane G1b (is_detect.net_income_slot, imported): ProfitLoss when no NCI / preferred line is printed | net income: 25 companies, 1,353 keys |
| 1 | `is.net_income_available_to_common_bridge@1` | lane G2b: ProfitLoss bridged through NCI lines to NetIncomeLossAvailableToCommonStockholdersBasic, plus the per-column tie PL - NCI = it | same |
| 1 | `is.net_income_bottom_line_tie@1` | NEW G2c: no NetIncomeLoss / ProfitLoss / NCI / preferred line; the bottom line before the per-share block, labelled net income, ties pretax - tax (+ lines between) per column | same |
| 2 | `is.pretax_above_tax_line_tie@1` | NEW P1 (`fsn_store/is_structure.py`): the line directly above IncomeTaxExpenseBenefit, before-tax label, tie: it - tax = the next line, per column; any tag (custom, domestic-only, another concept's tag) | pre-tax: 39 companies, 1,987 keys |
| 3 | `is.interest_single_gross_face_line@1` | NEW I1: the face's ONLY interest-expense line under a debt-component tag; held with a net-interest line, a deposit line, a separate financing-cost amortization line, or a net/other label | interest expense: 122 companies, 4,544 keys |

Every detector is additive (acts only where the seed mapped no line to the concept in the filing) and maps only a line
the seed left unmapped.

## Measured (local scratch store, pilot sequence)
Store: every SEC FSN set 2014q1 to 2026m10 fetched from sec.gov (one request at a time), filtered to the 212 cohort
companies blocked as no_mapped_line on an IS data point, sharded with `fsn_store.shard`, loaded, all committed concept
rules seeded; 209 companies, 9,390 filings. `scrooner-fsn pilot` run twice on copies: origin/main (e229e60) vs batch 3.
0 companies failed in either run.

| data point | template keys | valued before -> after | no_mapped_line keys before -> after |
|---|---|---|---|
| net_income_resolved | 10,824 | 8,287 -> 9,771 | 1,272 -> 127 |
| income_before_tax_resolved | 10,824 | 7,667 -> 8,660 | 1,987 -> 1,209 |
| interest_expense_resolved | 10,239 | 5,042 -> 5,703 (before the CubeSmart hold; it removes 23 CubeSmart filings) | 4,566 -> 3,618 |

Cells: 3,511 new, 0 removed, 77 changed. Of the 77: 51 were blanks (defects) that now get a value (a quarter becomes
derivable once neighbouring filings have a mapped line), 4 keep the same value by another method (MELI, CUBE), and
**22 change a shown value**, listed as set B in the sample file. Their cause is select's own latest-copy rule, not a
different line in the same filing: later filings that restated comparatives (Viatris, AST SpaceMobile, Galaxy Digital
reverse mergers; Ball discontinued operations; Tenet, NiSource restatements) had no mapped line before, so select fell
back to the older copy. Eversource is the G2b case the lane built G2b for (NetIncomeLoss 1,212.7M is consolidated incl.
subsidiary preferred dividends; the G2b line 1,205.2M is the parent's). Regions 2019-Q1 pre-tax turns blank
(`latest_copy_fails_identity`: the newer 10-Q's column fails an unrelated interest-income calc check).

FSN 2025q1 cross-check (195 companies): where the seed maps a pre-tax line, P1 picks the same line 119/119 (0 disagree).

## For the Verifier
`IS-STRUCTURE-VERIFIER-SAMPLE-2026-11-09.csv`: set A = 51 new printed cells (8-12 per rule, one per company, seed
20261109); set B = all 22 changed shown values (old and new value and accession). Open each filing at the accession,
report and line given. Nothing in this file is filing-checked yet (DATA-INFERRED).

## Not done here (owner / next)
- 51 interest-blocked companies print only a NET interest line; several file a gross InterestExpense in the notes of
  the same filing (DIS, CHWY, CARR, SW): a note-sourced cell candidate, not a face mapping.
- EPS at MLPs (EPD, PAA, ET, MPLX, WES, SUN, CQP, ARES): per-unit earnings; whether that serves basic_eps is a
  Standardization Lead decision.
- AFG prints "Earnings before income taxes" under OperatingIncomeLoss, which the seed maps to operating income: a
  wrong-value candidate for the Verifier (P1 does not re-map a line the seed owns).
- BSX (FY2015-2024), SPG, AMH: a preferred line below ProfitLoss; parent net income is not printed; held.
