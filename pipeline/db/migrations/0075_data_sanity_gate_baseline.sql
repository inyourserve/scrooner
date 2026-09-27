-- Baseline for the yfinance sanity CI gate (2026-09-27, founder direction:
-- "fail on regressions"). The old gate failed on any critical row or more
-- than 10 'major' rows, but analytics.data_sanity_check held ~18,000 major
-- rows the day it was checked, so .github/workflows/pipeline-sanity.yml had
-- never passed once since it was added (2026-09-09). Now `scrooner-sanity
-- report --fail-on-findings` compares current severity counts against the
-- most recent baseline and fails only when they get worse; a passing run
-- records a new baseline, so it ratchets down as the backlog is fixed and a
-- failing run can never promote its own regression to the new normal.
create table if not exists analytics.data_sanity_gate_baseline (
    recorded_at timestamptz not null default now(),
    metric_name text not null,
    severity text not null,
    count integer not null,
    primary key (recorded_at, metric_name, severity)
);
