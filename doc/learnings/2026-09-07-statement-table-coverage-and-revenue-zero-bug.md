# Statement table coverage deep-dive + a real revenue-resolves-to-$0 bug (2026-09-07)

Prompted by a direct user report: "lots of row and column have no value" on the company page's Income Statement / Balance Sheet / Cash Flow tables. Investigated live against the real database (5,216 active companies), not from memory.

## Finding 1 (fixed): Gross Profit / Cost of Revenue / Operating Expenses had no fallback at all

`statements/classify.py`'s `STATEMENT_LINES` mapped these three Income Statement rows to a single raw XBRL-tag concept each (`gross_profit`, `cost_of_revenue`, `operating_expenses`), despite doc 40 (2026-09-02) already establishing that the *metric* `gross_margin` derives cleanly from Revenue − Cost of Revenue — that derivation was never extended to the canonical_fact layer the statement table actually reads from.

Real coverage before the fix (active population, "ever had a value" basis):

| Line | Companies with a value | % |
|---|---|---|
| Gross Profit | 2,528 / 5,216 | 48.5% |
| Cost of Revenue | 3,087 / 5,216 | 59.2% |
| Operating Expenses | 3,748 / 5,216 | 71.9% |

Per-period fill opportunity confirmed before implementing (this is the number that matters for "blank cells," not the company-level count above):

- 45,001 (company, period) rows have Revenue + Cost of Revenue but no Gross Profit.
- 11,412 have Revenue + Gross Profit but no Cost of Revenue.
- 53,303 have Gross Profit + Operating Income but no Operating Expenses.

Accounting-identity sanity check against the 128,885 periods that already report Revenue, Cost of Revenue, AND Gross Profit together: 92.0% match `Revenue − Cost of Revenue` exactly, another 1.8% within 2% (immaterial rounding/reclass), 6.3% genuinely disagree. Investigating the disagreement led directly to Finding 2.

### Fix

New migration `pipeline/db/migrations/0047_statement_line_arithmetic_fallbacks.sql` adds three zero-`concept_mapping` "resolved" concepts (`gross_profit_resolved`, `cost_of_revenue_resolved`, `operating_expenses_resolved`), same "new THIRD concept, resolve() never touches it" idiom as `total_debt_resolved` (migration 0033) — but an *arithmetic* merge (derive from two other concepts when the primary tag is absent) instead of 0033's simple concept-vs-concept coalesce. New `mapper/concept_fallback.py` function `resolve_arithmetic_fallback` / `resolve_all_arithmetic_fallbacks`, wired to a new CLI command `scrooner-map resolve-statement-fallbacks`. Set-based SQL (one DELETE + one INSERT...SELECT per concept covering the whole population), not a per-company Python loop — this project's own established rule against query-per-row-in-a-loop batch jobs.

`statements/classify.py`'s `STATEMENT_LINES` repointed to the three `*_resolved` concepts; re-ran `seed-statements` to update the existing `analytics.statement_line` rows.

Real gain, full population, run and verified 2026-09-07:

| Concept | Cells (period-rows) before | After | Gain |
|---|---|---|---|
| Gross Profit | 151,492 | 195,817 | +44,325 (+29.3%) |
| Cost of Revenue | 186,365 | 197,521 | +11,156 (+6.0%) |
| Operating Expenses | 230,338 | 292,415 | +62,077 (+27.0%) |

**+117,558 previously-blank statement-table cells filled**, purely additive (zero regression risk — the primary branch always wins where it exists; `pytest tests/unit/` 427/427 passing before and after).

## Finding 2 (documented, NOT fixed): `resolve.py` can resolve Revenue to an authoritative $0 for a real, large company

Investigating the 6.3% Gross-Profit-identity mismatch above led to Flowserve Corp: **all 7 of its FY revenue canonical_fact rows are exactly $0**, despite Flowserve being a real ~$4-5B/year industrial company (confirmed via its own Cost of Revenue and Net Income for the same periods, both clearly multi-hundred-million-dollar figures). Root cause, traced to `core.fact` directly:

```
tag=RevenueFromContractWithCustomerExcludingAssessedTax (priority 1): 3 rows, values ~$3.94B, ALL is_authoritative=false
tag=Revenues (priority 2, first_match's fallback):                    3 rows, values $0 / $0 / $0, ONE is_authoritative=true
```

