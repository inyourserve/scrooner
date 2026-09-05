-- Institutional ownership name-based fallback matching (2026-09-05).
--
-- Found live: 1,461 of 5,216 active companies have never had a Schedule
-- 13D/13G filed against them, so ownership/institutional.py's CUSIP
-- crosswalk (sourced from core.beneficial_ownership.cusip) never learns
-- their CUSIP and can never match their real Form 13F holdings, even
-- though those holdings exist in the bulk data under the company's true
-- CUSIP. Piloted a name-based fallback: Form 13F's own INFOTABLE.tsv
-- carries NAMEOFISSUER, previously read but discarded. A normalized
-- exact-match (uppercase, strip legal-entity suffixes/punctuation)
-- against core.company.company_name, restricted to companies not already
-- covered by CUSIP and only when the normalized name is unambiguous
-- (maps to exactly one company) produced zero collisions across all
-- 1,461 uncovered companies and matched 814 of them from a single bulk
-- window alone -- see doc/learnings/2026-09-05-institutional-ownership-name-fallback.md.
--
-- match_method traces which mechanism resolved each row -- CUSIP is a
-- hard identifier scoped to exactly the subject security; a name match,
-- even unambiguous within our own universe, carries a small residual
-- risk of coinciding with an unrelated real-world issuer that also uses
-- that exact name. Traceability, not a correctness downgrade: every
-- existing row is backfilled 'cusip' (the only mechanism that existed
-- before this column), matching this project's "flag, don't hide"
-- discipline (is_amendment, aff10b5One, etc.).
alter table core.institutional_ownership add column if not exists match_method text not null default 'cusip';
alter table core.institutional_ownership add constraint institutional_ownership_match_method_check
    check (match_method in ('cusip', 'name'));
