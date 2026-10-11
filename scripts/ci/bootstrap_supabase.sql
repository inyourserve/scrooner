-- GitHub Actions runs the migrations against plain PostgreSQL, while the
-- deployed database is Supabase. Supabase owns auth.users; this minimal stub
-- lets CI validate Scrooner's foreign keys without copying Supabase internals.

create schema if not exists auth;

create table if not exists auth.users (
    id uuid primary key
);

-- Supabase also provides the standard API roles and auth.uid(); migrations that
-- add row-level-security policies reference them (0087/0088: `to authenticated`,
-- `auth.uid() = user_id`). Plain PostgreSQL in CI has neither. Roles are
-- cluster-wide, so create them only if missing.
do $$
declare
    r text;
begin
    foreach r in array array['anon', 'authenticated', 'service_role'] loop
        if not exists (select 1 from pg_roles where rolname = r) then
            execute format('create role %I nologin', r);
        end if;
    end loop;
end
$$;

-- Same contract as Supabase's: the caller's user id from the JWT claim, or NULL.
create or replace function auth.uid() returns uuid
language sql stable
as $$
    select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;
