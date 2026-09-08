-- SEC Frames API self-consistency check (2026-09-08, doc 45 follow-on --
-- "high impact task", explicit user direction). Genuinely different from
-- every other check built this session: yfinance/statement comparisons
-- ask "does our number agree with an INDEPENDENT third party." This asks
-- "does our number agree with SEC's OWN bulk-served copy of the SAME
-- filing" -- a re-fetch of the ground truth, not a second opinion. A
-- mismatch here is much stronger evidence of a bug in OUR OWN pipeline
-- (Collector/Normalizer/resolve()) than any yfinance disagreement can be,
-- since both sides are supposed to be reading the identical XBRL fact.
--
-- https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json
-- returns EVERY filer's value for one (tag, period) in a single call --
-- verified live before building: 1,696 companies for us-gaap:Revenues
-- CY2026Q1 in one request, 5,543 for us-gaap:Assets CY2026Q1I (instant).
-- Fetched via the EXISTING common/sec_client.py (same User-Agent, same
-- 8 req/s aggregate rate limit as every other SEC call this project
-- makes) -- this is standard SEC EDGAR access, not a new external
-- dependency or a new rate budget to manage.

create table if not exists analytics.frames_consistency_check (
    id bigint generated always as identity primary key,
    company_id bigint not null references core.company(id),
    canonical_concept_id bigint not null references analytics.canonical_concept(id),
    taxonomy text not null,
    tag text not null,
    period_start date,
    period_end date not null,
    frames_value numeric not null,
    our_value numeric,
    pct_diff numeric,
    severity text not null check (severity in ('ok', 'mismatch', 'missing_ours')),
    accession text,
    checked_at timestamptz not null default now(),
    unique (company_id, taxonomy, tag, period_end)
);

create index if not exists idx_frames_consistency_check_severity on analytics.frames_consistency_check (severity) where severity <> 'ok';
create index if not exists idx_frames_consistency_check_concept on analytics.frames_consistency_check (canonical_concept_id);
