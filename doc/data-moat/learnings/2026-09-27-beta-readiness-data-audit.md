# 2026-09-27: Beta-readiness data audit

## What prompted it

The founder asked for data that is "top notch" and complete across companies before the beta. Instead of chasing one metric, I audited every operating company's stock page. That's the 4,587 active companies left after removing SPACs, trusts, BDCs and other classified non-operating entities. Each one was checked against 15 page essentials: a fresh price, revenue, 5+ years of history, a current FY and quarter, net income, assets, CFO, EPS, equity, sector, About, insider and institutional ownership, and a recent 10-K/10-Q. Companies were ranked by revenue, and each tier was checked separately.

At the start, **87–89% of the top 100/500/1,000 companies passed every check, but only 62% of all companies did.** The top-tier failures were well-known names, and nearly every one traced to a systemic bug rather than a one-off gap.

## Findings and fixes

| # | Problem | Scale | Fix | Commit |
|---|---|---|---|---|
| 1 | `price_date` was the run date, not the bar's trading date. Weekend runs duplicated Friday's close, and tickers with no recent trades had years-old bars stamped as today's price. | 23,367 of 53,508 rows | Key on the bar's New York trading date. Existing rows re-dated once in place; 10,944 duplicates removed. | 8787e17 |
| 2 | Price metrics used any price, however old. | 131 companies valued off 1-month to 5-year-old bars | `MAX_PRICE_AGE_DAYS = 14` → `stale:real_price` | 8787e17 |
| 3 | Share-class tickers (`BRK-A`) were rejected by Alpaca, which uses `BRK.A`. | Berkshire, Brown-Forman, Moog, Crawford had no price | Translate `X-A` → `X.A` (never `-P…` preferreds) | 8787e17 |
| 4 | Nothing recomputed price metrics or rebuilt the screener snapshot on a schedule. | Market caps were on 09-08 prices; the snapshot was last built 09-19 | New `valuations-and-screener` job + `scripts/refresh_valuations.sh` | 8787e17 |
| 5 | A `company_tag_preference` blanked every period after its tag was last filed. | Mohawk revenue stopped at 2017 | Primary concept fills periods after the preferred tag's last one | 8787e17 |
| 6 | Utilities moved to `RegulatedAndUnregulatedOperatingRevenue` after ASC 606, which wasn't mapped. | DTE (2017), Xcel (2018), 20 utilities / 636 periods | Migration 0078, revenue priority 6. Zero conflicting values in the periods it fills. | 8787e17 |
| 7 | The reprocess cron's 10-day lookback lost filings during outages. | 348 companies' latest 10-K/10-Q never normalized: NextEra, Dow, DTE, Cintas FY2026 | Backlog branch: latest 10-K/Q with no `core.fact` rows but a newer payload, 150/run | (reprocess commit) |
| 8 | Market cap used share counts of any age. Multi-class filers moved to per-class tagging, which Company Facts strips. | 173 companies on pre-2024 counts: Visa, Mastercard, UPS, Accenture (2010), Ford (2011), Comcast (2009). Visa showed $173B. | Share count must be within 480 days. Otherwise use the cover-page count cross-checked (±25%) against the diluted weighted average, then the weighted average, then the cover page, then null. Visa $666B, Comcast $79B. | (shares commit) |
| 9 | The 10-K's own XBRL tags the annual total with a Q4 context, and derive-q4 trusted any reported Q4. | 95 companies with a quarter exactly equal to FY: NiSource $6.5B "Q4", L3Harris $21.3B | Demote a reported Q4 equal to FY when Q1–Q3 are non-zero, then derive | 62318c8 |
| 10 | Display concepts were fill-only, so corrections never reached the page. | NiSource stayed at $6.52B after the fix; 2 revenue + 5 gross-profit rows population-wide | Drop single-source display rows whose cited fact changed value, and rows built only from demoted Q4s | 482a012 |
| 11 | MLPs report EPS per LP unit under a different tag. | ~20 partnerships (ET, MPLX, PAA, WES) had no EPS or P/E | Migration 0079, diluted_eps priority 2, zero conflicts across 36 filers | 482a012 |
| 12 | JPM files quarterly total net revenue only under `RevenuesNetOfInterestExpense`. | JPM quarterly revenue stopped at 2014 | JPM-only `company_tag_preference` (equal to `Revenues` in all 8 overlapping FYs). Rejected as a global mapping: 13% agreement population-wide. | DB row |

## Checked and deliberately not changed

- **Blanket "refresh display from primary."** 7,123 fact-backed display rows differ from `revenue`, but the display is often the correct one (American Tower Q3 2020: $2.0B vs $131.6M; CPS: $1.2B vs 0). Only the two narrow stale shapes above are refreshed. The rest need per-row adjudication.
- **L3Harris FY2025.** There's no FY context at all: the annual $21.865B is filed only with Q4 dates. Deriving a quarter from it would be inference, so it's left as filed.
- **Berkshire market cap** is now null instead of using a 2011 count. Class A and B can't be summed; one A share equals 1,500 B shares.
- **Multi-class EPS** (Visa, Hershey, Airbnb, KKR, Constellation Brands). Their EPS is per class and dimensional, so Company Facts strips it. It needs a rendered-report parser like `cost_of_revenue_parser.py`. Their P/E stays blank until then.
- **67 companies that file only basic EPS.** Using basic as diluted isn't justified without evidence.
- **OTC-only names** (Fannie Mae, Freddie Mac, cannabis MSOs) have no Alpaca price; that's a vendor coverage limit. Tickers that stopped trading in August (AvalonBay, Webster, Talkspace, Two Harbors, Liberty Broadband) should be reviewed for `status`.

## Operational lessons

- **An interrupted session can keep running.** After a restart, the pre-restart session (`scrooner-8b`) kept executing and launched a duplicate backfill over the same 348 companies. `ListAgents` showed it as a busy peer. Check `ListAgents` and `ps` after any restart before assuming earlier commands died.
- **macOS `ps` has no `etimes`.** The first watchdog silently never killed anything. Also, elapsed-time watchdogs kill legitimate long stages. "No CPU progress for 15 minutes" is the right hang signal here, because the pooler's 2-minute `statement_timeout` means a healthy worker is never idle that long.
- **Full-population recomputes belong on GitHub Actions** (`pipeline-recompute.yml`, runners a few ms from us-east-1). From the dev machine each round trip costs 0.3–1.7s, and a full Mapper pass is about 20 hours.
