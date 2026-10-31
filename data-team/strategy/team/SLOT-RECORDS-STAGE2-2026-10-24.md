# Slot-record builder stage 2: 16-cell replay + AAPL/MSFT format stability (scrooner-25, 2026-10-24)

Branch `work/scrooner-25/slot-records`. Read-only (no migration, no DB writes); records are JSONL proposals under `pipeline/scripts/slot_records/results/`. SEC: ~320 requests this stage (one wasted pass on a mkdir bug, rerun; then 11 MetaLinks + 5 xsd), shared limiter ≤4 req/s, one process, `SEC_USER_AGENT`; all downloads deleted after use. Labels: compositions FILING-CHECKED (parsed from the filings' own linkbases); value replay DATA-INFERRED (stored facts; no R-file opened).

## Format stability (the founder's premise, now measured on 3 companies)

| Company | 10-K/10-Q since 2015 | Slot records (eras) | Format changes and what each was |
|---|---|---|---|
| MU | 48 | 3 | ASC 842 on (2019), op-lease line off face (2026 10-K) |
| AAPL | 47 | 4 | 2015 current/noncurrent LTD split; 2020 Q2–Q3 `OtherShortTermBorrowings` on face (pilot cells 1–2, caught automatically as a 2-filing era); reverts 2020 10-K |
| MSFT | 47 | 7 | one-quarter blip 2016-09-30 (no current LTD); ASC 842 (2017); ST borrowings off face (2018); commercial paper on (2023) and off (2025) |

Every detected change is a real accounting/presentation event. ~142 filings → 14 era records. The format gate is cheap and the eras are long.

## 16-cell replay (vs the pilot's filing-checked values)

Debt cells (1–13): **12 of 13 fully reproduced** — slot composition from the filing's own cal + stored API values equal the pilot's filing numbers exactly: AAPL 2020 Q2/Q3 (109,507M / 112,723M incl. `OtherShortTermBorrowings`), GOOG 2023 (13,253M = LTD 11,870 + noncurrent finance leases, composed from the debt-note slot), NVDA FY2015 (1,384,342K + 14,086K), MU 2021 (6,776M), ABBV 2022/2017 (12M / 400M ST borrowings), CVX 2015/2014 (65M / 84M cap leases), GOOG 2015–2016 ×3 (current debt + 238/223/220M cap-lease split). The remaining debt cell, **TSLA 2018-09-30: composition now fully detected including the custom tag** `tsla:ConvertibleSeniorNotesIssueToRelatedPartiesNonCurrent` (the widened Convertible regex), but its VALUE is absent from stored facts (custom tags never reach the companyfacts API) — needs one instance read, exactly as the pilot predicted. Cells 14 (revenue total: both routes already right) and 15–16 (EPS split basis: Period Engineer's root fix #2, built on its branch) are out of this family's scope by design.

Score vs the pilot's own hybrid: pilot fixed 13/16; this engine reproduces those 13 programmatically (12 values + TSLA pending one filing read) and does it from era records instead of per-cell hand analysis.

## New findings (durable, engine-relevant)

1. **Modern filings can ship NO separate `_cal.xml`** (MSFT 2024+, Donnelley agent): the `-xbrl.zip` contains no XML at all, MetaLinks.json carries calc for note roles but NOT the balance sheet in 3 of 5 checked filings, and the calculation linkbase is **embedded in the schema (.xsd)**. Loader fallback implemented: `_cal.xml` → embedded-in-xsd → MetaLinks.json. FSN bulk `cal.tsv` remains the systematic production path (V2 design holds).
2. **Two structural extractor rules** found on real filings: debt lines can hang directly under `LiabilitiesAndStockholdersEquity` (NVDA FY2015, GOOG 2015 — no `Liabilities` calc node), and `LiabilitiesOtherThanLongtermDebtNoncurrent` is a non-debt remainder line that lexically matches "Debt" (ABBV 2017) — both now handled with an explicit exclusion list.
3. **Authoritative-flag gaps the slot replay surfaced**: NVDA FY2015 `LongTermDebt` — the exact original (1,384,342K) and every copy are `is_authoritative=false` (no authoritative row at that instant); GOOG 2023 `LongTermDebtAndCapitalLeaseObligations` 13,253M exists only as non-authoritative copies (composable from authoritative members). Both go to triage: the hard is_authoritative filter would blank cells the filer actually reported.

## Ship path (unchanged)

Verifier R-file sample of the era records (queued by Dhairya) → `analytics.company_slot_record` migration (0110+, claim in doc 53 ledger at build time) → certification I12 → `resolve.py` reads verified records. Nothing in this stage changed any displayed value.
