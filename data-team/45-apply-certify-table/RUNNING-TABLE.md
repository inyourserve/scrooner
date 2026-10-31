# Apply day running table (2026-10-31, UTC) — certify dry run + reason counts per applied package

Owner: scrooner-8a (engineering). Method: after each package Ritwik applies, `scrooner-certify --dry-run` on the touched CIKs
(one read-only connection, chunks of 50, retried on dropped SSL) and a run-scoped reason/blank count. "Before" for the
certify columns = pre-apply chunked baseline (started 16:05 UTC; chunk 000 lost to a dropped connection during the OI apply
at 16:06-16:07, so the OI row has no pre-apply certify measurement). Reason counts are exact before/after because
`cell_blank_reason` and `canonical_fact_retired` are keyed by run_id: before = everything except the package's run.

Expected-cell universe for reason counts: (company, FY/Q period since 2015-01-01) where revenue or net income has a value.

| package | rule_run | companies | cells written | reasonless blanks before → after | wrong_value findings before → after | new regressions | status |
|---|---|---|---|---|---|---|---|
| OI blank reasons (`slot.is_operating_income_not_presented@1`) | 4d7b48ee | 253 | 13,942 reasons (9,412 inside the universe), 3,313 values archived (2,363 inside) | 9,686 → 2,637 (OI cells; 1,632 still valued) | not measured pre-apply → 9,286 after (top rules: per_share_derived_by_subtraction 3,841, share_basis_mismatch 2,096, liabilities_nci_added 854, reit_calculated_subtotal 604; none of them OI rules) | none attributable to the package (its cells are blanks, certify does not flag blanks) | closed; after-run 16:11-16:29 UTC, chunks scratchpad/certify/chunks/oi-after |

Scratch outputs: scratchpad/certify/chunks/<run>/NNN.json, logs scratchpad/certify/<run>.log (this Mac; copied here when a row closes).

## Full-cohort reference run (986 companies, 16:05-17:17 UTC, origin/main ff9a9ba..)
Pre-apply for every package except OI (its 253 companies were measured after 4d7b48ee). wrong_value 40,554 · review 199,505 · info 37,560.
Top wrong_value rules: per_share_derived_by_subtraction 16,045 · share_basis_mismatch 7,519 · liabilities_nci_added 4,440 · wrong_unit_family 3,875 · reit_calculated_subtotal 1,658 · negative_on_nonnegative_concept 1,529.
Chunks: scratchpad/certify/chunks/baseline-preapply/000-019.json (this Mac); the "before" column of the next rows (EPS, debt, capex 2a, buybacks, split) reads from here.
