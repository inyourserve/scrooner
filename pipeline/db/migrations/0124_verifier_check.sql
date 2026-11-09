-- Verifier filing checks as data (certification ladder, FSN era; founder approval relayed by
-- Dhairya 2026-11-09). One row per cell a Verifier opened in the original filing: the shown
-- value, the printed value, the accession and the locator (R page and row). The `verified`
-- rung of analytics.company_certification is granted by `scrooner-certify-promote` only when
-- the company's latest headline cells each have a `right` row whose shown_value equals the
-- value served today, and the company has no open `wrong` row. Until now verdicts lived only
-- in markdown reports, which no code can read.
-- A verdict that a later fix makes obsolete is closed by setting superseded_at and
-- superseded_reason once; rows are never deleted.
-- Written 2026-11-09 (work/certification-lead/promote); NOT applied; applying it needs the
-- founder's typed words.
create table if not exists analytics.verifier_check (
    id                 bigint generated always as identity primary key,
    company_id         bigint not null references core.company (id),
    data_point_name    text   not null check (btrim(data_point_name) <> ''),
    period_grain       text   not null check (period_grain in ('FY', 'Q', 'I', 'TTM')),
    period_start       date   not null,
    period_end         date   not null,
    basis              text   not null default 'latest' check (basis in ('latest', 'as_filed')),
    -- right / wrong: a shown value compared with the filing; blank_right / blank_wrong: a blank
    -- and its stated reason compared with the filing
    verdict            text   not null check (verdict in ('right', 'wrong', 'blank_right', 'blank_wrong')),
    shown_value        numeric,
    filing_value       numeric,
    accession          text check (accession ~ '^[0-9]{10}-[0-9]{2}-[0-9]{6}$'),
    locator            text,
    draw_id            text   not null check (btrim(draw_id) <> ''),
    verifier_session   text   not null check (btrim(verifier_session) <> ''),
    report_path        text,
    note               text,
    checked_at         timestamptz not null default now(),
    superseded_at      timestamptz,
    superseded_reason  text,
    check (period_start <= period_end),
    check (period_grain <> 'I' or period_start = period_end),
    -- a value verdict names what was shown and where in the filing it was checked
    check (verdict not in ('right', 'wrong')
           or (shown_value is not null and accession is not null and coalesce(btrim(locator), '') <> '')),
    check (verdict <> 'right' or filing_value is not null),
    check ((superseded_at is null) = (superseded_reason is null))
);

create index if not exists idx_verifier_check_cell
    on analytics.verifier_check (company_id, data_point_name, period_grain, period_end);
create index if not exists idx_verifier_check_open_wrong
    on analytics.verifier_check (company_id)
    where verdict in ('wrong', 'blank_wrong') and superseded_at is null;

comment on table analytics.verifier_check is
    'Verifier filing checks, one row per opened cell (0122, 2026-11-09). Read by scrooner-certify-promote for the verified rung.';
