-- 0110: analytics.company_slot_record - THE company-wise mapper table.
-- Design: data-team/strategy/EXCEPTION-RULE-REGISTER-DESIGN-2026-10-24.md (v2,
-- one table, not a register beside the mapper). Claimed in doc 53 on
-- 2026-10-25 by scrooner-25 after the Verifier passed the balance-sheet-totals
-- slot family (VERIFY-BS-TOTALS-V3-2026-10-25: 55 cells, 0 wrong).
--
-- One row = for ONE company, ONE canonical concept, ONE slot, ONE taxonomy era:
-- which face lines (member tags, with weights, under which calc parent) make
-- up the value in THAT company's own filing, read from the filing's
-- presentation/calculation tree. Resolution reads only status='verified' rows;
-- 'proposed' rows are triage-visible and change nothing shown.
--
-- Governance: evidence_accession is mandatory; evidence_level is the data
-- team's label; approved_by must differ from created_by (preparer never
-- approves own work; founder decision 2026-10-24: all-agent approval, founder
-- signs only novel definition calls); supersedes_id is the audit chain.
-- Additive, idempotent, no existing table touched.

create table if not exists analytics.company_slot_record (
    id                   bigint generated always as identity primary key,
    -- scope: a company row (cohort), a sector row (template), or a global fallback row
    company_id           bigint references core.company(id),
    sector_code          text,
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    slot                 text not null,            -- e.g. 'total_debt.current_borrowings', 'bs_totals.total_liabilities'
    rule_type            text not null check (rule_type in (
                           'tag_mapping',          -- v1: this tag feeds this slot
                           'slot_composition',     -- v1: member tags + weights under a calc parent
                           'not_applicable'        -- v1: evidenced N/A, feeds the single 'Not disclosed' state
                         )),
    composition_rule     text,                     -- slot_composition: 'printed_total' | 'face_sum' | 'hold_<reason>'
    member_tags          jsonb,                    -- [{tag, custom, weight, calc_parent, cal_confirmed, dedup}] from the filer's own cal
    requires_identity_tie boolean not null default false, -- face_sum values publish only when the statement identity ties on the same accession
    taxonomy_era_from    text,                     -- us-gaap taxonomy version of the first filing this applies to; null = all eras
    taxonomy_era_to      text,                     -- null = current
    filing_from          text,                     -- first accession observed with this face format
    filing_to            text,                     -- last accession observed with this face format
    period_from          date,                     -- first period_of_report observed
    period_to            date,                     -- last period_of_report observed
    filings_observed     integer,
    fingerprint_hash     text,                     -- the format-change gate's fingerprint this record was verified against
    cal_source           text,                     -- 'own' | 'own:xsd' | 'own:metalinks' | 'borrowed:<accessions>' | null
    record               jsonb,                    -- the full slot record as produced by the builder (equity/nci/mezzanine slots, exclusions, labels)
    evidence_accession   text not null,            -- REQUIRED: the filing this was read from
    evidence_level       text not null check (evidence_level in ('FILING-CHECKED','DATA-INFERRED')),
    source               text not null,            -- builder script + version, verifier report, pilot cell
    status               text not null default 'proposed'
                         check (status in ('proposed','verified','retired')),
    approved_by          text,                     -- independent approver (agent or founder), never the preparer
    approved_at          timestamptz,
    review_note          text,                     -- one line in the approver's own words
    supersedes_id        bigint references analytics.company_slot_record(id),
    created_by           text not null,
    created_at           timestamptz not null default now(),
    check (approved_by is not null or status <> 'verified'),
    check (approved_by is null or approved_by <> created_by),
    check (num_nonnulls(company_id, sector_code) <= 1)
);

comment on table analytics.company_slot_record is
    'Company-wise mapper: per company, concept, slot and taxonomy era, the filer''s own face lines that compose the value. Only status=verified rows resolve. Preparer never approves own row.';

create index if not exists company_slot_record_lookup_idx
    on analytics.company_slot_record (company_id, canonical_concept_id, slot, status);

create index if not exists company_slot_record_sector_idx
    on analytics.company_slot_record (sector_code, canonical_concept_id, slot)
    where sector_code is not null;

-- one verified record per (company, concept, slot, era start) at a time
create unique index if not exists company_slot_record_one_verified_idx
    on analytics.company_slot_record (company_id, canonical_concept_id, slot, coalesce(taxonomy_era_from, ''), coalesce(period_from, '0001-01-01'))
    where status = 'verified' and company_id is not null;
