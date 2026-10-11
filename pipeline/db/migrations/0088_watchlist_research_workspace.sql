-- Personal watchlist research state. Financial updates remain derived from
-- canonical filings/metrics; only user-authored state and review events live
-- here.

alter table app.watchlist_item
    add column if not exists note text,
    add column if not exists reviewed_at timestamptz,
    add column if not exists updated_at timestamptz not null default now();

create table if not exists app.watchlist_review (
    id bigint generated always as identity primary key,
    user_id uuid not null references auth.users (id) on delete cascade,
    company_id bigint not null references core.company (id) on delete cascade,
    reviewed_at timestamptz not null default now()
);

create index if not exists idx_watchlist_review_user_company_date
    on app.watchlist_review (user_id, company_id, reviewed_at desc);

alter table app.watchlist_review enable row level security;

create policy "Users can read their own watchlist reviews"
    on app.watchlist_review for select to authenticated
    using ((select auth.uid()) = user_id);

create policy "Users can create their own watchlist reviews"
    on app.watchlist_review for insert to authenticated
    with check ((select auth.uid()) = user_id);

create policy "Users can update their own watchlist items"
    on app.watchlist_item for update to authenticated
    using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);

