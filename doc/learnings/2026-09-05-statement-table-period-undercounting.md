# 2026-09-05 — Quarterly Results / Profit & Loss showed too few periods, because "8 period rows" isn't "8 real quarters"

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

## What happened

Reported directly: the Quarterly Results and Profit & Loss tables on the company page looked wrong, and both needed to show more history. Loading a real page (AAPL) confirmed the Quarterly Results table rendered only **2 quarters** (Q2 2026, Q3 2026) and the annual Profit & Loss/Balance Sheet/Cash Flow tables showed only **4 years** — despite the underlying SQL intending 8 quarters / 8 years.

## Root cause

`apps/site/src/lib/db.ts`'s `annual_periods`/`quarterly_periods` CTEs picked `distinct period.id ... limit 8` — treating each `core.period` row as one "period." That's wrong: a single real calendar quarter routinely produces **2 or more** distinct `core.period` rows — one `instant` (balance-sheet "as of" snapshot) and one `duration` (income-statement/cash-flow "for the period"), which is correct, standard XBRL modeling, not a bug in itself — plus, for some quarters, a third stray `instant` row a few weeks later (e.g. a shares-outstanding-as-of-filing-date fact). Confirmed live for AAPL: its real Q3 2026 has **three** separate `core.period` rows (ids 631, 714, 784) for what a user experiences as one quarter. `limit 8` on raw rows therefore covered only ~2-4 real quarters, not 8.

## Fix

Changed the CTEs to select 8 (quarterly) / 7 (annual, matching this project's own already-decided public-page depth policy) **distinct `(fiscal_year, fiscal_period)` combinations** first — the real reporting periods a user actually thinks of as "a quarter" or "a year" — then join back to pull in every `core.period` row belonging to those chosen periods (both `instant` and `duration`), so `assembleStatement()`'s existing per-statement-type filtering (income statement wants duration rows, balance sheet wants instant rows) always has a complete period to draw from.

One real implementation bug caught before shipping: an early draft computed `row_number()` in the same `select distinct` that was supposed to deduplicate `(company_id, fiscal_year, fiscal_period)` — since `row_number()` produces a unique value per underlying raw row *before* `distinct` is applied, every row became "distinct" by its own row number alone, defeating the dedup entirely. Fixed by computing `row_number()` in a second CTE layered on top of an already-deduplicated one.

## Verified

Restarted the dev server, fetched real rendered pages (not just reasoned about the SQL): AAPL's Quarterly Results now shows Q4 2024 through Q3 2026 (8 real quarters, correct seasonal pattern — Q1's holiday-quarter revenue spike visible at $124-144B vs. $94-111B for other quarters), and Profit & Loss/Balance Sheet/Cash Flow all show FY2019-FY2025 (7 real years). Re-verified against JPM (a second, independent company) with the same result shape (8 quarters, 7 years). `npm test` (apps/site's own suite) still passes; no automated test exists for this specific SQL query (no test-DB fixture for this class of query in this codebase), so live verification against real rendered pages was the primary evidence, matching this project's own established discipline for DB-integration logic without a mocking fixture.

## Lesson

**"Distinct rows" and "distinct real-world periods" are not the same thing whenever more than one row can legitimately represent one period** — the same class of miscounting this project already hit once for XBRL facts themselves (an `instant` vs `duration` context is a standard, correct XBRL modeling choice, not a data quality problem), but here it silently leaked into a *counting/limiting* query rather than a value-resolution one. Any future `limit N` intended to mean "N real reporting periods" needs to dedupe on the real period identity `(fiscal_year, fiscal_period)` first, then expand back out to whatever raw rows are needed — never limit on the raw row count directly when more than one row can back a single real period.
