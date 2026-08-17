-- Company Master schema extensions (doc 13, Part 4a). Extends `core` --
-- Company Master completes identity structures the Normalizer already
-- created but deliberately left incomplete (see core.listing's own Stage 2a
-- comment). No new schema: `core` already owns "normalized identities."
--
-- core.market_price (Part 4b) is NOT created here -- doc 13 sketches its
-- shape but leaves it unbuilt until doc 02's market-price vendor decision
-- closes. Don't add it "while we're in here."

alter table core.company add column if not exists sic_code text;
alter table core.company add column if not exists sic_description text;
alter table core.company add column if not exists state_of_incorporation text;
alter table core.company add column if not exists entity_type text;
alter table core.company add column if not exists filer_category text;
alter table core.company add column if not exists status text
    check (status in ('active', 'stale', 'unknown'));
alter table core.company add column if not exists status_as_of date;
alter table core.company add column if not exists status_reason text;

-- How effective_from/effective_to (still nullable, still legitimately null
-- for a ticker with no known change date) were derived, so a downstream
-- consumer can tell an observed change from a proxied one from an honestly
-- unknown one. See doc 13 Sec 2.
alter table core.listing add column if not exists source text
    check (source in ('submissions_snapshot', 'former_names_backfill', 'unknown'));

-- Direct 1:1 capture of submissions' own formerNames array, plus the
-- current name as the still-open final interval. Useful standalone (a
-- company page's "formerly known as") and as the ticker-change-date proxy
-- signal doc 13 Sec 2 describes.
create table if not exists core.company_name_history (
    id             bigint generated always as identity primary key,
    company_id     bigint not null references core.company (id),
    company_name   text not null,
    effective_from date,
    effective_to   date,
    unique (company_id, company_name, effective_from)
);
