# Apply day running table (2026-10-31, UTC) — certify dry run + reason counts per applied package

Owner: scrooner-8a (engineering). Method: after each package Ritwik applies, `scrooner-certify --dry-run` on the touched CIKs
(one read-only connection, chunks of 50, retried on dropped SSL) and a run-scoped reason/blank count. "Before" for the
certify columns = pre-apply chunked baseline (started 16:05 UTC; chunk 000 lost to a dropped connection during the OI apply
at 16:06-16:07, so the OI row has no pre-apply certify measurement). Reason counts are exact before/after because
`cell_blank_reason` and `canonical_fact_retired` are keyed by run_id: before = everything except the package's run.

Expected-cell universe for reason counts: (company, FY/Q period since 2015-01-01) where revenue or net income has a value.

| package | rule_run | companies | cells written | reasonless blanks before → after | wrong_value findings before → after | new regressions | status |
|---|---|---|---|---|---|---|---|
| OI blank reasons (`slot.is_operating_income_not_presented@1`) | 4d7b48ee | 253 | 13,942 reasons (9,412 inside the universe), 3,313 values archived (2,363 inside) | 9,686 → 2,637 (OI cells; 1,632 still valued) | not measured pre-apply → (running) | (running) | certify after-run in progress |

Scratch outputs: scratchpad/certify/chunks/<run>/NNN.json, logs scratchpad/certify/<run>.log (this Mac; copied here when a row closes).
