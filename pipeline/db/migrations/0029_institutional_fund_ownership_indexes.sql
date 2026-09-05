-- Found live 2026-08-31: institutional.py's/mutual_fund.py's own
-- delete-then-reinsert write pattern (`delete ... where company_id =
-- any($1) [and source_zip = $2]`) has no supporting index on either
-- table -- fine at golden-10 scale (a few hundred rows), but at the
-- real full-population scale these tables reached this same day
-- (2.35M / 1.9M rows, once the CUSIP crosswalk stopped being golden-10-
-- only), the delete has to sequentially scan the whole table and hit
-- Supabase's statement timeout before the batched-insert fix (same day,
-- same finding) ever got a chance to run.

create index if not exists idx_institutional_ownership_company_source
    on core.institutional_ownership (company_id, source_zip);

create index if not exists idx_fund_ownership_company
    on core.fund_ownership (company_id);
