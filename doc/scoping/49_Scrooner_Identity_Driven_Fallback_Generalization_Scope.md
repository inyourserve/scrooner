# Identity-Driven Fallback Generalization — Scope

**Status: Draft scope for evaluation, 2026-10-04. Nothing built. Prompted directly by a live question: "resolve-statement-fallbacks is a sub-tree of revenue — why not the same scalable sub-tree for all the metrics?"**

## 1. What already exists (verified by reading the code, not assumed)

Two separate, independently-built mechanisms already encode overlapping "one financial line equals a combination of others" relationships:

**`mapper/concept_fallback.py`'s `ARITHMETIC_FALLBACKS`** — a declarative list of `(resolved_concept, primary_tag, minuend, subtrahend, min_value_floor)` tuples, consumed generically by one function, `resolve_arithmetic_fallback()`. Currently exactly 3 entries:

```python
("gross_profit_resolved", "gross_profit", "revenue", "cost_of_revenue_resolved", 0),
("cost_of_revenue_resolved", "cost_of_revenue", "revenue", "gross_profit", 0),
("operating_expenses_resolved", "operating_expenses", "gross_profit_resolved", "operating_income", None),
```

This is **already the generalized, scalable mechanism** the user is asking about — it is not three hand-written functions, it's one function reading a table. The real gap is that the table only has 3 rows. Verified live this session: running it just now produced 215,270 / 208,000 / 275,505 newly-filled rows across the active population, purely from these 3 entries.

**`sanity/accounting_identity.py`'s `IDENTITIES`** — a separate declarative list of `Identity(name, kind, target, terms, adjustments, tolerance, basis)` tuples, used only for *validation* (does `target` actually equal the signed sum of `terms` + `adjustments`, within `tolerance`). Currently 6 identities, including two `KIND_EQUALS` ones that are structurally identical in shape to what a fallback needs:

```python
Identity(name="balance_sheet", target="total_assets",
         terms=(("total_liabilities", 1), ("stockholders_equity", 1)), ...)
Identity(name="net_income", target="net_income",
         terms=(("income_before_tax", 1), ("income_tax_expense", -1)), ...)
```

**These two lists currently duplicate the same kind of knowledge in two different shapes, maintained separately, for two different purposes (check vs. fill).**

## 2. The idea

`IDENTITIES` has already been validated against real company data (doc 48, `analytics.identity_check_score`) — it's not a guess, it's a measured, trusted relationship with a known real-world pass rate per identity. The proposal: **use the same identity definitions to drive both the existing validator and a generalized gap-filler**, instead of maintaining `ARITHMETIC_FALLBACKS` as a separate, narrower, hand-curated list.

Concretely, for any `KIND_EQUALS` identity with exactly one missing term and all others present, solve for the missing term algebraically and write it into that term's own `_resolved` concept, the same additive, never-overwrite-a-real-value discipline `resolve_arithmetic_fallback()` already uses.

## 3. Candidate new fallback relationships (from identities already measured, not proposed blind)

| Target (if missing) | Derivable from | Known real pass rate (doc 48) | Caveats already documented |
|---|---|---|---|
| `total_assets` | `total_liabilities + stockholders_equity` (+ NCI/temp equity adjustments) | ~93-95% | NCI/temporary-equity adjustments must be included or this undercounts for companies with those line items |
| `total_liabilities` | `total_assets - stockholders_equity` | ~93-95% (inverse direction, not separately measured) | Same adjustment terms apply in reverse |
| `stockholders_equity` | `total_assets - total_liabilities` | ~93-95% (inverse direction) | Same |
| `income_before_tax` | `net_income + income_tax_expense` (+ disc. ops / NCI / equity-method adjustments) | ~96-100% | Adjustment terms are real and sometimes material (doc 48's own subset-search fix) |
| `net_income` | *(already resolved directly today, not usually missing — low priority)* | ~96-100% | — |

**Not proposed:** `revenue_nonnegative`, `current_assets_within_total`, `cash_within_total` — these are inequalities (`KIND_AT_MOST`/`KIND_NONNEGATIVE`), not equalities, and cannot be algebraically solved for a missing term. Only the two `KIND_EQUALS` identities are real candidates today.

## 4. Real risks to resolve before building, not after

1. **Direction matters for pass-rate trust.** Doc 48's measured pass rates are for checking the identity as originally defined (solve for `target`). Solving for a *different* missing term (e.g., `total_liabilities` instead of `total_assets`) algebraically re-arranges the same equation, so the real-world failure rate should be identical — but this has NOT been separately verified live, only asserted here by algebra. Must spot-check before trusting.
2. **Adjustment terms are not optional.** `balance_sheet`'s NCI/temporary-equity adjustments and `net_income`'s discontinued-ops/NCI/equity-method adjustments are real and sometimes material (that's *why* doc 48 added them, after finding real companies where omitting them produced a false identity failure). A naive fallback using only the bare `terms` tuple without `adjustments` would reproduce the exact false-gap class this project has hit and fixed multiple times (`CostsAndExpenses`, `LongTermDebtNoncurrent`, etc.) — the fix must read `adjustments` too, and only derive when the adjustment inputs are either present or confirmed zero/not-applicable for that company.
3. **Tolerance, not exact equality, is correct in the checker — but a fallback needs an actual number, not a tolerance band.** Deciding what to do when the "solve for X" result would only be approximately consistent with a third redundant data point (if one exists) needs a design decision: trust the algebra unconditionally, or only derive when corroborated.
4. **Order dependency, same shape `ARITHMETIC_FALLBACKS` already documents.** `operating_expenses_resolved`'s current entry depends on `gross_profit_resolved` already being populated — any new identity-driven entries need the same explicit ordering discipline, not implicit.
5. **Unifying the two lists is itself a refactor with real migration cost** — `IDENTITIES` and `ARITHMETIC_FALLBACKS` have different dataclass shapes (`Identity` has `kind`/`adjustments`/`tolerance`/`basis`; `ARITHMETIC_FALLBACKS` tuples don't). A full unification is a larger, separate decision from just "add 2-4 new fallback entries using the existing `ARITHMETIC_FALLBACKS` shape, informed by `IDENTITIES`' already-validated relationships" — the latter is far lower-risk and could ship first.

## 5. Recommended next step (not started)

**Low-risk first move:** add `total_assets_resolved`/`total_liabilities_resolved`/`stockholders_equity_resolved` and `income_before_tax_resolved` as new `ARITHMETIC_FALLBACKS` entries (reusing the existing mechanism as-is, not a refactor), explicitly including the adjustment terms as additional optional minuends/subtrahends, and measure the real bounded gap-fill count + a coexistence/accuracy check against `identity_check_score`'s existing pass-rate data before shipping — same discipline as every tag addition this project has made.

**Deferred, bigger decision:** whether to actually unify `IDENTITIES` and `ARITHMETIC_FALLBACKS` into one declarative source so future identities automatically get both a validator and a fallback for free. That's a real architectural call, not a quick addition — worth a separate decision once the low-risk version above is proven.

**Not in scope here:** `KIND_AT_MOST`/`KIND_NONNEGATIVE` identities (not invertible), and any identity whose adjustment terms aren't yet confirmed reliably available as their own resolved concepts.
