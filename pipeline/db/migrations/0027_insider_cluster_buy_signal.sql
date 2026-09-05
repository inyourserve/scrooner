-- Insider cluster-buy signal (doc/audit/2026-08-29_ownership_insider_data_audit.md's
-- #3 "missing" finding: "multiple insiders buying in the same short window
-- is one of the most reliable documented insider signals, stronger than
-- any single transaction"). Deferred at the time the audit was written
-- because ownership/insider_summary.py's full-population run was still
-- in progress; that run is now complete (4,305/4,305 companies), so this
-- is a follow-up pass over already-fully-collected core.insider_transaction
-- data -- no new SEC fetch.
--
-- Purely additive columns on the existing one-row-per-company summary
-- table, not a new table: this is one more fact about the same company,
-- not a new entity with its own cardinality.
--
-- cluster_buy_max_insiders: the largest number of DISTINCT reporting
-- owners who each placed at least one open-market buy (transaction_code
-- 'P') with a transaction_date inside some single rolling 7-day window,
-- over the trailing 12 months. A value of 0 or 1 means no real cluster
-- signal (routine, independent insider activity); >=2 is the signal this
-- column exists to surface. NULL only when a company has zero Form 4 buy
-- transactions in the window at all (an honest "not applicable", not "0"
-- -- 0 would incorrectly imply "we checked and found no cluster" for a
-- company where clustering isn't even a meaningful question).
alter table core.insider_ownership_summary
    add column if not exists cluster_buy_max_insiders int,
    add column if not exists cluster_buy_window_start  date,
    add column if not exists cluster_buy_window_end    date;
