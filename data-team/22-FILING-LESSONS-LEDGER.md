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
| 2026-10-18 | Apple FY2023 = 371 days, FY2022 = 364; Q1 FY2023 = 98 days; 9M YTD = 280 days | Annual duration tests must accept 364 and 371 days; one quarter can be 14 weeks; YTD lengths shift | 0000320193-23-000106, 0000320193-23-000006, 0000320193-23-000077 |
| 2026-10-18 | Apple first XBRL 10-Q (2009-06-27) tags 2007-2008 comparatives | Structured history predates phase-in only as later re-presentation | 0001193125-09-153165 |
| 2026-10-18 | Calumet Item 4.02 on Q1/Q2 2025 10-Q cash flows (CFO/CFF misclassification) | Item 4.02 can target interim statements; restatement arrives as 10-Q/A | 0002013745-25-000015 |
| 2026-10-18 | First Merchants adopted CECL 2021-01-01 under CARES/CAA; First Seacoast (EGC) adopted ASC 842 on 2022-01-01 | Standard adoption year varies by filer; never assume one break year | 0000712534-21-000077, 0000950170-23-009640 |
| 2026-10-18 | Apple revenue tag `Revenues` (FY2018) -> `RevenueFromContractWithCustomerExcludingAssessedTax` (FY2019, ASC 606 year) | Tag switch coincides with ASC 606 adoption year | 0000320193-18-000145, 0000320193-19-000119 |
| 2026-10-18 | Stale-fill refresh joined by (company, period) only: 64% of 4,755 proposals swap in a different tag (ASC 606 subset, continuing-ops subtotal, opposite-signed alternative tag) | A value refresh must require the same source tag; a different tag is a precedence decision, not staleness | ANDE 0000821026-26-000010 R3/R60; XPL 0000917225-15-000038 R6; QWTR 0001493152-23-024965 R4 |
| 2026-10-18 | Authoritative derived Q4 facts include EPS by subtraction and negative revenue/DPS | Derived facts are not eligible replacement sources; route derivation of non-additive or sign-impossible values | RMNI 0001635282-20-000014 R89; MUR 0001193125-14-077534 R132; AGNT 0001104659-26-019145 R6 |
| 2026-10-18 | Filers tag annual values with 3-month contexts in 10-Ks (UP, RTB, AIBT) | A stored "Q4" equal to the same filing's FY value is a label error; verify Q4 as FY minus 9M | UP 0001819516-22-000009 R5 vs 0001819516-21-000014 R4; RTB 0001185185-13-000910 R4 |
| 2026-10-18 | DEF 14A pay-versus-performance tags NetIncomeLoss rounded to $10K | Never take financial-statement values from proxy filings | AEMD 0001683168-26-006844 R2 vs 0001683168-25-004780 R4 |
