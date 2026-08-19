-- Auditable dead-letter resolution for every pipeline layer.
--
-- `resolved` alone cannot explain who/what proved an error fixed.  These
-- fields make reconciliation reviewable while retaining the existing tables
-- and indexes.  The application resolves only explicit, locked error IDs.

alter table raw.collector_errors
    add column if not exists resolved_at timestamptz,
    add column if not exists resolution_note text;

alter table core.normalizer_error
    add column if not exists resolved_at timestamptz,
    add column if not exists resolution_note text;

alter table analytics.mapper_error
    add column if not exists resolved_at timestamptz,
    add column if not exists resolution_note text;

-- Preserve the meaning of any legacy rows that were resolved before the
-- audit fields existed.  New resolutions must use a specific evidence note.
update raw.collector_errors
set resolved_at = coalesce(resolved_at, occurred_at),
    resolution_note = coalesce(resolution_note, 'Legacy resolution predating migration 0017')
where resolved;

update core.normalizer_error
set resolved_at = coalesce(resolved_at, occurred_at),
    resolution_note = coalesce(resolution_note, 'Legacy resolution predating migration 0017')
where resolved;

update analytics.mapper_error
set resolved_at = coalesce(resolved_at, occurred_at),
    resolution_note = coalesce(resolution_note, 'Legacy resolution predating migration 0017')
where resolved;

do $$
begin
    if not exists (select 1 from pg_constraint where conname = 'collector_errors_resolution_audit_ck') then
        alter table raw.collector_errors add constraint collector_errors_resolution_audit_ck check (
            (not resolved and resolved_at is null and resolution_note is null)
            or
            (resolved and resolved_at is not null and nullif(btrim(resolution_note), '') is not null)
        );
    end if;

    if not exists (select 1 from pg_constraint where conname = 'normalizer_error_resolution_audit_ck') then
        alter table core.normalizer_error add constraint normalizer_error_resolution_audit_ck check (
            (not resolved and resolved_at is null and resolution_note is null)
            or
            (resolved and resolved_at is not null and nullif(btrim(resolution_note), '') is not null)
        );
    end if;

    if not exists (select 1 from pg_constraint where conname = 'mapper_error_resolution_audit_ck') then
        alter table analytics.mapper_error add constraint mapper_error_resolution_audit_ck check (
            (not resolved and resolved_at is null and resolution_note is null)
            or
            (resolved and resolved_at is not null and nullif(btrim(resolution_note), '') is not null)
        );
    end if;
end
$$;
