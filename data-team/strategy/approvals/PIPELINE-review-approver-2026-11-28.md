# Approver review of PIPELINE.md sections 2-4 (stage 5 Certify; steps M3, M4, M5)

Reviewer: Ritwik (cloud), approver, session_01GLmSDz8UUfjBrVex2j8ugb, 2026-11-28. Reviewed `data-team/PIPELINE.md` at 07cf6bfc5.
This is a review, not a decision. Each item names the stage, the merge step, the problem, the evidence and a proposed change.

## Must fix before M3 or M4 is built

1. **Stage 5 and orchestration conflict: approver is not the preparer** (section 3 Workers; M4). "Each worker takes one company at a time and runs stages 1-6 in order" makes the worker run Certify on its own output. Proposed change: a worker may run the judge read-only and file a request (today: `requests/<T>-request-<date>.md`, then `display-certify.yml` publishes to `certify-out/run-<id>`, never main). The verdict, the registry row and the certificate are recorded only by the approver. Loading `analytics.display_cell_certificate` stays a production write that needs the founder's typed words in the applying session. State this in the stage 5 row and in section 3.
2. **Stage 5 guarantee is incomplete** (section 2; M3). The row lists only the 199-cell sample. The FAILs that caught real defects were census checks over every cell, not the sample. 0 errors were found in 995 drawn cells across the five PASS companies, while these census checks failed companies:
   - badge mislabels: JNJ cf_ap_change (11 cells); BMY gross_profit FY2015-20 and opex FY2017-18 (8 cells, rule 2b78da15);
   - unbadged shown cells (WMT, 17 cells);
   - per-share plausibility (STX DPS);
   - hidden-row and hidden-year evidence;
   - total_debt and derived identities.

   Proposed guarantee: "every census check passes (gate, badge, debt, derived, per-share, hidden rows and years, identity web) AND the 199-cell sample has 0 errors at a ≤1.5% 95% upper bound; pooled Clopper-Pearson bound over the latest PASS row per company reported against the 0.10% target." Section 6 should carry the pooled bound too.
3. **Stage 5 idempotency key** (section 2; M3). "company + certificate id" is not reproducible. Today a verdict is keyed by the coverage sha256: seed = TICKER + the first 12 hex digits of the sha, and reads are `reads/<T>-<sha12>.csv`. Proposed key: `ticker`, `coverage_sha256` and the judge version (`code_sha` and `draw_check@N` in the certificate JSON). A re-draw happens only on a new coverage sha, never with a new seed on the same coverage. Every verdict, FAILs included, stays in `registry-history.csv`.
4. **Stage 4 guarantee should include the badge and parts contract** (section 2; M3). Proposed rules:
   - the badge states how the value was obtained (data_points.csv);
   - a `derived:` cell carries its parts, each `TAG=value@accession#R`, all from one filing;
   - a value badged as printed never has a formula locator.

   BMY opex FY2017-18 (coverage 2a1319707e95) are badged derived with no parts, so the census can't rebuild FY2018 and the company sits in REVIEW. The "one vintage" rule (X87) also belongs in Prove: inputs to an identity come from one filing. LLY gross profit FY2023-24 mixes the FY2025 10-K's rounded revenue reprint with the own-10-K precise prints.
5. **Orchestration connection rule is stale** (section 3 Backpressure and Workers; M4). "At most 4 shards (repo rule)" and "MAX_BACKENDS 60" contradict the founder decision of 2026-11-13 as recorded in doc 02 and root CLAUDE.md: up to 70 connections, company-disjoint shards, no fixed shard cap, pause while `pg_stat_activity` exceeds 80. Cite doc 02 instead of restating numbers.

## Should fix

6. **Exceptions queue is missing the approver's item** (section 4; M5). Add a row:

   | Exception | Source | Owner | Closes when |
   |---|---|---|---|
   | NEEDS_READ / REVIEW (a drawn or census cell the checker could not settle) | stage 5 | approver | a read is committed (`reads/<T>-<sha12>.csv`), or the export is fixed |

   A read class that recurs becomes a draw_check rule. Measured candidates:
   - BMY needed 9 reads across two coverages for one pattern: accounts_receivable as the undimensioned `AccountsReceivableNetCurrent` note fact of the cited filing, where the face line also holds other receivables. draw_check could match an undimensioned fact of the cited filing at the period end with its tag in the data point's family, without requiring the fact to be presented.
   - MA needed reads twice for cash_paid_for_interest tagged `InterestExpenseDebt`.
7. **"Sample FAIL ... the company is re-drawn"** (section 4). It should say "re-drawn on a new coverage sha after the fix" (item 3). Most FAILs here were census FAILs, so add a "census FAIL" row: source stage 5, owner the stage 4 lane (badge or parts) or stage 3 (value), closes with a rule plus a test, as with 2b78da15.
8. **"A certified company that changes is held"** (section 2) is undefined. Proposed text: a served-cell change (new coverage sha) moves the company to *re-cert required*. Say what users see meanwhile. Under the 2026-11-04 decision there is no old-table fallback, so either the last certified cells stay served until re-cert, or the changed cells are OPEN. That choice is the founder's.
9. **Data contract, derived rows** (section 2). "Every row carries cik, accession_number" should say a multi-part cell carries one accession per part, and that all parts' accessions are equal (one filing per derivation, doc 02).

## Elsewhere, for the owner

- SYSTEMS.md section 14 says "2 of 100 certified (GILD, JNJ); BA, MA, MO, STX, WMT failed". The registry on main has GILD, JNJ, LRCX, MA and MO PASS, and BA, BMY, STX and WMT FAIL. Read `registry.csv` rather than restating counts.
- `registry.csv` gained a carriage return inside fields from a CRLF writer mixed with LF appends. It was fixed in cbdef305, and `registry_problems` now reports it. Any stage 5 writer in M3 should reuse `display_cert.record_verdict`.
