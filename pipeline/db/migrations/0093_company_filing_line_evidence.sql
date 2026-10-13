-- Per-company evidence of whether a concept's line appears on the face of the
-- company's latest 10-K/10-Q balance sheet or income statement
-- (parsers/filing_line_evidence.py). Independent of our XBRL extraction, so it
-- can tell "this line does not exist for this kind of company" from "it is in
-- the filing and we failed to extract it" -- which the coverage score cannot do
-- from our own data (defining "applies" as "has a value" is circular).
--
-- Evidence, not proof: a line absent from the statement's face may still be
-- disclosed in the notes (measured: 14-34% of the time we HAVE a value without
-- a face line), so the stored fact is "not shown on the statements", and every
-- row keeps the accession it was read from.
--
-- gap_reason values written onto company_data_point_coverage by
-- coverage_matrix.apply_filing_line_evidence():
--   line_not_presented_in_filing          line_present = false
--   line_presented_combined_with_others   line_present and combined
--   line_in_filing_not_extracted          line_present and not combined (a real gap)

create table if not exists analytics.company_filing_line_evidence (
    company_id       bigint not null references core.company (id) on delete cascade,
    data_point       text not null,
    statement        text not null check (statement in ('BS', 'IS')),
    -- true: a matching row exists; false: the statement was read and has none;
    -- null: the statement could not be located (no evidence either way).
    line_present     boolean,
    matched_label    text,
    -- true when the matching label is a combined line ("Accounts payable and
    -- accrued expenses"): the plain concept is not presented on its own, and
    -- mapping the combined total as the plain concept would be wrong.
    combined         boolean not null default false,
    accession_number text not null,
    form             text not null,
    checked_at       timestamptz not null default now(),
    primary key (company_id, data_point)
);

create index if not exists idx_filing_line_evidence_point_present
    on analytics.company_filing_line_evidence (data_point, line_present);

comment on table analytics.company_filing_line_evidence is
    'Does the concept''s line appear on the face of the latest 10-K/10-Q balance sheet / income statement? Evidence, not proof (notes-only disclosure is possible). See parsers/filing_line_evidence.py.';
