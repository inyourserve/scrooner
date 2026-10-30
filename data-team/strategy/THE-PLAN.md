# THE PLAN (single canonical direction, 2026-10-24)

Owner: Dhairya. Status: APPROVED by the founder in the main session, 2026-10-24 ("yes all plan is approved"). Section 7's four decisions (approver policy, Q4 earnings figures, notes data sets, push permission) were not answered individually by that message and stay open until he answers them. Everything else in `data-team/strategy/` and `doc/data-moat/` is detail or history; if it conflicts with this page, this page wins. Running log of results: `doc/data-moat/team/PLAN.md`.

## 1. The bet
For the top 1,000 US companies (cohort v1.1, 2015 to date), every cell on a company page is either **a correct value that traces to a filing** or **a visible, evidenced reason**. We prove it one company at a time, then in batches of 10. We never claim "100% correct"; we claim "checked against the filing, error rate published".

## 2. Architecture (the hybrid)
1. **Values:** SEC `companyfacts` (93.4% of face facts exact in the pilot; 0 standard face facts missing).
2. **Company slot records (the mapper):** per company, per statement line, the tags that make up the total in THAT company's filing (from its presentation/calculation tree), versioned by effective period, taxonomy version and evidence accession. Table: `analytics.company_slot_record`. Replaces vocabulary patching.
3. **Format gate:** on every new 10-K/10-Q compare the statement fingerprint with the slot record. Same: map from the API. Changed: hold affected cells ("format changed, under review"), read the filing, propose a record update, check, release.
4. **Filing reads** for what the API drops: custom tags (6.4% of face facts), dimensions, note facts via SEC's Financial Statement and Notes sets.
5. **Derivation layer** with proof stamps (`derived`, rule id, input facts, arithmetic). Per-share values are never derived; additive Q4/quarters only on the same basis.
6. **Reason layer** (8 cell states) and **certification** (invariant suite + Verifier filing checks, state ladder to `certified`).

## 3. The two numbers we report
- **Certified companies:** 0 today. Goal: MU first, then batches of 10.
- **Reasonless blanks:** 13,349 at the 2026-10-20 baseline. Goal: 0.
Also reported: wrong-value rate in Verifier samples. Nothing else counts as progress.

## 4. Quality bar (stated once)
Nothing reaches a page unless it passed a **Verifier filing check with zero wrong shown values** and the certification suite; every value-changing rule ships behind a flag with a dry-run and a rollback. A hidden value always carries a reason.

## 5. Lanes (at most 3 agents at once)
- **A. Core engine:** slot-record builder, MU first, replaying the 16 known-wrong cells (scrooner-25).
- **B. Root fixes, in order:** (1) the live total-liabilities bug in `resolve_balance_sheet_identity_fallback` (5,252 cohort cells, 185 companies); (2) split re-base + per-share derivation ban; (3) reason rules (7,724 pending closures need audits); (4) total debt via slot records; (5) common equity + W10; (6) interest expense (new 2024 tag, ~1,500 companies).
- **C. Verify and release:** Verifier samples each fix; Release Manager merges; certification round 4 is frozen.
Stopped until the cohort is done: non-cohort companies, new studies and cards, anything without a cohort wrong value behind it.

## 6. Gates (nothing ships before these)
Push path to `main` open; migrations 0098-0100 on `main`; four scheduled workflows green; quiet window; clock G set. 0096/0097 are applied.

## 7. Decisions only the founder can make
1. Approver policy: DECIDED 2026-10-25, confirmed by the founder in the main session: agents only; the approver is never the preparer; the founder signs only novel definition calls. (Closed.)
2. Show unaudited 8-K Q4 earnings figures (labelled)? 
3. Load SEC Notes data sets for the cohort after a one-month size pilot?
4. Push permission for the Release Manager.

## 8. Detail (appendices, read only when needed)
Operating standard: `data-team/DATA-MOAT-OPERATING-STANDARD.md`. Supporting detail: `team/EDGAR-ATLAS-2026-10-24.md`, `team/SCROONER-V2-DESIGN-PROPOSAL-2026-10-24.md`, `team/OPEN-SOURCES-FOR-COVERAGE-2026-10-24.md`, `team/DERIVATION-CATALOG-2026-10-24.md`, `team/AS-FILED-PILOT-2026-10-24.md`, `ONE-COMPANY-100-ENGINEERING/PRODUCT-2026-10-24.md`, `EXCEPTION-RULE-REGISTER-DESIGN-2026-10-24.md`, `49-FINAL-PLAN-SIGNED-2026-10-22.md`, `FREEZE-REGISTER-2026-10-22.md`, `BLOCKER-LIST-2026-10-23.md`, `team/DATA-CONSUMPTION-AUDIT-2026-10-24.md`.

## 9. Lowering data consumption (measured, audit 2026-10-24)
Biggest facts: Storage bucket `raw` is 94 GB (companyfacts 79 GB in 44,630 objects but only 8,829 distinct; 92% of the last 9 days' fetches were byte-identical repeats; growth 7-10 GB/week); DB 47 GB (core.fact 32 GB, 76.7M rows, 10.6M dead tuples, never autovacuumed); only 22.5% of core.fact is cohort 2015+ and 5.9% is cohort 2015+ on mapped tags. Levers, in order: (1) hash-dedupe before upload and refetch only on a new accession (saves 63-68 GB of Storage, ~90% of companyfacts fetches; deleting old duplicates needs explicit authorization); (2) reprocess by watermark (new accession since last normalize) instead of the 10-day window: 70-125 min to about 10-20 min (assumed), which removes the stage timeouts; (3) autovacuum tuning and dropping two never-scanned indexes (2.2 GB) after any archive; (4) archive pre-2015 (16.8M rows, ~7 GB); a cohort-2015+ hot table only after the founder confirms scope (saves ~19.8 GB, assumed; risk: new mappings come from today's unmapped tags); (5) drop repeat non-authoritative copies (up to ~14 GB) only after a dry-run (7% of keys have no authoritative copy: never delete blindly). Cost impact is small (disk ~$0.125/GB-month, assumed); the real gain is runtime and reliability. Cannot lower: the 5.2k-company product universe (9.3 GB), the three hot indexes, the latest raw payload per CIK, raw immutability for changed filings.
