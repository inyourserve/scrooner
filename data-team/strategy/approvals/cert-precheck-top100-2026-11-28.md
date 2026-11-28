# Certification precheck of near-gate top-100 companies, 2026-11-28 (Data Verifier, preparer)

Status: PARTIAL (no company certifiable; all four fail the census gate; every 199-cell draw clean).

## Rank check (origin/main doc/data-moat/team/top1000/shards.csv)
- AKTX (9), TBLA (11), RPAY (33): excluded, wrong mcap (ADS ratio / filer shares 1000x). Not top-100. Dropped.
- SPCX (18): SpaceX, "keep: mcap understated (~$1.92T)", real top-100 but TEMPLATE_UNAVAILABLE, 0 cells (no docmap). open_shown 0 is vacuous; not certifiable until a docmap exists.
- BA 84, CRWD 51, PFE 75 real. PM 38 also has open_shown 1 (added).

## Requests / queue
- requests/ on origin/main: only BA-request-2026-11-15 (sha d0d3a6f1..., registry FAIL n=32). None for CRWD, PFE, PM. Stale for BA.
- gh run list top100-flow: 46174337050 QUEUED (proof refresh 2026-11-28); top100-auto-trigger 46174840428 in progress. Queue not empty: no dispatch.
- A flow run now would not yield a request anyway: each company fails the gate below.

## Commands
- gh run download 46167654745 (top100-coverage hourly artifact, as_of 2026-11-28T16:55Z); split per company.
- certify_display.py (origin/main f0f7ffbd9, extracted to scratch) --ticker T --cik C --coverage <split> --live --no-registry [--reads] ; pg_stat_activity 24 conns before.
- sec.gov: 9 primary 10-K docs + PM FY2024 R3 + PFE FY2023 R3, 2.1 s apart, declared UA.

## Results (n=199 each, 0 wrong, CP95 upper bound 1.49%)
| T | coverage sha256 | auto-matched | reads | census FAILs |
|---|---|---|---|---|
| BA | 73ef96e1cff9... | 192 | 7 MATCH | 2 pageless DPS FY2020/21 |
| CRWD | 4f3ea5752152... | 196 | 3 MATCH | OPEN interest_income FY2020; hidden_year interest_income FY2018/19 |
| PFE | d50118dc25cf... | 199 | 0 | OPEN revenue FY2021; badge gross_profit FY2017/21/22/23 |
| PM | d1139a42ea3a... | 197 | 2 MATCH | OPEN other_income_expense_net FY2016; badge OIE FY2015 |

## Files (untracked in the shared tree; not committed)
- data-team/strategy/approvals/{BA,CRWD,PFE,PM}-precheck-2026-11-28.md (+ -evidence.csv)
- data-team/strategy/approvals/reads/{BA-73ef96e1cff9,CRWD-4f3ea5752152,PM-d1139a42ea3a}.csv
- data-team/strategy/certification/{BA,CRWD,PFE,PM}-coverage-2026-11-28.csv

## Untested
- 5% AUTO_MATCH audit (--audit-out); census FAILs not re-read beyond PFE revenue 2021 (R3 confirmed) and the cited open-shown-fixes quotes.
