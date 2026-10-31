# Slot-record builder v0: MU total debt (scrooner-25, 2026-10-24)

Read-only build on branch `work/scrooner-25/slot-records` (off `work/data-engineer/as-filed-pilot` 2487435). No migration, no DB writes; records are JSONL PROPOSALS (`pipeline/scripts/slot_records/results/mu_debt_slots.jsonl`). Code: `pipeline/scripts/slot_records/build_debt_slots.py` (stdlib, run with `python3 -I`). SEC access: 48 filings × 2 requests (index + `_cal.xml`), shared limiter ≤4 req/s, one process, `SEC_USER_AGENT` from pipeline/.env; all downloads (4.9 MB) deleted after use.

## What was built

For every MU 10-K/10-Q since 2015 (48 filings, incl. the newest 10-K 0000723125-26-000023), parse the filing's own calculation linkbase and extract the debt-family children of the filer's `LiabilitiesCurrent`/`Liabilities(Noncurrent)` — the founder's company-wise mapper, for one family, one company. Records are era-keyed (taxonomy version from the cal file, per Dhairya's instruction) and fingerprinted (sha256 of the ordered debt arcs) for the format-change gate.

## Result 1: format stability (FILING-CHECKED — the cal files ARE the filings)

48 filings collapse into **3 slot records**:

| Taxonomy era | Periods | Filings | Face debt composition |
|---|---|---|---|
| 2014–2019 | 2014-12-04..2019-08-29 | 20 | `DebtCurrent` + `LongTermDebtAndCapitalLeaseObligations` |
| 2019–2025 | 2019-11-28..2026-05-28 | 27 | same + `OperatingLeaseLiabilityNoncurrent` appears (ASC 842 — a known break class) |
| 2026 | 2026-09-03 | 1 | operating-lease line off the face again |

The founder's premise ("mostly the same format every time; gate on change") is measured fact for MU: one format change in 12 years, and it is exactly the ASC 842 adoption the gate was designed to catch.

## Result 2: value replay, 53/53 EXACT (DATA-INFERRED: stored facts vs the filer's own stored aggregate; anchors FILING-CHECKED by Dhairya)

At every balance-sheet instant where MU filed facts (53 instants, 2012-08-30..2026-09-03, comparatives included): `DebtCurrent + LongTermDebtAndCapitalLeaseObligations` equals the filer's own `DebtAndCapitalLeaseObligations` **to the dollar, with zero exceptions**. Both regression anchors pass: 2021-09-02 = 6,776M; 2025-08-28 = 14,577M lease-inclusive / 11,533M (`LongTermDebt`) borrowings-only.

## Result 3: what production shows today (the baseline this must beat)

| Instant | prod `total_debt` | prod `total_debt_resolved` | Filer's own total | Verdict on prod |
|---|---|---|---|---|
| 2015-09-03 | 1,089M | 7,341M | 7,341M | resolved OK (lease-inclusive); raw = `DebtCurrent` alone |
| 2019-08-29 | 1,310M | 5,851M | 5,851M | resolved OK (lease-inclusive) |
| 2021-09-02 | 6,123M | 5,968M | 6,776M | **both wrong**: 5,968 = `LongTermDebt` only (misses current debt + finance leases); 6,123 misses finance leases |
| 2025-08-28 | 12,093M | 11,533M | 14,577M / 11,533M | resolved = borrowings-only |
| 2026-09-03 | 3,283M | 2,792M | 5,179M / 2,792M | resolved = borrowings-only |

The deeper defect is not any single value: **production's `total_debt_resolved` switches perimeter across MU's own history** — lease-inclusive in 2015/2019, borrowings-only in 2021/2025/2026 (and 2021 is not even a clean borrowings-only number). A user reading MU's debt trend today compares two different definitions without knowing it. The slot approach gives one perimeter, from the filer's own composition, exact at all 53 instants — and makes BOTH perimeters (borrowings-only and lease-inclusive) available explicitly, so the perimeter becomes a product decision instead of a tag-priority accident.

## Honest limits of v0

- One company, one family. The claim is "the engine works and the approach beats production on MU"; the 16-cell pilot regression set (AAPL/TSLA/GOOG/NVDA/ABBV/CVX…) is the next replay target and needs those companies' cal files (~2 requests each).
- 53/53 is stored-vs-stored against the filer's own tagged aggregate — strong (a filer's own calc identity), but a Verifier sample opening R-files is still required before anything ships.
- The member classifier labels combined lines (`LongTermDebtAndCapitalLeaseObligations`) by first regex match; a `combined` class is needed before perimeter variants are computed from member sums rather than from the filer's aggregates.
- Nothing here changes any displayed value. Ship path: Verifier sample → wire into `analytics.company_slot_record` (migration 0110+, doc 53 ledger) → certification I12 → resolve.py reads verified records.
