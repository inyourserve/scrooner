# Backend API — Stages 7a-7d

## Two serialization bugs, same root cause, two different layers

Both real bugs this phase found trace to the same underlying fact: FastAPI's automatic response encoding (`jsonable_encoder`) is not the only place data gets serialized, and it's easy to assume it covers a path it doesn't. `Decimal` values round-trip correctly through every HTTP *response* in this app for free — but the raw `json.dumps()` call used to build a JSONB column for a *database write* bypasses that entirely and crashes on the exact same `Decimal` values. The fix (`model_dump_json()` instead of `json.dumps(model_dump())`) is a one-line change, but the lesson is about where to place trust: "FastAPI handles this" is true for the response path and false for a manual serialization call three lines away in the same file, even though both start from the same Pydantic model.

## A security-adjacent bug that failed in the safe direction, and why that's not the same as "found early"

The `uuid.UUID` vs. `str` comparison bug meant the ownership check (`row[0] != user_id`) was `True` for *every* caller, including the actual owner — psycopg returns a typed `UUID` object from a `uuid` column, and that's never equal to the plain string Supabase Auth hands back. This failed closed: no unauthorized delete or rename ever succeeded, at any point, including before the fix. That's the fortunate direction for a bug like this to fail in — but it's worth being precise that "it never let the wrong person in" and "it works correctly" are different claims. The first was true from the start; the second wasn't, and only got caught because the very first thing tried after building the endpoint was the rightful owner actually using it, not just the negative case.

## Verifying the architecture decision, not just the code

Before writing a single endpoint, `uv sync` confirmed `scrooner-pipeline` installed as `(from file:///Users/vikash/scrooner/pipeline)` — an editable local dependency, not a copy. This was a one-line check that turned "we decided apps/backend should reuse pipeline's code, not duplicate it" from a design intention into a verified fact before any route handler was written. Worth doing this kind of check *before* building on top of an architectural decision, not after — if the dependency wiring had been wrong, every endpoint built on top of it would have needed rework, not just the wiring itself.

## Verification summary

- 2 real Supabase Auth users created via the Admin API, signed in via the real password grant — genuine JWTs used throughout, not hand-crafted tokens.
- `/v1/screen` and `/v1/ask`, called over real HTTP, reproduced doc 14b/15b's already-verified results exactly, including `Decimal` values preserved to full precision as strings.
- Auth rejection verified in 3 cases: missing header, invalid token, valid token.
- Per-user scoping verified in both directions: the non-owner blocked (before and after the fix), the owner allowed (only after the fix).
- Determinism confirmed via two consecutive identical requests, byte-identical response bodies.
- `app.usage_event` row counts reconciled exactly against the number of calls actually made.

## Why it matters going forward

Any future endpoint that writes a Pydantic model into a JSONB column should use `model_dump_json()` by default, not `json.dumps(model_dump())` — this is now a real, demonstrated failure mode, not a hypothetical one. And any future ownership/authorization check comparing a database-returned identifier against an application-level one should account for the two potentially being different Python types, not just equal-looking values — `str()` both sides explicitly rather than trusting `==` across a database driver boundary.
