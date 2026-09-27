-- Widens analytics.concept_parser_attempt's outcome CHECK constraint for
-- cost_of_revenue_parser.py (2026-09-21): a yfinance-VALIDATING parser
-- (unlike revenue_parser.py, which needs no external check) has a real
-- fifth outcome -- a parsed sum that does not reconcile against
-- yfinance's own already-fetched figure within tolerance, discarded
-- rather than stored. ('no_yfinance_target', the sixth conceivable
-- outcome, is deliberately never recorded at all -- see cost_of_revenue_
-- parser.py's run() docstring -- so it does not need a place here.)
alter table analytics.concept_parser_attempt drop constraint if exists concept_parser_attempt_outcome_check;
alter table analytics.concept_parser_attempt
    add constraint concept_parser_attempt_outcome_check
    check (outcome in ('matched', 'no_report', 'no_row_matched', 'no_yfinance_match', 'errored'));
