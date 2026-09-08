-- Reorder analytics.statement_line's display_order for balance_sheet and
-- cash_flow (2026-09-08, direct user report: "please verify the row of
-- all financial table -- are rows name correct? flow is correct?").
--
-- Row NAMES were already correct -- the real problem was FLOW: Cash and
-- Equivalents sat between two subtotals (Current Assets, itself
-- INCLUDING cash) making the table look additive when it isn't. Verified
-- live against AAPL FY2025: Cash ($35.9B) + Current Assets ($148.0B) +
-- PPE ($49.8B) = $233.7B, nowhere near real Total Assets ($359.2B) --
-- summing the visible rows the way they were ordered doesn't reproduce
-- the total, and there's a real, un-labeled $161.4B (45%) of Total
-- Assets with no row at all (goodwill/investments/other non-current
-- assets -- AAPL itself hasn't tagged Goodwill as its own XBRL line
-- since FY2018, confirmed live; a real filing-convention fact, not a
-- Scrooner gap). Same shape on the liabilities side: Total Debt sat
-- between Current Liabilities and Total Liabilities, again implying
-- additivity it doesn't have (debt spans both current and non-current).
--
-- Fix: group the two real GAAP subtotals/total together first (Current
-- Assets -> PPE -> Total Assets), then the cross-cutting "memo" line
-- (Cash and Equivalents -- a real component of Current Assets, not
-- additive with it) directly after, clearly separated from the additive
-- chain. Same treatment for Total Debt after Total Liabilities.
--
-- cash_flow gets the identical treatment: the three real GAAP section
-- totals (Operating, Investing, Financing) grouped together first, then
-- the "memo" detail lines (Capital Expenditures -- a component of
-- Investing; Dividends Paid/Share Buybacks -- components of Financing)
-- after, clearly separated rather than interleaved mid-total as before.
--
-- Two-step update (not one) to avoid transiently violating
-- statement_line_statement_display_order_key (statement, display_order)
-- UNIQUE -- Postgres checks a UNIQUE btree constraint per row as an
-- UPDATE executes, not deferred until statement end, so swapping values
-- directly in one pass can collide mid-statement even though the final
-- state has no duplicates.

update analytics.statement_line set display_order = display_order + 100
where statement in ('balance_sheet', 'cash_flow');

update analytics.statement_line set display_order = case display_label
    when 'Current Assets' then 1
    when 'Property, Plant & Equipment' then 2
    when 'Total Assets' then 3
    when 'Cash and Equivalents' then 4
    when 'Current Liabilities' then 5
    when 'Total Liabilities' then 6
    when 'Total Debt' then 7
    when 'Stockholders'' Equity' then 8
end
where statement = 'balance_sheet';

update analytics.statement_line set display_order = case display_label
    when 'Cash from Operations' then 1
    when 'Cash from Investing' then 2
    when 'Cash from Financing' then 3
    when 'Capital Expenditures' then 4
    when 'Dividends Paid' then 5
    when 'Share Buybacks' then 6
end
where statement = 'cash_flow';
