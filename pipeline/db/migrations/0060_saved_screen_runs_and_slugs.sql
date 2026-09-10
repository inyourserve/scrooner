-- Persist immutable screener runs so pagination, reloads, and saved screens
-- read an existing result instead of executing the financial query again.

create table if not exists app.screen_run (
    id               uuid primary key default gen_random_uuid(),
    user_id          uuid not null references auth.users (id),
    query_text       text not null,
    normalized_query jsonb not null,
    total_count      integer not null check (total_count >= 0),
    exclusions       jsonb not null default '{}'::jsonb,
    created_at       timestamptz not null default now(),
    expires_at       timestamptz
);

create index if not exists idx_screen_run_user_created
    on app.screen_run (user_id, created_at desc);

create table if not exists app.screen_run_result (
    run_id       uuid not null references app.screen_run (id) on delete cascade,
    position     integer not null check (position >= 0),
    company_id   bigint not null references core.company (id),
    result       jsonb not null,
    primary key (run_id, position),
    unique (run_id, company_id)
);

alter table app.saved_screen add column if not exists slug text;
alter table app.saved_screen add column if not exists last_run_id uuid references app.screen_run (id) on delete set null;

-- Existing private screens receive a stable collision-free slug. New screens
-- get human slugs in application code before the column becomes required.
update app.saved_screen
set slug = trim(both '-' from regexp_replace(lower(name), '[^a-z0-9]+', '-', 'g')) || '-' || id
where slug is null;

alter table app.saved_screen alter column slug set not null;

create unique index if not exists idx_saved_screen_user_slug
    on app.saved_screen (user_id, slug);

create index if not exists idx_saved_screen_last_run
    on app.saved_screen (last_run_id)
    where last_run_id is not null;
