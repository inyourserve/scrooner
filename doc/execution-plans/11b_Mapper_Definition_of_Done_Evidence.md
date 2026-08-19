# 11b — Mapper & Metrics Engine Definition-of-Done: Evidence Report

Day 6's deliverable (doc 11): *"Full Definition of Done demonstrated with real evidence, not asserted."* This doc is that proof — a consolidation of evidence already gathered during Days 1–5, plus checks run fresh on Day 6 specifically because the DoD names properties no prior day had actually exercised (incremental-reprocessing isolation, an independent external cross-check via `edgartools`, and full source-to-`core.fact` lineage).

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When the Mapper's implementation changes in a way that would invalidate this evidence

## Doc 11's exact Definition of Done, quoted verbatim

> **Output:** every canonical concept the 12 EDGAR-only metrics need resolves to the correct tag(s), including taxonomy-drift and composite-concept cases; all 18 metrics formally defined and formula-versioned, including ROIC's previously-open detail; 12 EDGAR-only metrics computed correctly for every reported period, hand-reconciled against real figures for at least 3 companies; TTM and growth-window values correct, hand-reconciled against manual math; full lineage: every `metric_value` traceable back to the exact `core.fact` row(s) that produced it; nulls appear exactly where an authoritative input is missing — never a silent wrong guess.
>
> **Operationally, it can:** reprocess a company and get the same computed metrics (determinism); handle a company whose primary concept tag differs by industry (JPM) without special-casing it outside the mapping table; handle a composite concept whose component tags vary by company (Total Debt); leave a metric null, with a reason, rather than guess when an input is unresolved or missing; be re-run incrementally as the Normalizer produces new facts, without recomputing the entire golden set every time.

## Base output shape — golden-8, real rows

| Table | Rows |
|---|---|
| `analytics.canonical_concept` | 17 |
| `analytics.concept_mapping` | 32 (28 approved, 3 provisional, 1 rejected) |
| `analytics.canonical_fact` | 7,904 |
| `analytics.metric_definition` | 20 (14 EDGAR-only computable now, 6 `requires_price=true`, blocked on Company Master) |
| `analytics.metric_definition_input` | 39 |
| `analytics.metric_value` | 6,058 (2,271 point-in-time + 1,369 growth + 440 TTM ROIC/ROE, remainder correctly null) |

DB size: **58 MB** post-Mapper (11.6% of the 500 MB free-tier budget), up from Normalizer's 53 MB — the `analytics` schema added ~5 MB for 8 fact-bearing golden companies, confirming Mapper-phase storage growth is small relative to the raw/core layers underneath it.

TSM, ENB excluded throughout, same as the Normalizer — no `core.fact` rows exist for them (20-F/40-F scope still open per doc 02).

---

## Output requirements

### Every canonical concept resolves to the correct tag(s), including taxonomy-drift and composite cases — PASS

17/17 canonical concepts mapped via 32 curated `concept_mapping` rows. Taxonomy drift: AAPL's revenue resolves smoothly across all 3 of its historical tags (`SalesRevenueNet` → `Revenues` → `RevenueFromContractWithCustomerExcludingAssessedTax`) with no discontinuity at either ASC-606 transition point (Day 2). Industry-specific tags: JPM's bank-style `InterestAndDividendIncomeOperating` resolves without any special-casing outside the ordered mapping list (Day 1). Composite concepts: NKE (3-tag sum), ARCC (single tag, the control case), and Block (a third, different 2-tag combination) all sum Total Debt correctly per company (Days 1–2). Coverage: 113/136 (83%) of (company, concept) pairs resolve for the golden-8; the remainder are industry-structural nulls (banks/BDCs genuinely lack a `revenue`/`current_assets` concept) or flagged gaps, not silent failures (Day 1).

### All 18 metrics formally defined and formula-versioned, ROIC's detail pinned — PASS

