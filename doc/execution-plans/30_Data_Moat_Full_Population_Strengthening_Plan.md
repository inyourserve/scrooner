# 30 — Data Moat: Full-Population Strengthening Plan

**Status:** Effectively complete — status line corrected 2026-09-06 (found stale during a doc-consolidation audit; this had said "Active" since 2026-08-24). All 5 tracks below were subsequently completed via later, more specific work: Ownership & Insider Activity full-population scale-out (2026-08-29, see `doc/learnings/2026-08-29-ownership-scale-out-and-zero-fetch-metrics.md`) and the price-metrics full-population rollout (2026-09-02/03, see root `CLAUDE.md`'s narrative). Treat this doc as historical scoping context, not a live plan. **Owner:** Founder/Product, executed by pipeline agent.

Prompted directly, following the full-project inspection (`doc/audit/2026-08-24_full_project_inspection.md`): "pick the point which is related to data, because data is moat... whatever is required do the needful." Doc 01 names the data moat first, ahead of trust/distribution/UX — this doc scopes and executes closing the data gaps the inspection found, specifically the ones created or exposed by tonight's 174→5,258-company full-population expansion.

## Why these five tracks, in this order

The inspection found five concrete, data-specific gaps against the newly-expanded population. Each is scoped below as an independently executable track — small batches, parallelizable, so progress is real and checkable at every step rather than one large opaque job.

| # | Track | Blocked on | Differentiator value (doc 10) |
|---|---|---|---|
| 1 | Real price data for single-listing companies | Nothing — code fix done, ready now | Unblocks 6 of 18 locked V1 metrics for 83% of the universe |
| 2 | Ownership & Insider Activity expansion (Form 4, 13D/13G, 13F) | Nothing — CLI already supports `--ciks`, tables disjoint from the running Normalizer/Mapper pipeline | Doc 10's own named differentiator for a $100/year product; currently 0.19% of the population has this data |
| 3 | Concept-mapping coverage verification at full scale | Current pipeline's Mapper `resolve-facts`/`calculate` stages finishing | Determines whether the whole expansion's *data* is trustworthy, not just present |
| 4 | Dedupe conflict-rate measurement at full scale | Current pipeline's Normalizer `dedupe` stage finishing (imminent — stage 4 of 7) | Answers the project's own "single biggest open data-quality question" at real scale |
| 5 | Multi-listing companies (894, 17%) primary-ticker resolution | A deliberate decision: re-scope OpenFIGI to just these 894 (cheap, small), or accept the gap | Smaller, bounded remainder of Track 1 |

Tracks 1 and 2 do not touch any table the currently-running Normalizer/Mapper pipeline writes to (`core.market_price_alpaca`/`analytics.metric_value[requires_price=true]` for Track 1; `core.insider_transaction`/`core.beneficial_ownership`/`core.institutional_ownership` for Track 2) — confirmed safe to run concurrently, same reasoning already proven tonight for running Company Master alongside Normalizer.

---

## Track 1 — Real price data for single-listing companies (paused, dev/test scope only)

**Status update 2026-08-24, mid-execution:** 39 of 44 chunks (~3,900 companies) got real Alpaca prices before 5 chunks hit a deterministic `HTTPStatusError: 400 Bad Request` from Alpaca's bulk `/stocks/bars/latest` endpoint — almost certainly one malformed/unsupported ticker symbol poisoning its whole batch request (a preferred-share ticker like `CMS-PB`'s hyphen notation is a likely suspect, not yet confirmed). **By explicit direction, this track is paused rather than debugged further — Alpaca is being treated as a dev/testing-only data source right now, not a priority to harden.** The `resolve_primary_tickers`/`update-market-price --ciks` code fix itself remains in place and correct; resuming this track later just means isolating the bad symbol(s) and re-running the remaining ~500 companies.


**Fix already made** (`company_master/security_type.py`'s `resolve_primary_tickers`, `jobs/company_master.py`'s `update-market-price` CLI): a company with exactly one active `core.listing` row needs no OpenFIGI classification at all — there's nothing to disambiguate. Verified live: **4,364 of 5,258 companies (83%)** qualify. Sample-tested against 5 real newly-added companies before trusting it (all resolved correctly: AIR, ABT, ACU, ADX, BKTI).

**Execution plan:** batch `update-market-price --ciks <chunk>` across the 4,364-company list, then `mapper/price_metrics.py`'s existing calculation (`scrooner-map calculate` already covers this — no new command, just needs to run again now that real prices exist for more companies). Small chunks (~100 companies), dynamic work-queue, same pattern proven tonight.

