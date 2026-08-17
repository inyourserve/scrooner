# 20 — Scrooner: Remaining Work, End to End

Prompted directly: after doc 19 (Ownership & Insider Activity), "plan all the remaining thing end to end." This doc is the single inventory of everything not yet done across all 14 of doc 06's parts, as of this pass — cross-checked against `doc/PROGRESS.md` (not re-derived from memory), with a concrete sequencing recommendation and, for each item, whether it's a **build task** (this project can just do it) or a **decision** (needs the user, doc 02's guardrail against silent scope expansion applies).

> **Status:** Canonical (2026-08-17) — a planning doc, not a build log. Supersedes nothing; consolidates doc 02's still-open decisions, doc 18's proposed metric tiers, and doc 19's deferred stages into one place instead of three. **Owner:** Founder / Product · **Review:** after each item below is closed, update `doc/PROGRESS.md` first, then re-derive this doc's "what's left" list from it — never let this doc drift into being its own source of truth.

---

## 1. Where things actually stand (from `doc/PROGRESS.md`, not memory)

| Part | Status |
|---|---|
| 1 Data Collector | ✅ Complete |
| 2 Normalizer | ✅ Complete |
| 3 Mapper & Metrics Engine | ✅ Complete |
| 4 Company Master / Market Data | 🟨 4a complete. 4b built on **mock** price data only — real vendor decision still open |
| 4c Ownership & Insider Activity (doc 19, folded into Part 4's identity-adjacent scope) | 🟨 Stages 1-4 (8-K, Form 4, Schedule 13D/13G, Form 13F institutional ownership) built and verified 2026-08-17 — see `doc/PROGRESS.md` and `doc/learnings/form-13f-cusip-crosswalk.md` for current evidence. Stage 5 (DEF 14A) explicitly deferred |
| 5 Screener Engine | ✅ Complete |
| 6 AI Query Engine | 🟨 6a/6b complete (deterministic parser). 6c (real LLM) deferred — vendor decision open |
| 7 Backend / Product API | ✅ Complete |
| 8 Frontend Product | 🟨 Company page MVP only. Screener UI, saved-screens UI, auth pages **not started** |
| 9 User System | ⬜ Not started |
| 10 Billing | ⬜ Not started |
| 11 Internal Admin | ⬜ Not started |
| 12 SEO / Content Engine | ⬜ Not started — deliberately deferred past MVP (doc 02) |
| 13 Analytics & Monitoring | ⬜ Not started |
| 14 Infrastructure / DevOps | ⬜ Not started — hosting for recurring Python jobs still an open decision |

---

## 2. Immediate: finish what's in flight (doc 19)

Stages 1-3 were built this pass; treat this doc's own §1 as authoritative for exactly what's verified by the time it's read — check `doc/19_Scrooner_Ownership_and_Insider_Activity_Plan.md`'s own status line and `doc/learnings/ownership-and-8k-discovery.md` before assuming completion. Remaining inside doc 19's own scope:

- Full golden-10 run of Stage 2 (`scrooner-ownership update-insider-transactions`) and Stage 3 (`scrooner-ownership update-beneficial-ownership`), verified — not just AAPL.
- `apps/site`'s company page: Insider Activity + Major Shareholders sections wired to `core.insider_transaction`/`core.beneficial_ownership` — build task, not a decision.
- Doc 19's status line corrected to reflect exactly what's verified, not aspirational.

## 3. Decisions the user still needs to make (doc 02's open list — do not assume answers)

These block real functionality; every one of them has a mock/deferred/stub already in place so development wasn't blocked, but none of the blocked functionality can go to a real user until each is actually decided:

| Decision | Blocks | Current stopgap |
|---|---|---|
| Market-price vendor (source, delay, cost) | 6 price-dependent metrics (Market Cap, P/E, P/S, P/B, Dividend Yield, FCF Yield), EV-based Tier A metrics, real top-ratios on the company page | `core.market_price` holds 300 mock rows, `is_mock=true` |
| LLM vendor for AI Query (6c) | Real natural-language flexibility beyond the curated rule-based grammar | `ai_query/rules.py`'s deterministic parser (6a/6b), swappable via `NLInterpreter` |
| Free-vs-paid usage limits | Entitlement enforcement having a real number to check against | `app.user_entitlement` schema exists, shape only |
| Final pricing tiers | Billing (Part 10) can't be built meaningfully without this | Not started |
| Hosting for recurring Python jobs | Part 14 (Infra) | Local/manual execution only so far |
| Public saved-screen indexing rules | Part 12 (SEO), and whether saved screens ever get a public URL | Saved screens stay auth-only per doc 02's existing lock; this only matters if that's revisited |
| Legal disclaimers / data licensing review | Public launch readiness generally | Not addressed anywhere yet |

**Recommendation**: the market-price vendor decision is the highest-leverage one to close next — it unblocks 6 of doc 02's 18 locked metrics, all of Tier A's price-dependent metrics (§4), and the company page's top-ratios grid, which is the single most visible gap against the Screener.in reference (doc 17).

## 4. Doc 18's Tier A metrics — proposed, not yet built or locked

9 candidate metrics found in the doc 10 vs. doc 02 gap analysis, 6 of which need **zero price dependency**: Quick Ratio, ROA, FCF Growth (3Y/5Y CAGR), Share Count Dilution Trend, SBC % of Revenue, FCF-vs-Net-Income Divergence Flag. These are genuinely buildable now with the existing Mapper pattern (curate a composite concept, same shape as Mapper Day 1's revenue-tag work) — **but doc 02's locked list hasn't been amended to include them.** Per this project's own guardrail ("~15–20 metrics — not permission to expand ad hoc"), building these requires an explicit go-ahead to add them to doc 02's locked list first, not just picking up doc 18 as if it were already approved.

The other 3 (Net Debt/EBITDA needs a D&A tag curation pass first; EV/EBITDA, EV/Sales, buyback/shareholder yield need price) are blocked on the price-vendor decision (§3) regardless.

## 5. Ownership Stage 4/5

- **Form 13F (institutional ownership)**: **built and verified 2026-08-17**, not deferred anymore — see `doc/learnings/form-13f-cusip-crosswalk.md`. The CUSIP↔CIK crosswalk question this section originally flagged needed no external vendor: Schedule 13D/13G cover pages already carry the golden company's own CUSIP, sourced from documents Stage 3 already fetches. 58,095 real institutional holdings matched across the golden-10, now rendering on the company page.
- **DEF 14A / deep 8-K text parsing**: narrative- and HTML-table-heavy, not structured data like Stages 1-4. P2 in doc 10's own priority scheme. Lower product value than Stage 2/3's already-built insider/ownership signals — not worth prioritizing ahead of the frontend work in §6.

## 6. Frontend — the largest remaining build surface

Company page MVP (doc 17) is the only piece of `apps/app`/`apps/site`'s actual product surface built so far. Still needed, roughly in dependency order:

1. **Screener UI** (`app.scrooner.com`) — a form/table UI over the already-complete, already-verified `POST /v1/screen`. No new backend logic; this is the first place a user can actually run a plain-English or structured screen.
2. **AI Query UI** — a prompt box over `POST /v1/ask`, showing the interpreted query explicitly (doc 02's explainability gate) before showing results.
3. **Auth pages** (sign-up/sign-in/session) — needed before saved screens or entitlement-gated features mean anything to a real user. Supabase Auth is already the decided provider (doc 04); the two-domain cookie-sharing setup (`Domain=.scrooner.com`) still needs to be built and tested explicitly per the root CLAUDE.md's own flagged risk.
4. **Saved screens UI** — CRUD already exists at the API layer (`apps/backend`'s `saved_screens.py`, doc 16); needs a UI.
5. **Home / pricing pages** (`scrooner.com`) — static marketing surface, blocked on §3's pricing-tier decision for the pricing page specifically, not blocked for the home page.

None of these need new pipeline work — they're consumers of already-verified backend/screener/AI-query output. This is real UI-engineering effort, not a data or correctness question, which is why it's the single largest remaining item by raw hours even though it's the lowest-risk one architecturally.

## 7. Parts not yet started at all

- **Part 9, User System**: mostly covered by §6.3 (auth pages) + Supabase Auth already chosen. What's left beyond that is profile/account-settings UI, not a new architecture decision.
- **Part 10, Billing**: Stripe already locked as the choice (doc 04); genuinely blocked on §3's pricing-tier decision before there's anything concrete to build against.
- **Part 11, Internal Admin**: Django + Django Admin already locked (doc 04); can run in parallel with anything else per doc 06 — lowest-dependency remaining part, could be picked up any time without blocking on a decision.
- **Part 12, SEO / Content Engine**: deliberately deferred past MVP (doc 02, confirmed 2026-08-14) — guides, glossary, public indexed screens. Correctly not on the near-term list.
- **Part 13, Analytics & Monitoring**: structlog is already in use pipeline-side; Sentry + lightweight product analytics (doc 04's stack) not yet wired into `apps/backend`/`apps/site`. Worth doing once real users exist, not before — no data to analyze yet.
- **Part 14, Infrastructure / DevOps**: genuinely blocked on §3's hosting decision for the recurring Python jobs; GitHub Actions CI/CD (doc 04's choice) not yet set up for any of the apps.

---

## 8. Recommended sequencing

Critical path stays **Data → Screener → Product** (doc 06) — data-side work (Parts 1-5, 4c) is essentially done or in its deferred-by-design state; the real remaining critical path is now **Product**, specifically:

1. Finish doc 19 Stages 1-3 verification (§2) — in flight, closes this pass.
2. **Close the market-price vendor decision** (§3) — highest leverage single decision, unblocks 6 locked metrics + Tier A price metrics + real top-ratios.
3. **Screener UI + AI Query UI** (§6.1-6.2) — the first point a real user can do the product's actual job. Everything before this has been building toward a demo only a developer can see.
4. **Auth + saved screens UI** (§6.3-6.4) — needed before anyone can meaningfully be a "user" of the product rather than an anonymous visitor.
5. **Pricing-tier decision → Billing** (§3, §7) — first commercial milestone per CLAUDE.md's own stated business intent.
6. Everything else (Admin, Analytics, Infra, SEO/Content, Tier A metrics, Ownership Stage 4/5) can run in parallel or after, per doc 06's own parallel-track allowance — none of them block the critical path above.

**What this doc does not do**: assume an answer to any decision in §3, silently add doc 18's Tier A metrics to doc 02's locked list, or treat Ownership Stage 4/5 as scheduled rather than deferred. Each remains exactly as open as it already was — this doc's job is to make the *shape* of what's left legible in one place, not to make the calls only the user can make.
