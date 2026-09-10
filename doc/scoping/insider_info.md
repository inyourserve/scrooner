# Scrooner: Ownership Page-Section MVP Scope

> **Frontend architecture note (2026-09-05):** This document contains historical implementation evidence from the retired frontend. Current implementation guidance is one Next.js App Router application in `apps/app` on `scrooner.com`, with authenticated workflows under `/app`.

> **Status:** Locked (2026-08-25) — a user-supplied product spec, not an execution plan. **Owner:** Founder/Product · **Review:** when the Ownership page section's scope changes. Uploaded directly by the user rather than written as a numbered `NN_Scrooner_...md` doc — left under its original filename rather than renamed/renumbered, since it's a source input other docs (doc 19, doc 21, `doc/reference/36_Scrooner_SEC_Filing_Types_Reference.md`) now cite by this name; renumbering it would break those references for no real benefit. Treat it the same as any other locked scoping doc despite the non-standard filename.
>
> **Build status (2026-08-29):** all three subsections' underlying data are built and verified against the golden-10 — Insider (full population, `ownership/insider.py` + `ownership/insider_summary.py`), Institutional Form 13F (two-quarter comparison, `ownership/institutional.py` + `ownership/institutional_summary.py`), Mutual Fund Form N-PORT (two-period comparison, `ownership/mutual_fund.py` + `ownership/mutual_fund_summary.py`).
>
> **Frontend built (2026-08-29)**, same day, following [`doc/audit/2026-08-29_ownership_insider_data_audit.md`](../audit/2026-08-29_ownership_insider_data_audit.md)'s findings — `apps/site/src/pages/stock/[ticker].astro` + `apps/site/src/lib/db.ts` now render the Overview strip and all three subsections, still within the page's single-query contract. Institutional and Mutual Fund render the rich two-period comparison (QoQ %, holder counts, Top 10 with status) for the golden-10 companies that have a `core.institutional_ownership_summary`/`core.fund_ownership_summary` row; every other company falls back to the older single-window list (Institutional) or an honest "not yet computed" note (Mutual Fund, which has no older fallback to fall back to). Insider ownership %/rolling summary renders wherever `ownership/insider_summary.py`'s in-progress full-population run has already reached (~68% of companies with any Form 4 data as of this pass) — same honest-null discipline, not an error state. See that section's own **Display-rule addendum** below for two display decisions locked as part of this build.

Understood. Scrooner will include **all three ownership sections** in the MVP.

## Final Ownership MVP

### 1. Insider Ownership & Transactions

* Current insider ownership percentage
* Last **12 months** of transactions
* Latest **10 transactions** on the company page
* Summary for 3, 6 and 12 months
* Total open-market buying and selling
* Number of insiders buying and selling
* Largest purchase and sale
* Transaction classifications:

  * Open-market buy
  * Open-market sale
  * Grant
  * Option exercise
  * Gift
  * Tax-related disposal
* Insider name, designation, shares, price, value, transaction date and post-transaction holding
* Link to the original SEC Form 4 filing
* “View All” for the complete 12-month list

### 2. Institutional Ownership — Form 13F

* Latest **two consecutive quarters**
* Total institutional ownership percentage
* Quarter-over-quarter change
* Total number of institutional holders
* Institutions increasing positions
* Institutions reducing positions
* New positions
* Exited positions
* Top **10 institutional holders**
* Holder name, shares, holding value, ownership percentage, share change, percentage change, status and reporting date
* “View All Institutional Holders”

### 3. Mutual Fund Ownership

* Latest **two consecutive reporting periods**
* Total mutual fund ownership percentage
* Change from the previous period
* Number of mutual funds holding the company
* Funds increasing and reducing positions
* New and exited fund positions
* Top **10 mutual fund holders**
* Fund name
* Fund family
* Shares held
* Estimated holding value
* Company ownership percentage
* Portfolio weight, when available
* Change in shares
* Change percentage
* Position status
* Reporting date
* “View All Mutual Funds”

## Page structure

Use one main section called **Ownership**, containing:

1. Ownership Overview
2. Insider Ownership
3. Institutional Ownership
4. Mutual Fund Ownership

The overview should display:

* Insider ownership %
* Institutional ownership %
* Mutual fund ownership %
* Latest reporting dates
* Change from the previous reporting period

## Important data rule

Do not add institutional and mutual fund percentages together. A mutual fund can appear through an institutional investment manager’s filing, creating overlap between the datasets.

Treat them as separate perspectives:

* **Institutional ownership:** manager-level Form 13F positions
* **Mutual fund ownership:** individual fund-level positions
* **Insider ownership:** officers, directors and major internal shareholders

## MVP history

* Insider transactions: **12 months**
* Institutional ownership: **two quarters**
* Mutual fund ownership: **two reporting periods**
* Top holders displayed: **10 per section**
* No five-year history
* Preserve newly collected data so history develops naturally

## Disclosure

Clearly mention that ownership data comes from regulatory filings, is not live, and reporting dates may differ. Institutional filings can arrive up to 45 days after a quarter ends, while individual mutual fund reporting schedules may vary.

This gives you the complete Trendlyne-style ownership coverage without taking on unnecessary historical backfilling for the MVP.

## Display-rule addendum (2026-08-29)

Two presentation rules, locked before the frontend build so they didn't need retrofitting afterward — findings 1 and 2 of [`doc/audit/2026-08-29_ownership_insider_data_audit.md`](../audit/2026-08-29_ownership_insider_data_audit.md)'s top-3 recommendation list. Neither needed new pipeline data; both are display decisions over fields `ownership/insider_summary.py` already computes.

1. **Net $ leads, not separate gross totals.** The Insider Ownership & Transactions subsection's rolling 3/6/12-month summary shows **Net $ (open-market buy − open-market sell)** as its own headline column, signed and colored, ahead of the separate gross-bought/gross-sold figures (both still shown, just secondary). Rationale: a headcount or a pair of gross totals doesn't tell a common investor the one thing they actually want at a glance — did insiders net buy or net sell, and by how much. `buy_dollar_volume`/`sell_dollar_volume` were already computed per window; net is a display-layer subtraction, zero pipeline change.
2. **The 12-month transaction list defaults to open-market only.** Form 4 filings are dominated by routine grants/option-exercises/gifts/tax-withholding; genuine buy/sell conviction transactions (codes P/S) are the minority. The full list defaults to showing only P/S rows, with an explicit "Show all transaction types" toggle — never silently hiding data, just not letting routine compensation mechanics drown out the signal by default. Zero pipeline change: `transaction_code` was already stored and classified (`ownership/transaction_codes.py`); this is a client-side filter over the existing 15-row query.

Both are implemented in `apps/site/src/pages/stock/[ticker].astro` (see its own inline comment pointing back to this addendum) — not schema or pipeline changes, so they carry no migration and apply retroactively to every company as soon as the page loads.
