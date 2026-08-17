-- Statement schema (doc 17, Part 8 prep -- the company page's financial
-- statement tables). Extends `analytics` additively -- doc 11's 17
-- canonical concepts and their concept_mapping rows are NOT touched, only
-- new rows added for statement-display-only concepts (cost_of_revenue,
-- operating_expenses, total_assets, etc.) that the 18 locked ratio
-- metrics never needed. Mapper's own frozen resolve()/calculate() logic
-- is reused unchanged -- this is new DATA on the same schema, not new
-- resolution code.

-- Which canonical_concept goes on which statement, in what display order,
-- under what human-readable label. One row per statement line; the value
-- itself is resolved from analytics.canonical_fact (already-verified,
-- taxonomy-drift-safe) via the concept it references -- no new value-
-- resolution logic, just a presentation-order lookup table.
create table if not exists analytics.statement_line (
    id                  bigint generated always as identity primary key,
    statement           text not null check (statement in ('income_statement', 'balance_sheet', 'cash_flow')),
    display_order       int not null,
    display_label       text not null,
    canonical_concept_id bigint not null references analytics.canonical_concept (id),
    unique (statement, display_order)
);
