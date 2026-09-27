-- Multi-tag support for analytics.company_tag_preference (2026-09-21).
--
-- sanity/tag_investigator.py's original design (migration 0051) only ever
-- covers a "resolve() picked the wrong ALREADY-MAPPED tag" bug -- one
-- company, one replacement tag. It has no way to represent a company that
-- has NO facts under any currently-mapped tag at all, because the real
-- rolled-up concept doesn't exist as a single XBRL tag for that filer --
-- Hyatt Hotels' Operating Expenses is a SUM of several tags it reports
-- separately (DirectCostsOfOwnedHotels, GeneralAndAdministrativeExpense,
-- etc.), not one substitute tag. Found live 2026-09-21 investigating a
-- direct user report of blank Hyatt quarterly-results rows; sized at
-- ~570-572 companies across dozens of unrelated sectors for cost_of_revenue
-- /gross_profit, ~306 for operating_expenses.
--
-- `tags` is the new source of truth: a JSON array of {"taxonomy", "tag"}
-- objects, summed together per period once every listed tag has a real,
-- reconciled value for that period (see mapper/tag_discovery.py). The
-- legacy `taxonomy`/`tag` columns are kept and kept in sync (mirroring
-- `tags[0]`) purely for backward-compat display of existing single-tag
-- rows written before this migration -- no code path reads them for
-- resolution logic after this change.
alter table analytics.company_tag_preference
    add column if not exists tags jsonb not null default '[]'::jsonb;

update analytics.company_tag_preference
set tags = jsonb_build_array(jsonb_build_object('taxonomy', taxonomy, 'tag', tag))
where tags = '[]'::jsonb;
