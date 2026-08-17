-- Stage 4 -- Form 13F institutional ownership (doc 19 Sec 5). Extends
-- `core`, same identity-adjacent home as insider_transaction/
-- beneficial_ownership (0009).
--
-- The CUSIP↔CIK crosswalk problem doc 19 originally deferred Stage 4
-- behind is resolved without any external vendor: Schedule 13D/13G cover
-- pages carry a mandatory CUSIP field for the subject security, and
-- Stage 3 (beneficial_ownership.py) already fetches that exact document.
-- See doc/learnings/form-13f-cusip-crosswalk.md for the live investigation.

-- Additive column -- captured from the same full-submission .txt Stage 3
-- already downloads, no new fetch. Nullable: a company whose only 13D/13G
-- filings predate a parseable cover-page format (none found in the
-- golden-10, but not guaranteed in general) simply has no CUSIP on file
-- yet, same "leave null, never guess" discipline as percent_of_class.
alter table core.beneficial_ownership add column if not exists cusip text;

-- One row per SEC Form 13F INFOTABLE line item whose CUSIP matches a
-- golden company's own (sourced from core.beneficial_ownership.cusip).
-- Deliberately NOT one row per company -- shares/value legitimately vary
-- per filing manager, and each row traces to its own accession_number
-- (doc 04's "every number traces to source" trust-moat requirement),
-- same granularity precedent as insider_transaction/beneficial_ownership.
--
-- Scoped to golden-company CUSIP matches only, not the full SEC 13F
-- universe -- the source bulk file covers ~6M info-table lines across
-- every US-listed security; storing all of it would blow the Supabase
-- free-tier 500MB budget for the same reason Normalizer/Mapper were
-- scoped to the golden-10 (doc 09's live-measured capacity check).
create table if not exists core.institutional_ownership (
    id                bigint generated always as identity primary key,
    company_id        bigint not null references core.company (id),
    accession_number  text not null,
    infotable_sk      bigint not null,
    filer_name        text not null,
    filer_cik         text,
    shares            numeric,
    -- Actual dollars, NOT thousands, despite the SEC field's original name
    -- (VALUE) and its own field-layout spec PDF's stale "(x$1000)"
    -- description -- the bulk zip's own bundled FORM13F_readme.htm states
    -- SEC changed this convention 2023-01-03 to report to the nearest
    -- dollar. Caught live: AAPL's own top holder briefly rendered as a
    -- $242 TRILLION position before this was found and fixed. Every row
    -- in this table is post-2023 data, so this is never ambiguous here.
    value_usd numeric,
    report_period     date,
    filing_date       date,
    is_amendment      boolean not null default false,
    source_zip        text not null,
    created_at        timestamptz not null default now(),
    unique (accession_number, infotable_sk)
);
create index if not exists idx_institutional_ownership_company on core.institutional_ownership (company_id, shares desc);

-- Lightweight provenance for the bulk 13F zip itself -- this is a
-- genuinely new SEC discovery fetch (unlike Form 4/13D-13G, which reused
-- raw.sec_submissions's already-fetched list), so it gets its own audit
-- row, mirroring raw.collector_runs's shape without the full per-object
-- granularity that table's per-company fetches need.
create table if not exists raw.sec_13f_bulk_fetch (
    id                  bigint generated always as identity primary key,
    source_url          text not null,
    window_label        text not null,
    sha256              text not null,
    fetched_at          timestamptz not null default now(),
    infotable_row_count bigint,
    matched_row_count   bigint,
    unique (window_label)
);
