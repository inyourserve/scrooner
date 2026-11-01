# Verify: shared-accession post-apply audit (live DB after scrooner-31's chain, finished 2026-10-31 06:45 UTC), 2026-11-03

Live analytics.canonical_fact (read-only, one connection) vs each parent's FY2025 10-K face. Evidence class: FILING-CHECKED (10-K R pages) plus a live DB read. Verifier 2 (scrooner-bc).

## Result
**NO.**
1. **Subsidiaries still show the parent's numbers.** Live total_assets rows, rewritten 2026-10-31:
   - SoCalGas 115,281M at 2026-06-30 (Sempra's consolidated);
   - Consumers 41,683M at 2026-09-30 (CMS's);
   - SCE 96,171M (Edison International's);
   - Entergy Arkansas 79,002,618K (Entergy Corp's).
   The `*_resolved` copies from 2026-09-08 are unchanged. The facts on the combined filings were not dropped from the subsidiaries.
2. **Parents mostly right.** 16 of 20 cells equal the 10-K face. Exceptions:
   - ETR and ES net income are the consolidated lines (incl. NCI/subsidiary preferred), not the parent-attributable lines: ETR 1,773,328K vs attributable 1,758,272K; ES 1,699,891K vs 1,692,372K.
   - SRE revenue 12,418M vs face "Total revenues" 13,702M.
   - SRE CFO 4,565M not readable on the face here.

| Parent | Revenue (live / face) | Net income (live / face) | Total assets 2025-12-31 (live / face) | CFO (live / face) |
|---|---|---|---|---|
| ETR | 12,946,686K / 12,946,686K | 1,773,328K / consolidated 1,773,328K, attributable 1,758,272K | 71,890,730K / 71,890,730K (Entergy Corp block) | 5,150,651K / same |
| SO | 29,553M / 29,553M | 4,341M / attributable 4,341M | 155,720M / 155,720M | 9,802M / 9,802M |
| ES | 13,547,244K / same | 1,699,891K / consolidated 1,699,891K, to common 1,692,372K | 63,786,711K / same | 4,113,572K / same |
| SRE | **12,418M / 13,702M** | 1,837M / earnings attributable to Sempra 1,837M (2,072 - 238 + 3) | 110,878M / same | 4,565M / not read |
| CTVA | 17,401M / Net Sales 17,401M | 1,094M / attributable 1,094M | 42,845M / same | 3,406M / total 3,406M |

## Findings
1. The shared-accession apply moved the filings to the parents, but the subsidiaries' `core.fact` rows from the four carrier filings still resolve. Re-normalize the four subsidiaries (1080, 142, 1079, 1165), or delete their facts on those accessions, then re-run resolve and calculate.
2. ETR/ES net income (consolidated vs attributable) and SRE revenue (a component tag vs total revenues) are concept-mapping issues for the parents, not caused by the move. Route them to the income-statement slot records.
3. `*_resolved` values for these companies wait for the nightly (statement fallbacks and conflict fills not run per company).

SEC requests: 32. DB: one read-only connection.
