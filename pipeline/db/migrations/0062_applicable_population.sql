-- 2026-09-12: corrected-coverage-denominator methodology, applied to the
-- whole registry, not just revenue/dividends -- see
-- doc/data-moat/learnings/2026-09-12-corrected-coverage-denominator-methodology.md
--
-- analytics.company_population: which named population(s) each company
-- belongs to (a company can belong to several -- e.g. a real operating
-- company that also pays dividends is in both). Rebuilt from scratch on
-- every classify_company_populations() run, same discipline as
-- data_point_registry/company_data_point_coverage.
create table if not exists analytics.company_population (
    company_id bigint not null references core.company(id),
    population_name text not null,
    primary key (company_id, population_name)
);

-- analytics.data_point_registry: which named population a data point's
-- coverage should be measured against. Defaults to 'real_operating_company'
-- (the corrected replacement for "all active companies") for anything not
-- explicitly narrower.
alter table analytics.data_point_registry
    add column if not exists applicable_population text not null default 'real_operating_company';
