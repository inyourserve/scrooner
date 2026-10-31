-- Provenance of every VALUED cell (data-team/46-canonical-fact-v2/CELL-FORMAT-v1.md, design line 2, approved by
-- scrooner-0f 2026-10-31): which rule run and which family wrote a canonical_fact row. Filed cells already trace to
-- their filing through source_fact_ids -> core.fact; the producing rule did not. Nullable: rows written before the
-- cell loader keep null. Additive only; nothing else changes. Apply needs the founder's words (Ritwik's session).
alter table analytics.canonical_fact
    add column if not exists rule_run_id uuid references analytics.rule_run (run_id),
    add column if not exists family text;
create index if not exists idx_canonical_fact_family_company
    on analytics.canonical_fact (family, company_id);