**Explicitly not in scope for this track:** the 894 multi-listing companies (Track 5) — correctly resolve to nothing rather than guess.

## Track 2 — Ownership & Insider Activity, full population

**Mechanically ready:** `update-insider-transactions` and `update-beneficial-ownership` already accept `--ciks`, no code change needed. `update-institutional-ownership` has no `--ciks` (by design — CUSIP-driven against whatever `core.beneficial_ownership` already has), so it will pick up automatically once Stage 3 (beneficial ownership) has real CUSIPs for more companies.

**Real cost not yet sized, sizing it as part of execution:** golden-10's 55,109 Form 4 rows are dominated by heavy filers (JPM alone contributes a large share). A full-population run's SEC-fetch volume and runtime is unknown — start with a modest batch (e.g. 200 companies), measure real per-company cost, then extrapolate before committing to the full 5,258.

**Execution plan:** same dynamic work-queue pattern, small chunks, starting with insider transactions (Stage 2) since beneficial ownership (Stage 3) needs to follow for institutional ownership (Stage 4) to pick up new CUSIPs.

## Track 3 — Concept-mapping coverage at full scale

**Cannot start until the current pipeline's Mapper `resolve-facts` stage has run for the full population** (concept resolution needs to have actually happened first). Tooling already exists (`mapper/concepts.py`'s `unmapped_tag_report`/`coverage_report`) but has never been run wider than the golden-10, and the CLI (`scrooner-map coverage`) silently defaults back to the golden-10 if `--ciks` is omitted — **must be run with the explicit full CIK list**, not the default.

**Action when unblocked:** run `scrooner-map coverage --ciks <full population>` and `unmapped-tags` the moment `resolve-facts`/`calculate` finish; compare against the golden-10's known ~83-100% coverage; document the real number in `DATA_COVERAGE.md` regardless of outcome.

## Track 4 — Dedupe conflict-rate at full scale (complete, 2026-08-24)

**Answered.** `dedupe` finished for the full 5,258-company population. First read of the raw flag rate (48.62% of all 70.6M facts marked `is_authoritative=false`) looked alarming against the golden-8's documented 6.57% — but that was comparing two different things. The golden-8's 6.57% measures *fraction of duplicate groups with genuine value disagreement*; the 48.62% measures *fraction of all facts flagged non-authoritative*, which includes harmless duplicate suppression (the same fact correctly re-cited across multiple later filings' comparative-period columns, e.g. Harmonic Inc.'s identical $26,300,000 accounts-payable figure appearing in 5 filings, 1 correctly kept authoritative). Live sampling confirmed **~77% of flagged rows are this harmless kind**.

**The correctly comparable number: genuine-conflict rate rose from 6.57% (golden-8) to 23.57% of duplicate groups (sampled: 5,196 of 22,046) — a real ~3.6x increase, not the ~7.4x the raw flag rate suggested.** Likely explanation: the full population includes many smaller/newer companies with less consistent XBRL tagging discipline than the golden-8's mega-caps (AAPL, JPM, MSFT) — a real, worth-tracking data-quality shift, not a bug (dedupe's refuse-to-guess-on-disagreement design is working exactly as documented). Worth a `DATA_COVERAGE.md`/`SCORECARD.md` update once those get their post-expansion refresh (§1), and worth periodically re-checking this rate as more of the population's history gets processed — this was measured right after dedupe finished, not months into stable operation.

## Track 5 — Multi-listing companies (894, 17%)

**Deliberately deferred, not started today.** Re-running OpenFIGI for just these 894 companies (not all 5,258) would be a ~6x cheaper, more scoped version of what was dropped earlier tonight — worth doing once Tracks 1-2 are underway and there's a clear read on whether it's worth the OpenFIGI rate-limit cost (confirmed tonight: ~1.5s/request pace, so 894 companies ≈ 22 minutes of real wall-clock fetch time — genuinely cheap). Recorded here as a real, sized, ready-to-approve follow-on, not an open-ended gap.

---

## Track 6 — Finviz comparison gaps (2026-08-24, `doc/html/finviz-appl.html`)

A real Finviz AAPL page was read section-by-section (not recalled from memory) and cross-referenced against what's built. Two verified-live, zero-new-fetch wins, plus smaller cheap ones:

