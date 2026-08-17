-- Phase 1 EDGAR signal batch (doc 24): 5 small, zero-new-fetch additions,
-- each already scoped with real evidence in doc 23.

-- 8-K structured item classification (doc 21) -- comma-separated item
-- codes exactly as raw.sec_submissions already carries them (e.g.
-- "2.02,9.01"), captured while normalizing identity. NULL for any
-- non-8-K form and for any 8-K where EDGAR itself didn't populate items.
alter table core.filing add column if not exists items text;

-- Form 15/15F -> a real, evidenced `delisted` status (doc 23 Stage C).
-- Widened, not replaced: `active`/`stale`/`unknown` keep their exact
-- existing meaning (company_master/status.py's own module docstring) --
-- `delisted` is the one state that previously had no data source at all.
alter table core.company drop constraint if exists company_status_check;
alter table core.company add constraint company_status_check
    check (status in ('active', 'stale', 'unknown', 'delisted'));

-- Form 4's aff10b5One (doc 23 Stage A) -- whether the filing's
-- transaction(s) were made under a Rule 10b5-1(c) trading plan. Nullable:
-- the field doesn't exist on any Form 4 filed before 2023-04-01, and a
-- missing value must never be defaulted to false (same "leave null,
-- don't guess" discipline as percent_of_class/shares_owned).
alter table core.insider_transaction add column if not exists is_10b5_1_plan boolean;
