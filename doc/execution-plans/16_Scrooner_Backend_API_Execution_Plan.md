# 16 — Scrooner Backend API: Execution Plan

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

AI Query Engine (6a/6b) is done. This is the concrete build plan for Part 7 (Backend / Product API) — scoped, by explicit user direction, to **Scrooner's own internal product use only**: letting `app.scrooner.com` (Next.js) call the already-verified Screener and AI Query Engine, check a user's paid/free status, and manage saved screens. It does **not** cover the public/B2B data API — see "What this phase does not decide" for why that's a different thing entirely, not a later increment of this one. It does not relitigate anything already locked in doc 02/03/04/06 — it operationalizes them, the same way docs 08/09/11/13/14/15 did for the earlier phases.

> **Status:** Canonical (2026-08-17) — all 4 stages built and verified against real HTTP requests, two real Supabase Auth users, and the golden-10; `/v1/screen`/`/v1/ask` reproduce doc 14b/15b's results exactly. Evidence: [doc 16b](16b_Backend_API_Definition_of_Done_Evidence.md). **Owner:** Founder / Product · **Review:** When a core decision changes, or when Frontend (Part 8) needs an endpoint this doc didn't anticipate.

---

## Where this sits

```
PHASE 5   Screener Engine                ✅ done
              ↓
PHASE 6   AI Query Engine (6a/6b)        ✅ done
              ↓
PHASE 7   Backend / Product API          ← this doc
              ↓
PHASE 8   Frontend Product
```

**One-line job description**, from doc 06: *"Expose company, screener, user and screen data."* Narrower in practice than that sounds — see the naming clarification immediately below, and the scope table after it.

---

## Naming clarification — this is not `apps/data-api`

DOCUMENTATION.md's repo tree already names a FastAPI service: `apps/data-api`, explicitly labeled *"FastAPI service (Phase 3, B2B data API)"* — a customer-facing, API-key-authenticated product for **external** consumers, gated in doc 02/03 on demonstrated demand ("Deferred until stable demand appears" / "Multiple consumers or external API demand"). That is a different component from what this doc builds.

What this doc builds is the **internal bridge** that lets Scrooner's own Next.js app invoke Python logic it cannot execute itself: the Screener (`screener/`) and AI Query Engine (`ai_query/`) are Python, `app.scrooner.com` is Node.js/TypeScript, and a browser can't call Python functions directly — something has to sit in between. That need exists independent of any B2B ambition, and would exist even if Scrooner never sold a data API to anyone. Building it under the `apps/data-api` name risks exactly the kind of quiet scope-merge doc 02/03 drew a hard line against — so this doc uses a different name: **`apps/backend`**. If the B2B product is ever greenlit, it's a separate build (its own auth model, its own rate limiting, its own doc), not an extension of this one.

---

## What the Backend API is allowed to do — and not

Doc 04's boundary table has no row for this component; this resolves it, following the same shape as Company Master/Screener/AI Query before it:

