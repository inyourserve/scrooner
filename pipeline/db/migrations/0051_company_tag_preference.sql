-- Per-company SEC tag preference (2026-09-08, explicit user direction):
-- "for every data fill or fix, use only SEC EDGAR, yfinance for sanity
-- and matching only -- we have to store the sec tag wrt metric, company
-- and fetch from sec only."
--
-- Supersedes analytics.canonical_fact_sanity_override's per-PERIOD value
-- snapshot (migration 0049) with a per-COMPANY TAG preference instead --
-- once the Tag Investigator confirms a specific SEC tag reconciles for a
-- company (against yfinance, used only to detect/verify, never as the
-- stored value), that tag preference applies to EVERY period the company
-- has data for under it, not just the one period that was flagged. The
-- actual VALUE always comes from core.fact (a real SEC filing), never
-- from yfinance -- yfinance's role stops at "this is the tag that
-- reconciles," it never supplies a number that gets stored.
--
-- Old canonical_fact_sanity_override rows/table are left in place
-- (harmless, no longer written to) rather than dropped -- see doc 44 /
-- doc/learnings/2026-09-08-yfinance-financials-system.md for the
-- migration note.

create table if not exists analytics.company_tag_preference (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    taxonomy text not null,
    tag text not null,
    confidence text not null default 'provisional' check (confidence in ('approved', 'provisional', 'rejected')),
    evidence text not null,
    discovered_at timestamptz not null default now(),
    unique (company_id, canonical_concept_id)
);

create index if not exists idx_company_tag_preference_concept on analytics.company_tag_preference (canonical_concept_id);