The priority-1 tag's 3 rows disagree by a trivial <0.13% (a cross-filing rounding difference — $3,944,850,000 vs $3,939,697,000) — Stage 2e's dedup logic correctly marks all of them `is_authoritative=false` on ANY disagreement, exactly as documented and intended (see `pipeline/CLAUDE.md`'s 2026-08-19 `total_debt` entry for the identical, deliberate mechanism on a different concept: "picking any single value here — even 'most recent' — would be a guess the Mapper shouldn't inherit as settled fact"). But `resolve()`'s `first_match` mode then falls through to the priority-2 tag, which happens to have an authoritative-but-spurious $0 for that period, and confidently returns it.

**This is a real correctness bug, not the intended behavior of the conflict policy that causes it** — the conflict policy is working exactly as designed (never guess between $3,944,850,000 and $3,939,697,000); the bug is that `first_match` treats "an authoritative $0 from a worse tag" as more trustworthy than "no authoritative value from the best tag," when in this case the reverse is obviously true. A confidently-wrong $0 is arguably worse than an honest blank cell, per this project's own "never fabricate, trust before showing" principle.

**Scope, measured before deciding whether to chase further:**
- 883 companies, 11,992 periods have `revenue.value = 0` in `canonical_fact`.
- Of those, only 266 periods also have a same-period Cost of Revenue > $1M — a strong, cheap signal of "this $0 is provably wrong," not just "this company genuinely has no revenue" (most of the 11,992 are legitimately pre-revenue: biotechs, SPACs, shell/holding companies). Real, named companies hit by the provably-wrong subset include Eaton Corp, DENTSPLY SIRONA, Flowserve, PriceSmart, and OGE Energy — real, well-known operating businesses, not edge cases.

**Not fixed in this pass** — `resolve.py`/`dedupe.py` is a frozen Mapper boundary (per `pipeline/CLAUDE.md`: "The Mapper must not... bypass `core.fact.is_authoritative`"), and a general fix (e.g., "don't fall through to a lower-priority tag if the higher-priority tag has data, just disagreeing data" vs. "apply a trivial-difference tolerance before marking non-authoritative") deserves its own careful design and review rather than a same-session patch bundled into an unrelated statement-table fix. The new derived concepts above are structurally immune to this bug (they require `revenue > 0` before deriving anything), so Finding 1's fix does not propagate Finding 2's bug — confirmed live: Flowserve's FY2019 (a known $0-revenue period) correctly shows Revenue=$0 but Cost of Revenue/Gross Profit/Operating Expenses as blank (`null`), not a wrong negative-billions figure.

**Recommended next step for whoever picks this up:** the safest fix is likely a small tolerance in `dedupe.py`'s conflict check (e.g., don't mark non-authoritative for a <1% cross-filing difference, or prefer the most-recent-filing's value when the disagreement is immaterial) rather than touching `resolve()`'s fallback order — changing `first_match`'s fallback semantics risks regressing every other concept relying on that exact "next tag if no authoritative value" behavior.

## Finding 3 (confirmed structural, not a bug): Balance Sheet current/non-current lines missing for financial-sector companies

Checked whether `current_assets`/`current_liabilities`'s ~82% coverage (vs. `total_assets`'s ~99.7%) was a fixable gap. It is not: companies with `total_assets` but no `current_assets` are overwhelmingly REITs (176), banks (173+83+36+32), brokers/dealers (88+13), and insurers (54+17) — sectors that legally report an **unclassified balance sheet** under GAAP (no current/non-current split at all), the same structural absence this project has already documented for Piotroski F-Score and BDC revenue. Confirmed via `c.sic_description` grouping on the gap population — no fix needed or possible without inventing a number the filing itself never reported.

## Full verification

- `pytest tests/unit/` — 427/427 passing before and after.
- `scrooner-map seed-statements` re-run (confirmed `analytics.statement_line`'s income_statement rows 2/3/4 now point to the `*_resolved` concepts).
- `scrooner-map resolve-statement-fallbacks` run against the full population (0 errors; 197,088 / 198,762 / 294,173 total rows written per concept, including carried-over primary-tag rows).
- Live company-page render checked directly (not just SQL): Flowserve's quarterly table shows real Cost of Revenue/Gross Profit for every recent quarter; its annual table's FY2019 column (the known $0-revenue period) correctly shows a blank Cost of Revenue/Gross Profit/Operating Expenses cell instead of a fabricated value.
