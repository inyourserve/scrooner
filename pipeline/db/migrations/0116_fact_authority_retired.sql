-- 0116 (claimed by scrooner-26, Dhairya 2026-11-03; doc 53): before-image of every core.fact authority change made
-- by a reviewed retirement run (mapper/derived_row_retirement.py apply_plan: Family A derived ratio facts, Family B
-- proxy-form facts, Family C derived EPS facts). A fact is never deleted: a run sets is_authoritative and logs the
-- prior value here, in the SAME transaction; restore(run_id) writes prior_is_authoritative back and stamps
-- restored_at. NOT applied; production applies need the founder's own words.
--
-- Same columns as FACT_AUTHORITY_RETIRED_DDL_DRAFT (the draft the reviewed code and its dry runs were written
-- against): fact_id / company_id / rule_id / reason_code / run_id / prior_is_authoritative / retired_at / restored_at.

create table if not exists analytics.fact_authority_retired (
    id                     bigint generated always as identity primary key,
    fact_id                bigint not null,
    company_id             bigint not null,
    rule_id                text not null,
    reason_code            text not null,
    run_id                 text not null,
    prior_is_authoritative boolean not null,
    retired_at             timestamptz not null default now(),
    restored_at            timestamptz
);

create index if not exists idx_fact_authority_retired_run
    on analytics.fact_authority_retired (run_id);

create index if not exists idx_fact_authority_retired_fact
    on analytics.fact_authority_retired (fact_id);
