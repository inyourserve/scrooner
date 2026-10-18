# Filing lessons ledger (append-only, repo-verified)

Each entry: what happened, the filing or table that proved it, the rule it implies. Agents append here after a verified case (accession required). Source for the first block: CLAUDE.md and pipeline learnings as of 2026-10-18.

| Date | Case | Rule it implies | Proof |
|---|---|---|---|
| 2026-08 | AAPL revenue is filed under 3 different tags over time | Map by period-scoped tag sets, never one tag per concept | doc 11 |
| 2026-08 | JPM FY2014 revenue exists but is non-authoritative, not untagged | "Not authoritative" is a valid null, not "missing from filing" | doc 12, 11b |
| 2026-08 | JPM has 9 listings sharing one CIK (preferreds, ETNs) | Primary ticker comes from the golden company file, not a listing query | doc 25 |
| 2026-08 | Cumulative-YTD-tagged cash flow broke TTM CFO reconstruction | 10-Q cash flows are YTD; derive discrete quarters before summing | doc 25 §9 |
| 2026-09 | `dei:EntityPublicFloat` had a unit-scaling bug (eBay $31 quintillion) | Validate scale before using any dei value as a number | doc 37 |
| 2026-10-10 | `basic_eps` did not map `EarningsPerShareBasicAndDiluted`, which `diluted_eps` did | Verify a ticket's cause against raw tags before trusting its finding type | CLAUDE.md |
| 2026-10-13 | 14-34% of values we hold show no face line in the statements | Face-line absence is evidence, not proof | migration 0093 |
| 2026-10-13 | `no_line_item_filed` meant only "no matching XBRL fact"; 18% of a rendered sample did show the line | Never classify as legitimate absence without rendered-statement evidence | CLAUDE.md |
| 2026-10-17 | 64% of `core.fact` rows sit under unmapped tags; gap wording is relative to OUR tag vocabulary | Coverage loss is vocabulary, applicability and denominator, not the pipeline | CLAUDE.md |
| 2026-10-17 | TTWO: 3,372,772K vs 3,372.8M | A rounded copy never replaces a more precise one | log.md Round 2c |
| 2026-10-17 | LGND: a 10-K/A carried a mislabeled period (full-year value under a quarter label) | Detect label errors in amendments with code, not by adding forms | log.md Round 4a |
| 2026-10-17 | Company 2835 FY2023 revenue stored 6.98B vs authoritative 4.73B | Fills written when all copies were non-authoritative go stale; refresh with a dry-run | log.md Round 4a |
| 2026-10-18 | Blank sample (n=72): 24 ours, 15 structural, 30 unclear, 3 suppression rule | Vendor-only evidence cannot call a blank structural | triage CSV |
| 2026-10-18 | CVX/AJG/HTZ: Revenues - CostsAndExpenses equals pretax income (interest sits inside the costs total) | Never derive operating income from CostsAndExpenses without checking that the total excludes interest and non-operating items | CVX 0000093410-26-000078 R3; AJG 0001628280-26-008662 R3; HTZ 0001657853-26-000008 R7 |
| 2026-10-18 | yfinance "Total Debt" includes operating lease liabilities (CATO 150,448K, ATEX 4,419K, both with no borrowings) | A vendor debt figure cannot show that borrowings exist | CATO 0001562762-26-000041 R3/R58; ATEX 0001304492-26-000027 R3 |
| 2026-10-18 | R-file footnote cells (`td class="th"` with `<sup>`) shift value columns (CVX LTD showed "[1]" in the 2025 column) | Drop footnote cells before positional parsing | CVX 0000093410-26-000078 R5 |
