# 09b — Normalizer Definition-of-Done: Evidence Report

Day 7's deliverable (doc 09): *"End-to-end proof against doc 09's Definition of Done... demonstrated, not asserted."* This doc is that proof — a consolidation of real evidence already gathered during Days 1–7, plus two checks (incremental-processing isolation, §7) run fresh today specifically because the DoD names a property no prior day had actually exercised.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When the Normalizer's implementation changes in a way that would invalidate this evidence

## Doc 09's exact Definition of Done, quoted verbatim

> **Output:** for every golden-set company — canonical period records (with correct start/end dates and duration/instantaneous type), canonical unit records, fact records under original issuer tag names, linked to period + unit + filing, restatement history preserved (not overwritten), derived Q4 values explicitly flagged as derived, full lineage: every fact traceable back to its raw object and filing.
>
> **Operationally, it can:** reprocess a company from raw data and get the same normalized output (determinism); handle a non-calendar fiscal year correctly; handle a restated company without losing the original figures; flag, not silently resolve, any conflicting duplicate fact it can't confidently reconcile; be re-run incrementally as new raw data arrives, without reprocessing the entire universe every time.

## Base output shape — every golden company, real rows

| Ticker | CIK | Listings | Filings | Periods | Facts | Derived (Q4) |
|---|---|---|---|---|---|---|
| JPM | 0000019617 | 9 | 137 | 351 | 49,363 | 1,285 |
| NKE | 0000320187 | 1 | 130 | 222 | 20,385 | 419 |
| AAPL | 0000320193 | 1 | 132 | 299 | 24,491 | 474 |
| MSFT | 0000789019 | 1 | 137 | 304 | 31,988 | 1,087 |
| ENB | 0000895728 | 16 | 60 | 202 | 0 *(scope-excluded)* | 0 |
| TSM | 0001046179 | 2 | 26 | 56 | 0 *(scope-excluded)* | 0 |
| ARCC | 0001287750 | 1 | 93 | 103 | 5,530 | 110 |
| XYZ (Block) | 0001512673 | 2 | 43 | 144 | 18,360 | 410 |
| GOOGL | 0001652044 | 4 | 46 | 165 | 20,649 | 471 |
| RDDT | 0001713445 | 1 | 10 | 45 | 3,456 | 141 |

Totals: 10/10 companies → 1 `core.company` row each; 38 listings; 814 filings; 1,891 periods; 28 canonical units (global); 1,976 canonical concepts (global); **174,222 facts** (169,825 reported + 4,397 derived); DB size **53 MB** post-vacuum (10.6% of the 500 MB free-tier budget). ENB/TSM correctly show 0 facts — excluded from fact extraction per this doc's own Day-7 scope note, pending doc 02's open 20-F/40-F decision; their identity/period/unit structure is populated and correct.

---

## Output requirements

### Canonical period records, correct start/end + duration/instant type — PASS

