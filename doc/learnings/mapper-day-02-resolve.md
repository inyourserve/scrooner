# Mapper Day 2 — Canonical Fact Resolution

## A third real correctness bug, caught by verifying the resolver's own output

Day 1 already caught two mapping bugs before any resolver code existed. Day 2 built the resolver (`mapper/resolve.py`) and, while checking its output against real numbers (doc 11's own stated Day 2 gate — "NKE/ARCC/Block's debt combinations sum correctly"), found a third: Block's `OtherLongTermDebtNoncurrent` — marked `provisional` on Day 1 specifically pending this check — tracks 70-100% of `LongTermDebt`'s own value across every period checked, including one quarter where the two are *exactly* equal. A genuinely separate additive debt category (compare `SecuredDebtCurrent`, consistently 2-10% of the total) doesn't look like that; this looks like the same debt facility reported under two different tags across filing vintages.

**Fix:** downgraded to `rejected`. Re-verified: Block's total debt now sums `LongTermDebt + SecuredDebtCurrent` only, and the values move sensibly period to period.

## A fourth bug, this time in the resolver's own idempotency, not the mapping data

Reran the resolver after the fix above to confirm idempotency (the established habit at this point) and found the row count didn't match: `analytics.canonical_fact` had 7,907 rows, but the resolver had just reported resolving 7,904. Investigated instead of assuming a logging discrepancy — found 3 stale Block rows still citing the now-rejected tag.

**Why:** the resolver's write step was upsert-only (`INSERT ... ON CONFLICT DO UPDATE`). For most periods, rejecting a tag just means a rerun resolves that period differently and overwrites the old row. But 3 specific Block quarters (2022 Q1-Q3) had *only* `OtherLongTermDebtNoncurrent` reporting debt data — no `LongTermDebt`, no `SecuredDebtCurrent` for those exact periods. Once that tag was rejected, the rerun had nothing left to resolve for those periods at all, so it never touched those rows — leaving the old, now-invalid value sitting in the table indefinitely, invisible unless someone thought to check the row count against the resolver's own reported total.

**Fix:** the resolver now deletes a company's entire `canonical_fact` row set before reinserting, every run — same truncate-and-reload discipline the Collector already applies to `raw.company_universe`. A mapping change (approving a new tag, rejecting an old one) can never again leave orphaned data behind, regardless of which specific periods happen to lose their only qualifying source.

## Verification, not just re-running until numbers looked plausible

- NKE, ARCC, Block's total_debt all spot-checked component-by-component against the real tags and values that produced them (not just the final number) — ARCC's is cleanly `LongTermDebt` alone every period, confirming the "simple case" control worked as expected.
- AAPL's revenue resolution reproduces the real ASC 606 taxonomy transition exactly: `SalesRevenueNet` through FY2015, one transition year to `Revenues` in FY2016, `RevenueFromContractWithCustomerExcludingAssessedTax` from FY2017 on — smooth values, no artificial jump at the tag switchover.
- Zero `canonical_fact` rows cite a non-authoritative `core.fact` row (checked directly, not assumed from the `WHERE is_authoritative` clause alone).
- `unresolved_concepts=57` from the resolver matches Stage 3a's coverage-report count exactly — a real cross-stage consistency check, not just "both numbers looked reasonable."
- Reran after the idempotency fix: row count (7,904) now matches the resolver's own reported total exactly, and zero rows cite a rejected mapping.

## Why it matters going forward

Two different kinds of bugs this session, caught two different ways: the mapping-data bug (Block's debt tag) was caught by checking the *values* the resolver produced against real numbers; the idempotency bug (stale rows) was caught by checking the *row count* against the resolver's own log output, something neither Day 1's design nor the resolver's own success message would have surfaced on its own. "The resolver ran and logged a plausible-looking summary" was not sufficient evidence either time — matches the standing lesson from every prior day on this project, still finding new shapes to apply to.
