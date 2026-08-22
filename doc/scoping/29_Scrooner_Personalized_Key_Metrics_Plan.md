# Doc 29 — Personalized Key Metrics (Company Page) — Execution Plan

**Status: Draft (2026-08-22) — a concrete plan, not yet built.** Scoped narrowly to one feature: letting a logged-in user choose which metrics appear in the company page's "Key Metrics" bar (`apps/site`'s `keyMetrics` array, currently a single hardcoded 8-item set for every user — design framework §12.2's own recommended list). Explicitly does **not** cover custom peer sets or any other personalization idea raised alongside it — those are named as future, separate features (see "Why this generalizes" below), not designed or built here.

**Hard dependency, not yet built:** this entire feature requires Part 9 (User System / auth) to exist. `apps/site` currently has zero auth awareness — no session read, no login state, nothing. Nothing in this plan can start until Part 9 lands; this doc exists so the shape is decided ahead of time, not so it can jump the queue.

## The problem, stated plainly

Every visitor to `/stock/{ticker}/` — logged in or not — sees the exact same 8 metrics up top (Market Cap, P/E, Revenue Growth 3Y CAGR, Operating Margin, ROIC, FCF Yield, Debt/Equity, Share Count Dilution). A logged-in user should be able to pick their own set from the full 45-metric catalog, and have it apply globally across every company page they visit — not a per-ticker setting (nobody wants to configure this separately for AAPL vs. MSFT).

## Architecture — no new cross-service coupling

This reuses two things this project has already built rather than inventing a third system:

1. **The shared session cookie** (`Domain=.scrooner.com`, doc 04) — already the planned mechanism for `app.scrooner.com` login to carry across to `scrooner.com`. Supabase Auth JWTs are self-verifying, so Astro can check who's logged in **without calling `apps/backend` or the Next.js app at all** — same `@supabase/ssr` library Next.js already uses, just instantiated server-side inside the Astro route.
2. **Astro's existing direct-Postgres pattern** (`apps/site/src/lib/db.ts`, doc 04/17: "Astro reads approved serving views directly") — once Astro has a `user_id` from the verified cookie, it queries the new preference table the same way it queries everything else on that page. No new dependency on `apps/backend` for the read path.

Writing the preference (the picker UI itself) is genuinely "authenticated interaction," so it belongs on `app.scrooner.com` (Next.js) → `apps/backend` → Postgres, the same auth-checked write path `app.saved_screen` already proved out (doc 16).

```
Logged-out visitor  →  scrooner.com/stock/aapl  →  hardcoded default 8 metrics (unchanged)

Logged-in visitor   →  scrooner.com/stock/aapl  →  Astro verifies the shared cookie server-side
                                                 →  queries app.user_key_metrics_preference directly
                                                 →  found?  use it  :  fall back to the same hardcoded default

Editing preference   →  app.scrooner.com/settings  →  apps/backend (auth-checked write)
                                                     →  app.user_key_metrics_preference
```

## New schema

One new table, same shape/conventions as the existing `app.saved_screen`/`app.user_entitlement` (doc 16, `db/migrations/0007_app_schema.sql`) — `user_id` as the primary key (one preference per user, not a history of them), a plain Postgres array (not JSONB) since this is just an ordered list of metric names, nothing nested:

```sql
create table if not exists app.user_key_metrics_preference (
    user_id      uuid primary key references auth.users (id),
    metric_names text[] not null,
    updated_at   timestamptz not null default now()
);
```

`metric_names` is validated against the real screenable/displayable metric catalog at write time (`apps/backend`, not a DB constraint — same "validate in application code, not a check constraint" pattern already used elsewhere) — a stale or renamed metric_name should fail the write with a clear error, never silently store garbage the Astro page then can't resolve. Astro's read path treats any `metric_names` entry that isn't a real, currently-known metric as if it weren't in the list at all (skip, don't crash) — the same "null over guess" discipline as everywhere else, applied to a config value instead of a financial one.

## Build stages

**Stage A — Astro session verification (the one genuinely new capability).** Add a small `apps/site/src/lib/auth.ts` that reads the shared cookie via `@supabase/ssr`'s server client and returns `{ userId } | null`. This is `apps/site`'s first-ever auth-aware code — test explicitly that an anonymous visitor gets `null` (not an error) and that the page's existing fully-public rendering path is completely unaffected when auth fails or the cookie is absent. This is also the natural place to verify the doc 04 cross-domain cookie plumbing actually works end-to-end for the first time, since nothing has exercised it yet.

**Stage B — Migration.** `app.user_key_metrics_preference`, per the schema above.

**Stage C — Backend endpoints** (`apps/backend`, doc 16's existing pattern): `GET /v1/me/key-metrics` (returns the current list or the default), `PUT /v1/me/key-metrics` (validates against the real metric catalog, upserts). Reuses the exact ownership/auth-check pattern doc 16b already proved (and already fixed one real bug in — the `uuid.UUID`-vs-`str` comparison trap — so this new endpoint should `str()` both sides from the start rather than rediscover that bug a second time).

**Stage D — Picker UI** (`app.scrooner.com`, Next.js): a simple settings surface — show the full 45-metric catalog grouped the same way the company page's own categories already are (Valuation/Growth/Profitability/etc., doc 17), let the user check/order up to 8, save via Stage C's endpoint.

**Stage E — Astro page wiring.** `[ticker].astro`'s `keyMetrics` construction becomes: verified user_id present → query `app.user_key_metrics_preference` → present and non-empty → use it; anything else (logged out, no row yet, row present but empty) → fall back to today's exact hardcoded default. The default set itself doesn't change and stays the fallback for every currently-existing user until they actively customize.

## Why this generalizes to future personalization (peers, etc.) without a rewrite now

Not by building a generic "user preference" framework today — this project's own operating principle ("three similar lines is better than a premature abstraction," doc 05) argues directly against that, and every existing `app`-schema table (`saved_screen`, `user_entitlement`, `usage_event`) is already its own precisely-named table, not a shared generic store. A future custom-peers feature would follow the exact same shape as this one — its own table (e.g. `app.user_peer_set`), its own pair of backend endpoints, its own picker UI — reusing Stage A's session-verification helper (already generic, not Key-Metrics-specific) and Astro's already-proven "verify, then query Postgres directly" read pattern. The thing that generalizes is the *pattern*, not a shared table or a JSONB blob with a type discriminator — which is also why this plan doesn't propose one.

## Sequencing

This sits behind Part 9 (User System) in the backlog (doc 24), the same dependency every other personalization idea has. Once Part 9 exists, Stage A is the only genuinely new architectural risk (the cross-domain cookie has never been exercised); Stages B-E are all small, precedented, low-risk additions on top of already-proven patterns (doc 16's backend/auth work, doc 17's company page).