1. **Employee headcount.** Finviz shows "Employees: 166,000." Scrooner has none. Checked live: `dei:EntityNumberOfEmployees` is unmapped in `analytics.concept_mapping`, with **1,452 real fact rows already sitting in `core.fact`, unused**. Task: add a canonical concept + mapping in `mapper/concepts.py`, no new fetch, no new Collector work.
2. **Aggregate Insider Ownership %.** Finviz shows "Insider Own: 0.12%." Scrooner only exposes insider activity as a transaction feed, never aggregated. Checked live: `core.insider_transaction.shares_owned_following` already has exactly the field needed. Task: latest `shares_owned_following` per unique `reporting_owner_cik` per company, summed, ÷ shares outstanding — same shape as the already-built `institutional_ownership_pct` (`mapper/expanded_metrics.py`), applied to insiders instead. Highest-value item here, since doc 10 names insider+institutional ownership as *the* named differentiator and only half of that pair is currently aggregated.
3. **Cash/Share, Price/Cash** — trivial derivatives of already-mapped Cash & Equivalents ÷ Shares Outstanding.
4. **Dividend Payout Ratio** — `dividends_per_share / EPS`, both already resolved.
5. **Basic Peers list** — same-SIC-code grouping. Previously blocked ("needs a wider universe than the golden-10") — that blocker is gone now that the full 5,258-company population exists. Zero new data, just a query.
6. **"Industry" as its own field** — `sic_description` is already captured (e.g. "Consumer Electronics" for AAPL, matching Finviz exactly) but not surfaced as its own company-page field, only folded into the coarser 11-bucket sector.

**Confirmed genuinely vendor-blocked, not worth chasing** (consistent with existing `DATA_COVERAGE.md` findings): 52-week range, Beta, all technical indicators (SMA/RSI/ATR/volatility), Short Interest/Float/Ratio, analyst Recommendation/Target Price/forward estimates, index membership (DJIA/NDX/S&P 500) — none are in SEC filings, all need a market-data or index vendor.

**Status: documented, not yet executed** — items 1 and 2 are the recommended first pick whenever this track starts (cheapest, highest differentiator value, zero new fetch for either).

## Track 7 — StockAnalysis.com comparison gaps (2026-08-24, `doc/html/stock analysis/*.html`, NVDA)

Five real pages read (Overview, Profile, Metrics, Dividend, Financials), not recalled from memory. Genuinely new, free/SEC-native items:

1. **Employer ID (EIN)** — `dei:EntityTaxIdentificationNumber`, a standard XBRL cover-page tag. Not captured anywhere in Scrooner today. Same cheap shape as SIC code (already via `update-identity`).
2. **Expanded filing-type coverage** — the Profile page's Recent Filings feed shows **Form 144, 424B5, FWP**, none currently in `normalizer/identity.py`'s `FORM_ALLOWLIST`. Already sitting in `raw.sec_submissions` (Collector captures every form type) — purely a Normalizer allowlist widening, same additive pattern already used for 8-K/DEF 14A.
3. **Net Cash (Cash − Debt) and Net Cash Per Share** — trivial derivatives of already-mapped Cash & Equivalents / Total Debt.
4. **Pretax Margin** — pretax income ÷ revenue; likely cheap, a pretax-income concept already exists (used by the tax-reconciliation metric).

**Confirmed genuinely blocked, not worth chasing (with a new, stronger piece of evidence):**
- **Revenue by Segment/Geography and all "Operating Metrics & Breakdowns"** (Data Center/Gaming/Compute/Networking, country-level revenue) — this page **explicitly discloses "Business metrics are provided by TipRanks"** (a paid vendor). This isn't just doc 22's own live API check anymore — a real competitor's own page admits it needed a paid vendor for this, not raw SEC parsing. Stronger confirmation than before that this is genuinely blocked, not merely unbuilt.
- **Dividend declaration/record/pay dates** (only the per-quarter amount is free/already built) — needs real 8-K text parsing, same deferred territory as doc 19 Stage 5.
- **Executive officer roster/bios** — named in a 10-K/DEF 14A but as free text, not a structured tag — same unstructured-parsing bucket, not a clean win.
- **52-week range, Beta, technical indicators, analyst ratings/targets, Forward P/E, ISIN** — same already-known vendor-blocked bucket.

**Status: documented, not yet executed.**

## Doc updates made alongside this plan

- `doc/foundational/02_Scrooner_Decision_Register.md`: addendum noting the EODHD evaluation and Alpaca reconfirmation (see that doc's own changelog).
- `doc/status/DATA_COVERAGE.md` / `PROGRESS.md`: to be updated with real coverage numbers once Tracks 1-4 report actual results — not updated speculatively before real evidence exists, per this project's own standing discipline.
