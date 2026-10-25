---
name: xbrl-structure
description: Map and check Scrooner financial lines by a filing's own structure (statement, line position, label, calculation tree, accounting identities) instead of by tag name. Use when a company's tag differs from the usual one, a custom extension tag may hold a standard line, a total's contents are in doubt, or you must classify a blank as vocabulary gap vs. line not presented.
---

Scrooner's name-based mapper asks "is this tag in my list for concept X?" That cannot converge (about 12.4k SEC tags, most facts under unmapped tags). A filing already states what each line is. Use that as an independent second path. Background and proof of concept: `data-team/strategy/38-TAG-UNIFORMITY-FRESH-LENS-2026-10-21.md`.

## Sources, in order of use (all free; SEC fair-access: declared `SEC_USER_AGENT`, at most 2 requests/second)
1. **FSDS `pre.txt`** (SEC Financial Statement Data Sets, quarterly zip about 65 MB): per filing, statement (`IS/BS/CF/CI/EQ`), `report`, `line` order, `inpth` indent, `tag`, `version` (a non-`us-gaap` version means a custom extension), the filer's own `plabel`, `negating`. `sub.txt` gives CIK, SIC, form. `num.txt` gives values.
2. **FSN `cal.txt`** (Financial Statement and Notes Data Sets, 41-810 MB per zip): the filer's own calculation tree, parent tag to child tag with weight. Shows what is inside a total (CVX case, `data-team/22` 2026-10-19). Stream one zip at a time and delete it; the dev disk is near full (`df -h`).
3. **FASB taxonomy** calc trees and definitions (`data-team/tags/sources.md` rank 1) for what a standard tag officially contains. Official definition is not evidence of how a filer used it.

## Method (one filing, one concept)
1. Find the statement and the anchor lines: income statement top line and its next sibling (cost of revenue or expenses), balance sheet totals, cash flow subtotals.
2. Classify the target line by position + label class + rollup: does it sit first on the income statement, is it followed by cost of revenue, does `cal` roll it into a known anchor?
3. Check with identities on the filing's own numbers (`num.txt`, same `adsh`, same `ddate`, `qtrs`): assets = liabilities + equity; revenue - cost = gross profit; CFO + CFI + CFF (+ FX) = change in cash. Allow rounding only. A failed identity quarantines the filing; never flip a sign to pass.
4. Compare with the name-based result (`concept_mapping` / `analytics.canonical_fact`):
   - agree: high confidence.
   - disagree: record a finding for the Data Verifier (this is a wrong-value detector).
   - structure-only: a candidate fill, never auto-published; needs the tag-mapper coexistence check and a Verifier filing sample with zero wrong rows.
5. A custom tag that rolls into a standard anchor becomes a company-scoped mapping with the accession and `cal` path as evidence, never a global mapping.

## Rules that stop false positives
- A line missing from the face statements may be a legitimate non-line: banks, BDCs, insurers, REITs, shells, trusts present no revenue/COGS (the first PoC: 56 of 353 10-Ks had no standard revenue tag in the first six income-statement lines, most legitimately). Classify by sector family before calling it a gap (`12-SECTOR-ANALYST.md`).
- Same label, different meaning (e.g. PEBO `OperatingIncomeLoss` printed as "income before income taxes"): confirm in the filing, not from the label.
- Period basis: match `qtrs` (4 = year, 1 = quarter) and `ddate`; never mix cumulative YTD with quarter.
- Evidence labels: FILING-CHECKED only when a filing was opened and cited (accession + locator). Anything from data sets alone is DATA-INFERRED.
- No database writes from this skill. Proposals go to the Tag Mapper / Data Engineer; perimeter changes need the named accountant.

## Script
`python3 -I .claude/skills/xbrl-structure/scripts/fsds_first_lines.py <dir with sub.txt and pre.txt> [--form 10-K] [--vocab Revenues,RevenueFromContractWithCustomerExcludingAssessedTax,...]`
Lists filings whose first income-statement lines hold none of the vocabulary tags, with the first two lines' tag, version and label. Read-only; reproduces the doc 38 proof of concept. Extend, do not fork, when adding concepts.
