-- Real gap found live 2026-08-17 verifying mapper/price_metrics.py:
-- Block and Reddit both have zero point-in-time shares_outstanding
-- facts in core.fact at all. Confirmed root cause: both are multi-class
-- share structure companies (Reddit: Class A/B/C, Block: Class A/B)
-- whose SEC cover-page disclosure is dimensionally tagged per class --
-- the same "dimensional XBRL" limitation doc 22 already found for
-- segment revenue, confirmed here to also strip share counts entirely
-- from the standard Company Facts API.
--
-- A SEPARATE table, not a core.fact row -- this is sourced from cover-
-- page TEXT parsing (Company Master's job, ingests real data it fetches
-- itself), not XBRL (the Normalizer's exclusive domain, and that module
-- has a hard "no new network calls" boundary this genuinely violates,
-- since the cover page document isn't already in Storage). Mirrors the
-- exact same Company-Master-ingests/Mapper-calculates split already
-- used for core.market_price_alpaca (doc 25).
create table if not exists core.shares_outstanding_fallback (
    id                bigint generated always as identity primary key,
    company_id        bigint not null references core.company (id),
    shares            numeric not null,
    source            text not null default 'cover_page_text',
    accession_number  text not null,
    filing_date       date,
    extracted_at      timestamptz not null default now(),
    unique (company_id)
);
