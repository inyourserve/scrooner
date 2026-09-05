# Ownership & Insider Activity data-point audit — 2026-08-29

> **Scope:** the three Ownership page-section subsections locked by [`doc/scoping/insider_info.md`](../scoping/insider_info.md) — Insider Ownership & Transactions, Institutional Ownership (Form 13F), Mutual Fund Ownership (Form N-PORT) — evaluated for investor decision-value, not build status. Build status is already tracked in `DATA_COVERAGE.md` §8 and root `CLAUDE.md`'s Ownership paragraph; this audit asks a different question: **if a common, self-directed investor opened this section, how much of it actually helps them decide, and what's missing to make it a real differentiator rather than a data dump.** Grounded in the real `insider_info.md` spec text, the real transaction-code classification (`pipeline/src/scrooner_pipeline/ownership/transaction_codes.py`), and the real current frontend (`apps/site/src/pages/stock/[ticker].astro`), not recalled from memory.

## Executive finding

The underlying data is unusually good for a retail product — better-sourced and more precisely classified than most paid tools (Fintel, OpenInsider, Trendlyne). **The weakness isn't the data, it's presentation: everything is a flat, unranked list with no signal-weighting and no context**, plus the frontend today (confirmed by reading `[ticker].astro` directly) renders only a fraction of what's already computed — no Overview, no Mutual Fund card, no rolling 3/6/12-month summaries, no QoQ change, no Top-10-with-status. The single highest-leverage fix (holder-category split for institutional ownership) is **already identified** in `doc/scoping/28_Scrooner_Trendlyne_Data_Point_Gap_Analysis.md` §2 but isn't in `insider_info.md`'s locked scope.

## Strong points

- **Real SEC transaction-code classification.** `transaction_codes.py` maps P/S/A/M/G/F to the doc's 6 human categories and deliberately leaves ambiguous codes (D, C, I, and 8 others) as "Other" rather than force-fitting them — e.g. code D ("disposition to the issuer") is often tax-related in practice but its SEC definition is broader, so it's correctly left unclassified. Most retail insider tools either lump everything together or misclassify tax-withholding dispositions as sells.
- **`is_10b5_1_plan` flag** (doc 24 Phase 1) — distinguishing a pre-scheduled sale from a discretionary one is the single highest-value insider signal that exists, and almost no retail tool surfaces it.
- **Post-transaction holding per row** — lets a user judge whether a transaction is 2% or 90% of an insider's stake, which matters more than the raw dollar figure alone.
- **Institutional QoQ trend with increasing/decreasing/new/exited counts** (`ownership/institutional_summary.py`) — the actual "smart money direction" signal, not just a static snapshot %.
- **Mutual fund portfolio weight field** — rare even among paid tools; knowing a stock is 8% of a fund's book (conviction) vs. 0.05% (index filler) is a real differentiator once built.
- **The "never sum institutional + mutual fund" rule is enforced in code**, not just documented — correct, and most competitors either get this wrong or don't disclose the overlap at all.

## Weak points

1. **No signal ranking — everything is presented flat.** Form 4 filings are dominated by routine grants/vesting/tax-withholding; genuine conviction buys/sells are the minority. If "Latest 10 transactions" isn't defaulted to open-market P/S rows (grants available via toggle), a common investor sees mostly "Grant"/"Tax-related disposal" noise and misses the one real signal — the most common complaint about naive insider-trading tools.
2. **Institutional ownership doesn't distinguish passive index funds from active/concentrated managers.** Vanguard/BlackRock/State Street mechanically hold nearly every large-cap; their presence in a Top 10 table is close to noise next to a concentrated active manager building a position. Already named as a real gap in doc 28 §2 ("`core.institutional_ownership` has `filer_name`/`filer_cik` but no `filer_type` column... a real build item, not a freebie") but not in `insider_info.md`'s locked scope.
3. **No benchmarking/context.** "68% institutional ownership" means nothing standalone — high, low, typical for the sector? Every number in this section is presented in isolation; ties to doc 26's still-unbuilt peer/sector comparison.
4. **Headcount stats ("N insiders buying/selling") aren't dollar-weighted.** 10 insiders selling $10K each via routine 10b5-1 plans looks identical in headcount to 1 insider dumping $50M. A **net dollar figure** (total $ bought − total $ sold, trailing 12mo) is the number a common investor actually wants at a glance; the spec's "total open-market buying and selling" doesn't even specify $ vs. share count.
5. **No cluster-buying detection.** Multiple insiders buying in the same short window is one of the most reliable documented insider signals, stronger than any single transaction — not in scope.
6. **13F's structural limits are under-disclosed.** The spec's disclosure note covers filing lag but not what 13F *cannot* see at all: short positions, most derivatives, and it's a quarter-end snapshot subject to window dressing. A user reading "68%, increasing" will over-trust a number that can't see the short side.

## Arguably extra (low value relative to cost)

- **"Fund family" as a first-class column** — fine to keep, but for a common investor it adds table width without much decision value versus portfolio weight and % change; don't prioritize polish here.
- **Three separate 3/6/12-month rolling summary blocks** — probably collapses to "12-month total + a small trend indicator" for most users; worth a UX pass before building three parallel stat blocks.

## Missing (ranked by investor value)

1. **Holder-category split** (passive index / active fund / hedge fund / insider) for institutional ownership — the single biggest credibility upgrade to that subsection; already scoped in doc 28, not yet in `insider_info.md`.
2. **Net insider $ bought/sold** as the headline stat, not buried under separate buy/sell totals.
3. **Cluster-buy detection** ("3 insiders bought within 5 days") — cheap given data already collected, high signal.
4. **Insider ownership in absolute $**, not just % — "$50M of CEO skin in the game" lands harder than "1.2%."
5. **Multi-year ownership trend** — correctly deferred for MVP (`insider_info.md`'s own "no five-year history" line), but flag now as the highest-value V2 item once 2+ periods of real history accumulate.
6. **Screenability.** None of insider net-buying, institutional QoQ direction, or mutual-fund accumulation appear to be wired into `screener/`'s catalog or `ai_query/aliases.py` yet — `DATA_COVERAGE.md`'s own "what moves the needle next" section names alias-vocabulary coverage as the product's single largest current gap (14 of 45 metrics). "Show me companies where insiders bought net last quarter" is exactly the kind of query that makes the plain-English wedge feel real; right now this data is company-page-only display, not query-able.

## Frontend reality check

`apps/site/src/pages/stock/[ticker].astro` today renders only three raw tables — Insider Activity, Institutional Holders, Beneficial Ownership (grep-confirmed 2026-08-29). **No Overview, no Mutual Fund card, no rolling summaries, no QoQ change, no Top-10-with-status** — matches root `CLAUDE.md`'s own note that the frontend build is "scoped only, not built." Everything above about ranking/net-$/context applies to a page that doesn't exist yet — worth deciding the display logic (grants filtered by default, net-$ headline, passive/active placeholder column) *before* building the frontend, since it's cheap to bake into the summary layer now and expensive to retrofit after the UI ships.

## Top 3 recommendations if only doing three things

1. Default the insider transaction list to open-market P/S rows with a toggle for grants/exercises/gifts (presentation-only change, zero new data).
2. Add filer-type (passive index / active) classification to institutional ownership (doc 28 §2 — a real build item, scope it into `insider_info.md` or a successor doc).
3. Wire net insider buying and institutional QoQ direction into the Screener catalog and AI Query alias vocabulary, so this data is query-able, not just displayed.
