# 24 — Scrooner: Final Build Backlog

One consolidated, ordered backlog before building starts — synthesizes doc 18 (metric tiers), doc 19 (ownership), doc 20 (remaining work), doc 21 (MF holdings/corporate actions), doc 22 (EDGAR evaluation), and doc 23 (signal enhancements) into a single sequence instead of six scattered ones. **Supersedes doc 20 as the "what's left, in what order" reference** — doc 20 predates docs 21-23 and is now stale for that purpose; it stays in place for its own historical record (§2's decision table is still accurate) but this doc is what to read for sequencing going forward.

> **Status:** Canonical (2026-08-17) — this is the plan being executed, not a survey. **Owner:** Founder / Product · **Review:** after each phase closes, update `doc/PROGRESS.md` first, same discipline doc 20 already established.

---

## Where things stand (from `doc/PROGRESS.md`)

Parts 1-7 (Collector → Backend API) are complete. Part 8 (Frontend) has only the company-page MVP — no Screener UI, AI Query UI, auth, or saved-screens UI exists yet; `apps/app` isn't scaffolded. Ownership Stages 1-4 are complete (Form 4, Schedule 13D/13G, Form 13F). Parts 9-14 (User System, Billing, Admin, SEO, Analytics, Infra) haven't started.

Three decisions remain genuinely open and are **not** resolved by this doc (doc 02's guardrail): market-price vendor, LLM vendor for AI Query 6c, free/paid usage limits + pricing tiers. Each has a working stopgap already in place (mock prices, rule-based parser, entitlement schema with no enforced numbers) so nothing below is blocked waiting on them except the items that explicitly say so.

---

## Phase 1 — EDGAR signal batch (cheap, fully scoped, zero open decisions) — ✅ COMPLETE, verified 2026-08-17

Every item here is small, needs no new SEC fetch, mirrors a pattern already proven elsewhere in this codebase, and was checked live in doc 23. Batchable into one build session.

1. **Form 4 `aff10b5One`** (doc 23 Stage A) — `is_10b5_1_plan` on `core.insider_transaction`. Backfilled across the full golden-10 (55,109 transactions, exact match to the pre-existing total — zero data loss). Real, internally-consistent result: RDDT (IPO'd March 2024, entirely post-rule) shows zero nulls and a real, plausible 86% pre-arranged-plan rate; older companies show the expected null/populated split around the 2023-04-01 effective date. Verified rendering live on the company page (RDDT CEO's real recent sale correctly tagged "10b5-1").
2. **Form 15 → real `delisted` status** (doc 23 Stage C) — extend `company_master/status.py`. **Caught and fixed a real false-positive during verification**: JPM's own CIK has 4 Form 15/15D filings, but all four are subsidiary financing trusts ("Chase Capital I", capital securities) deregistering debt instruments, not JPM's common stock — fixed by fetching each filing's own cover page and requiring it actually say "common stock" before trusting the signal. All 10 golden companies correctly remain `active`.
3. **8-K `items` capture** (doc 21) — new column on `core.filing`. Verified rendering live with real SEC item codes translated to plain English (e.g. "Earnings Results", "Officer/Director Change").
4. **SC 14D9 presence signal** (doc 23 Stage D) — form-type recognized; no golden-10 example exists to visually verify (matches doc 23's own noted gap), same as Form 15 before JPM's real (if initially misread) example turned up.
5. **`dei:EntityPublicFloat`** (doc 23 Stage B) — new `public_float` canonical concept, resolved for 8 of 10 companies (ENB/TSM excluded, the same known foreign-filer taxonomy gap every other Mapper concept already has). Real, plausible values (AAPL $3.25T as of 2025-03-28); rendered on the company page, explicitly labeled apart from the still-blocked Market Cap field.

**Also built this pass, beyond the original Phase 1 scope, per direct follow-up instruction**: doc 02's market-price vendor decision resolved (Alpaca, free tier) and integrated (doc 25) — real prices for all 10 golden companies via the `delayed_sip` feed into a new `core.market_price_alpaca` table. A real ticker-resolution bug was found and fixed twice during this: first via a `golden_companies.json` stopgap, then replaced with a general, non-Alpaca mechanism (`company_master/security_type.py`, sourced from OpenFIGI) after explicit direction not to lean on the price vendor for identity classification.

**Not in this phase**: dimensional/segment XBRL (doc 23 Stage E — deliberately undesigned, needs its own pass) and Form N-PORT (Phase 2 — bigger, standalone).

## Phase 2 — Form N-PORT: mutual-fund-only ownership (doc 21)

Reuses Stage 4's proven CUSIP-matching pattern against a second, larger bulk data set (~420MB/quarter vs. 13F's ~100MB). New `ownership/mutual_fund.py`, new `core.fund_ownership` table. Standalone effort, not bundled with Phase 1 because of its size.

## Phase 3 — Screener UI + AI Query UI (`apps/app`)

**The highest-value remaining work, per doc 20's own analysis, unchanged by anything scoped since**: `apps/app` doesn't exist yet. Every EDGAR enhancement in Phases 1-2 makes the *data* richer, but no real user can run a screen or ask a plain-English question anywhere yet — `POST /v1/screen` and `POST /v1/ask` are complete and verified (Part 7) with nothing in front of them. This is the first point the product does its actual job for someone who isn't a developer reading a psql prompt.

- Scaffold Next.js `app.scrooner.com`.
- Screener UI — form/table over `POST /v1/screen`.
- AI Query UI — prompt box over `POST /v1/ask`, showing the interpreted query explicitly before results (doc 02's explainability gate).

No new pipeline work; both are pure consumers of already-verified output.

## Phase 4 — Auth + saved screens UI

Needed before "saved screens" or entitlements mean anything to a real user. Supabase Auth is the already-decided provider; the two-domain cookie-sharing setup (`Domain=.scrooner.com`) needs to be built and tested explicitly (root `CLAUDE.md`'s own flagged risk). CRUD already exists at the API layer (`apps/backend`'s `saved_screens.py`) — needs a UI only.

## Deferred, not scheduled

- **Dimensional/segment XBRL** (doc 23 Stage E) — needs its own design pass before any build plan exists for it, per that doc's own honest assessment.
- **DEF 14A / deep 8-K text parsing** (doc 19 Stage 5) — unstructured, P2.
- **Doc 18's Tier A metrics** (Quick Ratio, ROA, FCF Growth, etc.) — buildable, but adding them requires an explicit go-ahead to amend doc 02's locked 18-metric list first, not just picking them up as pre-approved.
- **SC TO-T deal-detail extraction** (beyond Phase 1's presence-only signal) — needs its own issuer-vs-filer verification pass first, per doc 23's own note.

## Decisions this backlog doesn't make

Market-price vendor, LLM vendor (6c), usage limits/pricing tiers, legal/licensing review — exactly as open as doc 20 already left them. None of Phases 1-4 are blocked on any of them.

---

## Recommended order

**Phase 1 → Phase 3 → Phase 2 → Phase 4**, not strictly numeric. Reasoning: Phase 1 is cheap and de-risked, worth clearing first. Phase 3 (Screener/AI Query UI) is the single most consequential gap in the whole product — it's the thing that turns "a very well-verified backend" into "a product a user can actually use" — and doesn't depend on Phase 2 at all, so there's no reason to make a user wait on mutual-fund data before they can run a screen. Phase 2 (N-PORT) is real value but enrichment, not core-loop-unlocking, so it can follow. Phase 4 (auth/saved screens) naturally comes after there's a UI worth logging into.

This doc's job is done once Phase 1 starts — from here, execution updates `doc/PROGRESS.md` per phase, the same discipline every prior phase in this project has followed.
