# Strategy log (Head of Data Product)

Decisions, evidence and corrections, newest first.

- 2026-10-21 (Ritwik): Strategy v1 written (37-STRATEGY-BEST-SCREENER-2026-10-21.md). Core call: trust before breadth; certification state is the visible differentiator. Benchmark evidence is thin (no independent competitor accuracy tests found). Headline 80.86% fill is overstated (coverage_matrix.py:746). Not yet measured fresh: DB skipped, pooler busy.

## 2026-10-21 (Head of Data Product) - strategy doc 37 recommendations
Source: `data-team/strategy/37-STRATEGY-BEST-SCREENER-2026-10-21.md`. All are RECOMMENDATIONS; founder decides.
- D1 Position as "the screener whose numbers you can verify" (certification + per-number evidence, top 1,000), first job compounders/quality, insider/ownership as free differentiator. Evidence: no retail product page read advertises per-number provenance (not a trial; unverified); J1/J2/J5 blocked by total_debt and operating income wrong values (FILING-CHECKED, VERIFY-W1).
- D2 Data window 2015-01-01 to date (about 11.8y). Logged-out 7 FY + 8Q; logged-in full window; retire "15 years". 10y CAGR only when all 11 annuals certified. Evidence: competitors' 10y paid tier is parity (Koyfin, TIKR, SA; VENDOR-CLAIM).
- D3 Freeze new metrics/sectors/sources until 300 certified; name a human accounting reviewer; show a number only if it passes I1-I11, else a reasoned blank.
- Gates: certified 10/300/700 at day 30/60/90; wrong per 1,000 cells baseline at day 30 then <=2.0 then <=0.5; history present >=99% and 100% classified; latency p50<=24h p95<=72h.
- Kill: coverage-% as headline, "latest filed wins" without filing validation, the 15-year tier, new feeds before 300 certified.
- Caveat to revisit: DB counts not refreshed (17 connections). Re-baseline when connections <= 14. What would be wrong if: F2 panel usage < 5% of sessions after 60 days.
- 2026-10-21 (Ritwik): Founder clarified the problem = tag non-uniformity across companies (coverage + quality). Wrote doc 38: map by filing structure (pre/cal + identities) as second path beside name lookup. PoC on FSDS 2025q4 only; not a certified result.
