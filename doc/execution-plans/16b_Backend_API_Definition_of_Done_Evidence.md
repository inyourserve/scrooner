# 16b — Backend API Definition-of-Done: Evidence Report

Doc 16's deliverable: end-to-end proof against its Definition of Done, "demonstrated... not asserted." Gathered the same session all 4 stages were built, against a real running `uvicorn` server, real Supabase-issued JWTs from two real test users, and the golden-10 dataset — not a self-report.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes, or when Frontend (Part 8) needs an endpoint this doc didn't anticipate.

## Doc 16's exact Definition of Done, quoted verbatim

> **Output:** every endpoint above exists, matches its documented shape, and — for `/v1/screen`/`/v1/ask` — reproduces doc 14b/15b's already-verified results exactly when called over real HTTP, not just when called as a Python function; saved screens are correctly scoped per-user; every call is logged to `app.usage_event`.
>
> **Operationally, it can:** reject an invalid/missing auth token before touching any handler logic; return the same result for the same request twice (determinism...); be extended with a real LLM-backed `/v1/ask`... or real price data... with zero route-level changes.

---

## Base setup — real, not simulated

Two real Supabase Auth users created via the Admin API and signed in via the real password grant (genuine JWTs, not hand-crafted tokens): `test-golden-user@scrooner.test` and `test-second-user@scrooner.test`. `apps/backend` runs as a real `uvicorn` process on `127.0.0.1:8123`, hit with real `curl` requests throughout — no `TestClient` shortcut, no mocked HTTP layer.

`scrooner-pipeline` confirmed installed as an **editable local package** (`uv sync` output: `scrooner-pipeline==0.1.0 (from file:///Users/vikash/scrooner/pipeline)`) — the one-source-of-truth architecture decision from doc 16 is real, not aspirational.

---

## Output requirements

### Every endpoint exists and matches its documented shape — PASS

`GET /health`, `POST /v1/screen`, `POST /v1/ask`, `GET /v1/me/entitlement`, `GET/POST/PATCH/DELETE /v1/screens` all built and exercised with real requests.

### `/v1/screen`/`/v1/ask` reproduce doc 14b/15b exactly over real HTTP — PASS, after finding a real serialization concern

`POST /v1/screen` with `roe > 0.30`: matched `Apple Inc., MICROSOFT CORP, Alphabet Inc.`, excluded-missing `ENBRIDGE INC, TAIWAN SEMICONDUCTOR MANUFACTURING CO LTD` — **identical** to doc 14b. `POST /v1/ask` with `"companies with ROE above 30%", run=true` — identical matched set, identical explanation. `POST /v1/ask` with `"revenue growth above 10%"` — correctly returned the same ambiguity note as doc 15b, `query: null`, no silent default.

**Checked explicitly, not assumed**: whether wrapping the Screener's `Decimal` output in HTTP/JSON would silently lose precision — a real, live risk given this project's Decimal-everywhere discipline (doc 04). Confirmed FastAPI's default `jsonable_encoder` serializes `Decimal` as a full-precision **string** (`"1.199125744047619047619047619"`, not a lossy `1.199125744047619`-truncated float) with zero custom code required. Verified directly by reading the raw response body, not by trusting the framework's documentation.

### Saved screens correctly scoped per-user — PASS, after a real bug

First attempt: user1 created a screen, then **user1's own** rename/delete on it also failed with `404 Screen not found` — including the case that mattered (owning their own resource). Root cause: psycopg returns a `uuid.UUID` Python object for a Postgres `uuid` column, compared directly (`row[0] != user_id`) against the plain string `user_id` string this app gets from Supabase Auth — `UUID(...) != "a53aefa2-..."` is always `True` in Python, so the ownership check failed for every caller, not just unauthorized ones. **Not a security hole** — it failed closed, no unauthorized delete/rename ever succeeded — but a real functional bug: nobody, including the rightful owner, could manage their own saved screens. Fixed with `str(row[0]) != user_id`. Re-verified with a fresh screen and both users: user2's delete/rename attempts on user1's screen correctly return 404 both before and after the fix; user1's own rename/delete correctly succeed only after the fix.

### Every call logged to `app.usage_event` — PASS

Final tally after the full verification session: `ask_run=2`, `screen_run=4` — reconciled exactly against the number of `/v1/ask` and `/v1/screen` calls actually made (including the two duplicate `/v1/screen` calls used for the determinism check).

---

## Operational requirements

### Rejects invalid/missing auth before touching handler logic — PASS

Three cases against `GET /v1/me/entitlement`: no `Authorization` header → `401 Missing or malformed Authorization header`; garbage token → `401 Invalid or expired token`; a real, valid token → `200 {"tier": "free"}` (the default for a user with no `app.user_entitlement` row, confirmed correct — no row was created for either test user before this check).

### Determinism — PASS

Two consecutive `POST /v1/screen` calls with the same `debt_to_equity between (0,1)` body, over real HTTP, produced **byte-identical** response bodies (`diff` returned nothing).

### Extensible without route-level changes — Not yet exercised, by design

`routers/screen.py` calls `run_query()`/`interpret()` exactly as `pipeline`'s own CLI does — no branching on whether the underlying data is mock or real, no LLM-specific code path. Structurally true by construction (same functions, same imports); not separately re-tested with a real vendor since neither exists yet (doc 13/15 both still deferred).

---

## Bugs found and fixed during this build

1. **`json.dumps(model_dump())` on a `ScreenQuery` containing `Decimal`** — raw stdlib `json` can't serialize `Decimal` at all (unlike FastAPI's response-path `jsonable_encoder`, which handles it correctly). Fixed by using Pydantic's own `model_dump_json()` for the JSONB write, matching the exact guarantee already relied on for HTTP responses.
2. **`uuid.UUID` vs. `str` comparison in the saved-screen ownership check** — psycopg returns a typed `UUID` object for a `uuid` column; comparing it directly against the plain string `user_id` from Supabase Auth always evaluated `False`, blocking every caller including the legitimate owner. Fixed with an explicit `str()` cast.

Both were caught the same way every real bug in this project has been: by making the real call (create a screen, sign in as two different real users) rather than trusting the code's own logic by inspection.

---

## What this evidence does not cover

- **Real LLM (6c) or real price vendor (4b)** — both stay exactly as deferred as their own docs left them; this phase's endpoints are structurally ready but untested against either, since neither exists.
- **The separate, evidence-gated B2B `apps/data-api`** — explicitly a different component, not built or touched here.
- **Actual rate-limit enforcement** — `app.usage_event` records what happened; nothing throttles based on it yet, per doc 02's still-open usage-limits decision.
- **Production deployment/hosting** — verified against a local `uvicorn` process only; Infrastructure (Part 14) still owns where this actually runs.

## Conclusion

Every item in doc 16's Definition of Done is demonstrated with real, checked evidence — two real bugs found via genuine end-to-end testing (a real server, real users, real tokens) and fixed before being marked done, not asserted from reading the code. Per doc 16's own promotion rule, its status moves to **Canonical**.
