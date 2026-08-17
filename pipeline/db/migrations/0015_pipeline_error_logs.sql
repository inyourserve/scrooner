-- Per-company dead-letter logging for the Normalizer and Mapper (Phase 1
-- scaling foundation, see doc/learnings/ once written). Mirrors
-- raw.collector_errors's shape -- each layer's error log lives in the
-- schema that layer already owns (Normalizer -> core, Mapper -> analytics),
-- consistent with doc 04's boundary table rather than a new shared schema.
--
-- No run-lifecycle table yet (no collector_runs equivalent) -- Normalizer/
-- Mapper runs are short enough today that resume-after-crash isn't a
-- demonstrated need (doc 05 "evidence before expansion"). Add one later if
-- a wide run actually needs it.

create table if not exists core.normalizer_error (
    id          bigint generated always as identity primary key,
    cik         text not null,
    stage       text not null,
    error_type  text not null,
    message     text not null,
    occurred_at timestamptz not null default now(),
    resolved    boolean not null default false
);

create index if not exists normalizer_error_cik_idx on core.normalizer_error (cik);
create index if not exists normalizer_error_unresolved_idx on core.normalizer_error (occurred_at) where not resolved;

create table if not exists analytics.mapper_error (
    id          bigint generated always as identity primary key,
    cik         text not null,
    stage       text not null,
    error_type  text not null,
    message     text not null,
    occurred_at timestamptz not null default now(),
    resolved    boolean not null default false
);

create index if not exists mapper_error_cik_idx on analytics.mapper_error (cik);
create index if not exists mapper_error_unresolved_idx on analytics.mapper_error (occurred_at) where not resolved;
