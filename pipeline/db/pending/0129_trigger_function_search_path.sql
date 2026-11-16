-- 0129: fixed search_path on the 8 trigger functions flagged by the Supabase advisor "function_search_path_mutable".
-- Every body was read (pg_proc.prosrc, 2026-11-16): all relations are schema-qualified (analytics.* / core.*); the only
-- unqualified names are pg_catalog built-ins (current_setting, to_jsonb, coalesce) and NEW/OLD, so
-- search_path = pg_catalog, <function's own schema> resolves everything the bodies reference. Metadata-only, no data change.
-- NOT applied: needs the founder's typed words (FOUNDER-QUEUE.md).
alter function analytics.check_first_match_priority_unique() set search_path = pg_catalog, analytics;
alter function analytics.cell_evidence_append_only() set search_path = pg_catalog, analytics;
alter function core.company_identity_audit_guard() set search_path = pg_catalog, core;
alter function analytics.slot_protected_cell_guard() set search_path = pg_catalog, analytics;
alter function analytics.company_value_owner_guard() set search_path = pg_catalog, analytics;
alter function core.company_history_source_no_overlap() set search_path = pg_catalog, core;
alter function analytics.company_tag_map_no_overlap() set search_path = pg_catalog, analytics;
alter function analytics.verifier_check_writer_guard() set search_path = pg_catalog, analytics;