1,891 `core.period` rows. Structural check: **0** rows where `period_type='instant'` and `start_date≠end_date`, and **0** where `period_type='duration'` and `start_date=end_date` (Day 2, reconfirmed after Day 7's 59 new derived-Q4 periods). Fiscal-year/quarter derivation spot-checked exactly against real public fiscal calendars for AAPL (Sept FYE), MSFT (June FYE), NKE (May FYE), and JPM (calendar FYE) — see `doc/learnings/normalizer-day-02-periods.md`.

### Canonical unit records — PASS

28 canonical units from 29 raw XBRL unit strings (one real case-collision, `Segment`/`segment`, correctly merged; deliberately did not merge different custom units like `Store` vs `Job` counts). Zero case-duplicate rows confirmed directly. See `doc/learnings/normalizer-day-03-units.md`.

### Fact records under original issuer tags, linked to period+unit+filing — PASS

169,825 reported facts (Day 4) + 4,397 derived facts (Day 7) = 174,222, every row referencing `concept_id`/`unit_id`/`period_id`/`filing_id` via `NOT NULL` foreign keys (schema-enforced, not just convention). Concept tags preserved verbatim (`RevenueFromContractWithCustomerExcludingAssessedTax`, not "Revenue"). Reconciled exactly against public record for AAPL, MSFT, and JPM (Day 4); zero cross-stage lookup misses across all 178,811 raw datapoints processed (`skipped_unmapped_unit=0`, `skipped_period_not_found=0`).

### Restatement history preserved, not overwritten — PASS

43 amendments found across the golden-10; 36 linked to their original filing (7 correctly left unmatched — pre-2002 filings with no captured original, not guessed at); 681 fact pairs superseded. Verified directly: every superseded original row remains queryable with its original value intact (`is_authoritative=false`, row never deleted), every amendment row correctly `is_authoritative=true` with `supersedes_fact_id` populated. Checked against both a routine case (ARCC's 5 cover-page-update `10-K/A`s) and genuine material restatements (JPM's EPS $1.31→$1.19/$1.20; AAPL's FY2008 assets $39.572B→$36.171B). See `doc/learnings/normalizer-day-06-restatements.md`.

### Derived Q4 values, explicitly flagged as derived — PASS

4,397 facts with `is_derived=true`; 169,825 with `is_derived=false` — clean, unambiguous split. Verified by hand: AAPL FY2024 revenue, `FY $391,035,000,000 − Q1 $119,575,000,000 − Q2 $90,753,000,000 − Q3 $85,777,000,000 = $94,930,000,000`, matching Apple's actual reported Q4 FY2024 revenue exactly. Never overwrites a genuinely reported value — verified against MSFT's directly-disclosed quarterly dividends (96 cases correctly left alone, not re-derived). See `doc/learnings/normalizer-day-07-derived-q4.md`.

### Full lineage: every fact traceable to its raw object and filing — PASS

`raw_object_id` and `filing_id` are `NOT NULL` on every `core.fact` row (schema-enforced) — a derived fact's lineage anchors to the FY fact's own filing/raw object, with its Q1-Q3 inputs always reconstructable via `(company, concept, unit, fiscal_year)`. Every `core.filing` row carries `raw_submission_id`, tracing filing metadata itself back to the exact `raw.sec_submissions` fetch it was parsed from.

---

## Operational requirements

### Determinism (reprocess → same output) — PASS

Every one of the 7 stages independently reran with identical stats: identity (814 filings both times), periods (1,832 both times), units (28 both times), facts (169,825 both times), dedupe (48,360/45,182/3,178 both times), restatements (36/7/681 both times), Q4 derivation (14,907/4,397/174/10,336 both times).

### Non-calendar fiscal year handled correctly — PASS

AAPL (Sept 26 nominal FYE), MSFT (June 30), NKE (May 31) all spot-checked exactly against real public fiscal-quarter-end dates (Day 2) — including AAPL's Q1–Q4 FY2024 boundaries reproducing Apple's actual reported dates to the day.

### Restated company without losing original figures — PASS

Same evidence as "Restatement history preserved" above — ARCC's full `EntityPublicFloat` history (4 original + 4 amendment rows) directly queried and confirmed intact, correctly ordered, both flags correct.

### Flag, don't silently resolve, unreconcilable conflicts — PASS

3,178 of 48,360 duplicate `(company, concept, unit, period)` groups (6.57%) genuinely disagree — every row in each such group marked `is_authoritative=false`, fully queryable via a documented query (`normalizer/dedupe.py::conflict_summary`), never resolved by guessing. Verified against a known real conflict (JPM's `DerivativeNotionalAmount`, a small silent revision with no `10-K/A` filed) and a full consistency check across all 48,360 groups (zero with a wrong authoritative-row count).

### Re-run incrementally without reprocessing the entire set — PASS

Live-demonstrated today, not assumed from reading the code: snapshotted every company's `core.fact` row count, reran fact extraction scoped to a single CIK (RDDT), and confirmed every other company's count was byte-for-byte unchanged. Every stage accepts a `ciks` parameter and writes are scoped strictly to `company_id` (or, for the two global lookups `core.unit`/`core.concept`, purely additive upserts) — the same design that made this test pass by construction is what any future incremental run (new company, or a company with fresh raw data) will rely on.

---

## What this evidence does not cover

- **Full-universe or wider-than-golden-10 coverage** — deliberately out of scope per doc 09's Supabase free-tier capacity decision (doc 02). This DoD is scoped to the golden-10, as doc 09 itself specifies.
- **20-F/40-F fact extraction** (TSM, ENB) — deliberately excluded pending doc 02's open decision. Their identity/period/unit structure is correct and complete; no fact-level claim is made for them.
- **Concept-to-canonical-metric mapping** — explicitly Mapper's job (Phase 3), not this phase's. A `core.fact` row still carries the issuer's original tag, not a canonical Scrooner concept.

## Conclusion

Every item in doc 09's Definition of Done — 6 output requirements, 5 operational requirements — is demonstrated with real, checked evidence from Days 1–7, not self-reported. Per doc 09's own promotion rule, its status line moves from Draft to **Canonical** as of this report. The team moves to Part 3, Mapper & Metrics Engine, next.
