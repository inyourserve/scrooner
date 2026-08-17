# Normalizer Day 4 — Fact Extraction

## Finding: ~5% of golden-8 datapoints trace to filings outside MVP scope

Before writing `facts.py`, scanned all 178,811 raw datapoints across the golden-8 (excluding TSM/ENB per doc 09's Day-7 scope note) for their `form` field. 8,986 (~5%) belong to forms not in `FORM_ALLOWLIST` (10-K/10-Q + amendments): 8-K (5,476), 424B2 (3,301), DEF 14A (163), 424B5 (30), S-8 (8), S-3/A (5), 424B8 (3).

### How it was found, and the decision

Cross-checked which *concepts* appear only via those non-allowlisted forms, to make sure skipping them wasn't dropping something the product needs: `ffd`/`cef`-taxonomy fund-fee-table data (from ARCC's 424B2 prospectus supplements — ARCC is BDC-like) and `ecd`-taxonomy executive-pay disclosures (from DEF 14A proxies). None are financial-statement line items doc 03's MVP needs. Decision: facts whose `accn` doesn't resolve to a filing already in `core.filing` are skipped and counted (`skipped_no_filing`), never silently dropped. Confirmed live: exactly 8,986 skipped, matching the pre-count precisely — no surprise gap.

## Finding: idempotent-looking upserts still bloat the table until vacuumed

Reran the whole extraction job a second time to confirm idempotency (same 169,825 written per company, identical stats). Row count matched exactly (`core.fact`: 169,825 both times) — but `pg_database_size` grew from 58 MB to 77 MB anyway.

### How it was found

`select n_live_tup, n_dead_tup from pg_stat_user_tables` showed 3,315 dead tuples after the rerun even though nothing changed logically. Postgres's `ON CONFLICT ... DO UPDATE SET value = excluded.value` still writes a new physical row version on every conflict (MVCC), leaving the old version as reclaimable dead space until vacuumed — true even when the new value is byte-identical to the old one.

### Fix

`VACUUM FULL core.fact` reclaimed it — final size 52 MB (row count unchanged at 169,825).

### Why it matters going forward

An idempotency check that only looks at row *count* can miss real budget consumption on a 500 MB free tier — repeated dev-loop reruns of any stage using `ON CONFLICT DO UPDATE` will quietly bloat the table until something vacuums it (autovacuum will eventually, but not necessarily before the next check). Worth a periodic `VACUUM` during active development on this stage, not just a row-count check, per doc 09's capacity section.

## Verification: reconciled against real filings, not just "it ran"

Doc 09's Stage 2d gate is "facts for at least 3 golden companies reconcile 1:1 against the actual filing, by hand." Queried three companies' reported figures directly against public record:
- AAPL Q1 FY2024 revenue: `$119,575,000,000` — exact match (`RevenueFromContractWithCustomerExcludingAssessedTax`), reported twice (original 10-Q filed 2024-02-02, plus a comparative in the following year's 10-Q) — both rows correct, both kept (Stage 2e's job to pick an authoritative one, not this stage's).
- MSFT Q3 FY2024 net income: `$21,939,000,000` — exact match, same original + comparative pattern.
- JPM FY2023 net income: `$49,552,000,000` — exact match, reported three times across three consecutive 10-Ks (as current-year, then twice more as a prior-year comparative).

All three stored as exact `Decimal` values (confirmed no floating-point drift) — `_load_json` parses with `parse_float=Decimal` specifically because Python's default JSON float parsing can lose precision on monetary values, which is exactly what `core.fact.value`'s `numeric` (not `double precision`) column type exists to prevent.

## Cross-stage consistency check

Zero `skipped_period_not_found` and zero `skipped_unmapped_unit` across all 178,811 raw datapoints — every period Stage 2b resolved and every unit Stage 2c resolved was actually sufficient for Stage 2d's needs, with nothing missing. This is a real (not assumed) confirmation that Days 2-3's extraction was exhaustive, not just "probably fine."