| Can do | Cannot do |
|---|---|
| Expose `screener/query.py` and `ai_query/rules.py` over HTTP, unchanged | Reimplement or duplicate their logic — this is a thin wrapper, not a second implementation (see "Repository footprint") |
| Authenticate a request via Supabase Auth and identify the calling user | Invent its own auth scheme — Supabase Auth is already locked (doc 02) |
| Check and record a user's entitlement/usage | Enforce a specific rate limit or pricing number — doc 02's "free vs paid usage limits" decision is still open; this phase builds the *shape* (a tier lookup, a usage log), not the *policy* |
| Store/retrieve saved screens for an authenticated user | Serve or authenticate an external, API-key-based consumer — that's the separate, not-yet-greenlit `apps/data-api` |
| Return exactly what `run_query()`/`interpret()` already produce, over JSON | Perform a "hidden one-off financial calculation inconsistent with metric definitions" (doc 04's existing Web/app boundary line) — no shortcut math in a route handler, ever |

---

## The real problems this phase has to solve

### 1. Two Python environments, one shared logic — resolved by dependency, not duplication

`pipeline/` (Collector→AI Query) and this new `apps/backend/` are separate deployable units with separate concerns (a batch/cron worker vs. a request-serving API), but they must never become two implementations of the Screener's null-handling or the AI Query grammar — that would reopen the exact "worked for the case it was built around, wrong elsewhere" risk this project has hit three times already (Mapper, Company Master, Screener). **Resolved**: `apps/backend` depends on `pipeline` as a local/workspace Python package (`scrooner_pipeline` importable directly, e.g. via a path dependency in `apps/backend/pyproject.toml`) — one source of truth, doc 05's own principle, not a special case invented for this phase.

### 2. Auth — Supabase Auth is already locked, this just consumes it

Doc 02 locks Supabase Auth; doc 04 notes the shared cookie (`Domain=.scrooner.com`) that carries a session across `scrooner.com`/`app.scrooner.com`. This phase adds nothing new to that model — it validates the same Supabase-issued JWT (passed as `Authorization: Bearer <token>` from Next.js, which already holds it from the shared session) and extracts the user id. No new auth system, no API keys — this is strictly internal, first-party traffic.

### 3. "Check paid user" needs a shape now, a policy later — same discipline as every other open decision this project has deferred

Doc 02's "Free vs paid usage limits" row is explicitly still open, deadline "before private beta." This phase cannot wait for that decision (Frontend needs *something* to call), so it builds the smallest honest shape: `app.user_entitlement` stores a `tier` (`'free'` or `'paid'`) per user, and `app.usage_event` records every screen/ask call. **Neither table enforces a specific number** — no "3 screens per day" logic anywhere in this phase. That's the exact same pattern as Company Master 4b (build the pipe, not the policy) and doc 13/15's vendor splits — a decision flagged and deferred, not silently assumed.

### 4. Saved screens store a query, not a result — determinism makes this safe

Doc 03: saved screens support create/name/view/rerun/delete. Storing the *result* would go stale the moment underlying data changes; storing the *`ScreenQuery`* and re-running it on each view is both simpler and correct, because the Screener is already deterministic (doc 14b) — "rerun" is just "run again," not a new operation.

---

## Database schema — new `app` schema

First component to actually populate the `app` schema CLAUDE.md's own architecture table named from the start ("Users, saved screens, entitlements, usage events") but that no phase has built until now.

| Table | Purpose | Key fields |
|---|---|---|
| `app.user_entitlement` | One row per Supabase Auth user; the *shape* for "is this a paid user," not the *policy* | `user_id` (FK `auth.users`, unique), `tier` (`free`\|`paid`), `updated_at` |
| `app.saved_screen` | A named, stored `ScreenQuery` per user | `id`, `user_id` (FK `auth.users`), `name`, `query` (`jsonb`, a serialized `ScreenQuery`), `created_at`, `updated_at` |
| `app.usage_event` | Append-only log of screen/ask calls — recording only, no enforcement yet | `id`, `user_id` (FK `auth.users`, nullable — anonymous calls are logged too), `event_type` (`screen_run`\|`ask_run`), `created_at` |

`auth.users` is Supabase's own managed table (created by enabling Auth, not by this migration) — `app.*` tables reference it by `user_id`, never duplicate user data into a second table.

---

## API surface — Scrooner's own use case only

| Endpoint | Auth | Wraps | Notes |
|---|---|---|---|
| `POST /v1/screen` | None | `screener.query.run_query()` | Body: a `ScreenQuery` (the exact Pydantic model from `screener/schema.py`, not a redefinition) |
| `POST /v1/ask` | None | `ai_query.rules.interpret()`, then optionally `run_query()` | Body: `{text: str, run: bool}`. Matches doc 03's "displays the interpreted filters... before or alongside execution" — `run=false` returns just the interpretation for the frontend to show first |
| `GET /v1/me/entitlement` | Required | `app.user_entitlement` lookup | Returns `{tier: "free" \| "paid"}` — the "check paid user" case named directly |
| `GET /v1/screens` | Required | `app.saved_screen` | List the caller's saved screens |
| `POST /v1/screens` | Required | `app.saved_screen` | Body: `{name: str, query: ScreenQuery}` |
| `PATCH /v1/screens/{id}` | Required | `app.saved_screen` | Rename only (doc 03's "name" verb) — not a query edit, which is delete-and-recreate to keep versioning unambiguous |
| `DELETE /v1/screens/{id}` | Required | `app.saved_screen` | |

Every call (authenticated or not) writes one `app.usage_event` row. No endpoint here talks to the future B2B API's concerns (API keys, per-key rate limits, public docs) — those don't exist in this phase at all.

---

## Build sequence

| Stage | Deliverable | Gate before moving on |
|---|---|---|
| 7a. Schema + auth | ✅ **Done and verified 2026-08-17.** `db/migrations/0007_app_schema.sql`; `apps/backend/auth.py`. Two real Supabase Auth users created via the Admin API; real JWTs (via the real password grant) correctly resolve to a user id; missing/garbage tokens correctly rejected with 401 before any handler logic runs. |
| 7b. Public endpoints | ✅ **Done and verified 2026-08-17, after 1 real bug.** `POST /v1/screen`, `POST /v1/ask`. Both reproduce doc 14b/15b's results **exactly** over real HTTP, including `Decimal` values preserved to full precision as strings (checked directly, not assumed from FastAPI's docs). Found and fixed: `json.dumps(model_dump())` on a `ScreenQuery` crashes on `Decimal` — fixed with `model_dump_json()`. |
| 7c. Authenticated endpoints | ✅ **Done and verified 2026-08-17, after 1 real bug.** `GET /v1/me/entitlement`, saved-screen CRUD, usage logging. Found and fixed: a `uuid.UUID`-vs-`str` comparison in the ownership check failed for **every** caller, including the rightful owner (failed closed, not a security hole, but a real functional bug) — fixed with an explicit `str()` cast, re-verified with two real users in both directions. `app.usage_event` counts reconciled exactly against calls made. See `doc/learnings/backend-api-7a-7d.md`. |
| 7d. End-to-end verification | ✅ **Done and verified 2026-08-17.** `doc/16b` DoD evidence. Determinism confirmed byte-identical over real HTTP. |

---

## Definition of Done

**Output:** every endpoint above exists, matches its documented shape, and — for `/v1/screen`/`/v1/ask` — reproduces doc 14b/15b's already-verified results exactly when called over real HTTP, not just when called as a Python function; saved screens are correctly scoped per-user; every call is logged to `app.usage_event`.

**Operationally, it can:** reject an invalid/missing auth token before touching any handler logic; return the same result for the same request twice (determinism, inherited from the Screener/AI Query it wraps); be extended with a real LLM-backed `/v1/ask` (once 6c exists) or real price data (once 4b's vendor is chosen) with zero route-level changes, since both are swapped behind interfaces this phase doesn't touch.

---

## What this phase does *not* decide

- **The public/B2B data API (`apps/data-api`)** — a different component, different auth model, different doc, gated on demonstrated external demand per doc 02/03. Nothing here is a stepping stone toward it by design.
- **Actual free/paid usage limits** — `app.user_entitlement`'s `tier` column exists; what a free user is and isn't allowed to do is still doc 02's open decision, due "before private beta."
- **Company detail data serving** — doc 04 already specifies Astro/Next.js read approved serving views directly from Postgres for this; duplicating that behind an endpoint here would contradict already-locked architecture, not extend it.
- **Rate limiting enforcement** — `app.usage_event` records what happened; nothing in this phase throttles based on it yet.
- **6c (real LLM) or 4b (real price vendor)** — both stay exactly as deferred as docs 13/15 already left them; this phase's endpoints call whatever `screener`/`ai_query` currently do, mock or real, without knowing the difference.

---

## Repository footprint

```text
apps/
└── backend/                    # NEW -- this phase, Scrooner's own internal API only
    ├── pyproject.toml              # depends on `pipeline` as a local package -- no logic duplication
    ├── main.py                     # FastAPI app, route registration
    ├── auth.py                     # 7a -- Supabase JWT verification dependency
    ├── routers/
    │   ├── screen.py                # 7b -- POST /v1/screen, POST /v1/ask
    │   ├── entitlement.py           # 7c -- GET /v1/me/entitlement
    │   └── saved_screens.py         # 7c -- saved-screen CRUD
    └── tests/
        └── test_golden_screens.py   # 7d -- real HTTP requests vs. doc 14b/15b expected results

pipeline/
└── db/
    └── migrations/
        └── 0007_app_schema.sql   # NEW -- this phase (app.user_entitlement, app.saved_screen, app.usage_event)
```

Migration stays in `pipeline/db/migrations/` (the one place all schema migrations already live, regardless of which app eventually reads/writes the tables) rather than duplicating a migrations folder inside `apps/backend/`.

---

## Gotchas to watch for, specifically

- Don't let `apps/backend` reimplement anything `screener/`/`ai_query/` already do — if a route handler needs new logic beyond calling `run_query()`/`interpret()`, that logic belongs in `pipeline/`, reviewed and verified the same way every other Screener/AI Query change has been, not written inline in a FastAPI handler.
- Don't let this phase's name or folder drift toward `apps/data-api` — that name is spoken for, deliberately, by a different, not-yet-greenlit product.
- Don't invent a specific rate limit number "since Frontend needs something to show" — return the real `tier`, log the real usage, and leave enforcement for whoever closes doc 02's still-open decision.
- Don't skip the real-HTTP-request verification step (7b/7d) in favor of just unit-testing the route functions — the whole point of this phase is proving that wrapping already-verified logic in HTTP didn't silently change anything, which a function-level test can't show.
