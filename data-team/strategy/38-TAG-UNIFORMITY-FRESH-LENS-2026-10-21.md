# 38. Tag non-uniformity: fresh-lens diagnosis and fix (Ritwik, 2026-10-21)

Problem (founder): companies tag the same economic line differently, so coverage has holes and some values are wrong.

## Diagnosis
Our mapper answers "is this tag NAME in my list for concept X?" (a vocabulary lookup). That approach can never converge: ~12.4k SEC tags, 64% of core.fact rows under unmapped tags, only ~90 approved/provisional (CLAUDE.md, 2026-10-17 audit). Each new filer, custom extension or taxonomy year opens new holes, and every added tag needs a coexistence check. The gap list is circular, because it is measured against our own vocabulary.
The filing already says what each line IS, in two machine-readable places we do not use (PLAN.md deferred them past launch):
1. Presentation (SEC FSDS `pre.txt`): statement (IS/BS/CF), line order, indent, the filer's own label, for every tag including custom ones.
2. Calculation (FSN `cal`): the filer's parent-child sums with weights (what is inside a total; data-team/22 CVX case proved it).
Plus accounting arithmetic (assets = liabilities + equity, gross profit = revenue - cost, CFO + CFI + CFF = net cash change) as a self-check.

## Proof of concept (DATA-INFERRED, FSDS 2025q4, 353 10-K filings with an income statement)
Method: take the first 6 lines of each filing's income statement; does any carry a tag from our revenue vocabulary? 56 of 353 (15.9%) do not. Most are legitimate non-revenue filers (banks, BDCs, shells, trusts: Gouverneur, Gladstone, Golub, IB Acquisition). One is a real vocabulary miss: Nikola, whose line labeled "Revenue", followed by "Cost of revenues", uses a company extension tag. Position + label + sibling structure identifies it; name matching cannot. This is one quarter, one concept, no value check: it shows the signal exists, not the hit rate. Not a certified result.

## Recommendation: add a structural resolver as a second, independent mapping path
- Per filing, classify each statement line by (statement, position, rollup into a known anchor via `cal`, label class) into our canonical concepts. Name-based mapping stays as path A. Path B (structure) runs beside it.
- Agree = high confidence, publish. Disagree = a finding for the Verifier (this is also a population-wide wrong-value detector, which data-team/34 invariants lack today). B-only = candidate fill, goes through the existing coexistence check + Verifier sample, never auto-published. Custom tags that roll into a standard anchor via `cal` become scoped company mappings, not global ones.
- Gate with arithmetic identities per filing; failing identities quarantine, never flip signs.
- Data: FSDS zips (65 MB per quarter, free, bulk, no rate limit); `cal` needs the FSN set (larger; disk is at 98%, 4.4 GB free on 2026-10-21, so stream and delete per quarter).
- Scope first: the top 1,000, five anchors (revenue, operating income, net income, total debt, total equity), the latest 8 filings each. Measure: blanks filled, disagreements with path A, and Verifier-checked wrong rate. Kill if disagreements are noise.
Owner: Tag Mapper + Data Engineer; Verifier samples; accountant approves any perimeter change. Founder call: fund this (about 2 weeks ASSUMED) ahead of more shard hunting.

## Do not
Map more tags by name as the main strategy; trust structure alone without arithmetic; auto-publish B-only values.