20 `metric_definition` rows (18 product-facing metrics; Revenue/EPS Growth each split into YoY + 3Y-CAGR variants) at `formula_version=1`, 39 input links, 14 EDGAR-only / 6 price-dependent — matching doc 02's counts exactly (Day 3). ROIC's tax-rate/invested-capital formula pinned with live evidence: naive quarterly ×4 annualization produced an implausible 127.8% for AAPL vs a sane 31.95% single-quarter figure, confirmed structural (shared with ROE) and not a resolver bug — both restricted to FY-only in Stage 3d, then properly extended via Stage 3e's trailing-4-quarter TTM (Day 3, Day 5).

### 12 EDGAR-only metrics computed correctly, hand-reconciled against ≥3 companies — PASS

2,271 point-in-time values computed, 1,187 correctly null, across the golden-8's 10 EDGAR-only non-growth metrics (the other 2 EDGAR-only metrics are the growth pair, computed in Stage 3e). Hand-reconciled at the time of Day 4 against AAPL (margins and FCF exact matches; ROE 164.6%, ROIC 28–64% across periods with complete data — both sane) and MSFT (current ratio 1.2–1.4). Re-verified independently on Day 6 via `edgartools` (doc 12), a second, unrelated data path: AAPL FY2025 `net_margin` — Scrooner's stored value `0.2691506412181823861438241450` vs `112,010 / 416,161` computed directly from `edgartools`' own pulled income statement, `0.269150641218182386143824144982` — exact match to full decimal precision; FY2024 likewise (`0.2397125576994386691728361911` vs `0.239712557699438669172836191134`). A fourth and fifth company's numbers, independently cross-checked against a source outside this project's own pipeline.

### TTM and growth-window values correct, hand-reconciled — PASS

1,369 growth values, 440 TTM ROIC/ROE values. AAPL FY2024 revenue growth (2.0220% YoY, 2.2470% 3Y CAGR) matches manual math to the digit. Strongest check of the whole phase: TTM ROIC at a Q4 boundary (Stage 3e) and FY ROIC (Stage 3d, computed by an entirely separate, never-cross-calling code path) agree to full decimal precision for AAPL FY2021 — `0.6432163420699880117275573775` both ways (Day 5).

### Full lineage: every `metric_value` traceable to the exact `core.fact` row(s) — PASS

Checked two ways. (1) Global invariant, all rows: `mapper/validate.py`'s `lineage_integrity()` — every `source_fact_ids` entry across `analytics.canonical_fact` and `analytics.metric_value` resolves to a real `core.fact` row; **0 dangling references** in either table (Day 6, run against the full golden-8, not sampled). (2) Manual spot check: AAPL FY2024 `net_margin`'s 2 source facts resolve to real, `is_authoritative=true` `core.fact` rows (`NetIncomeLoss=$93,736M`, `RevenueFromContractWithCustomerExcludingAssessedTax=$391,035M`); AAPL FY2024 ROIC's 5 present source facts (of 6 expected — `total_debt` genuinely missing) likewise all resolve to real, authoritative rows, and the partial lineage is preserved on the row even though the metric itself is correctly null (Day 6).

### Nulls appear exactly where an authoritative input is missing, never a silent wrong guess — PASS

Global invariant checked directly (not inferred): `mapper/validate.py`'s `non_authoritative_leaks()` — **0** `analytics.canonical_fact` rows and **0** `analytics.metric_value` rows cite a non-authoritative `core.fact`, across the entire golden-8 (Day 6). Concretely: AAPL FY2024 ROIC is null with `is_null_reason='incomplete:invested_capital_add'`, correctly reflecting a genuine Stage 2e conflict on `total_debt` rather than silently computing from `stockholders_equity` alone (the Day 4 bug this discipline exists to prevent — see below).

---

## Operational requirements

### Determinism (reprocess → same output) — PASS, but only after a real bug was found and fixed

Full golden-8 rerun of all three write stages (`calculate`, `growth`, `ttm-returns`) on Day 6 reproduced Days 4–5's exact totals: 2,271/1,187 point-in-time, 1,369/433 growth, 440/358 TTM. But getting here required fixing a genuine bug first — see "Bug found and fixed on Day 6" below. Determinism at the full-set level was never actually in question; what Day 6 discovered is that determinism at the *single-company* level was silently broken until fixed.

### Handles an industry-specific primary tag (JPM) without special-casing — PASS

