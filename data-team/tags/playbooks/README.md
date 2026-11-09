# Line identification playbooks (Tag Expert)

One file per data point in the FSN write (`.github/workflows/pipeline-fsn-write.yml`, input `data_points`). Each playbook says, for the top-1,000 cohort: which tag and structure patterns carry the line, ranked by how many companies use them; what the current concept rules already catch; what they miss and why; and the traps. They are knowledge for the builders and the Verifier. **They approve nothing**: every "candidate" below needs the Tag Mapper's coexistence check and a Verifier draw before it enters `data-team/47-fsn-store/concept_rules/`.

Started 2026-11-09 by the Tag Expert session (manager: session_01GLmSDyzegqZw4JqC91z7XH).

## How the counts were made (applies to every playbook unless it says otherwise)

- Source: the production `fsn.*` store (read-only, `statement_timeout` 15 s, one connection; client backends 6 at the start). `fsn.*` holds SEC FSN rows for the companies the 2026-11-09 load reached (`fsn.company_load` 901 rows).
- Unit: **one filing per company, its latest non-amended 10-K** in `fsn.filing`. 873 companies have one; **632 of them have `fsn.line_map` rows** on it (the mapper ran). Every "X of 632" is out of those 632. The other 241 are not in this measurement (line_map not built for them yet, as of the read).
- "Mapped" = `fsn.line_map.status = 'mapped'` to the data point's `canonical_concept_id`. "Gap" = a company with no mapped line for that concept in that filing.
- Evidence level: **DATA-INFERRED (FSN row)**. Every example cites accession + FSN report number + line, so the Verifier can open `R<report>.htm` of that accession. I could not open filings this run: sec.gov returned 403 "undeclared automated tool" because this cloud session has no `SEC_USER_AGENT` with a contact address, and I will not invent one. **No verdict in these playbooks is FILING-CHECKED unless it cites an existing card that is.**
- Latest-10-K only: era patterns (taxonomy 2024 tags, CECL tags) are in the cards (`../cards/`), not re-measured here.

## Structural facts every playbook depends on (from the code, read 2026-11-09 at main 49334b4)

1. **The mapper only reads statements `BS`, `IS`, `CF`** (`pipeline/src/scrooner_pipeline/fsn_store/mapping.py`, the `l.stmt in ('BS','IS','CF')` read) **and excludes every parenthetical line** (`inpth` → status `excluded`, `{"why": "parenthetical"}`). So anything printed only on the equity statement (`EQ`), a parenthetical, the comprehensive-income statement (`CI`) or an unclassified statement (`UN`) can never be mapped. This is the main reason `shares_outstanding_resolved` (18 of 632) and `dividends_per_share_resolved` (64 of 632) are low. See those playbooks.
2. **FSN's `stmt` code is SEC's classification and is sometimes wrong for the income statement.** Diluted EPS (`EarningsPerShareDiluted`) sits in `IS` for 866 of 873 latest 10-Ks; it sits in `IS`+`UN` for 4, `CI`+`IS` for 1, `CI` only for 1 (GATX), `UN` only for 1 (Revvity). Cases:
   - Revvity 0000031791-26-000012: R4 "Consolidated Statements of Operations" is `stmt=UN` (26 lines); the only `IS` lines are a derivative/debt detail table (R12). So every IS concept is blank for Revvity's latest 10-K.
   - GATX 0000040211-26-000018: R5 "Statement of Comprehensive Income (Statement)" (8 lines, the OCI block) is `stmt=IS`, and R6 "Consolidated Statements of Comprehensive Income" (31 lines, the real income statement) is `stmt=CI`. The classes are swapped.
   - Fix direction (for the builder, not me): when a filing has no `IS` report holding an anchor (`NetIncomeLoss`/`ProfitLoss`/EPS) but a `menucat='S'` report in `CI`/`UN` does, treat that report as the IS. Small (about 3 of 873), but it blanks the whole income statement for those companies.
3. **Note values exist in `fsn.value` for every report**, not only statements (`fsn.line` holds statement lines only; MSFT's latest 10-K has 130 statement lines and 1,029 values). Non-dimensional facts have `dim_id = 0` and `coreg = ''` (not NULL). The select step already uses this for interest expense (`select.NOTE_TAGS`).

## Index

| Data point | Mapped (of 632) | Playbook |
|---|---|---|
| interest_expense_resolved | 427 (+ note fill at select) | [interest_expense.md](interest_expense.md) |
| revenue_sanity_resolved | 603 | [revenue.md](revenue.md) |
| cost_of_revenue_resolved, gross_profit_resolved | 424, 236 | [cost_of_revenue.md](cost_of_revenue.md) |
| share_buybacks_resolved | 490 | [share_buybacks.md](share_buybacks.md) |
| dividends_paid_resolved | 455 | [dividends_paid.md](dividends_paid.md) |
| net_income_resolved | 569 | [net_income.md](net_income.md) |
| shares_outstanding_resolved | 18 | [shares_outstanding.md](shares_outstanding.md) |
| dividends_per_share_resolved | 64 | [dividends_per_share.md](dividends_per_share.md) |
| operating_income, income_before_tax, income_tax_expense, basic/diluted EPS, CFO | 466, 569, 612, 611/610, 632 | [income_statement_and_cfo_others.md](income_statement_and_cfo_others.md) |

The SQL for every count is in [queries.md](queries.md), so anyone can re-run it.
