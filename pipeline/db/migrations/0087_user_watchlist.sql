-- One default personal watchlist per user. The unique ownership/company pair
-- makes repeated adds idempotent and keeps the first useful version simple;
-- named lists can later be introduced as a parent table without changing
-- company identity or the customer-facing API.

create table if not exists app.watchlist_item (
    id         bigint generated always as identity primary key,
    user_id    uuid not null references auth.users (id) on delete cascade,
    company_id bigint not null references core.company (id) on delete cascade,
    created_at timestamptz not null default now(),
    unique (user_id, company_id)
);

create index if not exists idx_watchlist_item_user_created
    on app.watchlist_item (user_id, created_at desc);

-- Supports the company foreign key's delete path; the user-leading unique
-- constraint above cannot serve lookups beginning with company_id.
create index if not exists idx_watchlist_item_company
    on app.watchlist_item (company_id);

alter table app.watchlist_item enable row level security;

create policy "Users can read their own watchlist"
    on app.watchlist_item for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy "Users can add to their own watchlist"
    on app.watchlist_item for insert
    to authenticated
    with check ((select auth.uid()) = user_id);

create policy "Users can remove from their own watchlist"
    on app.watchlist_item for delete
    to authenticated
    using ((select auth.uid()) = user_id);

