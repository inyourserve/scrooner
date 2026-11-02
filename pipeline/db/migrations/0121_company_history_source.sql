-- 0121: where a company's 2015-to-date filing history lives (scrooner-87, 2026-11-01; rulings Dhairya 2026-11-01).
-- History follows the economic entity the company reports as itself (the accounting predecessor), judged by
-- the company's own later 10-K comparative columns, not the legal registrant.
--   relation 'predecessor': filings of source_cik with period in [valid_from, valid_to] are this company's
--     history (holding-company reorganisation: Exxon Mobil Corp 0000034088 -> ExxonMobil Holdings Corp; merger
--     whose legal acquirer reports the other party: Praxair -> Linde). One CIK may serve several companies in
--     separate windows (Dow Chemical: Dow Inc and DowDuPont); one company may have several predecessors
--     (Broadcom, STERIS), and their windows must not overlap.
--   relation 'exclude': the company's OWN filings in the window are another entity's (the legal acquirer's
--     pre-merger filings: Tyco under Johnson Controls' CIK) and are not its history (wrong_entity_history).
-- Seeded from data-team/47-fsn-store/company_history_sources.csv. The FSN store shard writes predecessor
-- filings into the company's directory and skips excluded ones. NOT applied: needs the founder's typed words.
create table if not exists core.company_history_source (
    company_id   bigint not null references core.company (id),
    source_cik   text   not null check (source_cik ~ '^[0-9]{10}$'),
    relation     text   not null check (relation in ('predecessor', 'exclude')),
    source_name  text   not null,
    valid_from   date   not null,
    valid_to     date   not null,
    reason       text   not null check (btrim(reason) <> ''),
    evidence     text,
    created_at   timestamptz not null default now(),
    primary key (company_id, source_cik, valid_from),
    check (valid_from <= valid_to)
);

create index if not exists idx_company_history_source_cik on core.company_history_source (source_cik);

-- predecessor windows of one company must not overlap
create or replace function core.company_history_source_no_overlap() returns trigger
language plpgsql as $$
begin
    if new.relation = 'predecessor' and exists (
        select 1 from core.company_history_source s
        where s.company_id = new.company_id and s.relation = 'predecessor'
          and (s.source_cik, s.valid_from) <> (new.source_cik, new.valid_from)
          and s.valid_from <= new.valid_to and new.valid_from <= s.valid_to
    ) then
        raise exception 'overlapping predecessor window for company % (% to %)', new.company_id, new.valid_from, new.valid_to;
    end if;
    return new;
end;
$$;

drop trigger if exists trg_company_history_source_no_overlap on core.company_history_source;
create trigger trg_company_history_source_no_overlap
    before insert or update on core.company_history_source
    for each row execute function core.company_history_source_no_overlap();

comment on table core.company_history_source is
    'Company filing history sources: predecessor CIK windows and wrong-entity exclusions of its own CIK.';
