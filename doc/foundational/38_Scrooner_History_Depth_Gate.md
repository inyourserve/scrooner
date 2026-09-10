# 38 — History-Depth Gate: How Much History Any New Fetch Actually Needs

> **Status:** Canonical, a mandatory gate — check this before writing any new fetch that could pull historical data. **Owner:** Founder/Product · **Review:** whenever a new fetch/module is scoped, and whenever this gate is itself found wrong against real evidence.

Prompted directly (2026-08-30) after a real, expensive pattern repeated three times in one night: a fetch module built with no history bound at all, later found to be pulling and storing years of data nobody needed. This doc turns that repeated mistake into a rule to check **before** writing the fetch, not a lesson re-learned after the fact.

## The rule

**Before writing any new SEC fetch (or extending an existing one to pull more history), answer this, in order, and stop at the first match:**

1. **Does the filing already contain its own embedded comparison?** (e.g., a 10-Q's segment/disaggregated-revenue table already shows current quarter + year-ago quarter + YTD + year-ago YTD, all in one document.) → **Fetch only the single most recent filing. No backfill, no multiple periods, no historical fetch at all.** History accumulates naturally as this job reruns on a schedule and keeps old rows instead of overwriting them.
2. **Does the source require mandatory periodic refiling regardless of whether anything changed?** (Form 13F: every manager, every quarter, no exceptions. Form N-PORT: every fund, every reporting period.) → **2 consecutive periods is enough.** The mandatory cadence guarantees fresh data exists at that interval; going back further only adds noise, not real coverage.
3. **Does the source represent discrete, per-event transactions with no natural "snapshot" period?** (Form 4: one filing per trade.) → **A rolling window sized to match the actual display need** (this project's own precedent: 12 months, because the UI only ever shows the 15 most recent transactions — even 12 months is generous headroom over that, not a tight fit).
4. **Does the source have NO mandatory refiling requirement — only refiled if something changed?** (Schedule 13D/13G: no annual refile required if the position is unchanged.) → **This is the dangerous case. A short window (matching case 3's logic) will silently drop real, currently-active data**, because "hasn't filed recently" does not mean "no longer applies" the way it does for a mandatory-cadence source. Use a longer window (this project's own precedent: 3 years, chosen only after checking live that a 1-year bound would have excluded the overwhelming majority of genuinely-active positions) and say explicitly why the window is longer than cases 2/3.
5. **Hard ceiling, applies regardless of the above**: never fetch, keep, or resolve data older than **January 1, 2015** as "current" for any feature. This project's own live check found real XBRL tagging reliability craters before ~2011 (27% of all FY periods are pre-2015, overwhelmingly from the pre-mandatory-XBRL era) — pre-2015 data is not a source of truth for anything display-facing, only a lossless historical record `core`/`raw` may still hold.

**If none of cases 1-4 clearly apply, don't guess — write down the source's real refiling behavior first** (checked live against the actual filing type, not assumed), then pick the shortest window that reliably covers it. A window chosen without checking the source's real refiling cadence is exactly the mistake this doc exists to prevent.

## The real evidence behind each precedent, so a future session can verify or override it

| Source | Real refiling cadence (checked live) | Window chosen | Evidence |
|---|---|---|---|
| Form 4 (insider transactions) | Per-transaction, no fixed cadence | 12 months rolling | Matches `apps/app`'s own display (15 most recent transactions shown) — even 12 months is generous headroom, not tight |
| Form 13F (institutional ownership) | Mandatory every quarter, every manager, no exceptions | 2 consecutive quarters | `insider_info.md`'s own locked MVP spec; mandatory cadence guarantees freshness at that interval |
| Form N-PORT (mutual fund ownership) | Mandatory every reporting period, every fund | 2 consecutive periods | Same reasoning as Form 13F |
| Schedule 13D/13G (beneficial ownership, >5% holders) | **No mandatory refiling if unchanged** | 3 years | Found live 2026-08-30: 73% of all (company, filer) relationships in the *unbounded* live table had their most-recent filing >3 years old — almost certainly genuinely-closed positions, not stale-but-current ones. A 1-year bound was tested against the same data and found wrong: only 1 of 53,067 relationships had a most-recent filing within the last year, which would make a 1-year window actively harmful, not just conservative, given 13G's own no-change exemption |
| Revenue-by-segment (10-Q/10-K disaggregation notes) | Filed quarterly/annually, but each filing already shows multiple comparison periods in one table | Single most-recent filing, zero backfill | Confirmed live 2026-08-30: Apple's own most recent 10-Q already contains current quarter, year-ago quarter, current YTD, and year-ago YTD — all four in one fetch, one document |
| Financial statement periods / metric "most recent value" resolution | N/A — a display/resolution floor, not a source-specific fetch bound | Floor: 2015-01-01. Ceiling: today + 30 days | 27% of all `core.period` FY rows are pre-2015 (pre-mandatory-XBRL era, sparse/unreliable). Ceiling exists because a genuinely malformed future-dated period (found live: one filer's real XBRL typo dated `2104-12-31`; a second, `6016-06-30`) would otherwise sort as "most recent" under every `ORDER BY period_end DESC` resolution rule in this project |

## What this gate would have prevented, if it had existed sooner

`beneficial_ownership.py` was built and run for weeks with no history bound at all — every Schedule 13D/13G filing ever filed for a company, back to whenever they started filing. The real cost, found only after the fact: **193,751 of 214,907 stored rows (90%) were outside the window this doc's own case-4 reasoning would have picked from the start**, and the unbounded fetch was very likely the direct cause of the crosswalk job's own real-time slowdown (large companies with decades of filing history taking many minutes each, one HTTP request per historical filing). The fix, applied 2026-08-30, cost nothing beyond writing this doc's own case-4 answer down *before* the module existed — the fetch-time filter and the 3-year number are exactly what this gate would have produced on day one.

## How to apply this gate going forward

- **Before scoping any new fetch module** (the segment-revenue work, doc 37, already applied this correctly from the start — case 1 above, confirmed live before writing a line of fetch code): write down which of cases 1-5 applies, with real evidence for the source's refiling cadence, in the scoping doc itself.
- **Before extending an existing fetch to pull more history than it currently does**: re-run this same check — "more history" is not free just because the code already exists.
- **This gate itself is not exempt from being wrong**: if a future case's real cadence turns out to need a different window than 2 periods / 12 months / 3 years, check live and say so explicitly, the same discipline this whole table already used to arrive at its own numbers.