Same evidence as the taxonomy-drift/industry item above — JPM's bank-style revenue tag resolves purely through the ordered `concept_mapping` list, no branching code anywhere in `mapper/`.

### Handles a composite concept whose component tags vary by company — PASS

Same evidence as above — NKE/ARCC/Block's three different Total Debt shapes, one summation mechanism.

### Leaves a metric null, with a reason, rather than guess — PASS

Same evidence as the nulls item above, plus the Day 4 per-role completeness-check fix this discipline depends on structurally, not just by convention.

### Re-run incrementally without recomputing the entire golden set — PASS, after fixing what it found

Live-demonstrated on Day 6: snapshotted every company's `analytics.metric_value` row count, reran `calculate` scoped to a single CIK (RDDT, cik `0001713445`), and checked the result.

**First attempt failed the test it was meant to pass.** RDDT's row count dropped from 243 to 143 — a loss of exactly 100 rows, matching Day 5's RDDT growth+TTM total (72+28) to the row. Root cause: `calculate.py`'s delete statement was scoped only by `company_id`, not by which `metric_definition_id`s Stage 3d actually owns — deleting *all* of a company's `metric_value` rows before reinserting only its own 10-metric subset, silently destroying Stage 3e's previously-computed growth/TTM rows for that company on every single-company rerun. All 7 other companies were untouched (correct), but RDDT itself was not (incorrect) — the exact asymmetry a naive read of "other companies are fine" would have missed.

Fixed in two steps, because the first fix was itself incomplete: (1) scoped the delete to `metric_definition_id = any(target_ids)`, which fixed 72 of the 100 lost rows (growth) but not the remaining 28 (TTM ROIC/ROE) — because `roic`/`roe` share the *same* `metric_definition_id` between Stage 3d's FY rows and Stage 3e's TTM rows, distinguished only by `period_label`. (2) added `and period_label != 'TTM'` to the delete, mirroring the exclusion `ttm.py`'s own `compute_ttm_returns` delete already used in the opposite direction (`and period_label = 'TTM'`). Re-ran the isolation test a third time: RDDT's count returned to 243 (including its 28 TTM rows, individually reconfirmed), and every other company's count remained byte-for-byte unchanged throughout all three attempts.

This is the single most consequential finding of Day 6 — see `doc/learnings/mapper-day-06-validation.md` for the full writeup and the generalized lesson.

---

## Bug found and fixed on Day 6

**Unscoped-then-under-scoped delete in `calculate.py` silently destroyed another stage's data on rerun.** Not caught by Days 4–5's own verification (both days checked *that day's* output was correct, never checked what a rerun would do to *other* stages' prior output) — only surfaced because Day 6 explicitly tested the "re-run incrementally... without recomputing the entire golden set" operational property named in doc 11's own Definition of Done, rather than assuming it from code review. Fixed in `pipeline/src/scrooner_pipeline/mapper/calculate.py`; full golden-set data restored and re-verified idempotent. See learnings entry for the generalizable lesson about shared-table ownership boundaries.

---

## What this evidence does not cover

- **Full-universe or wider-than-golden-10 coverage** — deliberately out of scope; doc 11's own "Scaling concept mapping beyond the golden set" section already addresses the path there without reopening doc 02's still-open wider-coverage decision.
- **20-F/40-F concept mapping** (TSM, ENB) — deliberately excluded, pending doc 02's open decision, same as the Normalizer.
- **The 6 price-dependent metrics' actual computation** — formally defined and formula-versioned here, but genuinely blocked on Company Master (Part 4)'s market-price source, not this phase's job to unblock.
- **Screen predicate evaluation** — Screener Engine's job (Part 4/5), not this one's.

## Conclusion

Every item in doc 11's Definition of Done — 6 output requirements, 5 operational requirements — is demonstrated with real, checked evidence from Days 1–6, not self-reported, including one requirement (incremental reprocessing) that failed on first real test and was fixed before being marked done. Per doc 11's own promotion rule, its status line moves from Draft to **Canonical** as of this report. The team moves to Part 4, Company Master / Market Data, next.
