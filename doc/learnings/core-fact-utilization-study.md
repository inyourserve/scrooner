# Why `core.fact` utilization looks like "4%" — and what's actually worth doing about it

Prompted by a direct question during the 174-company pilot expansion: `analytics.canonical_fact` only references 14,043 of 331,600 `core.fact` rows — "why are we only utilizing 4% of the raw data, and how do we improve that?" Investigated live against the real database rather than reasoned from memory, using the project's own existing `scrooner-map unmapped-tags` discovery tool (built doc 11, never run at this scale before).

## The "4%" number measures a narrower thing than it sounds like

Two different, both-correct utilization numbers exist depending on what you're counting:

| Measure | Count | Share |
|---|---|---|
| `core.fact` rows referenced by `analytics.canonical_fact.source_fact_ids` (i.e., actually feed a currently-computed metric) | 14,043 | 4% of all 331,600 rows |
| Authoritative (`is_authoritative=true`) facts on a **tag that has any `concept_mapping` row at all** | 31,084 | 17% of 186,351 authoritative rows |
| Authoritative facts on a tag with **zero** `concept_mapping` row | 155,267 | 83% of authoritative rows |

The gap between 4% and 17% is `combination_mode`/priority mechanics working as designed — e.g. `total_debt` is `sum` mode across several component tags, and `revenue`/`depreciation_and_amortization` are `first_match` across alternates, so a mapped tag's facts don't all become a winning `canonical_fact` even when the tag itself is curated. That's not waste; that's the alternates system doing its job.

The real question worth investigating is the 83% — facts on tags nobody has looked at yet.

## The 83% is a long tail, not a few forgotten giants

```
2,837 distinct unmapped tags, 155,267 total facts
Top 40 tags by volume: 28,212 facts -- only 18% of the unmapped pool
```

Ranked the full unmapped set by fact-row-count (real SEC data, golden-set-plus-6-companies currently normalized). The top of that list, with company counts checked live, not assumed:

| Tag | Facts | Companies | What it is |
|---|---:|---:|---|
| `EarningsPerShareBasic` | 1,393 | 16 | Basic EPS (we map diluted only) |
| `WeightedAverageNumberOfSharesOutstandingBasic`/`...Diluted` | 2,631 combined | 16 | Per-share denominators |
| `ComprehensiveIncomeNetOfTax` | 1,157 | 14 | Comprehensive income |
| `Goodwill` | 558 | 11 | Balance-sheet goodwill |
| `IncreaseDecreaseInAccountsReceivable`/`...Inventories`/`...AccountsPayable` | 852+755+569 | up to 10 | Cash-flow-statement *period changes* — different concept from the balance-sheet snapshots mapped last week |
| `LongTermDebtNoncurrent` | 503 | 10 | Alternate debt-split tag |
| `AllocatedShareBasedCompensationExpense` | 626 | 10 | Looked like an SBC alternate |
| `EffectiveIncomeTaxRateContinuingOperations` | 502 | 11 | Directly-reported tax rate |
| `AmortizationOfIntangibleAssets` | 508 | 12 | D&A sub-component |
| `SellingGeneralAndAdministrativeExpense`/`GeneralAndAdministrativeExpense` | 539+829 | up to 12 | Opex line items |

Below the top ~40, volume drops into hundreds and then dozens of facts per tag — company-specific footnote disclosures, dimensional/segment breakdowns, one-off items. That's the inherent shape of XBRL: every company tags some things nobody else does. **This is not neglect; it's the real, expected shape of unstructured-by-nature disclosure data**, the same conclusion doc 22 already reached independently for dimensional/segment XBRL specifically.

## Checked the two most promising-looking finds before trusting them — one was real, one wasn't

Volume alone isn't evidence of value; checked company overlap for the two candidates that looked most like "free coverage wins":

- **`AllocatedShareBasedCompensationExpense` as an SBC alternate — disproven.** All 10 companies using it already have the primary `ShareBasedCompensation` tag mapped. Adding it as an alternate would add **zero** new company coverage — it's a naming variant some filers use, not a gap-filler. Correctly left unmapped.
- **`LongTermDebtNoncurrent` as a `total_debt` alternate — real, if modest.** 1 of 10 companies using this tag isn't already covered by the currently-mapped `LongTermDebt` tag. Small win in this 16-company sample; likely larger at 174-company scale, since a wider universe means more filers using the split current/noncurrent reporting convention instead of the combined tag.
- **`EarningsPerShareBasic` — same 16 companies as diluted EPS, zero *new* company reach**, but genuine new *data*: basic EPS is a real, useful standalone figure (e.g. comparing basic-vs-diluted spread is itself a dilution-quality signal), just not a coverage expansion in the company-count sense.

## What's actually worth curating next (ranked by verified value, not raw volume)

1. **`Goodwill`** (11 companies, entirely new concept) — directly closes doc 26's own named P2 gap ("Goodwill & Intangibles % of assets"), not a hypothetical use.
2. **Cash-flow-statement AR/Inventory/AP change tags** — a genuinely different concept from the balance-sheet snapshots already mapped for Debtor/Inventory/Payables Days. Enables a real cross-check: does the balance-sheet-implied change match what the company itself reported as the cash-flow adjustment? A quality-of-earnings signal, not just more data.
3. **`total_debt`'s alternate set widened** to include the current/noncurrent split tags — cheap (already-`sum`-mode composite, just add two more component tags), safe (checked live, doesn't double-count anything the combined tag already covers).
4. **`EarningsPerShareBasic`** as its own concept — cheap, single-tag, and enables a real basic-vs-diluted dilution-spread signal without needing a new fetch.
5. **`EffectiveIncomeTaxRateContinuingOperations`** — worth checking as a cross-validation for ROIC's internally-derived tax rate (`tax_expense / pretax_income`) before trusting either blindly.

Everything else in the top-40 list is real and could eventually matter (SG&A for expense-ratio analysis, amortization as a D&A sub-component, comprehensive income) but doesn't have a named product gap pulling for it the way Goodwill does — worth keeping as a ranked backlog, not building speculatively.

## The generalizable lesson

**"Utilization percentage" is the wrong metric to optimize toward.** A canonical-concept mapper's job is to capture the subset of tags that are *widely comparable across companies* — most of XBRL's long tail is deliberately NOT that, by the nature of free-form disclosure. Chasing utilization % as a target would mean mapping company-specific one-off tags that provide zero cross-company screening value, which is the opposite of what this product needs. The right question is never "how do we use more of the raw data" in the aggregate — it's "does this specific, real, checked tag close a specific, real, named product gap" — the same evidence-before-expansion discipline this project has applied at every other stage, just now applied to the mapping-coverage question itself.

Investigation method worth reusing: `scrooner-map unmapped-tags` (already built, doc 11) gives the ranked candidate list for free; the discipline that made this useful was checking company-overlap for each candidate live before recommending it, the same way `AllocatedShareBasedCompensationExpense` turned out to be a false lead that pure volume-ranking would have missed.
