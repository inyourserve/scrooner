-- App schema (doc 16, Part 7). First phase to actually populate `app` --
-- named in this project's architecture from the start ("Users, saved
-- screens, entitlements, usage events") but unbuilt until now.
--
-- Scoped deliberately to Scrooner's OWN internal product use, not the
-- separate, evidence-gated B2B data API (doc 16's naming clarification).
--
-- `app.user_entitlement`/`saved_screen`/`usage_event` reference
-- auth.users (Supabase's own managed table, created by enabling Auth --
-- never duplicated here).

create schema if not exists app;

-- Shape only, not policy: doc 02's "free vs paid usage limits" decision
-- is still open. This table answers "is this user paid," never "what are
-- they allowed to do" -- that enforcement doesn't exist yet, deliberately.
create table if not exists app.user_entitlement (
    user_id    uuid primary key references auth.users (id),
    tier       text not null default 'free' check (tier in ('free', 'paid')),
    updated_at timestamptz not null default now()
);

-- Stores the QUERY, not a result -- doc 16 Sec 4: the Screener is already
-- deterministic (doc 14b), so "rerun" is just "run again," not a new
-- operation, and a stored result would go stale the moment underlying
-- data changes.
create table if not exists app.saved_screen (
    id         bigint generated always as identity primary key,
    user_id    uuid not null references auth.users (id),
    name       text not null,
    query      jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists idx_saved_screen_user on app.saved_screen (user_id);

-- Append-only, recording only -- no enforcement reads this table yet.
-- user_id nullable: anonymous /v1/screen and /v1/ask calls are logged
-- too (both are auth-free per doc 16's API surface).
create table if not exists app.usage_event (
    id         bigint generated always as identity primary key,
    user_id    uuid references auth.users (id),
    event_type text not null check (event_type in ('screen_run', 'ask_run')),
    created_at timestamptz not null default now()
);
create index if not exists idx_usage_event_user on app.usage_event (user_id, created_at);
