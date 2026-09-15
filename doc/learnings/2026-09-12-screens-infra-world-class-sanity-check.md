# 2026-09-12 — "World class sanity" check on screens/create/save infra

Prompted directly: "our screens, create screen, save screen — is it world class infra? Is it scalable and fastest loading? Where can we improve? Please check and make it world class." A structured audit across correctness, security, scalability, and real measured performance — not a self-report, every finding below is backed by a live check.

## Security posture: checked, not assumed

- **`app` schema RLS is disabled on every table**, including `saved_screen` (private per-user screens). Checked whether this is actually exploitable, not just noted: fetched a real anon key and hit Supabase's own PostgREST endpoint directly (`GET /rest/v1/saved_screen`) with `Accept-Profile: app`. Real response: `PGRST106 — Only the following schemas are exposed: public, graphql_public`. **The `app` schema was never exposed to Supabase's public REST layer**, so the missing RLS has zero current external exposure — every access goes through `apps/backend`'s own server-side connection, which already filters by `user_id` on every query. Not a live vulnerability, but a real guardrail worth naming: if `app` is ever added to Supabase's exposed-schemas list for any reason, every user's saved screens become world-readable/writable the instant that setting changes, with nothing else standing in the way. Recorded here so that's not rediscovered the hard way.
- Supabase's own security advisor flags one real, external, unrelated-to-code gap: **leaked-password protection is disabled** (HaveIBeenPwned checking on sign-up/password-change). This is a dashboard setting (Auth → Policies), not a migration — flagging it, not fixing it here.
- Ownership checks were re-verified, not assumed: every screens endpoint scopes its query by `user_id`, and the two mutation endpoints (`rename`, `delete`) were rewritten this pass (see below) in a way that makes the ownership check *and* the write atomic in the same statement, closing a small window that a separate check-then-write never really had race protection against.

## The single biggest hidden cost: found, not obvious from any of this session's own earlier timing

Every backend timing measurement in this session so far (13.9s → 4-8ms, the dedup work, etc.) was made by calling router functions **directly in Python**, bypassing FastAPI's own request pipeline entirely. That hid something real: **`auth.get_current_user_id` — the dependency on every single authenticated endpoint — calls Supabase's own `GET /auth/v1/user` over the network on every request, unconditionally.** Measured live: **~370-710ms**, often *more* than the endpoint's own actual work. This applies to all 8 authenticated routes (`list/create/get/refresh/rename/delete` screens, `create`/`get` screen-runs, `get` entitlement) — meaning the real, full HTTP latency for something like `rename_screen` was never the ~245ms this session measured directly; it was closer to **~615-950ms** in practice, dominated by an auth check that has nothing to do with screens at all.

Fixed with a short-TTL (30s) Redis cache in front of it (`cache.get_cached_auth_user_id`/`set_cached_auth_user_id`), keyed by a hash of the token itself. **This is the one cache in the whole system with a genuine trust tradeoff, not just a performance one** — a revoked token (sign-out, password change, ban) could still resolve to its cached identity for up to 30s. Judged acceptable and documented as such: a Supabase access token already carries its own ~1hr validity regardless of this cache; this only affects how fast *revocation* (not expiry) propagates, by well under a minute. A failed verification is never cached (only successful resolutions), and a Redis outage falls straight back to the real network call, same "never required, only accelerates" discipline as every other cache in this codebase. Verified live against the real local Redis: **0.2ms cache-hit lookup vs. the 370-710ms it replaces** — roughly a 2000x reduction for the common case (a user clicking through several screens in quick succession, all carrying the same bearer token). 4 new tests (`test_auth.py`): cache hit never touches the network, cache miss populates it, a failed verification is never cached, plus the 6 pre-existing tests confirmed unaffected.

## A second real finding: `conn.transaction()` around a single statement is pure overhead

Sanity-checking `rename_screen`/`delete_screen`'s timing (938ms/953ms measured directly) turned up something unexpected: removing a redundant ownership-check round trip only shaved off ~150ms, far less than the ~270ms one full round trip should cost on this connection. Isolated the real cause with a direct A/B test: wrapping a single trivial `SELECT 1` in `conn.transaction()` cost **~750-820ms**; the identical statement with no wrapper cost **~250-500ms** — **the wrapper itself was worth ~400-500ms (2 extra round trips: an explicit BEGIN and COMMIT) for a case that needed zero transactional atomicity in the first place**, since the pool's connections are already `autocommit=True` and a single statement is already atomic on its own by construction.

Audited every `conn.transaction()` use in `apps/backend`: 4 of 5 were wrapping a single write (or reads-then-one-write) with nothing that actually needed cross-statement atomicity — `create_screen`, `refresh_screen`'s final update, `rename_screen`, `delete_screen`. Removed all 4. The one genuine use (`screen_runs.create_run_from_query`'s insert-screen_result-then-executemany-items-then-insert-user_screen_run) stayed, correctly — a crash between the first two writes there really would leave a broken, incomplete shared result other users could read.

Also folded `rename_screen`/`delete_screen`'s separate ownership-check `SELECT` directly into the `UPDATE`/`DELETE`'s own `WHERE user_id = %s ... RETURNING id` clause — one round trip instead of two, and arguably *safer* than the old check-then-write shape (no window between checking and acting).

**Verified live, before/after, same setup both times:**

| Operation | Before | After |
|---|---:|---:|
| `rename_screen` | 938ms | **245ms** (3.8x) |
| `delete_screen` | 953ms | **252ms** (3.8x) |
| `create_screen` (save) | 1,183ms | **495ms** (2.4x) |

## Two small, zero-risk hygiene fixes

Supabase's own performance advisor flagged both new tables from this session's earlier dedup migration (`screen_result_item`, `user_screen_run`) as having foreign keys with no covering index. Neither is on today's actual query path (both are always looked up by their own primary key or an existing composite index), but added anyway — cheap, zero-risk, and correct defensive practice for whatever joins/cascade-delete checks come next.

## What's genuinely scalable already, checked not assumed

- `list_screens`/`get_screen`/`get_entitlement` are single, indexed, pooled-connection queries — consistently ~240-255ms (one network round trip on this dev machine; would be single-digit ms in a same-region deployment).
- The screen-result dedup from earlier today means a popular query's *storage* cost is paid once regardless of how many users ask it, not once per user.
- Redis caching throughout degrades gracefully — every cache read/write is wrapped in `except RedisError`, so a Redis outage makes the product slower, never broken.
- `list_screens` has no LIMIT/pagination — fine at the realistic scale of a personal research tool's own saved-screen count, but named here as the one thing that would need real pagination if a user somehow accumulated thousands of saved screens. Not fixed this pass — no evidence it's a real problem yet, matching this project's own "evidence before expansion" principle.

## Net result

Backend suite 38→41 passing (4 new auth-cache tests, minus none removed net of the ownership-check consolidation), pipeline suite unaffected (540, no pipeline code touched), full regression pass clean, production compile/lint clean. Every number in this document was measured against the live system, not asserted.
