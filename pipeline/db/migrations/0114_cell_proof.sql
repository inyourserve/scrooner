-- 0114: analytics.cell_proof -- one proof row per displayed cell (2026-10-31).
--
-- Founder direction: assume every production value from the EDGAR pipeline may
-- be wrong; one proof system instead of per-family patches. A cell is PROVEN only
-- when the value production shows today (a) equals, at the filer's presentation
-- precision, the value at the statement position the structure selects (b: the
-- slot-record line, or the printed total by pre/calc), b's line is the expected
-- printed statement line (a total, not a component), and every check passes.
-- Independence comes from POSITION, the identity checks and the printed-page
-- sample (c), never from comparing two numeric feeds of the same XBRL instance
-- (companyfacts and FSN num are the same instance; comparing them proves nothing,
-- the same trap as validating against SEC Frames, root CLAUDE.md 2026-10-18).
-- The website serves only PROVEN cells once proof.serve_proven_only@1 is ON;
-- until then UNCHECKED never blanks a cell that is on screen today.
-- Cell key = the 0100 contract (cell_evidence / cell_blank_reason join on it).

create table if not exists analytics.cell_proof (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company (id),
    data_point_name text not null,
    period_grain text not null check (period_grain in ('FY', 'Q', 'TTM', 'I', 'TP')),
    period_start date not null,
    period_end date not null,
    basis text not null default 'latest' check (basis in ('latest', 'as_filed')),
    -- (a) what production shows today, with its provenance
    shown_value numeric,
    shown_tag text,
    shown_accession text,
    shown_source_fact_ids bigint[] not null default '{}',
    -- (b) the value at the structure-selected statement position
    position_value numeric,
    position_tag text,
    position_accession text,
    position_source text check (position_source in ('slot_record', 'fsn_pre_calc', 'face_total')),
    fsn_set text,
    fsn_stmt text,
    fsn_line integer,
    fsn_label text,
    fsn_calc_parent text,
    position_is_expected_line boolean,
    -- (c) the printed statement page, sampled or on disagreement
    face_value numeric,
    face_report text,
    face_label text,
    face_scale numeric,
    face_hash text,
    -- checks: {identity_tie, components_sum, period_length, unit_scale} -> {status: pass|fail|n/a, ...numbers}
    checks jsonb not null default '{}'::jsonb,
    verdict text not null check (verdict in ('PROVEN', 'DISAGREE', 'NOT_PRESENTED', 'UNCHECKED')),
    reason_code text,
    reason_text text,
    rule_id text not null default 'proof.cell_proof@1'
        check (rule_id ~ '^[a-z][a-z0-9_]*(\.[A-Za-z0-9_]+)+@[0-9]+$'),
    detector_version text not null,
    proved_at timestamptz not null default now(),
    check (period_start <= period_end),
    check (period_grain <> 'I' or period_start = period_end),
    check (verdict <> 'PROVEN' or (shown_value is not null and position_value is not null and position_is_expected_line)),
    check ((verdict in ('DISAGREE', 'NOT_PRESENTED')) = (reason_code is not null)),
    unique (company_id, data_point_name, period_grain, period_start, period_end, basis, rule_id)
);

create index if not exists idx_cell_proof_company on analytics.cell_proof (company_id);
create index if not exists idx_cell_proof_verdict on analytics.cell_proof (verdict);
create index if not exists idx_cell_proof_accession on analytics.cell_proof (shown_accession);

comment on table analytics.cell_proof is
    'One proof row per displayed cell: shown value (a), structure-selected position value (b), face sample (c), checks, verdict. 2026-10-31.';
