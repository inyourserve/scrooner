# Scrooner Watchlist — Product One-Pager

**Promise:** Your companies. What changed. Pick up where you left off.

**User problem:** Investors save companies but lose track of new results, changes in fundamentals and their own reasons for following them.

**Product goal:** Help users quickly catch up on their followed companies and decide which deserve further research. Watchlist and Alerts are separate features.

## Core experience

One watchlist at `/app/watchlist`, with three views:

**All · Unreviewed · Reporting soon**

At the top, show a simple catch-up summary:

> **3 of your 12 companies have new updates. 2 report in the next 7 days.**

Users add companies from stock pages or screener results. Companies with unreviewed updates appear first by default.

## What each company row shows

| Field | Purpose |
|---|---|
| Company and ticker | Identify the stock |
| Price and daily change | See current market context |
| One valuation metric | Assess valuation at a glance; label the metric |
| Latest update | Understand what changed |
| Next earnings date | Prepare for results; label estimated dates |
| Review status | Distinguish new updates from reviewed ones |

Click a row to expand its updates and personal note.

## Three core capabilities

**1. What changed since my last review**

Show new earnings results and changes in four fundamentals: revenue growth, operating margin, EPS and free cash flow.

Display previous and latest values side by side. Compare quarterly figures with the same quarter last year, clearly label periods and link to the source. Keep explanations short and factual.

If several results arrived since the last review, show the latest first and keep earlier unread updates accessible.

**2. Remember why I saved this company**

Provide one editable personal note per company.

Example: “Watching whether services growth supports margins.”

Keep the note visible alongside updates so users can relate new information to their research.

**3. Pick up where I left off**

A **Mark as reviewed** action clears the updates the user has seen. Future updates return the company to the Unreviewed view.

Opening the watchlist alone does not mark updates as reviewed.

## Simple controls

- Search within the watchlist.
- Sort by unreviewed updates, earnings date, daily movement or company name.
- Add or remove companies.
- Edit a note and mark updates as reviewed.

## Keep / Kill scope

**Keep:** Catch-up summary, compact company rows, fundamental comparisons, earnings dates, personal notes and review history.

**Exclude:** Health scores, automatic risk rankings, buy/sell judgments, every filing as an update, daily AI price commentary, attachments and elaborate tagging.

**Separate Alerts feature:** Price thresholds, valuation conditions, custom monitoring rules and notification delivery settings.

## Quality and success

Show timestamps, sources and unavailable data clearly. Corrected data must be labelled as a correction.

Measure repeat watchlist use, update reviews and continued use over time. The key validation: **Do users return because the watchlist helps them catch up faster?**