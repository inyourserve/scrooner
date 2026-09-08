# SEC Frames self-consistency checker (2026-09-08)

Built by explicit user direction ("high impactful task") following doc 45's recommendation. A fundamentally different check than anything else built this session: `sanity/yfinance_check.py` and `yfinance_financials/` both ask "does our number agree with an *independent third party*." This asks "does our number agree with **SEC's own bulk-served copy of the identical filing**" — a re-fetch of the ground truth, not a second opinion. A real mismatch here is much stronger evidence of a bug in *our own* pipeline than any yfinance disagreement could be.

## What it is

`https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json` returns **every** SEC filer's value for one (tag, period) combination in a single request — verified live before building: 1,696 companies for `us-gaap:Revenues` CY2026Q1, 5,543 for `us-gaap:Assets` CY2026Q1I (instant concepts need an `I` suffix on the period code; duration concepts don't — both formats confirmed against real responses, not assumed from docs). Fetched via the *existing* `common/sec_client.py` — same User-Agent, same shared 8 req/s SEC rate limit every other SEC call in this project already respects. New package `frames/` (`fetch.py`, `compare.py`), new tables (`analytics.frames_consistency_check`, migration 0053), new CLI `scrooner-frames-check run --year --quarter` / `report`.

Checked 7 of the highest-value concepts (doc 02's locked V1 metrics' own underlying facts): `revenue`, `net_income`, `cfo`, `operating_income` (duration), `total_assets`, `cash_and_equivalents`, `stockholders_equity` (instant) — 7 SEC requests total, covering ~28,000 (company, concept) pairs across the whole active population in one pass. Extremely cheap relative to the per-company yfinance approach: no ticker resolution, no ~1.2s-per-company pacing, matched directly by CIK.

## First real run: a serious-looking finding that turned out to be my own bug, not the pipeline's

First pass (before the fix below): 27,382/28,187 (97.1%) exact matches overall, but `revenue`/`net_income`/`operating_income` showed a meaningfully higher mismatch rate (~6-7%) than the near-perfect balance-sheet concepts (<1%). Investigating the worst `net_income` mismatches surfaced something that looked like a genuinely serious, previously-invisible integrity bug: **91% of the 308 net_income mismatches (280 companies) had *two* `core.fact` rows both marked `is_authoritative = true`** for the same (company, tag, period) — a state this project's own `is_authoritative` discipline is built to prevent (exactly one authoritative value per slot is the whole point of the flag).

**Traced to the exact rows before concluding anything** (Madison Square Garden Sports Corp., the largest such case): both facts share the identical `raw_object_id` and `filing_id` — but their real `core.period` rows are genuinely different: one is `start=2025-07-01, end=2026-03-31` (a 9-month YTD cumulative span, correctly left `fiscal_period=NULL` by the Normalizer's own established design), the other is `start=2026-01-01, end=2026-03-31, fiscal_period='Q3'` (the real, discrete quarter). **These are not duplicate/conflicting facts at all — they're two legitimately different reporting spans from the same filing, both correctly authoritative.** The bug was entirely in this new checker's own matching logic: `_load_our_facts_for_tag` keyed by `(company_id, end_date)` alone, the exact "multiple periods can share an end_date" trap this project already has one prior documented instance of (Nike's FY2025/Q4 sharing 2025-05-31, found 2026-09-08 earlier the same day building `yfinance_financials/`). When SEC's Frames row reported the true Q3 figure, a Python dict with a non-deterministic insertion-order tie between the two candidate periods sometimes picked the 9-month YTD value instead, producing a false "mismatch."

**Fixed** by keying on `(company_id, end_date, start_date)` together, with a further tie-break preferring a real `fiscal_period`-classified period over an unclassified one when a genuine ambiguity remains. Instant concepts (Frames omits `start` entirely for point-in-time facts) are handled by defaulting the missing `start` to `end_date` — matching `core.period`'s own established convention of `start_date == end_date` for instant periods, so instant concepts key correctly without needing a separate code path.

**Lesson, worth restating even though a close cousin of it is already documented twice in this project:** a brand-new detection tool's own *first* alarming finding deserves the same "trace to the real underlying rows before trusting it" discipline as every other finding this project has ever investigated — the tool itself can have the bug, not just the thing it's checking. Finding this before publishing "280 companies have a serious authoritative-fact integrity violation" as a headline result is the entire point of this project's verification culture.

## Corrected results — real, final numbers for CY2026Q1

Re-ran all 7 concepts after the fix. Mismatches dropped from 752 to **88** (an 88% reduction) — confirming 664 of the original 752 were entirely artifacts of the period-matching bug above, not real pipeline issues.

| Concept | Matched companies | Mismatch | Rate |
|---|---|---|---|
| revenue | 2,225 | 2 | 0.09% |
| net_income | 4,569 | 28 | 0.61% |
| cfo | 4,086 | 5 | 0.12% |
| operating_income | 3,777 | 7 | 0.19% |
| total_assets | 4,950 | 6 | 0.12% |
| cash_and_equivalents | 3,886 | 5 | 0.13% |
| stockholders_equity | 4,694 | 35 | 0.75% |
| **Total** | **28,187** | **88** | **0.31%** |

**99.69% exact agreement** between our own extracted SEC data and SEC's own independently re-served copy of the same filings, across ~28,000 company-concept pairs, for the current quarter.

Root-cause breakdown of the remaining 88 real mismatches:

| Pattern | Count | What it means |
|---|---|---|
| Both candidate facts non-authoritative | 79 (90%) | The already-documented, deliberate Stage 2e design (dedupe.py correctly refuses to guess between trivially-disagreeing restated values, e.g. Adial Pharmaceuticals: $2,022,392 vs $2,023,000, a 0.03% cross-filing rounding difference). Our fallback and Frames' own "most recent filing" convention pick different non-authoritative candidates. **Not a bug** — see "open design question" below. |
| Exactly one authoritative fact, still disagrees | 9 (10%) | Genuinely worth a closer look case by case. Sampled: dominated by tiny, obscure SPAC entities (e.g. "D. Boral ARC Acquisition I Corp.") with messy, amendment-heavy filing histories and near-zero real economic activity — not a systematic pattern across real, substantial companies. Left as named, unresolved residual findings rather than chased individually given the low materiality. |
| Multiple authoritative facts (the false alarm) | 0 | Fully eliminated by the period-matching fix. |

**Open design question surfaced, not decided here:** when every candidate for a (company, concept, period) slot is non-authoritative (a genuine, small-magnitude cross-filing disagreement), should the fallback prefer the *most recent* filing's value — matching SEC's own Frames convention — rather than an arbitrary pick? This would resolve the 79-case majority pattern above and make our data consistent with SEC's own canonical resolution, but it touches `resolve()`-adjacent tie-break behavior this project has repeatedly treated as a deliberate human decision, not an automatic "fix" — flagged for explicit sign-off, not applied.

## Verification

- `pytest tests/unit/test_frames_fetch.py tests/unit/test_frames_compare.py` — period-code format and tolerance-boundary logic covered; full suite 479/479 after the build, unchanged after the period-matching fix.
- Both real shapes (`CY2026Q1` duration, `CY2026Q1I` instant) verified against live SEC responses before any code was written, not assumed from documentation.
- The false "authoritative-conflict" finding was traced to the literal `core.fact`/`core.period` rows before being reported as a bug, and disproven by that trace — not asserted from the aggregate count alone.
