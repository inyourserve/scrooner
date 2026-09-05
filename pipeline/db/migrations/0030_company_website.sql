-- Company website (2026-08-31), doc 39's business_text.py extension.
-- Sourced from each 10-K's mandatory "Available Information" section
-- (Item 101(e)) -- checked live before building: submissions.json's own
-- `website`/`investorWebsite` fields exist in SEC's schema but are
-- empty for every company checked, even Apple/Microsoft/Costco. The
-- real, populated source is the filing's own prose text, not a
-- structured field -- same fetch as employee headcount/About text
-- (zero additional SEC calls, same already-fetched 10-K document).

alter table core.company add column if not exists website text;
