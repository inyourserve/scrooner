-- GitHub Actions runs the migrations against plain PostgreSQL, while the
-- deployed database is Supabase. Supabase owns auth.users; this minimal stub
-- lets CI validate Scrooner's foreign keys without copying Supabase internals.

create schema if not exists auth;

create table if not exists auth.users (
    id uuid primary key
);
